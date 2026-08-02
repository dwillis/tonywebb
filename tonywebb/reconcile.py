"""Multi-run OCR reconciliation with an image referee.

Runs 2-3 transcription models over the same collection, auto-accepts lines
where they agree, and asks a vision model to read the original page image
where they disagree. Line-level alignment plus targeted adjudication turns
"review 247 pages" into "review a few flagged lines per page."

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


def _wrap_repair(ref_keys, other_keys, other_content, i1, i2, j1, j2) -> list[Segment]:
    """Repair a ``replace`` opcode for the wrap-style difference between runs.

    If joining the ref-block keys and the other-block keys yields the same
    string, the runs agree (one wraps, one does not) → one equal segment.
    Otherwise peel equal prefix and suffix lines off into their own equal
    segments and leave the unsplittable core as a single replace (or, if one
    side is fully peeled away, a ref_only/other_only).
    """
    ref_block = ref_keys[i1:i2]
    other_block = other_keys[j1:j2]
    if " ".join(ref_block) == " ".join(other_block):
        return [Segment("equal", (i1, i2), other_content[j1:j2])]

    segs: list[Segment] = []
    # Greedy equal-prefix peel.
    ri, oj = i1, j1
    while ri < i2 and oj < j2 and ref_keys[ri] == other_keys[oj]:
        segs.append(Segment("equal", (ri, ri + 1), [other_content[oj]]))
        ri += 1
        oj += 1
    # Greedy equal-suffix peel (from the end, not crossing the prefix).
    suffix: list[Segment] = []
    ri2, oj2 = i2 - 1, j2 - 1
    while ri2 >= ri and oj2 >= oj and ref_keys[ri2] == other_keys[oj2]:
        suffix.append(Segment("equal", (ri2, ri2 + 1), [other_content[oj2]]))
        ri2 -= 1
        oj2 -= 1
    suffix.reverse()

    ref_left = ri2 >= ri      # reference lines remain in the core
    other_left = oj2 >= oj    # other lines remain in the core
    if ref_left and other_left:
        segs.append(Segment("replace", (ri, ri2 + 1), other_content[oj:oj2 + 1]))
    elif ref_left:
        segs.append(Segment("ref_only", (ri, ri2 + 1), []))
    elif other_left:
        segs.append(Segment("other_only", (ri, ri), other_content[oj:oj2 + 1]))
    # If neither side remains, both were fully peeled (all-equal core) — nothing to add.
    segs.extend(suffix)
    return segs


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

    coverages = [
        (label, _run_coverage(ref_content, split_content_lines(other_text)[0]))
        for label, other_text in active_runs
    ]
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
            non_ref_keys = [k for k, ls in key_counts.items() if ref_label not in ls]
            # Find a 2-of-3 majority.
            majority_key = None
            for key, ls in key_counts.items():
                if len(ls) >= 2:
                    majority_key = key
                    break
            if majority_key is not None:
                majority_label = key_counts[majority_key][0]
                chosen_lines = _variant_raw_lines(variants, majority_label)
                resolution = "majority"
                stats["majority"] += 1
                kind = "conflict"
            else:
                # Three-way disagreement → referee.
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
    """Group contiguous disagreements into ``(r0, r1, gap_inserts)`` regions.

    A ref position is active when not stable. A gap (before content index g) is
    active when any run inserts there. Maximal contiguous active-node groups
    become regions. ``gap_inserts`` is a list of ``(gap, {label: lines})`` for
    active gaps inside the region (so the caller can fold insertions into
    variants and output).
    """
    # Collect inserts per run per gap. coverages entries are (label, coverage)
    # where coverage = (segments, seg_at, block_lines, inserts).
    gap_has_insert = set()
    gap_insert_map: dict[int, dict[str, list[str]]] = {}
    for label, cov in coverages:
        inserts = cov[3]
        for g, lines in inserts.items():
            gap_has_insert.add(g)
            gap_insert_map.setdefault(g, {})[label] = lines

    regions: list[tuple[int, int, list[tuple[int, dict[str, list[str]]]]]] = []
    r = 0
    while r <= n:
        active_gap = r in gap_has_insert
        active_ref = r < n and not stable[r]
        if not (active_gap or active_ref):
            r += 1
            continue
        # Start a region. r0 is the first ref index covered (or r if insertion-only).
        # Walk forward consuming contiguous active nodes.
        r0 = r
        region_gaps: list[tuple[int, dict[str, list[str]]]] = []
        # Leading gap insertion at r0 (if ref r0 is active it still belongs to region).
        if active_gap:
            region_gaps.append((r, gap_insert_map[r]))
        # Consume ref positions and internal/trailing gaps until a break.
        r1 = r
        j = r
        if active_ref:
            while j < n and not stable[j]:
                j += 1
            r1 = j
            # Internal + trailing gaps within (r0, r1] are part of the region.
            for g in range(r0 + 1, r1 + 1):
                if g in gap_has_insert:
                    region_gaps.append((g, gap_insert_map[g]))
            # A trailing gap at r1 (just past the last active ref line) is contiguous too.
            if r1 in gap_has_insert and (r1, gap_insert_map[r1]) not in region_gaps:
                region_gaps.append((r1, gap_insert_map[r1]))
            regions.append((r0, r1, region_gaps))
            r = r1
        else:
            # Insertion-only region at gap r (ref r is stable or out of range).
            regions.append((r, r, region_gaps))
            r += 1
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


def build_referee_prompt(page: int, disputes: list[Dispute]) -> tuple[str, str]:
    """Build (system_prompt, user_prompt) batching every dispute for one page.

    Variants are labeled neutrally as Version 1/2/3 — never model names — with
    two reference context lines on each side of each dispute.
    """
    system = transcribe.SYSTEM_PROMPT + REFEREE_EXTRA
    lines = [
        f"This is page {page} from the Tony Webb minor counties collection of "
        f"cricket newspaper cuttings (1895). Several OCR engines transcribed "
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
                 disputes: list[Dispute]):
    """One vision call resolving all of a page's disputes. Returns (items, raw, error).

    ``items`` is the parsed ``disputes`` list (possibly empty / partial). The
    raw response is returned even on failure for logging. Missing ids /
    unparseable entries degrade to ``unresolved`` upstream — never fail the page.
    """
    system, user = build_referee_prompt(page, disputes)
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
        help="Reconcile 2-3 OCR runs; auto-accept agreements, referee disagreements.",
    )
    p.add_argument("run_dirs", nargs="+",
                   help="2-3 run directories; FIRST is the reference (best model first).")
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
        out_file = out_dir / f"tw_newspaper_cuttings_1895_{page}.txt"
        if out_file.exists() and out_file.stat().st_size > 0:
            print(f"Skipping page {page} (already reconciled)")
            continue

        ref_text = ref_pages.get(page)
        if ref_text is None:
            # Reference missing for this page: use the longest available other as a
            # fallback spine and note it. (Reference is expected to be complete.)
            fallback = max(
                ((label, p[page]) for label, p in others if page in p),
                key=lambda x: len(x[1]), default=None,
            )
            if fallback is None:
                print(f"  ⚠ Page {page}: no run has it; skipping")
                continue
            ref_text = fallback[1]
            ref_label_page = fallback[0]
            note_prefix = [f"reference missing; used {fallback[0]} as reference"]
        else:
            ref_label_page = ref_label
            note_prefix = []

        runs = [(label, p[page]) for label, p in others if page in p]

        print(f"Processing page {page}")
        rec = reconcile_page(page, ref_text, runs, ref_label=ref_label_page)
        rec.notes = note_prefix + rec.notes

        # Referee: only if there are undecided conflicts.
        undecided = [d for d in rec.disputes if d.resolution in ("conflict", "missing_line")]
        if undecided and not no_referee and not dry_run:
            try:
                image_bytes, media_type = fetch_image(page, local_dir=local_dir, session=session)
            except Exception as e:
                print(f"  ⚠ Could not fetch image for page {page}: {e}; leaving disputes unresolved",
                      file=sys.stderr)
                image_bytes = None
            if image_bytes is not None:
                items, raw, error = call_referee(model, page, image_bytes, media_type, undecided)
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