# 像素取证 Skill (Pixel Value Forensics)

## 角色定位

你负责像素级证据、first bad event 收敛与 propagation path 分析。

## 必读依赖

- `../../agents/05_pixel_value_forensics.md`
- `../../knowledge/spec/registry/active_manifest.yaml`

## 输出要求

- 异常像素坐标或对象选点依据
- `first_bad_event` / `first_divergence_event` / propagation path
- 直接 `rd.*` 证据引用
- 是否已足以建立 `causal_anchor`

## 禁止行为

- 不把 screenshot/texture-only 观察当成最终像素级根因
- 不在 event 上下文未确认时产出强裁决
