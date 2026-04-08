"""Configuration loading from YAML files."""
from __future__ import annotations

from pathlib import Path

import yaml

from ccupp.models import Profile


def load_profiles(yaml_path: str | Path) -> list[Profile]:
    """Load user profiles from a YAML configuration file.

    Supports both a single profile dict and a list of profiles.

    Args:
        yaml_path: Path to the YAML configuration file.

    Returns:
        List of validated Profile objects.

    Raises:
        FileNotFoundError: If the YAML file doesn't exist.
        yaml.YAMLError: If YAML parsing fails.
        pydantic.ValidationError: If data validation fails.
    """
    yaml_path = Path(yaml_path)
    if not yaml_path.exists():
        raise FileNotFoundError(f'Configuration file not found: {yaml_path}')

    with open(yaml_path, encoding='utf-8') as f:
        data = yaml.safe_load(f)

    if not isinstance(data, list):
        data = [data]

    return [Profile(**entry) for entry in data]
