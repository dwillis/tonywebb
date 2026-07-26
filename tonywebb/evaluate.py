"""Evaluate a match_index_<model>.csv against the Willis ground-truth index.

Willis is a PARTIAL manual index (388 rows, pages 1-61 only) rather than a
complete ground truth, so this treats "Willis coverage" (recall against the
rows Willis has) as the headline metric, and reports surplus model rows as a
human-review list rather than calling them false positives -- Willis may
simply not have gotten to them.
"""

from __future__ import annotations

import csv
import glob
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path

from .normalize import normalize_date, symmetric_matchup_key, title_key
from .pipeline import parse_page_spec


@dataclass
class IndexRow:
    matchup: str
    page: int
    date: str
    content_type: str
    pages: int = 1  # how many distinct pages this entry appears on (1 = single page)


def load_index(path: Path) -> tuple[list[IndexRow], list[dict]]:
    """Return (rows, skipped). Skipped rows are reported, never silently dropped."""
    rows: list[IndexRow] = []
    skipped: list[dict] = []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, raw in enumerate(reader, start=2):
            matchup = (raw.get("matchup") or "").strip()
            content_type = (raw.get("content_type") or "").strip().lower()
            try:
                page = int((raw.get("page") or "").strip())
            except (ValueError, TypeError):
                skipped.append({"line": i, "reason": "bad page", "row": raw})
                continue
            if not matchup:
                skipped.append({"line": i, "reason": "empty matchup", "row": raw})
                continue
            if not content_type:
                skipped.append({"line": i, "reason": "empty content_type", "row": raw})
                continue
            date = normalize_date(raw.get("date", ""))
            try:
                pages = int((raw.get("pages") or "").strip())
            except (ValueError, TypeError):
                pages = 1
            rows.append(IndexRow(matchup=matchup, page=page, date=date, content_type=content_type, pages=pages))
    return rows, skipped


def _key(row: IndexRow) -> str:
    # Order-insensitive for matches: sources disagree on which team is
    # listed first (prose word order vs. a manual index's own convention),
    # and neither is "wrong" -- see symmetric_matchup_key()'s docstring.
    return symmetric_matchup_key(row.matchup) if row.content_type == "match information" else title_key(row.matchup)


def _similarity(a: IndexRow, b: IndexRow) -> float:
    return SequenceMatcher(None, _key(a), _key(b)).ratio()


@dataclass
class MatchPair:
    truth: IndexRow
    model: IndexRow
    kind: str  # "exact" | "fuzzy"
    similarity: float


@dataclass
class EvalResult:
    pages_covered: list[int]
    matched: list[MatchPair]
    missed: list[IndexRow]  # in truth, no model match
    surplus: list[IndexRow]  # in model (on a Willis page), no truth match
    date_agree: int
    date_total: int
    type_agree: int
    type_total: int
    pages_agree: int
    pages_total: int


def _match_page(truth_rows: list[IndexRow], model_rows: list[IndexRow], fuzzy_threshold: float) -> tuple[list[MatchPair], list[IndexRow], list[IndexRow]]:
    """Exact pass on (key, content_type), then greedy best-first fuzzy pass on leftovers."""
    used_model: set[int] = set()
    matched: list[MatchPair] = []
    leftover_truth: list[IndexRow] = []

    # Exact pass
    model_by_key: dict[tuple[str, str], list[int]] = {}
    for j, m in enumerate(model_rows):
        model_by_key.setdefault((_key(m), m.content_type), []).append(j)

    for t in truth_rows:
        candidates = model_by_key.get((_key(t), t.content_type), [])
        picked = next((j for j in candidates if j not in used_model), None)
        if picked is not None:
            used_model.add(picked)
            matched.append(MatchPair(truth=t, model=model_rows[picked], kind="exact", similarity=1.0))
        else:
            leftover_truth.append(t)

    # Fuzzy pass on leftovers (same content_type required)
    still_missed: list[IndexRow] = []
    for t in leftover_truth:
        best_j, best_sim = None, 0.0
        for j, m in enumerate(model_rows):
            if j in used_model or m.content_type != t.content_type:
                continue
            sim = _similarity(t, m)
            if sim > best_sim:
                best_j, best_sim = j, sim
        if best_j is not None and best_sim >= fuzzy_threshold:
            used_model.add(best_j)
            matched.append(MatchPair(truth=t, model=model_rows[best_j], kind="fuzzy", similarity=round(best_sim, 3)))
        else:
            still_missed.append(t)

    surplus = [m for j, m in enumerate(model_rows) if j not in used_model]
    return matched, still_missed, surplus


def evaluate(truth_rows: list[IndexRow], model_rows: list[IndexRow], fuzzy_threshold: float = 0.8) -> EvalResult:
    truth_pages = sorted({r.page for r in truth_rows})

    all_matched: list[MatchPair] = []
    all_missed: list[IndexRow] = []
    all_surplus: list[IndexRow] = []

    for page in truth_pages:
        t_page = [r for r in truth_rows if r.page == page]
        m_page = [r for r in model_rows if r.page == page]
        matched, missed, surplus = _match_page(t_page, m_page, fuzzy_threshold)
        all_matched.extend(matched)
        all_missed.extend(missed)
        all_surplus.extend(surplus)

    date_agree = sum(1 for p in all_matched if p.truth.date and p.model.date and p.truth.date == p.model.date)
    date_total = sum(1 for p in all_matched if p.truth.date and p.model.date)

    # "pages" (how many distinct pages this entry spans) agreement among
    # matched pairs -- both sides flag rather than merge cross-page entries,
    # so a matched pair's pages counts should usually agree.
    pages_agree = sum(1 for p in all_matched if p.truth.pages == p.model.pages)
    pages_total = len(all_matched)

    # Content-type agreement measured on a type-blind key match (so it's not
    # trivially 100% for the exact-match pass, which requires type equality
    # by construction).
    type_agree, type_total = _type_agreement(truth_rows, model_rows, truth_pages, fuzzy_threshold)

    return EvalResult(
        pages_covered=truth_pages,
        matched=all_matched,
        missed=all_missed,
        surplus=all_surplus,
        date_agree=date_agree,
        date_total=date_total,
        type_agree=type_agree,
        type_total=type_total,
        pages_agree=pages_agree,
        pages_total=pages_total,
    )


def _type_agreement(truth_rows, model_rows, truth_pages, fuzzy_threshold) -> tuple[int, int]:
    agree, total = 0, 0
    for page in truth_pages:
        t_page = [r for r in truth_rows if r.page == page]
        m_page = [r for r in model_rows if r.page == page]
        used: set[int] = set()
        for t in t_page:
            best_j, best_sim = None, 0.0
            for j, m in enumerate(m_page):
                if j in used:
                    continue
                sim = SequenceMatcher(None, title_key(t.matchup), title_key(m.matchup)).ratio()
                if sim > best_sim:
                    best_j, best_sim = j, sim
            if best_j is not None and best_sim >= fuzzy_threshold:
                used.add(best_j)
                total += 1
                if m_page[best_j].content_type == t.content_type:
                    agree += 1
    return agree, total


def coverage_by_content_type(result: EvalResult, truth_rows: list[IndexRow]) -> dict[str, tuple[int, int]]:
    """{content_type: (matched_count, total_count)} restricted to covered pages."""
    covered = set(result.pages_covered)
    truth_on_covered = [r for r in truth_rows if r.page in covered]
    matched_truth_ids = {id(p.truth) for p in result.matched}
    out: dict[str, list[int]] = {}
    for r in truth_on_covered:
        bucket = out.setdefault(r.content_type, [0, 0])
        bucket[1] += 1
        if id(r) in matched_truth_ids:
            bucket[0] += 1
    return {k: (v[0], v[1]) for k, v in out.items()}


def format_report(
    label: str,
    result: EvalResult,
    truth_rows: list[IndexRow],
    skipped_truth: list[dict],
    skipped_model: list[dict],
    pages_filter: set[int] | None = None,
    content_types_filter: set[str] | None = None,
) -> str:
    total_truth = sum(1 for r in truth_rows if r.page in set(result.pages_covered))
    n_matched = len(result.matched)
    coverage = n_matched / total_truth if total_truth else 0.0
    exact = sum(1 for p in result.matched if p.kind == "exact")
    fuzzy = n_matched - exact

    lines = [
        f"# Evaluation: {label} vs Willis ground truth\n",
    ]
    if pages_filter:
        lines.append(
            f"**Restricted to pages {sorted(pages_filter)}** (--pages was given) — "
            f"coverage below is scoped to only these pages, not the full Willis set.\n"
        )
    if content_types_filter:
        lines.append(
            f"**Restricted to content type(s) {sorted(content_types_filter)}** "
            f"(--content-types was given) — coverage below only counts Willis rows "
            f"of these type(s), not her full mix of content types.\n"
        )
    lines += [
        f"Willis pages covered: {len(result.pages_covered)} "
        f"(pages {min(result.pages_covered)}-{max(result.pages_covered)}; "
        f"no claim made about pages outside this range)\n",
        f"- **Willis coverage (recall): {n_matched}/{total_truth} ({coverage:.1%})**",
        f"- Exact-key matches: {exact}; fuzzy-only matches: {fuzzy}",
        f"- Date agreement (matched pairs, both dated): {result.date_agree}/{result.date_total}"
        + (f" ({result.date_agree / result.date_total:.1%})" if result.date_total else ""),
        f"- Content-type agreement (type-blind matches): {result.type_agree}/{result.type_total}"
        + (f" ({result.type_agree / result.type_total:.1%})" if result.type_total else ""),
        f"- Pages-count agreement (matched pairs -- does the model flag the same "
        f"number of pages this entry spans as Willis does): {result.pages_agree}/{result.pages_total}"
        + (f" ({result.pages_agree / result.pages_total:.1%})" if result.pages_total else ""),
        f"- Missed Willis rows: {len(result.missed)}",
        f"- Surplus model rows on Willis-covered pages (review list, NOT false positives -- "
        f"Willis is partial even within these pages): {len(result.surplus)}",
    ]
    if skipped_truth:
        lines.append(f"- Skipped (malformed) Willis rows: {len(skipped_truth)}")
    if skipped_model:
        lines.append(f"- Skipped (malformed) model rows: {len(skipped_model)}")
    lines.append("")

    by_type = coverage_by_content_type(result, truth_rows)
    lines.append("## Coverage by content type\n")
    lines.append("| Content type | Matched | Total | Coverage |")
    lines.append("|---|---:|---:|---:|")
    for ct in sorted(by_type):
        m, t = by_type[ct]
        pct = f"{m / t:.1%}" if t else "-"
        lines.append(f"| {ct} | {m} | {t} | {pct} |")
    lines.append("")

    lines.append("## Missed Willis rows (review)\n")
    lines.append("| Page | Matchup | Date | Type |")
    lines.append("|---:|---|---|---|")
    for r in sorted(result.missed, key=lambda r: (r.page, r.matchup)):
        lines.append(f"| {r.page} | {r.matchup} | {r.date} | {r.content_type} |")
    lines.append("")

    lines.append("## Fuzzy matches below 0.95 similarity (review)\n")
    lines.append("| Page | Willis | Model | Similarity |")
    lines.append("|---:|---|---|---:|")
    for p in sorted(result.matched, key=lambda p: p.similarity):
        if p.kind == "fuzzy" and p.similarity < 0.95:
            lines.append(f"| {p.truth.page} | {p.truth.matchup} | {p.model.matchup} | {p.similarity} |")
    lines.append("")

    lines.append("## Surplus model rows on Willis-covered pages (review)\n")
    lines.append("| Page | Matchup | Date | Type |")
    lines.append("|---:|---|---|---|")
    for r in sorted(result.surplus, key=lambda r: (r.page, r.matchup)):
        lines.append(f"| {r.page} | {r.matchup} | {r.date} | {r.content_type} |")
    lines.append("")

    return "\n".join(lines)


_LABEL_PREFIXES = ("match_index_", "stats_index_", "scorecard_index_")


def _label(path: str) -> str:
    import os
    base = os.path.basename(path).removesuffix(".csv")
    for prefix in _LABEL_PREFIXES:
        if base.startswith(prefix):
            return base.removeprefix(prefix)
    return base


# ── CLI ──────────────────────────────────────────────────────────────────────

def register_parser(subparsers):
    p = subparsers.add_parser(
        "evaluate",
        help="Evaluate a match_index_<model>.csv against the Willis ground-truth index.",
    )
    p.add_argument("csv_path", nargs="?", default=None, help="match_index_<model>.csv to evaluate.")
    p.add_argument("--truth", default="match_index_willis.csv")
    p.add_argument("--fuzzy-threshold", type=float, default=0.8)
    p.add_argument("--report", default=None, help="Write a Markdown report here (default: eval_<label>.md)")
    p.add_argument("--all", action="store_true", help="Evaluate every match_index_*.csv (except the truth file).")
    p.add_argument(
        "--pages", default=None,
        help="Comma-separated page numbers or ranges, e.g. '1,3,5-10'. Restricts scoring to "
             "only these pages -- use this for partial/test runs so coverage isn't diluted by "
             "pages you never attempted.",
    )
    p.add_argument(
        "--content-types", default=None,
        help="Comma-separated content types, e.g. 'statistics' or 'match information'. "
             "Restricts scoring to only Willis rows of these type(s) -- use this when "
             "evaluating a focused index (stats_index_*.csv, scorecard_index_*.csv) "
             "against Willis's full mix of content types.",
    )
    p.set_defaults(func=run)
    return p


def run(args) -> None:
    truth_path = Path(args.truth)
    if not truth_path.exists():
        raise SystemExit(f"Ground truth not found: {truth_path}")
    truth_rows, skipped_truth = load_index(truth_path)
    if skipped_truth:
        print(f"Skipped {len(skipped_truth)} malformed row(s) in {truth_path}")

    pages_filter = parse_page_spec(args.pages)
    if pages_filter:
        truth_rows = [r for r in truth_rows if r.page in pages_filter]
        if not truth_rows:
            raise SystemExit(f"No Willis rows on page(s) {sorted(pages_filter)}.")
        print(f"Restricting to page(s) {sorted(pages_filter)}: {len(truth_rows)} Willis row(s)")

    content_types_filter: set[str] | None = None
    if args.content_types:
        content_types_filter = {t.strip().lower() for t in args.content_types.split(",")}
        truth_rows = [r for r in truth_rows if r.content_type in content_types_filter]
        if not truth_rows:
            raise SystemExit(f"No Willis rows with content type in {sorted(content_types_filter)}.")
        print(f"Restricting to content type(s) {sorted(content_types_filter)}: {len(truth_rows)} Willis row(s)")

    if args.all:
        paths = sorted(
            p for p in glob.glob("match_index_*.csv")
            if Path(p).resolve() != truth_path.resolve()
        )
    elif args.csv_path:
        paths = [args.csv_path]
    else:
        raise SystemExit("Pass a CSV path, or use --all to evaluate every match_index_*.csv.")

    leaderboard = []
    for csv_path in paths:
        path = Path(csv_path)
        if not path.exists():
            print(f"Skipping {path}: not found")
            continue
        model_rows, skipped_model = load_index(path)
        result = evaluate(truth_rows, model_rows, fuzzy_threshold=args.fuzzy_threshold)

        total_truth = sum(1 for r in truth_rows if r.page in set(result.pages_covered))
        coverage = len(result.matched) / total_truth if total_truth else 0.0
        label = _label(str(path))
        leaderboard.append((label, coverage, len(result.matched), total_truth))

        print(f"{label:20s} coverage={coverage:.1%} ({len(result.matched)}/{total_truth}) "
              f"missed={len(result.missed)} surplus={len(result.surplus)}")

        report_path = Path(args.report) if (args.report and not args.all) else Path(f"eval_{label}.md")
        report = format_report(
            label, result, truth_rows, skipped_truth, skipped_model,
            pages_filter=pages_filter, content_types_filter=content_types_filter,
        )
        report_path.write_text(report, encoding="utf-8")
        print(f"  wrote {report_path}")

    if len(leaderboard) > 1:
        print("\nLeaderboard (Willis coverage):")
        for label, coverage, matched, total in sorted(leaderboard, key=lambda x: -x[1]):
            print(f"  {label:20s} {coverage:.1%} ({matched}/{total})")
