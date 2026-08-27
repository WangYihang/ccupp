# PII2PW - Personal Information to Password Wordlists

> A social-engineering-based weak password wordlist generator

**English** · [简体中文](README.zh-CN.md)

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://github.com/WangYihang/pii2pw/actions/workflows/test.yaml/badge.svg)](https://github.com/WangYihang/pii2pw/actions/workflows/test.yaml)

PII2PW turns a target's personal information — name, birthday, phone number, places and so on — into a ranked wordlist of the passwords that person is most likely to have chosen.

It is tuned for Chinese users: names and places become pinyin, birthdays become the date formats people actually type, and culturally significant numbers like 520 and 1314 get mixed in.

## Install

```bash
pip install pii2pw
```

Or as a standalone CLI, isolated from your other projects' dependencies:

```bash
uv tool install pii2pw
```

## Use

Describe the target in `config.yaml`. Run `pii2pw init` to write an example, or `pii2pw interactive` to fill one in step by step:

```yaml
- surname: 李
  first_name: 二狗
  phone_numbers:
    - '13512345678'
  birthdate:
    - '1983'
    - '09'
    - '24'
  hometowns:
    - 四川
    - 成都
  accounts:
    - twodogs
  passwords:
    - old_password
```

Then generate:

```bash
pii2pw generate                                  # to stdout
pii2pw generate -o passwords.txt                 # to a file
pii2pw generate --min-length 8 --max-length 16   # filter by length
pii2pw generate -f json -o passwords.json        # JSON output
pii2pw generate --stats                          # also print a length histogram
```

Candidates come out ranked, most likely first, so a truncated list is still the best N guesses. `pii2pw generate --help` lists every option, including switches to turn individual strategies off.

## Config fields

Every field is optional — give it what you know.

| Field | Type | Meaning | Example |
|-------|------|---------|---------|
| `surname` | string | Family name | `李` |
| `first_name` | string | Given name | `二狗` |
| `phone_numbers` | list[string] | Phone numbers | `['13512345678']` |
| `identity` | string | National ID number | `'220281198309243953'` |
| `birthdate` | list[string] | Birthday as [year, month, day] | `['1983', '09', '24']` |
| `hometowns` | list[string] | Hometowns | `['四川', '成都']` |
| `places` | list[list[string]] | Places | `[['河北', '秦皇岛']]` |
| `social_media` | list[string] | Social media handles | `['987654321']` |
| `workplaces` | list[list[string]] | Employers | `[['腾讯', 'tencent']]` |
| `educational_institutions` | list[list[string]] | Schools | `[['清华大学', 'tsinghua']]` |
| `accounts` | list[string] | Account handles | `['twodogs']` |
| `passwords` | list[string] | Known old passwords | `['old_password']` |

A config file may hold several targets; candidates are deduplicated across all of them.

## From Python

```python
from pii2pw import Profile, generate_passwords

profile = Profile(
    surname='李',
    first_name='二狗',
    birthdate=['1983', '09', '24'],
    phone_numbers=['13512345678'],
)

for pw in generate_passwords(profile, min_length=6, max_length=16):
    print(pw)
```

`generate_passwords` returns a lazy iterator, ranked and deduplicated. It also accepts a list of profiles — `load_profiles('config.yaml')` gives you one. See `help(generate_passwords)` for the full set of options.

The package is fully type annotated and ships a [PEP 561](https://peps.python.org/pep-0561/) `py.typed` marker.

## Development

```bash
git clone https://github.com/WangYihang/pii2pw.git
cd pii2pw
uv sync --dev
uv run pytest -v
```

Issues and pull requests are welcome.

## License

MIT License. See [LICENSE](LICENSE).

## Acknowledgements

- Design informed by [chinese-weak-password-generator](http://www.moonsec.com/post-181.html)
- Related research: [arXiv:2306.01545](https://arxiv.org/abs/2306.01545)

## Disclaimer

This tool is for security research and authorised security testing only. Users must comply with applicable laws and regulations and must not use it for unlawful purposes. The author accepts no responsibility for misuse.
