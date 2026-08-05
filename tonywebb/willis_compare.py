"""Build side-by-side comparison rows for a match_index_<model>.csv against
match_index_willis.csv. See willis_compare.run_willis_compare() for the HTML
generation this feeds into.
"""

from __future__ import annotations

from . import evaluate


def _row(page: int, status: str, content_type: str, willis: dict | None, model: dict | None, similarity: float | None) -> dict:
    """Single source of truth for the row schema -- Task 3's HTML/JS template
    depends key-for-key on this shape, so every branch below builds rows
    through here rather than duplicating the dict literal.
    """
    return {
        "page": page,
        "status": status,
        "content_type": content_type,
        "willis": willis,
        "model": model,
        "similarity": similarity,
    }


def build_comparison_rows(
    truth_rows: list[evaluate.IndexRow],
    model_rows: list[evaluate.IndexRow],
    fuzzy_threshold: float = 0.8,
) -> list[dict]:
    """Return a flat list of {page, status, content_type, willis, model, similarity}.

    status is one of:
      - "matched": Willis and the model agree (exact or fuzzy key match)
      - "missed": in Willis, no model match, on a page Willis covers
      - "surplus": in the model, no Willis match, on a page Willis covers
      - "unindexed": in the model, on a page outside Willis's covered range
        (no ground truth exists there, so this is not a "surplus"/false-positive
        claim — just unreviewed)
    """
    result = evaluate.evaluate(truth_rows, model_rows, fuzzy_threshold=fuzzy_threshold)
    covered = set(result.pages_covered)

    rows: list[dict] = []
    for pair in result.matched:
        rows.append(_row(
            page=pair.truth.page,
            status="matched",
            content_type=pair.truth.content_type,
            willis={"matchup": pair.truth.matchup, "date": pair.truth.date},
            model={"matchup": pair.model.matchup, "date": pair.model.date},
            similarity=pair.similarity,
        ))
    for r in result.missed:
        rows.append(_row(
            page=r.page,
            status="missed",
            content_type=r.content_type,
            willis={"matchup": r.matchup, "date": r.date},
            model=None,
            similarity=None,
        ))
    for r in result.surplus:
        rows.append(_row(
            page=r.page,
            status="surplus",
            content_type=r.content_type,
            willis=None,
            model={"matchup": r.matchup, "date": r.date},
            similarity=None,
        ))
    for r in model_rows:
        if r.page not in covered:
            rows.append(_row(
                page=r.page,
                status="unindexed",
                content_type=r.content_type,
                willis=None,
                model={"matchup": r.matchup, "date": r.date},
                similarity=None,
            ))

    # Primary sort by page; secondary sort by matchup text (from whichever
    # side has a row) so ordering within a page is stable and deterministic.
    rows.sort(key=lambda r: (r["page"], (r["willis"] or r["model"] or {}).get("matchup", "")))
    return rows
