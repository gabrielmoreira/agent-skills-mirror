# 飞书接入实操与排障指南

本文档记录当前 `BioClaw` 飞书通道的**实操步骤**和**真实排障结论**，适用于希望把 BioClaw 跑在飞书私聊或企业内部群聊中的场景。

## 当前支持范围

当前主线版本已经支持：

- 飞书机器人**文本消息接收**
- 飞书机器人**文本消息回复**
- 飞书**私聊自动注册会话**
- 飞书**群聊 @ 机器人**后接收与回复

当前仍未支持：

- 图片/文件回发
- QQ 通道
- 对飞书外部群的稳定支持

关于“外部群是否可用”：基于当前实测，企业自建应用机器人可以正常私聊收发，但在**外部群**里常见“暂无可添加的机器人”。这更像是飞书产品侧的租户/范围限制，而不是 BioClaw 代码问题。因此，**群聊测试请优先使用企业内部群**。

## 一、飞书后台最小配置

### 1. 创建应用

1. 打开 <https://open.feishu.cn/app>
2. 创建一个**企业自建应用**
3. 获取并保存：
   - `App ID`
   - `App Secret`

不要把 `App Secret` 发到聊天、工单或截图里；如果泄露，立即重置。

### 2. 开启机器人能力

在应用后台中：

1. 打开 `添加应用能力`
2. 确认已添加 `机器人`
3. 在 `机器人` 页面确认机器人已启用

### 3. 配置事件与回调

当前 BioClaw 推荐使用**长连接 / WebSocket**，不要优先走 webhook。

在飞书后台：

1. 打开 `开发配置 -> 事件与回调`
2. 将订阅方式设置为：`长连接`
3. 添加事件：

```text
im.message.receive_v1
```

如果后台提示“未检测到应用连接信息”，不要先硬点保存。应先在服务器上启动 BioClaw，看到：

```text
Connected to Feishu (websocket)
[ws] ws client ready
```

然后刷新飞书后台页面，再保存长连接配置。

### 4. 配置权限

权限页面的名称可能随控制台版本略有变化，但当前至少要保证以下方向的权限已开通：

- 以应用身份发消息
- 读取用户发给机器人的单聊消息
- 接收群聊中 @ 机器人消息事件

如果只开了“群聊中 @ 机器人消息事件”，那么**私聊发 `你好` 不一定会收到**；第一次测试建议根据你已开通的权限选择测试方式。

### 5. 发布版本

完成上面改动后，进入：

- `版本管理与发布`

创建一个新版本并发布。版本号可以用：

```text
1.0.0
```

更新说明可以写：

```text
启用飞书机器人长连接事件接收，添加消息接收事件 im.message.receive_v1，用于 BioClaw 文本消息收发测试。
```

## 二、服务器端 `.env` 配置

如果你准备用 OpenRouter，直接执行：

```bash
cd /home/ubuntu/cqr_files/Bioclaw_new/BioClaw

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

read -rsp 'OpenRouter API key: ' OPENROUTER_KEY
echo
read -rp 'Feishu App ID: ' FEISHU_APP_ID_INPUT
read -rsp 'Feishu App Secret: ' FEISHU_APP_SECRET_INPUT
echo

upsert_env MODEL_PROVIDER openrouter
upsert_env OPENROUTER_API_KEY "$OPENROUTER_KEY"
upsert_env OPENROUTER_BASE_URL https://openrouter.ai/api/v1
upsert_env OPENROUTER_MODEL openai/gpt-5.4

upsert_env FEISHU_APP_ID "$FEISHU_APP_ID_INPUT"
upsert_env FEISHU_APP_SECRET "$FEISHU_APP_SECRET_INPUT"
upsert_env FEISHU_CONNECTION_MODE websocket
upsert_env ENABLE_WHATSAPP false

sed -i 's/^WECOM_BOT_ID=.*/# WECOM_BOT_ID=/' .env
sed -i 's/^WECOM_SECRET=.*/# WECOM_SECRET=/' .env
sed -i 's/^ANTHROPIC_API_KEY=.*/# ANTHROPIC_API_KEY=/' .env

unset OPENROUTER_KEY FEISHU_APP_ID_INPUT FEISHU_APP_SECRET_INPUT
```

如果你不用 OpenRouter，而是 Anthropic，则保留 `ANTHROPIC_API_KEY` 并确保其有效。

## 三、启动方式

```bash
cd /home/ubuntu/cqr_files/Bioclaw_new/BioClaw
source /home/ubuntu/.nvm/nvm.sh
nvm use 22
npm run build
npm start
```

出现以下日志，说明飞书连接已经成功：

```text
Connected to Feishu (websocket)
[ws] ws client ready
BioClaw running (trigger: @Bioclaw)
```

## 四、如何测试

### 1. 私聊测试

如果单聊权限已开通：

1. 直接私聊机器人
2. 发送：

```text
你好
```

成功时，服务器会出现：

```text
Feishu message received
Feishu message sent
```

### 2. 群聊测试

群聊测试请优先用**企业内部群**，不要先用外部群。

1. 新建一个企业内部群
2. 把机器人加进群
3. 第一条消息先发：

```text
@机器人 你好
```

如果你只开了“群聊中 @ 机器人消息事件”，那就必须带 `@` 测试。

## 五、常见问题

### 1. `Invalid API key · Fix external API key`

这通常不是飞书问题，而是模型提供商 key 无效。当前容器逻辑在未显式配置 `MODEL_PROVIDER` 且没有 OpenRouter / OpenAI-compatible key 时，会默认走 Anthropic。

如果你准备使用 OpenRouter，请确保 `.env` 中至少有：

```bash
MODEL_PROVIDER=openrouter
OPENROUTER_API_KEY=...
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=openai/gpt-5.4
```

### 2. `未检测到应用连接信息，请确保长连接建立成功后再保存配置`

含义是：飞书后台还没检测到这个应用的长连接在线。

处理顺序应该是：

1. 先在服务器上启动 BioClaw
2. 确认终端出现 `Connected to Feishu (websocket)`
3. 保持进程运行
4. 刷新飞书后台页面
5. 再保存长连接配置

### 3. 群里显示“暂无可添加的机器人”

这通常不是 BioClaw 代码问题，而是飞书客户端侧的群可见性/租户范围限制。最常见原因：

- 当前群是**外部群**
- 应用可用范围不包含当前账号或群成员
- 你没有群管理权限
- 应用虽然能私聊，但没有被客户端认定为可加入该群的机器人

**结论：请优先用企业内部群测试。**

## 六、成功日志示例

当飞书消息真正进入 BioClaw 并回发成功时，常见日志如下：

```text
Group registered
Feishu message received
Processing messages
Spawning container agent
Feishu message sent
```

这说明：

- 飞书事件投递成功
- 会话自动注册成功
- Agent 容器已启动
- 回复已成功回发到飞书

## 相关文档

- [消息通道配置](CHANNELS.zh-CN.md)
- [QQ / 飞书实施方案](QQ_FEISHU_MIGRATION_PLAN.zh-CN.md)
