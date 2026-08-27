"""Case transforms for password generation."""
from collections.abc import Iterator


def case_variants(word: str) -> Iterator[str]:
    """Generate case variants of a word.

    Yields: original, title case, upper case, inverted case.
    Skips duplicates.

    >>> list(case_variants('liergou'))
    ['liergou', 'Liergou', 'LIERGOU', 'LIERGOU']
    """
    if not word:
        return

    seen = set()
    variants = [
        word,                                          # original
        word[0].upper() + word[1:] if word else word,  # Title
        word.upper(),                                  # UPPER
        word.swapcase(),                               # iNVERTED
    ]
    for v in variants:
        if v not in seen:
            seen.add(v)
            yield v
