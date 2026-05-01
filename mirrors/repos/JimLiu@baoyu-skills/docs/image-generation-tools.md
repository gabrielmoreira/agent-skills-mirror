# Image Generation Tools

Skills in this repo are loaded by multiple agent runtimes (Claude Code, Codex, Hermes, other agents, bare CLI). Each runtime exposes a different image-generation capability — some have a runtime-native tool (Codex `imagegen`, Hermes `image_generate`), others rely on an installed skill (`baoyu-imagine`, or user-defined). This document defines the canonical **backend-selection rule** every skill that renders images follows so skills stay portable.

## The Rule

When a skill needs to render an image, resolve the backend in this order:

1. **Current-request override** — if the user names a specific backend in the current message, use it.
2. **Saved preference** — if the skill's `EXTEND.md` sets `preferred_image_backend` to a backend available right now, use it.
3. **Auto-select** (when the preference is `auto`, unset, or the pinned backend isn't available):
   - If the current runtime exposes a native image tool (e.g., Codex `imagegen`, Hermes `image_generate`), use it. Runtime-native tools are preferred by default — agents that know their own tool inventory should surface the native one here.
   - Otherwise, if exactly one non-native backend is installed (e.g., `baoyu-imagine`), use it.
   - Otherwise (multiple non-native backends with no runtime-native tool), ask the user once — batch with any other initial questions.
4. **If none are available**, tell the user and ask how to proceed.

Setting `preferred_image_backend: ask` forces the step-3 prompt every run regardless of available backends.

## The Preference Field

Each image-consuming skill's `EXTEND.md` carries a single `preferred_image_backend` field:

| Value | Meaning |
|---|---|
| `auto` (default) | Apply the auto-select rule — runtime-native preferred, fall back to only installed backend, ask if multiple non-native. |
| `ask` | Always confirm the backend on every run, even when a runtime-native tool exists. |
| `<backend-id>` (e.g., `codex-imagegen`, `baoyu-imagine`, `image_generate`) | Pin this backend when available; fall back to `auto` if it isn't. |

The field is **absent-equals-auto**: older `EXTEND.md` files without this field behave exactly as if `preferred_image_backend: auto` were set. No schema version bump is needed to introduce it.

## Prompt File Requirement (hard)

Regardless of which backend is chosen, every skill that renders images MUST write each image's full, final prompt to a standalone file under `prompts/` (naming: `NN-{type}-[slug].md`) BEFORE invoking any backend. The backend receives the prompt file (or its content); the file is the reproducibility record and allows switching backends without regenerating prompts.

## How Skills Declare This

Each `SKILL.md` that renders images includes **exactly one** `## Image Generation Tools` section (near the top, after `## User Input Tools` and before the main workflow) that **inlines** this rule. Skills are self-contained and cannot link to `docs/` — each skill folder must ship the rule inside its own `SKILL.md`. See [CLAUDE.md → Skill Self-Containment](../CLAUDE.md).

Each skill's `references/config/preferences-schema.md` (and its `EXTEND.md` template in `first-time-setup.md`) lists `preferred_image_backend` alongside other preference fields. First-time setup does NOT ask the user about the backend — `auto` is set silently. Users who want to pin a specific backend edit `EXTEND.md` later, and each skill's `## Changing Preferences` section documents the common one-line edits.

Concrete tool names (`imagegen`, `image_generate`, `baoyu-imagine`) in this document and in SKILL.md are **examples** — agents in other runtimes apply the rule above and substitute the local equivalent. Skill-specific parameters for these backends are illustrative; runtimes without those knobs can omit them.

## Backend Skills Are Exempt

Skills that **are themselves** image-generation backends — currently `baoyu-imagine`, `baoyu-image-gen` (deprecated), and `baoyu-danger-gemini-web` — do NOT include a `## Image Generation Tools` section. They render directly via their own provider integrations and have no need to "select a backend." The rule applies only to consumer skills that delegate rendering to whatever backend the runtime exposes.
