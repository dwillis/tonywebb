"""Merge multiple match_index_*.csv files (+ optional Willis ground truth) into
one submittable consensus index via majority-vote date/matchup text.

This is the missing "last mile" command: extract-matches/index-stats/
index-scorecards each produce one model's opinion, and compare/browse/
evaluate are all diagnostic -- nothing assembles those per-model opinions
into a single deliverable index. Willis, when present, is treated as
authoritative for any row she has (both matchup spelling and date);
otherwise the majority vote among model files wins, with every disagreement
flagged in the review report rather than silently discarded.
"""

from __future__ import annotations

import csv
import glob
import os
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from . import config
from .evaluate import IndexRow, load_index
from .indexing import recompute_pages_column
from .normalize import symmetric_matchup_key, title_key


def _label(path: str) -> str:
    base = os.path.basename(path).removesuffix(".csv")
    for prefix in ("match_index_", "stats_index_", "scorecard_index_"):
        if base.startswith(prefix):
            return base.removeprefix(prefix)
    return base


def _key(row: IndexRow) -> str:
    # Order-insensitive for matches: sources disagree on which team is
    # listed first (prose word order vs. a manual index's own convention),
    # and neither is "wrong" -- see symmetric_matchup_key()'s docstring.
    return symmetric_matchup_key(row.matchup) if row.content_type == "match information" else title_key(row.matchup)


@dataclass
class ConsensusRow:
    matchup: str
    page: int
    date: str
    content_type: str
    sources: list[str]
    total_sources: int
    date_variants: dict[str, str]
    matchup_variants: dict[str, str]
    from_willis: bool
    has_date_conflict: bool
    has_matchup_conflict: bool


def build_consensus(
    model_rows_by_label: dict[str, list[IndexRow]],
    truth_rows: list[IndexRow] | None = None,
) -> list[ConsensusRow]:
    """Group rows across all sources by (key, page, content_type); majority-vote date/matchup.

    Willis's matchup spelling and date win outright for any group she has a
    row in. Otherwise the most common date/matchup text among the model
    files wins. Every group that ANY source found is kept -- no model has
    near-complete recall on its own, so requiring multi-source agreement
    would silently drop real matches; low-agreement rows are flagged for
    human review instead.
    """
    total_sources = len(model_rows_by_label)
    groups: dict[tuple[str, int, str], dict[str, IndexRow]] = {}

    for label, rows in model_rows_by_label.items():
        for row in rows:
            gk = (_key(row), row.page, row.content_type)
            groups.setdefault(gk, {})[label] = row

    willis_by_group: dict[tuple[str, int, str], IndexRow] = {}
    if truth_rows:
        for row in truth_rows:
            gk = (_key(row), row.page, row.content_type)
            willis_by_group[gk] = row
            groups.setdefault(gk, {})

    consensus: list[ConsensusRow] = []
    for gk, present in groups.items():
        willis_row = willis_by_group.get(gk)
        date_variants = {label: r.date for label, r in present.items() if r.date}
        matchup_variants = {label: r.matchup for label, r in present.items()}

        if willis_row and willis_row.date:
            final_date = willis_row.date
        elif date_variants:
            final_date = Counter(date_variants.values()).most_common(1)[0][0]
        else:
            final_date = ""

        if willis_row:
            final_matchup = willis_row.matchup
        elif matchup_variants:
            final_matchup = Counter(matchup_variants.values()).most_common(1)[0][0]
        else:
            final_matchup = ""

        if not final_matchup:
            continue  # nothing usable to emit (defensive -- shouldn't happen)

        consensus.append(ConsensusRow(
            matchup=final_matchup,
            page=gk[1],
            date=final_date,
            content_type=gk[2],
            sources=sorted(present.keys()),
            total_sources=total_sources,
            date_variants=date_variants,
            matchup_variants=matchup_variants,
            from_willis=willis_row is not None,
            has_date_conflict=len(set(date_variants.values())) > 1,
            has_matchup_conflict=len(set(matchup_variants.values())) > 1,
        ))

    return consensus


def format_consensus_report(consensus: list[ConsensusRow]) -> str:
    total = len(consensus)
    from_willis = sum(1 for c in consensus if c.from_willis)
    unanimous = sum(1 for c in consensus if not c.has_date_conflict and not c.has_matchup_conflict)
    date_conflicts = [c for c in consensus if c.has_date_conflict]
    matchup_conflicts = [c for c in consensus if c.has_matchup_conflict]
    low_agreement = [
        c for c in consensus
        if not c.from_willis and c.total_sources > 1 and len(c.sources) == 1
    ]

    lines = [
        "# Consensus Index Report\n",
        f"- Total consensus rows: {total}",
        f"- From Willis ground truth: {from_willis}",
        f"- Unanimous (no date or matchup conflict among sources): {unanimous}",
        f"- Date conflicts: {len(date_conflicts)}",
        f"- Matchup text conflicts: {len(matchup_conflicts)}",
        f"- Low-agreement rows (found by only 1 model, not in Willis): {len(low_agreement)}",
        "",
        "## Date conflicts (review)\n",
        "| Page | Matchup | Chosen date | Variants |",
        "|---:|---|---|---|",
    ]
    for c in sorted(date_conflicts, key=lambda c: (c.page, c.matchup)):
        variants = "; ".join(f"{label}={d}" for label, d in sorted(c.date_variants.items()))
        lines.append(f"| {c.page} | {c.matchup} | {c.date} | {variants} |")
    lines.append("")

    lines.append("## Matchup text conflicts (review)\n")
    lines.append("| Page | Chosen | Variants |")
    lines.append("|---:|---|---|")
    for c in sorted(matchup_conflicts, key=lambda c: (c.page, c.matchup)):
        variants = "; ".join(f"{label}={m}" for label, m in sorted(c.matchup_variants.items()))
        lines.append(f"| {c.page} | {c.matchup} | {variants} |")
    lines.append("")

    lines.append("## Low-agreement rows (review -- found by only one model, not in Willis)\n")
    lines.append("| Page | Matchup | Date | Found by |")
    lines.append("|---:|---|---|---|")
    for c in sorted(low_agreement, key=lambda c: (c.page, c.matchup)):
        lines.append(f"| {c.page} | {c.matchup} | {c.date} | {', '.join(c.sources)} |")
    lines.append("")

    return "\n".join(lines)


# ── CLI ──────────────────────────────────────────────────────────────────────

def register_parser(subparsers):
    p = subparsers.add_parser(
        "consensus",
        help="Merge match_index_*.csv files into one consensus index via majority vote.",
    )
    p.add_argument("--pattern", default="match_index_*.csv")
    p.add_argument(
        "--truth", default="match_index_willis.csv",
        help="Ground truth file, treated as authoritative for any row it has. Pass '' to disable.",
    )
    p.add_argument("--output", "-o", default="consensus_index.csv")
    p.add_argument("--report", default="consensus_report.md")
    p.add_argument(
        "--min-agreement", type=int, default=1,
        help="Drop non-Willis rows found by fewer than this many model files, instead of "
             "just flagging them for review (default 1 = keep everything).",
    )
    p.set_defaults(func=run)
    return p


def run(args) -> None:
    truth_path = Path(args.truth) if args.truth else None
    paths = sorted(
        p for p in glob.glob(args.pattern)
        if not (truth_path and Path(p).resolve() == truth_path.resolve())
    )
    if not paths:
        print(f"No files matching {args.pattern} found.")
        return

    model_rows_by_label: dict[str, list[IndexRow]] = {}
    for p in paths:
        rows, skipped = load_index(Path(p))
        label = _label(p)
        model_rows_by_label[label] = rows
        if skipped:
            print(f"  {label}: skipped {len(skipped)} malformed row(s)")

    truth_rows: list[IndexRow] | None = None
    if truth_path and truth_path.exists():
        truth_rows, skipped = load_index(truth_path)
        if skipped:
            print(f"  willis: skipped {len(skipped)} malformed row(s)")
    elif truth_path:
        print(f"Truth file not found: {truth_path} (proceeding without it)")

    print(f"Merging {len(paths)} file(s): {', '.join(model_rows_by_label)}")
    consensus = build_consensus(model_rows_by_label, truth_rows)

    if args.min_agreement > 1:
        kept = [c for c in consensus if c.from_willis or len(c.sources) >= args.min_agreement]
        dropped = len(consensus) - len(kept)
        if dropped:
            print(f"Dropped {dropped} row(s) below --min-agreement {args.min_agreement} "
                  f"(not in Willis, found by fewer model(s))")
        consensus = kept

    consensus.sort(key=lambda c: (c.page, c.matchup))

    out_path = Path(args.output)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["matchup", "page", "date", "content_type", "collection", "pages"])
        for c in consensus:
            writer.writerow([c.matchup, c.page, c.date, c.content_type, config.COLLECTION_NAME, 1])
    if consensus:
        recompute_pages_column(out_path)
    print(f"Wrote {out_path} ({len(consensus)} rows)")

    report_path = Path(args.report)
    report_path.write_text(format_consensus_report(consensus), encoding="utf-8")
    print(f"Wrote {report_path}")
