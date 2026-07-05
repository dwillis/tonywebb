"""Consistency checks and confidence scoring for normalized scorecards."""

from __future__ import annotations

import re
from difflib import SequenceMatcher

from ..normalize import matchup_key

_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z' .-]*$")

# Dismissals that credit a specific bowler with taking the wicket.
_CREDITED_DISMISSALS = {"b", "c", "c and b", "st", "lbw", "hit wicket"}

# Must sum to 1.0.
WEIGHTS = {
    "totals": 0.40,
    "structure": 0.20,
    "names": 0.15,
    "bowler_wickets": 0.15,
    "index_link": 0.10,
}


def check_totals(innings: dict, tolerance: int = 0) -> dict:
    """Batting runs + extras vs the stated total. 'incomplete' (not 'mismatch')
    when a batting figure is missing -- that's a transcription gap, not an error."""
    total = innings.get("total")
    extras = innings.get("extras") or 0
    batting = innings.get("batting") or []
    runs = [b["runs"] for b in batting]
    if total is None or not runs or any(r is None for r in runs):
        return {"status": "incomplete", "stated": total, "computed": None, "delta": None}
    computed = sum(runs) + extras
    delta = computed - total
    return {
        "status": "ok" if abs(delta) <= tolerance else "mismatch",
        "stated": total,
        "computed": computed,
        "delta": delta,
    }


def check_bowler_wickets(innings: dict) -> list[dict]:
    """Cross-check stated bowling wickets against dismissals credited to that bowler.

    Soft signal: prose bowling figures often cover only one bowler, so a
    mismatch here is informative but not damning on its own.
    """
    credited: dict[str, int] = {}
    for b in innings.get("batting") or []:
        if b["dismissal"] in _CREDITED_DISMISSALS and b.get("bowler"):
            credited[b["bowler"]] = credited.get(b["bowler"], 0) + 1

    results = []
    for bl in innings.get("bowling") or []:
        stated = bl.get("wickets")
        if stated is None:
            continue
        got = credited.get(bl["bowler"], 0)
        results.append({"bowler": bl["bowler"], "credited": got, "stated": stated, "ok": got == stated})
    return results


def check_names(scorecard: dict) -> bool:
    for innings in scorecard.get("innings") or []:
        names = [b["batter"] for b in innings.get("batting") or []]
        names += [bl["bowler"] for bl in innings.get("bowling") or []]
        for n in names:
            if n and not _NAME_RE.match(n):
                return False
    return True


def check_structure(scorecard: dict) -> dict:
    innings = scorecard.get("innings") or []
    counts = [len(i.get("batting") or []) for i in innings]
    ok = 1 <= len(innings) <= 4 and all(c <= 12 for c in counts)
    return {"innings_count": len(innings), "batting_counts": counts, "ok": ok}


def link_to_index(scorecard: dict, index_rows_for_page: list[dict], threshold: float = 0.8) -> dict:
    """Link a scorecard to its match_index row on the same page.

    Exact matchup_key equality first, then best-match SequenceMatcher ratio.
    """
    mk = matchup_key(scorecard["match_key"]["matchup"])

    for row in index_rows_for_page:
        if matchup_key(row.get("matchup", "")) == mk:
            return {"matched": True, "index_matchup": row.get("matchup"), "match_kind": "exact", "similarity": 1.0}

    best_row = None
    best_sim = 0.0
    for row in index_rows_for_page:
        sim = SequenceMatcher(None, mk, matchup_key(row.get("matchup", ""))).ratio()
        if sim > best_sim:
            best_sim, best_row = sim, row

    if best_row is not None and best_sim >= threshold:
        return {
            "matched": True,
            "index_matchup": best_row.get("matchup"),
            "match_kind": "fuzzy",
            "similarity": round(best_sim, 3),
        }
    return {
        "matched": False,
        "index_matchup": None,
        "match_kind": "none",
        "similarity": round(best_sim, 3) if best_row is not None else 0.0,
    }


def score_confidence(checks: dict) -> tuple[float, list[str]]:
    flags: list[str] = []
    scores: dict[str, float] = {}

    total_scores = []
    for t in checks["totals"]:
        if t["status"] == "ok":
            total_scores.append(1.0)
        elif t["status"] == "incomplete":
            total_scores.append(0.5)
        else:
            total_scores.append(0.0)
    scores["totals"] = sum(total_scores) / len(total_scores) if total_scores else 0.0
    if any(t["status"] == "mismatch" for t in checks["totals"]):
        flags.append("total_mismatch")

    scores["structure"] = 1.0 if checks["structure"]["ok"] else 0.0
    if not checks["structure"]["ok"]:
        flags.append("bad_structure")

    scores["names"] = 1.0 if checks["names_ok"] else 0.0
    if not checks["names_ok"]:
        flags.append("suspect_names")

    bw = checks["bowler_wickets"]
    if bw:
        ok_count = sum(1 for c in bw if c["ok"])
        scores["bowler_wickets"] = ok_count / len(bw)
        if ok_count < len(bw):
            flags.append("bowler_wicket_mismatch")
    else:
        scores["bowler_wickets"] = 0.5  # nothing to check -- neutral, not penalized

    scores["index_link"] = 1.0 if checks["index_linked"] else 0.0
    if not checks["index_linked"]:
        flags.append("not_in_index")

    confidence = sum(WEIGHTS[k] * scores[k] for k in WEIGHTS)
    return round(confidence, 3), flags


def validate_scorecard(
    scorecard: dict,
    index_rows_for_page: list[dict] | None = None,
    sum_tolerance: int = 0,
    link_threshold: float = 0.8,
) -> dict:
    """Run all checks, then attach 'index_link' and 'validation' to the scorecard in place."""
    innings = scorecard.get("innings") or []
    totals = [check_totals(i, tolerance=sum_tolerance) for i in innings]
    bowler_wickets = [c for i in innings for c in check_bowler_wickets(i)]
    names_ok = check_names(scorecard)
    structure = check_structure(scorecard)
    index_link = link_to_index(scorecard, index_rows_for_page or [], threshold=link_threshold)

    checks = {
        "totals": totals,
        "bowler_wickets": bowler_wickets,
        "names_ok": names_ok,
        "structure": structure,
        "index_linked": index_link["matched"],
    }
    confidence, flags = score_confidence(checks)

    scorecard["index_link"] = index_link
    scorecard["validation"] = {"checks": checks, "confidence": confidence, "flags": flags}
    return scorecard
