---
name: chatgpt-apps
description: "Scaffolds ChatGPT Apps SDK apps that pair an MCP server with a widget UI: tool plans, resource registration, MCP Apps bridge, window.openai extensions, CSP/domain metadata, and directory submission. Use when designing tools, wiring widgets, or producing a docs-aligned Apps SDK scaffold. Not for generic ChatGPT chat prompts or standalone MCP servers with no Apps SDK widget contract."
version: 1.0.1
---

# ChatGPT Apps

## Overview

Scaffold ChatGPT Apps SDK implementations with a docs-first, example-first workflow, then generate code that follows current Apps SDK and MCP Apps bridge patterns.

This skill produces:

- A primary app-archetype classification and repo-shape decision
- A tool plan (names, schemas, annotations, outputs)
- An upstream starting-point recommendation (official example, ext-apps example, or local fallback scaffold)
- An MCP server scaffold (resource registration, tool handlers, metadata)
- A widget scaffold (MCP Apps bridge first, `window.openai` compatibility/extensions second)
- A reusable Node + `@modelcontextprotocol/ext-apps` starter scaffold for low-dependency fallbacks
- A validation report against the minimum working repo contract
- Local dev and connector setup steps
- A short stakeholder summary of what the app does (when requested)

## When to Use

Use this skill when the task involves any of the following:

- **Scaffolding a new ChatGPT App** from scratch or adapting an upstream example
- **Designing or refactoring MCP tools** for a ChatGPT App (names, schemas, annotations, `structuredContent`, `_meta`)
- **Wiring the MCP Apps bridge** in a widget (`ui/notifications/tool-result`, `tools/call`, `ui/update-model-context`)
- **Applying `window.openai` compatibility APIs** (file upload, modal, display mode, theme, locale)
- **Setting resource metadata and security** (`_meta.ui.csp`, `_meta.ui.domain`, `connectDomains`, `resourceDomains`)
- **Preparing an app for local testing** in ChatGPT Developer Mode via HTTPS tunnel
- **Preparing an app for public submission** to the ChatGPT app directory
- **Troubleshooting** tool descriptors, widget rendering, CSP violations, or bridge communication

**Trigger keywords:** ChatGPT app, Apps SDK, MCP Apps bridge, widget, ext-apps, tool annotations, structuredContent, submission, connector, `window.openai`, MCP server scaffold.

## Prerequisites

- **Node.js** (v18+ recommended) installed and available on `PATH`
- **PowerShell** as the primary shell on the Windows host (`~\agent-skills\library\chatgpt-apps\`)
- **`$openai-docs` skill** or the OpenAI developer docs MCP server (`mcp__openaiDeveloperDocs__search_openai_docs`, `mcp__openaiDeveloperDocs__fetch_openai_doc`) for docs-first workflow
- **ngrok** or equivalent HTTPS tunneling tool for local ChatGPT testing
- **ChatGPT Developer Mode** access (Settings → Apps & Connectors → Advanced settings)
- **`@modelcontextprotocol/ext-apps`** package when using the fallback scaffold or ext-apps examples

## Procedure

### 0. Mandatory Docs-First Workflow

Before writing any code, fetch current Apps SDK documentation.

1. Invoke `$openai-docs` (preferred) or call the OpenAI docs MCP server directly.
2. Fetch current Apps SDK docs before writing code, especially these baseline pages:
   - `apps-sdk/build/mcp-server`
   - `apps-sdk/build/chatgpt-ui`
   - `apps-sdk/build/examples`
   - `apps-sdk/plan/tools`
   - `apps-sdk/reference`
3. Fetch `apps-sdk/quickstart` when scaffolding a new app or generating a first-pass implementation. Check the official examples repo/page before inventing a scaffold from scratch.
4. Fetch deployment/submission docs when the task includes local ChatGPT testing, hosting, or public launch:
   - `apps-sdk/deploy`
   - `apps-sdk/deploy/submission`
   - `apps-sdk/app-submission-guidelines`
5. Cite the docs URLs you used when explaining design choices or generated scaffolds.
6. Prefer current docs guidance over older repo patterns when they differ, and call out compatibility aliases explicitly.
7. If doc search times out or returns poor matches, fetch the canonical Apps SDK pages directly by URL and continue. Do not let search failure block scaffolding.

**Load these reference files at specific points:**

| Reference File | When to Load |
|---|---|
| `references/apps-sdk-docs-workflow.md` | At the start, for suggested doc queries and a compact checklist |
| `references/app-archetypes.md` | Before choosing examples or scaffolds, to classify the request into a supported app shape |
| `references/repo-contract-and-validation.md` | When generating or reviewing a repo, to keep output inside a stable "working app" contract |
| `references/search-fetch-standard.md` | When the app is connector-like, data-only, sync-oriented, or meant to work with company knowledge or deep research |
| `references/upstream-example-workflow.md` | When starting a greenfield app or deciding whether to adapt an upstream example or use the local fallback scaffold |
| `references/window-openai-patterns.md` | When the task needs ChatGPT-specific widget behavior or when translating repo examples that use wrapper-specific `app.*` helpers |
| `references/interactive-state-sync-patterns.md` | When the app has long-lived widget state, repeated interactions, or component-initiated tool calls (games, boards, maps, dashboards, editors) |

### 1. Classify the App Archetype

Before choosing examples, repo shape, or scaffolds, classify the request into one primary archetype and state it explicitly.

- `tool-only` — no UI, just MCP tools
- `vanilla-widget` — minimal HTML widget, MCP Apps bridge
- `react-widget` — React widget with `@modelcontextprotocol/ext-apps/react`
- `interactive-decoupled` — decoupled data/render tools, long-lived state
- `submission-ready` — public directory launch target

Infer the archetype unless a missing detail is truly blocking. Use the archetype to choose:

- Whether a UI is needed at all
- Whether to preserve a split `server/` + `web/` layout
- Whether to prefer official OpenAI examples, ext-apps examples, or the local fallback scaffold
- Which validation checks matter most
- Whether `search` and `fetch` should be the default read-only tool surface

Escalate to `submission-ready` only when the user asks for public launch, directory submission, or review-ready deployment.

**Load `references/app-archetypes.md`** for the full decision rubric.

### 2. Plan Tools Before Code

Define the tool surface area from user intents.

1. Use one job per tool.
2. Write tool descriptions that start with "Use this when..." behavior cues.
3. Make inputs explicit and machine-friendly (enums, required fields, bounds).
4. Decide whether each tool is data-only, render-only, or both.
5. Set annotations accurately:
   - `readOnlyHint`
   - `destructiveHint`
   - `openWorldHint`
   - `idempotentHint` (when true)
6. If the app is connector-like, data-only, sync-oriented, or intended for company knowledge or deep research, default to the standard `search` and `fetch` tools instead of inventing custom read-only equivalents.
7. For educational/demo apps, prefer one concept per tool so the model can pick the right example cleanly.
8. Group demo tools by learning objective: data into the widget, widget actions back into the conversation or tools, host/layout environment signals, and lifecycle/streaming behavior.

**Load `references/search-fetch-standard.md`** when `search` and `fetch` may be relevant.

### 3. Choose an App Architecture

Choose the simplest structure that fits the goal.

- **Minimal demo pattern** — for quick prototypes, workshops, or proofs of concept.
- **Decoupled data/render pattern** — for production UX so the widget does not re-render on every tool call.

Prefer the decoupled pattern for non-trivial apps:

- Data tools return reusable `structuredContent`.
- Render tools attach `_meta.ui.resourceUri` and optional `_meta["openai/outputTemplate"]`.
- Render tool descriptions state prerequisites (for example, "Call `search` first").

### 3a. Choose a Starting Point

For greenfield apps, prefer these starting points in order:

1. **Official OpenAI examples** — when a close example already matches the requested stack or interaction pattern.
2. **Version-matched `@modelcontextprotocol/ext-apps` examples** — when the user needs a lower-level or more portable MCP Apps baseline.
3. **`scripts/scaffold_node_ext_apps.mjs`** — only when no close example fits, the user wants a tiny Node + vanilla starter, or network access/example retrieval is undesirable.

Do not generate a large custom scaffold from scratch if a close upstream example already exists. Copy the smallest matching example, remove unrelated demo code, then patch it to the current docs and the user request.

**Load `references/upstream-example-workflow.md`** for the selection and adaptation rubric.

### 3b. Use the Starter Script (Low-Dependency Fallback)

Use `scripts/scaffold_node_ext_apps.mjs` only when:

- The user wants a quick, greenfield Node starter
- A vanilla HTML widget is acceptable
- No upstream example is a better starting point

**Skip it when:**

- A close official example exists
- The user already has an existing app structure
- The user needs a non-Node stack
- The user explicitly wants React first
- The user only wants a plan/review instead of code

Run it only after fetching current docs, then reconcile the generated files with the docs you fetched.

```powershell
node scripts/scaffold_node_ext_apps.mjs
```

The script generates a minimal `@modelcontextprotocol/ext-apps` server plus a vanilla HTML widget that uses the MCP Apps bridge by default. The generated widget keeps follow-up messaging on the standard `ui/message` bridge and only uses `window.openai` for optional host signals/extensions.

After running it, patch the generated output to match the current docs and the user request: adjust tool names/descriptions, annotations, resource metadata, URI versioning, and README/run instructions.

### 4. Scaffold the MCP Server

Generate a server that:

1. Registers a widget resource/template with the MCP Apps UI MIME type (`text/html;profile=mcp-app`) or the SDK constant (`RESOURCE_MIME_TYPE`) when using `@modelcontextprotocol/ext-apps/server`.
2. Registers tools with clear names, schemas, titles, and descriptions.
3. Returns `structuredContent` (model + widget), `content` (model narration), and `_meta` (widget-only data) intentionally.
4. Keeps handlers idempotent or documents non-idempotent behavior explicitly.
5. Includes tool status strings (`openai/toolInvocation/*`) when helpful in ChatGPT.

Keep `structuredContent` concise. Move large or sensitive widget-only payloads to `_meta`.

### 5. Scaffold the Widget UI

Use the MCP Apps bridge first for portability, then add ChatGPT-specific `window.openai` APIs when they materially improve UX.

1. Listen for `ui/notifications/tool-result` (JSON-RPC over `postMessage`).
2. Render from `structuredContent`.
3. Use `tools/call` for component-initiated tool calls.
4. Use `ui/update-model-context` only when UI state should change what the model sees.

Use `window.openai` for compatibility and extensions (file upload, modal, display mode, etc.), not as the only integration path for new apps.

#### API Surface Guardrails

Some examples wrap the bridge with an `app` object (for example, `@modelcontextprotocol/ext-apps/react`) and expose helper names like `app.sendMessage()`, `app.callServerTool()`, `app.openLink()`, or host getter methods.

- Treat those wrappers as implementation details or convenience layers, not the canonical public API to teach by default.
- For ChatGPT-facing guidance, prefer the current documented surface:
  - `window.openai.callTool(...)`
  - `window.openai.sendFollowUpMessage(...)`
  - `window.openai.openExternal(...)`
  - `window.openai.requestDisplayMode(...)`
  - Direct globals: `window.openai.theme`, `window.openai.locale`, `window.openai.displayMode`, `window.openai.toolInput`, `window.openai.toolOutput`, `window.openai.toolResponseMetadata`, `window.openai.widgetState`
- If you reference wrapper helpers from repo examples, map them back to the documented `window.openai` or MCP Apps bridge primitives and call out that the wrapper is not the normative API surface.

**Load `references/window-openai-patterns.md`** for the wrapper-to-canonical mapping and for React helper extraction patterns.

### 6. Add Resource Metadata and Security

Set resource metadata deliberately on the widget resource/template:

1. `_meta.ui.csp` with exact `connectDomains` and `resourceDomains`.
2. `_meta.ui.domain` for app submission-ready deployments.
3. `_meta.ui.prefersBorder` (or OpenAI compatibility alias when needed).
4. Optional `openai/widgetDescription` to reduce redundant narration.

Avoid `frameDomains` unless iframe embeds are core to the product.

### 7. Enforce the Minimum Working Repo Contract

Every generated repo should satisfy a small, stable contract before you consider it done.

- The repo shape matches the chosen archetype.
- The MCP server and tools are wired to a reachable `/mcp` endpoint.
- Tools have clear descriptions, accurate annotations, and UI metadata where needed.
- Connector-like, data-only, sync-oriented, and company-knowledge-style apps use the standard `search` and `fetch` tool shapes when relevant.
- The widget uses the MCP Apps bridge correctly when a UI exists.
- The repo includes enough scripts or commands for a user to run and check it locally.
- The response explicitly says what validation was run and what was not run.

**Load `references/repo-contract-and-validation.md`** for the detailed checklist and validation ladder.

### 8. Validate the Local Loop

Validate against the minimum working repo contract, not just "did files get created."

**Low-cost checks first:**

1. Static contract review.
2. Syntax or compile checks when feasible.
3. Local `/mcp` health check when feasible.

```powershell
# Example: check if the MCP server responds on the expected endpoint
curl http://localhost:3000/mcp
```

**Runtime checks next:**

4. Verify tool descriptors and widget rendering in MCP Inspector.
5. Test the app in ChatGPT developer mode through HTTPS tunneling.
6. Exercise retries and repeated tool calls to confirm idempotent behavior.
7. Check widget updates after host events and follow-up tool calls.

If you are only delivering a scaffold and are not installing dependencies, still run low-cost checks and say exactly what you did not run.

### 9. Connect and Test in ChatGPT (Developer Mode)

For local development, include explicit ChatGPT setup steps.

1. Run the MCP server locally on `http://localhost:<port>/mcp`.
2. Expose the local server with a public HTTPS tunnel:

```powershell
ngrok http <port>
```

3. Use the tunneled HTTPS URL plus `/mcp` path when connecting from ChatGPT.
4. In ChatGPT, enable Developer Mode under **Settings → Apps & Connectors → Advanced settings**.
5. In ChatGPT app settings, create a new app for the remote MCP server and paste the public MCP URL.
6. Tell users to refresh the app after MCP tool/metadata changes so ChatGPT reloads the latest descriptors.

> **Note:** Some docs/screenshots still use older "connector" terminology. Prefer current product wording ("app") while acknowledging both labels when giving step-by-step instructions.

### 10. Plan Production Hosting and Deployment

When the user asks to deploy or prepare for launch, generate hosting guidance for the MCP server (and widget assets if hosted separately).

1. Host behind a stable public HTTPS endpoint (not a tunnel) with dependable TLS.
2. Preserve low-latency streaming behavior on `/mcp`.
3. Configure secrets outside the repo (environment variables / secret manager).
4. Add logging, request latency tracking, and error visibility for tool calls.
5. Add basic observability (CPU, memory, request volume) and a troubleshooting path.
6. Re-test the hosted endpoint in ChatGPT Developer Mode before submission.

### 11. Prepare Submission and Publish (Public Apps Only)

Only include these steps when the user intends a public directory listing.

1. Use `apps-sdk/deploy/submission` for the submission flow and `apps-sdk/app-submission-guidelines` for review requirements.
2. Keep private/internal apps in Developer Mode instead of submitting.
3. Confirm org verification and Owner-role prerequisites before submission work.
4. Ensure the MCP server uses a public production endpoint (no localhost/testing URLs) and has submission-ready CSP configured.
5. Prepare submission artifacts: app metadata, logo/screenshots, privacy policy URL, support contact, test prompts/responses, localization info.
6. If auth is required, include review-safe demo credentials and test the login path end-to-end.
7. Submit for review in the Platform dashboard, monitor review status, and publish only after approval.

## Interactive State Guidance

**Load `references/interactive-state-sync-patterns.md`** when the app has long-lived widget state, repeated interactions, or component-initiated tool calls (for example, games, boards, maps, dashboards, editors).

Use it to choose patterns for:

- State snapshots plus monotonic event tokens (`stateVersion`, `resetCount`, etc.)
- Idempotent retry-safe handlers
- `structuredContent` vs `_meta` partitioning
- MCP Apps bridge-first update flows with optional `window.openai` compatibility
- Decoupled data/render tool architecture for more complex interactive apps

## Output Expectations

When using this skill to scaffold code, produce output in this order unless the user asks otherwise:

> For direct scaffold requests, do not stop at the plan: give the brief plan, then create the files immediately.

1. Primary app archetype chosen and why
2. Tool plan and architecture choice (minimal vs decoupled)
3. Upstream starting point chosen (official example, ext-apps example, or local fallback scaffold) and why
4. Doc pages/URLs used from `$openai-docs`
5. File tree to create or modify
6. Implementation (server + widget)
7. Validation performed against the minimum working repo contract
8. Local run/test instructions (including tunnel + ChatGPT Developer Mode app setup)
9. Deployment/hosting guidance (if requested or implied)
10. Submission-readiness checklist (for public launch requests)
11. Risks, gaps, and follow-up improvements

## Prompt Guidance

Use prompts that explicitly pair this skill with `$openai-docs` so the resulting scaffold is grounded in current docs.

Preferred prompt patterns:

- `Use $chatgpt-apps with $openai-docs to scaffold a ChatGPT app for <use case> with a <TS/Python> MCP server and <React/vanilla> widget.`
- `Use $chatgpt-apps with $openai-docs to adapt the closest official Apps SDK example into a ChatGPT app for <use case>.`
- `Use $chatgpt-apps and $openai-docs to refactor this Apps SDK demo into a production-ready structure with tool annotations, CSP, and URI versioning.`
- `Use $chatgpt-apps with $openai-docs to plan tools first, then generate the MCP server and widget code.`

When responding, ask for or infer these inputs before coding:

- Use case and primary user flows
- Read-only vs mutating tools
- Demo vs production target
- Private/internal use vs public directory submission
- Backend language and UI stack
- Auth requirements
- External API domains for CSP allowlists
- Hosting target and local dev approach
- Org ownership/verification readiness (for submission tasks)

## Pitfalls

- **Do not generate a large custom scaffold from scratch if a close upstream example already exists.** Copy the smallest matching example, remove unrelated demo code, then patch it to current docs.
- **Do not treat wrapper `app.*` helpers as the canonical public API.** They are implementation details. Map them back to `window.openai` or MCP Apps bridge primitives.
- **Do not use `window.openai` as the only integration path for new apps.** Use the MCP Apps bridge first for portability.
- **Do not let doc search failure block scaffolding.** If search times out or returns poor matches, fetch canonical Apps SDK pages directly by URL.
- **Do not prefer older repo patterns over current docs when they differ.** Call out compatibility aliases explicitly.
- **Do not skip validation.** Even when only delivering a scaffold, run low-cost checks and state exactly what was not run.
- **Do not submit private/internal apps to the public directory.** Keep them in Developer Mode.
- **Do not use localhost/testing URLs for submission.** Ensure the MCP server uses a public production endpoint.
- **Do not put large or sensitive payloads in `structuredContent`.** Move them to `_meta`.
- **Do not use `frameDomains` unless iframe embeds are core to the product.**
- **Do not mix multiple primary archetypes.** Pick one and escalate only when the user explicitly asks for public launch.
- **Do not forget to tell users to refresh the app** after MCP tool/metadata changes so ChatGPT reloads the latest descriptors.

## Verification

After generating or modifying a ChatGPT App, verify the following:

### Static Checks

```powershell
# Verify file tree matches the chosen archetype
Get-ChildItem -Recurse -Name | Select-String -Pattern "server|web|package.json"

# Verify MCP server file has no syntax errors (Node.js)
node --check server/index.ts
# or
npx tsc --noEmit
```

### Local MCP Health Check

```powershell
# Start the MCP server
npm run dev

# In a separate terminal, verify the /mcp endpoint responds
curl http://localhost:3000/mcp
```

### Tool Descriptor Verification

- Confirm each tool has: name, description starting with "Use this when...", input schema, accurate annotations (`readOnlyHint`, `destructiveHint`, `openWorldHint`, `idempotentHint`).
- Confirm `structuredContent`, `content`, and `_meta` are returned intentionally per tool.
- Confirm widget resource/template uses MIME type `text/html;profile=mcp-app` or `RESOURCE_MIME_TYPE`.

### Widget Bridge Verification

- Confirm the widget listens for `ui/notifications/tool-result` via `postMessage`.
- Confirm rendering comes from `structuredContent`.
- Confirm `tools/call` is used for component-initiated tool calls.
- Confirm `window.openai` APIs are used only for extensions, not as the sole integration path.

### CSP and Metadata Verification

- Confirm `_meta.ui.csp` has exact `connectDomains` and `resourceDomains`.
- Confirm `_meta.ui.domain` is set for submission-ready deployments.
- Confirm no `frameDomains` unless iframe embeds are core to the product.

### ChatGPT Developer Mode Verification

1. Confirm the MCP server is running on `http://localhost:<port>/mcp`.
2. Confirm ngrok tunnel is active and the HTTPS URL is reachable.
3. Confirm the app was created in ChatGPT with the tunneled HTTPS URL + `/mcp` path.
4. Confirm Developer Mode is enabled under **Settings → Apps & Connectors → Advanced settings**.
5. Confirm tool calls execute and widget renders correctly in ChatGPT.
6. Confirm repeated tool calls behave idempotently.
7. Confirm widget updates after host events and follow-up tool calls.

### Submission Readiness Verification (Public Apps Only)

- [ ] Public production HTTPS endpoint (no localhost/tunnel URLs)
- [ ] Submission-ready CSP configured
- [ ] Org verification and Owner-role confirmed
- [ ] App metadata, logo/screenshots, privacy policy URL, support contact prepared
- [ ] Test prompts/responses documented
- [ ] Localization info prepared
- [ ] Review-safe demo credentials included (if auth required)
- [ ] Login path tested end-to-end (if auth required)

## References

- `references/app-archetypes.md` — Classifying requests into supported app shapes
- `references/apps-sdk-docs-workflow.md` — Doc queries, page targets, and code-generation checklist
- `references/interactive-state-sync-patterns.md` — Reusable patterns for stateful or highly interactive widget apps
- `references/repo-contract-and-validation.md` — Minimum working repo contract and lightweight validation ladder
- `references/search-fetch-standard.md` — When and how to default to the standard `search` and `fetch` tools
- `references/upstream-example-workflow.md` — Choosing between official examples, ext-apps examples, and the local fallback scaffold
- `references/window-openai-patterns.md` — ChatGPT-specific extensions, wrapper API translation, and React helper patterns
- `scripts/scaffold_node_ext_apps.mjs` — Minimal Node + `@modelcontextprotocol/ext-apps` fallback starter scaffold

## Related Skills

- `$openai-docs` — Fetch current OpenAI developer documentation; always pair with this skill for docs-first scaffolding
- `mcp__openaiDeveloperDocs__search_openai_docs` — Direct docs search when `$openai-docs` is unavailable
- `mcp__openaiDeveloperDocs__fetch_openai_doc` — Direct doc fetch when `$openai-docs` is unavailable
