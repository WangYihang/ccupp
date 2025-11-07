"""Pinyin conversion utilities."""
from collections.abc import Iterator

from pypinyin import lazy_pinyin
from pypinyin import Style


def to_pinyin(word: str) -> str:
    """Convert Chinese characters to full pinyin."""
    return ''.join(lazy_pinyin(word))


def to_pinyin_first_letter(word: str) -> str:
    """Convert Chinese characters to the first letter of pinyin."""
    return ''.join(lazy_pinyin(word, style=Style.FIRST_LETTER))


def to_title_case(word: str) -> str:
    """Convert a word to title case."""
    if not word:
        return word
    return word[0].upper() + word[1:]


def extract_components(data, use_pinyin: bool = True) -> Iterator[str]:
    """
    Extract components from input data as an iterator.
    Supports tuples, lists, and strings.
    """
    if isinstance(data, tuple):
        for item in data:
            pinyin = to_pinyin(item) if use_pinyin else item
            yield pinyin
            yield to_pinyin_first_letter(item)
            yield to_title_case(pinyin)
    elif isinstance(data, list):
        for item in data:
            yield from extract_components(item, use_pinyin)
    else:
        pinyin = to_pinyin(data) if use_pinyin else data
        yield pinyin
        yield to_pinyin_first_letter(data)
        yield to_title_case(pinyin)
