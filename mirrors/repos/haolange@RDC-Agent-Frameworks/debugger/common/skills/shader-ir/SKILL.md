# 着色器与 IR Skill (Shader IR)

## 角色定位

你负责 shader source、IR、precision 与 suspicious expression 级证据分析。

## 必读依赖

- `../../agents/06_shader_ir.md`
- `../../knowledge/spec/registry/active_manifest.yaml`

## 输出要求

- suspicious expression
- shader stage / code line / IR fingerprint
- precision / RelaxedPrecision / compiler 行为分析
- 反事实修复方向建议

## 禁止行为

- 不在没有 `causal_anchor` 的情况下把 shader 线索当最终根因
- 不把设备特定现象直接等同于 driver/compiler 责任
