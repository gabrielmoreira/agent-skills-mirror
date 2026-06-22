---
name: deployment-scaffolder
description: Generates deployment configuration for the app — local Docker/docker-compose setup and cloud deployment manifests (Vercel, AWS, GCP, or container-based platforms). Use when asked to "containerize this", "set up local deployment", "deploy this to <cloud provider>", or "add CI/CD for deployment".
---

# Deployment Scaffolder Skill

Covers both **local** (Docker Compose, for parity with production and for teammates without cloud access) and **cloud** (provider-specific manifests/config) deployment targets for this Next.js + Node.js stack.

## Local deployment (Docker)

1. Use [Dockerfile.template](./Dockerfile.template) — a multi-stage build (deps → build → runtime) using the `node:20-alpine` base and Next.js standalone output (`output: 'standalone'` must be set in `next.config.ts`).
2. Use [docker-compose.template.yml](./docker-compose.template.yml) for local orchestration — app container + Postgres (or the project's actual DB) + any other local dependency (Redis, etc).
3. Add a `.dockerignore` excluding `node_modules`, `.next`, `.git`, `.env*` (except `.env.example`).
4. Confirm environment variables are injected via `docker-compose.yml`'s `environment:`/`env_file:`, never baked into the image.
5. Verify with `docker compose up --build` that the app boots and the healthcheck passes before considering this done.

## Cloud deployment

The right artifact depends on target — confirm with the user which provider before generating config, since the wrong scaffold (e.g. a Dockerfile for a platform that wants zero-config) creates noise:

- **Vercel** (default for Next.js apps with no special infra needs): no Dockerfile needed — generate `vercel.json` only if non-default behavior is required (custom headers, redirects, cron). Document required env vars in `.env.example` and note they must be set in the Vercel dashboard/CLI, not committed.
- **AWS** (ECS/Fargate or App Runner): use the same Dockerfile as local, add [ecs-task-definition.template.json](./ecs-task-definition.template.json) and a GitHub Actions workflow that builds, pushes to ECR, and updates the service.
- **GCP** (Cloud Run): use the same Dockerfile, add a `cloudbuild.yaml` building and deploying to Cloud Run.
- **Generic container platform** (Fly.io, Railway, Render): use the same Dockerfile plus that platform's minimal config file (`fly.toml`, etc).

## Process
1. Ask (or infer from existing repo files like `vercel.json`, `fly.toml`, `.github/workflows/`) which target(s) are actually needed — don't generate config for every provider speculatively.
2. Generate only the files for the confirmed target(s).
3. Document required environment variables in `.env.example`, with a comment on which are server-only vs `NEXT_PUBLIC_`.
4. Add a corresponding CI workflow step (build, typecheck, test) that must pass before deploy — never wire deploy to run before checks pass.
5. Never commit actual secret values — only variable names and placeholder/example values.

## Checklist
- [ ] Correct target(s) confirmed before generating config
- [ ] Multi-stage Docker build (if containerized) — no dev dependencies in the final runtime image
- [ ] `.dockerignore` excludes secrets and build artifacts
- [ ] Env vars documented, not hardcoded
- [ ] CI runs typecheck/lint/test before any deploy step
- [ ] Healthcheck endpoint exists and is wired into the deployment config
