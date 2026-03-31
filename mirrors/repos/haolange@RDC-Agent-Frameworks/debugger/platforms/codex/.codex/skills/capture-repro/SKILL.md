---
name: capture-repro
description: Internal specialist skill for Establish reproducible capture baselines and anchors.. Use when `rdc-debugger` dispatches capture-repro work.
metadata:
  short-description: Capture & Repro
---

# 角色技能包装说明

Current file is the role skill entry for Codex.

该角色默认是 internal/debug-only specialist。平台启动后不会自动进入该角色；只有用户手动召唤 `rdc-debugger` 并由它分派时，才进入当前 role。

Read first:

1. common/skills/rdc-debugger/SKILL.md
2. common/skills/capture-repro/SKILL.md
3. common/config/platform_capabilities.json

Platform contract: `coordination_mode = staged_handoff`, `sub_agent_mode = puppet_sub_agents`, `peer_communication = via_main_agent`.


当前平台的 role gate 由 `rdc-debugger` 通过 `.codex/runtime_guard.py` 统一执行。
没有 passed `artifacts/intake_gate.yaml`、passed `artifacts/runtime_topology.yaml` 与主 agent handoff 前，不得进入 live 调查。
当前 role 只读消费 gate 结果，不得重判 intent gate，不得直接分派其他 specialist。

Do not use this platform template before copying top-level `debugger/common/` into the platform-local `common/`.
Runtime case/run artifacts and reports are written under the platform-local `workspace/`.
