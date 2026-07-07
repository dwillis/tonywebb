"""
Cricket Player Statistics Extractor
=====================================
Reads pre-transcribed page text, then sends each page's text to an LLM to
extract cumulative player statistics: batting averages, bowling averages,
and fielding figures from end-of-season tables.

Outputs:
    player_stats_<model>.json   — cumulative player statistics across all pages
    raw_responses_stats_<model>.jsonl  — per-page raw LLM output for diagnostics
"""

import json
import logging
from pathlib import Path

from . import config
from .llm_common import JSONExtractError, no_thinking_kwargs, parse_json_object
from .normalize import normalize_title, title_key
from .pipeline import RawResponseLog, load_pages, parse_page_spec, resolve_model, run_pages

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are an expert at reading historical cricket newspaper cuttings "
    "and extracting structured statistics from end-of-season averages tables. "
    "You accurately read team match summaries (matches played, won, lost, drawn, "
    "aggregate runs and wickets for and against), batting figures (innings, "
    "not-outs, runs, highest score, average), bowling figures (overs, maidens, "
    "runs, wickets, average, best figures), and fielding figures (catches, "
    "stumpings). Respond ONLY with a JSON object — no markdown fences, no prose."
)


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
        raise JSONExtractError("missing 'teams' key", raw=raw)
    if not isinstance(teams, list):
        raise JSONExtractError("'teams' is not a list", raw=raw)
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
        "season": config.SEASON,
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


# ── CLI ──────────────────────────────────────────────────────────────────────

def register_parser(subparsers):
    p = subparsers.add_parser(
        "extract-stats",
        help="Extract end-of-season player/team statistics from transcribed page text.",
    )
    p.add_argument("--input", "-i", default=config.DEFAULT_TEXT_INPUT)
    p.add_argument("--model", "-m", default=config.DEFAULT_EXTRACT_STATS_MODEL)
    p.add_argument("--output", "-o", default=None)
    p.add_argument(
        "--pages",
        default=None,
        help="Comma-separated page numbers or ranges, e.g. '1,3,5-10'",
    )
    p.set_defaults(func=run)
    return p


def run(args) -> None:
    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"Input not found: {input_path}")

    pages = load_pages(input_path)

    safe_model = config.safe_model_name(args.model)
    json_path = Path(args.output) if args.output else Path(f"player_stats_{safe_model}.json")
    raw_log_path = Path(f"raw_responses_stats_{safe_model}.jsonl")
    raw_log = RawResponseLog(raw_log_path)

    page_filter = parse_page_spec(args.pages)

    print(f"Input : {input_path}")
    print(f"Model : {args.model}")
    print(f"Output: {json_path}")
    print(f"Raw   : {raw_log_path}")

    if page_filter:
        pages = [(n, t) for n, t in pages if n in page_filter]
        print(f"Pages : {sorted(page_filter)}")
    else:
        print(f"Pages : {len(pages)} total")

    model = resolve_model(args.model)

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
        except (OSError, json.JSONDecodeError, KeyError) as e:
            logger.warning("Could not read existing %s for resume: %s", json_path, e)

    total_added = 0
    total_errors = 0

    def extract_fn(page_num: int, page_text: str) -> tuple[list[dict], str]:
        return extract_teams(model, page_num, page_text)

    def on_result(page_result) -> None:
        nonlocal all_teams, total_added, total_errors
        teams_raw = page_result.items
        raw = page_result.raw
        error = page_result.error

        all_teams, added = merge_teams(all_teams, teams_raw or [], page_result.page)
        total_added += added

        processed_pages.add(page_result.page)

        # Write full JSON after every page so progress is never lost
        json_path.write_text(
            json.dumps(
                {
                    "metadata": {
                        "collection": config.COLLECTION_NAME,
                        "season": config.SEASON,
                        "model": args.model,
                        "pages_processed": len(processed_pages),
                    },
                    "teams": all_teams,
                },
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        raw_log.write(
            page_result.page,
            raw,
            parsed_count=len(teams_raw or []),
            added_count=added,
            error=error,
        )

        if error:
            total_errors += 1
            print(f"ERROR: {error}")
        else:
            print(f"{added} team(s) added" if added else "no new teams")

    run_pages(pages, processed_pages, extract_fn, on_result)

    # Final write with accurate pages_processed count
    total_players = sum(len(t.get("players", [])) for t in all_teams)
    json_path.write_text(
        json.dumps(
            {
                "metadata": {
                    "collection": config.COLLECTION_NAME,
                    "season": config.SEASON,
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
