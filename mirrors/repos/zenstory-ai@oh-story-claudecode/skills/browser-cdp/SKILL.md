---
name: browser-cdp
description: "Use this skill when you need to control a Chrome browser via CDP (Chrome DevTools Protocol) to reuse existing login sessions. Covers: launching Chrome in debug mode, opening URLs, waiting for page load, evaluating JavaScript, taking snapshots, and extracting auth tokens. Trigger phrases: browser automation, CDP, agent-browser, 浏览器操作, 操作浏览器, Chrome CDP, 复用登录态, extract token from browser."
metadata: {"openclaw":{"requires":{"bins":["agent-browser"]},"source":"https://github.com/zenstory-ai/oh-story-claudecode"}}
---
# Browser CDP 操作工具

通过 CDP（Chrome DevTools Protocol）连接 Chrome，复用登录态并执行浏览器操作。

## 前置条件

- macOS / Linux / Windows（实验性），已安装并使用过 Google Chrome，来源 profile 已存在
- Node.js 20+
- `agent-browser` 已安装：`npm install -g agent-browser`

> 启动或重建时，若需结束 Chrome 进程，先按下方流程征得同意；未保存的标签页或草稿可能丢失。

---

## 启动流程（skill-mode 强制步骤）

**第一步：探测当前状态（无副作用）**

```bash
node {SKILL_DIR}/scripts/setup-cdp-chrome.js 9222 --detect-only
```

输出形如：

```
CDP_STATUS=ready                        # 已就绪，可直接复用
CDP_URL=http://127.0.0.1:9222/json/version
BROWSER=Chrome/148.0.7778.168
```

或：

```
CDP_STATUS=needs-setup
CHROME_RUNNING=yes                      # 用户有 Chrome 在跑，启动会杀掉
CHROME_PID_COUNT=3
```

**第二步：根据探测结果分支**

- `CDP_STATUS=ready` 且本次只需连接 → 直接使用 `agent-browser --cdp 9222 ...`，**不要运行 setup**。
- 明确请求 `--reset` / `--profile` → 即使 ready 也走重建。用 `--dry-run` 查看将结束的进程，按下方同意流程带原定选项启动。
- `CDP_STATUS=needs-setup` 且 `CHROME_RUNNING=no` → 安全启动：
  ```bash
  node {SKILL_DIR}/scripts/setup-cdp-chrome.js 9222 --yes
  ```
- `CDP_STATUS=needs-setup` 且 `CHROME_RUNNING=yes` → **先向用户确认**：告知会结束 N 个 Chrome 进程、可能丢失未保存工作；同意后带 `--yes` 启动，拒绝则放弃这次自动化。

非 TTY 调用中，Chrome 在运行且未传 `--yes` 时，脚本以退出码 3 报 `NEEDS_CONSENT: ...` 并中止。取得同意后再重跑，不自动补 `--yes`。

---

## 启动脚本选项

| 选项 | 说明 |
|------|------|
| `--detect-only` | 只探测，不修改任何状态（skill 用） |
| `--yes` | 已征得同意，跳过交互提示 |
| `--reset` | 启动前清空 `~/chrome-debug-profile`（登录失效时用） |
| `--profile <name>` | 指定来源 profile（默认 `Default`，如 `"Profile 1"`）；显式传入即重建 |
| `--dry-run` | 打印将执行的步骤，不执行 |

退出码：`0` 成功 / `1` 通用错误 / `2` 用户拒绝（TTY）/ `3` 需同意但缺 `--yes`。

---

## 常用操作

### 打开页面并等待加载

```bash
agent-browser --cdp 9222 open "<URL>"
agent-browser --cdp 9222 wait 3000
```

### 提取页面文本

```bash
agent-browser --cdp 9222 eval 'document.body.innerText.substring(0, 8000)'
```

### 提取 Auth Token

示例读取 localStorage 的 `token` 项或 JavaScript 可读的 Cookie；实际存放位置按站点确认。

```bash
agent-browser --cdp 9222 eval 'localStorage.getItem("token") || document.cookie'
```

### 复杂 JS（含引号 / `$` / 反引号）

用 base64 或标准输入传入脚本，避免 shell 转义错误：

```bash
# 1) base64 包裹
agent-browser --cdp 9222 eval -b "$(echo -n "document.querySelectorAll('a').length" | base64)"

# 2) heredoc + --stdin
cat <<'EOF' | agent-browser --cdp 9222 eval --stdin
const links = document.querySelectorAll('a');
links.length;
EOF
```

### 页面交互（snapshot 拿元素引用）

```bash
agent-browser --cdp 9222 snapshot -i        # 仅交互元素
agent-browser --cdp 9222 click "<CSS or @e1>"
agent-browser --cdp 9222 type "<sel>" "<text>"
```

---

## 停止 / 清理

- 关掉 debug Chrome 窗口即可。若窗口无响应，先按 `--user-data-dir` 核验出 debug 实例的 PID 再只结束它：
  - macOS / Linux：`pgrep -af chrome-debug-profile`
  - Windows：`wmic process where "name='chrome.exe'" get ProcessId,CommandLine | findstr chrome-debug-profile`
  核验 PID 后用 `kill -9 {PID}` / `taskkill /F /PID {PID}`，无法核验则停止。**手工清理不得按 Chrome 可执行文件名批量结束进程**；启动脚本仍走上述同意流程。
- 登录态失效：`node {SKILL_DIR}/scripts/setup-cdp-chrome.js 9222 --reset --yes` 重新复制来源 profile；需结束 Chrome 时仍先征得同意。

---

## OpenCode 环境注意事项

在 OpenCode 前台执行耗时的 CDP 命令时，为页面加载和批量采集设置超时，避免单次调用长时间占住会话。

### 超时包装

Windows 用 PowerShell Job 设置超时：

```powershell
$job = Start-Job { agent-browser --cdp 9222 eval "window.location.replace('https://www.qidian.com/rank/')" }
Wait-Job $job -Timeout 30 | Out-Null
if ($job.State -eq 'Running') { Stop-Job $job; Write-Output "⏱ CDP 操作超时（30s），请重试或手动打断" }
else { Receive-Job $job }
Remove-Job $job -Force
```

macOS / Linux 有 `timeout` 时：

```bash
timeout 30 agent-browser --cdp 9222 eval "window.location.replace('https://www.qidian.com/rank/')" || echo "⏱ CDP 操作超时（30s），请重试或手动打断"
```

### 已知限制

| 场景 | 风险 | 缓解 |
|------|------|------|
| 页面加载超时 | eval 命令等待永不返回 | 设置 30s 超时，超时后重试 |
| 大批量数据抓取 | 多页翻页时累计等待过长 | 每页独立超时，失败后从断点继续 |
| Chrome 进程僵死 | CDP 连接断开但进程未退出 | 先核验 debug profile 对应 PID，只结束该 debug 实例后重连；不得连带普通 Chrome |
| 网络波动 | 请求挂起无超时 | 超时后自动重试一次 |

持续卡死时，在 OpenCode 按 `ESC` 打断。

---

## 常见问题

| 问题 | 解决方案 |
|------|----------|
| `NEEDS_CONSENT` + 退出码 3 | 询问用户是否允许结束现有 Chrome，同意后加 `--yes` 重跑 |
| `CHROME_INSTALLED=no` 或来源 profile 不存在 | 安装并使用 Chrome 一次；已有其他 profile 时用 `--profile` 指定 |
| CDP 端口未监听 | `--detect-only` 再确认；端口被占用则换端口 |
| 页面跳转到登录页 | `snapshot -i` 找登录按钮并操作 |
| `eval` 返回 `null` | 检查 localStorage key 名；含引号的 JS 用 `eval -b` 或 `--stdin` |
| 登录态过期 | `setup-cdp-chrome.js 9222 --reset --yes` 重新拷贝 |
| 有多个 Chrome profile | `--profile "Profile 1"` 指定 |
| Chrome 不会启动（30s 超时） | 试 `--reset`；检查端口冲突；查看 `~/chrome-debug-profile/` 是否损坏 |
