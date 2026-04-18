# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

Clawd 桌宠 — 一个 Electron 桌面宠物，通过 hook 系统和日志轮询实时感知 AI coding agent 的工作状态并播放对应的像素风动画（SVG / APNG / GIF / PNG 等）。支持 **Claude Code**（command + HTTP hook）、**Codex CLI**（JSONL 日志轮询）、**Copilot CLI**（command hook）、**Cursor Agent**（`~/.cursor/hooks.json`，stdin JSON + stdout JSON）、**Gemini CLI**（session JSON 轮询）、**Kiro CLI**（per-agent `~/.kiro/agents/*.json`）、**CodeBuddy**（Claude Code-兼容 hook）、**opencode**（in-process plugin + 反向 HTTP bridge）并行运行。内置两套主题 **Clawd**（像素螃蟹）与 **Calico**（三花猫），并支持用户自定义主题。支持 Windows、macOS 和 Linux，UI 三语（en / zh / ko）。

## 常用命令

```bash
npm start              # 启动 Electron 应用（开发模式）
npm run build          # electron-builder 打包 Windows NSIS 安装包
npm run build:mac      # electron-builder 打包 macOS DMG（x64 + arm64）
npm run build:linux    # electron-builder 打包 Linux AppImage + deb
npm run build:all      # 同时打包 Windows + macOS + Linux
npm install            # 安装依赖（electron + electron-builder）
npm run install:claude-hooks   # 手动注册 Claude Code hooks 到 ~/.claude/settings.json
npm run uninstall:claude-hooks # 移除 Claude Code hooks
npm run install:cursor-hooks   # 注册 Cursor Agent hooks 到 ~/.cursor/hooks.json
npm run install:gemini-hooks   # 注册 Gemini CLI hooks 到 ~/.gemini/settings.json
npm run install:kiro-hooks     # 注入 Clawd hooks 到 ~/.kiro/agents/*.json（含维护 clawd agent）
npm run create-theme           # 脚手架生成新主题（用户 themes 目录下），见 docs/guides/guide-theme-creation.md
npm test               # 运行单元测试（node --test test/*.test.js）
```

手动测试状态切换：
```bash
curl -X POST http://127.0.0.1:23333/state \
  -H "Content-Type: application/json" \
  -d '{"state":"working","svg":"clawd-working-building.svg"}'
```

Shell 测试脚本（仅开发用，不随仓库分发）：
```bash
bash test-demo.sh [秒] # 逐个播放所有 SVG 动画（默认每个 8 秒）
bash test-mini.sh [秒] # 逐个播放极简模式 SVG 动画（默认每个 6 秒）
bash test-sleep.sh     # 缩短睡眠超时快速测试睡眠序列
bash test-bubble.sh    # 发送模拟权限请求测试气泡堆叠
bash test-macos.sh     # macOS 适配测试（需先 npm start）
bash test-oneshot-gate.sh [state] [秒] # 测 Animation Map 的 5 个 ONESHOT disable 开关（error/notification/sweeping/attention/carrying），省略 state 则全测
```

单元测试覆盖 agents/、hook 注册和端口发现逻辑（`test/registry.test.js`、`test/codex-log-monitor.test.js`、`test/gemini-log-monitor.test.js`、`test/gemini-install.test.js`、`test/install.test.js`、`test/server-config.test.js`、`test/menu-autostart.test.js`），使用 Node.js 内置 test runner。Electron 主进程（状态机、窗口、托盘）无自动化测试，依赖手动 + shell 脚本验证。

## 架构与数据流

```
Claude Code 状态同步（command hook，非阻塞）：
  Claude Code 触发事件
    → hooks/clawd-hook.js（零依赖 Node 脚本，stdin 读 JSON 取 session_id + source_pid）
    → HTTP POST 127.0.0.1:23333/state { state, session_id, event, source_pid, cwd }
    → src/server.js 路由 → src/state.js 状态机（多会话追踪 + 优先级 + 最小显示时长 + 睡眠序列）
    → IPC state-change 事件
    → src/renderer.js（<object> SVG 预加载 + 淡入切换 + 眼球追踪）

Copilot CLI 状态同步（command hook，非阻塞）：
  Copilot 触发事件
    → hooks/copilot-hook.js（camelCase 事件名 → agents/copilot-cli.js 映射 → HTTP POST）
    → 同上状态机

Cursor Agent 状态同步（command hook，stdin JSON，非阻塞）：
  Cursor IDE 触发事件
    → hooks/cursor-hook.js（hook_event_name → 映射为 PascalCase event + HTTP POST，stdout 返回 allow/continue 以满足 preToolUse 等 hook）
    → 同上状态机（agent_id: cursor-agent）

Codex CLI 状态同步（JSONL 日志轮询，~1.5s 延迟）：
  Codex 写入 ~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl
    → agents/codex-log-monitor.js（增量读取，事件类型 → agents/codex.js 映射）
    → 同上状态机

Gemini CLI 状态同步（session JSON 轮询，~1.5s 延迟 + 4s 完成延迟窗口）：
  Gemini 写入 ~/.gemini/tmp/<project>/chats/session-*.json
    → agents/gemini-log-monitor.js（轮询 JSON，diff 消息数组检测工具调用/完成）
    → 同上状态机（agent_id: gemini-cli）

Kiro CLI 状态同步（per-agent hook，stdin JSON）：
  Kiro CLI 触发事件
    → hooks/kiro-hook.js（camelCase 事件 → agents/kiro-cli.js 映射 → HTTP POST）
    → 同上状态机（agent_id: kiro-cli）
  注意：Kiro 无 global hooks，hooks/kiro-install.js 把 hook 注入到 ~/.kiro/agents/ 下每个
  custom agent 配置里，并额外维护一个 "clawd" agent（继承 kiro_default，启动时从 kiro_default
  重新同步以避免行为漂移）。内置 kiro_default 没有可编辑 JSON，用户需 `kiro-cli --agent clawd`
  或 `/agent swap clawd` 才能启用 hooks。

CodeBuddy 状态同步（Claude Code 兼容 hook，command）：
  CodeBuddy 触发事件
    → hooks/codebuddy-hook.js（PascalCase 事件 → agents/codebuddy.js 映射 → HTTP POST）
    → 同上状态机（agent_id: codebuddy）
  Hook 注册到 ~/.codebuddy/settings.json，格式与 Claude Code 完全兼容。

opencode 状态同步（in-process plugin，~0ms 延迟）：
  opencode 触发事件（session.created / session.status / message.part.updated 等）
    → hooks/opencode-plugin/index.mjs（Bun 运行时，插件跑在 opencode.exe 进程内）
    → translateEvent 映射（opencode v2 事件名 → PascalCase Clawd event 名）
    → fire-and-forget HTTP POST 127.0.0.1:23333/state
    → 同上状态机（agent_id: opencode）

opencode 权限气泡（event hook + 反向 bridge，非阻塞）：
  opencode 请求权限 → event hook 收到 permission.asked
    → plugin POST /permission（带 bridge_url + bridge_token）→ Clawd 立即 200 ACK（不挂连接）
    → Clawd 创建 bubble 窗口 → 用户 Allow/Always/Deny
    → Clawd POST plugin 的反向 bridge → bridge 用 ctx.client._client.post() 调 opencode 内置 Hono 路由 /permission/:id/reply
    → opencode 执行对应行为（once/always/reject）

远程 SSH 状态同步（反向端口转发）：
  远程服务器上的 Claude Code / Codex CLI
    → hooks 通过 SSH 隧道 POST 到本地 127.0.0.1:23333
    → 同上状态机（CLAWD_REMOTE=1 模式跳过 PID 收集）

权限决策流（Claude Code HTTP hook，阻塞）：
  Claude Code PermissionRequest
    → HTTP POST 127.0.0.1:23333/permission { tool_name, tool_input, session_id, permission_suggestions }
    → main.js 创建 bubble 窗口（bubble.html）显示权限卡片
    → 用户点击 Allow / Deny / suggestion → HTTP 响应 { behavior }
    → Claude Code 执行对应行为
```

### 双窗口架构（输入/渲染分离）

桌宠使用两个独立的顶层窗口：
- **渲染窗口（win）**：透明大窗口，永久 `setIgnoreMouseEvents(true)`（click-through），只负责显示 SVG 动画和眼球追踪
- **输入窗口（hitWin）**：小矩形窗口，`transparent: true` + `setShape` 覆盖 hitbox 区域，`focusable: true`，永久 `setIgnoreMouseEvents(false)`，接收所有 pointer 事件

输入事件流：hitWin renderer → IPC → main（移动两个窗口 + relay）→ renderWin renderer（播放反应动画）

这个架构解决了 Windows 上的拖拽失效 bug：`WS_EX_NOACTIVATE`（`setFocusable(false)`）+ layered window + Chromium child HWND 的组合，在 z-order 变化后会导致 click 走 WM_MOUSEACTIVATE 激活死路径。分离后输入窗口 `focusable: true` 避免了这个问题。

### 多 Agent 架构（agents/）

每个 agent 定义为一个配置模块，导出事件映射、进程名、能力声明（`capabilities` 含 `httpHook` / `permissionApproval` / `sessionEnd` / `subagent`）：
- `agents/claude-code.js` — Claude Code 事件映射 + 能力（hooks、permission、terminal focus）
- `agents/codex.js` — Codex CLI JSONL 事件映射 + 轮询配置
- `agents/copilot-cli.js` — Copilot CLI camelCase 事件映射
- `agents/cursor-agent.js` — Cursor Agent（hooks.json）事件映射
- `agents/gemini-cli.js` — Gemini CLI 事件映射 + JSON 轮询配置
- `agents/kiro-cli.js` — Kiro CLI 事件映射（camelCase），无 HTTP hook / 无权限 / 无 subagent
- `agents/codebuddy.js` — CodeBuddy 事件映射（PascalCase，Claude Code 兼容），支持权限
- `agents/opencode.js` — opencode 事件映射 + 能力（plugin、permission、terminal focus）
- `agents/registry.js` — agent 注册表：按 ID 或进程名查找 agent 配置
- `agents/codex-log-monitor.js` — Codex JSONL 增量轮询器（文件监视 + 增量读取 + 事件去重）
- `agents/gemini-log-monitor.js` — Gemini session JSON 轮询器（消息数组 diff + 4s 完成延迟窗口）

运行时的 agent 启停 / 权限气泡开关通过 `src/agent-gate.js` 读 `prefs.agents[id].enabled` / `.permissionsEnabled`（默认 true，snapshot 缺字段时也 true 以兼容旧版），供 state.js 和 server.js 判断是否处理该 agent 的事件。

### 核心文件

| 文件 | 职责 |
|------|------|
| `src/main.js` | Electron 主进程胶水：窗口创建、ipcMain 分发、ctx 组装、app 生命周期、屏幕工具、HWND 恢复 |
| `src/prefs.js` | 纯数据层：`clawd-prefs.json` 的 schema / load / save / migrate / validate，零 Electron 依赖；`SCHEMA` 定义版本化字段 |
| `src/settings-store.js` | 不可变 snapshot + subscribers，closure-private `_commit`（外部拿不到 mutator） |
| `src/settings-controller.js` | 设置系统**唯一写入者**：组合 prefs + store + actions；`applyUpdate` / `applyBulk` / `applyCommand` / `hydrate` / `subscribe`；pre-commit effect gate（validate → effect → commit，effect 失败不提交）|
| `src/settings-actions.js` | updateRegistry + commands：每个字段的 validate/effect 对，以及 `removeTheme`/`installHooks` 等命令 |
| `src/settings-renderer.js` | 设置窗口渲染进程（2k+ 行）：主题卡片、animation overrides、agent 面板、诊断 |
| `src/preload-settings.js` | 设置窗口 contextBridge：读 snapshot、发 update/command、订阅变更 |
| `src/preload-prompt.js` | 轻量提示子窗口（elicitation / 更新气泡等）preload |
| `src/theme-loader.js` | 主题运行时（~1400 行）：加载 `theme.json`、必需状态校验、变体 merge、能力感知 overrides、SVG 白名单消毒、用户主题目录发现 |
| `src/agent-gate.js` | 纯函数 gate：`isAgentEnabled(snapshot, id)` / `isAgentPermissionsEnabled(...)`，默认 true 兼容旧 prefs |
| `src/animation-cycle.js` | 解析 SVG/APNG 的动画周期（精确 / 估算 / static / unavailable），供渲染循环与抖动检测使用 |
| `src/i18n.js` | 多语言字符串表（en / zh / ko），菜单与气泡按钮共享 |
| `src/state.js` | 状态机核心：setState/applyState、多会话追踪、resolveDisplayState、DND、wake poll、进程存活检测、session submenu |
| `src/server.js` | HTTP 服务：/state（GET 健康检查 + POST 状态更新）、/permission（权限 hook）、端口发现、hook 注册 |
| `src/permission.js` | 权限气泡：BrowserWindow 创建/堆叠/销毁、allow/deny/suggestion 决策、PASSTHROUGH_TOOLS |
| `src/updater.js` | 自动更新：electron-updater 懒加载、GitHub API 版本检查、更新对话框、菜单状态标签 |
| `src/update-bubble.js` + `update-bubble.html` | 自定义更新提示气泡（替代原生对话框），与 `preload-update-bubble.js` 配对 |
| `src/focus.js` | 终端聚焦：持久 PowerShell 进程 + C# FFI（Windows）、osascript 序列化（macOS）、VS Code tab 聚焦 |
| `src/mini.js` | 极简模式：边缘吸附、螃蟹步入场、抛物线跳跃、peek hover、窗口滑动动画 |
| `src/menu.js` | 菜单系统：i18n（en / zh / ko）、右键菜单、系统托盘、contextMenuOwner、语言切换、窗口缩放 |
| `src/tick.js` | 主循环（50ms）：光标轮询、mouseOverPet 计算、mini peek、idle→sleep 序列、眼球位置计算 + dedup |
| `src/renderer.js` | 渲染进程（纯 view）：动画切换（预加载防闪烁）、眼球 DOM 挂接、接收 IPC 触发的反应动画 |
| `src/hit.html` / `hit-renderer.js` / `hit-geometry.js` / `preload-hit.js` | 输入窗口：setShape 小矩形、pointer capture 拖拽、多击反应、hitbox 几何计算 |
| `src/preload.js` | 渲染窗口 contextBridge（onStateChange、onEyeMove、reaction 接收、pauseCursorPolling） |
| `src/bubble.html` + `preload-bubble.js` | 权限气泡 UI + contextBridge（permission-show、permission-decide、bubble-height、elicitation 输入） |
| `src/mac-window.js` | macOS 专用窗口行为（alwaysOnTop 恢复、space 行为等） |
| `src/login-item.js` | 开机自启：封装 `app.getLoginItemSettings` / `setLoginItemSettings`，供 controller 做 validate/effect |
| `src/work-area.js` + `size-utils.js` | 多显示器工作区查询 / 窗口尺寸钳制工具 |
| `src/log-rotate.js` | 1MB 循环追加日志工具：超限时从文件中点的换行处切半保留新内容 |
| `hooks/clawd-hook.js` | Claude Code command hook：事件名 → 状态映射 → HTTP POST，零依赖 |
| `hooks/copilot-hook.js` | Copilot CLI command hook：camelCase 事件名，与 clawd-hook.js 相同架构 |
| `hooks/gemini-hook.js` + `gemini-install.js` | Gemini CLI hook + 安全注册到 ~/.gemini/settings.json，导出 `registerGeminiHooks()` |
| `hooks/cursor-hook.js` + `cursor-install.js` | Cursor Agent hook（stdin/stdout JSON，支持 display_svg 工具提示）+ 注册到 ~/.cursor/hooks.json（append-only 幂等）|
| `hooks/kiro-hook.js` + `kiro-install.js` | Kiro CLI hook（camelCase）+ per-agent 注入（遍历 ~/.kiro/agents/*.json），额外维护 `clawd` agent（启动时从 `kiro_default` 重新同步行为） |
| `hooks/codebuddy-hook.js` + `codebuddy-install.js` | CodeBuddy hook（Claude Code 兼容 PascalCase）+ 注册到 ~/.codebuddy/settings.json |
| `hooks/opencode-plugin/index.mjs` + `opencode-install.js` | opencode in-process plugin（Bun runtime）+ 注册到 ~/.config/opencode/opencode.json（打包时 asar → asar.unpacked） |
| `hooks/install.js` + `uninstall.js` | Claude Code hooks 的安全注册 / 卸载（逐事件追加不覆盖）；`registerHooks()` 在 main.js 启动时自动调用 |
| `hooks/shared-process.js` | hook 脚本共享的进程树遍历 + stdin JSON 读取 + 终端 / 编辑器进程名白名单 + 系统边界常量，**所有 hook 脚本复用** |
| `hooks/json-utils.js` | 原子写 JSON（`writeJsonAtomic`）+ 从现有 hook command 提取 node bin 路径（`extractExistingNodeBin`） |
| `hooks/auto-start.js` | SessionStart hook：检测 Electron 是否在运行，未运行则 detached 启动，<500ms 退出 |
| `hooks/server-config.js` | 共享工具：端口常量、运行时配置读写、HTTP helper、服务发现 |
| `hooks/codex-remote-monitor.js` | 远程 Codex 监控：独立守护进程，通过 SSH 隧道轮询 JSONL 日志并 POST 状态变更 |
| `scripts/create-theme.js` / `validate-theme.js` | 主题脚手架 CLI + 校验器（`npm run create-theme`） |
| `launch.js` | 启动器：清除 `ELECTRON_RUN_AS_NODE` 环境变量后 spawn Electron |
| `extensions/vscode/` | VS Code 扩展（clawd-terminal-focus）：通过 `onUri` 协议聚焦正确的终端 tab |

### 状态机关键机制（state.js）

- **多会话追踪**：`sessions` Map 按 session_id 独立记录状态，`resolveDisplayState()` 取最高优先级
- **状态优先级**：error(8) > notification(7) > sweeping(6) > attention(5) > carrying/juggling(4) > working(3) > thinking(2) > idle(1) > sleeping(0)
- **最小显示时长**：防止快速闪切（error 5s、attention/notification 4s、carrying 3s、sweeping 2s、working/thinking 1s）
- **单次性状态**：attention/error/sweeping/notification/carrying 显示后自动回退（AUTO_RETURN_MS）
- **睡眠序列**：20s 鼠标静止 → idle-look → 60s → yawning(3s) → dozing → 10min → collapsing(0.8s) → sleeping；鼠标移动触发 waking(1.5s) → 恢复
- **DND 模式**：右键菜单 / 托盘"休眠（免打扰）"→ 跳过 dozing 直接 yawning → collapsing → sleeping，屏蔽所有 hook 事件；唤醒后播放 waking 动画
- **working 子动画**：1 个会话 → typing，2 个 → juggling，3+ → building
- **juggling 子动画**：1 个 subagent → juggling，2+ → conducting

### 主题系统（theme-loader.js + themes/）

Clawd 是一个**主题化**的桌宠——所有动画资源、计时、hitbox、眼球追踪参数都来自主题配置，不是硬编码。

- **内置主题位置**：`themes/clawd/`（像素螃蟹，默认）、`themes/calico/`（三花猫）、`themes/template/`（脚手架源，从 Discovery 菜单隐藏）、`themes/static-test/` + `themes/pr4-*/`（回归测试用）
- **用户主题位置**：`<userData>/themes/<id>/theme.json`（Windows `%APPDATA%/clawd-on-desk/themes/`、macOS `~/Library/Application Support/...`、Linux `~/.config/...`）
- **theme.json 必填**：`REQUIRED_STATES = ["idle", "working", "thinking"]`；若启用 `eyeTracking.enabled` 则 idle 资源必须是 SVG 并包含 `#eyes-js`；若声明 `fullSleep` 能力则需 `yawning / dozing / collapsing / waking`；若声明 `miniMode` 则需 8 个 `mini-*` 状态
- **能力感知（capability-aware）**：主题通过顶层 `capabilities` 声明支持的高级功能（fullSleep / miniMode / eyeTracking / visualFallback 等），UI 用"能力徽章"展示；缺失能力的 state 走 `VISUAL_FALLBACK_STATES` 的回退链（error/attention/notification/sweeping/carrying/sleeping → 回落到 idle 或其它 available state）
- **默认值覆盖**：`theme-loader.js` 顶部的 `DEFAULT_SOUNDS / DEFAULT_TIMINGS / DEFAULT_HITBOXES / DEFAULT_OBJECT_SCALE / DEFAULT_LAYOUT / DEFAULT_EYE_TRACKING` 为缺省值；主题只需覆盖不同的字段
- **变体（variants，Phase 3b-swap）**：主题可声明多个变体（如"冬装""夏装"），变体是**白名单 deep-merge**——`VARIANT_ALLOWED_KEYS` 限制可覆盖的字段，`VARIANT_REPLACE_FIELDS`（数组 + displayHintMap）整体替换而非合并
- **Animation Overrides（PR#95 Path A）**：用户可在 Settings → Animations 里**逐槽位**替换某个状态的资源（持久化到 `prefs.animationOverrides`），与变体正交：变体是作者整套，override 是用户 per-slot
- **SVG 安全消毒**：`DANGEROUS_TAGS`（script/iframe/foreignObject 等）删除、`on*` 属性剥离、`javascript:` / 外部 `http://` href 阻断、`..` 路径穿越拦截——用户主题不能越狱
- **资源格式**：支持 SVG / GIF / APNG / WebP / PNG / JPG；动画周期由 `src/animation-cycle.js` 探测（SMIL / CSS 动画精确解析，GIF/APNG 估算，静态图标记 static）
- **主题创建流程**见 `docs/guides/guide-theme-creation.md`；脚手架 CLI `npm run create-theme <name>` 从 `themes/template/` 拷贝

### Settings Panel（src/settings-*.js + settings.html）

独立的 BrowserWindow，分 4 层严格解耦（核心原则：**store 是唯一真相，controller 是唯一写入者**）：

| 层 | 文件 | 职责 |
|---|---|---|
| Schema / 持久化 | `src/prefs.js` | 版本化 `SCHEMA` 定义；`load/save/migrate/validate`；零 Electron 依赖，坏文件自动 `.bak` + fallback 默认值 |
| 内存 store | `src/settings-store.js` | `createStore()` 返回 `{getSnapshot, subscribe, _commit}`；`_commit` closure-private，外部拿不到；shallow-equal death-loop guard |
| 控制器 | `src/settings-controller.js` | 唯一写入者；`applyUpdate(key, v)` / `applyBulk(partial)` / `applyCommand(name, payload)` / `hydrate(partial)`（只 validate 跳过 effect，用于启动期导入系统状态如 login-item）；**pre-commit effect gate**——`updates` 注册表里每字段可配 `{validate, effect}`，effect 失败则不提交；返回 `{status, message?}` 同步或 Promise，取决于涉及的 effect 是否 async |
| UI | `src/settings-renderer.js` + `settings.html` + `preload-settings.js` | 主题卡片 / animation overrides 折叠行 / agent 开关 / 诊断；通过 IPC 调 controller，不直接写任何东西 |

关键取舍：
- `applyUpdate` 单字段和 `applyBulk` 多字段是**同步/异步同构**的——所有 effect 都同步时返回普通对象，任何 effect 返回 thenable 就整体转 Promise。这对保持"菜单 setter 立即可读"很关键（`ctx.lang = "zh"` 必须立刻在下一行读到）。`applyCommand` 永远 async（命令如 `installHooks` 做真实 IO）。
- `hydrate()` 是唯一跳过 `effect` 的入口，用于启动时从 `app.getLoginItemSettings()` 等系统 API 导入状态而不触发回写。
- 设置写入 → controller `_commit` → store 广播 → subscribe 订阅者（menu.js / main.js / tray）响应副作用。没有其它路径能修改 prefs。

### Permission Bubble 系统（permission.js + server.js → bubble.html 渲染）

- **HTTP hook**：PermissionRequest 事件使用 `type: "http"` hook（阻塞，600s 超时），而非 command hook
- **`POST /permission`** 端点接收 `{ tool_name, tool_input, session_id, permission_suggestions }`
- **气泡窗口**：每个权限请求创建独立的 `BrowserWindow`（透明、无边框、alwaysOnTop），加载 `bubble.html`
- **堆叠布局**：多个权限请求从屏幕右下角向上堆叠，`repositionBubbles()` 管理位置
- **动态高度**：bubble 通过 IPC `bubble-height` 上报实际渲染高度，主进程据此精确堆叠
- **决策选项**：Allow（允许）、Deny（拒绝）、suggestion 按钮（如"始终允许"、"自动接受编辑"）
- **全局快捷键**：`Ctrl+Shift+Y`（Allow）/ `Ctrl+Shift+N`（Deny）操作最新的可操作气泡（排除 elicitation/codex notify/ExitPlanMode），仅在气泡可见时注册，hideBubbles/petHidden 时注销
- **客户端断连**：`res.on("close")` 检测 Claude Code 超时或用户在终端回答，自动清理气泡
- **DND 模式**：休眠时自动 deny 所有权限请求，不弹气泡
- **suggestion 格式**：支持 `addRules`（权限规则）和 `setMode`（切换模式）两种类型
- **Codex 通知气泡**：Codex CLI 无法使用阻塞式 HTTP hook，通过 JSONL 日志检测 `exec_approval_request` / `apply_patch_approval_request` 触发通知气泡，仅提供 Dismiss 按钮（无 Allow/Deny），30 秒自动过期

### opencode Plugin 架构（hooks/opencode-plugin/index.mjs）

opencode 是唯一**以 plugin 形式集成**的 agent，其他 agent 都是 hook 脚本（fork 子进程）。Plugin 跑在 opencode 进程内的 Bun runtime 里，拿到 `ctx.client`、`ctx.serverUrl`、`ctx.directory` 等上下文。

- **进程树 walk 从 process.pid 起步**（不是 ppid），因为 plugin IS opencode；其他 hook 脚本从 ppid 起步因为它们是 opencode spawn 的子进程。在 `getStablePid()` 里实现，同时采用"外层终端优先"策略以适配 Antigravity 等 Electron 终端（renderer → main 都叫 `antigravity.exe`）
- **session 生命周期 = 主 session + 多个子 session**：opencode 的 `task` 工具不生 subtask part，而是**直接 session.created 出新 sessionID**（agent=explore）。Clawd 多会话 fanout 因此免费跑通 1→typing / 2→juggling / 3+→building
- **Root session 门控**（Phase 3）：plugin 模块状态 `_rootSessionId` 记首次见到的 sessionID；只有 root 的 `session.idle` 才映射 `attention/Stop`（happy 动画），其他子 session 的 `session.idle` 降级为 `sleeping/SessionEnd` 让 state.js 从 Map 里删掉，避免每次子任务完成都闪一下 happy
- **反向 HTTP bridge**（Phase 2）：opencode TUI 不对外绑定 HTTP（`ctx.serverUrl` 是 phantom URL，`ctx.client.fetch` 绑在 in-process Hono router 上），Clawd 无法直接调 opencode REST 回复权限。解决方法：plugin 启动时用 `Bun.serve({port: 0})` 随机端口起一个 bridge，token 用 `randomBytes(32).toString("hex")` + `timingSafeEqual` 鉴权；Clawd POST 到 bridge，bridge 再用 `ctx.client._client.post({url: "/permission/:id/reply", body: {reply}})` 调 in-process Hono
- **permission.ask hook 是死 hook**（2026-04-05 Phase 2 Spike 实测）：opencode 1.3.13 二进制已迁到 v2 `permission.asked` 事件名，但 SDK 1.1.51 的 `permission.ask` hook 派发没跟着迁，hook 0 次调用。只能走 event hook 路线
- **event hook 必须 fire-and-forget**：plugin 跑在 opencode 进程内，fetch 阻塞会直接拖慢 TUI。POST 用 1000ms AbortController 超时 + try-catch 吞错误，从不 await 结果
- **端口自愈**：plugin 独立维护 `_cachedPort`，读 `~/.clawd/runtime.json` 失败时扫 23333-23337 全候选，用 `x-clawd-server: clawd-on-desk` response header 鉴别身份
- **打包路径处理**：`opencode-install.js` 把 `app.asar/` 替换为 `app.asar.unpacked/`（参考 cursor-install.js:78），确保打包后 opencode 能直接 require plugin 的绝对路径

### 终端聚焦系统

- hook 脚本通过 `getStablePid()` 遍历进程树找到终端应用 PID（Windows Terminal、VS Code、iTerm2 等）
- `source_pid` 随状态更新发送到 main.js，存入 session 记录
- 右键菜单 Sessions 子菜单点击 → `focusTerminalWindow()` 用 PowerShell（Win）/ osascript（Mac）聚焦终端窗口
- 通知状态（attention/notification）自动聚焦对应会话的终端

### i18n 国际化

- 支持英文（en）、中文（zh）、韩语（ko），通过右键菜单 / 托盘菜单 Language 切换
- 字符串表集中在 `src/i18n.js`，菜单 / 气泡按钮 / Settings Panel / 更新气泡共用同一份
- 语言偏好持久化到 `clawd-prefs.json`，启动时通过 `hydrate()` 灌入 controller

### 自动更新

- **Git 模式**（非打包，macOS/Linux 源码运行）：`git fetch` 比较 HEAD → 有更新时 `git pull` + `npm install`（依赖变化时）→ `app.relaunch()`；通过 `getRepoRoot()` 检测 `.git` 目录自动启用
- **electron-updater 模式**（打包，Windows NSIS）：下载安装 NSIS 更新包，`autoInstallOnAppQuit = true`
- 托盘菜单"Check for Updates"手动触发

### 提示音系统（main.js playSound → IPC → renderer.js Audio）

- `app.commandLine.appendSwitch("autoplay-policy", "no-user-gesture-required")` 在任何窗口创建之前设置，解决 Chromium autoplay 限制
- `playSound(name)` 在 main.js 中定义，检查 `soundMuted`、`doNotDisturb`、10 秒 cooldown 后通过 IPC `play-sound` 发送到渲染窗口
- renderer.js 用 `_audioCache` 缓存 Audio 对象，避免重复创建
- state.js `applyState()` 中触发：attention/mini-happy → complete 音效，notification/mini-alert → confirm 音效
- 菜单"音效"checkbox 控制 `soundMuted`，持久化到 `clawd-prefs.json`
- 音效素材：`assets/sounds/complete.mp3`、`assets/sounds/confirm.mp3`（≤50KB）

### 眼球追踪系统（tick.js 计算 → renderer.js 渲染）

- tick.js 每 50ms（~20fps）轮询光标位置，计算眼球偏移量（MAX_OFFSET=3px，量化到 0.5px 像素网格）
- 通过 IPC `eye-move` 发送 `{dx, dy}` 到 renderer
- renderer 操作 SVG 内部 DOM：`#eyes-js` translate + `#body-js` 轻微偏移 + `#shadow-js` 拉伸
- **dedup 优化**：鼠标未移动时跳过发送；但从 idle-look 返回 idle-follow 时需要 `forceEyeResend` 旁路，否则眼球位置不会重新同步

### 点击反应系统（hit-renderer.js 检测 → main relay → renderer.js 播放）

- 双击 → 戳反应（左/右方向检测，2.5s，react-left/react-right SVG）
- 4 连击 → 双手拍反应（3.5s，react-double SVG）
- 拖拽 → 拖拽反应（持续到松手）
- 拖拽判定：鼠标位移 > 3px（DRAG_THRESHOLD），否则视为点击
- 输入检测在 hitWin，反应动画在 renderWin，通过 main IPC relay
- 反应期间 detach 眼球追踪，结束后 reattach

### 极简模式（Mini Mode）

角色藏在屏幕右边缘，窗口一半推到屏幕外，屏幕边缘自然遮住另一半身体。

**进入方式**：
- 拖拽到右边缘（SNAP_TOLERANCE=30px）→ 快速滑入 + mini-enter 动画
- 右键菜单"Mini Mode" → 螃蟹步走到边缘 → 抛物线跳入 → 探头入场

**核心机制**（mini.js + main.js）：
- `miniMode` 顶层标志，`applyState()` 拦截 notification → mini-alert, attention → mini-happy，其他状态静默
- `miniTransitioning` 过渡保护，螃蟹步/入场期间屏蔽 hook 事件和 peek
- `checkMiniModeSnap()` 遍历所有显示器右边缘 + 中心点 XY 范围检查
- Peek hover：`startMainTick()` 检测 `mouseOverPet` + `currentState === "mini-peek"` 控制滑出/滑回
- `miniIdleNow` 独立于 `idleNow`，仅走眼球追踪，跳过 idle-look/sleep 序列
- 窗口动画：`animateWindowX()`（滑动）+ `animateWindowParabola()`（抛物线跳跃，用 `setPosition()` 避免 DPI 漂移）
- 持久化：`savePrefs()` 存 miniMode/preMiniX/preMiniY，启动时恢复 + Y 轴 clamp

**Mini 状态 → SVG 映射**：
| 状态 | SVG | 用途 |
|------|-----|------|
| mini-idle | clawd-mini-idle.svg | 待机：呼吸+眨眼+手臂晃动+眼球追踪 |
| mini-enter | clawd-mini-enter.svg | 入场：一次性滑入弹跳→手臂伸出→静止 |
| mini-peek | clawd-mini-peek.svg | Hover 探头：快速招手 3 下 |
| mini-alert | clawd-mini-alert.svg | 通知：感叹号弹出 + >< 挤眼 |
| mini-happy | clawd-mini-happy.svg | 完成：花花 + ^^ 眯眼 + 星星 |
| mini-crabwalk | clawd-mini-crabwalk.svg | 右键进入时的螃蟹步 |
| mini-enter-sleep | clawd-mini-enter-sleep.svg | DND 状态下进入 mini 的入场动画 |
| mini-sleep | clawd-mini-sleep.svg | DND 休眠：Zzz + hover 可探头（不唤醒） |

## 状态 → 动画映射

**权威表格见 `docs/guides/state-mapping.md`**（带 Clawd / Calico 主题的 GIF 预览），此处只补充内部行为要点。

- **working 子动画**：1 个会话 → typing，2 个 → juggling，3+ → building
- **juggling 子动画**：1 个 subagent → juggling，2+ → conducting
- **Mini 状态**（极简模式下用的小尺寸动画）：`mini-idle` / `mini-enter` / `mini-enter-sleep` / `mini-crabwalk` / `mini-peek` / `mini-alert` / `mini-happy` / `mini-sleep` / **`mini-working`**（1 会话时的 mini typing，PR#121/122/123 引入；主题若无 typing 资源则静默跳过）
- **睡眠序列**：20s 鼠标静止 → idle-look → 60s → yawning(3s) → dozing → 10min → collapsing(0.8s) → sleeping；鼠标移动触发 waking(1.5s) → 恢复
- **DND 休眠**：跳过 dozing 直接 yawning → collapsing → sleeping，屏蔽所有 hook
- **自动回退**：attention / error / sweeping / notification / carrying 是一次性状态，显示后按 `autoReturn` 表自动回 idle（时长由主题 `theme.json timings.autoReturn` 覆盖，默认见 `theme-loader.js DEFAULT_TIMINGS`）

## 素材规则

- **按主题组织**：每个主题目录自带 `assets/`（`themes/clawd/assets/`、`themes/calico/assets/`、用户主题 `<userData>/themes/<id>/assets/`）；`assets/svg/` 和 `assets/gif/` 是默认 Clawd 主题使用的根路径（theme-loader 里 `assetsSvgDir` / `assetsSoundsDir` 指向这里）
- **文档预览用 GIF**：`assets/gif/` 里的 GIF 给 README / docs 展示（导出自 APNG / SVG）；运行时不直接读
- **源文件工作区**：需要编辑的素材复制到 `assets/source/` 再修改，不动发布版
- **支持的运行时格式**：SVG / GIF / APNG / WebP / PNG / JPG；SVG 走 `<object type="image/svg+xml">` 因为需要访问内部 DOM（眼球追踪），其他格式走 `<img>`
- **SVG 内部约定 ID**（主题可在 `theme.json eyeTracking.ids` 覆盖）：`#eyes-js`（眼球）、`#body-js`（身体）、`#shadow-js`（影子）、`#eyes-doze`（睡眠眼）
- **SVG 消毒**：用户主题 SVG 进来走白名单消毒（`DANGEROUS_TAGS` 剥离、`on*` 属性删除、`javascript:` href 阻断、外部 http 资源阻断、`..` 路径穿越阻断）

## 关键 Electron 配置

- `win.setFocusable(false)` — 渲染窗口永不抢焦点
- `hitWin.focusable: true` — 输入窗口允许激活（修复拖拽 bug 的关键，副作用是点击会短暂抢焦点）
- `win.showInactive()` — 显示时不打断用户输入
- 资源路径始终用 `path.join(__dirname, ...)` — 确保打包后不丢文件
- 透明无边框浮窗：`frame: false`, `transparent: true`, `alwaysOnTop: true`
- 单实例锁：`app.requestSingleInstanceLock()` 防止重复启动
- 位置持久化：窗口坐标 + 尺寸存入 `clawd-prefs.json`
- 多显示器边界钳制：`clampToScreen()` 用 `getNearestWorkArea()` 查找最近显示器工作区

## 开发规范

- 敏感信息只放 `.env`，禁止硬编码
- 注册 Claude Code hook 时必须**追加**到已有 hook 数组，不能覆盖
- HTTP 服务端口范围 `127.0.0.1:23333-23337`，运行时端口写入 `~/.clawd/runtime.json`，退出时清理；全部占用时降级为 idle-only 模式
- hook 脚本仅依赖 Node 内置模块 + 同目录的 `server-config.js` / `shared-process.js` / `json-utils.js`，禁止引入三方包（所有 hook 入口：`clawd-hook.js` / `copilot-hook.js` / `cursor-hook.js` / `gemini-hook.js` / `kiro-hook.js` / `codebuddy-hook.js` 都复用 `shared-process.js` 的进程树遍历 + 终端名白名单）
- main.js 启动时自动调用 `registerHooks({ silent: true })` 注册缺失的 hooks
- PermissionRequest 必须用 HTTP hook（阻塞式），其他事件用 command hook（非阻塞式）
- 极简模式动画期间（`miniTransitioning`），所有窗口定位路径（`always-on-top-changed`、`display-metrics-changed`、`display-removed` 等）都必须检查此标志，否则并发定位会导致 `setPosition()` 崩溃

## 已知限制

- **hitWin 点击会抢焦点**：输入窗口 `focusable: true` 是修复拖拽 bug 的关键（去掉 WS_EX_NOACTIVATE），但副作用是点击桌宠会短暂抢走编辑器焦点。目前认为可接受，暂不处理。
- **启动恢复**：桌宠在 agent 会话中途启动时，`detectRunningClaudeProcesses()` 会检测已运行的 Claude 进程并激活 `startupRecoverActive` 标志，抑制 idle→sleep 序列，保持 idle-follow 等待 hook 到来；若未检测到进程则保持 idle 直到下一个 hook 事件触发
- **Windows 前台窗口锁**：已通过 ALT key trick + koffi FFI `AllowSetForegroundWindow` 委托前台权限给 PowerShell helper 进程来绕过。菜单点击时 Electron 持有前台权限，通过 `AllowSetForegroundWindow(psProc.pid)` 委托给 PS 进程，PS 进程再用 ALT keybd_event + `SetForegroundWindow` 激活目标窗口。大多数场景有效，但仍有边缘情况可能失败（PID 不匹配终端窗口、PS helper 未初始化、koffi 加载失败等）
- hook 脚本依赖 Node.js 可用
- Windows 终端聚焦依赖 `koffi`（FFI 调用 `user32.dll AllowSetForegroundWindow`），koffi 加载失败时降级为纯 ALT trick；macOS 用 `osascript`
- Codex CLI：JSONL 轮询有 ~1.5s 延迟；无终端聚焦（日志不含终端 PID）；Windows 下 hooks 被 Codex 硬编码禁用
- Copilot CLI：需手动创建 `~/.copilot/hooks/hooks.json`；无权限气泡（仅支持 deny）
- Gemini CLI：需 Gemini CLI 支持 hooks；无权限气泡；无 subagent 检测
- Cursor Agent：无权限气泡（Cursor 权限在 stdout 处理，非 HTTP 阻塞式）；启动恢复检测匹配编辑器本体会误触发，已移除进程检测，靠 hook 事件激活
- Kiro CLI：无 global hooks 机制——hooks 只能注入到 per-agent 配置（`~/.kiro/agents/*.json`）。内置 `kiro_default` 没有可编辑 JSON，无法覆盖；`kiro-install.js` 的策略是（a）遍历所有现有 custom agent 注入 hooks（b）额外创建并维护 `clawd` agent，启动时从 `kiro_default` 的 built-in 定义重新同步字段（EXCLUDED_KEYS 过滤），用户必须 `kiro-cli --agent clawd` 或 `/agent swap clawd` 才能启用。无 HTTP hook / 无权限 / 无 subagent（仅状态同步）。状态 hook 已在 macOS 验证
- CodeBuddy：Claude Code 兼容的 hook 格式，注册到 `~/.codebuddy/settings.json`；支持权限，capabilities 同 Claude Code 但无 subagent
- opencode：子会话（task 工具分派的 explore agent）跑起来那 5-8 秒会短暂出现在 Sessions 右键菜单里，完成后自动清理——是纯视觉问题，不影响建筑动画。真要彻底隐藏需要新增 `subagent` 字段贯穿 server.js / state.js / menu.js（不能复用 headless，因为 headless 会把 session 从多会话计数里排除，导致建筑动画丢失）
- opencode：终端聚焦锚定启动 opencode 的终端窗口；用 `opencode attach` 从其他窗口接入时，点击桌宠仍会跳到最初的启动窗口
- opencode：permission.ask hook 在 1.3.13 未被调用（SDK/二进制版本不一致），权限只能走 event hook + 反向 bridge 路线；未来 opencode 修复此 hook 后可以考虑迁回
- 进程存活检测：main.js 定期检查 agent 进程是否存活，清理孤儿会话；但依赖进程名匹配，非标准进程名可能漏检

## ⚠️ 不要再修 Language 子菜单截断 bug

右键菜单的 Language 子菜单底部被截掉一小条（约 2-4px）。这是 Electron transparent + alwaysOnTop 窗口与 Windows DWM 菜单渲染的底层兼容问题，**不影响使用**。

已花费 3+ 小时尝试多种方案全部失败。结论：截断的不是某个菜单项，而是"菜单底部"这个位置。win 的透明矩形 bounds 在 DWM z-order 中遮住了菜单底边一小条。这是 Electron + Windows DWM 的底层行为，纯 JS 层面无法解决。

**绝对不要碰 `win.setAlwaysOnTop(false)`：** 这个窗口是 transparent + unfocusable + skipTaskbar 的，一旦掉出 topmost 就沉到桌面底层，看不见也关不掉。
