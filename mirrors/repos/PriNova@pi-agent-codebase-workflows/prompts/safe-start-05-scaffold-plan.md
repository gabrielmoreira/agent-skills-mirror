---
description: "Safe-start pass 5: plan minimal scaffold and tooling before code"
argument-hint: "[framework/tooling preference]"
---
Use `/skill:safe-start` Pass 5 — Scaffold Plan.

Framework/tooling preference: $ARGUMENTS

Read prior design docs under `docs/agent/` if present. Do not scaffold before the plan is explicit unless user already approved implementation.

Produce a minimal scaffold plan with:
- File tree to create
- Package/build config choices
- Format/lint/typecheck choices where suitable
- Test runner and initial tests
- App entrypoint and health/hello path
- Config/env example if needed
- Exact commands to create/install/run
- Files that will be generated or edited
- Validation commands expected after scaffold
- Risks/assumptions

Avoid:
- speculative abstractions
- unused frameworks
- broad feature implementation
- auth/payment/admin systems unless the initial project goal requires them

Approval gate: ask whether to write files and run scaffold commands unless user explicitly requested implementation now.
