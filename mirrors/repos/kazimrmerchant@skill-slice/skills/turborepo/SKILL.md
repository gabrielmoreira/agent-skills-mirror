---
name: turborepo
description: Configures Turborepo v2.8 monorepo pipelines including turbo.json tasks, remote cache, filter and affected CI, boundaries, and microfrontend deploys. Use when orchestrating JS/TS workspace builds or optimizing turbo CI. Not for a single Next.js app with no shared packages, Vercel Functions runtimes (vercel-functions), or package-manager workspaces that never invoke turbo.
version: 1.0.1
metadata:
  priority: 5
  docs:
    - "https://turborepo.dev/docs"
  sitemap: "https://turborepo.dev/sitemap.xml"
  pathPatterns:
    - 'turbo.json'
    - 'turbo/**'
  bashPatterns:
    - '\bturbo\s+(run|build|test|lint|dev|watch|prune|ls|login|link|devtools|docs|boundaries)\b'
    - '\bnpx\s+turbo\b'
    - '\bbunx\s+turbo\b'
    - '\bnpx\s+create-turbo\b'
    - '\bnpx\s+@turbo/codemod\b'
---

# Turborepo

You are an expert in Turborepo v2.8 — the high-performance, Rust-powered build system for JavaScript/TypeScript monorepos by Vercel. Provide precise, actionable guidance for task pipelines, caching, filtering, CI optimization, and architectural boundary enforcement.

## When to Use

Activate this skill when the user is working with any of the following:

- **turbo.json configuration** — defining task pipelines, outputs, inputs, env vars, cache rules
- **Monorepo build orchestration** — multiple apps or packages sharing code
- **CI optimization** — `--affected` flag, remote caching, dynamic matrix jobs
- **Workspace filtering** — `--filter` syntax for scoped task execution
- **Boundary enforcement** — architectural constraints via `boundaries` in turbo.json
- **Microfrontend orchestration** — independent deploys with shared packages
- **Bun workspace support** — lockfile detection, granular cache invalidation
- **Upgrading Turborepo** — codemod migration, version-specific features

**Do NOT recommend Turborepo** for a single Next.js app without shared code — standard Turopack or Next.js built-in tooling is simpler.

## Prerequisites

- **Node.js 18+** (Node 22 recommended for latest features)
- **Package manager**: npm, pnpm, yarn, or Bun (Bun support stable since 2.6; requires `bun.lock` text format)
- **Git** — required for `--affected` and `--filter=[branch]` to compute changed files
- **Windows host (PowerShell)**: Commands below use POSIX-style flags. In PowerShell, wrap glob patterns in single quotes or use `--filter='web...'` to avoid splatting issues. For multi-line YAML in CI, use standard GitHub Actions runners (Ubuntu) — Windows runners are supported but not primary for CI.

## Procedure

### 1. Install or Upgrade Turborepo

```bash
# Create a new monorepo
npx create-turbo@latest

# Add to existing monorepo
npm install turbo --save-dev

# Upgrade existing Turborepo to latest
npx @turbo/codemod migrate
```

### 2. Define turbo.json Task Pipeline

Create or edit `turbo.json` at the repository root:

```json
{
  "$schema": "https://turborepo.dev/schema.json",
  "globalDependencies": [".env"],
  "globalEnv": ["CI", "NODE_ENV"],
  "tasks": {
    "build": {
      "description": "Compile TypeScript and bundle the application",
      "dependsOn": ["^build"],
      "outputs": [".next/**", "dist/**"],
      "env": ["DATABASE_URL", "NEXT_PUBLIC_API_URL"],
      "inputs": ["src/**", "package.json", "tsconfig.json"]
    },
    "test": {
      "description": "Run the test suite",
      "dependsOn": ["build"],
      "outputs": ["coverage/**"],
      "env": ["TEST_DATABASE_URL"]
    },
    "test:unit": {
      "dependsOn": [],
      "outputs": ["coverage/**"]
    },
    "lint": {
      "description": "Lint source files",
      "inputs": ["src/**", ".eslintrc.*"]
    },
    "typecheck": {
      "dependsOn": ["^build"],
      "inputs": ["src/**", "tsconfig.json"]
    },
    "db:generate": {
      "cache": false
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "clean": {
      "cache": false
    }
  }
}
```

**Key configuration fields:**

| Field | Meaning |
|-------|---------|
| `dependsOn: ["^build"]` | Run `build` in dependencies first (`^` = topological) |
| `dependsOn: ["build"]` | Run `build` in the same package first (no `^`) |
| `outputs` | Files to cache (build artifacts) |
| `inputs` | Files that affect the task hash (default: all non-gitignored files) |
| `env` | Environment variables that affect the task hash |
| `cache: false` | Skip caching (dev servers, codegen) |
| `persistent: true` | Long-running tasks (dev servers) |
| `globalDependencies` | Files that invalidate all task caches when changed |
| `globalEnv` | Env vars that invalidate all task caches when changed |

### 3. Composable Configuration (2.7+)

Package-level `turbo.json` can extend from any workspace package:

```json
// packages/ui/turbo.json
{
  "extends": ["@myorg/config"],
  "tasks": {
    "build": {
      "outputs": ["dist/**"]
    }
  }
}
```

### 4. Run Tasks with Workspace Filtering

```bash
# Single package
turbo build --filter=web

# Package and its dependencies
turbo build --filter=web...

# Package and its dependents (what depends on it)
turbo build --filter=...ui

# Multiple packages
turbo build --filter=web --filter=api

# By directory
turbo build --filter=./apps/*

# Packages that changed since main
turbo build --filter=[main]

# Combine: changed packages and their dependents
turbo build --filter=...[main]

# Exclude a package
turbo build --filter=!docs

# Packages matching a pattern
turbo build --filter=@myorg/*
```

**Filter syntax reference:**

| Pattern | Meaning |
|---------|---------|
| `web` | Only the `web` package |
| `web...` | `web` and all its dependencies |
| `...web` | `web` and all its dependents |
| `...web...` | `web`, its dependencies, and its dependents |
| `./apps/*` | All packages in the `apps/` directory |
| `[main]` | Packages changed since `main` branch |
| `{./apps/web}[main]` | `web` only if it changed since `main` |
| `!docs` | Exclude the `docs` package |

### 5. Use --affected for Incremental CI

The single most important CI optimization:

```bash
# Only build/test packages that changed since main
turbo build test lint --affected
```

This performs intelligent graph traversal:
1. Identifies changed files since the base branch
2. Maps changes to affected packages
3. Includes all dependent packages (transitively)
4. Runs tasks only for the affected subgraph

### 6. Set Up Remote Caching

```bash
# Login to Vercel for remote caching
turbo login

# Link to a Vercel team
turbo link

# Builds now share cache across all machines and CI
turbo build
```

For CI, set environment variables (use placeholders — never commit real tokens):

```bash
TURBO_TOKEN=YOUR_TOKEN
TURBO_TEAM=YOUR_TEAM
turbo build
```

### 7. Configure CI Pipeline (GitHub Actions)

**Basic parallel job with --affected:**

```yaml
name: CI
on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Required for --affected
      - uses: actions/setup-node@v4
        with:
          node-version: 22
      - run: npm ci
      - run: turbo build test lint --affected
        env:
          TURBO_TOKEN: ${{ secrets.TURBO_TOKEN }}
          TURBO_TEAM: ${{ vars.TURBO_TEAM }}
```

**Dynamic matrix from workspace list:**

```yaml
jobs:
  detect:
    runs-on: ubuntu-latest
    outputs:
      packages: ${{ steps.list.outputs.packages }}
    steps:
      - uses: actions/checkout@v4
      - id: list
        run: |
          PACKAGES=$(turbo ls --affected --output=json | jq -c '[.[].name]')
          echo "packages=$PACKAGES" >> "$GITHUB_OUTPUT"

  test:
    needs: detect
    if: needs.detect.outputs.packages != '[]'
    runs-on: ubuntu-latest
    strategy:
      matrix:
        package: ${{ fromJson(needs.detect.outputs.packages) }}
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: turbo test --filter=${{ matrix.package }}
```

### 8. Enforce Architectural Boundaries

Add `boundaries` to `turbo.json`:

```json
{
  "boundaries": {
    "tags": {
      "apps/*": ["app"],
      "packages/ui": ["shared", "ui"],
      "packages/utils": ["shared"],
      "packages/config": ["config"]
    },
    "rules": [
      { "from": ["app"], "allow": ["shared"] },
      { "from": ["shared"], "deny": ["app"] }
    ]
  }
}
```

Check compliance:

```bash
turbo boundaries
```

Add to your pipeline:

```json
{
  "tasks": {
    "check": {
      "dependsOn": ["lint", "typecheck", "boundaries"]
    },
    "boundaries": {}
  }
}
```

### 9. Use Watch Mode for Development

```bash
# Watch a specific task — re-executes on file changes
turbo watch test

# Watch with a filter
turbo watch test --filter=web

# Watch multiple tasks
turbo watch test lint
```

Watch mode respects the task graph — if `test` depends on `build`, changing a source file re-runs `build` first, then `test`.

**Persistent tasks vs watch:**
- `persistent: true` in turbo.json: The task itself is long-running (e.g., `next dev`). Turbo starts it and keeps it alive.
- `turbo watch`: Turbo re-invokes the task on file changes. Use for tasks that run and exit (e.g., `vitest run`, `tsc --noEmit`).

### 10. Visualize and Dry-Run the Task Graph

```bash
# Print graph to terminal
turbo build --graph

# Output as DOT format (Graphviz)
turbo build --graph=graph.dot

# Output as JSON
turbo build --graph=graph.json

# Open interactive graph in browser
turbo build --graph=graph.html

# Show tasks that would run without executing
turbo build --dry-run

# JSON output for programmatic use
turbo build --dry-run=json
```

### 11. Prune for Single-App Deployment

```bash
# Generate minimal monorepo for deploying a single app
turbo prune web --docker
```

### 12. Devtools & AI Docs (2.8+)

```bash
# Visual package/task graph explorer (hot-reloads on changes)
turbo devtools

# Search Turborepo docs from the terminal (returns agent-friendly markdown)
turbo docs
```

> `turbo docs` output is optimized for AI coding agents — markdown format preserves context windows.

### 13. Bun Workspace Support (2.6+)

```bash
# Ensure text lockfile for Turborepo compatibility
bun install --save-text-lockfile

# Run only affected packages (works with Bun lockfile detection)
turbo build --affected
```

Turborepo parses `bun.lock` (text format) for granular cache invalidation — only affected tasks are invalidated, not the entire monorepo. If only `bun.lockb` (binary) is found, Turborepo errors with a prompt to generate a text lockfile.

### 14. Microfrontend Orchestration

Structure for independent deploys with shared packages:

```
my-platform/
├── turbo.json
├── package.json
├── apps/
│   ├── shell/          # Layout / shell app (owns top-level routing)
│   ├── dashboard/      # Micro-app
│   ├── settings/       # Micro-app
│   └── marketing/      # Micro-app
└── packages/
    ├── ui/             # Shared component library
    ├── auth/           # Shared auth utilities
    └── config/         # Shared tsconfig, eslint
```

```bash
# Deploy only the dashboard micro-app
turbo build --filter=dashboard

# Deploy all micro-apps in parallel
turbo build --filter=./apps/*

# Deploy only micro-apps that changed since main
turbo build --filter=./apps/*...[main]
```

Combine with boundary rules to enforce architectural isolation:

```json
{
  "boundaries": {
    "tags": {
      "apps/*": ["micro-app"],
      "packages/ui": ["shared"],
      "packages/auth": ["shared"]
    },
    "rules": [
      { "from": ["micro-app"], "allow": ["shared"] },
      { "from": ["shared"], "deny": ["micro-app"] }
    ]
  }
}
```

**When to use Turborepo for microfrontends:**

| Scenario | Recommended? |
|----------|-------------|
| Multiple teams owning independent features | Yes — independent deploys + shared packages |
| Single team, single app | No — standard Next.js is simpler |
| Shared component library across apps | Yes — `packages/ui` with boundary rules |
| Gradual migration from monolith | Yes — extract features into micro-apps incrementally |
| Need version-skew protection | Yes — isolated builds per micro-app |

## Pitfalls

- **`fetch-depth: 0` is mandatory for `--affected`** — Without full git history, Turborepo cannot compute changed files. Always set `fetch-depth: 0` in `actions/checkout`.
- **Bun binary lockfile (`bun.lockb`) is not supported** — Turborepo requires `bun.lock` text format. Run `bun install --save-text-lockfile` to generate it. Without it, Turborepo errors.
- **`turbo prune` with Bun 1.3+ may produce broken lockfiles** — Known issue: formatting differences can break `bun i --frozen-lockfile`. Track fixes at [turborepo#11007](https://github.com/vercel/turborepo/issues/11007).
- **Forgetting `outputs` means no caching** — If you don't declare `outputs`, Turborepo caches the task exit code but not artifacts. Always specify build output directories.
- **`persistent: true` tasks cannot be cached** — Always set `cache: false` alongside `persistent: true` for dev servers. Turbo will warn if you don't.
- **`inputs` too narrow can cause stale caches** — If you specify `inputs` and miss a file (e.g., `.env`), changes to that file won't invalidate the cache. Use `globalDependencies` for root-level files.
- **PowerShell glob splatting** — In PowerShell, `--filter=web...` may be interpreted as splatting. Wrap in single quotes: `--filter='web...'`.
- **Remote cache token leakage** — Never hardcode `TURBO_TOKEN` in source files or turbo.json. Use CI secrets or `.env` (gitignored). Use `YOUR_TOKEN` placeholders in documentation.
- **`^build` vs `build` confusion** — `^build` means "build my dependencies first" (topological). `build` (no `^`) means "build this same package first" (sequential within package). Mixing these up causes circular dependencies or missing builds.
- **Composable config `extends` requires published package** — The `extends` field references a workspace package name, not a file path. The package must exist in the workspace and be resolvable.

## Verification

### Verify Turborepo is installed and version is correct

```bash
npx turbo --version
# Expected: 2.8.x or higher
```

### Verify task graph is valid

```bash
turbo build --dry-run
# Expected: lists all tasks that would execute with cache status (HIT/MISS)
```

### Verify caching works

```bash
# First run — should be MISS
turbo build

# Second run — should be HIT
turbo build
# Expected output: "FULL TURBO" or cache HIT messages
```

### Verify --affected detects changes correctly

```bash
# On main branch, make a change to one package
git checkout -b test-affected
echo "// test" >> packages/ui/src/index.ts
git add -A && git commit -m "test"

# Run affected — should only show ui and its dependents
turbo build --affected
# Expected: only packages that depend on ui are built
```

### Verify boundary rules pass

```bash
turbo boundaries
# Expected: no violations, exit code 0
```

### Verify remote cache is connected

```bash
turbo login
# Expected: browser opens for Vercel authentication

turbo link
# Expected: links to your Vercel team

turbo build
# Expected: "Remote cache HIT" or "Remote cache MISS" in output
```

### Verify Bun lockfile compatibility

```bash
# Check lockfile format
ls bun.lock
# If only bun.lockb exists:
bun install --save-text-lockfile
ls bun.lock  # Should now exist
```

## Examples

### Minimal turbo.json for a Next.js + API monorepo

```json
{
  "$schema": "https://turborepo.dev/schema.json",
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": [".next/**", "dist/**"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "lint": {},
    "test": {
      "dependsOn": ["build"]
    }
  }
}
```

### Standard monorepo structure

```
my-monorepo/
├── turbo.json
├── package.json
├── apps/
│   ├── web/           # Next.js app
│   ├── api/           # Backend service
│   └── docs/          # Documentation site
├── packages/
│   ├── ui/            # Shared component library
│   ├── config/        # Shared configs (eslint, tsconfig)
│   └── utils/         # Shared utilities
└── node_modules/
```

## Related skills

- **nextjs** — Next.js app configuration and deployment
- **vercel** — Vercel deployment platform integration
- **github-actions** — CI/CD pipeline configuration
- **bun** — Bun runtime and package manager

## Official Documentation

- [Turborepo Documentation](https://turborepo.dev/docs)
- [Getting Started](https://turborepo.dev/docs/getting-started)
- [Crafting Your Repository](https://turborepo.dev/docs/crafting-your-repository)
- [Task Configuration](https://turborepo.dev/docs/reference/configuration)
- [Filtering](https://turborepo.dev/docs/crafting-your-repository/running-tasks#using-filters)
- [GitHub: Turborepo](https://github.com/vercel/turborepo)
- [Vercel Microfrontends](https://vercel.com/docs/microfrontends)
- [Next.js Multi-Zones](https://nextjs.org/docs/app/building-your-application/deploying/multi-zones)
