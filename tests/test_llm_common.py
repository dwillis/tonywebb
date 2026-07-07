"""Tests for llm_common.py — shared LLM response parsing helpers."""

import json

import pytest

from tonywebb.llm_common import JSONExtractError, parse_json_object


class TestParseJsonObject:
    def test_plain_json(self):
        assert parse_json_object('{"entries": []}') == {"entries": []}

    def test_strips_markdown_fences(self):
        raw = "```json\n" + json.dumps({"teams": [1]}) + "\n```"
        assert parse_json_object(raw) == {"teams": [1]}

    def test_fence_without_language_tag(self):
        raw = "```\n{\"entries\": []}\n```"
        assert parse_json_object(raw) == {"entries": []}

    def test_preamble_before_fence(self):
        raw = 'Here is the JSON you asked for:\n```json\n{"entries": [{"title": "A v B"}]}\n```'
        assert parse_json_object(raw) == {"entries": [{"title": "A v B"}]}

    def test_preamble_without_fence(self):
        raw = 'Sure! The extracted data:\n{"entries": []}'
        assert parse_json_object(raw) == {"entries": []}

    def test_trailing_prose_after_object(self):
        raw = '{"entries": []}\nLet me know if you need anything else.'
        assert parse_json_object(raw) == {"entries": []}

    def test_nested_braces_in_strings(self):
        obj = {"entries": [{"title": "A {odd} name"}]}
        raw = "Result:\n" + json.dumps(obj) + "\nDone."
        assert parse_json_object(raw) == obj

    def test_invalid_json_raises(self):
        with pytest.raises(JSONExtractError, match="invalid JSON"):
            parse_json_object("not json at all")

    def test_non_object_raises(self):
        with pytest.raises(JSONExtractError, match="not a JSON object"):
            parse_json_object("[1, 2, 3]")

    def test_empty_string_raises(self):
        with pytest.raises(JSONExtractError):
            parse_json_object("")

    def test_raised_error_carries_raw_text(self):
        raw = "not json at all"
        with pytest.raises(JSONExtractError) as exc_info:
            parse_json_object(raw)
        assert exc_info.value.raw == raw

    def test_non_object_error_carries_raw_text(self):
        raw = "[1, 2, 3]"
        with pytest.raises(JSONExtractError) as exc_info:
            parse_json_object(raw)
        assert exc_info.value.raw == raw

    def test_reasoning_preamble_previews_entries_as_small_json_fragments(self):
        # Reproduces a real failure: glm-5.2:cloud "thinks out loud" before
        # answering, and that reasoning previews each entry as its own valid
        # JSON object (e.g. "1. {...}\n2. {...}") -- each of those parses
        # successfully on its own, so grabbing the FIRST valid object picks a
        # preview fragment instead of the real {"entries": [...]} payload.
        raw = (
            'Let me analyze this page.\n\n'
            '1. {"title": "Reading Cricket Week", "date": "18950800", "content_type": "season information"}\n'
            '2. {"title": "Reading v MCC", "date": "18950805", "content_type": "match information"}\n\n'
            'So the final answer is:\n```json\n'
            + json.dumps({"entries": [
                {"title": "Reading Cricket Week", "date": "18950800", "content_type": "season information"},
                {"title": "Reading v MCC", "date": "18950805", "content_type": "match information"},
            ]})
            + '\n```'
        )
        parsed = parse_json_object(raw)
        assert "entries" in parsed
        assert len(parsed["entries"]) == 2

    def test_prefers_largest_object_when_real_payload_appears_first(self):
        # The heuristic must not depend on the real payload being last --
        # a small preview fragment appearing AFTER the real payload (e.g. in
        # a trailing summary) must not win either.
        raw = (
            json.dumps({"entries": [{"title": "A v B"}, {"title": "C v D"}]})
            + '\nIn summary: {"title": "A v B"} was the first match.'
        )
        parsed = parse_json_object(raw)
        assert "entries" in parsed
        assert len(parsed["entries"]) == 2
