# External chat and email conversations — agent access

Product map: [External chat and email conversations](../feature-map/chat-channels.md).

Review date: 2026-10-12. Source commit: `f981fa3cc10cb8663a87dec60345fbff46d54d0a`.

This is a source-reviewed baseline of representative operations and known gaps.
Each capability needs operation-level review before its entire scope can be
qualified. No live agent execution is claimed. Follow the [map contract](../README.md)
for format, permission checks, evidence and maintenance.

## `providers`

Review: `baseline`.

API: `present` — representative operation IDs:

- `POST /api/companies/{companyId}/chat-endpoints`.

Agent access: `restricted` — Board setup APIs; native connection request can ask for
setup.

Policy: Endpoint management/identity linking requires a board user; delivery is
server-owned and agent tools use scoped assignments.

Evidence: `source-only` — [implementation](../../server/src/routes/chat-channels.ts#L75)
at the reviewed commit above.

Verification: `not-run` — assert the documented agent denial with an owned test fixture;
verify any listed agent request/result path separately. A delegated operation needs its
own policy and access review.

Gaps: Provider installation and account enrollment are not available to an ordinary
agent actor.

## `identity`

Review: `baseline`.

API: `present` — representative operation IDs:

- `POST /api/chat-identity-links/confirm`.

Agent access: `restricted` — Human identity-link flow.

Policy: Endpoint management/identity linking requires a board user; delivery is
server-owned and agent tools use scoped assignments.

Evidence: `source-only` — [implementation](../../server/src/routes/chat-channels.ts#L75)
at the reviewed commit above.

Verification: `not-run` — assert the documented agent denial with an owned test fixture;
verify any listed agent request/result path separately. A delegated operation needs its
own policy and access review.

Gaps: No impersonation path; native call_api additionally blocks identity-link
operations.

## `conversation`

Review: `baseline`.

API: `present` — representative operation IDs:

- `POST /api/chat-endpoints/{endpointId}/conversations/{conversationId}/publications`.

Agent access: `partial` — Assigned-agent reply pipeline; native completion; provider
tools where assigned.

Policy: Endpoint management/identity linking requires a board user; delivery is
server-owned and agent tools use scoped assignments.

Evidence: `source-only` — [implementation](../../server/src/routes/chat-channels.ts#L75)
at the reviewed commit above.

Verification: `not-run` — exercise a listed permitted operation with actual agent
credentials/run context; inspect its result and applicable persistence/attribution.
Assert the relevant denied actor, owner, company or mode from Policy. Review the
remaining operations before qualifying the whole capability.

Gaps: Normal agent replies work through server delivery. Explicit endpoint publication
APIs are board management paths.

New conversations resolve typed project/workspace defaults from their endpoint
and destination under the task-creation transaction. Defaults do not authorize
private sources: admission checks the linked user's authority and assigned agent.
An existing conversation keeps its task binding. See
[creation service](../../server/src/services/chat-channels.ts) and
[defaults contract](../../packages/shared/src/types/chat-channels.ts).

## `attachments`

Review: `baseline`.

API: `present` — representative operation IDs:

- `GET /api/issues/{id}/attachments`.
- `POST /api/companies/{companyId}/issues/{issueId}/attachments`.

Agent access: `partial` — Native register_deliverable / attachment tools when admitted;
agent REST; server-owned delivery.

Policy: Endpoint management/identity linking requires a board user; delivery is
server-owned and agent tools use scoped assignments.

Evidence: `source-only` — [implementation](../../server/src/routes/chat-channels.ts#L75)
at the reviewed commit above.

Verification: `not-run` — exercise a listed permitted operation with actual agent
credentials/run context; inspect its result and applicable persistence/attribution.
Assert the relevant denied actor, owner, company or mode from Policy. Review the
remaining operations before qualifying the whole capability.

Gaps: Uploading/registering is supported. Provider delivery status and board replay are
separate operations.

## `lifecycle`

Review: `baseline`.

API: `present` — representative operation IDs:

- `GET /api/chat-endpoints/{endpointId}/activity`.
- `PATCH /api/chat-endpoints/{endpointId}`.
- `PUT /api/chat-endpoints/{endpointId}/resources` configures destination defaults.

Agent access: `restricted` — Board lifecycle APIs; agent requests repair when blocked.

Policy: Endpoint management/identity linking requires a board user; delivery is
server-owned and agent tools use scoped assignments.

Evidence: `source-only` — [implementation](../../server/src/routes/chat-channels.ts#L75)
at the reviewed commit above.

Verification: `not-run` — assert the documented agent denial with an owned test fixture;
verify any listed agent request/result path separately. A delegated operation needs its
own policy and access review.

Gaps: Activity/repair/replay/disable use board endpoint access, not the agent's ability
to reply.

Endpoint/destination execution defaults use the same board-only management
boundary. Agents select an authorized workspace for their current task through
the [workspace APIs](workspaces.md), rather than editing channel configuration.
