---
name: Reminders
name-zh: 提醒事项
description: '创建新的提醒事项。当用户需要记得做某事、设置待办或提醒时使用。'
version: "1.0.0"
icon: bell
disabled: false
type: device

triggers:
  - 提醒
  - 待办
  - 记得
  - 提示

allowed-tools:
  - reminders-create

examples:
  - query: "提醒我今晚八点发文件"
    scenario: "新建提醒事项"
---

# 提醒事项创建

你负责帮助用户创建新的提醒事项。

## 可用工具

- **reminders-create**: 创建提醒事项
  - `title`: 必填，提醒标题
  - `due`: 可选，ISO 8601 提醒时间，例如 `2026-04-07T20:00:00`
  - `notes`: 可选，备注

## 执行流程

1. 只有当用户明确要设置提醒或待办时才调用工具
2. 由你提取标题、时间、备注
3. 如果有时间，必须转换成 ISO 8601 字符串
4. 如果缺少 `title`，先简短追问
5. 工具成功后，直接告诉用户提醒已创建

## 调用格式

<tool_call>
{"name": "reminders-create", "arguments": {"title": "发文件", "due": "2026-04-07T20:00:00"}}
</tool_call>
