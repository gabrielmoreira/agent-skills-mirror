# Runs, harnesses, and model accounts — agent access

Product map: [Runs, harnesses, and model accounts](../feature-map/runs-adapters.md).

Review date: 2026-10-12. Source commit: `f981fa3cc10cb8663a87dec60345fbff46d54d0a`.

This is a source-reviewed baseline of representative operations and known gaps.
Each capability needs operation-level review before its entire scope can be
qualified. No live agent execution is claimed. Follow the [map contract](../README.md)
for format, permission checks, evidence and maintenance.

## `availability`

Review: `baseline`.

API: `present` — representative operation IDs:

- `GET /api/adapters`.
- `GET /api/companies/{companyId}/adapters/{type}/models`.

Agent access: `partial` — Agent company-model API and bound runtime context; board
adapter/account inventories.

Policy: Run/cost visibility and agent configuration policy; adapter installation/account
login/session control require board/admin.

Evidence: `source-only` — [implementation](../../server/src/routes/agents.ts#L6608) at
the reviewed commit above.

Verification: `not-run` — exercise a listed permitted operation with actual agent
credentials/run context; inspect its result and applicable persistence/attribution.
Assert the relevant denied actor, owner, company or mode from Policy. Review the
remaining operations before qualifying the whole capability.

Gaps: Raw instance adapter listing requires board, while company model discovery exists
for eligible agents.

## `validation`

Review: `baseline`.

API: `present` — representative operation IDs:

- `POST /api/companies/{companyId}/adapters/{type}/test-environment`.

Agent access: `partial` — Permitted agent-creation validation path / REST / CLI;
operator account login.

Policy: Run/cost visibility and agent configuration policy; adapter installation/account
login/session control require board/admin.

Evidence: `source-only` — [implementation](../../server/src/routes/agents.ts#L6608) at
the reviewed commit above.

Verification: `not-run` — exercise a listed permitted operation with actual agent
credentials/run context; inspect its result and applicable persistence/attribution.
Assert the relevant denied actor, owner, company or mode from Policy. Review the
remaining operations before qualifying the whole capability.

Gaps: Environment test path checks creation/configuration policy; missing provider auth
must use its owner setup flow.

## `runs`

Review: `baseline`.

API: `present` — representative operation IDs:

- `GET /api/heartbeat-runs/{runId}`.
- `GET /api/heartbeat-runs/{runId}/log`.

Agent access: `available` — REST / native call_api / CLI run.

Policy: Run/cost visibility and agent configuration policy; adapter installation/account
login/session control require board/admin.

Evidence: `source-only` — [implementation](../../server/src/routes/agents.ts#L6608) at
the reviewed commit above.

Verification: `not-run` — exercise a listed permitted operation with actual agent
credentials/run context; inspect its result and applicable persistence/attribution.
Assert the relevant denied actor, owner, company or mode from Policy. Review the
remaining operations before qualifying the whole capability.

Gaps: Provider trace reveals/downloads require instance-admin and cannot be counted as
ordinary run output access.

## `session`

Review: `baseline`.

API: `present` — representative operation IDs:

- `POST /api/agents/{id}/runtime-state/reset-session`.
- `GET /api/agents/{id}/task-sessions`.

Agent access: `restricted` — Board session controls; native server-owned session
continuation.

Policy: Run/cost visibility and agent configuration policy; adapter installation/account
login/session control require board/admin.

Evidence: `source-only` — [implementation](../../server/src/routes/agents.ts#L6608) at
the reviewed commit above.

Verification: `not-run` — assert the documented agent denial with an owned test fixture;
verify any listed agent request/result path separately. A delegated operation needs its
own policy and access review.

Gaps: Execution context reset is not a permitted generic native API mutation or an
ordinary agent management path.
