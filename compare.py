"""
Compare match_index CSV files produced by different LLMs.

Checks:
  1. Row counts per model and per page
  2. Matchup agreement across models (by page)
  3. Date agreement for shared matchups
  4. Field-level diffs for rows that share a page + approximate matchup
  5. Summary statistics

Usage:
    python compare.py
"""

import csv
import os
import re
from collections import defaultdict
from difflib import SequenceMatcher

# ── Discover CSV files ────────────────────────────────────────────────────────

CSV_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILES = sorted(
    f for f in os.listdir(CSV_DIR) if f.startswith("match_index_") and f.endswith(".csv")
)
MODEL_NAMES = [f.replace("match_index_", "").replace(".csv", "") for f in CSV_FILES]


def load_csv(path):
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        return [row for row in reader]


def normalize(text):
    """Lowercase, collapse whitespace, strip punctuation for fuzzy compare."""
    text = text.strip().lower()
    text = re.sub(r"[''`]", "'", text)
    text = re.sub(r"\s+", " ", text)
    return text


def similarity(a, b):
    return SequenceMatcher(None, normalize(a), normalize(b)).ratio()


# ── Load all data ─────────────────────────────────────────────────────────────

data = {}  # model_name -> list of row dicts
for name, fname in zip(MODEL_NAMES, CSV_FILES):
    data[name] = load_csv(os.path.join(CSV_DIR, fname))

# ── 1. Row counts ────────────────────────────────────────────────────────────

print("=" * 70)
print("1. TOTAL ROW COUNTS")
print("=" * 70)
for name in MODEL_NAMES:
    print(f"  {name:20s}: {len(data[name]):>4d} rows")

# ── 2. Rows per page ─────────────────────────────────────────────────────────

page_counts = {}  # model -> {page: count}
all_pages = set()
for name in MODEL_NAMES:
    counts = defaultdict(int)
    for row in data[name]:
        p = row.get("page", "")
        counts[p] += 1
        all_pages.add(p)
    page_counts[name] = counts

print()
print("=" * 70)
print("2. ROWS PER PAGE (pages where models disagree)")
print("=" * 70)
header = f"  {'Page':>6s}" + "".join(f"  {n:>14s}" for n in MODEL_NAMES)
print(header)
print("  " + "-" * (len(header) - 2))

disagree_pages = 0
for page in sorted(all_pages, key=lambda p: (int(p) if p.isdigit() else 999, p)):
    counts = [page_counts[n].get(page, 0) for n in MODEL_NAMES]
    if len(set(counts)) > 1:
        row_str = f"  {page:>6s}" + "".join(f"  {c:>14d}" for c in counts)
        print(row_str)
        disagree_pages += 1

if disagree_pages == 0:
    print("  All models agree on row counts for every page.")
else:
    print(f"\n  ({disagree_pages} pages with differing counts)")

# ── 3. Match matchups across models by page ──────────────────────────────────

# Build page -> list of matchups per model
page_matchups = {}  # model -> {page: [matchup, ...]}
for name in MODEL_NAMES:
    pm = defaultdict(list)
    for row in data[name]:
        pm[row.get("page", "")].append(row.get("matchup", ""))
    page_matchups[name] = pm

SIMILARITY_THRESHOLD = 0.70

print()
print("=" * 70)
print("3. MATCHUP COMPARISON (pairwise, by page)")
print("=" * 70)

pair_stats = {}
for i, m1 in enumerate(MODEL_NAMES):
    for m2 in MODEL_NAMES[i + 1:]:
        exact = 0
        fuzzy = 0
        only_m1 = 0
        only_m2 = 0
        total_compared = 0
        diff_examples = []

        for page in sorted(all_pages, key=lambda p: (int(p) if p.isdigit() else 999, p)):
            list1 = page_matchups[m1].get(page, [])
            list2 = page_matchups[m2].get(page, [])

            # Greedy best-match alignment
            used2 = set()
            matched_pairs = []
            unmatched1 = []
            for matchup1 in list1:
                best_sim = 0
                best_j = -1
                for j, matchup2 in enumerate(list2):
                    if j in used2:
                        continue
                    s = similarity(matchup1, matchup2)
                    if s > best_sim:
                        best_sim = s
                        best_j = j
                if best_j >= 0 and best_sim >= SIMILARITY_THRESHOLD:
                    matched_pairs.append((matchup1, list2[best_j], best_sim))
                    used2.add(best_j)
                else:
                    unmatched1.append(matchup1)

            unmatched2 = [list2[j] for j in range(len(list2)) if j not in used2]

            for matchup1, matchup2, sim in matched_pairs:
                total_compared += 1
                if normalize(matchup1) == normalize(matchup2):
                    exact += 1
                else:
                    fuzzy += 1
                    if len(diff_examples) < 10:
                        diff_examples.append((page, matchup1, matchup2, sim))

            only_m1 += len(unmatched1)
            only_m2 += len(unmatched2)

        pair_stats[(m1, m2)] = {
            "exact": exact,
            "fuzzy": fuzzy,
            "only_m1": only_m1,
            "only_m2": only_m2,
            "total": total_compared,
        }

        pct = (exact / total_compared * 100) if total_compared else 0
        print(f"\n  {m1} vs {m2}:")
        print(f"    Matched rows:       {total_compared}")
        print(f"    Exact matchup:      {exact} ({pct:.1f}%)")
        print(f"    Fuzzy matchup:      {fuzzy} (similar but not identical)")
        print(f"    Only in {m1:14s}: {only_m1}")
        print(f"    Only in {m2:14s}: {only_m2}")
        if diff_examples:
            print(f"    Sample differences (matchup text):")
            for pg, t1, t2, sim in diff_examples[:5]:
                print(f"      p{pg}: \"{t1}\"")
                print(f"      {' ' * len(f'p{pg}')}: \"{t2}\"  (sim={sim:.2f})")

# ── 4. Date agreement for matched rows ───────────────────────────────────────

print()
print("=" * 70)
print("4. DATE AGREEMENT (for matched rows)")
print("=" * 70)

for i, m1 in enumerate(MODEL_NAMES):
    for m2 in MODEL_NAMES[i + 1:]:
        date_match = 0
        date_mismatch = 0
        date_diff_examples = []

        for page in sorted(all_pages, key=lambda p: (int(p) if p.isdigit() else 999, p)):
            rows1 = [r for r in data[m1] if r.get("page") == page]
            rows2 = [r for r in data[m2] if r.get("page") == page]

            used2 = set()
            for r1 in rows1:
                best_sim = 0
                best_j = -1
                for j, r2 in enumerate(rows2):
                    if j in used2:
                        continue
                    s = similarity(r1.get("matchup", ""), r2.get("matchup", ""))
                    if s > best_sim:
                        best_sim = s
                        best_j = j
                if best_j >= 0 and best_sim >= SIMILARITY_THRESHOLD:
                    used2.add(best_j)
                    d1 = r1.get("date", "").strip()
                    d2 = rows2[best_j].get("date", "").strip()
                    if d1 == d2:
                        date_match += 1
                    else:
                        date_mismatch += 1
                        if len(date_diff_examples) < 8:
                            date_diff_examples.append(
                                (page, r1.get("matchup", ""), d1, d2)
                            )

        total = date_match + date_mismatch
        pct = (date_match / total * 100) if total else 0
        print(f"\n  {m1} vs {m2}:")
        print(f"    Date matches:    {date_match}/{total} ({pct:.1f}%)")
        print(f"    Date mismatches: {date_mismatch}")
        if date_diff_examples:
            print(f"    Sample date differences:")
            for pg, mu, d1, d2 in date_diff_examples:
                print(f"      p{pg} \"{mu}\": {d1} vs {d2}")

# ── 5. Consensus rows (all models agree exactly) ─────────────────────────────

print()
print("=" * 70)
print("5. CONSENSUS (rows where ALL models agree exactly)")
print("=" * 70)

consensus = 0
total_union = 0

for page in sorted(all_pages, key=lambda p: (int(p) if p.isdigit() else 999, p)):
    # Get matchup lists per model for this page
    per_model = {}
    for name in MODEL_NAMES:
        per_model[name] = [
            (normalize(r.get("matchup", "")), r.get("date", "").strip())
            for r in data[name]
            if r.get("page") == page
        ]

    # Check each row from first model against all others
    base = MODEL_NAMES[0]
    for matchup_norm, date_val in per_model[base]:
        found_in_all = True
        for other in MODEL_NAMES[1:]:
            if (matchup_norm, date_val) not in per_model[other]:
                found_in_all = False
                break
        if found_in_all:
            consensus += 1

    # Union count: unique (page, norm_matchup) across all models
    seen = set()
    for name in MODEL_NAMES:
        for mn, dv in per_model[name]:
            seen.add((page, mn, dv))
    total_union += len(seen)

print(f"  Rows in all models with identical matchup+date: {consensus}")
print(f"  Total unique (page, matchup, date) across models: {total_union}")
if total_union:
    print(f"  Consensus rate: {consensus / total_union * 100:.1f}%")

# ── 6. Overall summary ───────────────────────────────────────────────────────

print()
print("=" * 70)
print("6. OVERALL SUMMARY")
print("=" * 70)

print(f"\n  Models compared: {', '.join(MODEL_NAMES)}")
print(f"  Row counts: {', '.join(str(len(data[n])) for n in MODEL_NAMES)}")

# Average pairwise exact match rate
if pair_stats:
    rates = []
    for key, stats in pair_stats.items():
        if stats["total"]:
            rates.append(stats["exact"] / stats["total"] * 100)
    if rates:
        print(f"  Avg pairwise exact matchup rate: {sum(rates) / len(rates):.1f}%")

print()
