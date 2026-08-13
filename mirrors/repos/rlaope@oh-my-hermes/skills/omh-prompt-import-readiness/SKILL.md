---
name: omh-prompt-import-readiness
description: [omh] Prompt import readiness - review and normalize external CLI-agent prompt files before offering slash-command candidates; use external-connector-readiness for plugin or API adoption and toolbelt-readiness for missing runtime capabilities. Use when the user says: prompt-import-readiness, prompt import readiness, slash prompt import, slash prompts import, slash command prompt import, prompt library import, prompt folder import, prompt directory import.
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, prompt]
    category: prompt
    phase: prompt-import-readiness
    role: guide
    quality_tier: workflow-surface-gated
---

# Prompt Import Readiness

This is a Hermes-native `prompt-import-readiness` workflow skill.

## Why This Exists

`prompt-import-readiness` exists so Hermes users can ask for this workflow in chat and receive a structured, evidence-bounded OMH operating surface instead of ad hoc narration.

## Do Not Use When

- The request is already handled by a narrower explicit skill with stronger evidence.
- The user asks OMH to secretly run external platforms, connectors, schedulers, file exports, or runtime agents.
- The only safe answer is to ask for missing authority, credentials, target, or observed evidence first.

## Examples

Good example:

- Prompt: prompt-import-readiness review Codex and Claude Code prompt folders before exposing them as Hermes slash commands with $ARGUMENTS mapping.
- Expected behavior: Produce `prepare_prompt_import_readiness` with required context, wrapper actions, and not-evidence boundaries.
- Why: The prompt names a real workflow surface that Hermes can orchestrate without hiding execution.

Bad example:

- Prompt: prompt-import-readiness silently import every external prompt, overwrite slash commands, and claim the prompts are trusted without review.
- Expected behavior: Report the missing observed evidence or authority instead of claiming the external step happened.
- Why: Prepared OMH guidance is not platform, runtime, connector, file, memory, or delivery evidence.

## Completion Checklist

- Prompt sources, agent family, expected file formats, argument syntax, slash-command names, trust level, and stop condition are explicit.
- Explicit-path audit reads and compatibility results are observed only in their audit output; source discovery, command registration, prompt mutation, slash-command activation, and dry-run execution remain marked not_observed.
- Route broad candidate discovery to skill-scout, prompt/tool safety to security-safety-review, missing CLIs or directories to toolbelt-readiness, and approved implementation to a selected executor handoff.
- Imported prompts, generated command files, registry updates, and dry-run results are reported only from observed prompt-import evidence.

## Recovery Notes

- If source prompt directories are unknown, route to workspace-audit or skill-scout before readiness scoring.
- If source trust, prompt-injection risk, secrets, or destructive command content is unclear, route to security-safety-review before import.
- If the user asks to actually copy, generate, or register prompt files, prepare an executor or workspace-file handoff and keep readiness prepared_not_observed until file evidence exists.

## Workflow Lane

- Current lane: **Automation and status** (`achievements`, `workspace-audit`, `production-audit`, `automation-blueprint`, `github-event-ops`, `buzz`, `agent-board`, `gateway-intent-card`, `+34 more`) - schedules, status, health, and ops review.
- If intent belongs to another lane, hand back to `oh-my-hermes` or name the adjacent workflow.
- Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.

## Use When

Use before importing, normalizing, or exposing external prompt files as Hermes slash commands so source trust, formats, argument interpolation, name collisions, review status, and dry-run evidence stay explicit.

    Strong routing signals: `prompt-import-readiness`, `prompt import readiness`, `slash prompt import`, `slash prompts import`, `slash command prompt import`, `prompt library import`, `prompt folder import`, `prompt directory import`, `import CLI prompts`, `import agent prompts`, `CLI agent prompt files`, `OpenCode prompt import`, `Claude Code prompt import`, `Codex prompt import`, `codex prompt import`, `Gemini CLI prompt import`, `frontmatter prompt import`, `prompt compatibility audit`, `explicit prompt file audit`, `argument interpolation`, `$ARGUMENTS mapping`, `{{args}} mapping`, `$1-$9 prompt arguments`, `prompt slash command collision`, `Hermes slash prompts`, `슬래시 프롬프트 가져오기`, `프롬프트 가져오기`, `프롬프트 디렉터리 가져오기`, `프롬프트 폴더 가져오기`, `슬래시 명령 프롬프트`, `프롬프트 인자 매핑`

## Catalog Metadata

Category: `prompt`
Phase: `prompt-import-readiness`
Hermes role: `guide`
Quality tier: `workflow-surface-gated`
Reasoning demand: `standard`

Quality bar:

- Name the user-facing workflow objective, required context, next action, and stop condition.
- Separate prepared guidance from observed platform, runtime, connector, file, memory, or delivery evidence.
- Expose missing tools, credentials, targets, or observations as user-visible gaps.

Handoff policy:

Keep this as Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or host-runtime handoff only when the user accepts that next step and observed evidence can be recorded.

Required inputs:

- user request
- target context
- delivery or status expectation
- known missing evidence

Expected outputs:

- prompt_import_readiness_card/v1
- prompt_compatibility_audit/v1 for explicitly named local files
- prompt_source_inventory/v1
- prompt_format_matrix/v1
- argument_interpolation_policy/v1
- slash_command_collision_report/v1
- prompt_trust_review/v1
- prompt_import_manifest/v1 when observed
- next action
- prepared-vs-observed boundary

Artifact expectations:

- prompt_import_readiness_card/v1 metadata-only wrapper card when prepared
- prompt_compatibility_audit/v1 with bounded source metadata, format classification, argument syntax, collisions, and review reasons for explicitly named local files
- prompt_source_inventory/v1 with source directory, agent family, file count, format claim, and review state
- prompt_format_matrix/v1 separating YAML frontmatter, TOML frontmatter, raw markdown/text, and unsupported formats
- argument_interpolation_policy/v1 for $ARGUMENTS, $1-$9, {{args}}, named placeholders, escaping, and missing argument handling
- slash_command_collision_report/v1 with command names, aliases, existing Hermes commands, and conflict resolution policy
- prompt_trust_review/v1 with source trust, prompt-injection risk, secret leakage risk, license/source notes, and review owner
- prompt_import_manifest/v1 only when file reads, parsed prompts, generated slash-command candidates, or dry-run output are observed

Safety rules:

- An explicit-path prompt compatibility audit observes only bounded local file classification and metadata. It is not source-directory discovery, prompt import, slash command registration, prompt mutation, command activation, imported prompt trust, or successful dry-run evidence.
- Do not claim connector, gateway, runtime, file generation, memory mutation, or host automation evidence from prepared guidance.

## Runtime Evidence

Preferred harness for this skill: `prompt-import-readiness`.

```sh
omh runtime record --skill prompt-import-readiness --harness prompt-import-readiness --status started
```

Record observed delegation results; otherwise return `not_available` or `not_observed`.
Prepared OMH routing is not execution, review, CI, merge-readiness, or merge evidence.
- Treat wrapper memory/context summaries as advisory local context, not proof of opaque Hermes memory reads or changes.
Preserve workflow intent and stop conditions; verify before claiming completion.

Use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
