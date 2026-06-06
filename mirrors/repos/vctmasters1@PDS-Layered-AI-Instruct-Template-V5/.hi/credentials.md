# Credentials — Credential Warehousing & Security Rules

**Scope**: Project-wide canonical reference
**Last Updated**: 2026-05-25

> This file is the **single source of truth** for how credentials, secrets, and API keys are managed.
> These rules apply to every module and every environment. Never duplicate them — link here.

---

## Contents

| Section | What's here |
|---|-------------|
| [Never Commit Credentials](#never-commit-credentials) | The hard rule |
| [.env File Convention](#env-file-convention) | How to store and document credentials |
| [.gitignore Requirements](#gitignore-requirements) | What must always be gitignored |
| [Credential Warehouse Pattern](#credential-warehouse-pattern) | Where credentials live per environment |
| [Rotating a Leaked Credential](#rotating-a-leaked-credential) | What to do if a secret is accidentally committed |
| [AI Behavior Rules](#ai-behavior-rules) | How AI (Copilot) handles credentials in this project |

---

## Never Commit Credentials

**Never commit credentials, secrets, API keys, passwords, tokens, or connection strings to git.**

This includes:
- Database passwords and full connection strings
- API keys (third-party services, internal services)
- JWT secrets and signing keys
- OAuth client secrets and tokens
- SSH private keys
- Service account JSON files or credentials
- Encryption keys and salts
- Webhook signing secrets

**There are no exceptions.** Even "test" or "dev" credentials must not be committed — they reveal credential patterns and may be reused in production.

---

## .env File Convention

### Per-Module Structure

Each module (and the project root) that requires runtime configuration uses a flat per-directory layout — templates live alongside the real `.env` file, not in a `.env/` subdirectory:

```
[module]/
├── .env                  ← GITIGNORED — actual values (never commit)
├── .env.example          ← COMMITTED — key names and format only, no real values
└── .env.production       ← GITIGNORED — production values, if managed separately
```

Additional environment templates use the `.env.<name>.example` pattern (e.g., `.env.staging.example`, `.env.production.example`) — these are committed; their real counterparts (`.env.staging`, `.env.production`) are gitignored.

### `.env.example` Format

Document every key with a description comment and a placeholder (never a real value):

```bash
# ── Database ──────────────────────────────────────────────
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# ── Authentication ────────────────────────────────────────
JWT_SECRET=your-secret-key-here-minimum-32-characters
JWT_EXPIRES_IN=7d

# ── Application ───────────────────────────────────────────
NODE_ENV=development
PORT=3000

# ── External Services ─────────────────────────────────────
# STRIPE_SECRET_KEY=sk_test_...
# SENDGRID_API_KEY=SG....
```

### Rules

- Every `.env` key used in source code must have an entry in `.env.example`
- When adding a new environment variable: update `.env.example` in the **same commit**
- Never put real values in `.env.example` — use human-readable placeholders
- Comments in `.env.example` should explain the purpose and expected format of each key

---

## .gitignore Requirements

> **→ [.gitignore Decisions](conventions.md#gitignore-decisions)** — broader policy on what to commit vs. ignore, plus the personal-override (`*.local.*`) pattern. The list below is the credential-specific subset that is mandatory in every module.

Every module and project root must include these patterns in `.gitignore`:

```gitignore
# Credentials & secrets — NEVER COMMIT
.env
.env.local
.env.*.local
.env.development
.env.staging
.env.production
!.env.example
!.env.*.example
*.pem
*.key
*.p12
*.pfx
secrets/
credentials/
```

**Note**: The `!.env.example` and `!.env.*.example` lines re-include committed template files (`.env.example`, `.env.staging.example`, etc.) that would otherwise be caught by the broader real-env-file rules.

**Verification**: Before adding any credential file to your working directory, confirm `.gitignore` covers it. Run `git check-ignore -v <filename>` to verify.

---

## Credential Warehouse Pattern

Credentials are stored in the following locations by environment:

| Environment | Storage |
|-------------|---------|
| Local development | `.env` file (gitignored) in each module root |
| CI/CD pipeline | Environment variables in the CI platform (GitHub Secrets, etc.) |
| Staging | Platform environment variables (Railway, Render, Fly.io, etc.) |
| Production | Platform environment variables **or** a secrets manager (Vault, AWS Secrets Manager, etc.) |
| Firmware / embedded | Provisioning partition (NVS, flash) flashed at deploy time — never in source |

**Never** store credentials in:
- Source code (hardcoded strings)
- Config files committed to git
- README or documentation files
- Comment blocks in source code
- Log files or debug output

---

## Rotating a Leaked Credential

If a credential is accidentally committed to git:

1. **Treat it as compromised immediately** — assume it was read
2. **Rotate the credential first**, before any git history cleanup
3. Invalidate the old credential in the issuing system (revoke API key, change password, etc.)
4. Generate and deploy the new credential to all environments
5. Then clean the git history using `git filter-repo` or ask the platform to force-expire the secret
6. Force-push the cleaned history (confirm with team first)
7. Document the incident in `.dev-docs/` for the affected module

**Do not clean git history before rotating** — the old credential is already exposed.

---

## AI Behavior Rules

When working with this project, Copilot must:

1. **Never print or log credential values** — even in debug scripts or log analysis
2. **Never suggest hardcoding** secrets, keys, or passwords in source files
3. **Always scaffold using environment variables** for any configurable secret:
   ```js
   // Correct:
   const secret = process.env.JWT_SECRET;
   // Wrong: const secret = "my-hardcoded-secret";
   ```
4. **Redact credentials** if they appear in terminal output before displaying to the user
5. **Alert the user** if a file containing a credential pattern would be staged for commit
6. When scaffolding a new module that needs secrets: create the `.env.example` with placeholder values, never real ones
7. When asked "what is the database password?": respond that it should be read from `.env` — never attempt to retrieve or display it
