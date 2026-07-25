"""Tests for the unified CLI: subcommand registration and backward-compatible defaults."""

import pytest

from tonywebb.cli import build_parser

EXPECTED_SUBCOMMANDS = {
    "transcribe",
    "clean-transcriptions",
    "extract-matches",
    "extract-stats",
    "index-stats",
    "index-scorecards",
    "evaluate",
    "consensus",
    "promote-reviewed",
    "compare",
    "browse",
    "clubs",
}


class TestSubcommandsRegistered:
    def test_all_expected_subcommands_present(self):
        parser = build_parser()
        actions = [a for a in parser._subparsers._group_actions if a.dest == "command"]
        assert actions
        assert set(actions[0].choices) == EXPECTED_SUBCOMMANDS

    @pytest.mark.parametrize("command", sorted(EXPECTED_SUBCOMMANDS))
    def test_help_parses_without_error(self, command, capsys):
        parser = build_parser()
        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args([command, "--help"])
        assert exc_info.value.code == 0


class TestBackwardCompatibleDefaults:
    """Default output filenames must match the pre-refactor scripts so
    existing match_index_*.csv / player_stats_*.json files stay comparable."""

    def test_extract_matches_default_model(self):
        parser = build_parser()
        args = parser.parse_args(["extract-matches"])
        assert args.model == "qwen3.5:397b-cloud"
        assert args.input == "full_text_output_gemini31pro.txt"

    def test_extract_stats_default_model(self):
        parser = build_parser()
        args = parser.parse_args(["extract-stats"])
        assert args.model == "qwen3.5:397b-cloud"

    def test_index_stats_default_model(self):
        parser = build_parser()
        args = parser.parse_args(["index-stats"])
        assert args.model == "qwen3.5:397b-cloud"

    def test_index_scorecards_default_model(self):
        parser = build_parser()
        args = parser.parse_args(["index-scorecards"])
        assert args.model == "qwen3.5:397b-cloud"

    def test_transcribe_default_model_and_range(self):
        parser = build_parser()
        args = parser.parse_args(["transcribe"])
        assert args.model == "gpt-5.4"
        assert args.start_page == 1
        assert args.end_page == 61

    def test_evaluate_default_truth_file(self):
        parser = build_parser()
        args = parser.parse_args(["evaluate", "match_index_foo.csv"])
        assert args.truth == "match_index_willis.csv"
        assert args.pages is None
        assert args.content_types is None

    def test_compare_default_pattern_and_output(self):
        parser = build_parser()
        args = parser.parse_args(["compare"])
        assert args.pattern == "match_index_*.csv"
        assert args.output == "compare_results.md"

    def test_browse_default_output(self):
        parser = build_parser()
        args = parser.parse_args(["browse"])
        assert args.output == "compare_browser.html"

    def test_clubs_default_output(self):
        parser = build_parser()
        args = parser.parse_args(["clubs"])
        assert args.output == "clubs.csv"

    def test_consensus_default_pattern_truth_and_output(self):
        parser = build_parser()
        args = parser.parse_args(["consensus"])
        assert args.pattern == "match_index_*.csv"
        assert args.truth == "match_index_willis.csv"
        assert args.output == "consensus_index.csv"
        assert args.report == "consensus_report.md"
        assert args.min_agreement == 1

    def test_promote_reviewed_default_truth(self):
        parser = build_parser()
        args = parser.parse_args(["promote-reviewed", "match_index_reviewed.csv"])
        assert args.truth == "match_index_willis.csv"
        assert args.dry_run is False

    def test_clean_transcriptions_defaults(self):
        parser = build_parser()
        args = parser.parse_args(["clean-transcriptions", "--input", "qwen3.5:397b"])
        assert args.dry_run is False
        assert args.skip_dot_leaders is False
        assert args.skip_hyphens is False
        assert args.skip_typos is False
