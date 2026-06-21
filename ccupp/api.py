"""High-level SDK entry points for using CCUPP as a library."""
from __future__ import annotations

from collections.abc import Iterable
from collections.abc import Iterator

from ccupp.extractors.components import extract_components
from ccupp.generator import PasswordGenerator
from ccupp.models import Profile


def generate_passwords(
    profile: Profile | Iterable[Profile],
    *,
    min_length: int = 0,
    max_length: int = 0,
    enable_leetspeak: bool = True,
    enable_case_variants: bool = True,
    enable_cultural_numbers: bool = True,
    enable_keyboard_patterns: bool = True,
    suffixes: list[str] | None = None,
    prefixes: list[str] | None = None,
    delimiters: list[str] | None = None,
) -> Iterator[str]:
    """Generate candidate passwords for one or more profiles.

    This is the one-call convenience wrapper around
    :func:`~ccupp.extractors.components.extract_components` and
    :class:`~ccupp.generator.PasswordGenerator`. Passwords are yielded
    lazily, ordered by likelihood, deduplicated across all given profiles.

    Args:
        profile: A single :class:`~ccupp.models.Profile` or any iterable of
            profiles (e.g. the result of :func:`~ccupp.config.load_profiles`).
        min_length: Drop passwords shorter than this (0 = no minimum).
        max_length: Drop passwords longer than this (0 = no maximum).
        enable_leetspeak: Enable leetspeak transforms (a→@, e→3, ...).
        enable_case_variants: Enable upper/lower/title-case variants.
        enable_cultural_numbers: Enable Chinese lucky-number combinations.
        enable_keyboard_patterns: Enable keyboard-pattern combinations.
        suffixes: Override the default common suffixes.
        prefixes: Override the default common prefixes.
        delimiters: Override the default component delimiters.

    Yields:
        Candidate password strings, most likely first, without duplicates.

    Example:
        >>> from ccupp import Profile, generate_passwords
        >>> profile = Profile(surname='李', first_name='二狗',
        ...                   birthdate=['1983', '09', '24'])
        >>> for pw in generate_passwords(profile, min_length=6, max_length=16):
        ...     ...
    """
    profiles = [profile] if isinstance(profile, Profile) else list(profile)

    seen: set[str] = set()
    for prof in profiles:
        generator = PasswordGenerator(
            components=extract_components(prof),
            enable_leetspeak=enable_leetspeak,
            enable_case_variants=enable_case_variants,
            enable_cultural_numbers=enable_cultural_numbers,
            enable_keyboard_patterns=enable_keyboard_patterns,
            suffixes=suffixes,
            prefixes=prefixes,
            delimiters=delimiters,
        )
        for pw in generator.generate():
            if min_length and len(pw) < min_length:
                continue
            if max_length and len(pw) > max_length:
                continue
            if pw in seen:
                continue
            seen.add(pw)
            yield pw
