"""Extract password components from a user Profile."""
from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING

from ccupp.transforms.date import date_variants
from ccupp.transforms.pinyin import pinyin_variants

if TYPE_CHECKING:
    from ccupp.models import Profile


def _text_variants(word: str, use_pinyin: bool = True) -> Iterator[str]:
    """Generate variants of a single text value.

    If use_pinyin is True, generates pinyin variants for Chinese text.
    Otherwise yields the original and title-case form.
    """
    if not word:
        return
    if use_pinyin:
        yield from pinyin_variants(word)
    else:
        seen = set()
        for v in (word, word[0].upper() + word[1:] if word else word):
            if v not in seen:
                seen.add(v)
                yield v


def _extract_flat(items: list[str], use_pinyin: bool = True) -> Iterator[str]:
    """Extract variants from a flat list of strings."""
    for item in items:
        yield from _text_variants(item, use_pinyin)


def _extract_nested(groups: list[list[str]], use_pinyin: bool = True) -> Iterator[str]:
    """Extract variants from a nested list (list of groups)."""
    for group in groups:
        for item in group:
            yield from _text_variants(item, use_pinyin)


def extract_components(profile: Profile) -> dict[str, list[str]]:
    """Extract all password components from a Profile.

    Returns a dict mapping component categories to lists of unique values.
    Each category represents a type of personal information that might
    appear in passwords.
    """
    components: dict[str, list[str]] = {}

    # Name components (pinyin)
    name_parts = []
    if profile.surname:
        name_parts.extend(pinyin_variants(profile.surname))
    if profile.first_name:
        name_parts.extend(pinyin_variants(profile.first_name))
    # Full name combined
    if profile.surname and profile.first_name:
        full = profile.surname + profile.first_name
        name_parts.extend(pinyin_variants(full))
    if name_parts:
        components['name'] = _dedup(name_parts)

    # Phone numbers (no pinyin)
    phone_parts = list(_extract_flat(profile.phone_numbers, use_pinyin=False))
    # Also extract last 4/6 digits
    for phone in profile.phone_numbers:
        if len(phone) >= 4:
            phone_parts.append(phone[-4:])
        if len(phone) >= 6:
            phone_parts.append(phone[-6:])
    if phone_parts:
        components['phone'] = _dedup(phone_parts)

    # Identity number (no pinyin)
    if profile.identity:
        id_parts = [profile.identity]
        if len(profile.identity) >= 4:
            id_parts.append(profile.identity[-4:])
        if len(profile.identity) >= 6:
            id_parts.append(profile.identity[-6:])
        components['identity'] = _dedup(id_parts)

    # Birthdate (date variants)
    if profile.birthdate and len(profile.birthdate) >= 3:
        year, month, day = profile.birthdate[0], profile.birthdate[1], profile.birthdate[2]
        components['birthdate'] = _dedup(date_variants(year, month, day))
    elif profile.birthdate:
        # Partial date — just use raw values
        components['birthdate'] = _dedup(profile.birthdate)

    # Hometowns (pinyin)
    hometown_parts = list(_extract_flat(profile.hometowns, use_pinyin=True))
    if hometown_parts:
        components['hometowns'] = _dedup(hometown_parts)

    # Places (nested, pinyin)
    place_parts = list(_extract_nested(profile.places, use_pinyin=True))
    if place_parts:
        components['places'] = _dedup(place_parts)

    # Social media (no pinyin)
    social_parts = list(_extract_flat(profile.social_media, use_pinyin=False))
    if social_parts:
        components['social_media'] = _dedup(social_parts)

    # Workplaces (nested, pinyin)
    work_parts = list(_extract_nested(profile.workplaces, use_pinyin=True))
    if work_parts:
        components['workplaces'] = _dedup(work_parts)

    # Educational institutions (nested, pinyin)
    edu_parts = list(_extract_nested(profile.educational_institutions, use_pinyin=True))
    if edu_parts:
        components['education'] = _dedup(edu_parts)

    # Accounts (no pinyin)
    account_parts = list(_extract_flat(profile.accounts, use_pinyin=False))
    if account_parts:
        components['accounts'] = _dedup(account_parts)

    # Old passwords (as-is)
    if profile.passwords:
        components['passwords'] = _dedup(profile.passwords)

    return components


def _dedup(items) -> list[str]:
    """Deduplicate while preserving order."""
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
