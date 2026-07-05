"""
Cricket Content Extractor
==========================
Reads pre-transcribed page text, then sends each page's text to an LLM to
extract structured cricket content: match reports, statistics, team
information, player information, biographies, and newspaper cuttings.

Outputs:
    match_index_<model>.csv  — one row per entry found (post-normalized + deduped)
    raw_responses_<model>.jsonl  — per-page raw LLM output for diagnostics
"""

import csv
import logging
from pathlib import Path

from . import config
from .llm_common import JSONExtractError, no_thinking_kwargs, parse_json_object
from .normalize import (
    ClubRegistry,
    detect_publication_date,
    matchup_key,
    normalize_date,
    normalize_matchup,
    normalize_title,
    relative_dates,
    title_key,
)
from .pipeline import RawResponseLog, load_pages, parse_page_spec, resolve_model, run_pages

logger = logging.getLogger(__name__)

VALID_CONTENT_TYPES = config.VALID_CONTENT_TYPES

SYSTEM_PROMPT = (
    "You are an expert at reading historical cricket newspaper cuttings "
    "and extracting structured information from them. You identify match "
    "reports, player/team statistics, team season summaries, biographical "
    "sketches, general cricket commentary, and player information. "
    "Respond ONLY with a JSON object — no markdown fences, no prose."
)


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

def _parse_response(raw: str) -> list[dict]:
    parsed = parse_json_object(raw)
    entries = parsed.get("entries")
    if entries is None:
        entries = parsed.get("matches")
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


def extract_entries(model, page_num: int, page_text: str) -> tuple[list[dict], str]:
    """Returns (entries, raw_response_text). Raises JSONExtractError on bad shape."""
    prompt = build_user_prompt(page_num, page_text)
    response = model.prompt(prompt, system=SYSTEM_PROMPT, **no_thinking_kwargs(model))
    raw = response.text()
    return _parse_response(raw), raw


# ── Post-processing ──────────────────────────────────────────────────────────

def normalize_and_dedup(
    entries: list[dict],
    page_num: int,
    allowed_types: set[str] | None = None,
    registry: ClubRegistry | None = None,
) -> tuple[list[dict], list[dict]]:
    """Normalize title/date and drop duplicates within a page.

    Returns (kept, discarded). Each discarded item records the reason and the
    original entry so dropped data stays visible in the raw-responses log.
    """
    seen: set[tuple[str, str, str]] = set()
    out: list[dict] = []
    discarded: list[dict] = []

    def discard(reason: str, entry) -> None:
        discarded.append({
            "reason": reason,
            "entry": entry if isinstance(entry, dict) else str(entry),
        })

    for entry in entries:
        if not isinstance(entry, dict):
            discard("not a dict", entry)
            continue
        content_type = (entry.get("content_type") or "match information").strip().lower()
        if content_type not in VALID_CONTENT_TYPES:
            content_type = "match information"
        if allowed_types and content_type not in allowed_types:
            discard("filtered content type", entry)
            continue

        raw_title = entry.get("matchup", "") or entry.get("title", "")
        date = normalize_date(entry.get("date", ""))

        if content_type == "match information":
            title = normalize_matchup(raw_title, registry=registry)
            if not title:
                discard("empty title", entry)
                continue
            key = matchup_key(title)
        else:
            title = normalize_title(raw_title)
            if not title:
                discard("empty title", entry)
                continue
            key = title_key(title)

        dedup = (key, date, content_type)
        if dedup in seen:
            discard("duplicate", entry)
            continue
        seen.add(dedup)
        out.append(
            {
                "matchup": title,
                "page": page_num,
                "date": date,
                "content_type": content_type,
                "collection": config.COLLECTION_NAME,
                "record_id": (entry.get("record_id") or "").strip(),
            }
        )
    return out, discarded


def _row_key(matchup: str, date: str, content_type: str) -> tuple[str, str, str]:
    key = matchup_key(matchup) if content_type == "match information" else title_key(matchup)
    return (key, date, content_type)


def track_cross_page(global_seen: dict, rows: list[dict]) -> list[dict]:
    """Track entries across pages; return rows already seen on an earlier page.

    Cross-page duplicates are reported, not dropped — the same fixture can
    legitimately appear in consecutive issues, so a human decides.
    """
    dupes: list[dict] = []
    for row in rows:
        key = _row_key(row["matchup"], row["date"], row["content_type"])
        first_page = global_seen.get(key)
        if first_page is not None and first_page != row["page"]:
            dupes.append({**row, "first_page": first_page})
        else:
            global_seen.setdefault(key, row["page"])
    return dupes


# ── CLI ──────────────────────────────────────────────────────────────────────

def register_parser(subparsers):
    p = subparsers.add_parser(
        "extract-matches",
        help="Extract match/content index entries from transcribed page text.",
    )
    p.add_argument("--input", "-i", default=config.DEFAULT_TEXT_INPUT)
    p.add_argument("--model", "-m", default=config.DEFAULT_EXTRACT_MATCHES_MODEL)
    p.add_argument("--output", "-o", default=None)
    p.add_argument(
        "--pages",
        default=None,
        help="Comma-separated page numbers or ranges, e.g. '1,3,5-10'",
    )
    p.add_argument(
        "--content-types",
        default=None,
        help="Comma-separated content types to include (default: all). "
             "Common types: 'match information', 'statistics', 'team information', "
             "'newspaper cuttings', 'player information', 'biography'.",
    )
    p.set_defaults(func=run)
    return p


def run(args) -> None:
    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"Input not found: {input_path}")

    pages = load_pages(input_path)

    safe_model = config.safe_model_name(args.model)
    csv_path = Path(args.output) if args.output else Path(f"match_index_{safe_model}.csv")
    raw_log_path = Path(f"raw_responses_{safe_model}.jsonl")
    raw_log = RawResponseLog(raw_log_path)

    page_filter = parse_page_spec(args.pages)

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

    model = resolve_model(args.model)
    registry = ClubRegistry(config.CLUBS_CSV_PATH) if Path(config.CLUBS_CSV_PATH).exists() else None

    # Load already-processed pages from existing CSV to allow resuming;
    # also seed cross-page duplicate tracking from prior rows.
    processed_pages: set[int] = set()
    global_seen: dict[tuple[str, str, str], int] = {}
    if csv_path.exists():
        try:
            with csv_path.open(newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        page = int(row["page"])
                    except (KeyError, ValueError, TypeError):
                        continue
                    processed_pages.add(page)
                    key = _row_key(
                        row.get("matchup", ""),
                        row.get("date", ""),
                        (row.get("content_type") or "match information").strip().lower(),
                    )
                    global_seen.setdefault(key, page)
        except (OSError, csv.Error) as e:
            logger.warning("Could not read existing %s for resume: %s", csv_path, e)
    if processed_pages:
        print(f"Resuming: {len(processed_pages)} page(s) already in {csv_path}")

    if not csv_path.exists():
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["matchup", "page", "date", "content_type", "collection", "record_id"])

    total_entries = 0
    total_errors = 0
    cross_page_dupes: list[dict] = []

    def extract_fn(page_num: int, page_text: str) -> tuple[list[dict], str]:
        return extract_entries(model, page_num, page_text)

    def on_result(page_result) -> None:
        nonlocal total_entries, total_errors
        entries = page_result.result[0] if page_result.result else []
        raw = page_result.result[1] if page_result.result else ""
        error = page_result.error

        normalized, discarded = normalize_and_dedup(
            entries or [], page_result.page, allowed_types=content_filter, registry=registry,
        )
        page_dupes = track_cross_page(global_seen, normalized)
        cross_page_dupes.extend(page_dupes)

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

        raw_log.write(
            page_result.page,
            raw,
            parsed_count=len(entries or []),
            kept_count=len(normalized),
            discarded=discarded,
            error=error,
        )

        if error:
            total_errors += 1
            print(f"ERROR: {error}")
        else:
            note = f" ({len(page_dupes)} also on earlier page)" if page_dupes else ""
            print((f"{len(normalized)} entry(ies)" if normalized else "no entries") + note)

    run_pages(pages, processed_pages, extract_fn, on_result)

    print(f"\nDone. {total_entries} entries written to {csv_path}; {total_errors} page error(s).")
    if cross_page_dupes:
        print(f"{len(cross_page_dupes)} entry(ies) also appear on an earlier page (kept; review manually):")
        for d in cross_page_dupes:
            print(f"  page {d['page']}: {d['matchup']} [{d['date']}] first seen on page {d['first_page']}")
