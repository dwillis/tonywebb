"""PaddleOCR transcription engine.

Submits a page image to the PaddleOCR async jobs API, polls the job to
completion, and returns the extracted text as Markdown. Used by the
`transcribe --engine paddleocr` path as an alternative to the vision-LLM
engine.

The API is a three-step async flow:
  1. POST the image bytes  -> a jobId
  2. poll GET jobs/{id}    -> until state == "done", yielding a JSONL result URL
  3. GET the JSONL         -> Markdown text per layout-parsing result
"""

import json
import re
import time

from . import config

# PaddleOCR's VL model sometimes degenerates on an unparseable region (a
# masthead, an advert border) and emits the same word hundreds of times. Three
# identical consecutive words never occur in real scorecard/prose text, so a
# run of 3+ collapses to one -- turning the noise wall back into its lead words.
_REPEAT_RUN_RE = re.compile(r"\b(\w+)(?:\s+\1\b){2,}")


def _collapse_repeats(text: str) -> str:
    return _REPEAT_RUN_RE.sub(r"\1", text)


# A dot-leader loop: PaddleOCR sometimes repeats a scorecard's "..." leader
# hundreds of times. Collapse any run of 2+ dot groups (dots plus interior
# spaces) to the normal " .. " leader. Single sentence periods and initials
# (one dot, broken by letters) never match.
_DOT_RUN_RE = re.compile(r"[ \t]*(?:\.[ \t]*){2,}")


def _collapse_dot_runs(text: str) -> str:
    return _DOT_RUN_RE.sub(" .. ", text)


def _is_degenerate(text: str) -> bool:
    """True for a VL repetition-collapse block: a smear of a few repeated words.

    Keyed on distinct-vocabulary SIZE, not ratio: a degeneration loop repeats a
    handful of words (the walls we've seen have 2-3 distinct), whereas any real
    block -- even a column-wrapped scorecard where one bowler takes every wicket
    and 'b'/initials repeat -- carries dozens of distinct names and numbers. A
    ratio test wrongly flagged those bowler-dominated cards; a vocabulary-size
    test does not.
    """
    tokens = re.findall(r"\w+", text)
    return len(tokens) >= 8 and len({t.lower() for t in tokens}) <= 4

_OPTIONAL_PAYLOAD = {
    "useDocOrientationClassify": False,
    "useDocUnwarping": False,
    "useChartRecognition": False,
}


def submit_job(session, token, image_bytes, media_type, model):
    """Upload image bytes and return the created job's id.

    Raises RuntimeError on any non-200 response (the outer retry loop treats
    that as a transient failure and re-submits).
    """
    headers = {"Authorization": f"bearer {token}"}
    data = {"model": model, "optionalPayload": json.dumps(_OPTIONAL_PAYLOAD)}
    files = {"file": (f"page.{_ext(media_type)}", image_bytes, media_type)}
    resp = session.post(
        config.PADDLEOCR_JOB_URL, headers=headers, data=data, files=files, timeout=(60, 120)
    )
    if resp.status_code != 200:
        raise RuntimeError(f"PaddleOCR submit failed ({resp.status_code}): {resp.text}")
    return resp.json()["data"]["jobId"]


def poll_job(
    session,
    token,
    job_id,
    interval=config.PADDLEOCR_POLL_INTERVAL,
    timeout=config.PADDLEOCR_JOB_TIMEOUT,
    sleep=time.sleep,
    now=time.monotonic,
):
    """Poll a job until it finishes, returning the result JSONL URL.

    Raises RuntimeError if the job reports state "failed" or if it does not
    complete within `timeout` seconds.
    """
    headers = {"Authorization": f"bearer {token}"}
    start = now()
    while True:
        resp = session.get(f"{config.PADDLEOCR_JOB_URL}/{job_id}", headers=headers, timeout=(60, 120))
        resp.raise_for_status()
        data = resp.json()["data"]
        state = data["state"]
        if state == "done":
            return data["resultUrl"]["jsonUrl"]
        if state == "failed":
            raise RuntimeError(f"PaddleOCR job failed: {data.get('errorMsg')}")
        if now() - start > timeout:
            raise RuntimeError(f"PaddleOCR job {job_id} timed out after {timeout}s")
        sleep(interval)


# Layout labels that are headings, mapped to their Markdown marker. Everything
# else is treated as body text (dewrapped to one logical line per block).
_HEADING_MARK = {
    "doc_title": "#",
    "header": "#",
    "paragraph_title": "##",
    "figure_title": "###",
}


def _dewrap(content: str) -> str:
    """Join a block's column-wrapped lines into one logical line.

    Each `\\n` inside a block is a physical column wrap, joined with a space --
    except a trailing hyphen, whose `-\\n` is preserved so the downstream
    clean-transcriptions guarded-hyphen pass can decide whether to drop it.
    """
    lines = [ln.strip() for ln in content.split("\n")]
    lines = [ln for ln in lines if ln]
    out = ""
    for i, ln in enumerate(lines):
        if i == 0:
            out = ln
        elif out.endswith("-"):
            out += "\n" + ln
        else:
            out += " " + ln
    return out


def blocks_to_text(blocks) -> str:
    """Rebuild page text from a `parsing_res_list`, one logical line per block.

    This is the wrapped-line reflow: PaddleOCR's layout model has already
    segmented the page (each team's scorecard, each paragraph, each fixture
    list is its own block), so we dewrap within a block and keep block
    boundaries -- which the flattened markdown cannot distinguish from wraps.
    """
    parts = []
    for block in blocks:
        label = block.get("block_label", "")
        content = block.get("block_content") or ""
        if not content.strip():
            continue
        if label == "table":
            parts.append(_collapse_dot_runs(content.strip()))
        elif label == "reference_content":
            parts.append("\n".join(ln.strip() for ln in content.split("\n") if ln.strip()))
        else:
            text = _collapse_dot_runs(_collapse_repeats(_dewrap(content)))
            if _is_degenerate(text):
                continue
            mark = _HEADING_MARK.get(label)
            parts.append(f"{mark} {text}" if mark else text)
    return "\n\n".join(parts)


def build_page_text(layout_results) -> str:
    """Join each layout-parsing result's block text with a blank line."""
    pages = []
    for res in layout_results:
        blocks = res.get("prunedResult", {}).get("parsing_res_list", [])
        text = blocks_to_text(blocks)
        if text:
            pages.append(text)
    return "\n\n".join(pages)


def text_from_jsonl(session, jsonl_url):
    """Download the result JSONL and rebuild the page text from layout blocks."""
    resp = session.get(jsonl_url, timeout=(60, 120))
    resp.raise_for_status()
    results = []
    for line in resp.text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        results.extend(json.loads(line)["result"]["layoutParsingResults"])
    return build_page_text(results)


def transcribe_page_paddle(
    session,
    token,
    page_num,
    image_bytes,
    media_type,
    model,
    interval=config.PADDLEOCR_POLL_INTERVAL,
    timeout=config.PADDLEOCR_JOB_TIMEOUT,
):
    """Transcribe one page via PaddleOCR: submit, poll, and return Markdown.

    Mirrors transcribe.transcribe_page's contract: raises ValueError on empty
    input and RuntimeError if the OCR result comes back empty, so the shared
    retry loop can re-submit.
    """
    if not image_bytes:
        raise ValueError(f"Page {page_num}: image_bytes is empty — nothing to transcribe")
    job_id = submit_job(session, token, image_bytes, media_type, model)
    jsonl_url = poll_job(session, token, job_id, interval=interval, timeout=timeout)
    text = text_from_jsonl(session, jsonl_url).strip()
    if not text:
        raise RuntimeError(f"Page {page_num}: PaddleOCR returned empty text")
    return text


def _ext(media_type):
    return {"image/jpeg": "jpg", "image/png": "png"}.get(media_type, "jpg")
