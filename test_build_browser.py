"""Tests for build_browser.py — confidence scoring, fuzzy grouping, and HTML generation."""

import csv
import json
import re
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from build_browser import compute_confidence, load_rows, label


# ── Label extraction ───────────────────────────────────────────────────────


class TestLabel:
    def test_strips_prefix_and_suffix(self):
        assert label("match_index_deepseek-v4-pro.csv") == "deepseek-v4-pro"

    def test_handles_complex_name(self):
        assert label("match_index_mistral-large-3:675b-cloud.csv") == "mistral-large-3:675b-cloud"

    def test_handles_willis(self):
        assert label("match_index_willis.csv") == "willis"


# ── Confidence scoring ─────────────────────────────────────────────────────


class TestComputeConfidence:
    def test_all_models_agree(self):
        present = ["m1", "m2", "m3"]
        details = {
            "m1": {"date": "18950527", "matchup": "A v B"},
            "m2": {"date": "18950527", "matchup": "A v B"},
            "m3": {"date": "18950527", "matchup": "A v B"},
        }
        conf = compute_confidence(present, details, total_models=3)
        assert conf == 1.0

    def test_single_model_low_confidence(self):
        present = ["m1"]
        details = {"m1": {"date": "18950527", "matchup": "A v B"}}
        conf = compute_confidence(present, details, total_models=6)
        assert conf < 0.4

    def test_date_disagreement_lowers_confidence(self):
        present = ["m1", "m2"]
        agree_details = {
            "m1": {"date": "18950527", "matchup": "A v B"},
            "m2": {"date": "18950527", "matchup": "A v B"},
        }
        disagree_details = {
            "m1": {"date": "18950527", "matchup": "A v B"},
            "m2": {"date": "18950603", "matchup": "A v B"},
        }
        conf_agree = compute_confidence(present, agree_details, total_models=6)
        conf_disagree = compute_confidence(present, disagree_details, total_models=6)
        assert conf_agree > conf_disagree

    def test_matchup_text_disagreement_lowers_confidence(self):
        present = ["m1", "m2"]
        same_text = {
            "m1": {"date": "18950527", "matchup": "Waterlow's v East Finchley"},
            "m2": {"date": "18950527", "matchup": "Waterlow's v East Finchley"},
        }
        diff_text = {
            "m1": {"date": "18950527", "matchup": "Waterlow's v East Finchley"},
            "m2": {"date": "18950527", "matchup": "Waterlows OC v East Finchley CC"},
        }
        conf_same = compute_confidence(present, same_text, total_models=6)
        conf_diff = compute_confidence(present, diff_text, total_models=6)
        assert conf_same > conf_diff

    def test_willis_boosts_confidence(self):
        present_no_willis = ["m1", "m2"]
        present_with_willis = ["m1", "willis"]
        details = {
            "m1": {"date": "18950527", "matchup": "A v B"},
            "m2": {"date": "18950527", "matchup": "A v B"},
            "willis": {"date": "18950527", "matchup": "A v B"},
        }
        conf_no = compute_confidence(
            present_no_willis,
            {k: details[k] for k in present_no_willis},
            total_models=6,
        )
        conf_yes = compute_confidence(
            present_with_willis,
            {k: details[k] for k in present_with_willis},
            total_models=6,
        )
        assert conf_yes > conf_no

    def test_confidence_between_0_and_1(self):
        for count in [1, 2, 3, 6]:
            present = [f"m{i}" for i in range(count)]
            details = {m: {"date": "18950527", "matchup": "A v B"} for m in present}
            conf = compute_confidence(present, details, total_models=6)
            assert 0.0 <= conf <= 1.0


# ── CSV loading ────────────────────────────────────────────────────────────


@pytest.fixture
def sample_csv(tmp_path):
    csv_path = tmp_path / "match_index_test.csv"
    with csv_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["matchup", "page", "date", "content_type", "collection", "record_id"])
        writer.writerow(["Team A v Team B", "1", "18950527", "match information", "Tony Webb minor counties collection", ""])
        writer.writerow(["Team C v Team D", "1", "18950603", "match information", "Tony Webb minor counties collection", ""])
        writer.writerow(["LCR Thring", "5", "18950814", "biography", "Tony Webb minor counties collection", ""])
    return csv_path


class TestLoadRows:
    def test_loads_correct_count(self, sample_csv):
        rows = load_rows(str(sample_csv))
        assert len(rows) == 3

    def test_key_structure(self, sample_csv):
        rows = load_rows(str(sample_csv))
        for key in rows:
            assert len(key) == 4  # (norm_key, page, date, content_type)

    def test_match_key_normalized(self, sample_csv):
        rows = load_rows(str(sample_csv))
        keys = list(rows.keys())
        # matchup_key strips punctuation and lowercases
        for k in keys:
            assert k[0] == k[0].lower()

    def test_biography_uses_title_key(self, sample_csv):
        rows = load_rows(str(sample_csv))
        bio_keys = [k for k in rows if k[3] == "biography"]
        assert len(bio_keys) == 1

    def test_empty_date_excluded(self, tmp_path):
        csv_path = tmp_path / "match_index_empty.csv"
        with csv_path.open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["matchup", "page", "date", "content_type", "collection", "record_id"])
            writer.writerow(["A v B", "1", "", "match information", "col", ""])
        rows = load_rows(str(csv_path))
        assert len(rows) == 0


# ── HTML generation (integration) ─────────────────────────────────────────


class TestBuildBrowserIntegration:
    def test_html_output_contains_key_elements(self, tmp_path, monkeypatch):
        """Build the browser with test data and check the HTML output."""
        # Create minimal test CSVs
        for model in ["model_a", "model_b"]:
            csv_path = tmp_path / f"match_index_{model}.csv"
            with csv_path.open("w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["matchup", "page", "date", "content_type", "collection", "record_id"])
                writer.writerow(["Team A v Team B", "1", "18950527", "match information", "coll", ""])
                if model == "model_b":
                    writer.writerow(["Team A v Team B", "1", "18950603", "match information", "coll", ""])

        monkeypatch.chdir(tmp_path)
        import build_browser
        build_browser.main()

        html_path = tmp_path / "compare_browser.html"
        assert html_path.exists()
        html = html_path.read_text()

        assert "Match Index Browser" in html
        assert "confidence" in html.lower()
        assert "Review Queue" in html
        assert "Export Reviewed CSV" in html
        assert "date-conflict" in html or "date_conflict" in html
        assert "Show page image" in html or "data-img" in html

    def test_json_data_embedded(self, tmp_path, monkeypatch):
        csv_path = tmp_path / "match_index_test.csv"
        with csv_path.open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["matchup", "page", "date", "content_type", "collection", "record_id"])
            writer.writerow(["X v Y", "1", "18950527", "match information", "coll", ""])

        monkeypatch.chdir(tmp_path)
        import build_browser
        build_browser.main()

        html = (tmp_path / "compare_browser.html").read_text()
        # Extract JSON from script tag
        match = re.search(r'<script id="data" type="application/json">(.*?)</script>', html, re.DOTALL)
        assert match
        data = json.loads(match.group(1))
        assert "models" in data
        assert "rows" in data
        assert len(data["rows"]) >= 1
        assert data["rows"][0]["confidence"] is not None
