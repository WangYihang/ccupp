"""Date format transforms for password generation."""
from collections.abc import Iterator


def date_variants(year: str, month: str, day: str) -> Iterator[str]:
    """Generate common date format variants from year/month/day strings.

    Yields various date formats people commonly use in passwords.

    >>> sorted(date_variants('1983', '09', '24'))  # doctest: +SKIP
    ['0924', '1983', '19830924', '198309', '24', '830924', '8309', '83', '09', '24', ...]
    """
    seen = set()

    # Strip leading zeros for short forms
    m_short = month.lstrip('0') or month
    d_short = day.lstrip('0') or day
    y_short = year[-2:] if len(year) == 4 else year

    # Order is emission order, and downstream stages consume these in
    # sequence — so the forms that dominate real corpora lead. Published
    # analyses of Chinese password sets put YYYYMMDD, MMDD and YYYY well
    # ahead of the partial and delimited shapes.
    variants = [
        # Dominant forms
        f'{year}{month}{day}',      # 19830924
        f'{month}{day}',            # 0924
        f'{year}',                  # 1983
        f'{y_short}{month}{day}',   # 830924
        # Secondary full forms
        f'{year}{month}',           # 198309
        f'{y_short}{month}',        # 8309
        f'{y_short}',               # 83
        # No-leading-zero forms
        f'{m_short}{d_short}',      # 924
        f'{y_short}{m_short}{d_short}',  # 83924
        # Individual parts
        month,                       # 09
        day,                         # 24
        # With delimiters
        f'{year}-{month}-{day}',    # 1983-09-24
        f'{year}.{month}.{day}',    # 1983.09.24
        f'{month}-{day}',           # 09-24
        f'{month}.{day}',           # 09.24
        # Reversed
        f'{day}{month}{year}',      # 24091983
        f'{day}{month}',            # 2409
    ]

    for v in variants:
        if v and v not in seen:
            seen.add(v)
            yield v
