"""Promote human-reviewed entries into the Willis ground-truth index.

`tonywebb browse` produces compare_browser.html with an "Export Reviewed
CSV" button that writes accepted rows (matchup,page,date,content_type,
collection,record_id,notes) as match_index_reviewed.csv. This command
appends any of those rows not already present in match_index_willis.csv,
turning your own review decisions into an expanding ground truth instead of
a one-time manual index -- Willis currently only covers pages 1-61.
"""

from __future__ import annotations

import csv
from pathlib import Path

from . import config
from .evaluate import IndexRow, load_index
from .normalize import symmetric_matchup_key, title_key


def _key(row: IndexRow) -> str:
    # Order-insensitive for matches: a reviewed row shouldn't be treated as
    # "new" just because it lists the same two teams in the opposite order
    # from the existing Willis row -- see symmetric_matchup_key()'s docstring.
    return symmetric_matchup_key(row.matchup) if row.content_type == "match information" else title_key(row.matchup)


def register_parser(subparsers):
    p = subparsers.add_parser(
        "promote-reviewed",
        help="Append accepted rows from a reviewed-entries export into the Willis ground truth.",
    )
    p.add_argument(
        "reviewed",
        help="CSV exported from the browse review queue (default filename: match_index_reviewed.csv).",
    )
    p.add_argument("--truth", default="match_index_willis.csv", help="Ground-truth file to append into.")
    p.add_argument("--dry-run", action="store_true", help="Preview what would be promoted without writing.")
    p.set_defaults(func=run)
    return p


def run(args) -> None:
    reviewed_path = Path(args.reviewed)
    if not reviewed_path.exists():
        raise SystemExit(f"Reviewed-entries file not found: {reviewed_path}")
    reviewed_rows, skipped_reviewed = load_index(reviewed_path)
    if skipped_reviewed:
        print(f"Skipped {len(skipped_reviewed)} malformed row(s) in {reviewed_path}")

    truth_path = Path(args.truth)
    existing_keys: set[tuple[str, int, str]] = set()
    if truth_path.exists():
        existing_rows, skipped_truth = load_index(truth_path)
        if skipped_truth:
            print(f"Skipped {len(skipped_truth)} malformed row(s) in {truth_path}")
        existing_keys = {(_key(r), r.page, r.content_type) for r in existing_rows}
    else:
        print(f"{truth_path} does not exist yet -- it will be created.")

    new_rows = [r for r in reviewed_rows if (_key(r), r.page, r.content_type) not in existing_keys]
    duplicate_count = len(reviewed_rows) - len(new_rows)

    print(f"Reviewed entries: {len(reviewed_rows)}")
    print(f"Already in {truth_path}: {duplicate_count}")
    print(f"New: {len(new_rows)}")

    if not new_rows:
        print("Nothing to promote.")
        return

    for r in sorted(new_rows, key=lambda r: (r.page, r.matchup)):
        print(f"  + page {r.page}: {r.matchup} [{r.date}] ({r.content_type})")

    if args.dry_run:
        print("\n--dry-run: no changes written.")
        return

    file_exists = truth_path.exists()
    with truth_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["matchup", "page", "date", "content_type", "collection", "record_id"])
        for r in new_rows:
            writer.writerow([r.matchup, r.page, r.date, r.content_type, config.COLLECTION_NAME, ""])

    print(f"\nPromoted {len(new_rows)} row(s) into {truth_path}.")
