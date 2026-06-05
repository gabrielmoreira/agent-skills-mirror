# Environment — deployment and runtime for pds-pipeline

**Scope**: Authoritative for pds-pipeline/ directory
**Last Updated**: 2026-05-27

> This file extends the root .ai/environment.md with pds-pipeline-specific patterns.

> **→ [Master Environment Guide](../.ai/environment.md)** — project-wide environment and deployment rules.

---

## Deployment Environments

| Environment | Runtime | Notes |
|-------------|---------|-------|
| VS Code extension webview | Chromium (embedded) | Bundled by esbuild; no require() |
| Railway server (API) | Node.js | Compiled via tsc; served as CommonJS |

> **Portability Requirement**: the package must run in both environments without modification.

---

## Railway Build Configuration

WEB-HMI/api/railway.toml:

```toml
buildCommand = cd PDS-Pipeline && npm ci && npm run build && cd ../WEB-HMI/api && npm ci && npm run build
startCommand = node WEB-HMI/api/dist/index.js
```

Steps:

1. Build PDS-Pipeline generates dist/ with compiled JS + .d.ts types
2. Install API deps (npm ci) creates the file:../PDS-Pipeline symlink in node_modules/@pds/pipeline
3. Compile API (tsc) resolves types from @pds/pipeline/dist/index.d.ts

---

## Local Development

```sh
cd PDS-Pipeline && npm ci && npm run build
cd ../WEB-HMI/api && npm install && npm run build
```

---

## Environment Variables

| Variable | Required | Default | Description |

# Note: This package is environment-agnostic and uses no env vars directly.

# Environment variables are used by consumers (WEB-HMI/api, PDS-vscode-extension).

# See consumer module docs for required env vars.
