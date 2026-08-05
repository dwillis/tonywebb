# Consecutive-Page Continuation Auto-Merge Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** When `extract-matches`/`index-stats`/`index-scorecards` produce the same entry on two or more immediately-consecutive pages (a model violating the "don't index a continuation" prompt rule), collapse it into one row on the first page with `pages` set to the run length, instead of today's flag-both-keep-both behavior — while leaving non-adjacent duplicates (likely genuine separate write-ups) untouched, and leaving `match_index_willis.csv`/`consensus_index.csv` untouched entirely.

**Architecture:** Add a new function, `merge_consecutive_continuations()`, to `tonywebb/indexing.py` alongside the existing (unmodified) `recompute_pages_column()`. Wire the new function into `run_index_extraction()`'s end-of-run pass only — `consensus.py` and `promote_reviewed.py` keep calling `recompute_pages_column()` exactly as today. Dropped rows are appended to a JSONL audit log derived from the output CSV's path.

**Tech Stack:** Python 3.12 stdlib only (`csv`, `json`, `dataclasses`, `pathlib`). pytest, following `tests/test_indexing.py`'s existing conventions.

**Reference reading before starting:** `tonywebb/indexing.py` (existing `_row_key()` at line 224 and `recompute_pages_column()` at line 256 — read both in full; the new function reuses `_row_key()` unchanged and sits right next to `recompute_pages_column()` without modifying it), `tests/test_indexing.py` (existing test conventions for this file), `tests/test_index_stats.py`'s `TestEndToEnd` class (the `_FakeModel`/`_FakeResponse` pattern for testing `run_index_extraction()` end-to-end via `cli.main()`), and `reports/2026-08-05-consecutive-page-merge-design.md` (the full design this plan implements).

---

### Task 1: `merge_consecutive_continuations()` in indexing.py

**Files:**
- Modify: `tonywebb/indexing.py` (add `MergeResult` dataclass + `merge_consecutive_continuations()` right after `recompute_pages_column()`, i.e. after line 293; add `import json` and `from dataclasses import dataclass` to the existing import block at the top)
- Test: `tests/test_indexing.py` (append a new test class)

**Step 1: Write the failing tests**

Append to `tests/test_indexing.py`:

```python
import json as json_module

from tonywebb.indexing import MergeResult, merge_consecutive_continuations


class TestMergeConsecutiveContinuations:
    def test_two_consecutive_pages_merged(self, tmp_path):
        path = _write_csv(tmp_path, [
            {"matchup": "A v B", "page": "9", "date": "18950527", "content_type": "match information"},
            {"matchup": "A v B", "page": "10", "date": "18950527", "content_type": "match information"},
        ])
        result = merge_consecutive_continuations(path)
        rows = _read_rows(path)
        assert len(rows) == 1
        assert rows[0]["page"] == "9"
        assert rows[0]["pages"] == "2"
        assert result.merged_count == 1

    def test_three_consecutive_pages_merged(self, tmp_path):
        path = _write_csv(tmp_path, [
            {"matchup": "A v B", "page": "9", "date": "18950527", "content_type": "match information"},
            {"matchup": "A v B", "page": "10", "date": "18950527", "content_type": "match information"},
            {"matchup": "A v B", "page": "11", "date": "18950527", "content_type": "match information"},
        ])
        result = merge_consecutive_continuations(path)
        rows = _read_rows(path)
        assert len(rows) == 1
        assert rows[0]["page"] == "9"
        assert rows[0]["pages"] == "3"
        assert result.merged_count == 2

    def test_non_consecutive_pages_not_merged(self, tmp_path):
        # Same regression case as recompute_pages_column's own test: a real
        # separate write-up elsewhere in the collection must NOT be merged
        # away, just flagged.
        path = _write_csv(tmp_path, [
            {"matchup": "Liverpool v Oxton", "page": "59", "date": "18950907", "content_type": "match information"},
            {"matchup": "Liverpool v Oxton", "page": "61", "date": "18950907", "content_type": "match information"},
        ])
        result = merge_consecutive_continuations(path)
        rows = _read_rows(path)
        assert len(rows) == 2
        assert {r["page"] for r in rows} == {"59", "61"}
        assert result.merged_count == 0
        assert len(result.remaining_duplicates) == 2

    def test_mixed_run_and_isolated_occurrence(self, tmp_path):
        # Pages 9+10 are a continuation (merge to one row); page 20 is a
        # separate write-up of the same match (stays its own row, flagged).
        path = _write_csv(tmp_path, [
            {"matchup": "A v B", "page": "9", "date": "18950527", "content_type": "match information"},
            {"matchup": "A v B", "page": "10", "date": "18950527", "content_type": "match information"},
            {"matchup": "A v B", "page": "20", "date": "18950527", "content_type": "match information"},
        ])
        result = merge_consecutive_continuations(path)
        rows = _read_rows(path)
        assert len(rows) == 2
        by_page = {r["page"]: r for r in rows}
        assert by_page["9"]["pages"] == "2"
        assert by_page["20"]["pages"] == "1"
        assert result.merged_count == 1
        assert len(result.remaining_duplicates) == 2

    def test_unrelated_entries_untouched(self, tmp_path):
        path = _write_csv(tmp_path, [
            {"matchup": "A v B", "page": "1", "date": "18950527", "content_type": "match information"},
            {"matchup": "C v D", "page": "2", "date": "18950603", "content_type": "match information"},
        ])
        result = merge_consecutive_continuations(path)
        rows = _read_rows(path)
        assert len(rows) == 2
        assert [r["pages"] for r in rows] == ["1", "1"]
        assert result.merged_count == 0
        assert result.remaining_duplicates == []

    def test_audit_log_written_for_merged_rows(self, tmp_path):
        path = _write_csv(tmp_path, [
            {"matchup": "A v B", "page": "9", "date": "18950527", "content_type": "match information"},
            {"matchup": "A v B", "page": "10", "date": "18950527", "content_type": "match information"},
        ])
        result = merge_consecutive_continuations(path)
        assert result.log_path.exists()
        entries = [json_module.loads(line) for line in result.log_path.read_text().splitlines()]
        assert len(entries) == 1
        assert entries[0]["dropped_page"] == 10
        assert entries[0]["merged_into_page"] == 9
        assert entries[0]["matchup"] == "A v B"
        assert entries[0]["date"] == "18950527"
        assert entries[0]["content_type"] == "match information"

    def test_audit_log_path_derived_from_csv_path(self, tmp_path):
        path = _write_csv(tmp_path, [
            {"matchup": "A v B", "page": "9", "date": "18950527", "content_type": "match information"},
            {"matchup": "A v B", "page": "10", "date": "18950527", "content_type": "match information"},
        ])
        result = merge_consecutive_continuations(path)
        assert result.log_path == tmp_path / "match_index_test.merges.jsonl"

    def test_no_audit_log_written_when_nothing_merged(self, tmp_path):
        path = _write_csv(tmp_path, [
            {"matchup": "A v B", "page": "1", "date": "18950527", "content_type": "match information"},
        ])
        result = merge_consecutive_continuations(path)
        assert not result.log_path.exists()

    def test_malformed_page_row_preserved_untouched(self, tmp_path):
        path = _write_csv(tmp_path, [
            {"matchup": "A v B", "page": "not-a-number", "date": "18950527", "content_type": "match information"},
            {"matchup": "C v D", "page": "1", "date": "18950603", "content_type": "match information"},
        ])
        result = merge_consecutive_continuations(path)
        rows = _read_rows(path)
        assert len(rows) == 2
        assert any(r["matchup"] == "A v B" and r["page"] == "not-a-number" for r in rows)
        assert result.merged_count == 0

    def test_output_sorted_by_page(self, tmp_path):
        path = _write_csv(tmp_path, [
            {"matchup": "C v D", "page": "5", "date": "18950527", "content_type": "match information"},
            {"matchup": "A v B", "page": "1", "date": "18950603", "content_type": "match information"},
        ])
        merge_consecutive_continuations(path)
        rows = _read_rows(path)
        assert [r["page"] for r in rows] == ["1", "5"]

    def test_reversed_team_order_still_merged(self, tmp_path):
        # Same symmetric-key behavior as recompute_pages_column -- see
        # _row_key()'s docstring.
        path = _write_csv(tmp_path, [
            {"matchup": "Liverpool v Rock Ferry", "page": "9", "date": "18950527", "content_type": "match information"},
            {"matchup": "Rock Ferry v Liverpool", "page": "10", "date": "18950527", "content_type": "match information"},
        ])
        result = merge_consecutive_continuations(path)
        rows = _read_rows(path)
        assert len(rows) == 1
        assert result.merged_count == 1
```

**Step 2: Run the tests to verify they fail**

Run: `uv run pytest tests/test_indexing.py::TestMergeConsecutiveContinuations -v`
Expected: FAIL — `ImportError: cannot import name 'MergeResult' from 'tonywebb.indexing'`

**Step 3: Write the minimal implementation**

In `tonywebb/indexing.py`, change the import block near the top (after the existing `from __future__ import annotations` line) to add two imports:

```python
import csv
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Callable
```

(This replaces the existing `import csv` / `import logging` / `from pathlib import Path` / `from typing import Callable` lines — just insert `import json` and `from dataclasses import dataclass` alphabetically among them.)

Then add this right after `recompute_pages_column()` (after line 293, before the `# ── LLM extraction ──` section header):

```python
@dataclass
class MergeResult:
    """Result of merge_consecutive_continuations()."""
    merged_count: int
    log_path: Path
    remaining_duplicates: list[dict]  # [{matchup, page, date, content_type}, ...]


def _page_sort_key(row: dict) -> int:
    try:
        return int((row.get("page") or "").strip())
    except (ValueError, TypeError):
        return 10**9


def merge_consecutive_continuations(csv_path: Path) -> MergeResult:
    """Collapse same-entry rows on immediately-consecutive pages into one row
    on the first page, with `pages` set to the run length.

    A continuation onto the very next page is overwhelmingly the extraction
    prompt's "do NOT create a new entry for it" rule being violated by the
    model, not a genuinely separate write-up -- unlike a duplicate on a
    non-adjacent page (a strong signal of a real separate write-up
    elsewhere in the collection, see _row_key()'s docstring), which is left
    exactly as today: both rows kept, flagged for human review via
    `remaining_duplicates`.

    Every dropped row is appended to a `<csv stem>.merges.jsonl` audit log
    next to csv_path (only created if something was actually merged), so a
    wrong merge is always recoverable -- it's removed from the CSV, not
    silently gone.

    Unlike recompute_pages_column(), this rewrites the file sorted by page.
    """
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    rows_by_key: dict[tuple[str, str, str], dict[int, dict]] = {}
    unparseable_rows: list[dict] = []
    for row in rows:
        content_type = (row.get("content_type") or "match information").strip().lower()
        key = _row_key(row.get("matchup", ""), row.get("date", ""), content_type)
        try:
            page = int((row.get("page") or "").strip())
        except (ValueError, TypeError):
            unparseable_rows.append(row)
            continue
        rows_by_key.setdefault(key, {})[page] = row

    dropped_log_entries: list[dict] = []
    survivors_by_key: dict[tuple[str, str, str], list[dict]] = {}

    for key, by_page in rows_by_key.items():
        pages_sorted = sorted(by_page)
        runs: list[list[int]] = []
        for page in pages_sorted:
            if runs and page == runs[-1][-1] + 1:
                runs[-1].append(page)
            else:
                runs.append([page])

        key_survivors = []
        for run in runs:
            first_page = run[0]
            survivor = by_page[first_page]
            survivor["pages"] = str(len(run))
            key_survivors.append(survivor)
            for page in run[1:]:
                dropped = by_page[page]
                dropped_log_entries.append({
                    "dropped_page": page,
                    "matchup": dropped.get("matchup", ""),
                    "date": dropped.get("date", ""),
                    "content_type": (dropped.get("content_type") or "match information").strip().lower(),
                    "merged_into_page": first_page,
                })
        survivors_by_key[key] = key_survivors

    log_path = csv_path.with_name(csv_path.stem + ".merges.jsonl")
    if dropped_log_entries:
        with log_path.open("a", encoding="utf-8") as f:
            for entry in dropped_log_entries:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    surviving_rows: list[dict] = list(unparseable_rows)
    remaining_duplicates: list[dict] = []
    for key_survivors in survivors_by_key.values():
        surviving_rows.extend(key_survivors)
        if len(key_survivors) > 1:
            for row in key_survivors:
                remaining_duplicates.append({
                    "matchup": row.get("matchup", ""),
                    "page": row.get("page", ""),
                    "date": row.get("date", ""),
                    "content_type": row.get("content_type", ""),
                })

    surviving_rows.sort(key=_page_sort_key)

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(surviving_rows)

    return MergeResult(
        merged_count=len(dropped_log_entries),
        log_path=log_path,
        remaining_duplicates=remaining_duplicates,
    )
```

**Step 4: Run the tests to verify they pass**

Run: `uv run pytest tests/test_indexing.py -v`
Expected: PASS (all existing `TestRecomputePagesColumn` tests still pass unmodified, plus the new `TestMergeConsecutiveContinuations` tests)

**Step 5: Commit**

```bash
git add tonywebb/indexing.py tests/test_indexing.py
git commit -m "$(cat <<'EOF'
Add merge_consecutive_continuations for cross-page dedup

Collapses same-entry rows on immediately-consecutive pages into one
row with pages set to the run length, instead of flagging both --
recompute_pages_column (used by consensus/promote-reviewed) is
unchanged; this is a separate function for the extraction commands
only, since a continuation on the very next page is a different,
higher-confidence signal than a same-key duplicate on a distant page.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 2: Wire into run_index_extraction()

**Files:**
- Modify: `tonywebb/indexing.py:462-471` (the end-of-run block inside `run_index_extraction()`)
- Test: `tests/test_indexing.py`

**Step 1: Write the failing test**

Append to `tests/test_indexing.py`:

```python
from unittest import mock

from tonywebb import cli


class _FakeResponse:
    def __init__(self, text):
        self._text = text

    def text(self):
        return self._text


class _FakeModel:
    model_id = "fake-model"

    def __init__(self, raw_text):
        self.raw_text = raw_text
        self.calls = 0

    def prompt(self, *a, **k):
        self.calls += 1
        return _FakeResponse(self.raw_text)


class TestRunIndexExtractionMergesConsecutivePages:
    def test_consecutive_page_duplicate_merged_end_to_end(self, tmp_path, monkeypatch, capsys):
        input_dir = tmp_path / "pages"
        input_dir.mkdir()
        (input_dir / "tw_newspaper_cuttings_1895_9.txt").write_text("Dunstable Second XI v Houghton, page 9 text")
        (input_dir / "tw_newspaper_cuttings_1895_10.txt").write_text("continuation text, no header")

        fake_raw = json.dumps({"entries": [
            {"title": "Dunstable Second XI v Houghton", "date": "18950800", "content_type": "match information"},
        ]})
        fake_model = _FakeModel(fake_raw)

        monkeypatch.chdir(tmp_path)
        out_csv = tmp_path / "match_index_fake-model.csv"
        with mock.patch("tonywebb.indexing.resolve_model", return_value=fake_model), \
             mock.patch("tonywebb.pipeline.time.sleep"):
            cli.main([
                "extract-matches", "--input", str(input_dir), "--model", "fake-model",
                "--output", str(out_csv),
            ])

        rows = _read_rows(out_csv)
        assert len(rows) == 1
        assert rows[0]["page"] == "9"
        assert rows[0]["pages"] == "2"

        merge_log = tmp_path / "match_index_fake-model.merges.jsonl"
        assert merge_log.exists()

        captured = capsys.readouterr()
        assert "merged" in captured.out.lower()
```

Add `import json` near the top of `tests/test_indexing.py` if it isn't already imported as `json_module` from Task 1 — use a single `import json` at the top of the file instead of the `import json as json_module` alias from Task 1's step (clean up: change Task 1's `json_module.loads` calls to plain `json.loads` once this shared top-level `import json` exists, so the whole test file has one consistent import rather than two names for the same module).

**Step 2: Run the test to verify it fails**

Run: `uv run pytest tests/test_indexing.py::TestRunIndexExtractionMergesConsecutivePages -v`
Expected: FAIL — 2 rows in the CSV instead of 1 (today's code just flags, doesn't merge), and no `match_index_fake-model.merges.jsonl` file

**Step 3: Wire the new function into the end-of-run block**

In `tonywebb/indexing.py`, find this block (currently around line 462, inside `run_index_extraction()`):

```python
    print(f"\nDone. {total_entries} entries written to {csv_path}; {total_errors} page error(s).")
    if cross_page_dupes:
        print(f"{len(cross_page_dupes)} entry(ies) also appear on an earlier page (kept; review manually):")
        for d in cross_page_dupes:
            print(f"  page {d['page']}: {d['matchup']} [{d['date']}] first seen on page {d['first_page']}")

    if csv_path.exists():
        changed = recompute_pages_column(csv_path)
        if changed:
            print(f"Updated 'pages' count for {changed} row(s) spanning more than one page.")
```

Replace the final `if csv_path.exists():` block (leave the `cross_page_dupes` live-streaming notice above it untouched — that's still a useful per-page signal during a long run, and it's superseded by the more accurate final pass below, not made incorrect by it):

```python
    if csv_path.exists():
        merge_result = merge_consecutive_continuations(csv_path)
        if merge_result.merged_count:
            print(
                f"{merge_result.merged_count} entry(ies) merged into an earlier page's row "
                f"(continuation, auto-resolved; see {merge_result.log_path} for what was dropped)."
            )
        if merge_result.remaining_duplicates:
            print(
                f"{len(merge_result.remaining_duplicates)} entry(ies) also appear on a "
                f"non-adjacent page (kept; may be a separate write-up, review manually):"
            )
            for d in merge_result.remaining_duplicates:
                print(f"  page {d['page']}: {d['matchup']} [{d['date']}]")
```

Note this entirely replaces the call to `recompute_pages_column()` inside `run_index_extraction()` — `recompute_pages_column()` itself stays completely unmodified in the file (still used, unchanged, by `consensus.py:242` and `promote_reviewed.py:88`).

**Step 4: Run the tests to verify they pass**

Run: `uv run pytest tests/test_indexing.py -v`
Expected: PASS (every test in the file, old and new)

Run the full suite to confirm `extract-stats`, `index-stats`, `index-scorecards`, `consensus`, and `promote-reviewed` are all unaffected:
Run: `uv run pytest -q`
Expected: PASS

**Step 5: Commit**

```bash
git add tonywebb/indexing.py tests/test_indexing.py
git commit -m "$(cat <<'EOF'
Wire consecutive-page merge into run_index_extraction

extract-matches/index-stats/index-scorecards now auto-merge
consecutive-page continuations at the end of every run; consensus and
promote-reviewed are untouched, since they still call
recompute_pages_column() directly.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 3: Manual verification against real data

**Files:** none (verification only)

**Step 1: Re-run extraction on a page range known to have this problem**

The screenshot that prompted this change showed `match_indexes/match_index_glm52_cleaned.csv` indexing "Dunstable Second XI v Houghton" on both page 9 and page 10. Re-run extraction for just that page range with whatever model/input produced that file (check `raw_responses/raw_responses_glm52_cleaned.jsonl` or similar to confirm the original `--model`/`--input` used), e.g.:

```bash
uv run tonywebb extract-matches --input <original-input> --model <original-model> --pages 9,10 --output match_indexes/match_index_glm52_cleaned.csv
```

Expected console output includes a line like `1 entry(ies) merged into an earlier page's row (continuation, auto-resolved; see match_indexes/match_index_glm52_cleaned.merges.jsonl for what was dropped).`

**Step 2: Confirm the CSV and merge log**

```bash
grep "Dunstable Second XI v Houghton" match_indexes/match_index_glm52_cleaned.csv
cat match_indexes/match_index_glm52_cleaned.merges.jsonl
```

Expected: exactly one CSV row for that match (page 9, `pages=2`), and the merge log contains one JSON line recording the page-10 row that was dropped.

**Step 3: Regenerate the willis-compare browser and confirm the noise is gone**

```bash
uv run tonywebb willis-compare
```

Open `browser/willis_compare.html`, select `glm52_cleaned`, and confirm page 10 no longer shows a spurious `unindexed` "Dunstable Second XI v Houghton" row (it was never in Willis's ground truth on page 10 to begin with — that's exactly why it showed up as noise).

No commit for this task — it's verification of Tasks 1–2's already-committed work. If it surfaces a bug, fix it as a follow-up commit on top of the relevant task.
