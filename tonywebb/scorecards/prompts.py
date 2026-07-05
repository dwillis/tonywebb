"""Prompt construction for scorecard extraction (text pass and vision recheck pass)."""

import json

from ..normalize import detect_publication_date, relative_dates

SYSTEM_PROMPT = (
    "You are an expert at reading historical cricket scorecards from Victorian "
    "newspaper cuttings and extracting them into structured JSON. You accurately "
    "capture every batter's dismissal, the bowler and fielder involved, runs "
    "scored, extras, and innings totals, as well as bowling figures -- including "
    "figures given only in prose (e.g. 'Tilley took five wickets for 12 runs'). "
    "Respond ONLY with a JSON object — no markdown fences, no prose."
)

RECHECK_SYSTEM_PROMPT = (
    "You are an expert at reading historical cricket scorecards from Victorian "
    "newspaper page images. You correct a prior text-based extraction by "
    "comparing it against the actual page image, changing only what the image "
    "contradicts. You never invent figures that are illegible in the image. "
    "Respond ONLY with a JSON object — no markdown fences, no prose."
)


def build_text_prompt(page_num: int, page_text: str) -> str:
    pub = detect_publication_date(page_text)
    if pub:
        rel = relative_dates(pub)
        rel_lines = "\n".join(f"  {wd.capitalize()}: {iso}" for wd, iso in rel.items())
        date_context = (
            f"PUBLICATION DATE: {pub.isoformat()} ({pub.strftime('%A')})\n"
            "Resolve relative weekday references the same way match dates are "
            "resolved elsewhere in this collection:\n"
            f"{rel_lines}\n"
        )
    else:
        date_context = "PUBLICATION DATE: unknown — extract dates only when stated explicitly.\n"

    return f"""Below is the transcribed text of page {page_num} from the Tony Webb
minor counties collection of cricket newspaper cuttings (1895).

{date_context}
Extract the full SCORECARD (batting and bowling figures) for every match report
that BEGINS on this page. If a match report continues from a previous page
(starts mid-scorecard, no header), skip it — only extract scorecards that
begin here.

Return a JSON object with a single key "scorecards" — an array, one element
per match, each with:

  - "matchup": "Team A v Team B" (same style as the match index: no periods
    in abbreviations, drop trailing CC/Cricket Club, title case).
  - "date": YYYYMMDD, or "" if unknown. Use the same date-resolution rules
    as match extraction (publication date, weekday references, holidays).
  - "venue": short verbatim description if given (e.g. "On the Asylum
    Grounds"), else null.
  - "result": a short verbatim result note if explicitly stated, else null.
  - "innings": an array, one element per completed innings, in the order
    they were played:
      - "team": the batting team's name for this innings.
      - "order": 1 for the first innings shown, 2 for the second, etc.
      - "batting": array of batting lines, each with:
          - "batter": name, honorifics kept but no periods ("Dr Stuart" not
            "Dr. Stuart"), drop trailing "Esq"/"Esq." ("W Moore" not
            "W Moore, Esq.").
          - "dismissal": one of "b", "c", "c and b", "st", "run out", "lbw",
            "hit wicket", "retired", "absent", "not out", "unknown".
          - "bowler": the bowler's name if the dismissal credits one
            (b/c/c and b/st/lbw/hit wicket), else null.
          - "fielder": the fielder's name for "c" or "st" dismissals, else
            null.
          - "runs": integer runs scored, or null if the figure is illegible
            or missing. NEVER invent or guess a number.
          - "not_out": true if the batter was not out.
          - "raw": the verbatim source line for this batter, copied exactly
            as transcribed (this is the human-review reference — always
            include it).
      - "did_not_bat": array of names listed as not batting (e.g. from
        "Others did not bat" or a named list), else [].
      - "extras": integer extras total for the innings, or null.
      - "total": integer innings total, or null.
      - "total_qualifier": verbatim qualifier if given (e.g. "for 5 wickets",
        "innings declared closed"), else null.
      - "bowling": array of bowling figures for the OPPOSING team's bowlers
        in this innings, each with:
          - "bowler": name.
          - "overs": overs bowled AS A STRING exactly as printed (e.g.
            "10.2"), or null if not given.
          - "maidens": integer, or null.
          - "runs": integer runs conceded, or null.
          - "wickets": integer wickets taken, or null.
          - "source": "table" if from a bowling-figures table/column, or
            "prose" if only mentioned in a sentence (e.g. "Tilley took five
            wickets for 12 runs" — convert spelled-out numbers to digits).
          - "raw": the verbatim source line or sentence.

RULES:
- NEVER invent or guess a number. If a figure is illegible, garbled, or
  missing, use null for that field rather than guessing.
- Every batting and bowling line MUST include "raw" — the verbatim source
  text it was extracted from.
- If bowling figures for an innings are only given in prose (not a table),
  still create bowling entries with "source": "prose", using null for any
  figure (overs, maidens) not stated in the prose.
- If a page has no scorecards beginning on it, return {{"scorecards": []}}.

PAGE {page_num} TEXT:
{page_text}"""


def build_recheck_prompt(page_num: int, scorecard: dict, flags: list[str]) -> str:
    flags_text = ", ".join(flags) if flags else "low confidence"
    scorecard_json = json.dumps(scorecard, indent=2, ensure_ascii=False)
    return f"""This is page {page_num} from the Tony Webb minor counties collection of
cricket newspaper cuttings (1895), shown as an image.

A previous text-only extraction produced this scorecard, which was flagged
for review ({flags_text}):

{scorecard_json}

Look at the IMAGE and correct ONLY the fields that are contradicted by what
you can actually see on the page. Do not change fields that are already
correct. Do not invent figures that are illegible in the image — use null.
Preserve the same JSON shape (same keys, same structure) as the scorecard
above, including "match_key", "venue", "result", and "innings".

Return a JSON object with a single key "scorecard" containing the corrected
object."""
