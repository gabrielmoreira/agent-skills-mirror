# 角色技能包装说明

当前文件是 Manus 的 role skill 入口。

该角色默认是 internal/debug-only specialist。平台启动后不会自动进入该角色；只有用户手动召唤 `rdc-debugger` 并由它分派时，才进入当前 role。

先阅读：

1. common/skills/rdc-debugger/SKILL.md
2. common/skills/shader-ir/SKILL.md
3. common/config/platform_capabilities.json

当前平台的 `coordination_mode = workflow_stage`，`sub_agent_mode = instruction_only_sub_agents`，`peer_communication = none`。


未先将顶层 `debugger/common/` 拷入当前平台根目录的 `common/` 之前，不允许在宿主中使用当前平台模板。
运行时 case/run 现场与第二层报告统一写入平台根目录下的 `workspace/`
