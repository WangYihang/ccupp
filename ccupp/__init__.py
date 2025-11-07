"""CCUPP - Chinese Character-based User Password Generator."""

__version__ = '0.1.0'

from ccupp.config import load_person_from_yaml, load_persons_from_yaml
from ccupp.generator import PasswordGenerator
from ccupp.models import Person, PersonConfig

__all__ = [
    'Person',
    'PersonConfig',
    'PasswordGenerator',
    'load_person_from_yaml',
    'load_persons_from_yaml',
]
