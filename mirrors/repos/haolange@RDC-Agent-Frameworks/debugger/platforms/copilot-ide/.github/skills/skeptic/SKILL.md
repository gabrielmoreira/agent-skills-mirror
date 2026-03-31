---
name: skeptic
description: Internal specialist skill for Challenge weak claims and sign off only when proven.. Use when `rdc-debugger` dispatches skeptic work.
metadata:
  short-description: Skeptic
---

# 角色技能包装说明

Current file is the role skill entry for Copilot IDE.

该角色默认是 internal/debug-only specialist。平台启动后不会自动进入该角色；只有用户手动召唤 `rdc-debugger` 并由它分派时，才进入当前 role。

Read first:

1. common/skills/rdc-debugger/SKILL.md
2. common/skills/skeptic/SKILL.md
3. common/config/platform_capabilities.json

Platform contract: `coordination_mode = staged_handoff`, `sub_agent_mode = puppet_sub_agents`, `peer_communication = via_main_agent`.


Do not use this platform template before copying top-level `debugger/common/` into the platform-local `common/`.
Runtime case/run artifacts and reports are written under the platform-local `workspace/`.
