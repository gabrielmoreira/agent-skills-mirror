# AGENTS.md — Discovery Anchor → Master Reference

> ⛔ **STOP. This file holds no rules.** It is the cross-tool **discovery anchor**. The rules live in the single master reference.

## You MUST read and obey the master reference

**→ [`.hi/instruct.md`](.hi/instruct.md) is the single authoritative master.**

Before reading anything else, taking any action, or suggesting any change, **read and obey** its **[⛔ Mandatory Reading Contract](.hi/instruct.md#-stop--mandatory-reading-contract-non-negotiable)**. That contract is the *only* place that defines the mandatory reading order, the cross-cutting canonical map, the depth-priority rule (**deepest `.hi/instruct.md` wins**), and the governed import/merge guard. Do not duplicate those rules here.

## Tool compatibility (discovery only)

This repo's instruction system is read automatically by **GitHub Copilot** (via [`.github/copilot-instructions.md`](.github/copilot-instructions.md)). Every entry file below is a thin pointer to the master above:

| Tool | How it discovers the rules |
|------|----------------------------|
| GitHub Copilot | [`.github/copilot-instructions.md`](.github/copilot-instructions.md) (auto) |
| OpenAI Codex CLI | this `AGENTS.md` (auto) |
| Claude Code | [`CLAUDE.md`](CLAUDE.md) (auto) |
| Cursor | [`.cursor/rules/project.mdc`](.cursor/rules/project.mdc) |
| Continue | [`.continue/rules/project.md`](.continue/rules/project.md) |
| Cline | [`.clinerules/project.md`](.clinerules/project.md) |
| Aider | no auto-discovery — point it explicitly: `--read .hi/instruct.md` |

Any other agent: point it at [`.hi/instruct.md`](.hi/instruct.md) and obey the deepest `.hi/instruct.md` in your working directory. **Do not add rules to any pointer file** — they belong in `.hi/`.

## Pointers

- **Adopting this template** → [TEMPLATE-USAGE.md](TEMPLATE-USAGE.md); run `/hip-onboard` to fill placeholders (including [`.hi/dev-specs.md`](.hi/dev-specs.md)).
- **Autonomous layer** (opt-in, disabled by default) → [`.hi/autonomous/`](.hi/autonomous/); start at [`safety-guardrails.md`](.hi/autonomous/safety-guardrails.md) and enable via [`autonomy-config.yaml`](.hi/autonomous/autonomy-config.yaml). Invoke with [`/hip-autonomous-start`](.hi/prompts/tier-1/hip-autonomous-start.prompt.md).

