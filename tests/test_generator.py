"""Tests for the password generator."""
from ccupp.extractors.components import extract_components
from ccupp.generator import PasswordGenerator


class TestPasswordGenerator:
    def test_generates_passwords(self, sample_profile):
        components = extract_components(sample_profile)
        gen = PasswordGenerator(components=components)
        passwords = list(gen.generate())
        assert len(passwords) > 0

    def test_no_duplicates(self, sample_profile):
        components = extract_components(sample_profile)
        gen = PasswordGenerator(components=components)
        passwords = list(gen.generate())
        assert len(passwords) == len(set(passwords))

    def test_old_passwords_first(self, sample_profile):
        components = extract_components(sample_profile)
        gen = PasswordGenerator(components=components)
        passwords = list(gen.generate())
        # Old password should be among the first results
        assert passwords[0] == 'old_password'

    def test_contains_name_date_combos(self, sample_profile):
        components = extract_components(sample_profile)
        gen = PasswordGenerator(components=components)
        passwords = set(gen.generate())
        # Common pattern: name + birthday
        assert 'li19830924' in passwords or 'li0924' in passwords

    def test_contains_cultural_numbers(self, sample_profile):
        components = extract_components(sample_profile)
        gen = PasswordGenerator(components=components)
        passwords = set(gen.generate())
        # Should contain some cultural number combinations
        assert any('520' in pw for pw in passwords)

    def test_disable_leetspeak(self, sample_profile):
        components = extract_components(sample_profile)
        gen = PasswordGenerator(components=components, enable_leetspeak=False)
        passwords = list(gen.generate())
        assert len(passwords) > 0
        # Should not contain leetspeak of old_password
        assert '0ld_p@$$w0rd' not in passwords

    def test_disable_cultural(self, sample_profile):
        components = extract_components(sample_profile)
        gen_with = PasswordGenerator(components=components, enable_cultural_numbers=True)
        gen_without = PasswordGenerator(components=components, enable_cultural_numbers=False)
        count_with = len(list(gen_with.generate()))
        count_without = len(list(gen_without.generate()))
        assert count_with > count_without

    def test_disable_keyboard(self, sample_profile):
        components = extract_components(sample_profile)
        gen_with = PasswordGenerator(components=components, enable_keyboard_patterns=True)
        gen_without = PasswordGenerator(components=components, enable_keyboard_patterns=False)
        count_with = len(list(gen_with.generate()))
        count_without = len(list(gen_without.generate()))
        assert count_with > count_without

    def test_empty_components(self):
        gen = PasswordGenerator(components={})
        passwords = list(gen.generate())
        # Should still generate keyboard patterns
        assert len(passwords) > 0

    def test_minimal_components(self):
        gen = PasswordGenerator(
            components={'name': ['test']},
            enable_cultural_numbers=False,
            enable_keyboard_patterns=False,
        )
        passwords = list(gen.generate())
        assert 'test' in passwords
        assert 'test123' in passwords
        assert 'Test' in passwords


def _rank(passwords: list[str], target: str) -> int | None:
    """1-based position of `target`, or None if it is never generated."""
    for i, pw in enumerate(passwords, 1):
        if pw == target:
            return i
    return None


class TestGenerationOrder:
    """Ordering regressions.

    Coverage alone says nothing for online guessing, where an attacker gets
    10-1000 attempts. These assert that the patterns real Chinese users pick
    most often are ranked where a throttled attacker would still reach them,
    which a set-membership test cannot express.
    """

    def test_name_birthdate_ranks_early(self, sample_profile):
        """Full-pinyin name + birthdate is the dominant pattern; it leads."""
        gen = PasswordGenerator(components=extract_components(sample_profile))
        passwords = list(gen.generate())
        for target in ('liergou19830924', 'liergou0924', 'liergou1983'):
            rank = _rank(passwords, target)
            assert rank is not None, f'{target} was never generated'
            assert rank <= 200, f'{target} ranked {rank}, expected within 200'

    def test_bare_identity_values_rank_first(self, sample_profile):
        """A bare account handle or full name outranks any decorated form."""
        gen = PasswordGenerator(components=extract_components(sample_profile))
        passwords = list(gen.generate())
        bare = _rank(passwords, 'liergou')
        decorated = _rank(passwords, 'liergou123')
        assert bare is not None and decorated is not None
        assert bare < decorated
        assert bare <= 50, f'bare full name ranked {bare}, expected within 50'

    def test_undelimited_before_delimited(self, sample_profile):
        """The empty delimiter dominates, so it is exhausted first."""
        gen = PasswordGenerator(components=extract_components(sample_profile))
        passwords = list(gen.generate())
        tight = _rank(passwords, 'liergou1983')
        delimited = _rank(passwords, 'liergou.1983')
        assert tight is not None and delimited is not None
        assert tight < delimited

    def test_pii_outranks_profile_independent_sources(self, sample_profile):
        """Targeted guesses come before the generic fallback list."""
        gen = PasswordGenerator(components=extract_components(sample_profile))
        passwords = list(gen.generate())
        pii = _rank(passwords, 'liergou19830924')
        generic = _rank(passwords, '123456')
        assert pii is not None and generic is not None
        assert pii < generic

    def test_combination_plus_suffix_is_reachable(self, sample_profile):
        """name+date+suffix has no other stage that would produce it."""
        gen = PasswordGenerator(components=extract_components(sample_profile))
        passwords = set(gen.generate())
        assert 'liergou1983!' in passwords

    def test_common_fallback_can_be_disabled(self, sample_profile):
        """The generic list is profile-independent and must be switchable."""
        components = extract_components(sample_profile)
        with_fallback = set(PasswordGenerator(components=components).generate())
        without = set(PasswordGenerator(
            components=components, enable_common_passwords=False,
        ).generate())
        assert '123456' in with_fallback
        assert '123456' not in without
