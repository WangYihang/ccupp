"""Tests for transform modules."""
from ccupp.transforms.case import case_variants
from ccupp.transforms.date import date_variants
from ccupp.transforms.leetspeak import leetspeak
from ccupp.transforms.leetspeak import leetspeak_variants
from ccupp.transforms.pinyin import pinyin_variants
from ccupp.transforms.pinyin import to_pinyin
from ccupp.transforms.pinyin import to_pinyin_initials


class TestPinyin:
    def test_to_pinyin_single_char(self):
        assert to_pinyin('李') == 'li'

    def test_to_pinyin_multi_char(self):
        assert to_pinyin('二狗') == 'ergou'

    def test_to_pinyin_initials(self):
        assert to_pinyin_initials('李') == 'l'
        assert to_pinyin_initials('二狗') == 'eg'

    def test_pinyin_variants(self):
        variants = list(pinyin_variants('李'))
        assert 'li' in variants
        assert 'l' in variants
        assert 'Li' in variants

    def test_pinyin_variants_multi_char(self):
        variants = list(pinyin_variants('四川'))
        assert 'sichuan' in variants
        assert 'sc' in variants
        assert 'Sichuan' in variants

    def test_pinyin_variants_dedup(self):
        """Single-char pinyin shouldn't duplicate with initials."""
        variants = list(pinyin_variants('李'))
        assert len(variants) == len(set(variants))


class TestDateVariants:
    def test_basic_date(self):
        variants = list(date_variants('1983', '09', '24'))
        assert '19830924' in variants
        assert '830924' in variants
        assert '0924' in variants
        assert '1983' in variants
        assert '198309' in variants

    def test_short_year(self):
        variants = list(date_variants('1983', '09', '24'))
        assert '83' in variants
        assert '8309' in variants

    def test_delimited_forms(self):
        variants = list(date_variants('1983', '09', '24'))
        assert '1983-09-24' in variants
        assert '1983.09.24' in variants

    def test_reversed(self):
        variants = list(date_variants('1983', '09', '24'))
        assert '24091983' in variants

    def test_no_leading_zero(self):
        variants = list(date_variants('1983', '09', '24'))
        assert '924' in variants
        assert '83924' in variants

    def test_no_duplicates(self):
        variants = list(date_variants('2000', '10', '10'))
        assert len(variants) == len(set(variants))


class TestLeetspeak:
    def test_leetspeak(self):
        assert leetspeak('password') == 'p@$$w0rd'
        assert leetspeak('test') == '73$7'

    def test_leetspeak_no_change(self):
        assert leetspeak('123') == '123'

    def test_leetspeak_variants(self):
        variants = list(leetspeak_variants('test'))
        assert 'test' in variants
        assert '73$7' in variants

    def test_leetspeak_variants_no_change(self):
        variants = list(leetspeak_variants('123'))
        assert variants == ['123']


class TestCaseVariants:
    def test_basic(self):
        variants = list(case_variants('hello'))
        assert 'hello' in variants
        assert 'Hello' in variants
        assert 'HELLO' in variants

    def test_empty(self):
        assert list(case_variants('')) == []

    def test_no_duplicates(self):
        variants = list(case_variants('ABC'))
        assert len(variants) == len(set(variants))
