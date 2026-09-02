# 技能验证工具

Agent Skills 验证和转换工具集，用于检查 `SKILL.md` 文件是否符合规范。

## 快速开始

```bash
# 验证所有技能
python tools/skill_validator.py validate

# 验证单个技能
python tools/skill_validator.py validate skills/agent-team

# 读取技能属性
python tools/skill_validator.py read-properties skills/agent-team

# 输出 JSON 格式
python tools/skill_validator.py read-properties skills/agent-team --json

# 生成 XML prompt
python tools/skill_validator.py to-prompt skills/agent-team
```

## 验证规则

| 规则 | 级别 | 说明 |
|------|------|------|
| YAML frontmatter | 错误 | 必须以 `---` 开头和结尾 |
| name 字段 | 错误 | 必填，小写字母+数字+连字符 |
| description 字段 | 错误 | 必填，至少 10 字符 |
| 内容行数 | 错误 | 至少 10 行 |
| 至少一个标题 | 错误 | Markdown 必须包含 `#` 标题 |
| version 格式 | 警告 | 建议使用 semver 格式 |
| 非标准字段 | 警告 | 不在标准白名单中的字段 |
| 目录名匹配 | 警告 | 目录名应与 skill name 一致 |

## 目录结构支持

验证器自动识别两种目录结构：

```
# 单层结构
skills/skill-name/SKILL.md

# 双重嵌套结构
skills/skill-name/skill-name/SKILL.md
```

## 标准字段白名单

| 字段 | 必填 | 类型 | 说明 |
|------|------|------|------|
| `name` | 是 | string | 技能名（小写、连字符） |
| `description` | 是 | string | 技能描述 |
| `version` | 否 | string | 版本号 (semver) |
| `author` | 否 | string | 作者 |
| `tags` | 否 | list | 标签列表 |
| `dependencies` | 否 | list | 依赖列表 |
| `license` | 否 | string | 许可证 |

非标准字段（如 `dependency`、`homepage`）会产生警告，但不会导致验证失败。

## 模块说明

```
tools/
├── skill_validator.py          # 入口脚本
├── README.md                   # 本文件
└── skill_validator/
    ├── __init__.py             # 包导出
    ├── cli.py                  # CLI 命令
    ├── models.py               # 数据模型
    ├── parser.py               # YAML/Markdown 解析
    ├── validator.py            # 验证逻辑
    ├── prompt.py               # XML prompt 生成
    └── errors.py               # 错误类型
```
