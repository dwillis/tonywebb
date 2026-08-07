"""Tests for collection-aware image fetching and page-count discovery."""

from unittest.mock import MagicMock

from tonywebb.config import Collection
from tonywebb.images import discover_page_count, fetch_image

C1939 = Collection(slug="tw_newspaper_cuttings_1939", season="1939")


def _session_with_pages(last_page: int):
    """Fake session: HEAD/GET return 200 up to last_page, 404 after."""
    session = MagicMock()

    def _resp(url):
        import re
        page = int(re.search(r"page(\d{4})_5\.jpg", url).group(1))
        resp = MagicMock()
        resp.status_code = 200 if page <= last_page else 404
        resp.ok = page <= last_page
        resp.content = b"jpgbytes"
        resp.headers = {"Content-Type": "image/jpeg"}
        resp.raise_for_status = MagicMock(
            side_effect=None if page <= last_page else Exception("404")
        )
        return resp

    session.head.side_effect = lambda url, **kw: _resp(url)
    session.get.side_effect = lambda url, **kw: _resp(url)
    return session


def test_fetch_image_uses_collection_url():
    session = _session_with_pages(77)
    fetch_image(3, collection=C1939, session=session)
    url = session.get.call_args[0][0]
    assert "tw_newspaper_cuttings_1939" in url
    assert "page0003_5.jpg" in url


def test_discover_page_count_77():
    assert discover_page_count(C1939, session=_session_with_pages(77)) == 77


def test_discover_page_count_1():
    assert discover_page_count(C1939, session=_session_with_pages(1)) == 1


def test_discover_page_count_247():
    assert discover_page_count(C1939, session=_session_with_pages(247)) == 247


def test_discover_page_count_empty_collection():
    import pytest
    with pytest.raises(SystemExit):
        discover_page_count(C1939, session=_session_with_pages(0))
