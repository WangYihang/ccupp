"""Dataset loading and management for benchmark evaluation.

Supports loading password lists from:
- Local files (one password per line)
- Built-in common password lists
- SecLists (if available)
"""
from __future__ import annotations

import gzip
from pathlib import Path

# Top common passwords (from public research, NOT from leaked data)
# These are widely published in security reports and academic papers
TOP_COMMON_PASSWORDS = [
    '123456', 'password', '12345678', 'qwerty', '123456789',
    '12345', '1234', '111111', '1234567', 'dragon',
    '123123', 'baseball', 'abc123', 'football', 'monkey',
    'letmein', 'shadow', 'master', '666666', 'qwertyuiop',
    '123321', 'mustang', '1234567890', 'michael', '654321',
    'superman', '1qaz2wsx', '7777777', '121212', '000000',
    'qazwsx', '123qwe', 'killer', 'trustno1', 'jordan',
    'jennifer', 'zxcvbnm', 'asdfgh', 'hunter', 'buster',
    'soccer', 'harley', 'batman', 'andrew', 'tigger',
    'sunshine', 'iloveyou', '2000', 'charlie', 'robert',
    'thomas', 'hockey', 'ranger', 'daniel', 'starwars',
    '112233', 'george', 'computer', 'michelle', 'jessica',
    'pepper', '1111', 'zxcvbn', '555555', '11111111',
    '131313', 'freedom', '777777', 'pass', 'maggie',
    '159753', 'aaaaaa', 'ginger', 'princess', 'joshua',
    'cheese', 'amanda', 'summer', 'love', 'ashley',
    'nicole', 'chelsea', 'biteme', 'matthew', 'access',
    'yankees', '987654321', 'dallas', 'austin', 'thunder',
    'taylor', 'matrix', 'welcome', 'william', 'internet',
    'hello', 'password1', 'password123', 'admin', 'admin123',
    'iloveu', 'changeme', 'passw0rd', 'p@ssword', 'p@ssw0rd',
    # Chinese-common patterns (from published research)
    '5201314', '520520', '1314520', '888888', '666666',
    'woaini', 'woaini520', 'aini1314', '521521', '168168',
    'woaini1314', 'iloveyou520', 'asd123', 'qwe123',
    'abc123456', '1q2w3e4r', 'asdf1234', 'zxcvbnm123',
]


def load_password_set(path: str | Path) -> set[str]:
    """Load a password list file into a set.

    Supports:
    - Plain text files (one password per line)
    - Gzip compressed files (.gz)

    Args:
        path: Path to the password list file.

    Returns:
        Set of passwords (stripped, non-empty lines).
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f'Password list not found: {path}')

    passwords: set[str] = set()
    open_fn = gzip.open if path.suffix == '.gz' else open
    encoding_kw = {'encoding': 'utf-8', 'errors': 'ignore'}

    if path.suffix == '.gz':
        with gzip.open(path, 'rt', **encoding_kw) as f:
            for line in f:
                pw = line.strip()
                if pw:
                    passwords.add(pw)
    else:
        with open(path, encoding='utf-8', errors='ignore') as f:
            for line in f:
                pw = line.strip()
                if pw:
                    passwords.add(pw)

    return passwords


def get_builtin_common_passwords() -> set[str]:
    """Get the built-in set of common passwords."""
    return set(TOP_COMMON_PASSWORDS)


def find_password_lists() -> list[Path]:
    """Search for common password list locations on the system."""
    candidates = [
        Path('/usr/share/wordlists/rockyou.txt'),
        Path('/usr/share/wordlists/rockyou.txt.gz'),
        Path('/usr/share/seclists/Passwords/Common-Credentials/10-million-password-list-top-100000.txt'),
        Path('/usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt.gz'),
    ]
    return [p for p in candidates if p.exists()]
