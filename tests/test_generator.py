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
