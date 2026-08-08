"""
Statistics Index Extractor
============================
Reads pre-transcribed page text and asks an LLM to find end-of-season
batting/bowling averages tables, emitting one index entry per team per page
(the ACS/Willis convention -- NOT one entry per individual table, even when
a team has separate 1st XI / 2nd XI, or separate batting/bowling, tables).

This is a focused counterpart to extract-matches' general 18-type prompt:
a single-purpose prompt that only hunts for statistics tables should have
higher recall on this content type than the general pass.

Outputs:
    stats_index_<model>.csv                  — one row per team-with-statistics found
    raw_responses_stats_index_<model>.jsonl  — per-page raw LLM output for diagnostics
"""

from . import config
from .indexing import STYLE_RULES, build_date_context, key_dates_block, run_index_extraction
from .llm_common import JSONExtractError, parse_json_object

SYSTEM_PROMPT = (
    "You are an expert at reading historical cricket newspaper cuttings and "
    "identifying end-of-season batting/bowling averages tables. You "
    "distinguish these season-long summary tables from individual match "
    "scorecards, and you group every table belonging to the same team "
    "(1st XI, 2nd XI, batting, bowling) into a single index entry for that "
    "team. Respond ONLY with a JSON object — no markdown fences, no prose."
)


# ── Prompt building ──────────────────────────────────────────────────────────

def build_user_prompt(page_num: int, page_text: str, season: str = config.SEASON) -> str:
    date_context = build_date_context(page_text)

    return f"""Below is the transcribed text of page {page_num} from the Tony Webb
minor counties collection of cricket newspaper cuttings ({season}).

{date_context}
Find every END-OF-SEASON AVERAGES TABLE on this page — batting averages,
bowling averages, or aggregate team figures for a club's season. These are
SUMMARY tables listing multiple players with season-long totals, NOT
individual match scorecards.

For each team that has at least one such table, create ONE entry in
"entries" — even if that team has several separate tables (e.g. a 1st XI
table AND a 2nd XI table, or a batting table AND a bowling table, are ALL
covered by a single entry for that team):
  - "title": "Team Name player statistics" (drop trailing CC/Cricket Club,
    use county names as used today, title case)
  - "date": as YYYYMMDD. Averages tables are usually undated (season-long) —
    use "{season}0000" unless the text ties the table to a specific month, in
    which case use month precision (e.g. "{season}0800"). Do not guess a day.
  - "content_type": "statistics"
  - "collection": "Tony Webb minor counties collection"
  - "page": {page_num}

If the SAME team ALSO has separate AGGREGATE TEAM figures on this page
(e.g. total runs scored for/against as a team, matches played/won/lost/drawn
as a team, rather than per-player figures), create a SECOND entry:
  - "title": "Team Name team aggregates"
  - same date/content_type/collection/page rules as above

{STYLE_RULES}

{key_dates_block(season)}

RULES:
- Do NOT create an entry for an individual match scorecard (a report of one
  specific match, with batting/bowling figures for just that match). Those
  are "match information", not "statistics" — skip them entirely here.
- Do NOT create an entry for upcoming/unplayed fixture lists.
- Exactly one "Team Name player statistics" entry per team per page, no
  matter how many separate tables (1st XI, 2nd XI, batting, bowling) that
  team has on the page.
- If a table continues from a previous page with no header, do NOT create
  a new entry for it — only entries for tables that BEGIN on this page.
- If no averages tables are found on this page, return {{"entries": []}}.

EXAMPLE:
  A page with an "Abingdon Cricket and Football Club" season summary,
  followed by separate "BATTING AVERAGES" and "BOWLING AVERAGES" tables for
  the 1st XI, and then another pair of batting/bowling tables for "THE
  SECOND ELEVEN", is still just ONE entry:
  {{"title": "Abingdon player statistics", "date": "{season}0000",
    "content_type": "statistics"}}

Return ONLY a JSON object with a single key "entries" (array).

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
            entry["content_type"] = "statistics"
    return entries


# ── CLI ──────────────────────────────────────────────────────────────────────

def register_parser(subparsers):
    p = subparsers.add_parser(
        "index-stats",
        help="Index pages containing end-of-season player/team statistics tables.",
    )
    p.add_argument("--input", "-i", default=config.DEFAULT_TEXT_INPUT)
    p.add_argument("--model", "-m", default=config.DEFAULT_INDEX_STATS_MODEL)
    p.add_argument("--output", "-o", default=None)
    config.add_collection_arg(p)
    p.add_argument(
        "--pages",
        default=None,
        help="Comma-separated page numbers or ranges, e.g. '1,3,5-10'",
    )
    p.set_defaults(func=run)
    return p


def run(args) -> None:
    collection = config.Collection.from_arg(args.collection)

    run_index_extraction(
        args,
        prompt_builder=lambda n, t: build_user_prompt(n, t, season=collection.season),
        system_prompt=SYSTEM_PROMPT,
        parse_response=_parse_response,
        csv_prefix="stats_index",
        raw_log_prefix="raw_responses_stats_index",
        allowed_types={"statistics"},
    )
