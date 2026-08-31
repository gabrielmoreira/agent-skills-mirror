# `ntm spawn` — Exhaustive Reference

## Contents

- [Project resolution (read this first)](#project-resolution-read-this-first)
- [Agent-count flags](#agent-count-flags) — `--cc`, `--cod`, `--grok`, `--agy`, `--gmi`, `--cursor`, `--windsurf`, `--aider`, `--oc`, `--local`/`--ollama`
- [Pane layout](#pane-layout) — `--no-user`, `--worktrees`, `--worktree-name`, `--pane-env`, `-l/--label`
- [Prompt delivery](#prompt-delivery) — `--prompt`, `--init-prompt`, `--marching-orders`
- [Recipes / workflows / templates / personas](#recipes--workflows--templates--personas)
- [Stagger (prompt delivery pacing)](#stagger-prompt-delivery-pacing)
- [Session profiles](#session-profiles)
- [CASS context injection](#cass-context-injection)
- [Auto-assign pipeline (spawn then claim work)](#auto-assign-pipeline-spawn-then-claim-work)
- [Privacy, safety, resilience](#privacy-safety-resilience)
- [Interactive wizard](#interactive-wizard)
- [Error matrix](#error-matrix)
- [Scenario catalog](#scenario-catalog) — 9 common spawn patterns

---

Spawn creates (or extends) a tmux session with typed agent panes. Flag registrations
are at `/dp/ntm/internal/cli/spawn.go:2048-2102`.

Spawn does **not** attach. On success it prints how to run `ntm attach`.

## Project resolution (read this first)

`ntm spawn <name>` resolves the project directory by:

1. Looking up `<name>` under `projects_base` (`ntm config get projects_base`, or env `NTM_PROJECTS_BASE`).
2. Falling back to a symlink in `~/ntm_Dev/` if the name doesn't match a directory.

**Session name must equal the project directory basename.** If it doesn't, agent-mail,
beads, and file reservations will register under a different project key than NTM sees.
This is the single most common cross-tool breakage; always set `NTM_PROJECTS_BASE` to the
parent of your project directory, and use the directory's basename as the session name.

If the resolved directory does not exist, spawn prompts to create it; pass `--create-dir`
to create it without a prompt (`spawn.go:2111`). Non-TTY spawns without `--create-dir`
fail fast with a structured error instead of hanging on the prompt (`spawn.go:2348`).
When `--robot-spawn` output carries `effective_project_key` (omitted when it equals
`working_dir`), NTM and Agent Mail disagree on the project key (symlink or macOS
`/private` aliasing) — feed that value, not `working_dir`, to Agent Mail queries.

## Agent-count flags

All accept `N`, `N:model`, or (for agents with an effort hint) `N:model:effort`
(`/dp/ntm/internal/cli/agent_spec.go:124-201`). `N` ≥ 1. `N:model@effort` is accepted
sugar for `N:model:effort` on the effort-capable types — claude, codex, grok
(`agent_spec.go:114-121`); for every other type `@` stays a literal model character.
A requested model or effort is valid only when the configured `[agents]` command
template references `{{.Model}}` (or `{{.ModelAlias}}`) and `{{.ReasoningEffort}}`,
respectively; NTM fails this preflight before any mutation (worktrees, session, panes)
rather than silently dropping an unsupported override (`validateSpawnAgentCommands`, `spawn.go:820`).
Since v1.29, an explicit model that misses the registry gets an advisory
did-you-mean (`model "claude-opus5" is not in the model registry; did you mean
"claude-opus-5"?`) — a warning only; the spawn proceeds with the requested model,
so custom/unregistered models are never blocked.

Model allowed charset: `^[A-Za-z0-9._/@:+-]+$` (`agent_spec.go:16`). Multiple flags of
the same type accumulate — `--cc=2:opus --cc=1:sonnet` yields 2 Opus + 1 Sonnet panes.

| Flag | Agent | Source |
|------|-------|--------|
| `--cc N[:model[:effort]]` | Claude | `spawn.go:2048` |
| `--cod N[:model[:effort]]` | Codex | `spawn.go:2049` |
| `--grok N[:model[:effort]]` | Grok Build (**phase 2 as of v1.28**, GH#251 — full swarm citizenship: `--prompt`/`--init-prompt`, CASS injection, marching orders, `--assign`, `--auto-restart`, `ntm respawn`, send/interrupt/restart/health all flow through the grok-aware composer-verified protocol; launches `grok --always-approve`. The one remaining refusal is **persona injection**: the grok CLI has no system-prompt mechanism) | `spawn.go:2052` |
| `--agy N` | Gemini via the **Antigravity CLI** (`agy`). Model is hard-pinned by NTM (`Gemini 3.7 Flash (High)` since v1.29.0; earlier releases pinned `Gemini 3.1 Pro (High)`); any `:model` you pass is ignored with a warning. **Preferred Gemini provider.** | `spawn.go:2051` |
| `--gmi N[:model]` | Gemini via the legacy **Gemini CLI** (`gmi`), **retired 2026-06-18** (flag still accepted for legacy setups). Use `--agy` for Gemini. | `spawn.go:2050` |
| `--cursor N[:model]` | Cursor | `spawn.go:2059` |
| `--windsurf N[:model]` | Windsurf | `spawn.go:2060` |
| `--aider N[:model]` | Aider | `spawn.go:2061` |
| `--oc N[:model]` | Opencode (`opencode` binary unless `[agents] oc` overrides) | `spawn.go:2062` |
| `--local N` | Ollama-backed | `spawn.go:2053` |
| `--ollama N` | alias of `--local` (sums) | `spawn.go:2054` |
| (plugin flags) | per-plugin | Dynamically registered, `spawn.go:2133-2160` |

Ollama specifics:

- `--local-model <name>` default `codellama:latest` (`spawn.go:2055`).
- `--local-host <url>` overrides `OLLAMA_HOST` / `NTM_OLLAMA_HOST` (`spawn.go:2056`).
- `--local-fallback` converts local agents to cloud if preflight fails (`spawn.go:2057`).
- `--local-fallback-provider` `cc|cod|gmi|agy`, default `cod` (`spawn.go:2058`).

## Pane layout

| Flag | Effect | Source |
|------|--------|--------|
| `--no-user` | Omit user pane — total panes = agents (vs agents+1) | `spawn.go:2064` |
| `--worktrees` | Each agent gets an isolated worktree on branch `ntm/<session>/<agent>` | `spawn.go:2110` |
| `--worktree-name <name>` | Override the auto-derived worktree dir name (single-agent spawns only; keeps `cc_1`/`cod_1` paths from colliding when orchestrators spawn the same slot across `--label` variants) | `spawn.go:2113` |
| `--pane-env KEY=TEMPLATE` | Repeatable NTM-owned per-pane env; templates expand `{project}`, `{pane}`, `{role}`; persisted in the manifest and re-exposed by `--robot-env` as `pane_environment[]` | `spawn.go:2114` |
| `-l/--label <label>` | Session becomes `project--label` (parallel workspace) | `spawn.go:2070` |

### Label rules (`/dp/ntm/internal/config/label.go:64-78`)

- Non-empty, ≤ 50 chars.
- Must not contain `--` (reserved separator).
- Must match `^[a-zA-Z0-9][a-zA-Z0-9_-]*$`.
- Project name cannot contain `--` (errored by `ValidateProjectName`, `spawn.go:954-956`).
- `SessionBase(name)` strips the `--<label>` suffix for cross-session broadcasts.

## Prompt delivery

| Flag | Purpose | Source |
|------|---------|--------|
| `--prompt <string>` | Injected into each agent at launch | `spawn.go:2089` |
| `--init-prompt <string>` | Sent *after* agents become ready (paired with `--assign`) | `spawn.go:2090` |
| `--with-agent-name` | Prepend a `You are agent <name>` preamble to `--init-prompt` per pane (deterministic identity) | `spawn.go:2091` |
| `--marching-orders <file>` | Per-pane prompts using `pane:N <prompt>` syntax | `spawn.go:2121` |

`--marching-orders` file format: each line is either `pane:N <prompt>` or a global line
(applied to all unspecified panes). User pane is always excluded.

Since v1.29.1 (GH#255) spawn publishes every pane's Agent Mail identity
durably BEFORE launching the agent CLIs (one identity coordinator per spawn,
fail-open when mail is down) — so a pane's mail identity is queryable the
moment the agent boots; there is no registration race to wait out.

## Recipes / workflows / templates / personas

These are three overlapping asset families. Know the difference.

### `-r/--recipe <name>` (`spawn.go:2065`)

An **agent-count template**. Loads from `recipe.NewLoader()` (`spawn.go:1841`). Built-ins
(`spawn.go:1681`): `quick-claude`, `full-stack`, `minimal`, `codex-heavy`, `balanced`,
`review-team`. User recipes live in `~/.config/ntm/recipes.toml`; project overrides in
`.ntm/recipes.toml` (`recipe.go:166-187`). Enumerate with `ntm recipes list`.

### `-t/--template <name>` (`spawn.go:2066`)

There is no `--workflow` flag on spawn — the flag is `-t/--template`.

A **workflow template** adding coordination metadata on top of a recipe. Loaded via
`workflow.NewLoader()` (`spawn.go:1763`). Built-ins: `red-green`, `review-pipeline`,
`specialist-team`, `parallel-explore` (`spawn.go:1581`).

**Mutually exclusive** with `--recipe` (`spawn.go:1761`).

**Workflow ≠ pipeline YAML.** `ntm pipeline run` workflows are a separate concept
(see `PIPELINES.md`). Enumerate spawn workflows with `ntm workflows list`.

### `--persona name[:count]` (`spawn.go:2063`)

Repeatable. Personas are **prompt specializations** attached to an agent pane. Schema
at `/dp/ntm/internal/cli/persona_spec.go:53-76`. Registry: built-ins + user
(`~/.config/ntm/personas.toml`) + project (`.ntm/personas.toml`).

Combines with `--cc=N` — persona agents are ADDITIONAL to count agents.

```bash
# 3 Claude + 1 architect-persona agent + 2 implementer-persona agents
ntm spawn myproject --cc=3 --persona=architect --persona=implementer:2
```

## Stagger (prompt delivery pacing)

Three overlapping flag families for backward-compat. For new code, prefer
`--stagger-mode=smart`.

| Flag | Values | Source |
|------|--------|--------|
| `--stagger[=<dur>]` | optional duration; bare enables the 90s default (`fixed`) | `spawn.go:2076` |
| `--stagger-mode <mode>` | `smart`, `fixed`, `none` (default `none`) | `spawn.go:2080` |
| `--stagger-delay <dur>` | fixed delay (used with `--stagger-mode=fixed`), default `30s` | `spawn.go:2081` |

- `smart` — adapts delay based on rate-limit tracker observations.
- `fixed` — uniform `--stagger-delay` between sends.
- `none` — all prompts fire immediately.

**Panes are always created at once for dashboard visibility; only prompt delivery is staggered.**

## Session profiles

Saved spawn configurations you can reapply.

| Flag | Purpose | Source |
|------|---------|--------|
| `--profile <name>` | Load saved spawn options | `spawn.go:2131` |
| `--profiles foo,bar` | CSV of persona names mapped to agents in order | `spawn.go:2124` |
| `--profile-set <name>` | Named persona set (e.g. `backend-team`) | `spawn.go:2125` |

Explicit flags override loaded profile values. Save with `ntm profile save`.

`--profiles` and `--profile-set` are mutually exclusive (`spawn.go:1812`).

## CASS context injection

Injects past-session context (summaries, prior decisions) into fresh panes via CASS.

| Flag | Default | Source |
|------|---------|--------|
| `--cass-context <query>` | `""` (uses auto-generated) | `spawn.go:2084` |
| `--no-cass-context` | false | `spawn.go:2085` |
| `--no-recovery` | false (session-recovery prompt injection) | `spawn.go:2086` |
| `--cass-context-limit N` | 0 (config default) | `spawn.go:2087` |
| `--cass-context-days N` | 0 (config default) | `spawn.go:2088` |

`--no-cass-context` and `--no-recovery` are independent toggles — recovery injection
runs separately from CASS context injection.

## Auto-assign pipeline (spawn then claim work)

With `--assign`, spawn waits until agents become ready then runs `ntm assign` against
them automatically.

| Flag | Default | Source |
|------|---------|--------|
| `--assign` | false | `spawn.go:2096` |
| `--strategy <name>` | (inherits assign default `balanced`) | `spawn.go:2097` |
| `--limit N` | 0 (unlimited) | `spawn.go:2098` |
| `--ready-timeout <dur>` | `60s` | `spawn.go:2099` |
| `--assign-verbose` / `--assign-quiet` | false | `spawn.go:2100-2101` |
| `--assign-timeout <dur>` | `30s` | `spawn.go:2102` |
| `--assign-agent <type>` | `""` (`claude`, `codex`, `gemini`, `antigravity`) | `spawn.go:2103` |
| `--assign-cc-only` / `--assign-cod-only` / `--assign-gmi-only` / `--assign-agy-only` | false | `spawn.go:2104-2107` |

See `ntm assign` for strategy details (`balanced`, `speed`, `quality`, `dependency`, `round-robin`).

## Privacy, safety, resilience

| Flag | Effect | Source |
|------|--------|--------|
| `--safety` | Errors if session exists (prevents accidental reuse) | `spawn.go:2093` |
| `--privacy` | Disables session data persistence | `spawn.go:2117` |
| `--allow-persist` | Override `--privacy` | `spawn.go:2118` |
| `--auto-restart` | Monitor + restart crashed agents per `[resilience]` config | `spawn.go:2067` |
| `--verify-boot` | Block up to 30s until every agent reaches a working prompt; exit non-zero naming the panes that failed to boot (session and panes still exist — inspect with `--robot-tail`) | `spawn.go:2112` |

Without `--safety`, spawn is additive: existing sessions are reused and new panes appended.

Per-pane Claude credential isolation is opt-in via `[agents] claude_isolate_credentials`
plus `claude_token_file` (`config.go:853-859`); the token is passed by reference, never
typed into the pane.

## Interactive wizard

`-i/--interactive` triggers the wizard **only** if no specs given (`spawn.go:1686`):
`len(agentSpecs)==0 && recipe=="" && template=="" && len(personaSpecs)==0`.

Wizard populates specs and returns; not used from scripts.

## Error matrix

| Condition | Message |
|-----------|---------|
| No agents | `no agents specified (use --cc, --cod, --gmi, --agy, --grok, ...)` (`spawn.go:2145`) |
| `--safety` + existing session | `session '%s' already exists (--safety mode prevents reuse; use 'ntm kill %s' first)` |
| Invalid label | via `config.ValidateLabel` |
| Project name has `--` | `project name %q contains '--'` (`label.go:85`) |
| `--recipe` + `--template` | `cannot use both --recipe and --template; pick one` (`spawn.go:1761`) |
| Model/effort spec vs `[agents]` template | preflight fails before any mutation when the template lacks `{{.Model}}`/`{{.ReasoningEffort}}` (`validateSpawnAgentCommands`, `spawn.go:820`) |
| Missing project dir, non-TTY | `project directory %s does not exist; pass --create-dir to create it, ...` (`spawn.go:2348`) |
| `--worktree-name` with >1 agent | `--worktree-name is only valid for single-agent spawns; got %d agents` (`spawn.go:1394`) |
| `--grok` + `--persona` | `Grok Build spawn does not support persona prompt injection: the Grok Build CLI has no system-prompt flag or env var` (the last remaining grok refusal after the v1.28 phase-2 flip; `--prompt`/`--init-prompt` etc. now work) |

## Scenario catalog

### 1. Balanced swarm

```bash
ntm spawn myproject --cc=3 --cod=2 --agy=1 --stagger-mode=smart
```

### 2. Labeled variant alongside an existing session

```bash
ntm spawn myproject --label=frontend --cc=2 --worktrees
# Session: myproject--frontend
# Worktree branches: ntm/myproject--frontend/cc_1, cc_2
```

### 3. Recipe-driven spawn

```bash
ntm spawn myproject -r full-stack
```

### 4. Workflow + personas

```bash
ntm spawn myproject -t red-green \
  --persona=test-writer --persona=implementer:2
```

### 5. Pinned model variants

```bash
ntm spawn myproject --cc=2:opus --cc=1:sonnet --cod=1:gpt-5
```

### 6. No-user swarm (headless, for CI)

```bash
ntm spawn ci-worker --no-user --cc=4 --auto-restart
```

### 7. Spawn then auto-claim bv-prioritized work

```bash
ntm spawn myproject --cc=3 --cod=2 \
  --assign --strategy=dependency --limit=5
```

### 8. Ollama-only local swarm with cloud fallback

```bash
ntm spawn myproject --local=4 \
  --local-model='llama4:70b' \
  --local-fallback --local-fallback-provider=cod
```

### 9. Marching orders file

```bash
cat > /tmp/orders.txt <<'EOF'
pane:2 You own internal/auth; pick the next ready bead there.
pane:3 You own internal/storage; pick the next ready bead there.
You are part of a swarm; reserve your edit surface before editing.
EOF

ntm spawn myproject --cc=2 --cod=2 --marching-orders=/tmp/orders.txt
```
