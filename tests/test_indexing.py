"""Tests for indexing.py's recompute_pages_column -- the shared cross-page
"pages" count computation used by extract-matches/index-stats/
index-scorecards' own output, and re-used as a post-hoc pass by consensus
and promote-reviewed.
"""

import csv
from pathlib import Path

from tonywebb.indexing import recompute_pages_column


def _write_csv(tmp_path: Path, rows: list[dict]) -> Path:
    path = tmp_path / "match_index_test.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["matchup", "page", "date", "content_type", "collection", "pages"]
        )
        writer.writeheader()
        for r in rows:
            writer.writerow({"collection": "Tony Webb minor counties collection", "pages": 1, **r})
    return path


def _read_rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


class TestRecomputePagesColumn:
    def test_unique_entries_stay_at_1(self, tmp_path):
        path = _write_csv(tmp_path, [
            {"matchup": "A v B", "page": "1", "date": "18950527", "content_type": "match information"},
            {"matchup": "C v D", "page": "2", "date": "18950603", "content_type": "match information"},
        ])
        recompute_pages_column(path)
        rows = _read_rows(path)
        assert [r["pages"] for r in rows] == ["1", "1"]

    def test_non_consecutive_pages_still_grouped(self, tmp_path):
        # Regression case: the same match reported on page 59 AND page 61
        # (a different newspaper's recap of the same Saturday) must be
        # flagged, exactly like a continuation onto the very next page --
        # "pages" tracks ANY two pages, not just adjacent ones.
        path = _write_csv(tmp_path, [
            {"matchup": "Liverpool v Oxton", "page": "59", "date": "18950907", "content_type": "match information"},
            {"matchup": "Liverpool v Oxton", "page": "61", "date": "18950907", "content_type": "match information"},
        ])
        changed = recompute_pages_column(path)
        rows = _read_rows(path)
        assert [r["pages"] for r in rows] == ["2", "2"]
        assert changed == 2

    def test_consecutive_pages_also_grouped(self, tmp_path):
        path = _write_csv(tmp_path, [
            {"matchup": "A v B", "page": "5", "date": "18950527", "content_type": "match information"},
            {"matchup": "A v B", "page": "6", "date": "18950527", "content_type": "match information"},
        ])
        recompute_pages_column(path)
        rows = _read_rows(path)
        assert [r["pages"] for r in rows] == ["2", "2"]

    def test_three_pages_counted_correctly(self, tmp_path):
        path = _write_csv(tmp_path, [
            {"matchup": "A v B", "page": "1", "date": "18950527", "content_type": "match information"},
            {"matchup": "A v B", "page": "5", "date": "18950527", "content_type": "match information"},
            {"matchup": "A v B", "page": "9", "date": "18950527", "content_type": "match information"},
        ])
        recompute_pages_column(path)
        rows = _read_rows(path)
        assert [r["pages"] for r in rows] == ["3", "3", "3"]

    def test_different_dates_not_grouped(self, tmp_path):
        path = _write_csv(tmp_path, [
            {"matchup": "A v B", "page": "1", "date": "18950527", "content_type": "match information"},
            {"matchup": "A v B", "page": "5", "date": "18950603", "content_type": "match information"},
        ])
        recompute_pages_column(path)
        rows = _read_rows(path)
        assert [r["pages"] for r in rows] == ["1", "1"]

    def test_different_content_types_not_grouped(self, tmp_path):
        path = _write_csv(tmp_path, [
            {"matchup": "Newbury", "page": "1", "date": "18950000", "content_type": "team information"},
            {"matchup": "Newbury", "page": "5", "date": "18950000", "content_type": "statistics"},
        ])
        recompute_pages_column(path)
        rows = _read_rows(path)
        assert [r["pages"] for r in rows] == ["1", "1"]

    def test_matchup_text_variant_still_grouped(self, tmp_path):
        # Punctuation/apostrophe differences shouldn't defeat grouping --
        # recompute_pages_column uses the same normalized key as
        # track_cross_page.
        path = _write_csv(tmp_path, [
            {"matchup": "Waterlow's v East Finchley", "page": "1", "date": "18950527", "content_type": "match information"},
            {"matchup": "Waterlows v East Finchley", "page": "9", "date": "18950527", "content_type": "match information"},
        ])
        recompute_pages_column(path)
        rows = _read_rows(path)
        assert [r["pages"] for r in rows] == ["2", "2"]

    def test_reversed_team_order_still_grouped(self, tmp_path):
        # Cross-page duplicates are frequently two different newspapers'
        # independent write-ups of the same match, which routinely name the
        # teams in the opposite order -- see _row_key()'s docstring in
        # indexing.py. Confirmed live: page 59 ("New Brighton v Formby")
        # and page 61 ("Formby v New Brighton") report the same match.
        path = _write_csv(tmp_path, [
            {"matchup": "Liverpool v Rock Ferry", "page": "1", "date": "18950527", "content_type": "match information"},
            {"matchup": "Rock Ferry v Liverpool", "page": "9", "date": "18950527", "content_type": "match information"},
        ])
        recompute_pages_column(path)
        rows = _read_rows(path)
        assert [r["pages"] for r in rows] == ["2", "2"]

    def test_no_change_returns_zero(self, tmp_path):
        path = _write_csv(tmp_path, [
            {"matchup": "A v B", "page": "1", "date": "18950527", "content_type": "match information"},
        ])
        recompute_pages_column(path)  # first pass sets it to 1 (no change from initial 1)
        changed = recompute_pages_column(path)  # second pass: still 1, no change
        assert changed == 0

    def test_rows_not_dropped(self, tmp_path):
        # Flag, don't merge -- every page's row stays in the CSV.
        path = _write_csv(tmp_path, [
            {"matchup": "A v B", "page": "1", "date": "18950527", "content_type": "match information"},
            {"matchup": "A v B", "page": "5", "date": "18950527", "content_type": "match information"},
        ])
        recompute_pages_column(path)
        rows = _read_rows(path)
        assert len(rows) == 2
        assert {r["page"] for r in rows} == {"1", "5"}


import json as json_module

from tonywebb.indexing import MergeResult, merge_consecutive_continuations


class TestMergeConsecutiveContinuations:
    def test_two_consecutive_pages_merged(self, tmp_path):
        path = _write_csv(tmp_path, [
            {"matchup": "A v B", "page": "9", "date": "18950527", "content_type": "match information"},
            {"matchup": "A v B", "page": "10", "date": "18950527", "content_type": "match information"},
        ])
        result = merge_consecutive_continuations(path)
        rows = _read_rows(path)
        assert len(rows) == 1
        assert rows[0]["page"] == "9"
        assert rows[0]["pages"] == "2"
        assert result.merged_count == 1

    def test_three_consecutive_pages_merged(self, tmp_path):
        path = _write_csv(tmp_path, [
            {"matchup": "A v B", "page": "9", "date": "18950527", "content_type": "match information"},
            {"matchup": "A v B", "page": "10", "date": "18950527", "content_type": "match information"},
            {"matchup": "A v B", "page": "11", "date": "18950527", "content_type": "match information"},
        ])
        result = merge_consecutive_continuations(path)
        rows = _read_rows(path)
        assert len(rows) == 1
        assert rows[0]["page"] == "9"
        assert rows[0]["pages"] == "3"
        assert result.merged_count == 2

    def test_non_consecutive_pages_not_merged(self, tmp_path):
        # Same regression case as recompute_pages_column's own test: a real
        # separate write-up elsewhere in the collection must NOT be merged
        # away, just flagged.
        path = _write_csv(tmp_path, [
            {"matchup": "Liverpool v Oxton", "page": "59", "date": "18950907", "content_type": "match information"},
            {"matchup": "Liverpool v Oxton", "page": "61", "date": "18950907", "content_type": "match information"},
        ])
        result = merge_consecutive_continuations(path)
        rows = _read_rows(path)
        assert len(rows) == 2
        assert {r["page"] for r in rows} == {"59", "61"}
        assert result.merged_count == 0
        assert len(result.remaining_duplicates) == 2

    def test_mixed_run_and_isolated_occurrence(self, tmp_path):
        # Pages 9+10 are a continuation (merge to one row); page 20 is a
        # separate write-up of the same match (stays its own row, flagged).
        path = _write_csv(tmp_path, [
            {"matchup": "A v B", "page": "9", "date": "18950527", "content_type": "match information"},
            {"matchup": "A v B", "page": "10", "date": "18950527", "content_type": "match information"},
            {"matchup": "A v B", "page": "20", "date": "18950527", "content_type": "match information"},
        ])
        result = merge_consecutive_continuations(path)
        rows = _read_rows(path)
        assert len(rows) == 2
        by_page = {r["page"]: r for r in rows}
        assert by_page["9"]["pages"] == "2"
        assert by_page["20"]["pages"] == "1"
        assert result.merged_count == 1
        assert len(result.remaining_duplicates) == 2

    def test_unrelated_entries_untouched(self, tmp_path):
        path = _write_csv(tmp_path, [
            {"matchup": "A v B", "page": "1", "date": "18950527", "content_type": "match information"},
            {"matchup": "C v D", "page": "2", "date": "18950603", "content_type": "match information"},
        ])
        result = merge_consecutive_continuations(path)
        rows = _read_rows(path)
        assert len(rows) == 2
        assert [r["pages"] for r in rows] == ["1", "1"]
        assert result.merged_count == 0
        assert result.remaining_duplicates == []

    def test_audit_log_written_for_merged_rows(self, tmp_path):
        path = _write_csv(tmp_path, [
            {"matchup": "A v B", "page": "9", "date": "18950527", "content_type": "match information"},
            {"matchup": "A v B", "page": "10", "date": "18950527", "content_type": "match information"},
        ])
        result = merge_consecutive_continuations(path)
        assert result.log_path.exists()
        entries = [json_module.loads(line) for line in result.log_path.read_text().splitlines()]
        assert len(entries) == 1
        assert entries[0]["dropped_page"] == 10
        assert entries[0]["merged_into_page"] == 9
        assert entries[0]["matchup"] == "A v B"
        assert entries[0]["date"] == "18950527"
        assert entries[0]["content_type"] == "match information"

    def test_audit_log_path_derived_from_csv_path(self, tmp_path):
        path = _write_csv(tmp_path, [
            {"matchup": "A v B", "page": "9", "date": "18950527", "content_type": "match information"},
            {"matchup": "A v B", "page": "10", "date": "18950527", "content_type": "match information"},
        ])
        result = merge_consecutive_continuations(path)
        assert result.log_path == tmp_path / "match_index_test.merges.jsonl"

    def test_no_audit_log_written_when_nothing_merged(self, tmp_path):
        path = _write_csv(tmp_path, [
            {"matchup": "A v B", "page": "1", "date": "18950527", "content_type": "match information"},
        ])
        result = merge_consecutive_continuations(path)
        assert not result.log_path.exists()

    def test_malformed_page_row_preserved_untouched(self, tmp_path):
        path = _write_csv(tmp_path, [
            {"matchup": "A v B", "page": "not-a-number", "date": "18950527", "content_type": "match information"},
            {"matchup": "C v D", "page": "1", "date": "18950603", "content_type": "match information"},
        ])
        result = merge_consecutive_continuations(path)
        rows = _read_rows(path)
        assert len(rows) == 2
        assert any(r["matchup"] == "A v B" and r["page"] == "not-a-number" for r in rows)
        assert result.merged_count == 0

    def test_output_sorted_by_page(self, tmp_path):
        path = _write_csv(tmp_path, [
            {"matchup": "C v D", "page": "5", "date": "18950527", "content_type": "match information"},
            {"matchup": "A v B", "page": "1", "date": "18950603", "content_type": "match information"},
        ])
        merge_consecutive_continuations(path)
        rows = _read_rows(path)
        assert [r["page"] for r in rows] == ["1", "5"]

    def test_reversed_team_order_still_merged(self, tmp_path):
        # Same symmetric-key behavior as recompute_pages_column -- see
        # _row_key()'s docstring.
        path = _write_csv(tmp_path, [
            {"matchup": "Liverpool v Rock Ferry", "page": "9", "date": "18950527", "content_type": "match information"},
            {"matchup": "Rock Ferry v Liverpool", "page": "10", "date": "18950527", "content_type": "match information"},
        ])
        result = merge_consecutive_continuations(path)
        rows = _read_rows(path)
        assert len(rows) == 1
        assert result.merged_count == 1
