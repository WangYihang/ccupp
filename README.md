# PII2PW - Personal Information to Password Wordlists

> A social-engineering-based weak password wordlist generator

**English** · [简体中文](README.zh-CN.md)

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://github.com/WangYihang/pii2pw/actions/workflows/test.yaml/badge.svg)](https://github.com/WangYihang/pii2pw/actions/workflows/test.yaml)

PII2PW turns a target's personal information — name, birthday, phone number, places and so on — into a ranked wordlist of the passwords that person is most likely to have chosen.

## Features

- **Pinyin conversion** — Chinese names and place names become full pinyin, initials, and title case
- **Rule-based generation** — output is ranked by likelihood, high-signal patterns first (see [Generation strategy](#generation-strategy))
- **Culturally significant numbers** — combines 520, 1314, 888, 666 and friends
- **Date variants** — a birthday becomes 19830924, 830924, 0924, 83-09-24 and a dozen more forms
- **Leetspeak** — a→@, e→3, o→0 and so on
- **Filtering** — by length and character class
- **Output formats** — txt and json
- **Statistics** — `--stats` prints the length distribution of what was generated
- **Interactive mode** — guided entry of a target's details
- **Memory efficient** — candidates are generated lazily, never materialised in bulk

## Installation

From PyPI:

```bash
pip install pii2pw
```

Or as a standalone CLI tool, isolated from your other projects' dependencies:

```bash
uv tool install pii2pw
```

From source:

```bash
git clone https://github.com/WangYihang/pii2pw.git
cd pii2pw
uv sync
uv run pii2pw --help
```

## Quick start

### 1. Prepare a config file

```bash
# Write out an example config
pii2pw init

# Or fill one in interactively
pii2pw interactive
```

Or write `config.yaml` by hand:

```yaml
- surname: 李
  first_name: 二狗
  phone_numbers:
    - '13512345678'
  identity: '220281198309243953'
  birthdate:
    - '1983'
    - '09'
    - '24'
  hometowns:
    - 四川
    - 成都
  places:
    - - 河北
      - 秦皇岛
  social_media:
    - '987654321'
  workplaces:
    - - 腾讯
      - tencent
  educational_institutions:
    - - 清华大学
      - tsinghua
  accounts:
    - twodogs
  passwords:
    - old_password
```

### 2. Generate

```bash
# Basic usage
pii2pw generate

# Write to a file
pii2pw generate -o passwords.txt

# Filter by length
pii2pw generate --min-length 8 --max-length 16

# Print statistics
pii2pw generate --stats

# JSON output
pii2pw generate -f json -o passwords.json

# Turn strategies off
pii2pw generate --no-leetspeak --no-cultural --no-keyboard --no-common
```

## Using PII2PW as a library

Everything the CLI does is available from Python. The core API is exported from the top-level `pii2pw` package.

### One call: `generate_passwords`

```python
from pii2pw import Profile, generate_passwords

profile = Profile(
    surname='李',
    first_name='二狗',
    birthdate=['1983', '09', '24'],
    phone_numbers=['13512345678'],
    passwords=['old_password'],
)

# A lazy iterator, ranked most-likely-first and deduplicated
for pw in generate_passwords(profile, min_length=6, max_length=16):
    print(pw)
```

Common options:

| Option | Meaning | Default |
|--------|---------|---------|
| `min_length` / `max_length` | Length filter (0 means no bound) | `0` |
| `enable_leetspeak` | Leetspeak transforms (a→@, e→3, …) | `True` |
| `enable_case_variants` | Upper / lower / title case variants | `True` |
| `enable_cultural_numbers` | Culturally significant numbers (520, 1314, …) | `True` |
| `enable_keyboard_patterns` | Keyboard-pattern combinations | `True` |
| `enable_common_passwords` | Generic weak-password fallback, for targets whose password contains no personal information at all | `True` |
| `suffixes` / `prefixes` / `delimiters` | Override the built-in suffix / prefix / delimiter rules | built-in defaults |

The first argument also accepts several profiles at once, deduplicated across all of them:

```python
from pii2pw import load_profiles, generate_passwords

profiles = load_profiles('config.yaml')         # several targets from YAML
passwords = list(generate_passwords(profiles))  # deduplicated across targets
```

### Finer control: the underlying pieces

To put your own logic between component extraction and generation, call the two steps separately:

```python
from pii2pw import Profile, extract_components, PasswordGenerator

profile = Profile(surname='李', first_name='二狗', passwords=['old_password'])

components = extract_components(profile)   # Profile → {category: [value, ...]}
generator = PasswordGenerator(
    components,
    enable_keyboard_patterns=False,
    suffixes=['', '123', '!'],             # custom suffix rules
)
for pw in generator.generate():
    ...
```

### Public API

| Name | Meaning |
|------|---------|
| `Profile` | The target's details (Pydantic model) |
| `load_profiles(path)` | Load `list[Profile]` from a YAML file |
| `extract_components(profile)` | Extract password components from a Profile |
| `PasswordGenerator` | The underlying rule engine |
| `generate_passwords(profile, **options)` | The one-call wrapper (recommended) |

> PII2PW is **fully type annotated**: the package ships a [PEP 561](https://peps.python.org/pep-0561/) `py.typed` marker and passes `mypy --strict`, so type checking and editor completion work in your project too.

## Configuration

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

## Generation strategy

Candidates come out ranked by likelihood, high-signal patterns first:

1. **Old password variants** — known passwords plus case / leetspeak / suffix transforms
2. **Bare identity values** — account handle, full pinyin name, phone number
3. **Name + birthday** — the most common Chinese weak-password shape
4. **High-signal suffixes** — name / account / birthday plus 123, 520, 1314 and so on
5. **Name + phone or ID tail**
6. **Generic weak passwords** — common passwords carrying no personal information (`--no-common` disables)
7. **Exhaustive** — combinations with suffixes, every component with every suffix, delimited combinations, two-component combinations, cultural numbers, keyboard patterns

## Project layout

```
pii2pw/                      # repository
├── pii2pw/                  # Python package
│   ├── __main__.py          # CLI entry point (Typer)
│   ├── api.py               # high-level SDK (generate_passwords)
│   ├── models.py            # Profile model (Pydantic)
│   ├── config.py            # YAML config loading
│   ├── generator.py         # the rule-based generation engine
│   ├── extractors/
│   │   └── components.py    # Profile → password components
│   ├── transforms/
│   │   ├── pinyin.py        # Chinese pinyin conversion
│   │   ├── date.py          # date format variants
│   │   ├── case.py          # case variants
│   │   └── leetspeak.py     # leetspeak transforms
│   └── data/                # example configs, common-password list
├── tests/                   # pytest suite
├── .github/workflows/       # CI/CD (test + release)
├── pyproject.toml
└── Dockerfile
```

## Built with

- **Python 3.12+**
- **Typer** — CLI framework
- **Pydantic** — data validation
- **pypinyin** — Chinese pinyin conversion
- **PyYAML** — config parsing
- **Rich** — terminal output

## Development

```bash
git clone https://github.com/WangYihang/pii2pw.git
cd pii2pw
uv sync --dev
uv run pytest -v
```

## Contributing

Issues and pull requests are welcome.

## License

MIT License. See [LICENSE](LICENSE).

## Acknowledgements

- Design informed by [chinese-weak-password-generator](http://www.moonsec.com/post-181.html)
- Related research: [arXiv:2306.01545](https://arxiv.org/abs/2306.01545)

## Disclaimer

This tool is for security research and authorised security testing only. Users must comply with applicable laws and regulations and must not use it for unlawful purposes. The author accepts no responsibility for misuse.
