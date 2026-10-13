# Skill discovery, authoring, and policy — agent access

Product map: [Skill discovery, authoring, and policy](../feature-map/skills.md).

Review date: 2026-10-12. Source commit: `f981fa3cc10cb8663a87dec60345fbff46d54d0a`.

This is a source-reviewed baseline of representative operations and known gaps.
Each capability needs operation-level review before its entire scope can be
qualified. No live agent execution is claimed. Follow the [map contract](../README.md)
for format, permission checks, evidence and maintenance.

## `discovery`

Review: `baseline`.

API: `present` — representative operation IDs:

- `GET /api/companies/{companyId}/skills`.
- `POST /api/companies/{companyId}/skills/import`.

Agent access: `available` — REST / native call_api / CLI skills and sources.

Policy: Company skill policy by action/resource plus platform invariants; test execution
additionally requires task-assignment authority.

Evidence: `source-only` —
[implementation](../../server/src/routes/company-skills.ts#L208) at the reviewed commit
above.

Verification: `not-run` — exercise a listed permitted operation with actual agent
credentials/run context; inspect its result and applicable persistence/attribution.
Assert the relevant denied actor, owner, company or mode from Policy. Review the
remaining operations before qualifying the whole capability.

Gaps: Installation/import is governed by company skill policy, not inferred from an
agent's role name.

## `authoring`

Review: `baseline`.

API: `present` — representative operation IDs:

- `POST /api/companies/{companyId}/skills`.
- `PATCH /api/companies/{companyId}/skills/{skillId}/files`.

Agent access: `available` — Native create_skill/update_skill for single-file operations;
REST for other files/metadata.

Policy: Company skill policy by action/resource plus platform invariants; test execution
additionally requires task-assignment authority.

Evidence: `source-only` —
[implementation](../../server/src/routes/company-skills.ts#L208) at the reviewed commit
above.

Verification: `not-run` — exercise a listed permitted operation with actual agent
credentials/run context; inspect its result and applicable persistence/attribution.
Assert the relevant denied actor, owner, company or mode from Policy. Review the
remaining operations before qualifying the whole capability.

Gaps: Writable/fork policy and expected version apply. Native helpers intentionally
support a narrower shape than full API.

## `versions`

Review: `baseline`.

API: `present` — representative operation IDs:

- `GET /api/companies/{companyId}/skills/{skillId}/versions`.

Agent access: `available` — REST / native call_api / CLI skills.

Policy: Company skill policy by action/resource plus platform invariants; test execution
additionally requires task-assignment authority.

Evidence: `source-only` —
[implementation](../../server/src/routes/company-skills.ts#L208) at the reviewed commit
above.

Verification: `not-run` — exercise a listed permitted operation with actual agent
credentials/run context; inspect its result and applicable persistence/attribution.
Assert the relevant denied actor, owner, company or mode from Policy. Review the
remaining operations before qualifying the whole capability.

Gaps: Revision metadata has an API; pinned execution skill versions and installed latest
are distinct.

## `policy`

Review: `baseline`.

API: `present` — representative operation IDs:

- `PUT /api/companies/{companyId}/skill-policy`.
- `POST /api/agents/{id}/skills/sync`.

Agent access: `partial` — REST / native call_api under users:manage_permissions or
target configuration policy.

Policy: Company skill policy by action/resource plus platform invariants; test execution
additionally requires task-assignment authority.

Evidence: `source-only` —
[implementation](../../server/src/routes/company-skills.ts#L208) at the reviewed commit
above.

Verification: `not-run` — exercise a listed permitted operation with actual agent
credentials/run context; inspect its result and applicable persistence/attribution.
Assert the relevant denied actor, owner, company or mode from Policy. Review the
remaining operations before qualifying the whole capability.

Gaps: Policy administration has an explicit agent grant branch; assigning agent skills
also checks the target's config authority.

## `testing`

Review: `baseline`.

API: `present` — representative operation IDs:

- `POST /api/companies/{companyId}/skills/{skillId}/test-runs`.

Agent access: `partial` — Permitted agent REST; native read fallback for history; no
dedicated CLI test command found.

Policy: Company skill policy by action/resource plus platform invariants; test execution
additionally requires task-assignment authority.

Evidence: `source-only` —
[implementation](../../server/src/routes/company-skills.ts#L208) at the reviewed commit
above.

Verification: `not-run` — exercise a listed permitted operation with actual agent
credentials/run context; inspect its result and applicable persistence/attribution.
Assert the relevant denied actor, owner, company or mode from Policy. Review the
remaining operations before qualifying the whole capability.

Gaps: Native call_api rejects test-run creation/control while the route can authorize
agents. No default native orchestration binding.
