"""Tests for transcribe.py — verbatim page transcription."""

import pytest

from tonywebb.transcribe import transcribe_page


class _FakeResponse:
    def __init__(self, text):
        self._text = text

    def text(self):
        return self._text


class _FakeModel:
    # no_thinking_kwargs() keys off model_id substrings (claude/opus/sonnet/haiku)
    # for non-Ollama modules, since it can't be told apart by module name here.
    model_id = "claude-sonnet-4.6"

    def __init__(self):
        self.calls = []
        self.prompts = []

    def prompt(self, *args, **kwargs):
        self.calls.append(kwargs)
        self.prompts.append(args[0] if args else "")
        return _FakeResponse("transcribed text")


class TestTranscribePage:
    def test_disables_thinking_like_extraction_commands(self):
        # Regression test: transcription used to be the only command that
        # didn't disable thinking, an asymmetry with every extraction command.
        model = _FakeModel()
        transcribe_page(model, 1, b"fake-bytes", "image/jpeg")
        assert model.calls[0].get("thinking") is False

    def test_empty_image_bytes_raises(self):
        model = _FakeModel()
        with pytest.raises(ValueError, match="empty"):
            transcribe_page(model, 1, b"", "image/jpeg")

    def test_returns_stripped_text(self):
        model = _FakeModel()
        result = transcribe_page(model, 1, b"fake-bytes", "image/jpeg")
        assert result == "transcribed text"

    def test_contains_two_column_side_by_side_rule(self):
        # Regression test: qwen3.5:397b's real page-1 transcription split
        # side-by-side two-column scorecards (one row per player, both
        # columns on the same printed line -- confirmed against the scan)
        # into two separate sequential lists instead. This happened for BOTH
        # shapes seen on that page: a team's 1st/2nd innings printed side by
        # side, and two different teams' batting printed side by side. Either
        # way it made reconciling against other runs (which kept the correct
        # layout) treat the entire scorecard as one giant dispute. The prompt
        # must say to keep both columns on one line in either case.
        model = _FakeModel()
        transcribe_page(model, 1, b"fake-bytes", "image/jpeg")
        prompt = model.prompts[0]
        assert "SIDE BY SIDE" in prompt
        assert "F. Dickens c Gladman .. .. 6    b Tompkins .. .. 0" in prompt
        assert "F. Love, b L Samm .. 12   E. Goodyear, b Darby .. 33" in prompt
        assert "Do NOT un-flatten" in prompt
