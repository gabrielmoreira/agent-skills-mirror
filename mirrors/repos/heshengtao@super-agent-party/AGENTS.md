# Super Agent Party 项目上下文

## 项目概述

**Super Agent Party** (v0.4.3) 是一个 **AI 桌面伴侣应用**，基于 **Electron 桌面应用 + Python/FastAPI 后端** 架构。提供多智能体 AI 助手体验，包括 3D/2D 虚拟角色、桌面自动化、IM 机器人、直播互动等功能。

- 仓库: https://github.com/heshengtao/super-agent-party
- 协议: AGPL-3.0
- 作者: Heshengtao (hst97@qq.com)

## 技术栈

| 层 | 技术 |
|---|---|
| 桌面壳 | Electron 39, electron-builder |
| 前端 | Vue 3 (内联在 index.html), Element Plus, Three.js/VRM |
| 后端 | Python 3.12, FastAPI, SQLite |
| 包管理 | npm (Node), uv (Python) |
| 打包 | PyInstaller (Python→exe), electron-builder (整体) |

## 目录结构速查

```
super-agent-party/
├── main.js              # Electron 主进程 (~3000+ 行): 窗口管理、IPC、后端启动
├── start.js             # 开发启动器: 设置 NODE_ENV 后启动 Electron
├── server.py            # FastAPI 后端入口 (~12500+ 行): 所有路由、WebSocket、聊天引擎
├── py/                  # Python 后端模块 (75个模块)
│   ├── agent.py         # 工具权限管理 (.party/config.json)
│   ├── cli_tool.py      # Shell 执行 (Docker沙箱/本地/WSL)
│   ├── computer_use_tool.py  # 鼠标键盘自动化
│   ├── cdp_tool.py      # Chrome DevTools Protocol
│   ├── web_search.py    # 多引擎网页搜索
│   ├── knowledge_base.py # 向量知识库
│   ├── diary_*.py       # 日记/记忆系统
│   ├── moss_tts.py      # 文本转语音
│   ├── sherpa_asr.py    # 语音识别
│   ├── *_bot_manager.py # 各平台 IM 机器人 (QQ/微信/Discord/Telegram/Slack/DingTalk/Feishu)
│   ├── extensions.py    # 前端扩展管理
│   ├── node_runner.py   # Node.js 扩展管理
│   ├── skills.py        # Agent 技能系统
│   ├── mcp_clients.py   # MCP 客户端管理
│   ├── task_center.py   # 任务中心
│   ├── scheduler.py     # 定时任务调度
│   └── ws_manager.py    # WebSocket 连接管理
├── config/
│   ├── settings_template.json  # 默认设置模板
│   ├── locales.json            # 中英文翻译
│   └── safety_words.json       # 内容过滤词
├── static/              # 前端静态资源
│   ├── index.html       # 主界面 (Vue 3 SPA ~19000 行)
│   ├── vrm.html         # VRM 3D 角色窗口
│   ├── tha.html         # THA 2D 角色窗口
│   ├── minimal.html     # 迷你模式窗口
│   ├── island.html      # 灵犀岛 (Dynamic Island)
│   └── js/              # JS 文件 (preload, renderer, vue_data, vue_methods, vrm, tha 等)
├── skills/              # Agent 技能定义 (SKILL.md)
├── vrm/                 # 默认 VRM 模型和动画
├── tha_models/          # THA 2D 角色模型
├── scripts/             # 构建/工具脚本
├── doc/                 # 文档图片
├── node_modules/        # Node 依赖
├── .venv/               # Python 虚拟环境 (uv 管理)
├── .agents/             # 项目级 agent 配置
│   └── skills/frontend-design/  # 前端设计技能
├── .opencode/           # OpenCode 配置
├── Dockerfile           # Docker 部署
├── docker-compose.yml   # Docker 编排 (backend + nginx gateway)
└── server.spec          # PyInstaller 打包配置
```

## 架构要点

### 三大通信通道

1. **HTTP REST (FastAPI → BrowserWindow)**: 后端起在动态端口 (默认 3456)，前端通过 fetch 调用 `/api/*` 等端点
2. **WebSocket**: `/ws/asr`, `/ws/tts`, `/ws/vrm`, `/ws/tha`, `/ws/subtitles` — 实时双向通信
3. **Electron IPC (preload.js)**: contextBridge 暴露原生能力 (VMC协议、截图、剪贴板、文件系统、窗口管理)

### 启动流程

```
start.js → electron . → main.js
  → 启动 Python 后端 (server.py) 作为子进程
  → 监听 stdout 中的 REAL_PORT_FOUND:<port>
  → 加载 BrowserWindow 指向 http://127.0.0.1:<PORT>
  → 前端 Vue 3 SPA 加载完成
```

### 多账户架构

每个账户有独立的数据目录，通过 `--data-dir` 传给 Python 后端。所有数据（对话、设置、记忆、上传文件、知识库）按账户隔离。

### 前端静态资源缓存与版本号（重要！）

启动"秒开"与"更新即时生效"两全依赖内容版本号缓存机制，改代码/加资源时需遵守以下约定：

- **HTML 文档**（`index.html` 等）：由 `server.py` 中间件 `inject_asset_versions` 重写输出，始终带 `Cache-Control: no-cache`（每次重新校验）。主文档永远是最新的。
- **资源 URL 版本化**：中间件把 HTML 中引用的 js/css/图片改写为 `path.ext?v=<内容md5前8位>`。文件没变 → hash 不变 → URL 不变 → 缓存命中秒开；文件变了 → URL 变 → 旧缓存作废 → 自动加载新代码（无需强刷）。
- **Service Worker**（`static/sw.js`）：带 `?v=` 的资源走 cache-first（永不 revalidate），非版本化懒加载库走 stale-while-revalidate，HTML 走 network-first。
- **升级缓存策略/结构时必须递增 `sw.js` 里的 `CACHE_NAME`**（如 `sap-cache-v2` → `v3`），否则旧缓存不会被 `activate` 清理，用户仍会用老代码。
- **新增被 HTML 引用的静态资源类型**（如某种新字体/媒体格式）时，需同步更新两处正则：`server.py` 的 `_ASSET_VERSION_RE` 与 `sw.js` 的 `VERSIONED_ASSET_RE`。
- **新增 HTML 页面**会自动被版本化，无需额外配置。
- 依赖缓存命中的资源（如修改了 `sw.js` 或引入新的懒加载文件）测试时请用无痕/强刷确认首次生效。

## 开发命令

```bash
npm start           # 开发模式启动
npm run dev         # 同上
npm run build       # 构建所有平台 (Windows+Mac+Linux)
npm run build:win   # 仅构建 Windows (NSIS 安装包)
npm run build:mac   # 仅构建 macOS (DMG)
npm run build:linux # 仅构建 Linux (AppImage)
npm run pack        # 仅打包不构建安装器
npm run test        # 无测试 (echo "Error: no test specified")
```

## 扩展系统 (三层)

1. **前端扩展 (HTML/JS/CSS)** — 安装在 `ext/` 目录，在独立 BrowserWindow 或 sidebar iframe 中加载
2. **Node.js 扩展 (Sidecar 进程)** — `py/node_runner.py` 管理，自动分配端口 (3100-13999)，通过 WebSocket 暴露 MCP 工具
3. **MCP 服务器** — 在设置中配置 `mcpServers`，工具自动发现并注入工具调度系统
4. **Agent 技能** — `skills/` 目录下的 SKILL.md 文件，可从 GitHub 安装

## 配置约定

- 默认设置: `config/settings_template.json`
- 运行时持久化: SQLite (路径由 `get_setting.py` 管理)
- 环境变量/API Key: 存储在用户数据目录的 `config.json` (由 Electron 主进程写入)
- 包管理: Python 依赖用 `uv` (pyproject.toml + uv.lock)，Node 依赖用 `npm` (package.json)
- 前后端分离但非典型: 前端是静态文件由 FastAPI 托管，数据通过 HTTP/WebSocket 交互，不经过 Electron IPC 传业务数据

## 代码风格注意事项

- **Python**: `server.py` 是单体文件 (~12500行)，所有路由和核心逻辑都在此文件中。`py/` 目录是各功能模块。无显式类型注解。使用 `async/await` 异步模式。
- **前端**: Vue 3 以内联方式写在 `static/index.html` 中 (~19000行)，不使用单文件组件(.vue)。数据层在 `js/vue_data.js`，方法层在 `js/vue_methods.js`。UI 组件库: Element Plus。
- **主进程**: `main.js` (~3000行) 管理所有原生窗口、IPC 处理器、托盘、自动更新、多账户、下载管理等。使用 CommonJS 模块系统。
- **配置**: JSON 模板 + SQLite 持久化 + WebSocket 广播变更。
- **无测试**: 项目目前没有自动化测试 (`npm test` 输出 "Error: no test specified")。
