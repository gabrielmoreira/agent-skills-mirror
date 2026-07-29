# lateralus — project context

> **Single source of truth for all AI agents working in this repo.**
> `CLAUDE.md` and `GEMINI.md` both point here.

## Project overview

Lateralus is a lateral-thinking skill for AI coding agents that breaks debugging tunnel vision.
It surfaces the user's end goal and solution horizon (long-term, MVP, POC, workaround), then generates
goal-appropriate alternatives in two tiers: grounded-but-unlikely and wild/speculative reframes.

Ships as a Copilot repo skill and direct install via `install.sh` / `install.ps1`.

---

## What lives where

```
lateralus/
├── README.md                         # Front door (product pitch + install one-liners)
├── INSTALL.md                        # Full install matrix
├── CONTRIBUTING.md                   # Dev guide and file ownership
├── AGENTS.md                         # This file — maintainer context for all agents
├── CLAUDE.md / GEMINI.md             # Thin stubs pointing here
│
├── install.sh                        # macOS / Linux / WSL installer
├── install.ps1                       # Windows PowerShell installer
│
├── skills/                           # ALL skills — single source of truth
│   ├── lateralus/
│   │   ├── SKILL.md                  # Full debugging skill
│   │   └── README.md
│   └── lateralus-brainstorm/
│       └── SKILL.md                  # Full brainstorming / plan-mode skill
│
├── agents/                           # Subagents — single source of truth
│   ├── lateralus-ideator-ground.md   # Generates Tier 1 grounded hypotheses
│   ├── lateralus-ideator-balanced.md # Generates middle-ground hypotheses
│   ├── lateralus-ideator-wild.md     # Generates Tier 3 wild reframes
│   └── lateralus-workaround.md       # Makeshift bypasses with debt log
│
├── hooks/                            # PostToolUse hook implementations
│   ├── lateralus-hook.py             # Python hook (macOS / Linux / WSL)
│   └── lateralus-hook.ps1            # PowerShell hook (Windows, requires pwsh 6+)
│
├── .github/skills/                   # Copilot-discoverable mirrors (CI-synced)
│   ├── lateralus/SKILL.md
│   └── lateralus-brainstorm/SKILL.md
│
└── .github/workflows/
    └── sync-skill.yml                # Syncs skills/ → .github/skills/ on push to main
```

---

## File ownership — edit only these

| I want to change... | Edit this file |
|---|---|
| Core skill behavior (tiers, horizon routing, rules) | `skills/lateralus/SKILL.md` |
| Brainstorming / plan-mode skill | `skills/lateralus-brainstorm/SKILL.md` |
| Scout (interview + audit) | Built into `skills/lateralus/SKILL.md` Step 0 |
| Tier 1 grounded hypotheses | `agents/lateralus-ideator-ground.md` |
| Middle-ground hypotheses | `agents/lateralus-ideator-balanced.md` |
| Tier 3 wild reframes | `agents/lateralus-ideator-wild.md` |
| Makeshift bypass rules | `agents/lateralus-workaround.md` |
| Hook behavior | `hooks/lateralus-hook.py`, `hooks/lateralus-hook.ps1` |
| Install steps | `install.sh`, `install.ps1`, `INSTALL.md` |
| Agent context (this file) | `AGENTS.md` — then CLAUDE.md/GEMINI.md update automatically |

Do NOT edit `.github/skills/` directly — those are CI-synced mirrors.

---

## CI sync workflow

`.github/workflows/sync-skill.yml` triggers on push to `main` when any `skills/**/SKILL.md` changes.

What it does:
1. Copies `skills/lateralus/SKILL.md` → `.github/skills/lateralus/SKILL.md`
2. Copies `skills/lateralus-brainstorm/SKILL.md` → `.github/skills/lateralus-brainstorm/SKILL.md`
3. Commits with `[skip ci]` to avoid loops.

After merging a skill change, wait for the workflow before declaring the release complete.

---

## Skill system

Three skills ship from this repo:

| Skill | File | Purpose |
|---|---|---|
| `lateralus` | `skills/lateralus/SKILL.md` | Full debugging skill — goal context + two-tier ideation |
| `lateralus-brainstorm` | `skills/lateralus-brainstorm/SKILL.md` | Brainstorming / plan mode — Grounded, Balanced, Wild |

Each skill has:
- A `SKILL.md` (LLM-facing prompt body — what the agent loads)
- A `README.md` alongside for humans browsing GitHub

Don't merge them. Different audiences, different formats.

---

## Agent system

Four subagents covering the full lateralus workflow:

| Stage | Agent | Model |
|---|---|---|
| 1. Ground | `lateralus-ideator-ground` | sonnet |
| 2. Balanced | `lateralus-ideator-balanced` | sonnet |
| 3. Wild | `lateralus-ideator-wild` | sonnet |
| 4. Bypass | `lateralus-workaround` | sonnet |

Interrogation (interview + codebase audit) is built into the skill itself as Step 0.

Horizon routing (after Step 0 context block is complete) — user picks from the menu:
- Just unblock / demo → workaround directly
- Long-term / MVP → user picks ground + wild (or agent runs both sequentially)
- POC / test → ideator-ground only
- Time-pressured → ideator-balanced only

---

## Install system

Two plain shell scripts. Both install a `PostToolUse` hook and wire it into `~/.claude/settings.json`.

`install.sh` and `install.ps1`:
- Copy all three skills to `~/.claude/skills/`
- Copy all four agent files to `~/.claude/agents/`
- Copy the hook to `~/.claude/hooks/`
- Wire the hook into `~/.claude/settings.json` (idempotent; backs up `.bak` before writing)
- Respect `CLAUDE_CONFIG_DIR` env var
- Work from curl-pipe or local clone
- Safe to re-run

Hook notes:
- `install.sh` requires Python 3 for JSONC-tolerant settings.json merge
- `install.ps1` requires `pwsh` (PowerShell 6+) for hook wiring; skips gracefully on PS 5.1
- If `settings.json` can't be parsed, wiring is skipped and the file is never modified
- A `.bak` copy is written alongside `settings.json` before any write

---

## Key rules for agents working here

- Edit `skills/<name>/SKILL.md` for behavior changes. Never edit the `.github/skills/` mirrors.
- Edit `agents/<name>.md` for subagent behavior. All agents are single-source at the repo root.
- Edit `AGENTS.md` for maintainer context. `CLAUDE.md` and `GEMINI.md` are stubs — don't edit them.
- Keep skill descriptions keyword-rich — the `description` field is how agents discover when to load the skill.
- Keep SKILL.md under 500 lines. Use reference files if it grows.
- `install.sh` and `install.ps1` are the single source for install logic. Don't add OS-specific logic to one without the other.
- After merging a skill edit, confirm CI synced the `.github/skills/` mirror before marking done.
- README is user-facing. Keep install one-liners accurate. If an install path changes, update README, INSTALL.md, and both install scripts.

---

@./skills/lateralus/SKILL.md
@./skills/lateralus-brainstorm/SKILL.md
@./agents/lateralus-ideator-ground.md
@./agents/lateralus-ideator-balanced.md
@./agents/lateralus-ideator-wild.md
@./agents/lateralus-workaround.md
