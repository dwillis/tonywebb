"""Multi-run OCR reconciliation with an image referee.

Runs 2 or more transcription models over the same collection, auto-accepts
lines where they agree (with plurality voting when 3+ runs are used), and
asks a vision model to read the original page image where they disagree.
Line-level alignment plus targeted adjudication turns "review 247 pages"
into "review a few flagged lines per page."

The first run directory passed on the CLI is the reference (best model first);
its line breaks and ornaments are preserved in the output. Other runs are
aligned to it. See ``docs/ocr_review_plan.md`` for the full design.
"""

from __future__ import annotations

import difflib
import json
import logging
import re
import sys
import time
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

import llm

from . import config, transcribe
from .images import fetch_image, new_session
from .llm_common import JSONExtractError, load_pages_from_dir, no_thinking_kwargs, parse_json_object
from .pipeline import RawResponseLog, call_with_retry, parse_page_spec

logger = logging.getLogger(__name__)

# ── Normalization ────────────────────────────────────────────────────────────

# Unicode dashes that should fold to a hyphen-minus for comparison.
_DASHES = "\u2010\u2011\u2012\u2013\u2014\u2015\u2212\u00ad\u2043"
# A line that is nothing but separator punctuation / whitespace is an ornament.
_ORNAMENT_ONLY = re.compile(r"[-_=*.~\s]+$")


def normalize_line(line: str) -> str:
    """Return a comparison key for one line.

    Folds unicode dashes/quotes to ASCII, collapses dot-leaders (``....``) to a
    single space, collapses all whitespace, and strips the result. Ornament-only
    lines (``———``, ``....``, rules) become ``""``. Case-sensitive: ``b`` and
    ``B`` are genuinely different in dismissal notation.
    """
    text = unicodedata.normalize("NFC", line)
    for d in _DASHES:
        text = text.replace(d, "-")
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    # Dot-leaders: a run of 2+ dots is a leader, not content (`Curtis... 9` -> `Curtis 9`,
    # `... 136` -> `136`). A single dot (abbreviation) is left alone.
    text = re.sub(r"\.{2,}", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    if text and _ORNAMENT_ONLY.fullmatch(text):
        return ""
    return text


def normalize_block(text: str) -> str:
    """Comparison key for a block of text: normalized content lines joined."""
    return " ".join(normalize_line(l) for l in text.splitlines() if normalize_line(l))


def split_content_lines(text: str) -> tuple[list[str], list[tuple[int, str]]]:
    """Split page text into content lines and positioned filler lines.

    Returns ``(content_lines, ornaments)`` where ``ornaments`` is a list of
    ``(insert_before_index, raw_line)`` pairs. A line is filler (ornament or
    blank) when its normalized form is empty; everything else is content.
    Filler is excluded from alignment and re-interleaved into the output from
    the reference run, so the reference's spacing is preserved.
    """
    content_lines: list[str] = []
    ornaments: list[tuple[int, str]] = []
    for raw in text.split("\n"):
        if normalize_line(raw):
            content_lines.append(raw)
        else:
            ornaments.append((len(content_lines), raw))
    return content_lines, ornaments


# ── Alignment ────────────────────────────────────────────────────────────────


@dataclass
class Segment:
    """One piece of a pairwise alignment of ``other`` against the reference.

    ``ref_span`` is a ``(start, end)`` index range into the reference content
    lines; ``other_lines`` is the other run's raw lines that correspond.
    """

    kind: str  # equal | replace | ref_only | other_only
    ref_span: tuple[int, int]
    other_lines: list[str]


def align_to_reference(ref_content: list[str], other_content: list[str]) -> list[Segment]:
    """Align ``other_content`` to the reference, returning ordered Segments.

    Uses :class:`difflib.SequenceMatcher` over normalized keys with
    ``autojunk=False`` (the default heuristic mis-handles the repetitive
    scorecard lines), then a wrap-repair pass on each ``replace`` opcode: if
    the joined keys match (one long line == several wrapped lines) it is
    reclassified as equal; otherwise matching prefix/suffix lines are peeled
    off as equal and the unsplittable core stays a multi-line dispute.
    """
    ref_keys = [normalize_line(l) for l in ref_content]
    other_keys = [normalize_line(l) for l in other_content]
    sm = difflib.SequenceMatcher(a=ref_keys, b=other_keys, autojunk=False)
    segments: list[Segment] = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            segments.append(Segment("equal", (i1, i2), other_content[j1:j2]))
        elif tag == "delete":
            segments.append(Segment("ref_only", (i1, i2), []))
        elif tag == "insert":
            segments.append(Segment("other_only", (i1, i1), other_content[j1:j2]))
        else:  # replace
            segments.extend(
                _wrap_repair(ref_keys, other_keys, other_content, i1, i2, j1, j2)
            )
    return segments


# How many lines one side may wrap a single line of the other into (a safety
# valve only -- the length early-abort in _join_match is the real bound), how
# far ahead to search (on each side) for the next point both sides agree
# again after a genuine difference, and how similar two lines must be to be
# paired 1:1 as a "changed line" rather than treated as unrelated. Bounded so
# a single misread word deep inside a long, otherwise-identical passage costs
# a small local search, not a linear rescan of the whole page.
_MAX_WRAP_JOIN = 64
_RESYNC_WINDOW = 48
_PAIR_SIMILARITY = 0.7


def _join_match(target: str, keys, start: int, limit: int) -> int | None:
    """Return k >= 2 if keys[start:start+k] space-joined equals target.

    Grows the join incrementally and aborts as soon as the accumulated
    length exceeds the target's -- content-line keys are never empty, so the
    length grows by at least 2 per line and the loop is O(len(target))
    regardless of _MAX_WRAP_JOIN. This is what lets one run's single-line
    paragraph match another run's 30-plus wrapped lines (the old fixed cap
    of 8 could never bridge a real column-width paragraph wrap).
    """
    tlen = len(target)
    acc = [keys[start]]
    acc_len = len(keys[start])
    k = 1
    while start + k < limit and k < _MAX_WRAP_JOIN and acc_len < tlen:
        nxt = keys[start + k]
        acc.append(nxt)
        acc_len += 1 + len(nxt)
        k += 1
        if acc_len == tlen and " ".join(acc) == target:
            return k
    return None


def _fuzzy_join(target: str, keys, start: int, limit: int) -> int | None:
    """Return k >= 1 if keys[start:start+k] space-joined is ~similar to target.

    The exact-join test above handles clean re-wrapping; this handles a
    wrapped passage that ALSO contains a small OCR difference (one misread
    word inside a paragraph one run wrapped over many lines). Joins are only
    scored once their length is within ~15% of the target's, and accepted at
    _PAIR_SIMILARITY -- confining the noise to a single-position dispute
    instead of opening an ever-growing core.
    """
    tlen = len(target)
    acc = keys[start]
    k = 1
    best: tuple[float, int] | None = None
    while True:
        if acc and abs(len(acc) - tlen) <= max(8, int(0.15 * tlen)):
            ratio = difflib.SequenceMatcher(None, target, acc).ratio()
            if ratio >= _PAIR_SIMILARITY and (best is None or ratio > best[0]):
                best = (ratio, k)
        if start + k >= limit or k >= _MAX_WRAP_JOIN or len(acc) > 1.15 * tlen + 8:
            break
        acc = acc + " " + keys[start + k]
        k += 1
    return best[1] if best else None


def _match_at(ref_keys, other_keys, ri: int, oj: int, i2: int, j2: int) -> tuple[int, int] | None:
    """If ref/other resync at (ri, oj), return (ref_lines_consumed, other_lines_consumed).

    Tries an exact single-line match first, then a wrap-join in either
    direction (ref-is-one-other-is-many, or the reverse). Returns None if
    none of those hold at this exact position -- a genuine difference.
    """
    if ref_keys[ri] == other_keys[oj]:
        return 1, 1
    if j2 - oj >= 2:
        k = _join_match(ref_keys[ri], other_keys, oj, j2)
        if k is not None:
            return 1, k
    if i2 - ri >= 2:
        k = _join_match(other_keys[oj], ref_keys, ri, i2)
        if k is not None:
            return k, 1
    return None


def _wrap_repair(ref_keys, other_keys, other_content, i1, i2, j1, j2) -> list[Segment]:
    """Repair a ``replace`` opcode, resyncing after every genuine difference
    instead of giving up on the whole block.

    Two things turn a real, small difference into one giant dispute if left
    unhandled: (a) the runs wrap text differently -- one run keeps a whole
    paragraph/scorecard row on one line, another wraps it across several --
    which makes EVERY line's key differ even though the actual content
    mostly agrees; (b) once even one of those wrap-driven "differences"
    isn't resolved, difflib's own line-level match has no further equal
    anchors to find, so it lumps the rest of the block into one opcode.

    This walks the block position by position, matching wrap-joins (a) or
    exact lines (the common case) as it goes, and -- only at a genuine
    content difference (b) -- searches a bounded window for the next point
    both sides agree again, confining the dispute to just the lines between
    here and there. Falls back to the previous whole-block-vs-give-up
    behavior when nothing in the window resyncs (rare; e.g. truly scrambled
    OCR for a whole section).
    """
    ref_block = ref_keys[i1:i2]
    other_block = other_keys[j1:j2]
    if " ".join(ref_block) == " ".join(other_block):
        return [Segment("equal", (i1, i2), other_content[j1:j2])]

    segs: list[Segment] = []
    ri, oj = i1, j1
    core_r0: int | None = None
    core_o0: int | None = None

    def flush_core(r_end: int, o_end: int) -> None:
        nonlocal core_r0, core_o0
        if core_r0 is None:
            return
        ref_left = r_end > core_r0
        other_left = o_end > core_o0
        if ref_left and other_left:
            segs.append(Segment("replace", (core_r0, r_end), other_content[core_o0:o_end]))
        elif ref_left:
            segs.append(Segment("ref_only", (core_r0, r_end), []))
        elif other_left:
            segs.append(Segment("other_only", (core_r0, core_r0), other_content[core_o0:o_end]))
        core_r0 = core_o0 = None

    while ri < i2 and oj < j2:
        m = _match_at(ref_keys, other_keys, ri, oj, i2, j2)
        if m is not None:
            rlen, olen = m
            flush_core(ri, oj)
            segs.append(Segment("equal", (ri, ri + rlen), other_content[oj:oj + olen]))
            ri += rlen
            oj += olen
            continue

        # Nearly-identical content is the same printed passage with an
        # OCR-level difference (a misread digit or surname) -- pair it as a
        # bounded replace instead of letting it open a growing core. k=1
        # pairs noisy scorecard lines 1:1; k>1 pairs one run's long
        # paragraph line against the other's wrapped-but-slightly-noisy
        # lines. Without pairing, dense noise leaves no clean resync anchor
        # anywhere nearby and whole scorecards/prose columns collapse into
        # one giant dispute.
        k = _fuzzy_join(ref_keys[ri], other_keys, oj, j2)
        if k is not None:
            flush_core(ri, oj)
            segs.append(Segment("replace", (ri, ri + 1), other_content[oj:oj + k]))
            ri += 1
            oj += k
            continue
        k = _fuzzy_join(other_keys[oj], ref_keys, ri, i2)
        if k is not None and k > 1:
            flush_core(ri, oj)
            segs.append(Segment("replace", (ri, ri + k), [other_content[oj]]))
            ri += k
            oj += 1
            continue

        # A genuine difference. Open (or extend) the pending dispute span and
        # search a bounded window for the next point both sides resync --
        # via an exact match OR a wrap-join, same test as above, so we can
        # resync back into wrapped rows on the far side of the difference,
        # not just an exact line match.
        if core_r0 is None:
            core_r0, core_o0 = ri, oj
        max_dr = i2 - ri - 1
        max_do = j2 - oj - 1
        anchor = None
        for dr in range(0, min(_RESYNC_WINDOW, max_dr) + 1):
            for do in range(0, min(_RESYNC_WINDOW, max_do) + 1):
                if dr == 0 and do == 0:
                    continue
                if _match_at(ref_keys, other_keys, ri + dr, oj + do, i2, j2) is not None:
                    anchor = (dr, do)
                    break
            if anchor:
                break
        if anchor is None:
            # Nothing resyncs in range -- close out the rest of the block as
            # one final dispute, same as the old give-up behavior.
            ri, oj = i2, j2
            break
        dr, do = anchor
        ri += dr
        oj += do

    flush_core(ri, oj)
    if ri < i2:
        segs.append(Segment("ref_only", (ri, i2), []))
    if oj < j2:
        segs.append(Segment("other_only", (ri, ri), other_content[oj:j2]))
    return segs


# ── Section-order canonicalization ───────────────────────────────────────────

# A match header: an all-caps-ish line containing " v " / " v. " (e.g.
# "HIGH WYCOMBE v. MR. E. STEVENS' XI."). No lowercase before the separator.
_SECTION_HDR = re.compile(r"^[^a-z]+\sv\.?\s")
_SECTION_MATCH_THRESHOLD = 0.6


def _is_section_header(key: str) -> bool:
    return bool(_SECTION_HDR.match(key)) and len(key) < 90


def _split_sections(content: list[str]) -> list[tuple[int, int, str]]:
    """Split content lines into (start, end, header_key) sections at match headers."""
    keys = [normalize_line(l) for l in content]
    starts = [i for i, k in enumerate(keys) if _is_section_header(k)]
    if not starts:
        return [(0, len(content), "")]
    secs: list[tuple[int, int, str]] = []
    if starts[0] > 0:
        secs.append((0, starts[0], ""))
    bounds = starts + [len(content)]
    for a, b in zip(bounds, bounds[1:]):
        secs.append((a, b, keys[a]))
    return secs


def _reorder_sections(ref_content: list[str], other_content: list[str]) -> tuple[list[str], bool]:
    """Reorder ``other_content``'s sections to the reference's section order.

    These are scrapbook pages of pasted newspaper cuttings, and different
    models read the collage in different orders -- the same matches appear in
    both runs but transposed. Line-level alignment cannot bridge transposed
    blocks (difflib keeps the longest in-order subsequence; everything out of
    order becomes one giant dispute), so sections are matched by their
    "X v. Y" headers and the other run is re-sequenced to the reference's
    order before alignment. Unmatched sections stay next to the matched
    neighbor they originally followed. Returns (content, was_reordered).
    """
    ref_secs = _split_sections(ref_content)
    oth_secs = _split_sections(other_content)
    if len(ref_secs) < 2 or len(oth_secs) < 2:
        return other_content, False

    pairs = []
    for oi, (_, _, ok) in enumerate(oth_secs):
        if not ok:
            continue
        for rix, (_, _, rk) in enumerate(ref_secs):
            if not rk:
                continue
            ratio = difflib.SequenceMatcher(None, ok, rk).ratio()
            if ratio >= _SECTION_MATCH_THRESHOLD:
                pairs.append((ratio, oi, rix))
    pairs.sort(reverse=True)
    o2r: dict[int, int] = {}
    used_r: set[int] = set()
    for ratio, oi, rix in pairs:
        if oi in o2r or rix in used_r:
            continue
        o2r[oi] = rix
        used_r.add(rix)
    if len(o2r) < 2:
        return other_content, False

    sort_keys: list[float] = []
    last = -1.0
    for oi, sec in enumerate(oth_secs):
        if oi in o2r:
            last = float(o2r[oi])
            sort_keys.append(last)
        elif oi == 0 and sec[2] == "":
            sort_keys.append(-1.0)  # leading pre-header chunk stays first
        else:
            sort_keys.append(last + 0.5)  # unmatched: stay after original neighbor
    order = sorted(range(len(oth_secs)), key=lambda oi: sort_keys[oi])
    if order == list(range(len(oth_secs))):
        return other_content, False

    out: list[str] = []
    for oi in order:
        s, e, _ = oth_secs[oi]
        out.extend(other_content[s:e])
    return out, True


# ── Data model ────────────────────────────────────────────────────────────────


@dataclass
class Dispute:
    page: int
    dispute_id: int
    ref_line_start: int
    ref_line_end: int
    kind: str  # conflict | missing_line
    variants: dict[str, str]          # label -> raw text (reference included)
    chosen_lines: list[str]            # raw lines selected for output
    context_before: str = ""
    context_after: str = ""
    resolution: str = "conflict"      # unanimous|majority|conflict|referee|referee_novel|unresolved
    chosen_label: str = ""
    referee_reading: str = ""
    referee_unclear: bool = False
    confidence: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.dispute_id,
            "ref_line_start": self.ref_line_start,
            "ref_line_end": self.ref_line_end,
            "kind": self.kind,
            "resolution": self.resolution,
            "chosen": "\n".join(self.chosen_lines),
            "chosen_label": self.chosen_label,
            "variants": self.variants,
            "context_before": self.context_before,
            "context_after": self.context_after,
            "referee_reading": self.referee_reading,
            "referee_unclear": self.referee_unclear,
            "confidence": self.confidence,
        }


@dataclass
class ArithFlag:
    page: int
    line_index: int
    computed_sum: int
    printed_total: int

    def to_dict(self) -> dict:
        return {
            "page": self.page,
            "line_index": self.line_index,
            "computed_sum": self.computed_sum,
            "printed_total": self.printed_total,
        }


@dataclass
class PageReconciliation:
    page: int
    ref_label: str
    output_lines: list[str]
    disputes: list[Dispute]
    notes: list[str] = field(default_factory=list)
    stats: dict = field(default_factory=dict)
    arithmetic_flags: list[ArithFlag] = field(default_factory=list)
    # Internal: kept so output can be rebuilt after the referee runs.
    ref_content: list[str] = field(default_factory=list)
    ref_ornaments: list[tuple[int, str]] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "page": self.page,
            "ref_label": self.ref_label,
            "notes": self.notes,
            "stats": self.stats,
            "disputes": [d.to_dict() for d in self.disputes],
            "arithmetic_flags": [f.to_dict() for f in self.arithmetic_flags],
        }


# ── Reference election ───────────────────────────────────────────────────────


def elect_reference(texts_by_label: list[tuple[str, str]], default_label: str) -> str:
    """Pick the run that agrees best with the others as this page's reference.

    Which model deviates structurally (splits a two-column table, fuses two
    columns onto one line, reads the collage in a different order) varies
    page by page, and a deviant REFERENCE poisons every pairwise alignment
    at once -- no global "best model first" ordering fixes that. For each
    candidate, align every other run against it and score the mean fraction
    of its lines covered by equal segments; the outlier scores low against
    everyone and can never win. ``default_label`` (the first CLI dir) wins
    ties.
    """
    if len(texts_by_label) < 3:
        return default_label
    contents = {label: split_content_lines(text)[0] for label, text in texts_by_label}
    best_label, best_score = default_label, -1.0
    for label, ref_content in contents.items():
        if not ref_content:
            continue
        cover = 0.0
        for other_label, other_content in contents.items():
            if other_label == label:
                continue
            segs = align_to_reference(ref_content, other_content)
            eq = sum(s.ref_span[1] - s.ref_span[0] for s in segs if s.kind == "equal")
            cover += eq / len(ref_content)
        score = cover / (len(contents) - 1)
        if score > best_score + 1e-9 or (abs(score - best_score) <= 1e-9 and label == default_label):
            best_label, best_score = label, score
    return best_label


# ── Classification ────────────────────────────────────────────────────────────

# Sentinel for a run that is missing a line the reference has.
_ABSENT = ""


def _run_coverage(ref_content: list[str], other_content: list[str]):
    """Return per-run structures describing how ``other_content`` maps to ref.

    - ``seg_at[r]``: the Segment covering reference content index ``r`` (one of
      equal/replace/ref_only — these partition ref positions).
    - ``block_lines[seg_id]``: the other lines for that segment.
    - ``inserts[gap]``: other-only lines inserted before ref content index ``gap``.
    """
    segments = align_to_reference(ref_content, other_content)
    seg_at: dict[int, Segment] = {}
    block_lines: dict[int, list[str]] = {}
    inserts: dict[int, list[str]] = {}
    for k, seg in enumerate(segments):
        i1, i2 = seg.ref_span
        if seg.kind == "other_only":
            inserts.setdefault(i1, []).extend(seg.other_lines)
            continue
        block_lines[k] = seg.other_lines
        for r in range(i1, i2):
            seg_at[r] = seg
    return segments, seg_at, block_lines, inserts


def reconcile_page(
    page: int,
    ref_text: str,
    runs: list[tuple[str, str]],
    ref_label: str = "ref",
    garbage_min_chars: int = 200,
) -> PageReconciliation:
    """Reconcile one page. Pure function: no I/O.

    ``runs`` is a list of ``(label, other_text)`` for the non-reference runs
    that have this page. Garbage runs (``len < garbage_min_chars`` or char-level
    ``quick_ratio`` vs the reference ``< 0.5``) are dropped with a note. With no
    usable runs the reference is copied through (single-source). The default
    200-char floor is a per-page garbage threshold for real full-page OCR;
    callers unit-testing on short snippets may pass ``garbage_min_chars=0``.
    """
    ref_content, ref_ornaments = split_content_lines(ref_text)

    # Garbage guard: drop runs that look broken for this page.
    ref_block_key = normalize_block(ref_text)
    active_runs: list[tuple[str, str]] = []
    notes: list[str] = []
    for label, other_text in runs:
        if other_text is None:
            continue
        if len(other_text) < garbage_min_chars:
            notes.append(f"{label}: dropped (len < {garbage_min_chars})")
            continue
        ratio = difflib.SequenceMatcher(None, ref_block_key,
                                         normalize_block(other_text), autojunk=False).quick_ratio()
        if ratio < 0.5:
            notes.append(f"{label}: dropped (quick_ratio < 0.5)")
            continue
        active_runs.append((label, other_text))

    if not active_runs:
        notes.append("single-source (no usable runs); reference copied through")
        arith = arithmetic_flags(ref_content, page)
        return PageReconciliation(
            page=page,
            ref_label=ref_label,
            output_lines=list(ref_content),
            disputes=[],
            notes=notes,
            stats={"unanimous": 0, "majority": 0, "conflict": 0, "missing_line": 0,
                   "single_source": 1},
            arithmetic_flags=arith,
            ref_content=ref_content,
            ref_ornaments=ref_ornaments,
        )

    def _equal_cover(cov) -> int:
        return sum(1 for seg in cov[1].values() if seg.kind == "equal")

    coverages = []
    for label, other_text in active_runs:
        other_content = split_content_lines(other_text)[0]
        cov = _run_coverage(ref_content, other_content)
        reordered_content, reordered = _reorder_sections(ref_content, other_content)
        if reordered:
            # Header matching can misfire (misread headers pair the wrong
            # sections and scramble a run that was fine) -- keep the reorder
            # only when it demonstrably aligns MORE reference lines.
            cov2 = _run_coverage(ref_content, reordered_content)
            if _equal_cover(cov2) > _equal_cover(cov):
                cov = cov2
                notes.append(f"{label}: sections reordered to match reference order")
        coverages.append((label, cov))
    labels = [ref_label] + [label for label, _ in active_runs]
    n = len(ref_content)

    # stable[r] is True iff every run agrees with the reference at r (equal).
    stable = [True] * n
    for _, (segments, seg_at, _block_lines, _inserts) in coverages:
        for r in range(n):
            seg = seg_at.get(r)
            if seg is None or seg.kind != "equal":
                stable[r] = False

    # Group contiguous active nodes (ref positions that are not stable, plus
    # gaps with insertions from any run) into dispute regions.
    regions = _build_regions(n, stable, coverages)

    disputes: list[Dispute] = []
    stats = {"unanimous": 0, "majority": 0, "conflict": 0, "missing_line": 0,
             "single_source": 0}
    next_id = 1

    for r0, r1, gap_inserts in regions:
        # Gather each source's raw text for this region (ref + each active run).
        variants: dict[str, str] = {}
        # Reference text: the ref content lines over [r0, r1).
        ref_text_region = ref_content[r0:r1]
        variants[ref_label] = "\n".join(ref_text_region)

        run_texts: list[tuple[str, str]] = []
        for label, cov in coverages:
            segments, seg_at, block_lines, inserts = cov
            lines = _region_lines_for_run(r0, r1, ref_content, seg_at, block_lines)
            # Insertions from this run at gaps inside the region (leading/internal/trailing).
            for g, ins_lines in gap_inserts:
                if label in ins_lines:
                    pos = ins_lines[label]
                    if g == r0:
                        lines = pos + lines
                    else:
                        lines = lines + pos
            text = "\n".join(lines)
            variants[label] = text
            run_texts.append((label, text))

        # Classify by normalized keys.
        keys = [(label, normalize_block(text)) for label, text in variants.items()]
        key_counts: dict[str, list[str]] = {}
        for label, key in keys:
            key_counts.setdefault(key, []).append(label)

        is_insertion_only = (r0 == r1)
        context_before = "\n".join(ref_content[max(0, r0 - 2):r0])
        context_after = "\n".join(ref_content[r1:min(n, r1 + 2)])

        if is_insertion_only:
            # Both runs insert matching keys at this gap → accept (majority insert).
            # One run inserts → conflict (missing_line).
            non_empty = [k for k, ls in key_counts.items() if k]
            kind = "missing_line"
            if len(non_empty) == 1 and len(key_counts[non_empty[0]]) >= 2:
                # Both runs inserted the same line (2-of-3 with ref absent).
                majority_label = key_counts[non_empty[0]][0]
                chosen_lines = _variant_raw_lines(variants, majority_label)
                resolution = "majority"
                stats["majority"] += 1
                kind = "insert"
            else:
                majority_label = ref_label
                chosen_lines = ref_text_region  # empty for a pure insertion
                resolution = "conflict"
                stats["missing_line"] += 1
        elif len(key_counts) == 1:
            # Unanimous (all sources, including ref, agree).
            resolution = "unanimous"
            chosen_lines = ref_text_region
            majority_label = ref_label
            stats["unanimous"] += 1
            kind = "conflict"  # placeholder; unanimous means no real dispute
        else:
            # Find a clear plurality: a key held by strictly more runs than any
            # other key. A tie for the top count (e.g. a genuine 2-2 split
            # across a 4-run ensemble) is NOT a majority -- with only 2-3 runs
            # "the first key with >=2 supporters" was always a real majority
            # over the remaining 1, but that stops being true at 4+ runs, where
            # two distinct readings can each hold exactly half the votes.
            counts_by_key = {key: len(ls) for key, ls in key_counts.items()}
            top_count = max(counts_by_key.values())
            top_keys = [key for key, count in counts_by_key.items() if count == top_count]
            if top_count >= 2 and len(top_keys) == 1:
                majority_key = top_keys[0]
                majority_label = key_counts[majority_key][0]
                chosen_lines = _variant_raw_lines(variants, majority_label)
                resolution = "majority"
                stats["majority"] += 1
                kind = "conflict"
            else:
                # No clear plurality (a tie for the top count, or every run
                # disagrees uniquely) → referee.
                majority_label = ref_label
                chosen_lines = ref_text_region  # placeholder; referee may overwrite
                resolution = "conflict"
                stats["conflict"] += 1
                kind = "conflict"

        # Emit a Dispute for everything that isn't unanimous. Majority disputes
        # are logged (resolution="majority") but never re-adjudicated; conflicts
        # and missing_line disputes go to the referee.
        if resolution != "unanimous":
            disputes.append(Dispute(
                page=page,
                dispute_id=next_id,
                ref_line_start=r0,
                ref_line_end=r1,
                kind=kind,
                variants=variants,
                chosen_lines=chosen_lines,
                context_before=context_before,
                context_after=context_after,
                resolution=resolution,
                chosen_label=majority_label,
            ))
            next_id += 1

    output_lines = build_output(ref_content, ref_ornaments, disputes)
    arith = arithmetic_flags(ref_content, page)
    return PageReconciliation(
        page=page,
        ref_label=ref_label,
        output_lines=output_lines,
        disputes=disputes,
        notes=notes,
        stats=stats,
        arithmetic_flags=arith,
        ref_content=ref_content,
        ref_ornaments=ref_ornaments,
    )


def _variant_raw_lines(variants: dict[str, str], label: str) -> list[str]:
    text = variants.get(label, "")
    return text.split("\n") if text else []


def _region_lines_for_run(r0, r1, ref_content, seg_at, block_lines) -> list[str]:
    """The raw lines a run contributes over ref content [r0, r1).

    Equal spans contribute the reference text (the run agrees there); replace
    spans contribute the run's whole other-line block (once); ref_only spans
    contribute nothing (the run is missing those lines).
    """
    lines: list[str] = []
    seen: set[int] = set()
    for r in range(r0, r1):
        seg = seg_at.get(r)
        if seg is None:
            lines.append(ref_content[r])
            continue
        if seg.kind == "equal":
            lines.append(ref_content[r])
        elif seg.kind == "replace":
            seg_id = id(seg)
            if seg_id not in seen:
                seen.add(seg_id)
                lines.extend(seg.other_lines)
        # ref_only: contribute nothing.
    return lines


def _build_regions(n, stable, coverages):
    """Group disagreements into ``(r0, r1, gap_inserts)`` regions.

    A ref position is active when not stable. A gap (before content index g) is
    active when any run inserts there. Contiguous active nodes group into a
    region, but the region is CUT at any boundary that no run's multi-line
    non-equal segment spans -- on dense scorecard pages nearly every line has
    some run disagreeing, and without cutting, whole scorecards merge into one
    giant dispute that votes (and referees) as a single unit. Per-line regions
    instead let a line where only one run misread a digit resolve as an
    ordinary 3-1 majority. A boundary inside one run's multi-line replace/
    ref_only segment can't be cut (there is no way to attribute that run's
    block lines to either side), and a gap insert glues its two neighbors.

    Each active gap belongs to exactly ONE region (tracked via ``consumed``):
    previously a trailing gap was folded into the region ending at it and then
    revisited as its own insertion-only region, double-counting the inserted
    lines in two disputes.
    """
    # Collect inserts per run per gap. coverages entries are (label, coverage)
    # where coverage = (segments, seg_at, block_lines, inserts).
    gap_insert_map: dict[int, dict[str, list[str]]] = {}
    for label, cov in coverages:
        for g, lines in cov[3].items():
            gap_insert_map.setdefault(g, {})[label] = lines

    def cuttable(r: int) -> bool:
        """Can the boundary between positions r-1 and r be a region edge?"""
        if r in gap_insert_map:
            return False  # an insertion sits on this boundary; keep it glued
        for _, cov in coverages:
            seg = cov[1].get(r - 1)
            if seg is not None and seg is cov[1].get(r) and seg.kind != "equal":
                return False
        return True

    regions: list[tuple[int, int, list[tuple[int, dict[str, list[str]]]]]] = []
    consumed_gaps: set[int] = set()
    r = 0
    while r <= n:
        active_gap = r in gap_insert_map and r not in consumed_gaps
        active_ref = r < n and not stable[r]
        if not (active_gap or active_ref):
            r += 1
            continue
        r0 = r
        region_gaps: list[tuple[int, dict[str, list[str]]]] = []
        if active_gap:
            region_gaps.append((r, gap_insert_map[r]))
            consumed_gaps.add(r)
        if not active_ref:
            # Insertion-only region at gap r (ref r is stable or out of range).
            regions.append((r, r, region_gaps))
            r += 1
            continue
        # Consume ref positions until a stable position or a cuttable boundary.
        j = r + 1
        while j < n and not stable[j] and not cuttable(j):
            j += 1
        r1 = j
        # Internal + trailing gaps within (r0, r1] are part of the region.
        for g in range(r0 + 1, r1 + 1):
            if g in gap_insert_map and g not in consumed_gaps:
                region_gaps.append((g, gap_insert_map[g]))
                consumed_gaps.add(g)
        regions.append((r0, r1, region_gaps))
        r = r1
    return regions


def build_output(
    ref_content: list[str],
    ref_ornaments: list[tuple[int, str]],
    disputes: list[Dispute],
) -> list[str]:
    """Reconstruct output lines: ref content + chosen dispute text + ornaments.

    Ornaments from the reference run are re-interleaved at their original
    content-index boundaries. Content regions in a dispute emit the dispute's
    chosen lines in place of the reference lines they cover.
    """
    ornaments_before: dict[int, list[str]] = {}
    for idx, raw in ref_ornaments:
        ornaments_before.setdefault(idx, []).append(raw)

    # Regions with ref content (r1 > r0) are emitted at r0, skipping to r1.
    regions_by_start: dict[int, Dispute] = {}
    # Pure-insertion regions (r1 == r0) emit at their gap.
    insertions_at: dict[int, list[str]] = {}
    for d in disputes:
        if d.ref_line_end > d.ref_line_start:
            regions_by_start[d.ref_line_start] = d
        else:
            insertions_at.setdefault(d.ref_line_start, []).extend(d.chosen_lines)

    out: list[str] = []
    n = len(ref_content)
    r = 0
    while r <= n:
        out.extend(ornaments_before.get(r, []))
        out.extend(insertions_at.get(r, []))
        if r < n:
            d = regions_by_start.get(r)
            if d is not None:
                out.extend(d.chosen_lines)
                r = d.ref_line_end
            else:
                out.append(ref_content[r])
                r += 1
        else:
            break
    return out


def rebuild_output(rec: PageReconciliation) -> None:
    """Recompute ``rec.output_lines`` after a referee has updated disputes."""
    rec.output_lines = build_output(rec.ref_content, rec.ref_ornaments, rec.disputes)


# ── Arithmetic attention-flags ────────────────────────────────────────────────

_SCORE_LINE = re.compile(r".+\s\d+$")        # "... b Oats 9" but not a bare "9"
_EXTRAS = re.compile(r"^extras\b", re.IGNORECASE)
_TOTAL = re.compile(r"^(?:total\s+)?\d+$", re.IGNORECASE)
_TRAILING_INT = re.compile(r"(-?\d+)\s*$")


def _trailing_int(line: str) -> int | None:
    m = _TRAILING_INT.search(line)
    return int(m.group(1)) if m else None


def arithmetic_flags(lines: list[str], page: int = 0) -> list[ArithFlag]:
    """Detect innings blocks whose printed total disagrees with the score sum.

    An innings block is ≥6 consecutive score-pattern lines that include an
    Extras line, followed by a total line within 2 lines (ornaments allowed in
    between). The sum of the scores (Extras included) is compared with the
    printed total; a mismatch emits an :class:`ArithFlag`. This is the only
    detector for correlated same-family errors (e.g. both Geminis misreading the
    same digit). It never alters text and never triggers the referee in v1.
    """
    norm = [normalize_line(l) for l in lines]
    n = len(norm)
    flags: list[ArithFlag] = []
    i = 0
    while i < n:
        if not (_SCORE_LINE.fullmatch(norm[i]) or _EXTRAS.match(norm[i])):
            i += 1
            continue
        # Gather the consecutive score/extras block (skip ornament/blank lines within it).
        j = i
        score_vals: list[int] = []
        has_extras = False
        last_score = i
        while j < n:
            ln = norm[j]
            if _EXTRAS.match(ln):
                has_extras = True
                v = _trailing_int(ln)
                if v is not None:
                    score_vals.append(v)
                last_score = j
                j += 1
            elif _SCORE_LINE.fullmatch(ln):
                v = _trailing_int(ln)
                if v is not None:
                    score_vals.append(v)
                last_score = j
                j += 1
            elif ln == "":
                j += 1
            else:
                break
        if has_extras and len(score_vals) >= 6:
            # Find a total line within 2 lines after the last score (j..j+2),
            # skipping blank/ornament lines.
            total: int | None = None
            total_idx = None
            for k in range(j, min(j + 3, n)):
                if _TOTAL.fullmatch(norm[k]):
                    total = int(_trailing_int(norm[k]))
                    total_idx = k
                    break
            if total is not None and total != sum(score_vals):
                flags.append(ArithFlag(page, total_idx if total_idx is not None else j,
                                       sum(score_vals), total))
        i = max(j, i + 1)
    return flags


# ── Referee ───────────────────────────────────────────────────────────────────

REFEREE_EXTRA = (
    "\n\nYou are now adjudicating disputes between several OCR transcriptions of "
    "the SAME page. For each dispute, transcribe exactly what is PRINTED in the "
    "image for that passage — even if the arithmetic looks wrong (compositor "
    "errors are real). If a word is illegible, write [unclear]. Your reading need "
    "NOT match any of the offered versions. If a dispute asks about a line that "
    "is not actually printed in the image, respond with the single word ABSENT."
)

REFEREE_SCHEMA_INSTRUCTION = (
    '\nReturn ONLY a JSON object of the form: '
    '{"disputes": [{"id": 1, "reading": "...", "confidence": "high"}]}. '
    "Use the dispute id from each prompt. confidence is one of high|medium|low."
)


def build_referee_prompt(page: int, disputes: list[Dispute],
                          season: str = config.SEASON) -> tuple[str, str]:
    """Build (system_prompt, user_prompt) batching every dispute for one page.

    Variants are labeled neutrally as Version 1/2/3 — never model names — with
    two reference context lines on each side of each dispute.
    """
    system = transcribe.SYSTEM_PROMPT + REFEREE_EXTRA
    lines = [
        f"This is page {page} from the Tony Webb minor counties collection of "
        f"cricket newspaper cuttings ({season}). Several OCR engines transcribed "
        f"this page and disagreed on the passages below. For each dispute, read "
        f"the corresponding region of the image and transcribe exactly what is "
        f"printed there.",
        "",
    ]
    for d in disputes:
        lines.append(f"=== Dispute {d.dispute_id} ===")
        if d.context_before:
            lines.append(f"Context before (2 lines): {d.context_before}")
        for idx, (label, text) in enumerate(d.variants.items(), start=1):
            display = text if text else "(nothing — this version has no line here)"
            lines.append(f"Version {idx}: {display}")
        if d.context_after:
            lines.append(f"Context after (2 lines): {d.context_after}")
        lines.append("")
    lines.append(REFEREE_SCHEMA_INSTRUCTION)
    return system, "\n".join(lines)


def call_referee(model, page: int, image_bytes: bytes, media_type: str,
                 disputes: list[Dispute], season: str = config.SEASON):
    """One vision call resolving all of a page's disputes. Returns (items, raw, error).

    ``items`` is the parsed ``disputes`` list (possibly empty / partial). The
    raw response is returned even on failure for logging. Missing ids /
    unparseable entries degrade to ``unresolved`` upstream — never fail the page.
    """
    system, user = build_referee_prompt(page, disputes, season=season)
    attachment = llm.Attachment(content=image_bytes, type=media_type)

    def fn():
        resp = model.prompt(
            user, attachments=[attachment], system=system, **no_thinking_kwargs(model)
        )
        raw = resp.text().strip()
        parsed = parse_json_object(raw)
        items = parsed.get("disputes", [])
        if not isinstance(items, list):
            items = []
        return items, raw

    return call_with_retry(fn, attempts=config.RETRY_ATTEMPTS)


def apply_referee(disputes: list[Dispute], items, ref_label: str = "ref") -> None:
    """Apply referee verdicts to disputes, in place.

    Majority/unanimous disputes are never re-adjudicated. For each conflict/
    missing_line dispute: a verdict that key-matches a variant adopts that
    variant's raw text (``referee``); a novel non-empty reading adopts the
    referee's text (``referee_novel``); ``[unclear]`` / missing id / ABSENT leaves
    it ``unresolved`` with the reference reading retained.
    """
    by_id: dict[int, dict] = {}
    for it in items or []:
        if isinstance(it, dict) and isinstance(it.get("id"), int):
            by_id[it["id"]] = it

    for d in disputes:
        if d.resolution in ("unanimous", "majority"):
            continue
        item = by_id.get(d.dispute_id)
        if item is None:
            d.resolution = "unresolved"
            d.chosen_lines = d.variants.get(ref_label, "").split("\n") if d.variants.get(ref_label) else []
            continue
        reading = (item.get("reading") or "").strip()
        d.referee_reading = reading
        d.confidence = str(item.get("confidence", "")).strip()

        if not reading or reading.upper() == "ABSENT":
            d.resolution = "unresolved"
            d.chosen_lines = d.variants.get(ref_label, "").split("\n") if d.variants.get(ref_label) else []
            continue
        if "[unclear]" in reading:
            d.resolution = "unresolved"
            d.referee_unclear = True
            d.chosen_lines = d.variants.get(ref_label, "").split("\n") if d.variants.get(ref_label) else []
            continue

        norm_reading = normalize_block(reading)
        matched_label = None
        for label, text in d.variants.items():
            if normalize_block(text) == norm_reading:
                matched_label = label
                break
        if matched_label is not None:
            d.resolution = "referee"
            d.chosen_label = matched_label
            d.chosen_lines = _variant_raw_lines(d.variants, matched_label)
        else:
            d.resolution = "referee_novel"
            d.chosen_label = "referee"
            d.chosen_lines = reading.split("\n")


# ── Report ────────────────────────────────────────────────────────────────────


def build_report(conflicts_path: Path) -> str:
    """Rebuild the Markdown report in full from the JSONL (latest record per page)."""
    records: dict[int, dict] = {}
    if conflicts_path.exists():
        for line in conflicts_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(rec, dict) and "page" in rec:
                records[rec["page"]] = rec

    pages = sorted(records)
    total_unresolved = 0
    total_novel = 0
    total_flags = 0
    unresolved_rows: list[str] = []
    novel_rows: list[str] = []
    flag_rows: list[str] = []
    note_rows: list[str] = []

    for page in pages:
        rec = records[page]
        for d in rec.get("disputes", []):
            if d.get("resolution") == "unresolved":
                total_unresolved += 1
                unresolved_rows.append(
                    f"| {page} | {d.get('id')} | {d.get('ref_line_start')} | "
                    f"{_md_escape(_chosen_preview(d))} |"
                )
            if d.get("resolution") == "referee_novel":
                total_novel += 1
                novel_rows.append(
                    f"| {page} | {d.get('id')} | {d.get('ref_line_start')} | "
                    f"{_md_escape(d.get('referee_reading', ''))} |"
                )
        for f in rec.get("arithmetic_flags", []):
            total_flags += 1
            flag_rows.append(
                f"| {page} | {f.get('line_index')} | {f.get('computed_sum')} | "
                f"{f.get('printed_total')} |"
            )
        for note in rec.get("notes", []):
            note_rows.append(f"- page {page}: {note}")

    lines = [
        "# Reconcile report",
        "",
        f"Pages reconciled: {len(pages)}.",
        f"Unresolved disputes: {total_unresolved}.",
        f"Referee-novel readings: {total_novel}.",
        f"Arithmetic flags: {total_flags}.",
        "",
        "## Unresolved disputes",
        "",
        "| Page | ID | Ref line | Chosen (reference retained) |",
        "|------|----|----------|------------------------------|",
    ]
    lines.extend(unresolved_rows or ["| — | — | — | — |"])
    lines += ["", "## Referee-novel readings", "",
              "| Page | ID | Ref line | Referee reading |",
              "|------|----|----------|-----------------|"]
    lines.extend(novel_rows or ["| — | — | — | — |"])
    lines += ["", "## Arithmetic flags", "",
              "Sum of scores ≠ printed total — compositor error OR misread digit. "
              "Check the scan.",
              "",
              "| Page | Line | Computed sum | Printed total |",
              "|------|------|--------------|----------------|"]
    lines.extend(flag_rows or ["| — | — | — | — |"])
    if note_rows:
        lines += ["", "## Page notes", ""] + note_rows
    lines.append("")
    return "\n".join(lines)


def _md_escape(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ⏎ ")


def _chosen_preview(d: dict) -> str:
    chosen = d.get("chosen", "")
    if chosen:
        return chosen
    variants = d.get("variants", {})
    ref = next(iter(variants.values()), "") if variants else ""
    return ref


# ── CLI ───────────────────────────────────────────────────────────────────────


def register_parser(subparsers):
    p = subparsers.add_parser(
        "reconcile",
        help="Reconcile 2+ OCR runs; auto-accept agreements, referee disagreements.",
    )
    p.add_argument("run_dirs", nargs="+",
                   help="2 or more run directories; FIRST is the reference (best model first).")
    config.add_collection_arg(p)
    p.add_argument("--output-dir", default="reconciled/",
                   help="Directory for reconciled per-page .txt files.")
    p.add_argument("--referee-model", default=config.DEFAULT_RECONCILE_MODEL,
                   help="Vision model used to adjudicate disputes (not an ensemble member).")
    p.add_argument("--no-referee", action="store_true",
                   help="Majority/flag only; do not call a referee model.")
    p.add_argument("--pages", default=None,
                   help="Comma-separated page numbers or ranges, e.g. '1,5-10'.")
    p.add_argument("--local-dir", default=None,
                   help="Directory of local JPG images (local-first fetch).")
    p.add_argument("--report", default="reconcile_report.md",
                   help="Path for the regenerated Markdown report.")
    p.add_argument("--conflicts", default="reconcile_conflicts.jsonl",
                   help="Append-only JSONL of per-page disputes/stats.")
    p.add_argument("--dry-run", action="store_true",
                   help="Align + classify + stats only; no writes, no referee.")
    p.set_defaults(func=run)
    return p


def run(args) -> None:
    if len(args.run_dirs) < 2:
        raise SystemExit("reconcile needs at least 2 run directories (first = reference).")

    collection = config.Collection.from_arg(args.collection)

    page_filter = parse_page_spec(args.pages)
    dry_run = args.dry_run
    no_referee = args.no_referee

    # Load pages per directory.
    run_label_pages: list[tuple[str, dict[int, str]]] = []
    for d in args.run_dirs:
        path = Path(d)
        if not path.is_dir():
            raise SystemExit(f"Not a directory: {d}")
        pages = dict(load_pages_from_dir(path))
        run_label_pages.append((path.name, pages))

    ref_label, ref_pages = run_label_pages[0]
    others = run_label_pages[1:]

    # Warn if the referee shares a family prefix with a run dir.
    if not no_referee:
        ref_id = args.referee_model.lower()
        for label, _ in others:
            prefix = label.split("-")[0].split(":")[0].lower()
            if prefix and prefix in ref_id:
                print(f"  ⚠ Referee model {args.referee_model!r} shares family prefix "
                      f"with run {label!r}; consider a different family for honest "
                      f"adjudication.", file=sys.stderr)

    all_pages = set(ref_pages)
    for _, p in others:
        all_pages |= set(p)
    if page_filter:
        all_pages &= page_filter

    out_dir = Path(args.output_dir)
    conflicts_path = Path(args.conflicts)
    report_path = Path(args.report)
    if not dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)

    raw_log = None
    if not no_referee:
        raw_log = RawResponseLog(
            Path(f"raw_responses_reconcile_{config.safe_model_name(args.referee_model)}.jsonl")
        )

    model = None
    if not no_referee:
        from .pipeline import resolve_model
        model = resolve_model(args.referee_model)

    session = new_session()
    local_dir = Path(args.local_dir) if args.local_dir else None

    for page in sorted(all_pages):
        if page_filter and page not in page_filter:
            continue
        out_file = out_dir / collection.page_filename(page)
        if out_file.exists() and out_file.stat().st_size > 0:
            print(f"Skipping page {page} (already reconciled)")
            continue

        avail = [(label, p[page]) for label, p in run_label_pages if page in p]
        if not avail:
            print(f"  ⚠ Page {page}: no run has it; skipping")
            continue
        # Which model deviates structurally varies page by page; elect the
        # run that agrees best with the others as this page's reference
        # (the first CLI dir wins ties). This also covers pages the first
        # dir is missing entirely.
        ref_label_page = elect_reference(avail, avail[0][0])
        ref_text = dict(avail)[ref_label_page]
        runs = [(label, text) for label, text in avail if label != ref_label_page]
        note_prefix = []
        if ref_label_page != ref_label:
            note_prefix = [f"reference: {ref_label_page} (elected over {ref_label})"]

        print(f"Processing page {page}")
        rec = reconcile_page(page, ref_text, runs, ref_label=ref_label_page)
        rec.notes = note_prefix + rec.notes

        # Referee: only if there are undecided conflicts.
        undecided = [d for d in rec.disputes if d.resolution in ("conflict", "missing_line")]
        if undecided and not no_referee and not dry_run:
            try:
                image_bytes, media_type = fetch_image(page, local_dir=local_dir, session=session,
                                                        collection=collection)
            except Exception as e:
                print(f"  ⚠ Could not fetch image for page {page}: {e}; leaving disputes unresolved",
                      file=sys.stderr)
                image_bytes = None
            if image_bytes is not None:
                items, raw, error = call_referee(model, page, image_bytes, media_type, undecided,
                                                  season=collection.season)
                if raw_log is not None:
                    raw_log.write(page, raw, model=args.referee_model)
                if error:
                    print(f"  ⚠ Referee error on page {page}: {error}", file=sys.stderr)
                apply_referee(rec.disputes, items, ref_label=ref_label_page)
                rebuild_output(rec)
                time.sleep(config.RATE_LIMIT_DELAY)

        # Refresh stats from final resolutions.
        rec.stats = _final_stats(rec.disputes)

        if dry_run:
            n_disputes = len(rec.disputes)
            n_flags = len(rec.arithmetic_flags)
            print(f"  page {page}: {n_disputes} disputes, {n_flags} arith flags "
                  f"({rec.stats})")
            continue

        out_file.write_text("\n".join(rec.output_lines), encoding="utf-8")
        with conflicts_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec.to_dict(), ensure_ascii=False) + "\n")
        n_undone = sum(1 for d in rec.disputes if d.resolution == "unresolved")
        print(f"  ✓ page {page}: {len(rec.disputes)} disputes "
              f"({n_undone} unresolved), {len(rec.arithmetic_flags)} arith flags")

    if not dry_run:
        report_path.write_text(build_report(conflicts_path), encoding="utf-8")
        print(f"\nReconciled text: {out_dir}/")
        print(f"Conflicts JSONL: {conflicts_path}")
        print(f"Report: {report_path}")
    else:
        print(f"\nDry run complete ({len(all_pages)} pages considered); no files written.")


def _final_stats(disputes: list[Dispute]) -> dict:
    stats: dict[str, int] = {}
    for d in disputes:
        stats[d.resolution] = stats.get(d.resolution, 0) + 1
        if d.kind == "missing_line":
            stats["missing_line"] = stats.get("missing_line", 0) + 1
    return stats