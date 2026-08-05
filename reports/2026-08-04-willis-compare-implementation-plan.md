# Willis Comparison Browser Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add `tonywebb willis-compare`, a new subcommand that generates a self-contained HTML page showing any `match_indexes/match_index_*.csv` side by side with `match_index_willis.csv`, page by page, with a model-switching dropdown, filters, and a scanned-page-image toggle.

**Architecture:** New module `tonywebb/willis_compare.py`. A pure function (`build_comparison_rows`) reuses `evaluate.py`'s existing `evaluate()`/`load_index()` to classify every row as `matched` / `missed` / `surplus` (pages 1–61, Willis's range) or `unindexed` (pages 62–247, no ground truth to compare against). An orchestration function loads every candidate CSV, builds one row-list per model, and embeds it all as JSON into a static HTML/CSS/vanilla-JS template — the same self-contained-page pattern `build_browser.py` already uses for `compare_browser.html`. No changes needed to `evaluate.py` itself: its public API already provides exactly the per-page matching this needs.

**Tech Stack:** Python 3.12, stdlib only (`csv`, `glob`, `json`, `pathlib`) + vanilla JS/HTML/CSS in the generated page. pytest for tests, following the conventions in `tests/test_evaluate.py` and `tests/test_build_browser.py`.

**Reference reading before starting:** `tonywebb/evaluate.py` (the `IndexRow` dataclass, `load_index()`, `evaluate()`, and the `EvalResult` dataclass this plan builds on) and `tonywebb/build_browser.py` (the self-contained-HTML pattern and its `label()` helper, which this plan reuses directly rather than duplicating).

---

### Task 1: Comparison-row builder

**Files:**
- Create: `tonywebb/willis_compare.py`
- Test: `tests/test_willis_compare.py`

**Step 1: Write the failing tests**

```python
"""Tests for willis_compare.py — Willis-vs-model comparison row building."""

from tonywebb.evaluate import IndexRow
from tonywebb.willis_compare import build_comparison_rows


class TestBuildComparisonRows:
    def test_exact_match_is_matched(self):
        truth = [IndexRow("Team A v Team B", 1, "18950527", "match information")]
        model = [IndexRow("Team A v Team B", 1, "18950527", "match information")]
        rows = build_comparison_rows(truth, model)
        assert len(rows) == 1
        assert rows[0]["status"] == "matched"
        assert rows[0]["page"] == 1
        assert rows[0]["content_type"] == "match information"
        assert rows[0]["willis"] == {"matchup": "Team A v Team B", "date": "18950527"}
        assert rows[0]["model"] == {"matchup": "Team A v Team B", "date": "18950527"}

    def test_fuzzy_match_is_matched(self):
        truth = [IndexRow("Kensworth v Dunstable Victoria", 1, "18950527", "match information")]
        model = [IndexRow("Kensworth v Dunstable Vic", 1, "18950527", "match information")]
        rows = build_comparison_rows(truth, model, fuzzy_threshold=0.8)
        assert len(rows) == 1
        assert rows[0]["status"] == "matched"
        assert rows[0]["similarity"] is not None
        assert 0.0 < rows[0]["similarity"] < 1.0

    def test_willis_only_is_missed(self):
        truth = [IndexRow("Team A v Team B", 1, "18950527", "match information")]
        model = []
        rows = build_comparison_rows(truth, model)
        assert len(rows) == 1
        assert rows[0]["status"] == "missed"
        assert rows[0]["willis"]["matchup"] == "Team A v Team B"
        assert rows[0]["model"] is None
        assert rows[0]["similarity"] is None

    def test_model_only_on_covered_page_is_surplus(self):
        truth = [IndexRow("Team A v Team B", 1, "18950527", "match information")]
        model = [
            IndexRow("Team A v Team B", 1, "18950527", "match information"),
            IndexRow("Team C v Team D", 1, "18950527", "match information"),
        ]
        rows = build_comparison_rows(truth, model)
        surplus = [r for r in rows if r["status"] == "surplus"]
        assert len(surplus) == 1
        assert surplus[0]["willis"] is None
        assert surplus[0]["model"]["matchup"] == "Team C v Team D"

    def test_model_only_on_uncovered_page_is_unindexed(self):
        # Willis only covers page 1 here; page 62 has no ground truth at all.
        truth = [IndexRow("Team A v Team B", 1, "18950527", "match information")]
        model = [
            IndexRow("Team A v Team B", 1, "18950527", "match information"),
            IndexRow("Team E v Team F", 62, "18950801", "match information"),
        ]
        rows = build_comparison_rows(truth, model)
        page_62 = next(r for r in rows if r["page"] == 62)
        assert page_62["status"] == "unindexed"
        assert page_62["willis"] is None
        assert page_62["model"]["matchup"] == "Team E v Team F"

    def test_rows_sorted_by_page(self):
        truth = [
            IndexRow("A v B", 5, "18950527", "match information"),
            IndexRow("C v D", 1, "18950527", "match information"),
        ]
        model = [
            IndexRow("A v B", 5, "18950527", "match information"),
            IndexRow("C v D", 1, "18950527", "match information"),
        ]
        rows = build_comparison_rows(truth, model)
        pages = [r["page"] for r in rows]
        assert pages == sorted(pages)

    def test_similarity_none_for_missed_and_surplus(self):
        truth = [IndexRow("Team A v Team B", 1, "18950527", "match information")]
        model = [IndexRow("Team C v Team D", 1, "18950527", "match information")]
        rows = build_comparison_rows(truth, model, fuzzy_threshold=0.8)
        for r in rows:
            assert r["similarity"] is None
```

**Step 2: Run the tests to verify they fail**

Run: `uv run pytest tests/test_willis_compare.py -v`
Expected: FAIL/ERROR — `ModuleNotFoundError: No module named 'tonywebb.willis_compare'`

**Step 3: Write the minimal implementation**

```python
"""Build side-by-side comparison rows for a match_index_<model>.csv against
match_index_willis.csv. See willis_compare.run_willis_compare() for the HTML
generation this feeds into.
"""

from . import evaluate


def build_comparison_rows(
    truth_rows: list[evaluate.IndexRow],
    model_rows: list[evaluate.IndexRow],
    fuzzy_threshold: float = 0.8,
) -> list[dict]:
    """Return a flat list of {page, status, content_type, willis, model, similarity}.

    status is one of:
      - "matched": Willis and the model agree (exact or fuzzy key match)
      - "missed": in Willis, no model match, on a page Willis covers
      - "surplus": in the model, no Willis match, on a page Willis covers
      - "unindexed": in the model, on a page outside Willis's covered range
        (no ground truth exists there, so this is not a "surplus"/false-positive
        claim — just unreviewed)
    """
    result = evaluate.evaluate(truth_rows, model_rows, fuzzy_threshold=fuzzy_threshold)
    covered = set(result.pages_covered)

    rows: list[dict] = []
    for pair in result.matched:
        rows.append({
            "page": pair.truth.page,
            "status": "matched",
            "content_type": pair.truth.content_type,
            "willis": {"matchup": pair.truth.matchup, "date": pair.truth.date},
            "model": {"matchup": pair.model.matchup, "date": pair.model.date},
            "similarity": pair.similarity,
        })
    for r in result.missed:
        rows.append({
            "page": r.page,
            "status": "missed",
            "content_type": r.content_type,
            "willis": {"matchup": r.matchup, "date": r.date},
            "model": None,
            "similarity": None,
        })
    for r in result.surplus:
        rows.append({
            "page": r.page,
            "status": "surplus",
            "content_type": r.content_type,
            "willis": None,
            "model": {"matchup": r.matchup, "date": r.date},
            "similarity": None,
        })
    for r in model_rows:
        if r.page not in covered:
            rows.append({
                "page": r.page,
                "status": "unindexed",
                "content_type": r.content_type,
                "willis": None,
                "model": {"matchup": r.matchup, "date": r.date},
                "similarity": None,
            })

    rows.sort(key=lambda r: (r["page"], (r["willis"] or r["model"] or {}).get("matchup", "")))
    return rows
```

**Step 4: Run the tests to verify they pass**

Run: `uv run pytest tests/test_willis_compare.py -v`
Expected: PASS (7 tests)

**Step 5: Commit**

```bash
git add tonywebb/willis_compare.py tests/test_willis_compare.py
git commit -m "$(cat <<'EOF'
Add build_comparison_rows for Willis-vs-model comparison

Classifies every row as matched/missed/surplus/unindexed, reusing
evaluate.py's existing exact/fuzzy matcher rather than duplicating it.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 2: Orchestration function and CLI wiring

**Files:**
- Modify: `tonywebb/willis_compare.py`
- Modify: `tonywebb/cli.py`
- Test: `tests/test_willis_compare.py`

**Step 1: Write the failing tests**

Append to `tests/test_willis_compare.py`:

```python
import csv
import json
import re

import pytest


def _write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["matchup", "page", "date", "content_type", "collection", "pages"])
        for row in rows:
            writer.writerow(row)


class TestRunWillisCompare:
    def test_writes_output_file(self, tmp_path, monkeypatch):
        _write_csv(tmp_path / "match_index_willis.csv", [
            ["Team A v Team B", "1", "18950527", "match information", "coll", ""],
        ])
        _write_csv(tmp_path / "match_index_modelx.csv", [
            ["Team A v Team B", "1", "18950527", "match information", "coll", ""],
        ])

        monkeypatch.chdir(tmp_path)
        from tonywebb.willis_compare import run_willis_compare
        run_willis_compare(
            pattern="match_index_*.csv",
            truth_path="match_index_willis.csv",
            output_path="browser/willis_compare.html",
        )

        out = tmp_path / "browser" / "willis_compare.html"
        assert out.exists()

    def test_truth_file_excluded_from_models(self, tmp_path, monkeypatch):
        _write_csv(tmp_path / "match_index_willis.csv", [
            ["Team A v Team B", "1", "18950527", "match information", "coll", ""],
        ])
        _write_csv(tmp_path / "match_index_modelx.csv", [
            ["Team A v Team B", "1", "18950527", "match information", "coll", ""],
        ])

        monkeypatch.chdir(tmp_path)
        from tonywebb.willis_compare import run_willis_compare
        run_willis_compare(
            pattern="match_index_*.csv",
            truth_path="match_index_willis.csv",
            output_path="willis_compare.html",
        )

        html = (tmp_path / "willis_compare.html").read_text()
        match = re.search(r'<script id="data" type="application/json">(.*?)</script>', html, re.DOTALL)
        assert match
        data = json.loads(match.group(1))
        assert data["models"] == ["modelx"]
        assert "willis" not in data["models"]

    def test_missing_truth_file_does_not_crash(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        from tonywebb.willis_compare import run_willis_compare
        run_willis_compare(truth_path="does_not_exist.csv")
        captured = capsys.readouterr()
        assert "not found" in captured.out.lower()
        assert not (tmp_path / "browser" / "willis_compare.html").exists()


class TestCLI:
    def test_registered_in_parser(self):
        from tonywebb.cli import build_parser
        parser = build_parser()
        args = parser.parse_args(["willis-compare", "--pattern", "x.csv"])
        assert args.pattern == "x.csv"
        assert args.command == "willis-compare"
```

**Step 2: Run the tests to verify they fail**

Run: `uv run pytest tests/test_willis_compare.py::TestRunWillisCompare tests/test_willis_compare.py::TestCLI -v`
Expected: FAIL — `ImportError: cannot import name 'run_willis_compare'` and `argument willis-compare: invalid choice` (not yet registered)

**Step 3: Add the orchestration function, a placeholder HTML builder, and CLI registration**

Append to `tonywebb/willis_compare.py`:

```python
import glob
import json
from pathlib import Path

from .build_browser import label


def run_willis_compare(
    pattern: str = "match_indexes/match_index_*.csv",
    truth_path: str = "match_indexes/match_index_willis.csv",
    output_path: str = "browser/willis_compare.html",
    fuzzy_threshold: float = 0.8,
) -> None:
    truth_file = Path(truth_path)
    if not truth_file.exists():
        print(f"Ground truth not found: {truth_file}")
        return
    truth_rows, _ = evaluate.load_index(truth_file)

    files = sorted(
        p for p in glob.glob(pattern)
        if Path(p).resolve() != truth_file.resolve()
    )
    if not files:
        print(f"No files matched {pattern} (besides the truth file).")
        return

    models: list[str] = []
    data: dict[str, list[dict]] = {}
    for path in files:
        name = label(path)
        model_rows, _ = evaluate.load_index(Path(path))
        data[name] = build_comparison_rows(truth_rows, model_rows, fuzzy_threshold)
        models.append(name)

    payload = json.dumps({"models": models, "data": data}, ensure_ascii=False)
    html = _build_html().replace("__DATA__", payload)

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"Wrote {output_path} ({len(models)} model(s) vs {truth_path})")


def _build_html() -> str:
    # Filled in with the real template in Task 3. Placeholder keeps this
    # task's tests (which only check the models list and file existence)
    # passing without depending on Task 3's work.
    return "<!doctype html><html><body>__DATA__</body></html>"


# ── CLI ──────────────────────────────────────────────────────────────────────

def register_parser(subparsers):
    p = subparsers.add_parser(
        "willis-compare",
        help="Generate a self-contained HTML page comparing match_index_*.csv "
             "files against match_index_willis.csv, page by page.",
    )
    p.add_argument("--pattern", default="match_indexes/match_index_*.csv")
    p.add_argument("--truth", default="match_indexes/match_index_willis.csv")
    p.add_argument("--output", "-o", default="browser/willis_compare.html")
    p.add_argument("--fuzzy-threshold", type=float, default=0.8)
    p.set_defaults(func=run)
    return p


def run(args) -> None:
    run_willis_compare(args.pattern, args.truth, args.output, args.fuzzy_threshold)
```

Modify `tonywebb/cli.py`:

```python
from . import (
    build_browser,
    clean_transcriptions,
    clubs,
    compare,
    consensus,
    evaluate,
    extract_matches,
    extract_stats,
    index_scorecards,
    index_stats,
    promote_reviewed,
    reconcile,
    transcribe,
    willis_compare,
)
```

```python
    for module in (
        transcribe,
        clean_transcriptions,
        extract_matches,
        extract_stats,
        index_stats,
        index_scorecards,
        evaluate,
        consensus,
        promote_reviewed,
        reconcile,
        compare,
        build_browser,
        willis_compare,
        clubs,
    ):
        module.register_parser(subparsers)
```

**Step 4: Run the tests to verify they pass**

Run: `uv run pytest tests/test_willis_compare.py -v`
Expected: PASS (all tests from Task 1 and Task 2)

Also sanity-check the CLI is wired up end to end:
Run: `uv run tonywebb willis-compare --help`
Expected: prints usage including `--pattern`, `--truth`, `--output`, `--fuzzy-threshold`

**Step 5: Commit**

```bash
git add tonywebb/willis_compare.py tonywebb/cli.py tests/test_willis_compare.py
git commit -m "$(cat <<'EOF'
Wire up tonywebb willis-compare CLI command

Orchestrates build_comparison_rows across every match_indexes/*.csv
and embeds the result as JSON for the HTML template (added next).

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 3: HTML/CSS/JS template

**Files:**
- Modify: `tonywebb/willis_compare.py` (replace the `_build_html()` placeholder)
- Test: `tests/test_willis_compare.py`

**Step 1: Write the failing test**

Append to `tests/test_willis_compare.py`:

```python
class TestHTMLTemplate:
    def test_html_contains_key_elements(self, tmp_path, monkeypatch):
        _write_csv(tmp_path / "match_index_willis.csv", [
            ["Team A v Team B", "1", "18950527", "match information", "coll", ""],
        ])
        _write_csv(tmp_path / "match_index_modelx.csv", [
            ["Team A v Team B", "1", "18950527", "match information", "coll", ""],
            ["Team E v Team F", "62", "18950801", "match information", "coll", ""],
        ])

        monkeypatch.chdir(tmp_path)
        from tonywebb.willis_compare import run_willis_compare
        run_willis_compare(
            pattern="match_index_*.csv",
            truth_path="match_index_willis.csv",
            output_path="willis_compare.html",
        )

        html = (tmp_path / "willis_compare.html").read_text()
        assert "Willis Comparison Browser" in html
        assert 'id="model"' in html
        assert 'id="status"' in html
        assert 'id="q"' in html
        assert "unindexed" in html
        assert "Show page image" in html or "data-img" in html

    def test_json_embedded_and_valid(self, tmp_path, monkeypatch):
        _write_csv(tmp_path / "match_index_willis.csv", [
            ["Team A v Team B", "1", "18950527", "match information", "coll", ""],
        ])
        _write_csv(tmp_path / "match_index_modelx.csv", [
            ["Team A v Team B", "1", "18950527", "match information", "coll", ""],
        ])

        monkeypatch.chdir(tmp_path)
        from tonywebb.willis_compare import run_willis_compare
        run_willis_compare(
            pattern="match_index_*.csv",
            truth_path="match_index_willis.csv",
            output_path="willis_compare.html",
        )

        html = (tmp_path / "willis_compare.html").read_text()
        match = re.search(r'<script id="data" type="application/json">(.*?)</script>', html, re.DOTALL)
        assert match
        data = json.loads(match.group(1))
        assert data["models"] == ["modelx"]
        assert data["data"]["modelx"][0]["status"] == "matched"
```

**Step 2: Run the tests to verify they fail**

Run: `uv run pytest tests/test_willis_compare.py::TestHTMLTemplate -v`
Expected: FAIL — the placeholder template from Task 2 doesn't contain "Willis Comparison Browser", `id="model"`, etc.

**Step 3: Replace `_build_html()` with the real template**

Replace the placeholder `_build_html()` in `tonywebb/willis_compare.py` with:

```python
def _build_html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Willis Comparison Browser</title>
<style>
  :root { color-scheme: light dark; }
  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 1rem; }
  header { display: flex; flex-wrap: wrap; gap: .75rem; align-items: center; margin-bottom: 1rem; }
  input[type=search] { padding: .4rem .6rem; min-width: 240px; font-size: 1rem; }
  select { padding: .35rem .55rem; font-size: .95rem; }
  .meta { color: #888; font-size: .85rem; margin-left: auto; }

  .page-block { border: 1px solid #ccc5; border-radius: 6px; margin-bottom: 1rem; overflow: hidden; }
  .page-header { display: flex; align-items: center; gap: .75rem; padding: .5rem .75rem; background: #00000008; }
  .page-header h3 { margin: 0; font-size: 1rem; }
  .toggle-img { font-size: .82rem; cursor: pointer; background: #eee; border: 1px solid #ccc; border-radius: 3px; padding: 2px 8px; }
  .page-preview img { max-width: 100%; max-height: 600px; border: 1px solid #ccc; margin: .5rem .75rem; display: block; }

  .col-headers { display: flex; font-size: .78rem; color: #888; padding: .3rem .75rem 0; }
  .col-headers .cmp-col { padding: 0 .75rem; }

  .cmp-row { display: flex; border-top: 1px solid #ccc3; }
  .cmp-col { flex: 1; padding: .4rem .75rem; min-width: 0; }
  .cmp-col.willis { border-right: 1px solid #ccc3; }
  .cmp-status { width: 90px; flex: none; padding: .4rem .5rem; font-size: .78rem; text-align: center; align-self: center; }
  .empty-cell { color: #aaa; font-style: italic; }

  .cmp-row.status-matched { border-left: 4px solid #28a745; }
  .cmp-row.status-missed { border-left: 4px solid #dc3545; background: #f8d7da22; }
  .cmp-row.status-surplus { border-left: 4px solid #ffc107; background: #fff3cd22; }
  .cmp-row.status-unindexed { border-left: 4px solid #6c757d; background: #00000008; }
</style>
</head>
<body>
<header>
  <h2 style="margin:0">Willis Comparison Browser</h2>
  <label>Model:
    <select id="model"></select>
  </label>
  <input id="q" type="search" placeholder="Search matchup, date, or page...">
  <label>Status:
    <select id="status">
      <option value="all">any</option>
      <option value="matched">matched</option>
      <option value="missed">missed (Willis only)</option>
      <option value="surplus">surplus (model only, Willis-covered page)</option>
      <option value="unindexed">unindexed (page beyond Willis's range)</option>
    </select>
  </label>
  <label>Type:
    <select id="contentType"><option value="">(any)</option></select>
  </label>
  <span class="meta" id="meta"></span>
</header>
<div id="pages"></div>
<script id="data" type="application/json">__DATA__</script>
<script>
const DATA = JSON.parse(document.getElementById('data').textContent);
const MODELS = DATA.models;

const IMG_URL = 'https://archive.acscricket.com/research/tw/tw_newspaper_cuttings_1895/files/assets/common/page-html5-substrates/page{page}_5.jpg';

const modelSel = document.getElementById('model');
for (const m of MODELS) {
  const o = document.createElement('option');
  o.value = m; o.textContent = m;
  modelSel.appendChild(o);
}

const pagesEl = document.getElementById('pages');
const meta = document.getElementById('meta');
const q = document.getElementById('q');
const statusSel = document.getElementById('status');
const typeSel = document.getElementById('contentType');

let typesPopulatedFor = null;

[modelSel, q, statusSel, typeSel].forEach(el => el.addEventListener('input', render));

function esc(s) {
  return String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

function render() {
  const rows = DATA.data[modelSel.value] || [];

  if (typesPopulatedFor !== modelSel.value) {
    typeSel.innerHTML = '<option value="">(any)</option>';
    const types = [...new Set(rows.map(r => r.content_type))].sort();
    for (const t of types) {
      const o = document.createElement('option');
      o.value = t; o.textContent = t;
      typeSel.appendChild(o);
    }
    typesPopulatedFor = modelSel.value;
  }

  const term = q.value.trim().toLowerCase();
  const statusFilter = statusSel.value;
  const typeFilter = typeSel.value;

  const filtered = rows.filter(r => {
    if (statusFilter !== 'all' && r.status !== statusFilter) return false;
    if (typeFilter && r.content_type !== typeFilter) return false;
    if (term) {
      const hay = [
        r.page,
        r.willis && r.willis.matchup, r.willis && r.willis.date,
        r.model && r.model.matchup, r.model && r.model.date,
      ].filter(Boolean).join(' ').toLowerCase();
      if (!hay.includes(term)) return false;
    }
    return true;
  });

  const byPage = new Map();
  for (const r of filtered) {
    if (!byPage.has(r.page)) byPage.set(r.page, []);
    byPage.get(r.page).push(r);
  }

  pagesEl.innerHTML = '';
  for (const [page, pageRows] of [...byPage.entries()].sort((a, b) => a[0] - b[0])) {
    const block = document.createElement('div');
    block.className = 'page-block';

    const padded = String(page).padStart(4, '0');
    const imgUrl = IMG_URL.replace('{page}', padded);
    const header = document.createElement('div');
    header.className = 'page-header';
    header.innerHTML = '<h3>Page ' + esc(page) + '</h3>' +
      '<button class="toggle-img" data-img="' + esc(imgUrl) + '">Show page image</button>';
    block.appendChild(header);

    const imgContainer = document.createElement('div');
    imgContainer.className = 'page-preview';
    imgContainer.style.display = 'none';
    block.appendChild(imgContainer);

    const colHeaders = document.createElement('div');
    colHeaders.className = 'col-headers';
    colHeaders.innerHTML = '<div class="cmp-col">Willis</div><div class="cmp-col">' +
      esc(modelSel.value) + '</div><div class="cmp-status"></div>';
    block.appendChild(colHeaders);

    for (const r of pageRows) {
      const row = document.createElement('div');
      row.className = 'cmp-row status-' + r.status;
      const willisHtml = r.willis
        ? esc(r.willis.matchup) + (r.willis.date ? ' <small>(' + esc(r.willis.date) + ')</small>' : '')
        : '<span class="empty-cell">&mdash;</span>';
      const modelHtml = r.model
        ? esc(r.model.matchup) + (r.model.date ? ' <small>(' + esc(r.model.date) + ')</small>' : '')
        : '<span class="empty-cell">&mdash;</span>';
      row.innerHTML =
        '<div class="cmp-col willis">' + willisHtml + '</div>' +
        '<div class="cmp-col">' + modelHtml + '</div>' +
        '<div class="cmp-status">' + esc(r.status) + '</div>';
      block.appendChild(row);
    }

    pagesEl.appendChild(block);
  }

  meta.textContent = filtered.length + ' row(s) across ' + byPage.size + ' page(s)';
}

document.addEventListener('click', function(e) {
  const btn = e.target.closest('.toggle-img');
  if (!btn) return;
  const url = btn.dataset.img;
  const container = btn.closest('.page-header').nextElementSibling;
  if (container.style.display === 'none') {
    container.style.display = '';
    if (!container.innerHTML) {
      container.innerHTML = '<img loading="lazy" src="' + url + '">';
    }
    btn.textContent = 'Hide page image';
  } else {
    container.style.display = 'none';
    btn.textContent = 'Show page image';
  }
});

render();
</script>
</body>
</html>
"""
```

**Step 4: Run the tests to verify they pass**

Run: `uv run pytest tests/test_willis_compare.py -v`
Expected: PASS (all tests from Tasks 1–3)

Also run the full test suite to make sure nothing else broke:
Run: `uv run pytest -q`
Expected: PASS

**Step 5: Commit**

```bash
git add tonywebb/willis_compare.py tests/test_willis_compare.py
git commit -m "$(cat <<'EOF'
Add HTML/JS template for willis-compare browser

Two-column page-by-page layout (Willis | model), model dropdown,
search/status/content-type filters, and a lazy-loaded page-image
toggle -- same self-contained-HTML pattern as compare_browser.html.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 4: Manual verification against real data

**Files:** none (verification only)

**Step 1: Generate the real comparison page**

Run: `uv run tonywebb willis-compare`
Expected: `Wrote browser/willis_compare.html (N model(s) vs match_indexes/match_index_willis.csv)` — N should match the number of `match_indexes/match_index_*.csv` files minus the truth file itself.

**Step 2: Open it and check the layout**

Open `browser/willis_compare.html` in a browser (e.g. via the Browser pane's `preview_start`/`navigate` tools, or just double-click it locally). Select `reconciled_glm` from the model dropdown and confirm:
- Page blocks render in ascending page order
- Page 24 shows a Willis row aligned with a matched model row (this is the page fixed earlier this session — a good known-good check)
- A page in the 62–247 range shows `unindexed` rows with an empty Willis column
- The status filter dropdown correctly isolates `missed` / `surplus` / `unindexed` rows
- Clicking "Show page image" on a page block loads the scan

**Step 3: Confirm switching models works without regenerating**

Switch the model dropdown to `glm52_cleaned` (or another available CSV) and confirm the page blocks re-render with that model's data, and the content-type filter options refresh accordingly.

**Step 4: Note anything visually off**

If page 247 (fixed a few turns ago) still shows odd data, or if any page block looks broken, capture it — that's a bug to fix before considering this done, not a new task to defer.

No commit for this task — it's verification of Tasks 1–3's already-committed work. If it surfaces a bug, fix it as a follow-up commit on top of the relevant task.
