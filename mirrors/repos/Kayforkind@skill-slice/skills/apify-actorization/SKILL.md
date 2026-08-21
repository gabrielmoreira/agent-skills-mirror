---
name: apify-actorization
description: "Converts an existing CLI, script, or Crawlee project into an Apify Actor: Docker image, .actor/input_schema.json, Actor.init/exit lifecycle, apify run then apify push. Use when wrapping software for the Apify platform, adding Apify SDK I/O, or deploying an Actor. Not for general Docker/Compose ops (docker-management) or writing a scraper from scratch without Actor packaging."
version: 1.0.1
risk: unknown
source: community
---

# Apify Actorization

Actorization converts existing software into reusable serverless applications compatible with the Apify platform. Actors are programs packaged as Docker images that accept well-defined JSON input, perform an action, and optionally produce structured JSON output.

## When to Use

- Converting an existing project to run on the Apify platform
- Adding Apify SDK integration to a project
- Wrapping a CLI tool or script as an Actor
- Migrating a Crawlee project to Apify
- Packaging a scraper, automation script, or data pipeline as a deployable Actor

**Trigger keywords:** "apify actor", "actorize", "apify init", "apify push", "convert to actor", "apify SDK", "actor input schema", "apify deploy"

## Prerequisites

### 1. Verify `apify` CLI is installed

```powershell
apify --help
```

If not installed:

```powershell
# Option A: npm (cross-platform)
npm install -g apify-cli

# Option B: Homebrew (macOS/Linux)
brew install apify-cli

# Option C: Official release package verified by your OS package manager
```

### 2. Verify CLI is logged in

```powershell
apify info  # Should return your username
```

If not logged in:

1. Check whether the `APIFY_TOKEN` environment variable is already set.
2. If not, ask the user to generate a token at `https://console.apify.com/settings/integrations`.
3. The user should add the token to their shell profile or secret manager **without putting the literal token in command history**.
4. Then run:

```powershell
apify login
```

> **HARD RULE:** Never echo, log, or commit a live `APIFY_TOKEN`. Use `YOUR_TOKEN` as a placeholder in all examples and documentation.

### 3. Verify Docker is available (for local builds and `apify push`)

```powershell
docker --version
```

## Procedure

### Actorization Checklist

Copy this checklist to track progress:

- [ ] Step 1: Analyze project (language, entry point, inputs, outputs)
- [ ] Step 2: Run `apify init` to create Actor structure
- [ ] Step 3: Apply language-specific SDK integration
- [ ] Step 4: Configure `.actor/input_schema.json`
- [ ] Step 5: Configure `.actor/output_schema.json` (if applicable)
- [ ] Step 6: Update `.actor/actor.json` metadata
- [ ] Step 7: Test locally with `apify run`
- [ ] Step 8: Deploy with `apify push`

---

### Step 1: Analyze the Project

Before making changes, understand the project:

1. **Identify the language** — JavaScript/TypeScript, Python, or other.
2. **Find the entry point** — The main file that starts execution.
3. **Identify inputs** — Command-line arguments, environment variables, config files.
4. **Identify outputs** — Files, console output, API responses.
5. **Check for state** — Does it need to persist data between runs (request queues, key-value stores)?

Record findings in a short summary before proceeding.

---

### Step 2: Initialize Actor Structure

Run in the project root:

```powershell
apify init
```

This creates:
- `.actor/actor.json` — Actor configuration and metadata
- `.actor/input_schema.json` — Input definition for the Apify Console
- `Dockerfile` (if not present) — Container image definition

> **HARD RULE:** Do not delete an existing `Dockerfile` without explicit user confirmation. If `apify init` detects one, review its contents before overwriting.

---

### Step 3: Apply Language-Specific Changes

Choose based on your project's language. **Load the matching reference file before editing code:**

| Language | Reference file | When to load |
|----------|---------------|--------------|
| JavaScript / TypeScript | `references/js-ts-actorization.md` | Before wrapping JS/TS code with `Actor.init()` / `Actor.exit()` |
| Python | `references/python-actorization.md` | Before wrapping Python code with `async with Actor:` |
| Other (CLI-based) | `references/cli-actorization.md` | Before writing a wrapper script that shells out to a CLI tool |

#### Quick Reference

| Language | Install | Wrap Code |
|----------|---------|-----------|
| JS/TS | `npm install apify` | `await Actor.init()` ... `await Actor.exit()` |
| Python | `pip install apify` | `async with Actor:` |
| Other | Use CLI in wrapper script | `apify actor:get-input` / `apify actor:push-data` |

---

### Steps 4–6: Configure Schemas

**Load `references/schemas-and-output.md` before configuring these files.** It covers detailed configuration of:

- Input schema (`.actor/input_schema.json`)
- Output schema (`.actor/output_schema.json`)
- Actor configuration (`.actor/actor.json`)
- State management (request queues, key-value stores)

Validate schemas against the `@apify/json_schemas` npm package:

```powershell
npx @apify/json_schemas validate .actor/actor.json --schema actor.schema.json
npx @apify/json_schemas validate .actor/input_schema.json --schema input.schema.json
npx @apify/json_schemas validate .actor/output_schema.json --schema output.schema.json
```

---

### Step 7: Test Locally

Run the actor with inline input (for JS/TS and Python actors):

```powershell
apify run --input '{\"startUrl\": \"https://example.com\", \"maxItems\": 10}'
```

Or use an input file:

```powershell
apify run --input-file ./test-input.json
```

> **HARD RULE:** Always use `apify run`, not `npm start` or `python main.py`. The CLI sets up the proper environment and storage (local storage, env vars, input injection). Running directly will silently miss Actor lifecycle setup.

---

### Step 8: Deploy

```powershell
apify push
```

This uploads and builds your actor on the Apify platform. Confirm the build succeeds in the Apify Console before announcing completion.

---

### Monetization (Optional)

After deploying, you can monetize your actor in the Apify Store. The recommended model is **Pay Per Event (PPE)**:

- Per result/item scraped
- Per page processed
- Per API call made

Configure PPE in the Apify Console under **Actor > Monetization**. Charge for events in your code with:

```javascript
await Actor.charge('result');
```

Other options: **Rental** (monthly subscription) or **Free** (open source).

## Pre-Deployment Checklist

- [ ] `.actor/actor.json` exists with correct name and description
- [ ] `.actor/actor.json` validates against `@apify/json_schemas` (`actor.schema.json`)
- [ ] `.actor/input_schema.json` defines all required inputs
- [ ] `.actor/input_schema.json` validates against `@apify/json_schemas` (`input.schema.json`)
- [ ] `.actor/output_schema.json` defines output structure (if applicable)
- [ ] `.actor/output_schema.json` validates against `@apify/json_schemas` (`output.schema.json`)
- [ ] `Dockerfile` is present and builds successfully
- [ ] `Actor.init()` / `Actor.exit()` wraps main code (JS/TS)
- [ ] `async with Actor:` wraps main code (Python)
- [ ] Inputs are read via `Actor.getInput()` / `Actor.get_input()`
- [ ] Outputs use `Actor.pushData()` or key-value store
- [ ] `apify run` executes successfully with test input
- [ ] `generatedBy` is set in `actor.json` meta section

## Pitfalls

1. **Running directly instead of `apify run`** — `npm start` or `python main.py` bypasses the Actor lifecycle, local storage, and input injection. Always test with `apify run`.
2. **Overwriting an existing `Dockerfile`** — `apify init` may detect one; review before replacing. Never delete without user confirmation.
3. **Hardcoded tokens in command history** — Never pass a literal `APIFY_TOKEN` on the command line. Use environment variables or `apify login` interactively.
4. **Missing `Actor.init()` / `Actor.exit()`** — Forgetting the lifecycle calls means the Actor won't properly connect to storage, logging, or the platform's run orchestration.
5. **Unvalidated schemas** — Pushing an actor with an invalid `input_schema.json` causes Console errors. Always validate with `@apify/json_schemas` before `apify push`.
6. **PowerShell JSON quoting** — Inline JSON in PowerShell requires escaped double quotes (`\"`) or single-quote wrapping. Prefer `--input-file` for complex inputs.
7. **Missing `generatedBy` field** — The `actor.json` meta section should include `generatedBy` to identify the tooling that created the actor.
8. **Not testing locally before push** — `apify push` builds remotely; a local `apify run` catches errors faster and without consuming platform build minutes.

## Verification

1. **CLI installed and authenticated:**

```powershell
apify info
# Expected: your Apify username and account details
```

2. **Actor structure initialized:**

```powershell
Test-Path .actor/actor.json
Test-Path .actor/input_schema.json
Test-Path Dockerfile
# All should return True
```

3. **Schemas valid:**

```powershell
npx @apify/json_schemas validate .actor/input_schema.json --schema input.schema.json
# Expected: validation success, no errors
```

4. **Local run succeeds:**

```powershell
apify run --input-file ./test-input.json
# Expected: actor runs to completion, output appears in local storage
```

5. **Deployment succeeds:**

```powershell
apify push
# Expected: build completes on Apify platform, actor appears in Console
```

## Apify MCP Tools

If an MCP server is configured, use these tools for documentation:

- `search-apify-docs` — Search Apify documentation
- `fetch-apify-docs` — Get full doc pages

Otherwise, the MCP Server URL is: `https://mcp.apify.com/?tools=docs`

## Resources

- [Actorization Academy](https://docs.apify.com/academy/actorization) — Comprehensive guide
- [Apify SDK for JavaScript](https://docs.apify.com/sdk/js) — Full SDK reference
- [Apify SDK for Python](https://docs.apify.com/sdk/python) — Full SDK reference
- [Apify CLI Reference](https://docs.apify.com/cli) — CLI commands
- [Actor Specification](https://raw.githubusercontent.com/apify/actor-whitepaper/refs/heads/master/README.md) — Complete specification

## Limitations

- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
