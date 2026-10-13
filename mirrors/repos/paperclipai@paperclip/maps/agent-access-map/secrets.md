# Secrets, personal credentials, and proposals — agent access

Product map: [Secrets, personal credentials, and proposals](../feature-map/secrets.md).

Review date: 2026-10-12. Source commit: `f981fa3cc10cb8663a87dec60345fbff46d54d0a`.

This is a source-reviewed baseline of representative operations and known gaps.
Each capability needs operation-level review before its entire scope can be
qualified. No live agent execution is claimed. Follow the [map contract](../README.md)
for format, permission checks, evidence and maintenance.

## `company-secrets`

Review: `baseline`.

API: `present` — representative operation IDs:

- `GET /api/companies/{companyId}/secrets/catalog`.
- `POST /api/companies/{companyId}/secrets`.

Agent access: `partial` — Agent metadata catalog; board secret administration; agent
secret proposal API.

Policy: Board secret administration, active-run/self/report proposal policy, and scoped
secret broker bindings; personal secret values belong to their user.

Evidence: `source-only` — [implementation](../../server/src/routes/secrets.ts#L194) at
the reviewed commit above.

Verification: `not-run` — exercise a listed permitted operation with actual agent
credentials/run context; inspect its result and applicable persistence/attribution.
Assert the relevant denied actor, owner, company or mode from Policy. Review the
remaining operations before qualifying the whole capability.

Gaps: Metadata and requesting a change exist; generic native API blocks secret
management/value transport.

## `user-secrets`

Review: `baseline`.

API: `present` — representative operation IDs:

- `GET /api/companies/{companyId}/me/user-secrets`.
- `POST /api/companies/{companyId}/me/user-secrets`.

Agent access: `restricted` — Current board user's personal-secret API; agent receives
only authorized run binding.

Policy: Board secret administration, active-run/self/report proposal policy, and scoped
secret broker bindings; personal secret values belong to their user.

Evidence: `source-only` — [implementation](../../server/src/routes/secrets.ts#L194) at
the reviewed commit above.

Verification: `not-run` — assert the documented agent denial with an owned test fixture;
verify any listed agent request/result path separately. A delegated operation needs its
own policy and access review.

Gaps: Agent cannot edit a person's private credential value through their ordinary agent
key.

## `proposals`

Review: `baseline`.

API: `present` — representative operation IDs:

- `POST /api/agents/me/secret-proposals`.
- `GET /api/agents/me/secret-proposals`.

Agent access: `partial` — Active-run agent REST with redaction; board
approval/rejection.

Policy: Board secret administration, active-run/self/report proposal policy, and scoped
secret broker bindings; personal secret values belong to their user.

Evidence: `source-only` — [implementation](../../server/src/routes/secrets.ts#L194) at
the reviewed commit above.

Verification: `not-run` — exercise a listed permitted operation with actual agent
credentials/run context; inspect its result and applicable persistence/attribution.
Assert the relevant denied actor, owner, company or mode from Policy. Review the
remaining operations before qualifying the whole capability.

Gaps: Native call_api blocks secret-proposals and no dedicated production proposal tool
is in its default authority set.

## `vault-import`

Review: `baseline`.

API: `present` — representative operation IDs:

- `POST /api/companies/{companyId}/secrets/remote-import/preview`.
- `POST /api/companies/{companyId}/secrets/remote-import`.

Agent access: `restricted` — Board authorized vault import API / CLI provider
operations.

Policy: Board secret administration, active-run/self/report proposal policy, and scoped
secret broker bindings; personal secret values belong to their user.

Evidence: `source-only` — [implementation](../../server/src/routes/secrets.ts#L194) at
the reviewed commit above.

Verification: `not-run` — assert the documented agent denial with an owned test fixture;
verify any listed agent request/result path separately. A delegated operation needs its
own policy and access review.

Gaps: Vault import is not implied by having a secret binding or the ability to propose a
secret.

## `runtime-delivery`

Review: `baseline`.

API: `present` — representative operation IDs:

- `GET /api/agents/me/secrets`.
- `POST /api/agents/me/secrets/{key}/value`.

Agent access: `partial` — Authorized environment/broker delivery; eligible legacy agent
REST access.

Policy: Board secret administration, active-run/self/report proposal policy, and scoped
secret broker bindings; personal secret values belong to their user.

Evidence: `source-only` — [implementation](../../server/src/routes/secrets.ts#L194) at
the reviewed commit above.

Verification: `not-run` — exercise a listed permitted operation with actual agent
credentials/run context; inspect its result and applicable persistence/attribution.
Assert the relevant denied actor, owner, company or mode from Policy. Review the
remaining operations before qualifying the whole capability.

Gaps: Native metadata reads exist; value call is blocked and scenario read_secret_value
is unbound. Do not add raw secret-returning fallback tools.
