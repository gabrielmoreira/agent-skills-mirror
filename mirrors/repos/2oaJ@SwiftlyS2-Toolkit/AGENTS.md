# SwiftlyS2 Toolkit Agent Guidance

## Canonical entry

- This repository root is a standard agent skill. Read `SKILL.md` completely before planning, editing, or reviewing SwiftlyS2 work.
- In a downstream project, also read the nearest applicable `AGENTS.md` and any project-local skills it names.
- Route direct implementation, planning, and auditing through `references/edit-workflow.md`, `references/plan-workflow.md`, and `references/audit-workflow.md` respectively.

## Layout rules

- The repository root is the skill root. Keep reusable domain guidance, references, scripts, and assets directly under it.
- `SKILL.md` frontmatter must keep a stable `name` (`swiftlys2-toolkit`) and a vendor-neutral `description`; every `./`-relative path inside the skill must resolve inside this repository.
- Do not add IDE-vendor-specific agent, prompt, instruction-file, handoff-button, tool-list, or chat-mode compatibility paths.

## Implementation rules

- Prefer the smallest correct change and preserve the target project's current architecture.
- Do not add backward-compatibility branches, aliases, adapters, fallback routes, or duplicate read/write paths unless the current user request explicitly requires them.
- Treat map load/unload, player connect/disconnect, main-thread-sensitive APIs, delayed `IPlayer` access, bot identity, entity handles, and worker cancellation as mandatory review boundaries when relevant.
- For high-frequency hooks, prove the hotspot before adding pooling, `Span`, `stackalloc`, aggressive inlining, or native interop optimizations.
- Do not claim completion from static reading or a successful build alone. Drive the changed behavior through its matching runtime surface when one exists.

## Public references

Public toolkit material may depend only on SwiftlyS2 official documentation, the SwiftlyS2 official repository, and `sw2-mdwiki`. Keep private paths, project names, credentials, and workspace-only rules in the downstream project's `AGENTS.md` or a project-local skill.

## Validation

Before committing toolkit changes:

1. Validate `SKILL.md` frontmatter and that all `./`-relative paths resolve inside the repository.
2. Scan the tracked tree for vendor-specific agent/prompt formats and broken paths.
3. Re-read the full diff and keep `references/swiftlys2-asset-inventory.md` synchronized with `SKILL.md`.
