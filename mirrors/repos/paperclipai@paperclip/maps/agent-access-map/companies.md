# Companies and portability — agent access

Product map: [Companies and portability](../feature-map/companies.md).

Review date: 2026-10-12. Source commit: `f981fa3cc10cb8663a87dec60345fbff46d54d0a`.

This is a source-reviewed baseline of representative operations and known gaps.
Each capability needs operation-level review before its entire scope can be
qualified. No live agent execution is claimed. Follow the [map contract](../README.md)
for format, permission checks, evidence and maintenance.

## `selection`

Review: `baseline`.

API: `present` — representative operation IDs:

- `GET /api/companies/{companyId}`.
- `GET /api/companies`.
- `POST /api/companies`.

Agent access: `partial` — Agent reads its bound company; CLI context chooses it; board
lists/creates companies.

Policy: Same-company CEO or board for identity/import operations; list/create/archive
convenience endpoint is board-gated.

Evidence: `source-only` — [implementation](../../server/src/routes/companies.ts#L1245)
at the reviewed commit above.

Verification: `not-run` — exercise a listed permitted operation with actual agent
credentials/run context; inspect its result and applicable persistence/attribution.
Assert the relevant denied actor, owner, company or mode from Policy. Review the
remaining operations before qualifying the whole capability.

Gaps: A worker cannot enumerate/create companies via its company agent key. Browser
selection is local state.

## `identity`

Review: `baseline`.

API: `present` — representative operation IDs:

- `PATCH /api/companies/{companyId}`.
- `PATCH /api/companies/{companyId}/branding`.

Agent access: `available` — Same-company CEO REST / native call_api / CLI company.

Policy: Same-company CEO or board for identity/import operations; list/create/archive
convenience endpoint is board-gated.

Evidence: `source-only` — [implementation](../../server/src/routes/companies.ts#L1245)
at the reviewed commit above.

Verification: `not-run` — exercise a listed permitted operation with actual agent
credentials/run context; inspect its result and applicable persistence/attribution.
Assert the relevant denied actor, owner, company or mode from Policy. Review the
remaining operations before qualifying the whole capability.

Gaps: The CEO restriction is a real policy, not a missing API; ordinary employees need
denial evidence.

## `archive`

Review: `baseline`.

API: `present` — representative operation IDs:

- `POST /api/companies/{companyId}/archive`.
- `PATCH /api/companies/{companyId}`.

Agent access: `partial` — Board archive endpoint; CEO company PATCH can express status
changes.

Policy: Same-company CEO or board for identity/import operations; list/create/archive
convenience endpoint is board-gated.

Evidence: `source-only` — [implementation](../../server/src/routes/companies.ts#L1245)
at the reviewed commit above.

Verification: `not-run` — exercise a listed permitted operation with actual agent
credentials/run context; inspect its result and applicable persistence/attribution.
Assert the relevant denied actor, owner, company or mode from Policy. Review the
remaining operations before qualifying the whole capability.

Gaps: Convenience archive and general company PATCH have different authorization. Review
equivalence rather than declaring all archival human-only.

## `portability`

Review: `baseline`.

API: `present` — representative operation IDs:

- `POST /api/companies/{companyId}/exports`.
- `POST /api/companies/{companyId}/imports/preview`.
- `POST /api/companies/{companyId}/imports/apply`.

Agent access: `partial` — CEO REST / CLI company; native export restricted, eligible
same-company import uses fallback.

Policy: Same-company CEO or board for identity/import operations; list/create/archive
convenience endpoint is board-gated.

Evidence: `source-only` — [implementation](../../server/src/routes/companies.ts#L1245)
at the reviewed commit above.

Verification: `not-run` — exercise a listed permitted operation with actual agent
credentials/run context; inspect its result and applicable persistence/attribution.
Assert the relevant denied actor, owner, company or mode from Policy. Review the
remaining operations before qualifying the whole capability.

Gaps: Secure exports lack a default native binding; new-company/ZIP import flows have
different board and transport constraints.
