"""Rule-based password generation engine."""
from __future__ import annotations

from collections.abc import Callable
from collections.abc import Iterator
from itertools import product

from pii2pw.transforms.case import case_variants
from pii2pw.transforms.leetspeak import leetspeak_variants

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
    '233',      # internet laugh
]

# Short digit runs that carry no cultural meaning but are common padding.
# Kept separate from CHINESE_LUCKY_NUMBERS so --no-cultural does not also
# disable plain padding, which is not a cultural pattern.
PADDING_NUMBERS = ['000', '111', '123', '321']

# Common keyboard patterns
KEYBOARD_PATTERNS = [
    'qwerty', 'qwert', 'qazwsx', '1qaz2wsx', 'zxcvbn',
    'asdfgh', 'qwertyuiop', '1q2w3e4r', 'asd123',
    'zxc123', 'qwe123', '!@#$%^',
]

# The highest-signal suffixes, tried early against name/account/date values.
# Order within the tier is the priority order.
TOP_SUFFIXES = [
    '123', '1', '123456', '12', '1234', '520', '1314', '666', '888',
    '!', '@', '.', '00', '01', '520520',
]

# The full suffix table, used for exhaustive enumeration after the
# high-signal stages. TOP_SUFFIXES entries repeat here; the generator
# deduplicates across stages so the repeats cost nothing.
COMMON_SUFFIXES = [
    '', '1', '12', '123', '1234', '12345', '123456',
    '!', '!!', '!!!', '@', '#', '.',
    'a', 'abc', 'aa', 'aaa',
    '0', '00', '000',
    '01', '02', '03', '04', '05', '06', '07', '08', '09',
    '11', '111', '1111',
    '520', '521', '1314',
    '666', '888', '88', '99',
    '~', '~!@#',
]

# Common password prefixes
COMMON_PREFIXES = ['', 'a', 'i', 'my', 'wo', 'the']

# Delimiters between components. The empty delimiter is by far the most
# common, so the generator iterates delimiters as the OUTER loop: every
# undelimited combination is emitted before any delimited one.
DELIMITERS = ['', '.', '-', '_', '@', '#']

# Component categories in descending order of how often the category carries
# the whole password, per published analyses of Chinese password corpora
# (Li/Wang/Sun INFOCOM'16; Wang et al. CCS'16). Categories a profile does not
# have are skipped; any category missing from this tuple is emitted after
# these, in extraction order.
CATEGORY_PRIORITY = (
    'passwords',
    'accounts',
    'name',
    'birthdate',
    'phone',
    'social_media',
    'hometowns',
    'places',
    'education',
    'workplaces',
    'identity',
)


class PasswordGenerator:
    """Rule-based password generator.

    Generates passwords by applying rules to extracted components, ordered
    so that the patterns most often observed in real corpora come first.
    Ordering matters more than coverage for online guessing, where an
    attacker gets 10-1000 attempts: a candidate ranked 2,800th is useless
    even though it is technically in the dictionary.
    """

    def __init__(
        self,
        components: dict[str, list[str]],
        *,
        enable_leetspeak: bool = True,
        enable_case_variants: bool = True,
        enable_cultural_numbers: bool = True,
        enable_keyboard_patterns: bool = True,
        enable_common_passwords: bool = True,
        suffixes: list[str] | None = None,
        prefixes: list[str] | None = None,
        delimiters: list[str] | None = None,
    ) -> None:
        self.components = components
        self.enable_leetspeak = enable_leetspeak
        self.enable_case_variants = enable_case_variants
        self.enable_cultural_numbers = enable_cultural_numbers
        self.enable_keyboard_patterns = enable_keyboard_patterns
        self.enable_common_passwords = enable_common_passwords
        self.suffixes = suffixes if suffixes is not None else COMMON_SUFFIXES
        self.prefixes = prefixes if prefixes is not None else COMMON_PREFIXES
        self.delimiters = delimiters if delimiters is not None else DELIMITERS

    def generate(self) -> Iterator[str]:
        """Generate passwords ordered by likelihood, without duplicates.

        Stages run in the order returned by :meth:`_stages`; within a stage
        the emission order is the stage's own priority order. A candidate is
        yielded at the rank of its *first* appearance, so putting a cheap
        high-signal stage early is what moves Success Rate @ N.
        """
        seen: set[str] = set()
        for stage in self._stages():
            for password in stage():
                if password and password not in seen:
                    seen.add(password)
                    yield password

    def _stages(self) -> list[Callable[[], Iterator[str]]]:
        """The ordered generation stages.

        The first five stages are the high-signal ones: they emit a few
        hundred candidates that cover the patterns most Chinese users
        actually pick. Everything after them is exhaustive enumeration.
        """
        stages: list[Callable[[], Iterator[str]]] = [
            self._old_password_variants,
            self._bare_identity_values,
            self._name_date_tight,
            self._high_signal_suffixed,
            self._name_id_tight,
            self._bare_components,
        ]
        if self.enable_common_passwords:
            stages.append(self._common_weak_passwords)
        stages.append(self._combo_suffixed)
        stages.append(self._single_component_suffixed)
        stages.append(self._name_date_combos)
        stages.append(self._name_id_combos)
        stages.append(self._two_component_combos)
        if self.enable_cultural_numbers:
            stages.append(self._cultural_number_combos)
        if self.enable_keyboard_patterns:
            stages.append(self._keyboard_pattern_combos)
        return stages

    # ── helpers ──────────────────────────────────────────────────────────

    def _ordered_categories(self) -> Iterator[tuple[str, list[str]]]:
        """Yield (category, values) with the high-signal categories first."""
        for category in CATEGORY_PRIORITY:
            values = self.components.get(category)
            if values:
                yield category, values
        for category, values in self.components.items():
            if category not in CATEGORY_PRIORITY and values:
                yield category, values

    def _all_single_values(self) -> Iterator[str]:
        """Yield all individual component values, high-signal categories first."""
        for _, values in self._ordered_categories():
            yield from values

    def _name_like(self) -> list[str]:
        """Values that behave like a name: the account handle and the name."""
        return self.components.get('accounts', []) + self.components.get('name', [])

    # ── high-signal stages ───────────────────────────────────────────────

    def _old_password_variants(self) -> Iterator[str]:
        """Generate variants of old/known passwords."""
        passwords = self.components.get('passwords', [])
        for pw in passwords:
            yield pw
            if self.enable_case_variants:
                yield from case_variants(pw)
            # Old password + common suffixes
            for suffix in self.suffixes[:10]:
                if suffix:
                    yield pw + suffix
            if self.enable_leetspeak:
                yield from leetspeak_variants(pw)

    def _bare_identity_values(self) -> Iterator[str]:
        """The handful of bare values that are themselves plausible passwords.

        An account handle, a full-pinyin name or a phone number used alone
        is common enough to outrank every decorated form. The remaining bare
        values — hometown, employer, school — are not, so they wait for
        :meth:`_bare_components` further down.
        """
        for category in ('accounts', 'name', 'phone'):
            yield from self.components.get(category, [])

    def _bare_components(self) -> Iterator[str]:
        """Every remaining component value on its own, undecorated."""
        yield from self._all_single_values()

    def _name_date_tight(self) -> Iterator[str]:
        """Name + birthdate with no delimiter — the dominant Chinese pattern.

        Emitted before the generic suffix stages because a name glued to a
        birthdate outranks almost every single-component variant.
        """
        names = self._name_like()
        dates = self.components.get('birthdate', [])
        if not names or not dates:
            return
        for name, date in product(names, dates):
            yield name + date
        for name, date in product(names, dates):
            yield date + name

    def _high_signal_suffixed(self) -> Iterator[str]:
        """Name/account/date + the highest-signal suffixes."""
        values = self._name_like() + self.components.get('birthdate', [])
        for value in values:
            for suffix in TOP_SUFFIXES:
                yield value + suffix

    def _name_id_tight(self) -> Iterator[str]:
        """Name + phone tail / identity tail, no delimiter."""
        names = self._name_like()
        if not names:
            return
        for category in ('phone', 'identity'):
            id_values = self.components.get(category, [])
            for name, id_val in product(names, id_values):
                yield name + id_val
            for name, id_val in product(names, id_values):
                yield id_val + name

    def _common_weak_passwords(self) -> Iterator[str]:
        """Generic weak passwords that contain no personal information.

        A meaningful share of users pick a password with no PII in it at
        all, which no amount of profile-driven rules will reach. These are
        emitted after the high-signal PII stages so they never displace a
        targeted guess, but before exhaustive enumeration.
        """
        from pii2pw.data.common_passwords import COMMON_WEAK_PASSWORDS

        yield from COMMON_WEAK_PASSWORDS

    def _combo_suffixed(self) -> Iterator[str]:
        """Two-component combinations with a suffix appended.

        Covers forms like ``xuwei87!`` — a name glued to a short year and
        then decorated — which neither the single-component suffix stage
        nor the undecorated combination stages reach.
        """
        names = self._name_like()
        dates = self.components.get('birthdate', [])
        if not names or not dates:
            return
        for name, date in product(names, dates):
            for suffix in TOP_SUFFIXES:
                if suffix:
                    yield name + date + suffix

    # ── exhaustive stages ────────────────────────────────────────────────

    def _single_component_suffixed(self) -> Iterator[str]:
        """Single component + prefix/suffix, across every case variant."""
        for value in self._all_single_values():
            if self.enable_case_variants:
                for cv in case_variants(value):
                    yield cv
                    for suffix in self.suffixes:
                        if suffix:
                            yield cv + suffix
            else:
                for suffix in self.suffixes:
                    if suffix:
                        yield value + suffix
            for prefix in self.prefixes:
                if prefix:
                    yield prefix + value

    def _name_date_combos(self) -> Iterator[str]:
        """Name + birthdate, delimited. Undelimited forms come from _name_date_tight."""
        names = self.components.get('name', [])
        dates = self.components.get('birthdate', [])
        if not names or not dates:
            return

        for delim in self.delimiters:
            for name, date in product(names, dates):
                yield name + delim + date
                yield date + delim + name

    def _name_id_combos(self) -> Iterator[str]:
        """Name + phone tail / identity tail, delimited."""
        names = self.components.get('name', [])

        for delim in self.delimiters:
            for category in ('phone', 'identity'):
                id_values = self.components.get(category, [])
                if not id_values:
                    continue
                for name, id_val in product(names, id_values):
                    yield name + delim + id_val
                    yield id_val + delim + name

    def _two_component_combos(self) -> Iterator[str]:
        """Combinations of any two component categories."""
        categories = [category for category, _ in self._ordered_categories()]
        for delim in self.delimiters[:3]:
            for i, cat_a in enumerate(categories):
                for cat_b in categories[i + 1:]:
                    vals_a = self.components[cat_a]
                    vals_b = self.components[cat_b]
                    # Limit to avoid explosion: top 5 values from each
                    for va, vb in product(vals_a[:5], vals_b[:5]):
                        yield va + delim + vb
                        yield vb + delim + va

    def _cultural_number_combos(self) -> Iterator[str]:
        """Components combined with culturally significant numbers."""
        numbers = CHINESE_LUCKY_NUMBERS + PADDING_NUMBERS
        for value in self._all_single_values():
            for num in numbers:
                yield value + num
                yield num + value

    def _keyboard_pattern_combos(self) -> Iterator[str]:
        """Keyboard patterns, alone and combined with components."""
        for pattern in KEYBOARD_PATTERNS:
            yield pattern
            for suffix in self.suffixes:
                if suffix:
                    yield pattern + suffix
            for value in list(self._all_single_values())[:10]:
                yield pattern + value
                yield value + pattern
