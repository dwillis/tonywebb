"""Generate a self-contained HTML browser for match_index_*.csv comparisons.

One row per unique (matchup, page, date) across all files; a column per model
with a checkmark when that model has the row. Includes search and agreement-
count filters. Open compare_browser.html in a browser.
"""

import csv
import glob
import html
import json
import os

from normalize import matchup_key as normalize_matchup, normalize_date


def label(path: str) -> str:
    base = os.path.basename(path)
    return base.removeprefix("match_index_").removesuffix(".csv")


def load_rows(path: str) -> dict[tuple[str, str, str], dict]:
    """Return {(norm_matchup, page, date): row_dict_with_original_fields}."""
    out: dict[tuple[str, str, str], dict] = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            matchup = normalize_matchup(row.get("matchup", ""))
            page = (row.get("page") or "").strip()
            date = normalize_date(row.get("date", ""))
            if matchup and date:
                out[(matchup, page, date)] = {
                    "matchup": (row.get("matchup") or "").strip(),
                    "page": page,
                    "content_type": (row.get("content_type") or "").strip(),
                    "collection": (row.get("collection") or "").strip(),
                    "record_id": (row.get("record_id") or "").strip(),
                }
    return out


def main() -> None:
    files = sorted(glob.glob("match_index_*.csv"))
    if not files:
        print("No match_index_*.csv files found.")
        return

    names = [label(p) for p in files]
    per_model = {label(p): load_rows(p) for p in files}

    union: set[tuple[str, str, str]] = set()
    for d in per_model.values():
        union.update(d.keys())

    def page_sort(key):
        try:
            return (int(key[1]), key[2], key[0])
        except ValueError:
            return (10**9, key[2], key[0])

    rows = []
    for key in sorted(union, key=page_sort):
        norm_matchup, page_num, date = key
        display_matchup = norm_matchup
        details: dict[str, dict] = {}
        present = []
        for n in names:
            if key in per_model[n]:
                present.append(n)
                details[n] = per_model[n][key]
                if display_matchup == norm_matchup:
                    display_matchup = per_model[n][key]["matchup"]
        rows.append(
            {
                "matchup": display_matchup,
                "page": page_num,
                "date": date,
                "present": present,
                "count": len(present),
                "details": details,
            }
        )

    data_json = json.dumps({"models": names, "rows": rows}, ensure_ascii=False)

    page = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Match Index Browser</title>
<style>
  :root { color-scheme: light dark; }
  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 1rem; }
  header { display: flex; flex-wrap: wrap; gap: .75rem; align-items: center; margin-bottom: 1rem; }
  input[type=search] { padding: .4rem .6rem; min-width: 280px; font-size: 1rem; }
  select, button { padding: .35rem .55rem; font-size: .95rem; }
  table { border-collapse: collapse; width: 100%; font-size: .9rem; }
  th, td { border-bottom: 1px solid #ccc3; padding: .35rem .5rem; text-align: left; vertical-align: top; }
  th { position: sticky; top: 0; background: Canvas; cursor: pointer; user-select: none; }
  th.num, td.num { text-align: right; font-variant-numeric: tabular-nums; }
  td.check { text-align: center; }
  td.yes { background: #2ecc7022; color: #1a8f4d; font-weight: 600; }
  td.no { color: #aaa; }
  tr.expanded td { border-bottom: 0; }
  tr.detail-row td { background: #00000008; padding: .5rem 1rem; }
  tr.detail-row pre { margin: 0; white-space: pre-wrap; font-size: .82rem; }
  .meta { color: #888; font-size: .85rem; margin-left: auto; }
  .pill { display: inline-block; padding: 1px 6px; border-radius: 8px; background: #00000010; font-size: .75rem; margin-right: 4px; }
</style>
</head>
<body>
<header>
  <h2 style="margin:0">Match Index Browser</h2>
  <input id="q" type="search" placeholder="Search matchup or date…">
  <label>Agreement:
    <select id="agreement">
      <option value="all">any</option>
      <option value="unique">only 1 model</option>
      <option value="disagree">disagreement (&lt; all models)</option>
      <option value="all-agree">all models agree</option>
    </select>
  </label>
  <label>Model:
    <select id="model"><option value="">(any)</option></select>
  </label>
  <span class="meta" id="meta"></span>
</header>
<table id="t">
  <thead><tr id="head"></tr></thead>
  <tbody id="body"></tbody>
</table>
<script id="data" type="application/json">__DATA__</script>
<script>
const DATA = JSON.parse(document.getElementById('data').textContent);
const MODELS = DATA.models;
const ROWS = DATA.rows;

const head = document.getElementById('head');
const PAGE_URL = 'https://archive.acscricket.com/research/tw/tw_newspaper_cuttings_1895/{page}/index.html';
const cols = [
  {key:'page', label:'Page', cls:'num'},
  {key:'matchup', label:'Matchup'},
  {key:'date', label:'Date'},
  {key:'count', label:'#', cls:'num'},
];
for (const c of cols) {
  const th = document.createElement('th');
  th.textContent = c.label;
  th.dataset.key = c.key;
  if (c.cls) th.className = c.cls;
  head.appendChild(th);
}
for (const m of MODELS) {
  const th = document.createElement('th');
  th.textContent = m;
  th.dataset.key = 'm:' + m;
  th.className = 'check';
  head.appendChild(th);
}

const modelSel = document.getElementById('model');
for (const m of MODELS) {
  const o = document.createElement('option');
  o.value = m; o.textContent = m;
  modelSel.appendChild(o);
}

let sortKey = 'page', sortDir = 1;
head.addEventListener('click', e => {
  const th = e.target.closest('th'); if (!th) return;
  const k = th.dataset.key;
  if (sortKey === k) sortDir = -sortDir; else { sortKey = k; sortDir = 1; }
  render();
});

const body = document.getElementById('body');
const meta = document.getElementById('meta');
const q = document.getElementById('q');
const agreement = document.getElementById('agreement');

[q, agreement, modelSel].forEach(el => el.addEventListener('input', render));

function render() {
  const term = q.value.trim().toLowerCase();
  const ag = agreement.value;
  const onlyModel = modelSel.value;

  let rows = ROWS.filter(r => {
    if (term && !((r.matchup + ' ' + r.date + ' ' + r.page).toLowerCase().includes(term))) return false;
    if (ag === 'unique' && r.count !== 1) return false;
    if (ag === 'all-agree' && r.count !== MODELS.length) return false;
    if (ag === 'disagree' && r.count === MODELS.length) return false;
    if (onlyModel && !r.present.includes(onlyModel)) return false;
    return true;
  });

  rows.sort((a, b) => {
    let av, bv;
    if (sortKey.startsWith('m:')) {
      const m = sortKey.slice(2);
      av = a.present.includes(m) ? 1 : 0;
      bv = b.present.includes(m) ? 1 : 0;
    } else if (sortKey === 'page') {
      av = parseInt(a.page, 10); bv = parseInt(b.page, 10);
      if (Number.isNaN(av)) av = Infinity;
      if (Number.isNaN(bv)) bv = Infinity;
    } else {
      av = a[sortKey]; bv = b[sortKey];
    }
    if (av < bv) return -sortDir;
    if (av > bv) return sortDir;
    return 0;
  });

  body.innerHTML = '';
  for (const r of rows) {
    const tr = document.createElement('tr');
    tr.dataset.key = r.matchup + '|' + r.page + '|' + r.date;
    const pageCell = r.page
      ? '<td class="num"><a href="' + PAGE_URL.replace('{page}', encodeURIComponent(r.page)) + '" target="_blank" rel="noopener">' + escapeHtml(r.page) + '</a></td>'
      : '<td class="num"></td>';
    tr.innerHTML =
      pageCell +
      '<td>' + escapeHtml(r.matchup) + '</td>' +
      '<td>' + escapeHtml(r.date) + '</td>' +
      '<td class="num">' + r.count + '/' + MODELS.length + '</td>' +
      MODELS.map(m => r.present.includes(m)
        ? '<td class="check yes">✓</td>'
        : '<td class="check no">·</td>').join('');
    tr.addEventListener('click', e => {
      if (e.target.closest('a')) return;
      toggleDetail(tr, r);
    });
    body.appendChild(tr);
  }
  meta.textContent = rows.length + ' of ' + ROWS.length + ' rows';
}

function toggleDetail(tr, r) {
  const next = tr.nextElementSibling;
  if (next && next.classList.contains('detail-row')) {
    next.remove(); tr.classList.remove('expanded'); return;
  }
  tr.classList.add('expanded');
  const dr = document.createElement('tr');
  dr.className = 'detail-row';
  const td = document.createElement('td');
  td.colSpan = 4 + MODELS.length;
  const blocks = MODELS.map(m => {
    const d = r.details[m];
    if (!d) return '<div><span class="pill">' + m + '</span><em>not present</em></div>';
    return '<div><span class="pill">' + m + '</span>' +
      'matchup="' + escapeHtml(d.matchup) + '" page=' + escapeHtml(d.page) +
      ' content_type=' + escapeHtml(d.content_type) +
      (d.record_id ? ' record_id=' + escapeHtml(d.record_id) : '') +
      '</div>';
  }).join('');
  td.innerHTML = blocks;
  dr.appendChild(td);
  tr.after(dr);
}

function escapeHtml(s) {
  return String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

render();
</script>
</body>
</html>
"""
    out_path = "compare_browser.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(page.replace("__DATA__", data_json))
    print(f"Wrote {out_path} ({len(rows)} unique keys, {len(names)} models)")


if __name__ == "__main__":
    main()
