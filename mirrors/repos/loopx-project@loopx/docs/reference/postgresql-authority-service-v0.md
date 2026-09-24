# PostgreSQL authority service admission v0

This document defines the service-owned admission boundary for the switchable
PostgreSQL authority provider. It is an opt-in Stage 2B seam: it does not make
PostgreSQL the default, change file/SQLite selection, add a runtime caller, or
claim promotion readiness.

## Boundary

`PostgreSqlAuthorityService` receives an opaque transport credential, a tenant,
a goal, and the expected database-incarnation identity. It calls injected
authentication and tenant-authorization functions before opening the provider.
The credential is never persisted, passed to PostgreSQL, or exposed through the
provider-neutral `AuthorityStore` contract. A denied or unverifiable principal
fails closed before a database connection is opened.

The service returns one of these typed outcomes:

| Outcome | Meaning |
| --- | --- |
| `opened` | The principal is authenticated, authorized for the tenant, and the database identity matches the requested binding. |
| `principal_unauthenticated` | Authentication rejected the opaque credential or returned an invalid principal. |
| `principal_verification_unavailable` | Authentication could not be completed. |
| `tenant_unauthorized` | The authenticated principal is not allowed to use the tenant. |
| `tenant_authorization_unavailable` | Tenant policy could not be evaluated. |
| `store_identity_unavailable` | Provider metadata could not be read. |
| `store_identity_mismatch` | The requested incarnation is not the database's current incarnation. |

The service is intentionally in-process. A deployment supplies its own
transport, credential verifier, tenant policy, connection pool, and secret
handling. This module does not grant network access, actor ownership, lease
ownership, cross-host synchronization, or promotion authority.

## Restore-incarnation rotation

`rotatePostgreSqlAuthorityStoreIdentity` is an administrative operation owned by
the authenticated service deployment. It locks the singleton metadata row,
verifies the expected identity, and atomically writes a newly minted
`postgresql:<32 lowercase hex>` identity. It does not rewrite heads, commits,
events, receipts, goals, or operation IDs.

Provider revision tokens contain the database identity. Consequently, tokens
minted before a restore rotation become stale and conflict, while the durable
head and receipt history remain readable through a store opened with the new
identity. A wrong expected identity is rejected without a write. If the server
loses the response after `COMMIT`, the result is `ambiguous`; the service must
read metadata before retrying, rather than guessing whether rotation applied.

## Validation

The public synthetic fixture is
[`postgresql_authority_service_v0.json`](../../tests/fixtures/control_plane/postgresql_authority_service_v0.json).
It covers authenticated admission, authentication denial, tenant denial,
identity drift, and restore rotation without credentials or private database
details.

Run the deterministic seam tests with:

```sh
npm run typecheck:control-plane
npm run test:postgresql-authority-service
```

Run the real PostgreSQL path against an isolated disposable database by setting
`LOOPX_TEST_POSTGRES_SERVICE_URL` and invoking the same script. The database
must be disposable and separate from any active goal or other PostgreSQL test
schema; the integration test mutates only its own tenant/goal and metadata.
