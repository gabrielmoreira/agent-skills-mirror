---
name: oh-my-opencode-slim
description: Configure and improve oh-my-opencode-slim for the current user. Use when users want to tune agents, models, prompts, custom agents, skills, MCPs, presets, or plugin behavior. Also use when recurring workflow friction suggests a safe config or prompt improvement.
---

# oh-my-opencode-slim Configuration Skill

You help users configure and safely improve oh-my-opencode-slim, including
small prompt/config changes that make future runs better.

## When to Use

Use when the user asks about, or a session reveals repeatable friction in:

- plugin config (`oh-my-opencode-slim.json[c]`), presets, models/variants
- delegation behavior, specialist prompts, custom agents (`agents.<name>`)
- skills, MCPs, tool access, disabled agents; background/multiplexer/deepwork

Suggest config changes only for recurring behavior, not one-offs.

## Files

- User config: `~/.config/opencode/oh-my-opencode-slim.jsonc` (preferred) or `.json`; project override: `<project>/.opencode/oh-my-opencode-slim.json`.
- Prompt tuning: `~/.config/opencode/oh-my-opencode-slim/{agent}[_append].md` (prefer `_append.md`; preset variant under `{preset}/`).
- Skill shadow: `~/.config/opencode/skills/<skill-name>/SKILL.md` shadows the bundled skill.
- Agent names: `orchestrator|oracle|explorer|designer|fixer|observer|council`.

Lookup: with an active preset, check `{preset}/` first, then the base dir.
`{agent}.md` replaces the built-in prompt; `{agent}_append.md` appends to it. Each works alone; neither present → unchanged built-in prompt.

Common customizations:

- Presets/models: switch preset; cheaper models for `explorer`/`fixer`, stronger ones for `orchestrator`/`oracle`/`designer`.
- Permissions: per-agent `skills`/`mcps` (`['*']`, names, or `['*', '!x']`); enable optional agents by removing them from `disabled_agents`.
- Custom agents under `agents.<name>` with `prompt` plus `orchestratorPrompt` (trigger and non-use).
- Prompt tuning via `{agent}_append.md` for recurring behavior or house style.

Important schema boundary:

- Built-in agents (`orchestrator`, `oracle`, `explorer`,
  `designer`, `fixer`, `observer`, `council`) can set models, variants, skills,
  MCPs, options, and display names in config.
- Built-in agent `prompt` and `orchestratorPrompt` fields are **not** supported
  in `oh-my-opencode-slim.json[c]`; use markdown prompt override files instead.
- Unknown keys under top-level `agents` are custom agents. Custom agents may use
  `prompt` and `orchestratorPrompt` directly in config.

## Config Shapes

Tune built-ins at `presets.<preset>.<agent>` (model/variant/skills/mcps).
Append tuning via `{agent}_append.md` (preset variant under `{preset}/`).
Full `{agent}.md` replacement is rare — it must restate all essential behavior.

## Safe Improvement Rules

Configuration changes affect future agent behavior, so treat them as user-owned.

1. **Ask before changing config or prompts.**
   - Explain the proposed improvement briefly.
   - State which file would change.
   - Ask for confirmation unless the user explicitly requested the exact edit.
2. **Prefer narrow changes.**
   - Do not rewrite large prompts when a small rule solves the problem.
   - Do not add custom agents for one-off tasks.
3. **Preserve existing user settings.**
   - Merge with current config rather than regenerating from scratch.
   - Keep comments and formatting where practical for JSONC files.
4. **Avoid hidden behavior changes.**
   - Mention cost, permissions, or delegation changes before applying them.
   - Be explicit if a model/provider change may increase spend.
5. **Tell the user about restart requirements.**
   - Config, prompt, agent, skill, MCP, or plugin changes may need a restart.
   - Phrase it as: "This should apply on the next OpenCode run; restart OpenCode
     if you need it immediately."

## Configuration Workflow

1. Inspect: read current config, active `preset`, relevant agent blocks, project overrides.
2. Minimize: pick the smallest change (model/preset, prompt rule, custom agent, or permission).
3. Confirm: show a concise proposal with the target file path.
4. Edit: preserve unrelated settings, JSONC formatting, and exact agent/skill/MCP names.
5. Validate: ensure the file still parses; run repo config checks if available.
6. Activate: state whether it applies immediately or on next OpenCode run/restart.

## Custom Agent Pattern

Custom agents suit narrow, repeatable jobs the Orchestrator can route.

Use this shape:

```jsonc
{
  "agents": {
    "api-reviewer": {
      "model": "openai/gpt-6",
      "variant": "high",
      "prompt": "You review API contracts, error semantics, and migration risk. Return concise findings with file references.",
      "orchestratorPrompt": "Delegate API contract, public SDK, or backwards-compatibility reviews to @api-reviewer. Do not use it for routine implementation.",
      "skills": [],
      "mcps": []
    }
  }
}
```

Good custom agents have:

- a specific job;
- clear trigger conditions in `orchestratorPrompt`;
- explicit non-use conditions;
- only the skills and MCPs they actually need;
- a model appropriate to the task's judgment/cost needs.

Avoid custom agents that duplicate existing specialists:

- codebase scouting and external docs/research → `explorer`
- architecture/debugging/review → `oracle`
- UI/UX polish → `designer`
- scoped mechanical implementation → `fixer`

## Prompt Tuning Pattern

Prompt edits suit recurring behavior across many sessions.

Good reasons to tune a prompt:

- The Orchestrator repeatedly over- or under-delegates for this workflow.
- A specialist repeatedly misses a project convention.
- The user wants a stable communication or verification style.
- The team has a recurring review checklist or deployment rule.

Poor reasons to tune a prompt:

- A one-off task failed once.
- The current problem can be solved by normal instruction in this session.
- The change would make the agent worse for general use.

When suggesting a prompt improvement, say:

```text
I noticed this is recurring. I can add a small rule to <agent/config path> so
future runs handle it automatically. Want me to make that config change?
```

## Final Checklist

- [ ] Did the user confirm config/prompt edits, unless explicitly requested?
- [ ] Did the edit preserve existing settings?
- [ ] Is the active preset still valid?
- [ ] Are skill/MCP/tool permissions intentional and minimal?
- [ ] Did you mention OpenCode restart/next-run behavior?
