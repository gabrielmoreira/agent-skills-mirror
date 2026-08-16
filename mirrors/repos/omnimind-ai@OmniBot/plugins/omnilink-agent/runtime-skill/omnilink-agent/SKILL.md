---
name: omnilink-agent
description: Use the built-in OmniLink collaboration primitives to inspect trusted devices, compose cross-device event workflows, send messages to another Xiaowan, and continue after reconnect.
metadata:
  version: "0.2.0"
  source: official-runtime-bundle
---

# OmniLink 跨设备协作工具箱

这是小万的内置跨设备能力。它让两个设备上的小万通过 OmniLink 互相查询状态、接收事件和发信号。你要根据用户意图组合通用工具，不要为每个场景假造新的工具名，也不要要求用户复制 token、端口、MCP JSON 或 shell 命令。

这里的“生成工具”是由你在当前对话中生成一组有顺序的工具调用，而不是修改插件、编写 shell 或创造一个绕过授权的新 API。把自然语言意图拆成：发现设备 → 选择真实的 `device_id` → 读取或订阅事件 → 必要时给另一台小万发消息。一个意图可以组合多次调用；工具返回的状态、事件和 cursor 是下一步调用的输入。

例如，用户说“如果另一台手机有通知，就告诉那台设备上的小万我已经知道了”时，先用 `omnilink_devices` 找到目标，再用 `omnilink_events(mode=subscribe)` 订阅 `NOTIFICATION_UPSERTED` / `NOTIFICATION_REMOVED`。收到事件后，如果用户确实要求回信，再用 `omnilink_control(action=send_message, input=...)` 发送；不要把这个流程固化成一个名为“通知确认”的专用工具。对于只要求一次查询的意图，完成一次读取即可，不要擅自建立长期订阅。

## 对话触发

- “列出协作设备” → `omnilink_devices`
- “查另一台手机的电量/是否在线/是否充电/网络状态” → `omnilink_devices`，从目标设备的 `reachable` 和 `readiness.device` 自己组合答案
- “现在读取另一台手机的通知” → `omnilink_events`，传入 `device_id`、`event_types=[NOTIFICATION_UPSERTED, NOTIFICATION_REMOVED]` 和 `mode=read`，需要短等候时使用 `wait_ms`
- “开始持续接收另一台手机的通知” → `omnilink_events`，传入同一组 `event_types` 和 `mode=subscribe`
- “停止接收另一台手机的通知” → `omnilink_events`，传入目标 `device_id` 和 `mode=stop`
- “给另一台设备上的小万发信号/消息：……” → `omnilink_control`，传入 `action=send_message` 和结构化 `input`
- “读取另一台设备的小万消息事件” → `omnilink_events`，传入 `event_types=[AGENT_MESSAGE_RECEIVED]` 和 `mode=read`

## 操作约束

1. 先调用 `omnilink_devices`，再使用返回的稳定 `device_id`；不要猜设备 ID。
2. 状态回答必须以 `omnilink_devices` 返回的 `reachable` 和 `readiness.device` 为准；不要根据设备名、上次结果或猜测回答电量。
3. `batteryPercent` 可能为空；为空时明确说“暂时没有电量读数”，不要补估计值。`reachable=false` 时明确说设备当前不可达。
4. 通知事件只回流应用标识和安全摘要。通知标题、正文和敏感内容不会通过 Agent 工具传输；不要要求绕过这个限制。
5. 发送消息时把用户原意放进 `omnilink_control` 的 `input.message`，不要把 token、私有路径或其他敏感数据放进消息。
6. 只在确实需要时指定 `input.conversationId`、`input.recipientAgentId`、`input.messageId`；省略时由插件使用小万 Agent 的安全默认值并生成幂等 ID。
7. `omnilink_events` 的 `event_types` 只能使用 Agent-safe 类型；不要猜测未注册事件类型。
8. 返回的 `cursor` 是不透明值，只能原样带回下一次读取；订阅由插件负责持久化游标和断线恢复。
9. `omnilink_control(action=send_message)` 返回 `queued` 只代表已进入 OmniLink 队列，不代表对方小万已经读到；只有看到入站事件或明确 receipt 才能说“已收到”。
10. 如果返回本地授权或连接失败，明确告诉用户需要在 OmniLink 中批准/恢复，不要假装消息或通知已经送达。

开启通知监听后，后续通知由插件自动回流当前聊天；收到后说明“协作设备收到通知”及安全摘要，不显示通知正文、认证凭据或稳定设备 ID。入站 Agent 消息也会自动回流当前聊天。
