# 会话诊断：<session-id>

Report path: ~/.superpowers/diagnosing-superpowers/<session-id>/report.md
Written: <ISO timestamp>

## 1. 问题陈述（必填）

<从案例文件复制。>

## 2. 分诊结论（必填）

<证据表明报告问题附近发生了什么。用文字叙述，每条声明后面都跟 `path:line`。说明置信度：
high / medium / low，以及什么能提高它。不对 superpowers 应该怎么做发表任何意见。>

## 3. 环境（必填）

- 操作系统：
- 工具及版本：
- 出现过的模型：
- Superpowers install root / 版本 / git sha：
- 读取或注入的技能文件（来自案例文件的 sha1 表）：
- 其他插件、扩展、MCP 服务器：
- 存在的指令文件（只列路径）：

把每个环境字段和技能观察标注为 historical evidence（历史证据）、unverified snapshot
（未核实快照）、current observation（当前观测）或 unknown（未知），并记录其支撑证据的位置。

## 4. 检查过的会话（必填）

| 角色 | Session id | 绝对路径 | 行数 | 字节数 |
|---|---|---|---|---|

被排除的候选：<id — 路径 — 理由>，或 "none"。

## 5. 时间线（必填）

每条人类输入的提示词一行。Events 列列出调用的技能、派发的子智能体、压缩、错误、恢复、中止。

| 轮次 | 行 | 时间 | 请求（一行） | Events |
|---|---|---|---|---|

## 6. 发现（必填，每个维度一小节）

每条发现：
```
- finding: <一句话>
  evidence: <path:line> — "<简短引文>"
  turns: <first>–<last>
  confidence: high | medium | low
```
没有可报告内容的维度写 `none found — checked: <检查了什么>`。

### 6.1 技能时间线
### 6.2 计划遵循
### 6.3 重复劳动
### 6.4 磕绊
### 6.5 质量证据
### 6.6 请求冲突
### 6.7 成本与耗时
### 6.8 用到的其他插件和技能

## 7. Superpowers 涉及程度（必填）

not indicated | possible | likely

证据行：<path:line 列表>。本节只陈述涉及程度。不指出缺陷，也不提议修改。

## 8. 覆盖说明（必填）

- 未读取：<范围、文件及原因>
- 不可用的工具功能：<列表或 none>
- 读取时会话仍在进行：yes/no
- 请你的人类伙伴复核：<列表或 none>

## 9. 相似会话（仅在被要求时）

| Session id | 路径 | 日期 | 工具 | 匹配 | 未匹配 |
|---|---|---|---|---|---|
