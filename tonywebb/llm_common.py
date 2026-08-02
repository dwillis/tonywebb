"""Shared helpers for the LLM extraction commands (extract_matches, extract_stats, scorecards)."""

import json
import re
from pathlib import Path


class JSONExtractError(Exception):
    """Raised when the model's response can't be parsed as the expected JSON shape.

    Carries the raw response text (even though parsing failed) so callers can
    still log it for diagnostics and can distinguish an empty response (likely
    a transient generation glitch, worth a retry) from a non-empty malformed
    one (likely a real prompt/model problem, not worth retrying).
    """

    def __init__(self, message: str, raw: str = ""):
        super().__init__(message)
        self.raw = raw


def _strip_fences(text: str) -> str:
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text


def parse_json_object(raw: str) -> dict:
    """Parse a model response as a JSON object.

    Tolerates markdown fences, preamble prose before the object, and trailing
    prose after it. Raises JSONExtractError if no JSON object can be found.
    """
    text = _strip_fences(raw.strip())
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as e:
        try:
            parsed = _first_json_object(text, e)
        except JSONExtractError as inner:
            inner.raw = raw
            raise
    if not isinstance(parsed, dict):
        raise JSONExtractError("response is not a JSON object", raw=raw)
    return parsed


def _first_json_object(text: str, original_error: json.JSONDecodeError) -> dict:
    """Decode the JSON object embedded in surrounding prose.

    Reasoning models sometimes think out loud before emitting the real
    payload, and that reasoning often previews individual entries as small,
    independently-valid JSON fragments (e.g. '1. {"title": "...", ...}\\n2.
    {"title": "...", ...}') before the actual answer. Picking the FIRST
    successfully-parsed object risks grabbing one of those preview fragments
    instead of the real one. Instead, try every '{' position and keep
    whichever object consumes the most characters from its own start point --
    the real payload wraps everything else, so it is virtually always the
    largest self-contained object in the response, regardless of where in
    the text it appears.
    """
    decoder = json.JSONDecoder()
    best: dict | None = None
    best_span = -1
    idx = text.find("{")
    while idx != -1:
        candidate = _strip_fences(text[idx:].strip())
        try:
            parsed, end = decoder.raw_decode(candidate)
        except json.JSONDecodeError:
            idx = text.find("{", idx + 1)
            continue
        if isinstance(parsed, dict) and end > best_span:
            best, best_span = parsed, end
        idx = text.find("{", idx + 1)
    if best is not None:
        return best
    raise JSONExtractError(f"invalid JSON: {original_error}") from original_error


def no_thinking_kwargs(model) -> dict:
    """Return prompt kwargs that disable thinking for models that support it."""
    model_id: str = getattr(model, "model_id", "") or ""
    model_type = type(model).__module__ or ""
    if "ollama" in model_type:
        # llm-ollama exposes thinking as `think`
        return {"think": False}
    if any(x in model_id.lower() for x in ("claude", "opus", "sonnet", "haiku")):
        # Anthropic extended thinking: current llm-anthropic (0.25+) disables
        # it via a boolean `thinking` option. An older plugin version used a
        # bare `budget_tokens=0` kwarg -- that field no longer exists on
        # ClaudeOptionsWithThinking and now raises a pydantic validation
        # error ("Extra inputs are not permitted") instead of silently
        # disabling thinking.
        return {"thinking": False}
    return {}


def load_pages_from_dir(directory: Path) -> list[tuple[int, str]]:
    """Load per-page .txt files from a directory, sorted by page number."""
    pages = []
    for f in directory.glob("*.txt"):
        m = re.search(r"_(\d+)\.txt$", f.name)
        if m:
            pages.append((int(m.group(1)), f.read_text(encoding="utf-8").strip()))
    return sorted(pages, key=lambda x: x[0])


# ── Concatenated-file page splitting ─────────────────────────────────────────
# Used when the input is a single file with "PAGE N" separators
# (e.g. full_text_output_*.txt) rather than a directory of per-page files.

PAGE_SEPARATOR = re.compile(
    r"={10,}\s*\nPAGE\s+(\d+)\s*\n={10,}",
    re.MULTILINE,
)


def split_pages(text: str) -> list[tuple[int, str]]:
    """Split a concatenated transcription file into (page_num, page_text) pairs."""
    pages = []
    matches = list(PAGE_SEPARATOR.finditer(text))
    for i, m in enumerate(matches):
        page_num = int(m.group(1))
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        pages.append((page_num, text[start:end].strip()))
    return pages
