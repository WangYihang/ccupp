"""Shared test fixtures."""
import pytest

from ccupp.models import Profile


@pytest.fixture
def sample_profile() -> Profile:
    """A typical Chinese user profile for testing."""
    return Profile(
        surname='李',
        first_name='二狗',
        phone_numbers=['13512345678'],
        identity='220281198309243953',
        birthdate=('1983', '09', '24'),
        hometowns=['四川', '成都'],
        places=[['河北', '秦皇岛']],
        social_media=['987654321'],
        workplaces=[['腾讯', 'tencent']],
        educational_institutions=[['清华大学', 'tsinghua']],
        accounts=['twodogs'],
        passwords=['old_password'],
    )


@pytest.fixture
def minimal_profile() -> Profile:
    """A minimal profile with only name."""
    return Profile(surname='王', first_name='明')


@pytest.fixture
def empty_profile() -> Profile:
    """An empty profile."""
    return Profile()
