"""Compare match_index_*.csv files on (matchup, date, content_type) and build an agreement matrix."""

import csv
import glob
import os
from itertools import combinations

from normalize import matchup_key, normalize_date, title_key


def load_keys(path: str) -> set[tuple[str, str, str, str]]:
    keys = set()
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
                keys.add((key, page, date, content_type))
    return keys


def label(path: str) -> str:
    base = os.path.basename(path)
    return base.removeprefix("match_index_").removesuffix(".csv")


def write_markdown(sets: dict, names: list, union_all: set, intersection_all: set, coverage: dict, output_path: str = "compare_results.md") -> None:
    lines: list[str] = []

    lines.append("# Match Index Comparison Results\n")

    lines.append("## Files Loaded\n")
    lines.append("| File | Unique (matchup, page, date, content_type) rows |")
    lines.append("|------|---------------------------------------------------|")
    for n in names:
        lines.append(f"| {n} | {len(sets[n])} |")
    lines.append("")
    lines.append(f"- **Union across all files:** {len(union_all):,}")
    lines.append(f"- **Intersection across all files:** {len(intersection_all):,}")
    lines.append("")

    lines.append("---\n")
    lines.append("## Pairwise Shared (matchup, page, date, content_type) Counts\n")
    header_cols = "| " + " | ".join([""] + names) + " |"
    sep_cols = "| " + " | ".join(["--"] + ["--:"] * len(names)) + " |"
    lines.append(header_cols)
    lines.append(sep_cols)
    for a in names:
        cells = [f"**{a}**"] + [str(len(sets[a] & sets[b])) for b in names]
        lines.append("| " + " | ".join(cells) + " |")
    lines.append("")

    lines.append("---\n")
    lines.append("## Pairwise Jaccard Similarity (|A∩B| / |A∪B|)\n")
    lines.append(header_cols)
    lines.append(sep_cols)
    for a in names:
        cells = [f"**{a}**"]
        for b in names:
            inter = len(sets[a] & sets[b])
            union = len(sets[a] | sets[b])
            j = inter / union if union else 0.0
            cells.append(f"{j:.3f}")
        lines.append("| " + " | ".join(cells) + " |")
    lines.append("")

    lines.append("---\n")
    lines.append("## Pair Disagreements\n")
    lines.append("Rows present in one file but not the other:\n")
    lines.append("| Pair | Only in A | Only in B |")
    lines.append("|------|----------:|----------:|")
    for a, b in combinations(names, 2):
        only_a = len(sets[a] - sets[b])
        only_b = len(sets[b] - sets[a])
        lines.append(f"| {a} vs {b} | {only_a} | {only_b} |")
    lines.append("")

    lines.append("---\n")
    lines.append("## Agreement Distribution\n")
    lines.append("How many of the 7 files agree on each unique (matchup, page, date, content_type) key:\n")
    lines.append("| Files agreeing | Count of keys |")
    lines.append("|---------------:|--------------:|")
    for c in sorted(coverage):
        lines.append(f"| {c} / {len(names)} | {coverage[c]} |")
    lines.append("")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Results written to {output_path}")


def main() -> None:
    files = sorted(glob.glob("match_index_*.csv"))
    if not files:
        print("No match_index_*.csv files found.")
        return

    sets = {label(p): load_keys(p) for p in files}
    names = list(sets)

    print(f"Loaded {len(names)} files:")
    for n in names:
        print(f"  {n:30s} {len(sets[n]):5d} unique (matchup, page, date, content_type) rows")
    print()

    union_all = set().union(*sets.values())
    intersection_all = set.intersection(*sets.values()) if sets else set()
    print(f"Union across all files:        {len(union_all)}")
    print(f"Intersection across all files: {len(intersection_all)}")
    print()

    # Pairwise agreement matrix: count of shared keys.
    width = max(len(n) for n in names)
    header = " " * (width + 2) + "  ".join(f"{n:>{width}}" for n in names)
    print("Pairwise shared (matchup, page, date, content_type) counts:")
    print(header)
    for a in names:
        row = [f"{a:<{width}}"]
        for b in names:
            row.append(f"{len(sets[a] & sets[b]):>{width}}")
        print("  ".join(row))
    print()

    # Pairwise Jaccard similarity.
    print("Pairwise Jaccard similarity (|A∩B| / |A∪B|):")
    print(header)
    for a in names:
        row = [f"{a:<{width}}"]
        for b in names:
            inter = len(sets[a] & sets[b])
            union = len(sets[a] | sets[b])
            j = inter / union if union else 0.0
            row.append(f"{j:>{width}.3f}")
        print("  ".join(row))
    print()

    # Per-pair disagreements summary.
    print("Pair disagreements (rows present in one but not the other):")
    for a, b in combinations(names, 2):
        only_a = sets[a] - sets[b]
        only_b = sets[b] - sets[a]
        print(f"  {a} vs {b}: only in {a}={len(only_a)}, only in {b}={len(only_b)}")
    print()

    # Coverage: how many files agree on each unique key.
    coverage: dict[int, int] = {}
    for key in union_all:
        c = sum(1 for s in sets.values() if key in s)
        coverage[c] = coverage.get(c, 0) + 1
    print("Agreement distribution (N files agreeing -> count of keys):")
    for c in sorted(coverage):
        print(f"  agreed by {c}/{len(names)}: {coverage[c]}")

    write_markdown(sets, names, union_all, intersection_all, coverage)


if __name__ == "__main__":
    main()
