#!/usr/bin/env python3
"""Generate a realistic synthetic PII-password paired dataset.

Password patterns are modeled after published research on Chinese password habits:
- Li et al. (USENIX Sec 2014): 60.1% of Chinese users embed PII in passwords
- Wang et al. (CCS 2016): name+birthday is the most common pattern

Pattern distribution (approximating real-world):
  30% name + birthday variants
  15% name + simple suffix (123, abc, etc.)
  10% phone number or tail digits
  10% account/username + suffix
  10% pinyin name only (with case variants)
  5%  name + cultural number (520, 1314, etc.)
  5%  keyboard pattern + personal info
  5%  old password / reused password
  10% random / no PII pattern (hard cases)
"""
import json
import random
from pypinyin import lazy_pinyin

random.seed(42)

# Chinese surname/name pools (common ones)
SURNAMES = list('李王张刘陈杨赵黄周吴徐孙马胡朱郭何罗高林')
FIRST_NAMES = [
    '伟', '芳', '明', '静', '强', '磊', '洋', '勇', '杰', '娟',
    '军', '敏', '燕', '丽', '波', '鹏', '超', '辉', '琳', '雪',
    '婷', '龙', '萍', '欣', '帅', '露', '威', '莹', '旭', '颖',
    '佳', '浩', '慧', '建', '平', '文', '博', '宁', '涛', '飞',
    '秀', '亮', '刚', '英', '华', '鑫', '凯', '瑞', '健', '志',
]
HOMETOWNS = ['北京', '上海', '广州', '深圳', '成都', '杭州', '武汉', '南京',
             '重庆', '西安', '天津', '苏州', '长沙', '郑州', '青岛', '大连']
COMPANIES = [
    ('腾讯', 'tencent'), ('阿里巴巴', 'alibaba'), ('百度', 'baidu'),
    ('华为', 'huawei'), ('字节跳动', 'bytedance'), ('美团', 'meituan'),
    ('京东', 'jd'), ('小米', 'xiaomi'), ('网易', 'netease'), ('滴滴', 'didi'),
]
SCHOOLS = [
    ('清华大学', 'tsinghua'), ('北京大学', 'pku'), ('浙江大学', 'zju'),
    ('复旦大学', 'fudan'), ('上海交通大学', 'sjtu'), ('南京大学', 'nju'),
]
CULTURAL_NUMBERS = ['520', '1314', '5201314', '888', '666', '168', '886', '521']
KEYBOARD_PATTERNS = ['qwerty', 'qwert', '1qaz2wsx', 'qazwsx', 'asdfgh', 'asd123', 'qwe123']
COMMON_SUFFIXES = ['123', '1234', '12345', '123456', '!', '@', '#', 'abc', '666', '888', '520', '0', '00', '01']
RANDOM_PASSWORDS = [
    'iloveyou', 'sunshine', 'dragon', 'monkey', 'shadow', 'master',
    'letmein', 'football', 'baseball', 'trustno1', 'welcome',
    'passw0rd', 'p@ssword', 'admin123', 'root1234', 'test1234',
]


def pinyin(text):
    return ''.join(lazy_pinyin(text))


def generate_record():
    surname = random.choice(SURNAMES)
    first_name = random.choice(FIRST_NAMES)
    full_name_py = pinyin(surname) + pinyin(first_name)
    surname_py = pinyin(surname)
    first_name_py = pinyin(first_name)
    name_initials = surname_py[0] + first_name_py[0]

    year = str(random.randint(1980, 2000))
    month = f'{random.randint(1, 12):02d}'
    day = f'{random.randint(1, 28):02d}'

    phone = f'1{random.choice([3,5,7,8,9])}{random.randint(0,9)}{random.randint(10000000, 99999999)}'

    profile = {
        'surname': surname,
        'first_name': first_name,
        'phone_numbers': [phone],
        'birthdate': [year, month, day],
        'hometowns': [random.choice(HOMETOWNS)],
    }

    # Randomly add optional fields
    if random.random() < 0.4:
        company = random.choice(COMPANIES)
        profile['workplaces'] = [[company[0], company[1]]]
    if random.random() < 0.3:
        school = random.choice(SCHOOLS)
        profile['educational_institutions'] = [[school[0], school[1]]]
    if random.random() < 0.5:
        account = full_name_py if random.random() < 0.5 else f'{surname_py}{first_name_py}{year[-2:]}'
        profile['accounts'] = [account]

    # Generate password based on weighted pattern
    pattern = random.choices(
        ['name_birthday', 'name_suffix', 'phone', 'account_suffix',
         'pinyin_only', 'cultural', 'keyboard', 'reuse', 'random'],
        weights=[30, 15, 10, 10, 10, 5, 5, 5, 10],
        k=1,
    )[0]

    if pattern == 'name_birthday':
        # Most common Chinese pattern
        variants = [
            f'{full_name_py}{year}{month}{day}',
            f'{full_name_py}{month}{day}',
            f'{full_name_py}{year[-2:]}{month}{day}',
            f'{surname_py}{first_name_py}{month}{day}',
            f'{name_initials}{year}{month}{day}',
            f'{full_name_py}{year}',
            f'{full_name_py.title()}{month}{day}',
            f'{first_name_py}{year}{month}{day}',
        ]
        password = random.choice(variants)

    elif pattern == 'name_suffix':
        suffix = random.choice(COMMON_SUFFIXES)
        name_form = random.choice([full_name_py, surname_py + first_name_py, full_name_py.title()])
        password = name_form + suffix

    elif pattern == 'phone':
        variants = [phone, phone[-4:], phone[-6:], f'{surname_py}{phone[-4:]}']
        password = random.choice(variants)

    elif pattern == 'account_suffix':
        acc = profile.get('accounts', [full_name_py])[0]
        suffix = random.choice(COMMON_SUFFIXES)
        password = acc + suffix

    elif pattern == 'pinyin_only':
        variants = [full_name_py, full_name_py.title(), surname_py + first_name_py,
                     full_name_py.upper(), first_name_py]
        password = random.choice(variants)

    elif pattern == 'cultural':
        num = random.choice(CULTURAL_NUMBERS)
        name_form = random.choice([full_name_py, surname_py, first_name_py])
        password = random.choice([name_form + num, num + name_form])

    elif pattern == 'keyboard':
        kp = random.choice(KEYBOARD_PATTERNS)
        password = random.choice([kp, kp + random.choice(COMMON_SUFFIXES),
                                   f'{surname_py}{kp}'])

    elif pattern == 'reuse':
        # Simulate password reuse with slight modifications
        base = f'{full_name_py}{year[-2:]}'
        password = random.choice([base, base + '!', base + '@', base.title()])

    else:  # random - no PII pattern
        password = random.choice(RANDOM_PASSWORDS)

    profile['target_password'] = password
    return profile


def main():
    records = [generate_record() for _ in range(200)]

    # Print statistics
    patterns = {}
    for r in records:
        pw = r['target_password']
        name_py = pinyin(r['surname']) + pinyin(r['first_name'])
        if name_py in pw.lower():
            cat = 'contains_full_name'
        elif pinyin(r['surname']) in pw.lower() or pinyin(r['first_name']) in pw.lower():
            cat = 'contains_partial_name'
        elif any(d in pw for d in [r['birthdate'][0], r['birthdate'][1] + r['birthdate'][2]]):
            cat = 'contains_date'
        elif r['phone_numbers'][0][-4:] in pw:
            cat = 'contains_phone'
        else:
            cat = 'no_obvious_pii'
        patterns[cat] = patterns.get(cat, 0) + 1

    print(f'Generated {len(records)} records')
    print('Password pattern distribution:')
    for k, v in sorted(patterns.items(), key=lambda x: -x[1]):
        print(f'  {k}: {v} ({v/len(records)*100:.0f}%)')

    # Write JSONL
    outpath = '/home/user/ccupp/benchmark_data/synthetic_200.jsonl'
    with open(outpath, 'w', encoding='utf-8') as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    print(f'\nWritten to {outpath}')


if __name__ == '__main__':
    main()
