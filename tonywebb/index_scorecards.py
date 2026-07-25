"""
Scorecard Index Extractor
===========================
Reads pre-transcribed page text and asks an LLM to identify which match
reports include a full scorecard (batting lines with dismissals/runs, an
innings total) as opposed to a prose-only result. Emits ordinary
"match information" index rows -- the file itself, not a special
content_type, is what marks "these matches have scorecards", since the ACS
controlled vocabulary has no dedicated scorecard type.

This intentionally does NOT attempt to extract the scorecard's actual
batting/bowling figures (that was tried and abandoned -- see notes.md-era
extract-scorecards; on a full run, 613/786 extracted scorecards scored below
0.7 confidence because Victorian print quality and transcription noise make
figure-level extraction unreliable). This command only answers "does a
scorecard exist here", which is far more reliable.

Outputs:
    scorecard_index_<model>.csv                  — one row per match report with a scorecard
    raw_responses_scorecard_index_<model>.jsonl  — per-page raw LLM output for diagnostics
"""

from . import config
from .indexing import STYLE_RULES, build_date_context, run_index_extraction
from .llm_common import JSONExtractError, parse_json_object

SYSTEM_PROMPT = (
    "You are an expert at reading historical cricket newspaper cuttings and "
    "identifying which match reports include a full scorecard -- individual "
    "batting lines with how each batter was out and their runs, plus an "
    "innings total -- as opposed to a prose-only result with no figures. "
    "Respond ONLY with a JSON object — no markdown fences, no prose."
)


# ── Prompt building ──────────────────────────────────────────────────────────

def build_user_prompt(page_num: int, page_text: str) -> str:
    date_context = build_date_context(page_text)

    return f"""Below is the transcribed text of page {page_num} from the Tony Webb
minor counties collection of cricket newspaper cuttings (1895).

{date_context}
Find every match report on this page that includes a SCORECARD: a list of
individual batters with how each was out (e.g. "b Smith", "c Jones b Brown",
"run out", "not out") and their runs, together with an innings total (and
usually "Extras"). Bowling figures may appear as a table OR only in prose
(e.g. "Smith took five wickets for 20 runs") -- either counts as a
scorecard as long as the BATTING side has individual figures.

Do NOT include a match whose result is reported only in prose with no
individual batting figures (e.g. "Newbury beat Speen by 20 runs" with no
scorecard) -- that is a result, not a scorecard.

For each match report WITH a scorecard, create an entry in "entries" with:
  - "title": "Team A v Team B" (use "v" with no period)
  - "date_phrase": the VERBATIM text indicating when this was played (e.g.
    "on Whit-Monday", "on Saturday", "Friday in last week"), copied exactly
    as printed. This is resolved to a date deterministically in code, NOT
    by you -- do not compute a date yourself. Use "" if no date reference
    is present.
  - "date": your own best-effort YYYYMMDD guess, used only as a fallback if
    "date_phrase" can't be resolved. Use "18950000" if only the year is
    clear, "18950800" if only the month is clear, "" if completely unknown.
  - "content_type": "match information"
  - "collection": "Tony Webb minor counties collection"
  - "page": {page_num}

{STYLE_RULES}

RULES:
- If a match report's scorecard continues from a previous page (starts
  mid-scorecard with no match header), do NOT create a new entry for it —
  only entries for scorecards that BEGIN on this page.
- Do not create an entry for a match with no scorecard, even if it is
  otherwise a fully reported result.
- A typical page has 0-9 scorecards. If you find more than 12, reconsider
  whether you are splitting one match's scorecard into multiple entries.
- If no match report on this page has a scorecard, return {{"entries": []}}.

EXAMPLE — has a scorecard (include):
  "Dr. Stuart, b Tilley ... 0\\nA. Cuthinson, b Tilley ... 17\\n...
  Extras ... 6\\nTotal ... 45"
  → {{"title": "Roberts and Roberts v County Asylum", "date_phrase": "",
      "date": "18950616", "content_type": "match information"}}

EXAMPLE — no scorecard (exclude):
  "NEWBURY v SPEEN.--Newbury won by 20 runs."
  → no entry (prose result only, no individual batting figures)

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
            entry["content_type"] = "match information"
    return entries


# ── CLI ──────────────────────────────────────────────────────────────────────

def register_parser(subparsers):
    p = subparsers.add_parser(
        "index-scorecards",
        help="Index match reports that include a full batting/bowling scorecard.",
    )
    p.add_argument("--input", "-i", default=config.DEFAULT_TEXT_INPUT)
    p.add_argument("--model", "-m", default=config.DEFAULT_INDEX_SCORECARDS_MODEL)
    p.add_argument("--output", "-o", default=None)
    p.add_argument(
        "--pages",
        default=None,
        help="Comma-separated page numbers or ranges, e.g. '1,3,5-10'",
    )
    p.set_defaults(func=run)
    return p


def run(args) -> None:
    run_index_extraction(
        args,
        prompt_builder=build_user_prompt,
        system_prompt=SYSTEM_PROMPT,
        parse_response=_parse_response,
        csv_prefix="scorecard_index",
        raw_log_prefix="raw_responses_scorecard_index",
        allowed_types={"match information"},
    )
