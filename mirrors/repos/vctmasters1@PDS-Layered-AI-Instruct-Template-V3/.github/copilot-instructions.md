# Copilot Meta-Instructions — Depth-Priority Hierarchical AI-INSTRUCT V3

**Role of this file**: META — defines AI tooling conventions and meta-rules for how the instruction system operates. Business domain rules live in `.ai/instruct.md` files throughout the directory tree.

**Template Version**: V3.1.1
**Last Updated**: 2026-05-25

---

## Contents

| Section | What's here |
|---------|-------------|
| [Read Project Specs First](#read-project-specs-first) | AI must load `dev-specs.md` at session start |
| [The Depth-Priority Hierarchical Paradigm](#the-depth-priority-hierarchical-paradigm) | How layering works |
| [Global Shared Instructions (`.ai/`)](#global-shared-instructions-ai) | Cross-cutting canonical files |
| [AI Prompt Files (`.github/prompts/`)](#ai-prompt-files-githubprompts) | Slash commands |
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

Before suggesting commands, file paths, line endings, or tooling, **read [`.github/dev-specs.md`](dev-specs.md)** to determine the developer OS, shell, target platform, language versions, and frameworks for this project.

Do not assume the platform from the user's prompt or your environment. The contents of `dev-specs.md` are authoritative for these facts.

For template-first repositories, `dev-specs.md` may still be partially unfilled during onboarding. In that case, ask to run `/ai-onboard` (or ask focused follow-up questions) so inferred values are confirmed and written before giving platform-specific guidance.

---

## The Depth-Priority Hierarchical Paradigm

This project uses **Hierarchical Layering by Directory Depth**. The deeper your current working directory, the more authoritative its `.ai/instruct.md` becomes.

### Precedence Rules

When working in a directory:
- **That directory's `.ai/instruct.md` is authoritative** for your current context
- Shallower `.ai/instruct.md` files provide **background/context only**
- Each level is **self-contained** — no delegation upward
- **Deeper always wins** over shallower

### Resolution Order

```
.github/copilot-instructions.md              ← META: explains HOW layering works (this file)
    ↓
.ai/instruct.md                              ← AUTHORITATIVE at workspace root
    ↓
[module]/.ai/instruct.md                     ← AUTHORITATIVE when working in that module
    ↓
[module]/[submodule]/.ai/instruct.md         ← AUTHORITATIVE when working in that submodule
```

### How to Use

1. **When you start working**: check what directory you're in
2. **Find the deepest `.ai/instruct.md`** in or above your current directory
3. **That file is authoritative** — follow it precisely
4. **Parent files** provide architectural context only
5. **Do not mix contexts** across modules

---

## Global Shared Instructions (`.ai/`)

Cross-cutting rules that would otherwise be duplicated across many files live here as single sources of truth.

```
.ai/
├── conventions.md    ← Naming, file organization, TOC rules (canonical)
├── maintenance.md    ← Archive patterns, never-delete, never-reset-db rules (canonical)
├── credentials.md    ← Credential warehousing + .gitignore rules (canonical)
├── environment.md    ← Host-vs-container isolation rules; never silently mutate the host (canonical)
└── index.md          ← MASTER INDEX of all instruction sections across the project
```

**Rule**: If a directory's `.ai/instruct.md` needs to reference a global convention, it **links** to `.ai/` rather than restating it. Never copy content from these files.

---

## AI Prompt Files (`.github/prompts/`)

AI-invocable slash commands live as `.prompt.md` files in `.github/prompts/`.

```
.github/prompts/
├── ai-onboard.prompt.md        ← /ai-onboard: Interactive wizard to ask/infer/confirm template fields
├── ai-update-index.prompt.md   ← /ai-update-index: Rebuild .ai/index.md after changes
├── ai-archive.prompt.md        ← /ai-archive: Archive a file following the convention
├── ai-new-module.prompt.md     ← /ai-new-module: Scaffold a new module and register it
├── ai-env-check.prompt.md      ← /ai-env-check: Audit host-vs-container isolation; report only, never installs
├── ai-validate.prompt.md       ← /ai-validate: Run the AI-INSTRUCT drift validator
└── ai-commit.prompt.md         ← /ai-commit: Refresh dates, validate, draft a Conventional Commits message, optionally push
```

Type the slash command in Copilot Chat to invoke. All project-specific commands use the `/ai-` prefix to distinguish them from built-in Copilot commands.

**Create when**: a multi-step workflow is executed more than twice in a session, or a workflow is complex enough that the AI needs explicit sequencing to do it correctly.

---

## Custom Agents (`.github/agents/`)

Custom Copilot agent modes live in `.github/agents/`. Each `.agent.md` defines a specialized persona with restricted tools and behavior.

```
.github/agents/
└── project-explorer.agent.md   ← Read-only codebase exploration agent
```

**Create when**: a constrained persona (restricted tools, specific behavior) adds meaningful safety or quality value. Examples: read-only exploration agents, agents scoped to a single directory or task type.

---

## Skills (`.github/skills/`)

Domain knowledge skill packs for AI specialization. A skill is invoked when a task falls within its described domain.

```
.github/skills/
└── project-navigation/
    └── SKILL.md                ← How to navigate this project's AI-INSTRUCT hierarchy
```

Skills are **knowledge packs**, not task scripts — they describe how to orient, not what to do.

**Create when**: a domain has enough specialized conventions that the AI needs a briefing to act correctly and general instructions are insufficient to reliably guide it.

---

## Git Hooks (`.github/hooks/`)

Commit-time safety checks. Scripts in `.github/hooks/` must be installed into `.git/hooks/` during project setup.

```
.github/hooks/
├── pre-commit                   ← Credential leak check + staged-`.env` block
├── install-hooks.sh             ← Activate via `git config core.hooksPath .github/hooks` (POSIX)
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

> **→ [`.dev-docs` Convention](../.ai/conventions.md#dev-docs-convention)** — canonical rules for `.dev-docs/`, its `.old/` archive, and the required `index.md`.

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

**Whenever an architectural change is made, the relevant `.ai/instruct.md` file(s) must be updated in the same operation.** Then run `/ai-update-index` to rebuild the index.

An architectural change includes:
- Adding, removing, or renaming a module, package, layer, or subsystem
- Changing a data format, protocol, or schema
- Adding a new integration, block type, or subsystem
- Any change that would make existing `.ai/` instruction guidance incorrect or incomplete

Do not defer `.ai/instruct.md` updates. They are part of the change, not a follow-up task.

---

## `.github/` File Placement Rules

| What | Where |
|------|-------|
| Copilot meta-instructions | `.github/copilot-instructions.md` |
| Project specs (platform, frameworks, dev environment) | `.github/dev-specs.md` |
| Prompt files (slash commands) | `.github/prompts/` |
| Custom agents | `.github/agents/` |
| Domain knowledge skills | `.github/skills/` |
| Git hook scripts | `.github/hooks/` |
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

## Automatic Date Maintenance

> **→ [Versioning](../.ai/conventions.md#versioning)** — canonical rules for `Last Updated` auto-fill and `[PLACEHOLDER]` resolution.

Summary (do not restate; this is a one-line reminder only): the AI updates `**Last Updated**` to today whenever it edits a `.ai/*.md` file, and fills any `[PLACEHOLDER]` whose value is unambiguous from context, without waiting to be asked.
