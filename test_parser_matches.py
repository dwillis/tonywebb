"""Tests for parser_matches.py — extraction, prompt building, and post-processing."""

import json

import pytest

from parser_matches import (
    VALID_CONTENT_TYPES,
    _parse_response,
    build_user_prompt,
    normalize_and_dedup,
    split_pages,
    JSONExtractError,
)


# ── Page splitting ─────────────────────────────────────────────────────────


class TestSplitPages:
    def test_basic_split(self):
        text = (
            "==========\nPAGE 1\n==========\n"
            "Content of page 1\n"
            "==========\nPAGE 2\n==========\n"
            "Content of page 2"
        )
        pages = split_pages(text)
        assert len(pages) == 2
        assert pages[0][0] == 1
        assert "Content of page 1" in pages[0][1]
        assert pages[1][0] == 2
        assert "Content of page 2" in pages[1][1]

    def test_no_pages(self):
        assert split_pages("Just some text") == []

    def test_single_page(self):
        text = "==========\nPAGE 42\n==========\nContent"
        pages = split_pages(text)
        assert len(pages) == 1
        assert pages[0][0] == 42


# ── Response parsing ───────────────────────────────────────────────────────


class TestParseResponse:
    def test_valid_json(self):
        raw = json.dumps({"entries": [
            {"title": "Team A v Team B", "date": "18950527", "content_type": "match information"}
        ]})
        entries = _parse_response(raw)
        assert len(entries) == 1
        assert entries[0]["matchup"] == "Team A v Team B"

    def test_title_renamed_to_matchup(self):
        raw = json.dumps({"entries": [{"title": "X v Y", "date": "18950527", "content_type": "match information"}]})
        entries = _parse_response(raw)
        assert "matchup" in entries[0]
        assert "title" not in entries[0]

    def test_matches_key_accepted(self):
        raw = json.dumps({"matches": [{"title": "X v Y", "content_type": "match information"}]})
        entries = _parse_response(raw)
        assert len(entries) == 1

    def test_invalid_content_type_defaults(self):
        raw = json.dumps({"entries": [{"title": "X v Y", "content_type": "invalid_type"}]})
        entries = _parse_response(raw)
        assert entries[0]["content_type"] == "match information"

    def test_strips_markdown_fences(self):
        raw = "```json\n" + json.dumps({"entries": [{"title": "A v B", "content_type": "match information"}]}) + "\n```"
        entries = _parse_response(raw)
        assert len(entries) == 1

    def test_invalid_json_raises(self):
        with pytest.raises(JSONExtractError, match="invalid JSON"):
            _parse_response("not json at all")

    def test_missing_entries_key_raises(self):
        with pytest.raises(JSONExtractError, match="missing"):
            _parse_response(json.dumps({"data": []}))

    def test_entries_not_list_raises(self):
        with pytest.raises(JSONExtractError, match="not a list"):
            _parse_response(json.dumps({"entries": "string"}))

    def test_response_not_object_raises(self):
        with pytest.raises(JSONExtractError, match="not a JSON object"):
            _parse_response(json.dumps([1, 2, 3]))


# ── Normalize and dedup ────────────────────────────────────────────────────


class TestNormalizeAndDedup:
    def test_basic_dedup(self):
        entries = [
            {"matchup": "Team A v Team B", "date": "18950527", "content_type": "match information"},
            {"matchup": "Team A v Team B", "date": "18950527", "content_type": "match information"},
        ]
        result = normalize_and_dedup(entries, page_num=1)
        assert len(result) == 1

    def test_different_dates_not_deduped(self):
        entries = [
            {"matchup": "Team A v Team B", "date": "18950527", "content_type": "match information"},
            {"matchup": "Team A v Team B", "date": "18950603", "content_type": "match information"},
        ]
        result = normalize_and_dedup(entries, page_num=1)
        assert len(result) == 2

    def test_content_type_filter(self):
        entries = [
            {"matchup": "Team A v Team B", "date": "18950527", "content_type": "match information"},
            {"title": "Reading School", "date": "18950527", "content_type": "statistics"},
        ]
        result = normalize_and_dedup(entries, page_num=1, allowed_types={"match information"})
        assert len(result) == 1
        assert result[0]["content_type"] == "match information"

    def test_collection_name_set(self):
        entries = [{"matchup": "A v B", "date": "18950527", "content_type": "match information"}]
        result = normalize_and_dedup(entries, page_num=5)
        assert result[0]["collection"] == "Tony Webb minor counties collection"
        assert result[0]["page"] == 5

    def test_empty_matchup_skipped(self):
        entries = [{"matchup": "", "date": "18950527", "content_type": "match information"}]
        result = normalize_and_dedup(entries, page_num=1)
        assert len(result) == 0

    def test_non_dict_entries_skipped(self):
        entries = ["not a dict", 42, None]
        result = normalize_and_dedup(entries, page_num=1)
        assert len(result) == 0

    def test_invalid_content_type_defaults_to_match(self):
        entries = [{"matchup": "A v B", "date": "18950527", "content_type": "bogus"}]
        result = normalize_and_dedup(entries, page_num=1)
        assert result[0]["content_type"] == "match information"


# ── Prompt building ────────────────────────────────────────────────────────


class TestBuildUserPrompt:
    def test_contains_page_number(self):
        prompt = build_user_prompt(42, "Some text")
        assert "page 42" in prompt.lower()

    def test_contains_1895_calendar(self):
        prompt = build_user_prompt(1, "Some text")
        assert "Whit-Monday" in prompt
        assert "27 May 1895" in prompt

    def test_contains_few_shot_examples(self):
        prompt = build_user_prompt(1, "Some text")
        assert "EXAMPLES OF CORRECT EXTRACTION" in prompt
        assert "18950527" in prompt

    def test_contains_anti_over_extraction_rules(self):
        prompt = build_user_prompt(1, "Some text")
        assert "fixture information" in prompt.lower()
        assert "2-8 entries" in prompt

    def test_contains_mr_dropping_hint(self):
        prompt = build_user_prompt(1, "Some text")
        assert "Mr" in prompt and "F Gentle" in prompt

    def test_contains_oc_dropping_hint(self):
        prompt = build_user_prompt(1, "Some text")
        assert "OC" in prompt

    def test_publication_date_detected(self):
        text = "SATURDAY 8 JUNE 1895\nCricket content"
        prompt = build_user_prompt(1, text)
        assert "1895-06-08" in prompt
        assert "Saturday" in prompt

    def test_publication_date_unknown(self):
        prompt = build_user_prompt(1, "No date here")
        assert "unknown" in prompt.lower()

    def test_page_text_included(self):
        prompt = build_user_prompt(1, "KENSWORTH v DUNSTABLE VICTORIA")
        assert "KENSWORTH v DUNSTABLE VICTORIA" in prompt


# ── Valid content types ────────────────────────────────────────────────────


class TestValidContentTypes:
    def test_match_information_is_valid(self):
        assert "match information" in VALID_CONTENT_TYPES

    def test_statistics_is_valid(self):
        assert "statistics" in VALID_CONTENT_TYPES

    def test_biography_is_valid(self):
        assert "biography" in VALID_CONTENT_TYPES

    def test_at_least_15_types(self):
        assert len(VALID_CONTENT_TYPES) >= 15
