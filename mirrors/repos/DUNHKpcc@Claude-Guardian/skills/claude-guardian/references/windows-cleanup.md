# Windows：Claude 本机数据清理（Agent 提示词，无内置宿主）

适用：用户在 **Windows** 上要清理 Claude Code 或 Claude 桌面端的本地数据。**Windows 没有内置清理宿主和事务引擎**（macOS 才有 `native_cleanup_mac.py`），全部由 Agent 按本文用 PowerShell 一步一步做，每一步按[分级授权](authorization-tiers.md)。路径和行为来自 Claude 官方文档，官方没写的地方明确标出，不凭记忆补。

**硬规则：**
- 不要由正在使用这些目录的 Claude Code 或 Claude 桌面端自己来执行；请用户在普通 PowerShell 或 Codex 里做。
- 不永久删除：移走的东西进私有隔离目录，可还原。
- 不轮换设备标识（`userID`、`machineID`）。不承诺解封或解除关联。
- 执行 `claude` 命令（含 `claude purge`、`/logout`）属于接触 Claude，要先过 PC1；本文的步骤都不运行 `claude`。

## 1. 官方文档给出的路径

| 对象 | Windows 路径 | 来源 |
| --- | --- | --- |
| Claude Code 用户目录 | `%USERPROFILE%\.claude`（设了 `CLAUDE_CONFIG_DIR` 则在那个目录下） | [Explore the .claude directory](https://code.claude.com/docs/en/claude-directory) |
| 全局配置、账号信息 | `%USERPROFILE%\.claude.json` | 同上；[卸载说明](https://code.claude.com/docs/en/setup#uninstall-claude-code) |
| 登录凭据 | `%USERPROFILE%\.claude\.credentials.json`（继承用户目录的访问控制） | [Authentication - Credential management](https://code.claude.com/docs/en/authentication#credential-management) |
| Claude Code 程序 | `%USERPROFILE%\.local\bin\claude.exe`、`%USERPROFILE%\.local\share\claude` | [Uninstall a native installation](https://code.claude.com/docs/en/setup#uninstall-a-native-installation) |
| WinGet 安装 | `winget uninstall Anthropic.ClaudeCode` | 同上 |
| VS Code 扩展数据 | `%APPDATA%\Code\User\globalStorage\anthropic.claude-code` | [卸载说明](https://code.claude.com/docs/en/setup#remove-configuration-files) |
| Anthropic 配置目录（profile） | `%APPDATA%\Anthropic` | [Authentication](https://code.claude.com/docs/en/authentication#anthropic-profiles-and-federation-credentials) |
| 会话临时目录 | `%TEMP%\claude\<project>\<session-id>\scratchpad\` | [claude-directory](https://code.claude.com/docs/en/claude-directory#session-scratchpad-directory) |
| Claude 桌面端配置、日志 | `%APPDATA%\Claude\claude_desktop_config.json`、`%APPDATA%\Claude\logs` | [MCP：连接本地服务器](https://modelcontextprotocol.io/docs/develop/connect-local-servers) |

**官方没有写出的：**桌面端其余本地数据（登录状态、网页存储、MSIX 包的本地应用数据）的具体路径。[部署指南](https://support.claude.com/en/articles/12622703-deploy-claude-desktop-for-windows)只说安装器的自动修复会删除“上一个包的本地应用数据，包括应用设置”，聊天记录和你自己文件夹里的文件不受影响。所以先用只读命令列出实际有什么（第 3 步），拿给用户看，**不按猜测的路径动手**。

## 2. 分档（沿用 macOS 宿主的划分）

**可再生，低风险**（官方说删除“没有用户可见损失”或会自动重新获取）：`%USERPROFILE%\.claude\` 下的 `cache`、`stats-cache.json`（只丢 `/usage` 历史合计）、`telemetry`、`usage-data`、`usage.jsonl`、`usage.with-fix.jsonl`、`remote-settings.json`、`policy-limits.json` 和它的 `.stamp.json`、`shell-snapshots`，以及旧版本遗留目录 `statsig`、`logs`、`image-cache`，调试日志 `debug`；桌面端的 `%APPDATA%\Claude\logs`。

**桌面端持久数据，含登录状态：**`%APPDATA%\Claude` 下除 `claude_desktop_config.json` 以外的内容。**`claude_desktop_config.json` 是你的 MCP 服务器配置，默认保留，**要动它必须单独说明并确认（里面的非法 MCP 按[非法工具清理](illegal-tools-cleanup.md)逐项处理）。

**对话记录（先问用户，建议移走）：**`%USERPROFILE%\.claude\projects`（每个项目的会话记录和自动记忆）和 `%USERPROFILE%\.claude\history.jsonl`（输入过的提示词）。会话记录里保存着 Claude Code 跑过的命令和输出，以前让 Claude 查过公网 IP、看过代理配置，真实 IP 和节点信息就在这里。清理时 Agent 要单独问一句“要不要把对话记录也移走？保险起见建议移走”，用户同意才放进范围。后果：旧会话在 Claude Code 里看不到、无法续接，自动记忆也一起移走；隔离可还原。

**始终保护，不进入任何清理范围：**`%USERPROFILE%\.claude` 整个目录，以及里面的 `file-history`、`settings.json`、`settings.local.json`、`CLAUDE.md`、`skills`、`plugins`、`commands`、`agents`、`agent-memory`、`hooks`、`rules`、`output-styles`、`workflows`、`mcp-servers`、`keybindings.json`、`themes`、`plans`、`tasks`、`todos`、`uploads`、`session-env`、`sessions`、`backups`、`jobs`、`daemon`、`.credentials.json`。官方也明确说：不要单独删 `settings.json`、`plugins`，不要删 `~/.claude.json`，除非你要彻底清掉账号、偏好和插件。例外：破限、反代分发等非法工具按[非法工具清理](illegal-tools-cleanup.md)逐项处理，只动查出来、用户确认的那几项。

代理客户端、VPN 和终端历史里的旧 IP 痕迹见[环境痕迹清理](trace-cleanup.md)。

**不在范围：**卸载程序（用 `winget uninstall` 或系统设置，单独确认）、凭据（见第 6 步）、浏览器站点数据、永久删除。

## 3. 只读审计（A 档，范围确认后自行做）

在普通 PowerShell 里，只读：

```powershell
# 有没有 Claude 进程（桌面端、CLI、编辑器里的 Claude Code）
Get-Process | Where-Object { $_.ProcessName -match '^(claude|Claude)' } | Select-Object Id, ProcessName, Path
# 候选目录是否存在、多大（不读文件内容）
foreach ($p in "$env:USERPROFILE\.claude\cache", "$env:USERPROFILE\.claude\telemetry", "$env:USERPROFILE\.claude\usage-data",
              "$env:APPDATA\Claude", "$env:APPDATA\Claude\logs") {
  if (Test-Path -LiteralPath $p) { "{0}  {1:N0} MB" -f $p, ((Get-ChildItem -LiteralPath $p -Recurse -Force -File -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum / 1MB) }
}
# 桌面端是否是 MSIX 包，它的包数据在哪（只列名称和位置）
Get-AppxPackage | Where-Object { $_.Name -match 'Claude' } | Select-Object Name, PackageFamilyName, InstallLocation
Get-ChildItem "$env:LOCALAPPDATA\Packages" -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -match 'Claude' } | Select-Object FullName
```

把结果列给用户，包括哪些路径存在、各自属于哪一档。**有进程在运行就停，请用户先退出所有 Claude、VS Code 里的 Claude Code 和终端会话。**

## 4. 备份（B 档，整个计划批准一次）

备份会包含登录状态等敏感文件，所以放在只有你自己能访问的目录：

```powershell
$ref = "backup-$(Get-Date -Format yyyyMMdd-HHmmss)"
$backup = "$env:USERPROFILE\.claude-guardian\backups\$ref"
New-Item -ItemType Directory -Path $backup -Force | Out-Null
icacls $backup /inheritance:r /grant:r "$($env:USERNAME):(OI)(CI)F" | Out-Null
# 逐文件清单：相对路径、大小、SHA-256 三项都要对上，只比哈希集合会漏掉放错位置的文件
function Get-Manifest($root) {
  $base = (Resolve-Path -LiteralPath $root).Path.TrimEnd('\') + '\'
  Get-ChildItem -LiteralPath $root -Recurse -Force -File | ForEach-Object {
    [pscustomobject]@{ Rel = $_.FullName.Substring($base.Length); Size = $_.Length
                       Hash = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash }
  } | Sort-Object Rel
}
# 对每个要处理的目录：复制，再按清单比对
Copy-Item -LiteralPath $src -Destination (Join-Path $backup 'root-0000') -Recurse -Force
$a = @(Get-Manifest $src)
$b = @(Get-Manifest (Join-Path $backup 'root-0000'))
($a.Count -eq $b.Count) -and ($a.Count -eq 0 -or -not (Compare-Object $a $b -Property Rel, Size, Hash))   # 必须是 True
```

比对不一致就停止并报告，不继续。备份目录由你自己保管，用完自己删除。

**备份可以放在另一个盘**（例如 D 盘，`$backup` 换成那个盘上只有你能访问的目录），但隔离目录不跟着换，见第 5 节。

## 5. 隔离（C 档，当场确认）

确认页必须逐项写明：要移走的每个目录及档位、受保护内容、隔离目录、备份位置、后果（桌面端会像新安装一样启动，登录状态丢失）、恢复办法。**你在对话里明确回复后才执行。**Windows 没有 macOS 那样的终端确认短语，沉默和超时都不算同意，Agent 不能自己批准。

**隔离目录放在原件所在的同一个盘。**同盘的 `Move-Item` 是重命名：一步完成，原件要么还在原处、要么已整体进了隔离目录，不会出现半套状态。跨盘的“移动”实际是复制、校验、再删原件三个阶段，最后一步是永久删除原件，本文不做（硬规则：不永久删除），而且 Agent 宿主常会拒绝这类删除命令。所以：

- 需要把数据放到另一个盘时，**放的是备份**（第 4 节），原件仍在本盘隔离。
- **副本建好不等于清理完成。**只要原件还在原路径，就只能报告“备份或副本已生成并校验，清理未完成”，不能说已清理。
- C 盘空间不够放隔离目录时不需要额外空间：同盘重命名不占用新空间。
- 本盘隔离目录里的内容，等你确认一切正常后由你自己决定是否删除（属于你自己的操作，见本节末尾的交接单）。

每完成一个阶段，在隔离目录的阶段记录里追加一行，中途被打断也知道停在哪：

```powershell
$q = "$env:USERPROFILE\.claude-guardian\quarantine\$ref"
New-Item -ItemType Directory -Path $q -Force | Out-Null
# 记下原路径，才能还原；然后移走（同一个盘内是重命名，不是复制再删除）
"$src" | Out-File -LiteralPath (Join-Path $q 'root-0000.path') -Encoding utf8
Add-Content -LiteralPath (Join-Path $q 'stages.log') "$(Get-Date -Format s) backup_verified root-0000 $backup"
Move-Item -LiteralPath $src -Destination (Join-Path $q 'root-0000')
Add-Content -LiteralPath (Join-Path $q 'stages.log') "$(Get-Date -Format s) quarantined root-0000"
# 移完核对：原路径已不存在；隔离副本与备份清单一致
(-not (Test-Path -LiteralPath $src)) -and
  ($a.Count -eq @(Get-Manifest (Join-Path $q 'root-0000')).Count) -and
  -not (Compare-Object $a @(Get-Manifest (Join-Path $q 'root-0000')) -Property Rel, Size, Hash)   # 必须是 True
```

移完还要核对：受保护路径仍在；用户没选对话记录时 `history.jsonl` 和 `projects` 没动。阶段记录里有 `quarantined` 且上面的核对为 True，这一项才算清理完成。

**还原（单独再确认一次）：**

```powershell
$orig = (Get-Content -LiteralPath (Join-Path $q 'root-0000.path') -Raw).Trim()
Move-Item -LiteralPath (Join-Path $q 'root-0000') -Destination $orig
```

### 被宿主策略或权限拦截时

命令被拒绝时（例如工具调用返回 `blocked by policy`、`Access denied`、文件被占用），按下面做：

1. **立即停止。**不换命令、不换工具、不换 shell 或渠道重试，不用别的写法绕开限制，也不自己把被拒的动作拆成小步再试。
2. **分清拦截来自哪一层，原因不明就写不明：**
   - **Agent 宿主策略**：命令在启动前就被宿主拒绝（如 `blocked by policy`），PowerShell 根本没执行。这是宿主的规则，本 Skill 和 Agent 都不能改，也不能推断具体是哪条规则。
   - **本项目的门禁**：授权档位没满足（例如 C 档没有当场确认）。按[分级授权](authorization-tiers.md)补确认，不算故障。
   - **Windows 文件权限或占用**：PowerShell 执行了但报 `Access denied`、`being used by another process`。先只读查有没有 Claude 进程（第 3 节）和目录权限，不提权、不改 ACL。
3. **只读核对现状**，逐项报告：每个原路径是否还在；每个备份、隔离副本是否存在、清单是否一致；阶段记录停在哪一步；有没有 Claude 进程。
4. **脱敏报告给用户**：哪一步、哪个命令被拒、返回原文（去掉用户名和完整路径）、属于哪一层（或“不明”）、现在的状态、**清理未完成**。用户说“我自己删可以”，只说明用户那边能做，不能用来判断这次拦截的原因。
5. **给用户选择，任何一项都单独确认：**保持现状（原件和副本都留着，之后再做）；把这一步交给用户自己做（见下面的交接单）；或者撤回本次已做的部分（Agent 自己建的副本属于 Agent 的产物，是否移走同样要确认）。

### 交给用户自己操作时的交接单

用户愿意自己动手时，Agent 给出一张交接单，不要求用户上传对话历史、凭据或目录内容：

- **准确范围**：只列这次确认过的目录，每个写完整的相对说明（如 `%USERPROFILE%\.claude\projects`），不扩大。
- **影响**：会话记录和自动记忆会从 Claude Code 里消失；桌面端数据会像新安装一样，登录状态丢失。
- **备份和副本在哪**：备份目录、隔离目录、阶段记录的位置，以及第 4 节比对已通过。
- **推荐做法**：用本节上面的 `Move-Item` 移到同盘隔离目录，而不是直接删除；还原命令照抄本节的还原块。
- **做完后告诉 Agent**：Agent 再只读核对一遍（原路径不在、受保护路径仍在、隔离副本与备份一致），然后才写“清理完成”。用户自己的操作结果由 Agent 核对后记录，不由 Agent 推测。

## 6. 退出登录与凭据（C 档，单独确认）

- **Claude Code：**登录凭据在 `%USERPROFILE%\.claude\.credentials.json`。官方的退出办法是在 Claude Code 里输入 `/logout`，那属于运行 Claude（PC1）。要在不运行 Claude 的情况下退出登录，只能移走这个文件：它属于凭据，先说明后果（需要重新登录），备份后再移，单独确认。
- **Claude 桌面端：**清掉 `%APPDATA%\Claude` 里的持久数据就会退出登录（第 5 步），官方没有单独的退出路径文档。
- Windows 凭据管理器里是否有 Claude 条目，官方文档没有写。如需检查，只读：`cmdkey /list`，把包含 `Claude` 的目标名列给用户看；删除用 `cmdkey /delete:<目标名>`，C 档，不可恢复，且不读取内容。

## 7. 最小提示词模式（可选，C 档）

`CLAUDE_CODE_SIMPLE=1`（官方环境变量，等同 `--bare`）：最小系统提示词，只保留 Bash、文件读写工具，不自动发现 hooks、skills、plugins、MCP、自动记忆和 CLAUDE.md；**不读取 OAuth 令牌和钥匙串凭据，认证只能用 `ANTHROPIC_API_KEY` 或 `apiKeyHelper`，订阅登录在此模式下不可用。**修改 `%USERPROFILE%\.claude\settings.json` 的 `env`：先备份文件，用结构化 JSON 工具改（PowerShell 的 `ConvertTo-Json` 必须加 `-Depth 100`，否则嵌套内容会被截断），只增删这一个键，改完对比其余键完全一致。

## 8. 官方的项目级清理

官方有 `claude purge <项目路径> --dry-run` / `claude purge <项目路径>`，只清一个项目的对话记录、自动记忆和 `~/.claude.json` 里该项目的条目，会先打印计划并要求确认。它要运行 Claude，所以由用户自己决定，且先过 PC1。`shell-snapshots` 和 `backups` 它不处理。

## 9. 不做的事

永久删除；轮换设备标识；改系统时区（属于环境对齐，不在清理里做，按[浏览器环境验收](whole-machine-ipv4.md#browser-acceptance)第 4 条改）；动注册表；用 `Get-AppxPackage | Remove-AppxPackage` 卸载桌面端（单独确认，且官方提醒 Repair/Reset 会删本地应用数据）；读取凭据内容；清理浏览器站点数据；承诺解封。

## 10. 限制

没有内置宿主，所以没有进程独占、没有模块自带的哈希清单，也没有终端确认短语，同意靠对话里的明确回复。命令是 PowerShell 的常规用法，**没有在真实 Windows 机器上跑过**；首次使用先用 `-WhatIf`（`Move-Item`、`Copy-Item` 支持）演练。桌面端的 MSIX 数据路径要在审计里看到实际结果后再用。备份放另一个盘、阶段记录、宿主拦截后的停止与交接，来自用户在 Windows（Codex 桌面端，PowerShell 7）上的反馈（issue #16）：那次跨盘复制和校验做完了，删除原件那一步被宿主拒绝；本文改为同盘隔离、不删除原件之后的流程，尚未在真机上重跑。
