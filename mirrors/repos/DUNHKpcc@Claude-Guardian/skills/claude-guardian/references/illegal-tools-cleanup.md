# 非法工具清理：破限、反代分发等 MCP、插件、hooks（Agent 提示词）

所有者 2026-10-26 要求：**清理时要查出用户给 Claude 装的非法工具，例如涉及破限、反代分发的 MCP、插件、skills、hooks，这些工具也要清理掉。**macOS、Windows、Linux 都适用。Claude 自己的缓存、日志、对话记录见 [macOS 清理](cleanup-cli-usage.md)、[Windows 清理](windows-cleanup.md)、[Linux 清理](linux-cleanup.md)；代理、VPN、终端历史见[环境痕迹清理](trace-cleanup.md)。

**和“始终保护”的关系：**各平台清理文档里 `~/.claude` 的设置、skills、插件，以及桌面端的 `claude_desktop_config.json` 始终保护，指的是不整目录清理。本文是唯一的例外：只处理审计查出来、用户逐项确认是非法工具的那几项，同一个文件、同一个目录里的其他东西一个都不动。

## 1. 算非法工具的

| 类型 | 怎么认出来 |
| --- | --- |
| **破限** | 让 Claude 绕过安全限制的提示词、skills、agents、output-styles、CLAUDE.md 片段：写着“破限”“越狱”“jailbreak”“无视之前的指令”“无任何限制”这类内容 |
| **反代分发** | 把 Claude 账号或订阅变成接口给别人用、或者用别人分发出来的接口：反代、中转、号池、拼车、账号共享服务；`ANTHROPIC_BASE_URL` 指向非官方地址；读取或转发 OAuth 令牌、会话的 MCP、插件、脚本；本机跑着的反代服务 |
| **偷传数据** | 把对话记录、令牌、凭据发到第三方的 hooks、MCP、插件 |

拿不准的一项列出来、说明看到了什么，由用户决定，不自动认定。正常的 MCP、插件、skills（比如官方或用户自己写的开发工具）不动。

## 2. 去哪查

| 位置 | 看什么 |
| --- | --- |
| `~/.claude.json` | `mcpServers`（用户级）和 `projects.<路径>.mcpServers`（项目级）里每个服务器的命令、参数、地址 |
| 项目里的 `.mcp.json` | 项目级 MCP |
| `~/.claude/settings.json`、`settings.local.json`，项目的 `.claude/settings*.json` | `hooks`、`env`（`ANTHROPIC_BASE_URL`、`ANTHROPIC_AUTH_TOKEN` 等）、`apiKeyHelper`、`statusLine` 命令、`enabledPlugins` |
| `~/.claude/` 下的 `plugins`、`skills`、`agents`、`commands`、`hooks`、`output-styles`、`mcp-servers`，全局和项目的 `CLAUDE.md` | 每一项的名字、来源和内容 |
| 桌面端 `claude_desktop_config.json`（macOS `~/Library/Application Support/Claude/`，Windows `%APPDATA%\Claude\`）和同目录的 `Claude Extensions` | MCP 服务器和桌面扩展 |
| Shell 配置（`~/.zshrc`、`~/.bashrc`、`~/.profile`）、Windows 用户环境变量 | `ANTHROPIC_BASE_URL`、`ANTHROPIC_AUTH_TOKEN`、`ANTHROPIC_API_KEY`、`CLAUDE_CODE_OAUTH_TOKEN` |
| 后台服务：macOS `~/Library/LaunchAgents`，Linux `systemctl --user`，Windows 计划任务和服务，Docker 容器，全局 npm／pip 包 | 本机跑着的反代、中转、号池服务 |

## 3. 只读审计（A 档）

先确认不是在 Claude Code 里面跑（是就停，换普通终端），并让用户退出 Claude Code 和桌面端。**只列名字、命令、地址和键名，不打印令牌、密钥的值。**不运行 `claude` 命令（包括 `claude mcp list`），只读文件。

JSON 配置用这段 Python 列出来（macOS、Linux 用 `python3`，Windows 用 `python`；把路径换成实际存在的文件）：

```python
import json, sys
sys.stdout.reconfigure(encoding="utf-8")  # Windows 控制台默认编码输出不了中文
HIDE = ("TOKEN", "KEY", "SECRET", "PASSWORD", "AUTH", "COOKIE")
def show(path):
    try:
        data = json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(path, "读不了:", exc); return
    def servers(block, where):
        for name, cfg in (block or {}).items():
            env = sorted((cfg.get("env") or {}).keys())
            print(f"[{where}] MCP {name}: {cfg.get('command') or ''} {' '.join(cfg.get('args') or [])} {cfg.get('url') or ''} env={env}")
    servers(data.get("mcpServers"), path)
    for proj, pcfg in (data.get("projects") or {}).items():
        servers(pcfg.get("mcpServers"), f"{path} 项目 {proj}")
    for k, v in (data.get("env") or {}).items():
        print(f"[{path}] env {k} =", "<已隐藏>" if any(s in k.upper() for s in HIDE) else v)
    for key in ("hooks", "apiKeyHelper", "statusLine", "enabledPlugins"):
        if key in data:
            print(f"[{path}] {key}:", json.dumps(data[key], ensure_ascii=False)[:500])
for p in sys.argv[1:]:
    show(p)
```

目录和文本：

```bash
# macOS / Linux：列出插件、skills、agents 等目录里有什么
ls -la ~/.claude/plugins ~/.claude/skills ~/.claude/agents ~/.claude/commands ~/.claude/hooks ~/.claude/output-styles ~/.claude/mcp-servers 2>/dev/null
# 搜破限、反代分发的关键词（只列文件名和行号）
P='破限|越狱|jailbreak|无视.*指令|ignore (all|previous) instructions|无任何限制|反代|中转|号池|拼车|relay|oauth.?token|session.?key|ANTHROPIC_BASE_URL'
grep -rniE -l "$P" ~/.claude/CLAUDE.md ~/.claude/skills ~/.claude/agents ~/.claude/commands ~/.claude/hooks ~/.claude/output-styles ~/.claude/plugins 2>/dev/null
grep -nE 'ANTHROPIC_(BASE_URL|AUTH_TOKEN|API_KEY)|CLAUDE_CODE_OAUTH_TOKEN' ~/.zshrc ~/.bashrc ~/.profile 2>/dev/null | sed -E 's/(TOKEN|KEY)=.*/\1=<已隐藏>/'
# 后台服务（只列名字）
ls ~/Library/LaunchAgents 2>/dev/null; systemctl --user list-units --type=service --no-pager 2>/dev/null; docker ps --format '{{.Names}} {{.Image}}' 2>/dev/null
```

```powershell
# Windows
Get-ChildItem "$env:USERPROFILE\.claude\plugins","$env:USERPROFILE\.claude\skills","$env:USERPROFILE\.claude\agents","$env:USERPROFILE\.claude\commands","$env:USERPROFILE\.claude\hooks" -ErrorAction SilentlyContinue
$P = '破限|越狱|jailbreak|无视.*指令|ignore (all|previous) instructions|无任何限制|反代|中转|号池|拼车|relay|oauth.?token|session.?key|ANTHROPIC_BASE_URL'
Get-ChildItem "$env:USERPROFILE\.claude" -Recurse -File -Include *.md,*.json,*.js,*.py,*.sh,*.ps1 -ErrorAction SilentlyContinue | Where-Object FullName -notmatch '\\projects\\' | Select-String -Pattern $P -List | Select-Object Path
'ANTHROPIC_BASE_URL','ANTHROPIC_AUTH_TOKEN','ANTHROPIC_API_KEY','CLAUDE_CODE_OAUTH_TOKEN' | ForEach-Object { if ([Environment]::GetEnvironmentVariable($_,'User')) { "$_ 已设置" } }
Get-ScheduledTask | Where-Object TaskPath -notlike '\Microsoft\*' | Select-Object TaskName,TaskPath
```

关键词命中只是线索。Agent 打开命中的文件看清楚是什么，再给用户一张清单：每一项写位置、名字、它做什么、为什么判定为破限／反代分发／偷传数据。

## 4. 清理（C 档，逐项确认）

1. 用户在对话里逐项确认要清的项目；没确认的不动。Claude Code、桌面端保持退出。
2. **备份：**把要动的配置文件整份、要移走的目录复制到 `~/.claude-guardian/illegal-tools-<时间>/`（Windows 为 `%USERPROFILE%\.claude-guardian\`），逐字节比对一致再继续。
3. **JSON 配置只删那一项：**用 Python 读入、删掉对应的 `mcpServers` 条目、`hooks` 条目、`env` 键或 `enabledPlugins` 项，其余原样写回；写回前把差异给用户看，写回后确认文件仍能解析。
4. **目录整项移走：**非法的插件、skill、agent、command、hook 脚本、桌面扩展移到隔离目录，记下原路径，可还原。
5. **环境变量：**备份后删掉 Shell 配置里对应的行；Windows 用 `[Environment]::SetEnvironmentVariable('<名字>', $null, 'User')`，删前记下原值的有无（不记值）。
6. **后台服务：**停掉并取消自启（`launchctl bootout gui/$(id -u) <plist>`、`systemctl --user disable --now <服务>`、`Disable-ScheduledTask`、`docker update --restart=no <容器>` 加 `docker stop <容器>`），plist、unit 文件移到隔离目录。卸载全局 npm／pip 包、删除容器和镜像要单独确认。
7. **令牌：**反代分发类工具读过或转发过 OAuth 令牌、API 密钥的，按凭据泄露处理：由用户本人在官方页面退出登录、重新登录或作废密钥（[accounts-and-payments.md 的 A3](accounts-and-payments.md)）。

## 5. 复验

重新跑第 3 节，清过的项目不再出现；改过的 JSON 都能解析；用户之后自己打开 Claude Code，确认正常的 MCP、插件还在。

## 6. 不做的事

永久删除；动审计没查出来、或用户没确认的项目；打印令牌、密钥的值；运行 `claude` 命令或替用户登录；整目录清理 `~/.claude`。
