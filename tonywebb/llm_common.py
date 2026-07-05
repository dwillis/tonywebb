"""Shared helpers for the LLM extraction commands (extract_matches, extract_stats, scorecards)."""

import json
import re
from pathlib import Path


class JSONExtractError(Exception):
    """Raised when the model's response can't be parsed as the expected JSON shape."""


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
        parsed = _first_json_object(text, e)
    if not isinstance(parsed, dict):
        raise JSONExtractError("response is not a JSON object")
    return parsed


def _first_json_object(text: str, original_error: json.JSONDecodeError) -> dict:
    """Decode the first JSON object embedded in surrounding prose."""
    decoder = json.JSONDecoder()
    idx = text.find("{")
    while idx != -1:
        candidate = _strip_fences(text[idx:].strip())
        try:
            parsed, _ = decoder.raw_decode(candidate)
        except json.JSONDecodeError:
            idx = text.find("{", idx + 1)
            continue
        if isinstance(parsed, dict):
            return parsed
        idx = text.find("{", idx + 1)
    raise JSONExtractError(f"invalid JSON: {original_error}") from original_error


def no_thinking_kwargs(model) -> dict:
    """Return prompt kwargs that disable thinking for models that support it."""
    model_id: str = getattr(model, "model_id", "") or ""
    model_type = type(model).__module__ or ""
    if "ollama" in model_type:
        # llm-ollama exposes thinking as `think`
        return {"think": False}
    if any(x in model_id.lower() for x in ("claude", "opus", "sonnet", "haiku")):
        # Anthropic extended thinking: budget_tokens=0 disables it
        return {"budget_tokens": 0}
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
