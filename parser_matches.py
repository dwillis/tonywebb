"""
Cricket Content Extractor
==========================
Reads pre-transcribed full text from a model output file, then sends each
page's text to an LLM to extract structured cricket content: match reports,
statistics, team information, player information, biographies, and newspaper
cuttings.

Usage:
    python parser_matches.py
    python parser_matches.py --model gpt-4o
    python parser_matches.py --input full_text_output_gemini31pro.txt --output match_index_new.csv
    python parser_matches.py --content-types "match information,statistics"

Outputs:
    match_index_<model>.csv  — one row per entry found (post-normalized + deduped)
    raw_responses_<model>.jsonl  — per-page raw LLM output for diagnostics
"""

import argparse
import csv
import json
import re
import time
from pathlib import Path

import llm

from normalize import (
    ClubRegistry,
    detect_publication_date,
    matchup_key,
    normalize_date,
    normalize_matchup,
    normalize_title,
    relative_dates,
    title_key,
)

_club_registry = ClubRegistry("clubs.csv") if Path("clubs.csv").exists() else None

# ── Defaults ──────────────────────────────────────────────────────────────────

DEFAULT_INPUT_FILE = "full_text_output_gemini31pro.txt"
DEFAULT_MODEL_ID = "qwen3.5:397b-cloud"
COLLECTION_NAME = "Tony Webb minor counties collection"
VALID_CONTENT_TYPES = {
    "article",
    "award information",
    "biography",
    "fixture information",
    "ground information",
    "laws",
    "league information",
    "match information",
    "newspaper cuttings",
    "obituary",
    "organisation information",
    "photograph",
    "player information",
    "season information",
    "scorer information",
    "statistics",
    "team information",
    "tour information",
    "umpire information",
    "updates",
}

RATE_LIMIT_DELAY = 1.5
RETRY_ATTEMPTS = 1  # one retry on transient errors (not on JSON parse errors)
RETRY_BACKOFF = 5.0

SYSTEM_PROMPT = (
    "You are an expert at reading historical cricket newspaper cuttings "
    "and extracting structured information from them. You identify match "
    "reports, player/team statistics, team season summaries, biographical "
    "sketches, general cricket commentary, and player information. "
    "Respond ONLY with a JSON object — no markdown fences, no prose."
)


# ── Page parsing ─────────────────────────────────────────────────────────────

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


# ── Prompt building ──────────────────────────────────────────────────────────

def build_user_prompt(page_num: int, page_text: str) -> str:
    pub = detect_publication_date(page_text)
    if pub:
        rel = relative_dates(pub)
        rel_lines = "\n".join(
            f"  {wd.capitalize()}: {iso}" for wd, iso in rel.items()
        )
        date_context = (
            f"PUBLICATION DATE: {pub.isoformat()} ({pub.strftime('%A')})\n"
            "When the text says 'on Friday', 'last Wednesday', etc., resolve "
            "those weekdays to the most recent occurrence prior to the "
            "publication date. For this page that means:\n"
            f"{rel_lines}\n"
        )
    else:
        date_context = (
            "PUBLICATION DATE: unknown — extract dates only when the text "
            "states them explicitly. Do not guess.\n"
        )

    return f"""Below is the transcribed text of page {page_num} from the Tony Webb
minor counties collection of cricket newspaper cuttings (1895).

{date_context}
For each distinct piece of cricket content on this page, create an entry
in "entries" with:
  - "title": a short descriptor (see rules per content_type below)
  - "date": as YYYYMMDD. Use "18950000" if only the year is clear,
            "18950800" if only the month is clear, "" if completely unknown.
  - "content_type": one of the allowed types below
  - "collection": "Tony Webb minor counties collection"
  - "page": {page_num}

STYLE RULES (apply to all titles):
  * Do not use periods/full stops in abbreviations: "Mr" not "Mr.",
    "Dr" not "Dr.", "Rev" not "Rev.", "St" not "St.", "MCC" not "M.C.C."
  * Write initials without periods and with a space before the surname:
    "MJK Smith" not "M.J.K. Smith".
  * Use Roman numerals: "XII" not "12" or "Twelve", "XI" not "Eleven".
  * Use "Second XI" not "2nd XI".
  * Use full university names: "Oxford University" not "Oxford Uni".
  * Preserve apostrophes in names: "King's" not "Kings".
  * Do not use brackets, commas, or full stops in titles.
  * Use county names as used today: "Somerset" not "Somersetshire".
  * Drop trailing "CC" or "Cricket Club" from team names.
  * Use title case.

CONTENT TYPES (most common for this collection listed first):

1. "match information" — A report of a specific cricket match between two
   named teams.
   Title format: "Team A v Team B" (use "v" with no period).
   Examples: "Chalton v Houghton Second XI", "Waterlow's v East Finchley".

2. "statistics" — A table of batting averages, bowling averages, or aggregate
   team statistics for a club's season. One entry per distinct table.
   Title format: "Team Name player statistics" or "Team Name team aggregates".
   Examples: "Sunningdale School player statistics",
             "Biscuit Factory team aggregates".

3. "team information" — A season summary, fixture list, or list of match
   results for a team (NOT a single match report).
   Title format: "Team Name" or "Team Name match list".
   Examples: "Newbury match list", "Reading School match list".

4. "player information" — Player rosters, lists of player names with roles.
   Distinct from statistics (which have numeric averages).
   Title format: "Team Name players".
   Example: "Reading School players".

5. "biography" — A biographical sketch or profile of a cricket personality.
   Title format: the person's name.
   Example: "LCR Thring".

6. "newspaper cuttings" — General cricket commentary, gossip columns, or
   cricket news that does not fit the other categories.
   Title format: the location or source name.
   Example: "Cambridge".

Other allowed content types (use when appropriate):
  "article", "award information", "fixture information",
  "ground information", "laws", "league information", "obituary",
  "organisation information", "photograph", "season information",
  "scorer information", "tour information", "umpire information",
  "updates".

IMPORTANT RULES:
- A page may contain multiple entries of different or the same type.
- Match scorecard details (individual batting/bowling figures within a match
  report) are part of the match, NOT separate "statistics" entries.
  "statistics" means end-of-season averages tables for a team.
- If a page contains a team's fixture list AND that team's batting/bowling
  averages, create BOTH a "team information" entry AND a "statistics" entry.
- Do NOT create "fixture information" entries for lists of upcoming or
  unplayed fixtures. Only create entries for matches that have RESULTS.
- If a match report continues from a previous page (starts mid-scorecard
  with no header), do NOT create a new entry for it. Only create entries
  for content that BEGINS on this page.
- A typical page has 2-8 entries. If you find more than 12, reconsider
  whether you are splitting single match reports into multiple entries.
- Drop "Mr", "Mr." and other honorifics from personal XI names:
  use "F Gentle's XI" not "Mr F Gentle's XI".
- Drop trailing "OC" from team names unless it is clearly part of the
  official team name (e.g., use "Waterlow's" not "Waterlow's OC").

KEY 1895 DATES (for resolving historical date references):
- Whit-Monday (Bank Holiday): 27 May 1895
- Whit-Tuesday: 28 May 1895
- Good Friday: 12 April 1895
- Easter Monday: 15 April 1895
- August Bank Holiday: 5 August 1895
When the text says "Whit-Monday", "Bank Holiday", etc., use these dates.
The PUBLICATION DATE is NOT the match date — matches are typically
reported days after they were played.

EXAMPLES OF CORRECT EXTRACTION:

Example 1 — Match report with a date reference:
  Text: "KENSWORTH v. DUNSTABLE VICTORIA.--Played on Whit-Monday..."
  (Publication date: Saturday 8 June 1895)
  Correct: {{"title": "Kensworth v Dunstable Victoria",
             "date": "18950527", "content_type": "match information"}}
  Note: "Whit-Monday" in 1895 was 27 May. Do NOT use the publication
  date (8 June) as the match date.

Example 2 — Match report with scorecard:
  A match header followed by detailed batting and bowling figures is
  ONE "match information" entry. Do NOT create separate "statistics"
  entries for the individual scores within a match report.

Example 3 — Resolving "on Friday":
  (Publication date: Saturday 8 June 1895)
  Text: "The match was played on Friday"
  Correct date: "18950607" (the Friday before the Saturday publication)

Return ONLY a JSON object with a single key "entries" (array). If no
cricket content is found, return {{"entries": []}}.

PAGE {page_num} TEXT:
{page_text}"""


# ── LLM extraction ───────────────────────────────────────────────────────────

class JSONExtractError(Exception):
    """Raised when the model's response can't be parsed as the expected JSON shape."""


def _parse_response(raw: str) -> list[dict]:
    text = raw.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as e:
        raise JSONExtractError(f"invalid JSON: {e}") from e
    if not isinstance(parsed, dict):
        raise JSONExtractError("response is not a JSON object")
    entries = parsed.get("entries") or parsed.get("matches")
    if entries is None:
        raise JSONExtractError("missing 'entries' (or 'matches') key")
    if not isinstance(entries, list):
        raise JSONExtractError("'entries' is not a list")
    for entry in entries:
        if isinstance(entry, dict):
            if "title" in entry and "matchup" not in entry:
                entry["matchup"] = entry.pop("title")
            ct = (entry.get("content_type") or "").strip().lower()
            if ct not in VALID_CONTENT_TYPES:
                ct = "match information"
            entry["content_type"] = ct
    return entries


def _no_thinking_kwargs(model) -> dict:
    """Return prompt kwargs that disable thinking for models that support it."""
    model_id: str = getattr(model, "model_id", "") or ""
    model_type = type(model).__module__ or ""
    if "ollama" in model_type:
        # llm-ollama exposes thinking as `think`
        return {"think": False}
    if any(x in model_id.lower() for x in ("claude", "opus", "sonnet", "haiku")):
        # Anthropic extended thinking: budget_tokens=0 disables it
        return {"budget_tokens": 0}
    return {}


def extract_entries(model, page_num: int, page_text: str) -> tuple[list[dict], str]:
    """Returns (entries, raw_response_text). Raises JSONExtractError on bad shape."""
    prompt = build_user_prompt(page_num, page_text)
    response = model.prompt(prompt, system=SYSTEM_PROMPT, **_no_thinking_kwargs(model))
    raw = response.text()
    return _parse_response(raw), raw


# ── Post-processing ──────────────────────────────────────────────────────────

def normalize_and_dedup(
    entries: list[dict],
    page_num: int,
    allowed_types: set[str] | None = None,
) -> list[dict]:
    """Normalize title/date and drop duplicates within a page."""
    seen: set[tuple[str, str, str]] = set()
    out: list[dict] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        content_type = (entry.get("content_type") or "match information").strip().lower()
        if content_type not in VALID_CONTENT_TYPES:
            content_type = "match information"
        if allowed_types and content_type not in allowed_types:
            continue

        raw_title = entry.get("matchup", "") or entry.get("title", "")
        date = normalize_date(entry.get("date", ""))

        if content_type == "match information":
            title = normalize_matchup(raw_title, registry=_club_registry)
            if not title:
                continue
            key = matchup_key(title)
        else:
            title = normalize_title(raw_title)
            if not title:
                continue
            key = title_key(title)

        dedup = (key, date, content_type)
        if dedup in seen:
            continue
        seen.add(dedup)
        out.append(
            {
                "matchup": title,
                "page": page_num,
                "date": date,
                "content_type": content_type,
                "collection": COLLECTION_NAME,
                "record_id": (entry.get("record_id") or "").strip(),
            }
        )
    return out


def load_pages_from_dir(directory: Path) -> list[tuple[int, str]]:
    """Load per-page .txt files from a directory, sorted by page number."""
    pages = []
    for f in directory.glob("*.txt"):
        m = re.search(r"_(\d+)\.txt$", f.name)
        if m:
            pages.append((int(m.group(1)), f.read_text(encoding="utf-8").strip()))
    return sorted(pages, key=lambda x: x[0])


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Extract cricket content from pre-transcribed page text."
    )
    parser.add_argument("--input", "-i", default=DEFAULT_INPUT_FILE)
    parser.add_argument("--model", "-m", default=DEFAULT_MODEL_ID)
    parser.add_argument("--output", "-o", default=None)
    parser.add_argument(
        "--pages",
        default=None,
        help="Comma-separated page numbers or ranges, e.g. '1,3,5-10'",
    )
    parser.add_argument(
        "--content-types",
        default=None,
        help="Comma-separated content types to include (default: all). "
             "Common types: 'match information', 'statistics', 'team information', "
             "'newspaper cuttings', 'player information', 'biography'. "
             "See VALID_CONTENT_TYPES for the full list.",
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
    csv_path = Path(args.output) if args.output else Path(f"match_index_{safe_model}.csv")
    raw_log_path = Path(f"raw_responses_{safe_model}.jsonl")

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

    content_filter: set[str] | None = None
    if args.content_types:
        content_filter = {t.strip().lower() for t in args.content_types.split(",")}
        invalid = content_filter - VALID_CONTENT_TYPES
        if invalid:
            raise SystemExit(f"Unknown content type(s): {invalid}. Valid: {VALID_CONTENT_TYPES}")

    print(f"Input : {input_path}")
    print(f"Model : {args.model}")
    print(f"Output: {csv_path}")
    print(f"Raw   : {raw_log_path}")
    if content_filter:
        print(f"Types : {', '.join(sorted(content_filter))}")

    if page_filter:
        pages = [(n, t) for n, t in pages if n in page_filter]
        print(f"Pages : {sorted(page_filter)}")
    else:
        print(f"Pages : {len(pages)} total")

    # Refresh all plugins on every run and look up model directly from the list.
    all_models = {m.model_id: m for m in llm.get_models()}
    if args.model not in all_models:
        raise SystemExit(f"Unknown model: {args.model!r}. Run 'llm models' to see available models.")
    model = all_models[args.model]

    # Load already-processed pages from existing CSV to allow resuming
    processed_pages: set[int] = set()
    if csv_path.exists():
        try:
            with csv_path.open(newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        processed_pages.add(int(row["page"]))
                    except (KeyError, ValueError):
                        pass
        except Exception:
            pass
    if processed_pages:
        print(f"Resuming: {len(processed_pages)} page(s) already in {csv_path}")

    if not csv_path.exists():
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["matchup", "page", "date", "content_type", "collection", "record_id"])

    total_entries = 0
    total_errors = 0

    for page_num, page_text in pages:
        if page_num in processed_pages:
            print(f"  Skipping page {page_num} (already processed)")
            continue
        print(f"  Processing page {page_num} …", end=" ", flush=True)
        entries: list[dict] | None = None
        normalized: list[dict] = []
        raw = ""
        error: str | None = None

        try:
            for attempt in range(RETRY_ATTEMPTS + 1):
                try:
                    entries, raw = extract_entries(model, page_num, page_text)
                    break
                except JSONExtractError as e:
                    error = str(e)
                    entries = []
                    break  # don't retry — model output is the problem
                except Exception as e:  # transient API/network
                    error = str(e)
                    if attempt < RETRY_ATTEMPTS:
                        time.sleep(RETRY_BACKOFF)
                        continue
                    entries = []
                    break

            normalized = normalize_and_dedup(
                entries or [], page_num, allowed_types=content_filter,
            )

            if normalized:
                with csv_path.open("a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    for row in normalized:
                        writer.writerow([
                            row["matchup"],
                            row["page"],
                            row["date"],
                            row["content_type"],
                            row["collection"],
                            row["record_id"],
                        ])
                total_entries += len(normalized)

            with raw_log_path.open("a", encoding="utf-8") as logf:
                logf.write(json.dumps({
                    "page": page_num,
                    "raw": raw,
                    "parsed_count": len(entries or []),
                    "kept_count": len(normalized),
                    "error": error,
                }, ensure_ascii=False) + "\n")

            if error:
                total_errors += 1
                print(f"ERROR: {error}")
            else:
                print(f"{len(normalized)} entry(ies)" if normalized else "no entries")
        finally:
            time.sleep(RATE_LIMIT_DELAY)

    print(f"\nDone. {total_entries} entries written to {csv_path}; {total_errors} page error(s).")


if __name__ == "__main__":
    main()
