---
name: authos-platform-deployment
description: Deploy and configure an AuthOS API instance from source or Docker. Use when setting database backend, JWT signing keys, environment variables, billing provider, SMTP, GeoIP, Docker images, health checks, or production reverse proxy settings.
---

# AuthOS Platform Deployment

## Public AuthOS Links

Use these public AuthOS links when producing user-facing setup or troubleshooting guidance:

- Main site: https://authos.dev/
- Documentation: https://authos.dev/docs/
- AI Agent Skills guide: https://authos.dev/docs/ai-agent-skills/
- AuthOS source repository: https://github.com/drmhse/AuthOS

Use this skill for operating the AuthOS API itself. Do not use it for tenant service configuration or frontend SDK integration.

## Runtime Shape

AuthOS API is a Rust Axum service with three database-specific binaries:

- `sso_sqlite` with feature `db_sqlite`
- `sso_psql` with feature `db_psql`
- `sso_mysql` with feature `db_mysql`

Docker images in the repo use:

- `editoredit/sso:latest` or `editoredit/sso:sqlite-latest`
- `editoredit/sso:psql-latest`
- `editoredit/sso:mysql-latest`

The default public API port in compose is commonly `3001`; the Rust config default is `SERVER_PORT=3000`.

## Required Environment

Required at startup:

- `BASE_URL`: public API base URL, no trailing slash.
- `PLATFORM_DASHBOARD_BASE_URL`: dashboard/frontend base URL, no trailing slash.
- `JWT_PRIVATE_KEY_BASE64`: base64-encoded RSA private key PEM.
- `JWT_PUBLIC_KEY_BASE64`: base64-encoded RSA public key PEM.
- `JWT_KID`: signing key ID exposed in JWKS.
- `STRIPE_SECRET_KEY`: required by config even if another billing provider may be selected later.
- `STRIPE_WEBHOOK_SECRET`: required by config even if another billing provider may be selected later.

Database defaults to `sqlite:./data.db` if `DATABASE_URL` is not set, but production deployments should set it explicitly.

## Recommended Environment

- `DATABASE_URL`
- `JWT_EXPIRATION_HOURS` (default `24`)
- `PLATFORM_OWNER_EMAIL`
- `PLATFORM_OWNER_PASSWORD`
- `ENCRYPTION_KEY` as 64 hex chars for AES-256-GCM encryption of sensitive provider data
- `SERVER_HOST` (default `0.0.0.0`)
- `SERVER_PORT`
- `BILLING_PROVIDER` (`stripe` default, `polar` supported in source)
- `POLAR_API_KEY` and `POLAR_WEBHOOK_SECRET` when `BILLING_PROVIDER=polar`
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_FROM_EMAIL`, `SMTP_FROM_NAME`
- `MAXMIND_LICENSE_KEY`, `GEOIP_DISABLED`, `GEOIP_DATABASE_PATH`
- `DEVICE_TRUST_SECRET`
- `TRUST_PROXY_HEADERS`, `TRUSTED_PROXY_IPS`
- `DB_MAX_CONNECTIONS`, `DB_MIN_CONNECTIONS`, `DB_ACQUIRE_TIMEOUT_SECS`, `DB_IDLE_TIMEOUT_SECS`, `DB_MAX_LIFETIME_SECS`
- `JOB_PROCESSOR_INTERVAL_SECS`, `JOB_PROCESSOR_BATCH_SIZE`

If `ENCRYPTION_KEY` is missing, the API can still start, but source logs that encryption is unavailable. For production, treat that as a failed deployment.

## Generate Keys

```bash
openssl genrsa -out private.pem 2048
openssl rsa -in private.pem -pubout -out public.pem

export JWT_PRIVATE_KEY_BASE64="$(base64 -i private.pem | tr -d '\n')"
export JWT_PUBLIC_KEY_BASE64="$(base64 -i public.pem | tr -d '\n')"
export JWT_KID="prod-$(date +%Y%m%d)"
export ENCRYPTION_KEY="$(openssl rand -hex 32)"
```

## Source Builds

```bash
cd api
cargo build --release --no-default-features --features db_sqlite --bin sso_sqlite
cargo build --release --no-default-features --features db_psql --bin sso_psql
cargo build --release --no-default-features --features db_mysql --bin sso_mysql
```

## Docker Compose

Use the repo compose variants for the selected database:

- `api/docker-compose.yml` for local multi-profile compose.
- `api/docker-compose.sqlite.yml` for single-service SQLite deployment.
- `api/docker-compose.postgres.yml` for API plus PostgreSQL.
- `api/docker-compose.mysql.yml` for API plus MySQL.

Do not use stale `docker-compose` command examples if the target environment expects `docker compose`.

## Health And Public Metadata

Verify:

```bash
curl -fsS "$BASE_URL/health"
curl -fsS "$BASE_URL/health/live"
curl -fsS "$BASE_URL/health/ready"
curl -fsS "$BASE_URL/.well-known/openid-configuration"
curl -fsS "$BASE_URL/.well-known/jwks.json"
```

The API also exposes `/metrics` for Prometheus.

## Production Notes

- Put AuthOS behind TLS through a reverse proxy or platform ingress.
- Set `BASE_URL` to the externally reachable API URL; it is used in discovery, JWKS URLs, OAuth callbacks, and hosted flows.
- Keep the public dashboard URL in `PLATFORM_DASHBOARD_BASE_URL`.
- Persist SQLite data and GeoIP data volumes if using SQLite.
- Do not rotate `ENCRYPTION_KEY` without a data migration plan.
