# Inbox, decisions, and search — agent access

Product map: [Inbox, decisions, and search](../feature-map/inbox-search.md).

Review date: 2026-10-12. Source commit: `f981fa3cc10cb8663a87dec60345fbff46d54d0a`.

This is a source-reviewed baseline of representative operations and known gaps.
Each capability needs operation-level review before its entire scope can be
qualified. No live agent execution is claimed. Follow the [map contract](../README.md)
for format, permission checks, evidence and maintenance.

## `views`

Review: `baseline`.

API: `present` — representative operation IDs:

- `GET /api/agents/me/inbox-lite`.
- `GET /api/agents/me/inbox/mine`.
- `GET /api/companies/{companyId}/issues`.

Agent access: `partial` — REST / native call_api; MCP inbox/task search.

Policy: Own agent context; responsible-user inbox policy and explicit opt-in/grants for
cross-user archive; decision policy separately. Automatic read cleanup does not
count as user participation, including historical reader-attributed rows.
Explicit user recovery decisions still count.

Evidence: `source-only` — [implementation](../../server/src/routes/agents.ts#L3952) at
the reviewed commit above. The cleanup exclusion in
[issue queries](../../server/src/services/issues.ts) was reviewed at
`89770ba707fb1ebd4cabd184eec2e7fee226e0c3`.
[Issue service regressions](../../server/src/__tests__/issues-service.test.ts)
cover membership, unread counts, timestamps, and retained audit rows.

Verification: `not-run` — exercise a listed permitted operation with actual agent
credentials/run context; inspect its result and applicable persistence/attribution.
Assert the relevant denied actor, owner, company or mode from Policy. Review the
remaining operations before qualifying the whole capability. Seed a completed
issue with only automatic read cleanup under a user identity: Mine and Unread
must exclude it while activity history retains the row. An explicit recovery
decision must still establish participation. No live user-inbox proof is claimed.

Gaps: Agent inbox and Mine support exist; board attention/unread/dismissal aggregation
is a separate user-only surface.

## `triage`

Review: `baseline`.

API: `present` — representative operation IDs:

- `POST /api/issues/{id}/inbox-archive`.
- `DELETE /api/issues/{id}/inbox-archive`.

Agent access: `partial` — REST / native call_api; existing garden-inbox workflow.

Policy: Own agent context; responsible-user inbox policy and explicit opt-in/grants for
cross-user archive; decision policy separately.

Evidence: `source-only` — [implementation](../../server/src/routes/agents.ts#L3952) at
the reviewed commit above.

Verification: `not-run` — exercise a listed permitted operation with actual agent
credentials/run context; inspect its result and applicable persistence/attribution.
Assert the relevant denied actor, owner, company or mode from Policy. Review the
remaining operations before qualifying the whole capability.

Gaps: Archive has an agent-aware responsible-user policy. Personal read/unread/dismissal
does not have equivalent agent semantics everywhere.

## `decisions`

Review: `baseline`.

API: `present` — representative operation IDs:

- `GET /api/companies/{companyId}/decision-queues`.
- `GET /api/companies/{companyId}/decision-queues/{key}/items`.

Agent access: `partial` — REST / native call_api under decision queue authorization.

Policy: Own agent context; responsible-user inbox policy and explicit opt-in/grants for
cross-user archive; decision policy separately.

Evidence: `source-only` — [implementation](../../server/src/routes/agents.ts#L3952) at
the reviewed commit above.

Verification: `not-run` — exercise a listed permitted operation with actual agent
credentials/run context; inspect its result and applicable persistence/attribution.
Assert the relevant denied actor, owner, company or mode from Policy. Review the
remaining operations before qualifying the whole capability.

Gaps: Queue browsing/managing may be allowed; governed approval decisions still have
separate board/resolver boundaries.

## `search`

Review: `baseline`.

API: `present` — representative operation IDs:

- `GET /api/companies/{companyId}/search`.
- `GET /api/companies/{companyId}/issues`.

Agent access: `available` — Native search_tasks for tasks; REST / native call_api for
broader search.

Policy: Own agent context; responsible-user inbox policy and explicit opt-in/grants for
cross-user archive; decision policy separately.

Evidence: `source-only` — [implementation](../../server/src/routes/agents.ts#L3952) at
the reviewed commit above.

Verification: `not-run` — exercise a listed permitted operation with actual agent
credentials/run context; inspect its result and applicable persistence/attribution.
Assert the relevant denied actor, owner, company or mode from Policy. Review the
remaining operations before qualifying the whole capability.

Gaps: General company search and dedicated task search are different result sets; use
the appropriate one.
