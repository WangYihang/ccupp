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

class Person:
    """
    Represents a person with more generic, flexible attributes.
    """
    def __init__(self):
        self.attributes = {}

    def set_surname(self, surname):
        self.attributes['surname'] = surname

    def set_first_name(self, first_name):
        self.attributes['first_name'] = first_name

    def set_phone_numbers(self, phone_numbers):
        self.attributes['phone_numbers'] = phone_numbers

    def set_identity(self, identity):
        self.attributes['identity'] = identity

    def set_birthdate(self, birthdate):
        self.attributes['birthdate'] = birthdate

    def set_hometowns(self, hometowns):
        self.attributes['hometowns'] = hometowns

    def set_places(self, places):
        self.attributes['places'] = places

    def set_social_media(self, social_media):
        self.attributes['social_media'] = social_media

    def set_workplaces(self, workplaces):
        self.attributes['workplaces'] = workplaces

    def set_educational_institutions(self, institutions):
        self.attributes['educational_institutions'] = institutions

    def set_accounts(self, accounts):
        self.attributes['accounts'] = accounts

    def set_passwords(self, passwords):
        self.attributes['passwords'] = passwords

    def get_components(self):
        """
        Extract components from all attributes for password generation.
        Use pinyin conversion where needed.
        """
        return {
            'name': extract_components((self.attributes.get('surname', ''), 
                                        self.attributes.get('first_name', ''))),
            'phone_numbers': extract_components(self.attributes.get('phone_numbers', []), use_pinyin=False),
            'identity': extract_components(self.attributes.get('identity', ''), use_pinyin=False),
            'birthdate': extract_components(self.attributes.get('birthdate', ''), use_pinyin=False),
            'hometowns': extract_components(self.attributes.get('hometowns', [])),
            'places': extract_components(self.attributes.get('places', [])),
            'social_media': extract_components(self.attributes.get('social_media', []), use_pinyin=False),
            'workplaces': extract_components(self.attributes.get('workplaces', [])),
            'educational_institutions': extract_components(self.attributes.get('educational_institutions', [])),
            'accounts': extract_components(self.attributes.get('accounts', []), use_pinyin=False),
        }

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
    person.set_surname("李")
    person.set_first_name("二狗")
    person.set_phone_numbers(["13512345678"])
    person.set_identity("220281198309243953")
    person.set_birthdate(("1983", "09", "24"))
    person.set_hometowns((u"四川", u"成都", u"高新区"))
    person.set_places([(u"河北", u"秦皇岛", u"北戴河")])
    person.set_social_media(["987654321"])
    person.set_workplaces([(u"腾讯", "tencent")])
    person.set_educational_institutions([(u"清华大学", u"清华", "tsinghua")])
    person.set_accounts(["twodogs"])
    person.set_passwords(["old_password"])

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
            print(password)


if __name__ == "__main__":
    main()
