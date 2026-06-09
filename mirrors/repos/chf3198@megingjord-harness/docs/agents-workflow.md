# Agent Development and Deploy Workflow

> Companion to `AGENTS.md`. Covers the full branch→deploy cycle, Layer-2
> routing, skill index regeneration, and dashboard development conventions.

## Development → deploy cycle

```
1. Ticket    gh issue create --title "..." --label "type:feat,priority:P2"
2. Branch    git checkout -b feat/<N>-slug
3. Worktree  git worktree add ../<repo>-<N> -b feat/<N>-slug  (if parallel work)
4. Edit      Make changes in the feature branch / worktree
5. Verify    npm run lint && npm test && npm run validate:triage
6. Baton     Post MANAGER_HANDOFF on issue; implement; post remaining artifacts
7. PR        gh pr create --title "feat(scope): description #<N>"
8. Merge     CI gates pass → GraphQL mergePullRequest (squash method)
9. Deploy    npm run deploy:apply  (and/or :codex / :both)
10. Verify   Confirm skill/script in runtime; run behaviour test
```

## Deploy commands

| Command                       | Effect                           |
| ----------------------------- | -------------------------------- |
| `npm run deploy:apply`        | Repo → `~/.copilot/`             |
| `npm run deploy:codex:apply`  | Repo → `~/.codex/`               |
| `npm run deploy:claude:apply` | Repo → `~/.claude/`              |
| `npm run deploy:both:apply`   | Repo → Copilot + Codex           |
| `npm run sync`                | `~/.copilot/` → repo (pull back) |
| `npm run sync:codex`          | `~/.codex/` → repo (pull back)   |
| `npm run sync:claude`         | `~/.claude/` → repo (pull back)  |

## Layer-2 routing

Two coordination backends; selected by `MEGINGJORD_HAMR_ENABLED`:

| Value       | Backend                             | Auth needed                          |
| ----------- | ----------------------------------- | ------------------------------------ |
| unset / `0` | GitHub-native (zero infra required) | GitHub token only                    |
| `1`         | HAMR Cloudflare Worker              | Cloudflare + `OPERATOR_KEY_SEED_B64` |

GitHub-native unified client: `scripts/global/github-native-client.js`

HAMR activation:

```bash
npm run hamr:activate        # writes HAMR config to local runtime
npm run hamr:sync-verify     # confirms routing through Worker
```

## Skill index

Auto-derived from `skills/<name>/SKILL.md` descriptors.
View: [`docs/skills-agents.md`](../docs/skills-agents.md)

Regenerate after adding or modifying any skill:

```bash
node scripts/global/skill-views-derive.js
```

## Dashboard conventions

The monitoring dashboard at `:8090` is a zero-build-step static web app:

- **Alpine.js** for reactive state; **vanilla JS** for all logic
- No build step; no bundler; all assets served as static files from `dashboard/`
- Panels declared as `<template>` elements in `dashboard/index.html`
- Pure render functions in `dashboard/js/render-panels.js`
- **Cloudflare Pages** for production deployment

When modifying the dashboard:

1. Test locally with `npm start` → `http://localhost:8090`
2. Verify SSE events appear in the event panel
3. Run `npm test` to validate E2E panel rendering

## Fleet auto-detection

Fleet topology auto-detected at runtime:

- `scripts/global/fleet-config.js` reads `inventory/devices.json`
- IPs resolve from `.env` overrides first, then Tailscale DNS discovery
- `scripts/health-check.js` pings all hosts; writes `.dashboard/state/fleet-health.json`

## Worktree cleanup

After a PR merges, clean up the worktree:

```bash
git worktree remove ../<repo>-<N>       # remove worktree directory
git branch -d feat/<N>-slug              # delete local branch
git push origin --delete feat/<N>-slug  # delete remote branch
```

See `research/concurrent-agent-worktrees-2026-04-24.md` for the full safety
contract including conflict quarantine and rescue procedures.
