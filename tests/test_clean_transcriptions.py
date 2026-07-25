"""Tests for clean_transcriptions.py — OCR-layer text cleanup with regression guards."""

from pathlib import Path

from tonywebb import cli
from tonywebb.clean_transcriptions import (
    clean_text,
    collapse_dot_leaders,
    fix_known_typos,
    join_hyphen_breaks,
)


class TestJoinHyphenBreaks:
    def test_joins_soft_wrap(self):
        text = "matches, but to this can be traced the falling off in the 1st XI. per-\nformances. If all"
        cleaned, count = join_hyphen_breaks(text)
        assert "performances" in cleaned
        assert "per-\nformances" not in cleaned
        assert count == 1

    def test_joins_saturday(self):
        cleaned, count = join_hyphen_breaks("Played on Satur-\nday last")
        assert cleaned == "Played on Saturday last"
        assert count == 1

    def test_preserves_hyphenated_surname(self):
        # Regression test: the ad-hoc predecessor of this command joined
        # this unconditionally, turning a real compound surname into one word.
        cleaned, count = join_hyphen_breaks("W. Tasker-\nEvans, b Smith ... 12")
        assert "Tasker-\nEvans" in cleaned
        assert count == 0

    def test_preserves_all_caps_compound(self):
        cleaned, count = join_hyphen_breaks("GRANT-\nCHESTER v Cambridge")
        assert "GRANT-\nCHESTER" in cleaned
        assert count == 0

    def test_mc_prefix_exception_joins(self):
        # "Mc-Guire" is one name split by the line wrap, not two joined by a
        # real hyphen -- unlike "Tasker-Evans", which is genuinely two names.
        cleaned, count = join_hyphen_breaks("McGuire replaced by Mc-\nGuire in the second innings")
        assert "McGuire in the second" in cleaned or cleaned.count("McGuire") == 2
        assert count == 1

    def test_mac_prefix_exception_joins(self):
        cleaned, count = join_hyphen_breaks("J. Mac-\nDonald, not out ... 5")
        assert "MacDonald" in cleaned
        assert count == 1

    def test_preserves_numeric_left_side(self):
        cleaned, count = join_hyphen_breaks("3-\nHawkins took the catch")
        assert "3-\nHawkins" in cleaned
        assert count == 0

    def test_preserves_numeric_right_side(self):
        cleaned, count = join_hyphen_breaks("12-\n34 was the over count")
        assert "12-\n34" in cleaned
        assert count == 0

    def test_no_hyphen_breaks_is_noop(self):
        cleaned, count = join_hyphen_breaks("No breaks here at all.")
        assert cleaned == "No breaks here at all."
        assert count == 0


class TestCollapseDotLeaders:
    def test_collapses_long_dot_run(self):
        cleaned, count = collapse_dot_leaders("Curtis........... 9 196 1 62 24.50")
        assert cleaned == "Curtis .. 9 196 1 62 24.50"
        assert count == 1

    def test_counts_multiple_runs(self):
        text = "Curtis........... 9 196 W. S. Payne............ 6 98"
        cleaned, count = collapse_dot_leaders(text)
        assert count == 2
        assert "Curtis .. 9 196" in cleaned
        assert "Payne .. 6 98" in cleaned

    def test_short_dot_run_untouched(self):
        # Fewer than 4 dots is not a table leader -- e.g. an abbreviation like "capt.."
        cleaned, count = collapse_dot_leaders("W. T. Morland (capt.).. 22 217")
        assert cleaned == "W. T. Morland (capt.).. 22 217"
        assert count == 0

    def test_no_dots_is_noop(self):
        cleaned, count = collapse_dot_leaders("Plain text with no leaders")
        assert count == 0
        assert cleaned == "Plain text with no leaders"


class TestFixKnownTypos:
    def test_ex_ras_fixed(self):
        cleaned, count = fix_known_typos("Ex ras ... 6\nTotal ... 45")
        assert "Extras ... 6" in cleaned
        assert count == 1

    def test_exras_fixed(self):
        cleaned, count = fix_known_typos("Exras ... 4")
        assert "Extras ... 4" in cleaned
        assert count == 1

    def test_r_h_haviland_fixed(self):
        cleaned, count = fix_known_typos("R H Haviland's XI")
        assert "R. H. Haviland's XI" in cleaned
        assert count == 1

    def test_no_typos_is_noop(self):
        cleaned, count = fix_known_typos("Extras ... 6")
        assert count == 0
        assert cleaned == "Extras ... 6"


class TestCleanText:
    def test_applies_all_transforms(self):
        text = "Curtis........... 9 196\nEx ras ... 6\nplayed on Satur-\nday last"
        cleaned, counts = clean_text(text)
        assert counts == {"hyphen_joins": 1, "dot_leaders": 1, "typo_fixes": 1}
        assert "Saturday" in cleaned
        assert "Extras" in cleaned
        assert "Curtis .. 9 196" in cleaned

    def test_skip_dot_leaders(self):
        text = "Curtis........... 9 196"
        cleaned, counts = clean_text(text, dot_leaders=False)
        assert counts["dot_leaders"] == 0
        assert cleaned == text

    def test_skip_hyphens(self):
        text = "played on Satur-\nday last"
        cleaned, counts = clean_text(text, hyphens=False)
        assert counts["hyphen_joins"] == 0
        assert cleaned == text

    def test_skip_typos(self):
        text = "Ex ras ... 6"
        cleaned, counts = clean_text(text, typos=False)
        assert counts["typo_fixes"] == 0
        assert cleaned == text

    def test_hyphenated_surname_survives_full_pipeline(self):
        text = "W. Tasker-\nEvans, b Smith ... 12\nEx ras ... 6"
        cleaned, counts = clean_text(text)
        assert "Tasker-\nEvans" in cleaned
        assert counts["hyphen_joins"] == 0
        assert counts["typo_fixes"] == 1


class TestRunCLI:
    def test_dry_run_leaves_files_untouched(self, tmp_path, monkeypatch, capsys):
        input_dir = tmp_path / "pages"
        input_dir.mkdir()
        f = input_dir / "tw_newspaper_cuttings_1895_1.txt"
        original = "Curtis........... 9 196\nEx ras ... 6"
        f.write_text(original)

        monkeypatch.chdir(tmp_path)
        cli.main(["clean-transcriptions", "--input", str(input_dir), "--dry-run"])

        assert f.read_text() == original
        out = capsys.readouterr().out
        assert "--dry-run: no files written" in out
        assert "Would change 1/1 file(s)" in out

    def test_in_place_write(self, tmp_path, monkeypatch):
        input_dir = tmp_path / "pages"
        input_dir.mkdir()
        f = input_dir / "tw_newspaper_cuttings_1895_1.txt"
        f.write_text("Curtis........... 9 196")

        monkeypatch.chdir(tmp_path)
        cli.main(["clean-transcriptions", "--input", str(input_dir)])

        assert f.read_text() == "Curtis .. 9 196"

    def test_unchanged_file_not_rewritten(self, tmp_path, monkeypatch, capsys):
        input_dir = tmp_path / "pages"
        input_dir.mkdir()
        f = input_dir / "tw_newspaper_cuttings_1895_1.txt"
        f.write_text("Nothing to clean here.")

        monkeypatch.chdir(tmp_path)
        cli.main(["clean-transcriptions", "--input", str(input_dir)])

        out = capsys.readouterr().out
        assert "Changed 0/1 file(s)" in out

    def test_missing_directory_exits(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        import pytest
        with pytest.raises(SystemExit):
            cli.main(["clean-transcriptions", "--input", str(tmp_path / "nope")])

    def test_empty_directory_exits(self, tmp_path, monkeypatch):
        input_dir = tmp_path / "pages"
        input_dir.mkdir()
        monkeypatch.chdir(tmp_path)
        import pytest
        with pytest.raises(SystemExit):
            cli.main(["clean-transcriptions", "--input", str(input_dir)])

    def test_skip_flags_wired_through(self, tmp_path, monkeypatch):
        input_dir = tmp_path / "pages"
        input_dir.mkdir()
        f = input_dir / "tw_newspaper_cuttings_1895_1.txt"
        f.write_text("Curtis........... 9 196")

        monkeypatch.chdir(tmp_path)
        cli.main(["clean-transcriptions", "--input", str(input_dir), "--skip-dot-leaders"])

        assert f.read_text() == "Curtis........... 9 196"
