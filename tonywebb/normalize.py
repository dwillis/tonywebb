"""Shared normalization for cricket index entries.

Used by parser_matches.py (post-extraction cleanup), compare_matches.py
(comparison key), and build_browser.py (display key).  Handles both
matchup-style titles ("Team A v Team B") and free-form titles used by
non-match content types (statistics, biography, etc.).
"""

from __future__ import annotations

import csv
import re
from datetime import date, timedelta
from pathlib import Path

# Tokens preserved verbatim (case-sensitive) when title-casing matchups.
_PRESERVE = {
    "XI": "XI",
    "II": "II",
    "III": "III",
    "IV": "IV",
}

# Honorifics / abbreviations — no trailing dot per ACS Style Guide.
_HONORIFICS = {"mr", "mrs", "st", "rev", "dr", "capt", "maj", "col", "lt", "sgt"}

# Initial-style tokens: dotted ("C.E.", "T.W.") or 2-4 uppercase ("CE", "TW").
_INITIALS_RE = re.compile(r"^(?:(?:[A-Z]\.){1,4}|[A-Z]{2,4})$")

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
    upper = tok.upper().replace(".", "")
    if upper in _PRESERVE:
        return _PRESERVE[upper]
    bare = tok.rstrip(".").lower()
    if bare in _HONORIFICS:
        return bare.capitalize()
    if _INITIALS_RE.match(tok):
        return upper
    return tok[:1].upper() + tok[1:].lower() if tok else tok


def _title_case_team(name: str) -> str:
    parts = re.split(r"(\s+|-)", name)  # keep hyphens / spaces
    return "".join(_title_token(p) if p.strip() and p != "-" else p for p in parts)


def _apply_team_style(s: str) -> str:
    """Style cleanups shared by every _normalize_team() exit path -- run once
    on the raw input, and again on whatever a registry lookup returns, so a
    non-style-compliant clubs.csv canonical_name (e.g. "Liberal 2nd XI" where
    "Second XI" is merely an alias) can't bypass these rules just by being
    the string the registry happens to return verbatim.
    """
    # Drop trailing C.C. / Cricket Club / O.C. (Old Cricketers-style suffix --
    # matches generate_clubs.py's strip_cc_oc(), which already treats OC the
    # same way; normalize_matchup previously didn't, causing e.g. "Waterlow's
    # OC" and "Waterlow's" to be treated as different teams).
    s = re.sub(r"[,\s]+(?:C\.?\s*C\.?|Cricket\s+Club|O\.?\s*C\.?)\.?\s*$", "", s, flags=re.IGNORECASE)
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


def _normalize_team(team: str, registry: ClubRegistry | None = None) -> str:
    s = _apply_team_style(team.strip())
    if registry:
        resolved = registry.resolve(s)
        if resolved:
            return _apply_team_style(resolved)
    return s


def normalize_matchup(matchup: str, registry: ClubRegistry | None = None) -> str:
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
        return _normalize_team(s, registry=registry)
    left, right = parts
    return f"{_normalize_team(left, registry=registry)} v {_normalize_team(right, registry=registry)}"


def matchup_key(matchup: str) -> str:
    """Lowercase, punctuation-stripped key for equality comparisons."""
    s = normalize_matchup(matchup).lower()
    s = s.replace(".", "").replace("'", "")
    return re.sub(r"\s+", " ", s).strip()


def symmetric_matchup_key(matchup: str) -> str:
    """Like matchup_key(), but order-insensitive: "A v B" and "B v A" produce
    the same key.

    Sources disagree on team order for the same match -- a prose report
    ("Rock Ferry were busy replying to Liverpool's challenge") preserves
    whatever order the sentence happens to name the teams in, while a
    manual index may consistently list the winner (or home team) first.
    Neither is "wrong"; there's no canonical order to extract. Use this for
    MATCHING/comparing rows across sources (evaluate, consensus) where that
    disagreement would otherwise look like two different matches.

    Extraction and within-run dedup should keep using matchup_key() (order
    left as printed) so a genuine home-and-away rematch on a different date
    isn't accidentally conflated -- the date still discriminates those, but
    there's no reason to introduce order-insensitivity into the pipeline's
    own output, only into cross-source comparisons.
    """
    key = matchup_key(matchup)
    parts = key.split(" v ")
    if len(parts) == 2:
        parts.sort()
        return " v ".join(parts)
    return key


def normalize_title(title: str) -> str:
    """Normalize a non-match title (statistics, team info, biography, etc.).

    Lighter than normalize_matchup: strips trailing CC/Cricket Club,
    collapses whitespace, strips punctuation, but preserves original casing.
    """
    if not title:
        return ""
    s = title.strip()
    s = re.sub(r"[,\s]+(?:C\.?\s*C\.?|Cricket\s+Club)\.?\s*$", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\s+", " ", s).strip()
    s = s.strip(",;:")
    return s


def title_key(title: str) -> str:
    """Lowercase, punctuation-stripped key for non-match title comparisons."""
    s = normalize_title(title).lower()
    s = s.replace(".", "").replace("'", "")
    return re.sub(r"\s+", " ", s).strip()


# ── Date normalization ───────────────────────────────────────────────────────

_DATE_RE = re.compile(r"^(\d{4})(\d{2})(\d{2})$")


def normalize_date(s: str) -> str:
    """Return a YYYYMMDD string. '' only if the input is unparseable.

    Date encoding convention used across every run:
      - ``YYYYMMDD`` — full date, day known (e.g. ``18950527``)
      - ``YYYYMM00`` — month known, day unknown (e.g. ``18950800``)
      - ``YYYY0000`` — year only, month/day unknown (e.g. ``18950000``)

    The collection is a single season (1895), so the year is always known
    and a row's date should never be empty in practice -- callers floor an
    empty result to ``{SEASON}0000`` rather than persisting ''. This function
    does not assume the season, so it returns '' for genuinely unparseable
    input and leaves the floor to the caller.
    """
    if s is None:
        return ""
    s = str(s).strip()
    if not s:
        return ""
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


# ── Date-phrase resolution (deterministic, replaces model arithmetic) ──────
# Models are unreliable at "resolve this weekday relative to the publication
# date" arithmetic, even when handed a precomputed lookup table in the prompt.
# Asking for the verbatim date phrase and resolving it here in Python removes
# that failure mode -- this is a lookup/regex problem, not a reasoning one.

_HOLIDAY_DATES_1895 = {
    "whit monday": (5, 27), "whit-monday": (5, 27),
    "whit tuesday": (5, 28), "whit-tuesday": (5, 28),
    "good friday": (4, 12),
    "easter monday": (4, 15),
    "august bank holiday": (8, 5),
    "bank holiday": (8, 5),
}

_LAST_WEEK_RE = re.compile(r"last\s+week", re.IGNORECASE)
_WEEKDAY_RE = re.compile(
    r"\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", re.IGNORECASE
)
_MONTH_DAY_RE = re.compile(
    r"\b(?P<day>\d{1,2})(?:st|nd|rd|th)?\s+(?P<month>january|february|march|april|may|june|"
    r"july|august|september|october|november|december)\b",
    re.IGNORECASE,
)
_DAY_MONTH_RE = re.compile(
    r"\b(?P<month>january|february|march|april|may|june|july|august|september|october|"
    r"november|december)\s+(?P<day>\d{1,2})(?:st|nd|rd|th)?\b",
    re.IGNORECASE,
)


def resolve_date_phrase(phrase: str | None, publication_date: date | None, year: int = 1895) -> str | None:
    """Deterministically resolve a verbatim date reference to YYYYMMDD.

    Handles: named 1895 holidays ("on Whit-Monday"), explicit month/day
    ("5 August" or "August 5th"), and weekday names relative to the page's
    publication date ("on Saturday", with a "last week" qualifier pushing the
    result back an additional 7 days, e.g. "Friday in last week").

    Returns None if the phrase can't be confidently resolved -- callers
    should fall back to the model's own "date" field in that case.
    """
    if not phrase:
        return None
    p = phrase.strip().lower()
    if not p:
        return None

    for name, (month, day) in _HOLIDAY_DATES_1895.items():
        if name in p:
            return f"{year}{month:02d}{day:02d}"

    m = _MONTH_DAY_RE.search(p) or _DAY_MONTH_RE.search(p)
    if m:
        month = _MONTHS[m.group("month").lower()]
        day = int(m.group("day"))
        try:
            return date(year, month, day).strftime("%Y%m%d")
        except ValueError:
            return None

    if publication_date is None:
        return None
    wd_match = _WEEKDAY_RE.search(p)
    if not wd_match:
        return None
    weekday_name = wd_match.group(1).lower()
    rel = relative_dates(publication_date)
    resolved = rel.get(weekday_name)
    if resolved is None:
        return None
    resolved_date = date.fromisoformat(resolved)
    if _LAST_WEEK_RE.search(p):
        resolved_date -= timedelta(days=7)
    return resolved_date.strftime("%Y%m%d")


# ── Club Registry ───────────────────────────────────────────────────────────

def _registry_key(name: str) -> str:
    s = name.strip().lower()
    s = re.sub(r"[^a-z0-9 ]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


class ClubRegistry:
    """Resolves team names to canonical forms using clubs.csv."""

    def __init__(self, csv_path: str | Path = "clubs.csv"):
        self._canonical: dict[str, str] = {}  # registry_key -> canonical name
        path = Path(csv_path)
        if not path.exists():
            return
        with path.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                canon = row["canonical_name"].strip()
                if not canon:
                    continue
                self._canonical[_registry_key(canon)] = canon
                for alias in (row.get("aliases") or "").split("|"):
                    alias = alias.strip()
                    if alias:
                        self._canonical[_registry_key(alias)] = canon

    def resolve(self, name: str) -> str | None:
        key = _registry_key(name)
        if key in self._canonical:
            return self._canonical[key]
        # Try without trailing "cc" or "oc"
        stripped = re.sub(r"\s+(cc|oc)$", "", key)
        if stripped != key and stripped in self._canonical:
            return self._canonical[stripped]
        # Try without leading "mr"
        no_mr = re.sub(r"^mr\s+", "", key)
        if no_mr != key and no_mr in self._canonical:
            return self._canonical[no_mr]
        return None

    def is_known(self, name: str) -> bool:
        return self.resolve(name) is not None

    def __len__(self) -> int:
        return len(set(self._canonical.values()))
