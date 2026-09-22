---
sidebar_position: 2
---

# extras

管理與 skill 一起同步的非 skill 資源（rules、commands、prompts 等）。

## Overview

Extras 是 skillshare 管理的額外資源類型——可以把它想成「給非 skill 內容用的 skill」。常見的使用情境包含跨工具同步 AI rules、編輯器 commands，或 prompt 範本。

每個 extra 都有：
- 一個**名稱**（例如 `rules`、`prompts`、`commands`）
- 一個**source 目錄**——可透過 `extras_source` 或個別 extra 的 `source` 設定，預設為 `~/.config/skillshare/extras/<name>/`（global）或 `.skillshare/extras/<name>/`（project）
- 一個或多個檔案同步的 **target**

## Commands

### `extras init`

建立新的 extra 資源類型。

```bash
# 互動式精靈
skillshare extras init

# CLI 旗標
skillshare extras init <name> --target <path> [--target <path2>] [--mode <mode>]
```

**Options:**

| Flag | Description |
|------|-------------|
| `--target <path>` | Target 目錄路徑（可重複指定） |
| `--mode <mode>` | Sync 模式：`merge`（預設）、`copy`，或 `symlink` |
| `--flatten` | 將子目錄中的檔案直接同步到 target 根目錄（無法與 `symlink` 模式一起使用） |
| `--source <path>` | 此 extra 的自訂 source 目錄（會覆寫 `extras_source` 與預設值；**僅限 global mode**） |
| `--force` | 若 extra 已存在則覆寫 |
| `--no-tui` | 略過互動式精靈，只使用 CLI 旗標 |
| `--project, -p` | 在 project 設定中建立（`.skillshare/`） |
| `--global, -g` | 在 global 設定中建立 |

:::note
`--source` 只在 global mode 中支援。Project mode 一律使用 `.skillshare/extras/<name>/` 作為 source 目錄。
:::

**Examples:**

```bash
# 將 rules 同步到 Claude 與 Cursor
skillshare extras init rules --target ~/.claude/rules --target ~/.cursor/rules

# 使用自訂的 source 目錄
skillshare extras init rules --target ~/.claude/rules --source ~/company-shared/rules

# 用新的 target 覆寫既有的 extra
skillshare extras init rules --target ~/.cursor/rules --force

# 使用 copy 模式的 project 範圍 extra
skillshare extras init prompts --target .claude/prompts --mode copy -p

# 以扁平方式同步 agents（像 Claude Code 這類工具只會探索扁平的檔案）
skillshare extras init agents --target ~/.claude/agents --flatten
```

### `extras list`

列出所有已設定的 extras 及其同步狀態。預設會啟動互動式 TUI。

```bash
skillshare extras list [--json] [--no-tui] [-p|-g]
```

**Options:**

| Flag | Description |
|------|-------------|
| `--json` | JSON output（包含 `source_type`：`per-extra` / `extras_source` / `default`，以及設定時每個 target 的 `extension` 欄位） |
| `--no-tui` | 停用互動式 TUI，改用純文字輸出 |
| `--project, -p` | 使用 project mode 的 extras（`.skillshare/`） |
| `--global, -g` | 使用 global 的 extras（`~/.config/skillshare/`） |

#### Interactive TUI

TUI 提供分割面板介面，左側為 extras 清單，右側為詳細資訊面板。按鍵綁定如下：

| Key | Action |
|-----|--------|
| `↑↓` | 瀏覽清單 |
| `/` | 依名稱篩選 |
| `Enter` | 內容檢視器（瀏覽 source 檔案） |
| `N` | 建立新的 extra |
| `X` | 移除 extra（需確認） |
| `S` | 將 extra 同步到 target |
| `C` | 從 target 收集 |
| `M` | 變更某個 target 的 sync 模式 |
| `F` | 切換某個 target 的 flatten 開/關 |
| `Ctrl+U/D` | 捲動詳細資訊面板 |
| `q` / `Ctrl+C` | 離開 |

每一列的顏色列代表整體同步狀態：cyan（青色）= 全部已同步，yellow（黃色）= drift（有差異），red（紅色）= 未同步，gray（灰色）= 沒有 source。

對於有多個 target 的 extra，`S`、`C`、`M`、`F` 會開啟 target 子選單。`S` 與 `C` 可以一次選取所有 target；`M` 與 `F` 則必須選擇特定的 target。

可以用 `skillshare tui off` 永久停用 TUI。

#### Plain text output

當 TUI 被停用時（透過 `--no-tui`、`skillshare tui off`，或輸出被 pipe）：

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

已同步的列只會顯示圖示、路徑與模式；未同步的列則會附加狀態文字（`drift`、`not synced`、`no source`）。有 transform extension 的 target 會以 `extension: <name>` 取代 sync 模式標示（其底層模式一律是 `copy`）。

### `extras source`

顯示或設定全域的 `extras_source` 目錄。這是儲存 extras source 檔案的預設父目錄。

```bash
skillshare extras source            # 顯示目前的值
skillshare extras source <path>     # 設定新的值
```

不帶參數時，會顯示目前的 `extras_source` 路徑（若為自動偵測則附上 `(default)`）。帶路徑參數時，會更新 global 設定中的 `extras_source`。

:::note
此指令僅限 global。Project mode 一律使用 `.skillshare/extras/`，不支援 `extras_source`。
:::

**Examples:**

```bash
# 顯示目前的 extras_source
skillshare extras source

# 設定為共用目錄
skillshare extras source ~/company-shared/extras
```

### Operating on an existing extra

透過 `extras <name>` 上的旗標，變更某個 target 的 sync 模式或 flatten 設定，或新增/移除 target。這些操作只會變更設定；之後請執行 `skillshare sync extras` 才會套用到磁碟上。

```bash
skillshare extras <name> --mode <mode> [--target <path>] [-p|-g]
skillshare extras <name> --flatten | --no-flatten [--target <path>]
skillshare extras <name> --add-target <path> [--mode <mode>] [--flatten] [-p|-g]
skillshare extras <name> --remove-target <path> [--prune] [-p|-g]
```

**Options:**

| Flag | Description |
|------|-------------|
| `--mode <mode>` | 新的 sync 模式：`merge`、`copy`，或 `symlink` |
| `--flatten` | 啟用 flatten（將子目錄檔案同步到 target 根目錄） |
| `--no-flatten` | 停用 flatten |
| `--add-target <path>` | 為此 extra 新增一個 target |
| `--remove-target <path>` | 從此 extra 移除一個 target（預設僅變更設定） |
| `--prune` | 搭配 `--remove-target` 使用：同時刪除該 target 底下由 skillshare 管理的檔案 |
| `--target <path>` | Target 目錄路徑（多 target 的 extra 使用 `--mode` 時為必填；省略時 `--flatten`/`--no-flatten` 會套用到所有 target） |
| `--project, -p` | 使用 project mode 的 extras（`.skillshare/`） |
| `--global, -g` | 使用 global 的 extras（`~/.config/skillshare/`） |

**Examples:**

```bash
# 變更 rules 模式（單一 target — 自動解析）
skillshare extras rules --mode copy

# 明確指定 target（多 target 的 extra 需要）
skillshare extras rules --mode copy --target ~/.claude/rules

# 一次啟用／停用所有 target 的 flatten
skillshare extras agents --flatten
skillshare extras agents --no-flatten

# 為既有的 extra 新增一個 target（之後再 sync）
skillshare extras rules --add-target ~/.cursor/rules
skillshare extras commands --add-target ~/.config/opencode/commands --mode copy

# 移除一個 target（保留已同步的檔案）
skillshare extras rules --remove-target ~/.cursor/rules

# 移除一個 target 並刪除其已同步的檔案
skillshare extras rules --remove-target ~/.cursor/rules --prune
```

也可以透過 TUI（`M` 鍵）以及 Web UI（每個 target 上的模式下拉選單與 flatten 核取方塊）操作。

### `extras remove`

從設定中移除一個 extra。

```bash
skillshare extras remove <name> [--force] [-p|-g]
```

source 檔案與已同步的 target 都不會被刪除——只會移除設定項目。

### `extras collect`

把 target 中的本機檔案收集回 extras source 目錄。檔案會被複製到 source，並以 symlink 取代。

```bash
skillshare extras collect <name> [--from <path>] [--dry-run] [-p|-g]
```

**Options:**

| Flag | Description |
|------|-------------|
| `--from <path>` | 要從中收集的 target 目錄（若有多個 target 則為必填） |
| `--dry-run` | 顯示會收集哪些內容，但不做任何變更 |

**Example:**

```bash
# 把 rules 從 Claude 收集回 source
skillshare extras collect rules --from ~/.claude/rules

# 預覽會收集哪些內容
skillshare extras collect rules --from ~/.claude/rules --dry-run
```

---

## Sync Modes

| Mode | Behavior |
|------|----------|
| `merge` (default) | 從 target 到 source 的逐檔 symlink |
| `copy` | 逐檔複製 |
| `symlink` | 整個目錄的 symlink |

切換模式時（例如從 `merge` 切換到 `copy`），下一次 `sync` 會自動用新模式的格式取代既有的 symlink。不需要 `--force`——symlink 一律可以安全地取代。本機建立的一般檔案則需要 `--force` 才能覆寫。

---

## Flatten

有些 AI 工具（例如 Claude Code 的 `/agents`）只會探索其設定目錄**最上層**的檔案——不會遞迴進入子目錄。如果你的 extras source 使用子目錄來組織檔案，同步後的檔案對該工具來說會是不可見的。

`flatten` 選項可以解決這個問題：無論檔案在 source 中的子目錄深度為何，都會直接同步到 target 根目錄：

```yaml
extras:
  - name: agents
    targets:
      - path: ~/.claude/agents
        flatten: true
```

**Behavior:**
- `flatten: true`: `source/curriculum/tactician.md` → `target/tactician.md`
- `flatten: false` (default): `source/curriculum/tactician.md` → `target/curriculum/tactician.md`

**檔名衝突：** 當兩個不同子目錄中的檔案同名時（例如 `team-a/agent.md` 與 `team-b/agent.md`），先出現的檔案會生效（依路徑字母順序排序）。之後的衝突則會被略過並顯示警告。

**限制：**
- 只適用於 `merge` 與 `copy` 模式——無法與 `symlink` 模式一起使用
- `collect` 會把新收集到的檔案放在 source 根目錄（新檔案沒有子目錄對應）

---

## Extension transforms

有些工具不讀取 markdown。Gemini CLI 需要 TOML 格式的 commands；Codex CLI 需要 TOML 格式的 agents。target 上的 `extension` 欄位會在同步時執行外部腳本，把每個 source 檔案轉換成該 target 的原生格式。

```yaml
extras:
  - name: commands
    targets:
      - path: .claude/commands        # no extension — synced as-is
      - path: .gemini/commands
        extension: gemini-commands           # transform during sync
```

**解析方式** — 單純的名稱會在 extensions 目錄下解析（global 為 `~/.config/skillshare/extensions/<name>`，project 為 `.skillshare/extensions/<name>`）；路徑（`./x.sh`、`/abs/x`）則直接使用。

**複製語意** — `extension` 隱含 `copy` 模式。在帶有 `extension` 的 target 上設定 `mode: merge` 或 `mode: symlink` 會是錯誤。

**單向** — transform 只會由 source 執行到 target。`extras collect` 會略過有 extension 的 target。

**覆寫安全性** — 產生的輸出遵循與 `copy` 模式相同的衝突規則。輸出路徑上殘留的 symlink 會自動被取代；本機建立的既有一般檔案或目錄則會維持原狀並被略過，除非你加上 `--force`（加上 `--force` 時，衝突的目錄會被產生的檔案整個取代）。

### Extension layout

可以是單一可執行檔，或帶有 manifest 的目錄：

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

單純的單檔可執行檔（沒有 manifest）會直接被 exec（在 Unix 上依賴 shebang），並保留 source 的副檔名。需要重新命名副檔名的 transform 必須使用目錄形式。

### Execution contract

- Source 檔案內容會透過 **stdin** 傳入；腳本則將轉換後的內容寫到 **stdout**。
- 環境變數：`SS_SRC_PATH`、`SS_REL_PATH`（相對於 source 根目錄的路徑——對 Gemini 的 `/namespace:command` 命名方式很有用）、`SS_TARGET_DIR`、`SS_MODE`。
- 非零的結束碼會將該檔案標記為失敗；其他檔案則會繼續處理。

### Cross-platform

這個機制是跨平台的；某個 extension 能否執行取決於它的直譯器（interpreter）。因為 `run` 是明確的指令，用 `node` 或 `python3` 撰寫的 extension 可以在 Windows、macOS、Linux 上運作。純 `bash` 腳本只能在有 shell 可用的環境執行（Unix，或是裝有 Git Bash 的 Windows）。參考用的 extension 偏好使用 Node 作為直譯器，因為它在各平台上都能一致地提供。

### Reference extensions

skillshare repo 在 `extensions/` 底下附上了範例 extension（`gemini-commands`、`codex-agents`、`opencode-agents`）。把其中一個複製到你的 extensions 目錄並自行調整——它們是參考範例，不會自動安裝。每個參考 extension 都會讓 `convert.js` 保持精簡，讓你只需要編輯欄位對應；`md-toml.js` 負責讀取 markdown、解析簡單的 frontmatter，並寫出 TOML。

### Recipe: Codex agents

Codex CLI 需要 TOML 格式的 agents，而非 markdown。因為 `source` 可以指向任何目錄，你可以把你的 agents source 重複用作 extras source，並用 `codex-agents` 轉換它：

```yaml
extras:
  - name: codex-agents
    source: ~/.config/skillshare/agents   # reuse the agents source
    targets:
      - path: ~/.codex/agents
        extension: codex-agents
```

`skillshare sync extras` 會把每個 `<agent>.md` 轉換成 `~/.codex/agents/<agent>.toml`，對應 frontmatter 的 `name`、`description`、`model`，並把 markdown 內文摺進 `developer_instructions`（其他 frontmatter 欄位則會被捨棄）。[Codex custom agent schema](https://developers.openai.com/codex/subagents#custom-agent-file-schema) 要求 `name`、`description`、`developer_instructions`，因此當解析出的 name、description 或 Markdown 內文為空白時，這個參考 transform 會回報清楚的錯誤。不需要另外複製一份 agents。

Agent targets 也可以直接使用 `extension`，不需要透過 extra。詳見 [使用 extension 轉換 agents](/docs/understand/agents#extensions)。

---

## Recipe: shared instructions across agents

現在大多數 coding agent 都會讀取 `AGENTS.md` 作為常設指示，但每一個都把自己使用者層級的
複本放在不同的目錄。一個帶有多個 target 的 extra，就能把單一的 source 檔案分發給所有工具：

```bash
skillshare extras init instructions \
  --target ~/.codex \
  --target ~/.config/opencode \
  --target ~/.claude \
  --target ~/.gemini \
  --no-tui
```

把你的 `AGENTS.md` 放進解析出的 source 目錄（預設為 `~/.config/skillshare/extras/instructions/`），然後執行 `skillshare sync extras`。

| Agent | Global path | Reads `AGENTS.md` |
|-------|-------------|-------------------|
| Codex CLI | `~/.codex/AGENTS.md` | 直接讀取 |
| opencode | `~/.config/opencode/AGENTS.md` | 直接讀取 |
| Claude Code | `~/.claude/AGENTS.md` | 透過 `CLAUDE.md` 匯入 |
| Antigravity | `~/.gemini/AGENTS.md` | 透過 `GEMINI.md` 匯入 |

有兩個 agent 在使用者層級會讀取自己固定的檔名，因此各自需要一個一行檔案，放在同步的檔案
旁邊。這些只需要寫一次；skillshare 之後不會再碰它們：

```markdown title="~/.claude/CLAUDE.md"
@AGENTS.md
```

```markdown title="~/.gemini/GEMINI.md"
@AGENTS.md
```

Claude Code 讀取的是 `CLAUDE.md` 而不是 `AGENTS.md`，而匯入正是它的 [memory 文件](https://code.claude.com/docs/en/memory) 建議用來與其他 agent 共享單一檔案的做法。Antigravity 把它的全域 rules 放在 `~/.gemini/GEMINI.md`，並會相對於該 rules 檔案自身所在的目錄解析 `@filename`，所以同樣的一行寫法就能抓到同步過來的 `AGENTS.md`。`~/.gemini` 這個 target 也涵蓋了 Antigravity CLI，因為它讀取的是同一個全域檔案。

請保持 source 檔案的名稱為 `AGENTS.md`。像 `memory.md` 這種中性名稱一樣可以同步成功，但會不再被讀取：Codex 是依名稱串接 `AGENTS.md` 檔案，且沒有 import 語法，因此只認得這個名稱的檔案。

因為 target 都是目錄，每個 target 都會以其 source 名稱收到每個檔案。請只在 source 目錄中放你想要到處都有的檔案——多放一個檔案，就會出現在全部四個 target 裡。

:::note
這份 recipe 分享的是你自己寫的指示，不是 agent 自己寫下的 memory。Agent 會以私有格式儲存自己的學習結果——Claude Code 用一個 Markdown 目錄，Codex 用資料庫，Cursor 則是非檔案式的儲存——這些內容無法透過在 target 之間複製檔案來搬移。
:::

---

## Directory Structure

```
~/.config/skillshare/
├── config.yaml          # extras 設定放在這裡
├── skills/              # skill source
└── extras/              # extras source 根目錄
    ├── rules/           # extras/rules/ 的 source 檔案
    │   ├── coding.md
    │   └── testing.md
    └── prompts/
        └── review.md
```

---

## Configuration

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

### Source Resolution Priority

每個 extra 的 source 目錄會依三層優先順序解析：

1. **個別 extra 的 `source`**（最高）— 直接使用該精確路徑
2. **`extras_source`** — `<extras_source>/<name>/`
3. **預設值** — `~/.config/skillshare/extras/<name>/`（global）或 `.skillshare/extras/<name>/`（project）

`extras list --json` 的輸出包含 `source_type` 欄位（`per-extra`、`extras_source`，或 `default`），表示路徑是由哪一層解析出來的。

:::tip Auto-populated
執行 `skillshare init`，或用 `extras init` 建立你的第一個 extra 時，`extras_source` 會自動被設為預設路徑（`~/.config/skillshare/extras/`）。之後若要變更，請使用 `skillshare extras source <path>`。
:::

---

## Syncing

Extras 透過以下方式同步：

```bash
skillshare sync extras        # 只同步 extras
skillshare sync --all         # 同時同步 skills 與 extras
```

完整的 sync 文件（包含 `--json`、`--dry-run`、`--force` 選項）請參閱 [sync extras](/docs/reference/commands/sync#sync-extras)。

---

## Workflow

```bash
# 1. 建立新的 extra
skillshare extras init rules --target ~/.claude/rules --target ~/.cursor/rules

# 1b. 或使用自訂的 source 目錄
skillshare extras init rules --target ~/.claude/rules --source ~/my-rules

# 1c. 重新設定既有的 extra（覆寫）
skillshare extras init rules --target ~/.cursor/rules --force

# 2. 把檔案加入 source 目錄
# （編輯解析出來的 source 目錄——可用 skillshare extras list --json 檢查）

# 3. 同步到 target
skillshare sync extras

# 4. 列出狀態（source_type 顯示每個 extra 的 source 是從哪裡解析出來的）
skillshare extras list

# 5. 把在 target 中編輯過的檔案收集回 source
skillshare extras collect rules --from ~/.claude/rules

# 6. 變更全域的 extras source 目錄
skillshare extras source ~/company-shared/extras
```

---

## See Also

- [sync](/docs/reference/commands/sync#sync-extras) — 把 extras 同步到 target
- [status](/docs/reference/commands/status) — 顯示 extras 的檔案與 target 數量
- [Configuration](/docs/reference/targets/configuration#extras) — Extras 設定參考
