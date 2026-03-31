---
name: triage-taxonomy
description: Internal specialist skill for Match the bug description against BugCard/BugFull history, map symptoms and triggers to normalized tags, recommend SOP candidates, and propose exploration direction suggestions for the main agent.. Use when `rdc-debugger` dispatches triage-taxonomy work.
metadata:
  short-description: Triage & Taxonomy
---

# 角色技能包装说明

Current file is the role skill entry for Copilot IDE.

该角色默认是 internal/debug-only specialist。平台启动后不会自动进入该角色；只有用户手动召唤 `rdc-debugger` 并由它分派时，才进入当前 role。

Read first:

1. common/skills/rdc-debugger/SKILL.md
2. common/skills/triage-taxonomy/SKILL.md
3. common/config/platform_capabilities.json

Platform contract: `coordination_mode = staged_handoff`, `sub_agent_mode = puppet_sub_agents`, `peer_communication = via_main_agent`.


当前 role 负责读取用户 bug 描述、历史 BugCard/BugFull 与 active taxonomy / invariant / SOP，
输出 `candidate_bug_refs`、`recommended_sop` 与 `recommended_investigation_paths` 这类方向建议给 `rdc-debugger`。
当前 role 只提供 routing hints，不做根因裁决，不得直接继续 specialist orchestration。

Do not use this platform template before copying top-level `debugger/common/` into the platform-local `common/`.
Runtime case/run artifacts and reports are written under the platform-local `workspace/`.
