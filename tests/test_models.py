"""Tests for Profile model."""
import pytest
from pydantic import ValidationError

from ccupp.models import Profile


class TestProfile:
    def test_empty_profile(self):
        p = Profile()
        assert p.surname == ''
        assert p.phone_numbers == []
        assert p.birthdate == ()

    def test_full_profile(self, sample_profile):
        assert sample_profile.surname == '李'
        assert sample_profile.first_name == '二狗'
        assert sample_profile.phone_numbers == ['13512345678']
        assert sample_profile.birthdate == ('1983', '09', '24')

    def test_normalize_birthdate_from_list(self):
        p = Profile(birthdate=['1990', '01', '15'])
        assert p.birthdate == ('1990', '01', '15')
        assert isinstance(p.birthdate, tuple)

    def test_normalize_nested_lists(self):
        p = Profile(places=[['北京', '海淀']])
        assert p.places == [['北京', '海淀']]

    def test_normalize_scalar_to_nested(self):
        """Single strings in nested fields get wrapped in a list."""
        p = Profile(workplaces=['腾讯'])
        assert p.workplaces == [['腾讯']]

    def test_extra_fields_ignored(self):
        p = Profile(surname='李', unknown_field='ignored')
        assert p.surname == '李'
        assert not hasattr(p, 'unknown_field')

    def test_from_dict(self):
        data = {
            'surname': '王',
            'first_name': '小明',
            'phone_numbers': ['13800138000'],
        }
        p = Profile(**data)
        assert p.surname == '王'
        assert p.phone_numbers == ['13800138000']
