"""Shared normalization for cricket match index entries.

Used by parser_matches.py (post-extraction cleanup), compare_matches.py
(comparison key), and build_browser.py (display key).
"""

from __future__ import annotations

import re
from datetime import date, timedelta

# Tokens preserved verbatim (case-sensitive) when title-casing matchups.
_PRESERVE = {
    "XI": "XI",
    "II": "II",
    "III": "III",
    "IV": "IV",
}

# Honorifics / abbreviations kept with a trailing dot.
_HONORIFICS = {"mr", "mrs", "st", "rev", "dr"}

# Initial-style tokens (e.g. "C.E.", "T.W.") detected by pattern instead.
_INITIALS_RE = re.compile(r"^(?:[A-Z]\.){1,4}$", re.IGNORECASE)

_MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11,
    "december": 12,
}

_WEEKDAYS = {
    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
    "friday": 4, "saturday": 5, "sunday": 6,
}


# ── Matchup normalization ────────────────────────────────────────────────────

def _title_token(tok: str) -> str:
    upper = tok.upper()
    if upper in _PRESERVE:
        return _PRESERVE[upper]
    if _INITIALS_RE.match(tok):
        return tok.upper()
    bare = tok.rstrip(".").lower()
    if bare in _HONORIFICS:
        return bare.capitalize() + "."
    # Words like "and", "of", "the" inside team names — keep title case for simplicity.
    return tok[:1].upper() + tok[1:].lower() if tok else tok


def _title_case_team(name: str) -> str:
    parts = re.split(r"(\s+|-)", name)  # keep hyphens / spaces
    return "".join(_title_token(p) if p.strip() and p != "-" else p for p in parts)


def _normalize_team(team: str) -> str:
    s = team.strip()
    # Drop trailing C.C. / Cricket Club
    s = re.sub(r"[,\s]+(?:C\.?\s*C\.?|Cricket\s+Club)\.?\s*$", "", s, flags=re.IGNORECASE)
    # G.S. → Grammar School (only as a standalone token)
    s = re.sub(r"\bG\.?\s*S\.?(?![A-Za-z])", "Grammar School", s, flags=re.IGNORECASE)
    # 2nd / 2ND → Second, 1st → First, 3rd → Third
    s = re.sub(r"\b1st\b", "First", s, flags=re.IGNORECASE)
    s = re.sub(r"\b2nd\b", "Second", s, flags=re.IGNORECASE)
    s = re.sub(r"\b3rd\b", "Third", s, flags=re.IGNORECASE)
    # "Eleven" / "ELEVEN" → "XI" (only when preceded by a word, e.g. "Second Eleven")
    s = re.sub(r"\bEleven\b", "XI", s, flags=re.IGNORECASE)
    # Collapse whitespace
    s = re.sub(r"\s+", " ", s).strip()
    # Strip surrounding punctuation
    s = s.strip(",;:")
    return _title_case_team(s)


def normalize_matchup(matchup: str) -> str:
    """Canonicalize a 'Team A v Team B' string. Returns '' for unparseable input."""
    if not matchup:
        return ""
    s = matchup.strip()
    # Normalize separator: "vs.", "vs", "versus", "V.", "V" → " v "
    s = re.sub(r"\s+(?:vs?\.?|versus|V\.?)\s+", " v ", s, flags=re.IGNORECASE)
    # Collapse whitespace
    s = re.sub(r"\s+", " ", s).strip()
    parts = re.split(r"\s+v\s+", s, maxsplit=1)
    if len(parts) != 2:
        # Fall back: best-effort cleanup of the whole string
        return _normalize_team(s)
    left, right = parts
    return f"{_normalize_team(left)} v {_normalize_team(right)}"


def matchup_key(matchup: str) -> str:
    """Lowercase, punctuation-stripped key for equality comparisons."""
    s = normalize_matchup(matchup).lower()
    s = s.replace(".", "").replace("'", "")
    return re.sub(r"\s+", " ", s).strip()


# ── Date normalization ───────────────────────────────────────────────────────

_DATE_RE = re.compile(r"^(\d{4})(\d{2})(\d{2})$")


def normalize_date(s: str) -> str:
    """Return a YYYYMMDD string. '' if unparseable; partial allowed (year/month only)."""
    if not s:
        return ""
    s = s.strip()
    m = _DATE_RE.match(s)
    if not m:
        # Tolerate hyphens and slashes
        digits = re.sub(r"\D", "", s)
        if len(digits) == 8:
            m = _DATE_RE.match(digits)
    if not m:
        return ""
    y, mo, d = m.group(1), m.group(2), m.group(3)
    # Sanity: year 1800-2099, month 0-12, day 0-31
    if not (1800 <= int(y) <= 2099):
        return ""
    if int(mo) > 12 or int(d) > 31:
        return ""
    return f"{y}{mo}{d}"


# ── Publication-date detection ───────────────────────────────────────────────

# Examples: "SATURDAY 8 JUNE 1895", "Saturday, June 8th, 1895", "8 June, 1895"
_PUBDATE_RE = re.compile(
    r"(?:(?P<weekday>Mon|Tues|Tuesd|Wed|Wednes|Thur|Thursd|Fri|Satur|Sun)day[,\s]+)?"
    r"(?:(?P<day1>\d{1,2})(?:st|nd|rd|th)?[\s,]+)?"
    r"(?P<month>January|February|March|April|May|June|July|August|"
    r"September|October|November|December)"
    r"[\s,]+(?:(?P<day2>\d{1,2})(?:st|nd|rd|th)?[,\s]+)?"
    r"(?P<year>\d{4})",
    re.IGNORECASE,
)


def detect_publication_date(page_text: str) -> date | None:
    """Find the publication date in the first ~300 characters of a page."""
    head = page_text[:400]
    for m in _PUBDATE_RE.finditer(head):
        month = _MONTHS[m.group("month").lower()]
        day_str = m.group("day1") or m.group("day2")
        if not day_str:
            continue
        try:
            return date(int(m.group("year")), month, int(day_str))
        except ValueError:
            continue
    return None


def relative_dates(pub: date) -> dict[str, str]:
    """Map weekday names to ISO dates immediately preceding pub.

    'Friday' from a Saturday-published paper means yesterday, not next Friday.
    """
    out: dict[str, str] = {}
    for name, idx in _WEEKDAYS.items():
        delta = (pub.weekday() - idx) % 7
        if delta == 0:
            delta = 7  # "on Monday" in a Monday paper means a week prior
        out[name] = (pub - timedelta(days=delta)).isoformat()
    return out
