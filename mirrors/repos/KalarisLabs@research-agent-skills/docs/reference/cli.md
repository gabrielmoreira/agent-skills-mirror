---
title: Installer CLI reference | Research Agent Skills
description: Reference for the research-agent-skills installer CLI (built from source; not on npm), covering install, list, search, update, uninstall and doctor.
---

> **Not on npm.** To install skills, use skills.sh: `npx skills add KalarisLabs/research-agent-skills`
> ([installation guide](/getting-started/installation)). This page documents the optional installer in `cli/`,
> which you can build from source with `cd cli && npm ci && npm run build`, then run as `node dist/bin.js`.

The `research-agent-skills` CLI installs skills from a verified release into supported agent directories.
The examples use `npx research-agent-skills`; when running from source, substitute `node cli/dist/bin.js`.

| Command | Purpose |
|---|---|
| `install [skill...]` | Install named skills, a bundle, or a category |
| `list --categories` | Show available categories |
| `search <query>` | Find skills by name, description or tags |
| `installed` | Show installed skills and target directories |
| `update` | Reinstall managed skills from the selected release |
| `uninstall [skill...]` | Remove managed skills |
| `doctor` | Check harnesses, dependencies and installed file integrity |

Without selection flags, `install` chooses `research-essentials`. Without `--project`, installation goes
to the selected agent's global user directory. Use `--harness codex` (or a comma-separated list) to target
specific agents. Use `--dry-run` to inspect changes before installing.

```bash
npx research-agent-skills install --bundle ai-research --harness codex --project
npx research-agent-skills install citation-verification --dry-run
```

See the [full CLI README](https://github.com/KalarisLabs/research-agent-skills/blob/main/cli/README.md)
for release and standalone installer details.
