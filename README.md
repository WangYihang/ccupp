[English](README_en.md) | **中文**

# CCUPP - Chinese Common User Passwords Profiler

> 基于社会工程学的弱口令密码字典生成工具

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://github.com/WangYihang/ccupp/actions/workflows/test.yaml/badge.svg)](https://github.com/WangYihang/ccupp/actions/workflows/test.yaml)

CCUPP 是一个基于社会工程学的弱口令密码字典生成工具，通过分析用户的个人信息（姓名、生日、电话、地址等），智能生成可能的弱口令密码字典。

## 特性

- **智能拼音转换**：自动将中文姓名、地名等转换为拼音、首字母、首字母大写等多种形式
- **基于规则的生成**：按优先级生成密码（旧密码变体 → 姓名+生日 → 姓名+电话 → 组合 → 文化数字 → 键盘模式）
- **中国特色数字**：自动组合 520、1314、888、666 等文化含义数字
- **日期格式变换**：从生日自动生成 19830924、830924、0924、83-09-24 等十余种变体
- **Leetspeak 变换**：支持 a→@、e→3、o→0 等变换
- **密码过滤**：支持按长度、字符类型过滤
- **多输出格式**：支持 txt、json 格式输出
- **统计信息**：`--stats` 显示生成密码的长度分布
- **交互模式**：引导式输入用户信息
- **高性能**：迭代器生成，内存高效

## 安装

```bash
pip install ccupp
```

```bash
git clone https://github.com/WangYihang/ccupp.git
cd ccupp
uv sync
```

## 快速开始

### 1. 准备配置文件

```bash
# 自动生成示例配置
ccupp init

# 或使用交互模式
ccupp interactive
```

手动创建 `config.yaml`：

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

### 2. 生成密码

```bash
# 基本使用
ccupp generate

# 输出到文件
ccupp generate -o passwords.txt

# 过滤长度
ccupp generate --min-length 8 --max-length 16

# 查看统计
ccupp generate --stats

# JSON 格式
ccupp generate -f json -o passwords.json

# 禁用某些策略
ccupp generate --no-leetspeak --no-cultural --no-keyboard
```

## 配置说明

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

## 密码生成策略

密码按可能性优先级排序输出：

1. **旧密码变体**：旧密码 + 大小写/leetspeak/后缀变换
2. **单组件 + 后缀**：姓名/电话/账号 + 常见后缀（123, @, !!! 等）
3. **姓名 + 生日**：最常见的中国用户弱口令模式
4. **姓名 + 电话/身份证尾号**
5. **双组件组合**：任意两类信息的组合
6. **文化数字组合**：组件 + 520/1314/888/666 等
7. **键盘模式**：qwerty/1qaz2wsx 等 + 组件

## 项目结构

```
ccupp/
├── ccupp/
│   ├── __main__.py          # CLI 入口 (Typer)
│   ├── models.py            # Profile 数据模型 (Pydantic)
│   ├── config.py            # YAML 配置加载
│   ├── generator.py         # 基于规则的密码生成引擎
│   ├── extractors/
│   │   └── components.py    # 从 Profile 提取密码组件
│   ├── transforms/
│   │   ├── pinyin.py        # 中文拼音转换
│   │   ├── date.py          # 日期格式变换
│   │   ├── case.py          # 大小写变换
│   │   └── leetspeak.py     # Leetspeak 变换
│   └── data/                # 示例配置文件
├── tests/                   # pytest 测试套件
├── .github/workflows/       # CI/CD (test + release)
├── pyproject.toml
└── Dockerfile
```

## 技术栈

- **Python 3.12+**
- **Typer** — CLI 框架
- **Pydantic** — 数据验证
- **pypinyin** — 中文拼音转换
- **PyYAML** — 配置解析
- **Rich** — 终端美化

## 开发

```bash
git clone https://github.com/WangYihang/ccupp.git
cd ccupp
uv sync --dev
uv run pytest -v
```

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License. 详见 [LICENSE](LICENSE) 文件。

## 致谢

- 参考了 [chinese-weak-password-generator](http://www.moonsec.com/post-181.html) 的设计思路
- 相关研究：[arXiv:2306.01545](https://arxiv.org/abs/2306.01545)

## 免责声明

本工具仅用于安全研究和授权的安全测试。使用者需遵守相关法律法规，不得用于非法用途。作者不对任何误用行为承担责任。
