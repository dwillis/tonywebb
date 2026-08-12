"""Tests for config.Collection parsing and URL/filename generation."""

import pytest

from tonywebb import config
from tonywebb.config import Collection, DEFAULT_COLLECTION


def test_paddleocr_token_reads_env(monkeypatch):
    monkeypatch.setenv(config.PADDLEOCR_TOKEN_ENV, "secret-tok")
    assert config.paddleocr_token() == "secret-tok"


def test_paddleocr_token_missing_exits(monkeypatch):
    monkeypatch.delenv(config.PADDLEOCR_TOKEN_ENV, raising=False)
    with pytest.raises(SystemExit, match=config.PADDLEOCR_TOKEN_ENV):
        config.paddleocr_token()


FULL_URL = "https://archive.acscricket.com/research/tw/tw_newspaper_cuttings_1939/index.html"


def test_from_arg_full_url():
    c = Collection.from_arg(FULL_URL)
    assert c.slug == "tw_newspaper_cuttings_1939"
    assert c.season == "1939"


def test_from_arg_url_without_index_html():
    c = Collection.from_arg("https://archive.acscricket.com/research/tw/tw_newspaper_cuttings_1939/")
    assert c.slug == "tw_newspaper_cuttings_1939"


def test_from_arg_bare_slug():
    c = Collection.from_arg("tw_newspaper_cuttings_1939")
    assert c.season == "1939"


def test_from_arg_none_returns_default():
    assert Collection.from_arg(None) is DEFAULT_COLLECTION
    assert DEFAULT_COLLECTION.slug == "tw_newspaper_cuttings_1895"
    assert DEFAULT_COLLECTION.season == "1895"


def test_from_arg_rejects_unrelated_url():
    with pytest.raises(SystemExit):
        Collection.from_arg("https://example.com/whatever")


def test_from_arg_rejects_slug_without_year():
    with pytest.raises(SystemExit):
        Collection.from_arg("tw_newspaper_cuttings")


def test_page_url():
    c = Collection.from_arg(FULL_URL)
    assert c.page_url(3) == (
        "https://archive.acscricket.com/research/tw/tw_newspaper_cuttings_1939"
        "/files/assets/common/page-html5-substrates/page0003_5.jpg"
    )


def test_page_filename():
    c = Collection.from_arg(FULL_URL)
    assert c.page_filename(3) == "tw_newspaper_cuttings_1939_3.txt"


def test_default_collection_page_url_matches_legacy():
    from tonywebb import config
    assert DEFAULT_COLLECTION.page_url(7) == config.page_url(7)
