# Agent Skills 规范文档

## 概述

Agent Skills 是用于 AI Agent 的可复用技能包。每个技能以 `SKILL.md` 文件为核心，通过 YAML frontmatter 声明元数据，Markdown 正文描述执行逻辑。

## 文件结构

### 单层结构

```
skills/
└── my-skill/
    ├── SKILL.md          ← 核心文件（必需）
    ├── assets/           ← 静态资源（可选）
    └── references/       ← 参考文档（可选）
```

### 双重嵌套结构

```
skills/
└── my-skill/
    └── my-skill/
        ├── SKILL.md
        ├── assets/
        └── references/
```

两种结构均被验证工具支持。

## SKILL.md 格式

### YAML Frontmatter

文件必须以 YAML frontmatter 开头：

```yaml
---
name: my-skill
description: 一句话描述技能的用途和能力。
version: 1.0.0
author: your-name
tags:
  - productivity
  - automation
dependencies:
  - python>=3.8
license: MIT
---

# 技能标题

正文内容...
```

### 标准字段

| 字段 | 必填 | 类型 | 约束 | 说明 |
|------|------|------|------|------|
| `name` | 是 | string | `^[a-z][a-z0-9-]*$`, ≤64字符 | 技能唯一标识 |
| `description` | 是 | string | 10-500字符 | 技能描述 |
| `version` | 否 | string | semver 格式 | 版本号 |
| `author` | 否 | string | - | 作者 |
| `tags` | 否 | list[string] | - | 标签 |
| `dependencies` | 否 | list[string] | - | 依赖项 |
| `license` | 否 | string | - | 许可证 |

### 非标准字段

不在白名单中的字段（如 `dependency`、`homepage`）会产生**警告**，但不会导致验证失败。建议将非标准字段迁移到标准字段或移除。

## 正文规范

### 最低要求

- 至少 10 行内容
- 至少一个 `#` 标题
- 每个标题下应有实际内容（空标题会产生警告）

### 推荐结构

```markdown
# <技能标题>

## 任务目标
- 技能用途
- 能力范围
- 触发条件

## 使用方式
### 输入
### 输出

## 核心逻辑
### 步骤 1
### 步骤 2

## 注意事项

## 示例
```

### 命名规范

- **技能名**: 全小写，单词间用连字符 (`-`)，如 `code-review`
- **目录名**: 与技能名一致
- **标签**: 全小写，无空格

## 验证工具

使用内置验证工具检查技能是否符合规范：

```bash
# 验证所有技能
python tools/skill_validator.py validate

# 验证单个技能
python tools/skill_validator.py validate skills/my-skill
```

验证结果分为三种状态：
- ✅ **通过** — 无错误无警告
- ⚠️ **通过（有警告）** — 有非标准字段或空段落等
- ❌ **失败** — 缺少必填字段或格式不符
