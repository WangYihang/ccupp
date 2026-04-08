"""Rule-based password generation engine."""
from __future__ import annotations

from collections.abc import Iterator
from itertools import product

from ccupp.transforms.case import case_variants
from ccupp.transforms.leetspeak import leetspeak_variants

# Chinese culturally significant numbers commonly used in passwords
CHINESE_LUCKY_NUMBERS = [
    '520',      # 我爱你 (I love you)
    '1314',     # 一生一世 (forever)
    '5201314',  # 我爱你一生一世
    '888',      # 发发发 (prosperity)
    '666',      # 溜溜溜 (awesome)
    '168',      # 一路发 (prosperity all the way)
    '886',      # 拜拜了 (bye bye)
    '521',      # 我爱你 (variant)
    '1688',     # 一路发发
    '8888',     # 发发发发
    '6666',     # 溜溜溜溜
    '000',      # padding
    '111',
    '123',
    '321',
    '233',      # internet laugh
]

# Common keyboard patterns
KEYBOARD_PATTERNS = [
    'qwerty', 'qwert', 'qazwsx', '1qaz2wsx', 'zxcvbn',
    'asdfgh', 'qwertyuiop', '1q2w3e4r', 'asd123',
    'zxc123', 'qwe123', '!@#$%^',
]

# Common password suffixes
COMMON_SUFFIXES = [
    '', '1', '12', '123', '1234', '12345', '123456',
    '!', '!!', '!!!', '@', '#', '.',
    'a', 'abc', 'aa', 'aaa',
    '0', '00', '000',
    '11', '111', '1111',
    '520', '521', '1314',
    '666', '888',
    '~', '~!@#',
]

# Common password prefixes
COMMON_PREFIXES = ['', 'a', 'i', 'my', 'wo', 'the']

# Delimiters between components
DELIMITERS = ['', '.', '-', '_', '@', '#']


class PasswordGenerator:
    """Rule-based password generator.

    Generates passwords by applying rules to extracted components,
    ordered by priority (most likely passwords first).
    """

    def __init__(
        self,
        components: dict[str, list[str]],
        *,
        enable_leetspeak: bool = True,
        enable_case_variants: bool = True,
        enable_cultural_numbers: bool = True,
        enable_keyboard_patterns: bool = True,
        suffixes: list[str] | None = None,
        prefixes: list[str] | None = None,
        delimiters: list[str] | None = None,
    ) -> None:
        self.components = components
        self.enable_leetspeak = enable_leetspeak
        self.enable_case_variants = enable_case_variants
        self.enable_cultural_numbers = enable_cultural_numbers
        self.enable_keyboard_patterns = enable_keyboard_patterns
        self.suffixes = suffixes if suffixes is not None else COMMON_SUFFIXES
        self.prefixes = prefixes if prefixes is not None else COMMON_PREFIXES
        self.delimiters = delimiters if delimiters is not None else DELIMITERS

    def generate(self) -> Iterator[str]:
        """Generate passwords ordered by priority.

        Priority order:
        1. Old passwords and their variants
        2. Single components + suffix (most common pattern)
        3. Name + birthdate combinations
        4. Name + phone/identity tail
        5. Two-component combinations
        6. Components + cultural numbers
        7. Keyboard patterns + components
        8. Leetspeak variants of top passwords
        """
        # Track yielded passwords for dedup
        seen: set[str] = set()

        def _yield_new(password: str) -> Iterator[str]:
            if password and password not in seen:
                seen.add(password)
                yield password

        # Priority 1: Old passwords and variants
        for pw in self._old_password_variants():
            yield from _yield_new(pw)

        # Priority 2: Single components with suffixes
        for pw in self._single_component_suffixed():
            yield from _yield_new(pw)

        # Priority 3: Name + birthdate
        for pw in self._name_date_combos():
            yield from _yield_new(pw)

        # Priority 4: Name + phone/identity tail
        for pw in self._name_id_combos():
            yield from _yield_new(pw)

        # Priority 5: Two-component combinations
        for pw in self._two_component_combos():
            yield from _yield_new(pw)

        # Priority 6: Components + cultural numbers
        if self.enable_cultural_numbers:
            for pw in self._cultural_number_combos():
                yield from _yield_new(pw)

        # Priority 7: Keyboard patterns
        if self.enable_keyboard_patterns:
            for pw in self._keyboard_pattern_combos():
                yield from _yield_new(pw)

    def _all_single_values(self) -> Iterator[str]:
        """Yield all individual component values."""
        for values in self.components.values():
            yield from values

    def _old_password_variants(self) -> Iterator[str]:
        """Generate variants of old/known passwords."""
        passwords = self.components.get('passwords', [])
        for pw in passwords:
            yield pw
            if self.enable_case_variants:
                yield from case_variants(pw)
            # Old password + common suffixes
            for suffix in self.suffixes[:10]:  # Top 10 suffixes only
                if suffix:
                    yield pw + suffix
            if self.enable_leetspeak:
                yield from leetspeak_variants(pw)

    def _single_component_suffixed(self) -> Iterator[str]:
        """Single component + prefix/suffix — most common weak password pattern."""
        for value in self._all_single_values():
            # Value alone
            yield value
            # With case variants
            if self.enable_case_variants:
                for cv in case_variants(value):
                    yield cv
                    # Case variant + suffix
                    for suffix in self.suffixes:
                        if suffix:
                            yield cv + suffix
            else:
                for suffix in self.suffixes:
                    if suffix:
                        yield value + suffix
            # prefix + value
            for prefix in self.prefixes:
                if prefix:
                    yield prefix + value

    def _name_date_combos(self) -> Iterator[str]:
        """Name + birthdate — the most common Chinese weak password pattern."""
        names = self.components.get('name', [])
        dates = self.components.get('birthdate', [])
        if not names or not dates:
            return

        for name, date in product(names, dates):
            for delim in self.delimiters:
                yield name + delim + date
                yield date + delim + name

    def _name_id_combos(self) -> Iterator[str]:
        """Name + phone tail / identity tail."""
        names = self.components.get('name', [])

        for id_category in ('phone', 'identity'):
            id_values = self.components.get(id_category, [])
            if not id_values:
                continue
            for name, id_val in product(names, id_values):
                for delim in self.delimiters:
                    yield name + delim + id_val
                    yield id_val + delim + name

    def _two_component_combos(self) -> Iterator[str]:
        """Combinations of any two component categories."""
        categories = list(self.components.keys())
        for i, cat_a in enumerate(categories):
            for cat_b in categories[i + 1:]:
                vals_a = self.components[cat_a]
                vals_b = self.components[cat_b]
                # Limit to avoid explosion: top 5 values from each
                for va, vb in product(vals_a[:5], vals_b[:5]):
                    for delim in self.delimiters[:3]:  # Top 3 delimiters
                        yield va + delim + vb
                        yield vb + delim + va

    def _cultural_number_combos(self) -> Iterator[str]:
        """Components combined with culturally significant numbers."""
        for value in self._all_single_values():
            for num in CHINESE_LUCKY_NUMBERS:
                yield value + num
                yield num + value

    def _keyboard_pattern_combos(self) -> Iterator[str]:
        """Keyboard patterns combined with components."""
        for pattern in KEYBOARD_PATTERNS:
            yield pattern
            for suffix in self.suffixes[:5]:
                if suffix:
                    yield pattern + suffix
            # Pattern + top component values
            for value in list(self._all_single_values())[:10]:
                yield pattern + value
                yield value + pattern
