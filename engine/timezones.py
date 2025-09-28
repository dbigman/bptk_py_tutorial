"""
Timezone helpers: IANA validation, alias normalization, and a curated fallback whitelist.

Purpose:
- Provide small, deterministic utilities used by validators and runtime.
- Keep KISS: use stdlib zoneinfo.available_timezones when available.
- Provide a small alias map and curated fallback whitelist for common local names
  (e.g., 'America/La_Paz', 'UTC', 'GMT', 'Etc/UTC').
"""

from __future__ import annotations

from zoneinfo import available_timezones
from typing import Optional, Set, Dict


# Minimal alias map for common non‑standard timezone inputs that appear in datasets.
# Phase‑2: expand this map as needed from a maintained source.
_ALIAS_MAP: Dict[str, str] = {
    # Bolivia / La Paz common variants
    "LA_PAZ": "America/La_Paz",
    "AMERICA/LA_PAZ": "America/La_Paz",
    "BOLIVIA": "America/La_Paz",
    "BOL": "America/La_Paz",
    "LA PAZ": "America/La_Paz",
    # Common canonical names and abbreviations
    "UTC": "UTC",
    "UT": "UTC",
    "GMT": "UTC",
    "LOCAL": "UTC",
    # US zone abbreviations (mapped to common continental zones)
    "PST": "America/Los_Angeles",
    "PDT": "America/Los_Angeles",
    "MST": "America/Denver",
    "MDT": "America/Denver",
    "CST": "America/Chicago",
    "CDT": "America/Chicago",
    "EST": "America/New_York",
    "EDT": "America/New_York",
    # Europe / UK
    "BST": "Europe/London",
    "CET": "Europe/Berlin",
    "CEST": "Europe/Berlin",
    # Asia pacific
    "JST": "Asia/Tokyo",
    "CST-CHINA": "Asia/Shanghai",
}


# Curated fallback list for common timezone names to accept even if zoneinfo lookup
# isn't available or the environment lacks the full database.
_FALLBACK_WHITELIST: Set[str] = {
    "UTC",
    "Etc/UTC",
    "GMT",
    "America/La_Paz",
    "America/New_York",
    "America/Los_Angeles",
    "America/Chicago",
    "America/Denver",
    "America/Sao_Paulo",
    "Europe/London",
    "Europe/Berlin",
    "Europe/Paris",
    "Asia/Shanghai",
    "Asia/Tokyo",
    "Asia/Kolkata",
    "Australia/Sydney",
    "Pacific/Auckland",
}


def get_known_timezones() -> Set[str]:
    """
    Return the set of known IANA timezones available in this environment.
    Falls back to the curated fallback whitelist if zoneinfo doesn't provide a set.
    """
    try:
        tzs = set(available_timezones())
        if tzs:
            return tzs
    except Exception:
        pass
    return set(_FALLBACK_WHITELIST)


def normalize_timezone(tz: Optional[str]) -> Optional[str]:
    """
    Normalize a timezone string:
    - Apply alias map (case-insensitive).
    - If alias applied or exact match in known set, return canonical timezone name.
    - Otherwise return None.
    """
    if tz is None:
        return None
    t = str(tz).strip()
    if not t:
        return None

    # quick uppercase key for alias lookup
    key = t.upper()
    if key in _ALIAS_MAP:
        return _ALIAS_MAP[key]

    # Direct membership in known timezones (case-sensitive by convention)
    known = get_known_timezones()
    if t in known:
        return t

    # Try to match case-insensitively to known timezones
    t_lower = t.lower()
    for candidate in known:
        if candidate.lower() == t_lower:
            return candidate

    # Not found
    return None


def is_valid_timezone(tz: Optional[str]) -> bool:
    """
    Return True if tz normalizes to a known timezone.
    """
    return normalize_timezone(tz) is not None