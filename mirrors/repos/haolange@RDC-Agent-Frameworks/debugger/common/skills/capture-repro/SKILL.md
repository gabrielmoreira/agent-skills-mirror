# 捕获与复现 Skill (Capture Repro)

## 角色定位

你负责建立可复用的 capture/session 基线，并确认 capture 集合是否与当前 `fix reference` 可对齐。

## 输出要求

- capture/session anchor
- 初始 `runtime_baton`
- `reference_alignment_status`
- `reference_alignment_gaps`

## 禁止行为

- 不在没有基线或 fix reference 对齐性的情况下让 specialist 直接进入根因调查
- 不把 capture/session anchor 当成最终 `causal_anchor`
