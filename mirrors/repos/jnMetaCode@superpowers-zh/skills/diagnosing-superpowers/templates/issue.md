Title: <skill or symptom>: <one-line observable> (<harness>)

- [x] 我已搜索现有 issue，确认这不是重复的（搜索词：<query terms>；最接近的：<#n 标题，或 "none">）

## 环境信息（必填）

| 字段 | 值 | 来源标注 / 支撑证据 |
|-------|-------|-------------------------------|
| Superpowers 版本 | <version> (<sha or "not a checkout">) | <historical evidence / unverified snapshot / current observation / unknown>; <location> |
| 工具（Claude Code、Cursor 等） | <harness> | <label>; <location> |
| 工具版本 | <version> | <label>; <location> |
| 模型及版本 | <model ids seen> | <label>; <location> |
| 已安装的全部插件 | <list> | <label>; <location> |
| 操作系统 + Shell | <os version>, <shell> | <label>; <location> |

## 这是 Superpowers 的问题还是平台的问题？

- [ ] 我已确认此问题在未安装 Superpowers 的情况下不会发生

提交者没有尝试过在不装 superpowers 的情况下复现。下面是涉及程度的证据；它不能确立因果。

## 发生了什么？

<问题陈述，然后是分诊结论，`path:line` 引用改写为 `transcript line <n>`。>

## 复现步骤

1. <第一条人类提示词，已脱敏>
2. <导致问题的各轮次，每轮一行>
3. <可观测量>

## 预期行为

<来自问题陈述>

## 实际行为

<来自分诊结论>

## 调试日志或对话记录

Session id(s): <ids>。已交付的本地归档：<路径，脱敏级别 <level>
| none built>。附加的打包材料：<不作声明；仅在批准后附上>。
按诊断报告，Superpowers 的涉及程度：<possible | likely>，证据见 <transcript lines>。
本报告不提出修复方案。

---
由 `diagnosing-superpowers` 技能提交。模型、工具、工具版本和已安装插件已在上方列出。
