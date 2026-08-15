---
name: wrangler
description: "Runs Cloudflare Wrangler v4+: wrangler.jsonc, deploy/dev, KV/R2/D1/Vectorize/Hyperdrive/Queues/Workflows/Pages, secrets, types, and tail. Use when editing wrangler config, bindings, or any wrangler command. Not for Cloudflare Agents SDK application code (building-ai-agent-on-cloudflare) or Vercel/Netlify CLIs. Never trust baked-in flag knowledge — fetch developers.cloudflare.com/workers/wrangler first."
version: 1.0.1
---

# Wrangler CLI

Your knowledge of Wrangler CLI flags, config fields, and subcommands may be outdated. **Prefer retrieval over pre-training** for any Wrangler task. Fetch the latest docs before writing or reviewing commands and config.

## When to Use

Load this skill whenever you need to:

- Create, deploy, or manage Cloudflare Workers (`wrangler init`, `wrangler deploy`, `wrangler dev`)
- Edit `wrangler.jsonc` or `wrangler.toml` configuration files
- Provision or manage bindings: KV, R2, D1, Vectorize, Hyperdrive, Workers AI, Queues, Workflows, Pipelines, Containers, Secrets Store, Durable Objects
- Debug Worker deployment, local dev, or type generation issues
- Run migrations, manage secrets, or tail logs
- Set up Cloudflare Pages projects

Trigger keywords: `wrangler`, `cloudflare workers`, `wrangler.jsonc`, `wrangler.toml`, `worker deploy`, `kv namespace`, `r2 bucket`, `d1 database`, `vectorize`, `hyperdrive`, `workers ai`, `cloudflare pages`, `durable objects`, `wrangler tail`, `wrangler types`.

## Prerequisites

1. **Node.js** installed (LTS recommended).
2. **Wrangler v4.x+** installed locally or as a dev dependency.
3. **Cloudflare account** authenticated via `wrangler login` or `CLOUDFLARE_API_TOKEN` env var.
4. On Windows (PowerShell), use `npx wrangler` or ensure `wrangler` is in PATH. Line continuations differ: use backtick `` ` `` in PowerShell instead of `\`.

## Procedure

### 1. Verify Installation

```bash
wrangler --version  # Requires v4.x+
```

If not installed:

```bash
npm install -D wrangler@latest
```

### 2. Retrieve Latest Docs Before Writing Commands

Before writing or reviewing Wrangler commands and config, fetch the latest information. Do not rely on baked-in knowledge for CLI flags, config fields, or binding shapes.

| Source | How to retrieve | Use for |
|--------|----------------|---------|
| Wrangler docs | `https://developers.cloudflare.com/workers/wrangler/` | CLI commands, flags, config reference |
| Wrangler config schema | `node_modules/wrangler/config-schema.json` | Config fields, binding shapes, allowed values |
| Cloudflare docs | Search tool or `https://developers.cloudflare.com/workers/` | API reference, compatibility dates/flags |

### 3. Initialize a New Worker

```bash
# Initialize new project
npx wrangler init my-worker

# Or with a framework
npx create-cloudflare@latest my-app
```

### 4. Configure `wrangler.jsonc`

Prefer JSON config (`wrangler.jsonc`) over TOML. Newer features are JSON-only.

**Minimal config:**

```jsonc
{
  "$schema": "./node_modules/wrangler/config-schema.json",
  "name": "my-worker",
  "main": "src/index.ts",
  "compatibility_date": "2026-03-18"
}
```

**Full config with bindings:**

```jsonc
{
  "$schema": "./node_modules/wrangler/config-schema.json",
  "name": "my-worker",
  "main": "src/index.ts",
  "compatibility_date": "2026-03-18",
  "compatibility_flags": ["nodejs_compat_v2"],

  // Environment variables
  "vars": {
    "ENVIRONMENT": "production"
  },

  // KV Namespace
  "kv_namespaces": [
    { "binding": "KV", "id": "<KV_NAMESPACE_ID>" }
  ],

  // R2 Bucket
  "r2_buckets": [
    { "binding": "BUCKET", "bucket_name": "my-bucket" }
  ],

  // D1 Database
  "d1_databases": [
    { "binding": "DB", "database_name": "my-db", "database_id": "<DB_ID>" }
  ],

  // Workers AI (always remote)
  "ai": { "binding": "AI" },

  // Vectorize
  "vectorize": [
    { "binding": "VECTOR_INDEX", "index_name": "my-index" }
  ],

  // Hyperdrive
  "hyperdrive": [
    { "binding": "HYPERDRIVE", "id": "<HYPERDRIVE_ID>" }
  ],

  // Durable Objects
  "durable_objects": {
    "bindings": [
      { "name": "COUNTER", "class_name": "Counter" }
    ]
  },

  // Cron triggers
  "triggers": {
    "crons": ["0 * * * *"]
  },

  // Environments
  "env": {
    "staging": {
      "name": "my-worker-staging",
      "vars": { "ENVIRONMENT": "staging" }
    }
  }
}
```

### 5. Generate TypeScript Types After Config Changes

```bash
# Generate worker-configuration.d.ts
wrangler types

# Custom output path
wrangler types ./src/env.d.ts

# Check types are up to date (CI)
wrangler types --check
```

### 6. Local Development

```bash
# Local mode (default) - uses local storage simulation
wrangler dev

# With specific environment
wrangler dev --env staging

# Force local-only (disable remote bindings)
wrangler dev --local

# Remote mode - runs on Cloudflare edge (legacy)
wrangler dev --remote

# Custom port
wrangler dev --port 8787

# Live reload for HTML changes
wrangler dev --live-reload

# Test scheduled/cron handlers
wrangler dev --test-scheduled
# Then visit: http://localhost:8787/__scheduled
```

**Remote bindings for local dev** — use `remote: true` in binding config to connect to real resources while running locally:

```jsonc
{
  "r2_buckets": [
    { "binding": "BUCKET", "bucket_name": "my-bucket", "remote": true }
  ],
  "ai": { "binding": "AI", "remote": true },
  "vectorize": [
    { "binding": "INDEX", "index_name": "my-index", "remote": true }
  ]
}
```

Recommended remote bindings: AI (required), Vectorize, Browser Rendering, mTLS, Images.

**Local secrets** — create `.dev.vars` for local development secrets:

```
API_KEY=local-dev-key
DATABASE_URL=postgres://localhost:5432/dev
```

### 7. Deploy

```bash
# Deploy to production
wrangler deploy

# Deploy specific environment
wrangler deploy --env staging

# Dry run (validate without deploying)
wrangler deploy --dry-run

# Keep dashboard-set variables
wrangler deploy --keep-vars

# Minify code
wrangler deploy --minify
```

### 8. Manage Secrets

```bash
# Set secret interactively
wrangler secret put API_KEY

# Set from stdin
echo "secret-value" | wrangler secret put API_KEY

# List secrets
wrangler secret list

# Delete secret
wrangler secret delete API_KEY

# Bulk secrets from JSON file
wrangler secret bulk secrets.json
```

### 9. Versions and Rollback

```bash
# List recent versions
wrangler versions list

# View specific version
wrangler versions view <VERSION_ID>

# Rollback to previous version
wrangler rollback

# Rollback to specific version
wrangler rollback <VERSION_ID>
```

### 10. KV (Key-Value Store)

**Manage namespaces:**

```bash
# Create namespace
wrangler kv namespace create MY_KV

# List namespaces
wrangler kv namespace list

# Delete namespace
wrangler kv namespace delete --namespace-id <ID>
```

**Manage keys:**

```bash
# Put value
wrangler kv key put --namespace-id <ID> "key" "value"

# Put with expiration (seconds)
wrangler kv key put --namespace-id <ID> "key" "value" --expiration-ttl 3600

# Get value
wrangler kv key get --namespace-id <ID> "key"

# List keys
wrangler kv key list --namespace-id <ID>

# Delete key
wrangler kv key delete --namespace-id <ID> "key"

# Bulk put from JSON
wrangler kv bulk put --namespace-id <ID> data.json
```

**Config binding:**

```jsonc
{
  "kv_namespaces": [
    { "binding": "CACHE", "id": "<NAMESPACE_ID>" }
  ]
}
```

### 11. R2 (Object Storage)

**Manage buckets:**

```bash
# Create bucket
wrangler r2 bucket create my-bucket

# Create with location hint
wrangler r2 bucket create my-bucket --location wnam

# List buckets
wrangler r2 bucket list

# Get bucket info
wrangler r2 bucket info my-bucket

# Delete bucket
wrangler r2 bucket delete my-bucket
```

**Manage objects:**

```bash
# Upload object
wrangler r2 object put my-bucket/path/file.txt --file ./local-file.txt

# Download object
wrangler r2 object get my-bucket/path/file.txt

# Delete object
wrangler r2 object delete my-bucket/path/file.txt
```

**Config binding:**

```jsonc
{
  "r2_buckets": [
    { "binding": "ASSETS", "bucket_name": "my-bucket" }
  ]
}
```

### 12. D1 (SQL Database)

**Manage databases:**

```bash
# Create database
wrangler d1 create my-database

# Create with location
wrangler d1 create my-database --location wnam

# List databases
wrangler d1 list

# Get database info
wrangler d1 info my-database

# Delete database
wrangler d1 delete my-database
```

**Execute SQL:**

```bash
# Execute SQL command (remote)
wrangler d1 execute my-database --remote --command "SELECT * FROM users"

# Execute SQL file (remote)
wrangler d1 execute my-database --remote --file ./schema.sql

# Execute locally
wrangler d1 execute my-database --local --command "SELECT * FROM users"
```

**Migrations:**

```bash
# Create migration
wrangler d1 migrations create my-database create_users_table

# List pending migrations
wrangler d1 migrations list my-database --local

# Apply migrations locally
wrangler d1 migrations apply my-database --local

# Apply migrations to remote
wrangler d1 migrations apply my-database --remote
```

**Export/Backup:**

```bash
# Export schema and data
wrangler d1 export my-database --remote --output backup.sql

# Export schema only
wrangler d1 export my-database --remote --output schema.sql --no-data
```

**Config binding:**

```jsonc
{
  "d1_databases": [
    {
      "binding": "DB",
      "database_name": "my-database",
      "database_id": "<DATABASE_ID>",
      "migrations_dir": "./migrations"
    }
  ]
}
```

### 13. Vectorize (Vector Database)

**Manage indexes:**

```bash
# Create index with dimensions
wrangler vectorize create my-index --dimensions 768 --metric cosine

# Create with preset (auto-configures dimensions/metric)
wrangler vectorize create my-index --preset @cf/baai/bge-base-en-v1.5

# List indexes
wrangler vectorize list

# Get index info
wrangler vectorize get my-index

# Delete index
wrangler vectorize delete my-index
```

**Manage vectors:**

```bash
# Insert vectors from NDJSON file
wrangler vectorize insert my-index --file vectors.ndjson

# Query vectors
wrangler vectorize query my-index --vector "[0.1, 0.2, ...]" --top-k 10
```

**Config binding:**

```jsonc
{
  "vectorize": [
    { "binding": "SEARCH_INDEX", "index_name": "my-index" }
  ]
}
```

### 14. Hyperdrive (Database Accelerator)

**Manage configs:**

```bash
# Create config
wrangler hyperdrive create my-hyperdrive --connection-string "postgres://user:pass@host:5432/database"

# List configs
wrangler hyperdrive list

# Get config details
wrangler hyperdrive get <HYPERDRIVE_ID>

# Update config
wrangler hyperdrive update <HYPERDRIVE_ID> --origin-password "new-password"

# Delete config
wrangler hyperdrive delete <HYPERDRIVE_ID>
```

**Config binding:**

```jsonc
{
  "compatibility_flags": ["nodejs_compat_v2"],
  "hyperdrive": [
    { "binding": "HYPERDRIVE", "id": "<HYPERDRIVE_ID>" }
  ]
}
```

### 15. Workers AI

```bash
# List available models
wrangler ai models

# List finetunes
wrangler ai finetune list
```

**Config binding:**

```jsonc
{
  "ai": { "binding": "AI" }
}
```

> **HARD RULE**: Workers AI always runs remotely and incurs usage charges even in local dev. Never assume local simulation for AI bindings.

### 16. Queues

**Manage queues:**

```bash
# Create queue
wrangler queues create my-queue

# List queues
wrangler queues list

# Delete queue
wrangler queues delete my-queue

# Add consumer to queue
wrangler queues consumer add my-queue my-worker

# Remove consumer
wrangler queues consumer remove my-queue my-worker
```

**Config binding:**

```jsonc
{
  "queues": {
    "producers": [
      { "binding": "MY_QUEUE", "queue": "my-queue" }
    ],
    "consumers": [
      {
        "queue": "my-queue",
        "max_batch_size": 10,
        "max_batch_timeout": 30
      }
    ]
  }
}
```

### 17. Containers

**Build and push images:**

```bash
# Build container image
wrangler containers build -t my-app:latest .

# Build and push in one command
wrangler containers build -t my-app:latest . --push

# Push existing image to Cloudflare registry
wrangler containers push my-app:latest
```

**Manage containers:**

```bash
# List containers
wrangler containers list

# Get container info
wrangler containers info <CONTAINER_ID>

# Delete container
wrangler containers delete <CONTAINER_ID>
```

**Manage images:**

```bash
# List images in registry
wrangler containers images list

# Delete image
wrangler containers images delete my-app:latest
```

**Manage external registries:**

```bash
# List configured registries
wrangler containers registries list

# Configure external registry (e.g., ECR)
wrangler containers registries configure <DOMAIN> --public-credential <AWS_ACCESS_KEY_ID>

# Delete registry configuration
wrangler containers registries delete <DOMAIN>
```

### 18. Workflows

**Manage workflows:**

```bash
# List workflows
wrangler workflows list

# Describe workflow
wrangler workflows describe my-workflow

# Trigger workflow instance
wrangler workflows trigger my-workflow

# Trigger with parameters
wrangler workflows trigger my-workflow --params '{"key": "value"}'

# Delete workflow
wrangler workflows delete my-workflow
```

**Manage workflow instances:**

```bash
# List instances
wrangler workflows instances list my-workflow

# Describe instance
wrangler workflows instances describe my-workflow <INSTANCE_ID>

# Terminate instance
wrangler workflows instances terminate my-workflow <INSTANCE_ID>
```

**Config binding:**

```jsonc
{
  "workflows": [
    {
      "binding": "MY_WORKFLOW",
      "name": "my-workflow",
      "class_name": "MyWorkflow"
    }
  ]
}
```

### 19. Pipelines

**Manage pipelines:**

```bash
# Create pipeline
wrangler pipelines create my-pipeline --r2 my-bucket

# List pipelines
wrangler pipelines list

# Show pipeline details
wrangler pipelines show my-pipeline

# Update pipeline
wrangler pipelines update my-pipeline --batch-max-mb 100

# Delete pipeline
wrangler pipelines delete my-pipeline
```

**Config binding:**

```jsonc
{
  "pipelines": [
    { "binding": "MY_PIPELINE", "pipeline": "my-pipeline" }
  ]
}
```

### 20. Secrets Store

**Manage stores:**

```bash
# Create store
wrangler secrets-store store create my-store

# List stores
wrangler secrets-store store list

# Delete store
wrangler secrets-store store delete <STORE_ID>
```

**Manage secrets in store:**

```bash
# Add secret to store
wrangler secrets-store secret put <STORE_ID> my-secret

# List secrets in store
wrangler secrets-store secret list <STORE_ID>

# Get secret
wrangler secrets-store secret get <STORE_ID> my-secret

# Delete secret from store
wrangler secrets-store secret delete <STORE_ID> my-secret
```

**Config binding:**

```jsonc
{
  "secrets_store_secrets": [
    {
      "binding": "MY_SECRET",
      "store_id": "<STORE_ID>",
      "secret_name": "my-secret"
    }
  ]
}
```

### 21. Pages (Frontend Deployment)

```bash
# Create Pages project
wrangler pages project create my-site

# Deploy directory to Pages
wrangler pages deploy ./dist

# Deploy with specific branch
wrangler pages deploy ./dist --branch main

# List deployments
wrangler pages deployment list --project-name my-site
```

### 22. Observability

**Tail logs:**

```bash
# Stream live logs
wrangler tail

# Tail specific Worker
wrangler tail my-worker

# Filter by status
wrangler tail --status error

# Filter by search term
wrangler tail --search "error"

# JSON output
wrangler tail --format json
```

**Config logging:**

```jsonc
{
  "observability": {
    "enabled": true,
    "head_sampling_rate": 1
  }
}
```

### 23. Testing with Vitest

```bash
npm install -D @cloudflare/vitest-pool-workers vitest
```

`vitest.config.ts`:

```typescript
import { defineWorkersConfig } from "@cloudflare/vitest-pool-workers/config";

export default defineWorkersConfig({
  test: {
    poolOptions: {
      workers: {
        wrangler: { configPath: "./wrangler.jsonc" },
      },
    },
  },
});
```

**Test scheduled events:**

```bash
# Enable in dev
wrangler dev --test-scheduled

# Trigger via HTTP
curl http://localhost:8787/__scheduled
```

## Pitfalls

| Issue | Solution |
|-------|----------|
| `command not found: wrangler` | Install: `npm install -D wrangler` |
| Auth errors | Run `wrangler login` or set `CLOUDFLARE_API_TOKEN` |
| Config validation errors | Run `wrangler check` before deploy |
| Type errors after config change | Run `wrangler types` to regenerate bindings |
| Local storage not persisting | Check `.wrangler/state` directory exists and is writable |
| Binding undefined in Worker | Verify binding name in code matches config `binding` field exactly |
| Workers AI charges in local dev | AI always runs remotely; there is no local simulation |
| `compatibility_date` too old | Update to a date within 30 days of today; check compatibility dates docs |
| TOML config missing newer features | Switch to `wrangler.jsonc`; newer features are JSON-only |
| Secrets committed to config | Use `.dev.vars` for local secrets; use `wrangler secret put` for production |
| PowerShell line continuation errors | Use backtick `` ` `` instead of `\` for multi-line commands on Windows |
| Binding name mismatch | The `binding` field in config must match the property accessed on `env` in code |

**HARD RULES:**

1. **Never commit real secrets** to `wrangler.jsonc`, `.dev.vars`, or any tracked file. Use `wrangler secret put` for production and `.dev.vars` (gitignored) for local dev.
2. **Always run `wrangler types`** after changing any binding in config. Stale types cause silent runtime errors.
3. **Always run `wrangler deploy --dry-run`** before major deploys to validate without pushing.
4. **Workers AI is always remote** — it incurs charges even during `wrangler dev`. Never assume local simulation.
5. **Prefer retrieval over pre-training** — Wrangler CLI flags and config fields change frequently. Fetch docs before writing commands.
6. **Use `wrangler.jsonc` over `wrangler.toml`** — newer features are JSON-only.
7. **Never delete resources** (KV namespaces, R2 buckets, D1 databases, Vectorize indexes) without explicit user confirmation. Data loss is irreversible.

## Verification

### Check Wrangler Version

```bash
wrangler --version
# Expected: 4.x.x or higher
```

### Check Auth Status

```bash
wrangler whoami
# Expected: shows account email and account ID
```

### Validate Config

```bash
wrangler check
# Expected: no errors; config is valid
```

### Verify Types Are Current

```bash
wrangler types --check
# Expected: exit code 0 if types match config
```

### Dry-Run Deploy

```bash
wrangler deploy --dry-run
# Expected: build succeeds, no deployment made, shows bundle size
```

### Verify Local Dev Server

```bash
wrangler dev --port 8787
# Expected: server starts on http://localhost:8787
# Then in another terminal:
curl http://localhost:8787/
```

### Verify Bindings Are Accessible

Check that generated types include your bindings:

```bash
wrangler types
# Then inspect worker-configuration.d.ts for expected binding names
```

### Verify KV Namespace

```bash
wrangler kv namespace list
# Expected: lists all KV namespaces with IDs
```

### Verify D1 Migration Status

```bash
wrangler d1 migrations list my-database --local
# Expected: shows applied and pending migrations
```

## Best Practices

1. **Version control `wrangler.jsonc`** — treat as source of truth for Worker config.
2. **Use automatic provisioning** — omit resource IDs for auto-creation on deploy where supported.
3. **Run `wrangler types` in CI** — add to build step to catch binding mismatches early.
4. **Use environments** — separate staging/production with `env.staging`, `env.production`.
5. **Set `compatibility_date`** — update quarterly to get new runtime features.
6. **Use `.dev.vars` for local secrets** — never commit secrets to config.
7. **Test locally first** — `wrangler dev` with local bindings before deploying.
8. **Use `--dry-run` before major deploys** — validate changes without deployment.

## Quick Reference: Core Commands

| Task | Command |
|------|---------|
| Start local dev server | `wrangler dev` |
| Deploy to Cloudflare | `wrangler deploy` |
| Deploy dry run | `wrangler deploy --dry-run` |
| Generate TypeScript types | `wrangler types` |
| Validate configuration | `wrangler check` |
| View live logs | `wrangler tail` |
| Delete Worker | `wrangler delete` |
| Auth status | `wrangler whoami` |
