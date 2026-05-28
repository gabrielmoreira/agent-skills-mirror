# bb-browser Agent 开发规范

## 架构

```
CLI ──HTTP──▶ Daemon ──controlConn CDP──▶ Chrome
                │
                │ --hub 模式 (可选)
                ├── Hub ProviderStream ──▶ Pinix Hub
                │
                │ Protocol 2
                └── Streamer (bb-viewer) ──captureConn + inputConn CDP──▶ Chrome
                         │
                         └── WebRTC video + DataChannel ──▶ Clip Web UI
```

**三根 CDP 连接到同一个 Chrome：**

| 连接 | Owner | 职责 |
|------|-------|------|
| controlConn | daemon | Agent 操作：tab/nav/site/DOM/click-by-ref |
| inputConn | streamer | Human 实时输入：鼠标/键盘/IME (DataChannel → CDP) |
| captureConn | streamer | 视频流：screencast → VP8 → WebRTC |

**组件：**

| 组件 | 位置 | 职责 |
|------|------|------|
| CLI | `packages/cli/` | 命令行入口，HTTP 调 daemon |
| Daemon | `packages/daemon/` | 控制中心：CDP controlConn、HTTP API、Hub 连接、site 执行、streamer 管理 |
| Shared | `packages/shared/` | 统一命令定义 (`commands.ts`)、协议类型 (`protocol.ts`) |
| Streamer | `bb-viewer` repo | 纯视频 + 实时输入（Go binary，daemon 子进程） |

## Daemon 两种模式

```bash
# 本地模式：Agent 用 CLI 操作浏览器
bb-browser daemon start

# Hub 模式：注册到 Pinix Hub，远程可用
bb-browser daemon start --hub https://hub.pinixai.com --hub-token xxx
```

## 协议

### Protocol 1: CLI ↔ daemon (`POST /command`)

请求：`{"method": "snap", "params": {"tab": "3ef9"}}`
成功：`{"result": {"tab": "3ef9", "title": "Google", "snapshot": "..."}}`
失败：`{"error": {"message": "Missing --tab", "hint": "Run 'bb-browser tab list'"}}`

### Protocol 2: daemon ↔ streamer (`POST /command`)

| Method | Params | 说明 |
|--------|--------|------|
| connect | {cdpUrl, ice?} | 连接 CDP，创建 WebRTC peer |
| answer | {answer_sdp, candidates} | 完成 WebRTC 信令 |
| switch | {cdpUrl} | 切到新 tab（peer 不变） |
| stop | {} | 停止 |

## 统一命令定义

`packages/shared/src/commands.ts` 是所有命令的单一定义源。每个命令包含 `method`、`group`、`description`、`requiresTab`、`params`。CLI 解析、daemon dispatch、Hub 注册都从这里读取。

添加新命令：
1. `commands.ts` — 添加 CommandDef
2. `protocol.ts` — 添加 ActionType
3. `command-dispatch.ts` — 添加处理分支
4. `packages/cli/src/commands/<name>.ts` + `index.ts` — CLI 命令

## CLI 命令

`--tab` 必填（除 `open`、`site` 组、`tab list/new`、`daemon`）。

| 组 | 命令 |
|----|------|
| 导航 | `open <url> [--tab]`, `back --tab`, `forward --tab`, `reload --tab`, `close --tab` |
| 观察 | `snap --tab`, `screenshot --tab`, `get <attr> --tab`, `eval <js> --tab` |
| 交互 | `click/hover/fill/type/press/scroll/check/uncheck/select --tab` |
| Tab | `tab list`, `tab new [url]` |
| Site | `site list`, `site info <name>`, `site run <name>` |
| 调试 | `network/console/errors/trace --tab` |
| 进程 | `daemon start [--hub]`, `daemon stop`, `daemon status` |

## 设计不变量

1. **Daemon 是唯一操作 API**。CLI 和 Hub invoke 都通过 daemon。
2. **Streamer 不做业务逻辑**。不管 tab、不做导航。只做帧编码和输入转发。
3. **Tab ID 统一用 daemon 分配的短 ID**（如 `3ef9`）。Streamer 不知道 tab ID，只接收 CDP WebSocket URL。
4. **Site 执行在 daemon 内**。不 shell-out CLI。
5. **所有操作响应包含 `tab`**（短 ID）。观察类响应包含 `cursor`。
6. **Per-tab 事件隔离**。tab 关闭时释放短 ID 和事件缓冲。
7. **`seq` 全局单调递增**，不可回退。
8. **Daemon 启动时清理旧进程**。`cleanupStaleDaemon()` 确保不残留。

## Hub Clip 注册

Hub 模式下 daemon 注册：

| Clip | 命令 |
|------|------|
| browser | 所有标准命令 + `stream.start/answer/close/switch` |
| \<platform\> | 每个 site adapter 一个命令（如 `google/search`） |

Clip Web UI 通过 Hub invoke 调用标准命令（tab_list、open、reload 等）和 stream 命令。

## Stream 生命周期 (view.html)

Clip Web UI (`web/view.html`) 通过心跳 + visibility 检测管理 stream 生命周期：

```
ACTIVE (visible) → Ping 每 5s via DataChannel (opcode 0x08)
IDLE   (hidden)  → Ping 每 10s, 30s 后自动 disconnect
CLOSED           → overlay 显示断开原因, 可点 Connect 重连
```

**前端 30s idle disconnect 是第一道防线，后端 45s watchdog 是安全网。**

`cleanup(reason)` 根据原因显示不同 overlay：
- `user` → "Disconnected"
- `idle` → "Stream closed — tab was inactive"
- `network` → "Connection lost"

关键实现约束：
- 不用 `setTimeout`（hidden tab 被浏览器节流），用 `setInterval` + 时间戳
- 不用 `BigInt`（兼容性），用 `Math.floor` + `>>>`
- `disconnect` 里 `invoke("stream.close")` 是 fire-and-forget，不 await

## Docker 运行模式

Docker 中 Chrome 必须以**有头模式**运行在 Xvfb 虚拟帧缓冲上。

```
Xvfb (:99) ← Chrome (headed, DISPLAY=:99) ← CDP screencast → bb-viewer → WebRTC
```

**为什么不能用 `--headless=new`：** Linux 上 `--headless=new` 跳过整个 X11/Ozone 显示层，导致 WebGL、`navigator.plugins`、屏幕信息等 API 返回异常值。Google 等反自动化系统检测这些底层渲染差异来识别 headless 浏览器。macOS 上 headless 没问题，因为 Chrome 仍链接完整的 Cocoa/CoreGraphics 框架，只是不显示窗口。

Chrome 始终以有头模式启动，不使用 `--headless=new`。macOS 上没有聚焦的用户 session 时 Chrome 自动离屏渲染（无可见窗口），效果等同 headless 但保留完整 GUI API。

**Docker 关键环境变量：**
- `DISPLAY=:99` — Xvfb 虚拟显示（Dockerfile 已设置）

**Stealth 注入 = 有害：** Google 的反自动化不检测 CDP 本身，而是检测 `Emulation.setUserAgentOverride`、`Page.addScriptToEvaluateOnNewDocument` 等 CDP domain 调用。不注入任何 stealth，用裸 CDP 即可。

### Docker 构建

```bash
# 构建（单阶段，下载预编译 bb-viewer + Chrome，阿里云 apt/npm 镜像）
docker build --platform linux/amd64 -t bb-browser:amd64 .

# 运行（TURN 凭证自动从 Hub API 获取，不需要配置）
docker run -d --platform linux/amd64 --name bb-browser \
  -v bb-browser-data:/data -p 19825:19824 --shm-size=2g \
  -e CHROME_WINDOW_SIZE=1280,720 \
  bb-browser:amd64 --host 0.0.0.0 \
  --hub https://hub.pinixai.com --hub-token <token>
```

镜像内预装了 Chrome for Testing + bb-viewer（静态链接），运行时无需下载。
`--shm-size=2g` 防止 Chrome 因共享内存不足 crash。
TURN 环境变量（`TURN_URL`/`TURN_SECRET`）仍可用于覆盖默认值。

**推荐：使用 Pinix 全家桶镜像 `lueco/pinix`，包含 pinixd + bb-browser + Chrome，一个 token 启动一切。**

### bb-viewer (streamer)

- 预编译 binary 在 COS 上，daemon 首次 stream 时自动下载（`~/.bb-browser/bin/bb-viewer`）
- 静态链接 libvpx + libturbojpeg，不依赖用户系统库版本
- JPEG → I420 解码使用 `tjDecompress2` (RGB) 再手动转 I420，而非 `tjDecompressToYUVPlanes`（后者在 libturbojpeg 2.1.x 对奇数高度帧有 bug）
- Decoder 自动 round down 到偶数尺寸

### TURN relay

TURN 凭证通过 Hub API `GET /turn/credentials` 动态获取（24h TTL），secret 只在服务端。
daemon 启动 streamer 时自动请求，不需要用户配置。
环境变量 `TURN_URL` / `TURN_SECRET` 可覆盖（standalone 模式）。

## 代码规范

- Commit：`<type>(<scope>): <summary>`，英文
- 类型：`fix` / `feat` / `refactor` / `chore` / `docs`
- 构建：`pnpm build`
- 测试：`pnpm test`
- lint：`pnpm lint`

## 参考

- [bb-viewer issue #5](https://github.com/epiral/bb-viewer/issues/5) — Stream 生命周期设计
- [issue #224](https://github.com/epiral/bb-browser/issues/224) — daemon 生命周期（已修复）
