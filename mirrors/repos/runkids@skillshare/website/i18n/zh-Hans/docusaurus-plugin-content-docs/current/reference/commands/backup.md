---
sidebar_position: 2
---

# backup

创建、列出并管理 target 目录的 Backup。

```bash
skillshare backup              # 备份所有 skill target
skillshare backup claude       # 备份指定 target
skillshare backup agents       # 备份所有 agent target
skillshare backup --all        # 备份 skills + agents
skillshare backup --list       # 列出所有 Backup
skillshare backup --cleanup    # 移除旧的 Backup
```

## 何时使用

- 在有风险的变更之前创建手动 Backup
- 列出现有 Backup 以检查恢复选项
- 清理旧的 Backup 以释放磁盘空间

## 自动 Backup

Backup 会在以下操作之前**自动**创建：
- `skillshare sync`（skill target 和 agent target）
- `skillshare sync agents`（仅 agent target）
- `skillshare target remove`

位置：`~/.local/share/skillshare/backups/<timestamp>/`（global）、`.skillshare/backups/`（project mode，仅 agents）

每次自动 Backup 之后都会自动应用 Retention 策略，使用与 `--cleanup` 相同的规则。你不需要手动清理快照。

## Commands

### 创建 Backup

```bash
skillshare backup              # 所有 target
skillshare backup claude       # 指定 target
skillshare backup --dry-run    # 预览
```

### 列出 Backup

```bash
skillshare backup --list
```

```
All backups (15.3 MB total)
  2026-01-20_15-30-00  claude, cursor     4.2 MB  ~/.local/share/.../2026-01-20_15-30-00
  2026-01-19_10-00-00  claude             2.1 MB  ~/.local/share/.../2026-01-19_10-00-00
  2026-01-18_09-00-00  claude, cursor     4.0 MB  ~/.local/share/.../2026-01-18_09-00-00
```

### 清理旧的 Backup

```bash
skillshare backup --cleanup           # 移除旧的 Backup
skillshare backup --cleanup --dry-run # 预览清理效果
```

默认清理策略：
- 保留最近 10 个 Backup
- 移除超过 30 天的 Backup
- 总大小上限为 500 MB

即使最新的快照单独就超过了大小上限，它也始终会被保留——你永远不会失去恢复点。

这个策略在每次 `sync` 之后都会自动运行，因此 `--cleanup` 只在你想按需清理时才需要用到。

## Options

| Flag | 说明 |
|------|------|
| `--all` | 同时备份 skills 和 agents |
| `--project, -p` | 使用 project mode（`.skillshare/backups/`）；**仅限 agents** |
| `--global, -g` | 使用 global mode（skills 的默认值） |
| `--list, -l` | 列出所有 Backup |
| `--cleanup, -c` | 移除旧的 Backup |
| `--target, -t <name>` | 针对指定 target 备份（作为位置参数的替代方式） |
| `--dry-run, -n` | 预览而不做任何变更 |

`backup` 还接受一个位置形式的 kind 参数：`skillshare backup agents` 会把备份范围限定为仅 agent target。

## Backup 结构

```
~/.local/share/skillshare/backups/
├── 2026-01-20_15-30-00/
│   ├── claude/
│   │   ├── skill-a/
│   │   └── skill-b/
│   └── cursor/
│       ├── skill-a/
│       └── skill-b/
└── 2026-01-19_10-00-00/
    └── claude/
        └── ...
```

存在的 skill 目录取决于该 target 的模式——参见 [What Gets Backed Up](#what-gets-backed-up)。

## What Gets Backed Up {#what-gets-backed-up}

一次 Backup 只保护 `sync` 可能会破坏的内容：**存在于 target、但不存在于你的 source 中的本地内容。**

- target 中的常规文件和目录会被备份
- merge 模式 target 中的逐个 skill symlink 会被**跳过**——它们指向你的 source（唯一的真实来源），本身已经是安全的。`skillshare sync` 会重新创建它们

这意味着：
- 在 merge 模式下：只有本地（非 symlink）的 skills 会被备份。被同步的 skills 存放在 source 中
- 在 copy 模式下：所有受管理的 skill 目录都会被备份（它们是真实文件）
- 在 symlink 模式下：不会备份任何内容（整个目录是一个 symlink）

如果一个 target 中只包含 symlink，则不会创建 Backup，`backup` 会报告没有需要做的事——一个空的恢复点没有意义。

## Backups & Disk Space {#backups--disk-space}

Backup 从不复制你的 source，因此它们一直很小。以下三种机制很容易混淆：

| 机制 | 范围 | 控制的内容 |
|-----------|-------|------------------|
| source 中的 `.gitignore` | 仅限 Git | Git 追踪的内容。被忽略的文件仍然存在于磁盘上 |
| `config.yaml` 中的 `ignore:` | `sync` | `sync` 复制到 target 的文件（主要是 copy 模式）。参见 [sync](/docs/reference/commands/sync) |
| Backup | 快照 | 仅限本地 target 内容——symlink 以及因此对应的 source 内容会被排除 |

因为 symlink 的 skills 不会被跟随，存放在 source skill 内部的重量级产物（模型权重、`.venv`、浏览器 profile、媒体文件）**永远不会**被复制进快照，无论 `.gitignore` 或 `ignore:` 是否提到它们。

Retention 会在每次 `sync` 之后自动运行，使用下方的默认策略。要手动查看用量：

```bash
du -sh ~/.local/share/skillshare/backups   # 磁盘上的总大小
skillshare backup --list                   # 每个快照的大小
skillshare backup --cleanup --dry-run      # 预览 Retention 会移除什么
```

Copy 模式的 target 是快照仍可能变大的唯一情形：它们是真实文件，因此某个 skill 目录下的任何内容都会被复制。请把运行时缓存和大型产物放在 skill 目录之外，或者用 `ignore:` 排除它们，避免它们一开始就到达 target。

## Agent Backup {#agent-backup}

Agents 有自己的 Backup 流程，与 skill Backup 并行运行，有两点值得注意的区别：

**条目命名。** Agent Backup 存储在每个 timestamp 目录内的 `<target>-agents/` 下，与 skill Backup 并列。例如，运行 `skillshare backup --all` 之后目录结构如下：

```
~/.local/share/skillshare/backups/2026-01-20_15-30-00/
├── claude/          # claude 的 skills 备份
├── claude-agents/   # claude 的 agents 备份
└── cursor/
```

**Project mode 与 skills 相反。** 在 project mode（`-p`）下，`backup` 会拒绝备份 skill target，但**会**备份 agent target。如果你忘了加 `agents` 过滤条件，会看到这样的错误：

```
backup is not supported in project mode (except for agents)
```

因此在 project mode 下，你必须使用 `skillshare backup -p agents` 或 `skillshare backup -p --all`。

```bash
skillshare backup agents                  # 所有 agent target（global）
skillshare backup agents claude           # 只备份 claude 的 agents
skillshare backup agents -p               # project 的 agent target
skillshare backup --all                   # 一次性备份 skills + agents
```

参见 [Agents](/docs/understand/agents) 了解 agent 资源模型，以及 [restore](/docs/reference/commands/restore) 了解恢复方式。

## 另请参阅

- [restore](/docs/reference/commands/restore) —— 从 Backup 恢复
- [sync](/docs/reference/commands/sync) —— 自动创建 Backup
- [target remove](/docs/reference/commands/target) —— 自动创建 Backup
