"""Tests for index_scorecards.py — the scorecard-presence index prompt/parser."""

import json
from pathlib import Path
from unittest import mock

import pytest

from tonywebb import cli, index_scorecards
from tonywebb.llm_common import JSONExtractError

FIXTURES = Path(__file__).parent / "fixtures"
PAGE_145 = (FIXTURES / "page_145.txt").read_text(encoding="utf-8")


# ── Prompt building ──────────────────────────────────────────────────────────

class TestBuildUserPrompt:
    def test_contains_page_number(self):
        prompt = index_scorecards.build_user_prompt(145, "Some text")
        assert "page 145" in prompt.lower()

    def test_matchup_title_format(self):
        prompt = index_scorecards.build_user_prompt(1, "Some text")
        assert '"Team A v Team B"' in prompt

    def test_scorecard_presence_criteria_present(self):
        prompt = index_scorecards.build_user_prompt(1, "Some text")
        assert "how each was out" in prompt or "individual batting figures" in prompt

    def test_prose_only_result_excluded(self):
        prompt = index_scorecards.build_user_prompt(1, "Some text")
        assert "prose" in prompt.lower()
        assert "not a scorecard" in prompt.lower() or "no entry" in prompt.lower()

    def test_worked_examples_present(self):
        prompt = index_scorecards.build_user_prompt(145, PAGE_145)
        assert "Roberts and Roberts v County Asylum" in prompt
        assert "NEWBURY" in prompt or "no scorecard" in prompt.lower()

    def test_continuation_rule_present(self):
        prompt = index_scorecards.build_user_prompt(1, "text")
        assert "continues from a previous page" in prompt

    def test_contains_whit_monday_example(self):
        prompt = index_scorecards.build_user_prompt(1, "Some text")
        assert "Whit-Monday" in prompt

    def test_contains_date_phrase_field(self):
        # Date resolution moved to deterministic Python code (resolve_date_phrase) --
        # the model is asked to quote the verbatim phrase, not compute a date itself.
        prompt = index_scorecards.build_user_prompt(1, "Some text")
        assert "date_phrase" in prompt
        assert "do not compute a date yourself" in prompt.lower()

    def test_publication_date_detected(self):
        prompt = index_scorecards.build_user_prompt(145, PAGE_145)
        assert "PUBLICATION DATE: 1895-06-17" in prompt

    def test_page_text_included(self):
        prompt = index_scorecards.build_user_prompt(145, PAGE_145)
        assert "ROBERTS and ROBERTS" in prompt


# ── Response parsing ───────────────────────────────────────────────────────

class TestParseResponse:
    def test_valid_json(self):
        raw = json.dumps({"entries": [{"title": "Roberts and Roberts v County Asylum", "date": "18950616"}]})
        entries = index_scorecards._parse_response(raw)
        assert len(entries) == 1
        assert entries[0]["matchup"] == "Roberts and Roberts v County Asylum"

    def test_content_type_forced_to_match_information(self):
        raw = json.dumps({"entries": [{"title": "A v B", "content_type": "statistics"}]})
        entries = index_scorecards._parse_response(raw)
        assert entries[0]["content_type"] == "match information"

    def test_matches_key_accepted(self):
        raw = json.dumps({"matches": [{"title": "A v B"}]})
        entries = index_scorecards._parse_response(raw)
        assert len(entries) == 1

    def test_empty_entries_valid(self):
        assert index_scorecards._parse_response(json.dumps({"entries": []})) == []

    def test_missing_entries_key_raises(self):
        with pytest.raises(JSONExtractError, match="missing"):
            index_scorecards._parse_response(json.dumps({"data": []}))

    def test_entries_not_list_raises(self):
        with pytest.raises(JSONExtractError, match="not a list"):
            index_scorecards._parse_response(json.dumps({"entries": "nope"}))


# ── End-to-end (fake model) ─────────────────────────────────────────────────

class _FakeResponse:
    def __init__(self, text):
        self._text = text

    def text(self):
        return self._text


class _FakeModel:
    model_id = "fake-model"

    def __init__(self, raw_text):
        self.raw_text = raw_text
        self.calls = 0

    def prompt(self, *a, **k):
        self.calls += 1
        return _FakeResponse(self.raw_text)


class TestEndToEnd:
    def test_writes_scorecard_index_csv(self, tmp_path, monkeypatch):
        input_dir = tmp_path / "pages"
        input_dir.mkdir()
        (input_dir / "tw_newspaper_cuttings_1895_145.txt").write_text(PAGE_145)

        fake_raw = json.dumps({"entries": [
            {"title": "Roberts and Roberts v County Asylum", "date": "18950616", "content_type": "match information"},
            {"title": "Lansdowne United v Granby", "date": "18950616", "content_type": "match information"},
        ]})
        fake_model = _FakeModel(fake_raw)

        monkeypatch.chdir(tmp_path)
        out_csv = tmp_path / "scorecard_index_fake-model.csv"
        with mock.patch("tonywebb.indexing.resolve_model", return_value=fake_model), \
             mock.patch("tonywebb.pipeline.time.sleep"):
            cli.main([
                "index-scorecards", "--input", str(input_dir), "--model", "fake-model",
                "--output", str(out_csv),
            ])

        rows = out_csv.read_text().strip().splitlines()
        assert rows[0] == "matchup,page,date,content_type,collection,record_id"
        assert len(rows) == 3  # header + 2 entries
        assert all(",match information," in r for r in rows[1:])
        assert fake_model.calls == 1

    def test_raw_log_written(self, tmp_path, monkeypatch):
        input_dir = tmp_path / "pages"
        input_dir.mkdir()
        (input_dir / "tw_newspaper_cuttings_1895_1.txt").write_text("no scorecards here")
        fake_model = _FakeModel(json.dumps({"entries": []}))

        monkeypatch.chdir(tmp_path)
        out_csv = tmp_path / "scorecard_index_fake-model.csv"
        with mock.patch("tonywebb.indexing.resolve_model", return_value=fake_model), \
             mock.patch("tonywebb.pipeline.time.sleep"):
            cli.main([
                "index-scorecards", "--input", str(input_dir), "--model", "fake-model",
                "--output", str(out_csv),
            ])

        raw_log = tmp_path / "raw_responses_scorecard_index_fake-model.jsonl"
        assert raw_log.exists()
