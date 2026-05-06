"""Tests for generate_clubs.py — club list generation and grouping logic."""

import csv
from pathlib import Path

import pytest

from generate_clubs import (
    canonical_key,
    extract_teams_from_csv,
    guess_type,
    normalize_apostrophes,
    strip_cc_oc,
    strip_mr,
)


# ── String cleaning helpers ────────────────────────────────────────────────


class TestNormalizeApostrophes:
    def test_curly_to_straight(self):
        assert normalize_apostrophes("Waterlow’s") == "Waterlow's"

    def test_left_quote_to_straight(self):
        assert normalize_apostrophes("Waterlow‘s") == "Waterlow's"

    def test_straight_unchanged(self):
        assert normalize_apostrophes("Waterlow's") == "Waterlow's"


class TestStripCcOc:
    def test_strips_cc(self):
        assert strip_cc_oc("Dunstable CC") == "Dunstable"

    def test_strips_cricket_club(self):
        assert strip_cc_oc("Dunstable Cricket Club") == "Dunstable"

    def test_strips_oc(self):
        assert strip_cc_oc("Waterlow's OC") == "Waterlow's"

    def test_strips_dotted_cc(self):
        assert strip_cc_oc("Dunstable C.C.") == "Dunstable"

    def test_preserves_regular_name(self):
        assert strip_cc_oc("East Finchley") == "East Finchley"


class TestStripMr:
    def test_strips_mr(self):
        assert strip_mr("Mr Smith") == "Smith"

    def test_strips_mr_dot(self):
        assert strip_mr("Mr. Smith") == "Smith"

    def test_preserves_non_mr(self):
        assert strip_mr("Smith") == "Smith"

    def test_case_insensitive(self):
        assert strip_mr("MR Smith") == "Smith"


# ── Canonical key ──────────────────────────────────────────────────────────


class TestCanonicalKey:
    def test_lowercase(self):
        assert canonical_key("Dunstable") == "dunstable"

    def test_strips_apostrophes(self):
        key = canonical_key("Waterlow's")
        assert "'" not in key
        assert key == "waterlows"

    def test_groups_variants(self):
        k1 = canonical_key("Waterlow's")
        k2 = canonical_key("Waterlows")
        k3 = canonical_key("Waterlows'")
        k4 = canonical_key("Waterlow's OC")
        assert k1 == k2 == k3 == k4

    def test_strips_mr_prefix(self):
        k1 = canonical_key("F Gentle's XI")
        k2 = canonical_key("Mr F Gentle's XI")
        assert k1 == k2

    def test_parenthetical_content_retained(self):
        k1 = canonical_key("St Mary's")
        k2 = canonical_key("St Mary's (Launceston)")
        assert k1 != k2  # locality qualifier differentiates clubs
        assert "launceston" in k2

    def test_normalizes_ordinals(self):
        k1 = canonical_key("Dunstable 2nd XI")
        k2 = canonical_key("Dunstable Second XI")
        assert k1 == k2

    def test_normalizes_eleven(self):
        k1 = canonical_key("Dunstable Eleven")
        k2 = canonical_key("Dunstable XI")
        assert k1 == k2

    def test_removes_non_alphanumeric(self):
        key = canonical_key("St. Paul's C.C.")
        assert "." not in key
        assert "'" not in key


# ── Type guessing ──────────────────────────────────────────────────────────


class TestGuessType:
    def test_school(self):
        assert guess_type("Dunstable Grammar School") == "school"

    def test_personal_xi(self):
        assert guess_type("F Gentle's XI") == "personal_xi"

    def test_works(self):
        assert guess_type("Aylesbury Printing Works") == "works"

    def test_military(self):
        assert guess_type("Dunstable Volunteers") == "military"

    def test_church(self):
        assert guess_type("St Paul's") == "church"

    def test_church_not_for_town_teams(self):
        # "St" + "First"/"Town" should not be classified as church
        assert guess_type("Dunstable First XI") == "club"

    def test_default_club(self):
        assert guess_type("East Finchley") == "club"


# ── Team extraction from CSV ──────────────────────────────────────────────


class TestExtractTeams:
    def test_extracts_teams(self, tmp_path):
        csv_path = tmp_path / "match_index_test.csv"
        with csv_path.open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["matchup", "page", "date", "content_type", "collection", "record_id"])
            writer.writerow(["Team A v Team B", "1", "18950527", "match information", "coll", ""])
            writer.writerow(["LCR Thring", "5", "18950814", "biography", "coll", ""])
        result = extract_teams_from_csv(csv_path)
        assert "test" in result
        teams = result["test"]
        assert "Team A" in teams
        assert "Team B" in teams
        assert "LCR Thring" not in teams  # biography, not match

    def test_ignores_non_match_types(self, tmp_path):
        csv_path = tmp_path / "match_index_test.csv"
        with csv_path.open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["matchup", "page", "date", "content_type", "collection", "record_id"])
            writer.writerow(["Reading School", "1", "18950527", "statistics", "coll", ""])
        result = extract_teams_from_csv(csv_path)
        assert len(result["test"]) == 0
