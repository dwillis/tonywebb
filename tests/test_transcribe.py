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


def test_transcribe_parser_accepts_collection_url():
    from tonywebb.cli import build_parser
    args = build_parser().parse_args([
        "transcribe",
        "--collection",
        "https://archive.acscricket.com/research/tw/tw_newspaper_cuttings_1939/index.html",
        "--pages", "1",
    ])
    assert args.collection.endswith("1939/index.html")


def test_user_prompt_mentions_collection_season():
    from tonywebb.transcribe import build_user_prompt
    prompt = build_user_prompt(page_num=3, season="1939")
    assert "1939" in prompt
    assert "1895" not in prompt


@pytest.mark.parametrize(
    "collection_arg, expected_dir",
    [
        # --collection omitted: from_arg(None) short-circuits to the
        # DEFAULT_COLLECTION singleton.
        (None, "gpt-5.4"),
        # --collection explicitly set to the default collection's slug/URL:
        # from_arg() constructs a NEW Collection instance here, == but not
        # `is` DEFAULT_COLLECTION -- regression test for that distinction.
        ("tw_newspaper_cuttings_1895", "gpt-5.4"),
        (
            "https://archive.acscricket.com/research/tw/tw_newspaper_cuttings_1895/index.html",
            "gpt-5.4",
        ),
        # A genuinely different collection still gets its own directory.
        ("tw_newspaper_cuttings_1939", "gpt-5.4-1939"),
    ],
)
def test_run_default_output_dir(monkeypatch, collection_arg, expected_dir):
    from tonywebb.cli import build_parser
    import tonywebb.transcribe as transcribe

    captured = {}

    def fake_run_bulk(model, page_nums, local_dir, session, output_dir, collection):
        captured["output_dir"] = output_dir

    monkeypatch.setattr(transcribe, "_run_bulk", fake_run_bulk)
    monkeypatch.setattr(transcribe.llm, "get_model", lambda name: object())
    monkeypatch.setattr(transcribe, "new_session", lambda: object())

    argv = ["transcribe", "--pages", "1"]
    if collection_arg is not None:
        argv += ["--collection", collection_arg]
    args = build_parser().parse_args(argv)

    transcribe.run(args)

    assert captured["output_dir"] == expected_dir
