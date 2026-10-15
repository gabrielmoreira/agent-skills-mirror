# Web Access

通过本机日常浏览器（任意 Chromium 内核，按用户数据目录选定）的 CDP 连接完成浏览器任务，Node.js 22+，无需独立自动化浏览器。

- 使用流程与浏览行为 → `SKILL.md`
- 环境检查、已有服务复用与后台启动 → `scripts/check-deps.mjs`
- 浏览器身份（数据目录路径，旧值 chrome / edge 等按平台映射）、偏好与端口发现 → `scripts/browser-discovery.mjs`
- 首次配置：列应用数据根目录的最外层文件夹名、在指定文件夹内探测数据目录 → `scripts/browser-probe.mjs`
- 用户数据位置（`~/.web-access/`）与旧版本数据一次性迁移 → `scripts/user-data.mjs`
- HTTP API、标签页生命周期和服务维护门 → `scripts/cdp-proxy.mjs`
- 页面中的 iframe（列举、在其中执行、坐标点击路由到跨进程 iframe 的子 session）→ `scripts/page-frames.mjs`
- 唯一 CDP 连接所有者、并发握手、命令结算 → `scripts/cdp-connection.mjs`
- 跨平台集中维护 → `scripts/proxy-maintenance.mjs`
- API 契约 → `references/cdp-api.md`
- 回归验证 → `node --test scripts/check-deps.test.mjs scripts/cdp-connection.test.mjs scripts/cdp-proxy.test.mjs scripts/proxy-maintenance.test.mjs scripts/browser-discovery.test.mjs scripts/browser-probe.test.mjs scripts/page-frames.test.mjs scripts/user-data.test.mjs`（临时副本、临时 HOME、假浏览器和随机本机端口，不操作用户浏览器与真实用户数据）

不维护浏览器名单、不扫描目录或固定端口：日常只读所配置数据目录的 `DevToolsActivePort`，不可用即硬错；首次配置只列根目录的文件夹名，探测范围由代码限定在应用数据根目录内（拒绝 ~、.. 越界、外部绝对路径与软链接逃逸），且无论找到几个都询问用户。配置值无效（不是含 Local State 的数据目录）时先报配置错误，与共享服务是否在运行无关。

Proxy 没有时长或空闲退出计时器；健康的已有连接直接复用，断线由原服务重新连接。不要为前置检查或任务结束停止已有服务。15 分钟自动清理仅作用于 Agent 创建的闲置标签页。浏览器授权由浏览器控制。

先绑定服务端口，再连接浏览器；从发现开始的并发请求共用一次连接尝试，旧 socket 事件按上下文身份隔离。升级时集中维护一次，不能通过 Unix 或 Windows 进程批量查杀命令制造各任务的授权弹窗。维护必须由当前实例按请求、命令、标签页、连接状态判断忙碌，禁止客户端抢替共享服务。

本机权威目录为 `~/Documents/.agent/skills/web-access/`，工具入口通过软链接引用。用户资料（`config.env`、`site-patterns/`）位于 `~/.web-access/`，不在仓库内、不随代码发布；仓库内旧位置（根目录 `config.env`、`references/site-patterns/`）运行时不再读取，只作一次性迁移来源（完成后写 `~/.web-access/.migrated`，不再扫描）；同名站点经验的旧副本见其文件内指引。
