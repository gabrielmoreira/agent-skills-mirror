---
name: aws-sst-development
description: "Authors SST v4 (Ion) AWS infra in TypeScript: sst.config.ts, infra/ modules (sst.aws.Function/Bucket/Dynamo/Cron/Service/Router, sst.Secret, sst.Linkable, raw aws.* Pulumi), resource links, sst deploy, and stack troubleshooting. Use when writing Ion stacks or diagnosing Pulumi-backed SST deploys. Not for SST Classic v2/v3 CDK projects; never interpolate a Pulumi Output into a bare JS template literal."
version: 1.0.1
risk: unknown
source: https://github.com/zxkane/aws-skills/tree/main/plugins/aws-iac/skills/aws-sst-development
source_repo: zxkane/aws-skills
source_type: community
date_added: 2026-07-01
license: MIT
license_source: https://github.com/zxkane/aws-skills/blob/main/LICENSE
---

# SST v4 for AWS

## Overview

SST v4 (the "Ion" engine) is a Pulumi-backed IaC framework: you describe AWS resources in TypeScript and SST/Pulumi reconciles them into your account. It gives you high-level `sst.aws.*` components (Function, Bucket, Dynamo, Cron, Service, …) that expand into many underlying resources, plus an escape hatch to *any* raw Pulumi `aws.*` resource for the long tail. This skill encodes a production-proven way to author, link, test, deploy, and troubleshoot SST stacks on AWS — distilled from real multi-stack projects that have paid for each lesson with a prod incident.

SST and Pulumi are third-party — verify current syntax with Context7 (`resolve-library-id` → `query-docs` for `sst` or `pulumi-aws`) when you're unsure about a component's options. Verify AWS-side facts (service limits, model IDs, IAM action names, region availability) with the AWS docs MCP, never from memory. The patterns here are the *how*; the docs are the *what*.

## When to Use

Use this skill when you need to:

- Write or edit `sst.config.ts` — app name, `home`, providers/region, `defaultTags`, global `$transform`, `run()` import order.
- Build `infra/` modules using `sst.aws.Function`, `sst.aws.Bucket`, `sst.aws.Dynamo`, `sst.aws.Cron`, `sst.aws.Service`, `sst.aws.Router`, `sst.Secret`, `sst.Linkable`, or raw `aws.*` Pulumi resources.
- Wire resource links between modules (SST `link:`, SSM Parameter Store, IAM scope).
- Write source-level Vitest tests for infra modules.
- Run a deploy, diagnose a deploy failure, or migrate a resource between Pulumi types.
- Troubleshoot SST stack issues on AWS.

**Do not use this skill for SST v2/v3 ("SST Classic", CDK-based) projects.** Those are a different framework — the patterns here do not apply. Run `npx sst version` to confirm you're on v4/Ion (look for the `$config` + `.sst/platform/` signature).

## Prerequisites

- **Node.js** matching the repo's `.nvmrc` — check before editing.
- **SST v4 (Ion)** installed — verify with `npx sst version`.
- **AWS CLI** configured with credentials for the target account.
- **Package manager** identified from `package.json` (npm vs pnpm).
- **Context7 MCP** available for SST/Pulumi syntax verification.
- **AWS docs MCP** available for AWS-side fact verification.
- **Windows host (PowerShell)** is the primary environment. Adjust path separators and shell syntax accordingly.

## Procedure

### Step 1 — Orient: read the repo before you touch it

SST projects are conventional but not identical. Before editing, build a quick map so your change matches the house style instead of fighting it:

1. **Read `sst.config.ts`** — the app name, `home`, providers/region, `defaultTags`, any global `$transform` (Node runtime pin, bundle fixups), and the order in which `run()` imports `infra/` modules. The import order *is* the dependency order; respect it.
2. **Read `infra/`** — one file per domain (storage, functions, api, observability…). This is where resources are declared. Check for an `infra/CLAUDE.md` — these projects keep IaC-specific rules there, and it's the single most valuable file to read first.
3. **Read `infra/tests/`** — source-level Vitest assertions that pin resource invariants. If they exist, your change must keep them green and probably needs a new assertion.
4. **Read `package.json` / `.nvmrc`** — package manager (npm vs pnpm), Node version, and the `sst`/`pulumi` versions actually installed.

```powershell
npx sst version
```

Confirm you're on v4/Ion. If you see v2/v3 ("SST Classic", CDK-based), stop — these patterns don't apply.

### Step 2 — Determine your mode

| Situation | Follow |
|-----------|--------|
| New project, or adding a resource/module to an existing SST app | Authoring conventions in Step 4 |
| Wiring one module's output into another (links, SSM, IAM scope) | Sharing notes in Step 4 (`link:` vs SSM) |
| Writing tests for infra so changes don't silently break | Step 5 — Test |
| Running a deploy, or a deploy just failed | Step 6 — Deploy/operate |
| Migrating a resource between Pulumi types, renaming a physical name | Step 6 migration notes |

**Read the matching procedure step before editing** — each step carries the *why* behind the rule, which matters more than the rule itself.

### Step 3 — Verify syntax

Verify current syntax with Context7 (`resolve-library-id` → `query-docs` for `sst` or `pulumi-aws`) when you're unsure about a component's options. Verify AWS-side facts (service limits, model IDs, IAM action names, region availability) with the AWS docs MCP, never from memory. Don't guess at a component's option name.

### Step 4 — Author the resource/module

Follow the authoring conventions below. Match the surrounding file's commenting density and naming — these projects comment the *why* heavily, and a terse one-liner in a heavily-annotated file reads as a regression.

**Universal conventions (apply everywhere):**

- **Control the Node runtime deliberately, in one place.** Don't leave it to whatever the installed SST happens to default to. The idiom is a single global `$transform(sst.aws.Function, (args) => { args.runtime ??= "nodejs24.x" })` in `run()` — `??=` is correct here (the transform runs before the component applies its own default, so it fills in only when the user didn't set one). Recent SST already defaults to a current Node runtime, so check the installed default first (Context7); the transform is then version-independence insurance so a future SST downgrade can't silently move your fleet.
- **Never interpolate a Pulumi `Output<T>` into a plain JS template literal.** Use `$interpolate` (or `pulumi.interpolate`). A bare top-level `` `${bucket.arn}/*` `` stringifies the `Output` to a `[Output<T>]` placeholder and produces a broken ARN that only fails at deploy time (it type-checks and `sst dev` runs fine). The fix is `$interpolate`​`` `${bucket.arn}/*` ``. This has caused prod deploy outages.
- **Prefer typed `sst.aws.*` / `aws.*` resources over the `aws.cloudcontrol.Resource` escape hatch.** CloudControl outputs are stringly-typed and `oneOf` fields don't patch cleanly. Use it only when no typed resource exists yet, and migrate off it when one ships.

**Project-specific defaults (adopt for consistency, but confirm per repo):**

- **Region `ap-northeast-1`**, `home: "aws"`, and `defaultTags` carrying `Project` / `Stage` / `ManagedBy: "sst"`.
- **Stage-gated lifecycle**: `removal: stage === "prod" ? "retain" : "remove"` and `protect: stage === "prod"` so prod resources survive a stack tear-down and non-prod previews clean up.
- **SSM Parameter Store as the out-of-graph contract** under a `/{app}/{stage}/{domain}/...` prefix — for consumers that aren't in the Pulumi graph (CI scripts, sibling apps, operators). For *same-app* Lambdas, prefer SST `link:` (it wires a real dependency edge and grants IAM); don't route same-app sharing through SSM.
- **Lazy `await import("./infra/<module>")` inside `run()`** so `sst dev` hot-reload stays light. (For testing, a module export still runs its top-level `new sst.aws.*` unless it's wrapped in a factory function — see Step 5 for how to test infra.)
- **Source-level Vitest tests** on every infra module — a lightweight, house-style regression net asserting on the *source text* (resource names, index shapes, IAM scopes). It's a deliberate choice, not an SST limit: Pulumi *does* support runtime mocks (`@pulumi/pulumi/runtime`) for behavioral graph tests when a module has real logic. Source assertions don't replace a preview-deploy + smoke test.
- **An observability gate**: every new Lambda/queue/schedule gets an alarm and structured logging before merge. Whether you enforce this depends on the project, but it's cheap insurance.

When you introduce a convention, say which bucket it's in ("this is universal" vs "matching this repo's house style") so the user can override the project-specific ones deliberately.

### Step 5 — Test

Add or update source-level assertions as described in this step and run:

```powershell
npx vitest
```

Or use the repo's `test` script:

```powershell
npm test
```

Run `npx sst diff` and/or `tsc --noEmit` to catch type and plan errors before deploying:

```powershell
npx sst diff
npx tsc --noEmit
```

### Step 6 — Deploy/operate

Follow the deploy steps below. **Confirm the target account before any deploy:**

```powershell
aws sts get-caller-identity
```

Then deploy:

```powershell
npx sst deploy
```

For migrations (resource between Pulumi types, renaming a physical name), default to **two sequential PRs** — Pulumi creates-before-destroys, so for a uniqueness-constrained AWS name (bucket, IAM role, gateway) the old resource still owns it and the create fails with `ConflictException`. Two sequential deploys (teardown, then recreate) is the conservative default; `aliases:` / `pulumi import` / state surgery can bridge identity in some cases but only with a reviewed plan. See the migration notes in this step.

### Step 7 — Clean up

Clean up any exported state files — they contain account IDs and ARNs and must not linger in `/tmp` or chat history.

## Pitfalls

1. **`Output<T>` in template literals causes silent prod outages.** A bare `` `${bucket.arn}/*` `` stringifies the `Output` to `[Output<T>]` and produces a broken ARN. It type-checks and `sst dev` runs fine — it only fails at deploy time. Always use `$interpolate`​`` `${bucket.arn}/*` `` or `pulumi.interpolate`. This has caused real prod deploy outages.

2. **Resource-type migrations fail with `ConflictException`.** Pulumi creates-before-destroys. For uniqueness-constrained AWS names (buckets, IAM roles, gateways), the old resource still owns the name when the new one tries to create. Default to two sequential deploys (teardown, then recreate). `aliases:` / `pulumi import` / state surgery can bridge identity but only with a reviewed plan.

3. **`aws.cloudcontrol.Resource` is a trap door.** Outputs are stringly-typed and `oneOf` fields don't patch cleanly. Use it only when no typed resource exists yet, and migrate off it when one ships.

4. **Don't route same-app sharing through SSM.** For same-app Lambdas, use SST `link:` — it wires a real dependency edge and grants IAM. SSM is for out-of-graph consumers (CI scripts, sibling apps, operators) only.

5. **Don't hand-set `runtime` on individual functions.** Use the global `$transform` with `??=` so you fill in only when the user didn't set one. Hand-setting diverges from the fleet unless intentionally diverging (e.g., a Python function).

6. **SST v2/v3 ("SST Classic") is a different framework.** These patterns don't apply. Always verify with `npx sst version` first.

7. **Import order in `run()` is dependency order.** Respect it. Reordering imports can break resource references.

8. **Source-level tests don't replace preview-deploy + smoke test.** They assert on source text, not runtime behavior. For modules with real logic, consider Pulumi runtime mocks (`@pulumi/pulumi/runtime`).

9. **State files contain account IDs and ARNs.** They must not linger in `/tmp` or chat history. Clean them up after any export.

10. **Don't guess at component option names.** Verify with Context7 (`resolve-library-id` → `query-docs` for `sst` or `pulumi-aws`). Verify AWS-side facts with the AWS docs MCP, never from memory.

## Verification

1. **Confirm SST version (must be v4/Ion):**
   ```powershell
   npx sst version
   ```
   Expected: v4.x with `$config` + `.sst/platform/` signature.

2. **Confirm target AWS account before deploy:**
   ```powershell
   aws sts get-caller-identity
   ```
   Verify the account ID matches your expectation before proceeding.

3. **Type-check the project:**
   ```powershell
   npx tsc --noEmit
   ```
   No errors expected.

4. **Preview the deploy plan:**
   ```powershell
   npx sst diff
   ```
   Review the diff for unexpected creates/deletes/updates.

5. **Run the test suite:**
   ```powershell
   npx vitest
   ```
   All source-level assertions must pass. Add new assertions for new resources.

6. **Post-deploy smoke test:** Verify the deployed resource is reachable and behaves as expected. Source-level tests don't replace this.

## What good looks like

- The change is the smallest diff that satisfies the requirement, in the right `infra/` module, wired into `run()` in dependency order.
- Every Lambda gets the right runtime via the global transform (you didn't hand-set `runtime` unless intentionally diverging — e.g. a Python function).
- Cross-resource references use `link:` (in-graph) and/or `$interpolate`-scoped IAM; outputs other tools consume are published to SSM under the stage prefix.
- New infra has a matching source-level test, and the existing suite stays green.
- You confirmed AWS-side facts via the docs MCP and SST/Pulumi syntax via Context7 rather than relying on recall.
- Anything irreversible (deploy, `sst remove`, a resource-type migration) was flagged to the user with the account it targets, and migrations were planned as two PRs, not one.

## Related skills

- **aws-cdk-development** — for CDK-based AWS IaC projects (SST v2/v3 Classic).
- **aws-lambda-development** — for Lambda function authoring patterns.
- **aws-iam-least-privilege** — for IAM policy scoping within SST resources.

## Limitations

- Use this skill only when the task clearly matches its upstream source and local project context.
- Verify commands, generated code, dependencies, credentials, and external service behavior before applying changes.
- Do not treat examples as a substitute for environment-specific tests, security review, or user approval for destructive or costly actions.
