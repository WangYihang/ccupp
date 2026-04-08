"""CCUPP - Chinese Common User Passwords Profiler."""

__version__ = '0.1.0'

from ccupp.config import load_profiles
from ccupp.generator import PasswordGenerator
from ccupp.models import Profile

__all__ = [
    'Profile',
    'PasswordGenerator',
    'load_profiles',
]
