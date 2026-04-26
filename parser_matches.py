"""
Cricket Match Extractor
========================
Reads pre-transcribed full text from a model output file, then sends each
page's text to an LLM to extract structured match information.

Usage:
    python parser_matches.py
    python parser_matches.py --model gpt-4o
    python parser_matches.py --input full_text_output_gemini31pro.txt --output match_index_new.csv

Outputs:
    match_index_<model>.csv  — one row per match found (post-normalized + deduped)
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
    detect_publication_date,
    matchup_key,
    normalize_date,
    normalize_matchup,
    relative_dates,
)

# ── Defaults ──────────────────────────────────────────────────────────────────

DEFAULT_INPUT_FILE = "full_text_output_gemini31pro.txt"
DEFAULT_MODEL_ID = "qwen3.5:397b-cloud"
COLLECTION_NAME = "Tony Webb minor counties collection"
CONTENT_TYPE = "match information"

RATE_LIMIT_DELAY = 1.5
RETRY_ATTEMPTS = 1  # one retry on transient errors (not on JSON parse errors)
RETRY_BACKOFF = 5.0

SYSTEM_PROMPT = (
    "You are an expert at reading historical cricket newspaper cuttings "
    "and extracting structured match information from them. "
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
Do not include player statistics or team statistics, only match reports.

For each distinct cricket match mentioned in the text, create an entry in
"matches" with:
  - "matchup": team names in the form "Team A v Team B" (use "v" with no period).
              * Use "XI" not "Eleven", and "Second XI" not "2nd XI".
              * Expand "G.S." or "G. S." to "Grammar School".
              * Drop trailing "C.C." from team names.
              * Keep "Mr.", "St.", and personal initials like "C.E.", "T.W."
              * Use title case.
              Examples: "Chalton v Houghton Second XI", "Waterlow's v East Finchley".
  - "date": match date as YYYYMMDD. Use "18950000" if only the year is clear,
            "18950800" if only the month is clear, "" if completely unknown.
  - "content_type": always "match information"
  - "collection": "Tony Webb minor counties collection"
  - "page": {page_num}

Return ONLY a JSON object with a single key "matches" (array). If no matches
are present, return {{"matches": []}}.

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
    if not isinstance(parsed, dict) or "matches" not in parsed:
        raise JSONExtractError("missing 'matches' key")
    matches = parsed.get("matches") or []
    if not isinstance(matches, list):
        raise JSONExtractError("'matches' is not a list")
    return matches


def extract_matches(model, page_num: int, page_text: str) -> tuple[list[dict], str]:
    """Returns (matches, raw_response_text). Raises JSONExtractError on bad shape."""
    prompt = build_user_prompt(page_num, page_text)
    response = model.prompt(prompt, system=SYSTEM_PROMPT)
    raw = response.text()
    return _parse_response(raw), raw


# ── Post-processing ──────────────────────────────────────────────────────────

def normalize_and_dedup(matches: list[dict], page_num: int) -> list[dict]:
    """Normalize matchup/date and drop duplicates within a page."""
    seen: set[tuple[str, str]] = set()
    out: list[dict] = []
    for m in matches:
        if not isinstance(m, dict):
            continue
        matchup = normalize_matchup(m.get("matchup", ""))
        date = normalize_date(m.get("date", ""))
        if not matchup:
            continue
        key = (matchup_key(matchup), date)
        if key in seen:
            continue
        seen.add(key)
        out.append(
            {
                "matchup": matchup,
                "page": page_num,
                "date": date,
                "content_type": CONTENT_TYPE,
                "collection": COLLECTION_NAME,
                "record_id": (m.get("record_id") or "").strip(),
            }
        )
    return out


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Extract cricket match records from pre-transcribed page text."
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
        raise SystemExit(f"Input file not found: {input_path}")

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

    print(f"Input : {input_path}")
    print(f"Model : {args.model}")
    print(f"Output: {csv_path}")
    print(f"Raw   : {raw_log_path}")

    full_text = input_path.read_text(encoding="utf-8")
    pages = split_pages(full_text)
    if not pages:
        raise SystemExit("No pages found. Check the PAGE separator format.")
    if page_filter:
        pages = [(n, t) for n, t in pages if n in page_filter]
        print(f"Pages : {sorted(page_filter)}")
    else:
        print(f"Pages : {len(pages)} total")

    model = llm.get_model(args.model)

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["matchup", "page", "date", "content_type", "collection", "record_id"])

    raw_log_path.write_text("", encoding="utf-8")

    total_matches = 0
    total_errors = 0

    for page_num, page_text in pages:
        print(f"  Processing page {page_num} …", end=" ", flush=True)
        matches: list[dict] | None = None
        raw = ""
        error: str | None = None

        try:
            for attempt in range(RETRY_ATTEMPTS + 1):
                try:
                    matches, raw = extract_matches(model, page_num, page_text)
                    break
                except JSONExtractError as e:
                    error = str(e)
                    matches = []
                    break  # don't retry — model output is the problem
                except Exception as e:  # transient API/network
                    error = str(e)
                    if attempt < RETRY_ATTEMPTS:
                        time.sleep(RETRY_BACKOFF)
                        continue
                    matches = []
                    break

            normalized = normalize_and_dedup(matches or [], page_num)

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
                total_matches += len(normalized)

            with raw_log_path.open("a", encoding="utf-8") as logf:
                logf.write(json.dumps({
                    "page": page_num,
                    "raw": raw,
                    "parsed_count": len(matches or []),
                    "kept_count": len(normalized),
                    "error": error,
                }, ensure_ascii=False) + "\n")

            if error:
                total_errors += 1
                print(f"ERROR: {error}")
            else:
                print(f"{len(normalized)} match(es)" if normalized else "no matches")
        finally:
            time.sleep(RATE_LIMIT_DELAY)

    print(f"\nDone. {total_matches} matches written to {csv_path}; {total_errors} page error(s).")


if __name__ == "__main__":
    main()
