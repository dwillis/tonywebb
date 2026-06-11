"""
Cricket Player Statistics Extractor
=====================================
Reads pre-transcribed full text from a model output file, then sends each
page's text to an LLM to extract cumulative player statistics: batting
averages, bowling averages, and fielding figures from end-of-season tables.

Usage:
    python parser_stats.py
    python parser_stats.py --model gpt-4o
    python parser_stats.py --input full_text_output_gemini31pro.txt --output player_stats_new.json

Outputs:
    player_stats_<model>.json   — cumulative player statistics across all pages
    raw_responses_stats_<model>.jsonl  — per-page raw LLM output for diagnostics
"""

import argparse
import json
import re
import time
from pathlib import Path

import llm

from llm_common import (
    JSONExtractError,
    load_pages_from_dir,
    no_thinking_kwargs,
    parse_json_object,
)
from normalize import (
    normalize_title,
    title_key,
)

# ── Defaults ──────────────────────────────────────────────────────────────────

DEFAULT_INPUT_FILE = "full_text_output_gemini31pro.txt"
DEFAULT_MODEL_ID = "qwen3.5:397b-cloud"
COLLECTION_NAME = "Tony Webb minor counties collection"

RATE_LIMIT_DELAY = 1.5
RETRY_ATTEMPTS = 1
RETRY_BACKOFF = 5.0

SYSTEM_PROMPT = (
    "You are an expert at reading historical cricket newspaper cuttings "
    "and extracting structured statistics from end-of-season averages tables. "
    "You accurately read team match summaries (matches played, won, lost, drawn, "
    "aggregate runs and wickets for and against), batting figures (innings, "
    "not-outs, runs, highest score, average), bowling figures (overs, maidens, "
    "runs, wickets, average, best figures), and fielding figures (catches, "
    "stumpings). Respond ONLY with a JSON object — no markdown fences, no prose."
)


# ── Page parsing ──────────────────────────────────────────────────────────────

PAGE_SEPARATOR = re.compile(
    r"={10,}\s*\nPAGE\s+(\d+)\s*\n={10,}",
    re.MULTILINE,
)


def split_pages(text: str) -> list[tuple[int, str]]:
    pages = []
    matches = list(PAGE_SEPARATOR.finditer(text))
    for i, m in enumerate(matches):
        page_num = int(m.group(1))
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        pages.append((page_num, text[start:end].strip()))
    return pages


# ── Prompt building ───────────────────────────────────────────────────────────

def build_user_prompt(page_num: int, page_text: str) -> str:
    return f"""Below is the transcribed text of page {page_num} from the Tony Webb
minor counties collection of cricket newspaper cuttings (1895).

Extract all statistics from end-of-season averages tables on this page.
These are summary tables (NOT individual match scorecards).

Return a JSON object with a single key "teams" — an array where each element
represents one team's statistics block found on this page:

  - "name": team name. Drop trailing "CC" or "Cricket Club". Use county
    names as used today (e.g. "Somerset" not "Somersetshire"). Title case.
  - "matches" (if a season summary line is present): object with any of:
      "played" (integer), "won" (integer), "drawn" (integer), "lost" (integer)
  - "runs_scored" (if aggregate run/wicket totals are present): object with:
      "for":     {{"runs": int, "wickets": int, "average_per_wicket": number}}
      "against": {{"runs": int, "wickets": int, "average_per_wicket": number}}
      Omit "for" or "against" if only one side's figures are given.
  - "players": array of player objects, each with:
      - "name": initials without periods, space before surname
        ("AJ Smith" not "A.J. Smith"). Title case. Drop honorifics.
      - "batting" (if batting columns present): object with any of:
          "innings" (int), "not_outs" (int), "runs" (int),
          "highest_score" (string — append "*" if not-out, e.g. "45*"),
          "average" (number, or null if denominator is zero)
      - "bowling" (if bowling columns present): object with any of:
          "overs" (number), "maidens" (int), "runs" (int),
          "wickets" (int), "average" (number, or null if 0 wickets),
          "best" (string, e.g. "5/23")
      - "fielding" (if fielding columns present): object with any of:
          "catches" (int), "stumpings" (int)

RULES:
- Only extract from end-of-season AVERAGES TABLES, not individual match
  scorecards. An averages table lists multiple players with aggregate totals.
- If a page has no averages tables, return {{"teams": []}}.
- Omit any key whose value is entirely absent from the source text.
- A single page may contain averages tables for multiple teams; include all.
- Do NOT invent or infer statistics not present in the text.
- Overs in Victorian cricket may be 4-ball or 5-ball; transcribe as printed.

NAME STYLE RULES:
  * Write initials without periods: "AJ Smith" not "A.J. Smith".
  * Space between initials and surname: "AJ Smith" not "AJSmith".
  * Drop honorifics: "Smith" not "Mr Smith", "AJ Smith" not "Mr AJ Smith".
  * Preserve apostrophes in surnames: "O'Brien" not "OBrien".

If no averages tables are found on this page, return {{"teams": []}}.

PAGE {page_num} TEXT:
{page_text}"""


# ── LLM extraction ────────────────────────────────────────────────────────────

def _parse_response(raw: str) -> list[dict]:
    parsed = parse_json_object(raw)
    teams = parsed.get("teams")
    if teams is None:
        raise JSONExtractError("missing 'teams' key")
    if not isinstance(teams, list):
        raise JSONExtractError("'teams' is not a list")
    return teams


def extract_teams(model, page_num: int, page_text: str) -> tuple[list[dict], str]:
    """Returns (teams, raw_response_text). Raises JSONExtractError on bad shape."""
    prompt = build_user_prompt(page_num, page_text)
    response = model.prompt(prompt, system=SYSTEM_PROMPT, **no_thinking_kwargs(model))
    raw = response.text()
    return _parse_response(raw), raw


# ── Post-processing ───────────────────────────────────────────────────────────

def _clean_stat_value(value):
    """Coerce numeric-looking strings to numbers; return None for unusable values.

    Textual figures like "57*" (not out) or "6-23" (best bowling) are kept
    verbatim — only empty values and containers are dropped.
    """
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return None
        try:
            return int(s)
        except ValueError:
            pass
        try:
            return float(s)
        except ValueError:
            pass
        return s
    return None


def _normalize_player(entry: dict) -> dict | None:
    """Validate and normalize a single player record within a team. Returns None to discard."""
    if not isinstance(entry, dict):
        return None
    name = normalize_title(entry.get("name", ""))
    if not name:
        return None
    out: dict = {"name": name}
    for stat_key in ("batting", "bowling", "fielding"):
        val = entry.get(stat_key)
        if not isinstance(val, dict):
            continue
        cleaned = {}
        for k, v in val.items():
            cv = _clean_stat_value(v)
            if cv is not None:
                cleaned[k] = cv
        if cleaned:
            out[stat_key] = cleaned
    return out


def _normalize_team_entry(entry: dict, page_num: int) -> dict | None:
    """Validate and normalize a team statistics block. Returns None to discard."""
    if not isinstance(entry, dict):
        return None
    name = normalize_title(entry.get("name", ""))
    if not name:
        return None

    out: dict = {
        "name": name,
        "season": "1895",
        "page": page_num,
    }

    matches = entry.get("matches")
    if isinstance(matches, dict) and matches:
        out["matches"] = matches

    runs_scored = entry.get("runs_scored")
    if isinstance(runs_scored, dict) and runs_scored:
        out["runs_scored"] = runs_scored

    players_raw = entry.get("players") or []
    players: list[dict] = []
    seen_names: set[str] = set()
    for p in players_raw:
        normalized = _normalize_player(p)
        if normalized is None:
            continue
        key = title_key(normalized["name"])
        if key not in seen_names:
            seen_names.add(key)
            players.append(normalized)
    out["players"] = players

    return out


def _team_key(entry: dict) -> str:
    """Deduplication key: normalised team name."""
    return title_key(entry["name"])


def merge_teams(
    existing: list[dict],
    new_entries: list[dict],
    page_num: int,
) -> tuple[list[dict], int]:
    """
    Merge new team entries into existing, deduplicating by team name.
    Returns (updated_list, count_of_teams_added).
    """
    index: dict[str, int] = {_team_key(t): i for i, t in enumerate(existing)}
    added = 0

    for raw in new_entries:
        entry = _normalize_team_entry(raw, page_num)
        if entry is None:
            continue
        key = _team_key(entry)
        if key in index:
            # Same team name seen again — note the additional page
            pos = index[key]
            existing_pages = existing[pos].get("pages_seen", [existing[pos]["page"]])
            if page_num not in existing_pages:
                existing_pages.append(page_num)
                existing[pos]["pages_seen"] = existing_pages
        else:
            index[key] = len(existing)
            existing.append(entry)
            added += 1

    return existing, added




# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Extract cumulative player statistics from pre-transcribed page text."
    )
    parser.add_argument("--input", "-i", default=DEFAULT_INPUT_FILE)
    parser.add_argument("--model", "-m", default=DEFAULT_MODEL_ID)
    parser.add_argument("--output", "-o", default=None)
    parser.add_argument(
        "--pages",
        default=None,
        help="Comma-separated page numbers or ranges, e.g. '1,3,5-10'",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"Input not found: {input_path}")

    if input_path.is_dir():
        pages = load_pages_from_dir(input_path)
        if not pages:
            raise SystemExit(f"No .txt files found in {input_path}")
    else:
        full_text = input_path.read_text(encoding="utf-8")
        pages = split_pages(full_text)
        if not pages:
            raise SystemExit("No pages found. Check the PAGE separator format.")

    safe_model = re.sub(r"[^\w\-.]", "_", args.model)
    json_path = Path(args.output) if args.output else Path(f"player_stats_{safe_model}.json")
    raw_log_path = Path(f"raw_responses_stats_{safe_model}.jsonl")

    page_filter: set[int] | None = None
    if args.pages:
        page_filter = set()
        for part in args.pages.split(","):
            part = part.strip()
            if "-" in part:
                lo, hi = part.split("-", 1)
                page_filter.update(range(int(lo), int(hi) + 1))
            elif part:
                page_filter.add(int(part))

    print(f"Input : {input_path}")
    print(f"Model : {args.model}")
    print(f"Output: {json_path}")
    print(f"Raw   : {raw_log_path}")

    if page_filter:
        pages = [(n, t) for n, t in pages if n in page_filter]
        print(f"Pages : {sorted(page_filter)}")
    else:
        print(f"Pages : {len(pages)} total")

    all_models = {m.model_id: m for m in llm.get_models()}
    if args.model not in all_models:
        raise SystemExit(f"Unknown model: {args.model!r}. Run 'llm models' to see available models.")
    model = all_models[args.model]

    # Load existing output to allow resuming
    processed_pages: set[int] = set()
    all_teams: list[dict] = []

    if json_path.exists():
        try:
            existing_data = json.loads(json_path.read_text(encoding="utf-8"))
            all_teams = existing_data.get("teams", [])
            for t in all_teams:
                processed_pages.add(t["page"])
                processed_pages.update(t.get("pages_seen", []))
            print(f"Resuming: {len(processed_pages)} page(s) already processed, "
                  f"{len(all_teams)} team(s) loaded")
        except Exception:
            pass

    total_added = 0
    total_errors = 0

    for page_num, page_text in pages:
        if page_num in processed_pages:
            print(f"  Skipping page {page_num} (already processed)")
            continue
        print(f"  Processing page {page_num} …", end=" ", flush=True)
        teams_raw: list[dict] = []
        raw = ""
        error: str | None = None

        try:
            for attempt in range(RETRY_ATTEMPTS + 1):
                try:
                    teams_raw, raw = extract_teams(model, page_num, page_text)
                    break
                except JSONExtractError as e:
                    error = str(e)
                    teams_raw = []
                    break
                except Exception as e:
                    error = str(e)
                    if attempt < RETRY_ATTEMPTS:
                        time.sleep(RETRY_BACKOFF)
                        continue
                    teams_raw = []
                    break

            all_teams, added = merge_teams(all_teams, teams_raw, page_num)
            total_added += added

            # Write full JSON after every page so progress is never lost
            json_path.write_text(
                json.dumps(
                    {
                        "metadata": {
                            "collection": COLLECTION_NAME,
                            "season": "1895",
                            "model": args.model,
                            "pages_processed": len(processed_pages) + 1,
                        },
                        "teams": all_teams,
                    },
                    indent=2,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            processed_pages.add(page_num)

            with raw_log_path.open("a", encoding="utf-8") as logf:
                logf.write(json.dumps({
                    "page": page_num,
                    "raw": raw,
                    "parsed_count": len(teams_raw),
                    "added_count": added,
                    "error": error,
                }, ensure_ascii=False) + "\n")

            if error:
                total_errors += 1
                print(f"ERROR: {error}")
            else:
                print(f"{added} team(s) added" if added else "no new teams")
        finally:
            time.sleep(RATE_LIMIT_DELAY)

    # Final write with accurate pages_processed count
    total_players = sum(len(t.get("players", [])) for t in all_teams)
    json_path.write_text(
        json.dumps(
            {
                "metadata": {
                    "collection": COLLECTION_NAME,
                    "season": "1895",
                    "model": args.model,
                    "pages_processed": len(processed_pages),
                    "total_teams": len(all_teams),
                    "total_players": total_players,
                },
                "teams": all_teams,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(f"\nDone. {total_added} team(s) added to {json_path}; {total_errors} page error(s).")


if __name__ == "__main__":
    main()
