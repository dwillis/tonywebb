"""
Transcription Text Cleanup
============================
Fixes common OCR-layer artifacts in already-transcribed page text: soft
line-wrap hyphens that split a word across two lines, dot-leader runs in
averages tables (e.g. "Curtis........... 9 196"), and a small set of known
misreadings.

This replaces an earlier ad-hoc script that did the same two transforms but
joined every "word-\\nword" break unconditionally, silently merging real
hyphenated surnames split at a line wrap into one word (e.g.
"Tasker-Evans" -> "TaskerEvans", "3-Hawkins" -> "3Hawkins"). The join here
is guarded: it skips the break when either side is numeric, or when the
right-hand side starts with a capital letter (a real compound name like
"Tasker-Evans"), with a narrow exception for "Mc-"/"Mac-" prefixes (e.g.
"Mc-Guire" -> "McGuire", which genuinely is one name split by the line
wrap, not two joined by a real hyphen).

Outputs: rewrites the input .txt files in place (or reports counts only
under --dry-run).
"""

import re
from pathlib import Path

TRANSFORM_KEYS = ("hyphen_joins", "dot_leaders", "typo_fixes")

_HYPHEN_BREAK_RE = re.compile(r"(\w+)[ \t]*-[ \t]*\n(\w+)")
_DOT_LEADER_RE = re.compile(r"\.{4,}")
_SPACED_DOTS_RE = re.compile(r"[ \t]+\.\.[ \t]+")
_TYPO_PATTERNS = [
    (re.compile(r"\bEx ras\b"), "Extras"),
    (re.compile(r"\bExras\b"), "Extras"),
    (re.compile(r"\bE xtras\b"), "Extras"),
    (re.compile(r"\bExtr as\b"), "Extras"),
    (re.compile(r"\bLllogan\b"), "Illogan"),
    (re.compile(r"\bR H Haviland\b"), "R. H. Haviland"),
]

_MC_MAC_PREFIXES = {"mc", "mac"}


def _is_mc_mac_prefix(left: str) -> bool:
    return left.lower() in _MC_MAC_PREFIXES


def join_hyphen_breaks(text: str) -> tuple[str, int]:
    """Rejoin a word split by a hyphen at a line wrap: 'per-\\nformances' -> 'performances'.

    Skipped (left as-is) when either side is numeric (a batting-order or
    over number glued to a name, e.g. '3-\\nHawkins') or the right side
    starts with a capital letter (a real hyphenated compound name, e.g.
    'Tasker-\\nEvans') -- except for the 'Mc'/'Mac' name-prefix exception.
    """
    count = 0

    def repl(m: "re.Match[str]") -> str:
        nonlocal count
        left, right = m.group(1), m.group(2)
        if left.isdigit() or right.isdigit():
            return m.group(0)
        if right[:1].isupper() and not _is_mc_mac_prefix(left):
            return m.group(0)
        count += 1
        return left + right

    return _HYPHEN_BREAK_RE.sub(repl, text), count


def collapse_dot_leaders(text: str) -> tuple[str, int]:
    """Collapse a run of 4+ dots (an averages-table leader) to ' .. ', then
    tidy any surrounding whitespace the collapse left behind."""
    text, count = _DOT_LEADER_RE.subn(" .. ", text)
    text = _SPACED_DOTS_RE.sub(" .. ", text)
    return text, count


def fix_known_typos(text: str) -> tuple[str, int]:
    """Fix a small set of known, specific OCR misreadings seen in this collection."""
    total = 0
    for pattern, replacement in _TYPO_PATTERNS:
        text, n = pattern.subn(replacement, text)
        total += n
    return text, total


def clean_text(
    text: str,
    *,
    dot_leaders: bool = True,
    hyphens: bool = True,
    typos: bool = True,
) -> tuple[str, dict[str, int]]:
    """Apply the enabled transforms in sequence. Returns (cleaned_text, counts)."""
    counts = {key: 0 for key in TRANSFORM_KEYS}
    if hyphens:
        text, counts["hyphen_joins"] = join_hyphen_breaks(text)
    if dot_leaders:
        text, counts["dot_leaders"] = collapse_dot_leaders(text)
    if typos:
        text, counts["typo_fixes"] = fix_known_typos(text)
    return text, counts


# ── CLI ──────────────────────────────────────────────────────────────────────

def register_parser(subparsers):
    p = subparsers.add_parser(
        "clean-transcriptions",
        help="Clean up OCR-layer artifacts (dot leaders, soft-wrap hyphens, known typos) "
             "in transcribed page text.",
    )
    p.add_argument("--input", "-i", required=True, help="Directory of per-page .txt files to clean.")
    p.add_argument("--dry-run", action="store_true", help="Report per-file change counts without writing.")
    p.add_argument(
        "--skip-dot-leaders", action="store_true",
        help="Skip the dot-leader collapse (the bulk of the changes -- table alignment "
             "is lost when this runs).",
    )
    p.add_argument("--skip-hyphens", action="store_true", help="Skip the soft-wrap hyphen rejoin.")
    p.add_argument("--skip-typos", action="store_true", help="Skip the known-typo fixes.")
    p.set_defaults(func=run)
    return p


def run(args) -> None:
    input_dir = Path(args.input)
    if not input_dir.is_dir():
        raise SystemExit(f"Not a directory: {input_dir}")

    files = sorted(input_dir.glob("*.txt"))
    if not files:
        raise SystemExit(f"No .txt files found in {input_dir}")

    totals = {key: 0 for key in TRANSFORM_KEYS}
    changed_files = 0

    for path in files:
        original = path.read_text(encoding="utf-8")
        cleaned, counts = clean_text(
            original,
            dot_leaders=not args.skip_dot_leaders,
            hyphens=not args.skip_hyphens,
            typos=not args.skip_typos,
        )
        for key, value in counts.items():
            totals[key] += value

        if cleaned != original:
            changed_files += 1
            note = ", ".join(f"{k}={v}" for k, v in counts.items() if v)
            print(f"  {path.name}: {note}")
            if not args.dry_run:
                path.write_text(cleaned, encoding="utf-8")

    verb = "Would change" if args.dry_run else "Changed"
    print(f"\n{verb} {changed_files}/{len(files)} file(s).")
    print(f"Hyphen breaks joined : {totals['hyphen_joins']}")
    print(f"Dot leaders collapsed: {totals['dot_leaders']}")
    print(f"Known typos fixed    : {totals['typo_fixes']}")
    if args.dry_run:
        print("\n--dry-run: no files written.")
