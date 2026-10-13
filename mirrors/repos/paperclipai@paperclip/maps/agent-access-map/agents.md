# Hiring, agent configuration, and organization — agent access

Product map: [Hiring, agent configuration, and organization](../feature-map/agents.md).

Review date: 2026-10-12. Source commit: `f981fa3cc10cb8663a87dec60345fbff46d54d0a`.

This is a source-reviewed baseline of representative operations and known gaps.
Each capability needs operation-level review before its entire scope can be
qualified. No live agent execution is claimed. Follow the [map contract](../README.md)
for format, permission checks, evidence and maintenance.

## `hire`

Review: `baseline`.

API: `present` — representative operation IDs:

- `POST /api/companies/{companyId}/agent-hires`.
- `POST /api/companies/{companyId}/agents`.

Agent access: `partial` — Native hire_agent; REST / CLI agent; runtime inheritance for
native hires.

Policy: Agent creation/configuration uses action grants, resource policies and change
consent; some controls require a board actor.

Evidence: `source-only` — [implementation](../../server/src/routes/agents.ts#L1395) at
the reviewed commit above.

Verification: `not-run` — exercise a listed permitted operation with actual agent
credentials/run context; inspect its result and applicable persistence/attribution.
Assert the relevant denied actor, owner, company or mode from Policy. Review the
remaining operations before qualifying the whole capability.

Gaps: Identity/persona hiring works. Operator account login and sensitive
adapter/environment configuration are separate guarded actions.

## `instructions`

Review: `baseline`.

API: `present` — representative operation IDs:

- `GET /api/agents/{id}/instructions-bundle/file`.
- `PUT /api/agents/{id}/instructions-bundle/file`.

Agent access: `available` — Native read/update/history/restore instruction tools; REST /
CLI.

Policy: Agent creation/configuration uses action grants, resource policies and change
consent; some controls require a board actor.

Evidence: `source-only` — [implementation](../../server/src/routes/agents.ts#L1395) at
the reviewed commit above.

Verification: `not-run` — exercise a listed permitted operation with actual agent
credentials/run context; inspect its result and applicable persistence/attribution.
Assert the relevant denied actor, owner, company or mode from Policy. Review the
remaining operations before qualifying the whole capability.

Gaps: Canonical entry file, revision guard, company boundary, and protected-change
policy apply.

## `organization`

Review: `baseline`.

API: `present` — representative operation IDs:

- `GET /api/companies/{companyId}/org`.
- `PATCH /api/agents/{id}`.

Agent access: `available` — list_agents/get_agent; native call_api for permitted
configuration fields; REST / CLI.

Policy: Agent creation/configuration uses action grants, resource policies and change
consent; some controls require a board actor.

Evidence: `source-only` — [implementation](../../server/src/routes/agents.ts#L1395) at
the reviewed commit above.

Verification: `not-run` — exercise a listed permitted operation with actual agent
credentials/run context; inspect its result and applicable persistence/attribution.
Assert the relevant denied actor, owner, company or mode from Policy. Review the
remaining operations before qualifying the whole capability.

Gaps: Reporting-line changes need configuration authorization; a title alone gives no
authority.

## `lifecycle`

Review: `baseline`.

API: `present` — representative operation IDs:

- `POST /api/agents/{id}/pause`.
- `POST /api/agents/{id}/resume`.
- `POST /api/agents/{id}/terminate`.

Agent access: `partial` — REST resume under change grant; pause/terminate require board;
native call_api blocks all three.

Policy: Agent creation/configuration uses action grants, resource policies and change
consent; some controls require a board actor.

Evidence: `source-only` — [implementation](../../server/src/routes/agents.ts#L1395) at
the reviewed commit above.

Verification: `not-run` — exercise a listed permitted operation with actual agent
credentials/run context; inspect its result and applicable persistence/attribution.
Assert the relevant denied actor, owner, company or mode from Policy. Review the
remaining operations before qualifying the whole capability.

Gaps: Resume is agent-eligible but lacks a default native binding. Pause and termination
are actor-boundary decisions.

## `built-in`

Review: `baseline`.

API: `present` — representative operation IDs:

- `POST /api/companies/{companyId}/built-in-agents/{key}/provision`.

Agent access: `partial` — REST / native fallback for eligible provisioning; built-in
routine controls require board.

Policy: Agent creation/configuration uses action grants, resource policies and change
consent; some controls require a board actor.

Evidence: `source-only` — [implementation](../../server/src/routes/agents.ts#L1395) at
the reviewed commit above.

Verification: `not-run` — exercise a listed permitted operation with actual agent
credentials/run context; inspect its result and applicable persistence/attribution.
Assert the relevant denied actor, owner, company or mode from Policy. Review the
remaining operations before qualifying the whole capability.

Gaps: Provisioning checks agents:create. Enabling/running its built-in routine is not
the same permission path.
