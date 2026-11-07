# Multi-User Operation

QuantDinger v5 uses PostgreSQL-backed users by default. `SINGLE_USER_MODE` is a
legacy compatibility option and should remain `false` for a normal deployment.

[中文](MULTI_USER_SETUP_CN.md)

## Initial setup

The recommended installers prompt for the initial administrator and write the
required environment files. For a source deployment, set at least:

```text
# .env
POSTGRES_PASSWORD=<strong unique password>

# .env
ADMIN_USER=<administrator username>
ADMIN_PASSWORD=<strong unique password>
SECRET_KEY=<independent random secret>
CREDENTIAL_ENCRYPTION_KEY=<stable independent encryption key>
SINGLE_USER_MODE=false
```

Start the stack with `docker compose up -d --build`. PostgreSQL initializes a
new database from `backend_api_python/migrations/init.sql`; later schema changes
are applied by the one-shot `migration` service. Do not run `init.sql` manually
against an existing database.

## Administrator bootstrap

When no user exists, the backend creates the first administrator from
`ADMIN_USER`, `ADMIN_PASSWORD`, and optional `ADMIN_EMAIL`. The built-in example
password `123456` is not suitable for deployment; the installers reject it.

If an existing database still has the untouched bootstrap administrator, the
backend can synchronize configured non-default credentials. Use the dedicated
[administrator troubleshooting guide](ADMIN_AND_SETTINGS_TROUBLESHOOTING_EN.md)
before editing database rows.

## Roles

| Role | Intended access |
| --- | --- |
| `viewer` | Dashboard and read-only views |
| `user` | Personal indicators, backtests, strategies, and portfolio |
| `manager` | User capabilities plus operational settings |
| `admin` | Full administration, user management, settings, and credentials |

The server remains authoritative. Hiding a menu item in the frontend is not an
authorization control.

## Current API surfaces

- Authentication: `/api/auth/login`, `/api/auth/logout`, `/api/auth/info`
- Registration and recovery: `/api/auth/register`, `/api/auth/reset-password`
- Admin user management: `/api/users/list`, `/api/users/create`,
  `/api/users/update`, `/api/users/delete`, `/api/users/reset-password`
- Self-service: `/api/users/profile`, `/api/users/profile/update`,
  `/api/users/change-password`, and MFA endpoints under `/api/users/mfa/*`

Use [Human OpenAPI](../api/README.md) for request and response schemas.

## Production checklist

1. Keep PostgreSQL and Redis on private/loopback networks.
2. Persist `SECRET_KEY`; changing it invalidates sessions.
3. Persist `CREDENTIAL_ENCRYPTION_KEY`; changing it can make stored credentials unreadable.
4. Enable HTTPS before allowing remote login.
5. Back up PostgreSQL and test restoration.
6. Review administrator login logs, MFA, user status, and role assignments.

There is no maintained automatic SQLite-to-PostgreSQL migration command in the
current repository. For a legacy SQLite installation, keep a verified backup
and plan a controlled data migration instead of running an obsolete script.
