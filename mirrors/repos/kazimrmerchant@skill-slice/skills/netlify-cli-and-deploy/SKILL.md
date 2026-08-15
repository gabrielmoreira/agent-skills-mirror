---
name: netlify-cli-and-deploy
description: "Operates the Netlify CLI: install, login or NETLIFY_AUTH_TOKEN, site link, Git or manual deploy, netlify dev / Vite plugin, and context-scoped env vars. Use when the user runs netlify, deploys to Netlify, or needs netlify env import/export. Not for Vercel env (env-vars), Cloudflare Workers (wrangler), or GitHub Actions workflow YAML. Never commit personal access tokens or deploy secrets in tracked scripts."
version: 1.0.1
---

# Netlify CLI and Deployment

## Overview

This skill covers the full lifecycle of working with the Netlify CLI: installation, authentication, site linking, deployment (Git-based continuous deployment and manual uploads), local development via `netlify dev` or the Netlify Vite Plugin, and environment variable management with context scoping. Use it whenever a task involves Netlify deployment, local dev with Netlify primitives, or env var configuration.

## When to Use

- Installing or upgrading the Netlify CLI (`netlify-cli`)
- Authenticating with Netlify (interactive login or CI token)
- Linking a local project to an existing Netlify site or creating a new one
- Deploying via Git-based continuous deployment or manual upload
- Running local development with `netlify dev` or the Netlify Vite Plugin
- Managing environment variables (set, get, list, import, unset) with context scoping
- Exporting or importing `.env` files for Netlify projects

## Prerequisites

- **Node.js 18.14.0+** installed and on PATH
- **npm** available (comes with Node.js)
- On Windows (PowerShell), ensure `npm` global bin directory is on your `PATH` so `netlify` resolves after global install
- For CI deployments: a `NETLIFY_AUTH_TOKEN` environment variable set (generate from the Netlify UI under User Settings → Applications → Personal access tokens)

## Procedure

### 1. Install the CLI

```bash
# Global install (for local development)
npm install -g netlify-cli

# Local install as dev dependency (for CI pipelines)
npm install netlify-cli -D
```

Verify installation:

```bash
netlify --version
```

### 2. Authenticate

**Interactive (local machine):**

```bash
netlify login       # Opens browser for OAuth flow
netlify status      # Check auth + linked site status
```

**CI / headless:**

Set the `NETLIFY_AUTH_TOKEN` environment variable instead of `netlify login`. In PowerShell:

```powershell
$env:NETLIFY_AUTH_TOKEN = "YOUR_TOKEN"
```

Or in a CI provider's secret configuration, set `NETLIFY_AUTH_TOKEN` to a personal access token.

### 3. Link a Site

First check if already linked:

```bash
netlify status
```

If not linked, choose one of the following:

```bash
# Interactive — prompts to select from your sites or enter a site ID
netlify link

# By Git remote URL (if the repo is connected to Netlify)
netlify link --git-remote-url https://github.com/org/repo

# Create a new site with Git CI/CD setup
netlify init

# Create a new site without Git CI/CD (manual deploys only)
netlify init --manual
```

The site ID is stored in `.netlify/state.json`. **Add `.netlify` to `.gitignore`** so it is never committed.

### 4. Deploy

#### 4a. Git-Based Continuous Deployment

Set up with `netlify init`. After setup, automatic deploys trigger on Git events:

| Git Action | Deploy Type |
|---|---|
| Push to production branch | Production deploy |
| Open a pull request | Deploy preview with unique URL |
| Push to other branches | Branch deploy |

The build runs on Netlify's servers. Configure build settings in `netlify.toml`:

```toml
[build]
  command = "npm run build"
  publish = "dist"
```

#### 4b. Manual / Local Deploys (No Git Required)

Build locally, then upload the output directory:

```bash
# Draft deploy — returns a preview URL, does not go to production
netlify deploy

# Production deploy
netlify deploy --prod

# Specify output directory explicitly
netlify deploy --dir=dist

# Production deploy with explicit directory
netlify deploy --prod --dir=dist
```

This works without Git — useful for prototypes, local-only projects, or CI pipelines that build artifacts before uploading.

### 5. Local Development

#### Option A: `netlify dev`

```bash
netlify dev
```

Wraps your framework's existing dev server and provides:

- Environment variable injection from Netlify
- Functions and edge functions execution
- Redirects and headers processing

#### Option B: Netlify Vite Plugin (Vite-based projects)

For projects using Vite (React SPA, TanStack Start, SvelteKit, Remix), the Vite plugin provides Netlify platform primitives directly in the framework's dev server — no `netlify dev` wrapper needed:

```bash
npm install @netlify/vite-plugin
```

```typescript
// vite.config.ts
import netlify from "@netlify/vite-plugin";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [netlify()],
});
```

Then run your normal dev command (`npm run dev`). This gives access to Blobs, DB, Functions, and environment variables during development.

> **See the `netlify-frameworks` skill for framework-specific local dev guidance.**

### 6. Environment Variables

#### CLI Management

```bash
# Set a variable
netlify env:set API_KEY "value"

# Set as secret (hidden from logs)
netlify env:set API_KEY "value" --secret

# Set for a specific deploy context
netlify env:set API_KEY "value" --context production

# Get a variable's value
netlify env:get API_KEY

# List all variables
netlify env:list

# Export to a .env file (plain text, no decoration)
netlify env:list --plain > .env

# Import from a .env file
netlify env:import .env

# Delete a variable
netlify env:unset API_KEY
```

#### Context Scoping

Variables can be scoped to deploy contexts:

```bash
netlify env:set API_URL "https://api.prod.com" --context production
netlify env:set API_URL "https://api.staging.com" --context deploy-preview
netlify env:set DEBUG "true" --context branch:feature-x
```

#### Accessing Variables in Code

| Environment | Access Method |
|---|---|
| Server-side (Functions) | `Netlify.env.get("VAR")` (preferred) or `process.env.VAR` |
| Client-side (Vite) | `import.meta.env.VITE_VAR` (only `VITE_`-prefixed vars) |
| Client-side (Astro) | `import.meta.env.PUBLIC_VAR` (only `PUBLIC_`-prefixed vars) |

**HARD RULE: Never use `VITE_` or `PUBLIC_` prefix for secrets.** These prefixes expose the value to the browser bundle. Use unprefixed names for secrets and access them only server-side.

### 7. Useful Commands Reference

| Command | Description |
|---|---|
| `netlify status` | Auth and site link status |
| `netlify dev` | Start local dev server with Netlify primitives |
| `netlify build` | Run build locally (mimics Netlify environment) |
| `netlify deploy` | Draft deploy (preview URL) |
| `netlify deploy --prod` | Production deploy |
| `netlify deploy --dir=dist` | Deploy from specific output directory |
| `netlify dev:exec <cmd>` | Run a command with Netlify environment loaded |
| `netlify env:list` | List environment variables |
| `netlify env:import .env` | Import env vars from a file |
| `netlify env:list --plain > .env` | Export env vars to a file |
| `netlify clone org/repo` | Clone, link, and set up in one step |

## Pitfalls

1. **Committing `.netlify/`** — The `.netlify/state.json` file contains the site ID and should never be committed. Add `.netlify` to `.gitignore` immediately after linking.

2. **Using `VITE_` or `PUBLIC_` prefix for secrets** — These prefixes inline the variable value into the client-side JavaScript bundle. Anyone can read them in the browser. Always use unprefixed names for secrets and access them only in server-side Functions.

3. **Forgetting `--prod` on deploy** — `netlify deploy` without `--prod` creates a draft deploy with a temporary preview URL. It will not update your production site. Always use `netlify deploy --prod` when you intend to update production.

4. **Wrong publish directory** — If `netlify deploy --dir=dist` points to a directory that doesn't exist or is empty, the deploy will succeed but serve a blank site. Verify the build output directory exists before deploying.

5. **Node.js version mismatch** — The CLI requires Node.js 18.14.0+. Running an older Node version will produce cryptic errors. Check with `node --version`.

6. **CI without auth token** — `netlify login` opens a browser and cannot work in CI. You must set `NETLIFY_AUTH_TOKEN` as an environment variable in your CI provider's secret store.

7. **Env var context confusion** — Variables set without a `--context` flag apply to all contexts. If you set a production-specific value without `--context production`, it will override or be overridden by context-specific values in unexpected ways. Always scope with `--context` when values differ across environments.

8. **`netlify dev` port conflicts** — `netlify dev` may pick a port that conflicts with another running process. If the dev server fails to start, check for port conflicts or specify a port via your framework's config.

## Verification

### Verify CLI installation

```bash
netlify --version
```

Expected: a version number string (e.g., `17.x.x`).

### Verify authentication and site link

```bash
netlify status
```

Expected output includes:
- `Logged in as: your-email@example.com`
- `Current site: <site-name>` or a message indicating no site is linked

### Verify a draft deploy

```bash
netlify deploy --dir=dist
```

Expected: output ending with a `Website Draft URL: https://<deploy-id>--<site-name>.netlify.app` link. Open the URL to confirm the site renders correctly.

### Verify a production deploy

```bash
netlify deploy --prod --dir=dist
```

Expected: output ending with `Unique Deploy URL:` and `Live URL: https://<site-name>.netlify.app`.

### Verify environment variables

```bash
netlify env:list
```

Expected: a table listing all variable names and their scopes. Confirm secrets show as `*****` or are hidden if set with `--secret`.

### Verify local dev server

```bash
netlify dev
```

Expected: the framework dev server starts, and Netlify prints a message like `◈ Server now ready on http://localhost:8888`. Open the URL to confirm the app loads with env vars and functions working.

## Related Skills

- **netlify-frameworks** — Framework-specific local dev guidance for Next.js, Astro, Remix, SvelteKit, TanStack Start, and other frameworks on Netlify.
