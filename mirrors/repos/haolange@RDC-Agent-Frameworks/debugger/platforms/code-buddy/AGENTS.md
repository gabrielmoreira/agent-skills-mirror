# Code Buddy 模板

## Common-First Adapter Contract

- 目标 contract：`staged_handoff + multi_agent + single_runtime_single_context`
- shared harness / broker 是唯一 enforcement SSOT
- pseudo-hooks 只负责转发，不再维护第二套 dispatch/runtime 规则

accepted intake 后必须具备：

- `artifacts/entry_gate.yaml`
- `artifacts/intake_gate.yaml`
- `artifacts/runtime_session.yaml`
- `artifacts/runtime_snapshot.yaml`
- `artifacts/ownership_lease.yaml`
- `artifacts/runtime_failure.yaml`