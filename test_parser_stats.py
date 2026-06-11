"""Tests for parser_stats.py — player/team statistics normalization."""

import json

import pytest

from llm_common import JSONExtractError
from parser_stats import (
    _normalize_player,
    _normalize_team_entry,
    _parse_response,
    merge_teams,
)


# ── Response parsing ───────────────────────────────────────────────────────


class TestParseResponse:
    def test_valid_teams(self):
        raw = json.dumps({"teams": [{"name": "Reading", "players": []}]})
        assert len(_parse_response(raw)) == 1

    def test_empty_teams_list_is_valid(self):
        assert _parse_response(json.dumps({"teams": []})) == []

    def test_missing_teams_key_raises(self):
        with pytest.raises(JSONExtractError, match="missing"):
            _parse_response(json.dumps({"entries": []}))


# ── Player normalization ───────────────────────────────────────────────────


class TestNormalizePlayer:
    def test_basic_player(self):
        p = _normalize_player({"name": "J Smith", "batting": {"runs": 120}})
        assert p["name"] == "J Smith"
        assert p["batting"] == {"runs": 120}

    def test_empty_name_discarded(self):
        assert _normalize_player({"name": "", "batting": {"runs": 1}}) is None

    def test_numeric_strings_coerced(self):
        p = _normalize_player({"name": "J Smith", "batting": {"runs": "120", "average": "12.5"}})
        assert p["batting"]["runs"] == 120
        assert p["batting"]["average"] == 12.5

    def test_textual_stat_values_kept(self):
        # "57*" (not out) and "6-23" (best bowling) are legitimate values
        p = _normalize_player({
            "name": "J Smith",
            "batting": {"highest_score": "57*"},
            "bowling": {"best": "6-23"},
        })
        assert p["batting"]["highest_score"] == "57*"
        assert p["bowling"]["best"] == "6-23"

    def test_empty_and_none_values_dropped(self):
        p = _normalize_player({"name": "J Smith", "batting": {"runs": 10, "average": "", "innings": None}})
        assert p["batting"] == {"runs": 10}

    def test_container_values_dropped(self):
        p = _normalize_player({"name": "J Smith", "batting": {"runs": 10, "junk": {"a": 1}, "more": [1]}})
        assert p["batting"] == {"runs": 10}

    def test_stat_dict_empty_after_cleaning_omitted(self):
        p = _normalize_player({"name": "J Smith", "batting": {"runs": None}})
        assert "batting" not in p


# ── Team normalization & merging ───────────────────────────────────────────


class TestNormalizeTeamEntry:
    def test_basic_team(self):
        t = _normalize_team_entry({"name": "Reading", "players": [{"name": "J Smith"}]}, page_num=3)
        assert t["name"] == "Reading"
        assert t["page"] == 3
        assert len(t["players"]) == 1

    def test_duplicate_players_deduped(self):
        t = _normalize_team_entry(
            {"name": "Reading", "players": [{"name": "J Smith"}, {"name": "J Smith"}]},
            page_num=1,
        )
        assert len(t["players"]) == 1


class TestMergeTeams:
    def test_new_team_added(self):
        merged, added = merge_teams([], [{"name": "Reading", "players": []}], page_num=1)
        assert added == 1
        assert len(merged) == 1

    def test_same_team_records_extra_page(self):
        merged, _ = merge_teams([], [{"name": "Reading", "players": []}], page_num=1)
        merged, added = merge_teams(merged, [{"name": "Reading", "players": []}], page_num=5)
        assert added == 0
        assert merged[0]["pages_seen"] == [1, 5]
