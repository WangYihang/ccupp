"""Tests for configuration loading."""
import tempfile
from pathlib import Path

import pytest
import yaml

from ccupp.config import load_profiles
from ccupp.models import Profile


class TestLoadProfiles:
    def test_load_single_profile(self, tmp_path):
        config = {
            'surname': '王',
            'first_name': '小明',
            'phone_numbers': ['13800138000'],
        }
        config_file = tmp_path / 'config.yaml'
        config_file.write_text(yaml.dump(config, allow_unicode=True))

        profiles = load_profiles(config_file)
        assert len(profiles) == 1
        assert profiles[0].surname == '王'

    def test_load_multiple_profiles(self, tmp_path):
        config = [
            {'surname': '王', 'first_name': '小明'},
            {'surname': '李', 'first_name': '二狗'},
        ]
        config_file = tmp_path / 'config.yaml'
        config_file.write_text(yaml.dump(config, allow_unicode=True))

        profiles = load_profiles(config_file)
        assert len(profiles) == 2
        assert profiles[0].surname == '王'
        assert profiles[1].surname == '李'

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            load_profiles('/nonexistent/config.yaml')

    def test_load_example_config(self):
        """Test loading the bundled example config."""
        config_path = Path(__file__).parent.parent / 'config.yaml'
        if config_path.exists():
            profiles = load_profiles(config_path)
            assert len(profiles) >= 1
            assert all(isinstance(p, Profile) for p in profiles)

    def test_extra_fields_ignored(self, tmp_path):
        config = {'surname': '王', 'extra_field': 'value'}
        config_file = tmp_path / 'config.yaml'
        config_file.write_text(yaml.dump(config, allow_unicode=True))

        profiles = load_profiles(config_file)
        assert len(profiles) == 1
        assert profiles[0].surname == '王'
