"""Shared configuration for the Tony Webb indexing toolkit."""

import logging
import re
from dataclasses import dataclass

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


ARCHIVE_ROOT = "https://archive.acscricket.com/research/tw"

# Accepts a full collection URL (any path under the collection), a URL with a
# trailing slash, or a bare slug like "tw_newspaper_cuttings_1939".
_COLLECTION_ARG_RE = re.compile(
    r"^(?:https?://archive\.acscricket\.com/research/tw/)?"
    r"(?P<slug>tw_[a-z0-9_]+?)(?:/.*)?$"
)


@dataclass(frozen=True)
class Collection:
    """One Tony Webb FlippingBook collection (a single season's cuttings)."""

    slug: str    # e.g. "tw_newspaper_cuttings_1939"
    season: str  # e.g. "1939"

    @property
    def base_url(self) -> str:
        return f"{ARCHIVE_ROOT}/{self.slug}"

    def page_url(self, page_num: int) -> str:
        """Image URL for a page. Suffix _5 is the maximum resolution."""
        return (
            f"{self.base_url}/files/assets/common/page-html5-substrates/"
            f"page{page_num:04d}_5.jpg"
        )

    def page_filename(self, page_num: int) -> str:
        """Per-page transcription filename, e.g. tw_newspaper_cuttings_1939_3.txt."""
        return f"{self.slug}_{page_num}.txt"

    @classmethod
    def from_arg(cls, arg: str | None) -> "Collection":
        """Resolve a --collection value (URL or slug) to a Collection.

        None means the default 1895 collection, so every existing invocation
        keeps working unchanged.
        """
        if not arg:
            return DEFAULT_COLLECTION
        m = _COLLECTION_ARG_RE.match(arg.strip())
        if not m:
            raise SystemExit(
                f"Unrecognized collection {arg!r}. Expected a URL like "
                f"{ARCHIVE_ROOT}/tw_newspaper_cuttings_1939/index.html or a "
                f"slug like tw_newspaper_cuttings_1939."
            )
        slug = m.group("slug")
        year_m = re.search(r"(18|19|20)\d{2}", slug)
        if not year_m:
            raise SystemExit(
                f"Could not find a season year in collection slug {slug!r}."
            )
        return cls(slug=slug, season=year_m.group(0))


DEFAULT_COLLECTION = Collection(slug="tw_newspaper_cuttings_1895", season=SEASON)


def add_collection_arg(parser) -> None:
    """Attach the shared --collection flag to a subcommand parser."""
    parser.add_argument(
        "--collection",
        default=None,
        help="Collection URL or slug (e.g. "
             "https://archive.acscricket.com/research/tw/tw_newspaper_cuttings_1939/index.html). "
             "Default: the 1895 collection.",
    )


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
DEFAULT_RECONCILE_MODEL = "gemini/gemini-3.5-flash"
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
