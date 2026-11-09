# 环境痕迹清理：代理、VPN、终端历史里的旧 IP（Agent 提示词）

适用：账号出过事、要换环境或重新注册前，把这台电脑上**记着旧出口、真实 IP 和直连记录**的本地痕迹清掉。macOS、Windows、Linux 都适用；手机端不在本文。Claude 里装的破限、反代分发等非法工具见[非法工具清理](illegal-tools-cleanup.md)。Claude 自己的本地数据（缓存、日志、对话记录）见 [macOS 清理](cleanup-cli-usage.md)、[Windows 清理](windows-cleanup.md)、[Linux 清理](linux-cleanup.md)。

**为什么要清：**这些日志都在本地，不会自动上传。风险在于以后在这台机器上跑 Claude Code 时，Agent 读到这些文件，或者你把输出贴进对话，旧的真实 IP 和直连记录就进了对话、发到了服务器。所以在换环境、重新注册之前清掉。

**怎么做：**全部按 [C 档](authorization-tiers.md)：先列清单给用户看，备份，用户在对话里明确同意后再动。日志目录**移到私有隔离目录**，不永久删除，可还原；历史文件只删匹配的行，删前整份备份。备份和隔离目录统一放在 `~/.claude-guardian/`（Windows 为 `%USERPROFILE%\.claude-guardian\`），权限只给本人。

## 1. 代理客户端日志（Clash Verge、Mihomo、FlClash）

开了连接日志的话，这里记着每次连接的目标、走的节点、节点切换和直连（DIRECT）记录。

| 客户端 | 日志目录 |
| --- | --- |
| Clash Verge Rev（macOS） | `~/Library/Application Support/io.github.clash-verge-rev.clash-verge-rev/logs` |
| Clash Verge Rev（Windows） | `%APPDATA%\io.github.clash-verge-rev.clash-verge-rev\logs` |
| Clash Verge Rev（Linux） | `~/.local/share/io.github.clash-verge-rev.clash-verge-rev/logs` |
| FlClash 及其他客户端 | 在应用数据目录里找：`find <应用数据目录> -maxdepth 3 -iname '*log*'`（Windows：`Get-ChildItem <目录> -Recurse -Depth 3 -Filter *log*`） |
| 单独运行的 Mihomo（systemd 服务） | 日志进了系统日志（journald），按第 6 节不清，只把以后的日志等级调低 |

做法：

1. **先退出客户端**（服务模式下核心可以继续跑，它不写 Verge 的 `logs` 目录）。
2. 只读列出日志目录的文件和大小，给用户看。
3. 备份后把**整个 `logs` 目录**移到隔离目录，记下原路径。旁边的 `profiles`、`clash-verge.yaml`、`verge.yaml` 等配置**一个都不动**。
4. 重新打开客户端，确认能正常连接、配置都在。
5. **以后少记：**把核心的日志等级调到 `warning`（只记警告）或 `silent`（不记）：Clash Verge 在“设置 → Clash 设置 → 日志等级”，配置文件里是 `log-level: warning`。改前记下原值，按 B 档批准。

## 2. VPN 客户端日志

VPN 客户端通常记着以前连过的服务器地址、连接时间和断开原因。每个产品的位置不一样：

1. 先列出实际装了哪些 VPN 客户端（应用列表、系统扩展、服务列表），只读。
2. **优先用客户端自带的“清除日志”按钮**；没有按钮的，按该客户端官方说明找日志目录，在应用数据目录里用第 1 节的 `find` 方法定位。
3. 需要管理员权限或要先停服务才能动的日志（例如 WireGuard for Windows 的 `C:\Program Files\WireGuard\Data\log.bin`），先说清后果：停服务期间 VPN 断开。单独确认。
4. 同样先备份，再把日志目录或文件移到隔离目录。

## 3. Shell 历史：只删查 IP 的命令

Shell 历史只记**命令**，不记输出。要删的是查过公网 IP 的那几行，其余历史保留（所有者 2026-10-25 确认）。

匹配规则（查 IP 和测泄漏的常见站点与命令）：

```text
ipinfo\.io|ip\.sb|ifconfig\.(me|co)|icanhazip|ipify|ip-api\.com|ipapi\.co|ip\.gs|cip\.cc|myip|ipecho|checkip|whatismyip|ping0\.cc|ip\.check\.place|ip\.net\.coffee|ipleak|browserleaks|dnsleaktest
```

用户还记得用过别的查 IP 站点，加进去。

**zsh / bash（macOS、Linux）：**

```bash
# 1) 先关掉其他所有终端窗口；在这个窗口里不让历史写回
unset HISTFILE
H=~/.zsh_history          # bash 用 ~/.bash_history；以实际 $HISTFILE 为准
P='ipinfo\.io|ip\.sb|ifconfig\.(me|co)|icanhazip|ipify|ip-api\.com|ipapi\.co|ip\.gs|cip\.cc|myip|ipecho|checkip|whatismyip|ping0\.cc|ip\.check\.place|ip\.net\.coffee|ipleak|browserleaks|dnsleaktest'
# 2) 只读：数一下、列出来给用户看
grep -a -i -c -E "$P" "$H"
grep -a -i -n -E "$P" "$H"
# 3) 备份整份
B=~/.claude-guardian/backups/trace-$(date +%Y%m%d-%H%M%S); mkdir -p -m 700 "$B"; cp -p "$H" "$B/"
# 4) 用户确认后删掉匹配行（写回原文件，保留权限）
grep -a -i -v -E "$P" "$H" > "$B/filtered" && cat "$B/filtered" > "$H"
# 5) 核对：匹配行为 0，总行数 = 原行数 - 删掉的行数
grep -a -i -c -E "$P" "$H"; wc -l "$B/$(basename "$H")" "$H"
```

做完关掉这个窗口再开新终端。zsh 开了 `SHARE_HISTORY` 或 `INC_APPEND_HISTORY` 时，其他开着的窗口会把旧历史写回去，所以第 1 步必须先关掉它们。

**fish：**用自带命令逐个删，例如 `history delete --contains ipinfo.io`，按提示选择要删的条目。不要用 `grep -v` 改 fish 的历史文件（它是多行格式）。

**PowerShell（Windows）：**

```powershell
# 1) 先关掉其他 PowerShell 和终端窗口
$H = (Get-PSReadLineOption).HistorySavePath
$P = 'ipinfo\.io|ip\.sb|ifconfig\.(me|co)|icanhazip|ipify|ip-api\.com|ipapi\.co|ip\.gs|cip\.cc|myip|ipecho|checkip|whatismyip|ping0\.cc|ip\.check\.place|ip\.net\.coffee|ipleak|browserleaks|dnsleaktest'
# 2) 只读：列出来给用户看
Select-String -LiteralPath $H -Pattern $P | Select-Object LineNumber, Line
# 3) 备份整份
$B = "$env:USERPROFILE\.claude-guardian\backups\trace-$(Get-Date -Format yyyyMMdd-HHmmss)"
New-Item -ItemType Directory -Path $B -Force | Out-Null; Copy-Item -LiteralPath $H -Destination $B
# 4) 用户确认后删掉匹配行，并清掉本窗口内存里的历史
(Get-Content -LiteralPath $H) | Where-Object { $_ -notmatch $P } | Set-Content -LiteralPath $H -Encoding utf8
[Microsoft.PowerShell.PSConsoleReadLine]::ClearHistory()
# 5) 核对：应该没有输出
Select-String -LiteralPath $H -Pattern $P
```

`cmd.exe` 不保存历史，不用处理。

**还原：**把备份里的历史文件拷回原位置。

## 4. 命令的输出存在哪

查 IP 的**输出**（真实 IP、地区）只会留在下面几处，Agent 逐项问用户，不全盘搜索：

- **终端自动会话日志：**iTerm2 可以开“自动记录会话”，只读查看：`defaults read com.googlecode.iterm2 | grep -i -E 'AutoLog|LogDirectory'`，开着的话把日志目录列给用户，按第 1 节的办法隔离。Windows Terminal 和 macOS 自带终端不保存输出。
- **tmux：**滚动缓冲只在内存里，结束会话就没了；装了 tmux-resurrect 且开了 `@resurrect-capture-pane-contents` 的，`~/.tmux/resurrect` 或 `~/.local/share/tmux/resurrect` 里存着窗格内容，一并隔离。
- **`script` 录屏文件、`tee` 或重定向保存的文件：**问用户当时存到了哪里。
- **Claude Code 的对话记录：**以前让 Claude 查过 IP，输出就在 `~/.claude/projects` 里。清理 Claude 数据时 Agent 会单独问要不要移走，建议移走（见第 5 节）。

## 5. Claude 对话记录

`~/.claude/projects`（会话记录和自动记忆）和 `~/.claude/history.jsonl`（输入过的提示词）是这类痕迹最完整的一份。Agent 要单独问一句“要不要把对话记录也移走？保险起见建议移走”，用户同意后按各平台的清理指引隔离：macOS 用 `native_cleanup_mac.py` 的 `conversation` 档，Windows 见 [windows-cleanup.md](windows-cleanup.md)，Linux 见 [linux-cleanup.md](linux-cleanup.md)。后果：旧会话看不到、无法续接，可还原。

## 6. 不碰的东西

- **系统日志：**macOS 统一日志（`log erase`）、Windows 事件查看器、Linux journald 都不清。它们属于整个系统，清掉影响别的排障。
- **代理和 VPN 的配置、订阅、节点信息：**只动日志，不动配置。
- **整份 Shell 历史：**只删匹配行，其余保留。
- **浏览器历史和站点数据：**不在本文范围。
