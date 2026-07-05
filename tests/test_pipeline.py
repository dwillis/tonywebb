from pathlib import Path

import pytest

from tonywebb.llm_common import JSONExtractError
from tonywebb.pipeline import (
    PageResult,
    RawResponseLog,
    call_with_retry,
    load_pages,
    parse_page_spec,
    run_pages,
)


class TestParsePageSpec:
    def test_none_returns_none(self):
        assert parse_page_spec(None) is None

    def test_empty_returns_none(self):
        assert parse_page_spec("") is None

    def test_singles(self):
        assert parse_page_spec("1,3,5") == {1, 3, 5}

    def test_range(self):
        assert parse_page_spec("5-10") == {5, 6, 7, 8, 9, 10}

    def test_mixed(self):
        assert parse_page_spec("1,3,5-7") == {1, 3, 5, 6, 7}

    def test_whitespace_tolerant(self):
        assert parse_page_spec(" 1 , 3 , 5-7 ") == {1, 3, 5, 6, 7}


class TestLoadPages:
    def test_from_dir(self, tmp_path: Path):
        (tmp_path / "tw_newspaper_cuttings_1895_2.txt").write_text("page two")
        (tmp_path / "tw_newspaper_cuttings_1895_1.txt").write_text("page one")
        pages = load_pages(tmp_path)
        assert pages == [(1, "page one"), (2, "page two")]

    def test_from_dir_empty_raises(self, tmp_path: Path):
        with pytest.raises(SystemExit):
            load_pages(tmp_path)

    def test_from_concatenated_file(self, tmp_path: Path):
        f = tmp_path / "full.txt"
        f.write_text(
            "=" * 20 + "\nPAGE 1\n" + "=" * 20 + "\nfirst\n"
            + "=" * 20 + "\nPAGE 2\n" + "=" * 20 + "\nsecond\n"
        )
        pages = load_pages(f)
        assert pages == [(1, "first"), (2, "second")]

    def test_from_file_no_separators_raises(self, tmp_path: Path):
        f = tmp_path / "full.txt"
        f.write_text("no page markers here")
        with pytest.raises(SystemExit):
            load_pages(f)


class TestCallWithRetry:
    def test_success_first_try(self):
        result, error = call_with_retry(lambda: ("ok", "raw"))
        assert result == ("ok", "raw")
        assert error is None

    def test_json_extract_error_not_retried(self):
        calls = []

        def fn():
            calls.append(1)
            raise JSONExtractError("bad shape")

        result, error = call_with_retry(fn, attempts=3, backoff=0)
        assert result is None
        assert error == "bad shape"
        assert len(calls) == 1

    def test_transient_error_retried_once(self):
        calls = []

        def fn():
            calls.append(1)
            if len(calls) < 2:
                raise ConnectionError("network blip")
            return ("ok", "raw")

        result, error = call_with_retry(fn, attempts=1, backoff=0)
        assert result == ("ok", "raw")
        assert error is None
        assert len(calls) == 2

    def test_transient_error_exhausts_attempts(self):
        calls = []

        def fn():
            calls.append(1)
            raise ConnectionError("still down")

        result, error = call_with_retry(fn, attempts=1, backoff=0)
        assert result is None
        assert error == "still down"
        assert len(calls) == 2


class TestRawResponseLog:
    def test_round_trip(self, tmp_path: Path):
        import json

        log_path = tmp_path / "raw.jsonl"
        log = RawResponseLog(log_path)
        log.write(1, "raw one", parsed_count=2)
        log.write(2, "raw two", parsed_count=0, error="oops")

        lines = log_path.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 2
        rec1 = json.loads(lines[0])
        rec2 = json.loads(lines[1])
        assert rec1 == {"page": 1, "raw": "raw one", "parsed_count": 2}
        assert rec2 == {"page": 2, "raw": "raw two", "parsed_count": 0, "error": "oops"}


class TestRunPages:
    def test_skips_processed_pages(self):
        seen = []
        run_pages(
            [(1, "a"), (2, "b")],
            processed={1},
            extract_fn=lambda n, t: ([t], "raw"),
            on_result=lambda r: seen.append(r.page),
            rate_limit=0,
        )
        assert seen == [2]

    def test_passes_result_and_error(self):
        results: list[PageResult] = []

        def extract_fn(page_num, page_text):
            if page_num == 2:
                raise JSONExtractError("bad")
            return ([page_text], "raw")

        run_pages(
            [(1, "a"), (2, "b")],
            processed=set(),
            extract_fn=extract_fn,
            on_result=lambda r: results.append(r),
            rate_limit=0,
        )
        assert results[0].result == (["a"], "raw")
        assert results[0].error is None
        assert results[1].result is None
        assert results[1].error == "bad"
