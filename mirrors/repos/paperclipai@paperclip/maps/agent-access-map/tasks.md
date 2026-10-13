# Task creation and lifecycle — agent access

Product map: [Task creation and lifecycle](../feature-map/tasks.md).

Review date: 2026-10-12. Source commit: `f981fa3cc10cb8663a87dec60345fbff46d54d0a`.

This is a source-reviewed baseline of representative operations and known gaps.
Each capability needs operation-level review before its entire scope can be
qualified. No live agent execution is claimed. Follow the [map contract](../README.md)
for format, permission checks, evidence and maintenance.

## `create`

Review: `baseline`.

API: `present` — representative operation IDs:

- `POST /api/companies/{companyId}/issues`.

Agent access: `available` — Native create_task; REST / CLI / MCP.

Policy: Company/task visibility, assignment/change policy, active-run checkout ownership
and lifecycle rules.

Evidence: `source-only` — [implementation](../../server/src/routes/issues.ts) at the
reviewed commit above.

Verification: `not-run` — exercise a listed permitted operation with actual agent
credentials/run context; inspect its result and applicable persistence/attribution.
Assert the relevant denied actor, owner, company or mode from Policy. Review the
remaining operations before qualifying the whole capability.

Gaps: Creation is implemented; agent/user assignment and attachments may need
narrower/different APIs.

## `organize`

Review: `baseline`.

API: `present` — representative operation IDs:

- `GET /api/companies/{companyId}/issues`.

Agent access: `available` — Native search_tasks; REST / CLI; UI grouping/navigation
state separately.

Policy: Company/task visibility, assignment/change policy, active-run checkout ownership
and lifecycle rules.

Evidence: `source-only` — [implementation](../../server/src/routes/issues.ts) at the
reviewed commit above.

Verification: `not-run` — exercise a listed permitted operation with actual agent
credentials/run context; inspect its result and applicable persistence/attribution.
Assert the relevant denied actor, owner, company or mode from Policy. Review the
remaining operations before qualifying the whole capability.

Gaps: Search/filter API exists; sorting/grouping/presentation defaults are not
necessarily shared server preferences.

## `properties`

Review: `baseline`.

API: `present` — representative operation IDs:

- `PATCH /api/issues/{id}`.
- `PUT /api/issues/{id}/title`.

Agent access: `partial` — Native set_task_title/reassign_task/set_dependencies; fallback
for permitted non-lifecycle fields; REST.

Policy: Company/task visibility, assignment/change policy, active-run checkout ownership
and lifecycle rules.

Evidence: `source-only` — [implementation](../../server/src/routes/issues.ts) at the
reviewed commit above.

Verification: `not-run` — exercise a listed permitted operation with actual agent
credentials/run context; inspect its result and applicable persistence/attribution.
Assert the relevant denied actor, owner, company or mode from Policy. Review the
remaining operations before qualifying the whole capability.

Gaps: Native fallback blocks status/assignment/dependency policy fields. Dedicated tools
differ in scope and supported fields.

## `discussion`

Review: `baseline`.

API: `present` — representative operation IDs:

- `POST /api/issues/{id}/comments`.
- `POST /api/companies/{companyId}/issues/{issueId}/attachments`.

Agent access: `available` — Native report_progress/comment_on_task/register_deliverable;
REST / CLI / MCP.

Policy: Company/task visibility, assignment/change policy, active-run checkout ownership
and lifecycle rules.

Evidence: `source-only` — [implementation](../../server/src/routes/issues.ts) at the
reviewed commit above.

Verification: `not-run` — exercise a listed permitted operation with actual agent
credentials/run context; inspect its result and applicable persistence/attribution.
Assert the relevant denied actor, owner, company or mode from Policy. Review the
remaining operations before qualifying the whole capability.

Gaps: Other-task comments and active-task progress have separate scopes; explicit
reopen/interrupt is not a generic comment capability.

## `completion`

Review: `baseline`.

API: `present` — representative operation IDs:

- `PATCH /api/issues/{id}`.

Agent access: `available` — Native paperclip_finish/paperclip_block through runner
protocol; legacy agent REST disposition.

Policy: Company/task visibility, assignment/change policy, active-run checkout ownership
and lifecycle rules.

Evidence: `source-only` — [implementation](../../server/src/routes/issues.ts) at the
reviewed commit above.

Verification: `not-run` — exercise a listed permitted operation with actual agent
credentials/run context; inspect its result and applicable persistence/attribution.
Assert the relevant denied actor, owner, company or mode from Policy. Review the
remaining operations before qualifying the whole capability.

Gaps: Server governs whether a reported result becomes done/review/blocked. A generic
lifecycle PATCH is intentionally rejected for native runs.
