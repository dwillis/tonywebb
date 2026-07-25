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

from . import config
from .indexing import (
    STYLE_RULES,
    VALID_CONTENT_TYPES,
    build_date_context,
    normalize_and_dedup,
    run_index_extraction,
    track_cross_page,
)
from .indexing import extract_entries as _extract_entries_generic
from .llm_common import JSONExtractError, parse_json_object

SYSTEM_PROMPT = (
    "You are an expert at reading historical cricket newspaper cuttings "
    "and extracting structured information from them. You identify match "
    "reports, player/team statistics, team season summaries, biographical "
    "sketches, general cricket commentary, and player information. "
    "Respond ONLY with a JSON object — no markdown fences, no prose."
)


# ── Prompt building ──────────────────────────────────────────────────────────

def build_user_prompt(page_num: int, page_text: str) -> str:
    date_context = build_date_context(page_text)

    return f"""Below is the transcribed text of page {page_num} from the Tony Webb
minor counties collection of cricket newspaper cuttings (1895).

{date_context}
For each distinct piece of cricket content on this page, create an entry
in "entries" with:
  - "title": a short descriptor (see rules per content_type below)
  - "date_phrase": the VERBATIM text in the source that indicates when this
    happened (e.g. "on Whit-Monday", "on Saturday", "Friday in last week",
    "5th August"), copied exactly as printed. This is resolved to a date
    deterministically in code, NOT by you -- do not compute a date yourself,
    just quote the phrase. Use "" if no date reference is present at all.
  - "date": your own best-effort YYYYMMDD guess, used only as a fallback if
    "date_phrase" can't be resolved. Use "18950000" if only the year is
    clear, "18950800" if only the month is clear, "" if completely unknown.
  - "content_type": one of the allowed types below
  - "collection": "Tony Webb minor counties collection"
  - "page": {page_num}

{STYLE_RULES}

CONTENT TYPES (most common for this collection listed first):

1. "match information" — A report of a specific cricket match between two
   named teams.
   Title format: "Team A v Team B" (use "v" with no period).
   Examples: "Chalton v Houghton Second XI", "Waterlow's v East Finchley".

2. "statistics" — End-of-season batting averages, bowling averages, or
   aggregate team statistics for a club's season. ONE "player statistics"
   entry per TEAM, no matter how many separate tables that team has (e.g.
   a batting table AND a bowling table, or separate First XI and Second XI
   tables, are ALL covered by a single entry for that team). If the SAME
   team ALSO has separate aggregate team figures (season record, total runs
   scored for/against as a team rather than per-player), create a SECOND
   entry titled "Team Name team aggregates".
   Title format: "Team Name player statistics" or "Team Name team aggregates".
   Examples: "Sunningdale School player statistics",
             "Biscuit Factory team aggregates".

3. "team information" — A season summary, fixture list, or list of match
   results for a team (NOT a single match report).
   Title format: "Team Name" or "Team Name match list".
   Examples: "Newbury match list", "Reading School match list".

4. "player information" — Player rosters, lists of player names with roles,
   OR a shared paragraph of brief (one- or two-sentence) character
   assessments covering SEVERAL players on one team (e.g. "Regarding the
   abilities of the players..." followed by a short note on each). This is
   ONE entry per team, no matter how many players are mentioned inside it.
   Distinct from statistics (which have numeric averages).
   Title format: "Team Name players".
   Example: "Reading School players".

5. "biography" — A SUBSTANTIAL, STANDALONE profile devoted to a single
   named individual — its own dedicated write-up, not one sentence sharing
   a paragraph with other players' assessments. If several players each get
   a short note in the same paragraph, that whole paragraph is ONE "player
   information" entry for the team (see above), NOT one "biography" entry
   per player.
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
- Exactly one "Team Name player statistics" entry per team per page, no
  matter how many separate tables (batting, bowling, First XI, Second XI,
  "An Eleven", etc.) that team has on the page.
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

The PUBLICATION DATE is NOT the match date — matches are typically
reported days after they were played. Do not try to resolve weekday names
or holiday names to a specific date yourself; just quote them verbatim in
"date_phrase" and let the deterministic resolver handle it.

EXAMPLES OF CORRECT EXTRACTION:

Example 1 — Match report with a date reference:
  Text: "KENSWORTH v. DUNSTABLE VICTORIA.--Played on Whit-Monday..."
  Correct: {{"title": "Kensworth v Dunstable Victoria",
             "date_phrase": "on Whit-Monday", "date": "18950527",
             "content_type": "match information"}}

Example 2 — Match report with scorecard:
  A match header followed by detailed batting and bowling figures is
  ONE "match information" entry. Do NOT create separate "statistics"
  entries for the individual scores within a match report.

Example 3 — A weekday reference:
  Text: "The match was played on Friday"
  Correct: {{"date_phrase": "on Friday", "date": "18950607"}}
  (Fill "date" with your own best guess, but "date_phrase" is what actually
  determines the final date — copy it verbatim.)

Example 4 — Shared player-assessment paragraph (NOT one biography per player):
  Text: "Regarding the abilities of the players the following should prove
  of interest:-R. H. Jackson (1892-5) captain. Very useful behind the
  wicket...-J. Hodge (1892-5). A much-improved bowler...-A. T. Cliff
  (1893-5). Is an untiring bowler..." (continuing with a one- or two-
  sentence note on each of several more players)
  Correct: ONE entry, {{"title": "Reading School players",
             "content_type": "player information"}}
  Incorrect: a separate "biography" entry for Jackson, another for Hodge,
  another for Cliff, etc. Only give a player their own "biography" entry
  if they get a substantial, standalone write-up of their own — not a
  single sentence inside a shared team paragraph like this one.

Example 5 — One team, several tables (NOT one entry per table):
  A page headed "LIVERPOOL CRICKET CLUB. BATTING AND BOWLING AVERAGES."
  with separate "BATTING.—First Eleven.", "BOWLING.—First Eleven.",
  "BATTING.—Second Eleven.", and "BOWLING.—Second Eleven." tables is still
  just ONE entry:
  {{"title": "Liverpool player statistics", "content_type": "statistics"}}
  Incorrect: separate entries for "Liverpool batting averages", "Liverpool
  bowling averages", "Liverpool Second XI batting averages", etc.

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
        raise JSONExtractError("missing 'entries' (or 'matches') key", raw=raw)
    if not isinstance(entries, list):
        raise JSONExtractError("'entries' is not a list", raw=raw)
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
    return _extract_entries_generic(
        model, page_num, page_text,
        prompt_builder=build_user_prompt, system_prompt=SYSTEM_PROMPT, parse_response=_parse_response,
    )


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
    content_filter: set[str] | None = None
    if args.content_types:
        content_filter = {t.strip().lower() for t in args.content_types.split(",")}
        invalid = content_filter - VALID_CONTENT_TYPES
        if invalid:
            raise SystemExit(f"Unknown content type(s): {invalid}. Valid: {VALID_CONTENT_TYPES}")
        print(f"Types : {', '.join(sorted(content_filter))}")

    run_index_extraction(
        args,
        prompt_builder=build_user_prompt,
        system_prompt=SYSTEM_PROMPT,
        parse_response=_parse_response,
        csv_prefix="match_index",
        raw_log_prefix="raw_responses",
        allowed_types=content_filter,
    )
