"""Shared scaffolding for the page-by-page LLM extraction commands.

Deduplicates what extract_matches.py, extract_stats.py, and scorecards/extract.py
all need: page-spec parsing, page loading, model resolution, retry-once-on-transient
error semantics, raw-response JSONL logging, and the skip/rate-limit page loop.
Each command still owns its own output-writing (append-CSV vs whole-JSON rewrite),
since that differs enough between them that forcing a shared writer would hide
more than it would save.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import llm

from . import config
from .llm_common import JSONExtractError, load_pages_from_dir, split_pages


def parse_page_spec(spec: str | None) -> set[int] | None:
    """Parse '1,3,5-10' into {1,3,5,6,7,8,9,10}. Returns None if spec is empty."""
    if not spec:
        return None
    pages: set[int] = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            lo, hi = part.split("-", 1)
            pages.update(range(int(lo), int(hi) + 1))
        else:
            pages.add(int(part))
    return pages


def load_pages(input_path: Path) -> list[tuple[int, str]]:
    """Load pages from a directory of per-page .txt files, or a single concatenated file."""
    if input_path.is_dir():
        pages = load_pages_from_dir(input_path)
        if not pages:
            raise SystemExit(f"No .txt files found in {input_path}")
        return pages
    full_text = input_path.read_text(encoding="utf-8")
    pages = split_pages(full_text)
    if not pages:
        raise SystemExit("No pages found. Check the PAGE separator format.")
    return pages


def resolve_model(model_id: str):
    """Look up a model by ID from all registered llm plugins."""
    all_models = {m.model_id: m for m in llm.get_models()}
    if model_id not in all_models:
        raise SystemExit(f"Unknown model: {model_id!r}. Run 'llm models' to see available models.")
    return all_models[model_id]


class RawResponseLog:
    """Append-only JSONL writer for per-page raw LLM diagnostics."""

    def __init__(self, path: Path):
        self.path = path

    def write(self, page: int, raw: str, **fields) -> None:
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"page": page, "raw": raw, **fields}, ensure_ascii=False) + "\n")


def call_with_retry(
    fn: Callable[[], tuple],
    *,
    attempts: int = config.RETRY_ATTEMPTS,
    backoff: float = config.RETRY_BACKOFF,
) -> tuple:
    """Call fn() with retry-once-on-transient-error semantics.

    Returns (result, error_message). result is None if every attempt failed.
    JSONExtractError is never retried -- it means the model's output was
    malformed, not that the call itself failed transiently.
    """
    error: str | None = None
    for attempt in range(attempts + 1):
        try:
            return fn(), None
        except JSONExtractError as e:
            return None, str(e)
        except Exception as e:  # transient API/network error
            error = str(e)
            if attempt < attempts:
                time.sleep(backoff)
                continue
            return None, error
    return None, error


@dataclass
class PageResult:
    page: int
    result: object | None
    error: str | None


def run_pages(
    pages: list[tuple[int, str]],
    processed: set[int],
    extract_fn: Callable[[int, str], tuple],
    on_result: Callable[[PageResult], None],
    *,
    rate_limit: float = config.RATE_LIMIT_DELAY,
    retry_attempts: int = config.RETRY_ATTEMPTS,
    retry_backoff: float = config.RETRY_BACKOFF,
) -> None:
    """Iterate pages, skipping already-processed ones, calling extract_fn per page.

    extract_fn(page_num, page_text) -> (items, raw) — may raise JSONExtractError.
    on_result(PageResult) is invoked for every non-skipped page and is responsible
    for writing output and printing its own progress line.
    """
    for page_num, page_text in pages:
        if page_num in processed:
            print(f"  Skipping page {page_num} (already processed)")
            continue
        print(f"  Processing page {page_num} …", end=" ", flush=True)
        try:
            result, error = call_with_retry(
                lambda: extract_fn(page_num, page_text),
                attempts=retry_attempts,
                backoff=retry_backoff,
            )
            on_result(PageResult(page=page_num, result=result, error=error))
        finally:
            time.sleep(rate_limit)
