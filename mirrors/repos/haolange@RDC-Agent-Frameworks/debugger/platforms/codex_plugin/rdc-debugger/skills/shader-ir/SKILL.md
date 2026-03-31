# 角色技能包装说明

当前文件是 Codex Plugin 的 role skill 入口。

该角色默认是 internal/debug-only specialist。平台启动后不会自动进入该角色；只有用户手动召唤 `rdc-debugger` 并由它分派时，才进入当前 role。

先阅读：

1. common/skills/rdc-debugger/SKILL.md
2. common/skills/shader-ir/SKILL.md
3. common/config/platform_capabilities.json

当前平台的 `coordination_mode = staged_handoff`，`sub_agent_mode = puppet_sub_agents`，`peer_communication = via_main_agent`。


当前平台不预注册 `.codex/agents` 自定义 agent；如需进入当前 role，`rdc-debugger` 必须显式要求 Codex 创建通用 sub-agent，并让它先加载当前插件内的 `skills/shader-ir/SKILL.md`。

未先将顶层 `debugger/common/` 拷入当前平台根目录的 `common/` 之前，不允许在宿主中使用当前平台模板。
运行时 case/run 现场与第二层报告统一写入平台根目录下的 `workspace/`
