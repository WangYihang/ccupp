import argparse
import hashlib
import logging
from itertools import product, combinations
from jinja2 import Template
from pypinyin import lazy_pinyin, Style
from rich.logging import RichHandler
from rich.console import Console

# Initialize rich console and logging
console = Console()
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(console=console)]
)
logger = logging.getLogger("PasswordGenerator")


# Utility functions
def to_pinyin(word):
    """Convert Chinese characters to full pinyin."""
    return ''.join(lazy_pinyin(word))


def to_pinyin_first_letter(word):
    """Convert Chinese characters to the first letter of pinyin."""
    return ''.join(lazy_pinyin(word, style=Style.FIRST_LETTER))


def to_title_case(word):
    """Convert a word to title case."""
    return word[0].upper() + word[1:]


def get_md5(password):
    """Generate MD5 hash of a password."""
    return hashlib.md5(password.encode()).hexdigest()


def extract_components(data, use_pinyin=True):
    """
    Extract components from input data.
    Supports tuples, lists, and strings.
    """
    result = []
    if isinstance(data, tuple):
        for item in data:
            pinyin = to_pinyin(item) if use_pinyin else item
            result.extend([pinyin, to_pinyin_first_letter(item), to_title_case(pinyin)])
    elif isinstance(data, list):
        for item in data:
            result.extend(extract_components(item, use_pinyin))
    else:
        pinyin = to_pinyin(data) if use_pinyin else data
        result.extend([pinyin, to_pinyin_first_letter(data), to_title_case(pinyin)])
    return result


# Person class
class Person:
    """
    Represents a person with various attributes.
    Attributes can be used to generate password components.
    """
    def __init__(self):
        self.attributes = {}

    def set_attributes(self, **kwargs):
        self.attributes.update(kwargs)

    def set_family_name(self, family_name):
        self.attributes['family_name'] = family_name

    def set_given_name(self, given_name):
        self.attributes['given_name'] = given_name

    def set_phone(self, phone):
        self.attributes['phone'] = phone

    def set_card(self, card):
        self.attributes['card'] = card

    def set_birthday(self, birthday):
        self.attributes['birthday'] = birthday

    def set_hometown(self, hometown):
        self.attributes['hometown'] = hometown

    def set_place(self, place):
        self.attributes['place'] = place

    def set_qq(self, qq):
        self.attributes['qq'] = qq

    def set_company(self, company):
        self.attributes['company'] = company

    def set_school(self, school):
        self.attributes['school'] = school

    def set_account(self, account):
        self.attributes['account'] = account

    def set_password(self, password):
        self.attributes['password'] = password

    def get_components(self):
        """
        Extract components from all attributes for password generation.
        """
        components = {
            'name': extract_components((self.attributes['family_name'], self.attributes['given_name'])),
            'phone': extract_components(self.attributes['phone'], use_pinyin=False),
            'card': extract_components(self.attributes['card'], use_pinyin=False),
            'birthday': extract_components(self.attributes['birthday'], use_pinyin=False),
            'hometown': extract_components(self.attributes['hometown']),
            'place': extract_components(self.attributes['place']),
            'qq': extract_components(self.attributes['qq'], use_pinyin=False),
            'company': extract_components(self.attributes['company']),
            'school': extract_components(self.attributes['school']),
            'account': extract_components(self.attributes['account'], use_pinyin=False),
        }
        return components


# Password generation functions
def generate_combinations(components, delimiters):
    """
    Generate all possible combinations of components with delimiters.
    """
    for length in range(1, len(components) + 1):
        for component_group in combinations(components.values(), length):
            for delimiter_group in product(delimiters, repeat=length - 1):
                for component_combination in product(*component_group):
                    password = component_combination[0]
                    for delim, comp in zip(delimiter_group, component_combination[1:]):
                        password += delim + comp
                    yield password


def generate_passwords(templates, combinations, prefixes, suffixes):
    """
    Generate passwords based on templates, combinations, prefixes, and suffixes.
    """
    for tmpl_str in templates:
        template = Template(tmpl_str)
        for combination in combinations:
            for prefix in prefixes:
                for suffix in suffixes:
                    yield template.render(combination=combination, prefix=prefix, suffix=suffix)


# Command-line interface
def parse_args():
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Password Generator using Personal Information")
    parser.add_argument("--prefixes", nargs="*", default=["qwert", "123"], help="List of prefixes")
    parser.add_argument("--suffixes", nargs="*", default=["", "123", "@", "abc", ".", "123.", "!!!"], help="List of suffixes")
    parser.add_argument("--delimiters", nargs="*", default=["", "-", ".", "|", "_", "+", "#", "@"], help="List of delimiters")
    parser.add_argument("--templates", nargs="*", default=['{{ prefix }}{{ combination }}{{ suffix }}'], help="List of templates")
    return parser.parse_args()


def main():
    """
    Main function to generate passwords based on user input.
    """
    args = parse_args()

    # Create a sample person
    person = Person()
    person.set_family_name("李")
    person.set_given_name("二狗")
    person.set_phone(["13512345678"])
    person.set_card("220281198309243953")
    person.set_birthday(("1983", "09", "24"))
    person.set_hometown((u"四川", u"成都", u"高新区"))
    person.set_place([(u"河北", u"秦皇岛", u"北戴河")])
    person.set_qq(["987654321"])
    person.set_company([(u"腾讯", "tencent")])
    person.set_school([(u"清华大学", u"清华", "tsinghua")])
    person.set_account(["twodogs"])
    person.set_password(["old_password"])

    # Extract components
    components = person.get_components()
    logger.info("Extracted components: %s", components)

    # Generate combinations
    combinations = generate_combinations(components, delimiters=args.delimiters)

    # Generate passwords
    passwords = set()
    for password in generate_passwords(args.templates, combinations, args.prefixes, args.suffixes):
        if password not in passwords:
            passwords.add(password)
            console.print(password)


if __name__ == "__main__":
    main()
