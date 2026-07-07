"""Shared configuration for the Tony Webb indexing toolkit."""

import logging
import re

COLLECTION_NAME = "Tony Webb minor counties collection"
SEASON = "1895"
CLUBS_CSV_PATH = "clubs.csv"

BASE_JPG = (
    "https://archive.acscricket.com/research/tw/"
    "tw_newspaper_cuttings_1895/files/assets/common/page-html5-substrates/"
    "page{page:04d}_5.jpg"
)


def page_url(page_num: int) -> str:
    """Return the image URL for a given page number. Suffix _5 is the maximum resolution."""
    return BASE_JPG.format(page=page_num)


# Seconds to wait between API calls to avoid rate-limiting.
RATE_LIMIT_DELAY = 1.5

# One retry on transient errors (not on JSON parse errors, which mean the
# model's output was malformed rather than the call failing transiently).
RETRY_ATTEMPTS = 1
RETRY_BACKOFF = 5.0

# Transcription uses more retries since a single failed page is expensive to redo.
TRANSCRIBE_RETRY_ATTEMPTS = 3
TRANSCRIBE_RETRY_BACKOFF = 5.0

DEFAULT_TRANSCRIBE_MODEL = "gpt-5.4"
DEFAULT_EXTRACT_MATCHES_MODEL = "qwen3.5:397b-cloud"
DEFAULT_EXTRACT_STATS_MODEL = "qwen3.5:397b-cloud"
DEFAULT_INDEX_STATS_MODEL = "qwen3.5:397b-cloud"
DEFAULT_INDEX_SCORECARDS_MODEL = "qwen3.5:397b-cloud"

DEFAULT_TEXT_INPUT = "full_text_output_gemini31pro.txt"

VALID_CONTENT_TYPES = {
    "article",
    "award information",
    "biography",
    "fixture information",
    "ground information",
    "laws",
    "league information",
    "match information",
    "newspaper cuttings",
    "obituary",
    "organisation information",
    "photograph",
    "player information",
    "season information",
    "scorer information",
    "statistics",
    "team information",
    "tour information",
    "umpire information",
    "updates",
}


def safe_model_name(model_id: str) -> str:
    """Sanitize a model ID for use in filenames."""
    return re.sub(r"[^\w\-.]", "_", model_id)


def setup_logging(verbose: bool = False) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )
