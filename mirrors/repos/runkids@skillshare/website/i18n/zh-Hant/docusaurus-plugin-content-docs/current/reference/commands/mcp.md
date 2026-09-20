---
sidebar_position: 3
---

# mcp

管理可攜式 MCP 連線定義，並同步原生 Agent 設定。
先從 [設定一次 MCP](/docs/how-to/daily-tasks/sharing-mcp) 開始。

## Commands

```bash
skillshare mcp
skillshare mcp add
skillshare mcp edit
skillshare mcp edit docs --url https://updated.example/mcp --no-tui
skillshare mcp add docs --url https://example.com/mcp --target claude --sync
skillshare mcp add local --target codex -- company-mcp --workspace /path/to/workspace
skillshare mcp import docs --from claude --target claude --target cursor --sync
skillshare mcp import docs --file ./provider.json --target claude
skillshare mcp list --json
skillshare mcp remove docs --sync
skillshare mcp restore BACKUP_ID --dry-run
skillshare sync mcp --dry-run --json
skillshare sync mcp
skillshare sync --all
```

| Option | 意義 |
|---|---|
| `--target CLIENT` | 接收端 client；重複指定可選擇多個 clients |
| `--url URL` | `add` 用的 Streamable HTTP 端點 |
| `-- command args...` | `add` 用的本機執行檔與字面參數 |
| `--disabled` | Project mode，搭配 `add`：關閉一個由 Agent 的 global config 定義的 server。參見[下方說明](#turn-off-a-global-server-in-one-project) |
| `--from CLIENT` | 要匯入的既有 client，或 `--file` 的格式 |
| `--file PATH` | 原生 JSON/JSONC、TOML 或 Goose YAML；`.toml` 預設為 Codex，其他格式會從其 MCP 區段偵測；使用 `--from` 可明確指定格式 |
| `--sync` | 儲存並同步；非互動式的 add/import/remove 預設只會儲存 |
| `--replace` | 在 add/import 期間明確取代既有的 source 定義；在 import 時，若匯入的 client 項目不同也會一併改寫 |
| `--dry-run`, `-n` | 只預覽，不儲存或寫入原生設定 |
| `--json` | 結構化輸出；sync/preview 報告只包含名稱、路徑與動作，不含 server 的值 |
| `--no-tui` | 停用互動選單；`tui: false`、`--json` 或非終端機輸入/輸出時也會停用 |
| `--revision ID` | 要求 add、import、remove 或 `sync mcp` 使用相符的 preview |
| `--global`, `-g` | 使用 global Skillshare 設定 |
| `--project`, `-p` | 使用 project Skillshare 設定 |

不帶任何 subcommand 時，`mcp` 會在互動式終端機中開啟可搜尋的管理介面，或在非互動模式下印出狀態。不帶名稱的非互動式匯入，會列出解析出的候選項供選擇，且不會儲存。候選項包含可攜式定義，可識別的機密資料會轉換為參照。Agent 專屬欄位會列為警告並被省略；已停用的 servers 與不支援的傳輸方式會擋下該候選項。`restore` 一律會先重新預覽再套用；使用 `--dry-run` 可只檢視而不套用。

`sync mcp` 接受 scope flags、`--dry-run`、`--json`、`--no-tui` 與 `--revision`。`sync --all` 包含 skills、agents、extras 與 MCP；單獨的 `sync` 則維持既有的資源行為。MCP 衝突會在 `--all` 變更其他資源之前先檢查。資源類型與原生檔案是各自獨立的操作，而非單一交易。

## 互動式管理

執行 `skillshare mcp` 或 `skillshare mcp list`。與 skills 列表相同，此管理介面支援 `/` 搜尋與 `Enter` 檢視詳情。連線列表會隱藏參數、標頭與環境變數的值，並省略 URL 查詢字串。

| 按鍵 | 動作 |
|---|---|
| `a` | 新增連線 |
| `i` | 匯入一或多個連線 |
| `e` | 編輯所選連線 |
| `x` | 移除所選連線 |
| `s` | 預覽並確認同步 |
| `b` | 依 client 瀏覽備份，最新在前 |
| `r` | 重新整理狀態 |
| `q` | 離開 |

當省略名稱或 backup ID 時，`mcp edit`、`mcp remove` 與 `mcp restore` 會提供選單。編輯器涵蓋 command/URL、參數、環境變數、HTTP headers、bearer-token 環境參照與接收端 targets。參數接受一行一個字面參數，或一個 JSON 陣列。切換傳輸方式會清除不適用於新連線類型的欄位。

Add、edit、remove 與 import 在 **Save and sync** 或 **Save only** 之前會顯示預覽。Escape 可取消待處理的草稿。Restore 會預覽並確認對 Agent 項目的變更；它不會改寫 source 定義。

不帶 server 名稱的 import 支援多重選取（`Space` 切換，`a` 全選）。無效的候選項會被跳過；除非指定 `--replace`，否則既有的 source 名稱會被跳過。此批次要選擇一組相容的接收端 clients。整個批次會先驗證完畢，source 才會一次儲存；後續原生檔案 I/O 失敗仍維持既有的復原行為。

對於腳本，請提供名稱與 flags。`mcp edit NAME --url URL`、`mcp edit NAME --target CLIENT` 與 `mcp edit NAME -- command args...` 會更新指定欄位，同時保留其他適用的設定。除非加上 `--sync`，否則只會儲存。搭配 `--no-tui` 時，remove 需要名稱，restore 需要 backup ID。`--dry-run` 永遠不會儲存或同步變更。

## Source 欄位

選擇內嵌的 `mcp.servers`，或是由 `sources.mcp` 指定的外部檔案。外部檔案要有頂層的 `servers` 映射。`mcp.targets` 仍留在 Skillshare config 中。Schema 位於 repository 中的 `schemas/mcp.schema.json`。

| Server 欄位 | 意義 |
|---|---|
| `command` | 本機執行檔；與 `url` 互斥 |
| `args` | 本機執行檔的字面參數列表 |
| `env` | 本機環境變數值：字串或 `{fromEnv: VARIABLE}` |
| `url` | HTTP(S) MCP 端點；不可含內嵌憑證或 fragment |
| `headers` | HTTP headers：字串或 `{fromEnv: VARIABLE}` |
| `bearerToken` | `{fromEnv: VARIABLE}`；不可與 Authorization header 並存 |
| `transport` | 選填的 `stdio` 或 `streamable-http`；省略時自動推斷 |
| `targets` | 選填的接收端 clients；覆寫 `mcp.targets` |
| `disabled` | 只能是 `true`，僅限 project mode，且不能有其他連線欄位。參見[下方說明](#turn-off-a-global-server-in-one-project) |

Client ID 有 `claude`、`codex`、`cursor`、`vscode`、`opencode`、`kilocode`、
`grok`、`antigravity`、`amp`、`claude-desktop`、`cline`、`copilot`、`factory`、`gemini`、
`goose`、`junie`、`kiro`、`lmstudio`、`warp`、`windsurf` 與 `pi`。
`grok` 指的是官方的 xAI Grok CLI。Server 名稱使用字母、
數字、點、底線與連字號。一個 server 必須直接或透過 `mcp.targets`
選擇至少一個 client 才能同步。

對於 Grok，名稱必須以字母或底線開頭，只能包含字母、
數字、連字號與單一底線，且不能以底線結尾。
像 `company-docs` 這樣的名稱適用於所有支援的 clients。

## Native destinations {#native-destinations}

| Client | Global | Project | Section |
|---|---|---|---|
| Claude Code | `~/.claude.json` | `.mcp.json` | `mcpServers` |
| Codex | `~/.codex/config.toml` | `.codex/config.toml` | `mcp_servers` |
| Cursor | `~/.cursor/mcp.json` | `.cursor/mcp.json` | `mcpServers` |
| VS Code | User `mcp.json`（如下） | `.vscode/mcp.json` | `servers` |
| OpenCode | `~/.config/opencode/opencode.json` | `opencode.json` | `mcp` |
| Kilo Code | `~/.config/kilo/kilo.jsonc` | `kilo.jsonc` | `mcp` |
| Grok CLI | `~/.grok/config.toml` | `.grok/config.toml` | `mcp_servers` |
| Antigravity (AGY) | `~/.gemini/config/mcp_config.json` | `.agents/mcp_config.json` | `mcpServers` |
| [Amp](https://ampcode.com/docs/customize/mcp) | `~/.config/amp/settings.json` | `.amp/settings.json` | `amp.mcpServers`（字面鍵值） |
| [Claude Desktop](https://modelcontextprotocol.io/docs/develop/connect-local-servers) | Claude 應用程式資料目錄下的 `claude_desktop_config.json` | 僅限 Global | `mcpServers` |
| [Cline](https://github.com/cline/cline/tree/main/apps/vscode/src/services/mcp) | `~/.cline/data/settings/cline_mcp_settings.json` | 僅限 Global | `mcpServers` |
| [Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-mcp-servers) | `~/.copilot/mcp-config.json` | `.github/mcp.json` | `mcpServers` |
| [Factory Droid](https://docs.factory.ai/harness/mcp) | `~/.factory/mcp.json` | `.factory/mcp.json` | `mcpServers` |
| [Gemini CLI](https://geminicli.com/docs/tools/mcp-server/) | `~/.gemini/settings.json` | `.gemini/settings.json` | `mcpServers` |
| [Goose](https://block.github.io/goose/docs/guides/config-files/) | `~/.config/goose/config.yaml` | 僅限 Global | `extensions`（YAML） |
| [Junie](https://junie.jetbrains.com/docs/junie-cli-mcp-configuration.html) | `~/.junie/mcp/mcp.json` | `.junie/mcp/mcp.json` | `mcpServers` |
| [Kiro](https://kiro.dev/docs/mcp/configuration/) | `~/.kiro/settings/mcp.json` | `.kiro/settings/mcp.json` | `mcpServers` |
| [LM Studio](https://lmstudio.ai/docs/app/mcp) | `~/.lmstudio/mcp.json` | 僅限 Global | `mcpServers` |
| [Warp](https://docs.warp.dev/agents/capabilities/mcp/) | `~/.warp/.mcp.json` | `.warp/.mcp.json` | `mcpServers` |
| [Windsurf (Cascade)](https://docs.devin.ai/desktop/cascade/mcp) | `~/.codeium/windsurf/mcp_config.json` | 僅限 Global | `mcpServers` |

Dashboard 的 server 表單編輯 HTTP headers 的方式與環境變數相同，
包括 `fromEnv` 參照。Server 選單中的 **View what each Agent gets**，以及其表單中檔案數量旁的同名選項，
會以唯讀方式顯示 Sync 對所選 client 會寫入的原生文字內容；在表單中，它會反映尚未儲存的編輯內容。機密資料仍以參照形式呈現。

JSON 項目會依照檔案本身的縮排，一行寫入一個欄位。若 Skillshare 擁有的某個項目
仍然寫在同一行，會回報為 `update` 並重新排版寫入。它不擁有的項目，
以及有人手動格式化過的項目，會保留原有排版。

Dashboard 只會提供目前 scope 與主機平台可用的目的地。每個 server 各佔一列；
右側的計數按鈕會開啟該 server 的完整 client 清單。僅限 Global 的 clients 在 project mode 中無法選擇。
右側的 **Sync** 框會列出尚未寫入的變更：勾選某個 client 只會編輯 source，
確認後才會在 Sync 頁面寫入檔案。下方的 **Agents** 會列出這台機器上偵測到的 clients。
當某個 client 的 MCP 檔案存在，或該 client 用來存放設定的資料夾存在時，就算做偵測到，
所以剛安裝、還沒有 MCP 檔案的 client 也會顯示出來。在 project mode 中，
當 project 有自己的 MCP 檔案，或該 client 在 global 層級被偵測到時，就會列出該 client。

其他 client 細節：

- `codex` 目的地是單一份 `config.toml`，由 Codex CLI、Codex IDE
  擴充功能與 ChatGPT 桌面應用程式共用，所以同步到 `codex` 的 server 會出現在
  這三者中。ChatGPT 桌面應用程式會在 **Settings → MCP servers** 下列出它們。
  Codex 只會在受信任的 project 中讀取 `.codex/config.toml`；在不受信任的
  project 中，已同步的 servers 不會載入，且不會顯示錯誤。`cwd`、
  `http_headers_helper`、工具清單與核准模式、逾時，以及 `oauth` 表格
  都沒有可攜式對應形式：import 會將它們省略並顯示警告，sync 則會將它們保留在
  既有項目中。由 Codex plugin 包裝的 MCP servers，會設定在
  `plugins.<plugin>.mcp_servers` 下，不受此處管理。
- Claude Desktop 的檔案同步僅支援 **stdio**，僅限 macOS 與 Windows。
  其目錄在 macOS 上為 `~/Library/Application Support/Claude`，在 Windows 上為
  `%APPDATA%/Claude`。遠端連接器請在應用程式內設定。
- Cline 只作用於預設的 VS Code Stable profile，不含 Cline CLI 或其他 IDE。
- Copilot CLI 為新項目匯出 `tools: ["*"]`，並保留既有的工具
  篩選條件。若存在 project 層級的 `.mcp.json`，sync 會停止，因為 Copilot 會優先讀取該
  檔案而非 `.github/mcp.json`；請先整合這些檔案。
  在 project mode 中同時選擇 Claude Code 與 Copilot CLI 也會在寫入任一檔案前被擋下。
  其中一個 client 請改用 global mode。
- Gemini 使用 `httpUrl` 表示 Streamable HTTP。其 `url` 欄位代表舊版 SSE，
  在 import 時會被拒絕。Cline 使用 `type: streamableHttp`；Goose 使用
  `type: streamable_http` 與 `uri`。Skillshare 會自動轉換這些格式。
- Goose 在 Windows 上使用 `%APPDATA%/Block/goose/config/config.yaml`。YAML 編輯
  會保留不相關的設定、註解與內建 extensions，但可能會改變格式。
  Aliases、merges、重複的鍵與多份文件會擋下編輯。
  內建 extensions 與 keychain 的 `env_keys` 無法作為可攜式 MCP
  連線匯入。
- Claude Code 會跳過名為 `workspace`、`claude-in-chrome` 或 `computer-use` 的 server，
  這些名稱由它保留給內建 servers 使用。它也絕不會把自己的憑證送給
  遠端 server：`ANTHROPIC_API_KEY`、`ANTHROPIC_AUTH_TOKEN`、`AWS_BEARER_TOKEN_BEDROCK`、
  `HTTPS_PROXY` 與 `NPM_TOKEN` 在 `url` 與 `headers` 中會讀取為空值。Skillshare 對 Claude
  的這兩者都會拒絕。請把憑證複製到一個你自訂名稱的變數中。
- Claude Code 也有一個本機 scope：使用 `claude mcp add` 且未指定
  `--scope` 新增的 servers，會依 project 各自存放在 `~/.claude.json` 中。本機 server
  會整體覆蓋 `.mcp.json` 或 user scope 中同名的 server。在 project mode 中，Skillshare
  會在被隱藏的項目旁回報這類 server 的存在，但不會阻擋同步。可從 project 資料夾中
  用 `claude mcp remove NAME -s local` 移除它。
- Cline 的 VS Code 擴充功能、CLI 與 SDK 共用 `~/.cline/data/settings/`。該
  擴充功能會把較舊的 VS Code `globalStorage` 檔案搬到那裡一次，之後就不再
  讀取它，所以 Skillshare 只有在 `~/.cline/data` 尚不存在時才會寫入舊檔案。
  `CLINE_MCP_SETTINGS_PATH`、`CLINE_DATA_DIR` 與 `CLINE_DIR` 會依此順序
  被採用。
- Windsurf 支援的是文件記載的 Cascade 設定。Windsurf 較新的
  Devin Local agent 會讀取自己的 `~/.config/devin/mcp_config.json`，Skillshare
  不管理它。Warp 的 project 連線每個 session 仍需要在 Warp 內部核准。
- Amp 只有在執行過 `amp mcp approve <name>` 後，才會從 project 的
  `.amp/settings.json` 執行 server。Global servers 不需要核准。
- Kiro 只會展開其「Mcp Approved Env Vars」設定中列出的名稱所對應的
  `${VARIABLE}`，且只接受 localhost 的 `http://` URL。
- VS Code 會為 `User/profiles/` 下每個非預設 profile 各自保留一份
  `mcp.json`。Skillshare 管理的是預設 profile 的檔案。

環境參照的匯出格式，對 Amp、Copilot CLI、
Factory、Gemini CLI 與 Kiro 為 `${VARIABLE}`，對 Cline 與 Windsurf 為 `${env:VARIABLE}`。
Claude Desktop、Goose、Junie、LM Studio 與 Warp 目前拒絕 `fromEnv` 與
`bearerToken` 的匯出，因為它們的原生插值行為尚未驗證。
請使用不含自訂憑證的連線，或在支援的接收端 client 中自行驗證。
Skillshare 絕不會將參照解析為明文。

Antigravity 使用目前的[官方 MCP 設定格式](https://antigravity.google/docs/mcp)，
包括遠端連線用的 `serverUrl`。Skillshare 會自動轉換可攜式 `url`。
較舊的 `.gemini/antigravity/` 與 `.gemini/antigravity-cli/` 設定
位置不受管理。Antigravity 的 `fromEnv` 與 `bearerToken` 匯出
會被封鎖，因為其文件記載的設定格式並未指定環境
插值方式。請使用不需要自訂機密 headers 的連線，並在 Antigravity 內完成
支援的 OAuth 登入。Skillshare 絕不會將參照展開為
明文憑證。

OpenCode 的 global 目錄遵循 `XDG_CONFIG_HOME`。若既有的
`opencode.jsonc` 存在，會優先使用它而不是建立 `opencode.json`；若所選目錄中
兩者皆存在，請先整合它們再進行同步。自訂的 OpenCode config
路徑、目錄覆寫、內嵌 config 與繼承的上層檔案不受
管理。它們可能會覆蓋 OpenCode 中所選的目的地。

Kilo Code 使用與 OpenCode 相同的格式。它會讀取 project 根目錄與
`.kilo/` 中的 `kilo.jsonc` 與 `kilo.json`，並將兩者合併，因此 Skillshare 會寫入
既有的那一個檔案，只有在都不存在時才會建立 `kilo.jsonc`。若
兩者都存在，請先整合它們再進行同步。`KILO_CONFIG`、
`KILO_CONFIG_DIR` 以及舊版 VS Code 擴充功能的 `mcp_settings.json`
不受管理。

Kilo Code 將 project config 視為不受信任。它不允許在其中使用 `{env:VARIABLE}`
參照，一旦發現 project 檔案就會忽略整個檔案。因此在 project
mode 中，Skillshare 會拒絕使用 `fromEnv` 或 `bearerToken` 的 Kilo Code server。
請在允許使用參照的 global mode 中定義該 server。

OpenCode 與 Kilo Code 使用 `local`/`remote` 類型與 `{env:VARIABLE}` 參照；Grok 使用
`${VARIABLE}` 參照。Skillshare 會自動轉換這些格式。Claude 的
`"type": "streamable-http"` 會匯入為 HTTP。已停用的連線會擋下 import。
其他沒有可攜式對應形式的原生選項，例如 Codex 的
`startup_timeout_sec` 或 `envFile`，會在 import 時被省略並顯示警告；
sync 會將它們保留在 Agent 既有的項目中。Pi 是透過明確
選擇的第三方 extension 支援的；詳見下方說明。

VS Code Stable 的預設 user 檔案為：

- macOS：`~/Library/Application Support/Code/User/mcp.json`
- Linux：`${XDG_CONFIG_HOME:-~/.config}/Code/User/mcp.json`
- Windows：`%APPDATA%/Code/User/mcp.json`

Global 的 Claude、Codex、Grok 與 Copilot 路徑遵循 `CLAUDE_CONFIG_DIR`、`CODEX_HOME`、
`GROK_HOME` 與 `COPILOT_HOME`。`OPENCODE_CONFIG` 與 `OPENCODE_CONFIG_DIR` 不受管理。Amp 與 Goose 在
使用 `.config` 路徑的平台上會遵循 `XDG_CONFIG_HOME`。
Project 目的地是相對於所選 project 根目錄。Project 信任、
server 核准與驗證仍屬於接收端 Agent 的責任。

## Turn off a global server in one project {#turn-off-a-global-server-in-one-project}

Agent 會同時讀取自己的 global MCP 檔案與 project 的檔案。因此定義在
global 檔案中的 server 會在每個 project 中載入。若要讓它在某個
project 中不要載入，請新增一個**使用該 Agent 的 global 檔案中相同名稱**的項目，
並標記為 `disabled`。

這只適用於四種 clients：

| Client | 是否支援 | Skillshare 會寫入什麼 |
|---|---|---|
| Claude Code | 是 | `~/.claude.json`：名稱會加入這個 project 的 `disabledMcpServers` 清單 |
| OpenCode | 是 | `opencode.json`：`"NAME": {"enabled": false}` |
| Kilo Code | 是 | `kilo.jsonc`：`"NAME": {"enabled": false}` |
| Pi with `pi-mcp-adapter` | 是 | `.pi/mcp.json`：`"NAME": {"disabled": true}` |
| Pi with `pi-mcp-extension` | 否 | 它沒有停用欄位 |
| Codex | 否 | 見下方說明 |
| 其他所有 client | 否 | 選擇它會是錯誤；不會寫入任何內容 |

只有開關會被寫入。Agent 仍會沿用其 global 項目中的 command 或 URL。
其他 clients 之所以被拒絕，是因為它們會用 project 項目整個取代 global
項目，或是沒有 project 檔案，因此單獨寫入一個開關反而會弄壞
server，而不是把它關閉。

Codex 被拒絕的原因不同。它確實會把 `.codex/config.toml` 逐欄位合併到
global 檔案之上，所以在 global config 有定義該 server 的機器上，單獨的
`enabled = false` 是可行的。但在沒有定義的機器上，合併後的項目會缺少
`command` 或 `url`，導致 Codex 因 `invalid transport` 而整個設定載入失敗。
`.codex/config.toml` 通常會被 commit，所以一個隊友的開關
可能導致另一個隊友的 Codex 無法啟動。請改為逐機器關閉該 server，
在 `~/.codex/config.toml` 中設定 `enabled = false`。

### OpenCode and Kilo Code

```bash
cd my-project
skillshare mcp add company-docs --disabled --target opencode --target kilocode
skillshare sync mcp
```

```yaml
# .skillshare/config.yaml
mcp:
  servers:
    company-docs:
      disabled: true
      targets: [opencode, kilocode]
```

### Claude Code

Claude Code 會從單一 scope 整個取用一個 server 項目，絕不會合併欄位，所以
在 `.mcp.json` 中設一個開關會取代該 server，而不是把它關閉。它把
自己每個 project 的關閉清單存放在 `~/.claude.json` 中，也就是 `/mcp` 面板編輯的那份。
Skillshare 會把名稱加到那裡，放在這個 project 的絕對路徑下，
不會寫入 `.mcp.json`。

```bash
skillshare mcp add company-docs --disabled --target claude
skillshare sync mcp
```

- 這份清單存放在你的機器上，而不是 repository 中。每個隊友都要在自己的
  checkout 中執行一次 `skillshare sync mcp`。
- 你自己在 `/mcp` 中關閉的名稱，永遠不會被認領或移除。
- 若你在 `/mcp` 中把 server 重新開啟，下一次同步會回報衝突。
  請從 `.skillshare/config.yaml` 中移除該項目，或用 replace 再次關閉它。
- 此清單以 project 的路徑為鍵值，所以搬移 project 需要重新同步。

### Pi

Pi 需要 `piExtension`（如同每個 Pi 項目一樣），且必須是 `pi-mcp-adapter`。
OpenCode 與 Kilo Code 會忽略該欄位，所以一個項目可以同時涵蓋這三者：

```bash
skillshare mcp add company-docs --disabled --target pi --pi-extension pi-mcp-adapter
```

```yaml
mcp:
  servers:
    company-docs:
      disabled: true
      piExtension: pi-mcp-adapter
      targets: [opencode, pi]
```

### Rules

- **僅限 Project mode。** 請在有 `.skillshare/config.yaml` 的 project 中執行
  （由 `skillshare init -p` 建立），或加上 `-p`。在 global mode 中會被拒絕。
- **`disabled` 必須單獨存在。** 該項目可以帶 `targets`，Pi 的話還可以帶
  `piExtension`。加入 `command`、`url`、`env` 或 `headers` 會是錯誤。
- **應該列出 `targets`。** 若省略，該項目會繼承 `mcp.targets`，
  該清單中任何不支援的 client 都會是錯誤。
- **名稱必須相符。** Skillshare 不會讀取 Agent 的 global 檔案，所以它
  無法確認該名稱的 server 是否真的存在。名稱不符任何 server 也無妨：
  Agent 會直接忽略它。
- **要重新開啟時**，移除該項目（`skillshare mcp remove company-docs`）
  並同步。開關會從 project 檔案中移除。
- **Skillshare 自己定義的 server 不需要這麼做。** 改為在該 server 上取消選擇
  該 Agent，下一次同步就會移除它的項目。

在 dashboard 中，這是新增 server 時，`stdio` 與
`streamable-http` 旁邊的 **Off in this project** 選項。它只會出現在 project mode 中。

## Safety and limitations

- JSONC 註解與不相關的設定會被保留。已變更的、由 Skillshare 擁有的
  項目會整體取代，所以那些項目內的註解可能因此改變。只有
  Skillshare 寫入的欄位會被比對與取代；Agent 專屬欄位（例如逾時設定）
  會被保留。
  Agent 自行填入的預設值，例如 `"type": "stdio"`、空的 `env` 或
  header 名稱大小寫，不算變更。用 `enabled: false` 或 `disabled: true`
  關閉一個受管理的 server，會回報為衝突。
- 當 Agent 重寫同一份檔案中不相關的設定時（如 Claude Code 對
  `~/.claude.json` 所做的那樣），預覽仍然有效。只有該檔案的
  MCP 項目發生變更時才需要重新預覽。
- Codex 與 Grok 的編輯支援一般的 `[mcp_servers.NAME]` 表格及其子表格。
  已更新的項目會保持原位，CRLF 換行符號也會保留。
  內嵌／點記法的 MCP 定義必須先轉換為表格才能寫入；
  否則會被拒絕，且不會修改檔案。
- 原生檔案的 symlinks、格式錯誤的檔案與重複的 JSON 屬性都會擋下
  寫入。被 symlink 的 Skillshare `config.yaml` 會直接寫入其目標檔案。檔案權限會被保留；新的原生
  檔案、擁有權紀錄與備份都使用私有權限。
- 若某項目已經與 source 相符，會回報為未變更且不會寫入，例如在
  拉取隊友的變更之後。如果這份設定先前並未管理它，例如在
  project 搬移之後，它仍會維持未受管理狀態：移除該 server
  不會影響它，除非你先匯入它。不同的未受管理項目需要匯入或
  明確的逐項目取代；只要另一份 Skillshare 設定檔仍然存在，
  就不能覆蓋它的擁有權。如果該設定檔已被搬移或刪除，就永遠無法釋放
  該項目，因此需要明確的匯入或取代才能接手。衝突訊息會指出擁有該檔案的來源。
- Dashboard 的 MCP 設定只有在瀏覽器以 `localhost` 或 IP 位址開啟
  dashboard 時才能運作。透過網域名稱存取時（包括 reverse
  proxy），MCP 請求會回傳 403，因為 DNS rebinding 攻擊一律使用
  網域名稱。
- 憑證使用環境參照；沒有機密儲存庫、OAuth session 同步、
  執行時健康檢查、套件安裝、gateway、registry 或 plugin 同步功能。
- 此版本不支援 VS Code Insiders、自訂 profiles、遠端 workspaces 與舊版 SSE。
- VS Code 目前不會在 `headers` 內代換 `${env:VARIABLE}`
  （[microsoft/vscode#336232](https://github.com/microsoft/vscode/issues/336232)），
  所以同步到 VS Code 的 header 與 `bearerToken` 參照，在此問題修復前
  會以未解析的原始值送達 server。
- 本機操作紀錄存放在 Skillshare state 目錄的 `mcp/` 下：
  `state.json`、寫入期間的 `pending.json`，以及 `backups/`（每個
  Agent 檔案保留最新 20 份）。請勿把這個
  目錄當作可攜式清單分享出去。


## Pi: choose your MCP extension {#pi-choose-your-mcp-extension}

Pi 可以透過 [pi-mcp-adapter](https://pi.dev/packages/pi-mcp-adapter)
或 [pi-mcp-extension](https://pi.dev/packages/pi-mcp-extension) 使用 MCP。這些是
Pi 官網上列出的第三方套件，並非 Pi 的內建功能。請在 Pi 中安裝**其中一個**：

```bash
pi install npm:pi-mcp-adapter
```

安裝後重新啟動 Pi。在 Skillshare 的 MCP 表單中，選擇 **Pi**，再選擇
你安裝的套件。Import 對話框提供相同的選項。在終端機中，
`mcp add` / `mcp edit` 會引導你選擇；腳本則必須提供 `--pi-extension`：

```bash
skillshare mcp add docs --url https://example.com/mcp --target pi --pi-extension pi-mcp-adapter --no-tui
skillshare sync mcp --dry-run
skillshare sync mcp
```

儲存後的 server 定義為：

```yaml
mcp:
  servers:
    docs:
      url: https://example.com/mcp
      targets: [pi]
      piExtension: pi-mcp-adapter
```

若使用另一個套件，安裝指令與選擇項目都請改用 `pi-mcp-extension`。
在單一 Skillshare source 中，所有指向 Pi 的 server 都必須選擇
相同的套件，因為兩個套件都讀取同一份目的地檔案。

| Package | 原生輸出 | 同步後該做什麼 |
|---|---|---|
| `pi-mcp-adapter` | `command`/`args` 或 `url`；`${VARIABLE}` 參照 | 重新啟動/重新載入 Pi；使用 `/mcp` 檢視連線。工具會依需求連線。 |
| `pi-mcp-extension` | 明確的 `transport: stdio` 或 `streamable-http` | 重新啟動 Pi；新 servers 預設為手動啟動，需用 `/mcp:start <server>`。既有的 `lifecycle` 設定會被保留。 |

兩者在 global 都使用 `~/.pi/agent/mcp.json`，project mode 則使用 `.pi/mcp.json`。
Skillshare 使用這些 Pi 專屬檔案，而不是 adapter 共用的 `.mcp.json` 或
`~/.config/mcp/mcp.json` 輸入來源。Project 項目會覆蓋同名的 global 項目。
對於 adapter，會遵循 global 的 `PI_CODING_AGENT_DIR` 覆寫設定。
Extension 不遵循該覆寫設定；global 同步會拒絕它，而不是寫入
一個該 extension 會忽略的檔案。

Adapter 支援在環境變數與 HTTP headers 中使用 `fromEnv`。
Extension **不會**插值環境參照：相符的 stdio
變數（例如 `TOKEN: {fromEnv: TOKEN}`）會改為繼承自 Pi 的行程；
重新命名變數與依賴環境變數的 HTTP 憑證則會被拒絕。
這類情況請改用 adapter。Skillshare 絕不會讀取或複製機密值。

使用 `--from pi` 匯入會讀取 Pi 專屬檔案。儲存匯入的連線時
請選擇 `--pi-extension`；單靠檔案本身無法識別安裝的是哪個套件。
不支援的舊版 SSE 仍會被封鎖。OAuth 與僅限套件內部的選項
仍由 Pi 管理。同步成功只代表設定已被寫入，不代表
某個 extension 已安裝或某個 server 已建立連線。
