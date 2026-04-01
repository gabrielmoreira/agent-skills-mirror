# BioClaw 接入 QQ / 飞书实施方案

## 1. 目标

本文档给出一套面向 BioClaw 的 QQ / 飞书接入方案，目标是让当前仅支持 WhatsApp、企业微信、Discord、Slack、本地网页的 BioClaw，在不破坏现有容器 Agent、消息落库、群组注册和任务调度能力的前提下，新增：

- 飞书（Lark）文本消息收发
- QQ 官方 Bot 文本消息收发
- 自动注册群组 / 会话
- 与现有 `Channel` 抽象一致的接入方式
- 后续可扩展的图片 / 文件发送能力

本文档只讨论 BioClaw 如何实现，不讨论把 omicclaw 整体并入。

---

## 2. 当前结论

### 2.1 BioClaw 当前不支持 QQ / 飞书

当前仓库官方文档已经明确说明：

- `QQ / 飞书（Lark）` 目前只是路线图展示
- 当前仓库内没有可直接启用的 QQ / 飞书通道实现

可核对：

- `docs/CHANNELS.zh-CN.md`
- `README.zh-CN.md`

当前实际存在的通道源码只有：

- WhatsApp
- 企业微信（WeCom）
- Discord
- Slack
- Local Web

可核对：

- `src/channels/`
- `src/index.ts`

### 2.2 omicclaw 支持 QQ / 飞书，但实现不在仓库内部

`omicclaw` 的 gateway 确实把 `telegram / feishu / qq / imessage` 作为支持通道来管理。

可核对：

- `gateway/inprocess_channel_manager.py`
- `gateway/channel_config_routes.py`
- `gateway/registry.py`
- `README.md`

但它实际启动 QQ / 飞书时，导入的是外部 Python 包：

- `omicverse.jarvis.channels.feishu`
- `omicverse.jarvis.channels.qq`

并且 `omicclaw` 的依赖明确要求：

- `omicverse>=2.0.0`

可核对：

- `gateway/inprocess_channel_manager.py`
- `pyproject.toml`

因此，`omicclaw` 对 BioClaw 的参考价值主要是：

- 配置项设计
- 通道生命周期管理思路
- channel -> session 映射思路

而不是“可以直接拷进 BioClaw 的现成协议实现”。

---

## 3. 推荐路线

### 3.1 推荐方案：在 BioClaw 中原生新增 Node/TypeScript 通道

推荐在 BioClaw 内新增：

- `src/channels/feishu.ts`
- `src/channels/qq.ts`

并接入现有 `Channel` 抽象。

原因：

1. BioClaw 当前运行时是 Node/TypeScript，主入口、消息调度、DB、容器 Agent 全部在这一层。
2. `omicclaw` 是 Python gateway，负责 Web UI 和通道编排，不适合直接并进 BioClaw。
3. 直接混入 Python sidecar 会引入双运行时、双配置、双日志、双会话语义，复杂度显著上升。
4. BioClaw 已经有稳定的通道接口和接入模式，可复用。

可核对：

- `src/types.ts`
- `src/index.ts`
- `src/channels/wecom.ts`
- `src/channels/slack.ts`

### 3.2 不推荐方案：直接依赖 omicclaw / omicverse 的 Python 通道运行时

不推荐把 BioClaw 做成：

- Node 主服务
- 外挂 Python channel 进程
- 通过 HTTP / IPC / DB 做桥接

原因：

- 部署复杂
- 故障面扩大
- 消息状态难对齐
- 需要额外维护协议桥
- 最终仍要为 BioClaw 做本地适配层

此方案只适合作为极短期 PoC，不适合作为主线实现。

---

## 4. 实施范围

### 4.1 飞书范围

第一版建议支持：

- 飞书 Bot 文本消息接收
- 飞书 Bot 文本消息发送
- 自动注册群组 / 私聊
- sender / chat 基础信息采集
- 事件去重
- 连接状态管理

第一版不必强行支持：

- 富文本卡片
- 复杂消息卡片
- 文件上传
- 图片发送
- 多租户管理

### 4.2 QQ 范围

第一版建议支持：

- 官方 QQ Bot / 开放平台文本消息接收
- 文本消息发送
- 自动注册群组 / 会话
- 基础 token 获取与刷新
- 事件去重

必须先明确：

- 本方案只做 **官方 QQ Bot**
- 不做个人 QQ 自动化
- 不做非官方客户端协议适配

### 4.3 与现有能力保持兼容

新增通道后，不应改动以下主流程语义：

- 消息落库
- 自动注册逻辑
- `chat_jid` 路由
- 群组文件夹映射
- `runContainerAgent()` 调用链
- scheduler / IPC / Local Web / trace

---

## 5. 设计原则

### 5.1 保持 `Channel` 接口不变

目标是让 QQ / 飞书像 WeCom / Slack 一样接入：

- `connect()`
- `sendMessage()`
- `isConnected()`
- `ownsJid()`
- `disconnect()`
- 可选 `sendImage()`
- 可选 `setTyping()`

参考：

- `src/types.ts`

### 5.2 JID 设计显式区分平台和会话粒度

建议：

- 飞书群聊：`<chat_id>@feishu.group`
- 飞书私聊：`<user_id>@feishu.user`
- QQ 群 / 频道：`<scope_id>@qq.group`
- QQ 私聊：`<scope_id>@qq.user`

这样可以：

- 避免与现有 `@wecom.group` / `@slack.conv` / `@local.web` 冲突
- 让 `ownsJid()` 实现简单稳定
- 保持跨平台唯一性

### 5.3 先文本，后多媒体

不要在第一版同时上：

- 文本
- 图片
- 文件
- markdown 卡片
- 富媒体回调

第一版只做文本，先把消息流打通。

---

## 6. 拟新增配置

### 6.1 飞书配置

建议在 `src/config.ts` 和 `.env.example` 增加：

```bash
FEISHU_APP_ID=
FEISHU_APP_SECRET=
FEISHU_CONNECTION_MODE=websocket
FEISHU_VERIFICATION_TOKEN=
FEISHU_ENCRYPT_KEY=
FEISHU_HOST=0.0.0.0
FEISHU_PORT=8080
FEISHU_PATH=/feishu/events
```

说明：

- `websocket` 作为默认模式
- `webhook` 作为第二优先模式

### 6.2 QQ 配置

建议增加：

```bash
QQ_APP_ID=
QQ_CLIENT_SECRET=
QQ_MARKDOWN=false
QQ_IMAGE_HOST=
QQ_IMAGE_SERVER_PORT=8081
```

说明：

- 第一版只要求 `QQ_APP_ID` 和 `QQ_CLIENT_SECRET`
- 图片相关项第二阶段再真正启用

---

## 7. 代码改动清单

### 7.1 新增文件

- `src/channels/feishu.ts`
- `src/channels/qq.ts`
- `src/channels/feishu.test.ts`
- `src/channels/qq.test.ts`

### 7.2 修改文件

- `src/index.ts`
- `src/config.ts`
- `package.json`
- `.env.example`
- `docs/CHANNELS.md`
- `docs/CHANNELS.zh-CN.md`

### 7.3 可选调整

- `src/channels/registry.ts`

说明：

当前 `src/index.ts` 仍主要用手工实例化通道，而不是完全通过 registry。为了降低风险，第一版建议继续沿用当前入口风格，不顺手做通道系统大重构。

---

## 8. 分阶段实施方案

### 阶段 0：协议和范围确认

目标：

- 明确 QQ 走官方 Bot 平台
- 明确飞书先做 `websocket`
- 明确第一版只做文本

输出：

- 环境变量命名冻结
- JID 命名冻结
- 第一版验收标准冻结

### 阶段 1：飞书文本 MVP

目标：

- 飞书消息进入 BioClaw 主链路
- Agent 输出能回发到飞书

实施内容：

1. 新增 `FeishuChannel`
2. 实现 `connect()`、`disconnect()`、`sendMessage()`、`ownsJid()`
3. 处理入站消息：
   - 提取 chat id
   - 提取 sender
   - 构造 `NewMessage`
   - `onChatMetadata()`
   - `onMessage()`
4. 自动注册未注册群组
5. 在 `src/index.ts` 接线
6. 增加最小测试

验收标准：

- 飞书群里发消息，BioClaw 能收到并落库
- 若群已注册，Agent 能回复
- 若群未注册且允许自动注册，消息链路可打通

### 阶段 2：QQ 文本 MVP

目标：

- 官方 QQ Bot 消息进入 BioClaw 主链路
- Agent 文本输出能回复到 QQ

实施内容：

1. 新增 `QQChannel`
2. 实现 token 获取 / 刷新
3. 实现连接与事件分发
4. 实现 `sendMessage()`
5. 在 `src/index.ts` 接线
6. 增加单元测试与基本模拟 payload

验收标准：

- QQ Bot 收到文本
- BioClaw 落库
- Agent 回复成功
- 断线重连 / token 过期有基本兜底

### 阶段 3：图片与附件

目标：

- 让 QQ / 飞书通道具备与 Slack / WeCom 类似的基础多媒体能力

实施内容：

- `sendImage()` 支持
- 文件 URL 或上传中转策略
- 文本 fallback

说明：

这一阶段必须等文本通道稳定后再做。

### 阶段 4：文档、运维和可观测性补全

目标：

- 降低接入成本
- 让部署和排障可操作

实施内容：

- 更新中英文文档
- 增加 `.env.example`
- 增加调试 checklist
- 在 Local Web / dashboard 中增加 channel 状态展示（可选）

---

## 9. 关键实现细节

### 9.1 飞书通道建议

建议优先实现：

- WebSocket 模式

理由：

- 不依赖公网回调
- 本地调试简单
- 与当前 BioClaw 部署方式更契合

第二阶段再补：

- Webhook 模式

飞书通道内部需处理：

- 事件验签
- 加密字段解包
- 事件去重
- sender/chat 元数据缓存
- 文本消息提取

### 9.2 QQ 通道建议

QQ 第一版建议只支持：

- 官方 Bot 平台的文本消息

通道内部需处理：

- app access token 获取
- token 刷新
- 入站事件处理
- 文本发送
- 消息对象去重

### 9.3 自动注册策略

延续 BioClaw 当前模式：

- 首次收到通道消息
- 若 `chat_jid` 未注册
- 调用现有 `autoRegister()`
- 生成 `${channelName}-${suffix}` 风格的 folder

参考：

- `src/index.ts`

### 9.4 数据落库策略

坚持使用现有 `NewMessage` 写库结构：

- `id`
- `chat_jid`
- `sender`
- `sender_name`
- `content`
- `timestamp`
- `is_from_me`

不要为了 QQ / 飞书重写数据库模型。

---

## 10. 风险与应对

### 风险 1：误把 omicclaw 当成可直接移植实现

风险：

- 实际 bot 协议实现不在 `omicclaw` 仓库内

应对：

- 只借鉴其配置与管理思路
- 协议层在 BioClaw 里原生实现

### 风险 2：QQ 范围不清

风险：

- “QQ 支持”容易被误解成个人号自动化

应对：

- 文档中明确写成“官方 QQ Bot”
- 不承诺个人 QQ

### 风险 3：第一版一次性上太多能力

风险：

- 文本、图片、文件、卡片一起做，调试成本高

应对：

- 先文本 MVP
- 稳定后再做图片与附件

### 风险 4：入口重构过大

风险：

- 顺手把 channel registry 全量接管，改动面扩大

应对：

- 第一版只按 `src/index.ts` 的现有入口模式接入

---

## 11. 测试计划

### 11.1 单元测试

覆盖：

- `ownsJid()`
- inbound payload -> `NewMessage`
- autoRegister 触发
- `sendMessage()` 请求构造
- token 刷新逻辑
- 断线状态下行为

### 11.2 集成测试

覆盖：

- 通道连接成功
- 首条消息自动注册
- 已注册会话能触发 Agent
- Agent 输出能回发

### 11.3 回归验证

必须验证以下现有通道不受影响：

- Local Web
- WhatsApp
- WeCom
- Slack
- Discord

---

## 12. 交付顺序建议

推荐顺序：

1. 飞书文本 MVP
2. QQ 文本 MVP
3. 文档和 `.env.example`
4. 图片 / 文件能力
5. UI / dashboard 状态增强

原因：

- 飞书的工程接入通常比 QQ 更稳定
- 能更快验证新通道接入 BioClaw 主链路是否成立

---

## 13. 预计工作量

以“文本 MVP + 基础测试 + 文档”为标准：

- 飞书：1 到 2 天
- QQ：1 到 2 天
- 文档与回归：0.5 到 1 天

总计：

- 约 3 到 5 天

不含：

- 图片 / 文件复杂能力
- dashboard 配置页面
- 多租户和复杂权限系统

---

## 14. 建议的下一步

如果按最稳路径推进，建议下一步直接开始：

1. 在 BioClaw 中实现 `FeishuChannel` 骨架
2. 增加飞书配置项
3. 在主入口接线
4. 用文本链路跑通第一个端到端闭环

在飞书文本版稳定之前，不建议并行启动 QQ 图片 / 附件能力。

---

## 15. 最终判断

结论如下：

- `BioClaw` 当前确实不支持 QQ / 飞书
- `omicclaw` 的确支持 QQ / 飞书，但依赖外部 `omicverse` runtime
- 最合理的路径不是把 `omicclaw` 整套搬进来
- 而是在 `BioClaw` 当前 Node/TypeScript 架构内，原生实现 `FeishuChannel` 和 `QQChannel`

这条路线改动边界清晰、部署成本可控、长期维护成本最低。
