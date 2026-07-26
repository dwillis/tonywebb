"""Tests for extract_matches.py — extraction, prompt building, and post-processing."""

import json
from datetime import date

import pytest

from tonywebb.extract_matches import (
    VALID_CONTENT_TYPES,
    _parse_response,
    build_user_prompt,
    normalize_and_dedup,
    track_cross_page,
)
from tonywebb.llm_common import JSONExtractError, split_pages


# ── Page splitting ─────────────────────────────────────────────────────────


class TestSplitPages:
    def test_basic_split(self):
        text = (
            "==========\nPAGE 1\n==========\n"
            "Content of page 1\n"
            "==========\nPAGE 2\n==========\n"
            "Content of page 2"
        )
        pages = split_pages(text)
        assert len(pages) == 2
        assert pages[0][0] == 1
        assert "Content of page 1" in pages[0][1]
        assert pages[1][0] == 2
        assert "Content of page 2" in pages[1][1]

    def test_no_pages(self):
        assert split_pages("Just some text") == []

    def test_single_page(self):
        text = "==========\nPAGE 42\n==========\nContent"
        pages = split_pages(text)
        assert len(pages) == 1
        assert pages[0][0] == 42


# ── Response parsing ───────────────────────────────────────────────────────


class TestParseResponse:
    def test_valid_json(self):
        raw = json.dumps({"entries": [
            {"title": "Team A v Team B", "date": "18950527", "content_type": "match information"}
        ]})
        entries = _parse_response(raw)
        assert len(entries) == 1
        assert entries[0]["matchup"] == "Team A v Team B"

    def test_title_renamed_to_matchup(self):
        raw = json.dumps({"entries": [{"title": "X v Y", "date": "18950527", "content_type": "match information"}]})
        entries = _parse_response(raw)
        assert "matchup" in entries[0]
        assert "title" not in entries[0]

    def test_empty_entries_list_is_valid(self):
        # The prompt instructs the model to return {"entries": []} when a
        # page has no cricket content — that must parse, not error.
        assert _parse_response(json.dumps({"entries": []})) == []

    def test_matches_key_accepted(self):
        raw = json.dumps({"matches": [{"title": "X v Y", "content_type": "match information"}]})
        entries = _parse_response(raw)
        assert len(entries) == 1

    def test_invalid_content_type_defaults(self):
        raw = json.dumps({"entries": [{"title": "X v Y", "content_type": "invalid_type"}]})
        entries = _parse_response(raw)
        assert entries[0]["content_type"] == "match information"

    def test_strips_markdown_fences(self):
        raw = "```json\n" + json.dumps({"entries": [{"title": "A v B", "content_type": "match information"}]}) + "\n```"
        entries = _parse_response(raw)
        assert len(entries) == 1

    def test_invalid_json_raises(self):
        with pytest.raises(JSONExtractError, match="invalid JSON"):
            _parse_response("not json at all")

    def test_missing_entries_key_raises(self):
        with pytest.raises(JSONExtractError, match="missing"):
            _parse_response(json.dumps({"data": []}))

    def test_entries_not_list_raises(self):
        with pytest.raises(JSONExtractError, match="not a list"):
            _parse_response(json.dumps({"entries": "string"}))

    def test_response_not_object_raises(self):
        with pytest.raises(JSONExtractError, match="not a JSON object"):
            _parse_response(json.dumps([1, 2, 3]))


# ── Normalize and dedup ────────────────────────────────────────────────────


class TestNormalizeAndDedup:
    def test_basic_dedup(self):
        entries = [
            {"matchup": "Team A v Team B", "date": "18950527", "content_type": "match information"},
            {"matchup": "Team A v Team B", "date": "18950527", "content_type": "match information"},
        ]
        result, _ = normalize_and_dedup(entries, page_num=1)
        assert len(result) == 1

    def test_different_dates_not_deduped(self):
        entries = [
            {"matchup": "Team A v Team B", "date": "18950527", "content_type": "match information"},
            {"matchup": "Team A v Team B", "date": "18950603", "content_type": "match information"},
        ]
        result, _ = normalize_and_dedup(entries, page_num=1)
        assert len(result) == 2

    def test_content_type_filter(self):
        entries = [
            {"matchup": "Team A v Team B", "date": "18950527", "content_type": "match information"},
            {"title": "Reading School", "date": "18950527", "content_type": "statistics"},
        ]
        result, _ = normalize_and_dedup(entries, page_num=1, allowed_types={"match information"})
        assert len(result) == 1
        assert result[0]["content_type"] == "match information"

    def test_collection_name_set(self):
        entries = [{"matchup": "A v B", "date": "18950527", "content_type": "match information"}]
        result, _ = normalize_and_dedup(entries, page_num=5)
        assert result[0]["collection"] == "Tony Webb minor counties collection"
        assert result[0]["page"] == 5

    def test_empty_matchup_skipped(self):
        entries = [{"matchup": "", "date": "18950527", "content_type": "match information"}]
        result, _ = normalize_and_dedup(entries, page_num=1)
        assert len(result) == 0

    def test_non_dict_entries_skipped(self):
        entries = ["not a dict", 42, None]
        result, _ = normalize_and_dedup(entries, page_num=1)
        assert len(result) == 0

    def test_invalid_content_type_defaults_to_match(self):
        entries = [{"matchup": "A v B", "date": "18950527", "content_type": "bogus"}]
        result, _ = normalize_and_dedup(entries, page_num=1)
        assert result[0]["content_type"] == "match information"

    def test_pages_defaults_to_1(self):
        # "pages" (how many distinct pages this entry spans) is a derived
        # field computed later by recompute_pages_column(), never supplied
        # by the model -- every freshly normalized entry starts at 1.
        entries = [{"matchup": "A v B", "date": "18950527", "content_type": "match information"}]
        result, _ = normalize_and_dedup(entries, page_num=1)
        assert result[0]["pages"] == 1


class TestNormalizeAndDedupDatePhrase:
    """date_phrase, resolved deterministically, is preferred over the model's own "date"."""

    def test_resolved_phrase_overrides_models_own_date(self):
        entries = [{
            "matchup": "A v B", "content_type": "match information",
            "date_phrase": "on Whit-Monday", "date": "18950601",  # model's own guess is wrong
        }]
        result, _ = normalize_and_dedup(entries, page_num=1)
        assert result[0]["date"] == "18950527"  # deterministic resolution wins

    def test_weekday_phrase_needs_publication_date(self):
        entries = [{
            "matchup": "A v B", "content_type": "match information",
            "date_phrase": "on Friday", "date": "18950608",
        }]
        result, _ = normalize_and_dedup(entries, page_num=1, publication_date=date(1895, 6, 8))
        assert result[0]["date"] == "18950607"

    def test_unresolvable_phrase_falls_back_to_models_date(self):
        entries = [{
            "matchup": "A v B", "content_type": "match information",
            "date_phrase": "sometime in spring", "date": "18950400",
        }]
        result, _ = normalize_and_dedup(entries, page_num=1)
        assert result[0]["date"] == "18950400"

    def test_no_phrase_falls_back_to_models_date(self):
        entries = [{"matchup": "A v B", "content_type": "match information", "date": "18950527"}]
        result, _ = normalize_and_dedup(entries, page_num=1)
        assert result[0]["date"] == "18950527"

    def test_empty_phrase_falls_back_to_models_date(self):
        entries = [{
            "matchup": "A v B", "content_type": "match information",
            "date_phrase": "", "date": "18950527",
        }]
        result, _ = normalize_and_dedup(entries, page_num=1)
        assert result[0]["date"] == "18950527"


class TestNormalizeAndDedupDiscards:
    def test_no_discards_for_clean_entries(self):
        entries = [{"matchup": "A v B", "date": "18950527", "content_type": "match information"}]
        _, discarded = normalize_and_dedup(entries, page_num=1)
        assert discarded == []

    def test_empty_title_discard_recorded(self):
        entries = [{"matchup": "", "date": "18950527", "content_type": "match information"}]
        _, discarded = normalize_and_dedup(entries, page_num=1)
        assert len(discarded) == 1
        assert discarded[0]["reason"] == "empty title"

    def test_filtered_content_type_discard_recorded(self):
        entries = [{"title": "Reading School", "date": "18950527", "content_type": "statistics"}]
        _, discarded = normalize_and_dedup(entries, page_num=1, allowed_types={"match information"})
        assert len(discarded) == 1
        assert discarded[0]["reason"] == "filtered content type"

    def test_non_dict_discard_recorded(self):
        _, discarded = normalize_and_dedup(["not a dict"], page_num=1)
        assert len(discarded) == 1
        assert discarded[0]["reason"] == "not a dict"

    def test_duplicate_discard_recorded(self):
        entries = [
            {"matchup": "A v B", "date": "18950527", "content_type": "match information"},
            {"matchup": "A v B", "date": "18950527", "content_type": "match information"},
        ]
        _, discarded = normalize_and_dedup(entries, page_num=1)
        assert len(discarded) == 1
        assert discarded[0]["reason"] == "duplicate"

    def test_discard_includes_original_entry(self):
        entries = [{"matchup": "", "date": "18950527", "content_type": "match information"}]
        _, discarded = normalize_and_dedup(entries, page_num=1)
        assert discarded[0]["entry"]["date"] == "18950527"


# ── Cross-page duplicate tracking ──────────────────────────────────────────


def _row(matchup, page, date="18950527", content_type="match information"):
    return {"matchup": matchup, "page": page, "date": date, "content_type": content_type}


class TestTrackCrossPage:
    def test_same_entry_on_later_page_reported(self):
        seen: dict = {}
        assert track_cross_page(seen, [_row("Team A v Team B", 1)]) == []
        dupes = track_cross_page(seen, [_row("Team A v Team B", 5)])
        assert len(dupes) == 1
        assert dupes[0]["page"] == 5
        assert dupes[0]["first_page"] == 1

    def test_different_dates_not_reported(self):
        seen: dict = {}
        track_cross_page(seen, [_row("Team A v Team B", 1, date="18950527")])
        assert track_cross_page(seen, [_row("Team A v Team B", 5, date="18950603")]) == []

    def test_first_occurrence_not_reported(self):
        assert track_cross_page({}, [_row("Team A v Team B", 1)]) == []

    def test_normalization_applied_to_key(self):
        # Punctuation differences shouldn't defeat cross-page matching
        seen: dict = {}
        track_cross_page(seen, [_row("Waterlow's v East Finchley", 1)])
        dupes = track_cross_page(seen, [_row("Waterlows v East Finchley", 9)])
        assert len(dupes) == 1

    def test_reversed_team_order_still_reported(self):
        # Cross-page duplicates are frequently two different newspapers'
        # write-ups of the same match, which routinely name the teams in
        # the opposite order -- unlike within-page dedup, this must not be
        # order-sensitive. See _row_key()'s docstring in indexing.py.
        seen: dict = {}
        track_cross_page(seen, [_row("Liverpool v Oxton", 59)])
        dupes = track_cross_page(seen, [_row("Oxton v Liverpool", 61)])
        assert len(dupes) == 1


# ── Prompt building ────────────────────────────────────────────────────────


class TestBuildUserPrompt:
    def test_contains_page_number(self):
        prompt = build_user_prompt(42, "Some text")
        assert "page 42" in prompt.lower()

    def test_contains_whit_monday_example(self):
        prompt = build_user_prompt(1, "Some text")
        assert "Whit-Monday" in prompt

    def test_contains_date_phrase_field(self):
        # Date resolution moved to deterministic Python code (resolve_date_phrase) --
        # the model is asked to quote the verbatim phrase, not compute a date itself.
        prompt = build_user_prompt(1, "Some text")
        assert "date_phrase" in prompt
        assert "do not compute a date yourself" in prompt.lower()

    def test_contains_few_shot_examples(self):
        prompt = build_user_prompt(1, "Some text")
        assert "EXAMPLES OF CORRECT EXTRACTION" in prompt
        assert "18950527" in prompt

    def test_contains_anti_over_extraction_rules(self):
        prompt = build_user_prompt(1, "Some text")
        assert "fixture information" in prompt.lower()
        assert "2-8 entries" in prompt

    def test_contains_mr_dropping_hint(self):
        prompt = build_user_prompt(1, "Some text")
        assert "Mr" in prompt and "F Gentle" in prompt

    def test_contains_oc_dropping_hint(self):
        prompt = build_user_prompt(1, "Some text")
        assert "OC" in prompt

    def test_contains_one_entry_per_team_player_assessments_rule(self):
        # Regression test: a page with brief one-sentence character
        # assessments for several players (e.g. "Regarding the abilities of
        # the players...") must be ONE "player information" entry per team,
        # not a separate "biography" entry per player mentioned.
        prompt = build_user_prompt(1, "Some text")
        assert "Reading School players" in prompt
        assert "a separate \"biography\" entry for Jackson" in prompt
        assert "standalone" in prompt.lower()

    def test_contains_one_statistics_entry_per_team_rule(self):
        # Regression test: a team with separate batting/bowling tables and/or
        # First XI + Second XI tables must be ONE "player statistics" entry,
        # not one entry per table (e.g. page 58's Liverpool Cricket Club,
        # which was split into 6 separate batting/bowling averages entries).
        prompt = build_user_prompt(1, "Some text")
        assert "Liverpool player statistics" in prompt
        assert "ONE \"player statistics\"" in prompt or "ONE entry" in prompt
        assert "Liverpool batting averages" in prompt  # named as an incorrect example

    def test_contains_unplayed_fixture_preview_example(self):
        # Regression test: pages 32 and 41 had future-tense fixture-preview
        # paragraphs ("will again be fought out by...", "have no fixture for
        # to-morrow... play the Wycombe Club") indexed as "fixture
        # information" entries -- these must be skipped entirely, not just
        # re-tagged under a different content_type.
        prompt = build_user_prompt(1, "Some text")
        assert "Old Higher Grade v Camden" in prompt
        assert "no entry of any kind" in prompt.lower()
        assert "will again be fought out" in prompt

    def test_contains_shared_roundup_date_rule(self):
        # Regression test: page 59's "CRICKET NOTES" roundup states "on
        # Saturday" only in the New Brighton v Formby recap; the day-less
        # recaps around it (Liverpool v Oxton, Rock Ferry v Cheadle Hulme,
        # Wallasey v Oxton Second XI, ...) were getting the PUBLICATION date
        # (18950914) instead of inheriting "on Saturday" (the real match
        # date, 18950907, confirmed by page 61's cross-reference to the
        # same matches).
        prompt = build_user_prompt(1, "Some text")
        assert "New Brighton...on Saturday...Formby" in prompt or "New Brighton v Formby" in prompt
        assert "date_phrase applies to EVERY recap in the run" in prompt
        assert "publication date" in prompt.lower()

    def test_contains_team_aggregates_without_player_table_rule(self):
        # Regression test: page 27's "Royal Berks Seed Establishment" and
        # "Biscuit Factory" give only a numeric season record (win/loss/
        # drawn, runs for/against) with NO separate player-averages table,
        # and got miscategorized as "team information" instead of
        # "statistics" -- the model was treating "team aggregates" as only
        # ever a second entry alongside player stats.
        prompt = build_user_prompt(1, "Some text")
        assert "Royal Berks Seed Establishment team aggregates" in prompt
        assert "WHETHER OR NOT" in prompt

    def test_contains_generic_headline_rule(self):
        # Regression test: page 3's "MESSRS FORDAM'S EMPLOYEES" headline is
        # a generic label, not "Team A v Team B" -- the model titled the
        # entry from the headline instead of the real opponents ("Sewell
        # Lime Works" and "Blows Down Lime Works") named in the body.
        prompt = build_user_prompt(1, "Some text")
        assert "Sewell Lime Works v Blows Down Lime Works" in prompt
        assert "Messrs Fordam's Employees" in prompt

    def test_contains_wrapped_team_qualifier_rule(self):
        # Regression test: page 44's headline "NEW CHESTERTON JUNIORS v.
        # LIBERAL\n2nd XI." wraps the "2nd XI" qualifier onto its own line
        # right after "LIBERAL" -- the model attached it to the wrong team,
        # producing "New Chesterton Juniors Second XI v Liberal" instead of
        # "New Chesterton Juniors v Liberal Second XI".
        prompt = build_user_prompt(1, "Some text")
        assert "New Chesterton Juniors v Liberal Second XI" in prompt
        assert "New Chesterton Juniors Second XI v Liberal" in prompt

    def test_publication_date_detected(self):
        text = "SATURDAY 8 JUNE 1895\nCricket content"
        prompt = build_user_prompt(1, text)
        assert "1895-06-08" in prompt
        assert "Saturday" in prompt

    def test_publication_date_unknown(self):
        prompt = build_user_prompt(1, "No date here")
        assert "unknown" in prompt.lower()

    def test_page_text_included(self):
        prompt = build_user_prompt(1, "KENSWORTH v DUNSTABLE VICTORIA")
        assert "KENSWORTH v DUNSTABLE VICTORIA" in prompt


# ── Valid content types ────────────────────────────────────────────────────


class TestValidContentTypes:
    def test_match_information_is_valid(self):
        assert "match information" in VALID_CONTENT_TYPES

    def test_statistics_is_valid(self):
        assert "statistics" in VALID_CONTENT_TYPES

    def test_biography_is_valid(self):
        assert "biography" in VALID_CONTENT_TYPES

    def test_at_least_15_types(self):
        assert len(VALID_CONTENT_TYPES) >= 15
