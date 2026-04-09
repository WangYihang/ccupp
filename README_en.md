**English** | [中文](README.md)

# CCUPP - Chinese Common User Passwords Profiler

> A social engineering-based weak password dictionary generation tool

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://github.com/WangYihang/ccupp/actions/workflows/test.yaml/badge.svg)](https://github.com/WangYihang/ccupp/actions/workflows/test.yaml)

CCUPP is a social engineering-based weak password dictionary generation tool. It analyzes personal information (name, birthday, phone number, address, etc.) to intelligently generate possible weak password dictionaries.

## Features

- **Smart Pinyin Conversion**: Automatically converts Chinese names and locations to pinyin, initials, and title case
- **Rule-based Generation**: Generates passwords by priority (old password variants -> name+birthday -> name+phone -> combinations -> cultural numbers -> keyboard patterns)
- **Chinese Cultural Numbers**: Automatically combines culturally significant numbers like 520, 1314, 888, 666
- **Date Format Transforms**: Generates 10+ date variants from birthdays (19830924, 830924, 0924, 83-09-24, etc.)
- **Leetspeak Transforms**: Supports a->@, e->3, o->0, etc.
- **Password Filtering**: Filter by length and character type
- **Multiple Output Formats**: Supports txt and json output
- **Statistics**: `--stats` shows password length distribution
- **Interactive Mode**: Guided profile input
- **High Performance**: Iterator-based generation, memory efficient

## Installation

```bash
pip install ccupp
```

```bash
git clone https://github.com/WangYihang/ccupp.git
cd ccupp
uv sync
```

## Quick Start

### 1. Prepare Configuration File

```bash
# Generate example configuration
ccupp init

# Or use interactive mode
ccupp interactive
```

Manually create `config.yaml`:

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

### 2. Generate Passwords

```bash
# Basic usage
ccupp generate

# Output to file
ccupp generate -o passwords.txt

# Filter by length
ccupp generate --min-length 8 --max-length 16

# Show statistics
ccupp generate --stats

# JSON format
ccupp generate -f json -o passwords.json

# Disable certain strategies
ccupp generate --no-leetspeak --no-cultural --no-keyboard
```

## Configuration Reference

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `surname` | string | Surname | `李` |
| `first_name` | string | First name | `二狗` |
| `phone_numbers` | list[string] | Phone numbers | `['13512345678']` |
| `identity` | string | ID number | `'220281198309243953'` |
| `birthdate` | list[string] | Birthdate [year, month, day] | `['1983', '09', '24']` |
| `hometowns` | list[string] | Hometowns | `['四川', '成都']` |
| `places` | list[list[string]] | Places | `[['河北', '秦皇岛']]` |
| `social_media` | list[string] | Social media accounts | `['987654321']` |
| `workplaces` | list[list[string]] | Workplaces | `[['腾讯', 'tencent']]` |
| `educational_institutions` | list[list[string]] | Educational institutions | `[['清华大学', 'tsinghua']]` |
| `accounts` | list[string] | Account names | `['twodogs']` |
| `passwords` | list[string] | Old passwords | `['old_password']` |

## Password Generation Strategy

Passwords are output in priority order (most likely first):

1. **Old password variants**: Old password + case/leetspeak/suffix transforms
2. **Single component + suffix**: Name/phone/account + common suffixes (123, @, !!! etc.)
3. **Name + birthday**: The most common Chinese weak password pattern
4. **Name + phone/ID tail digits**
5. **Two-component combinations**: Any two categories of information combined
6. **Cultural number combinations**: Components + 520/1314/888/666 etc.
7. **Keyboard patterns**: qwerty/1qaz2wsx etc. + components

## Project Structure

```
ccupp/
├── ccupp/
│   ├── __main__.py          # CLI entry (Typer)
│   ├── models.py            # Profile data model (Pydantic)
│   ├── config.py            # YAML configuration loading
│   ├── generator.py         # Rule-based password generation engine
│   ├── extractors/
│   │   └── components.py    # Extract password components from Profile
│   ├── transforms/
│   │   ├── pinyin.py        # Chinese pinyin conversion
│   │   ├── date.py          # Date format transforms
│   │   ├── case.py          # Case transforms
│   │   └── leetspeak.py     # Leetspeak transforms
│   └── data/                # Example configuration files
├── tests/                   # pytest test suite
├── .github/workflows/       # CI/CD (test + release)
├── pyproject.toml
└── Dockerfile
```

## Tech Stack

- **Python 3.12+**
- **Typer** -- CLI framework
- **Pydantic** -- Data validation
- **pypinyin** -- Chinese pinyin conversion
- **PyYAML** -- Configuration parsing
- **Rich** -- Terminal formatting

## Development

```bash
git clone https://github.com/WangYihang/ccupp.git
cd ccupp
uv sync --dev
uv run pytest -v
```

## Contributing

Issues and Pull Requests are welcome!

## License

MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by [chinese-weak-password-generator](http://www.moonsec.com/post-181.html)
- Related research: [arXiv:2306.01545](https://arxiv.org/abs/2306.01545)

## Disclaimer

This tool is intended for security research and authorized security testing only. Users must comply with applicable laws and regulations. It must not be used for illegal purposes. The authors assume no responsibility for any misuse.
