# Security Assessment

**System:** QuantDinger  
**Assessment scope:** public backend, MCP server, release workflows, and the
documented interfaces to the separately released frontend and mobile clients  
**Last reviewed:** 2026-10-25

## Security objectives

QuantDinger must protect account identity, broker and exchange credentials,
strategy code, trading permissions, order integrity, auditability, and tenant
separation. A research result must not silently gain live-trading authority.

## Actors and actions

| Actor | Permitted actions | Security boundary |
| --- | --- | --- |
| Anonymous user | Read public information and use explicitly public endpoints | No account, strategy, credential, or trading access |
| Authenticated user | Manage owned research, strategies, settings, and connected accounts | Tenant ownership and authorization checks |
| Administrator | Operate the deployment and manage authorized users | Administrative authorization and audit trail |
| Strategy or AI agent | Request only explicitly granted research or execution operations | Tool registry, execution policy, risk limits, and credential isolation |
| Broker or data provider | Return market/account data and accept authorized requests | Approved endpoint, TLS, provider authentication, and request validation |
| CI/release workflow | Test, scan, build, attest, sign, and publish releases | Minimal GitHub token permissions and protected secrets |

The detailed runtime components and data flows are documented in
[the architecture guide](../architecture/ARCHITECTURE.md), while public HTTP
interfaces are defined by the committed
[OpenAPI specification](../api/openapi.yaml) and
[Agent Gateway specification](../agent/agent-openapi.json).

## Primary risks and controls

| Risk | Impact | Current controls |
| --- | --- | --- |
| Credential disclosure | Unauthorized account or trading access | Local-first deployment, environment isolation, encrypted stored credentials, secret scanning, log redaction guidance |
| Authentication or authorization bypass | Cross-user access or privilege escalation | Strong deployment secret validation, authoritative database checks, route authorization tests, coordinated disclosure process |
| Untrusted strategy execution | Host compromise or secret access | Restricted execution boundary, process isolation, resource controls, documented trust assumptions |
| Server-side request forgery | Internal network or credential exposure | Approved broker endpoints, URL validation, and provider adapters |
| Incorrect or duplicate orders | Financial loss | Risk limits, idempotency and reconciliation logic, transactional execution accounting tests, paper-trading path |
| Supply-chain compromise | Malicious build or dependency | Pinned Actions and images, Dependabot, pip-audit, CodeQL, Bandit, Gitleaks, CI-built images, provenance, SBOM, and keyless release signing |
| Cross-tenant data leakage | Confidentiality breach | Ownership checks, isolated runtime state, authorization regression tests |
| Unsafe AI output | Unreviewed live-trading action | Typed tool boundaries, permission checks, auditable decisions, and explicit execution controls |

## Assessment method

The project reviews architecture boundaries, publicly reported vulnerabilities,
dependency findings, static-analysis findings, secret scans, authentication and
authorization tests, and release workflow permissions. Confirmed issues are
triaged under the severity and remediation targets in `SECURITY.md`.

## Residual risk

Self-hosted deployments remain responsible for operating-system, network,
reverse-proxy, database, and secret-store security. Third-party brokers,
exchanges, AI providers, and market-data sources retain their own security and
availability risks. QuantDinger does not guarantee strategy profitability or
eliminate market risk.

