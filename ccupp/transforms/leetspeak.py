"""Leetspeak transforms for password generation."""
from collections.abc import Iterator

# Common leetspeak substitutions
LEET_MAP = {
    'a': '@',
    'e': '3',
    'i': '1',
    'o': '0',
    's': '$',
    't': '7',
    'g': '9',
    'b': '8',
}


def leetspeak(word: str) -> str:
    """Convert a word to leetspeak.

    >>> leetspeak('password')
    'p@$$w0rd'
    >>> leetspeak('test')
    '73$7'
    """
    return ''.join(LEET_MAP.get(c.lower(), c) for c in word)


def leetspeak_variants(word: str) -> Iterator[str]:
    """Generate leetspeak variants of a word.

    Yields: original and leetspeak version (if different).

    >>> list(leetspeak_variants('test'))
    ['test', '73$7']
    >>> list(leetspeak_variants('123'))
    ['123']
    """
    yield word
    leet = leetspeak(word)
    if leet != word:
        yield leet
