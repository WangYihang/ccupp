"""Configuration loading from YAML files."""
from pathlib import Path

import yaml

from ccupp.models import Person
from ccupp.models import PersonConfig


def _normalize_to_tuple(data: list | tuple) -> tuple:
    """Convert list to tuple if needed."""
    return tuple(data) if isinstance(data, list) else data


def _normalize_list_items(items: list) -> list:
    """Convert list items to tuples if they are lists."""
    return [
        tuple(item) if isinstance(item, list) else item
        for item in items
    ]


def _config_to_person(config: PersonConfig) -> Person:
    """Convert PersonConfig to Person object."""
    person = Person()

    if config.surname:
        person.set_surname(config.surname)
    if config.first_name:
        person.set_first_name(config.first_name)
    if config.phone_numbers:
        person.set_phone_numbers(config.phone_numbers)
    if config.identity:
        person.set_identity(config.identity)
    if config.birthdate:
        person.set_birthdate(_normalize_to_tuple(config.birthdate))
    if config.hometowns:
        person.set_hometowns(_normalize_to_tuple(config.hometowns))
    if config.places:
        person.set_places(_normalize_list_items(config.places))
    if config.social_media:
        person.set_social_media(config.social_media)
    if config.workplaces:
        person.set_workplaces(_normalize_list_items(config.workplaces))
    if config.educational_institutions:
        person.set_educational_institutions(
            _normalize_list_items(config.educational_institutions),
        )
    if config.accounts:
        person.set_accounts(config.accounts)
    if config.passwords:
        person.set_passwords(config.passwords)

    return person


def load_persons_from_yaml(yaml_path: str | Path) -> list[Person]:
    """
    Load list of person information from a YAML file using Pydantic for validation.

    Args:
        yaml_path: Path to YAML configuration file

    Returns:
        List of Person objects with loaded attributes

    Raises:
        FileNotFoundError: If YAML file doesn't exist
        yaml.YAMLError: If YAML parsing fails
        ValidationError: If data validation fails
    """
    yaml_path = Path(yaml_path)
    if not yaml_path.exists():
        raise FileNotFoundError(f'YAML file not found: {yaml_path}')

    with open(yaml_path, encoding='utf-8') as f:
        data = yaml.safe_load(f)

    # Handle both list and single person formats for backward compatibility
    if not isinstance(data, list):
        data = [data]

    # Validate and parse each person using Pydantic
    persons = []
    for person_data in data:
        config = PersonConfig(**person_data)
        person = _config_to_person(config)
        persons.append(person)

    return persons


# Backward compatibility alias
def load_person_from_yaml(yaml_path: str | Path) -> Person:
    """
    Load single person information from a YAML file.

    This function is kept for backward compatibility.
    It returns the first person from the list.

    Args:
        yaml_path: Path to YAML configuration file

    Returns:
        Person object with loaded attributes
    """
    persons = load_persons_from_yaml(yaml_path)
    if not persons:
        raise ValueError('No person data found in YAML file')
    return persons[0]
