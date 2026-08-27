"""Pinyin conversion transforms for Chinese characters."""
from collections.abc import Iterator

from pypinyin import lazy_pinyin
from pypinyin import Style


def to_pinyin(word: str) -> str:
    """Convert Chinese characters to full pinyin.

    >>> to_pinyin('李')
    'li'
    >>> to_pinyin('二狗')
    'ergou'
    """
    return ''.join(lazy_pinyin(word))


def to_pinyin_initials(word: str) -> str:
    """Convert Chinese characters to pinyin first letters.

    >>> to_pinyin_initials('李')
    'l'
    >>> to_pinyin_initials('二狗')
    'eg'
    """
    return ''.join(lazy_pinyin(word, style=Style.FIRST_LETTER))


def pinyin_variants(word: str) -> Iterator[str]:
    """Generate pinyin variants of a Chinese word.

    Yields: full pinyin, initials, title-case pinyin.
    Skips duplicates (e.g. single-char where pinyin == initials).

    >>> list(pinyin_variants('李'))
    ['li', 'l', 'Li']
    >>> list(pinyin_variants('二狗'))
    ['ergou', 'eg', 'Ergou']
    """
    full = to_pinyin(word)
    initials = to_pinyin_initials(word)
    title = full[0].upper() + full[1:] if full else full

    seen = set()
    for variant in (full, initials, title):
        if variant and variant not in seen:
            seen.add(variant)
            yield variant
