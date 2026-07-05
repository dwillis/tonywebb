"""Scorecard JSON schema: response parsing and field normalization.

The scorecard shape is tolerant of Victorian-newspaper irregularity: fields are
nullable rather than guessed, dismissal strings are canonicalized to a small
enum, and every batting/bowling line keeps its verbatim source line ("raw")
as a human-review escape hatch.
"""

from __future__ import annotations

import re

from ..llm_common import JSONExtractError, parse_json_object
from ..normalize import ClubRegistry, normalize_date, normalize_matchup, normalize_title

VALID_DISMISSALS = {
    "b", "c", "c and b", "st", "run out", "lbw", "hit wicket",
    "retired", "absent", "not out", "did not bat", "unknown",
}

_DISMISSAL_ALIASES = {
    "b": "b", "bowled": "b",
    "c": "c", "caught": "c", "ct": "c",
    "c and b": "c and b", "caught and bowled": "c and b", "c & b": "c and b",
    "st": "st", "stumped": "st",
    "run out": "run out", "ran out": "run out", "run-out": "run out",
    "lbw": "lbw", "leg before wicket": "lbw", "l b w": "lbw",
    "hit wicket": "hit wicket", "hit-wicket": "hit wicket",
    "retired": "retired", "retired hurt": "retired", "retired not out": "retired",
    "absent": "absent",
    "not out": "not out",
    "did not bat": "did not bat", "dnb": "did not bat",
}

_NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
}

_ESQ_RE = re.compile(r",?\s*esq\.?\s*$", re.IGNORECASE)


def parse_response(raw: str) -> list[dict]:
    """Parse the LLM response, tolerating the 'matches' key alias."""
    parsed = parse_json_object(raw)
    entries = parsed.get("scorecards")
    if entries is None:
        entries = parsed.get("matches")
    if entries is None:
        raise JSONExtractError("missing 'scorecards' (or 'matches') key")
    if not isinstance(entries, list):
        raise JSONExtractError("'scorecards' is not a list")
    return entries


def canonical_dismissal(raw: str | None) -> str:
    if not raw:
        return "unknown"
    s = re.sub(r"\s+", " ", str(raw).strip().lower()).rstrip(".")
    return _DISMISSAL_ALIASES.get(s, "unknown")


def normalize_person_name(raw: str | None) -> str | None:
    """'Dr. Stuart' -> 'Dr Stuart'; 'W. Moore, Esq.' -> 'W Moore'."""
    if not raw:
        return None
    s = str(raw).strip()
    if not s:
        return None
    s = _ESQ_RE.sub("", s)
    s = s.replace(".", "").replace(",", "")
    s = re.sub(r"\s+", " ", s).strip()
    return s or None


def _clean_int(value) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value) if value.is_integer() else None
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return None
        try:
            return int(s)
        except ValueError:
            return None
    return None


def _clean_int_or_word(value) -> int | None:
    """Like _clean_int, but also accepts spelled-out numbers up to twelve.

    Handles prose bowling figures such as "took five wickets for 12 runs"
    in case the model copies the word through rather than converting it.
    """
    n = _clean_int(value)
    if n is not None:
        return n
    if isinstance(value, str):
        word = value.strip().lower()
        if word in _NUMBER_WORDS:
            return _NUMBER_WORDS[word]
    return None


def normalize_batting_line(entry: dict) -> dict | None:
    if not isinstance(entry, dict):
        return None
    batter = normalize_person_name(entry.get("batter"))
    if not batter:
        return None
    dismissal = canonical_dismissal(entry.get("dismissal"))
    not_out = bool(entry.get("not_out")) or dismissal == "not out"
    if not_out:
        dismissal = "not out"
    return {
        "batter": batter,
        "dismissal": dismissal,
        "bowler": normalize_person_name(entry.get("bowler")),
        "fielder": normalize_person_name(entry.get("fielder")),
        "runs": _clean_int(entry.get("runs")),
        "not_out": not_out,
        "raw": (entry.get("raw") or "").strip(),
    }


def normalize_bowling_line(entry: dict) -> dict | None:
    if not isinstance(entry, dict):
        return None
    bowler = normalize_person_name(entry.get("bowler"))
    if not bowler:
        return None
    overs = entry.get("overs")
    overs = str(overs).strip() if overs not in (None, "") else None
    source = entry.get("source") if entry.get("source") in ("table", "prose") else "table"
    return {
        "bowler": bowler,
        "overs": overs,
        "maidens": _clean_int_or_word(entry.get("maidens")),
        "runs": _clean_int_or_word(entry.get("runs")),
        "wickets": _clean_int_or_word(entry.get("wickets")),
        "source": source,
        "raw": (entry.get("raw") or "").strip(),
    }


def _infer_all_out(batting: list[dict]) -> bool:
    if not batting:
        return False
    dismissed = sum(1 for b in batting if not b["not_out"] and b["dismissal"] != "did not bat")
    return dismissed >= 10


def normalize_innings(entry: dict, registry: ClubRegistry | None = None) -> dict | None:
    if not isinstance(entry, dict):
        return None
    team = normalize_title(entry.get("team") or "")
    if not team:
        return None
    if registry:
        resolved = registry.resolve(team)
        if resolved:
            team = resolved

    batting = [b for b in (normalize_batting_line(b) for b in (entry.get("batting") or [])) if b]
    did_not_bat = [n for n in (normalize_person_name(n) for n in (entry.get("did_not_bat") or [])) if n]
    bowling = [b for b in (normalize_bowling_line(b) for b in (entry.get("bowling") or [])) if b]

    if not batting and not did_not_bat:
        return None

    all_out = entry.get("all_out")
    all_out = bool(all_out) if all_out is not None else _infer_all_out(batting)

    return {
        "team": team,
        "order": entry.get("order"),
        "batting": batting,
        "did_not_bat": did_not_bat,
        "extras": _clean_int(entry.get("extras")),
        "total": _clean_int(entry.get("total")),
        "total_qualifier": (entry.get("total_qualifier") or "").strip() or None,
        "all_out": all_out,
        "bowling": bowling,
    }


def normalize_scorecard(entry: dict, page_num: int, registry: ClubRegistry | None = None) -> dict | None:
    """Normalize one LLM-extracted scorecard entry. Returns None to discard."""
    if not isinstance(entry, dict):
        return None
    matchup_raw = entry.get("matchup") or entry.get("title") or ""
    matchup = normalize_matchup(matchup_raw, registry=registry)
    if not matchup:
        return None

    innings = [i for i in (normalize_innings(i, registry=registry) for i in (entry.get("innings") or [])) if i]
    if not innings:
        return None

    return {
        "match_key": {
            "page": page_num,
            "matchup": matchup,
            "date": normalize_date(entry.get("date", "")),
        },
        "venue": (entry.get("venue") or "").strip() or None,
        "result": (entry.get("result") or "").strip() or None,
        "innings": innings,
    }
