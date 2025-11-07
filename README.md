# CCUPP - Chinese Common User Passwords Profiler

> 基于社会工程学的弱口令密码字典生成工具

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

CCUPP 是一个基于社会工程学的弱口令密码字典生成工具，通过分析用户的个人信息（姓名、生日、电话、地址等），自动生成可能的弱口令密码字典。

## ✨ 特性

- 🔤 **智能拼音转换**：自动将中文姓名、地名等转换为拼音、首字母等多种形式
- 📝 **灵活配置**：支持 YAML 格式配置文件，可配置多个用户信息
- 🔄 **组合生成**：支持前缀、后缀、分隔符、模板等多种组合方式
- 🚀 **高性能**：使用迭代器生成，内存占用低，支持大规模密码生成
- ✅ **数据验证**：使用 Pydantic 进行配置验证，确保数据正确性
- 🎯 **去重处理**：自动去除重复密码，确保输出唯一

## 📦 安装

### 使用 uv（推荐）

```bash
# 克隆仓库
git clone https://github.com/WangYihang/ccupp.git
cd ccupp

# 安装依赖
uv sync
```

### 使用 pip

```bash
pip install -e .
```

## 🚀 快速开始

### 1. 准备配置文件

创建 `config.yaml` 文件，配置用户信息：

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
    - 高新区
  places:
    - - 河北
      - 秦皇岛
      - 北戴河
  social_media:
    - '987654321'
  workplaces:
    - - 腾讯
      - tencent
  educational_institutions:
    - - 清华大学
      - 清华
      - tsinghua
  accounts:
    - twodogs
  passwords:
    - old_password
```

### 2. 运行生成器

```bash
# 使用默认配置
python -m ccupp generate

# 指定配置文件
python -m ccupp generate --config my_config.yaml

# 自定义前缀和后缀
python -m ccupp generate --prefixes qwert 123 --suffixes @ 123 !!!
```

### 3. 查看输出

生成的密码会直接输出到标准输出，可以重定向到文件：

```bash
python -m ccupp generate > passwords.txt
```

## 📖 配置说明

配置文件支持多个用户，每个用户包含以下字段：

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
| `educational_institutions` | list[list[string]] | 教育机构列表 | `[['清华大学', '清华']]` |
| `accounts` | list[string] | 账号列表 | `['twodogs']` |
| `passwords` | list[string] | 旧密码列表（可选） | `['old_password']` |

## 🎛️ 命令行选项

```bash
python -m ccupp generate [OPTIONS]
```

### 选项说明

- `--config, -c`: YAML 配置文件路径（默认: `config.yaml`）
- `--prefixes`: 前缀列表（默认: `['qwert', '123']`）
- `--suffixes`: 后缀列表（默认: `['', '123', '@', 'abc', '.', '123.', '!!!']`）
- `--delimiters`: 分隔符列表（默认: `['', '-', '.', '|', '_', '+', '#', '@']`）
- `--templates`: Jinja2 模板列表（默认: `['{{ prefix }}{{ combination }}{{ suffix }}']`）

### 使用示例

```bash
# 基本使用
python -m ccupp generate

# 自定义前缀和后缀
python -m ccupp generate \
  --prefixes qwert 123 \
  --suffixes @ 123 !!! \
  --delimiters - _ .

# 自定义模板
python -m ccupp generate \
  --templates "{{ combination }}{{ suffix }}" \
              "{{ prefix }}{{ combination }}"
```

## 📁 项目结构

```
ccupp/
├── ccupp/                 # 主包目录
│   ├── __init__.py       # 包初始化
│   ├── __main__.py       # 入口点
│   ├── cli.py            # 命令行接口
│   ├── config.py         # 配置加载
│   ├── generator.py      # 密码生成器
│   ├── models.py         # 数据模型
│   └── pinyin.py         # 拼音转换工具
├── config.yaml           # 配置文件示例
├── pyproject.toml        # 项目配置
└── README.md             # 项目文档
```

## 🔧 技术栈

- **Python 3.12+**: 现代 Python 特性支持
- **Typer**: 现代化的 CLI 框架
- **Pydantic**: 数据验证和配置管理
- **PyYAML**: YAML 配置文件解析
- **pypinyin**: 中文拼音转换
- **Jinja2**: 模板引擎
- **structlog**: 结构化日志

## 💡 工作原理

1. **信息提取**：从配置文件中读取用户个人信息
2. **拼音转换**：将中文信息转换为拼音、首字母等多种形式
3. **组件组合**：使用分隔符、前缀、后缀等组合组件
4. **模板渲染**：使用 Jinja2 模板生成最终密码
5. **去重输出**：自动去除重复密码，确保输出唯一

## 📝 示例输出

```
liergou
Liergou
13512345678
19830924
sichuan
chengdu
gaoxinqu
Sichuan
Chengdu
Gaoxinqu
qinhuangdao
beidaihe
Qinhuangdao
Beidaihe
987654321
tengxun
Tengxun
tencent
Tencent
qinghuadaxue
Qinghuadaxue
qinghua
Qinghua
tsinghua
Tsinghua
twodogs
Twodogs
liergou123
Liergou123
13512345678123
...
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- 参考了 [chinese-weak-password-generator](http://www.moonsec.com/post-181.html) 的设计思路
- 相关研究：[arXiv:2306.01545](https://arxiv.org/abs/2306.01545)

## ⚠️ 免责声明

本工具仅用于安全研究和授权的安全测试。使用者需遵守相关法律法规，不得用于非法用途。作者不对任何误用行为承担责任。
