"""Tests for the high-level SDK API (ccupp.generate_passwords and re-exports)."""
import itertools

import ccupp
from ccupp import Profile
from ccupp import extract_components
from ccupp import generate_passwords


def test_public_api_reexports():
    """Core SDK names are importable straight from the top-level package."""
    for name in ('Profile', 'PasswordGenerator', 'extract_components',
                 'generate_passwords', 'load_profiles'):
        assert name in ccupp.__all__
        assert hasattr(ccupp, name)


def test_generate_passwords_single_profile(sample_profile: Profile):
    """A single Profile yields candidate passwords lazily."""
    gen = generate_passwords(sample_profile)
    first = list(itertools.islice(gen, 20))
    assert len(first) == 20
    # Known old password should surface early.
    assert 'old_password' in first


def test_generate_passwords_is_lazy(sample_profile: Profile):
    """The function returns an iterator, not a materialized list."""
    gen = generate_passwords(sample_profile)
    assert iter(gen) is gen


def test_generate_passwords_dedups_across_profiles():
    """Identical profiles must not produce duplicate passwords."""
    profile = Profile(surname='李', first_name='二狗', passwords=['secret'])
    results = list(itertools.islice(
        generate_passwords([profile, profile]), 500,
    ))
    assert len(results) == len(set(results))


def test_generate_passwords_length_filters(sample_profile: Profile):
    """min_length / max_length bound every emitted password."""
    results = list(itertools.islice(
        generate_passwords(sample_profile, min_length=8, max_length=12), 200,
    ))
    assert results
    assert all(8 <= len(pw) <= 12 for pw in results)


def test_generate_passwords_disable_strategies(minimal_profile: Profile):
    """Disabling keyboard patterns drops keyboard-derived candidates."""
    # A minimal profile produces a finite, fully-enumerable set.
    enabled = set(generate_passwords(minimal_profile, enable_keyboard_patterns=True))
    disabled = set(generate_passwords(minimal_profile, enable_keyboard_patterns=False))
    assert 'qwerty' in enabled
    assert 'qwerty' not in disabled


def test_generate_passwords_matches_manual_pipeline(sample_profile: Profile):
    """The convenience wrapper equals the explicit extract+generate pipeline."""
    from ccupp import PasswordGenerator

    manual = PasswordGenerator(extract_components(sample_profile))
    expected = list(itertools.islice(manual.generate(), 30))
    actual = list(itertools.islice(generate_passwords(sample_profile), 30))
    assert actual == expected


def test_generate_passwords_empty_profile(empty_profile: Profile):
    """An empty profile yields no component-derived passwords.

    Keyboard patterns are component-independent, so they are disabled here
    to assert that nothing is derived from the (empty) profile itself.
    """
    assert list(generate_passwords(empty_profile, enable_keyboard_patterns=False)) == []
