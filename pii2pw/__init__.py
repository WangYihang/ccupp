"""PII2PW - Personal Information to Password Wordlists."""

__version__ = '0.1.0'

from pii2pw.api import generate_passwords
from pii2pw.config import load_profiles
from pii2pw.extractors.components import extract_components
from pii2pw.generator import PasswordGenerator
from pii2pw.models import Profile

__all__ = [
    'Profile',
    'PasswordGenerator',
    'extract_components',
    'generate_passwords',
    'load_profiles',
]
