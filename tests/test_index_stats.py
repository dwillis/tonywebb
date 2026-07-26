"""Tests for index_stats.py — the focused end-of-season-statistics index prompt/parser."""

import json
from pathlib import Path
from unittest import mock

import pytest

from tonywebb import cli, index_stats
from tonywebb.llm_common import JSONExtractError

FIXTURES = Path(__file__).parent / "fixtures"
PAGE_145 = (FIXTURES / "page_145.txt").read_text(encoding="utf-8")


# ── Prompt building ──────────────────────────────────────────────────────────

class TestBuildUserPrompt:
    def test_contains_page_number(self):
        prompt = index_stats.build_user_prompt(24, "Some text")
        assert "page 24" in prompt.lower()

    def test_player_statistics_title_format(self):
        prompt = index_stats.build_user_prompt(1, "Some text")
        assert "player statistics" in prompt

    def test_team_aggregates_title_format(self):
        prompt = index_stats.build_user_prompt(1, "Some text")
        assert "team aggregates" in prompt

    def test_one_entry_per_team_not_per_table_rule(self):
        prompt = index_stats.build_user_prompt(1, "Some text")
        assert "ONE entry" in prompt
        assert "1st XI" in prompt and "2nd XI" in prompt

    def test_abingdon_worked_example_present(self):
        # Matches the real page-24 pattern: 1st XI + 2nd XI, batting + bowling
        # tables, all covered by a single "Abingdon player statistics" entry.
        prompt = index_stats.build_user_prompt(1, "Some text")
        assert "Abingdon player statistics" in prompt

    def test_excludes_match_scorecards(self):
        prompt = index_stats.build_user_prompt(1, "Some text")
        assert "individual match scorecard" in prompt.lower()

    def test_season_long_date_convention(self):
        prompt = index_stats.build_user_prompt(1, "Some text")
        assert "18950000" in prompt

    def test_contains_1895_calendar(self):
        prompt = index_stats.build_user_prompt(1, "Some text")
        assert "Whit-Monday" in prompt

    def test_publication_date_detected(self):
        text = "SATURDAY 8 JUNE 1895\nCricket content"
        prompt = index_stats.build_user_prompt(1, text)
        assert "1895-06-08" in prompt

    def test_continuation_rule_present(self):
        prompt = index_stats.build_user_prompt(1, "text")
        assert "continues from a previous page" in prompt

    def test_page_text_included(self):
        prompt = index_stats.build_user_prompt(24, PAGE_145)
        assert "LEICESTER DAILY PRESS" in prompt


# ── Response parsing ───────────────────────────────────────────────────────

class TestParseResponse:
    def test_valid_json(self):
        raw = json.dumps({"entries": [{"title": "Newbury player statistics", "date": "18950000"}]})
        entries = index_stats._parse_response(raw)
        assert len(entries) == 1
        assert entries[0]["matchup"] == "Newbury player statistics"

    def test_content_type_forced_to_statistics(self):
        # Even if the model mislabels it, this focused command always tags
        # its own output as "statistics" -- that's the whole point of it.
        raw = json.dumps({"entries": [{"title": "Newbury player statistics", "content_type": "match information"}]})
        entries = index_stats._parse_response(raw)
        assert entries[0]["content_type"] == "statistics"

    def test_matches_key_accepted(self):
        raw = json.dumps({"matches": [{"title": "Speen player statistics"}]})
        entries = index_stats._parse_response(raw)
        assert len(entries) == 1

    def test_empty_entries_valid(self):
        assert index_stats._parse_response(json.dumps({"entries": []})) == []

    def test_missing_entries_key_raises(self):
        with pytest.raises(JSONExtractError, match="missing"):
            index_stats._parse_response(json.dumps({"data": []}))

    def test_entries_not_list_raises(self):
        with pytest.raises(JSONExtractError, match="not a list"):
            index_stats._parse_response(json.dumps({"entries": "nope"}))


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
    def test_writes_stats_index_csv(self, tmp_path, monkeypatch):
        input_dir = tmp_path / "pages"
        input_dir.mkdir()
        (input_dir / "tw_newspaper_cuttings_1895_24.txt").write_text("Abingdon averages page")

        fake_raw = json.dumps({"entries": [
            {"title": "Abingdon player statistics", "date": "18950000", "content_type": "statistics"},
        ]})
        fake_model = _FakeModel(fake_raw)

        monkeypatch.chdir(tmp_path)
        out_csv = tmp_path / "stats_index_fake-model.csv"
        with mock.patch("tonywebb.indexing.resolve_model", return_value=fake_model), \
             mock.patch("tonywebb.pipeline.time.sleep"):
            cli.main([
                "index-stats", "--input", str(input_dir), "--model", "fake-model",
                "--output", str(out_csv),
            ])

        rows = out_csv.read_text().strip().splitlines()
        assert rows[0] == "matchup,page,date,content_type,collection,pages"
        assert "Abingdon player statistics" in rows[1]
        assert ",statistics," in rows[1]
        assert fake_model.calls == 1

    def test_raw_log_written(self, tmp_path, monkeypatch):
        input_dir = tmp_path / "pages"
        input_dir.mkdir()
        (input_dir / "tw_newspaper_cuttings_1895_1.txt").write_text("no stats here")
        fake_model = _FakeModel(json.dumps({"entries": []}))

        monkeypatch.chdir(tmp_path)
        out_csv = tmp_path / "stats_index_fake-model.csv"
        with mock.patch("tonywebb.indexing.resolve_model", return_value=fake_model), \
             mock.patch("tonywebb.pipeline.time.sleep"):
            cli.main([
                "index-stats", "--input", str(input_dir), "--model", "fake-model",
                "--output", str(out_csv),
            ])

        raw_log = tmp_path / "raw_responses_stats_index_fake-model.jsonl"
        assert raw_log.exists()
