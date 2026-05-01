[根目录](../CLAUDE.md) > **openai_pool_orchestrator (主包)**

# openai_pool_orchestrator -- 核心业务包

## 模块职责

项目唯一的 Python 包，包含全部后端业务逻辑：OpenAI 账号自动注册引擎、FastAPI REST API 服务、CPA / Sub2Api 双平台账号池维护、多邮箱提供商适配层，以及嵌入式 Web 前端静态资源。

## 入口与启动

| 入口 | 路径 | 说明 |
|------|------|------|
| Web 服务 | `__main__.py` -> `main()` | 启动 Uvicorn 服务器，监听 `0.0.0.0:18421`，加载 `server.app` |
| CLI 注册 | `register.py` -> `main()` | 命令行单次/循环注册模式，通过 argparse 接收参数 |
| 快捷脚本 | `../run.py` | 根据 `--cli` 标志分派到上述两种入口 |
| pip 命令 | `openai-pool` | pyproject.toml 注册的控制台入口，指向 `__main__:main` |

## 对外接口

### REST API（server.py）

FastAPI 应用提供 40+ 端点，核心分组：

**任务控制**
- `POST /api/start` -- 启动注册任务（支持多线程、目标数量、代理配置）
- `POST /api/stop` -- 停止运行中的任务

**代理管理**
- `POST /api/proxy/save` / `GET /api/proxy` -- 保存/获取代理地址
- `POST /api/check-proxy` -- 检测代理可用性
- `GET /api/proxy-pool/config` / `POST /api/proxy-pool/config` -- 代理池配置
- `POST /api/proxy-pool/test` -- 测试代理池取号

**配置管理**
- `GET /api/sync-config` / `POST /api/sync-config` -- Sub2Api 同步配置
- `GET /api/pool/config` / `POST /api/pool/config` -- CPA 池配置
- `GET /api/mail/config` / `POST /api/mail/config` -- 邮箱提供商配置
- `POST /api/upload-mode` -- 上传策略切换（snapshot / decoupled）

**Token 管理**
- `GET /api/tokens` -- 列出本地 Token 文件
- `DELETE /api/tokens/{filename}` -- 删除单个 Token
- `POST /api/sync-now` -- 单个 Token 导入 Sub2Api
- `POST /api/sync-batch` -- 批量导入

**CPA 池**
- `GET /api/pool/status` -- CPA 池状态
- `POST /api/pool/check` -- 探测 CPA 池
- `POST /api/pool/maintain` -- 执行 CPA 维护
- `POST /api/pool/auto` -- 开关自动维护

**Sub2Api 池**
- `GET /api/sub2api/accounts` -- 分页账号列表（支持状态/关键字筛选）
- `POST /api/sub2api/accounts/probe` -- 批量测活
- `POST /api/sub2api/accounts/delete` -- 批量删除
- `POST /api/sub2api/accounts/handle-exception` -- 异常处理
- `GET /api/sub2api/pool/status` -- Sub2Api 池状态
- `POST /api/sub2api/pool/maintain` -- Sub2Api 维护
- `POST /api/sub2api/pool/dedupe` -- 重复账号去重

**实时通信**
- `GET /api/logs` -- SSE 事件流（结构化事件：task_snapshot、runtime_snapshot、stats、log、pool_status 等）

### SSE 事件类型

| 事件类型 | 说明 |
|---------|------|
| `task_snapshot` | 任务全局状态快照 |
| `runtime_snapshot` | 多 Worker 运行时明细 |
| `stats` | 成功/失败计数统计 |
| `log` | 实时日志消息 |
| `pool_status` | CPA/Sub2Api 池状态变化 |

## 关键依赖与配置

### Python 依赖

| 包 | 用途 |
|----|------|
| `fastapi` >= 0.110 | Web 框架 |
| `uvicorn[standard]` >= 0.27 | ASGI 服务器 |
| `curl-cffi` >= 0.6 | TLS 指纹伪装 HTTP 客户端（模拟 Chrome） |
| `aiohttp` >= 3.9 | 异步 HTTP（池维护探测） |
| `requests` >= 2.31 | 同步 HTTP 客户端 |
| `pydantic` | 请求体校验（FastAPI 内置） |

### 配置文件

- `data/sync_config.json` -- 运行时配置（从 `config/sync_config.example.json` 生成）
- `data/state.json` -- 累计成功/失败计数持久化
- `data/tokens/` -- 注册获取的 Token JSON 文件

### 核心配置项

| 配置键 | 类型 | 说明 |
|--------|------|------|
| `proxy` | str | 固定代理地址 |
| `auto_register` | bool | 池不足时自动注册 |
| `mail_providers` | list[str] | 启用的邮箱提供商列表 |
| `mail_strategy` | str | 邮箱路由策略：round_robin / random / failover |
| `base_url` / `email` / `password` | str | Sub2Api 平台连接信息 |
| `cpa_base_url` / `cpa_token` | str | CPA 平台连接信息 |
| `upload_mode` | str | 上传策略：snapshot（串行）/ decoupled（双平台同传）|
| `proxy_pool_*` | mixed | 代理池 API 配置 |
| `sub2api_maintain_actions` | dict | Sub2Api 维护动作开关 |

## 数据模型

### Token 文件格式（data/tokens/*.json）

注册成功后保存的 Token 文件包含 OAuth 凭证信息，用于后续导入平台。

### TaskState（server.py）

全局单例，管理注册任务的完整生命周期：
- 多 Worker 线程管理与运行时快照
- SSE 事件订阅/分发
- 成功/失败计数与平台上传统计
- 注册步骤追踪：check_proxy -> create_email -> oauth_init -> sentinel -> signup -> send_otp -> wait_otp -> verify_otp -> create_account -> workspace -> get_token

### PoolMaintainer（pool_maintainer.py）

CPA 平台维护器：
- `fetch_auth_files()` -- 获取全部 auth 文件
- `get_pool_status()` -- 池状态统计
- `probe_accounts_async()` -- 异步批量探测账号有效性

### Sub2ApiMaintainer（pool_maintainer.py）

Sub2Api 平台维护器：
- `list_accounts()` / `_list_all_accounts()` -- 分页/全量列出账号
- `get_dashboard_stats()` -- 仪表盘统计
- 自动 token 刷新（401 -> re-login）

### MailProvider 体系（mail_providers.py）

抽象基类 + 4 种实现：

| 类名 | 提供商 | 认证方式 |
|------|--------|---------|
| `MailTmProvider` | Mail.tm | Bearer Token |
| `MoeMailProvider` | MoeMail | API Key |
| `DuckMailProvider` | DuckMail | Bearer Token |
| `CloudflareTempEmailProvider` | Cloudflare Workers | JWT + Admin Password |

`MultiMailRouter` -- 线程安全的多提供商路由器，支持轮询/随机/容错策略。

## 测试与质量

- **测试**：当前无测试套件
- **类型检查**：无 mypy/pyright 配置
- **Lint**：无 ruff/flake8 配置
- **CI/CD**：无

**建议优先覆盖的测试场景**：
1. `mail_providers.py` -- 各提供商创建邮箱与 OTP 轮询的异常路径
2. `register.py` -- OAuth 流程各步骤的错误处理与重试
3. `server.py` -- 核心 API 端点的请求/响应校验
4. `pool_maintainer.py` -- 池状态计算与维护动作

## 常见问题 (FAQ)

**Q: server.py 文件为何如此庞大？**
A: 当前 server.py 约 3500+ 行，包含了全部 REST API 路由、TaskState 状态管理、平台交互逻辑、自动维护定时器等。建议后续拆分为路由模块、任务管理模块、平台交互模块等。

**Q: register.py 中 curl-cffi 的作用？**
A: 使用 `curl_cffi.requests` 而非标准 `requests`，可伪装 Chrome TLS 指纹，避免被 OpenAI / Cloudflare 反爬检测拦截。

**Q: 如何新增邮箱提供商？**
A: 继承 `MailProvider` 基类，实现 `create_mailbox()` 和 `wait_for_otp()` 方法，然后在 `create_provider_by_name()` 工厂函数中注册。

**Q: 双平台上传策略的区别？**
A: `snapshot` 模式按顺序先补 CPA 再补 Sub2Api；`decoupled` 模式让单个账号同时上传到两个平台。

## 相关文件清单

| 文件 | 行数(估) | 说明 |
|------|----------|------|
| `__init__.py` | 29 | 包初始化，路径常量定义 |
| `__main__.py` | 119 | Uvicorn 启动与优雅关闭 |
| `server.py` | 3550+ | FastAPI 服务，全部 API 与任务状态 |
| `register.py` | 1600+ | OpenAI OAuth 注册引擎 |
| `pool_maintainer.py` | 800+ | CPA / Sub2Api 池维护 |
| `mail_providers.py` | 809 | 邮箱提供商抽象与 4 种实现 |
| `static/index.html` | 695 | Web UI 页面结构 |
| `static/app.js` | 2200+ | 前端交互逻辑 |
| `static/style.css` | 2800+ | iOS Flat Design 样式 |

## 变更记录 (Changelog)

| 时间 | 操作 | 说明 |
|------|------|------|
| 2026-03-18 09:19:57 | 初始扫描 | 首次生成模块级 CLAUDE.md |
