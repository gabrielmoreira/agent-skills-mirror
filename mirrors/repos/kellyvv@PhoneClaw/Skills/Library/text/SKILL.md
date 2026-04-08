---
name: Text
name-zh: 文本
description: '文本处理工具：哈希计算、翻转等。当用户需要对文本进行处理或转换时使用。'
version: "1.0.0"
icon: textformat
disabled: false
type: device

triggers:
  - 哈希
  - hash
  - 翻转
  - 反转
  - 文本处理

allowed-tools:
  - calculate-hash
  - text-reverse

examples:
  - query: "计算 Hello World 的哈希值"
    scenario: "哈希计算"
  - query: "把这段文字翻转过来"
    scenario: "文本翻转"
---

# 文本处理

你负责帮助用户进行文本处理操作。

## 可用工具

- **calculate-hash**: 计算文本的哈希值（参数: text — 要计算哈希的文本）
- **text-reverse**: 翻转文本（参数: text — 要翻转的文本）

## 执行流程

1. 判断用户需要哪种文本操作
2. 调用对应工具，传入 text 参数
3. 返回处理结果

## 调用格式

<tool_call>
{"name": "工具名", "arguments": {"text": "要处理的文本"}}
</tool_call>
