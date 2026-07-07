# `agents/` — Agent runtime entry points

This directory contains one YAML file per supported **agent runtime**
(also called *agent harness*, *IDE assistant*, or *CLI copilot*). Each
file documents how to install the AERS catalog onto that runtime and how
the runtime should reach the root router.

## What this directory is — and what it is not

- It is **NOT** a directory of AERS-internal agents (sub-agents, skill
  agents, etc.). The vendored skills themselves live under `skills/`, and
  the first-party catalog plugins live under `plugins/`.
- It **IS** a directory of *deployment manifests* — one per external
  runtime that the AERS catalog can be installed into. Each YAML tells a
  user (or a tool that consumes these manifests) what that runtime expects
  and where to put AERS so it works.

In other words: think of `skills/` as "the things AERS knows how to do"
and `agents/` as "the adapters that let each AI tool use those things".

## Why the catalog router pattern

Every entry point above points the runtime at **the same single router**:

> [`SKILL.md`](../SKILL.md) — `auto-empirical-research-skills`

Why not just register every vendored skill individually?

- The catalog ships **1,150+ skills**. Most IDEs auto-load *every*
  `SKILL.md` they find, which would blow past token budgets the moment a
  chat opens.
- Most vendored skills are research-tier — appropriate when the user
  asks for causal inference, replication, AER manuscript work, etc., but
  irrelevant 99% of the time.
- The root `SKILL.md` does the routing: it classifies the user request
  and points at the one or two child SKILL.md files needed.

So the recommended install for every runtime is:

1. Register the **repo root** as the home of `auto-empirical-research-skills`.
2. Skip copying individual vendored skills unless you have a specific
   reason (see the per-runtime notes in each YAML).
3. If your runtime *can* install via the marketplace, prefer that:
   `claude plugin marketplace add brycewang-stanford/Auto-Empirical-Research-Skills`.

## Supported runtimes

| File | Runtime | Native discovery | Recommended install |
|------|---------|------------------|----------------------|
| [`openai.yaml`](openai.yaml) | OpenAI Codex / CodeBuddy (legacy) | `<repo-root>` as a single skill | Whole-repo rsync, then call `$auto-empirical-research-skills`. |
| [`anthropic.yaml`](anthropic.yaml) | Anthropic Claude Code / Claude API | `.claude/skills/`, `~/.claude/settings.json` `additionalDirectories`, `/plugin marketplace` | `claude --add-dir <repo-root>` — or, preferred, `claude plugin install aer-skills@auto-empirical-research-skills`. |
| [`codebuddy.yaml`](codebuddy.yaml) | Tencent CodeBuddy IDE | `.codebuddy/skills/` | `rsync <repo-root>/ ~/.codebuddy/skills/auto-empirical-research-skills/`. |
| [`cursor.yaml`](cursor.yaml) | Cursor IDE | `.cursor/rules/*.mdc`, `.cursor/skills/` (0.45+) | Drop `.cursor/rules/aers.mdc` (template in `cursor.yaml`) that defers to `SKILL.md`. |
| [`aider.yaml`](aider.yaml) | Aider CLI | `--read FILE` or `read:` in `~/.aider.conf.yml` | `aider --read <repo-root>/SKILL.md …` — pin the path in `~/.aider.conf.yml` for persistent use. |

## Recommended starting set

If you do not know which runtime you are using, or you are introducing
AERS to a new runbook, the defaults are:

- **Claude Code / Anthropic SDK users**: `anthropic.yaml` → marketplace install.
- **Codex (OpenAI) / CodeBuddy (Tencent) users**: `codebuddy.yaml` → rsync the root.
- **Cursor users**: `cursor.yaml` → drop the `.cursor/rules/aers.mdc` shim.
- **Aider users**: `aider.yaml` → `--read` SKILL.md.
- **Generic OpenAI-shaped runtimes**: `openai.yaml` (canonical).

## Adding a new runtime

To add support for a new agent runtime:

1. Create `agents/<vendor>.yaml`.
2. Keep the top-level schema consistent:
   ```yaml
   interface:
     display_name: "AERS Empirical Research Router"
     short_description: "Route 1,150+ empirical-research skills from AERS"
     default_prompt: |
       Use $auto-empirical-research-skills to pick the right skill …
       Start with SKILL.md, follow its routing protocol, then read only
       the targeted child SKILL.md.
     install_methods:
       - <some_unique_key>:
           description: …
           command: …
           notes: …
     routes:
       catalog_router: SKILL.md
       search_ui: docs/search.html
       quickstart: make quickstart
       install_docs: INSTALL.md
   ```
3. Document the install path clearly enough that an unknown user can
   follow it without external context.
4. Call out the runtime's quirks: e.g. "Cursor only registers a directory
   that directly contains `SKILL.md` — nested folders are not surfaced".

## What is intentionally not here

- **`plugins/`** — generated first-party marketplace plugins for Claude
  Code. If you want the catalog as a *versioned Claude Code plugin*,
  install the marketplace version (see `INSTALL.md`). The `agents/`
  YAML is for *adapters that re-use the same SKILL.md folder* across
  different runtimes; `plugins/` is for *Claude Code specific plugin
  packaging* with plugin.json manifests, commands, hooks, etc.
- **`skills/<name>/SKILL.md`** — vendored child skills. The router
  always loads only the one(s) it dispatches to.

If you change anything in `agents/`, re-run a quick sanity check on
the affected YAML and then **do not** modify any CI / test / eval
artifacts — those are read-only inputs for the catalog.
