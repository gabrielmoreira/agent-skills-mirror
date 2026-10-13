# Delegation, dependencies, and signoff — agent access

Product map: [Delegation, dependencies, and
signoff](../feature-map/task-coordination.md).

Review date: 2026-10-12. Source commit: `f981fa3cc10cb8663a87dec60345fbff46d54d0a`.

This is a source-reviewed baseline of representative operations and known gaps.
Each capability needs operation-level review before its entire scope can be
qualified. No live agent execution is claimed. Follow the [map contract](../README.md)
for format, permission checks, evidence and maintenance.

## `delegation`

Review: `baseline`.

API: `present` — representative operation IDs:

- `POST /api/companies/{companyId}/issues`.

Agent access: `available` — Native create_task/reassign_task; REST / CLI / MCP.

Policy: Task visibility/mutation, task-assignment and ownership policy; review audience
independent; tree controls board-only.

Evidence: `source-only` —
[implementation](../../server/src/routes/issue-tree-control.ts#L95) at the reviewed
commit above.

Verification: `not-run` — exercise a listed permitted operation with actual agent
credentials/run context; inspect its result and applicable persistence/attribution.
Assert the relevant denied actor, owner, company or mode from Policy. Review the
remaining operations before qualifying the whole capability.

Gaps: Parent/child and provenance paths exist; same-company assignment does not remove
protected task/resource policy.

## `dependencies`

Review: `baseline`.

API: `present` — representative operation IDs:

- `PATCH /api/issues/{id}`.

Agent access: `available` — Native set_dependencies for current task; agent REST under
mutation/checkout policy.

Policy: Task visibility/mutation, task-assignment and ownership policy; review audience
independent; tree controls board-only.

Evidence: `source-only` —
[implementation](../../server/src/routes/issue-tree-control.ts#L95) at the reviewed
commit above.

Verification: `not-run` — exercise a listed permitted operation with actual agent
credentials/run context; inspect its result and applicable persistence/attribution.
Assert the relevant denied actor, owner, company or mode from Policy. Review the
remaining operations before qualifying the whole capability.

Gaps: Generic native PATCH rejects blockedByIssueIds so use its real dedicated tool.

## `signoff`

Review: `baseline`.

API: `present` — representative operation IDs:

- `PATCH /api/issues/{id}`.
- `POST /api/issues/{id}/interactions`.

Agent access: `partial` — Native paperclip_finish/paperclip_block and assigned
resolve_review; legacy agent REST disposition.

Policy: Task visibility/mutation, task-assignment and ownership policy; review audience
independent; tree controls board-only.

Evidence: `source-only` —
[implementation](../../server/src/routes/issue-tree-control.ts#L95) at the reviewed
commit above.

Verification: `not-run` — exercise a listed permitted operation with actual agent
credentials/run context; inspect its result and applicable persistence/attribution.
Assert the relevant denied actor, owner, company or mode from Policy. Review the
remaining operations before qualifying the whole capability.

Gaps: Review policy determines final completion; formal board approval is a different
boundary.

## `tree-control`

Review: `baseline`.

API: `present` — representative operation IDs:

- `POST /api/issues/{id}/tree-control/preview`.
- `POST /api/issues/{id}/tree-holds`.
- `POST /api/issues/{id}/tree-holds/{holdId}/release`.

Agent access: `restricted` — Board-only task-tree APIs.

Policy: Task visibility/mutation, task-assignment and ownership policy; review audience
independent; tree controls board-only.

Evidence: `source-only` —
[implementation](../../server/src/routes/issue-tree-control.ts#L95) at the reviewed
commit above.

Verification: `not-run` — assert the documented agent denial with an owned test fixture;
verify any listed agent request/result path separately. A delegated operation needs its
own policy and access review.

Gaps: Even reads/state/preview require board. There is no agent tree-control path just
from company/task permissions.
