"""Tests for paddle_ocr.py — PaddleOCR transcription engine."""

import json

import pytest
import requests

from tonywebb import config, paddle_ocr


class _FakeResponse:
    def __init__(self, *, status_code=200, json_data=None, text=""):
        self.status_code = status_code
        self._json = json_data
        self.text = text

    def json(self):
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")


class _FakeSession:
    """Records POST/GET calls and returns queued responses in order."""

    def __init__(self, posts=None, gets=None):
        self._posts = list(posts or [])
        self._gets = list(gets or [])
        self.post_calls = []
        self.get_calls = []

    def post(self, url, **kwargs):
        self.post_calls.append({"url": url, **kwargs})
        return self._posts.pop(0)

    def get(self, url, **kwargs):
        self.get_calls.append({"url": url, **kwargs})
        return self._gets.pop(0)


def _done(url):
    return _FakeResponse(json_data={"data": {"state": "done", "resultUrl": {"jsonUrl": url}}})


def _running():
    return _FakeResponse(json_data={"data": {"state": "running", "extractProgress": {}}})


def _failed(msg):
    return _FakeResponse(json_data={"data": {"state": "failed", "errorMsg": msg}})


class TestSubmitJob:
    def test_posts_multipart_and_returns_job_id(self):
        session = _FakeSession(
            posts=[_FakeResponse(json_data={"data": {"jobId": "job-123"}})]
        )
        job_id = paddle_ocr.submit_job(
            session, "tok", b"img-bytes", "image/jpeg", "PaddleOCR-VL-1.6"
        )
        assert job_id == "job-123"
        call = session.post_calls[0]
        assert call["url"] == config.PADDLEOCR_JOB_URL
        assert call["headers"]["Authorization"] == "bearer tok"
        # image bytes go up as a multipart file, not JSON
        assert call["files"]["file"][1] == b"img-bytes"
        assert call["data"]["model"] == "PaddleOCR-VL-1.6"

    def test_raises_on_non_200(self):
        session = _FakeSession(
            posts=[_FakeResponse(status_code=500, text="boom")]
        )
        with pytest.raises(RuntimeError, match="boom"):
            paddle_ocr.submit_job(
                session, "tok", b"img", "image/jpeg", "PaddleOCR-VL-1.6"
            )


class TestPollJob:
    def test_returns_jsonl_url_when_done(self):
        session = _FakeSession(gets=[_done("http://x/result.jsonl")])
        url = paddle_ocr.poll_job(session, "tok", "job-1", interval=0, sleep=lambda s: None)
        assert url == "http://x/result.jsonl"

    def test_loops_while_running_then_returns(self):
        session = _FakeSession(gets=[_running(), _running(), _done("http://x/r.jsonl")])
        slept = []
        url = paddle_ocr.poll_job(
            session, "tok", "job-1", interval=5, sleep=lambda s: slept.append(s)
        )
        assert url == "http://x/r.jsonl"
        assert slept == [5, 5]  # slept once per running poll

    def test_raises_on_failed_state(self):
        session = _FakeSession(gets=[_failed("bad image")])
        with pytest.raises(RuntimeError, match="bad image"):
            paddle_ocr.poll_job(session, "tok", "job-1", sleep=lambda s: None)

    def test_raises_on_timeout(self):
        session = _FakeSession(gets=[_running()])
        clock = iter([0.0, 700.0])
        with pytest.raises(RuntimeError, match="timed out"):
            paddle_ocr.poll_job(
                session, "tok", "job-1", timeout=600, sleep=lambda s: None,
                now=lambda: next(clock),
            )


def _block(label, content, **extra):
    return {"block_label": label, "block_content": content, **extra}


class TestBlocksToText:
    def test_dewraps_text_block_into_one_line(self):
        blocks = [_block("text", "Shire Hall: P. W. Scrivener c Fagg b\nMinns 44, R. James b\nBarker 0.")]
        assert paddle_ocr.blocks_to_text(blocks) == (
            "Shire Hall: P. W. Scrivener c Fagg b Minns 44, R. James b Barker 0."
        )

    def test_preserves_hyphen_wrap_for_later_cleanup(self):
        # A word split by a hyphen at the wrap keeps its "-\n" so the existing
        # clean-transcriptions guarded hyphen join handles it.
        blocks = [_block("text", "excellent per-\nformances all round")]
        assert paddle_ocr.blocks_to_text(blocks) == "excellent per-\nformances all round"

    def test_heading_labels_get_markdown_markers(self):
        blocks = [
            _block("doc_title", "BEDFORDSHIRE TIMES"),
            _block("paragraph_title", "BEDFORD BOWLERS\nPUNISHED"),
            _block("figure_title", "Peterborough"),
        ]
        assert paddle_ocr.blocks_to_text(blocks) == (
            "# BEDFORDSHIRE TIMES\n\n## BEDFORD BOWLERS PUNISHED\n\n### Peterborough"
        )

    def test_table_block_emitted_verbatim(self):
        html = "<table><tr><td>A. W. Snowden b Meldrum</td><td>96</td></tr></table>"
        assert paddle_ocr.blocks_to_text([_block("table", html)]) == html

    def test_reference_content_keeps_line_breaks(self):
        blocks = [_block("reference_content", "Wootton v. Britannia Works.\nWood End v. Lavendon.")]
        assert paddle_ocr.blocks_to_text(blocks) == (
            "Wootton v. Britannia Works.\nWood End v. Lavendon."
        )

    def test_skips_blank_blocks(self):
        blocks = [_block("text", "real"), _block("text", "   "), _block("text", "next")]
        assert paddle_ocr.blocks_to_text(blocks) == "real\n\nnext"

    def test_blocks_joined_with_blank_line(self):
        blocks = [_block("text", "one"), _block("text", "two")]
        assert paddle_ocr.blocks_to_text(blocks) == "one\n\ntwo"


class TestCollapseRepeats:
    def test_collapses_three_or_more_consecutive_duplicates(self):
        assert paddle_ocr._collapse_repeats("very very very odd") == "very odd"

    def test_leaves_a_single_repeat_alone(self):
        # A legitimate doubled word ("had had") must survive.
        assert paddle_ocr._collapse_repeats("he had had enough") == "he had had enough"

    def test_collapses_multiple_runs_independently(self):
        text = "INDUSTRY INDUSTRIAL INDUSTRIAL INDUSTRIAL INDUSTRAL INDUSTRAL INDUSTRAL"
        assert paddle_ocr._collapse_repeats(text) == "INDUSTRY INDUSTRIAL INDUSTRAL"


class TestCollapseDotRuns:
    def test_collapses_a_dot_leader_loop(self):
        line = "W. B. Franklin b Relf " + "... " * 400 + "11"
        out = paddle_ocr._collapse_dot_runs(line)
        assert out == "W. B. Franklin b Relf .. 11"

    def test_preserves_initials_and_periods(self):
        s = "P. J. Halsey c Sayles b Anderson 5. Next over."
        assert paddle_ocr._collapse_dot_runs(s) == s


class TestBlocksToTextRepetition:
    def test_degenerate_block_is_dropped(self):
        # A VL repetition-collapse block (huge, almost no distinct words) is
        # unrecoverable noise -- drop it rather than emit a wall or a fragment.
        good = _block("text", "Real match report with varied words here today.")
        junk = _block("paragraph_title", "INDUSTRY " + "INDUSTRIAL INDUSTRY " * 300)
        assert paddle_ocr.blocks_to_text([good, junk]) == (
            "Real match report with varied words here today."
        )

    def test_short_low_diversity_repetition_is_dropped(self):
        # A stochastically-short degeneration that dodges the length gate but is
        # still a repeated-word smear (few distinct words, one repeated 3+).
        junk = "INDUSTRY INDUSTRIAL INDUSTRY INDUSTRIAL INDUSTRAL INDUSTRIAL INDUSTRIAL INDUSTRAL"
        good = _block("text", "Report with plenty of genuinely different words in it.")
        assert paddle_ocr.blocks_to_text([good, _block("paragraph_title", junk)]) == (
            "Report with plenty of genuinely different words in it."
        )

    def test_ordinary_block_with_some_repeats_is_kept(self):
        # A normal scorecard repeats "b" and small scores but stays diverse.
        content = ("Blunham: T. Norman b Swales 30, R. Reid b Rowe 1, H. Single "
                   "b Swales 13, R. Brown b Swales 2, extras 11, total 104.")
        out = paddle_ocr.blocks_to_text([_block("text", content)])
        assert out == content

    def test_bowler_dominated_scorecard_is_kept(self):
        # Regression: a column-wrapped innings where one bowler takes every
        # wicket repeats "b"/"Anderson"/initials enough to push the distinct
        # RATIO under 0.5, but it has dozens of distinct words -- it must NOT
        # be mistaken for a repetition smear and dropped.
        content = ("F. Keable b Anderson 61, F. Parry b Anderson 3, F. Halsey b "
                   "Anderson 5, F. Smith b Anderson 0, F. Brown b Anderson 2, F. "
                   "Green b Anderson 1, F. White b Anderson 4, F. Black b Anderson "
                   "0, extras 4, total 80")
        assert not paddle_ocr._is_degenerate(content)
        assert paddle_ocr.blocks_to_text([_block("text", content)]) == content

    def test_table_html_is_not_touched_by_collapse(self):
        # td/td/td repetition in HTML must not be mangled.
        html = "<table><tr><td>0</td><td>0</td><td>0</td></tr></table>"
        assert paddle_ocr.blocks_to_text([_block("table", html)]) == html

    def test_dot_leader_loop_inside_a_table_cell_is_tamed(self):
        html = "<table><tr><td>Down " + "." * 200 + "</td></tr></table>"
        assert paddle_ocr.blocks_to_text([_block("table", html)]) == (
            "<table><tr><td>Down .. </td></tr></table>"
        )

    def test_dot_leader_loop_in_a_real_card_is_tamed(self):
        # A scorecard whose leader looped stays as content, dots collapsed.
        content = "I. G. Baker c Dedman b Tomlin " + "... " * 300 + "11"
        assert paddle_ocr.blocks_to_text([_block("text", content)]) == (
            "I. G. Baker c Dedman b Tomlin .. 11"
        )


class TestTextFromJsonl:
    def test_builds_from_layout_blocks_across_lines(self):
        line1 = json.dumps({"result": {"layoutParsingResults": [
            {"prunedResult": {"parsing_res_list": [
                _block("paragraph_title", "HEADLINE"),
                _block("text", "body wrapped\nonto two lines"),
            ]}},
        ]}})
        line2 = json.dumps({"result": {"layoutParsingResults": [
            {"prunedResult": {"parsing_res_list": [_block("text", "second page")]}},
        ]}})
        session = _FakeSession(gets=[_FakeResponse(text=f"{line1}\n{line2}\n")])
        text = paddle_ocr.text_from_jsonl(session, "http://x/r.jsonl")
        assert text == "## HEADLINE\n\nbody wrapped onto two lines\n\nsecond page"


class TestTranscribePagePaddle:
    def _jsonl(self, text):
        return json.dumps({"result": {"layoutParsingResults": [
            {"prunedResult": {"parsing_res_list": [_block("text", text)]}},
        ]}})

    def test_empty_image_bytes_raises(self):
        session = _FakeSession()
        with pytest.raises(ValueError, match="empty"):
            paddle_ocr.transcribe_page_paddle(
                session, "tok", 1, b"", "image/jpeg", "PaddleOCR-VL-1.6"
            )

    def test_submits_polls_and_returns_reflowed_text(self):
        session = _FakeSession(
            posts=[_FakeResponse(json_data={"data": {"jobId": "j-1"}})],
            gets=[_done("http://x/r.jsonl"), _FakeResponse(text=self._jsonl("wrapped line\none block"))],
        )
        text = paddle_ocr.transcribe_page_paddle(
            session, "tok", 1, b"img", "image/jpeg", "PaddleOCR-VL-1.6"
        )
        assert text == "wrapped line one block"

    def test_empty_result_raises(self):
        session = _FakeSession(
            posts=[_FakeResponse(json_data={"data": {"jobId": "j-1"}})],
            gets=[_done("http://x/r.jsonl"), _FakeResponse(text=self._jsonl("   "))],
        )
        with pytest.raises(RuntimeError, match="empty"):
            paddle_ocr.transcribe_page_paddle(
                session, "tok", 1, b"img", "image/jpeg", "PaddleOCR-VL-1.6"
            )
