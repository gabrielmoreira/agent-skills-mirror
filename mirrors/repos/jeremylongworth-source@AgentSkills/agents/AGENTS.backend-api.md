Use local skills as the primary routing layer for backend and API work.

Use `api-contract-design` when defining endpoints, resource models, request and
response schemas, status codes, idempotency, pagination, filtering, and
versioning.

Use `database-schema-review` when reviewing schema design, migrations, indexes,
constraints, relationships, tenant boundaries, and data integrity.

Use `auth-flow-design` when planning authentication, authorization, sessions,
tokens, roles, permissions, service accounts, tenant access, and auth errors.

Use `service-boundary-design` when defining backend module or service
responsibilities, owned data, interfaces, dependencies, transaction boundaries,
and migration paths.

Use `error-handling-contracts` for API and backend error envelopes, status-code
mapping, validation errors, retry behavior, logging, and client-safe messages.

Use `rate-limit-design` when defining quotas, throttling, abuse controls,
headers, retry guidance, monitoring, and support override paths.

Use `api-doc-writing` for published API docs, `backend-test-plan` for backend
verification coverage, `skill-threat-model` for high-risk backend review,
`qa-test-strategy` for broader QA strategy, and `concise-technical-writing` for
clear design memos.

Default to design and review outputs. Do not apply migrations, deploy services,
change auth policy, rotate credentials, alter production data, or change live
rate limits without explicit approval.
