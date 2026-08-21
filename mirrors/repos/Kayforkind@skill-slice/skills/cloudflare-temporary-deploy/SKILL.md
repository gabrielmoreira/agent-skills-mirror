---
name: cloudflare-temporary-deploy
description: "Deploys a Cloudflare Worker to a live workers.dev URL with wrangler deploy --temporary (Wrangler 4.102.0+), a 60-minute claim URL, and no OAuth. Use when shipping agent-written Worker code to a link without an account, or iterating a throwaway prototype. Not for production or CI with wrangler login / CLOUDFLARE_API_TOKEN, Cloudflare Pages/R2, or hosting that must outlive an unclaimed hour."
version: 1.0.1
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [cloudflare, workers, wrangler, deploy, temporary, agent, serverless, web-development]
    category: web-development
---

# Cloudflare Temporary Deploy

Deploy a Cloudflare Worker to a live `workers.dev` URL with zero account setup, using `wrangler deploy --temporary`. Cloudflare provisions a throwaway account, deploys, and prints a claim URL valid for 60 minutes; unclaimed accounts auto-delete. This gives an agent a tight write → deploy → verify loop without any OAuth, signup, or token copy-paste.

This skill does NOT cover production deploys (use `wrangler login` + a permanent account for those), nor non-Worker Cloudflare products beyond the temporary-account limits listed below.

## When to Use

Load this skill when the user wants to:

- **Ship agent-written code to a live URL** without first creating a Cloudflare account — "deploy this and give me a link"
- **Iterate in a background/autonomous session** where a browser OAuth step would be a hard stop
- **Prototype or evaluate Workers** quickly with a throwaway, claimable target
- **Build a self-verifying deploy loop** — deploy, `curl` the live URL, confirm output matches the code, redeploy

### When NOT to Use

- **Production or CI/CD** → use a permanent account (`wrangler login` or `CLOUDFLARE_API_TOKEN`). `--temporary` errors out if any credential is present.
- **Wrangler is already authenticated** → `--temporary` returns an error by design. Run `wrangler logout` first only if the user explicitly wants a throwaway deploy.
- **Long-lived hosting** → temporary deployments are deleted after 60 minutes unless claimed.

## Prerequisites

- **Wrangler 4.102.0 or later.** This is the version that introduced `--temporary`. Earlier versions do not have it. Verify with `npx wrangler@latest --version`.
- **Node 18+ / npm** (or `npx`, `yarn`, `pnpm`). No global install needed — `npx wrangler@latest` works.
- **No Cloudflare credentials present.** `--temporary` only works when Wrangler is unauthenticated: no OAuth login, no `CLOUDFLARE_API_TOKEN` / `CLOUDFLARE_API_KEY` env var, no `~/.wrangler` / `~/.config/.wrangler` cached OAuth. Use the `terminal` tool's environment as-is; do not set those vars.
- Network egress to `cloudflare.com` and `workers.dev`.
- Using `--temporary` accepts Cloudflare's Terms of Service and Privacy Policy.

### Windows / PowerShell Notes

Windows is the primary host. All commands below are PowerShell-compatible unless noted. Key differences:

- Pipe to the parser: use `2>&1` the same way — PowerShell supports it natively.
- `curl` on Windows is `curl.exe` (the real curl, not a PowerShell alias). If `curl` resolves to `Invoke-WebRequest`, use `curl.exe -sS <url>` explicitly.
- Paths use backslashes on Windows: `scripts\parse_deploy_output.py`. The parser script is invoked via `python` (not `python3`) on Windows if `python3` is not on PATH. Try `python3` first, fall back to `python`.
- The skill directory on the reference machine is `~\agent-skills\library\cloudflare-temporary-deploy\`.

## Procedure

Use the `terminal` tool for every step. Always pin the version (`wrangler@latest` or `wrangler@4.102.0` or newer) so you don't accidentally run an old global wrangler that lacks the flag.

### 1. Verify Wrangler version

```powershell
npx wrangler@latest --version
```

Confirm the output is `4.102.0` or higher. If it is older, `npx wrangler@latest` will fetch the newest version automatically.

### 2. Scaffold a minimal Worker (skip if the project already exists)

A Worker needs a `wrangler.toml` (or `wrangler.jsonc`) and an entry script. Write these with `write_file`:

**`wrangler.jsonc`:**

```jsonc
{
  "name": "hello-agent",
  "main": "src/index.ts",
  "compatibility_date": "2025-01-01"
}
```

**`src/index.ts`:**

```typescript
export default {
  async fetch(): Promise<Response> {
    return new Response("hello cloudflare");
  },
};
```

### 3. Deploy with `--temporary`

From the project directory:

```powershell
npx wrangler@latest deploy --temporary
```

The proof-of-work check adds a short automatic delay. On success Wrangler prints:

- An `Account: <name> (created)` (or `(reused)`) line
- A `Claim URL`
- The live `https://<worker>.<account>.workers.dev` URL

### 4. Parse the URLs

Run the helper to extract them reliably instead of eyeballing the output. Load `scripts/parse_deploy_output.py` from this skill's directory (`~\agent-skills\library\cloudflare-temporary-deploy\scripts\parse_deploy_output.py`):

```powershell
npx wrangler@latest deploy --temporary 2>&1 | python3 scripts/parse_deploy_output.py
```

On Windows, if `python3` is not on PATH, substitute `python`:

```powershell
npx wrangler@latest deploy --temporary 2>&1 | python scripts/parse_deploy_output.py
```

The parser prints JSON:

```json
{"live_url": "...", "claim_url": "...", "account": "...", "account_state": "created|reused", "expires_minutes": 60, "deployed": true}
```

### 5. Verify the deploy is live

Do not trust the deploy log alone. `curl` the live URL and confirm the body matches what the code returns:

```powershell
curl.exe -sS <live_url>
```

### 6. Iterate

Edit the code, redeploy with the same command:

```powershell
npx wrangler@latest deploy --temporary
```

Within the 60-minute window Wrangler reuses the cached temporary account (`Account: <name> (reused)`), so the URL stays stable. `curl` again to confirm the change.

### 7. Hand the claim URL to the user

Tell them: open it within 60 minutes to keep the deployment and any resources; if they don't claim it, everything auto-deletes. Treat the claim URL as a secret — it grants ownership of the account. Do not log it into shared transcripts as "just a link."

## Quick Reference

| Step | Command |
|---|---|
| Check version (need 4.102.0+) | `npx wrangler@latest --version` |
| Deploy (no account) | `npx wrangler@latest deploy --temporary` |
| Deploy + parse URLs | `npx wrangler@latest deploy --temporary 2>&1 \| python3 scripts/parse_deploy_output.py` |
| Verify live | `curl.exe -sS <live_url>` |
| Clear cached temp account | `npx wrangler@latest logout` |

### Temporary Account Product Limits

| Product | Limit on a temporary account |
|---|---|
| Workers | Deploys to `workers.dev` |
| Static Assets | Up to 1,000 files, 5 MiB each |
| KV | Allowed |
| D1 | 1 database, 100 MB per DB / 100 MB total |
| Durable Objects | Allowed |
| Hyperdrive | 2 configs, 10 connections |
| Queues | Up to 10 |
| SSL/TLS certs | Allowed |

## Pitfalls

- **`--temporary` is not in `wrangler deploy --help` and is not a global flag.** It is intentionally hidden and surfaced dynamically: when an unauthenticated `wrangler deploy` fails, Wrangler prints "rerun with `--temporary`". Don't conclude the flag is missing just because `--help` omits it — check the version instead.
- **Old global wrangler.** A stale globally-installed `wrangler` (`< 4.102.0`) silently lacks the flag. Always invoke `npx wrangler@latest` (or a pinned `>=4.102.0`) so you control the version.
- **Auth present → hard error.** If `wrangler login` was ever run, or `CLOUDFLARE_API_TOKEN`/`CLOUDFLARE_API_KEY` is set, `--temporary` errors. Either unset the var for this shell or `wrangler logout`. **Never strip a user's real credentials without telling them.**
- **Rate limiting.** Creating temporary accounts too fast fails. Reuse the cached account (just redeploy) within the 60-minute window instead of forcing a new one; if rate-limited, wait or use a permanent account.
- **60-minute hard expiry, not extendable.** If the deploy must outlive an hour, the user must claim it. Surface this clearly.
- **`curl` may briefly serve the old body after a redeploy.** `workers.dev` has a short edge cache; the `(reused)` line plus a new `Current Version ID` confirm the deploy succeeded even if `curl` shows stale content for a few seconds. Re-curl, or add a cache-busting query string (`?v=2`), before concluding a redeploy failed.
- **Don't log the claim URL into shared transcripts as "just a link."** It is credential-equivalent — anyone with the claim URL owns the account.
- **Windows `curl` alias.** On Windows PowerShell, `curl` may alias to `Invoke-WebRequest`. Always use `curl.exe` to ensure you get the real curl with `-sS` support.
- **`python3` vs `python` on Windows.** If `python3` is not found, fall back to `python`. The parser script works with both.

## Verification

Run these checks to confirm the skill executed correctly:

1. **Version check:**
   ```powershell
   npx wrangler@latest --version
   ```
   Output must be `>= 4.102.0`.

2. **Deploy output check:**
   ```powershell
   npx wrangler@latest deploy --temporary
   ```
   Output must include a `workers.dev` live URL and a `claim-preview?claimToken=` claim URL.

3. **Live URL check:**
   ```powershell
   curl.exe -sS <live_url>
   ```
   Body must match exactly what the Worker code returns (e.g., `hello cloudflare`).

4. **Reuse check (second deploy):**
   ```powershell
   npx wrangler@latest deploy --temporary
   ```
   Output must report `Account: <name> (reused)` and the live URL must be unchanged.

5. **Parser self-test:**
   ```powershell
   python3 scripts/parse_deploy_output.py --selftest
   ```
   (Or `python scripts/parse_deploy_output.py --selftest` on Windows if `python3` is unavailable.) Must exit with code 0 and report all assertions passing.

## Related Skills

- **cloudflare-workers-deploy** — permanent account deploy via `wrangler login` or `CLOUDFLARE_API_TOKEN` for production/CI.
- **cloudflare-workers-dev** — local dev server with `wrangler dev` for pre-deploy testing.
