# Security, versions, and vulnerability reporting

QuantDinger handles model secrets, trading credentials, and account data. A production operator should treat the application, database, cache, and reverse proxy as one security boundary and restrict network access to administration surfaces.

## Operator responsibilities

- Deploy trusted releases or images and read release notes before upgrading.
- Use long random passwords and separate administrators from regular users.
- Provide credentials through environment variables or a secret system; never put them in source, logs, screenshots, or issues.
- Grant trading APIs only the permissions required, disable withdrawals, and prefer a dedicated subaccount.
- Apply access control, encryption, and retention rules to databases, object storage, and backups.
- Enable HTTPS at the reverse proxy, restrict administration endpoints, and update dependencies and base images.
- Rotate model keys, OAuth secrets, Agent Tokens, and trading credentials regularly.

See [production hardening](../deployment/PRODUCTION_HARDENING.md) for the deployment baseline and [observability](../deployment/OBSERVABILITY.md) for operational monitoring.

## Agents and automation

Agent Tokens should use minimum scopes, expirations, rate limits, and notional limits. Human JWTs and Agent Tokens are not interchangeable. Every side-effecting Agent request should use a unique `Idempotency-Key`. Keep the global live-trading switch disabled unless an operator explicitly enables it after completing the [live-trading safety checklist](../trading/LIVE_TRADING_SAFETY.md).

## If exposure or suspicious activity is found

1. Stop affected strategies and new trading.
2. Revoke related tokens, API keys, and sessions.
3. Verify orders, positions, and permissions at the venue or broker.
4. Preserve the necessary logs without spreading secrets or personal data.
5. Restore service only after remediation and credential rotation.

## Report a vulnerability

Do not disclose exploitable details, credentials, or account data in a public issue. Follow the repository [security policy](../../SECURITY.md) to report privately. Include the affected version, reproduction conditions, impact, and any practical mitigation.

