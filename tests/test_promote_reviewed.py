"""Tests for promote_reviewed.py — merging reviewed entries into the Willis ground truth."""

import argparse
import csv
from pathlib import Path

from tonywebb.promote_reviewed import run


def _write_csv(tmp_path: Path, name: str, rows: list[dict], extra_fields: list[str] | None = None) -> Path:
    fieldnames = ["matchup", "page", "date", "content_type", "collection", "record_id"] + (extra_fields or [])
    path = tmp_path / name
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow({"collection": "Tony Webb minor counties collection", "record_id": "", **r})
    return path


def _make_ns(**kwargs) -> argparse.Namespace:
    defaults = dict(reviewed=None, truth="match_index_willis.csv", dry_run=False)
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


class TestPromoteReviewed:
    def test_new_rows_appended(self, tmp_path, monkeypatch, capsys):
        truth_path = _write_csv(tmp_path, "match_index_willis.csv", [
            {"matchup": "A v B", "page": "1", "date": "18950527", "content_type": "match information"},
        ])
        reviewed_path = _write_csv(tmp_path, "match_index_reviewed.csv", [
            {"matchup": "C v D", "page": "2", "date": "18950603", "content_type": "match information", "notes": "looks right"},
        ], extra_fields=["notes"])

        monkeypatch.chdir(tmp_path)
        run(_make_ns(reviewed=str(reviewed_path), truth=str(truth_path)))

        rows = truth_path.read_text().strip().splitlines()
        assert len(rows) == 3  # header + original + new
        assert any("C v D" in r for r in rows)
        out = capsys.readouterr().out
        assert "New: 1" in out
        assert "Promoted 1 row(s)" in out

    def test_duplicate_rows_not_reappended(self, tmp_path, monkeypatch, capsys):
        truth_path = _write_csv(tmp_path, "match_index_willis.csv", [
            {"matchup": "A v B", "page": "1", "date": "18950527", "content_type": "match information"},
        ])
        reviewed_path = _write_csv(tmp_path, "match_index_reviewed.csv", [
            {"matchup": "A v B", "page": "1", "date": "18950527", "content_type": "match information", "notes": ""},
        ], extra_fields=["notes"])

        monkeypatch.chdir(tmp_path)
        run(_make_ns(reviewed=str(reviewed_path), truth=str(truth_path)))

        rows = truth_path.read_text().strip().splitlines()
        assert len(rows) == 2  # header + original only -- nothing appended
        out = capsys.readouterr().out
        assert "New: 0" in out
        assert "Nothing to promote" in out

    def test_duplicate_detected_despite_text_variant(self, tmp_path, monkeypatch, capsys):
        # "Waterlow's OC" and "Waterlow's" normalize to the same key.
        truth_path = _write_csv(tmp_path, "match_index_willis.csv", [
            {"matchup": "Waterlow's v East Finchley", "page": "1", "date": "18950527", "content_type": "match information"},
        ])
        reviewed_path = _write_csv(tmp_path, "match_index_reviewed.csv", [
            {"matchup": "Waterlow's OC v East Finchley", "page": "1", "date": "18950527", "content_type": "match information", "notes": ""},
        ], extra_fields=["notes"])

        monkeypatch.chdir(tmp_path)
        run(_make_ns(reviewed=str(reviewed_path), truth=str(truth_path)))
        out = capsys.readouterr().out
        assert "New: 0" in out

    def test_dry_run_writes_nothing(self, tmp_path, monkeypatch, capsys):
        truth_path = _write_csv(tmp_path, "match_index_willis.csv", [
            {"matchup": "A v B", "page": "1", "date": "18950527", "content_type": "match information"},
        ])
        reviewed_path = _write_csv(tmp_path, "match_index_reviewed.csv", [
            {"matchup": "C v D", "page": "2", "date": "18950603", "content_type": "match information", "notes": ""},
        ], extra_fields=["notes"])
        original_content = truth_path.read_text()

        monkeypatch.chdir(tmp_path)
        run(_make_ns(reviewed=str(reviewed_path), truth=str(truth_path), dry_run=True))

        assert truth_path.read_text() == original_content
        out = capsys.readouterr().out
        assert "--dry-run: no changes written" in out

    def test_missing_reviewed_file_exits(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        import pytest
        with pytest.raises(SystemExit):
            run(_make_ns(reviewed=str(tmp_path / "nope.csv")))

    def test_creates_truth_file_if_missing(self, tmp_path, monkeypatch, capsys):
        reviewed_path = _write_csv(tmp_path, "match_index_reviewed.csv", [
            {"matchup": "C v D", "page": "2", "date": "18950603", "content_type": "match information", "notes": ""},
        ], extra_fields=["notes"])
        truth_path = tmp_path / "match_index_willis.csv"

        monkeypatch.chdir(tmp_path)
        run(_make_ns(reviewed=str(reviewed_path), truth=str(truth_path)))

        assert truth_path.exists()
        rows = truth_path.read_text().strip().splitlines()
        assert rows[0] == "matchup,page,date,content_type,collection,record_id"
        assert len(rows) == 2
        out = capsys.readouterr().out
        assert "does not exist yet" in out
