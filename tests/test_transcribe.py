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

    def prompt(self, *args, **kwargs):
        self.calls.append(kwargs)
        return _FakeResponse("transcribed text")


class TestTranscribePage:
    def test_disables_thinking_like_extraction_commands(self):
        # Regression test: transcription used to be the only command that
        # didn't disable thinking, an asymmetry with every extraction command.
        model = _FakeModel()
        transcribe_page(model, 1, b"fake-bytes", "image/jpeg")
        assert model.calls[0].get("budget_tokens") == 0

    def test_empty_image_bytes_raises(self):
        model = _FakeModel()
        with pytest.raises(ValueError, match="empty"):
            transcribe_page(model, 1, b"", "image/jpeg")

    def test_returns_stripped_text(self):
        model = _FakeModel()
        result = transcribe_page(model, 1, b"fake-bytes", "image/jpeg")
        assert result == "transcribed text"
