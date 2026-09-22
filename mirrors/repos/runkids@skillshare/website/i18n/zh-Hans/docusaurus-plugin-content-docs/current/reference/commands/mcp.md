---
sidebar_position: 3
---

# mcp

管理可移植的 MCP 连接定义，并同步各原生 Agent 的设置。
从 [Set up MCP once](/docs/how-to/daily-tasks/sharing-mcp) 开始了解。

## 命令

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

| 选项 | 含义 |
|---|---|
| `--target CLIENT` | 接收方 client；重复此标志可选择多个 client。`--target none` 会把 server 保留在 Skillshare 中，而不写入任何 client。参见[下文](#keep-a-server-without-syncing-it) |
| `--url URL` | 用于 `add` 的 Streamable HTTP 端点 |
| `-- command args...` | 用于 `add` 的本地可执行文件及其字面参数 |
| `--disabled` | Project mode，配合 `add` 使用：关闭一个由 Agent 全局配置定义的 server。参见[下文](#turn-off-a-global-server-in-one-project) |
| `--pi-extension PACKAGE` | target 包含 Pi 时必填，用于 `add`、`edit` 或 `import`：`pi-mcp-adapter` 或 `pi-mcp-extension`，填你在 Pi 里安装的那一个。参见[下文](#pi-choose-your-mcp-extension) |
| `--direct-tools VALUE` | 配合 `pi-mcp-adapter` 使用的 Pi，用于 `add` 或 `edit`：`true`、`false`、`search`，或用逗号分隔的工具名称。参见[下文](#pi-direct-tools) |
| `--pi-options JSON` | 配合 `pi-mcp-adapter` 使用的 Pi，用于 `add` 或 `edit`：以 JSON 对象传入 adapter 的其他字段；`{}` 会清空它们。参见[下文](#pi-options) |
| `--from CLIENT` | 要导入的现有 client，或 `--file` 的格式 |
| `--file PATH` | 原生 JSON/JSONC、TOML 或 Goose YAML；`.toml` 默认对应 Codex，其他格式会根据其 MCP 区块自动检测；如需明确指定方言请使用 `--from` |
| `--sync` | 保存并同步；非交互式的 add/import/remove 默认仅保存 |
| `--replace` | 在 add/import 期间显式替换已存在的 source 定义；在 import 时，若导入的 client 条目不同，也会重写它 |
| `--dry-run`, `-n` | 预览，不保存也不写入原生配置 |
| `--json` | 结构化输出；sync/preview 报告只包含名称、路径和动作，不包含 server 值 |
| `--no-tui` | 禁用交互式菜单；`tui: false`、`--json` 或非终端输入/输出也会禁用它 |
| `--revision ID` | 要求 add/import/remove 或 `sync mcp` 匹配指定的 preview |
| `--global`, `-g` | 使用 global Skillshare 配置 |
| `--project`, `-p` | 使用 project Skillshare 配置 |

不带子命令时，`mcp` 会在交互式终端中打开可搜索的管理器，
或在非交互模式下打印状态。不带名称的非交互式 import 会列出
已解析的候选项以供选择，并不会保存。候选项包含可移植的
定义，可识别的密钥会被转换为引用。Agent 专属的
字段会作为警告列出并被省略；已禁用的 server 和不受支持的
传输方式会阻止该候选项。`restore` 在应用之前总会再次预览；
使用 `--dry-run` 可以在不应用的情况下查看预览。

`sync mcp` 接受作用域标志、`--dry-run`、`--json`、`--no-tui` 和 `--revision`。
`sync --all` 包含 skills、agents、extras 和 MCP；普通的 `sync` 保持其
现有的资源行为。在 `--all` 更改其他资源之前会先检查 MCP 冲突。
资源类型与原生文件是各自独立的操作，而非单一事务。

## 交互式管理

运行 `skillshare mcp` 或 `skillshare mcp list`。与 skills 列表一样，该管理器
支持 `/` 搜索和 `Enter` 查看详情。连接列表会隐藏参数、
header 和环境变量的值，并省略 URL 中的查询参数。

| 按键 | 操作 |
|---|---|
| `a` | 添加一个连接 |
| `i` | 导入一个或多个连接 |
| `e` | 编辑所选的连接 |
| `x` | 移除所选的连接 |
| `s` | 预览并确认同步 |
| `b` | 按 client 浏览备份，按最新排序 |
| `r` | 刷新状态 |
| `q` | 退出 |

省略名称或备份 ID 时，`mcp edit`、`mcp remove` 和 `mcp restore` 会提供选择菜单。
编辑器涵盖 command/URL、参数、环境
变量、HTTP header、bearer-token 环境引用以及接收方
target。参数接受每行一个字面参数，或一个 JSON 数组。切换
传输方式时会清除不适用于新连接类型的字段。

Add、edit、remove 和 import 会在 **Save and sync** 或 **Save
only** 之前显示预览。Escape 会取消待处理的草稿。Restore 会预览并确认
对 Agent 条目所做的更改；它不会重写 source 定义。

不带 server 名称的 import 支持多选（`Space` 切换选中，
`a` 全选）。无效的候选项会被跳过；已存在的 source 名称会被跳过，
除非指定了 `--replace`。为整批操作选择一组兼容的接收方 client。
整批数据会先经过验证，然后 source 只被保存一次；
之后的原生文件 I/O 失败仍保留现有的恢复行为。

对于脚本，提供名称和标志。`mcp edit NAME --url URL`、
`mcp edit NAME --target CLIENT` 和 `mcp edit NAME -- command args...` 会更新
指定的字段，同时保留其他适用的设置。除非加上 `--sync`，
否则它们只会保存。使用 `--no-tui` 时，remove 需要名称，restore
需要备份 ID。`--dry-run` 绝不会保存或同步更改。

## Source 字段

选择内联的 `mcp.servers`，或使用 `sources.mcp` 指定的外部文件。
外部文件有一个顶层的 `servers` 映射。`mcp.targets` 和
[`mcp.projects`](#manage-several-projects-from-the-global-config) 保留在
Skillshare 配置中。schema 是仓库中的 `schemas/mcp.schema.json`。

| Server 字段 | 含义 |
|---|---|
| `command` | 本地可执行文件；与 `url` 互斥 |
| `args` | 本地可执行文件的字面参数列表 |
| `env` | 本地环境变量值：字符串或 `{fromEnv: VARIABLE}` |
| `url` | HTTP(S) MCP 端点；不能包含内嵌凭据或 fragment |
| `headers` | HTTP header：字符串或 `{fromEnv: VARIABLE}` |
| `bearerToken` | `{fromEnv: VARIABLE}`；不能与 Authorization header 共存 |
| `transport` | 可选的 `stdio` 或 `streamable-http`；省略时会自动推断 |
| `targets` | 可选的接收方 client；覆盖 `mcp.targets`。空列表会让该 server 只保留在 Skillshare 中。参见[下文](#keep-a-server-without-syncing-it) |
| `directTools` | 仅限使用 `pi-mcp-adapter` 的 Pi：`true`、`false`、`"search"` 或工具名称列表。参见[下文](#pi-direct-tools) |
| `piOptions` | 仅限使用 `pi-mcp-adapter` 的 Pi：adapter 的其他字段，会原样写入 Pi 中的条目。参见[下文](#pi-options) |
| `disabled` | 仅限 `true`，不能有其他连接字段，且必须有 project 在作用范围内：project mode，或 `mcp.projects` 下的某个项目根目录。参见[下文](#turn-off-a-global-server-in-one-project) |

Client ID 有 `claude`、`codex`、`cursor`、`vscode`、`opencode`、`kilocode`、
`grok`、`antigravity`、`amp`、`claude-desktop`、`cline`、`copilot`、`factory`、`gemini`、
`goose`、`junie`、`kiro`、`lmstudio`、`warp`、`windsurf` 和 `pi`。
`grok` 指的是官方的 xAI Grok CLI。Server 名称使用字母、
数字、点、下划线和连字符。一个 server 在同步之前，必须
直接或通过 `mcp.targets` 选择至少一个 client，除非它自己的
`targets` 是空列表。

### 保留 server 但不同步 {#keep-a-server-without-syncing-it}

带有 `targets: []` 的 server 会保留在 Skillshare source 中，不会被写入任何 client。
可以用它把一个 server 从所有 client 中拿掉，同时保留它的定义以备日后使用。
如果它之前同步过，下一次同步会从那些 client 中移除它的条目。

```yaml
mcp:
  targets: [claude, codex]
  servers:
    docs:
      url: https://example.com/mcp
      targets: []
```

```bash
skillshare mcp add docs --url https://example.com/mcp --target none
skillshare mcp edit docs --target none
skillshare mcp edit docs --target claude   # 把它加回来
```

- **不写 `targets` 则是另一回事。** 此时该 server 会继承 `mcp.targets`，如果
  那个列表也是空的，它就会被拒绝。
- `none` 不能与 client 一起使用。
- 在终端的选择菜单中，不选择任何 client 直接确认。在仪表盘中，取消勾选
  所有 client；该 server 会被标记为 **尚未选择 Agent**。
- 对 project 的 server 以及 `mcp.projects` 下的 server，行为相同。
- `disabled` 条目仍然需要至少一个 client，因为它必须在某个地方把该 server
  关闭。
- `mcp list` 会把这样的 server 显示为 `kept no targets`。

对于 Grok，名称必须以字母或下划线开头，只能包含字母、
数字、连字符和单个下划线，且不能以下划线结尾。
诸如 `company-docs` 这样的名称在所有支持的 client 中都可用。

## 原生目标位置 {#native-destinations}

| Client | Global | Project | 区块 |
|---|---|---|---|
| Claude Code | `~/.claude.json` | `.mcp.json` | `mcpServers` |
| Codex | `~/.codex/config.toml` | `.codex/config.toml` | `mcp_servers` |
| Cursor | `~/.cursor/mcp.json` | `.cursor/mcp.json` | `mcpServers` |
| VS Code | 用户级 `mcp.json`（如下） | `.vscode/mcp.json` | `servers` |
| OpenCode | `~/.config/opencode/opencode.json` | `opencode.json` | `mcp` |
| Kilo Code | `~/.config/kilo/kilo.jsonc` | `kilo.jsonc` | `mcp` |
| Grok CLI | `~/.grok/config.toml` | `.grok/config.toml` | `mcp_servers` |
| Antigravity (AGY) | `~/.gemini/config/mcp_config.json` | `.agents/mcp_config.json` | `mcpServers` |
| [Amp](https://ampcode.com/docs/customize/mcp) | `~/.config/amp/settings.json` | `.amp/settings.json` | `amp.mcpServers`（字面 key） |
| [Claude Desktop](https://modelcontextprotocol.io/docs/develop/connect-local-servers) | Claude 应用数据目录下的 `claude_desktop_config.json` | 仅限 Global | `mcpServers` |
| [Cline](https://github.com/cline/cline/tree/main/apps/vscode/src/services/mcp) | `~/.cline/data/settings/cline_mcp_settings.json` | 仅限 Global | `mcpServers` |
| [Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-mcp-servers) | `~/.copilot/mcp-config.json` | `.github/mcp.json` | `mcpServers` |
| [Factory Droid](https://docs.factory.ai/harness/mcp) | `~/.factory/mcp.json` | `.factory/mcp.json` | `mcpServers` |
| [Gemini CLI](https://geminicli.com/docs/tools/mcp-server/) | `~/.gemini/settings.json` | `.gemini/settings.json` | `mcpServers` |
| [Goose](https://block.github.io/goose/docs/guides/config-files/) | `~/.config/goose/config.yaml` | 仅限 Global | `extensions`（YAML） |
| [Junie](https://junie.jetbrains.com/docs/junie-cli-mcp-configuration.html) | `~/.junie/mcp/mcp.json` | `.junie/mcp/mcp.json` | `mcpServers` |
| [Kiro](https://kiro.dev/docs/mcp/configuration/) | `~/.kiro/settings/mcp.json` | `.kiro/settings/mcp.json` | `mcpServers` |
| [LM Studio](https://lmstudio.ai/docs/app/mcp) | `~/.lmstudio/mcp.json` | 仅限 Global | `mcpServers` |
| [Warp](https://docs.warp.dev/agents/capabilities/mcp/) | `~/.warp/.mcp.json` | `.warp/.mcp.json` | `mcpServers` |
| [Windsurf (Cascade)](https://docs.devin.ai/desktop/cascade/mcp) | `~/.codeium/windsurf/mcp_config.json` | 仅限 Global | `mcpServers` |

仪表盘的 server 表单编辑 HTTP header 的方式与编辑环境变量相同，
包括 `fromEnv` 引用。**View what each Agent gets** 位于某个 server 的菜单中，
以及其表单中文件计数旁边，只读地显示 Sync 会为所选
client 写入的原生文本；在表单中它反映的是尚未保存的编辑。密钥仍以
引用形式呈现。

JSON 条目会按照文件自身的缩进方式，逐字段单独一行写入。如果 Skillshare
拥有的某个条目仍然写在一行上，会被报告为一次 `update` 并重新
按分行格式写入。它不拥有的条目，以及由人工手动格式化的条目，会保留原有的格式。

仪表盘只提供当前作用域和主机平台下可用的目标位置。每个 server 是
一行；右侧的计数按钮会打开该 server 的完整 client 列表。仅限 Global 的 client
在 project mode 中无法被选中。右侧的 **Sync** 框列出了尚未写入的
更改：勾选某个 client 只会编辑 source，文件会在你在 Sync 页面确认后
才被写入。在其下方，**Agents** 列出了此机器上检测到的 client。当某个
client 的 MCP 文件存在，或该 client 用于保存设置的文件夹存在时，就算作
已检测到，因此即使是全新安装、还没有 MCP 文件，也仍会出现在列表中。在 project mode 下，
当项目拥有自己的 MCP 文件，或该 client 在全局范围内被检测到时，就会列出该 client。

其他 client 细节：

- `codex` 这个目标位置是一个 `config.toml`，由 Codex CLI、Codex IDE
  扩展和 ChatGPT 桌面应用共享，因此同步到 `codex` 的 server 会出现在
  这三者中。ChatGPT 桌面应用在 **Settings → MCP servers** 下列出它们。
  Codex 只有在信任某个项目时才会读取 `.codex/config.toml`；在不受信任的
  项目中，同步的 server 不会被加载，也不会报错。`cwd`、
  `http_headers_helper`、工具列表和审批模式、超时以及 `oauth` 表
  都没有可移植的形式：import 会将它们省略并给出警告，sync 则会将它们保留在
  现有条目中。由 Codex 插件捆绑的 MCP server 配置在
  `plugins.<plugin>.mcp_servers` 下，不由此处管理。
- Claude Desktop 的文件同步**仅支持 stdio**，仅限 macOS 和 Windows。
  其目录在 macOS 上为 `~/Library/Application Support/Claude`，
  在 Windows 上为 `%APPDATA%/Claude`。远程连接器需要在应用内配置。
- Cline 面向默认的 VS Code Stable profile，而不是 Cline CLI 或其他 IDE。
- Copilot CLI 为新条目导出 `tools: ["*"]`，并保留已有的工具
  过滤器。如果存在 project 级的 `.mcp.json`，同步会中止，因为 Copilot 优先读取该
  文件而不是 `.github/mcp.json`；请先合并这些文件。
  在 project mode 下同时选择 Claude Code 和 Copilot CLI 也会在写入任一文件之前
  被阻止。请为其中一个 client 使用 global mode。
- Gemini 使用 `httpUrl` 表示 Streamable HTTP。它的 `url` 字段代表旧版 SSE，
  在导入时会被拒绝。Cline 使用 `type: streamableHttp`；Goose 使用
  `type: streamable_http` 和 `uri`。Skillshare 会自动转换这些格式。
- Goose 在 Windows 上使用 `%APPDATA%/Block/goose/config/config.yaml`。YAML 编辑
  会保留不相关的设置、注释和内置 extension，但可能会改变
  格式。别名（alias）、merge、重复的 key 以及多个文档会阻止编辑。
  内置 extension 和 keychain 中的 `env_keys` 无法作为可移植的 MCP
  连接被导入。
- Claude Code 会跳过名为 `workspace`、`claude-in-chrome` 或 `computer-use` 的 server，
  这些名称被它保留给内置 server。它也绝不会向远程 server 发送自己的
  凭据：`ANTHROPIC_API_KEY`、`ANTHROPIC_AUTH_TOKEN`、`AWS_BEARER_TOKEN_BEDROCK`、
  `HTTPS_PROXY` 和 `NPM_TOKEN` 在 `url` 和 `headers` 中会读取为空。Skillshare 对
  Claude 拒绝这两者。请把凭据复制到一个你自己命名的变量中。
- Claude Code 还有一个本地作用域：用 `claude mcp add`（不带
  `--scope`）添加的 server 会按项目存储在 `~/.claude.json` 中。本地 server 会
  整体覆盖 `.mcp.json` 或 user 作用域中同名的 server。在 project mode 下，
  Skillshare 会在其隐藏的条目旁边报告这样的 server，但不会阻止同步。可以在项目文件夹中
  运行 `claude mcp remove NAME -s local` 来移除它。
- Cline 的 VS Code 扩展、CLI 和 SDK 共享 `~/.cline/data/settings/`。该
  扩展会把它较旧的 VS Code `globalStorage` 文件迁移到那里一次，之后就不再
  读取旧文件，因此 Skillshare 只有在 `~/.cline/data` 尚不存在时才会写入旧文件。
  `CLINE_MCP_SETTINGS_PATH`、`CLINE_DATA_DIR` 和 `CLINE_DIR` 会按此顺序
  被遵循。
- Windsurf 的支持针对的是文档中所述的 Cascade 配置。Windsurf 较新的
  Devin Local agent 读取它自己的 `~/.config/devin/mcp_config.json`，Skillshare
  不管理这个文件。Warp 的 project 连接仍需要在每次会话中在 Warp 内部
  批准。
- Amp 只有在执行 `amp mcp approve <name>` 之后，才会从 project 的
  `.amp/settings.json` 运行某个 server。Global server 不需要批准。
- Kiro 只会为其 "Mcp Approved Env Vars" 设置中列出的名称展开 `${VARIABLE}`，
  并且只接受 localhost 的 `http://` URL。
- VS Code 为每个非默认 profile 在 `User/profiles/` 下保留单独的 `mcp.json`。
  Skillshare 管理的是默认 profile 的文件。

环境引用对 Amp、Copilot CLI、
Factory、Gemini CLI 和 Kiro 导出为 `${VARIABLE}`，对 Cline 和 Windsurf 导出为
`${env:VARIABLE}`。Claude Desktop、Goose、Junie、LM Studio 和 Warp 目前会拒绝
`fromEnv` 和 `bearerToken` 的导出，因为它们的原生插值方式尚未得到验证。
请使用不带自定义凭据的连接，或在受支持的情况下在接收方
client 中进行认证。Skillshare 绝不会将引用解析为明文。

Antigravity 使用当前的[官方 MCP 配置](https://antigravity.google/docs/mcp)，
包括用于远程连接的 `serverUrl`。Skillshare 会自动转换可移植的 `url`。
较旧的 `.gemini/antigravity/` 和 `.gemini/antigravity-cli/` 配置
位置不受管理。Antigravity 的 `fromEnv` 和 `bearerToken` 导出会被
阻止，因为它有据可查的配置并未指定环境
插值方式。请使用不需要自定义密钥 header 的连接，并在 Antigravity 内部完成
受支持的 OAuth 登录。Skillshare 绝不会将引用展开为明文凭据。

OpenCode 会为其 global 目录遵循 `XDG_CONFIG_HOME`。如果已存在
`opencode.jsonc`，会使用它而不是创建 `opencode.json`。在项目中，
OpenCode 还会从 `.opencode/` 读取这两个文件名，因此如果文件放在那里，Skillshare 就会
写入那个文件；新文件则会创建在项目根目录。如果存在多个
文件，请在同步之前先合并它们。自定义的 OpenCode 配置
路径、目录覆盖、内联配置以及继承的祖先文件不受管理。
它们可能会在 OpenCode 中覆盖所选的目标位置。

Kilo Code 使用与 OpenCode 相同的格式。它会从项目根目录和 `.kilo/`
读取 `kilo.jsonc` 和 `kilo.json` 并进行合并，因此 Skillshare 会写入
已存在的那个文件，只有在两者都不存在时才会创建 `kilo.jsonc`。如果
两者都存在，请在同步之前先合并它们。`KILO_CONFIG`、
`KILO_CONFIG_DIR` 以及较旧 VS Code 扩展的 `mcp_settings.json` 不受
管理。

Kilo Code 将 project 配置视为不受信任。它不允许在其中使用 `{env:VARIABLE}`
引用，并且一旦发现整个 project 文件就会忽略它。因此在 project
mode 下，Skillshare 会拒绝使用了 `fromEnv` 或 `bearerToken` 的 Kilo Code server。请在
允许使用引用的 global mode 中定义该 server。

OpenCode 和 Kilo Code 使用 `local`/`remote` 类型以及 `{env:VARIABLE}` 引用；Grok 使用
`${VARIABLE}` 引用。Skillshare 会自动转换这些格式。Claude 的
`"type": "streamable-http"` 会作为 HTTP 导入。已禁用的连接会阻止导入。
其他没有可移植等价形式的原生选项，例如 Codex 的
`startup_timeout_sec` 或 `envFile`，会在导入时被省略并给出警告；
sync 会将它们保留在 Agent 现有的条目中。Pi 是通过显式
选择的第三方 extension 来支持的；见下文。

VS Code Stable 的默认用户文件是：

- macOS：`~/Library/Application Support/Code/User/mcp.json`
- Linux：`${XDG_CONFIG_HOME:-~/.config}/Code/User/mcp.json`
- Windows：`%APPDATA%/Code/User/mcp.json`

Global 的 Claude、Codex、Grok 和 Copilot 路径会遵循 `CLAUDE_CONFIG_DIR`、`CODEX_HOME`、
`GROK_HOME` 和 `COPILOT_HOME`。`OPENCODE_CONFIG` 和 `OPENCODE_CONFIG_DIR` 不受管理。Amp 和 Goose 在使用其
`.config` 路径的平台上会遵循 `XDG_CONFIG_HOME`。
Project 目标位置是相对于所选项目根目录的。Project 信任、
server 批准和身份验证仍是接收方 Agent 自身的责任。

## 在单个项目中关闭一个 global server {#turn-off-a-global-server-in-one-project}

一个 Agent 会同时读取它自己的 global MCP 文件和 project 的文件。因此
在 global 文件中定义的 server 会在每个项目中加载。要阻止它在
某个项目中加载，请添加一个**名称与该 Agent 的 global 文件所用名称相同**的条目，
并将其标记为 `disabled`。

这个方法仅适用于四个 client：

| Client | 是否支持 | Skillshare 写入的内容 |
|---|---|---|
| Claude Code | 是 | `~/.claude.json`：在此项目的 `disabledMcpServers` 列表中写入名称 |
| OpenCode | 是 | `opencode.json`：`"NAME": {"enabled": false}` |
| Kilo Code | 是 | `kilo.jsonc`：`"NAME": {"enabled": false}` |
| Pi（配合 `pi-mcp-adapter`） | 是 | `.pi/mcp.json`：`"NAME": {"disabled": true}` |
| Pi（配合 `pi-mcp-extension`） | 否 | 它没有 disable 字段 |
| Codex | 否 | 见下文 |
| 其他所有 client | 否 | 选择其中任何一个都会报错；不会写入任何内容 |

只会写入这个开关。Agent 仍会使用其 global 条目中的 command 或 URL。
其他 client 之所以被拒绝，是因为它们会用 project 条目整体替换 global 条目，
或者没有 project 文件，因此单独一个开关会破坏
该 server，而不是把它关闭。

Codex 因不同的原因被拒绝。它确实会将 `.codex/config.toml` 逐字段地
合并到 global 文件之上，因此如果某台机器的 global 配置定义了该 server，单独的
`enabled = false` 是有效的。但在没有定义该 server 的机器上，合并后的条目
没有 `command` 或 `url`，于是 Codex 会因 `invalid transport` 而无法加载它的
整个配置。`.codex/config.toml` 通常会被提交到仓库，因此一位队友的开关
可能会导致另一位队友的 Codex 无法启动。请改为在每台机器上单独
关闭该 server，在 `~/.codex/config.toml` 中设置 `enabled = false`。

### OpenCode 和 Kilo Code

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

Claude Code 会从某个作用域整体取用一个 server 条目，绝不会合并字段，因此
在 `.mcp.json` 中的开关会替换该 server，而不是将其关闭。它把
自己按项目区分的关闭列表保存在 `~/.claude.json` 中，也就是 `/mcp` 面板所编辑的那个列表。
Skillshare 会在该项目的绝对路径下把名称添加到那里，而不会向
`.mcp.json` 写入任何内容。

```bash
skillshare mcp add company-docs --disabled --target claude
skillshare sync mcp
```

- 该列表存在于你的机器上，而不是仓库中。每位队友都需要在自己的
  检出目录中运行一次 `skillshare sync mcp`。
- 你自己在 `/mcp` 中关闭的名称绝不会被认领或移除。
- 如果你在 `/mcp` 中重新打开该 server，下一次同步会报告冲突。
  请从 `.skillshare/config.yaml` 中移除该条目，或者用 replace 再次将其关闭。
- 该列表以项目路径为 key，因此移动项目后需要重新同步一次。

### Pi

Pi 需要 `piExtension`（正如每一条 Pi 条目都需要那样），并且必须是 `pi-mcp-adapter`。
OpenCode 和 Kilo Code 会忽略该字段，所以一条条目可以同时覆盖这三者：

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

### 规则

- **必须有 project 在作用范围内。** 在拥有 `.skillshare/config.yaml`（由 `skillshare init -p`
  创建）的项目内运行，传入 `-p`，或者把该条目放在
  [`mcp.projects`](#manage-several-projects-from-the-global-config) 下的某个项目根目录里。
  在 global `mcp.servers` 中没有 project 在作用范围内，因此会被拒绝。
- **`disabled` 必须单独存在。** 该条目可以带 `targets`，对 Pi 而言还可以带
  `piExtension`。添加 `command`、`url`、`env` 或 `headers` 会报错。
- **`targets` 可以省略。** 此时该条目会跟随项目的 targets：每次同步时，它都会写入
  该项目所用且支持按项目开关的 client。在 `mcp.projects` 下，Skillshare 还知道
  同名的 global server，因此范围会进一步缩小到该 server 写入的那些 client，并且 Pi 会
  沿用该 global server 的 `piExtension`。之后更改项目的 targets 时，无需修改该条目。
  如果想自行决定，请列出 `targets`；该列表中出现不受支持的 client 会报错。
- **名称必须匹配。** Skillshare 不会读取 Agent 的 global 文件，因此
  无法检查该文件中是否确实存在这个名称的 server。如果名称什么都没匹配到也无妨：
  Agent 会忽略它。
- **要重新打开它**，移除该条目（`skillshare mcp remove company-docs`）
  并同步。该开关会从它被写入的那个文件中移除：project 自己的文件，
  对 Claude Code 而言则是 `~/.claude.json`。
- **Skillshare 自身定义的 server 不需要这个方法。** 只需在该 server 上取消选择
  该 Agent，下一次同步就会移除它的条目。

在仪表盘中，这就是 **添加服务器** 旁边的 **关闭全局服务器** 按钮。它会出现在
project mode，以及项目的 MCP 标签页中。

## 通过 global 配置管理多个项目 {#manage-several-projects-from-the-global-config}

Project mode 会把每个项目的 MCP 设置保存在该项目的
`.skillshare/config.yaml` 中，并且需要在该文件夹内同步。如果你更希望
把所有项目放在同一个地方，可以在 **global** 配置的 `mcp.projects` 下列出这些项目文件夹。
之后在任意位置运行一次 `skillshare sync mcp`，就会在同一个计划中写入 global
文件和每个项目的文件。

```yaml
# ~/.config/skillshare/config.yaml
mcp:
  servers:
    context7:
      command: npx
      args: ["-y", "@upstash/context7-mcp"]
      targets: [opencode, pi]
      piExtension: pi-mcp-adapter
  projects:
    ~/work/project01:
      targets: [opencode, pi]
      servers:
        context7:                  # 仅在此项目中关闭
          disabled: true
          piExtension: pi-mcp-adapter
    ~/work/project02:
      servers:
        internal-docs:             # 仅存在于此项目中
          url: https://example.com/mcp
          targets: [opencode]
```

项目只需列出与 global 配置不同的部分。像 `context7` 这样的 global server 不需要在这里
添加条目：Agent 会同时读取它的 global 文件和 project 的文件，因此它已经会在每个项目中
加载。一条 `disabled` 条目会[在该文件夹中将它关闭](#turn-off-a-global-server-in-one-project)，
对其中列出的所有 client 生效。

每个 key 都是一个项目文件夹：可以是绝对路径，也可以是以 `~` 开头的路径。它下面写的是
该项目自己的 `config.yaml` 在 `mcp` 下会包含的同样的 `targets` 和 `servers`，
并且它们会被写入相同的 [project 文件](#native-destinations)。没有 `targets` 的
项目会继承 global 的 `mcp.targets`；没有 `directTools` 的项目则会继承 global 的
[`mcp.directTools`](#pi-direct-tools)。

当同一个 server 出现在多个位置时，预览会指明对应的文件：

```text
context7     add          opencode (~/.config/opencode/opencode.json)
context7     add          opencode (~/work/project01/opencode.json)
```

从列表中移除某个项目后，下一次同步会移除 Skillshare 在那里写入的条目，
与移除一个 server 的行为相同。

要让多个项目使用同一个 server，可以用 YAML anchor 定义一次，然后
复用它：

```yaml
mcp:
  projects:
    ~/work/project01:
      servers:
        internal-docs: &internal-docs
          url: https://example.com/mcp
          targets: [opencode]
    ~/work/project02:
      servers:
        internal-docs: *internal-docs
```

请把 anchor 保留在 `mcp.projects` 内部。指向 `mcp.servers` 上某个 anchor 的别名（alias）
也能工作，但 `skillshare mcp add` 和仪表盘会重写 `mcp.servers`；它们在
保存时会把这样的别名完整展开写出，以保证文件仍然有效，此后它就不再
跟随对该 global server 的后续修改。

### 仪表盘中的项目 {#projects-in-the-dashboard}

在 global mode 下，仪表盘中有一个 **项目** 页面。它会列出
[`projects`](/docs/reference/targets/configuration#projects) 和 `mcp.projects` 下的每个文件夹，
每个项目都有一个 **MCP** 标签页。

- **添加项目** 需要填写文件夹和它的 targets。勾选 **MCP** 可以让该文件夹同时列在
  `mcp.projects` 下。
- **MCP** 标签页列出每个 global server，并各带一个开关。关闭其中一个，会保存一条
  不带 `targets` 的 `disabled` 条目，因此它会如[上文](#turn-off-a-global-server-in-one-project)所述
  跟随项目的 targets；重新打开则会移除该条目。其下方是只存在于该项目中的 server。
- 已关闭的 server 会显示它在哪些 Agent 中被关闭的 logo。如果项目的某个 Agent 没有
  按项目的开关，该行会说明这个 server 在那里仍会加载。如果某个条目列出了自己的
  `targets`，且与项目的 targets 不同，就会出现 **改成与项目一致**：它会把该条目重新保存为
  不带 `targets` 的形式。
- **默认值** 位于 **MCP** 标签页底部，用于编辑 `mcp.targets` 和
  `mcp.directTools`。

保存只会重写你修改过的那个项目。其他项目的 YAML 保持原样，
包括 anchor 和别名（alias），写成 `~/work/app` 的文件夹也会保留它的 `~`。与
本页其他地方一样，保存只会修改 `config.yaml`；写入文件的是 Sync。

限制：

- `mcp.projects` 只会从 global 配置中读取。包含它的 project 配置会
  被拒绝。
- 没有命令可以编辑它：`skillshare mcp add` 管理 `mcp.servers`，并让
  `mcp.projects` 保持原样。请在 `config.yaml` 中编辑它，或者在
  [仪表盘](#projects-in-the-dashboard)中编辑。
- 以 Claude Code 为 target 的 `disabled` 条目会写入 `~/.claude.json`，也就是写入
  global server 的同一个文件，因为 Claude Code 把自己按项目区分的关闭列表保存在那里。
  server 本身则保持原样。
- 如果某个文件夹同时也有自己的 `.skillshare/config.yaml` 在管理同一个条目，
  计划会报告冲突，而不是将其覆盖。

## 安全性与限制

- JSONC 注释和不相关的设置会被保留。发生变化的、由 Skillshare 拥有的条目
  会作为一个整体被替换，因此这些条目内部的注释可能会改变。只有
  Skillshare 写入的字段会被比较和替换；Agent 专属的字段，例如超时，会被
  保留。
  由 Agent 自动填充的默认值，例如 `"type": "stdio"`、空的 `env` 或
  header 名称大小写，不算作变更。用 `enabled: false` 或 `disabled: true`
  关闭一个被管理的 server 会被报告为冲突。
- 当 Agent 在同一文件中重写不相关的设置时，预览仍然有效，就像 Claude Code
  对 `~/.claude.json` 所做的那样。只有该文件的 MCP 条目发生变化才需要
  新的预览。
- Codex 和 Grok 的编辑支持普通的 `[mcp_servers.NAME]` 表及其子表。
  被更新的条目会保持原位，CRLF 换行符也会被保留。
  内联/点号形式的 MCP 定义必须先转换为表格形式才能写入；
  否则会被拒绝，且不会修改文件。
- 原生文件的 symlink、格式错误的文件以及重复的 JSON 属性会阻止
  写入。被 symlink 的 Skillshare `config.yaml` 会被写入其目标文件。文件权限会被保留；新的原生
  文件、所有权记录和备份使用私有权限。
- 已经与 source 匹配的条目会被报告为未变更且不会写入，例如在
  拉取队友的更改之后。如果该配置以前从未管理过它，例如在
  移动项目之后，它就会保持无人管理状态：移除该 server 时它会原样保留，
  直到你导入它为止。一个不同的、无人管理的条目需要导入或显式的
  按条目替换；只要另一个 Skillshare 配置文件仍然存在，就不能覆盖它的
  所有权。如果该文件已经不在了，它就永远无法释放该条目，因此冲突会说明
  这是一个残留条目，并指出是哪个文件，然后在你执行显式的导入或替换时
  接管它；在终端中和在仪表盘的那条冲突上都可以这样做。只是读取不到的
  文件，例如位于未挂载的磁盘上，仍然算作拥有者还在。
- 仪表盘的 MCP 设置只有在浏览器通过 `localhost` 或 IP 地址打开
  仪表盘时才能工作。通过域名访问，包括反向
  代理，MCP 请求会返回 403，因为 DNS 重绑定攻击总是使用
  域名。
- 凭据使用环境引用；没有密钥存储、OAuth 会话同步、
  运行时健康检查、软件包安装、gateway、注册表或插件同步。
- 本版本不支持 VS Code Insiders、自定义 profile、远程工作区和旧版 SSE。
- VS Code 目前不会在 `headers` 内部替换 `${env:VARIABLE}`
  （[microsoft/vscode#336232](https://github.com/microsoft/vscode/issues/336232)），
  因此同步到 VS Code 的 header 和 `bearerToken` 引用在该问题修复之前，
  到达 server 时都是未解析的原始文本。
- 本地操作记录保存在 Skillshare state 目录下的 `mcp/` 中：
  `state.json`、写入期间的 `pending.json`，以及 `backups/`（每个
  Agent 文件保留最新的 20 份）。请勿将此
  目录作为可移植的清单来共享。


## Pi：选择你的 MCP Extension {#pi-choose-your-mcp-extension}

Pi 可以通过 [pi-mcp-adapter](https://pi.dev/packages/pi-mcp-adapter)
或 [pi-mcp-extension](https://pi.dev/packages/pi-mcp-extension) 使用 MCP。这些是 Pi 网站上列出的第三方
软件包，而不是 Pi 的内置功能。在 Pi 中安装**其中一个**：

```bash
pi install npm:pi-mcp-adapter
```

安装后重启 Pi。在 Skillshare 的 MCP 表单中，选择 **Pi**，然后选择
你所安装的软件包。导入对话框提供相同的选择。在终端中，
`mcp add` / `mcp edit` 会引导你完成选择；脚本必须提供 `--pi-extension`：

```bash
skillshare mcp add docs --url https://example.com/mcp --target pi --pi-extension pi-mcp-adapter --no-tui
skillshare sync mcp --dry-run
skillshare sync mcp
```

保存后的 server 定义是：

```yaml
mcp:
  servers:
    docs:
      url: https://example.com/mcp
      targets: [pi]
      piExtension: pi-mcp-adapter
```

对于另一个软件包，请在安装命令和选择中都使用 `pi-mcp-extension`。
一个 Skillshare source 中，所有以 Pi 为目标的 server 都必须选择
相同的软件包，因为两个软件包读取的是同一个目标文件。

| 软件包 | 原生输出 | 同步之后要做什么 |
|---|---|---|
| `pi-mcp-adapter` | `command`/`args` 或 `url`；`${VARIABLE}` 引用 | 重启/重新加载 Pi；使用 `/mcp` 查看连接。工具会按需连接。 |
| `pi-mcp-extension` | 显式的 `transport: stdio` 或 `streamable-http` | 重启 Pi；新 server 默认使用 `/mcp:start <server>` 手动启动。已有的 `lifecycle` 设置会被保留。 |

两者在 global 模式下都使用 `~/.pi/agent/mcp.json`，在 project 模式下使用 `.pi/mcp.json`。
Skillshare 使用的是这些 Pi 专属文件，而不是 adapter 共享的 `.mcp.json` 或
`~/.config/mcp/mcp.json` 输入。同名的 project 条目会覆盖 global 条目。
对于 adapter，会遵循 global 的 `PI_CODING_AGENT_DIR` 覆盖设置。
extension 不遵循该覆盖设置；global 同步会拒绝它，而不是
写入一个 extension 会忽略的文件。

adapter 在环境变量和 HTTP header 中支持 `fromEnv`。
extension **不会**插值环境引用：匹配的 stdio
变量（例如 `TOKEN: {fromEnv: TOKEN}`）会改为从 Pi 的进程中继承；
重命名变量以及基于环境变量的 HTTP 凭据会被拒绝。
遇到这些情况请使用 adapter。Skillshare 绝不会读取或复制密钥值。

### 直接工具 {#pi-direct-tools}

`pi-mcp-adapter` 通常通过一个 proxy 工具来访问 server 的工具。它的
`directTools` 设置会改为将这些工具注册为独立的 Pi 工具。请在 server 上
设置它；只有 Pi 会收到该设置，因此同一个 server 仍然可以提供给其他 Agent：

```yaml
mcp:
  servers:
    context7:
      command: npx
      args: ["-y", "@upstash/context7-mcp"]
      piExtension: pi-mcp-adapter
      directTools: true            # 或 [resolve-library-id]，或 "search"
      targets: [opencode, pi]
```

| 值 | adapter 的行为 |
|---|---|
| `true` | 注册此 server 的所有工具 |
| 名称列表 | 只注册这些工具，使用它们原始的 MCP 名称 |
| `"search"` | 以未激活状态注册工具；搜索会激活匹配的工具 |
| `false` | 仅使用 proxy，显式写入 |
| 省略 | Skillshare 不会改动该字段 |

省略表示不改动：你自己添加到 Pi 文件中的 `directTools` 会保留，并且
从配置中移除该字段并不会将它从文件中移除。要关闭它，请写入
`directTools: false`。它需要 `piExtension: pi-mcp-adapter`，并且
不能与 `disabled` 同时使用。

在命令行中，可以将 `--direct-tools` 传给 `mcp add` 或 `mcp edit`。选定
`pi-mcp-adapter` 后，仪表盘中 Pi extension 下也有相同的选项：

```bash
skillshare mcp add context7 --target pi --pi-extension pi-mcp-adapter --direct-tools true -- npx -y @upstash/context7-mcp
skillshare mcp edit context7 --direct-tools resolve-library-id,get-library-docs
```

如果想为每个 server 统一设置一次，可以将 `directTools` 直接写在 `mcp` 下。它会为
每个没有自己 `directTools` 的 `pi-mcp-adapter` server 填入该值；server 自己的值
优先。这是一个 Skillshare 默认值，会被写入每个 server 自己的条目。adapter 自身的
`settings.directTools` 与 server 定义在同一个文件中，需要你自行维护。

```yaml
mcp:
  directTools: search              # 除非另有说明，否则应用于下面每个 pi-mcp-adapter server
  servers:
    context7:
      command: npx
      args: ["-y", "@upstash/context7-mcp"]
      piExtension: pi-mcp-adapter
      targets: [pi]
```

[`mcp.projects`](#manage-several-projects-from-the-global-config) 下的项目可以
持有自己的 `directTools`，它会替换该项目的全局默认值。没有
命令可以编辑这个默认值。请在 `config.yaml` 中设置它，或者在仪表盘 MCP 页面的
**默认值** 下设置；当 Pi 是默认 target 之一时，它就会出现在那里。

使用 `--from pi` 导入会读取 Pi 专属的文件。带有 `directTools` 的条目
会连同该字段一起导入，并选定 `pi-mcp-adapter`，因为只有 adapter 才有
该字段。保存导入的连接时请选择
`--pi-extension`；仅凭文件本身无法识别安装的是哪个软件包。
仍不支持旧版 SSE。OAuth 和仅限软件包内的选项
仍由 Pi 自身管理。同步成功只代表配置已被写入，并不代表
某个 extension 已安装，或某个 server 已建立连接。

### 其他 adapter 设置 {#pi-options}

`pi-mcp-adapter` 的每个 server 字段比 Skillshare 提供的设置更多，例如
`excludeTools` 和 `approveTools`。把它们放在 `piOptions` 下，它们会原样写入
Pi 文件中该 server 的条目：

```yaml
mcp:
  servers:
    github:
      command: npx
      args: [-y, "@modelcontextprotocol/server-github"]
      piExtension: pi-mcp-adapter
      targets: [pi]
      piOptions:
        excludeTools: ["*emulator*"]
        approveTools: ["delete_*", "merge_pull_request"]
```

在命令行中，可以将一个 JSON 对象传给 `mcp add` 或 `mcp edit`。它会替换整个
`piOptions`，而 `{}` 会将其清空。仪表盘的 server 对话框中，**Direct tools**
下方也有相同的输入框，保存前会检查内容是否为 JSON 对象。

```bash
skillshare mcp edit github --pi-options '{"excludeTools":["*emulator*"]}'
```

- Skillshare 不会检查字段名称或值。只有 adapter 才了解它们。
- 由 Skillshare 自己写入的字段在这里会被拒绝：`command`、`args`、`env`、`url`、
  `headers`、`transport`、`enabled`、`disabled` 和 `directTools`。
- 这些值会按字面原样复制。凭据请通过 `fromEnv` 放在 `env` 或 `headers` 中，
  不要放在这里。
- 与 `directTools` 一样，从 `piOptions` 中移除的字段仍会留在 Pi 的文件中。请到
  那里自行删除。
- 它需要 `piExtension: pi-mcp-adapter`，并且不能与 `disabled` 同时使用。其他
  Agent 都不会收到它，`import --from pi` 也不会读回这些字段。
