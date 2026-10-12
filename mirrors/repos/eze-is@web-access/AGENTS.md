# Web Access

通过本机 Chrome / Edge 的 CDP 连接完成浏览器任务，Node.js 22+，无需独立自动化浏览器。

- 使用流程与浏览行为 → `SKILL.md`
- 环境检查、已有服务复用与后台启动 → `scripts/check-deps.mjs`
- 浏览器偏好和端口发现 → `scripts/browser-discovery.mjs`
- HTTP API、标签页生命周期和服务维护门 → `scripts/cdp-proxy.mjs`
- 唯一 CDP 连接所有者、并发握手、命令结算 → `scripts/cdp-connection.mjs`
- 跨平台集中维护 → `scripts/proxy-maintenance.mjs`
- API 契约 → `references/cdp-api.md`
- 回归验证 → `node --test scripts/check-deps.test.mjs scripts/cdp-connection.test.mjs scripts/cdp-proxy.test.mjs scripts/proxy-maintenance.test.mjs scripts/browser-discovery.test.mjs`（临时副本、假浏览器和随机本机端口，不操作用户浏览器）

Proxy 没有时长或空闲退出计时器；健康的已有连接直接复用，断线由原服务重新连接。不要为前置检查或任务结束停止已有服务。15 分钟自动清理仅作用于 Agent 创建的闲置标签页。浏览器授权由浏览器控制。

先绑定服务端口，再连接浏览器；从发现开始的并发请求共用一次连接尝试，旧 socket 事件按上下文身份隔离。升级时集中维护一次，不能通过 Unix 或 Windows 进程批量查杀命令制造各任务的授权弹窗。维护必须由当前实例按请求、命令、标签页、连接状态判断忙碌，禁止客户端抢替共享服务。

本机权威目录为 `~/Documents/.agent/skills/web-access/`，工具入口通过软链接引用。`config.env` 与 `references/site-patterns/` 是本机资料，不随代码发布；同名站点经验的旧副本见其文件内指引。
