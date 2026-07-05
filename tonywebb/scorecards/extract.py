"""extract-scorecards CLI command: LLM extraction + optional vision recheck pass."""

import csv
import json
import logging
from pathlib import Path

import llm

from .. import config
from ..images import fetch_image, new_session
from ..llm_common import JSONExtractError, no_thinking_kwargs, parse_json_object
from ..normalize import ClubRegistry
from ..pipeline import RawResponseLog, load_pages, parse_page_spec, resolve_model, run_pages
from . import prompts, schema, validate

logger = logging.getLogger(__name__)


def extract_scorecards_from_text(model, page_num: int, page_text: str) -> tuple[list[dict], str]:
    prompt = prompts.build_text_prompt(page_num, page_text)
    response = model.prompt(prompt, system=prompts.SYSTEM_PROMPT, **no_thinking_kwargs(model))
    raw = response.text()
    return schema.parse_response(raw), raw


def _load_index_rows(index_path: Path | None) -> dict[int, list[dict]]:
    """Return {page: [row, ...]} from a match_index CSV, or {} if none given."""
    by_page: dict[int, list[dict]] = {}
    if not index_path:
        return by_page
    if not index_path.exists():
        logger.warning("Index file not found: %s -- scorecards will not be linked", index_path)
        return by_page
    with index_path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                page = int(row.get("page", ""))
            except (TypeError, ValueError):
                continue
            by_page.setdefault(page, []).append(row)
    return by_page


def _club_registry() -> ClubRegistry | None:
    return ClubRegistry(config.CLUBS_CSV_PATH) if Path(config.CLUBS_CSV_PATH).exists() else None


# ── CLI ──────────────────────────────────────────────────────────────────────

def register_parser(subparsers):
    p = subparsers.add_parser(
        "extract-scorecards",
        help="Extract per-match batting/bowling scorecards from transcribed page text.",
    )
    p.add_argument("--input", "-i", default=config.DEFAULT_TEXT_INPUT)
    p.add_argument("--model", "-m", default=config.DEFAULT_SCORECARDS_MODEL)
    p.add_argument("--output", "-o", default=None)
    p.add_argument("--pages", default=None, help="Comma-separated page numbers or ranges, e.g. '1,3,5-10'")
    p.add_argument("--index", default=None, help="match_index_<model>.csv to link scorecards against.")
    p.add_argument("--sum-tolerance", type=int, default=0)
    p.add_argument("--link-threshold", type=float, default=0.8)

    p.add_argument("--recheck", action="store_true",
                    help="Re-run low-confidence scorecards against the page image with a vision model.")
    p.add_argument("--vision-model", default=config.DEFAULT_VISION_RECHECK_MODEL)
    p.add_argument("--local-dir", default=None, help="Directory of local JPG files for the recheck pass.")
    p.add_argument("--recheck-threshold", type=float, default=0.7)
    p.add_argument("--limit", type=int, default=None, help="Max scorecards to recheck in one run.")

    p.set_defaults(func=run)
    return p


def run(args) -> None:
    safe_model = config.safe_model_name(args.model)
    output_path = Path(args.output) if args.output else Path(f"scorecards_{safe_model}.json")

    if args.recheck:
        _run_recheck(args, output_path)
    else:
        _run_extract(args, output_path)


def _run_extract(args, output_path: Path) -> None:
    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"Input not found: {input_path}")

    pages = load_pages(input_path)
    page_filter = parse_page_spec(args.pages)
    if page_filter:
        pages = [(n, t) for n, t in pages if n in page_filter]

    index_by_page = _load_index_rows(Path(args.index) if args.index else None)
    registry = _club_registry()
    raw_log = RawResponseLog(Path(f"raw_responses_scorecards_{config.safe_model_name(args.model)}.jsonl"))

    print(f"Input : {input_path}")
    print(f"Model : {args.model}")
    print(f"Output: {output_path}")
    print(f"Pages : {sorted(page_filter) if page_filter else f'{len(pages)} total'}")
    if args.index:
        print(f"Index : {args.index} ({sum(len(v) for v in index_by_page.values())} rows)")

    model = resolve_model(args.model)

    processed_pages: set[int] = set()
    all_scorecards: list[dict] = []
    if output_path.exists():
        try:
            existing = json.loads(output_path.read_text(encoding="utf-8"))
            all_scorecards = existing.get("scorecards", [])
            processed_pages = set(existing.get("metadata", {}).get("pages_done", []))
            print(f"Resuming: {len(processed_pages)} page(s) already processed, "
                  f"{len(all_scorecards)} scorecard(s) loaded")
        except (OSError, json.JSONDecodeError, KeyError) as e:
            logger.warning("Could not read existing %s for resume: %s", output_path, e)

    total_added = 0
    total_errors = 0

    def extract_fn(page_num, page_text):
        return extract_scorecards_from_text(model, page_num, page_text)

    def write_output():
        output_path.write_text(
            json.dumps(
                {
                    "metadata": {
                        "collection": config.COLLECTION_NAME,
                        "season": config.SEASON,
                        "model": args.model,
                        "pages_processed": len(processed_pages),
                        "pages_done": sorted(processed_pages),
                        "total_scorecards": len(all_scorecards),
                    },
                    "scorecards": all_scorecards,
                },
                indent=2, ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    def on_result(page_result) -> None:
        nonlocal total_added, total_errors
        entries = page_result.result[0] if page_result.result else []
        raw = page_result.result[1] if page_result.result else ""
        error = page_result.error

        kept = []
        for entry in entries or []:
            card = schema.normalize_scorecard(entry, page_result.page, registry=registry)
            if card is None:
                continue
            validate.validate_scorecard(
                card,
                index_rows_for_page=index_by_page.get(page_result.page, []),
                sum_tolerance=args.sum_tolerance,
                link_threshold=args.link_threshold,
            )
            card["source"] = {"model": args.model, "pass": "text", "rechecked": False}
            kept.append(card)

        all_scorecards.extend(kept)
        total_added += len(kept)
        processed_pages.add(page_result.page)
        write_output()

        raw_log.write(
            page_result.page, raw,
            parsed_count=len(entries or []), kept_count=len(kept), error=error,
        )

        if error:
            total_errors += 1
            print(f"ERROR: {error}")
        else:
            flagged = sum(1 for c in kept if c["validation"]["confidence"] < args.recheck_threshold)
            note = f" ({flagged} flagged for recheck)" if flagged else ""
            print((f"{len(kept)} scorecard(s)" if kept else "no scorecards") + note)

    run_pages(pages, processed_pages, extract_fn, on_result)

    flagged_total = sum(
        1 for c in all_scorecards if c["validation"]["confidence"] < args.recheck_threshold
    )
    print(f"\nDone. {total_added} scorecard(s) added to {output_path}; {total_errors} page error(s).")
    print(f"{flagged_total} scorecard(s) below confidence {args.recheck_threshold} -- "
          f"run with --recheck to re-verify against page images.")


def _run_recheck(args, output_path: Path) -> None:
    if not output_path.exists():
        raise SystemExit(f"{output_path} does not exist -- run extract-scorecards first.")

    data = json.loads(output_path.read_text(encoding="utf-8"))
    all_scorecards = data.get("scorecards", [])

    candidates = [
        (i, c) for i, c in enumerate(all_scorecards)
        if c["validation"]["confidence"] < args.recheck_threshold
        and not c.get("source", {}).get("rechecked", False)
    ]
    if args.limit:
        candidates = candidates[: args.limit]

    print(f"{len(candidates)} scorecard(s) queued for vision recheck "
          f"(confidence < {args.recheck_threshold}) using {args.vision_model}")
    if not candidates:
        return

    local_dir = Path(args.local_dir) if args.local_dir else None
    index_by_page = _load_index_rows(Path(args.index) if args.index else None)
    registry = _club_registry()
    model = resolve_model(args.vision_model)
    session = new_session()
    raw_log = RawResponseLog(
        Path(f"raw_responses_scorecards_recheck_{config.safe_model_name(args.vision_model)}.jsonl")
    )

    improved = 0
    for i, card in candidates:
        page_num = card["match_key"]["page"]
        flags = card["validation"]["flags"]
        try:
            image_bytes, media_type = fetch_image(page_num, local_dir=local_dir, session=session)
        except Exception as e:
            print(f"  ✗ page {page_num}: could not fetch image: {e}")
            continue

        prompt = prompts.build_recheck_prompt(page_num, card, flags)
        attachment = llm.Attachment(content=image_bytes, type=media_type)
        try:
            response = model.prompt(
                prompt, attachments=[attachment], system=prompts.RECHECK_SYSTEM_PROMPT,
                **no_thinking_kwargs(model),
            )
            raw = response.text()
            parsed = parse_json_object(raw)
            corrected_entry = parsed.get("scorecard")
            if not isinstance(corrected_entry, dict):
                raise JSONExtractError("missing 'scorecard' object")
        except Exception as e:
            print(f"  ✗ page {page_num}: recheck failed: {e}")
            raw_log.write(page_num, "", error=str(e))
            continue

        new_card = schema.normalize_scorecard(corrected_entry, page_num, registry=registry)
        if new_card is None:
            print(f"  ✗ page {page_num}: recheck returned an unusable scorecard")
            continue
        validate.validate_scorecard(
            new_card,
            index_rows_for_page=index_by_page.get(page_num, []),
            sum_tolerance=args.sum_tolerance,
            link_threshold=args.link_threshold,
        )
        new_card["source"] = {"model": args.vision_model, "pass": "vision", "rechecked": True}

        old_confidence = card["validation"]["confidence"]
        new_confidence = new_card["validation"]["confidence"]
        raw_log.write(page_num, raw, old_confidence=old_confidence, new_confidence=new_confidence)

        if new_confidence > old_confidence:
            all_scorecards[i] = new_card
            improved += 1
            print(f"  ✓ page {page_num}: {old_confidence} -> {new_confidence}")
        else:
            card["source"]["rechecked"] = True  # don't re-queue it forever
            print(f"  = page {page_num}: no improvement ({old_confidence} -> {new_confidence}), kept original")

    output_path.write_text(
        json.dumps({**data, "scorecards": all_scorecards}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\nDone. {improved}/{len(candidates)} scorecard(s) improved and replaced.")

