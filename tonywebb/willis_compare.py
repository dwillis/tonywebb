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
    # Filled in with the real two-column page-by-page template in Task 3.
    # The <script id="data"> wrapper matches build_browser.py's convention
    # so this task's tests (which only check the embedded models list and
    # file existence) pass without depending on Task 3's work.
    return (
        '<!doctype html><html><body>'
        '<script id="data" type="application/json">__DATA__</script>'
        '</body></html>'
    )


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
