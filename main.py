from jinja2 import Template
from pypinyin import lazy_pinyin, Style
from itertools import product, combinations
import hashlib

def to_pinyin(word):
    return ''.join(lazy_pinyin(word))

def to_pinyin_first_letter(word):
    return ''.join(lazy_pinyin(word, style=Style.FIRST_LETTER))

def to_title_case(word):
    return word[0].upper() + word[1:]

def get_md5(password):
    return hashlib.md5(password).hexdigest()

def extract_components(data, use_pinyin=True):
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

def create_person() -> Person:
    person = Person()
    person.set_family_name("李")
    person.set_given_name("二狗")
    person.set_phone(["13512345678",])
    person.set_card("220281198309243953")
    person.set_birthday(("1983", "09", "24"))
    person.set_hometown((u"四川", u"成都", u"高新区"))
    person.set_place([(u"河北", u"秦皇岛", u"北戴河"),])
    person.set_qq(["987654321",])
    person.set_company([(u"腾讯", "tencent"),])
    person.set_school([(u"清华大学", u"清华",  "tsinghua")])
    person.set_account(["twodogs",])
    person.set_password(["old_password",])
    return person

def generate_passwords(templates, components):
    passwords = set()
    for tmpl_str in templates:
        template = Template(tmpl_str)
        password = template.render(**components)
        passwords.add(password)
    return passwords

def generate_combinations(components, delimiters):
    for length in range(1, len(components) + 1):
        for component_group in combinations(components.values(), length):
            for delimiter_group in product(delimiters, repeat=length - 1):
                for component_combination in product(*component_group):
                    password = component_combination[0]
                    for delim, comp in zip(delimiter_group, component_combination[1:]):
                        password += delim + comp
                    yield password

def generate_passwords(templates, combinations, prefixes, suffixes, delimiters):
    for tmpl_str in templates:
        template = Template(tmpl_str)
        for combination in combinations:
            for prefix in prefixes:
                for suffix in suffixes:
                    for delimiter in delimiters:
                        yield template.render(combination=combination, prefix=prefix, suffix=suffix, delimiter=delimiter)

def main():
    person = create_person()
    components = person.get_components()
    delimiters = ["", "-", ".", "|", "_", "+", "#", "@"]
    prefixes = ["qwert", "123"]
    suffixes = ["", "123", "@", "abc", ".", "123.", "!!!"]
    templates = [
        '{{ prefix }}{{ combination }}{{ suffix }}',
    ]
    combinations = generate_combinations(components, delimiters=delimiters)
    passwords = set()
    for password in generate_passwords(templates, combinations, prefixes, suffixes, delimiters):
        if password not in passwords:
            passwords.add(password)
            print(password)

if __name__ == "__main__":
    main()
