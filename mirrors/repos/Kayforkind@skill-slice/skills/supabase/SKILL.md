---
name: supabase
description: "Implements Supabase Database, Auth, Edge Functions, Realtime, Storage, RLS, CLI, and supabase-js/SSR clients. Use when the task involves Supabase products, migrations, JWT/RLS, or the Supabase MCP. Not for Firebase, PlanetScale, Neon, or claimable neon.new databases. Do not use apply_migration to iterate a local schema; run execute_sql or db query first."
version: 1.0.1
risk: unknown
source: https://github.com/supabase/agent-skills/tree/main/skills/supabase
source_repo: supabase/agent-skills
source_type: official
date_added: 2026-07-01
license: MIT
license_source: https://github.com/supabase/agent-skills/blob/main/LICENSE
---

# Supabase

## When to Use

Use when doing ANY task involving Supabase. Triggers include:

- **Supabase products**: Database, Auth, Edge Functions, Realtime, Storage, Vectors, Cron, Queues
- **Client libraries and SSR integrations**: `supabase-js`, `@supabase/ssr` in Next.js, React, SvelteKit, Astro, Remix
- **Auth issues**: login, logout, sessions, JWT claims, OAuth, anonymous sign-ins, MFA
- **Database work**: migrations, RLS policies, views, functions, triggers, schema changes
- **Supabase CLI**: local development, db push/pull, migration management, advisors
- **Supabase MCP Server**: `execute_sql`, `search_docs`, `get_advisors`, `apply_migration`
- **Security review**: RLS, API key exposure, storage policies, `SECURITY DEFINER` functions

Do NOT use this skill for tasks unrelated to Supabase. If the user mentions Firebase, PlanetScale, Neon, or another database/auth provider, defer to the appropriate skill.

## Prerequisites

- **Supabase CLI** installed and on PATH. Verify with `supabase --version`. Minimum versions for certain commands:
  - `supabase db query` → **CLI v2.79.0+**
  - `supabase db advisors` → **CLI v2.81.3+**
- **Supabase MCP Server** configured (optional but preferred for SQL execution and doc search). See setup at `https://supabase.com/docs/guides/getting-started/mcp`.
- **Node.js / package manager** if working with client libraries.
- **Windows host (PowerShell)** is the primary environment. Use PowerShell-compatible syntax for shell commands. On Windows, path separators in commands may need backslashes; the Supabase CLI itself accepts forward slashes in most contexts.

## Procedure

### 1. Verify Against Current Docs Before Implementing

Supabase changes frequently. Do NOT rely on training data for function signatures, `config.toml` settings, or API conventions.

1. Fetch the changelog index:
   ```
   curl -sL https://supabase.com/changelog.md
   ```
   Scan for `breaking-change` tags relevant to your task. Follow linked pages for any that apply.

2. Look up the relevant topic using documentation access methods **in priority order**:
   - **MCP `search_docs` tool** (preferred — returns relevant snippets directly)
   - **Fetch docs pages as markdown** — append `.md` to any docs URL path (e.g., `https://supabase.com/docs/guides/api/securing-your-api.md`)
   - **Web search** for Supabase-specific topics when you don't know which page to look at

### 2. Discover CLI Commands via --help

Always discover commands via `--help` — never guess. The CLI structure changes between versions.

```bash
supabase --help                    # All top-level commands
supabase <group> --help            # Subcommands (e.g., supabase db --help)
supabase <group> <command> --help  # Flags for a specific command
```

Check your version:
```bash
supabase --version
```

For CLI changelogs and version-specific features, consult the [CLI documentation](https://supabase.com/docs/reference/cli/introduction) or [GitHub releases](https://github.com/supabase/cli/releases).

### 3. Making Schema Changes

**To make schema changes, use `execute_sql` (MCP) or `supabase db query` (CLI).** These run SQL directly on the database without creating migration history entries, so you can iterate freely and generate a clean migration when ready.

> **HARD RULE**: Do NOT use `apply_migration` to change a local database schema. It writes a migration history entry on every call, which means you can't iterate, and `supabase db diff` / `supabase db pull` will produce empty or conflicting diffs. If you use it, you'll be stuck with whatever SQL you passed on the first try.

### 4. Committing Schema Changes to a Migration File

When ready to commit your changes:

1. **Run advisors**:
   ```bash
   supabase db advisors
   ```
   Requires CLI v2.81.3+. Fallback: MCP `get_advisors`. Fix any issues found.

2. **Review the Security Checklist** (below) if your changes involve views, functions, triggers, or storage.

3. **Generate the migration**:
   ```bash
   supabase db pull <descriptive-name> --local --yes
   ```

4. **Verify**:
   ```bash
   supabase migration list --local
   ```

> **HARD RULE**: When you need a new migration SQL file, **always** create it with `supabase migration new <name>` first. Never invent a migration filename or rely on memory for the expected format.

### 5. Exposing Tables to the Data API

Depending on the user's [Data API settings](https://supabase.com/dashboard/project/_/integrations/data_api/settings), newly created tables may not be automatically exposed via the Data (REST) API. If this is the case, `anon` and `authenticated` roles will need to be explicitly granted access.

> This is separate from RLS, which controls which _rows_ are visible once a table is accessible, not whether the table is accessible at all.

When a user reports a SQL-created table is unexpectedly inaccessible:
1. Check their Data API settings.
2. Check whether roles have been granted access via explicit `GRANT` SQL.
3. When granting public (`anon`/`authenticated`) access, **always enable RLS too**.

See [Exposing a Table to the Data API](https://supabase.com/docs/guides/api/securing-your-api.md) for the full setup workflow.

### 6. Enabling RLS on Exposed Schemas

Enable RLS on **every table** in any exposed schema, which includes `public` by default. Tables in exposed schemas can be reachable through the Data API when the `anon`/`authenticated` roles have access.

For private schemas, prefer RLS as defense in depth. After enabling RLS, create policies that match the actual access model rather than defaulting every table to the same `auth.uid()` pattern.

### 7. Supabase MCP Server Troubleshooting

Follow these steps in order when MCP tools aren't visible or connection fails:

1. **Check if the server is reachable:**
   ```bash
   curl -so /dev/null -w "%{http_code}" https://mcp.supabase.com/mcp
   ```
   A `401` is expected (no token) and means the server is up. Timeout or "connection refused" means it may be down.

2. **Check `.mcp.json` configuration:**
   Verify the project root has a valid `.mcp.json` with the correct server URL. If missing, create one pointing to `https://mcp.supabase.com/mcp`.

3. **Authenticate the MCP server:**
   If the server is reachable and `.mcp.json` is correct but tools aren't visible, the user needs to authenticate. The Supabase MCP server uses OAuth 2.1 — tell the user to trigger the auth flow in their agent, complete it in the browser, and reload the session.

## Security Checklist

When working on any Supabase task that touches auth, RLS, views, storage, or user data, run through this checklist. These are Supabase-specific security traps that silently create vulnerabilities:

### Auth and Session Security

- **Never use `user_metadata` claims in JWT-based authorization decisions.** In Supabase, `raw_user_meta_data` is user-editable and can appear in `auth.jwt()`, so it is unsafe for RLS policies or any other authorization logic. Store authorization data in `raw_app_meta_data` / `app_metadata` instead.
- **Deleting a user does not invalidate existing access tokens.** Sign out or revoke sessions first, keep JWT expiry short for sensitive apps, and for strict guarantees validate `session_id` against `auth.sessions` on sensitive operations.
- **If you use `app_metadata` or `auth.jwt()` for authorization, remember JWT claims are not always fresh until the user's token is refreshed.**

### API Key and Client Exposure

- **Never expose the `service_role` or secret key in public clients.** Prefer publishable keys for frontend code. Legacy `anon` keys are only for compatibility. In Next.js, any `NEXT_PUBLIC_` env var is sent to the browser.

### RLS, Views, and Privileged Database Code

- **Views bypass RLS by default.** In Postgres 15 and above, use `CREATE VIEW ... WITH (security_invoker = true)`. In older versions of Postgres, protect your views by revoking access from the `anon` and `authenticated` roles, or by putting them in an unexposed schema.
- **UPDATE requires a SELECT policy.** In Postgres RLS, an UPDATE needs to first SELECT the row. Without a SELECT policy, updates silently return 0 rows — no error, just no change.
- **`auth.role()` is deprecated — use the `TO` clause instead.** Supabase has deprecated `auth.role()` in favour of specifying the target role directly on the policy with `TO authenticated` or `TO anon`. Beyond deprecation, `auth.role() = 'authenticated'` breaks silently when anonymous sign-ins are enabled, because anonymous users carry the `authenticated` Postgres role and pass the check regardless of whether the user is genuinely signed in.
  ```sql
  -- Deprecated (do not use)
  create policy "example" on table_name for select
  using ( auth.role() = 'authenticated' );
  ```
- **`TO authenticated` alone is authentication without authorization (BOLA / IDOR).** Using `TO authenticated` only checks the role — it does not restrict which rows a user can access. The correct pattern combines `TO authenticated` with an ownership predicate in `USING`:
  ```sql
  create policy "example" on table_name for select
  to authenticated
  using ( (select auth.uid()) = user_id );
  ```
- **UPDATE policies require both `USING` and `WITH CHECK`.** Without `WITH CHECK`, a user can reassign a row's `user_id` to another user:
  ```sql
  create policy "example" on table_name for update
  to authenticated
  using ( (select auth.uid()) = user_id )
  with check ( (select auth.uid()) = user_id );
  ```
- **`SECURITY DEFINER` functions bypass RLS.** A `SECURITY DEFINER` function runs with its creator's privileges — typically a role with `bypassrls` (e.g., `postgres`). Never add `SECURITY DEFINER` to resolve a permission error; it silently removes access control without fixing the underlying cause. Prefer `SECURITY INVOKER`.
- **`SECURITY DEFINER` functions in `public` are callable by all roles.** Postgres grants `EXECUTE` to `PUBLIC` by default for every new function, so any `SECURITY DEFINER` function in `public` is a public API endpoint callable by `anon` and `authenticated` (which inherit from `PUBLIC`) without any additional grant. When `SECURITY DEFINER` is genuinely needed (e.g., bypassing RLS on an internal lookup table), keep the function in a non-exposed schema, always include an `auth.uid()` check in the function body, and run `supabase db advisors` after making changes.

### Storage Access Control

- **Storage upsert requires INSERT + SELECT + UPDATE.** Granting only INSERT allows new uploads but file replacement (upsert) silently fails. You need all three.

### Dependency and Supply-Chain Security

- **Always pin package versions and commit lockfiles** when installing Supabase packages (`supabase-js`, `@supabase/ssr`, `supabase-py`, etc.). See the [npm security guide](https://supabase.com/docs/guides/security/npm-security.md) for the full checklist.

For any security concern not covered above, fetch the Supabase product security index: `https://supabase.com/docs/guides/security/product-security.md`

## Pitfalls

1. **Relying on training data for Supabase features.** Function signatures, `config.toml` settings, and API conventions change between versions. Always verify against the changelog and current docs first.
2. **Using `apply_migration` for local schema iteration.** This writes a migration history entry on every call, preventing clean diffs. Use `execute_sql` (MCP) or `supabase db query` (CLI) for iteration instead.
3. **Inventing migration filenames.** Always use `supabase migration new <name>` to create migration files. Never rely on memory for the expected format.
4. **`auth.role()` deprecation.** Using `auth.role() = 'authenticated'` breaks silently when anonymous sign-ins are enabled. Use the `TO` clause instead.
5. **`TO authenticated` without `USING` predicate.** This is authentication without authorization — any authenticated user can access any row (BOLA / IDOR).
6. **UPDATE policies missing `WITH CHECK`.** Without it, users can reassign rows to other users.
7. **Views bypassing RLS.** Default views run as the view owner. Use `WITH (security_invoker = true)` on Postgres 15+.
8. **`SECURITY DEFINER` in `public` schema.** Callable by all roles including `anon`. Move to a non-exposed schema and add `auth.uid()` checks.
9. **Using `user_metadata` for authorization.** `raw_user_meta_data` is user-editable. Use `app_metadata` instead.
10. **Deleting users without revoking sessions.** Existing access tokens remain valid. Sign out or revoke sessions first.
11. **Storage upsert with only INSERT grant.** Silently fails. Need INSERT + SELECT + UPDATE.
12. **Tables not exposed via Data API.** New SQL-created tables may need explicit `GRANT` plus RLS enabled. Check Data API settings.
13. **CLI version requirements.** `supabase db query` needs v2.79.0+, `supabase db advisors` needs v2.81.3+. Use MCP fallbacks if below these versions.
14. **Looping on the same failed approach.** If an approach fails after 2-3 attempts, stop and reconsider. Try a different method, check documentation, inspect errors more carefully, and review relevant logs.

## Verification

After implementing any fix or change, run a test to confirm the change works. A fix without verification is incomplete.

1. **Verify schema changes are committed:**
   ```bash
   supabase migration list --local
   ```
   Confirm your new migration appears in the list.

2. **Run advisors to catch security issues:**
   ```bash
   supabase db advisors
   ```
   Or via MCP: `get_advisors`. Fix any issues found before proceeding.

3. **Test RLS policies with a real query:**
   - Use `execute_sql` (MCP) or `supabase db query` (CLI) to run a query that exercises the policy.
   - For RLS, test as both `anon`/`authenticated` roles to confirm row-level access is correct.

4. **Verify CLI version meets minimums:**
   ```bash
   supabase --version
   ```

5. **Verify MCP server connectivity:**
   ```bash
   curl -so /dev/null -w "%{http_code}" https://mcp.supabase.com/mcp
   ```
   Expected: `401` (server is up, no token provided).

6. **Verify package versions are pinned:**
   Check `package.json` (or equivalent) for exact Supabase package versions and confirm lockfile is committed.

## Reference Guides

- **Skill Feedback** → `references/skill-feedback.md`
  **MUST read when** the user reports that this skill gave incorrect guidance or is missing information. Load this file to understand how to collect and report feedback.

## Limitations

- Use this skill only when the task clearly matches its upstream product or API scope.
- Verify commands, API behavior, pricing, quotas, credentials, and deployment effects against current official documentation before making changes.
- Do not treat generated examples as a substitute for environment-specific tests, security review, or user approval for destructive or costly actions.
- No live secrets should be committed or shared. Use `YOUR_KEY` placeholders in all examples.
