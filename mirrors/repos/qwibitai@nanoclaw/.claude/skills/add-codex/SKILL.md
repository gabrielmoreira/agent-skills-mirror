---
name: add-codex
description: Use Codex (CLI + AppServer) as the full agent provider — planning, tool orchestration, native compaction, MCP tools, session resume — in place of the Claude Agent SDK. ChatGPT subscription or OPENAI_API_KEY. Per-group via agent_provider. Distinct from using OpenAI as an MCP tool (where Claude remains the planner).
---

# Codex agent provider

NanoClaw runs agents in a long-lived **poll loop** inside the container. The backend is selected with **`AGENT_PROVIDER`** (`claude` | `opencode` | `codex` | `mock`).

Trunk ships with only the `claude` provider baked in. This skill copies the Codex provider files in from the `providers` branch, wires them into the host and container barrels, updates the Dockerfile to install the Codex CLI, and rebuilds the image.

The Codex provider runs `codex app-server` as a child process and speaks JSON-RPC over stdio. That gives it native session resume, streaming events, MCP tool access, and `thread/compact/start` compaction — same feature bar as the Claude Agent SDK, without the Anthropic-only lock-in.

## Install

### Pre-flight

If all of the following are already present, skip to **Configuration**:

- `src/providers/codex.ts`
- `src/providers/codex-registration.test.ts`
- `container/agent-runner/src/providers/codex.ts`
- `container/agent-runner/src/providers/codex-app-server.ts`
- `container/agent-runner/src/providers/codex.factory.test.ts`
- `container/agent-runner/src/providers/codex-registration.test.ts`
- `container/agent-runner/src/providers/codex-dockerfile.test.ts`
- `import './codex.js';` line in `src/providers/index.ts`
- `import './codex.js';` line in `container/agent-runner/src/providers/index.ts`
- `ARG CODEX_VERSION` and `"@openai/codex@${CODEX_VERSION}"` in the pnpm global-install block in `container/Dockerfile`

Missing pieces — continue below. All steps are idempotent; re-running is safe.

### 1. Fetch the providers branch

```bash
git fetch origin providers
```

### 2. Copy the Codex source files and tests

Wholesale copies (owned entirely by this skill — user edits to these files won't survive a re-run, as designed):

```bash
git show origin/providers:src/providers/codex.ts                                         > src/providers/codex.ts
git show origin/providers:src/providers/codex-registration.test.ts                       > src/providers/codex-registration.test.ts
git show origin/providers:container/agent-runner/src/providers/codex.ts                  > container/agent-runner/src/providers/codex.ts
git show origin/providers:container/agent-runner/src/providers/codex-app-server.ts       > container/agent-runner/src/providers/codex-app-server.ts
git show origin/providers:container/agent-runner/src/providers/codex.factory.test.ts     > container/agent-runner/src/providers/codex.factory.test.ts
git show origin/providers:container/agent-runner/src/providers/codex-registration.test.ts > container/agent-runner/src/providers/codex-registration.test.ts
```

The two `codex-registration.test.ts` files are the **registration guards**. Each imports only the real barrel — the host one calls `listProviderContainerConfigNames()` from `src/providers/index.ts`, the container one calls `listProviderNames()` from `container/agent-runner/src/providers/index.ts` — and asserts `codex` is present. They go red the instant a barrel import line is deleted or drifts. (`codex.factory.test.ts` imports `./codex.js` directly and self-registers, so it stays green even if the barrel line is gone — keep it as a unit test of provider behavior, but it is **not** the registration guard.)

If `git show origin/providers:.../codex-registration.test.ts` errors with `path ... does not exist`, the registration tests have not landed on `origin/providers` yet. Run `git fetch origin providers` again; once the branch carries them, the copies above succeed. The rest of the install proceeds regardless — the Dockerfile and factory tests still run.

Copy the Dockerfile structural test that ships with this skill into the container provider tree:

```bash
cp .claude/skills/add-codex/codex-dockerfile.test.ts container/agent-runner/src/providers/codex-dockerfile.test.ts
```

`codex-dockerfile.test.ts` reads the real `container/Dockerfile` and asserts the `ARG CODEX_VERSION=` line and the `pnpm install -g "@openai/codex@${CODEX_VERSION}"` line are both present. The Codex CLI is a binary, not an importable package, so the registration tests cannot see it — this structural test is what guards the Dockerfile edits in step 4.

### 3. Append the self-registration imports

Each barrel gets one line — alphabetical placement keeps diffs small.

`src/providers/index.ts`:

```typescript
import './codex.js';
```

`container/agent-runner/src/providers/index.ts`:

```typescript
import './codex.js';
```

### 4. Add the Codex CLI to the container Dockerfile

Two edits to `container/Dockerfile`, both idempotent (skip if already present):

**(a)** In the "Pin CLI versions" ARG block (around line 18), add after `ARG CLAUDE_CODE_VERSION=...`:

```dockerfile
ARG CODEX_VERSION=0.124.0
```

**(b)** Add a new standalone `RUN` block for the Codex CLI, after the existing per-CLI install blocks (around line 106, right after the `@anthropic-ai/claude-code` block). The Dockerfile splits each global CLI into its own layer for cache granularity — keep that pattern; do not collapse them into a single combined `pnpm install -g` call:

```dockerfile
RUN --mount=type=cache,target=/root/.cache/pnpm \
    pnpm install -g "@openai/codex@${CODEX_VERSION}"
```

Note: **no agent-runner package dependency** — Codex is a CLI binary, not a library. Unlike OpenCode, there's nothing to add to `container/agent-runner/package.json`.

### 5. Build and validate

```bash
pnpm run build                                                          # host
pnpm exec vitest run src/providers/codex-registration.test.ts          # host registration guard
pnpm exec tsc -p container/agent-runner/tsconfig.json --noEmit         # container typecheck
cd container/agent-runner && bun test src/providers/codex-registration.test.ts && cd -   # container registration guard
cd container/agent-runner && bun test src/providers/codex-dockerfile.test.ts && cd -      # Dockerfile structural guard
./container/build.sh                                                    # agent image
```

All must be clean before proceeding.

- The **host** `codex-registration.test.ts` imports the real host barrel (`src/providers/index.ts`) and asserts `listProviderContainerConfigNames()` contains `codex`. It goes red if the `import './codex.js';` line is deleted or drifts, or if the barrel fails to evaluate.
- The **container** `codex-registration.test.ts` imports the real container barrel (`container/agent-runner/src/providers/index.ts`) and asserts `listProviderNames()` contains `codex`. Same failure surface for the container-side import line.
- The **Dockerfile** `codex-dockerfile.test.ts` reads `container/Dockerfile` and asserts the `ARG CODEX_VERSION=` and `@openai/codex@${CODEX_VERSION}` install lines are present — red if either edit is dropped.

The `@openai/codex` CLI binary is guarded by the Dockerfile structural test plus the container build (`./container/build.sh` fails if the install line is bad), **not** by the registration test — Codex is a CLI binary, not an importable package, so nothing imports it for the registration guard to trip on. To confirm the binary is actually present after the image rebuild, probe it inside a running container with `docker exec <container> codex --version`.

The host-side provider also consumes core APIs (per-session `~/.codex` mount, env passthrough); that typed core-API consumption is guarded by `pnpm run build`.

## Configuration

Codex supports two primary auth paths and one experimental BYO-endpoint path. Pick the one that matches your setup.

### Option A — ChatGPT subscription (recommended for individuals)

On the host (not inside the container), run Codex's OAuth login:

```bash
codex login
```

This writes `~/.codex/auth.json` with a subscription token. The host-side Codex provider ([src/providers/codex.ts](../../../src/providers/codex.ts)) copies `auth.json` into a per-session `~/.codex` directory mounted into the container — your host's own Codex CLI is never touched.

No `.env` variables required for this mode.

### Option B — API key (recommended for CI or API billing)

```env
OPENAI_API_KEY=sk-...
CODEX_MODEL=gpt-5.4-mini
```

The host forwards both variables into the container. If both subscription (`auth.json`) and `OPENAI_API_KEY` are present, Codex prefers the subscription.

### Option C — BYO OpenAI-compatible endpoint (experimental)

Codex's built-in `openai` provider honors the `OPENAI_BASE_URL` env var directly. Point it at any OpenAI-compatible endpoint — Groq, Together, self-hosted vLLM, an OpenAI proxy, etc.

```env
OPENAI_API_KEY=...
OPENAI_BASE_URL=https://api.groq.com/openai/v1
CODEX_MODEL=llama-3.3-70b-versatile
```

Codex also ships first-class local-runner flags — `codex --oss --local-provider ollama` or `--local-provider lmstudio` — that auto-detect a local server. To use those inside NanoClaw, set `CODEX_MODEL` to a model your local runner serves and add the corresponding base URL; see the Codex CLI docs for the full `model_provider = oss` configuration.

**Experimental caveat:** tool-calling quality depends on the model and endpoint. Not every OpenAI-compat provider implements the full function-calling spec, and smaller models (< 30B) often struggle with multi-step tool orchestration. Test before committing.

### Per group / per session

Set `"provider": "codex"` in the group's **`container.json`** (`groups/<folder>/container.json`) — the in-container runner reads `provider` from there, not from the DB. The DB columns **`agent_groups.agent_provider`** and **`sessions.agent_provider`** (session overrides group) only drive host-side provider contribution — per-session `~/.codex` mount, `OPENAI_*` / `CODEX_MODEL` env passthrough — and do not propagate into `container.json` at spawn time. Set both, or just edit `container.json`; if they disagree, the runner uses `container.json` and the host-side resolver falls back through session → group → `container.json` → `'claude'`.

`CODEX_MODEL` applies process-wide via `.env`; if you need different models for different groups, set them via `container_config.env` on the group.

Extra MCP servers still come from **`NANOCLAW_MCP_SERVERS`** / `container_config.mcpServers` on the host. The runner merges them into the same `mcpServers` object passed to all providers.

## Operational notes

- **Spawn-per-query:** Codex's app-server is spawned fresh per query invocation, matching the OpenCode pattern. No long-lived daemon to keep healthy across sessions.
- **Per-session `~/.codex` isolation:** each group gets its own copy of the host's `auth.json`. The container can rewrite `config.toml` freely on every wake without touching the host's Codex config.
- **Native compaction:** kicks in automatically at 40K cumulative input tokens between turns, via `thread/compact/start`. If compaction fails, the provider logs and continues uncompacted — no fatal error.
- **Approvals:** auto-accepted inside the container (the container is the sandbox; same posture as Claude/OpenCode).
- **Mid-turn input:** Codex turns don't accept mid-turn messages. Follow-up `push()` calls queue and drain between turns, matching the OpenCode pattern. The poll-loop only pushes between turns anyway, so no messages are dropped.
- **Stale thread recovery:** `isSessionInvalid` matches on stale-thread-ID errors (`thread not found`, `unknown thread`, etc.) so a cold-started app-server can recover cleanly when it sees a stored continuation it no longer has.

## Next Steps

The registration and Dockerfile guards in **Build and validate** confirm the wiring. For a live end-to-end check, set `agent_provider = 'codex'` on a test group and send a message after the image rebuild. A successful round-trip looks like:

- `init` event with a stable thread ID as continuation
- One or more `activity` / `progress` events during the turn
- `result` event with the model's reply

If the agent hangs or errors, check `~/.codex/auth.json` exists on the host (Option A) or that `OPENAI_API_KEY` is forwarding correctly (Option B) — `docker exec` into a running container and `env | grep -i openai` to confirm. To confirm the CLI binary itself landed in the image, `docker exec <container> codex --version`.

To back this provider out, follow [REMOVE.md](REMOVE.md).
