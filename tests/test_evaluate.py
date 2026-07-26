import argparse
import csv
from pathlib import Path

from tonywebb.evaluate import IndexRow, _label, coverage_by_content_type, evaluate, format_report, load_index, run

FIXTURES = Path(__file__).parent / "fixtures"
WILLIS_SAMPLE = FIXTURES / "willis_sample.csv"


class TestLoadIndex:
    def test_loads_valid_rows(self):
        rows, skipped = load_index(WILLIS_SAMPLE)
        assert len(rows) == 15
        assert all(isinstance(r, IndexRow) for r in rows)

    def test_skips_bad_page(self):
        rows, skipped = load_index(WILLIS_SAMPLE)
        reasons = {s["reason"] for s in skipped}
        assert "bad page" in reasons

    def test_skips_empty_content_type(self):
        rows, skipped = load_index(WILLIS_SAMPLE)
        reasons = {s["reason"] for s in skipped}
        assert "empty content_type" in reasons

    def test_skipped_count(self):
        rows, skipped = load_index(WILLIS_SAMPLE)
        assert len(skipped) == 2

    def test_page_is_int(self):
        rows, _ = load_index(WILLIS_SAMPLE)
        assert all(isinstance(r.page, int) for r in rows)

    def test_pages_column_parsed(self):
        rows, _ = load_index(WILLIS_SAMPLE)
        assert all(isinstance(r.pages, int) for r in rows)

    def test_missing_pages_column_defaults_to_1(self, tmp_path):
        # Older CSVs written before this feature existed have no "pages"
        # column at all -- must not error, just default to 1.
        path = tmp_path / "no_pages_column.csv"
        path.write_text(
            "matchup,page,date,content_type,collection\n"
            "A v B,1,18950527,match information,Tony Webb minor counties collection\n",
            encoding="utf-8",
        )
        rows, skipped = load_index(path)
        assert skipped == []
        assert rows[0].pages == 1

    def test_blank_pages_value_defaults_to_1(self, tmp_path):
        path = tmp_path / "blank_pages.csv"
        path.write_text(
            "matchup,page,date,content_type,collection,pages\n"
            "A v B,1,18950527,match information,Tony Webb minor counties collection,\n",
            encoding="utf-8",
        )
        rows, _ = load_index(path)
        assert rows[0].pages == 1


def _write_csv(tmp_path: Path, name: str, rows: list[dict]) -> Path:
    path = tmp_path / name
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["matchup", "page", "date", "content_type", "collection", "pages"])
        writer.writeheader()
        for r in rows:
            writer.writerow({"collection": "Tony Webb minor counties collection", "pages": "1", **r})
    return path


class TestEvaluate:
    def test_exact_match_counted(self, tmp_path: Path):
        truth = [IndexRow("Kensworth v Dunstable Victoria", 1, "18950527", "match information")]
        model = [IndexRow("Kensworth v Dunstable Victoria", 1, "18950527", "match information")]
        result = evaluate(truth, model)
        assert len(result.matched) == 1
        assert result.matched[0].kind == "exact"
        assert not result.missed
        assert not result.surplus

    def test_fuzzy_match_counted(self):
        truth = [IndexRow("Kensworth v Dunstable Victoria", 1, "18950527", "match information")]
        model = [IndexRow("Kensworth v Dunstable Vic", 1, "18950527", "match information")]
        result = evaluate(truth, model, fuzzy_threshold=0.8)
        assert len(result.matched) == 1
        assert result.matched[0].kind == "fuzzy"

    def test_reversed_team_order_is_exact_match(self):
        # Regression test: a prose-derived report and a manual index may
        # list the same two teams in opposite order (neither is "wrong") --
        # this must match exactly, not fall to fuzzy or miss entirely.
        truth = [IndexRow("Liverpool v Rock Ferry", 54, "18950817", "match information")]
        model = [IndexRow("Rock Ferry v Liverpool", 54, "18950817", "match information")]
        result = evaluate(truth, model)
        assert len(result.matched) == 1
        assert result.matched[0].kind == "exact"
        assert not result.missed
        assert not result.surplus

    def test_below_threshold_is_missed(self):
        truth = [IndexRow("Kensworth v Dunstable Victoria", 1, "18950527", "match information")]
        model = [IndexRow("Nowhere United v Somewhere Town", 1, "18950527", "match information")]
        result = evaluate(truth, model, fuzzy_threshold=0.8)
        assert len(result.matched) == 0
        assert len(result.missed) == 1
        assert len(result.surplus) == 1

    def test_surplus_on_covered_page(self):
        truth = [IndexRow("A v B", 1, "18950527", "match information")]
        model = [
            IndexRow("A v B", 1, "18950527", "match information"),
            IndexRow("C v D", 1, "18950527", "match information"),
        ]
        result = evaluate(truth, model)
        assert len(result.matched) == 1
        assert len(result.surplus) == 1
        assert result.surplus[0].matchup == "C v D"

    def test_pages_outside_truth_are_ignored(self):
        truth = [IndexRow("A v B", 1, "18950527", "match information")]
        model = [
            IndexRow("A v B", 1, "18950527", "match information"),
            IndexRow("Z v Y", 99, "18950527", "match information"),  # page not in truth
        ]
        result = evaluate(truth, model)
        assert result.pages_covered == [1]
        assert len(result.surplus) == 0  # page 99 not evaluated at all

    def test_date_agreement(self):
        truth = [
            IndexRow("A v B", 1, "18950527", "match information"),
            IndexRow("C v D", 1, "18950528", "match information"),
        ]
        model = [
            IndexRow("A v B", 1, "18950527", "match information"),  # date matches
            IndexRow("C v D", 1, "18950601", "match information"),  # date differs
        ]
        result = evaluate(truth, model)
        assert result.date_agree == 1
        assert result.date_total == 2

    def test_content_type_mismatch_detected(self):
        truth = [IndexRow("Newbury", 1, "", "team information")]
        model = [IndexRow("Newbury", 1, "", "statistics")]  # same title, different type
        result = evaluate(truth, model)
        # exact pass requires type equality, so this is a "missed" for coverage purposes...
        assert len(result.matched) == 0
        # ...but the type-blind pass should still see the title match and record the type mismatch
        assert result.type_total == 1
        assert result.type_agree == 0

    def test_greedy_fuzzy_prefers_higher_similarity(self):
        truth = [IndexRow("Kensworth v Dunstable Victoria", 1, "", "match information")]
        model = [
            IndexRow("Kensworth v Dunstable Vic", 1, "", "match information"),  # closer
            IndexRow("Kensworth v Dunstable", 1, "", "match information"),  # further
        ]
        result = evaluate(truth, model, fuzzy_threshold=0.5)
        assert len(result.matched) == 1
        assert result.matched[0].model.matchup == "Kensworth v Dunstable Vic"


class TestPagesAgreement:
    def test_matching_pages_count_agrees(self):
        truth = [IndexRow("A v B", 1, "18950527", "match information", pages=2)]
        model = [IndexRow("A v B", 1, "18950527", "match information", pages=2)]
        result = evaluate(truth, model)
        assert result.pages_agree == 1
        assert result.pages_total == 1

    def test_mismatched_pages_count_disagrees(self):
        # Willis flags this as spanning 2 pages; the model only caught it on
        # one -- exactly the page-61-style miss this feature exists to surface.
        truth = [IndexRow("A v B", 1, "18950527", "match information", pages=2)]
        model = [IndexRow("A v B", 1, "18950527", "match information", pages=1)]
        result = evaluate(truth, model)
        assert result.pages_agree == 0
        assert result.pages_total == 1

    def test_default_pages_of_1_agrees_by_default(self):
        truth = [IndexRow("A v B", 1, "18950527", "match information")]
        model = [IndexRow("A v B", 1, "18950527", "match information")]
        result = evaluate(truth, model)
        assert result.pages_agree == 1
        assert result.pages_total == 1

    def test_unmatched_rows_not_counted(self):
        truth = [IndexRow("A v B", 1, "18950527", "match information", pages=2)]
        model = [IndexRow("Nowhere United v Somewhere Town", 1, "18950527", "match information", pages=1)]
        result = evaluate(truth, model)
        assert result.pages_total == 0

    def test_report_includes_pages_agreement_line(self):
        truth = [IndexRow("A v B", 1, "18950527", "match information", pages=2)]
        model = [IndexRow("A v B", 1, "18950527", "match information", pages=1)]
        result = evaluate(truth, model)
        report = format_report("test", result, truth, [], [])
        assert "Pages-count agreement" in report
        assert "0/1" in report


class TestCoverageByContentType:
    def test_buckets_by_type(self):
        truth = [
            IndexRow("A v B", 1, "", "match information"),
            IndexRow("Newbury stats", 1, "", "statistics"),
        ]
        model = [IndexRow("A v B", 1, "", "match information")]
        result = evaluate(truth, model)
        by_type = coverage_by_content_type(result, truth)
        assert by_type["match information"] == (1, 1)
        assert by_type["statistics"] == (0, 1)


class TestFormatReportPagesFilter:
    def test_no_note_when_no_filter(self):
        truth = [IndexRow("A v B", 1, "", "match information")]
        model = [IndexRow("A v B", 1, "", "match information")]
        result = evaluate(truth, model)
        report = format_report("test", result, truth, [], [], pages_filter=None)
        assert "Restricted to pages" not in report

    def test_note_present_when_filtered(self):
        truth = [IndexRow("A v B", 1, "", "match information")]
        model = [IndexRow("A v B", 1, "", "match information")]
        result = evaluate(truth, model)
        report = format_report("test", result, truth, [], [], pages_filter={1})
        assert "Restricted to pages [1]" in report


def _make_ns(**kwargs) -> argparse.Namespace:
    defaults = dict(
        csv_path=None, truth=None, fuzzy_threshold=0.8, report=None, all=False,
        pages=None, content_types=None,
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


class TestRunPagesFilterCLI:
    def _setup(self, tmp_path: Path) -> tuple[Path, Path]:
        truth_path = _write_csv(tmp_path, "match_index_willis.csv", [
            {"matchup": "A v B", "page": "1", "date": "18950527", "content_type": "match information"},
            {"matchup": "C v D", "page": "1", "date": "18950527", "content_type": "match information"},
            {"matchup": "E v F", "page": "2", "date": "18950527", "content_type": "match information"},
        ])
        model_path = _write_csv(tmp_path, "match_index_test.csv", [
            {"matchup": "A v B", "page": "1", "date": "18950527", "content_type": "match information"},
            # page 2 deliberately not attempted by this model run
        ])
        return truth_path, model_path

    def test_unfiltered_coverage_dilutes_across_all_truth_pages(self, tmp_path, monkeypatch, capsys):
        truth_path, model_path = self._setup(tmp_path)
        monkeypatch.chdir(tmp_path)
        run(_make_ns(csv_path=str(model_path), truth=str(truth_path)))
        out = capsys.readouterr().out
        assert "coverage=33.3% (1/3)" in out

    def test_pages_filter_restricts_denominator(self, tmp_path, monkeypatch, capsys):
        truth_path, model_path = self._setup(tmp_path)
        monkeypatch.chdir(tmp_path)
        run(_make_ns(csv_path=str(model_path), truth=str(truth_path), pages="1"))
        out = capsys.readouterr().out
        assert "coverage=50.0% (1/2)" in out

    def test_pages_filter_report_has_note(self, tmp_path, monkeypatch):
        truth_path, model_path = self._setup(tmp_path)
        monkeypatch.chdir(tmp_path)
        run(_make_ns(csv_path=str(model_path), truth=str(truth_path), pages="1"))
        report = (tmp_path / "eval_test.md").read_text()
        assert "Restricted to pages [1]" in report

    def test_pages_filter_with_no_matching_truth_rows_exits(self, tmp_path, monkeypatch):
        truth_path, model_path = self._setup(tmp_path)
        monkeypatch.chdir(tmp_path)
        import pytest
        with pytest.raises(SystemExit):
            run(_make_ns(csv_path=str(model_path), truth=str(truth_path), pages="99"))


class TestRunContentTypesFilterCLI:
    def _setup(self, tmp_path: Path) -> tuple[Path, Path]:
        truth_path = _write_csv(tmp_path, "match_index_willis.csv", [
            {"matchup": "A v B", "page": "1", "date": "18950527", "content_type": "match information"},
            {"matchup": "Newbury player statistics", "page": "1", "date": "18950000", "content_type": "statistics"},
            {"matchup": "Speen player statistics", "page": "2", "date": "18950000", "content_type": "statistics"},
        ])
        model_path = _write_csv(tmp_path, "stats_index_test.csv", [
            {"matchup": "Newbury player statistics", "page": "1", "date": "18950000", "content_type": "statistics"},
            {"matchup": "Speen player statistics", "page": "2", "date": "18950000", "content_type": "statistics"},
        ])
        return truth_path, model_path

    def test_unfiltered_coverage_dilutes_across_all_content_types(self, tmp_path, monkeypatch, capsys):
        truth_path, model_path = self._setup(tmp_path)
        monkeypatch.chdir(tmp_path)
        run(_make_ns(csv_path=str(model_path), truth=str(truth_path)))
        out = capsys.readouterr().out
        assert "coverage=66.7% (2/3)" in out

    def test_content_types_filter_restricts_denominator(self, tmp_path, monkeypatch, capsys):
        truth_path, model_path = self._setup(tmp_path)
        monkeypatch.chdir(tmp_path)
        run(_make_ns(csv_path=str(model_path), truth=str(truth_path), content_types="statistics"))
        out = capsys.readouterr().out
        assert "coverage=100.0% (2/2)" in out

    def test_content_types_filter_report_has_note(self, tmp_path, monkeypatch):
        truth_path, model_path = self._setup(tmp_path)
        monkeypatch.chdir(tmp_path)
        run(_make_ns(csv_path=str(model_path), truth=str(truth_path), content_types="statistics"))
        report = (tmp_path / "eval_test.md").read_text()
        assert "Restricted to content type(s) ['statistics']" in report

    def test_content_types_filter_case_insensitive(self, tmp_path, monkeypatch, capsys):
        truth_path, model_path = self._setup(tmp_path)
        monkeypatch.chdir(tmp_path)
        run(_make_ns(csv_path=str(model_path), truth=str(truth_path), content_types="STATISTICS"))
        out = capsys.readouterr().out
        assert "coverage=100.0% (2/2)" in out

    def test_content_types_filter_with_no_matching_truth_rows_exits(self, tmp_path, monkeypatch):
        truth_path, model_path = self._setup(tmp_path)
        monkeypatch.chdir(tmp_path)
        import pytest
        with pytest.raises(SystemExit):
            run(_make_ns(csv_path=str(model_path), truth=str(truth_path), content_types="biography"))

    def test_label_strips_stats_index_prefix(self, tmp_path, monkeypatch):
        truth_path, model_path = self._setup(tmp_path)
        monkeypatch.chdir(tmp_path)
        run(_make_ns(csv_path=str(model_path), truth=str(truth_path), content_types="statistics"))
        assert (tmp_path / "eval_test.md").exists()


class TestLabel:
    def test_strips_match_index_prefix(self):
        assert _label("match_index_qwen3.5_cloud.csv") == "qwen3.5_cloud"

    def test_strips_stats_index_prefix(self):
        assert _label("stats_index_qwen3.5_397b-cloud.csv") == "qwen3.5_397b-cloud"

    def test_strips_scorecard_index_prefix(self):
        assert _label("scorecard_index_glm-5.2_cloud.csv") == "glm-5.2_cloud"

    def test_unknown_prefix_left_as_is(self):
        assert _label("something_else.csv") == "something_else"
