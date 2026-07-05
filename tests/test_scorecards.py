from pathlib import Path

import pytest

from tonywebb.llm_common import JSONExtractError
from tonywebb.scorecards import prompts, schema, validate

FIXTURES = Path(__file__).parent / "fixtures"
PAGE_145 = (FIXTURES / "page_145.txt").read_text(encoding="utf-8")


# ── schema.parse_response ────────────────────────────────────────────────────

class TestParseResponse:
    def test_plain_json(self):
        entries = schema.parse_response('{"scorecards": [{"matchup": "A v B"}]}')
        assert entries == [{"matchup": "A v B"}]

    def test_markdown_fences(self):
        entries = schema.parse_response('```json\n{"scorecards": []}\n```')
        assert entries == []

    def test_matches_alias(self):
        entries = schema.parse_response('{"matches": [{"matchup": "A v B"}]}')
        assert entries == [{"matchup": "A v B"}]

    def test_missing_key_raises(self):
        with pytest.raises(JSONExtractError):
            schema.parse_response('{"foo": []}')

    def test_not_a_list_raises(self):
        with pytest.raises(JSONExtractError):
            schema.parse_response('{"scorecards": "nope"}')


# ── schema.canonical_dismissal ───────────────────────────────────────────────

class TestCanonicalDismissal:
    @pytest.mark.parametrize("raw,expected", [
        ("b", "b"), ("bowled", "b"),
        ("c", "c"), ("caught", "c"), ("ct", "c"),
        ("c and b", "c and b"), ("caught and bowled", "c and b"),
        ("st", "st"), ("stumped", "st"),
        ("run out", "run out"), ("ran out", "run out"),
        ("lbw", "lbw"), ("leg before wicket", "lbw"),
        ("hit wicket", "hit wicket"),
        ("retired", "retired"), ("retired hurt", "retired"),
        ("absent", "absent"),
        ("not out", "not out"),
        ("did not bat", "did not bat"),
        ("something weird", "unknown"),
        (None, "unknown"),
        ("", "unknown"),
        ("B", "b"),  # case-insensitive
    ])
    def test_aliases(self, raw, expected):
        assert schema.canonical_dismissal(raw) == expected


# ── schema.normalize_person_name ─────────────────────────────────────────────

class TestNormalizePersonName:
    def test_honorific_period_stripped(self):
        assert schema.normalize_person_name("Dr. Stuart") == "Dr Stuart"

    def test_esq_suffix_dropped(self):
        assert schema.normalize_person_name("W. Moore, Esq.") == "W Moore"

    def test_initials(self):
        assert schema.normalize_person_name("A. Cuthinson") == "A Cuthinson"

    def test_none_returns_none(self):
        assert schema.normalize_person_name(None) is None

    def test_empty_returns_none(self):
        assert schema.normalize_person_name("   ") is None

    def test_garbled_ocr_name(self):
        # "... Lane" from page 145 -- leading garbage collapses away.
        assert schema.normalize_person_name("... Lane") == "Lane"


# ── schema.normalize_batting_line — every dismissal form on page 145 ────────

class TestNormalizeBattingLine:
    def test_bowled(self):
        # "Dr. Stuart, b Tilley ... 0"
        line = schema.normalize_batting_line(
            {"batter": "Dr. Stuart", "dismissal": "b", "bowler": "Tilley",
             "runs": 0, "raw": "Dr. Stuart, b Tilley ... 0"}
        )
        assert line == {
            "batter": "Dr Stuart", "dismissal": "b", "bowler": "Tilley",
            "fielder": None, "runs": 0, "not_out": False,
            "raw": "Dr. Stuart, b Tilley ... 0",
        }

    def test_caught_by_fielder_bowled_by(self):
        # "L. Clark, c Longcroft b Tilley ... 2"
        line = schema.normalize_batting_line(
            {"batter": "L. Clark", "dismissal": "c", "bowler": "Tilley",
             "fielder": "Longcroft", "runs": 2}
        )
        assert line["dismissal"] == "c"
        assert line["bowler"] == "Tilley"
        assert line["fielder"] == "Longcroft"

    def test_caught_and_bowled(self):
        # "H. James, c and b Roberts ... 5"
        line = schema.normalize_batting_line(
            {"batter": "H. James", "dismissal": "c and b", "bowler": "Roberts", "runs": 5}
        )
        assert line["dismissal"] == "c and b"
        assert line["bowler"] == "Roberts"

    def test_stumped(self):
        # "Astill, st Vernon, b Herbert ... 4"
        line = schema.normalize_batting_line(
            {"batter": "Astill", "dismissal": "st", "fielder": "Vernon",
             "bowler": "Herbert", "runs": 4}
        )
        assert line["dismissal"] == "st"
        assert line["fielder"] == "Vernon"
        assert line["bowler"] == "Herbert"

    def test_run_out(self):
        # "W. Moore, Esq., run out ... 1"
        line = schema.normalize_batting_line(
            {"batter": "W. Moore, Esq.", "dismissal": "run out", "runs": 1}
        )
        assert line["batter"] == "W Moore"
        assert line["dismissal"] == "run out"
        assert line["bowler"] is None

    def test_lbw(self):
        # "A. Holmes, lbw b Blaxley ... 5"
        line = schema.normalize_batting_line(
            {"batter": "A. Holmes", "dismissal": "lbw", "bowler": "Blaxley", "runs": 5}
        )
        assert line["dismissal"] == "lbw"
        assert line["bowler"] == "Blaxley"

    def test_not_out(self):
        # "D. Naylor, not out ... 0"
        line = schema.normalize_batting_line(
            {"batter": "D. Naylor", "dismissal": "not out", "runs": 0}
        )
        assert line["dismissal"] == "not out"
        assert line["not_out"] is True

    def test_not_out_flag_forces_dismissal(self):
        line = schema.normalize_batting_line(
            {"batter": "J. Younger", "dismissal": "unknown", "not_out": True, "runs": 0}
        )
        assert line["dismissal"] == "not out"
        assert line["not_out"] is True

    def test_garbled_runs_becomes_null_not_guessed(self):
        line = schema.normalize_batting_line(
            {"batter": "Someone", "dismissal": "b", "bowler": "X", "runs": "??"}
        )
        assert line["runs"] is None

    def test_no_batter_discarded(self):
        assert schema.normalize_batting_line({"dismissal": "b", "runs": 5}) is None

    def test_not_a_dict_discarded(self):
        assert schema.normalize_batting_line("not a dict") is None


# ── schema.normalize_bowling_line ────────────────────────────────────────────

class TestNormalizeBowlingLine:
    def test_table_figures(self):
        line = schema.normalize_bowling_line(
            {"bowler": "W. S. Payne", "overs": "65.4", "maidens": 21,
             "runs": 145, "wickets": 27, "source": "table"}
        )
        assert line["bowler"] == "W S Payne"
        assert line["overs"] == "65.4"
        assert line["maidens"] == 21
        assert line["source"] == "table"

    def test_prose_figures_with_word_numbers(self):
        # "Tilley for Roberts and Roberts took five wickets for 12 runs."
        line = schema.normalize_bowling_line(
            {"bowler": "Tilley", "overs": None, "maidens": None,
             "runs": 12, "wickets": "five", "source": "prose",
             "raw": "Tilley for Roberts and Roberts took five wickets for 12 runs."}
        )
        assert line["wickets"] == 5
        assert line["overs"] is None
        assert line["source"] == "prose"

    def test_prose_default_source_is_table(self):
        line = schema.normalize_bowling_line({"bowler": "X", "wickets": 3})
        assert line["source"] == "table"

    def test_no_bowler_discarded(self):
        assert schema.normalize_bowling_line({"wickets": 3}) is None


# ── schema.normalize_innings / normalize_scorecard ───────────────────────────

class TestNormalizeInnings:
    def test_did_not_bat_prose_list(self):
        # "F. Underwood, R. Howett, J. Thompson, and E. A. Woodford did not bat."
        innings = schema.normalize_innings({
            "team": "Kibworth",
            "batting": [
                {"batter": "F. A. Simpkin", "dismissal": "b", "bowler": "Newcombe", "runs": 28},
            ],
            "did_not_bat": ["F. Underwood", "R. Howett", "J. Thompson", "E. A. Woodford"],
            "extras": 6, "total": 159,
        })
        assert innings["did_not_bat"] == ["F Underwood", "R Howett", "J Thompson", "E A Woodford"]

    def test_all_out_inferred_true(self):
        batting = [
            {"batter": f"P{i}", "dismissal": "b", "bowler": "X", "runs": 1}
            for i in range(10)
        ]
        innings = schema.normalize_innings({"team": "T", "batting": batting, "total": 10})
        assert innings["all_out"] is True

    def test_all_out_inferred_false_when_not_outs_remain(self):
        batting = [
            {"batter": "A", "dismissal": "b", "bowler": "X", "runs": 5},
            {"batter": "B", "dismissal": "not out", "runs": 20},
            {"batter": "C", "dismissal": "not out", "runs": 30},
        ]
        innings = schema.normalize_innings({"team": "T", "batting": batting, "total": 55})
        assert innings["all_out"] is False

    def test_no_team_discarded(self):
        assert schema.normalize_innings({"batting": [{"batter": "A", "runs": 1}]}) is None

    def test_empty_innings_discarded(self):
        assert schema.normalize_innings({"team": "T", "batting": [], "did_not_bat": []}) is None


class TestNormalizeScorecard:
    def test_roberts_v_asylum(self):
        entry = {
            "matchup": "Roberts and Roberts v County Asylum",
            "date": "18950616",
            "venue": "On the Asylum Grounds",
            "innings": [
                {
                    "team": "County Asylum", "order": 1,
                    "batting": [
                        {"batter": "Dr. Stuart", "dismissal": "b", "bowler": "Tilley", "runs": 0},
                        {"batter": "D. Naylor", "dismissal": "not out", "runs": 0},
                    ],
                    "extras": 6, "total": 45,
                    "bowling": [],
                },
                {
                    "team": "Roberts and Roberts", "order": 2,
                    "batting": [
                        {"batter": "R. J. Tilley", "dismissal": "b", "bowler": "Roberts", "runs": 9},
                    ],
                    "extras": 4, "total": 43,
                    "bowling": [
                        {"bowler": "Tilley", "wickets": "five", "runs": 12, "source": "prose",
                         "raw": "Tilley for Roberts and Roberts took five wickets for 12 runs."},
                    ],
                },
            ],
        }
        card = schema.normalize_scorecard(entry, page_num=145)
        assert card["match_key"]["page"] == 145
        assert card["match_key"]["date"] == "18950616"
        assert "Roberts" in card["match_key"]["matchup"]
        assert "Asylum" in card["match_key"]["matchup"]
        assert card["venue"] == "On the Asylum Grounds"
        assert len(card["innings"]) == 2
        assert card["innings"][1]["bowling"][0]["wickets"] == 5

    def test_no_matchup_discarded(self):
        assert schema.normalize_scorecard({"innings": []}, page_num=1) is None

    def test_not_a_dict_discarded(self):
        assert schema.normalize_scorecard("nope", page_num=1) is None


# ── validate ──────────────────────────────────────────────────────────────────

def _card(innings, matchup="Team A v Team B", page=1, date="18950616"):
    return {
        "match_key": {"page": page, "matchup": matchup, "date": date},
        "venue": None, "result": None,
        "innings": innings,
    }


def _batting_line(batter, dismissal, runs, bowler=None, fielder=None, not_out=False):
    return {
        "batter": batter, "dismissal": dismissal, "bowler": bowler, "fielder": fielder,
        "runs": runs, "not_out": not_out, "raw": f"{batter} {dismissal} ... {runs}",
    }


class TestCheckTotals:
    def test_ok(self):
        innings = {
            "batting": [_batting_line("A", "b", 10, bowler="X"), _batting_line("B", "not out", 5, not_out=True)],
            "extras": 3, "total": 18,
        }
        result = validate.check_totals(innings)
        assert result == {"status": "ok", "stated": 18, "computed": 18, "delta": 0}

    def test_mismatch(self):
        innings = {
            "batting": [_batting_line("A", "b", 10, bowler="X")],
            "extras": 3, "total": 100,
        }
        result = validate.check_totals(innings)
        assert result["status"] == "mismatch"
        assert result["delta"] == 13 - 100

    def test_incomplete_when_runs_missing(self):
        innings = {
            "batting": [_batting_line("A", "b", None, bowler="X")],
            "extras": 3, "total": 18,
        }
        result = validate.check_totals(innings)
        assert result["status"] == "incomplete"
        assert result["computed"] is None

    def test_tolerance(self):
        innings = {
            "batting": [_batting_line("A", "b", 10, bowler="X")],
            "extras": 3, "total": 14,  # off by 1
        }
        assert validate.check_totals(innings, tolerance=0)["status"] == "mismatch"
        assert validate.check_totals(innings, tolerance=1)["status"] == "ok"


class TestCheckBowlerWickets:
    def test_matches(self):
        innings = {
            "batting": [
                _batting_line("A", "b", 1, bowler="Tilley"),
                _batting_line("B", "c", 2, bowler="Tilley", fielder="Longcroft"),
            ],
            "bowling": [{"bowler": "Tilley", "wickets": 2}],
        }
        results = validate.check_bowler_wickets(innings)
        assert results == [{"bowler": "Tilley", "credited": 2, "stated": 2, "ok": True}]

    def test_prose_mismatch(self):
        # Real page-145 case: prose says Tilley took 5, but only 1 dismissal in this innings credits him.
        innings = {
            "batting": [_batting_line("A", "b", 1, bowler="Tilley")],
            "bowling": [{"bowler": "Tilley", "wickets": 5}],
        }
        results = validate.check_bowler_wickets(innings)
        assert results[0]["ok"] is False
        assert results[0]["credited"] == 1

    def test_no_bowling_figures_no_checks(self):
        innings = {"batting": [_batting_line("A", "b", 1, bowler="Tilley")], "bowling": []}
        assert validate.check_bowler_wickets(innings) == []


class TestCheckNames:
    def test_clean_names_ok(self):
        card = _card([{"batting": [_batting_line("Dr Stuart", "b", 1, bowler="Tilley")], "bowling": []}])
        assert validate.check_names(card) is True

    def test_garbled_name_fails(self):
        card = _card([{"batting": [_batting_line("###!!!", "b", 1, bowler="Tilley")], "bowling": []}])
        assert validate.check_names(card) is False


class TestLinkToIndex:
    def test_exact_match(self):
        card = _card([], matchup="Kensworth v Dunstable Victoria")
        rows = [{"matchup": "Kensworth v Dunstable Victoria"}]
        link = validate.link_to_index(card, rows)
        assert link == {"matched": True, "index_matchup": "Kensworth v Dunstable Victoria",
                         "match_kind": "exact", "similarity": 1.0}

    def test_fuzzy_match(self):
        card = _card([], matchup="Kensworth v Dunstable Victoria")
        rows = [{"matchup": "Kensworth v Dunstable Vic"}]
        link = validate.link_to_index(card, rows, threshold=0.8)
        assert link["matched"] is True
        assert link["match_kind"] == "fuzzy"

    def test_no_match(self):
        card = _card([], matchup="Nowhere United v Somewhere Town")
        rows = [{"matchup": "Kensworth v Dunstable Victoria"}]
        link = validate.link_to_index(card, rows)
        assert link["matched"] is False

    def test_empty_index(self):
        card = _card([], matchup="Anyone v Anyone Else")
        link = validate.link_to_index(card, [])
        assert link["matched"] is False


class TestScoreConfidenceMonotonicity:
    def _checks(self, *, totals_ok=True, structure_ok=True, names_ok=True,
                bowler_ok=True, indexed=True):
        return {
            "totals": [{"status": "ok" if totals_ok else "mismatch", "stated": 1, "computed": 1, "delta": 0}],
            "bowler_wickets": [{"bowler": "X", "credited": 1, "stated": 1, "ok": bowler_ok}],
            "names_ok": names_ok,
            "structure": {"innings_count": 2, "batting_counts": [11, 11], "ok": structure_ok},
            "index_linked": indexed,
        }

    def test_all_good_is_high_confidence(self):
        confidence, flags = validate.score_confidence(self._checks())
        assert confidence == 1.0
        assert flags == []

    def test_total_mismatch_lowers_confidence(self):
        base, _ = validate.score_confidence(self._checks())
        lowered, flags = validate.score_confidence(self._checks(totals_ok=False))
        assert lowered < base
        assert "total_mismatch" in flags

    def test_bad_structure_lowers_confidence(self):
        base, _ = validate.score_confidence(self._checks())
        lowered, flags = validate.score_confidence(self._checks(structure_ok=False))
        assert lowered < base
        assert "bad_structure" in flags

    def test_not_indexed_lowers_confidence(self):
        base, _ = validate.score_confidence(self._checks())
        lowered, flags = validate.score_confidence(self._checks(indexed=False))
        assert lowered < base
        assert "not_in_index" in flags

    def test_multiple_failures_compound(self):
        one_bad, _ = validate.score_confidence(self._checks(totals_ok=False))
        two_bad, _ = validate.score_confidence(self._checks(totals_ok=False, structure_ok=False))
        assert two_bad < one_bad


class TestValidateScorecardIntegration:
    def test_low_confidence_flags_for_recheck(self):
        card = _card(
            [{
                "batting": [_batting_line("A", "b", 10, bowler="Tilley")],
                "extras": 0, "total": 999,  # deliberate mismatch
                "bowling": [{"bowler": "Tilley", "wickets": 5}],
            }],
            matchup="Nobody v Nobody Else",
        )
        result = validate.validate_scorecard(card, index_rows_for_page=[])
        assert result["validation"]["confidence"] < 0.7
        assert "total_mismatch" in result["validation"]["flags"]
        assert "not_in_index" in result["validation"]["flags"]


# ── prompts ───────────────────────────────────────────────────────────────────

class TestBuildTextPrompt:
    def test_includes_page_text(self):
        prompt = prompts.build_text_prompt(145, PAGE_145)
        assert "ROBERTS and ROBERTS" in prompt or "Roberts" in prompt
        assert "page 145" in prompt

    def test_includes_schema_keys(self):
        prompt = prompts.build_text_prompt(1, "some text")
        for key in ("scorecards", "matchup", "innings", "batting", "bowling", "raw", "not_out"):
            assert key in prompt

    def test_verbatim_raw_instruction_present(self):
        prompt = prompts.build_text_prompt(1, "text")
        assert "raw" in prompt.lower()
        assert "verbatim" in prompt.lower()

    def test_continuation_rule_present(self):
        prompt = prompts.build_text_prompt(1, "text")
        assert "continues from a previous page" in prompt or "BEGINS on this page" in prompt

    def test_never_guess_rule_present(self):
        prompt = prompts.build_text_prompt(1, "text")
        assert "never invent" in prompt.lower() or "never guess" in prompt.lower()

    def test_publication_date_detected(self):
        prompt = prompts.build_text_prompt(145, PAGE_145)
        assert "PUBLICATION DATE: 1895-06-17" in prompt


class TestBuildRecheckPrompt:
    def test_includes_flags_and_scorecard(self):
        card = _card([], matchup="A v B")
        prompt = prompts.build_recheck_prompt(145, card, ["total_mismatch"])
        assert "total_mismatch" in prompt
        assert "A v B" in prompt
        assert "IMAGE" in prompt
