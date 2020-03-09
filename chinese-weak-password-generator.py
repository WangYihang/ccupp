#!/usr/bin/env python
#coding:utf-8

import hanzi2pinyin
import hashlib
import sys


class Person:
    NAME = u"李二狗"
    PHONE = ["13512345678",]
    CARD = "220281198309243953"
    BIRTHDAY = ("1983", "09", "24")
    HOMETOWN = (u"四川", u"成都", u"高新区")
    PLACE = [(u"河北", u"秦皇岛", u"北戴河"),]
    QQ = ["987654321",]
    COMPANY = [(u"腾讯", "tencent"),]
    SCHOOL = [(u"清华大学", u"清华",  "tsinghua")]
    ACCOUNT = ["twodog",]
    PASSWORD = ["old_password",]

Delimiters = ["", "-", ".", "|", "_", "+", "#", "@"]
Prefix = ["",]
Suffix = ["","123","@","abc",".","123.","!!!",]

def get_md5(password):
    return hashlib.md5(password).hexdigest()

def get_pinyin(word):
    return hanzi2pinyin.hanzi2pinyin(word)

def get_abbreviation(word):
    result = ""
    for i in word:
        result += get_pinyin(i)[0]
    return result

def get_full_pinyin(word):
    return get_pinyin(word)

def get_title(word):
    result = list(word)
    result[0] = result[0].upper()
    return "".join(i for i in result)

def get_name_component(person):
    result = []
    result.append(get_pinyin(person.NAME))
    result.append(get_pinyin(person.NAME[0]))
    result.append(get_pinyin(person.NAME[1:]))
    result.append(get_title(get_pinyin(person.NAME)))
    result.append(get_title(get_pinyin(person.NAME[0])))
    result.append(get_title(get_pinyin(person.NAME[1:])))
    result.append(get_abbreviation(person.NAME))
    result.append(get_abbreviation(person.NAME[0]))
    result.append(get_abbreviation(person.NAME[1:]))
    return result

def get_phone_component(person):
    result = []
    for phone in person.PHONE:
        result.append(phone)
        result.append(phone[-4:])
    return result

def get_card_component(person):
    result = []
    result.append(person.CARD)
    result.append(person.CARD[-6:])
    result.append(person.CARD[0:6])
    return result

def get_birthday_component(person):
    result = []
    year = person.BIRTHDAY[0]
    month = person.BIRTHDAY[1]
    day = person.BIRTHDAY[2]
    result.append(year)
    result.append(year[2:])
    result.append(month+day)
    result.append(year+month+day)
    return result

def get_hometown_component(person):
    result = []
    result.append(get_pinyin(person.HOMETOWN[0]))
    result.append(get_pinyin(person.HOMETOWN[1]))
    result.append(get_pinyin(person.HOMETOWN[2]))
    result.append(get_title(get_pinyin(person.HOMETOWN[0])))
    result.append(get_title(get_pinyin(person.HOMETOWN[1])))
    result.append(get_title(get_pinyin(person.HOMETOWN[2])))
    result.append(get_abbreviation(person.HOMETOWN[0]))
    result.append(get_abbreviation(person.HOMETOWN[1]))
    result.append(get_abbreviation(person.HOMETOWN[2]))
    return result

def get_place_component(person):
    result = []
    for place in person.PLACE:
        result.append(get_pinyin(place[0]))
        result.append(get_pinyin(place[1]))
        result.append(get_pinyin(place[2]))
        result.append(get_title(get_pinyin(place[0])))
        result.append(get_title(get_pinyin(place[1])))
        result.append(get_title(get_pinyin(place[2])))
        result.append(get_abbreviation(place[0]))
        result.append(get_abbreviation(place[1]))
        result.append(get_abbreviation(place[2]))
    return result

def get_qq_component(person):
    result = []
    for qq in person.QQ:
        result.append(qq)
    return result

def get_company_component(person):
    result = []
    for company in person.COMPANY:
        for name in company:
            result.append(get_pinyin(name))
            result.append(get_title(get_pinyin(name)))
            result.append(get_abbreviation(name))
    return result

def get_school_component(person):
    result = []
    for school in person.SCHOOL:
        for name in school:
            result.append(get_pinyin(name))
            result.append(get_title(get_pinyin(name)))
            result.append(get_abbreviation(name))
    return result

def get_account_component(person):
    result = []
    for account in person.ACCOUNT:
        result.append(get_pinyin(account))
        result.append(get_title(get_pinyin(account)))
        result.append(get_abbreviation(account))
    return result

def get_all_component(person):
    result = []
    result.append(get_name_component(person))
    result.append(get_phone_component(person))
    result.append(get_card_component(person))
    result.append(get_birthday_component(person))
    result.append(get_hometown_component(person))
    result.append(get_place_component(person))
    result.append(get_qq_component(person))
    result.append(get_company_component(person))
    result.append(get_school_component(person))
    result.append(get_account_component(person))
    return result

def store_password(password, filename):
    md5 = get_md5(password)
    print("[+] %s => %s" % (password, md5))
    with open(filename, "a+") as f:
        f.write("%s\t%s\n" % (password, md5))

def main():
    compents = get_all_component(Person)
    filename = "password.list"
    # 单组件密码
    for Delimiter in Delimiters:
        for prefix in Prefix:
            for suffix in Suffix:
                for compent in compents:
                    for i in compent:
                        if Delimiter == "":
                            password = prefix + i + Delimiter + suffix
                            if len(password) > 6 and len(password) < 16:
                                store_password(password, filename)
                            continue
                        password = prefix + i + Delimiter + suffix
                        if len(password) > 6 and len(password) < 16:
                            store_password(password, filename)
                        password = prefix + Delimiter + i + suffix
                        if len(password) > 6 and len(password) < 16:
                            store_password(password, filename)
    # 两组件密码
    for Delimiter in Delimiters:
        for prefix in Prefix:
            for suffix in Suffix:
                for compent_a in compents:
                    for compent_b in compents:
                        for i in compent_a:
                            for j in compent_b:
                                password = prefix + i + Delimiter + j + suffix
                                if len(password) > 6 and len(password) < 16:
                                    store_password(password, filename)

if __name__ == "__main__":
    main()
