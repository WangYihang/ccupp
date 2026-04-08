"""Pure metric computation functions for academic evaluation."""
from __future__ import annotations

import statistics
from dataclasses import dataclass
from dataclasses import field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ccupp.models import Profile

# Default N values for Success Rate @ N (matches academic literature)
DEFAULT_N_VALUES = [10, 100, 1000, 10_000]

# Logarithmic sample points for Guess Curve
GUESS_CURVE_SAMPLE_POINTS = [
    1, 2, 5, 10, 20, 50, 100, 200, 500,
    1000, 2000, 5000, 10_000, 20_000, 50_000,
    100_000, 200_000, 500_000, 1_000_000,
]


@dataclass
class GuessNumberStats:
    """Statistics about guess numbers (ranks) of found passwords."""
    found: int = 0
    total: int = 0
    min_rank: int = 0
    max_rank: int = 0
    median_rank: float = 0.0
    mean_rank: float = 0.0
    ranks: list[int] = field(default_factory=list)

    @property
    def not_found(self) -> int:
        return self.total - self.found


def compute_success_rate_at_n(
    ordered_passwords: list[str],
    targets: set[str],
    n_values: list[int] | None = None,
) -> dict[int, float]:
    """Compute Success Rate @ N — fraction of targets found within first N guesses.

    This is the primary metric used in TarGuess (CCS'16), RFGuess (USENIX Sec'23),
    PassLLM (USENIX Sec'25), PointerGuess (USENIX Sec'24), and RankGuess (S&P'25).

    Args:
        ordered_passwords: Passwords in generation order (priority-ranked).
        targets: Set of target passwords to find.
        n_values: List of N values to evaluate at.

    Returns:
        Dict mapping each N to the fraction of targets found (0.0-1.0).
    """
    if not targets:
        return {n: 0.0 for n in (n_values or DEFAULT_N_VALUES)}

    n_values = sorted(n_values or DEFAULT_N_VALUES)
    results: dict[int, float] = {}
    found = 0
    remaining = set(targets)
    n_idx = 0

    for rank, pw in enumerate(ordered_passwords, 1):
        if pw in remaining:
            found += 1
            remaining.discard(pw)

        while n_idx < len(n_values) and rank == n_values[n_idx]:
            results[n_values[n_idx]] = found / len(targets)
            n_idx += 1

        if n_idx >= len(n_values):
            break

    # Fill remaining N values that exceed the password list length
    while n_idx < len(n_values):
        results[n_values[n_idx]] = found / len(targets)
        n_idx += 1

    return results


def compute_guess_numbers(
    ordered_passwords: list[str],
    targets: set[str],
) -> GuessNumberStats:
    """Compute Guess Number — the rank at which each target password first appears.

    Used in TarGuess, PassLLM, and PointerGuess.

    Args:
        ordered_passwords: Passwords in generation order.
        targets: Set of target passwords to find.

    Returns:
        GuessNumberStats with min/max/median/mean ranks and individual ranks.
    """
    if not targets:
        return GuessNumberStats(total=0)

    remaining = set(targets)
    ranks: list[int] = []

    for rank, pw in enumerate(ordered_passwords, 1):
        if pw in remaining:
            ranks.append(rank)
            remaining.discard(pw)
            if not remaining:
                break

    if not ranks:
        return GuessNumberStats(found=0, total=len(targets))

    return GuessNumberStats(
        found=len(ranks),
        total=len(targets),
        min_rank=min(ranks),
        max_rank=max(ranks),
        median_rank=statistics.median(ranks),
        mean_rank=statistics.mean(ranks),
        ranks=ranks,
    )


def compute_guess_curve(
    ordered_passwords: list[str],
    targets: set[str],
    sample_points: list[int] | None = None,
) -> list[tuple[int, float]]:
    """Compute Guess Curve — CDF of success rate vs guess count.

    Used in RankGuess (S&P'25) and PassLLM (USENIX Sec'25).
    Uses logarithmic sampling to keep output compact.

    Args:
        ordered_passwords: Passwords in generation order.
        targets: Set of target passwords to find.
        sample_points: N values to sample at (default: log-spaced).

    Returns:
        List of (N, success_rate) tuples.
    """
    if not targets:
        return []

    points = sorted(sample_points or GUESS_CURVE_SAMPLE_POINTS)
    # Add the total count as final point
    total = len(ordered_passwords)
    if total not in points:
        points = [p for p in points if p <= total] + [total]

    curve: list[tuple[int, float]] = []
    found = 0
    remaining = set(targets)
    point_idx = 0

    for rank, pw in enumerate(ordered_passwords, 1):
        if pw in remaining:
            found += 1
            remaining.discard(pw)

        while point_idx < len(points) and rank == points[point_idx]:
            curve.append((points[point_idx], found / len(targets)))
            point_idx += 1

        if point_idx >= len(points):
            break

    # Fill remaining sample points
    while point_idx < len(points):
        curve.append((points[point_idx], found / len(targets)))
        point_idx += 1

    return curve


def compute_pii_embedding_rate(
    passwords: set[str],
    profile: Profile,
) -> dict[str, float]:
    """Compute PII Embedding Rate — what fraction of passwords contain PII fragments.

    Based on Personal-PCFG (USENIX Sec'14) which found 60.1% of Chinese users
    embed PII in their passwords.

    Args:
        passwords: Set of generated passwords.
        profile: The user profile whose PII to check.

    Returns:
        Dict with per-category rates and overall rate.
    """
    if not passwords:
        return {'name': 0.0, 'date': 0.0, 'phone': 0.0, 'account': 0.0, 'overall': 0.0}

    from ccupp.transforms.pinyin import to_pinyin, to_pinyin_initials

    # Collect PII fragments to search for
    name_fragments: set[str] = set()
    if profile.surname:
        py = to_pinyin(profile.surname)
        if py and len(py) >= 2:
            name_fragments.add(py.lower())
    if profile.first_name:
        py = to_pinyin(profile.first_name)
        if py and len(py) >= 2:
            name_fragments.add(py.lower())
    if profile.surname and profile.first_name:
        full = to_pinyin(profile.surname + profile.first_name)
        if full and len(full) >= 3:
            name_fragments.add(full.lower())

    date_fragments: set[str] = set()
    if profile.birthdate and len(profile.birthdate) >= 3:
        y, m, d = profile.birthdate[0], profile.birthdate[1], profile.birthdate[2]
        for frag in [f'{y}{m}{d}', f'{m}{d}', f'{y[-2:]}{m}{d}', y, f'{y[-2:]}']:
            if len(frag) >= 3:
                date_fragments.add(frag)

    phone_fragments: set[str] = set()
    for phone in profile.phone_numbers:
        if len(phone) >= 4:
            phone_fragments.add(phone[-4:])
        if len(phone) >= 6:
            phone_fragments.add(phone[-6:])
        phone_fragments.add(phone)

    account_fragments: set[str] = set()
    for acc in profile.accounts:
        if len(acc) >= 2:
            account_fragments.add(acc.lower())

    # Count
    name_count = sum(1 for pw in passwords if any(f in pw.lower() for f in name_fragments)) if name_fragments else 0
    date_count = sum(1 for pw in passwords if any(f in pw for f in date_fragments)) if date_fragments else 0
    phone_count = sum(1 for pw in passwords if any(f in pw for f in phone_fragments)) if phone_fragments else 0
    account_count = sum(1 for pw in passwords if any(f in pw.lower() for f in account_fragments)) if account_fragments else 0

    total = len(passwords)
    # Overall: password contains ANY PII fragment
    all_fragments = name_fragments | date_fragments | phone_fragments | account_fragments
    overall_count = sum(
        1 for pw in passwords
        if any(f in pw.lower() for f in name_fragments | account_fragments) or
           any(f in pw for f in date_fragments | phone_fragments)
    ) if all_fragments else 0

    return {
        'name': name_count / total,
        'date': date_count / total,
        'phone': phone_count / total,
        'account': account_count / total,
        'overall': overall_count / total,
    }
