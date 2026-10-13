# Local, SSH, and sandbox environments — agent access

Product map: [Local, SSH, and sandbox
environments](../feature-map/execution-environments.md).

Review date: 2026-10-12. Source commit: `f981fa3cc10cb8663a87dec60345fbff46d54d0a`.

This is a source-reviewed baseline of representative operations and known gaps.
Each capability needs operation-level review before its entire scope can be
qualified. No live agent execution is claimed. Follow the [map contract](../README.md)
for format, permission checks, evidence and maintenance.

## `configuration`

Review: `baseline`.

API: `present` — representative operation IDs:

- `GET /api/companies/{companyId}/environments`.
- `POST /api/companies/{companyId}/environments`.

Agent access: `restricted` — Board read/admin management REST / CLI environment.

Policy: Environment management is instance administrator/board; permitted assignment
uses agent/project policy.

Evidence: `source-only` — [implementation](../../server/src/routes/environments.ts#L353)
at the reviewed commit above.

Verification: `not-run` — assert the documented agent denial with an owned test fixture;
verify any listed agent request/result path separately. A delegated operation needs its
own policy and access review.

Gaps: API exists; an agent cannot use instance environment management as an ordinary
company actor.

## `capabilities`

Review: `baseline`.

API: `present` — representative operation IDs:

- `GET /api/companies/{companyId}/environments/capabilities`.

Agent access: `partial` — Board environment capabilities endpoint; native run gets
server-selected runtime context.

Policy: Environment management is instance administrator/board; permitted assignment
uses agent/project policy.

Evidence: `source-only` — [implementation](../../server/src/routes/environments.ts#L353)
at the reviewed commit above.

Verification: `not-run` — exercise a listed permitted operation with actual agent
credentials/run context; inspect its result and applicable persistence/attribution.
Assert the relevant denied actor, owner, company or mode from Policy. Review the
remaining operations before qualifying the whole capability.

Gaps: Endpoint discovery and already-bound run capabilities differ; decide whether a
safe agent-readable capability listing is desired.

## `probe`

Review: `baseline`.

API: `present` — representative operation IDs:

- `POST /api/environments/{id}/probe`.
- `POST /api/companies/{companyId}/environments/probe-config`.

Agent access: `restricted` — Board/admin probes / CLI environment.

Policy: Environment management is instance administrator/board; permitted assignment
uses agent/project policy.

Evidence: `source-only` — [implementation](../../server/src/routes/environments.ts#L353)
at the reviewed commit above.

Verification: `not-run` — assert the documented agent denial with an owned test fixture;
verify any listed agent request/result path separately. A delegated operation needs its
own policy and access review.

Gaps: Reachability probes are not granted by an agent's right to execute assigned work.

## `assignment`

Review: `baseline`.

API: `present` — representative operation IDs:

- `PATCH /api/agents/{id}`.
- `PATCH /api/projects/{id}`.

Agent access: `partial` — Permitted agent/project REST / native fallback, subject to
protected configuration policy.

Policy: Environment management is instance administrator/board; permitted assignment
uses agent/project policy.

Evidence: `source-only` — [implementation](../../server/src/routes/environments.ts#L353)
at the reviewed commit above.

Verification: `not-run` — exercise a listed permitted operation with actual agent
credentials/run context; inspect its result and applicable persistence/attribution.
Assert the relevant denied actor, owner, company or mode from Policy. Review the
remaining operations before qualifying the whole capability.

Gaps: Choosing among permitted targets differs from creating/configuring host targets;
test authorized and denied selection.

## `images`

Review: `baseline`.

API: `present` — representative operation IDs:

- `POST /api/environments/{environmentId}/custom-image-setup-sessions`.

Agent access: `restricted` — Board/admin image APIs and existing terminal protocol.

Policy: Environment management is instance administrator/board; permitted assignment
uses agent/project policy.

Evidence: `source-only` — [implementation](../../server/src/routes/environments.ts#L353)
at the reviewed commit above.

Verification: `not-run` — assert the documented agent denial with an owned test fixture;
verify any listed agent request/result path separately. A delegated operation needs its
own policy and access review.

Gaps: No default agent custom-image administration/terminal path; this is a policy
decision before adding a tool.
