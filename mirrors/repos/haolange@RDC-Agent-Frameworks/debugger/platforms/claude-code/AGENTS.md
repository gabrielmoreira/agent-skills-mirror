# Claude Code 模板

## Common-First Adapter Contract

- 目标 contract：`staged_handoff + multi_agent + single_runtime_single_context`
- shared harness / broker 是唯一 enforcement SSOT
- 宿主 hooks 只负责接入与转发

accepted intake 后必须具备：

- `artifacts/entry_gate.yaml`
- `artifacts/intake_gate.yaml`
- `artifacts/runtime_session.yaml`
- `artifacts/runtime_snapshot.yaml`
- `artifacts/ownership_lease.yaml`
- `artifacts/runtime_failure.yaml`