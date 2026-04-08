---
name: Calendar
name-zh: 日历
description: '创建新的日历事项 (会议/约会/日程)。'
version: "1.0.0"
icon: calendar
disabled: false
type: device

triggers:
  - 日历
  - 日程
  - 会议
  - 约会
  - 安排

allowed-tools:
  - calendar-create-event

examples:
  - query: "帮我创建明天下午两点的产品评审会议"
    scenario: "新建日历事项"
---

# 日历事项创建

严格遵循下面的参数规则, 不要自由发挥, 不要反问多余问题。

## 参数

**硬参** (必填, 缺失才允许追问):
- `start`: ISO 8601 开始时间, 例如 `2026-04-07T14:00:00`

**软参** (用户没说就省略字段, 永远不追问):
- `title`: 事项标题
- `end`: 结束时间
- `location`: 地点
- `notes`: 备注

## start 提取规则

用户话语里**只要有任何时间线索就视为 start 已提供**:
- 相对时间: "明天下午两点" / "今晚八点" / "一小时后" / "后天中午"
- 绝对时间: "5月3日 15:00" / "4月10日晚上"

结合 system prompt 的**当前时间锚点**算出 ISO 8601 字符串。**禁止**对已经给了相对时间的用户反问 "哪一天"。

只有用户完全没给时间 (如"安排个会议") 才允许输出:
```
{"_needs_clarification": "请告诉我具体时间"}
```

## title 处理

- 用户话语里有名词短语 (如"产品评审会议") → 直接当 title
- 只有动作 (如"安排个会") → title 字段省略, 工具会用默认
- **永远禁止**输出 "请告诉我标题" / "标题是什么" 这类反问

## 行为

拿到 start 立刻输出工具调用 JSON, 不解释、不反问、不追问 end/location/notes。

## 调用格式

<tool_call>
{"name": "calendar-create-event", "arguments": {"title": "产品评审会议", "start": "2026-04-07T14:00:00"}}
</tool_call>
