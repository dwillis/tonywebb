"""Shared page-image fetching for transcription and scorecard vision recheck."""

from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from . import config


def new_session() -> requests.Session:
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


def fetch_image(
    page_num: int,
    local_dir: Path | None = None,
    session: requests.Session | None = None,
    collection: config.Collection = config.DEFAULT_COLLECTION,
) -> tuple[bytes, str]:
    """Download a page image and return (raw_bytes, media_type).

    If local_dir is given and a matching file exists, reads from disk instead.
    Retries up to 4 times with exponential backoff on connection errors.
    Raises requests.HTTPError on non-200 responses.
    """
    if local_dir is not None:
        local_file = local_dir / f"page{page_num:04d}_5.jpg"
        if local_file.exists():
            return local_file.read_bytes(), "image/jpeg"
    session = session or new_session()
    resp = session.get(collection.page_url(page_num), timeout=(60, 120))
    resp.raise_for_status()
    media_type = resp.headers.get("Content-Type", "image/jpeg").split(";")[0]
    return resp.content, media_type


def _page_exists(collection: config.Collection, session: requests.Session, page_num: int) -> bool:
    resp = session.head(collection.page_url(page_num), timeout=(30, 60))
    return resp.status_code == 200


def discover_page_count(
    collection: config.Collection, session: requests.Session | None = None
) -> int:
    """Find the collection's page count by probing image URLs.

    The archive returns 404 past the last page, so gallop upward (1, 2, 4, …)
    to bracket the last page, then binary-search inside the bracket.
    ~2*log2(n) HEAD requests (about 16 for a 250-page collection).
    """
    session = session or new_session()
    if not _page_exists(collection, session, 1):
        raise SystemExit(
            f"No pages found for {collection.slug} — is the collection URL right?"
        )
    lo, hi = 1, 2
    while _page_exists(collection, session, hi):
        lo, hi = hi, hi * 2
    # invariant: page lo exists, page hi does not
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if _page_exists(collection, session, mid):
            lo = mid
        else:
            hi = mid
    return lo
