# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## 仓库概述

Testany 公司的 Agent Skills 集合，为 Codex 提供产品研发流程中的专业技能。每个 skill 是独立的 plugin，包含 SKILL.md 和可选的 references/、scripts/、assets/ 资源。

## 开发方式

当前仓库已不再内置 `skill-creator` 初始化 / 校验 / 打包脚本。

- 新增或维护 skill 时，直接在对应 plugin 下编辑 `skills/<skill-name>/SKILL.md`
- 如需暴露 slash command，同步维护对应 plugin 的 `commands/`
- 发布前同步更新根目录 `README.md`、`.claude-plugin/marketplace.json`、plugin 级 `README.md` / `.claude-plugin/plugin.json` 与 `CHANGELOG.md`

## 架构

```
.claude-plugin/marketplace.json    # 插件注册与发现层描述
plugins/
├── testany-eng/                   # 研发流程工具集
├── testany-llm/                   # AI/LLM 工具集
├── testany-mrkt/                  # 营销内容工具集
└── testany-bot/                   # Testany 测试平台工具集
```

## Skill 编写规范

| 规范项 | 要求 |
|--------|------|
| 命名 | 英文 kebab-case |
| 必须文件 | SKILL.md |
| 行数限制 | < 500 行 |
| 语言 | 中文（技术术语可保留英文） |
| Frontmatter | 必须包含触发词 |
| 示例 | 必须有使用示例 |

## marketplace.json 结构

每个 skill 作为独立 plugin 注册，确保用户浏览时能看到各 skill 的描述：

```json
{
  "plugins": [
    {
      "name": "skill-name",
      "description": "触发词1、触发词2。功能描述。",
      "skills": ["./skills/skill-name"]
    }
  ]
}
```

## 文档维护

- 以仓库根目录 `README.md` 与各 plugin README 为对外说明事实源
- 以 `.claude-plugin/marketplace.json` 和各 plugin `plugin.json` 为安装发现层事实源
- 新增、删除或重命名 skill 后，必须同步更新上述文档与 `CHANGELOG.md`
