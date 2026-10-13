# Routines, schedules, and triggers — agent access

Product map: [Routines, schedules, and triggers](../feature-map/routines.md).

Review date: 2026-10-12. Source commit: `f981fa3cc10cb8663a87dec60345fbff46d54d0a`.

This is a source-reviewed baseline of representative operations and known gaps.
Each capability needs operation-level review before its entire scope can be
qualified. No live agent execution is claimed. Follow the [map contract](../README.md)
for format, permission checks, evidence and maintenance.

## `definition`

Review: `baseline`.

API: `present` — representative operation IDs:

- `POST /api/companies/{companyId}/routines`.
- `PATCH /api/routines/{id}`.

Agent access: `partial` — Agent REST / CLI routine create/update; optional installed MCP
generic request.

Policy: Agents may read company routines but only create/manage routines assigned to
themselves; trigger secrets need secure handling.

Evidence: `source-only` — [implementation](../../server/src/routes/routines.ts#L99) at
the reviewed commit above.

Verification: `not-run` — exercise a listed permitted operation with actual agent
credentials/run context; inspect its result and applicable persistence/attribution.
Assert the relevant denied actor, owner, company or mode from Policy. Review the
remaining operations before qualifying the whole capability.

Gaps: Native call_api rejects routine mutation; manage_routine is scenario-only/unbound.
Agent REST is implemented.

## `triggers`

Review: `baseline`.

API: `present` — representative operation IDs:

- `POST /api/routines/{id}/triggers`.
- `PATCH /api/routine-triggers/{id}`.

Agent access: `partial` — Owned-routine agent REST / CLI routine trigger commands.

Policy: Agents may read company routines but only create/manage routines assigned to
themselves; trigger secrets need secure handling.

Evidence: `source-only` — [implementation](../../server/src/routes/routines.ts#L99) at
the reviewed commit above.

Verification: `not-run` — exercise a listed permitted operation with actual agent
credentials/run context; inspect its result and applicable persistence/attribution.
Assert the relevant denied actor, owner, company or mode from Policy. Review the
remaining operations before qualifying the whole capability.

Gaps: No production default native trigger-management binding. Webhook creation/rotation
also returns credential material.

## `run-now`

Review: `baseline`.

API: `present` — representative operation IDs:

- `POST /api/routines/{id}/run`.

Agent access: `partial` — Owned-routine agent REST / CLI routine run.

Policy: Agents may read company routines but only create/manage routines assigned to
themselves; trigger secrets need secure handling.

Evidence: `source-only` — [implementation](../../server/src/routes/routines.ts#L99) at
the reviewed commit above.

Verification: `not-run` — exercise a listed permitted operation with actual agent
credentials/run context; inspect its result and applicable persistence/attribution.
Assert the relevant denied actor, owner, company or mode from Policy. Review the
remaining operations before qualifying the whole capability.

Gaps: A scheduled/waiting native agent cannot use call_api for this eligible operation;
a real control binding is missing.

## `history`

Review: `baseline`.

API: `present` — representative operation IDs:

- `GET /api/routines/{id}/runs`.
- `GET /api/routines/{id}/revisions`.

Agent access: `available` — REST / native call_api / CLI routine.

Policy: Agents may read company routines but only create/manage routines assigned to
themselves; trigger secrets need secure handling.

Evidence: `source-only` — [implementation](../../server/src/routes/routines.ts#L99) at
the reviewed commit above.

Verification: `not-run` — exercise a listed permitted operation with actual agent
credentials/run context; inspect its result and applicable persistence/attribution.
Assert the relevant denied actor, owner, company or mode from Policy. Review the
remaining operations before qualifying the whole capability.

Gaps: Runs are readable in company scope; configuration revision access checks routine
ownership for agents.

## `management`

Review: `baseline`.

API: `present` — representative operation IDs:

- `PATCH /api/routines/{id}`.

Agent access: `partial` — Owned-routine agent REST / CLI; normal native fallback can
manage separate folder metadata where permitted.

Policy: Agents may read company routines but only create/manage routines assigned to
themselves; trigger secrets need secure handling.

Evidence: `source-only` — [implementation](../../server/src/routes/routines.ts#L99) at
the reviewed commit above.

Verification: `not-run` — exercise a listed permitted operation with actual agent
credentials/run context; inspect its result and applicable persistence/attribution.
Assert the relevant denied actor, owner, company or mode from Policy. Review the
remaining operations before qualifying the whole capability.

Gaps: Pause/archive routine mutation lacks a production native binding. Plugin-managed
routine rules remain separate.
