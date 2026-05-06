"""Generate a starter clubs.csv from match_index CSVs.

Extracts all unique team names from Willis ground truth and model outputs,
groups obvious variants (differing only by CC/OC suffix, Mr prefix, or
punctuation), and writes clubs.csv with canonical names and aliases.

Usage:
    python generate_clubs.py
"""

import csv
import re
from collections import defaultdict
from pathlib import Path


def normalize_apostrophes(name: str) -> str:
    return name.replace("‘", "'").replace("’", "'").replace("“", '"').replace("”", '"')


def strip_cc_oc(name: str) -> str:
    s = normalize_apostrophes(name)
    s = re.sub(r"[,\s]+(?:C\.?\s*C\.?|Cricket\s+Club|O\.?\s*C\.?)\.?\s*$", "", s, flags=re.IGNORECASE)
    return s.strip()


def strip_mr(name: str) -> str:
    return re.sub(r"^Mr\.?\s+", "", name, flags=re.IGNORECASE).strip()


def strip_dots(name: str) -> str:
    return name.replace(".", "").strip()


def canonical_key(name: str) -> str:
    s = strip_cc_oc(name)
    s = strip_mr(s)
    s = strip_dots(s)
    s = re.sub(r"\s+", " ", s).strip().lower()
    # Remove all non-alphanumeric except spaces for key purposes
    s = re.sub(r"[^a-z0-9 ]", "", s)
    # Remove parenthetical qualifiers like "(launceston)"
    s = re.sub(r"\s*\(.*?\)\s*", " ", s)
    # Normalize ordinals
    s = re.sub(r"\b1st\b", "first", s)
    s = re.sub(r"\b2nd\b", "second", s)
    s = re.sub(r"\b3rd\b", "third", s)
    # Normalize "eleven" to "xi"
    s = re.sub(r"\beleven\b", "xi", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def extract_teams_from_csv(path: Path) -> dict[str, set[str]]:
    """Return {source_label: set of raw team names} from a match_index CSV."""
    teams: set[str] = set()
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            ct = (row.get("content_type") or "").strip().lower()
            if ct != "match information":
                continue
            matchup = row.get("matchup", "")
            if " v " in matchup:
                left, right = matchup.split(" v ", 1)
                for t in (left.strip(), right.strip()):
                    if t:
                        teams.add(t)
    label = path.stem.removeprefix("match_index_")
    return {label: teams}


def guess_type(name: str) -> str:
    low = name.lower()
    if "school" in low or "g.s." in low or "grammar" in low or "college" in low:
        return "school"
    if "xi" in low and ("'s" in low or "’s" in low):
        return "personal_xi"
    if "works" in low or "factory" in low or "printing" in low:
        return "works"
    if any(w in low for w in ("volunteer", "regiment", "garrison", "military", "barracks", "division", "battery")):
        return "military"
    if any(w in low for w in ("church", "chapel", "all saints", "parish")):
        return "church"
    if re.search(r"\bst\b", low) and not re.search(r"\b(first|second|third|xi|town)\b", low):
        return "church"
    return "club"


def main():
    csvs = sorted(Path(".").glob("match_index_*.csv"))
    if not csvs:
        raise SystemExit("No match_index_*.csv files found.")

    all_teams: dict[str, set[str]] = {}  # source -> set of raw names
    for p in csvs:
        all_teams.update(extract_teams_from_csv(p))

    # Group all raw names by canonical key
    groups: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    for source, teams in all_teams.items():
        for raw in teams:
            key = canonical_key(raw)
            groups[key][source].add(raw)

    # For each group, pick the canonical name (prefer Willis form, else most common)
    rows = []
    for key in sorted(groups):
        source_names = groups[key]
        all_raw: list[str] = []
        for names in source_names.values():
            all_raw.extend(names)

        # Prefer Willis form as canonical
        willis_names = source_names.get("willis", set())
        if willis_names:
            canonical = sorted(willis_names)[0]
        else:
            # Pick the most common raw form
            counts: dict[str, int] = defaultdict(int)
            for n in all_raw:
                counts[n] += 1
            canonical = max(counts, key=lambda n: (counts[n], n))

        # Normalize the canonical: strip CC/OC, Mr prefix, dots from abbreviations
        canonical = strip_cc_oc(canonical)
        canonical = strip_mr(canonical)
        canonical = strip_dots(canonical)
        canonical = re.sub(r"\s+", " ", canonical).strip()

        # Collect aliases (raw forms that differ from canonical after basic cleanup)
        aliases = set()
        for raw in all_raw:
            cleaned = strip_dots(raw).strip()
            if cleaned.lower() != canonical.lower() and cleaned:
                aliases.add(cleaned)

        club_type = guess_type(canonical)

        rows.append({
            "canonical_name": canonical,
            "aliases": "|".join(sorted(aliases)) if aliases else "",
            "location": "",
            "type": club_type,
        })

    out = Path("clubs.csv")
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["canonical_name", "aliases", "location", "type"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {out} with {len(rows)} clubs")
    # Summary
    with_aliases = sum(1 for r in rows if r["aliases"])
    type_counts = defaultdict(int)
    for r in rows:
        type_counts[r["type"]] += 1
    print(f"  {with_aliases} clubs have aliases")
    for t, c in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"  {t}: {c}")


if __name__ == "__main__":
    main()
