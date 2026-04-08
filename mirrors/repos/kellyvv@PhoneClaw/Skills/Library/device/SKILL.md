---
name: Device
name-zh: 设备
description: '查询当前设备的名称、机型、系统版本、内存、处理器数量等系统信息 (基于 iOS 公开 API)。'
version: "1.0.0"
icon: desktopcomputer
disabled: false
type: device

triggers:
  - 设备
  - 系统信息
  - 当前设备
  - 本机
  - 系统版本
  - 内存
  - 处理器

allowed-tools:
  - device-info
  - device-name
  - device-model
  - device-system-version
  - device-memory
  - device-processor-count
  - device-identifier-for-vendor

examples:
  - query: "这台手机的设备信息是什么"
    scenario: "整体汇总"
  - query: "系统版本是多少"
    scenario: "查单项"
  - query: "内存多大"
    scenario: "查单项"
---

# 设备信息查询

## 工具选择

- 用户问"整体配置 / 全部信息 / 这台手机什么样" → `device-info`
- 用户问单个属性 → 用最小的专用工具:
  - 名字 → `device-name`
  - 机型 → `device-model`
  - 系统版本 → `device-system-version`
  - 内存 → `device-memory`
  - CPU 核数 → `device-processor-count`
  - 厂商标识 → `device-identifier-for-vendor`

## 行为约束

1. 必须用户**明确**问当前设备/本机/手机的属性才调用。"配置""信息"这种含糊词不触发。
2. iOS 公开 API 只能返回通用机型 (如 `iPhone`)，**不要**自己映射成 "iPhone 17 Pro Max" 这种营销名。如果用户问"什么型号", 如实说明限制。
3. 工具返回 JSON 后, 转成自然中文描述, 不要照搬原始字段名。
4. 拿到结果直接答, 不要反问 "你指的是什么配置"。

## 调用格式

<tool_call>
{"name": "device-info", "arguments": {}}
</tool_call>
