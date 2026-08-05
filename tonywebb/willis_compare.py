"""Build side-by-side comparison rows for a match_index_<model>.csv against
match_index_willis.csv. See willis_compare.run_willis_compare() for the HTML
generation this feeds into.
"""

from __future__ import annotations

import glob
import json
from pathlib import Path

from . import evaluate
from .build_browser import label


def _row(page: int, status: str, content_type: str, willis: dict | None, model: dict | None, similarity: float | None) -> dict:
    """Single source of truth for the row schema -- Task 3's HTML/JS template
    depends key-for-key on this shape, so every branch below builds rows
    through here rather than duplicating the dict literal.
    """
    return {
        "page": page,
        "status": status,
        "content_type": content_type,
        "willis": willis,
        "model": model,
        "similarity": similarity,
    }


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
        rows.append(_row(
            page=pair.truth.page,
            status="matched",
            content_type=pair.truth.content_type,
            willis={"matchup": pair.truth.matchup, "date": pair.truth.date},
            model={"matchup": pair.model.matchup, "date": pair.model.date},
            similarity=pair.similarity,
        ))
    for r in result.missed:
        rows.append(_row(
            page=r.page,
            status="missed",
            content_type=r.content_type,
            willis={"matchup": r.matchup, "date": r.date},
            model=None,
            similarity=None,
        ))
    for r in result.surplus:
        rows.append(_row(
            page=r.page,
            status="surplus",
            content_type=r.content_type,
            willis=None,
            model={"matchup": r.matchup, "date": r.date},
            similarity=None,
        ))
    for r in model_rows:
        if r.page not in covered:
            rows.append(_row(
                page=r.page,
                status="unindexed",
                content_type=r.content_type,
                willis=None,
                model={"matchup": r.matchup, "date": r.date},
                similarity=None,
            ))

    # Primary sort by page; secondary sort by matchup text (from whichever
    # side has a row) so ordering within a page is stable and deterministic.
    rows.sort(key=lambda r: (r["page"], (r["willis"] or r["model"] or {}).get("matchup", "")))
    return rows


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
