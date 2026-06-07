# Copilot Meta-Instructions — Depth-Priority Hierarchical AI-INSTRUCT V6

**Role of this file**: META — defines AI tooling conventions and meta-rules for how the instruction system operates. Business domain rules live in `.hi/instruct.md` files throughout the directory tree.

**Template Version**: V6.0.0
**Last Updated**: 2026-06-05

---

## Contents

| Section | What's here |
|---------|-------------|
| [Read Project Specs First](#read-project-specs-first) | AI must load `dev-specs.md` at session start |
| [The Depth-Priority Hierarchical Paradigm](#the-depth-priority-hierarchical-paradigm) | How layering works |
| [Global Shared Instructions (`.ai/`)](#global-shared-instructions-ai) | Cross-cutting canonical files |
| [Agentic Runtime (`.ai/`)](#agentic-runtime-ai) | Governed tools, foresight, self-improvement, heartbeat |
| [AI Prompt Files (`.github/prompts/`)](#ai-prompt-files-githubprompts) | Slash commands |
| [Workflow Invocation Pattern](#workflow-invocation-pattern) | Workflows are repeatable; workflows vs. utilities; do not treat them as one-time setup |
| [Governed Workflows — Import/Merge Pattern Guard](#governed-workflows--importmerge-pattern-guard) | **CRITICAL:** Imports are orchestrated workflows, not ad-hoc copy operations |
| [Custom Agents (`.github/agents/`)](#custom-agents-githubagents) | Specialized personas |
| [Skills (`.github/skills/`)](#skills-githubskills) | Domain knowledge packs |
| [Git Hooks (`.github/hooks/`)](#git-hooks-githubhooks) | Commit-time safety checks |
| [YAML Frontmatter Schema](#yaml-frontmatter-schema) | Required and optional fields for prompts, agents, skills |
| [`.dev-docs/` — Development Documentation Convention](#dev-docs--development-documentation-convention) | Pointer to canonical rules |
| [Code Comment Convention](#code-comment-convention) | Why-not-what; no docblocks unless asked |
| [AI-INSTRUCT Maintenance Rule](#ai-instruct-maintenance-rule) | Update instructions with every architectural change |
| [`.github/` File Placement Rules](#github-file-placement-rules) | Where prompts, agents, debug scripts, tmp go |
| [Automatic Date Maintenance](#automatic-date-maintenance) | Auto-fill `Last Updated` and placeholders |

---

## Read Project Specs First

Before suggesting commands, file paths, line endings, or tooling, **read [`.github/dev-specs.md`](dev-specs.md)** to determine:

1. **Project Mode** (MOST IMPORTANT): Are we in **Template Development** mode (building the framework) or **Production/Adoption** mode (using the framework for a real project)?
   - Template mode: Framework files in `.ai/`, `.github/` are authoritative and can be modified
   - Production mode: Never commit adopter-specific configs; only commit project source and templates
2. Developer OS, shell, target platform, language versions, and frameworks

Do not assume the platform or mode from the user's prompt or your environment. The contents of `dev-specs.md` are authoritative for these facts.

For template-first repositories, `dev-specs.md` may still be partially unfilled during onboarding. In that case, ask to run `/ai-onboard` (or ask focused follow-up questions) so inferred values are confirmed and written before giving platform-specific guidance.

---

## The Routing Gateway — Core Orchestration Layer

**This is the magic.** The `/ai-route` gateway is the central nervous system that powers every major workflow in this project. It is **not optional** — it is the defining feature that makes depth-priority hierarchy practical at scale.

### What Routing Does

Before any workflow (import, validation, module creation, etc.) executes, the router:

1. **Resolves scope** — finds the deepest `.ai/instruct.md` that governs the affected paths
2. **Checks governance** — applies any external rules or constraints
3. **Routes to authority** — delegates to the domain manager/supervisor that owns that scope
4. **Enables escalation** — halts on conflicts and explains why

### Why This Matters

Without routing, each workflow would need to implement scope resolution independently → **duplicate logic, brittleness, easy to bypass.**

With routing, all workflows speak the same language → **consistent, auditable, scope-aware.**

### Routed Workflows (Today)

| Workflow | Routed to |
|----------|-----------|
| `/ai-import-execute` | `pds-man-imports` (Phase 0-7 orchestration) |
| `/ai-adapt-infrastructure` | `pds-man-infrastructure` (infrastructure compliance & adaptation) |
| `/ai-validate` | `pds-pipe-validator` (scope-aware validation) |
| `/ai-reflect` | `pds-meta-learner` (gap analysis) |
| `/ai-update-index` | `pds-man-curator` (index rebuild) |
| `/ai-new-module` | `pds-pipe-scaffolder` (module scaffolding) |

Each workflow does **not** know how to resolve scope or apply governance—it delegates that to the router and lets the router decide who should execute.

### The Router Itself

→ **[/ai-route prompt](prompts/ai-route.prompt.md)** — invoke when you need scope resolution before delegating  
→ **[pds-meta-router agent](agents/pds-meta-router.agent.md)** — technical details and governance resolution logic

---

## The Depth-Priority Hierarchical Paradigm

This project uses **Hierarchical Layering by Directory Depth**. The deeper your current working directory, the more authoritative its `.hi/instruct.md` becomes.

### Precedence Rules

When working in a directory:
- **That directory's `.hi/instruct.md` is authoritative** for your current context
- Shallower `.hi/instruct.md` files provide **background/context only**
- Each level is **self-contained** — no delegation upward
- **Deeper always wins** over shallower

### Resolution Order

```
.github/copilot-instructions.md              ← META: explains HOW layering works (this file)
    ↓
.hi/instruct.md                              ← AUTHORITATIVE at workspace root
    ↓
[module]/.hi/instruct.md                     ← AUTHORITATIVE when working in that module
    ↓
[module]/[submodule]/.hi/instruct.md         ← AUTHORITATIVE when working in that submodule
```

### How to Use

1. **When you start working**: check what directory you're in
2. **Find the deepest `.ai/instruct.md`** in or above your current directory
3. **That file is authoritative** — follow it precisely
4. **Parent files** provide architectural context only
5. **Do not mix contexts** across modules

---

## Global Shared Instructions (`.hi/`)

Cross-cutting rules that would otherwise be duplicated across many files live here as single sources of truth.

```
.hi/
├── conventions.md    ← Naming, file organization, TOC rules (canonical)
├── maintenance.md    ← Archive patterns, never-delete, never-reset-db rules (canonical)
├── credentials.md    ← Credential warehousing + .gitignore rules (canonical)
├── environment.md    ← Host-vs-container isolation rules; never silently mutate the host (canonical)
├── index.md          ← MASTER INDEX of all instruction sections across the project
├── agent-config.yaml ← Agentic runtime config: heartbeat, log format, safety, foresight, self-improvement
├── heartbeat.md      ← Heartbeat procedure: what agents do every N steps to re-align
├── engine/           ← Runtime scripts (foresight_engine.py, get_effective_instructions.py)
├── agents/tools/     ← Governed tool checklists read by agents (not MCP wire-protocol tools)
├── mcp/tools/        ← Project-specific governed tool checklists
├── foresight/        ← Foresight analysis outputs (runtime; gitignored)
├── knowledge/        ← Accumulated knowledge base (runtime; gitignored)
└── logs/             ← Agent audit logs (runtime; gitignored)
```

**Rule**: If a directory's `.hi/instruct.md` needs to reference a global convention, it **links** to `.hi/` rather than restating it. Never copy content from these files.

---

## Agentic Runtime (`.hi/`)

The `.hi/` directory doubles as the agentic runtime platform, layering proactive capabilities on top of the depth-priority instruction system.

**Key capabilities:**

| Capability | Mechanism |
|---|---|
| **Heartbeat** | Every 6 steps, agents re-read the active instruction scope and re-align |
| **Foresight** | Before acting, `foresight_engine.py` anticipates gaps (error handling, logging, tests) and forecasts risks |
| **Self-improvement** | After major tasks, agents reflect and propose edits to `.ai/instruct.md` files |
| **Governed tools** | Governed tool JSON files in `.ai/agents/tools/` include a `checklist` and `safety_level` — agents must follow the checklist before acting |
| **Audit logging** | All agent changes are logged to `.ai/logs/` for traceability |

**Rules:**
- `agent-config.yaml` is the single source of truth for runtime behavior — do not duplicate its settings elsewhere
- `.hi/foresight/`, `.hi/knowledge/`, and `.hi/logs/` are runtime outputs — gitignored; never commit them
- Governed tool checklists live in `.hi/agents/tools/` (built-in) or `.hi/mcp/tools/` (project-specific) — these are **governance documents read by agents**, not MCP wire-protocol tool definitions
- `heartbeat.md` defines the procedure agents follow at every heartbeat interval — configurable in `agent-config.yaml`
- `get_effective_instructions.py` implements depth-priority resolution — do not alter its traversal logic
- Heartbeat and foresight are configured via `agent-config.yaml`; adjust `heartbeat_interval` and `foresight:` keys to tune

---

## AI Prompt Files (`.github/prompts/`)

AI-invocable slash commands live as `.prompt.md` files in `.github/prompts/`.

```
.hi/prompts/
├── hip-onboard.prompt.md        ← /hip-onboard: Interactive wizard (also absorbs existing-project import)
├── hip-update-index.prompt.md   ← /hip-update-index: Rebuild .hi/index.md after changes
├── hip-archive.prompt.md        ← /hip-archive: Archive a file following the convention
├── hip-new-module.prompt.md     ← /hip-new-module: Scaffold a new module and register it
├── hip-env-check.prompt.md      ← /hip-env-check: Audit host-vs-container isolation; report only, never installs
├── hip-validate.prompt.md       ← /hip-validate: Run the AI-INSTRUCT drift validator
├── hip-foresight.prompt.md      ← /hip-foresight: Run foresight gap/risk analysis on current task before acting
├── hip-reflect.prompt.md        ← /hip-reflect: Post-task reflection; identify instruction gaps and propose .hi/ improvements
├── hip-plugin-discover.prompt.md ← /hip-plugin-discover: Enumerate optional plugins under .hi/plugins/; read-only
└── hip-git.prompt.md            ← /hip-git: Version control (subcommands: branch | commit | pr | status)
```

Type the slash command in Copilot Chat to invoke. All project-specific commands use the `/hip-` prefix to distinguish them from built-in Copilot commands.

**Create when**: a multi-step workflow is executed more than twice in a session, or a workflow is complex enough that the AI needs explicit sequencing to do it correctly.

---

## Workflow Invocation Pattern

**Workflows** are repeatable, idempotent operations that can be invoked at any time — not one-time setup tasks.

### Workflows (Repeatable)

Invoke these whenever the operation is needed, not just during initial setup:

| Workflow | Purpose | Repeatable? |
|----------|---------|------------|
| `/hip-onboard` | Initialize or update project metadata (identity, dev-specs, module list) | Yes — re-run to refresh identity or add modules |
| `/hip-import-execute` | Import/merge external projects with full Phase 0-6 orchestration | Yes — use each time you merge a new project |
| `/hip-new-module` | Scaffold a new module (instruct.md, dev-docs, registration) | Yes — invoke per module |
| `/hip-update-index` | Rebuild `.hi/index.md` from current state | Yes — run after editing any `.hi/instruct.md` |
| `/hip-archive` | Archive (never delete) a file or directory | Yes — use per archival task |

### Utilities (Informational, No State Change)

Run these to inspect or analyze; they do not modify the project:

| Utility | Purpose |
|---------|---------|
| `/hip-validate` | Audit instruction drift; report findings |
| `/hip-env-check` | Audit host-vs-container isolation |
| `/hip-foresight` | Analyze gaps/risks before acting |
| `/hip-reflect` | Post-task reflection; propose improvements |
| `/hip-observe` | Display runtime observability and metrics |
| `/hip-git` | Query version control state (no auto-commits) |

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
2. **Read** `.ai/instruct.md` to understand the authoritative import strategy for this project
3. **Invoke `/ai-import-execute`** (or the project's equivalent import orchestration prompt)
4. **Let the agent orchestration layer** (pds-meta-migrator → pds-pipe-importer) handle:
   - Phase 0: Operational validation (LLM dispatch, env, credentials, naming)
   - Phase 1-6: Artifact preservation, analysis, integration, modernization, and registry updates
5. **Wait for completion** before suggesting next steps

### Why This Matters

- **Naming conflicts** — Projects have different conventions; ad-hoc copies violate the registry
- **Module authority drift** — Each module's `.ai/instruct.md` is authoritative; manual moves break the hierarchy
- **Credential leakage** — Phase 0 validation catches `.env` files; ad-hoc copies miss them
- **Registry corruption** — Module lists, naming conventions, error codes, API endpoints all need updates; manual copies bypass the updater
- **Audit trail loss** — Proper import logs every decision; ad-hoc commands leave no trace

### Example (What NOT to Do)

```
User: "Clone https://github.com/user/project.git and move it into src/"

❌ WRONG:
  git clone https://github.com/user/project.git
  Move-Item project/* -Destination src/
  (no validation, no registry updates, no module supervision)

✅ RIGHT:
  Recognize: This is an import workflow
  → Invoke /ai-import-execute with the source URL
  → Let orchestration handle Phase 0 + Phases 1-6
  → Confirm completion before offering next steps
```

---

## Custom Agents (`.github/agents/`)

Custom Copilot agent modes live in `.github/agents/`. Each `.agent.md` defines a specialized persona with restricted tools and behavior.

```
.hi/agents/
├── tier-1/ (router, curator, imports, infrastructure, super)
├── tier-2/workers/ (scaffolder, generator, validator, tester, reviewer)
├── tier-2/observers/ (explorer, compliance, learner, observer)
└── tier-2/specialists/ (naming, ports, environment, deployment, workflow, prompt, todo, versioncontrol, cleanup)
```

**Create when**: a constrained persona (restricted tools, specific behavior) adds meaningful safety or quality value. Examples: read-only exploration agents, agents scoped to a single directory or task type.

---

## Skills (`.github/skills/`)

Domain knowledge skill packs for AI specialization. A skill is invoked when a task falls within its described domain.

```
.hi/skills/
└── project-navigation/
    └── SKILL.md                ← How to navigate this project's AI-INSTRUCT hierarchy
```

Skills are **knowledge packs**, not task scripts — they describe how to orient, not what to do.

**Create when**: a domain has enough specialized conventions that the AI needs a briefing to act correctly and general instructions are insufficient to reliably guide it.

---

## Git Hooks (`.github/hooks/`)

Commit-time safety checks. Scripts in `.github/hooks/` must be installed into `.git/hooks/` during project setup.

```
.hi/hooks/
├── post-merge                   ← Regenerate discovery registries after merge
├── install-hooks.sh             ← Activate via `git config core.hooksPath .hi/hooks` (POSIX)
└── install-hooks.ps1            ← Same, for Windows PowerShell
```

To install (run once per clone): `bash .github/hooks/install-hooks.sh` or `pwsh .github/hooks/install-hooks.ps1`

**Create when**: a class of commit-time errors can be prevented automatically. Examples: blocking `.env` commits, checking for credential patterns, enforcing instruction drift checks.

> **Tooling discipline**: Every facility above must be earned — create it when it provides clear, reusable value, not speculatively. The AI **may** proactively suggest creating tooling when a pattern is observed, but **must ask before creating** any `.github/` tooling file.

---

## YAML Frontmatter Schema

All three customization file types use a YAML frontmatter block. The fields differ by type.

### `.github/prompts/*.prompt.md` (slash commands)

```yaml
---
mode: agent          # required. One of: ask | edit | agent. Use `agent` for prompts that need full tool access (file edits, terminal, etc.); `edit` for surgical multi-file edits; `ask` for read-only Q&A.
description: ...     # required. One-line user-facing summary shown when the slash command surfaces in pickers.
---
```

Notes:
- All `/ai-*` prompts in this template use `mode: agent` because they perform multi-step file operations.
- Do not add a `tools:` list to prompts — prompts inherit the active chat's tool set.

### `.github/agents/*.agent.md` (custom agents)

```yaml
---
description: ...    # required. One-line summary of the agent's purpose and when to invoke it.
tools:              # optional but recommended. Whitelist of tools the agent may use. Omit to inherit the workspace default.
  - file_search
  - grep_search
  - read_file
---
```

Notes:
- Agents do **not** take a `mode:` field — they *are* a mode.
- When defining a read-only or scoped agent, always set a `tools:` whitelist so the constraint is enforced, not aspirational.

### `.github/skills/<skill>/SKILL.md` (knowledge packs)

```yaml
---
description: >      # required. Multi-line description is fine. Surfaces in the skill catalog;
  ...               # also used by the model to decide when to invoke the skill.
---
```

Notes:
- `SKILL.md` uppercase casing is required by the VS Code Copilot skill discovery system — do not rename.
- Skills do not declare `tools:` or `mode:`; they only provide knowledge.

---

## `.dev-docs/` — Development Documentation Convention

> **→ [`.dev-docs` Convention](.hi/conventions.md#dev-docs-convention)** — canonical rules for `.dev-docs/`, its `.old/` archive, and the required `index.md`.

Do not restate the rules here. Copilot must ignore `.dev-docs/.old/` unless the user explicitly asks otherwise.

---

## Code Comment Convention

- Comment on **why**, not what
- One line preferred; no rambling
- Do not add comments to code you did not touch in the current change
- Do not add header blocks, file-level docstrings, or function docstrings unless explicitly asked
- If a line implements a non-obvious architectural constraint, a comment **may** name the governing `.ai/instruct.md`:

```js
// See .ai/credentials.md — all secrets must come from environment variables
const secret = process.env.JWT_SECRET;
```

---

## AI-INSTRUCT Maintenance Rule

**Whenever an architectural change is made, the relevant `.hi/instruct.md` file(s) must be updated in the same operation.** Then run `/hip-update-index` to rebuild the index.

An architectural change includes:
- Adding, removing, or renaming a module, package, layer, or subsystem
- Changing a data format, protocol, or schema
- Adding a new integration, block type, or subsystem
- Any change that would make existing `.hi/` instruction guidance incorrect or incomplete

Do not defer `.hi/instruct.md` updates. They are part of the change, not a follow-up task.

---

## `.github/` File Placement Rules

| What | Where |
|------|-------|
| Copilot meta-instructions | `.github/copilot-instructions.md` |
| Project specs (platform, frameworks, dev environment) | `.github/dev-specs.md` |
| Prompt files (slash commands) | `.hi/prompts/` |
| Custom agents | `.hi/agents/` |
| Domain knowledge skills | `.hi/skills/` |
| Git hook scripts | `.hi/hooks/` |
| Project-level TODO lists | `.github/todo/` |
| Debug/helper scripts created by AI | `.github/debug/` |
| Temporary output files | `.github/tmp/` |

**VS Code settings** live in `.vscode/` (committed for shared project defaults; personal overrides use `settings.local.json` which is gitignored).

**Rules:**
- Debug scripts must **never** be placed in the workspace root
- Temporary files must **never** be placed in the workspace root
- `.github/tmp/` contents are ephemeral — may be deleted at any time
- `.github/debug/` scripts are AI-generated utilities — not part of the production codebase

---

## Deployment Modes — `.deployment/`

Deployment modes are first-class **depth-priority scopes** keyed by the `DEPLOY_MODE` environment variable. See [`.deployment/README.md`](../.deployment/README.md) for the convention and [`/hip-deploy-mode`](prompts/hip-deploy-mode.prompt.md) to inspect or switch.

```
.deployment/
├── README.md                          ← convention + required-section list for each mode
├── dev-local/.hi/instruct.md          ← AUTHORITATIVE when DEPLOY_MODE=dev-local
├── dev-lan/.hi/instruct.md            ← AUTHORITATIVE when DEPLOY_MODE=dev-lan
├── prod-railway/.hi/instruct.md       ← AUTHORITATIVE when DEPLOY_MODE=prod-railway
└── prod-self-serve/.hi/instruct.md    ← AUTHORITATIVE when DEPLOY_MODE=prod-self-serve
```

**Rules:**
- A mode's `.hi/instruct.md` is authoritative whenever `DEPLOY_MODE` matches its directory name. The depth-priority winner is `.deployment/<active>/.hi/instruct.md` for any deployment-relevant question.
- A mode **cannot relax** a rule from a shallower `.hi/*.md` (e.g., a mode cannot permit committing `.env`).
- Mode names are kebab-case and registered with the `naming` agent (Mode 3) — never invent one without a consultation.
- The [`deployment-manager`](agents/pds-man-deployment.agent.md) agent watches `.deployment/` for drift and proposes `update / add / retire / rename`.
- Switching mode is a **human action** — agents emit shell-export snippets but never mutate the active shell.

---

## Automatic Date Maintenance

> **→ [Versioning](.hi/conventions.md#versioning)** — canonical rules for `Last Updated` auto-fill and `[PLACEHOLDER]` resolution.

Summary (do not restate; this is a one-line reminder only): the AI updates `**Last Updated**` to today whenever it edits a `.hi/*.md` file, and fills any `[PLACEHOLDER]` whose value is unambiguous from context, without waiting to be asked.
