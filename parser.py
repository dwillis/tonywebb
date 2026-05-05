"""
Cricket Newspaper Cuttings Scraper
===================================
Fetches page images from a FlippingBook archive, sends each page image to
the configured model via the `llm` library, and saves verbatim transcriptions
as per-page .txt files inside a model-named output directory.

Outputs:
    {MODEL_ID}/tw_newspaper_cuttings_1895_{page}.txt
"""

import argparse
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
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

DEFAULT_MODEL_ID = "gpt-5.4"

# Seconds to wait between API calls to avoid rate-limiting
RATE_LIMIT_DELAY = 1.5

SYSTEM_PROMPT = (
    "You are an expert at transcribing historical cricket newspaper cuttings."
    "When asked, you will provide a verbatim transcription of all text "
    "visible on the page."
)

# ── Helpers ───────────────────────────────────────────────────────────────────

def page_url(page_num: int) -> str:
    """Return the image URL for a given page number. Suffix _5 is the maximum resolution."""
    return f"{BASE_URL}page{page_num:04d}_5.jpg"


def fetch_image(url: str, local_dir: Path | None = None, page_num: int | None = None) -> tuple[bytes, str]:
    """
    Download an image and return (raw_bytes, media_type).
    If local_dir is given and a matching file exists, reads from disk instead.
    Retries up to 4 times with exponential backoff on connection errors.
    Raises requests.HTTPError on non-200 responses.
    """
    if local_dir and page_num is not None:
        local_file = local_dir / f"page{page_num:04d}_5.jpg"
        if local_file.exists():
            print(f"  → Using local file {local_file}")
            return local_file.read_bytes(), "image/jpeg"
    session = requests.Session()
    retry = Retry(
        total=4,
        connect=4,
        read=4,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    session.mount("https://", HTTPAdapter(max_retries=retry))
    resp = session.get(url, timeout=(60, 120))
    resp.raise_for_status()
    media_type = resp.headers.get("Content-Type", "image/jpeg").split(";")[0]
    return resp.content, media_type


def extract_text(model, page_num: int, image_bytes: bytes, media_type: str) -> str:
    """
    Send the page image to the model via llm and return the verbatim transcription.
    """
    user_prompt = f"""This is page {page_num} from the Tony Webb minor counties collection of
cricket newspaper cuttings (1895).

Transcribe ALL visible text verbatim. Return only the transcribed text with no
additional commentary, formatting, or markup."""

    attachment = llm.Attachment(content=image_bytes, type=media_type)
    response = model.prompt(user_prompt, attachments=[attachment], system=SYSTEM_PROMPT)
    return response.text().strip()


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Transcribe Tony Webb cricket newspaper cuttings using a vision-capable LLM.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL_ID,
        help="LLM model ID to use for transcription (must support image attachments).",
    )
    parser.add_argument(
        "--start-page",
        type=int,
        default=START_PAGE,
        help="First page number to process (inclusive).",
    )
    parser.add_argument(
        "--end-page",
        type=int,
        default=END_PAGE,
        help="Last page number to process (inclusive).",
    )
    parser.add_argument(
        "--local-dir",
        default=None,
        help="Directory of local JPG files to use instead of fetching from the URL.",
    )
    args = parser.parse_args()

    local_dir = Path(args.local_dir) if args.local_dir else None

    model = llm.get_model(args.model)

    output_dir = Path(args.model)
    output_dir.mkdir(exist_ok=True)

    for page_num in range(args.start_page, args.end_page + 1):
        out_file = output_dir / f"tw_newspaper_cuttings_1895_{page_num}.txt"
        if out_file.exists() and out_file.stat().st_size > 0:
            print(f"Skipping page {page_num} (already exists)")
            continue

        url = page_url(page_num)
        print(f"Processing page {page_num}: {url}")

        # 1. Fetch image
        try:
            image_bytes, media_type = fetch_image(url, local_dir=local_dir, page_num=page_num)
        except (requests.HTTPError, requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            print(f"  ⚠ Could not fetch page {page_num}: {e}")
            continue

        # 2. Send to model via llm (retry up to 3 times)
        full_text = None
        for attempt in range(1, 4):
            try:
                full_text = extract_text(model, page_num, image_bytes, media_type)
                break
            except Exception as e:
                print(f"  ⚠ Extraction attempt {attempt}/3 failed for page {page_num}: {e}")
                if attempt < 3:
                    time.sleep(5 * attempt)
        if full_text is None:
            print(f"  ✗ Skipping page {page_num} after 3 failed attempts")
            continue

        # 3. Write per-page text file
        out_file = output_dir / f"tw_newspaper_cuttings_1895_{page_num}.txt"
        out_file.write_text(full_text, encoding="utf-8")
        print(f"  ✓ Saved {out_file}")

        time.sleep(RATE_LIMIT_DELAY)

    print(f"\nDone. Text files saved to {output_dir}/")


if __name__ == "__main__":
    main()