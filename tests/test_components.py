"""Tests for component extraction."""
from ccupp.extractors.components import extract_components
from ccupp.models import Profile


class TestExtractComponents:
    def test_name_components(self, sample_profile):
        components = extract_components(sample_profile)
        assert 'name' in components
        names = components['name']
        assert 'li' in names
        assert 'ergou' in names
        # Full name
        assert 'liergou' in names

    def test_phone_components(self, sample_profile):
        components = extract_components(sample_profile)
        assert 'phone' in components
        phones = components['phone']
        assert '13512345678' in phones
        # Last 4 digits
        assert '5678' in phones
        # Last 6 digits
        assert '345678' in phones

    def test_identity_components(self, sample_profile):
        components = extract_components(sample_profile)
        assert 'identity' in components
        ids = components['identity']
        assert '220281198309243953' in ids
        assert '3953' in ids

    def test_birthdate_components(self, sample_profile):
        components = extract_components(sample_profile)
        assert 'birthdate' in components
        dates = components['birthdate']
        assert '19830924' in dates
        assert '0924' in dates
        assert '830924' in dates

    def test_hometown_components(self, sample_profile):
        components = extract_components(sample_profile)
        assert 'hometowns' in components
        hometowns = components['hometowns']
        assert 'sichuan' in hometowns
        assert 'chengdu' in hometowns

    def test_workplace_components(self, sample_profile):
        components = extract_components(sample_profile)
        assert 'workplaces' in components
        workplaces = components['workplaces']
        assert 'tencent' in workplaces
        # Chinese company name in pinyin
        assert 'tengxun' in workplaces

    def test_education_components(self, sample_profile):
        components = extract_components(sample_profile)
        assert 'education' in components
        edu = components['education']
        assert 'tsinghua' in edu

    def test_account_components(self, sample_profile):
        components = extract_components(sample_profile)
        assert 'accounts' in components
        assert 'twodogs' in components['accounts']

    def test_password_components(self, sample_profile):
        components = extract_components(sample_profile)
        assert 'passwords' in components
        assert 'old_password' in components['passwords']

    def test_empty_profile(self, empty_profile):
        components = extract_components(empty_profile)
        assert components == {}

    def test_minimal_profile(self, minimal_profile):
        components = extract_components(minimal_profile)
        assert 'name' in components
        assert len(components) == 1

    def test_no_duplicates_in_components(self, sample_profile):
        components = extract_components(sample_profile)
        for category, values in components.items():
            assert len(values) == len(set(values)), f'Duplicates in {category}'
