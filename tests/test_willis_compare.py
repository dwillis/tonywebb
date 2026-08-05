"""Tests for willis_compare.py — Willis-vs-model comparison row building."""

import csv
import json
import re

import pytest

from tonywebb.evaluate import IndexRow
from tonywebb.willis_compare import build_comparison_rows


class TestBuildComparisonRows:
    def test_exact_match_is_matched(self):
        truth = [IndexRow("Team A v Team B", 1, "18950527", "match information")]
        model = [IndexRow("Team A v Team B", 1, "18950527", "match information")]
        rows = build_comparison_rows(truth, model)
        assert len(rows) == 1
        assert rows[0]["status"] == "matched"
        assert rows[0]["page"] == 1
        assert rows[0]["content_type"] == "match information"
        assert rows[0]["willis"] == {"matchup": "Team A v Team B", "date": "18950527"}
        assert rows[0]["model"] == {"matchup": "Team A v Team B", "date": "18950527"}

    def test_fuzzy_match_is_matched(self):
        truth = [IndexRow("Kensworth v Dunstable Victoria", 1, "18950527", "match information")]
        model = [IndexRow("Kensworth v Dunstable Vic", 1, "18950527", "match information")]
        rows = build_comparison_rows(truth, model, fuzzy_threshold=0.8)
        assert len(rows) == 1
        assert rows[0]["status"] == "matched"
        assert rows[0]["similarity"] is not None
        assert 0.0 < rows[0]["similarity"] < 1.0

    def test_willis_only_is_missed(self):
        truth = [IndexRow("Team A v Team B", 1, "18950527", "match information")]
        model = []
        rows = build_comparison_rows(truth, model)
        assert len(rows) == 1
        assert rows[0]["status"] == "missed"
        assert rows[0]["willis"]["matchup"] == "Team A v Team B"
        assert rows[0]["model"] is None
        assert rows[0]["similarity"] is None

    def test_model_only_on_covered_page_is_surplus(self):
        truth = [IndexRow("Team A v Team B", 1, "18950527", "match information")]
        model = [
            IndexRow("Team A v Team B", 1, "18950527", "match information"),
            IndexRow("Team C v Team D", 1, "18950527", "match information"),
        ]
        rows = build_comparison_rows(truth, model)
        surplus = [r for r in rows if r["status"] == "surplus"]
        assert len(surplus) == 1
        assert surplus[0]["willis"] is None
        assert surplus[0]["model"]["matchup"] == "Team C v Team D"

    def test_model_only_on_uncovered_page_is_unindexed(self):
        # Willis only covers page 1 here; page 62 has no ground truth at all.
        truth = [IndexRow("Team A v Team B", 1, "18950527", "match information")]
        model = [
            IndexRow("Team A v Team B", 1, "18950527", "match information"),
            IndexRow("Team E v Team F", 62, "18950801", "match information"),
        ]
        rows = build_comparison_rows(truth, model)
        page_62 = next(r for r in rows if r["page"] == 62)
        assert page_62["status"] == "unindexed"
        assert page_62["willis"] is None
        assert page_62["model"]["matchup"] == "Team E v Team F"

    def test_rows_sorted_by_page(self):
        truth = [
            IndexRow("A v B", 5, "18950527", "match information"),
            IndexRow("C v D", 1, "18950527", "match information"),
        ]
        model = [
            IndexRow("A v B", 5, "18950527", "match information"),
            IndexRow("C v D", 1, "18950527", "match information"),
        ]
        rows = build_comparison_rows(truth, model)
        pages = [r["page"] for r in rows]
        assert pages == sorted(pages)

    def test_similarity_none_for_missed_and_surplus(self):
        # These two matchups must be dissimilar enough that SequenceMatcher
        # stays below fuzzy_threshold — "Team A v Team B" vs "Team C v Team D"
        # share too much boilerplate structure ("Team _ v Team _") and score
        # 0.867, which would make evaluate() fuzzy-match them instead of
        # leaving them missed/surplus.
        truth = [IndexRow("Team A v Team B", 1, "18950527", "match information")]
        model = [IndexRow("Nowhere United v Somewhere Town", 1, "18950527", "match information")]
        rows = build_comparison_rows(truth, model, fuzzy_threshold=0.8)
        for r in rows:
            assert r["similarity"] is None


def _write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["matchup", "page", "date", "content_type", "collection", "pages"])
        for row in rows:
            writer.writerow(row)


class TestRunWillisCompare:
    def test_writes_output_file(self, tmp_path, monkeypatch):
        _write_csv(tmp_path / "match_index_willis.csv", [
            ["Team A v Team B", "1", "18950527", "match information", "coll", ""],
        ])
        _write_csv(tmp_path / "match_index_modelx.csv", [
            ["Team A v Team B", "1", "18950527", "match information", "coll", ""],
        ])

        monkeypatch.chdir(tmp_path)
        from tonywebb.willis_compare import run_willis_compare
        run_willis_compare(
            pattern="match_index_*.csv",
            truth_path="match_index_willis.csv",
            output_path="browser/willis_compare.html",
        )

        out = tmp_path / "browser" / "willis_compare.html"
        assert out.exists()

    def test_truth_file_excluded_from_models(self, tmp_path, monkeypatch):
        _write_csv(tmp_path / "match_index_willis.csv", [
            ["Team A v Team B", "1", "18950527", "match information", "coll", ""],
        ])
        _write_csv(tmp_path / "match_index_modelx.csv", [
            ["Team A v Team B", "1", "18950527", "match information", "coll", ""],
        ])

        monkeypatch.chdir(tmp_path)
        from tonywebb.willis_compare import run_willis_compare
        run_willis_compare(
            pattern="match_index_*.csv",
            truth_path="match_index_willis.csv",
            output_path="willis_compare.html",
        )

        html = (tmp_path / "willis_compare.html").read_text()
        match = re.search(r'<script id="data" type="application/json">(.*?)</script>', html, re.DOTALL)
        assert match
        data = json.loads(match.group(1))
        assert data["models"] == ["modelx"]
        assert "willis" not in data["models"]

    def test_missing_truth_file_does_not_crash(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        from tonywebb.willis_compare import run_willis_compare
        run_willis_compare(truth_path="does_not_exist.csv")
        captured = capsys.readouterr()
        assert "not found" in captured.out.lower()
        assert not (tmp_path / "browser" / "willis_compare.html").exists()


class TestCLI:
    def test_registered_in_parser(self):
        from tonywebb.cli import build_parser
        parser = build_parser()
        args = parser.parse_args(["willis-compare", "--pattern", "x.csv"])
        assert args.pattern == "x.csv"
        assert args.command == "willis-compare"
