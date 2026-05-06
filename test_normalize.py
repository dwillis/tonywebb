"""Tests for normalize.py — matchup/title/date normalization and ClubRegistry."""

import csv
import tempfile
from datetime import date
from pathlib import Path

import pytest

from normalize import (
    ClubRegistry,
    _normalize_team,
    detect_publication_date,
    matchup_key,
    normalize_date,
    normalize_matchup,
    normalize_title,
    relative_dates,
    title_key,
)


# ── Matchup normalization ──────────────────────────────────────────────────


class TestNormalizeMatchup:
    def test_basic_v_separator(self):
        assert normalize_matchup("Team A v Team B") == "Team A v Team B"

    def test_vs_separator(self):
        assert normalize_matchup("Team A vs Team B") == "Team A v Team B"

    def test_vs_dot_separator(self):
        assert normalize_matchup("Team A vs. Team B") == "Team A v Team B"

    def test_versus_separator(self):
        assert normalize_matchup("Team A versus Team B") == "Team A v Team B"

    def test_strips_trailing_cc(self):
        assert normalize_matchup("Waterlow's CC v East Finchley") == "Waterlow's v East Finchley"

    def test_strips_trailing_cricket_club(self):
        result = normalize_matchup("Dunstable Cricket Club v Luton")
        assert result == "Dunstable v Luton"

    def test_ordinals_to_words(self):
        assert normalize_matchup("Dunstable 2nd v Luton 1st") == "Dunstable Second v Luton First"

    def test_eleven_to_xi(self):
        result = normalize_matchup("Dunstable Second Eleven v Luton")
        assert result == "Dunstable Second XI v Luton"

    def test_gs_to_grammar_school(self):
        result = normalize_matchup("Dunstable G.S. v Bedford")
        assert result == "Dunstable Grammar School v Bedford"

    def test_title_case(self):
        result = normalize_matchup("DUNSTABLE v LUTON")
        assert result == "Dunstable v Luton"

    def test_preserves_roman_numerals(self):
        result = normalize_matchup("Dunstable XI v Luton XI")
        assert "XI" in result

    def test_preserves_initials(self):
        result = normalize_matchup("MJK Smith's XI v Luton")
        assert "MJK" in result

    def test_empty_string(self):
        assert normalize_matchup("") == ""

    def test_no_v_separator(self):
        result = normalize_matchup("Dunstable Cricket Club")
        assert result == "Dunstable"

    def test_collapses_whitespace(self):
        result = normalize_matchup("Team  A   v   Team  B")
        assert "  " not in result


class TestMatchupKey:
    def test_lowercase(self):
        key = matchup_key("Dunstable v Luton")
        assert key == key.lower()

    def test_strips_periods(self):
        key = matchup_key("Mr. F. Gentle's XI v Luton")
        assert "." not in key

    def test_strips_apostrophes(self):
        key = matchup_key("Waterlow's v King's")
        assert "'" not in key

    def test_same_key_for_variants(self):
        k1 = matchup_key("Waterlow's v East Finchley")
        k2 = matchup_key("Waterlows v East Finchley")
        assert k1 == k2


# ── Title normalization ────────────────────────────────────────────────────


class TestNormalizeTitle:
    def test_strips_trailing_cc(self):
        assert normalize_title("Reading CC") == "Reading"

    def test_strips_cricket_club(self):
        assert normalize_title("Reading Cricket Club") == "Reading"

    def test_preserves_content(self):
        assert normalize_title("LCR Thring") == "LCR Thring"

    def test_empty_string(self):
        assert normalize_title("") == ""


class TestTitleKey:
    def test_lowercase(self):
        assert title_key("Reading School") == "reading school"

    def test_strips_periods(self):
        assert "." not in title_key("Mr. Smith")


# ── Date normalization ─────────────────────────────────────────────────────


class TestNormalizeDate:
    def test_valid_date(self):
        assert normalize_date("18950527") == "18950527"

    def test_partial_year_only(self):
        assert normalize_date("18950000") == "18950000"

    def test_partial_month_only(self):
        assert normalize_date("18950800") == "18950800"

    def test_empty_string(self):
        assert normalize_date("") == ""

    def test_none(self):
        assert normalize_date(None) == ""

    def test_with_hyphens(self):
        assert normalize_date("1895-05-27") == "18950527"

    def test_invalid_month(self):
        assert normalize_date("18951327") == ""

    def test_invalid_day(self):
        assert normalize_date("18950532") == ""

    def test_year_out_of_range(self):
        assert normalize_date("17000527") == ""


# ── Publication date detection ─────────────────────────────────────────────


class TestDetectPublicationDate:
    def test_saturday_format(self):
        text = "SATURDAY 8 JUNE 1895\nSome cricket content here"
        result = detect_publication_date(text)
        assert result == date(1895, 6, 8)

    def test_comma_format(self):
        text = "Saturday, June 8th, 1895\nContent"
        result = detect_publication_date(text)
        assert result == date(1895, 6, 8)

    def test_no_date(self):
        text = "Just some text without a date"
        assert detect_publication_date(text) is None

    def test_only_checks_first_400_chars(self):
        text = "x" * 500 + "SATURDAY 8 JUNE 1895"
        assert detect_publication_date(text) is None


class TestRelativeDates:
    def test_friday_from_saturday(self):
        pub = date(1895, 6, 8)  # Saturday
        rel = relative_dates(pub)
        assert rel["friday"] == "1895-06-07"

    def test_saturday_from_saturday(self):
        pub = date(1895, 6, 8)  # Saturday
        rel = relative_dates(pub)
        assert rel["saturday"] == "1895-06-01"  # previous Saturday

    def test_all_weekdays_present(self):
        rel = relative_dates(date(1895, 6, 8))
        assert len(rel) == 7


# ── ClubRegistry ───────────────────────────────────────────────────────────


@pytest.fixture
def registry_csv(tmp_path):
    csv_path = tmp_path / "clubs.csv"
    with csv_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["canonical_name", "aliases", "location", "type"])
        writer.writerow(["Waterlow's", "Waterlow's OC|Waterlows|Waterlows'", "Dunstable", "works"])
        writer.writerow(["F Gentle's XI", "Mr F Gentle's XI", "", "personal_xi"])
        writer.writerow(["Dunstable Grammar School", "Dunstable G.S.", "", "school"])
        writer.writerow(["East Finchley", "", "", "club"])
    return csv_path


class TestClubRegistry:
    def test_load(self, registry_csv):
        reg = ClubRegistry(registry_csv)
        assert len(reg) == 4

    def test_resolve_canonical(self, registry_csv):
        reg = ClubRegistry(registry_csv)
        assert reg.resolve("Waterlow's") == "Waterlow's"

    def test_resolve_alias(self, registry_csv):
        reg = ClubRegistry(registry_csv)
        assert reg.resolve("Waterlows") == "Waterlow's"

    def test_resolve_oc_suffix(self, registry_csv):
        reg = ClubRegistry(registry_csv)
        assert reg.resolve("Waterlow's OC") == "Waterlow's"

    def test_resolve_mr_prefix(self, registry_csv):
        reg = ClubRegistry(registry_csv)
        assert reg.resolve("Mr F Gentle's XI") == "F Gentle's XI"

    def test_resolve_mr_prefix_fallback(self, registry_csv):
        """Strip Mr prefix and resolve to canonical form."""
        reg = ClubRegistry(registry_csv)
        assert reg.resolve("Mr East Finchley") == "East Finchley"

    def test_resolve_unknown(self, registry_csv):
        reg = ClubRegistry(registry_csv)
        assert reg.resolve("Unknown Team") is None

    def test_is_known(self, registry_csv):
        reg = ClubRegistry(registry_csv)
        assert reg.is_known("Waterlow's")
        assert reg.is_known("Waterlows")
        assert not reg.is_known("Nonexistent Club")

    def test_missing_csv(self, tmp_path):
        reg = ClubRegistry(tmp_path / "nonexistent.csv")
        assert len(reg) == 0
        assert reg.resolve("anything") is None

    def test_empty_csv(self, tmp_path):
        csv_path = tmp_path / "empty.csv"
        with csv_path.open("w") as f:
            f.write("canonical_name,aliases,location,type\n")
        reg = ClubRegistry(csv_path)
        assert len(reg) == 0


class TestNormalizeTeamWithRegistry:
    def test_resolves_via_registry(self, registry_csv):
        reg = ClubRegistry(registry_csv)
        result = _normalize_team("Waterlows", registry=reg)
        assert result == "Waterlow's"

    def test_resolves_after_normalization(self, registry_csv):
        reg = ClubRegistry(registry_csv)
        result = _normalize_team("Dunstable G.S.", registry=reg)
        assert result == "Dunstable Grammar School"

    def test_passthrough_without_registry(self):
        result = _normalize_team("Waterlows")
        assert result == "Waterlows"  # no registry, no resolution

    def test_normalize_matchup_with_registry(self, registry_csv):
        reg = ClubRegistry(registry_csv)
        result = normalize_matchup("Waterlows v Mr F Gentle's XI", registry=reg)
        assert result == "Waterlow's v F Gentle's XI"
