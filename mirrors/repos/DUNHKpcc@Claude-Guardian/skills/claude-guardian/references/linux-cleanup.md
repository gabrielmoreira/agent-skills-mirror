# Linux：Claude 本机数据清理（Agent 提示词，无内置宿主）

适用：用户在 **Linux** 上要清理 Claude Code 的本地数据，包括 VM 路线的 Linux 客机、VPS 开发机和 Linux 桌面。Claude 没有官方 Linux 桌面端，本文只涉及 Claude Code。Linux 没有内置清理宿主（macOS 才有 `native_cleanup_mac.py`），由 Agent 按本文用 bash 一步步做，每一步按[分级授权](authorization-tiers.md)。分档和 [Windows 清理](windows-cleanup.md)、macOS 宿主一致。

**规则：**
- 不要由正在使用这些目录的 Claude Code 自己来执行；请用户在普通终端或 Codex 里做。
- 不永久删除：移走的东西进私有隔离目录，可还原。
- 不轮换设备标识（`userID`、`machineID`）。
- 执行 `claude` 命令（含 `claude purge`、`/logout`）属于接触 Claude，要先过 PC1；本文的步骤都不运行 `claude`。

## 1. 路径

| 对象 | Linux 路径 |
| --- | --- |
| Claude Code 用户目录 | `~/.claude`（设了 `CLAUDE_CONFIG_DIR` 则在那个目录下） |
| 全局配置、账号信息 | `~/.claude.json` |
| 登录凭据 | `~/.claude/.credentials.json` |
| Claude Code 程序 | `~/.local/bin/claude`、`~/.local/share/claude` |
| 运行缓存 | `~/.cache/claude-cli-nodejs` |
| 会话临时目录 | `/tmp/claude-$(id -u)/` |
| VS Code Remote-SSH 扩展数据（VPS 上） | `~/.vscode-server/data/User/globalStorage/anthropic.claude-code` |

以只读审计（第 3 节）看到的实际结果为准，不按猜测的路径动手。

## 2. 分档

**可再生，低风险：**`~/.claude/` 下的 `cache`、`stats-cache.json`、`telemetry`、`usage-data`、`usage.jsonl`、`usage.with-fix.jsonl`、`remote-settings.json`、`policy-limits.json` 和它的 `.stamp.json`、`shell-snapshots`、`statsig`、`logs`、`image-cache`、`debug`；`~/.cache/claude-cli-nodejs`；`/tmp/claude-$(id -u)/`。

**对话记录（先问用户，建议移走）：**`~/.claude/projects`（会话记录和自动记忆）和 `~/.claude/history.jsonl`（输入过的提示词）。会话记录里保存着 Claude Code 跑过的命令和输出，以前查过公网 IP、看过代理配置，真实 IP 和节点信息就在这里。Agent 单独问一句“要不要把对话记录也移走？保险起见建议移走”，用户同意才放进范围。后果：旧会话看不到、无法续接，自动记忆也一起移走；隔离可还原。

**始终保护，不进入任何清理范围：**`~/.claude` 整个目录，以及里面的 `file-history`、`settings.json`、`settings.local.json`、`CLAUDE.md`、`skills`、`plugins`、`commands`、`agents`、`agent-memory`、`hooks`、`rules`、`output-styles`、`workflows`、`mcp-servers`、`keybindings.json`、`themes`、`plans`、`tasks`、`todos`、`uploads`、`session-env`、`sessions`、`backups`、`jobs`、`daemon`、`.credentials.json`；`~/.claude.json`。例外：破限、反代分发等非法工具按[非法工具清理](illegal-tools-cleanup.md)逐项处理，只动查出来、用户确认的那几项。

代理客户端、VPN 和终端历史里的旧 IP 痕迹见[环境痕迹清理](trace-cleanup.md)。

## 3. 只读审计（A 档）

```bash
# 是不是在 Claude Code 里面跑的（是就停，换普通终端）
[ -n "$CLAUDECODE" ] && echo "在 Claude Code 里，停止"
# 有没有 Claude Code 进程
pgrep -a -x claude; pgrep -a -f 'claude-code|@anthropic-ai/claude-code'
# 候选路径是否存在、多大（不读内容）
for p in ~/.claude/cache ~/.claude/telemetry ~/.claude/usage-data ~/.claude/logs ~/.claude/debug \
         ~/.claude/shell-snapshots ~/.claude/statsig ~/.cache/claude-cli-nodejs "/tmp/claude-$(id -u)" \
         ~/.claude/projects ~/.claude/history.jsonl; do
  [ -e "$p" ] && du -sh "$p"
done
```

把结果列给用户，标出每个路径属于哪一档。有 Claude 进程在跑就停，请用户先退出所有 Claude Code 会话（含 VS Code 和 tmux 里的）。

## 4. 备份（B 档，整个计划批准一次）

```bash
ref="backup-$(date +%Y%m%d-%H%M%S)"
backup=~/.claude-guardian/backups/$ref
mkdir -p -m 700 "$backup"
# 对每个要处理的路径（$src），编号 root-0000、root-0001……
cp -a "$src" "$backup/root-0000"
# 逐字节比对（目录和单个文件都适用），没有输出且打印“备份一致”才继续
diff -r "$src" "$backup/root-0000" && echo 备份一致
```

不一致就停止并报告。备份含登录状态等敏感文件，目录权限只给本人，用完由用户自己删除。

## 5. 隔离（C 档，当场确认）

确认单逐项写明：要移走的每个路径及档位、受保护内容、隔离目录、备份位置、后果、还原办法。用户在对话里明确回复后才执行；沉默和超时都不算同意。

```bash
q=~/.claude-guardian/quarantine/$ref
mkdir -p -m 700 "$q"
printf '%s\n' "$src" > "$q/root-0000.path"
mv "$src" "$q/root-0000"
```

移完核对：受保护路径仍在；用户没选对话记录时 `projects` 和 `history.jsonl` 没动；隔离目录里的内容与备份一致。`/tmp` 和家目录不在同一个文件系统时 `mv` 会变成复制再删除，先用 `df` 确认，跨盘的路径单独说明。

**还原（单独再确认一次）：**

```bash
mv "$q/root-0000" "$(cat "$q/root-0000.path")"
```

## 6. 退出登录与凭据（C 档，单独确认）

登录凭据在 `~/.claude/.credentials.json`。官方的退出办法是在 Claude Code 里输入 `/logout`，那属于运行 Claude（PC1）。不运行 Claude 时要退出登录，只能把这个文件移走：先说明后果（需要重新登录），备份后再移，单独确认。

## 7. 官方的项目级清理

`claude purge <项目路径> --dry-run` / `claude purge <项目路径>` 只清一个项目的对话记录、自动记忆和 `~/.claude.json` 里该项目的条目。它要运行 Claude，由用户自己决定，且先过 PC1。

## 8. 不做的事

永久删除；轮换设备标识；读取凭据内容；卸载程序（单独确认）；清系统日志（journald）。
