"""Shared orchestration for the index-producing extraction commands.

extract_matches.py, index_stats.py, and index_scorecards.py all follow the
same shape: load pages -> per-page prompt -> parse {"entries": [...]} ->
normalize/dedup -> append a 6-column CSV + raw-response JSONL, with
CSV-based resume and cross-page duplicate reporting. This module holds that
shared machinery so each command only supplies its own prompt and parser.
"""

from __future__ import annotations

import csv
import logging
from pathlib import Path
from typing import Callable

from . import config
from .llm_common import no_thinking_kwargs
from .normalize import (
    ClubRegistry,
    detect_publication_date,
    matchup_key,
    normalize_date,
    normalize_matchup,
    normalize_title,
    relative_dates,
    resolve_date_phrase,
    symmetric_matchup_key,
    title_key,
)
from .pipeline import RawResponseLog, load_pages, parse_page_spec, resolve_model, run_pages

logger = logging.getLogger(__name__)

VALID_CONTENT_TYPES = config.VALID_CONTENT_TYPES

# Max page gap over which a detected publication date may carry forward to a
# page whose own header OCR failed to parse. Covers a multi-page edition
# without bleeding across a large gap into a different edition.
_PUB_DATE_CARRY_GAP = 3

STYLE_RULES = """STYLE RULES (apply to all titles):
  * Do not use periods/full stops in abbreviations: "Mr" not "Mr.",
    "Dr" not "Dr.", "Rev" not "Rev.", "St" not "St.", "MCC" not "M.C.C."
  * Write initials without periods and with a space before the surname:
    "MJK Smith" not "M.J.K. Smith".
  * Use Roman numerals: "XII" not "12" or "Twelve", "XI" not "Eleven".
  * Use "Second XI" not "2nd XI".
  * Use full university names: "Oxford University" not "Oxford Uni".
  * Preserve apostrophes in names: "King's" not "Kings".
  * Do not use brackets, commas, or full stops in titles.
  * Use county names as used today: "Somerset" not "Somersetshire".
  * Drop trailing "CC" or "Cricket Club" from team names.
  * Use title case."""

KEY_1895_DATES = """KEY 1895 DATES (for resolving historical date references):
- Whit-Monday (Bank Holiday): 27 May 1895
- Whit-Tuesday: 28 May 1895
- Good Friday: 12 April 1895
- Easter Monday: 15 April 1895
- August Bank Holiday: 5 August 1895
When the text says "Whit-Monday", "Bank Holiday", etc., use these dates.
The PUBLICATION DATE is NOT the match date — matches are typically
reported days after they were played."""


def build_date_context(page_text: str) -> str:
    """Publication-date detection + weekday-resolution block shared by every prompt."""
    pub = detect_publication_date(page_text)
    if pub:
        rel = relative_dates(pub)
        rel_lines = "\n".join(f"  {wd.capitalize()}: {iso}" for wd, iso in rel.items())
        return (
            f"PUBLICATION DATE: {pub.isoformat()} ({pub.strftime('%A')})\n"
            "When the text says 'on Friday', 'last Wednesday', etc., resolve "
            "those weekdays to the most recent occurrence prior to the "
            "publication date. For this page that means:\n"
            f"{rel_lines}\n"
        )
    return (
        "PUBLICATION DATE: unknown — extract dates only when the text "
        "states them explicitly. Do not guess.\n"
    )


# ── Post-processing (shared by every index command) ─────────────────────────

def normalize_and_dedup(
    entries: list[dict],
    page_num: int,
    allowed_types: set[str] | None = None,
    registry: ClubRegistry | None = None,
    publication_date=None,
) -> tuple[list[dict], list[dict]]:
    """Normalize title/date and drop duplicates within a page.

    Returns (kept, discarded). Each discarded item records the reason and the
    original entry so dropped data stays visible in the raw-responses log.

    If an entry carries a "date_phrase" (a verbatim date reference like "on
    Whit-Monday" or "Saturday last week"), that phrase is resolved
    deterministically via resolve_date_phrase() and PREFERRED over the
    model's own "date" field when it resolves -- models are unreliable at
    doing the weekday-relative-to-publication-date arithmetic themselves,
    even when handed a precomputed lookup table, so deterministic resolution
    in Python is strictly more trustworthy when it succeeds. Falls back to
    the model's own "date" field when the phrase is absent or unresolvable.
    """
    seen: set[tuple[str, str, str]] = set()
    out: list[dict] = []
    discarded: list[dict] = []

    def discard(reason: str, entry) -> None:
        discarded.append({
            "reason": reason,
            "entry": entry if isinstance(entry, dict) else str(entry),
        })

    for entry in entries:
        if not isinstance(entry, dict):
            discard("not a dict", entry)
            continue
        content_type = (entry.get("content_type") or "match information").strip().lower()
        if content_type not in VALID_CONTENT_TYPES:
            content_type = "match information"
        if allowed_types and content_type not in allowed_types:
            discard("filtered content type", entry)
            continue

        raw_title = entry.get("matchup", "") or entry.get("title", "")
        resolved = resolve_date_phrase(entry.get("date_phrase"), publication_date)
        date = resolved if resolved else normalize_date(entry.get("date", ""))
        # Date convention: full YYYYMMDD, YYYYMM00 for known month / unknown
        # day, YYYY0000 for year-only. The whole collection is 1895, so the
        # year is always known -- a date is never empty. Floor anything the
        # model left blank (or that failed to resolve) to the season year so
        # every row carries a date that downstream matching/consensus can key
        # on. See normalize_date() for the encoding rules.
        if not date:
            date = f"{config.SEASON}0000"

        # Weekend-results convention: a Friday or Saturday paper's match
        # reports are for the previous Saturday (e.g. a Friday 16 Aug paper
        # reports Saturday 10 Aug matches). Match bodies often state no
        # explicit date -- the human index (Willis) applies this convention
        # and the model can't, since it's told not to compute dates. Apply it
        # here, but ONLY for "match information" whose date is still a
        # placeholder (day unknown -- the string ends in "00", i.e. YYYYMM00 or
        # YYYY0000) after phrase resolution and the year-floor fallback: a
        # specific date resolved from the text always wins, and non-match
        # content (season statistics, team info) is left alone. Fri/Sat-only
        # limits the heuristic to actual weekend-results papers.
        if (
            content_type == "match information"
            and publication_date is not None
            and publication_date.weekday() in (4, 5)  # Friday, Saturday
            and date.endswith("00")
        ):
            sat_iso = relative_dates(publication_date).get("saturday")
            if sat_iso:
                date = sat_iso.replace("-", "")

        if content_type == "match information":
            title = normalize_matchup(raw_title, registry=registry)
            if not title:
                discard("empty title", entry)
                continue
            key = matchup_key(title)
        else:
            title = normalize_title(raw_title)
            if not title:
                discard("empty title", entry)
                continue
            key = title_key(title)

        dedup = (key, date, content_type)
        if dedup in seen:
            discard("duplicate", entry)
            continue
        seen.add(dedup)
        out.append(
            {
                "matchup": title,
                "page": page_num,
                "date": date,
                "content_type": content_type,
                "collection": config.COLLECTION_NAME,
                "pages": 1,
            }
        )
    return out, discarded


def publication_date_for_page(
    page_num: int,
    page_text: str,
    last_pub_date,
    last_pub_page: int | None,
) -> tuple:
    """Publication date for a page, carrying the last detected date forward.

    A multi-page paper prints its date header once (on the first page); OCR
    can garble or drop it on continuation pages (e.g. p51 "FRIDAY 16 AUGUST
    1895" but p52 "FRIDAY AUGUST 1895" with the day lost). When detection
    fails on a page that closely follows a dated one, reuse the last date so
    the whole edition keeps its date context. Bounded to
    _PUB_DATE_CARRY_GAP pages so it can't bleed across a large gap into a
    different edition.

    Returns (pub_date_to_use, new_last_pub_date, new_last_pub_page) so callers
    can thread the state through pages in document order.
    """
    detected = detect_publication_date(page_text)
    if detected is not None:
        return detected, detected, page_num
    if last_pub_date is not None and (
        last_pub_page is None
        or 0 < page_num - last_pub_page <= _PUB_DATE_CARRY_GAP
    ):
        return last_pub_date, last_pub_date, last_pub_page
    return None, last_pub_date, last_pub_page


def _row_key(matchup: str, date: str, content_type: str) -> tuple[str, str, str]:
    # Order-insensitive for matches, unlike the exact matchup_key() used for
    # WITHIN-page dedup in normalize_and_dedup(). Cross-page duplicates in
    # this collection are frequently two different newspapers' independent
    # write-ups of the same match, which routinely name the teams in the
    # opposite order (prose word order vs. house style) -- the same reason
    # evaluate/consensus/promote-reviewed use symmetric_matchup_key() for
    # their own cross-source matching. The date is still part of this key,
    # so a genuine same-day-reversed-order rematch (e.g. First XI vs Second
    # XI fixtures between the same two clubs) is the only real edge case
    # this accepts, same tradeoff already made everywhere else.
    key = symmetric_matchup_key(matchup) if content_type == "match information" else title_key(matchup)
    return (key, date, content_type)


def track_cross_page(global_seen: dict, rows: list[dict]) -> list[dict]:
    """Track entries across pages; return rows already seen on an earlier page.

    Cross-page duplicates are reported, not dropped — the same fixture can
    legitimately appear in consecutive issues, so a human decides.
    """
    dupes: list[dict] = []
    for row in rows:
        key = _row_key(row["matchup"], row["date"], row["content_type"])
        first_page = global_seen.get(key)
        if first_page is not None and first_page != row["page"]:
            dupes.append({**row, "first_page": first_page})
        else:
            global_seen.setdefault(key, row["page"])
    return dupes


def recompute_pages_column(csv_path: Path) -> int:
    """Rewrite the "pages" column of an index CSV to the true count of distinct
    pages each (matchup, date, content_type) entry appears on across the whole
    file -- not just consecutive pages, any two.

    Every row sharing a key gets the same count (flagged, not merged: each
    page's row stays in the CSV so nothing is silently dropped). Returns the
    number of rows whose value changed.
    """
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    pages_by_key: dict[tuple[str, str, str], set[int]] = {}
    for row in rows:
        content_type = (row.get("content_type") or "match information").strip().lower()
        key = _row_key(row.get("matchup", ""), row.get("date", ""), content_type)
        try:
            page = int((row.get("page") or "").strip())
        except (ValueError, TypeError):
            continue
        pages_by_key.setdefault(key, set()).add(page)

    changed = 0
    for row in rows:
        content_type = (row.get("content_type") or "match information").strip().lower()
        key = _row_key(row.get("matchup", ""), row.get("date", ""), content_type)
        count = str(len(pages_by_key.get(key, set())) or 1)
        if row.get("pages") != count:
            changed += 1
        row["pages"] = count

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return changed


# ── LLM extraction ───────────────────────────────────────────────────────────

def extract_entries(
    model,
    page_num: int,
    page_text: str,
    *,
    prompt_builder: Callable[[int, str], str],
    system_prompt: str,
    parse_response: Callable[[str], list[dict]],
) -> tuple[list[dict], str]:
    """Returns (entries, raw_response_text). Raises JSONExtractError on bad shape."""
    prompt = prompt_builder(page_num, page_text)
    response = model.prompt(prompt, system=system_prompt, **no_thinking_kwargs(model))
    raw = response.text()
    return parse_response(raw), raw


# ── Shared CLI runner ────────────────────────────────────────────────────────

def run_index_extraction(
    args,
    *,
    prompt_builder: Callable[[int, str], str],
    system_prompt: str,
    parse_response: Callable[[str], list[dict]],
    csv_prefix: str,
    raw_log_prefix: str,
    allowed_types: set[str] | None = None,
) -> None:
    """Shared body for every index-producing command's `run(args)`.

    args must provide: input, model, output, pages. allowed_types restricts
    which content_type values are kept -- fixed for the focused commands
    (index-stats, index-scorecards), or CLI-driven for extract-matches.
    """
    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"Input not found: {input_path}")

    pages = load_pages(input_path)

    safe_model = config.safe_model_name(args.model)
    csv_path = Path(args.output) if args.output else Path(f"{csv_prefix}_{safe_model}.csv")
    raw_log_path = Path(f"{raw_log_prefix}_{safe_model}.jsonl")
    raw_log = RawResponseLog(raw_log_path)

    page_filter = parse_page_spec(args.pages)

    print(f"Input : {input_path}")
    print(f"Model : {args.model}")
    print(f"Output: {csv_path}")
    print(f"Raw   : {raw_log_path}")

    if page_filter:
        pages = [(n, t) for n, t in pages if n in page_filter]
        print(f"Pages : {sorted(page_filter)}")
    else:
        print(f"Pages : {len(pages)} total")

    model = resolve_model(args.model)
    registry = ClubRegistry(config.CLUBS_CSV_PATH) if Path(config.CLUBS_CSV_PATH).exists() else None

    # Load already-processed pages from existing CSV to allow resuming;
    # also seed cross-page duplicate tracking from prior rows.
    processed_pages: set[int] = set()
    global_seen: dict[tuple[str, str, str], int] = {}
    if csv_path.exists():
        try:
            with csv_path.open(newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        page = int(row["page"])
                    except (KeyError, ValueError, TypeError):
                        continue
                    processed_pages.add(page)
                    key = _row_key(
                        row.get("matchup", ""),
                        row.get("date", ""),
                        (row.get("content_type") or "match information").strip().lower(),
                    )
                    global_seen.setdefault(key, page)
        except (OSError, csv.Error) as e:
            logger.warning("Could not read existing %s for resume: %s", csv_path, e)
    if processed_pages:
        print(f"Resuming: {len(processed_pages)} page(s) already in {csv_path}")

    if not csv_path.exists():
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["matchup", "page", "date", "content_type", "collection", "pages"])

    total_entries = 0
    total_errors = 0
    cross_page_dupes: list[dict] = []
    page_text_by_num = dict(pages)

    # Carry-forward state for the publication date: a multi-page paper prints
    # its date header once (on the first page), and OCR can garble or drop it
    # on continuation pages (e.g. p51 "FRIDAY 16 AUGUST 1895" but p52 "FRIDAY
    # AUGUST 1895" with the day lost). When detection fails on a page that
    # closely follows a dated one, we reuse the last detected date so the
    # whole edition keeps its date context instead of falling back to a
    # year/month guess. Bounded to _PUB_DATE_CARRY_GAP pages so it can't bleed
    # across a large gap into a different edition.
    last_pub_date = None
    last_pub_page = None

    def extract_fn(page_num: int, page_text: str) -> tuple[list[dict], str]:
        return extract_entries(
            model, page_num, page_text,
            prompt_builder=prompt_builder, system_prompt=system_prompt, parse_response=parse_response,
        )

    def on_result(page_result) -> None:
        nonlocal total_entries, total_errors, last_pub_date, last_pub_page
        entries = page_result.items
        raw = page_result.raw
        error = page_result.error

        pub_date, last_pub_date, last_pub_page = publication_date_for_page(
            page_result.page,
            page_text_by_num.get(page_result.page, ""),
            last_pub_date,
            last_pub_page,
        )
        normalized, discarded = normalize_and_dedup(
            entries or [], page_result.page, allowed_types=allowed_types, registry=registry,
            publication_date=pub_date,
        )
        page_dupes = track_cross_page(global_seen, normalized)
        cross_page_dupes.extend(page_dupes)

        if normalized:
            with csv_path.open("a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                for row in normalized:
                    writer.writerow([
                        row["matchup"],
                        row["page"],
                        row["date"],
                        row["content_type"],
                        row["collection"],
                        row["pages"],
                    ])
            total_entries += len(normalized)

        raw_log.write(
            page_result.page,
            raw,
            parsed_count=len(entries or []),
            kept_count=len(normalized),
            discarded=discarded,
            error=error,
        )

        if error:
            total_errors += 1
            print(f"ERROR: {error}")
        else:
            note = f" ({len(page_dupes)} also on earlier page)" if page_dupes else ""
            print((f"{len(normalized)} entry(ies)" if normalized else "no entries") + note)

    run_pages(pages, processed_pages, extract_fn, on_result)

    print(f"\nDone. {total_entries} entries written to {csv_path}; {total_errors} page error(s).")
    if cross_page_dupes:
        print(f"{len(cross_page_dupes)} entry(ies) also appear on an earlier page (kept; review manually):")
        for d in cross_page_dupes:
            print(f"  page {d['page']}: {d['matchup']} [{d['date']}] first seen on page {d['first_page']}")

    if csv_path.exists():
        changed = recompute_pages_column(csv_path)
        if changed:
            print(f"Updated 'pages' count for {changed} row(s) spanning more than one page.")
