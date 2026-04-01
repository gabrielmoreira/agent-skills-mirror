# 消息通道配置

BioClaw 支持多种聊天平台，通过在项目根目录的 `.env` 中设置环境变量启用。

- **Windows 用户**（WSL2、本地网页、暂不接 WhatsApp）：优先阅读 [WINDOWS.zh-CN.md](WINDOWS.zh-CN.md)。
- **环境变量模板**：根目录 `.env.example`；纯本地网页可参考 `config-examples/.env.local-web.example`。

---

## WhatsApp（默认）

所有通道均为 opt-in（默认关闭）。启用 WhatsApp 需在 `.env` 中添加：

```bash
ENABLE_WHATSAPP=true
```

无需填密钥。首次运行时在终端扫描二维码，用 WhatsApp 登录即可。认证状态保存在 `store/auth/`。

---

## 企业微信（WeCom）

1. 登录[企业微信管理后台](https://work.weixin.qq.com/wework_admin/frame)。
2. **应用与小程序** → **智能机器人** → **创建**。
3. 选择 **API 模式**，连接方式选 **长连接**（不要用 URL 回调）。
4. 将 **Bot ID** 和 **Secret** 写入 `.env`：

   ```bash
   WECOM_BOT_ID=your-bot-id
   WECOM_SECRET=your-secret
   ```

5. 在群里添加该机器人，`@` 它即可对话。

**发送图片（可选）：** 在管理后台创建自建应用，并配置：

```bash
WECOM_CORP_ID=企业ID
WECOM_AGENT_ID=应用 AgentId
WECOM_CORP_SECRET=应用 Secret
```

服务器 IP 需加入该应用的**企业可信 IP**白名单。

---

## QQ 官方 Bot

BioClaw 当前已支持 **QQ 官方 Bot** 的**文本消息收发**，接入方式为 **WebSocket**。

当前 MVP 支持的入站事件：
- `C2C_MESSAGE_CREATE`：QQ 私聊机器人
- `GROUP_AT_MESSAGE_CREATE`：群里 `@` 机器人

1. 在 QQ 开放平台创建机器人应用。
2. 在机器人配置里启用 **WebSocket** 接收事件。
3. 订阅私聊消息和群聊 `@机器人` 消息事件。
4. 在 `.env` 中至少配置：

   ```bash
   QQ_APP_ID=your-app-id
   QQ_CLIENT_SECRET=your-client-secret
   # 可选：若使用 QQ 沙盒环境
   # QQ_SANDBOX=true
   ```

5. 启动 BioClaw 后，第一条私聊消息或群里 `@机器人` 的消息会自动注册该会话。

当前限制：
- 仅支持 **官方 QQ Bot**，不支持个人 QQ 自动化
- 第一版只做文本消息
- 群聊场景按 `@机器人` 触发路径实现

详细中文步骤与排障见 [QQ 接入实操与排障指南](QQ_SETUP.zh-CN.md)。

---

## 飞书（Lark）

BioClaw 当前已支持**飞书文本消息收发**。优先建议使用 **WebSocket / 长连接**；只有在部署环境必须走公网回调时，再切到 webhook。

1. 在[飞书开放平台](https://open.feishu.cn/)创建机器人应用。
2. 给应用开启**接收消息**事件，并授予读取 / 发送 IM 消息所需权限。
3. 在 `.env` 中至少配置：

   ```bash
   FEISHU_APP_ID=cli_xxx
   FEISHU_APP_SECRET=your-app-secret
   FEISHU_CONNECTION_MODE=websocket
   ```

4. 如果使用 **webhook** 模式，再补充：

   ```bash
   FEISHU_CONNECTION_MODE=webhook
   FEISHU_VERIFICATION_TOKEN=your-verification-token
   FEISHU_ENCRYPT_KEY=your-encrypt-key
   FEISHU_HOST=0.0.0.0
   FEISHU_PORT=8080
   FEISHU_PATH=/feishu/events
   ```

5. 把机器人拉进飞书群或私聊它，发送第一条消息后，BioClaw 会自动注册该会话，并能进行文本回复。

当前限制：暂未实现图片 / 文件发送。

更完整的中文实操、OpenRouter 配置、内外部群差异与排障见 [飞书接入实操与排障指南](FEISHU_SETUP.zh-CN.md)。

---

## Discord

1. 打开 [Discord Developer Portal](https://discord.com/developers/applications)。
2. **New Application** → **Bot** → **Add Bot**。
3. 在 **Privileged Gateway Intents** 下开启 **MESSAGE CONTENT INTENT**。
4. 将 **Bot Token** 写入 `.env`：

   ```bash
   DISCORD_BOT_TOKEN=your-bot-token
   ```

5. **OAuth2** → **URL Generator**：勾选 scope `bot`，权限包含发送消息、附加文件、阅读消息历史等。
6. 用生成链接把 bot 邀请进服务器。
7. 在频道里发消息，bot 会自动注册并可以回复。

---

## Slack（Socket Mode）

BioClaw 使用 **[Socket Mode](https://api.slack.com/apis/socket-mode)** 长连接，**不需要**公网 HTTPS 回调地址。

1. 在 **[api.slack.com/apps](https://api.slack.com/apps)** 创建 App。
2. 打开 **Socket Mode** → 开启 → **生成 App-Level Token**，权限勾选 **`connections:write`**，得到 `xapp-...`。
3. **OAuth & Permissions** → **Bot Token Scopes** 至少添加：
   - `channels:history`、`groups:history`、`im:history`、`mpim:history`（读消息）
   - `chat:write`（回复）
   - `files:write`（发图片，建议）
   - `users:read`（显示名）
   - `channels:read`（频道信息，可选）
4. **Install to Workspace**，复制 **Bot User OAuth Token**（`xoxb-...`）。
5. **Event Subscriptions** → 启用并订阅 bot 事件：**`message`**，或分别订阅 `message.channels` / `message.groups` / `message.im` / `message.mpim`（以控制台界面为准）。
6. 把 App 邀请进频道（`/invite @你的App`）或与其私聊。
7. 写入 `.env`：

   ```bash
   SLACK_BOT_TOKEN=xoxb-your-bot-token
   SLACK_APP_TOKEN=xapp-your-app-token
   ```

重启 BioClaw 后，在某个会话里发第一条消息会自动注册该会话（与 Discord 类似）。

---

## 本地网页聊天（浏览器）

适合暂时不用 WhatsApp、在浏览器里本地验证的场景。

1. 可选：从 `.env` 中移除 `ENABLE_WHATSAPP=true`（若只想用浏览器通道）；其它变量见 `config-examples/.env.local-web.example`。

2. **一条命令启动带网页的服务：**

   ```bash
   npm run web
   ```

   会启用 **`ENABLE_LOCAL_WEB`**：**对话与实验追踪在同一页**（`/`；窄屏顶部 Tab；**宽屏左侧为实验追踪 / 工作流时间线，右侧为对话**），并照常读取 `.env`（模型密钥、其它通道等）。

3. 浏览器打开 **`http://localhost:3000/`**（或你配置的 `LOCAL_WEB_HOST` / `LOCAL_WEB_PORT`）。

释放端口：**`npm run stop:web`**。仅打开浏览器、不启动服务可用 **`npm run open:web`**。

页面为**实验室风格**：消息走 **SSE**（`/api/events`），**实验追踪**与聊天**同一地址**（顶部 **实验追踪** Tab 在 **对话** 左侧；宽屏**左栏追踪、右栏聊天**），**`/dashboard`** 会重定向到 **`/?tab=trace`**。**设置**（齿轮）可切换语言与主题，说明见 [DASHBOARD.md](DASHBOARD.md)。

### 对话消息 vs 实验追踪（数据格式）

- **对话（`messages` 表、`/api/messages`）**：每条是常规消息，**`content` 为纯文本**（用户与助手看到的正文）。**没有**用于「同步更新」的固定 JSON 协议；网页端可对内容做 Markdown 渲染。上传文件等特殊展示依赖**纯文本行**前缀（如 `Uploaded file:`、`Workspace path:`、`Preview URL:`），由前端解析。
- **实验追踪（`agent_trace_events`、`/api/trace/list`）**：每条有 **`type`**（如 `run_start`、`stream_output`、`run_end`、`run_error`、`container_spawn`、`ipc_send`）和 **`payload` JSON**（库内以 JSON 文本存储），用于**可观测性**，不是聊天协议。合并页默认带 **`compact=1`**，会隐藏刷屏的 `stream_output`，需要时在界面勾选「显示流式片段」。

可选：`LOCAL_WEB_SECRET` 为 webhook 设置共享密钥。

更详细的 Windows 步骤见 [WINDOWS.zh-CN.md](WINDOWS.zh-CN.md)。

---

## 微信个人号

1. 在 `.env` 中添加：

   ```bash
   ENABLE_WECHAT=true
   ```

2. 在**前台终端**运行 BioClaw（需要能看到二维码）：

   ```bash
   npm start
   ```

3. 用微信扫描终端显示的二维码登录。登录状态**不会持久化**，每次重启需重新扫码。

4. 在任意微信对话中发消息，BioClaw 会自动注册该会话并回复文字和图片。

**限制：**
- 不支持主动发消息 —— SDK 只能在收到消息后回复（请求-响应模式）。
- 多条输出（文字+图片）会缓冲合并为一条回复。
- 不支持语音消息、文件分享和群 @ 功能。
- 底层基于腾讯 OpenClaw 微信通道（`@tencent-weixin/openclaw-weixin`），由 [weixin-agent-sdk](https://github.com/wong2/weixin-agent-sdk) 二次封装。非官方维护，API 可能随时变动。

---

## 禁用或组合使用

- 关闭 WhatsApp：从 `.env` 中移除 `ENABLE_WHATSAPP=true` 即可（所有通道均为 opt-in）。
- 不用的通道：对应 token 留空或不配置即可（飞书、企业微信、Discord、Slack 都是如此；Slack 需同时配置 `SLACK_BOT_TOKEN` 与 `SLACK_APP_TOKEN`）。

