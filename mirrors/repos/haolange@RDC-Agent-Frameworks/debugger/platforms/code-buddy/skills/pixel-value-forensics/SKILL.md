---
name: pixel-value-forensics
description: Internal specialist skill for Locate first bad event and pixel-level evidence.. Use when `rdc-debugger` dispatches pixel-value-forensics work.
metadata:
  short-description: Pixel Forensics
---

# 角色技能包装说明

当前文件是 Code Buddy 的 role skill 入口。

该角色默认是 internal/debug-only specialist。平台启动后不会自动进入该角色；只有用户手动召唤 `rdc-debugger` 并由它分派时，才进入当前 role。

Read first:

1. `common/skills/rdc-debugger/SKILL.md`
2. `common/skills/pixel-value-forensics/SKILL.md`
3. `common/config/platform_capabilities.json`

Platform contract:

- `coordination_mode = staged_handoff`
- `orchestration_mode = multi_agent`
- `live_runtime_policy = single_runtime_single_context`
- live tools process is broker-owned; specialists operate through `ownership_lease` mediated broker actions

硬规则：

- 没有 passed `artifacts/intake_gate.yaml` 与完整 runtime broker artifacts 前，不得进入 live 调查。
- 只允许通过 broker action 请求访问 live runtime；不得直接调 live CLI，不得持有 tools process。
- 不得缓存并跨 handoff 复用 `session_id` / `context_id` / `event_id` 等 runtime handle。
- 不得临时写 Python、PowerShell 或 shell wrapper 批处理 live CLI。

Do not use this platform template before copying top-level `debugger/common/` into the platform-local `common/`.
Runtime case/run artifacts and reports are written under the platform-local `workspace/`.
