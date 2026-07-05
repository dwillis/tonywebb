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
