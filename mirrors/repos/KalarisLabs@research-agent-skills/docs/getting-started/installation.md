---
title: Install Research Agent Skills
description: Install all 280+ research agent skills, or only the ones you need, in Claude Code, Codex, Cursor, Gemini CLI, Copilot, OpenCode and Windsurf with one skills.sh command, GitHub CLI, the Claude Code marketplace or a checksum-verified shell installer.
---

# Installation

## Install now with skills.sh

```bash
npx skills add KalarisLabs/research-agent-skills
npx skills add KalarisLabs/research-agent-skills --list
```

The first command lets you choose skills and agent harnesses; the second lists all available skills.
The skills.sh CLI installs into the current project by default. Add `--global` for your user account.
It supports Claude Code, Codex, Cursor, Gemini CLI, GitHub Copilot, OpenCode, Windsurf and other
Agent Skills consumers. Tool permissions and advanced metadata can differ by harness.

## Install everything, or only what you need

| Goal | Command |
|---|---|
| Every skill, every detected agent | `npx skills add KalarisLabs/research-agent-skills --all` |
| Specific skills | `npx skills add KalarisLabs/research-agent-skills --skill citation-verification apa7` |
| Every skill for one agent | `npx skills add KalarisLabs/research-agent-skills --skill '*' --agent codex` |
| User-wide instead of this project | add `--global` |
| No prompts (CI, scripts) | add `--yes` |
| Update later | `npx skills update` |

## Curated research bundles

Field bundles install as Claude Code plugins:

```text
/plugin marketplace add KalarisLabs/research-agent-skills
/plugin install biology-research@research-agent-skills
```

Without Claude Code, the checksum-verified standalone installer takes the same bundle names:

```bash
curl -fsSL https://raw.githubusercontent.com/KalarisLabs/research-agent-skills/main/install.sh | RAS_BUNDLE=biology-research sh
```

The curated bundles are `research-essentials`, `ml-research`, `ai-research`, `biology-research`,
`chemistry-research`, `medicine-research` and `physics-research`. Every category is also a bundle
(for example `literature-review`). Use individual skill names when a bundle is too broad.

> **Not on npm.** There is no `research-agent-skills` package on the npm registry. `npx skills` runs the
> open skills.sh CLI, which installs straight from this GitHub repository.

## Alternatives

| Method | Command |
|---|---|
| skills.sh (Vercel) | `npx skills add KalarisLabs/research-agent-skills --list`, then `npx skills add KalarisLabs/research-agent-skills --skill citation-verification` |
| GitHub CLI | `gh skill install KalarisLabs/research-agent-skills [skill]` |
| Claude Code | `/plugin marketplace add KalarisLabs/research-agent-skills` → `/plugin install research-essentials@research-agent-skills` |
| No Node.js (macOS/Linux) | `curl -fsSL https://raw.githubusercontent.com/KalarisLabs/research-agent-skills/main/install.sh \| sh` |
| No Node.js (Windows) | `irm https://raw.githubusercontent.com/KalarisLabs/research-agent-skills/main/install.ps1 \| iex` |

Installer options via environment variables: `RAS_VERSION`, `RAS_BUNDLE` (bundle or category, or `all`), `RAS_HARNESS`.
The standalone installers also default to global user directories. Vercel's skills CLI has its own
scope prompts and flags; review its choice before installing.

## skills.sh discovery

The [collection skill](https://github.com/KalarisLabs/research-agent-skills/blob/main/skills/research-agent-skills/SKILL.md)
indexes all 280 specialist skills. Each specialist remains separately installable.
To install the entire collection into this project for Codex, run:

```sh
npx skills add KalarisLabs/research-agent-skills --skill '*' --agent codex --yes
```

Use another agent name if appropriate, or add `--global` for a user-wide install.

The public repository's `skills/<name>/SKILL.md` folders are discoverable by the Vercel skills CLI.
The directory page lists skills it has seen through CLI installs. The root `skills.sh.json` groups
those entries by audience; it does not submit unseen skills. Run
`npx skills add KalarisLabs/research-agent-skills --list` to verify repository discovery.
[Browse the directory listing](https://skills.sh/kalarislabs/research-agent-skills).
The directory's rankings use the CLI's anonymous install telemetry.

## Python for skill scripts

Skills with a `scripts/` folder run Python 3.9+ (many are standard-library only). For skills with
dependencies, install [uv](https://docs.astral.sh/uv/). `npx skills list` shows what is installed where.
