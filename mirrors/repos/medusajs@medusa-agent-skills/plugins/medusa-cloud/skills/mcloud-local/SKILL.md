---
name: mcloud-local
description: Execute mcloud local build to reproduce a Cloud build on the local machine. Use when debugging a build-failed deployment without pushing to the tracked branch, iterating on a build fix, or testing build-variable changes locally. Requires Docker and must run inside the project's Git repo.
allowed-tools: Bash(mcloud local*), Bash(mcloud deployments*), Bash(mcloud use*), Bash(git*), Bash(jq*)
---

# Cloud CLI: Local Command

Execute `mcloud local build` to run a Cloud build on the local machine, mirroring how Cloud builds the project. Use it to debug `build-failed` deployments without pushing changes and waiting for a full Cloud build.

## Constraints

- **No `--json` flag.** `local build` streams plaintext build output and signals the result through its **exit code** (`0` = success). Do not parse its output as JSON.
- **Requires Docker installed and running**, and must run from **inside the project's Git repository**.
- Reproduces `build-failed` (build) failures only — not `deployment-failed` (runtime) failures. For runtime failures, use `mcloud logs --deployment <id>`.
- Available since mcloud CLI v0.1.10.
- The Docker build cache is **disabled by default** so variable changes always invalidate the cache; pass `--docker-cache` to enable it.

## Command

### local build

Run a Cloud build locally. Infers the root path and build variables from the linked Cloud project and environment. Builds the backend by default; pass `--type storefront` for the storefront.

```bash
mcloud local build \
  --organization <org-id> \
  --project <project-id-or-handle> \
  --environment <environment-handle>
```

**Options:**
- `-o/--organization <id>` — Organization ID (falls back to active context)
- `-p/--project <id-or-handle>` — Project ID or handle (falls back to active context)
- `-e/--environment <handle>` — Environment whose variables are used (falls back to active context)
- `-t/--type <backend|storefront>` — Build type (default: `backend`)
- `--root-path <path>` — Backend root path relative to the repo root (inferred if omitted; `.` if no Cloud project found)
- `--storefront-path <path>` — Storefront path relative to the repo root, for `--type storefront` (inferred if omitted)
- `--env-file <path>` — Use a local `.env` file instead of the Cloud environment's variables
- `-v/--var <KEY=VALUE>` — Override a single build variable; repeatable
- `--docker-cache` — Enable the Docker build cache (default: `false`)

**Output:**
- On success (exit `0`), the backend image is tagged `<repository-name>:cloud-local-build-<commit-hash>`; a storefront build writes its output directory and prints the path.
- On failure (non-zero exit), the command exits with the failing step's error — debug it as you would a Cloud build.

## Reproduce a Build Failure

Check out the same commit the failed deployment built so the local build matches, then route on the exit code:

```bash
# Identify the failing deployment and the commit it built
DEPLOYMENT_ID=$(
  mcloud deployments list --json \
    | jq -r '[.[] | select(.backend_status == "build-failed")][0].id'
)
COMMIT=$(mcloud deployments get "$DEPLOYMENT_ID" --json | jq -r '.commit_hash')

git checkout "$COMMIT"

if mcloud local build; then
  echo "Build succeeded locally; failure not reproducible from this commit."
else
  echo "Build failed locally; inspect the streamed output for the failing step."
fi
```

Once the local build exits `0`, push the fix to the tracked branch and start a fresh Cloud build with `mcloud environments trigger-build <env>`.

## Examples

```bash
# Reproduce the backend build for the active context
mcloud local build

# Reproduce the storefront build
mcloud local build --type storefront --storefront-path apps/storefront

# Test a build-variable fix without editing code
mcloud local build --var NODE_ENV=production

# Build against a local .env file
mcloud local build --env-file .env

# Reuse the Docker cache for a faster rebuild
mcloud local build --docker-cache
```
