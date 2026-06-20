---
name: api-flow-tester
description: Use when the user wants to run, debug, create, or update multi-step HTTP API test flows, especially when later requests depend on values captured from earlier responses.
---

# API Flow Tester

Use this skill for repeatable HTTP API flow testing against a running service.

## When to Use

- Run an existing flow file step by step
- Preview a flow safely with dry-run before hitting the server
- Debug why a chained API flow fails
- Create a new flow from an endpoint sequence or API spec
- Update a flow after endpoint, header, body, or response changes
- Verify auth and resource handoff across multiple requests
- Run only part of a flow while debugging
- Validate expected failure cases such as `401`, `403`, or `422`

Do not use this for a single one-off endpoint check unless the user explicitly wants a reusable flow artifact.

## Repository Discovery

Before doing anything, inspect the repo and identify:

1. Flow file location. Check user-provided paths first, then search in this order:
   - `tests/flows/*/flow.md`
   - `flows/*/flow.md`
   - `docs/flows/*/flow.md`
   Prefer per-flow directories such as `tests/flows/customer-login/flow.md`.
2. API reference. Prefer local files such as `openapi.json`, `openapi.yaml`, or `swagger.json`. If none exist, probe common server routes such as `/openapi.json`, `/api/openapi.json`, or the user-provided docs URL. If no spec is available, use the repo's route definitions or existing tests.
3. Base URL. Prefer the value inside the flow file, then user input, then project config or `.env` files. If nothing is explicit, use a clearly stated default such as `http://localhost:8080`.

If any of these are ambiguous, state the assumption before executing.

## Flow Format

Flow files are Markdown documents with:

- A flow title
- Base URL
- Optional OpenAPI URL
- Optional description
- Ordered `Step N` sections
- Per-step method and path
- Optional headers
- Optional JSON body
- Optional expectations such as status or required response fields
- Optional captured variables that map variable names to JSON paths

Use `{{variable_name}}` placeholders in later steps. Read [references/example-flow.md](./references/example-flow.md) before creating a new file or normalizing an existing one.

For secret-backed flows, also read [references/flow-test-env.example](./references/flow-test-env.example). For OTP or phone-based login flows, read [references/example-otp-flow.md](./references/example-otp-flow.md). For explicit negative-test patterns, read [references/example-negative-flow.md](./references/example-negative-flow.md).

If you create a new flow at `tests/flows/<flow-name>/flow.md`, also create `tests/flows/<flow-name>/.env.example`.

Supported expectation patterns:

- `Status`
- `JSON path exists`
- `JSON path not exists`
- `JSON path equals`
- `JSON path contains`
- `JSON path matches regex`
- `Header equals`
- `Header contains`

## Sensitive Inputs

Flow files may live in the repository, so do not hardcode secrets or personal data into committed files.

Use this order of preference:

1. Reuse existing environment variables or local secret files that are already ignored by git.
2. Use placeholders such as `{{ADMIN_EMAIL}}`, `{{ADMIN_PASSWORD}}`, `{{TEST_PHONE_NUMBER}}`, or `{{OTP_CODE}}` inside the flow file.
3. Before execution, resolve those placeholders from an untracked environment-specific source such as `.flow.test.local.env`, `.flow.test.staging.env`, `.flow.test.production.env`, or a per-flow secret file.
4. If a required sensitive value is still missing or ambiguous, ask the user for it before running the flow.

Default secret file names to propose:

- Per-flow:
  - `tests/flows/<flow-name>/flow.md`
  - `tests/flows/<flow-name>/.env.local`
  - `tests/flows/<flow-name>/.env.staging`
  - `tests/flows/<flow-name>/.env.production`
  - `tests/flows/<flow-name>/.env.example`
- Repo-wide fallback:
  - `.flow.test.local.env`
  - `.flow.test.staging.env`
  - `.flow.test.production.env`

When editing repo files:

- Keep only placeholders in committed flow files.
- The `.env.example` file is required for new secret-backed flows and must list every placeholder-backed input with blank or example-safe values only.
- If secret values will live in `.env`, `.env.*`, or per-flow secret files, make sure the real secret files are ignored by git before writing them.
- Never replace placeholders with real secrets in the saved flow file.
- If the repo lacks an ignored local secret source, propose one and ask before creating it.
- If the ignore rule is missing, ask before editing a tracked `.gitignore`, then add the required entries so `.env` and relevant `.env.*` files do not get committed.
- Do not ignore `.env.example`; it must stay committable so users can discover the required keys safely.
- Do not put real secrets or secret-like example values in `.env.example`; every value there must be blank or clearly safe to commit.
- If keys change in `.env`, `.env.*`, or per-flow secret files, update `.env.example` in the same change so the committed example stays in sync.
- When creating a new local secret file, also offer to create a matching example file such as `.flow.test.env.example` without real values.

## Running a Flow

Supported execution modes:

- Full run: execute every step in order
- Dry run: resolve inputs and show each request without sending it
- Partial run: execute only selected steps or start from a selected step

1. Read the flow file and parse each step in order.
2. Build a session variable map for captured values and external input values.
3. Resolve placeholders in path, headers, and body before each request.
4. Decide the execution mode from the user request. If the user asks to preview, validate, inspect, or verify without side effects, use dry run.
5. If the user asks to run only part of the flow, determine either:
   - a single target step
   - a start step and continue to the end
   - explicit steps to skip
6. For partial runs, make sure required inputs for skipped earlier steps still exist. Prefer existing env values or ask the user before running if a skipped step would have produced required captures.
7. Execute requests sequentially when not in dry run. Use `curl -sS` as the canonical request transport. Use `jq` for JSON extraction. If `jq` is unavailable or the extraction is too complex, use `python3` only for parsing or extraction, not for sending requests.
8. Validate expectations after each response.
9. Stop on the first unexpected failure unless the user explicitly asks to continue.

Environment resolution rules:

1. Determine the flow identifier from the directory name when the flow path is `<flow-name>/flow.md`. Use kebab-case such as `customer-login`.
2. Detect available per-flow environment files such as `./.env.local`, `./.env.staging`, and `./.env.production`.
3. If exactly one per-flow environment file exists, use it and state which environment was selected.
4. If multiple per-flow environment files exist, ask the user which environment to use before executing the flow.
5. If no per-flow environment file exists, fall back to repo-wide environment-specific secret files.
6. If multiple repo-wide candidates exist, ask the user which one to use.

Environment selection SOP:

1. When multiple environment files exist for the same flow, ask the user explicitly which one to use.
2. Use a direct prompt such as: `Flow "customer-login" has environments: local, staging, production. Which one should I run?`
3. Do not guess the environment from the current branch, hostname, or prior conversation unless the user already specified it in the current request.
4. If `production` is chosen, ask for explicit confirmation again before sending any request with side effects.

For each step, report:

- Step name
- Request summary: method and path
- Execution mode when not doing a normal full run
- Response status
- Key assertion result
- Captured variable names

Do not print secrets in full. Redact bearer tokens, refresh tokens, API keys, and cookies in the summary.

In dry run mode, report:

- resolved method and path
- resolved headers with secrets redacted
- resolved body with secrets redacted
- resolved `curl` command
- whether every placeholder was resolved
- whether the step is ready to execute

Prefer a single generated `curl` command per step for replay and debugging. Do not generate ad-hoc Python scripts to send HTTP requests unless `curl` cannot represent the request accurately.

## Capturing Variables

When a step defines captured variables:

1. Parse the response body as JSON.
2. Extract each value from the declared JSON path.
3. Store successful captures in the session variable map.
4. Fail fast if a required capture is missing, and show the relevant response snippet plus the missing path.

If a response body is not JSON, say so explicitly and do not pretend extraction succeeded.

## Assertions And Negative Tests

Treat non-2xx responses as valid only when the flow explicitly expects them.

Rules:

1. If `Status` is `401`, `403`, `404`, `409`, `422`, or another non-2xx value, treat the step as a negative test step.
2. For negative test steps, still validate all declared expectations.
3. If the flow expects a non-2xx status and the server returns `2xx`, mark the step as failed.
4. If the flow expects `2xx` and the server returns non-2xx, mark the step as failed.
5. When negative-test intent is not clear, ask the user before rewriting the flow.

Example expectation block:

```markdown
**Expect:**
- Status: 422
- JSON path exists: `.error.code`
- JSON path equals: `.error.code` -> `INVALID_PHONE_NUMBER`
- JSON path contains: `.error.message` -> `phone`
```

## Partial Run Rules

When the user asks to run only part of the flow:

1. Accept requests such as `run step 3`, `start from step 2`, `skip login`, or `only run get profile`.
2. Resolve step references by step number first, then by exact step name.
3. If a later step depends on captured values from skipped steps, prefer env-backed placeholders or ask the user how to supply them.
4. Do not silently invent missing captured values.
5. Report clearly which steps were skipped and why.

## Creating or Updating a Flow

1. Inspect the current API reference and any related existing flows.
2. Draft the flow using the documented format from the example reference.
3. Keep the flow definition environment-agnostic when the same flow will run against multiple targets.
4. If the new flow uses secret-backed or environment-backed placeholders, create a sibling `.env.example` file in the same flow directory and include every required placeholder-backed key with blank or example-safe values only.
5. If the flow will rely on `.env`, `.env.*`, or per-flow secret files, check whether `.gitignore` already ignores those real secret files before writing or recommending them.
6. If the ignore rule is missing, ask before editing a tracked `.gitignore`, then add the necessary entries so real secret files stay untracked while `.env.example` remains committable.
7. Keep `.env.example` safe to commit by using blank values or obviously non-secret placeholders only.
8. If secret-file keys change, update `.env.example` in the same change so it remains an accurate contract for required inputs.
9. If the user asked for an edit, summarize the intended changes before writing.
10. If the flow needs credentials, phone numbers, OTPs, or other sensitive values, keep them as placeholders and define how they will be provided at runtime through `.env.<environment>` files.
11. Ask for approval before saving any new or modified flow file.
12. After approval, write the file and optionally run it.

Never invent request or response fields when the spec or code does not support them. Mark assumptions clearly.

## When to Ask the User

Ask before proceeding when:

- The base URL is unclear and multiple plausible targets exist
- The OpenAPI spec is missing locally and probing server routes could hit the wrong service
- Multiple `.env.<environment>` files exist for the same flow and the user has not chosen one yet
- The flow may target `production` or another live environment with real side effects
- A flow depends on credentials, phone numbers, OTP codes, or other sensitive values that are not already available from a safe local source
- A partial run skips earlier steps that would normally generate required captured values
- The repo does not yet have an ignored file for local flow secrets and creating one would change tracked files such as `.gitignore`
- A non-2xx step could be either an expected negative test or an actual failure

Do not ask unnecessary implementation-detail questions when the repo or spec already answers them.

## Failure Handling

- Server unreachable: report the base URL and the connection failure clearly.
- Unexpected non-2xx status: show the step, status, and a short response excerpt.
- Missing variable capture: stop and show which JSON path failed.
- Spec missing: continue if the flow is otherwise clear, but say validation is limited.
- Placeholder unresolved: stop before sending the request and show the missing variable name.
- Production target: require explicit user confirmation before executing any write action or any endpoint with business side effects.

## Output Style

Keep the result compact and structured. A good run summary looks like:

```text
Step 1: Login
- Request: POST /auth/login
- Response: 200
- Captured: access_token, user_id

Step 2: Get profile
- Request: GET /users/42
- Response: 200
- Assertions: email exists
```

For dry run or partial run, include a short preface such as:

```text
Mode: dry run
Selected steps: 2-3
Secret source: tests/flows/customer-login/.env.staging
```

## Recommended Conventions

- Committed flow files: keep under `tests/flows/<flow-name>/flow.md` unless the repo already uses another convention
- Use `kebab-case` for flow directory names, for example `customer-login`, `admin-refresh-session`, `booking-create-and-pay`
- Each committed flow should declare `Base URL` explicitly, usually as `{{BASE_URL}}`
- Add `OpenAPI URL` to the flow whenever the spec is served over HTTP or differs by environment, usually as `{{OPENAPI_URL}}`
- Do not hardcode `Environment` into `flow.md` when the same flow can run against multiple targets
- Do not hardcode `Secrets File` into `flow.md` unless the user explicitly wants an override
- Per-flow secret files should be the default: `tests/flows/<flow-name>/.env.local`, `tests/flows/<flow-name>/.env.staging`, `tests/flows/<flow-name>/.env.production`
- Commit a per-flow example file when useful: `tests/flows/<flow-name>/.env.example`
- Repo-wide secret files are fallback only: `.flow.test.local.env`, `.flow.test.staging.env`, `.flow.test.production.env`
- Example secret files: prefer committed `*.env.example` files with blank or placeholder values only
- Placeholder names: use uppercase snake case such as `{{ADMIN_EMAIL}}`, `{{TEST_PHONE_NUMBER}}`, `{{OTP_CODE}}`
