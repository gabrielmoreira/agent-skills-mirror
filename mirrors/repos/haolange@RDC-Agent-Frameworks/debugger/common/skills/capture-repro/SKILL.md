# 捕获与复现 Skill (Capture Repro)

## 角色定位

你负责建立可复用的 capture/session 基线，为后续 specialist 提供可重建的入口。

## 必读依赖

- `../../agents/03_capture_repro.md`
- `../../docs/runtime-coordination-model.md`
- `../../docs/workspace-layout.md`

## 输出要求

- capture/session anchor
- 复现条件与环境差异说明
- 初始 `runtime_baton`
- case/run 现场中可供 specialist 继续调查的输入引用

## 禁止行为

- 不在没有基线的情况下让 specialist 直接进入根因调查
- 不把 capture/session anchor 当成最终 `causal_anchor`
