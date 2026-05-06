"""Generate a self-contained HTML browser for match_index_*.csv comparisons.

Rows are grouped by (matchup_key, page, content_type) to merge entries that
differ only by date. Each row shows model agreement, confidence score,
date/matchup disagreements, and a review queue with localStorage persistence.

Open compare_browser.html in a browser.
"""

import csv
import glob
import json
import os
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path

from normalize import ClubRegistry, matchup_key, normalize_date, title_key


def label(path: str) -> str:
    base = os.path.basename(path)
    return base.removeprefix("match_index_").removesuffix(".csv")


def load_rows(path: str) -> dict[tuple[str, str, str, str], dict]:
    """Return {(norm_key, page, date, content_type): row_dict}."""
    out: dict[tuple[str, str, str, str], dict] = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            content_type = (row.get("content_type") or "match information").strip().lower()
            raw_title = row.get("matchup", "")
            if content_type == "match information":
                key = matchup_key(raw_title)
            else:
                key = title_key(raw_title)
            page = (row.get("page") or "").strip()
            date = normalize_date(row.get("date", ""))
            if key and date:
                out[(key, page, date, content_type)] = {
                    "matchup": (row.get("matchup") or "").strip(),
                    "page": page,
                    "date": date,
                    "content_type": content_type,
                    "collection": (row.get("collection") or "").strip(),
                    "record_id": (row.get("record_id") or "").strip(),
                }
    return out


def compute_confidence(present, details, total_models):
    count = len(present)
    has_willis = "willis" in present

    # Factor 1: model agreement (0.50)
    if total_models <= 1:
        agree = 1.0
    else:
        agree = (count - 1) / (total_models - 1)
    if has_willis:
        agree = min(1.0, agree * 1.2)

    # Factor 2: date consensus (0.30)
    dates_seen: dict[str, int] = {}
    for m in present:
        d = details[m]["date"]
        dates_seen[d] = dates_seen.get(d, 0) + 1
    if dates_seen:
        majority = max(dates_seen.values())
        date_score = majority / count
    else:
        date_score = 0.0

    # Factor 3: matchup text similarity (0.20)
    matchup_texts = [details[m]["matchup"] for m in present]
    if count <= 1:
        text_score = 0.0
    elif count == 2:
        text_score = SequenceMatcher(
            None, matchup_texts[0].lower(), matchup_texts[1].lower()
        ).ratio()
    else:
        sims = []
        for i in range(len(matchup_texts)):
            for j in range(i + 1, len(matchup_texts)):
                sims.append(
                    SequenceMatcher(
                        None, matchup_texts[i].lower(), matchup_texts[j].lower()
                    ).ratio()
                )
        text_score = sum(sims) / len(sims) if sims else 1.0

    return round(0.50 * agree + 0.30 * date_score + 0.20 * text_score, 3)


def main() -> None:
    files = sorted(glob.glob("match_index_*.csv"))
    if not files:
        print("No match_index_*.csv files found.")
        return

    names = [label(p) for p in files]
    per_model = {label(p): load_rows(p) for p in files}
    total_models = len(names)

    # Load club registry for unknown-team flagging
    registry = ClubRegistry("clubs.csv") if Path("clubs.csv").exists() else None

    # Collect all entries grouped by (norm_key, page, content_type) ignoring date
    groups: dict[tuple[str, str, str], list[tuple[str, str, dict]]] = defaultdict(list)
    for model_name in names:
        for (norm_key, page, date, ct), detail in per_model[model_name].items():
            groups[(norm_key, page, ct)].append((date, model_name, detail))

    def page_sort(key):
        try:
            return (int(key[1]), key[2], key[0])
        except ValueError:
            return (10**9, key[2], key[0])

    rows = []
    for group_key in sorted(groups, key=page_sort):
        norm_key, page_num, content_type = group_key
        entries = groups[group_key]

        # Determine majority date
        date_counts = Counter(date for date, _, _ in entries)
        majority_date = date_counts.most_common(1)[0][0]
        has_date_conflict = len(date_counts) > 1

        # Build details and present list (deduplicate models)
        details: dict[str, dict] = {}
        present: list[str] = []
        display_matchup = norm_key
        for date, model_name, detail in entries:
            if model_name not in details:
                present.append(model_name)
            details[model_name] = {**detail, "date": date}
            if display_matchup == norm_key:
                display_matchup = detail["matchup"]

        # Date variants per model
        date_variants = {m: details[m]["date"] for m in present}

        # Confidence score
        confidence = compute_confidence(present, details, total_models)

        # Unknown teams check
        unknown_teams = []
        if registry and content_type == "match information":
            if " v " in display_matchup.lower():
                parts = display_matchup.split(" v ", 1)
                for t in parts:
                    t = t.strip()
                    if t and not registry.is_known(t):
                        unknown_teams.append(t)

        rows.append(
            {
                "matchup": display_matchup,
                "page": page_num,
                "date": majority_date,
                "content_type": content_type,
                "present": present,
                "count": len(present),
                "confidence": confidence,
                "details": details,
                "date_variants": date_variants,
                "has_date_conflict": has_date_conflict,
                "unknown_teams": unknown_teams,
            }
        )

    data_json = json.dumps(
        {"models": names, "rows": rows, "total_models": total_models},
        ensure_ascii=False,
    )

    page = _build_html()
    out_path = "compare_browser.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(page.replace("__DATA__", data_json))

    # Stats
    conflict_count = sum(1 for r in rows if r["has_date_conflict"])
    low_conf = sum(1 for r in rows if r["confidence"] < 0.4)
    print(f"Wrote {out_path} ({len(rows)} rows, {len(names)} models)")
    print(f"  {conflict_count} rows with date conflicts")
    print(f"  {low_conf} low-confidence rows (< 0.4)")


def _build_html() -> str:
    return """<!doctype html>
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
  th { position: sticky; top: 0; background: Canvas; cursor: pointer; user-select: none; z-index: 2; }
  th.num, td.num { text-align: right; font-variant-numeric: tabular-nums; }
  td.check { text-align: center; }
  td.yes { background: #2ecc7022; color: #1a8f4d; font-weight: 600; }
  td.no { color: #aaa; }

  /* Confidence color coding */
  tr.conf-high td:first-child { border-left: 4px solid #28a745; }
  tr.conf-med td:first-child { border-left: 4px solid #ffc107; }
  tr.conf-low td:first-child { border-left: 4px solid #dc3545; }
  tr.conf-low { background: #f8d7da22; }
  tr.conf-med { background: #fff3cd22; }

  /* Date conflict indicator */
  .date-conflict { color: #dc3545; font-weight: 600; }
  .unknown-team { color: #dc3545; cursor: help; }

  /* Detail row */
  tr.expanded td { border-bottom: 0; }
  tr.detail-row td { background: #00000008; padding: .5rem 1rem; }
  .disagreement { margin: .3rem 0; padding: .3rem .5rem; border-radius: 4px; font-size: .85rem; }
  .date-disagree { background: #f8d7da44; }
  .matchup-disagree { background: #fff3cd44; }
  .pill { display: inline-block; padding: 1px 6px; border-radius: 8px; background: #00000010; font-size: .75rem; margin-right: 4px; }
  .meta { color: #888; font-size: .85rem; margin-left: auto; }

  /* Page image */
  .page-preview { margin-top: .5rem; }
  .page-preview img { max-width: 100%; max-height: 600px; border: 1px solid #ccc; margin-top: .3rem; }
  .toggle-img { font-size: .82rem; cursor: pointer; background: #eee; border: 1px solid #ccc; border-radius: 3px; padding: 2px 8px; }

  /* Review controls */
  .review-controls { margin-top: .5rem; display: flex; gap: .5rem; align-items: center; flex-wrap: wrap; }
  .review-controls button { padding: 3px 10px; border-radius: 4px; border: 1px solid #ccc; cursor: pointer; font-size: .82rem; }
  .btn-accept { background: #d4edda; border-color: #28a745; }
  .btn-accept.active { background: #28a745; color: white; }
  .btn-reject { background: #f8d7da; border-color: #dc3545; }
  .btn-reject.active { background: #dc3545; color: white; }
  .btn-skip { background: #e2e3e5; }
  .btn-skip.active { background: #6c757d; color: white; }
  .review-notes { font-size: .82rem; padding: 3px 6px; flex: 1; min-width: 200px; }
  .review-status { font-size: .78rem; padding: 2px 6px; border-radius: 3px; }
  .status-accepted { background: #d4edda; color: #155724; }
  .status-rejected { background: #f8d7da; color: #721c24; }
  .status-skipped { background: #e2e3e5; color: #383d41; }

  /* Progress bar */
  .progress-bar { height: 4px; background: #e9ecef; border-radius: 2px; margin-top: .3rem; }
  .progress-fill { height: 100%; background: #28a745; border-radius: 2px; transition: width 0.3s; }

  /* Export button */
  .export-btn { background: #007bff; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: .9rem; }
  .export-btn:hover { background: #0056b3; }
</style>
</head>
<body>
<header>
  <h2 style="margin:0">Match Index Browser</h2>
  <input id="q" type="search" placeholder="Search matchup, date, or page...">
  <label>Agreement:
    <select id="agreement">
      <option value="all">any</option>
      <option value="unique">only 1 model</option>
      <option value="disagree">disagreement (&lt; all models)</option>
      <option value="all-agree">all models agree</option>
      <option value="date-conflict">date conflicts</option>
      <option value="unknown-team">unknown teams</option>
    </select>
  </label>
  <label>Confidence:
    <select id="confidence">
      <option value="all">any</option>
      <option value="low">low (&lt; 0.4)</option>
      <option value="med">medium (0.4-0.7)</option>
      <option value="high">high (&ge; 0.7)</option>
    </select>
  </label>
  <label>Model:
    <select id="model"><option value="">(any)</option></select>
  </label>
  <label>Mode:
    <select id="mode">
      <option value="browse">Browse</option>
      <option value="review">Review Queue</option>
    </select>
  </label>
  <button class="export-btn" id="exportBtn">Export Reviewed CSV</button>
  <span class="meta" id="meta"></span>
</header>
<div id="progressContainer" style="display:none">
  <span id="progressText" style="font-size:.85rem;color:#666"></span>
  <div class="progress-bar"><div class="progress-fill" id="progressFill"></div></div>
</div>
<table id="t">
  <thead><tr id="head"></tr></thead>
  <tbody id="body"></tbody>
</table>
<script id="data" type="application/json">__DATA__</script>
<script>
const DATA = JSON.parse(document.getElementById('data').textContent);
const MODELS = DATA.models;
const ROWS = DATA.rows;
const TOTAL_MODELS = DATA.total_models;

const IMG_URL = 'https://archive.acscricket.com/research/tw/tw_newspaper_cuttings_1895/files/assets/common/page-html5-substrates/page{page}_5.jpg';
const PAGE_URL = 'https://archive.acscricket.com/research/tw/tw_newspaper_cuttings_1895/{page}/index.html';

// Review state (localStorage)
function getReviewState() {
  try { return JSON.parse(localStorage.getItem('review_state') || '{}'); } catch(e) { return {}; }
}
function setReviewState(state) {
  localStorage.setItem('review_state', JSON.stringify(state));
}
function rowKey(r) { return r.matchup + '|' + r.page + '|' + r.date + '|' + r.content_type; }

const head = document.getElementById('head');
const cols = [
  {key:'page', label:'Page', cls:'num'},
  {key:'matchup', label:'Matchup'},
  {key:'date', label:'Date'},
  {key:'content_type', label:'Type'},
  {key:'confidence', label:'Conf', cls:'num'},
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
const confidenceSel = document.getElementById('confidence');
const modeSel = document.getElementById('mode');
const progressContainer = document.getElementById('progressContainer');
const progressText = document.getElementById('progressText');
const progressFill = document.getElementById('progressFill');

[q, agreement, confidenceSel, modelSel, modeSel].forEach(el => el.addEventListener('input', render));

function render() {
  const term = q.value.trim().toLowerCase();
  const ag = agreement.value;
  const conf = confidenceSel.value;
  const onlyModel = modelSel.value;
  const isReview = modeSel.value === 'review';
  const reviewState = getReviewState();

  let rows = ROWS.filter(r => {
    if (term && !((r.matchup + ' ' + r.date + ' ' + r.page + ' ' + r.content_type).toLowerCase().includes(term))) return false;
    if (ag === 'unique' && r.count !== 1) return false;
    if (ag === 'all-agree' && r.count !== TOTAL_MODELS) return false;
    if (ag === 'disagree' && r.count === TOTAL_MODELS) return false;
    if (ag === 'date-conflict' && !r.has_date_conflict) return false;
    if (ag === 'unknown-team' && (!r.unknown_teams || r.unknown_teams.length === 0)) return false;
    if (conf === 'low' && r.confidence >= 0.4) return false;
    if (conf === 'med' && (r.confidence < 0.4 || r.confidence >= 0.7)) return false;
    if (conf === 'high' && r.confidence < 0.7) return false;
    if (onlyModel && !r.present.includes(onlyModel)) return false;
    if (isReview) {
      const state = reviewState[rowKey(r)];
      if (state && state.status) return false; // hide already-reviewed
    }
    return true;
  });

  if (isReview) {
    rows.sort((a, b) => a.confidence - b.confidence);
    // Show progress
    const totalReviewable = ROWS.filter(r => r.confidence < 0.7).length;
    const reviewed = Object.values(reviewState).filter(s => s.status).length;
    progressContainer.style.display = '';
    progressText.textContent = reviewed + ' / ' + totalReviewable + ' reviewed';
    progressFill.style.width = (totalReviewable ? (reviewed / totalReviewable * 100) : 0) + '%';
  } else {
    progressContainer.style.display = 'none';
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
      } else if (sortKey === 'confidence') {
        av = a.confidence; bv = b.confidence;
      } else if (sortKey === 'count') {
        av = a.count; bv = b.count;
      } else {
        av = a[sortKey]; bv = b[sortKey];
      }
      if (av < bv) return -sortDir;
      if (av > bv) return sortDir;
      return 0;
    });
  }

  body.innerHTML = '';
  for (const r of rows) {
    const tr = document.createElement('tr');
    const confClass = r.confidence >= 0.7 ? 'conf-high' :
                      r.confidence >= 0.4 ? 'conf-med' : 'conf-low';
    tr.className = confClass;

    const pageCell = r.page
      ? '<td class="num"><a href="' + PAGE_URL.replace('{page}', encodeURIComponent(r.page)) + '" target="_blank" rel="noopener">' + esc(r.page) + '</a></td>'
      : '<td class="num"></td>';

    const dateHtml = r.has_date_conflict
      ? '<td><span class="date-conflict" title="Models disagree on date">' + esc(r.date) + ' !</span></td>'
      : '<td>' + esc(r.date) + '</td>';

    let matchupHtml = esc(r.matchup);
    if (r.unknown_teams && r.unknown_teams.length > 0) {
      matchupHtml += ' <span class="unknown-team" title="Unrecognized: ' + esc(r.unknown_teams.join(', ')) + '">?</span>';
    }
    // Show review status inline if already reviewed
    const rState = reviewState[rowKey(r)];
    if (rState && rState.status) {
      const cls = 'review-status status-' + rState.status;
      matchupHtml += ' <span class="' + cls + '">' + rState.status + '</span>';
    }

    tr.innerHTML =
      pageCell +
      '<td>' + matchupHtml + '</td>' +
      dateHtml +
      '<td>' + esc(r.content_type) + '</td>' +
      '<td class="num">' + r.confidence.toFixed(2) + '</td>' +
      '<td class="num">' + r.count + '/' + TOTAL_MODELS + '</td>' +
      MODELS.map(m => r.present.includes(m)
        ? '<td class="check yes">&#10003;</td>'
        : '<td class="check no">&middot;</td>').join('');
    tr.addEventListener('click', e => {
      if (e.target.closest('a') || e.target.closest('button') || e.target.closest('input')) return;
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
  td.colSpan = 6 + MODELS.length;

  let html = '';

  // Date disagreement
  if (r.has_date_conflict) {
    const dateGroups = {};
    for (const m of r.present) {
      const d = r.date_variants[m] || r.date;
      (dateGroups[d] = dateGroups[d] || []).push(m);
    }
    html += '<div class="disagreement date-disagree">Date conflict: ';
    html += Object.entries(dateGroups)
      .sort((a, b) => b[1].length - a[1].length)
      .map(([d, models]) => '<strong>' + esc(d) + '</strong> (' + models.join(', ') + ')')
      .join(' vs ');
    html += '</div>';
  }

  // Matchup text variants
  const matchupGroups = {};
  for (const m of r.present) {
    const t = r.details[m].matchup;
    (matchupGroups[t] = matchupGroups[t] || []).push(m);
  }
  if (Object.keys(matchupGroups).length > 1) {
    html += '<div class="disagreement matchup-disagree">Matchup variants: ';
    html += Object.entries(matchupGroups)
      .sort((a, b) => b[1].length - a[1].length)
      .map(([t, models]) => '"' + esc(t) + '" (' + models.join(', ') + ')')
      .join(' | ');
    html += '</div>';
  }

  // Per-model details
  html += '<div style="margin-top:.4rem">';
  for (const m of MODELS) {
    const d = r.details[m];
    if (!d) {
      html += '<div><span class="pill">' + m + '</span><em>not present</em></div>';
    } else {
      html += '<div><span class="pill">' + m + '</span>' +
        'matchup="' + esc(d.matchup) + '" date=' + esc(d.date) +
        ' type=' + esc(d.content_type) +
        (d.record_id ? ' id=' + esc(d.record_id) : '') +
        '</div>';
    }
  }
  html += '</div>';

  // Page image toggle
  const padded = String(r.page).padStart(4, '0');
  const imgUrl = IMG_URL.replace('{page}', padded);
  html += '<div class="page-preview">' +
    '<button class="toggle-img" data-img="' + esc(imgUrl) + '">Show page image</button>' +
    '<div class="img-container" style="display:none"></div>' +
    '</div>';

  // Review controls
  const rk = rowKey(r);
  const reviewState = getReviewState();
  const current = reviewState[rk] || {};
  const rkAttr = esc(rk);
  html += '<div class="review-controls" data-rk="' + rkAttr + '">' +
    '<button class="btn-accept' + (current.status === 'accepted' ? ' active' : '') + '" data-action="accepted">Accept</button>' +
    '<button class="btn-reject' + (current.status === 'rejected' ? ' active' : '') + '" data-action="rejected">Reject</button>' +
    '<button class="btn-skip' + (current.status === 'skipped' ? ' active' : '') + '" data-action="skipped">Skip</button>' +
    '<input class="review-notes" placeholder="Notes..." value="' + esc(current.notes || '') + '">' +
    '</div>';

  td.innerHTML = html;
  dr.appendChild(td);
  tr.after(dr);
}

document.addEventListener('click', function(e) {
  var btn = e.target.closest('.toggle-img');
  if (!btn) return;
  var url = btn.dataset.img;
  var container = btn.nextElementSibling;
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

// Review button delegation
document.addEventListener('click', function(e) {
  var btn = e.target.closest('[data-action]');
  if (!btn) return;
  var container = btn.closest('.review-controls');
  if (!container) return;
  var key = container.dataset.rk;
  var status = btn.dataset.action;
  var state = getReviewState();
  if (state[key] && state[key].status === status) {
    delete state[key].status;
  } else {
    state[key] = state[key] || {};
    state[key].status = status;
    state[key].timestamp = new Date().toISOString();
  }
  setReviewState(state);
  container.querySelectorAll('button').forEach(function(b) { b.classList.remove('active'); });
  if (state[key] && state[key].status) {
    btn.classList.add('active');
  }
});

// Review notes delegation
document.addEventListener('change', function(e) {
  if (!e.target.classList.contains('review-notes')) return;
  var container = e.target.closest('.review-controls');
  if (!container) return;
  var key = container.dataset.rk;
  var state = getReviewState();
  state[key] = state[key] || {};
  state[key].notes = e.target.value;
  setReviewState(state);
});

// Export reviewed entries as CSV
document.getElementById('exportBtn').addEventListener('click', () => {
  const state = getReviewState();
  const accepted = ROWS.filter(r => {
    const s = state[rowKey(r)];
    return s && s.status === 'accepted';
  });
  if (accepted.length === 0) {
    alert('No accepted entries to export. Review and accept entries first.');
    return;
  }
  let csv = 'matchup,page,date,content_type,collection,record_id,notes\\n';
  for (const r of accepted) {
    const s = state[rowKey(r)];
    const notes = (s.notes || '').replace(/"/g, '""');
    csv += '"' + r.matchup.replace(/"/g, '""') + '",' +
      r.page + ',' + r.date + ',' +
      '"' + r.content_type + '",' +
      '"Tony Webb minor counties collection",' +
      ',' +
      '"' + notes + '"\\n';
  }
  const blob = new Blob([csv], {type: 'text/csv'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'match_index_reviewed.csv';
  a.click();
  URL.revokeObjectURL(url);
});

function esc(s) {
  return String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

render();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
