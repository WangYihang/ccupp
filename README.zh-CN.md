# PII2PW - Personal Information to Password Wordlists

> 基于社会工程学的弱口令密码字典生成工具

[English](README.md) · **简体中文**

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://github.com/WangYihang/pii2pw/actions/workflows/test.yaml/badge.svg)](https://github.com/WangYihang/pii2pw/actions/workflows/test.yaml)

PII2PW 把目标的个人信息——姓名、生日、电话、地点等——转换成一份按可能性排序的弱口令字典。

工具针对中文用户做了适配：姓名和地名会转成拼音，生日会展开成中国人实际会用的各种日期写法，并自动组合 520、1314 这类有文化含义的数字。

## 安装

```bash
pip install pii2pw
```

或作为独立命令行工具安装，与其他项目的依赖隔离：

```bash
uv tool install pii2pw
```

## 使用

在 `config.yaml` 里描述目标。`pii2pw init` 可以生成示例配置，`pii2pw interactive` 则引导你逐项填写：

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

然后生成：

```bash
pii2pw generate                                  # 输出到终端
pii2pw generate -o passwords.txt                 # 输出到文件
pii2pw generate --min-length 8 --max-length 16   # 按长度过滤
pii2pw generate -f json -o passwords.json        # JSON 格式
pii2pw generate --stats                          # 同时打印长度分布
```

输出按可能性从高到低排序，因此就算只取前 N 条，拿到的也是最值得尝试的 N 个。`pii2pw generate --help` 列出全部选项，包括关闭单个生成策略的开关。

## 配置字段

所有字段都是可选的——知道多少填多少。

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `surname` | string | 姓氏 | `李` |
| `first_name` | string | 名字 | `二狗` |
| `phone_numbers` | list[string] | 电话号码列表 | `['13512345678']` |
| `identity` | string | 身份证号 | `'220281198309243953'` |
| `birthdate` | list[string] | 出生日期 [年, 月, 日] | `['1983', '09', '24']` |
| `hometowns` | list[string] | 家乡列表 | `['四川', '成都']` |
| `places` | list[list[string]] | 地点列表 | `[['河北', '秦皇岛']]` |
| `social_media` | list[string] | 社交媒体账号 | `['987654321']` |
| `workplaces` | list[list[string]] | 工作单位列表 | `[['腾讯', 'tencent']]` |
| `educational_institutions` | list[list[string]] | 教育机构列表 | `[['清华大学', 'tsinghua']]` |
| `accounts` | list[string] | 账号列表 | `['twodogs']` |
| `passwords` | list[string] | 旧密码列表 | `['old_password']` |

一份配置文件可以写多个目标，生成结果会跨目标去重。

## 在 Python 中调用

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

`generate_passwords` 返回一个惰性迭代器，已排序并去重。它也接受一个 Profile 列表——`load_profiles('config.yaml')` 就能得到。完整选项见 `help(generate_passwords)`。

本包带有完整类型标注，并附 [PEP 561](https://peps.python.org/pep-0561/) `py.typed` 标记。

## 开发

```bash
git clone https://github.com/WangYihang/pii2pw.git
cd pii2pw
uv sync --dev
uv run pytest -v
```

欢迎提交 Issue 和 Pull Request。

## 许可证

MIT License. 详见 [LICENSE](LICENSE) 文件。

## 致谢

- 参考了 [chinese-weak-password-generator](http://www.moonsec.com/post-181.html) 的设计思路
- 相关研究：[arXiv:2306.01545](https://arxiv.org/abs/2306.01545)

## 免责声明

本工具仅用于安全研究和授权的安全测试。使用者需遵守相关法律法规，不得用于非法用途。作者不对任何误用行为承担责任。
