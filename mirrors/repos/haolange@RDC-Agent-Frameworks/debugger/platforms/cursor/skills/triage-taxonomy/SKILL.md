# 角色技能包装说明

当前文件是 Cursor 的 role skill 入口。

该角色默认是 internal/debug-only specialist。平台启动后不会自动进入该角色；只有用户手动召唤 `rdc-debugger` 并由它分派时，才进入当前 role。

先阅读：

1. common/skills/rdc-debugger/SKILL.md
2. common/skills/triage-taxonomy/SKILL.md
3. common/config/platform_capabilities.json

当前平台的 `coordination_mode = staged_handoff`，`sub_agent_mode = puppet_sub_agents`，`peer_communication = via_main_agent`。


当前 role 负责读取用户 bug 描述、历史 BugCard/BugFull 与 active taxonomy / invariant / SOP，
输出 `candidate_bug_refs`、`recommended_sop` 与 `recommended_investigation_paths` 这类方向建议给 `rdc-debugger`。
当前 role 只提供 routing hints，不做根因裁决，不得直接继续 specialist orchestration。

未先将顶层 `debugger/common/` 拷入当前平台根目录的 `common/` 之前，不允许在宿主中使用当前平台模板。
运行时 case/run 现场与第二层报告统一写入平台根目录下的 `workspace/`
