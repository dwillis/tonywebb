"""Tests for tonywebb.reconcile — multi-run OCR reconciliation."""

import json

import pytest

from tonywebb import reconcile
from tonywebb.reconcile import (
    Dispute,
    align_to_reference,
    apply_referee,
    arithmetic_flags,
    build_referee_prompt,
    call_referee,
    normalize_line,
    reconcile_page,
)
from tonywebb.llm_common import JSONExtractError


# ── normalize_line ────────────────────────────────────────────────────────────


class TestNormalizeLine:
    def test_dot_leaders_collapsed(self):
        assert normalize_line("Curtis........... 9 196") == "Curtis 9 196"

    def test_dotted_total_reduced_to_number(self):
        # `... 136` → leading dot-run collapses to a space, leaving just the number.
        assert normalize_line("... 136") == "136"

    def test_ornament_lines_become_empty(self):
        assert normalize_line("———") == ""
        assert normalize_line("....") == ""
        assert normalize_line("----") == ""

    def test_unicode_dash_and_quote_folding(self):
        # em-dash en-dash curly quotes fold to ASCII; content still present
        assert normalize_line("Smith – Jones “quote”") == "Smith - Jones \"quote\""

    def test_case_sensitive(self):
        # b/B in dismissals is a real difference — must not be folded.
        assert normalize_line("c Smith b Jones") != normalize_line("c Smith B Jones")

    def test_blank_becomes_empty(self):
        assert normalize_line("   ") == ""


# ── align_to_reference ─────────────────────────────────────────────────────────


class TestAlignToReference:
    def test_identical(self):
        ref = ["one", "two", "three"]
        segs = align_to_reference(ref, ref)
        assert len(segs) == 1
        assert segs[0].kind == "equal"
        assert segs[0].ref_span == (0, 3)

    def test_one_long_line_equals_wrapped_lines(self):
        # The page-62 case: qwen emits one long paragraph line, gemini wraps at ~60 chars.
        long_line = "Played at Helston on Friday and resulted in a win for the visitors"
        wrapped = [
            "Played at Helston on Friday and",
            "resulted in a win for the",
            "visitors",
        ]
        segs = align_to_reference([long_line], wrapped)
        # Joined keys match → one equal segment (wrap-repair reclassifies the replace).
        assert len(segs) == 1
        assert segs[0].kind == "equal"
        assert segs[0].ref_span == (0, 1)
        assert "\n".join(segs[0].other_lines) == "\n".join(wrapped)

    def test_single_word_difference_is_one_replace(self):
        ref = ["the quick brown fox", "jumps over the lazy dog"]
        other = ["the quick RED fox", "jumps over the lazy dog"]
        segs = align_to_reference(ref, other)
        kinds = [s.kind for s in segs]
        assert "replace" in kinds
        replace = [s for s in segs if s.kind == "replace"][0]
        assert replace.ref_span == (0, 1)
        assert replace.other_lines == ["the quick RED fox"]

    def test_ref_only_when_other_missing_line(self):
        ref = ["a", "b", "c"]
        other = ["a", "c"]
        segs = align_to_reference(ref, other)
        ref_only = [s for s in segs if s.kind == "ref_only"]
        assert len(ref_only) == 1
        assert ref_only[0].ref_span == (1, 2)

    def test_other_only_insert_at_correct_gap(self):
        ref = ["a", "c"]
        other = ["a", "b", "c"]
        segs = align_to_reference(ref, other)
        insert = [s for s in segs if s.kind == "other_only"]
        assert len(insert) == 1
        # Insertion is at the gap before ref index 1.
        assert insert[0].ref_span == (1, 1)
        assert insert[0].other_lines == ["b"]

    def test_long_paragraph_wrapped_into_many_lines_still_matches(self):
        # The old fixed wrap-join cap of 8 lines could never bridge a real
        # column-width paragraph wrap (gemini wraps qwen's single-line
        # paragraphs into 30+ lines). The incremental join with length
        # early-abort must match regardless of how many lines the wrap spans.
        words = [f"word{i}" for i in range(120)]
        long_line = " ".join(words)
        wrapped = [" ".join(words[i:i + 6]) for i in range(0, 120, 6)]  # 20 lines
        assert len(wrapped) == 20
        segs = align_to_reference([long_line], wrapped)
        assert [s.kind for s in segs] == ["equal"]

    def test_noisy_scorecard_lines_pair_one_to_one(self):
        # Dense OCR noise: consecutive lines each differ slightly between
        # runs (a misread digit or surname per line), so no exact resync
        # anchor exists anywhere nearby. Nearly-identical lines must pair
        # 1:1 as single-line disputes instead of merging into one giant
        # unsplittable core.
        ref = [
            "H. Boddy, c Kent, b Barber 0",
            "J. Smith, b Barber 12",
            "W. Jones, run out 4",
        ]
        other = [
            "H. Boddy, c Keen, b Barber 9",
            "J. Smith, b Barber 13",
            "W. Jones, run ont 4",
        ]
        segs = align_to_reference(ref, other)
        assert [s.kind for s in segs] == ["replace", "replace", "replace"]
        assert all(s.ref_span[1] - s.ref_span[0] == 1 for s in segs)

    def test_elect_reference_prefers_run_agreeing_with_majority(self):
        # Page 55-style: the default first run deviates structurally (splits
        # two-column rows) while the other two agree with each other -- the
        # election must pick one of the agreeing runs as reference, so the
        # outlier can't poison every pairwise alignment at once.
        agreeing = "\n".join(f"Player{i} b Bowler{i} {i}    second col {i}" for i in range(12))
        deviant_lines = []
        for i in range(12):
            deviant_lines.append(f"Player{i} b Bowler{i} {i}")
        for i in range(12):
            deviant_lines.append(f"second col {i}")
        deviant = "\n".join(deviant_lines)
        texts = [("deviant", deviant), ("runB", agreeing), ("runC", agreeing)]
        assert reconcile.elect_reference(texts, "deviant") == "runB"

    def test_elect_reference_keeps_default_on_agreement(self):
        text = "\n".join(f"line {i}" for i in range(10))
        texts = [("runA", text), ("runB", text), ("runC", text)]
        assert reconcile.elect_reference(texts, "runA") == "runA"

    def test_transposed_sections_reordered_before_alignment(self):
        # Scrapbook pages: different models read the pasted cuttings in
        # different column orders, so the same matches appear transposed.
        # Section headers ("X v. Y") are matched and the run re-sequenced to
        # the reference's order, so line alignment sees them in one order.
        sec_a = ["ALPHA v. BRAVO.", "A. One, b Two 3", "Total 10"]
        sec_b = ["CHARLIE v. DELTA.", "C. Three, b Four 5", "Total 20"]
        ref = sec_a + sec_b
        other = sec_b + sec_a  # transposed
        rec = reconcile_page(1, "\n".join(ref), [("runA", "\n".join(other))],
                             ref_label="ref", garbage_min_chars=0)
        assert any("reordered" in n for n in rec.notes)
        assert rec.disputes == []  # identical content once reordered
        assert rec.output_lines == ref

    def test_local_difference_inside_long_wrapped_passage_stays_small(self):
        # Regression test: a real full run showed a single misread word deep
        # inside a ~150-line scorecard turning into ONE giant dispute
        # spanning the whole rest of the page, because once the runs' wrap
        # styles diverge, difflib has no further equal anchors to find and
        # lumps everything after the first mismatch into one "replace" op.
        # Ten player rows, one line each in ref; every row wraps onto two
        # lines in "other" -- except row 5, which also has a genuine
        # misread (Kirby -> Kirbey). The fix should confine the dispute to
        # just that one row, not swallow rows 6-10 too.
        ref = [f"Player{i} b Bowler{i} run {i}" for i in range(1, 11)]
        other = []
        for i in range(1, 11):
            name = "Kirbey" if i == 5 else f"Player{i}"
            other.append(f"{name} b Bowler{i}")
            other.append(f"run {i}")
        segs = align_to_reference(ref, other)

        replaces = [s for s in segs if s.kind == "replace"]
        assert len(replaces) == 1
        assert replaces[0].ref_span == (4, 5)  # only row 5 (0-indexed)

        # Rows 1-4 and 6-10 must still resolve as equal (via the wrap-join
        # path), not get pulled into the dispute.
        equal_spans = {s.ref_span for s in segs if s.kind == "equal"}
        for i in range(1, 5):
            assert (i - 1, i) in equal_spans
        for i in range(6, 11):
            assert (i - 1, i) in equal_spans


# ── reconcile_page ─────────────────────────────────────────────────────────────


def _rec_page(ref_text, runs):
    # Small-text tests: disable the per-page 200-char garbage floor so short
    # snippets aren't mistaken for garbage runs.
    return reconcile_page(1, ref_text, runs, ref_label="ref", garbage_min_chars=0)


class TestReconcilePage:
    def test_unanimous_no_disputes(self):
        text = "line one\nline two\nline three"
        rec = _rec_page(text, [("runA", text), ("runB", text)])
        assert rec.disputes == []
        assert rec.stats.get("unanimous", 0) >= 0  # nothing diverges
        assert rec.output_lines == text.split("\n")

    def test_two_of_three_majority(self):
        ref = "Kelynack c Thomas b Oats 9\nNunn run out 62"
        runA = "Kelynack c Thomas b Oats 9\nNunn run out 62"
        runB = "Kelynack c Thomas b Oats 9\nNunn run out 60"  # misread 62 as 60
        rec = _rec_page(ref, [("runA", runA), ("runB", runB)])
        # ref and runA agree (majority) → accept 62, no referee needed.
        majority = [d for d in rec.disputes if d.resolution == "majority"]
        assert len(majority) == 1
        assert "62" in "\n".join(majority[0].chosen_lines)

    def test_three_way_conflict(self):
        ref = "the score was 9\nnext line"
        runA = "the score was 8\nnext line"
        runB = "the score was 0\nnext line"
        rec = _rec_page(ref, [("runA", runA), ("runB", runB)])
        conflicts = [d for d in rec.disputes if d.resolution == "conflict"]
        assert len(conflicts) == 1

    def test_four_way_2_2_tie_is_conflict_not_majority(self):
        # Regression test: with a 4-run ensemble, two readings can each hold
        # exactly half the votes (ref+runA say "9", runB+runC say "0"). The
        # old code picked whichever key happened to be built first in the
        # variants dict (always the reference's) and called it "majority"
        # without ever consulting the referee -- a real tie is not a majority.
        ref = "the score was 9\nnext line"
        runA = "the score was 9\nnext line"
        runB = "the score was 0\nnext line"
        runC = "the score was 0\nnext line"
        rec = reconcile_page(1, ref, [("runA", runA), ("runB", runB), ("runC", runC)],
                              ref_label="ref", garbage_min_chars=0)
        assert len(rec.disputes) == 1
        assert rec.disputes[0].resolution == "conflict"

    def test_four_way_clear_plurality_still_majority(self):
        # A 2-1-1 split (no tie for the top count) is still a clear plurality
        # and should resolve without the referee, same as 2-of-3 did.
        ref = "the score was 9\nnext line"
        runA = "the score was 9\nnext line"
        runB = "the score was 0\nnext line"
        runC = "the score was 7\nnext line"
        rec = reconcile_page(1, ref, [("runA", runA), ("runB", runB), ("runC", runC)],
                              ref_label="ref", garbage_min_chars=0)
        assert len(rec.disputes) == 1
        assert rec.disputes[0].resolution == "majority"
        assert "9" in "\n".join(rec.disputes[0].chosen_lines)

    def test_n2_any_difference_is_conflict(self):
        # With only one other run (N=2: ref + runA), any diff → conflict (no majority possible).
        ref = "the score was 9\nnext line"
        runA = "the score was 8\nnext line"
        rec = _rec_page(ref, [("runA", runA)])
        assert any(d.resolution == "conflict" for d in rec.disputes)

    def test_both_insert_matching_line_accepted(self):
        ref = "alpha\nbravo"
        runA = "alpha\nINSERTED\nbravo"
        runB = "alpha\nINSERTED\nbravo"
        rec = _rec_page(ref, [("runA", runA), ("runB", runB)])
        # Both non-reference runs insert the same line → accepted (majority), not a dispute.
        assert all(d.resolution != "conflict" for d in rec.disputes)
        assert "INSERTED" in rec.output_lines

    def test_one_inserts_becomes_missing_line_conflict(self):
        ref = "alpha\nbravo"
        runA = "alpha\nINSERTED\nbravo"
        runB = "alpha\nbravo"
        rec = _rec_page(ref, [("runA", runA), ("runB", runB)])
        missing = [d for d in rec.disputes if d.kind == "missing_line"]
        assert len(missing) == 1

    def test_garbage_run_dropped(self):
        ref = ("a real page of cricket text " * 30).strip()
        garbage = "x"  # len < 200
        good = ref
        rec = reconcile_page(1, ref, [("garbage", garbage), ("good", good)], ref_label="ref")
        assert any("garbage" in n for n in rec.notes)
        # The good run still agrees fully → no disputes.
        assert all(d.resolution != "conflict" for d in rec.disputes)

    def test_garbage_run_quick_ratio_dropped(self):
        ref = ("a real page of cricket text " * 30).strip()
        # Long enough but totally different content → quick_ratio < 0.5.
        garbage = ("zzzz qqqq mmmm yyyy " * 30).strip()
        good = ref
        rec = reconcile_page(1, ref, [("garbage", garbage), ("good", good)], ref_label="ref")
        assert any("garbage" in n for n in rec.notes)

    def test_single_source_copy_through(self):
        ref = ("a real page of cricket text " * 30).strip()
        rec = reconcile_page(1, ref, [], ref_label="ref")
        assert rec.output_lines == ref.split("\n")
        assert any("single-source" in n for n in rec.notes)


# ── referee ───────────────────────────────────────────────────────────────────


class _FakeResponse:
    def __init__(self, text):
        self._text = text

    def text(self):
        return self._text


class _FakeModel:
    model_id = "claude-sonnet-4.6"

    def __init__(self, raw):
        self._raw = raw
        self.calls = []

    def prompt(self, *args, **kwargs):
        self.calls.append(kwargs)
        return _FakeResponse(self._raw)


def _make_dispute(dispute_id=1, reading_absent=False):
    return Dispute(
        page=1, dispute_id=dispute_id, ref_line_start=0, ref_line_end=1,
        kind="conflict",
        variants={"ref": "the score was 9", "runA": "the score was 8",
                  "runB": "the score was 0"},
        chosen_lines=["the score was 9"],
        context_before="", context_after="",
        resolution="conflict", chosen_label="ref",
    )


class TestReferee:
    def test_build_prompt_neutral_labels_and_no_model_names(self):
        d = _make_dispute()
        system, user = build_referee_prompt(1, [d])
        assert "Version 1" in user and "Version 2" in user
        # Model names must never appear in the referee prompt.
        for name in ("runA", "runB", "ref"):
            assert name not in user
        assert "ABSENT" in system
        assert "disputes" in user  # schema hint

    def test_apply_matches_variant(self):
        d = _make_dispute()
        items = [{"id": 1, "reading": "the score was 9", "confidence": "high"}]
        apply_referee([d], items, ref_label="ref")
        assert d.resolution == "referee"
        assert d.chosen_lines == ["the score was 9"]

    def test_apply_novel_reading(self):
        d = _make_dispute()
        items = [{"id": 1, "reading": "the score was 7", "confidence": "high"}]
        apply_referee([d], items, ref_label="ref")
        assert d.resolution == "referee_novel"
        assert d.chosen_lines == ["the score was 7"]
        assert d.referee_reading == "the score was 7"

    def test_apply_unclear_leaves_unresolved(self):
        d = _make_dispute()
        items = [{"id": 1, "reading": "the score was [unclear]", "confidence": "low"}]
        apply_referee([d], items, ref_label="ref")
        assert d.resolution == "unresolved"
        assert d.referee_unclear is True
        # Reference reading retained.
        assert d.chosen_lines == ["the score was 9"]

    def test_apply_absent_leaves_unresolved(self):
        d = _make_dispute()
        items = [{"id": 1, "reading": "ABSENT", "confidence": "high"}]
        apply_referee([d], items, ref_label="ref")
        assert d.resolution == "unresolved"

    def test_missing_id_leaves_unresolved(self):
        d = _make_dispute()
        apply_referee([d], [], ref_label="ref")
        assert d.resolution == "unresolved"

    def test_majority_not_re_adjudicated(self):
        d = Dispute(
            page=1, dispute_id=1, ref_line_start=0, ref_line_end=1, kind="conflict",
            variants={"ref": "9", "runA": "9", "runB": "0"},
            chosen_lines=["9"], resolution="majority", chosen_label="ref",
        )
        items = [{"id": 1, "reading": "5", "confidence": "high"}]
        apply_referee([d], items, ref_label="ref")
        assert d.resolution == "majority"
        assert d.chosen_lines == ["9"]

    def test_call_referee_parses_clean_json(self):
        raw = '{"disputes": [{"id": 1, "reading": "9", "confidence": "high"}]}'
        model = _FakeModel(raw)
        items, raw_out, error = call_referee(model, 1, b"img", "image/jpeg", [_make_dispute()])
        assert error is None
        assert items == [{"id": 1, "reading": "9", "confidence": "high"}]

    def test_call_referee_parses_fenced_json(self):
        raw = '```json\n{"disputes": [{"id": 1, "reading": "9", "confidence": "high"}]}\n```'
        model = _FakeModel(raw)
        items, _raw, error = call_referee(model, 1, b"img", "image/jpeg", [_make_dispute()])
        assert error is None
        assert items[0]["reading"] == "9"

    def test_call_referee_bad_json_returns_error(self):
        model = _FakeModel("not json at all")
        items, _raw, error = call_referee(model, 1, b"img", "image/jpeg", [_make_dispute()])
        assert error is not None
        assert items == []


# ── arithmetic_flags ──────────────────────────────────────────────────────────


class TestArithmeticFlags:
    INNINGS = [
        "Kelynack, c Thomas, b Oats 9",
        "Menneer, run out 1",
        "Nunn, run out 62",
        "B. Jenkin, b Blackwell 2",
        "T. D. White, c Badcock, b Hosking 17",
        "E. Jenkin, c Thomas, b Smith 14",
        "R. Craze, b Blackwell 11",
        "Brewer, c Johns, b Hosking 15",
        "D. Howell, b Blackwell 3",
        "Dr. Fox, not out 0",
        "Willey, b Hosking 0",
        "Extras 12",
        "———",
        "146",  # sum of the 12 scores above (incl Extras) = 9+1+62+2+17+14+11+15+3+0+0+12
    ]

    def test_mismatch_flagged(self):
        # Sum of the 12 scores (incl Extras) is 146 here; print a wrong total.
        lines = list(self.INNINGS)
        lines[-1] = "140"  # wrong total → mismatch
        flags = arithmetic_flags(lines, page=62)
        assert len(flags) == 1
        assert flags[0].printed_total == 140
        assert flags[0].computed_sum == 146

    def test_match_not_flagged(self):
        lines = list(self.INNINGS)  # total 146 == sum 146
        flags = arithmetic_flags(lines, page=62)
        assert flags == []

    def test_prose_with_numbers_not_flagged(self):
        # A prose paragraph ending in numbers but with no Extras line and < 6 score lines.
        prose = [
            "Daniel's eleven scored 64 against 42 knocked up by their opponents.",
            "For the winners T. D. White 13 and O. Hall 10 were the chief scorers.",
            "B. Jenkin 29 was the principal contributor for the losers.",
            "Thomas and Daniel bowled well for the winners.",
        ]
        assert arithmetic_flags(prose, page=62) == []

    def test_block_without_extras_not_flagged(self):
        # ≥6 score lines but no Extras line → not an innings block.
        lines = [f"Player {i} b Bowler {i}" for i in range(1, 9)] + ["", "100"]
        assert arithmetic_flags(lines, page=1) == []


# ── CLI end-to-end ─────────────────────────────────────────────────────────────


class TestCLI:
    def _write_run(self, tmp_path, name, pages):
        d = tmp_path / name
        d.mkdir()
        for page, text in pages.items():
            (d / f"tw_newspaper_cuttings_1895_{page}.txt").write_text(text, encoding="utf-8")
        return d

    def _run_cli(self, args):
        from tonywebb.cli import main
        main(args)

    def test_no_referee_writes_outputs_and_jsonl(self, tmp_path, monkeypatch):
        text = "alpha line one\nbravo line two\ncharlie line three\n" * 5
        ref = self._write_run(tmp_path, "refrun", {1: text, 2: text})
        runA = self._write_run(tmp_path, "runA", {1: text, 2: text})
        out_dir = tmp_path / "reconciled"
        conflicts = tmp_path / "conflicts.jsonl"
        report = tmp_path / "report.md"
        monkeypatch.chdir(tmp_path)
        self._run_cli([
            "reconcile", str(ref), str(runA), "--no-referee",
            "--output-dir", str(out_dir), "--conflicts", str(conflicts),
            "--report", str(report),
        ])
        assert (out_dir / "tw_newspaper_cuttings_1895_1.txt").exists()
        assert (out_dir / "tw_newspaper_cuttings_1895_2.txt").exists()
        assert conflicts.exists()
        rows = [json.loads(l) for l in conflicts.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert {r["page"] for r in rows} == {1, 2}
        assert report.exists()

    def test_resume_skips_existing(self, tmp_path, monkeypatch):
        text = "alpha line one\nbravo line two\ncharlie line three\n" * 5
        ref = self._write_run(tmp_path, "refrun", {1: text})
        runA = self._write_run(tmp_path, "runA", {1: text})
        out_dir = tmp_path / "reconciled"
        out_dir.mkdir()
        (out_dir / "tw_newspaper_cuttings_1895_1.txt").write_text("already done", encoding="utf-8")
        conflicts = tmp_path / "conflicts.jsonl"
        monkeypatch.chdir(tmp_path)
        self._run_cli([
            "reconcile", str(ref), str(runA), "--no-referee",
            "--output-dir", str(out_dir), "--conflicts", str(conflicts),
            "--report", str(tmp_path / "report.md"),
        ])
        # Existing output untouched; no JSONL row added for the skipped page.
        assert (out_dir / "tw_newspaper_cuttings_1895_1.txt").read_text() == "already done"
        assert not conflicts.exists() or not conflicts.read_text(encoding="utf-8").strip()

    def test_dry_run_writes_nothing(self, tmp_path, monkeypatch, capsys):
        text = "alpha line one\nbravo line two\ncharlie line three\n" * 5
        ref = self._write_run(tmp_path, "refrun", {1: text})
        runA = self._write_run(tmp_path, "runA", {1: text})
        out_dir = tmp_path / "reconciled"
        conflicts = tmp_path / "conflicts.jsonl"
        monkeypatch.chdir(tmp_path)
        self._run_cli([
            "reconcile", str(ref), str(runA), "--no-referee", "--dry-run",
            "--output-dir", str(out_dir), "--conflicts", str(conflicts),
            "--report", str(tmp_path / "report.md"),
        ])
        assert not out_dir.exists()
        assert not conflicts.exists()
        out = capsys.readouterr().out
        assert "Dry run" in out