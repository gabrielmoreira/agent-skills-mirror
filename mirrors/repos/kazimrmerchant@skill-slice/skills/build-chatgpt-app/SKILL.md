---
name: build-chatgpt-app
description: "Scaffolds ChatGPT Apps SDK apps that pair an MCP server with widget UI (MCP Apps bridge, window.openai, CSP, tool plans, Developer Mode, directory submission). Use when designing ChatGPT app tools, registering UI resources, wiring ext-apps, or producing a docs-aligned scaffold. Not for generic MCP servers outside ChatGPT Apps (mcp-server-authoring). Never invent window.openai APIs from memory — fetch current Apps SDK docs first."
version: 1.0.1
---

# Build ChatGPT App

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

- Scaffolding a new ChatGPT App (MCP server + widget UI)
- Planning tool surfaces for an Apps SDK project
- Adapting an official OpenAI example or `@modelcontextprotocol/ext-apps` example into a ChatGPT app
- Refactoring an existing Apps SDK demo into a production-ready structure
- Wiring the MCP Apps bridge (`postMessage` JSON-RPC) or `window.openai` compatibility APIs
- Applying Apps SDK metadata, CSP allowlists, domain settings, or URI versioning
- Preparing an app for local ChatGPT Developer Mode testing or public submission
- Troubleshooting tool descriptors, widget rendering, or connector setup

**Trigger keywords:** ChatGPT app, Apps SDK, MCP server, widget, ext-apps, connector, scaffold, tool plan, submission, `window.openai`, MCP Apps bridge, structuredContent, resourceUri.

## Prerequisites

- **Docs-first workflow is mandatory.** Use `$openai-docs` first whenever building or changing a ChatGPT Apps SDK app. If `$openai-docs` is unavailable, use `mcp__openaiDeveloperDocs__search_openai_docs` and `mcp__openaiDeveloperDocs__fetch_openai_doc`.
- **Node.js** installed for the fallback scaffold script (`scripts/scaffold_node_ext_apps.mjs`).
- **PowerShell** as the primary shell on Windows host. All commands below assume PowerShell unless noted.
- **ngrok** (or equivalent HTTPS tunnel) for local ChatGPT Developer Mode testing.
- **MCP Inspector** for runtime validation of tool descriptors and widget rendering.
- **OpenAI Platform dashboard access** for submission tasks (org verification + Owner role).

## Procedure

### 0. Classify the App Archetype

Before choosing examples, repo shape, or scaffolds, classify the request into one primary archetype and state it explicitly.

- `tool-only` — no UI; MCP server with tools only
- `vanilla-widget` — minimal HTML widget via MCP Apps bridge
- `react-widget` — React widget using `@modelcontextprotocol/ext-apps/react` or similar
- `interactive-decoupled` — decoupled data/render tools with stateful widget
- `submission-ready` — public directory launch target

**Rules:**
- Prefer a single primary archetype instead of mixing several.
- If the request is broad, infer the smallest archetype that can still satisfy it.
- Escalate to `submission-ready` only when the user asks for public launch, directory submission, or review-ready deployment.
- Call out the chosen archetype in your response so the user can correct it early.

**Load `references/app-archetypes.md`** for the full decision rubric.

### 1. Plan Tools Before Code

Define the tool surface area from user intents before writing any implementation code.

1. Use one job per tool.
2. Write tool descriptions that start with "Use this when..." behavior cues.
3. Make inputs explicit and machine-friendly (enums, required fields, bounds).
4. Decide whether each tool is data-only, render-only, or both.
5. Set annotations accurately: `readOnlyHint`, `destructiveHint`, `openWorldHint`; add `idempotentHint` when true.
6. If the app is connector-like, data-only, sync-oriented, or intended for company knowledge or deep research, default to the standard `search` and `fetch` tools instead of inventing custom read-only equivalents.
7. For educational/demo apps, prefer one concept per tool so the model can pick the right example cleanly.
8. Group demo tools by learning objective: data into the widget, widget actions back into the conversation or tools, host/layout environment signals, and lifecycle/streaming behavior.

**Load `references/search-fetch-standard.md`** when `search` and `fetch` may be relevant.

### 2. Choose an App Architecture

Choose the simplest structure that fits the goal.

- **Minimal demo pattern** — for quick prototypes, workshops, or proofs of concept.
- **Decoupled data/render pattern** — for production UX so the widget does not re-render on every tool call.

Prefer the decoupled pattern for non-trivial apps:
- Data tools return reusable `structuredContent`.
- Render tools attach `_meta.ui.resourceUri` and optional `_meta["openai/outputTemplate"]`.
- Render tool descriptions state prerequisites (for example, "Call `search` first").

### 2a. Start From an Upstream Example When One Fits

Default to upstream examples for greenfield work when they are close to the requested app.

1. Check the **official OpenAI examples** first for ChatGPT-facing apps, polished UI patterns, React components, file upload flows, modal flows, or apps that resemble the docs examples.
2. Use **`@modelcontextprotocol/ext-apps` examples** when the request is closer to raw MCP Apps bridge/server wiring, or when version-matched package patterns matter more than ChatGPT-specific polish.
3. Pick the smallest matching example and copy only the relevant files; do not transplant an entire showcase app unchanged.
4. After copying, reconcile the example with the current docs you fetched: tool names/descriptions, annotations, `_meta.ui.*`, CSP, URI versioning, and local run instructions.
5. State which example you chose and why in one sentence.

**Load `references/upstream-example-workflow.md`** for the selection and adaptation rubric.

### 2b. Use the Starter Script When a Low-Dependency Fallback Helps

Use `scripts/scaffold_node_ext_apps.mjs` only when:
- The user wants a quick, greenfield Node starter
- A vanilla HTML widget is acceptable
- No upstream example is a better starting point

**Skip the script when:**
- A close official example exists
- The user already has an existing app structure
- They need a non-Node stack
- They explicitly want React first
- They only want a plan/review instead of code

**To run the fallback scaffold (PowerShell):**

```powershell
node scripts/scaffold_node_ext_apps.mjs
```

After running it:
- Patch the generated output to match the current docs and the user request: adjust tool names/descriptions, annotations, resource metadata, URI versioning, and README/run instructions.
- The generated widget keeps follow-up messaging on the standard `ui/message` bridge and only uses `window.openai` for optional host signals/extensions.
- If you choose the script instead of an upstream example, say why the fallback is better for that request.

### 3. Scaffold the MCP Server

Generate a server that:

1. Registers a widget resource/template with the MCP Apps UI MIME type (`text/html;profile=mcp-app`) or the SDK constant (`RESOURCE_MIME_TYPE`) when using `@modelcontextprotocol/ext-apps/server`.
2. Registers tools with clear names, schemas, titles, and descriptions.
3. Returns `structuredContent` (model + widget), `content` (model narration), and `_meta` (widget-only data) intentionally.
4. Keeps handlers idempotent or documents non-idempotent behavior explicitly.
5. Includes tool status strings (`openai/toolInvocation/*`) when helpful in ChatGPT.

**Keep `structuredContent` concise.** Move large or sensitive widget-only payloads to `_meta`.

### 4. Scaffold the Widget UI

Use the MCP Apps bridge first for portability, then add ChatGPT-specific `window.openai` APIs when they materially improve UX.

1. Listen for `ui/notifications/tool-result` (JSON-RPC over `postMessage`).
2. Render from `structuredContent`.
3. Use `tools/call` for component-initiated tool calls.
4. Use `ui/update-model-context` only when UI state should change what the model sees.

Use `window.openai` for compatibility and extensions (file upload, modal, display mode, etc.), not as the only integration path for new apps.

#### API Surface Guardrails

- Some examples wrap the bridge with an `app` object (for example, `@modelcontextprotocol/ext-apps/react`) and expose helper names like `app.sendMessage()`, `app.callServerTool()`, `app.openLink()`, or host getter methods.
- Treat those wrappers as implementation details or convenience layers, not the canonical public API to teach by default.
- For ChatGPT-facing guidance, prefer the current documented surface:
  - `window.openai.callTool(...)`
  - `window.openai.sendFollowUpMessage(...)`
  - `window.openai.openExternal(...)`
  - `window.openai.requestDisplayMode(...)`
  - Direct globals: `window.openai.theme`, `window.openai.locale`, `window.openai.displayMode`, `window.openai.toolInput`, `window.openai.toolOutput`, `window.openai.toolResponseMetadata`, `window.openai.widgetState`
- If you reference wrapper helpers from repo examples, map them back to the documented `window.openai` or MCP Apps bridge primitives and call out that the wrapper is not the normative API surface.

**Load `references/window-openai-patterns.md`** for the wrapper-to-canonical mapping and for React helper extraction patterns.

### 5. Add Resource Metadata and Security

Set resource metadata deliberately on the widget resource/template:

- `_meta.ui.csp` with exact `connectDomains` and `resourceDomains`
- `_meta.ui.domain` for app submission-ready deployments
- `_meta.ui.prefersBorder` (or OpenAI compatibility alias when needed)
- Optional `openai/widgetDescription` to reduce redundant narration

Avoid `frameDomains` unless iframe embeds are core to the product.

### 5a. Enforce a Minimum Working Repo Contract

Every generated repo should satisfy a small, stable contract before you consider it done:

- The repo shape matches the chosen archetype.
- The MCP server and tools are wired to a reachable `/mcp` endpoint.
- Tools have clear descriptions, accurate annotations, and UI metadata where needed.
- Connector-like, data-only, sync-oriented, and company-knowledge-style apps use the standard `search` and `fetch` tool shapes when relevant.
- The widget uses the MCP Apps bridge correctly when a UI exists.
- The repo includes enough scripts or commands for a user to run and check it locally.
- The response explicitly says what validation was run and what was not run.

**Load `references/repo-contract-and-validation.md`** for the detailed checklist and validation ladder.

### 6. Validate the Local Loop

Validate against the minimum working repo contract, not just "did files get created."

**Lowest-cost checks first:**
1. Static contract review
2. Syntax or compile checks when feasible
3. Local `/mcp` health check when feasible

**Then move up to runtime checks:**
4. Verify tool descriptors and widget rendering in MCP Inspector
5. Test the app in ChatGPT developer mode through HTTPS tunneling
6. Exercise retries and repeated tool calls to confirm idempotent behavior
7. Check widget updates after host events and follow-up tool calls

If you are only delivering a scaffold and are not installing dependencies, still run low-cost checks and say exactly what you did not run.

**Load `references/repo-contract-and-validation.md`** for the validation ladder.

### 7. Connect and Test in ChatGPT (Developer Mode)

For local development, include explicit ChatGPT setup steps:

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

### 8. Plan Production Hosting and Deployment

When the user asks to deploy or prepare for launch, generate hosting guidance for the MCP server (and widget assets if hosted separately):

1. Host behind a stable public HTTPS endpoint (not a tunnel) with dependable TLS.
2. Preserve low-latency streaming behavior on `/mcp`.
3. Configure secrets outside the repo (environment variables / secret manager).
4. Add logging, request latency tracking, and error visibility for tool calls.
5. Add basic observability (CPU, memory, request volume) and a troubleshooting path.
6. Re-test the hosted endpoint in ChatGPT Developer Mode before submission.

### 9. Prepare Submission and Publish (Public Apps Only)

Only include these steps when the user intends a public directory listing:

1. Use `apps-sdk/deploy/submission` for the submission flow and `apps-sdk/app-submission-guidelines` for review requirements.
2. Keep private/internal apps in Developer Mode instead of submitting.
3. Confirm org verification and Owner-role prerequisites before submission work.
4. Ensure the MCP server uses a public production endpoint (no localhost/testing URLs) and has submission-ready CSP configured.
5. Prepare submission artifacts: app metadata, logo/screenshots, privacy policy URL, support contact, test prompts/responses, localization info.
6. If auth is required, include review-safe demo credentials and test the login path end-to-end.
7. Submit for review in the Platform dashboard, monitor review status, and publish only after approval.

## Mandatory Docs-First Workflow

Use `$openai-docs` first whenever building or changing a ChatGPT Apps SDK app.

1. Invoke `$openai-docs` (preferred) or call the OpenAI docs MCP server directly.
2. Fetch current Apps SDK docs before writing code, especially (baseline pages):
   - `apps-sdk/build/mcp-server`
   - `apps-sdk/build/chatgpt-ui`
   - `apps-sdk/build/examples`
   - `apps-sdk/plan/tools`
   - `apps-sdk/reference`
3. Fetch `apps-sdk/quickstart` when scaffolding a new app or generating a first-pass implementation, and check the official examples repo/page before inventing a scaffold from scratch.
4. Fetch deployment/submission docs when the task includes local ChatGPT testing, hosting, or public launch:
   - `apps-sdk/deploy`
   - `apps-sdk/deploy/submission`
   - `apps-sdk/app-submission-guidelines`
5. Cite the docs URLs you used when explaining design choices or generated scaffolds.
6. Prefer current docs guidance over older repo patterns when they differ, and call out compatibility aliases explicitly.
7. If doc search times out or returns poor matches, fetch the canonical Apps SDK pages directly by URL and continue; do not let search failure block scaffolding.

If `$openai-docs` is unavailable, use:
- `mcp__openaiDeveloperDocs__search_openai_docs`
- `mcp__openaiDeveloperDocs__fetch_openai_doc`

**Load `references/apps-sdk-docs-workflow.md`** for suggested doc queries and a compact checklist.

## Prompt Guidance

Use prompts that explicitly pair this skill with `$openai-docs` so the resulting scaffold is grounded in current docs.

Preferred prompt patterns:

- `Use $build-chatgpt-app with $openai-docs to scaffold a ChatGPT app for <use case> with a <TS/Python> MCP server and <React/vanilla> widget.`
- `Use $build-chatgpt-app with $openai-docs to adapt the closest official Apps SDK example into a ChatGPT app for <use case>.`
- `Use $build-chatgpt-app and $openai-docs to refactor this Apps SDK demo into a production-ready structure with tool annotations, CSP, and URI versioning.`
- `Use $build-chatgpt-app with $openai-docs to plan tools first, then generate the MCP server and widget code.`

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

## Interactive State Guidance

**Load `references/interactive-state-sync-patterns.md`** when the app has long-lived widget state, repeated interactions, or component-initiated tool calls (for example, games, boards, maps, dashboards, editors).

Use it to choose patterns for:

- State snapshots plus monotonic event tokens (`stateVersion`, `resetCount`, etc.)
- Idempotent retry-safe handlers
- `structuredContent` vs `_meta` partitioning
- MCP Apps bridge-first update flows with optional `window.openai` compatibility
- Decoupled data/render tool architecture for more complex interactive apps

## Default Starting-Point Order

For greenfield apps, prefer these starting points in order:

1. **Official OpenAI examples** when a close example already matches the requested stack or interaction pattern.
2. **Version-matched `@modelcontextprotocol/ext-apps` examples** when the user needs a lower-level or more portable MCP Apps baseline.
3. **`scripts/scaffold_node_ext_apps.mjs`** only when no close example fits, the user wants a tiny Node + vanilla starter, or network access/example retrieval is undesirable.

Do not generate a large custom scaffold from scratch if a close upstream example already exists. Copy the smallest matching example, remove unrelated demo code, then patch it to the current docs and the user request.

## Output Expectations

When using this skill to scaffold code, produce output in this order unless the user asks otherwise:

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

For direct scaffold requests, do not stop at the plan: give the brief plan, then create the files immediately.

## Pitfalls

- **Do not invent APIs or CLI flags.** Only use documented `window.openai.*` methods and MCP Apps bridge primitives. Wrapper helpers (`app.sendMessage()`, `app.callServerTool()`, etc.) are implementation details, not the canonical public API.
- **Do not skip the docs-first workflow.** Always fetch current Apps SDK docs before writing code. If search times out, fetch canonical pages directly by URL.
- **Do not generate a large custom scaffold from scratch if a close upstream example exists.** Copy the smallest matching example, remove unrelated demo code, then patch.
- **Do not use `frameDomains` unless iframe embeds are core to the product.**
- **Do not put large or sensitive widget-only payloads in `structuredContent`.** Move them to `_meta`.
- **Do not use `ui/update-model-context` casually.** Only when UI state should change what the model sees.
- **Do not submit private/internal apps to the public directory.** Keep them in Developer Mode.
- **Do not use localhost/testing URLs for submission.** The MCP server must use a public production endpoint.
- **Do not let doc search failure block scaffolding.** Fetch canonical pages directly by URL and continue.
- **Do not mix multiple archetypes.** Pick one primary archetype; escalate to `submission-ready` only for public launch.
- **Do not forget to tell users to refresh the app** after MCP tool/metadata changes so ChatGPT reloads the latest descriptors.
- **Do not drop the "what validation was run and what was not run" statement** — always include it.

## Verification

### Static Contract Review

Check the generated repo against the minimum working repo contract:

```powershell
# Verify repo structure matches archetype
Get-ChildItem -Recurse -Name | Select-String -Pattern "server|web|widget|mcp"
```

### Syntax / Compile Checks

```powershell
# TypeScript compile check (if applicable)
npx tsc --noEmit

# Node syntax check for server entry
node --check server/index.ts
```

### Local /mcp Health Check

```powershell
# Start the server
npm run dev

# In another terminal, verify the /mcp endpoint responds
curl http://localhost:<port>/mcp
```

### MCP Inspector Validation

```powershell
# Launch MCP Inspector against the local server
npx @modelcontextprotocol/inspector node server/index.ts
```

Verify:
- Tool descriptors appear with correct names, schemas, and annotations
- Widget resource/template is registered with `text/html;profile=mcp-app` MIME type
- `structuredContent` and `_meta` are returned correctly

### ChatGPT Developer Mode Test

```powershell
# Tunnel the local server
ngrok http <port>
```

Then in ChatGPT:
1. Settings → Apps & Connectors → Advanced settings → enable Developer Mode
2. Create a new app, paste the tunneled HTTPS URL + `/mcp`
3. Exercise each tool and confirm widget rendering
4. Test repeated tool calls for idempotent behavior
5. Check widget updates after host events and follow-up tool calls

### Submission Readiness Checklist (Public Apps Only)

- [ ] Public production HTTPS endpoint (no localhost/tunnel)
- [ ] Submission-ready CSP configured (`_meta.ui.csp` with exact `connectDomains` and `resourceDomains`)
- [ ] `_meta.ui.domain` set for app submission-ready deployments
- [ ] Org verification and Owner-role confirmed
- [ ] Submission artifacts prepared (metadata, logo/screenshots, privacy policy URL, support contact, test prompts/responses, localization info)
- [ ] If auth required: review-safe demo credentials included and login path tested end-to-end
- [ ] Submitted for review in Platform dashboard; publish only after approval

## References

| File | When to Load |
|------|-------------|
| `references/app-archetypes.md` | Classifying requests into supported app shapes before choosing examples or scaffolds |
| `references/apps-sdk-docs-workflow.md` | Doc queries, page targets, and code-generation checklist for the docs-first workflow |
| `references/interactive-state-sync-patterns.md` | Long-lived widget state, repeated interactions, or component-initiated tool calls (games, boards, maps, dashboards, editors) |
| `references/repo-contract-and-validation.md` | Generating or reviewing a repo against the minimum working repo contract and validation ladder |
| `references/search-fetch-standard.md` | Connector-like, data-only, sync-oriented apps, or apps meant to work with company knowledge or deep research |
| `references/upstream-example-workflow.md` | Starting a greenfield app or deciding whether to adapt an upstream example or use the local fallback scaffold |
| `references/window-openai-patterns.md` | ChatGPT-specific widget behavior or translating repo examples that use wrapper-specific `app.*` helpers |
| `scripts/scaffold_node_ext_apps.mjs` | Minimal Node + `@modelcontextprotocol/ext-apps` fallback starter scaffold (vanilla HTML widget) |
