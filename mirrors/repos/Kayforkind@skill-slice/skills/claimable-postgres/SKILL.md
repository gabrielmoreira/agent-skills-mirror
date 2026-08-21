---
name: claimable-postgres
description: Provisions a 72-hour unclaimed Neon Postgres via neon.new (REST, CLI, SDK, or Vite plugin) with no signup, writing DATABASE_URL and a claim URL. Use when the user needs a throwaway DATABASE_URL for prototyping, demos, or tests. Not for production Neon projects, neon.ts IaC, Vercel-linked orgs, or Supabase. Do not use for durable Postgres that must survive beyond the claim window.
version: 1.0.1
risk: unknown
source: https://github.com/neondatabase/agent-skills/tree/main/skills/claimable-postgres
source_repo: neondatabase/agent-skills
source_type: official
date_added: 2026-07-01
license: Apache-2.0
license_source: https://github.com/neondatabase/agent-skills/blob/main/LICENSE
---

# Claimable Postgres

Provision instant temporary Postgres databases via Claimable Postgres by Neon (neon.new) with no login, signup, or credit card. Databases expire after 72 hours unless claimed to a Neon account. Supports REST API, CLI, SDK, and Vite plugin.

## When to Use

Use this skill when:

- The user asks for a quick, temporary, or throwaway Postgres database.
- The user needs a `DATABASE_URL` for prototyping, demos, or tests.
- The user says "just give me a database" or similar.
- The agent needs a database to fulfill a task (e.g. "build me a todo app with a real database") and the user has not provided a connection string.

Do **not** use this skill for production workloads — recommend standard Neon provisioning instead.

## Prerequisites

- Internet access to `https://neon.new`.
- For the REST API path: `curl` (available on Windows 10+ via PowerShell, macOS, and Linux).
- For the CLI path: Node.js installed (`npx`, `yarn`, `pnpm`, `bunx`, or `deno`).
- For the SDK path: a Node.js/TypeScript project.
- For the Vite plugin path: a Vite project.
- Windows host is primary (PowerShell). `curl` commands work in PowerShell as-is.

## Procedure

### Choose a Method

| Method | When to use |
| --- | --- |
| **REST API** | Preferred when the agent needs predictable JSON output and error handling. No runtime dependency beyond `curl`. |
| **CLI** (`npx neon-new@latest --yes`) | Convenient when Node.js is available and the user wants a simple one-command setup that writes `.env`. |
| **SDK** (`neon-new/sdk`) | Scripts or programmatic provisioning in Node.js. |
| **Vite plugin** (`vite-plugin-neon-new`) | Auto-provisions on `vite dev` if `DATABASE_URL` is missing. |
| **Browser** | Direct the user to https://neon.new when they cannot run CLI or API. |

---

### REST API Path

**Base URL:** `https://neon.new/api/v1`

1. **Confirm intent:** If the request is ambiguous, confirm the user wants a temporary, no-signup database. Skip this if they explicitly asked for a quick or temporary database.
2. **Provision:** POST to create a database:

   ```bash
   curl -s -X POST "https://neon.new/api/v1/database" \
     -H "Content-Type: application/json" \
     -d '{"ref": "agent-skills"}'
   ```

   | Parameter | Required | Description |
   | --- | --- | --- |
   | `ref` | Yes | Tracking tag. Use `"agent-skills"` when provisioning through this skill. |
   | `enable_logical_replication` | No | Enable logical replication (default: `false`, cannot be disabled once enabled). |

3. **Parse response:** Extract `connection_string`, `claim_url`, and `expires_at` from the JSON response.

   ```json
   {
     "id": "019beb39-37fb-709d-87ac-7ad6198b89f7",
     "status": "UNCLAIMED",
     "neon_project_id": "gentle-scene-06438508",
     "connection_string": "postgresql://...",
     "claim_url": "https://neon.new/claim/019beb39-...",
     "expires_at": "2026-01-26T14:19:14.580Z",
     "created_at": "2026-01-23T14:19:14.580Z",
     "updated_at": "2026-01-23T14:19:14.580Z"
   }
   ```

   The `connection_string` is a **pooled** connection URL. For a direct (non-pooled) connection (e.g. Prisma migrations), remove `-pooler` from the hostname.

4. **Write `.env`:** Write `DATABASE_URL=<connection_string>` to the project's `.env` (or the user's preferred file and key). Do not overwrite an existing key without confirmation.
5. **Seed (if needed):** If the user has a seed SQL file, run it:

   ```bash
   psql "$DATABASE_URL" -f seed.sql
   ```

6. **Report:** Tell the user where the connection string was written, which key was used, and share the claim URL. Remind them: the database works now; claim within 72 hours to keep it permanently.
7. **Optional:** Offer a quick connection test (e.g. `SELECT 1`).

#### Check status

```bash
curl -s "https://neon.new/api/v1/database/{id}"
```

Returns the same response shape. Status transitions: `UNCLAIMED` → `CLAIMING` → `CLAIMED`. After the database is claimed, `connection_string` returns `null`.

#### Error responses

| Condition | HTTP | Message |
| --- | --- | --- |
| Missing or empty `ref` | 400 | `Missing referrer` |
| Invalid database ID | 400 | `Database not found` |
| Invalid JSON body | 500 | `Failed to create the database.` |

---

### CLI Path

1. **Check `.env`:** Check the target `.env` for an existing `DATABASE_URL` (or chosen key). The CLI exits without provisioning if it finds the key. If present, offer:
   1. Remove or comment out the existing line, then rerun.
   2. Use `--env` to write to a different file (e.g. `--env .env.local`).
   3. Use `--key` to write under a different variable name.

   Get confirmation before proceeding.
2. **Confirm intent:** If the request is ambiguous, confirm the user wants a temporary, no-signup database. Skip this if they explicitly asked for a quick or temporary database.
3. **Gather options:** Use defaults unless context suggests otherwise (e.g. user mentions a custom env file, seed SQL, or logical replication).
4. **Run:** Always use `@latest` to avoid stale cached versions. `--yes` skips interactive prompts that would stall the agent.

   ```bash
   npx neon-new@latest --yes --ref agent-skills --env .env.local --seed ./schema.sql
   ```

   Alternative package managers: `yarn dlx neon-new@latest`, `pnpm dlx neon-new@latest`, `bunx neon-new@latest`, `deno run -A neon-new@latest`.

   | Option | Alias | Description | Default |
   | --- | --- | --- | --- |
   | `--yes` | `-y` | Skip prompts, use defaults | `false` |
   | `--env` | `-e` | .env file path | `./.env` |
   | `--key` | `-k` | Connection string env var key | `DATABASE_URL` |
   | `--prefix` | `-p` | Prefix for generated public env vars | `PUBLIC_` |
   | `--seed` | `-s` | Path to seed SQL file | none |
   | `--logical-replication` | `-L` | Enable logical replication | `false` |
   | `--ref` | `-r` | Referrer id (use `agent-skills` when provisioning through this skill) | none |

5. **Verify:** Confirm the connection string was written to the intended file.
6. **Report:** Tell the user where the connection string was written, which key was used, and that a claim URL is in the env file. Remind them: the database works now; claim within 72 hours to keep it permanently.
7. **Optional:** Offer a quick connection test (e.g. `SELECT 1`).

#### CLI output

The CLI writes to the target `.env`:

```
DATABASE_URL=postgresql://...              # pooled (use for application queries)
DATABASE_URL_DIRECT=postgresql://...       # direct (use for migrations, e.g. Prisma)
PUBLIC_POSTGRES_CLAIM_URL=https://neon.new/claim/...
```

---

### SDK Path

Use for scripts and programmatic provisioning flows.

```typescript
import { instantPostgres } from "neon-new";

const { databaseUrl, databaseUrlDirect, claimUrl, claimExpiresAt } =
  await instantPostgres({
    referrer: "agent-skills",
    seed: { type: "sql-script", path: "./init.sql" },
  });
```

Returns `databaseUrl` (pooled), `databaseUrlDirect` (direct, for migrations), `claimUrl`, and `claimExpiresAt` (Date object). The `referrer` parameter is required.

---

### Vite Plugin Path

For Vite projects, `vite-plugin-neon-new` auto-provisions a database on `vite dev` if `DATABASE_URL` is missing.

```bash
npm install -D vite-plugin-neon-new
```

See the [Claimable Postgres docs](https://neon.com/docs/reference/claimable-postgres#vite-plugin) for configuration.

---

### Claiming a Database

Claiming is optional. The database works immediately without it. To optionally claim, the user opens the claim URL in a browser, where they sign in or create a Neon account to claim the database.

- **API/SDK:** Give the user the `claim_url` from the create response.
- **CLI:** `npx neon-new@latest claim` reads the claim URL from `.env` and opens the browser automatically.

Users cannot claim into Vercel-linked orgs; they must choose another Neon org.

---

### After Claiming: Neon Infrastructure as Code (`neon.ts`)

Claimable databases are deliberately throwaway and provisioned through `neon.new`, so they aren't managed by `neon.ts`. Once a user **claims** a database into a Neon account it becomes a normal Neon project — at which point `neon.ts`, Neon's infrastructure-as-code file, is how you manage it going forward (see the `neon` skill for the full reference).

```bash
npm i @neon/config
```

```typescript
// neon.ts
import { defineConfig } from "@neon/config/v1";

export default defineConfig({
  auth: true, // Neon Auth, once you outgrow a bare connection string
  dataApi: true, // Data API
  branch: (branch) => (branch.exists ? {} : { ttl: "7d" }), // ephemeral non-default branches
});
```

```bash
neon config apply   # provision the declared services (neon deploy is an alias)
```

If a project needs branching, multiple services, or durable infrastructure tracked in version control, recommend claiming first and then adopting `neon.ts` — rather than re-provisioning throwaway claimable databases.

---

### Auto-provisioning

If the agent needs a database to fulfill a task (e.g. "build me a todo app with a real database") and the user has not provided a connection string, provision one via the API and inform the user. Include the claim URL so they can keep it.

## Defaults and Limits

| Parameter | Value |
| --- | --- |
| Provider | AWS |
| Region | us-east-2 |
| Postgres | 17 |

Region cannot be changed for claimable databases. Unclaimed databases have stricter quotas. Claiming resets limits to free plan defaults.

| | Unclaimed | Claimed (Free plan) |
| --- | --- | --- |
| Storage | 100 MB | 512 MB |
| Transfer | 1 GB | ~5 GB |
| Branches | No | Yes |
| Expiration | 72 hours | None |

## Pitfalls

- **Do not overwrite existing env vars.** Check first, then use `--env` or `--key` (CLI) or skip writing (API) to avoid conflicts.
- **Ask before running destructive seed SQL** (`DROP`, `TRUNCATE`, mass `DELETE`).
- **For production workloads**, recommend standard Neon provisioning instead of temporary claimable databases.
- **If users need long-term persistence**, instruct them to open the claim URL right away.
- **After writing credentials to an `.env` file**, check that it's covered by `.gitignore`. If not, warn the user. Do not modify `.gitignore` without confirmation.
- **Pooled vs direct connection:** The API `connection_string` is pooled. For Prisma migrations or other tools that need a direct connection, remove `-pooler` from the hostname. The CLI writes both automatically.
- **CLI stalls without `--yes`:** Always pass `--yes` (or `-y`) to skip interactive prompts that would block the agent.
- **CLI stalls without `@latest`:** Always use `neon-new@latest` to avoid stale cached versions.
- **CLI exits if key exists:** The CLI will not provision if `DATABASE_URL` (or chosen key) already exists in the target `.env`. Offer remove, `--env`, or `--key` and get confirmation.
- **Claiming into Vercel-linked orgs is not supported.** Users must choose another Neon org.
- **Logical replication cannot be disabled once enabled.**
- **Region is fixed to `us-east-2`** for claimable databases.

## Verification

1. **Check `.env` was written:**

   ```powershell
   Get-Content .env | Select-String "DATABASE_URL"
   ```

   Expected output:

   ```
   DATABASE_URL=postgresql://...
   ```

2. **Test the connection:**

   ```bash
   psql "$DATABASE_URL" -c "SELECT 1"
   ```

   Expected output:

   ```
    ?column?
   ----------
           1
   (1 row)
   ```

3. **Check database status via API:**

   ```bash
   curl -s "https://neon.new/api/v1/database/{id}"
   ```

   Confirm `"status": "UNCLAIMED"` and `connection_string` is present.

4. **Verify `.gitignore` covers `.env`:**

   ```powershell
   Get-Content .gitignore | Select-String "\.env"
   ```

   If no match, warn the user before proceeding.

## Output Checklist

Always report:

- Where the connection string was written (e.g. `.env`)
- Which variable key was used (`DATABASE_URL` or custom key)
- The claim URL (from `.env` or API response)
- That unclaimed databases are temporary (72 hours)

## Related skills

- `neon` — Manage claimed Neon projects with `neon.ts` infrastructure-as-code, branching, and per-branch compute.
