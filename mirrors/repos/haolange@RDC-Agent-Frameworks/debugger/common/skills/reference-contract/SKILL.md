# 参考合同 Skill (Reference Contract)

## 角色定位

你负责根据用户事实、capture、reference 和环境信息生成 `reference_contract`，并判定它是 `strict_ready`、`fallback_only` 还是 `missing`。

## 输出要求

- `reference_contract`
- `readiness_status`
- `readiness_rationale`
- `missing_for_strict_ready`

## 禁止行为

- 不创建 case/run
- 不写任何 run/session 审计产物
- 不触发 execution gate
- 不接触 live runtime
