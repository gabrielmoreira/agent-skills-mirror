# Credentials — Credential Warehousing & Security Rules

**Scope**: web-marketplace/frontend module reference
**Last Updated**: 2026-05-27

> **? Root [``.ai/credentials.md``](../../.ai/credentials.md)** — This file is authoritative for all directories in this project.

## Contents

| Section | Description |
|---------|-------------|
| [Never Commit Credentials](#never-commit-credentials) | Prohibits committing credentials, secrets, and sensitive data to git |
| [.env File Convention](#env-file-convention) | File structure and purpose of .env, .env.example, and .env.production |
| [.gitignore Requirements](#gitignore-requirements) | Required patterns to exclude from version control |
| [Credential Warehouse Pattern](#credential-warehouse-pattern) | Storage locations for credentials across environments |
| [Rotating a Leaked Credential](#rotating-a-leaked-credential) | Incident response steps for credential compromise |

## Never Commit Credentials

**Never commit credentials, secrets, API keys, passwords, tokens, or connection strings to git.**

This includes:
- Database passwords and full connection strings
- API keys (third-party services, internal services)
- JWT secrets and signing keys
- OAuth client secrets and tokens
- SSH private keys
- Service account JSON files or credentials

## .env File Convention

```
web-marketplace/
+-- .env                  ? GITIGNORED — actual values (never commit)
+-- .env.example          ? COMMITTED — key names and format only, no real values
+-- .env.production       ? GITIGNORED — production values
```

### `.env.example` Format

```bash
# -- Database ----------------------------------------------
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# -- Authentication ----------------------------------------
JWT_SECRET=your-secret-key-here-minimum-32-characters
JWT_EXPIRES_IN=7d

# -- Application -------------------------------------------
NODE_ENV=development
PORT=3000

# -- External Services -------------------------------------
STRIPE_SECRET_KEY=sk_test_...
SENDGRID_API_KEY=SG....
```

## .gitignore Requirements

```gitignore
# Credentials & secrets — NEVER COMMIT
.env
.env.local
.env.*.local
*.pem
*.key
credentials/
secrets/
```

## Credential Warehouse Pattern

| Environment | Storage |
|-------------|---------|
| Local development | `.env` file (gitignored) in each module root |
| CI/CD pipeline | Environment variables in the CI platform |
| Staging | Platform environment variables |
| Production | Platform environment variables or secrets manager |

---

## Rotating a Leaked Credential

1. Treat as compromised immediately
2. Rotate the credential FIRST before any git cleanup
3. Invalidate old credential in issuing system
4. Generate and deploy new credential
5. Then clean git history
6. Document incident in ``.dev-docs/`

