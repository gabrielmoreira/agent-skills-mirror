# Development Environment Setup

## Prerequisites

| Tool              | Minimum version | Purpose                                               |
| ----------------- | --------------- | ----------------------------------------------------- |
| Node.js           | 18              | All scripts; `nvm` recommended for version management |
| Git               | 2.35            | Worktree support required for concurrent agents       |
| GitHub CLI (`gh`) | 2.x             | Issue, PR, and CI management                          |
| Tailscale         | any             | Fleet routing to Ollama hosts (optional)              |

## Install and verify

```bash
git clone https://github.com/chf3198/megingjord-harness.git
cd megingjord-harness
npm install

# Verify all baseline checks pass before making any changes
npm run lint            # ≤100-line file limit
npm test                # Playwright E2E + unit tests
npm run validate:triage # Skill triage JSON sync
npm run validate:compat # Plugin.json compatibility
```

## Key commands

| Command                      | Purpose                               |
| ---------------------------- | ------------------------------------- |
| `npm start`                  | Dashboard on `:8090`                  |
| `npm run lint`               | 100-line file limit check             |
| `npm run format:check`       | Prettier check (read-only, no writes) |
| `npm run format`             | Prettier write (auto-fix)             |
| `npm test`                   | Full E2E + unit test suite            |
| `npm run validate:triage`    | Skill triage JSON sync check          |
| `npm run validate:compat`    | `plugin.json` compatibility check     |
| `npm run sync`               | Pull Copilot runtime → repo           |
| `npm run sync:codex`         | Pull Codex runtime → repo             |
| `npm run deploy:apply`       | Deploy repo → Copilot runtime         |
| `npm run deploy:codex:apply` | Deploy repo → Codex runtime           |
| `npm run deploy:both:apply`  | Deploy repo → Copilot + Codex         |

## Code style

- **Formatter**: Prettier (config in `.prettierrc`) — run before every commit
- **Module system**: CommonJS (`require` / `module.exports`); no ESM; no build step
- **File cap**: ≤100 lines per file; split with a linked companion file if needed
- **Naming**: `camelCase` for JS identifiers; `kebab-case` for filenames; `UPPER_SNAKE` for env vars
- **Constants**: name magic numbers at the top of the file; no inline literals

## Environment variables

Copy `.env.example` → `.env` and populate as needed:

| Variable                   | Purpose                                              |
| -------------------------- | ---------------------------------------------------- |
| `GOOGLE_AI_STUDIO_API_KEY` | Free-cloud dispatch via Gemini                       |
| `MEGINGJORD_HAMR_ENABLED`  | Set to `1` to use HAMR Cloudflare Worker for Layer-2 |
| `OPERATOR_KEY_SEED_B64`    | 32-byte base64 seed for stable HAMR mailbox auth     |

Check `scripts/global/credential-availability.js` before prompting for any secret —
the value may already exist in `.env` or another approved hydration source.

## Worktree discipline (concurrent session safety)

Each agent or parallel task requires its own Git worktree and branch:

```bash
git worktree add ../<repo>-<issue> -b feat/<issue>-slug
# work in the worktree
git worktree remove ../<repo>-<issue>   # clean up after merge
```

See [`research/concurrent-agent-worktrees-2026-04-24.md`](../research/concurrent-agent-worktrees-2026-04-24.md)
for the full safety contract, conflict quarantine procedure, and rescue steps.

## Testing changes in a target runtime

1. Deploy to the target runtime: `npm run deploy:apply`
2. Open VS Code and exercise the changed skill or instruction
3. Verify behaviour matches `SKILL.md § Verification`
4. Pull changes back if needed: `npm run sync`

## settings.json drift

Copilot permission approvals append to `.claude/settings.json` automatically.
Commit these via a `chore:` commit with ticket reference before branching on
them. See note in `CONTRIBUTING.md § Constraints` and issue #506.
