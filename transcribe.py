"""
Tony Webb Archive — Page Transcription
=======================================
Fetches one or more pages from the Tony Webb minor counties collection and
sends each image to a vision-capable LLM for verbatim transcription.

Usage:
    uv run python transcribe.py --pages 58
    uv run python transcribe.py --pages 58 59 60 --output pages_58_60.txt
    uv run python transcribe.py --pages 58 --model gpt-5.4

Outputs:
    Writes transcribed text to --output (default: stdout), in the same
    paginated format used by full_text_output_*.txt:

        ============================================================
        PAGE 58
        ============================================================
        <transcribed text>
"""

import argparse
import sys
import time
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import llm

# ── Defaults ──────────────────────────────────────────────────────────────────

DEFAULT_MODEL_ID = "qwen2.5vl"
RATE_LIMIT_DELAY = 1.5
RETRY_ATTEMPTS = 3
RETRY_BACKOFF = 5.0

BASE_JPG = (
    "https://archive.acscricket.com/research/tw/"
    "tw_newspaper_cuttings_1895/files/assets/common/page-html5-substrates/"
    "page{page:04d}_5.jpg"
)

SYSTEM_PROMPT = (
    "You are an expert at transcribing historical cricket newspaper cuttings. "
    "When asked, you provide a complete verbatim transcription of every word, "
    "figure, heading, and column visible on the page — starting at the top-left "
    "and working through every line to the bottom-right. You never stop early, "
    "never summarise, and never omit any text. "
    "CRITICAL: You must ONLY transcribe text that is physically present and visible "
    "in the image. Do NOT invent, generate, or assume any content from your training "
    "data. Every single word you write must appear verbatim in the image. If you "
    "cannot read a word clearly, write [unclear] rather than guessing."
)

# Warn if the response looks implausibly short for a full page
MIN_EXPECTED_CHARS = 500

PAGE_HEADER = "=" * 60 + "\nPAGE {page}\n" + "=" * 60


# ── Image fetching ────────────────────────────────────────────────────────────

def _session() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=4,
        connect=4,
        read=4,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


def fetch_image(page_num: int, session: requests.Session) -> tuple[bytes, str]:
    """Fetch the page image and return (image_bytes, media_type)."""
    url = BASE_JPG.format(page=page_num)
    resp = session.get(url, timeout=(30, 90))
    resp.raise_for_status()
    media_type = resp.headers.get("Content-Type", "image/jpeg").split(";")[0]
    print(f"  ↳ Fetched {len(resp.content):,} bytes: {url}", file=sys.stderr)
    return resp.content, media_type


# ── LLM transcription ─────────────────────────────────────────────────────────

def transcribe_page(model, page_num: int, image_bytes: bytes, media_type: str) -> str:
    """Send the page image to the model and return the verbatim transcription."""
    user_prompt = (
        f"This is page {page_num} from the Tony Webb minor counties collection "
        f"of cricket newspaper cuttings (1895).\n\n"
        f"Transcribe the COMPLETE text of the ENTIRE page exactly as it appears. "
        f"Start at the top-left corner and work through every heading, every column, "
        f"every player name, every figure, and every line of text all the way to the "
        f"bottom-right corner. Do not stop early, do not skip any section, do not summarise.\n\n"
        f"IMPORTANT: Transcribe ONLY what you can actually see in this image. "
        f"Do NOT use your knowledge of cricket history to fill in or invent any names, "
        f"scores, or statistics. If text is unclear or illegible, write [unclear]. "
        f"Return only the transcribed text with no additional commentary, "
        f"formatting, or markup.\n\n"
        f"NOTE on cricket averages: batting and bowling averages are decimal numbers, "
        f"for example '27.62' or '13.02' — not '27-62' or '13-02'. If you see a number "
        f"that looks like two parts separated by a period or dot in an averages column, "
        f"transcribe it with a decimal point."
    )
    if not image_bytes:
        raise ValueError(f"Page {page_num}: image_bytes is empty — nothing to transcribe")

    attachment = llm.Attachment(content=image_bytes, type=media_type)
    print(
        f"  ↳ Sending attachment: {len(image_bytes):,} bytes, type={media_type}",
        file=sys.stderr,
    )
    response = model.prompt(user_prompt, attachments=[attachment], system=SYSTEM_PROMPT)
    return response.text().strip()


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(
        description="Transcribe Tony Webb archive pages using a vision-capable LLM.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    ap.add_argument(
        "--pages",
        type=int,
        nargs="+",
        required=True,
        metavar="PAGE",
        help="One or more page numbers to transcribe.",
    )
    ap.add_argument(
        "--model",
        default=DEFAULT_MODEL_ID,
        help="LLM model ID (must support image attachments).",
    )
    ap.add_argument(
        "--output",
        default=None,
        metavar="FILE",
        help="Write transcribed text to FILE instead of stdout.",
    )
    args = ap.parse_args()

    model = llm.get_model(args.model)
    session = _session()

    out_fh = open(args.output, "w", encoding="utf-8") if args.output else sys.stdout

    try:
        for i, page_num in enumerate(args.pages):
            print(f"Page {page_num} …", file=sys.stderr)

            # 1. Fetch image
            try:
                image_bytes, media_type = fetch_image(page_num, session)
            except Exception as e:
                print(f"  ✗ Skipping page {page_num}: {e}", file=sys.stderr)
                continue

            # 2. Transcribe with retries
            text = None
            for attempt in range(1, RETRY_ATTEMPTS + 1):
                try:
                    text = transcribe_page(model, page_num, image_bytes, media_type)
                    break
                except Exception as e:
                    print(f"  ⚠ Attempt {attempt}/{RETRY_ATTEMPTS} failed: {e}",
                          file=sys.stderr)
                    if attempt < RETRY_ATTEMPTS:
                        time.sleep(RETRY_BACKOFF * attempt)
            if text is None:
                print(f"  ✗ Skipping page {page_num} after {RETRY_ATTEMPTS} failed attempts.",
                      file=sys.stderr)
                continue

            # 3. Write output
            header = PAGE_HEADER.format(page=page_num)
            if i > 0:
                out_fh.write("\n")
            out_fh.write(header + "\n")
            out_fh.write(text + "\n")
            out_fh.flush()

            if len(text) < MIN_EXPECTED_CHARS:
                print(
                    f"  ⚠ Page {page_num}: response looks short ({len(text):,} chars) — "
                    f"the model may have stopped early. Consider re-running.",
                    file=sys.stderr,
                )
            else:
                print(f"  ✓ Page {page_num} transcribed ({len(text):,} chars)", file=sys.stderr)

            if i < len(args.pages) - 1:
                time.sleep(RATE_LIMIT_DELAY)
    finally:
        if args.output:
            out_fh.close()

    if args.output:
        print(f"\nSaved to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
