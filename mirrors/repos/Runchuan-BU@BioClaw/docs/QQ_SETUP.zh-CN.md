# QQ 接入实操与排障指南

本文档对应当前 BioClaw 中已经落地的 **QQ 官方 Bot 文本版**。

当前支持范围：
- QQ 官方 Bot
- WebSocket 长连接接收事件
- 私聊消息：`C2C_MESSAGE_CREATE`
- 群里 `@机器人` 消息：`GROUP_AT_MESSAGE_CREATE`
- 文本回复

当前不支持：
- 个人 QQ 自动化
- 图片 / 文件发送
- webhook 模式
- 频道场景的完整适配

## 1. 前提

1. 你使用的是 **QQ 开放平台 / 官方 Bot**，不是个人 QQ 号自动化。
2. 服务器可以访问：
   - `https://bots.qq.com`
   - `https://api.sgroup.qq.com`
3. BioClaw 已能正常启动，模型提供商配置正确。

## 2. 在 QQ 开放平台里做什么

1. 创建机器人应用。
2. 记录：
   - `App ID`
   - `Client Secret`
3. 在机器人配置里启用 **WebSocket** 接收事件。
4. 订阅这两个事件：
   - 私聊消息
   - 群聊 `@机器人` 消息
5. 如果平台区分沙盒与正式环境，先确认你当前使用的是哪一个。

说明：当前 BioClaw 的 QQ 通道监听的是官方文档中的 group/C2C 组合 intent（`1 << 25`），对应私聊和群里 `@机器人` 两类消息事件。

## 3. 写入服务器 `.env`

在服务器执行：

```bash
cd /home/ubuntu/cqr_files/Bioclaw_new/BioClaw

[ -f .env ] || cp .env.example .env
cp .env ".env.bak.$(date +%F-%H%M%S)"

upsert_env() {
  key="$1"
  value="$2"
  if grep -q "^${key}=" .env; then
    sed -i "s|^${key}=.*|${key}=${value}|" .env
  else
    printf '%s=%s\n' "$key" "$value" >> .env
  fi
}

read -rp 'QQ App ID: ' QQ_APP_ID_INPUT
read -rsp 'QQ Client Secret: ' QQ_CLIENT_SECRET_INPUT
echo

upsert_env QQ_APP_ID "$QQ_APP_ID_INPUT"
upsert_env QQ_CLIENT_SECRET "$QQ_CLIENT_SECRET_INPUT"
# 如使用沙盒环境，再打开这一行
# upsert_env QQ_SANDBOX true

unset QQ_APP_ID_INPUT QQ_CLIENT_SECRET_INPUT

grep -E '^(QQ_APP_ID|QQ_SANDBOX)=' .env || true
grep '^QQ_CLIENT_SECRET=' .env | sed 's/=.*/=***hidden***/'
```

## 4. 启动

```bash
cd /home/ubuntu/cqr_files/Bioclaw_new/BioClaw
source /home/ubuntu/.nvm/nvm.sh
nvm use 22
npm run build
npm start
```

如果 QQ 长连接成功，终端里应出现：

```text
Connected to QQ (websocket)
```

## 5. 如何测试

### 5.1 私聊测试

直接给机器人发：

```text
你好
```

期望日志：

```text
QQ direct message received
QQ message sent
```

### 5.2 群聊测试

把机器人加入群后，在群里发送：

```text
@机器人 你好
```

期望日志：

```text
QQ group message received
QQ message sent
```

## 6. 常见问题

### 6.1 没有任何 QQ 日志

重点检查：
- 机器人应用是否真的启用了 WebSocket
- 私聊 / 群里 `@机器人` 事件是否已订阅
- 服务器是否能访问 `bots.qq.com` 与 `api.sgroup.qq.com`
- `.env` 中 `QQ_APP_ID` / `QQ_CLIENT_SECRET` 是否对应同一个应用

### 6.2 提示模型 API key 无效

这不是 QQ 问题，而是模型提供商配置问题。优先检查：
- `MODEL_PROVIDER`
- `OPENROUTER_API_KEY`
- 或 `ANTHROPIC_API_KEY`

### 6.3 群里发普通消息机器人不回

当前实现按官方 `GROUP_AT_MESSAGE_CREATE` 路径工作。第一版默认只保证：
- 私聊消息
- 群里 `@机器人` 的消息

所以群里测试时请先显式 `@机器人`。

### 6.4 这是个人 QQ 机器人吗

不是。当前实现只支持 **官方 QQ Bot**。

## 7. 当前实现边界

当前版本为了稳妥，只做了最小可用集：
- 自动注册 QQ 会话
- 文本收发
- 私聊与群 `@机器人`

后续如果需要，再扩展：
- 图片 / 文件
- webhook 模式
- 更完整的富消息
- 更细的群资料同步

## 8. 参考

- QQ 机器人官方文档：<https://bot.q.qq.com/wiki/develop/api-v2/>
- WebSocket 接入说明：<https://bot.q.qq.com/wiki/develop/api-v2/dev-prepare/interface-framework/reference.html>
- 事件订阅与通知：<https://bot.q.qq.com/wiki/develop/api-v2/dev-prepare/interface-framework/event-emit.html>
- 消息事件：<https://bot.q.qq.com/wiki/develop/api-v2/server-inter/message/send-receive/event.html>
- 发送消息：<https://bot.q.qq.com/wiki/develop/api-v2/server-inter/message/send-receive/send.html>
