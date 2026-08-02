"""Tests for llm_common.py — shared LLM response parsing helpers."""

import json

import llm
import pytest

from tonywebb.llm_common import JSONExtractError, no_thinking_kwargs, parse_json_object


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


class _FakeOllamaModel:
    model_id = "qwen3.5:397b-cloud"


class _FakeClaudeModel:
    model_id = "claude-haiku-4.5"


class _FakeOtherModel:
    model_id = "gpt-5.4"


class TestNoThinkingKwargs:
    def test_ollama_uses_think_false(self):
        model = _FakeOllamaModel()
        # Real llm-ollama model instances live in a module containing "ollama";
        # a bare object won't match that, so patch __module__ via a real class.
        model.__class__.__module__ = "llm_ollama"
        assert no_thinking_kwargs(model) == {"think": False}

    def test_claude_uses_thinking_false(self):
        assert no_thinking_kwargs(_FakeClaudeModel()) == {"thinking": False}

    def test_opus_sonnet_haiku_all_match(self):
        for model_id in ("claude-opus-5", "claude-sonnet-5", "claude-haiku-4.5"):
            model = _FakeClaudeModel()
            model.model_id = model_id
            assert no_thinking_kwargs(model) == {"thinking": False}

    def test_other_model_gets_no_kwargs(self):
        assert no_thinking_kwargs(_FakeOtherModel()) == {}

    def test_missing_model_id_gets_no_kwargs(self):
        assert no_thinking_kwargs(object()) == {}


class TestNoThinkingKwargsAgainstRealPlugin:
    """Regression coverage for the actual bug: llm-anthropic changed its
    Options schema from a bare budget_tokens=0 kwarg to a boolean `thinking`
    field, and the old kwarg now raises a pydantic validation error
    ("Extra inputs are not permitted") instead of silently disabling
    thinking. A fake model with no real Options validation can't catch that
    kind of plugin-version drift -- only validating against the actual
    installed plugin's schema can.

    Anthropic model instantiation needs no network call or API key (only
    .prompt() does), so this is safe to run in CI. An equivalent live check
    for llm-ollama isn't included -- llm-ollama's model registration calls
    out to a running Ollama daemon to list available models, which CI
    doesn't have.
    """

    def test_claude_kwargs_validate_against_installed_plugin(self):
        model = llm.get_model("claude-haiku-4.5")
        kwargs = no_thinking_kwargs(model)
        model.Options(**kwargs)  # raises pydantic.ValidationError if rejected
