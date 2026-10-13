# Recovery — agent access

Product map: [Recovery](../feature-map/recovery.md).

Review date: 2026-10-12. Source commit: `f981fa3cc10cb8663a87dec60345fbff46d54d0a`.

This is a source-reviewed baseline of representative operations and known gaps.
Each capability needs operation-level review before its entire scope can be
qualified. No live agent execution is claimed. Follow the [map contract](../README.md)
for format, permission checks, evidence and maintenance.

## `diagnosis`

Review: `baseline`.

API: `present` — representative operation IDs:

- `GET /api/issues/{id}/diagnostics/blockers`.
- `GET /api/issues/{id}/recovery-actions`.

Agent access: `available` — REST / native call_api; CLI issue diagnostics.

Policy: Task/run visibility, run ownership and source/action policy; workspace export
retry and some operator controls require board.

Evidence: `source-only` — [implementation](../../server/src/routes/issues.ts#L9478) at
the reviewed commit above.

Verification: `not-run` — exercise a listed permitted operation with actual agent
credentials/run context; inspect its result and applicable persistence/attribution.
Assert the relevant denied actor, owner, company or mode from Policy. Review the
remaining operations before qualifying the whole capability.

Gaps: Diagnostics expose recorded cause and boundaries; source-backed reading does not
prove successful recovery.

## `bounded-continuation`

Review: `baseline`.

API: `present` — representative operation IDs:

- `POST /api/issues/{id}/recovery-actions/resolve`.

Agent access: `partial` — Eligible agent REST / CLI; native generic mutation restricted.

Policy: Task/run visibility, run ownership and source/action policy; workspace export
retry and some operator controls require board.

Evidence: `source-only` — [implementation](../../server/src/routes/issues.ts#L9478) at
the reviewed commit above.

Verification: `not-run` — exercise a listed permitted operation with actual agent
credentials/run context; inspect its result and applicable persistence/attribution.
Assert the relevant denied actor, owner, company or mode from Policy. Review the
remaining operations before qualifying the whole capability.

Gaps: Underlying route has agent checks; no corresponding default native recovery
mutation tool is advertised.

## `source-action`

Review: `baseline`.

API: `present` — representative operation IDs:

- `GET /api/issues/{id}/recovery-actions`.
- `POST /api/issues/{id}/recovery-actions/resolve`.

Agent access: `partial` — Eligible agent REST / CLI; source-bound recovery state.

Policy: Task/run visibility, run ownership and source/action policy; workspace export
retry and some operator controls require board. Completion or cancellation of a
task does not clear its exact unresolved native workspace owner hold. Physical
owner release still requires the [operator stop-verification procedure](../../doc/native-workspace-finalization-recovery.md).

Evidence: `source-only` — [implementation](../../server/src/routes/issues.ts#L9478) at
the reviewed commit above. Exact owner hold retention in the
[recovery state helper](../../server/src/services/native-runtime/native-workspace-finalization-recovery-state.ts)
was reviewed at `89770ba707fb1ebd4cabd184eec2e7fee226e0c3`.

Verification: `not-run` — exercise a listed permitted operation with actual agent
credentials/run context; inspect its result and applicable persistence/attribution.
Assert the relevant denied actor, owner, company or mode from Policy. Review the
remaining operations before qualifying the whole capability. Local
[recovery route regressions](../../server/src/__tests__/issue-recovery-actions.test.ts)
verify one unchanged hold across reads and sweeps on done/cancelled tasks, no
physical copyback, and cleanup after the receipt is cleared. Exercise this
sequence in a disposable instance; automatic cleanup must use the system actor
and must not create reader participation. No live recovery proof is claimed.

Gaps: Need operation-level eligibility and a real native binding for permitted recovery
actions; do not route around lifecycle authority.

## `exhaustion`

Review: `baseline`.

API: `present` — representative operation IDs:

- `GET /api/issues/{id}/recovery-actions`.
- `GET /api/heartbeat-runs/{runId}`.

Agent access: `partial` — REST / native call_api reads; operator escalation flow.

Policy: Task/run visibility, run ownership and source/action policy; workspace export
retry and some operator controls require board.

Evidence: `source-only` — [implementation](../../server/src/routes/issues.ts#L9478) at
the reviewed commit above.

Verification: `not-run` — exercise a listed permitted operation with actual agent
credentials/run context; inspect its result and applicable persistence/attribution.
Assert the relevant denied actor, owner, company or mode from Policy. Review the
remaining operations before qualifying the whole capability.

Gaps: Reading exhaustion is supported. Continuing past the recorded gate requires the
specified owner/action.

## `workspace`

Review: `baseline`.

API: `present` — representative operation IDs:

- `POST /api/issues/{id}/recovery-actions/retry-workspace-export`.
- `POST /api/execution-workspaces/{id}/reconcile-branch`.

Agent access: `restricted` — Board/runtime management APIs; agent reads diagnosis and
performs permitted workspace work.

Policy: Task/run visibility, run ownership and source/action policy; workspace export
retry and some operator controls require board.

Evidence: `source-only` — [implementation](../../server/src/routes/issues.ts#L9478) at
the reviewed commit above.

Verification: `not-run` — assert the documented agent denial with an owned test fixture;
verify any listed agent request/result path separately. A delegated operation needs its
own policy and access review.

Gaps: Export retry/reconciliation APIs exist but require board. Native generic
execution-control mutations are also blocked.

## `unknown-outcome`

Review: `baseline`.

API: `present` — representative operation IDs:

- `POST /api/chat-endpoints/{endpointId}/publications/{publicationId}/resolve`.

Agent access: `restricted` — Board provider-outcome resolution; agent may inspect
assigned provider tools.

Policy: Task/run visibility, run ownership and source/action policy; workspace export
retry and some operator controls require board.

Evidence: `source-only` — [implementation](../../server/src/routes/issues.ts#L9478) at
the reviewed commit above.

Verification: `not-run` — assert the documented agent denial with an owned test fixture;
verify any listed agent request/result path separately. A delegated operation needs its
own policy and access review.

Gaps: Uncertain-side-effect resolution is operator/source-specific; do not replay to
obtain apparent parity.

## `user-continuation`

Review: `baseline`.

API: `present` — representative operation IDs:

- `POST /api/issues/{id}/comments`.

Agent access: `partial` — User comment API and server-owned wake reconsideration; native
agent consumes bound wake.

Policy: Task/run visibility, run ownership and source/action policy; workspace export
retry and some operator controls require board.

Evidence: `source-only` — [implementation](../../server/src/routes/issues.ts#L9478) at
the reviewed commit above.

Verification: `not-run` — exercise a listed permitted operation with actual agent
credentials/run context; inspect its result and applicable persistence/attribution.
Assert the relevant denied actor, owner, company or mode from Policy. Review the
remaining operations before qualifying the whole capability.

Gaps: Receiving the continuation is supported; impersonating a saved user message or
retry control is not.

## `reconnect`

Review: `baseline`.

API: `present` — representative operation IDs:

- `GET /api/companies/{companyId}/events/ws`.
- `GET /api/issues/{id}`.

Agent access: `partial` — Existing event protocol; REST refresh of persisted task state.

Policy: Task/run visibility, run ownership and source/action policy; workspace export
retry and some operator controls require board.

Evidence: `source-only` — [implementation](../../server/src/routes/issues.ts#L9478) at
the reviewed commit above.

Verification: `not-run` — exercise a listed permitted operation with actual agent
credentials/run context; inspect its result and applicable persistence/attribution.
Assert the relevant denied actor, owner, company or mode from Policy. Review the
remaining operations before qualifying the whole capability.

Gaps: Streaming reconnect needs its protocol client. Polling/read APIs remain available;
replay is not proof of a fresh successful action.
