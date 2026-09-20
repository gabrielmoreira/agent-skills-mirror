---
sidebar_position: 2
---

# extras

管理与 Skill 一起同步的非 Skill 资源（rules、commands、prompts 等）。

## 概述

Extras 是 skillshare 管理的额外资源类型 —— 可以把它们理解为"给非 Skill 内容用的 Skill"。常见用例包括在各工具间同步 AI rules、编辑器 commands 或 prompt 模板。

每个 extra 都有：
- 一个**名称**（例如 `rules`、`prompts`、`commands`）
- 一个**source 目录** —— 可通过 `extras_source` 或每个 extra 各自的 `source` 配置，默认为 `~/.config/skillshare/extras/<name>/`（global）或 `.skillshare/extras/<name>/`（project）
- 一个或多个用于同步文件的 **target**

## 命令

### `extras init`

创建一个新的 extra 资源类型。

```bash
# 交互式向导
skillshare extras init

# CLI flags
skillshare extras init <name> --target <path> [--target <path2>] [--mode <mode>]
```

**Options:**

| Flag | Description |
|------|-------------|
| `--target <path>` | Target 目录路径（可重复） |
| `--mode <mode>` | Sync mode：`merge`（默认）、`copy` 或 `symlink` |
| `--flatten` | 将子目录中的文件直接同步到 target 根目录（不能与 `symlink` mode 一起使用） |
| `--source <path>` | 该 extra 的自定义 source 目录（覆盖 `extras_source` 和默认值；**仅 global mode**） |
| `--force` | 如果 extra 已存在则覆盖 |
| `--no-tui` | 跳过交互式向导，仅使用 CLI flags |
| `--project, -p` | 在 project 配置（`.skillshare/`）中创建 |
| `--global, -g` | 在 global 配置中创建 |

:::note
`--source` 仅在 global mode 下支持。Project mode 始终使用 `.skillshare/extras/<name>/` 作为 source 目录。
:::

**Examples:**

```bash
# 将 rules 同步到 Claude 和 Cursor
skillshare extras init rules --target ~/.claude/rules --target ~/.cursor/rules

# 使用自定义 source 目录
skillshare extras init rules --target ~/.claude/rules --source ~/company-shared/rules

# 用新的 targets 覆盖一个已存在的 extra
skillshare extras init rules --target ~/.cursor/rules --force

# project 范围的 extra，使用 copy mode
skillshare extras init prompts --target .claude/prompts --mode copy -p

# 以扁平方式同步 agents（像 Claude Code 这样的工具只能发现扁平文件）
skillshare extras init agents --target ~/.claude/agents --flatten
```

### `extras list`

列出所有已配置的 extras 及其同步状态。默认启动交互式 TUI。

```bash
skillshare extras list [--json] [--no-tui] [-p|-g]
```

**Options:**

| Flag | Description |
|------|-------------|
| `--json` | JSON 输出（包含 `source_type`：`per-extra` / `extras_source` / `default`，以及设置时的每个 target 的 `extension` 字段） |
| `--no-tui` | 禁用交互式 TUI，使用纯文本输出 |
| `--project, -p` | 使用 project-mode extras（`.skillshare/`） |
| `--global, -g` | 使用 global extras（`~/.config/skillshare/`） |

#### 交互式 TUI

该 TUI 提供左右分栏界面，左侧是 extras 列表，右侧是详情面板。按键说明：

| Key | Action |
|-----|--------|
| `↑↓` | 浏览列表 |
| `/` | 按名称筛选 |
| `Enter` | 内容查看器（浏览 source 文件） |
| `N` | 创建新 extra |
| `X` | 移除 extra（需确认） |
| `S` | 将 extra 同步到 target |
| `C` | 从 target 收集 |
| `M` | 更改某个 target 的 sync mode |
| `F` | 切换某个 target 的 flatten 开关 |
| `Ctrl+U/D` | 滚动详情面板 |
| `q` / `Ctrl+C` | 退出 |

每行的颜色条反映聚合同步状态：cyan（青色）= 全部已同步，黄色 = 存在差异，红色 = 未同步，灰色 = 无 source。

对于具有多个 target 的 extras，`S`、`C`、`M`、`F` 会打开 target 子菜单。`S` 和 `C` 允许一次选择所有 target；`M` 和 `F` 需要选定具体的 target。

可以通过 `skillshare tui off` 永久禁用该 TUI。

#### 纯文本输出

当 TUI 被禁用时（通过 `--no-tui`、`skillshare tui off`，或输出被管道传递）：

```
$ skillshare extras list --no-tui

Extras
─────────────────────────────────────────
→ rules  ~/.config/skillshare/extras/rules/ · 2 files
  ✓ ~/.claude/rules  merge
  ✓ ~/.cursor/rules  copy

→ codex-agents  ~/.config/skillshare/agents · 3 files
  ✓ ~/.codex/agents  extension: codex-agents
```

已同步的行只显示图标、路径和 mode；未同步的行会附加一个状态词（`drift`、`not synced`、`no source`）。带有 transform extension 的 target 会显示为 `extension: <name>`，取代 sync mode 的位置（其底层 mode 始终是 `copy`）。

### `extras source`

显示或设置全局 `extras_source` 目录。这是存放 extras source 文件的默认父目录。

```bash
skillshare extras source            # 显示当前值
skillshare extras source <path>     # 设置新值
```

不带参数时，显示当前的 `extras_source` 路径（若为自动检测则显示 `(default)`）。带路径参数时，更新 global 配置中的 `extras_source`。

:::note
此命令仅限 global 使用。Project mode 始终使用 `.skillshare/extras/`，不支持 `extras_source`。
:::

**Examples:**

```bash
# 显示当前的 extras_source
skillshare extras source

# 设置为共享目录
skillshare extras source ~/company-shared/extras
```

### 操作一个已存在的 extra

通过 `extras <name>` 上的 flags 更改某个 target 的 sync mode 或 flatten 设置，或添加/移除一个 target —— 均为纯配置操作；之后运行 `skillshare sync extras` 以将更改应用到磁盘。

```bash
skillshare extras <name> --mode <mode> [--target <path>] [-p|-g]
skillshare extras <name> --flatten | --no-flatten [--target <path>]
skillshare extras <name> --add-target <path> [--mode <mode>] [--flatten] [-p|-g]
skillshare extras <name> --remove-target <path> [--prune] [-p|-g]
```

**Options:**

| Flag | Description |
|------|-------------|
| `--mode <mode>` | 新的 sync mode：`merge`、`copy` 或 `symlink` |
| `--flatten` | 启用 flatten（将子目录文件同步到 target 根目录） |
| `--no-flatten` | 禁用 flatten |
| `--add-target <path>` | 为该 extra 添加一个新 target |
| `--remove-target <path>` | 从该 extra 中移除一个 target（默认仅修改配置） |
| `--prune` | 与 `--remove-target` 一起使用：同时删除该 target 下由 skillshare 管理的文件 |
| `--target <path>` | Target 目录路径（对多 target 的 extra 使用 `--mode` 时必填；省略时 `--flatten`/`--no-flatten` 会应用于所有 target） |
| `--project, -p` | 使用 project-mode extras（`.skillshare/`） |
| `--global, -g` | 使用 global extras（`~/.config/skillshare/`） |

**Examples:**

```bash
# 更改 rules 的 mode（单个 target — 自动解析）
skillshare extras rules --mode copy

# 明确指定 target（多 target 的 extra 必填）
skillshare extras rules --mode copy --target ~/.claude/rules

# 一次性对所有 target 启用 / 禁用 flatten
skillshare extras agents --flatten
skillshare extras agents --no-flatten

# 为已存在的 extra 添加一个新 target（然后 sync）
skillshare extras rules --add-target ~/.cursor/rules
skillshare extras commands --add-target ~/.config/opencode/commands --mode copy

# 移除一个 target（保留已同步的文件）
skillshare extras rules --remove-target ~/.cursor/rules

# 移除一个 target 并删除其已同步的文件
skillshare extras rules --remove-target ~/.cursor/rules --prune
```

也可以通过 TUI（`M` 键）和 Web UI（每个 target 上的 mode 下拉菜单和 flatten 复选框）进行操作。

### `extras remove`

从配置中移除一个 extra。

```bash
skillshare extras remove <name> [--force] [-p|-g]
```

Source 文件和已同步的 target 不会被删除 —— 只会移除配置条目。

### `extras collect`

将 target 上的本地文件收集回 extras source 目录。文件会被复制到 source，并替换为 symlink。

```bash
skillshare extras collect <name> [--from <path>] [--dry-run] [-p|-g]
```

**Options:**

| Flag | Description |
|------|-------------|
| `--from <path>` | 要从中收集的 target 目录（有多个 target 时必填） |
| `--dry-run` | 显示将会收集的内容而不做任何更改 |

**Example:**

```bash
# 从 Claude 收集 rules 回 source
skillshare extras collect rules --from ~/.claude/rules

# 预览将会收集的内容
skillshare extras collect rules --from ~/.claude/rules --dry-run
```

---

## Sync Mode

| Mode | Behavior |
|------|----------|
| `merge`（默认） | 从 target 到 source 的按文件 symlink |
| `copy` | 按文件复制 |
| `symlink` | 整个目录的 symlink |

切换 mode 时（例如从 `merge` 切换到 `copy`），下一次 `sync` 会自动将已有的 symlink 替换为新 mode 的格式。无需 `--force` —— symlink 始终可以安全替换。本地创建的普通文件需要 `--force` 才能被覆盖。

---

## Flatten

某些 AI 工具（例如 Claude Code 的 `/agents`）只在其配置目录的**顶层**发现文件 —— 它们不会递归进入子目录。如果你的 extras source 使用子目录来组织内容，同步后的文件对该工具而言将不可见。

`flatten` 选项通过将所有文件直接同步到 target 根目录来解决这个问题，无论它们在 source 中位于哪一层子目录：

```yaml
extras:
  - name: agents
    targets:
      - path: ~/.claude/agents
        flatten: true
```

**Behavior:**
- `flatten: true`：`source/curriculum/tactician.md` → `target/tactician.md`
- `flatten: false`（默认）：`source/curriculum/tactician.md` → `target/curriculum/tactician.md`

**文件名冲突：** 当两个位于不同子目录的文件同名时（例如 `team-a/agent.md` 和 `team-b/agent.md`），第一个文件生效（按路径字母顺序排序）。后续的冲突会被跳过并给出警告。

**Constraints:**
- 仅适用于 `merge` 和 `copy` mode —— 不能与 `symlink` mode 一起使用
- `collect` 会将新收集的文件放在 source 根目录（新文件不做子目录映射）

---

## Extension 转换

有些工具不读取 markdown。Gemini CLI 需要 TOML commands；Codex CLI 需要 TOML agents。target 上的 `extension` 字段会在 sync 期间运行一个外部脚本，将每个 source 文件转换为该 target 的原生格式。

```yaml
extras:
  - name: commands
    targets:
      - path: .claude/commands        # no extension — synced as-is
      - path: .gemini/commands
        extension: gemini-commands           # transform during sync
```

**Resolution** —— 裸名称会解析到 extensions 目录下（global 为 `~/.config/skillshare/extensions/<name>`，project 为 `.skillshare/extensions/<name>`）；路径（`./x.sh`、`/abs/x`）会被直接使用。

**Copy semantics** —— `extension` 隐含 `copy` mode。在带有 `extension` 的 target 上设置 `mode: merge` 或 `mode: symlink` 会报错。

**One-way** —— transform 只从 source 运行到 target。`extras collect` 会跳过带 extension 的 target。

**Overwrite safety** —— 生成的输出遵循与 `copy` mode 相同的冲突规则。输出路径上遗留的 symlink 会被自动替换；你在本地创建的现有普通文件或目录会被保留并跳过，除非传入 `--force`（使用 `--force` 时，冲突的目录会被生成的文件整体替换）。

### Extension 目录结构

单个可执行文件，或带 manifest 的目录：

```
.skillshare/extensions/gemini-commands/
├── extension.yaml
├── convert.js        # mapping rules you edit
└── md-toml.js        # helper for markdown/frontmatter/TOML
```

`extension.yaml`：

```yaml
run: ["node", "convert.js"]      # explicit command (argv), execed directly
output_ext: toml                  # .md → .toml; omit to keep the source extension
description: "Markdown command → Gemini CLI TOML"
```

没有 manifest 的裸单文件可执行程序会被直接执行（在 Unix 上依赖 shebang），并保留 source 的扩展名。需要改变扩展名的 transform 必须使用目录形式。

### 执行约定

- Source 文件内容通过 **stdin** 传入，脚本将转换后的内容写到 **stdout**。
- 环境变量：`SS_SRC_PATH`、`SS_REL_PATH`（相对于 source 根目录的路径 —— 对 Gemini 的 `/namespace:command` 命名很有用）、`SS_TARGET_DIR`、`SS_MODE`。
- 非零退出码会将该文件标记为失败；其他文件继续处理。

### 跨平台

该机制本身是跨平台的；某个 extension 能否运行取决于它的解释器。由于 `run` 是一个显式命令，用 `node` 或 `python3` 编写的 extension 可以在 Windows、macOS 和 Linux 上运行。纯 `bash` 脚本只能在有 shell 的环境中运行（Unix，或带 Git Bash 的 Windows）。Node 是参考 extensions 首选的解释器，因为它在各平台上都能统一提供。

### 参考 Extension

skillshare 仓库在 `extensions/` 下提供了示例 extensions（`gemini-commands`、`codex-agents`）。将其中一个复制到你的 extensions 目录并按需调整 —— 它们是参考实现，不会自动安装。每个参考 extension 都让 `convert.js` 保持简短，你只需编辑字段映射；`md-toml.js` 负责读取 markdown、解析简单的 frontmatter 并写出 TOML。

### Recipe: Codex agents

Codex CLI 需要 TOML agents 而非 markdown。由于 `source` 可以指向任意目录，你可以把你的 agents source 复用为 extras source，并用 `codex-agents` 进行转换：

```yaml
extras:
  - name: codex-agents
    source: ~/.config/skillshare/agents   # reuse the agents source
    targets:
      - path: ~/.codex/agents
        extension: codex-agents
```

`skillshare sync extras` 会将每个 `<agent>.md` 转换为 `~/.codex/agents/<agent>.toml`，映射 frontmatter 中的 `name`、`description` 和 `model`，并将 markdown 正文折叠进 `developer_instructions`（其他 frontmatter 字段会被丢弃）。[Codex custom agent schema](https://developers.openai.com/codex/subagents#custom-agent-file-schema) 要求 `name`、`description` 和 `developer_instructions`，因此当解析出的 name、description 或 Markdown 正文为空时，参考 transform 会报出明确的错误。不需要单独再复制一份 agents。

---

## Recipe：在多个 Agent 之间共享指令

现在大多数 coding agent 都会读取一个用于常驻指令的 `AGENTS.md`，但每个 agent 都把自己的用户级副本保存在不同的目录中。一个带有多个 target 的 extra，就能把同一个 source 文件分发到所有这些目录：

```bash
skillshare extras init instructions \
  --target ~/.codex \
  --target ~/.config/opencode \
  --target ~/.claude \
  --target ~/.gemini \
  --no-tui
```

把你的 `AGENTS.md` 放到解析出的 source 目录中
（默认是 `~/.config/skillshare/extras/instructions/`），然后运行
`skillshare sync extras`。

| Agent | Global path | Reads `AGENTS.md` |
|-------|-------------|-------------------|
| Codex CLI | `~/.codex/AGENTS.md` | 直接读取 |
| opencode | `~/.config/opencode/AGENTS.md` | 直接读取 |
| Claude Code | `~/.claude/AGENTS.md` | 通过 `CLAUDE.md` import |
| Antigravity | `~/.gemini/AGENTS.md` | 通过 `GEMINI.md` import |

有两个 agent 在用户级别读取各自固定的文件名，因此每个都需要在被同步的文件旁边放一个一行文件。这些文件只需写一次；skillshare 之后不会再碰它们：

```markdown title="~/.claude/CLAUDE.md"
@AGENTS.md
```

```markdown title="~/.gemini/GEMINI.md"
@AGENTS.md
```

Claude Code 读取的是 `CLAUDE.md` 而不是 `AGENTS.md`，而 import 正是它的[记忆文档](https://code.claude.com/docs/en/memory)推荐的与其他 agent 共享同一个文件的方式。Antigravity 将其全局 rules 保存在
`~/.gemini/GEMINI.md` 中，并相对于该 rules 文件自身所在目录解析相对的 `@filename`，因此同样的一行代码就能读取到同步过来的 `AGENTS.md`。`~/.gemini` 这个 target 同时也覆盖了同样读取该全局文件的 Antigravity CLI。

请将 source 文件保持命名为 `AGENTS.md`。一个中立的名字如 `memory.md` 同样可以正常同步，但会不再被读取：Codex 是按文件名拼接 `AGENTS.md` 文件的，且没有 import 语法，因此只有这个文件名才能被它识别。

由于 target 都是目录，每个 target 都会以 source 中的原始文件名接收每个文件。请让 source 目录只保留你想在所有地方都出现的文件 —— 多余的文件会同时出现在全部四个 target 中。

:::note
此 recipe 分享的是你自己写的指令，而不是 agent 自身写入的记忆。各 agent 会以私有格式存储自己的学习内容 —— Claude Code 是一个 Markdown 目录，Codex 是一个数据库，Cursor 是非文件存储 —— 这些内容无法通过在 target 之间复制文件来迁移。
:::

---

## 目录结构

```
~/.config/skillshare/
├── config.yaml          # extras config lives here
├── skills/              # skill source
└── extras/              # extras source root
    ├── rules/           # extras/rules/ source files
    │   ├── coding.md
    │   └── testing.md
    └── prompts/
        └── review.md
```

---

## 配置

在 `config.yaml` 中：

```yaml
# Optional: set a global default extras source directory
extras_source: ~/my-extras

extras:
  - name: rules
    source: ~/company-shared/rules    # optional per-extra override
    targets:
      - path: ~/.claude/rules
      - path: ~/.cursor/rules
        mode: copy
  - name: agents
    targets:
      - path: ~/.claude/agents
        flatten: true                  # sync subdirectory files flat
  - name: prompts
    targets:
      - path: ~/.claude/prompts
```

### Source 解析优先级

每个 extra 的 source 目录按三级优先顺序解析：

1. **每个 extra 各自的 `source`**（最高优先级）—— 精确路径，按原样使用
2. **`extras_source`** —— `<extras_source>/<name>/`
3. **默认值** —— `~/.config/skillshare/extras/<name>/`（global）或 `.skillshare/extras/<name>/`（project）

`extras list --json` 的输出包含一个 `source_type` 字段（`per-extra`、`extras_source` 或 `default`），指明路径是由哪一级解析出来的。

:::tip Auto-populated
当你运行 `skillshare init` 或用 `extras init` 创建你的第一个 extra 时，`extras_source` 会自动设置为默认路径（`~/.config/skillshare/extras/`）。之后如需更改，使用 `skillshare extras source <path>`。
:::

---

## 同步

Extras 通过以下方式同步：

```bash
skillshare sync extras        # sync extras only
skillshare sync --all         # sync skills + extras together
```

完整的同步文档（包括 `--json`、`--dry-run` 和 `--force` 选项）参见 [sync extras](/docs/reference/commands/sync#sync-extras)。

---

## 工作流程

```bash
# 1. 创建一个新的 extra
skillshare extras init rules --target ~/.claude/rules --target ~/.cursor/rules

# 1b. 或者使用自定义 source 目录
skillshare extras init rules --target ~/.claude/rules --source ~/my-rules

# 1c. 重新配置一个已存在的 extra（覆盖）
skillshare extras init rules --target ~/.cursor/rules --force

# 2. 向 source 目录添加文件
# (编辑解析出的 source 目录 — 可通过以下命令查看: skillshare extras list --json)

# 3. 同步到 target
skillshare sync extras

# 4. 列出状态（source_type 显示每个 extra 的 source 是从哪一级解析出来的）
skillshare extras list

# 5. 将在 target 中编辑过的文件收集回 source
skillshare extras collect rules --from ~/.claude/rules

# 6. 更改全局 extras source 目录
skillshare extras source ~/company-shared/extras
```

---

## 另请参阅

- [sync](/docs/reference/commands/sync#sync-extras) — 将 extras 同步到 target
- [status](/docs/reference/commands/status) — 显示 extras 的文件和 target 数量
- [Configuration](/docs/reference/targets/configuration#extras) — Extras 配置参考
