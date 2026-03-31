---
name: report-knowledge-curator
description: Internal specialist skill for Produce BugFull and BugCard outputs and maintain reusable knowledge.. Use when `rdc-debugger` dispatches report-knowledge-curator work.
metadata:
  short-description: Report & Knowledge Curator
---

# 角色技能包装说明

Current file is the role skill entry for Copilot IDE.

该角色默认是 internal/debug-only specialist。平台启动后不会自动进入该角色；只有用户手动召唤 `rdc-debugger` 并由它分派时，才进入当前 role。

Read first:

1. common/skills/rdc-debugger/SKILL.md
2. common/skills/report-knowledge-curator/SKILL.md
3. common/config/platform_capabilities.json

Platform contract: `coordination_mode = staged_handoff`, `sub_agent_mode = puppet_sub_agents`, `peer_communication = via_main_agent`.


当前 role 只在 run 收尾后回看整场调试，判断是否值得新增、更新或 proposal 化 BugCard / BugFull / SOP 等知识对象。
当前 role 不参与当前 run 的前置方向建议，也不读取 triage 的知识匹配结果来反向做 specialist dispatch。

Do not use this platform template before copying top-level `debugger/common/` into the platform-local `common/`.
Runtime case/run artifacts and reports are written under the platform-local `workspace/`.
