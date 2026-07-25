"""Tests for consensus.py — majority-vote merge of multiple match indexes."""

import argparse
import csv
from pathlib import Path

from tonywebb.consensus import ConsensusRow, _label, build_consensus, format_consensus_report, run
from tonywebb.evaluate import IndexRow


def _row(matchup, page, date, content_type="match information"):
    return IndexRow(matchup=matchup, page=page, date=date, content_type=content_type)


class TestLabel:
    def test_strips_match_index_prefix(self):
        assert _label("match_index_qwen3.5_cloud.csv") == "qwen3.5_cloud"

    def test_strips_stats_index_prefix(self):
        assert _label("stats_index_glm-5.2_cloud.csv") == "glm-5.2_cloud"


class TestBuildConsensus:
    def test_unanimous_row(self):
        rows = {
            "model_a": [_row("A v B", 1, "18950527")],
            "model_b": [_row("A v B", 1, "18950527")],
        }
        consensus = build_consensus(rows)
        assert len(consensus) == 1
        c = consensus[0]
        assert c.matchup == "A v B"
        assert c.date == "18950527"
        assert not c.has_date_conflict
        assert not c.has_matchup_conflict
        assert set(c.sources) == {"model_a", "model_b"}

    def test_date_conflict_majority_wins(self):
        rows = {
            "model_a": [_row("A v B", 1, "18950527")],
            "model_b": [_row("A v B", 1, "18950527")],
            "model_c": [_row("A v B", 1, "18950603")],
        }
        consensus = build_consensus(rows)
        c = consensus[0]
        assert c.date == "18950527"  # 2 vs 1
        assert c.has_date_conflict

    def test_matchup_text_conflict_majority_wins(self):
        # "Waterlows v East Finchley CC" normalizes (CC stripped, apostrophe
        # stripped for the grouping key) to the same key as the apostrophe'd
        # form, so these group together -- but the raw text differs, which is
        # exactly the kind of variant the report should flag for review.
        rows = {
            "model_a": [_row("Waterlow's v East Finchley", 1, "18950527")],
            "model_b": [_row("Waterlow's v East Finchley", 1, "18950527")],
            "model_c": [_row("Waterlows v East Finchley CC", 1, "18950527")],
        }
        consensus = build_consensus(rows)
        c = consensus[0]
        assert c.matchup == "Waterlow's v East Finchley"
        assert c.has_matchup_conflict

    def test_willis_date_wins_outright(self):
        rows = {
            "model_a": [_row("A v B", 1, "18950601")],
            "model_b": [_row("A v B", 1, "18950601")],
            "model_c": [_row("A v B", 1, "18950601")],
        }
        truth = [_row("A v B", 1, "18950527")]  # Willis disagrees with unanimous models
        consensus = build_consensus(rows, truth)
        c = consensus[0]
        assert c.date == "18950527"
        assert c.from_willis is True

    def test_willis_matchup_spelling_wins(self):
        rows = {"model_a": [_row("Waterlows v East Finchley CC", 1, "18950527")]}
        truth = [_row("Waterlow's v East Finchley", 1, "18950527")]
        consensus = build_consensus(rows, truth)
        assert consensus[0].matchup == "Waterlow's v East Finchley"

    def test_willis_only_row_included(self):
        # A row Willis has that no model found at all must still appear.
        rows = {"model_a": [_row("X v Y", 1, "18950527")]}
        truth = [_row("A v B", 1, "18950527")]
        consensus = build_consensus(rows, truth)
        matchups = {c.matchup for c in consensus}
        assert "A v B" in matchups
        willis_row = next(c for c in consensus if c.matchup == "A v B")
        assert willis_row.sources == []
        assert willis_row.from_willis is True

    def test_model_only_row_kept_and_flagged_low_agreement(self):
        rows = {
            "model_a": [_row("A v B", 1, "18950527")],
            "model_b": [],
        }
        consensus = build_consensus(rows)
        assert len(consensus) == 1
        assert consensus[0].sources == ["model_a"]
        assert consensus[0].total_sources == 2

    def test_different_pages_not_merged(self):
        rows = {
            "model_a": [_row("A v B", 1, "18950527")],
            "model_b": [_row("A v B", 2, "18950527")],
        }
        consensus = build_consensus(rows)
        assert len(consensus) == 2

    def test_different_content_types_not_merged(self):
        rows = {
            "model_a": [_row("Newbury", 1, "18950000", content_type="team information")],
            "model_b": [_row("Newbury", 1, "18950000", content_type="statistics")],
        }
        consensus = build_consensus(rows)
        assert len(consensus) == 2

    def test_no_usable_date_leaves_it_blank(self):
        rows = {"model_a": [_row("A v B", 1, "")]}
        consensus = build_consensus(rows)
        assert consensus[0].date == ""


class TestFormatConsensusReport:
    def test_summary_counts(self):
        rows = {
            "model_a": [_row("A v B", 1, "18950527")],
            "model_b": [_row("A v B", 1, "18950603")],
        }
        consensus = build_consensus(rows)
        report = format_consensus_report(consensus)
        assert "Total consensus rows: 1" in report
        assert "Date conflicts: 1" in report
        assert "A v B" in report

    def test_low_agreement_section_lists_single_source_rows(self):
        rows = {
            "model_a": [_row("A v B", 1, "18950527")],
            "model_b": [],
            "model_c": [],
        }
        consensus = build_consensus(rows)
        report = format_consensus_report(consensus)
        assert "Low-agreement rows (found by only 1 model, not in Willis): 1" in report


def _write_csv(tmp_path: Path, name: str, rows: list[dict]) -> Path:
    path = tmp_path / name
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["matchup", "page", "date", "content_type", "collection", "record_id"])
        writer.writeheader()
        for r in rows:
            writer.writerow({"collection": "Tony Webb minor counties collection", "record_id": "", **r})
    return path


def _make_ns(**kwargs) -> argparse.Namespace:
    defaults = dict(
        pattern="match_index_*.csv", truth="match_index_willis.csv",
        output="consensus_index.csv", report="consensus_report.md", min_agreement=1,
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


class TestRunCLI:
    def test_writes_consensus_csv_and_report(self, tmp_path, monkeypatch):
        _write_csv(tmp_path, "match_index_model_a.csv", [
            {"matchup": "A v B", "page": "1", "date": "18950527", "content_type": "match information"},
        ])
        _write_csv(tmp_path, "match_index_model_b.csv", [
            {"matchup": "A v B", "page": "1", "date": "18950527", "content_type": "match information"},
        ])
        monkeypatch.chdir(tmp_path)
        run(_make_ns(truth=""))

        out_csv = (tmp_path / "consensus_index.csv").read_text().strip().splitlines()
        assert out_csv[0] == "matchup,page,date,content_type,collection,record_id"
        assert len(out_csv) == 2
        assert (tmp_path / "consensus_report.md").exists()

    def test_min_agreement_drops_single_source_rows(self, tmp_path, monkeypatch, capsys):
        _write_csv(tmp_path, "match_index_model_a.csv", [
            {"matchup": "A v B", "page": "1", "date": "18950527", "content_type": "match information"},
        ])
        _write_csv(tmp_path, "match_index_model_b.csv", [])
        monkeypatch.chdir(tmp_path)
        run(_make_ns(truth="", min_agreement=2))

        out_csv = (tmp_path / "consensus_index.csv").read_text().strip().splitlines()
        assert len(out_csv) == 1  # header only -- the single-source row got dropped
        out = capsys.readouterr().out
        assert "Dropped 1 row(s)" in out

    def test_no_matching_files_prints_message(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        run(_make_ns(truth=""))
        out = capsys.readouterr().out
        assert "No files matching" in out

    def test_missing_truth_file_proceeds_without_it(self, tmp_path, monkeypatch, capsys):
        _write_csv(tmp_path, "match_index_model_a.csv", [
            {"matchup": "A v B", "page": "1", "date": "18950527", "content_type": "match information"},
        ])
        monkeypatch.chdir(tmp_path)
        run(_make_ns(truth="match_index_willis.csv"))  # doesn't exist in tmp_path
        out = capsys.readouterr().out
        assert "Truth file not found" in out
        assert (tmp_path / "consensus_index.csv").exists()
