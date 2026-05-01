---
name: angular-runtime-env-vars
description: Configure runtime environment variables for Angular prerender/static deployments, especially on Azure App Service. Use this skill whenever the user mentions Angular + prerender/static hosting + env vars, runtime-config.js, startup command injection, or stale config values after deploy/restart.
author: "Christian Fleishmann Silva (Oglaf)"
---

# Angular Runtime Env Vars

Use this skill to make Angular prerender/static apps read environment values at runtime instead of baking values at build time.

## What this skill does

1. Detect how runtime config is currently loaded (`window.__...`, `assets/runtime-config.js`, `environment*.ts`, `index.html` script order).
2. Implement or fix server-side injection of environment variables into runtime config on process startup.
3. Ensure stale values are not reused (cache headers for runtime config file).
4. Validate startup/deployment behavior for Azure App Service Linux startup commands.
5. Update docs so the deployed behavior matches implementation.

## Trigger contexts

Apply this skill when the user asks things like:

- "Write a feature flag for my frontend"
- "Make this variable a env var"
- "Should this env var be baked in CI or set on App Service?"
- "Why is API URL still old after changing env var?"
- "runtime-config.js still has old value"
- "Angular prerender env var strategy on Azure"
- "How to support multiple env vars without rebuild"

## Default working mode

Unless user asks analysis-only:

1. Make the code change.
2. Keep change surgical and compatible with current app behavior.
3. Provide concise Azure verification steps.

## Implementation checklist

### 1) Frontend runtime contract

- `src/assets/runtime-config.js` must define a global object, for example:
  - `window.__APP_RUNTIME_CONFIG__ = { apiUrl: '#{API_URL}#' }`
- Angular environments should read from runtime global:
  - `apiUrl: window.__APP_RUNTIME_CONFIG__?.apiUrl || ''`
- `index.html` should load runtime config before main bundle.

### 2) Server-side injection pattern

In `server.js` (or startup server):

- Locate deployed `assets/runtime-config.js`.
- Read runtime variable(s) from `process.env`.
- Replace target keys even if placeholder was already replaced in previous runs.
  - Do not rely only on `#{VAR}#` being present.
- Write updated file before serving requests.
- Log enough details to diagnose path/variable mismatches.

### 3) Caching guardrail

For `/assets/runtime-config.js`, set no-cache headers:

- `Cache-Control: no-store, no-cache, must-revalidate`
- `Pragma: no-cache`
- `Expires: 0`

Other static assets may keep normal cache policy.

### 4) Azure App Service checks

Verify:

1. Startup command points to the intended `server.js`.
2. App setting key names match code (`API_URL` vs legacy keys).
3. App restarts after env var changes.
4. Deployed `assets/runtime-config.js` exists in resolved dist path.

## Troubleshooting heuristics

- **Symptom:** old API URL after env var update  
  **Likely cause:** injection runs only once (placeholder-only replacement) or runtime config is cached.

- **Symptom:** env var appears ignored  
  **Likely cause:** wrong startup script path or wrong env var key.

- **Symptom:** works locally, not on Azure  
  **Likely cause:** dist path mismatch (`dist/app-name` vs `/home/site/wwwroot`).

## Output format

Return:

1. What was changed (files + behavior impact).
2. Exact App Service settings/checks to apply.
3. A short verification sequence (including cache-busted runtime-config URL check).
