# Custom Skills Guide / 自定义技能指南

BioClaw uses two skill directories for different purposes. This guide explains how to create your own.

BioClaw 使用两个技能目录，用途不同。本指南说明如何创建自定义技能。

---

## Two Skill Directories / 两个技能目录

| Directory | Purpose / 用途 | Audience / 受众 |
|-----------|----------------|-----------------|
| `container/skills/<name>/` | Loaded by the **chat agent** inside Docker containers. These guide how the agent handles user requests (e.g., run BLAST, plot data, query databases). | End users via chat 终端用户 |
| `.claude/skills/<name>/` | Used by **Claude Code** when working on the repo. These teach Claude how to modify the codebase (e.g., add a channel, set up integrations). | Developers 开发者 |

**简而言之：**
- `container/skills/` = agent 运行时用的技能（生物信息分析、数据库查询等）
- `.claude/skills/` = 开发者用 Claude Code 改代码时用的技能（添加通道、配置集成等）

---

## Creating a Runtime Skill / 创建运行时技能

Runtime skills live in `container/skills/` and are automatically synced into agent containers.

运行时技能放在 `container/skills/`，会自动同步到 agent 容器中。

### File Structure / 文件结构

```
container/skills/my-skill/
├── SKILL.md                    # Required — main skill file (必需)
├── technical_reference.md      # Optional — detailed reference (可选)
└── commands_and_thresholds.md  # Optional — commands and parameters (可选)
```

### SKILL.md Format / 格式

```markdown
---
name: my-skill
description: Short description of when to use this skill. Triggers on "keyword1", "keyword2".
---

# My Skill

## When to Use

- User asks to do X
- User provides Y and wants Z

## How to Execute

### Step 1 — Validate input
...

### Step 2 — Run analysis
\```bash
some-command --flag input.txt -o output.txt
\```

### Step 3 — Return results
...

## Output Format

Describe expected outputs and where they go.
```

### Key Rules / 关键规则

1. **Keep it flat** — Only root-level files are synced. Nested directories (`references/`, `lib/`) will **not** be copied into the container.

   **保持扁平** — 只有根级文件会被同步，嵌套目录不会被复制到容器中。

2. **SKILL.md is required** — The `name` and `description` in the frontmatter tell the agent when to use this skill.

   **SKILL.md 是必需的** — frontmatter 中的 `name` 和 `description` 告诉 agent 何时使用此技能。

3. **Write clear triggers** — The `description` field is how the agent matches user requests to skills. Be specific about keywords and use cases.

   **写清楚触发条件** — `description` 字段决定了 agent 如何将用户请求匹配到技能。

4. **No code dependencies** — Skills are markdown guidance, not executable code. They tell the agent *how* to use tools already installed in the container.

   **不要依赖额外代码** — 技能是 markdown 指导文档，不是可执行代码。它们告诉 agent 如何使用容器中已安装的工具。

5. **Don't modify source code** — A runtime skill PR should only add files under `container/skills/`.

   **不要修改源代码** — 运行时技能的 PR 只应添加 `container/skills/` 下的文件。

### Example: Existing Skills / 现有技能示例

| Skill | What it does |
|-------|-------------|
| `blast-search` | Guides BLAST sequence similarity searches |
| `pubmed-search` | Guides PubMed literature search and summary |
| `query-uniprot` | Guides UniProt protein database queries |
| `differential-expression` | Guides PyDESeq2 differential expression analysis |
| `scrna-preprocessing-clustering` | Guides scanpy scRNA-seq preprocessing |
| `structural-biology` | Guides PyMOL protein structure rendering |

Browse `container/skills/` for more examples.

浏览 `container/skills/` 查看更多示例。

---

## Creating a Developer Skill / 创建开发者技能

Developer skills live in `.claude/skills/` and are used by Claude Code when developers run slash commands on the repo.

开发者技能放在 `.claude/skills/`，开发者在 repo 上运行斜杠命令时由 Claude Code 使用。

### File Structure / 文件结构

```
.claude/skills/my-dev-skill/
└── SKILL.md    # Instructions for Claude Code
```

### SKILL.md Format / 格式

```markdown
---
name: my-dev-skill
description: What this skill does and when to invoke it.
---

# My Dev Skill

## What This Does
Explain the modification this skill makes to the codebase.

## Implementation Steps
1. Step one...
2. Step two...
3. Step three...

## What This Must Not Change
- List files/systems that should not be touched
```

### Example: Existing Developer Skills / 现有开发者技能

| Skill | What it does |
|-------|-------------|
| `setup` | First-time installation and configuration |
| `add-telegram` | Adds Telegram as a messaging channel |
| `add-gmail` | Adds Gmail integration |
| `customize` | General-purpose customization guidance |
| `debug` | Troubleshooting container and connection issues |
| `add-omics-runtime-pack` | Installs 8 omics runtime skills |

---

## Contributing Skills / 贡献技能

To contribute a skill via PR:

通过 PR 贡献技能：

1. **Runtime skill** — Add files under `container/skills/<your-skill>/`. Do not modify any source code.

   **运行时技能** — 在 `container/skills/<your-skill>/` 下添加文件，不要修改源代码。

2. **Developer skill** — Add files under `.claude/skills/<your-skill>/`. Do not modify source code — your skill should contain *instructions* that Claude follows.

   **开发者技能** — 在 `.claude/skills/<your-skill>/` 下添加文件，不要修改源代码。技能应包含 Claude 遵循的*指令*。

3. **Test before submitting** — Run your skill on a fresh clone to make sure it works.

   **提交前测试** — 在全新 clone 上运行你的技能确保可用。

See [CONTRIBUTING.md](../CONTRIBUTING.md) for the full contribution guidelines.

详见 [CONTRIBUTING.md](../CONTRIBUTING.md) 了解完整的贡献指南。
