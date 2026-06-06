# Depth-Priority Hierarchical-Instruct System V1

**Scope**: Authoritative meta-documentation for the Hierarchical-Instruct hierarchical governance system
**Last Updated**: 2026-06-05

> This file documents the **system itself** — how the depth-priority hierarchical paradigm works, how routing and governance are enforced, and the contract that all agents must follow.
> Project-specific content lives in [`.hi/.hi-instruct.md`](.hi-instruct.md) after adoption.
> Module-level rules live in `[module]/.hi/instruct.md` and are **more authoritative** than this file when working inside those directories.

---

## ⛔ STOP — MANDATORY READING CONTRACT (non-negotiable)

**This file is THE single master reference for the `.hi/` governance subsystem.** Every AI agent, assistant, and automated tool — regardless of vendor (GitHub Copilot, Claude Code, Cursor, Continue, Cline, Codex, Aider, or any other) — **MUST read and obey this contract BEFORE making changes that touch governed scope** (see *Scope & Coexistence* below). All other entry files (`.github/copilot-instructions.md`, `AGENTS.md`, `CLAUDE.md`, `.cursor/rules/`, `.continue/rules/`, `.clinerules/`) are **thin pointers to this file** — the governance rules live here, not in them.

**You MUST:**

1. **Obey the deepest `.hi/instruct.md`.** When working in any directory, find the deepest `.hi/instruct.md` on the path from the repo root to your working directory and follow it precisely. **Deeper always wins.** Shallower files (including this one) are background context only when a deeper file governs your scope.
2. **Read the mandatory order below before your first governed action in a session.**
3. **Route governed work through the gateway.** Imports/merges/adopts/migrations and scope-sensitive workflows go through [`/hip-route`](prompts/tier-1/hip-route.prompt.md) and the [Governed Workflows guard](#governed-workflows--importmerge-pattern-guard) — **never** ad-hoc `git clone`, `cp`, or `Move-Item`.
4. **Never bypass the standing safety contracts:** archive-first / never-delete, never-reset-db, credential isolation, host-vs-container isolation. See the cross-cutting map below.

### Scope, Authority & Coexistence (read this carefully)

This subsystem is a **governing authority for codebase coherence** — not a replacement for your tools or a cage around the codebase. It **self-governs**: it owns its own rules and its own maintenance lifecycle (edited only through `/hip-*` workflows and the `hia-*` agents, never ad-hoc).

> **Whose rules are these? Yours.** The content of every `.hi/instruct.md` is **your project's own instructions** — written by and for the adopting team. The `.hi/` subsystem does **not** impose a separate rule set on top of your project; it is the **custodian** that *maintains, scopes, resolves, and enforces the coherence of your instructions*. The authority is always your project's intent. The machinery exists only to keep that intent truthful, well-scoped, discoverable, and applied at the right depth. When an agent obeys "the deepest `.hi/instruct.md`," it is obeying **your** rules for that location — the subsystem just guarantees it reads the *right* ones.

- **It governs, it does not preclude.** Standard tooling — GitHub Copilot's native behavior, Cline, Cursor, Continue, plain `git`, your editor — keeps working exactly as usual. The `.hi/` system layers coherence and context-scoping *on top of* whatever workflow you already use; it never forbids using those tools normally.
- **What is "governed scope"** (where this contract is mandatory): the instruction system itself (`.hi/`, the pointer entry files, deployment/module `.hi/instruct.md`), plus the standing safety contracts (archive-first, never-reset-db, credentials, host isolation) which apply **everywhere**.
- **What is *not* governed:** ordinary application/source code in an adopting project. There you are **encouraged** to read, reference, navigate, and investigate freely. The instruction files exist to *scope the right context to the right place* — use them to orient quickly, then work normally. Quick read-only exploration of any part of the working codebase (the real project, **not** this template's scaffolding) never requires routing or ceremony.
- **Coherence over control.** When in doubt, the goal is a coherent codebase and accurate, well-scoped instruction files — not maximal restriction. Prefer the lightest action that keeps the instruction layer truthful.

### Mandatory reading order (once per session)

1. [`.hi/dev-specs.md`](dev-specs.md) — **CRITICAL FIRST**: project mode (Template vs Production), OS, shell, language/framework versions.
2. **This file** (`.hi/instruct.md`) — how the hierarchy, routing, and governance work.
3. [`.hi/index.md`](index.md) — master index of every instruction section; jump from here to any topic.
4. [`.hi/.hi-instruct.md`](.hi-instruct.md) — project-specific rules and conventions after adoption.
5. **The deepest `[module]/.hi/instruct.md`** on your current path — **authoritative**; overrides everything above for that scope.

### Cross-cutting canonical map (single source of truth)

| Topic | Canonical file |
|-------|----------------|
| How the hierarchy/routing works | [`.hi/instruct.md`](instruct.md) (this file) |
| Project conventions & tooling | [`.hi/.hi-instruct.md`](.hi-instruct.md) |
| Naming & file organization | [`.hi/conventions.md`](conventions.md) |
| Archive / never-delete / never-reset-db | [`.hi/maintenance.md`](maintenance.md) |
| Credentials, `.env`, `.gitignore` | [`.hi/credentials.md`](credentials.md) |
| Host vs. container isolation | [`.hi/environment.md`](environment.md) |
| Master topic index | [`.hi/index.md`](index.md) |

**If anything below conflicts with a deeper `.hi/instruct.md`, the deeper file wins.** This contract is the only place the reading order, scope/coexistence rule, and cross-cutting map are defined — do not duplicate them into pointer files.

---

## Contents

| Section | What's here |
|---------|-------------|
| [⛔ Mandatory Reading Contract](#-stop--mandatory-reading-contract-non-negotiable) | **Read first**: the single forcing contract, scope & coexistence, reading order, cross-cutting map |
| [The Routing Gateway](#the-routing-gateway--core-orchestration-layer) | **Core feature**: How `/hip-route` powers all major workflows |
| [The Depth-Priority Hierarchical Paradigm](#the-depth-priority-hierarchical-paradigm) | How layering works; deeper always wins |
| [Global Shared Instructions](#global-shared-instructions-hi) | Cross-cutting canonical files in `.hi/` |
| [Agentic Runtime](#agentic-runtime-hi) | Governed tools, foresight, self-improvement, heartbeat |
| [AI Prompt Files](#ai-prompt-files-githubprompts) | Slash commands and their modes |
| [Workflow Invocation Pattern](#workflow-invocation-pattern) | Workflows are repeatable; why they matter |
| [Governed Workflows — Import/Merge Pattern Guard](#governed-workflows--importmerge-pattern-guard) | **CRITICAL**: Imports are orchestrated, never ad-hoc copies |
| [Custom Agents](#custom-agents-githubagents) | Specialized personas with restricted tools |
| [Skills](#skills-githubskills) | Domain knowledge packs |
| [Git Hooks](#git-hooks-githubhooks) | Commit-time safety checks |
| [YAML Frontmatter Schema](#yaml-frontmatter-schema) | Required fields for prompts, agents, skills |
| [Development Documentation Convention](#dev-docs--development-documentation-convention) | `.dev-docs/` archival and indexing rules |
| [Code Comment Convention](#code-comment-convention) | Why, not what; no docblocks unless asked |
| [Hierarchical-Instruct Maintenance Rule](#hierarchical-instruct-maintenance-rule) | Update instructions with every architectural change |
| [Automatic Date Maintenance](#automatic-date-maintenance) | Auto-fill Last Updated and placeholders |

---

## The Routing Gateway — Core Orchestration Layer

**This is the magic.** The `/hip-route` gateway is the central nervous system that powers every major workflow in this project. It is **not optional** — it is the defining feature that makes depth-priority hierarchy practical at scale.

### What Routing Does

Before any workflow (import, validation, module creation, etc.) executes, the router:

1. **Resolves scope** — finds the deepest `.hi/instruct.md` that governs the affected paths
2. **Checks governance** — applies any external rules or constraints
3. **Routes to authority** — delegates to the domain manager/supervisor that owns that scope
4. **Enables escalation** — halts on conflicts and explains why

### Why This Matters

Without routing, each workflow would need to implement scope resolution independently → **duplicate logic, brittleness, easy to bypass.**

With routing, all workflows speak the same language → **consistent, auditable, scope-aware.**

### Routed Workflows (Today)

| Workflow | Routed to |
|----------|-----------|
| `/hip-import-execute` | `hia-imports` (Phase 0-7 orchestration) |
| `/hip-adapt-infrastructure` | `hia-infrastructure` (infrastructure compliance & adaptation) |
| `/hip-validate` | `hia-validator` (scope-aware validation) |
| `/hip-reflect` | `hia-learner` (gap analysis) |
| `/hip-update-index` | `hia-curator` (index rebuild) |
| `/hip-new-module` | `hia-scaffolder` (module scaffolding) |

Each workflow does **not** know how to resolve scope or apply governance—it delegates that to the router and lets the router decide who should execute.

### The Router Itself

→ **[/hip-route prompt](prompts/tier-1/hip-route.prompt.md)** — invoke when you need scope resolution before delegating
→ **[hia-router agent](agents/tier-1/hia-router.agent.md)** — technical details and governance resolution logic

---

## The Depth-Priority Hierarchical Paradigm

This system uses **Hierarchical Layering by Directory Depth**. The deeper your current working directory, the more authoritative its `.hi/instruct.md` becomes.

> **Prior art — this is a familiar pattern, not a novel one.** "Deepest wins" is the same nearest-ancestor-overrides model the rest of your toolchain already uses: ESLint/Prettier/`tsconfig.json` resolve the *nearest* config walking up the tree, language servers pick the closest project root, `.gitattributes`/`.editorconfig` let deeper files override shallower ones, and Kubernetes/Kustomize overlays apply leaf-wins. The contribution here is applying that well-understood resolution model to **AI instruction files** and making it machine-checkable (see [Programmatic enforcement](#programmatic-enforcement-the-contract-is-not-purely-advisory)).

### Precedence Rules

When working in a directory:
- **That directory's `.hi/instruct.md` is authoritative** for your current context
- Shallower `.hi/instruct.md` files provide **background/context only**
- Each level is **self-contained** — no delegation upward
- **Deeper always wins** over shallower

### Resolution Order

```
.hi/instruct.md                          ← SYSTEM: explains HOW layering works (this file)
    ↓
.hi/.hi-instruct.md                      ← AUTHORITATIVE at workspace root (project content)
    ↓
[module]/.hi/instruct.md                 ← AUTHORITATIVE when working in that module
    ↓
[module]/[submodule]/.hi/instruct.md     ← AUTHORITATIVE when working in that submodule
```

### How to Use

1. **When you start working**: check what directory you're in
2. **Find the deepest `.hi/instruct.md`** in or above your current directory
3. **That file is authoritative** — follow it precisely
4. **Parent files** provide architectural context only
5. **Do not mix contexts** across modules

---

## Global Shared Instructions (`.hi/`)

Cross-cutting rules that would otherwise be duplicated across many files live here as single sources of truth.

```
.hi/
├── instruct.md              ← SYSTEM: this file (how the hierarchy works)
├── .hi-instruct.md          ← PROJECT CONTENT: template for project-specific rules after adoption
├── conventions.md           ← Naming, file organization, TOC rules (canonical)
├── maintenance.md           ← Archive patterns, never-delete, never-reset-db rules (canonical)
├── credentials.md           ← Credential warehousing + .gitignore rules (canonical)
├── environment.md           ← Host-vs-container isolation rules; never silently mutate the host (canonical)
├── index.md                 ← MASTER INDEX of all instruction sections across the project
├── agent-config.yaml        ← Agentic runtime config: heartbeat, log format, safety, foresight, self-improvement
├── heartbeat.md             ← Heartbeat procedure: what agents do every N steps to re-align
├── engine/                  ← Runtime scripts (foresight_engine.py, get_effective_instructions.py)
├── agents/tools/            ← Governed tool checklists read by agents (not MCP wire-protocol tools)
├── mcp/tools/               ← Project-specific governed tool checklists
├── foresight/               ← Foresight analysis outputs (runtime; gitignored)
├── knowledge/               ← Accumulated knowledge base (runtime; gitignored)
└── logs/                    ← Agent audit logs (runtime; gitignored)
```

**Rule**: If a directory's `.hi/instruct.md` needs to reference a global convention, it **links** to `.hi/` rather than restating it. Never copy content from these files.

---

## Tier 1 vs Tier 2: User-Facing vs Internal Subsystem

The `.hi/` system is divided into two operational tiers:

### Tier 1: User-Facing Entry Points

**What**: Prompts and agents you invoke directly as a user
**Where**: `.hi/prompts/tier-1/` and `.hi/agents/agents/tier-1/`
**Naming**: `/hip-*` prefix (e.g., `/hip-onboard`, `/hip-import-execute`)
**Examples**:
- **Prompts**: `/hip-onboard`, `/hip-new-module`, `/hip-validate`, `/hip-reflect`, `/hip-import-execute`
- **Agents**: `hia-router` (Routing Gateway), `hia-curator` (index management), `hia-imports` (import orchestration)

**Use**: Type Tier 1 prompts in Copilot Chat whenever you need to execute a workflow. These are the **main entry points** for all user-initiated tasks.

### Tier 2: Internal `.hi/` Subsystem

**What**: Prompts and agents used by the orchestration layer, workflows, and other agents
**Where**: `.hi/prompts/tier-2/` and `.hi/agents/agents/tier-2/`
**Naming**: Internal utility (not typically invoked by users)
**Examples**:
- **Prompts**: `/hip-adapt-infrastructure`, `/hip-dispatch-test`, `/hip-phase-2-fixer`
- **Agents**: Workers (scaffolder, generator, validator), Observers (explorer, compliance, learner), Specialists (naming, ports, environment, deployment)

**Use**: These are called **automatically** by Tier 1 prompts and the routing gateway. You do not invoke them directly unless troubleshooting or debugging.

### The Contract

- **Tier 1 is stable**: User-facing API that changes rarely
- **Tier 2 is flexible**: Internal workers can be swapped, modified, or reorganized without affecting user experience
- **Depth-priority rules apply at all tiers**: Deeper instructions override shallower ones, regardless of tier

---

## Agentic Runtime (`.hi/`)

The `.hi/` directory doubles as the agentic runtime platform, layering proactive capabilities on top of the depth-priority instruction system.

**Key capabilities:**

| Capability | Mechanism |
|---|---|
| **Heartbeat** | Every 6 steps, agents re-read the active instruction scope and re-align |
| **Foresight** | Before acting, `foresight_engine.py` anticipates gaps (error handling, logging, tests) and forecasts risks |
| **Self-improvement** | After major tasks, agents reflect and propose edits to `.hi/instruct.md` files |
| **Governed tools** | Governed tool JSON files in `.hi/agents/tools/` include a `checklist` and `safety_level` — agents must follow the checklist before acting |
| **Audit logging** | All agent changes are logged to `.hi/logs/` for traceability |

**Rules:**
- `agent-config.yaml` is the single source of truth for runtime behavior — do not duplicate its settings elsewhere
- `.hi/foresight/`, `.hi/knowledge/`, and `.hi/logs/` are runtime outputs — gitignored; never commit them
- Governed tool checklists live in `.hi/agents/tools/` (built-in) or `.hi/mcp/tools/` (project-specific) — these are **governance documents read by agents**, not MCP wire-protocol tool definitions
- `heartbeat.md` defines the procedure agents follow at every heartbeat interval — configurable in `agent-config.yaml`
- `get_effective_instructions.py` is the **canonical depth-priority resolver** — it merges `.hi/instruct.md` shallowest→deepest (deepest wins) and is **bounded to the project root by default** (nearest `.git` ancestor) so instruction files *above* the project never bleed in. The MCP `resolve_instructions` tool (below) mirrors this exact contract. The traversal contract (shallow→deep, deepest wins, project-bounded) is fixed — do not change its meaning.
- Heartbeat and foresight are configured via `agent-config.yaml`; adjust `heartbeat_interval` and `foresight:` keys to tune

### Programmatic enforcement (the contract is not purely advisory)

The depth-priority rule is **machine-checkable**, not just documented prose:

| Mechanism | What it enforces | Where |
|---|---|---|
| **Canonical resolver** | Computes the authoritative deepest `.hi/instruct.md` for any path, project-bounded | [`.hi/engine/get_effective_instructions.py`](engine/get_effective_instructions.py) (CLI: `--path`, `--workspace`) |
| **Resolution explainer** | Audits *why* a path resolves as it does: governing layers + the topic **override map** (which deeper layer shadows which) — for code review | same resolver, `--explain` / `--explain --json`; surfaced via [`/hip-route`](prompts/tier-1/hip-route.prompt.md) explain mode |
| **MCP server** | Exposes `resolve_instructions(path)` to any MCP-aware client (Copilot, Cursor, Continue, Cline, Claude Code) — same bounded contract as the resolver | [`.hi/mcp/python/hia_mcp/server.py`](mcp/python/hia_mcp/server.py) |
| **Conformance gate** | Asserts the live repo satisfies depth-priority (deepest wins, no ancestor bleed) for every governed scope; runs in CI | [`.hi/engine/check_resolution_conformance.py`](engine/check_resolution_conformance.py) |
| **Drift validator** | Structure, naming, links, index freshness | [`.hi/scripts/validate-instructions.ps1`](scripts/validate-instructions.ps1) |
| **Git hooks** | Credential block, archive-first/never-delete, adopter-config guard | [`.hi/hooks/`](hooks/) |

Agents that consult `resolve_instructions` (MCP) and the conformance gate (CI) get the **same** answer the resolver computes — so "the deepest file wins" is an invariant the toolchain verifies, not a convention agents are merely trusted to honor. When a deeper file *overrides* a shallower one, the **resolution explainer** names exactly which topic is shadowed and where, so the decision is auditable in review rather than implicit.

---

## AI Prompt Files (`.hi/prompts/`)

AI-invocable slash commands live as `.prompt.md` files in `.hi/prompts/`.

### Tier 1: User-Facing Prompts

Invoked directly by users. These are the primary entry points for workflows.

```
.hi/prompts/tier-1/
├── hip-onboard.prompt.md             ← /hip-onboard: Initialize/update project metadata
├── hip-import-execute.prompt.md      ← /hip-import-execute: Orchestrated import workflow
├── hip-new-module.prompt.md          ← /hip-new-module: Scaffold new module
├── hip-archive.prompt.md             ← /hip-archive: Archive files (never delete)
├── hip-update-index.prompt.md        ← /hip-update-index: Rebuild .hi/index.md
├── hip-validate.prompt.md            ← /hip-validate: Audit instruction drift
├── hip-env-check.prompt.md           ← /hip-env-check: Audit host-vs-container isolation
├── hip-foresight.prompt.md           ← /hip-foresight: Gap/risk analysis before acting
├── hip-reflect.prompt.md             ← /hip-reflect: Post-task reflection & improvement proposals
├── hip-git.prompt.md                 ← /hip-git: Version control queries
├── hip-deploy-mode.prompt.md         ← /hip-deploy-mode: Inspect/switch deployment mode
├── hip-observe.prompt.md             ← /hip-observe: Display runtime metrics
└── hip-route.prompt.md               ← /hip-route: Scope resolution & routing gateway
```

### Tier 2: Internal `.hi/` Subsystem Prompts

Invoked by agents, workflows, or the orchestration layer. Not typically called directly by users.

```
.hi/prompts/tier-2/
├── hip-adapt-infrastructure.prompt.md  ← Infrastructure adaptation (invoked by import workflow)
├── hip-audit-registries.prompt.md      ← Internal registry audit
├── hip-dispatch-test.prompt.md         ← Test dispatch (internal orchestration)
├── hip-hide-example-code.prompt.md     ← Code example masking (internal utility)
├── hip-phase-2-fixer.prompt.md         ← Phase 2 infrastructure fixer
├── hip-phase-2-post-learner.prompt.md  ← Post-phase learning (internal reflection)
├── hip-suggest-tiers.prompt.md         ← Tier suggestion helper (internal)
└── hip-test-verification.prompt.md     ← Test verification (internal)
```

**User Tip**: Most users will only invoke Tier 1 prompts. Tier 2 prompts are called automatically by the orchestration layer when needed.

### Prompt YAML Frontmatter

```yaml
---
mode: agent          # required. One of: ask | edit | agent
description: ...     # required. One-line user-facing summary
---
```

**Create when**: a multi-step workflow is executed more than twice in a session, or a workflow is complex enough that the AI needs explicit sequencing to do it correctly.

---

## Workflow Invocation Pattern

**Tier 1 Workflows** are repeatable, on-demand operations you invoke directly. Use them whenever the operation is needed, not just during initial setup.

### Tier 1: User-Facing Workflows

| Workflow | Purpose | Repeatable? |
|----------|---------|------------|
| `/hip-onboard` | Initialize or update project metadata (identity, dev-specs, module list) | Yes — re-run to refresh identity or add modules |
| `/hip-import-execute` | Import/merge external projects with full Phase 0-6 orchestration | Yes — use each time you merge a new project |
| `/hip-new-module` | Scaffold a new module (instruct.md, dev-docs, registration) | Yes — invoke per module |
| `/hip-update-index` | Rebuild `.hi/index.md` from current state | Yes — run after editing any `.hi/instruct.md` |
| `/hip-archive` | Archive (never delete) a file or directory | Yes — use per archival task |

### Tier 1: User-Facing Utilities

Informational prompts for inspecting or analyzing; they do not modify the project:

| Utility | Purpose |
|---------|---------|
| `/hip-validate` | Audit instruction drift; report findings |
| `/hip-env-check` | Audit host-vs-container isolation |
| `/hip-foresight` | Analyze gaps/risks before acting |
| `/hip-reflect` | Post-task reflection; propose improvements |
| `/hip-observe` | Display runtime observability and metrics |
| `/hip-git` | Query version control state (no auto-commits) |
| `/hip-route` | Routing Gateway: resolve scope and route tasks to authority |
| `/hip-deploy-mode` | Inspect or switch deployment mode |

### Key Principle

**Do not treat workflows as one-time setup.** They are on-demand operations:

- **First time:** `/hip-onboard` fills template placeholders → project becomes usable
- **Later:** `/hip-onboard` again to update project name, add/remove modules, refresh dev-specs
- **Each import:** `/hip-import-execute` with a new source project → orchestrated Phase 0-6 pipeline
- **Each module:** `/hip-new-module` to scaffold a new capability

---

## Governed Workflows — Import/Merge Pattern Guard

**CRITICAL SAFETY RULE:** Importing, cloning, or merging external projects is a **governed workflow**, not a vanilla file-copy operation. This section explains why and enforces the guardrail.

### Pattern Recognition

If the user **mentions any of these**, you **MUST** recognize it as an import workflow trigger:

- "clone" + project/repo reference
- "import" + external project name or path
- "merge" + another project / workspace
- "adopt" + external codebase
- "migrate" + project / code
- "consolidate" + multiple projects
- "integrate" + external repo

### The Non-Negotiable Rule

**DO NOT:**
- Run ad-hoc `git clone` or `Move-Item` / `cp -r` commands
- Manually copy directories from one project to another without orchestration
- Decide module structure, naming, or registration on the fly
- Bypass Phase 0 validation (LLM dispatch, environment, credentials, naming conventions)

**DO:**
1. **Stop** and acknowledge the import request
2. **Read** `.hi/instruct.md` to understand the authoritative import strategy for this project
3. **Invoke `/hip-import-execute`** (or the project's equivalent import orchestration prompt)
4. **Let the agent orchestration layer** (hia-migrator → hia-importer) handle:
   - Phase 0: Operational validation (LLM dispatch, env, credentials, naming)
   - Phase 1-6: Artifact preservation, analysis, integration, modernization, and registry updates
5. **Wait for completion** before suggesting next steps

### Why This Matters

- **Naming conflicts** — Projects have different conventions; ad-hoc copies violate the registry
- **Module authority drift** — Each module's `.hi/instruct.md` is authoritative; manual moves break the hierarchy
- **Credential leakage** — Phase 0 validation catches `.env` files; ad-hoc copies miss them
- **Registry corruption** — Module lists, naming conventions, error codes, API endpoints all need updates; manual copies bypass the updater
- **Audit trail loss** — Proper import logs every decision; ad-hoc commands leave no trace

---

## Custom Agents (`.hi/agents/agents/`)

Custom Copilot agent modes live in `.hi/agents/agents/`. Each `.agent.md` defines a specialized persona with restricted tools and behavior.

### Tier 1: User-Facing Orchestration Agents

These are the primary entry-point agents users interact with or that orchestrate major workflows.

```
.hi/agents/agents/tier-1/
├── hia-router.agent.md              ← Routing Gateway: scope resolution
├── hia-curator.agent.md             ← Registry & index management
├── hia-imports.agent.md             ← Import/merge orchestration
├── hia-infrastructure.agent.md      ← Infrastructure adaptation
└── hia-super.agent.md               ← Super-user for complex multi-phase work
```

### Tier 2: Internal Infrastructure & Specialized Agents

These agents support the `.hi/` subsystem and are invoked by workflows or other agents. Not directly visible to users.

```
.hi/agents/agents/tier-2/
├── workers/                         ← Task executors (scaffolder, generator, validator, tester, reviewer)
├── observers/                       ← Observability agents (explorer, compliance, learner, observer)
└── specialists/                     ← Domain specialists (naming, ports, environment, deployment, workflow, prompt, etc.)
```

**Distinction**:
- **Tier 1**: User-facing, orchestration-level, routing-aware
- **Tier 2**: Worker bees, observers, specialists — called by Tier 1 or workflows

### Agent YAML Frontmatter

```yaml
---
description: ...    # required. One-line summary of the agent's purpose
tools:              # optional but recommended. Whitelist of tools the agent may use
  - file_search
  - grep_search
  - read_file
---
```

**Create when**: a constrained persona (restricted tools, specific behavior) adds meaningful safety or quality value. Examples: read-only exploration agents, agents scoped to a single directory or task type.

---

## Skills (`.hi/skills/`)

Domain knowledge skill packs for AI specialization. A skill is invoked when a task falls within its described domain.

```
.hi/skills/
└── project-navigation/
    └── SKILL.md                ← How to navigate this project's Hierarchical-Instruct hierarchy
```

Skills are **knowledge packs**, not task scripts — they describe how to orient, not what to do.

**Create when**: a domain has enough specialized conventions that the AI needs a briefing to act correctly and general instructions are insufficient to reliably guide it.

### Skill YAML Frontmatter

```yaml
---
description: >      # required. Multi-line description is fine
  ...               # Surfaces in skill catalog; used by model to decide when to invoke
---
```

---

## Git Hooks (`.hi/hooks/`)

Commit-time safety checks. Scripts in `.hi/hooks/` must be installed into `.git/hooks/` during project setup.

```
.hi/hooks/
├── post-merge                   ← Regenerate discovery registries after merge
├── install-hooks.sh             ← Activate via `git config core.hooksPath .hi/hooks` (POSIX)
└── install-hooks.ps1            ← Same, for Windows PowerShell
```

To install (run once per clone): `bash .hi/hooks/install-hooks.sh` or `pwsh .hi/hooks/install-hooks.ps1`

**Create when**: a class of commit-time errors can be prevented automatically. Examples: blocking `.env` commits, checking for credential patterns, enforcing instruction drift checks.

---

## YAML Frontmatter Schema

All three customization file types use a YAML frontmatter block. The fields differ by type.

> **Why frontmatter at all?** It is the **machine-readable index** for the discovery engine ([`.hi/registry/discovery_engine.py`](registry/discovery_engine.py)): `mode`/`description`/`tools` let the registry enumerate every prompt, agent, and skill — and what each is allowed to do — without parsing prose. It is also the interop contract editors and MCP clients read to list and route slash commands. The body is *what* the artifact does; the frontmatter is the *metadata* that makes it discoverable and governable. The validator enforces these fields so the registry never goes stale.

### `.hi/prompts/tier-1/*.prompt.md` (slash commands)

```yaml
---
mode: agent          # required. One of: ask | edit | agent
description: ...     # required. One-line user-facing summary
---
```

### `.hi/agents/*.agent.md` (custom agents)

```yaml
---
description: ...    # required. One-line summary of purpose
tools:              # optional but recommended. Whitelist of tools
  - file_search
  - read_file
---
```

### `.hi/skills/<skill>/SKILL.md` (knowledge packs)

```yaml
---
description: >      # required. Multi-line description is fine
  ...
---
```

---

## Development Documentation Convention

→ **[`.dev-docs` Convention](conventions.md#dev-docs-convention)** — canonical rules for `.dev-docs/`, its `.old/` archive, and the required `index.md`.

Do not restate the rules here. Copilot must ignore `.dev-docs/.old/` unless the user explicitly asks otherwise.

---

## Code Comment Convention

- Comment on **why**, not what
- One line preferred; no rambling
- Do not add comments to code you did not touch in the current change
- Do not add header blocks, file-level docstrings, or function docstrings unless explicitly asked
- If a line implements a non-obvious architectural constraint, a comment **may** name the governing `.hi/instruct.md`:

```js
// See .hi/credentials.md — all secrets must come from environment variables
const secret = process.env.JWT_SECRET;
```

---

## Hierarchical-Instruct Maintenance Rule

**Whenever an architectural change is made, the relevant `.hi/instruct.md` file(s) must be updated in the same operation.** Then run `/hip-update-index` to rebuild the index.

An architectural change includes:
- Adding, removing, or renaming a module, package, layer, or subsystem
- Changing a data format, protocol, or schema
- Adding a new integration, block type, or subsystem
- Any change that would make existing `.hi/` instruction guidance incorrect or incomplete

Do not defer `.hi/instruct.md` updates. They are part of the change, not a follow-up task.

---

## Automatic Date Maintenance

The AI updates `**Last Updated**` to today whenever it edits a `.hi/*.md` file, and fills any `[PLACEHOLDER]` whose value is unambiguous from context, without waiting to be asked.

---

## File Placement Rules

| What | Where |
|------|-------|
| System meta-instructions (this file) | `.hi/instruct.md` |
| Project content after adoption | `.hi/.hi-instruct.md` |
| Global shared rules | `.hi/conventions.md`, `.hi/maintenance.md`, `.hi/credentials.md`, etc. |
| Copilot gateway | `.github/copilot-instructions.md` |
| Project specs (platform, frameworks) | `.hi/dev-specs.md` |
| Prompt files (slash commands) | `.hi/prompts/tier-1/` |
| Custom agents | `.hi/agents/` |
| Domain knowledge skills | `.hi/skills/` |
| Git hook scripts | `.hi/hooks/` |
| Debug/helper scripts | `.hi/debug/` |
| Temporary output files | `.hi/tmp/` |

**Rules:**
- Debug scripts must **never** be placed in the workspace root
- Temporary files must **never** be placed in the workspace root
- `.hi/tmp/` contents are ephemeral — may be deleted at any time
- `.hi/debug/` scripts are AI-generated utilities — not part of the production codebase
