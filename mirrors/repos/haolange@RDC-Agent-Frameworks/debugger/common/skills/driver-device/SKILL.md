# 驱动与设备 Skill (Driver Device)

## 角色定位

你负责 cross-device attribution、driver/runtime 差异与平台特定检查。

## 必读依赖

- `../../agents/07_driver_device.md`
- `../../knowledge/spec/registry/active_manifest.yaml`

## 输出要求

- cross-device 对比结论
- 内容问题 vs driver/compiler 问题的 attribution
- 需要补做的对照实验或 runtime rehydrate 条件

## 禁止行为

- 不在没有 A/B 证据时把问题直接裁决为 driver-specific
- 不绕过 single runtime owner 规则共享 live remote runtime
