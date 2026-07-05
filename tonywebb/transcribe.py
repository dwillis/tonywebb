"""
Cricket Newspaper Cuttings Transcription
==========================================
Fetches page images from the Tony Webb archive (or a local directory) and
sends each to a vision-capable LLM for verbatim transcription.

Two output modes:
  - Bulk (default): one .txt file per page in an output directory, resumable.
    Outputs: {output_dir}/tw_newspaper_cuttings_1895_{page}.txt
  - Concatenated (--output/-o): a single file (or stdout) with "PAGE N"
    separators, matching the full_text_output_*.txt format.
"""

import logging
import sys
import time
from pathlib import Path

import llm

from . import config
from .images import fetch_image, new_session
from .pipeline import parse_page_spec

logger = logging.getLogger(__name__)

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
    response = model.prompt(user_prompt, attachments=[attachment], system=SYSTEM_PROMPT)
    return response.text().strip()


def _transcribe_with_retry(model, page_num: int, image_bytes: bytes, media_type: str) -> str | None:
    text = None
    for attempt in range(1, config.TRANSCRIBE_RETRY_ATTEMPTS + 1):
        try:
            text = transcribe_page(model, page_num, image_bytes, media_type)
            break
        except Exception as e:
            print(f"  ⚠ Attempt {attempt}/{config.TRANSCRIBE_RETRY_ATTEMPTS} failed: {e}", file=sys.stderr)
            if attempt < config.TRANSCRIBE_RETRY_ATTEMPTS:
                time.sleep(config.TRANSCRIBE_RETRY_BACKOFF * attempt)
    return text


# ── CLI ──────────────────────────────────────────────────────────────────────

def register_parser(subparsers):
    p = subparsers.add_parser(
        "transcribe",
        help="Transcribe page images via a vision-capable LLM.",
    )
    p.add_argument("--model", default=config.DEFAULT_TRANSCRIBE_MODEL)
    p.add_argument(
        "--pages",
        default=None,
        help="Comma-separated page numbers or ranges, e.g. '1,3,5-10'. "
             "Overrides --start-page/--end-page.",
    )
    p.add_argument("--start-page", type=int, default=1)
    p.add_argument("--end-page", type=int, default=61)
    p.add_argument("--local-dir", default=None, help="Directory of local JPG files.")
    p.add_argument(
        "--output-dir", default=None,
        help="Directory for per-page .txt files (default: {model}/). Bulk mode.",
    )
    p.add_argument(
        "--output", "-o", default=None,
        help="Write a single concatenated file with PAGE markers here instead of "
             "per-page files (concatenated mode). Use '-' for stdout.",
    )
    p.set_defaults(func=run)
    return p


def run(args) -> None:
    local_dir = Path(args.local_dir) if args.local_dir else None
    page_filter = parse_page_spec(args.pages)
    if page_filter:
        page_nums = sorted(page_filter)
    else:
        page_nums = list(range(args.start_page, args.end_page + 1))

    model = llm.get_model(args.model)
    session = new_session()

    if args.output is not None:
        _run_concatenated(model, page_nums, local_dir, session, args.output)
    else:
        _run_bulk(model, page_nums, local_dir, session, args.output_dir or args.model)


def _run_bulk(model, page_nums: list[int], local_dir: Path | None, session, output_dir: str) -> None:
    out_dir = Path(output_dir)
    out_dir.mkdir(exist_ok=True)

    for page_num in page_nums:
        out_file = out_dir / f"tw_newspaper_cuttings_1895_{page_num}.txt"
        if out_file.exists() and out_file.stat().st_size > 0:
            print(f"Skipping page {page_num} (already exists)")
            continue

        print(f"Processing page {page_num}")
        try:
            image_bytes, media_type = fetch_image(page_num, local_dir=local_dir, session=session)
        except Exception as e:
            print(f"  ⚠ Could not fetch page {page_num}: {e}")
            continue

        text = _transcribe_with_retry(model, page_num, image_bytes, media_type)
        if text is None:
            print(f"  ✗ Skipping page {page_num} after {config.TRANSCRIBE_RETRY_ATTEMPTS} failed attempts")
            continue

        out_file.write_text(text, encoding="utf-8")
        print(f"  ✓ Saved {out_file}")
        time.sleep(config.RATE_LIMIT_DELAY)

    print(f"\nDone. Text files saved to {out_dir}/")


def _run_concatenated(model, page_nums: list[int], local_dir: Path | None, session, output: str) -> None:
    out_fh = sys.stdout if output == "-" else open(output, "w", encoding="utf-8")
    try:
        for i, page_num in enumerate(page_nums):
            print(f"Page {page_num} …", file=sys.stderr)
            try:
                image_bytes, media_type = fetch_image(page_num, local_dir=local_dir, session=session)
            except Exception as e:
                print(f"  ✗ Skipping page {page_num}: {e}", file=sys.stderr)
                continue

            text = _transcribe_with_retry(model, page_num, image_bytes, media_type)
            if text is None:
                print(f"  ✗ Skipping page {page_num} after {config.TRANSCRIBE_RETRY_ATTEMPTS} failed attempts.",
                      file=sys.stderr)
                continue

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

            if i < len(page_nums) - 1:
                time.sleep(config.RATE_LIMIT_DELAY)
    finally:
        if output != "-":
            out_fh.close()

    if output != "-":
        print(f"\nSaved to {output}", file=sys.stderr)
