"""Dataset loading and management for benchmark evaluation.

Supports loading password lists from:
- Local files (one password per line)
- Built-in common password lists
- SecLists (if available)
- PII-password paired datasets (JSONL/CSV) for academic evaluation
"""
from __future__ import annotations

import csv
import gzip
import json
import warnings
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Any

from pii2pw.models import Profile


@dataclass
class PairedRecord:
    """A PII-password pair for targeted evaluation."""
    profile: Profile
    target_password: str

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
    '5201314', '520520', '1314520', '888888',
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

    if path.suffix == '.gz':
        with gzip.open(path, 'rt', encoding='utf-8', errors='ignore') as f:
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


@dataclass
class PairedDatasetLoad:
    """The outcome of loading a paired dataset, including what was dropped."""
    records: list[PairedRecord]
    skipped: list[tuple[int, str]] = field(default_factory=list)
    # (line number, reason) for every row that could not be parsed

    @property
    def total_rows(self) -> int:
        return len(self.records) + len(self.skipped)


def load_paired_dataset(
    path: str | Path,
    *,
    strict: bool = False,
) -> list[PairedRecord]:
    """Load a PII-password paired dataset for academic evaluation.

    Supports two formats:
    - JSONL (.jsonl): One JSON object per line with Profile fields + "target_password"
    - CSV (.csv): Header row with Profile field names + "target_password" column

    Example JSONL line:
        {"surname":"李","first_name":"伟","birthdate":["1990","01","15"],"target_password":"liwei1990"}

    Rows that cannot be parsed are skipped, but never silently: a warning
    naming the count and the first failure is emitted. Silent loss matters
    here more than usual — this feeds an evaluation harness, where dropping
    records shifts every reported rate with no visible cause.

    Args:
        path: Path to the paired dataset file.
        strict: Raise on the first unparseable row instead of skipping it.

    Returns:
        List of PairedRecord objects.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        ValueError: If the file format is not supported, or if `strict` is
            set and any row fails to parse.
    """
    load = load_paired_dataset_verbose(path)
    if load.skipped:
        line_num, reason = load.skipped[0]
        detail = (
            f'{len(load.skipped)} of {load.total_rows} rows in {path} could not '
            f'be parsed (first: line {line_num}: {reason})'
        )
        if strict:
            raise ValueError(detail)
        warnings.warn(detail, stacklevel=2)
    return load.records


def load_paired_dataset_verbose(path: str | Path) -> PairedDatasetLoad:
    """Load a paired dataset, returning the skipped rows alongside the records.

    Use this over :func:`load_paired_dataset` when the caller wants to report
    the skip count itself rather than rely on a warning.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f'Paired dataset not found: {path}')

    suffix = path.suffix.lower()
    if suffix == '.jsonl':
        return _load_paired_jsonl(path)
    elif suffix == '.csv':
        return _load_paired_csv(path)
    else:
        raise ValueError(f'Unsupported paired dataset format: {suffix} (use .jsonl or .csv)')


def _load_paired_jsonl(path: Path) -> PairedDatasetLoad:
    """Load paired data from JSONL file."""
    records: list[PairedRecord] = []
    skipped: list[tuple[int, str]] = []
    with open(path, encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                target = data.pop('target_password', None)
                if not target:
                    skipped.append((line_num, 'missing or empty target_password'))
                    continue
                profile = Profile(**data)
            except (TypeError, ValueError) as exc:
                # ValueError covers json.JSONDecodeError and pydantic's
                # ValidationError, both of which subclass it.
                skipped.append((line_num, f'{type(exc).__name__}: {exc}'))
                continue
            records.append(PairedRecord(profile=profile, target_password=target))
    return PairedDatasetLoad(records=records, skipped=skipped)


def _load_paired_csv(path: Path) -> PairedDatasetLoad:
    """Load paired data from CSV file."""
    records: list[PairedRecord] = []
    skipped: list[tuple[int, str]] = []
    with open(path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        # Row 1 is the header, so data rows start at 2.
        for line_num, row in enumerate(reader, 2):
            target = row.pop('target_password', None)
            if not target:
                skipped.append((line_num, 'missing or empty target_password'))
                continue
            # Convert CSV string fields to expected types
            data: dict[str, Any] = {}
            for key, value in row.items():
                if not value:
                    continue
                # List fields: split by semicolon
                if key in ('phone_numbers', 'hometowns', 'social_media', 'accounts', 'passwords'):
                    data[key] = [v.strip() for v in value.split(';') if v.strip()]
                elif key == 'birthdate':
                    data[key] = [v.strip() for v in value.split(';') if v.strip()]
                elif key in ('places', 'workplaces', 'educational_institutions'):
                    # Nested: groups separated by | , items within group by ;
                    groups = []
                    for group in value.split('|'):
                        items = [v.strip() for v in group.split(';') if v.strip()]
                        if items:
                            groups.append(items)
                    data[key] = groups
                else:
                    data[key] = value

            try:
                profile = Profile(**data)
            except (TypeError, ValueError) as exc:
                skipped.append((line_num, f'{type(exc).__name__}: {exc}'))
                continue
            records.append(PairedRecord(profile=profile, target_password=target))
    return PairedDatasetLoad(records=records, skipped=skipped)


def find_password_lists() -> list[Path]:
    """Search for common password list locations on the system."""
    candidates = [
        Path('/usr/share/wordlists/rockyou.txt'),
        Path('/usr/share/wordlists/rockyou.txt.gz'),
        Path('/usr/share/seclists/Passwords/Common-Credentials/10-million-password-list-top-100000.txt'),
        Path('/usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt.gz'),
    ]
    return [p for p in candidates if p.exists()]
