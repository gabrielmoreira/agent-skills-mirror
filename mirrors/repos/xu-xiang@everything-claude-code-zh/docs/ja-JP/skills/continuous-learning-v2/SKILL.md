---
name: continuous-learning-v2
description: 一种基于本能（Instinct）的训练系统，通过钩子（Hooks）观察会话，创建带有置信度评分的原子化本能，并将其进化为技能（Skills）、命令（Commands）或智能体（Agents）。
version: 2.0.0
---

# 持续学习（Continuous Learning）v2 - 基于本能（Instinct）的架构

这是一款先进的学习系统，能够通过带有置信度评分的小型已学习行为——“本能（Instinct）”，将 Claude Code 会话转化为可重用的知识。

## v2 新特性

| 特性 | v1 | v2 |
|---------|----|----|
| 观察（Observation） | Stop 钩子（会话结束时） | PreToolUse/PostToolUse（100% 可靠性） |
| 分析 | 主上下文（Main Context） | 后台智能体（Background Agent, Haiku） |
| 粒度 | 完整的技能（Skill） | 原子化“本能（Instinct）” |
| 置信度 | 无 | 0.3-0.9 加权 |
| 进化 | 直接转化为技能 | 本能 → 聚类 → 技能/命令/智能体 |
| 共享 | 无 | 本能导出/导入 |

## 本能模型（Instinct Model）

本能（Instinct）是小型且已学习的行为：

```yaml
---
id: prefer-functional-style
trigger: "when writing new functions"
confidence: 0.7
domain: "code-style"
source: "session-observation"
---

# 优先使用函数式风格

## Action
在合适的情况下，优先使用函数式模式而非类（Class）。

## Evidence
- 观察到 5 次优先使用函数式模式
- 用户在 2025-01-15 将基于类的方法修正为函数式
```

**属性：**
- **原子化（Atomic）** — 一个触发器，一个动作。
- **置信度加权（Confidence Weighting）** — 0.3 = 暂定，0.9 = 几乎确定。
- **领域标签（Domain Tagged）** — 如 `code-style`、`testing`、`git`、`debugging`、`workflow` 等。
- **基于证据（Evidence-based）** — 跟踪创建该本能的观察记录。

## 工作原理

```
会话活动（Session Activity）
      │
      │ 钩子捕获提示词 + 工具调用（100% 可靠性）
      ▼
┌─────────────────────────────────────────┐
│         observations.jsonl              │
│   (prompts, tool calls, outcomes)       │
└─────────────────────────────────────────┘
      │
      │ 观察者智能体（Observer Agent）读取（后台运行，Haiku）
      ▼
┌─────────────────────────────────────────┐
│              模式检测                   │
│   • 用户修正 → 本能                     │
│   • 错误解决 → 本能                     │
│   • 重复工作流 → 本能                   │
└─────────────────────────────────────────┘
      │
      │ 创建/更新
      ▼
┌─────────────────────────────────────────┐
│         instincts/personal/             │
│   • prefer-functional.md (0.7)          │
│   • always-test-first.md (0.9)          │
│   • use-zod-validation.md (0.6)         │
└─────────────────────────────────────────┘
      │
      │ /evolve 聚类
      ▼
┌─────────────────────────────────────────┐
│              evolved/                   │
│   • commands/new-feature.md             │
│   • skills/testing-workflow.md          │
│   • agents/refactor-specialist.md       │
└─────────────────────────────────────────┘
```

## 快速入门

### 1. 启用观察钩子（Observation Hooks）

添加到 `~/.claude/settings.json` 中。

**作为插件安装时**（推荐）：

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "${CLAUDE_PLUGIN_ROOT}/skills/continuous-learning-v2/hooks/observe.sh pre"
      }]
    }],
    "PostToolUse": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "${CLAUDE_PLUGIN_ROOT}/skills/continuous-learning-v2/hooks/observe.sh post"
      }]
    }]
  }
}
```

**在 `~/.claude/skills` 中手动安装时**：

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "~/.claude/skills/continuous-learning-v2/hooks/observe.sh pre"
      }]
    }],
    "PostToolUse": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "~/.claude/skills/continuous-learning-v2/hooks/observe.sh post"
      }]
    }]
  }
}
```

### 2. 初始化目录结构

Python CLI 会自动创建，但你也可以手动创建：

```bash
mkdir -p ~/.claude/homunculus/{instincts/{personal,inherited},evolved/{agents,skills,commands}}
touch ~/.claude/homunculus/observations.jsonl
```

### 3. 使用本能命令

```bash
/instinct-status     # 显示带有置信度评分的已学习本能
/evolve              # 将相关的本能聚类为技能/命令
/instinct-export     # 导出本能以便共享
/instinct-import     # 从他人处导入本能
```

## 命令（Commands）

| 命令 | 说明 |
|---------|-------------|
| `/instinct-status` | 显示所有已学习的本能及其置信度 |
| `/evolve` | 将相关的本能聚类为技能/命令 |
| `/instinct-export` | 导出本能以便共享 |
| `/instinct-import <file>` | 从他人处导入本能 |

## 配置（Configuration）

编辑 `config.json`：

```json
{
  "version": "2.0",
  "observation": {
    "enabled": true,
    "store_path": "~/.claude/homunculus/observations.jsonl",
    "max_file_size_mb": 10,
    "archive_after_days": 7
  },
  "instincts": {
    "personal_path": "~/.claude/homunculus/instincts/personal/",
    "inherited_path": "~/.claude/homunculus/instincts/inherited/",
    "min_confidence": 0.3,
    "auto_approve_threshold": 0.7,
    "confidence_decay_rate": 0.05
  },
  "observer": {
    "enabled": true,
    "model": "haiku",
    "run_interval_minutes": 5,
    "patterns_to_detect": [
      "user_corrections",
      "error_resolutions",
      "repeated_workflows",
      "tool_preferences"
    ]
  },
  "evolution": {
    "cluster_threshold": 3,
    "evolved_path": "~/.claude/homunculus/evolved/"
  }
}
```

## 文件结构

```
~/.claude/homunculus/
├── identity.json           # 个人资料、技术水平
├── observations.jsonl      # 当前会话观察记录
├── observations.archive/   # 已处理的观察记录
├── instincts/
│   ├── personal/           # 自动学习的本能
│   └── inherited/          # 从他人处导入的本能
└── evolved/
    ├── agents/             # 生成的专项智能体
    ├── skills/             # 生成的技能
    └── commands/           # 生成的命令
```

## 与 Skill Creator 的集成

使用 [Skill Creator GitHub App](https://skill-creator.app) 会**同时**生成：
- 传统的 `SKILL.md` 文件（用于向后兼容）
- 本能集合（用于 v2 学习系统）

来自仓库分析的本能会带有 `source: "repo-analysis"` 标记，并包含源仓库 URL。

## 置信度评分（Confidence Scoring）

置信度会随着时间进化：

| 分数 | 含义 | 行为 |
|-------|---------|----------|
| 0.3 | 暂定 | 会被建议但不会强制执行 |
| 0.5 | 中等 | 在相关情况下应用 |
| 0.7 | 强 | 应用会被自动批准 |
| 0.9 | 几乎确定 | 核心行为 |

**置信度提升**的情况：
- 模式被重复观察到。
- 用户未对建议的行为进行修正。
- 来自其他源的类似本能匹配。

**置信度下降**的情况：
- 用户显式修正了行为。
- 长期未观察到该模式。
- 出现了矛盾的证据。

## 为什么在观察中使用钩子（Hooks）而不是技能（Skills）？

> “v1 依赖于技能进行观察。技能是概率性的，根据 Claude 的判断，其触发概率约为 50-80%。”

钩子（Hooks）是**100% 确定性**触发的。这意味着：
- 所有的工具调用都会被观察到。
- 模式不会被遗漏。
- 学习是全面的。

## 向后兼容性

v2 与 v1 完全兼容：
- 现有的 `~/.claude/skills/learned/` 技能仍然有效。
- Stop 钩子仍然会运行（但也会为 v2 提供数据）。
- 平滑迁移路径：支持两者并行运行。

## 隐私（Privacy）

- 观察记录保留在机器**本地**。
- 仅可导出**本能**（模式）。
- 实际的代码或对话内容不会被共享。
- 你可以控制导出的内容。

## 相关链接

- [Skill Creator](https://skill-creator.app) - 从仓库历史生成本能。
- Homunculus - v2 架构的灵感来源（原子化观察、置信度评分、本能进化流水线）。
- [The Longform Guide](https://x.com/affaanmustafa/status/2014040193557471352) - 持续学习章节。

---

*基于本能的学习：一次一次地观察，教会 Claude 你的模式。*
