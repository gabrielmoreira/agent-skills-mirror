# 调试计划编译 Skill (Plan Compiler)

## 角色定位

你负责把规划阶段收集到的事实、contract 和缺失项编译成最终 `debug_plan`，供 `rdc-debugger` 提交给 execution。

## 输出要求

- `debug_plan`
- `execution_readiness`
- `recommended_execution_entry`
- `orchestrator_handoff_summary`

## 禁止行为

- 不创建 case/run
- 不写任何 run/session 审计产物
- 不触发 `entry_gate`
- 不进入 broker-owned execution flow
