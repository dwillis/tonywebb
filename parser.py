"""
Cricket Newspaper Cuttings Scraper
===================================
Fetches page images from a FlippingBook archive, sends each page image to
Claude via the `llm` library, extracts full text, and indexes match
information into a CSV.

Setup:
    pip install llm llm-anthropic requests
    llm keys set anthropic        # paste your Anthropic API key

Usage:
    python cricket_scraper.py

Outputs:
    full_text_output.txt  — concatenated transcription text for all pages
    match_index.csv       — CSV with one row per match found

CSV format (matching your example):
    matchup, page, date, content_type, collection, record_id
    e.g. Penzance v. Helston,62,18950809,match information,Tony Webb minor counties collection,1
"""

import csv
import json
import re
import time
import requests
import llm
from pathlib import Path

# ── Configuration ─────────────────────────────────────────────────────────────

BASE_URL = (
    "https://archive.acscricket.com/research/tw/"
    "tw_newspaper_cuttings_1895/files/assets/common/page-html5-substrates/"
)

# Page range to process. Adjust as needed.
# The full collection runs pages 1–247; page 62 is the one you linked to.
START_PAGE = 1
END_PAGE = 61  # Inclusive. Change to 247 to process the full collection.

COLLECTION_NAME = "Tony Webb minor counties collection"
CONTENT_TYPE = "match information"
MODEL_ID = "gpt-5.4"  # Any llm-anthropic vision-capable model

OUTPUT_TEXT_FILE = "full_text_output.txt"
OUTPUT_CSV_FILE = "match_index.csv"

# Seconds to wait between API calls to avoid rate-limiting
RATE_LIMIT_DELAY = 1.5

SYSTEM_PROMPT = (
    "You are an expert at transcribing historical cricket newspaper cuttings "
    "and extracting structured match information from them. "
    "When asked, you will first provide a verbatim transcription of all text "
    "visible on the page, then extract a structured list of cricket matches "
    "mentioned. Respond ONLY with a JSON object — no markdown fences, no prose."
)

# ── Helpers ───────────────────────────────────────────────────────────────────

def page_url(page_num: int) -> str:
    """Return the image URL for a given page number. Suffix _5 is the maximum resolution."""
    return f"{BASE_URL}page{page_num:04d}_5.jpg"


def fetch_image(url: str) -> tuple[bytes, str]:
    """
    Download an image and return (raw_bytes, media_type).
    Raises requests.HTTPError on non-200 responses.
    """
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    media_type = resp.headers.get("Content-Type", "image/jpeg").split(";")[0]
    return resp.content, media_type


def extract_text_and_matches(model, page_num: int, image_bytes: bytes, media_type: str) -> dict:
    """
    Send the page image to Claude via llm and return a dict:
        {
            "full_text": str,
            "matches": [
                {
                    "matchup": "Penzance v. Helston",
                    "date": "18950809",   # YYYYMMDD; "18950000" if year only; "" if unknown
                    "content_type": "match information",
                    "collection": "Tony Webb minor counties collection",
                    "record_id": 1        # sequential within this page
                },
                ...
            ]
        }
    """
    user_prompt = f"""This is page {page_num} from the Tony Webb minor counties collection of
cricket newspaper cuttings (1895).

The date at the top of each page is the date of publication. References to
match days (e.g. "on Friday", "last Wednesday") are relative to that
publication date and therefore always prior to it.

1. Transcribe ALL visible text verbatim as the value of "full_text".
2. For each distinct cricket match mentioned, create an entry in "matches" with:
   - "matchup": team names in the form "Team A v. Team B"
   - "date": match date as YYYYMMDD (use "18950000" if only the year is clear,
             "18950800" if only month is clear, "" if completely unknown)
   - "content_type": always "match information"
   - "collection": "Tony Webb minor counties collection"
   - "page": page_num

Return ONLY a JSON object with keys "full_text" (string) and "matches" (array).
Example:
{{
  "full_text": "PENZANCE v. HELSTON\\nPlayed at Penzance on Friday...",
  "matches": [
    {{
      "matchup": "Penzance v. Helston",
      "date": "18950809",
      "content_type": "match information",
      "collection": "Tony Webb minor counties collection",
      "page_num": 62
    }}
  ]
}}"""

    attachment = llm.Attachment(content=image_bytes, type=media_type)
    response = model.prompt(user_prompt, attachments=[attachment], system=SYSTEM_PROMPT)
    raw = response.text().strip()

    # Strip markdown fences if the model adds them despite instructions
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    return json.loads(raw)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    model = llm.get_model(MODEL_ID)

    text_out = Path(OUTPUT_TEXT_FILE)
    csv_out = Path(OUTPUT_CSV_FILE)

    # Write CSV header
    with csv_out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["matchup", "page", "date", "content_type", "collection", "record_id"])

    with text_out.open("w", encoding="utf-8") as txt_f:

        for page_num in range(START_PAGE, END_PAGE + 1):
            url = page_url(page_num)
            print(f"Processing page {page_num}: {url}")

            # 1. Fetch image
            try:
                image_bytes, media_type = fetch_image(url)
            except requests.HTTPError as e:
                print(f"  ⚠ Could not fetch page {page_num}: {e}")
                continue

            # 2. Send to Claude via llm
            try:
                result = extract_text_and_matches(model, page_num, image_bytes, media_type)
            except Exception as e:
                print(f"  ⚠ Extraction failed for page {page_num}: {e}")
                continue

            # 3. Write full text
            txt_f.write(f"\n\n{'='*60}\nPAGE {page_num}\n{'='*60}\n")
            txt_f.write(result.get("full_text", ""))

            # 4. Write CSV rows
            matches = result.get("matches", [])
            if matches:
                with csv_out.open("a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    for match in matches:
                        writer.writerow([
                            match.get("matchup", ""),
                            page_num,
                            match.get("date", ""),
                            match.get("content_type", CONTENT_TYPE),
                            match.get("collection", COLLECTION_NAME),
                            match.get("record_id", ""),
                        ])
                print(f"  ✓ Found {len(matches)} match(es) on page {page_num}")
            else:
                print(f"  — No matches found on page {page_num}")

            time.sleep(RATE_LIMIT_DELAY)

    print(f"\nDone. Text saved to {OUTPUT_TEXT_FILE}, index saved to {OUTPUT_CSV_FILE}")


if __name__ == "__main__":
    main()