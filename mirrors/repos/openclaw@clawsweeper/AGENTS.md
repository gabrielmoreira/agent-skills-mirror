# AGENTS.MD

ClawSweeper is the conservative maintenance bot for `openclaw/openclaw`.
Keep changes narrow, evidence-backed, and automation-safe.

## Structure

- Main code: `src/clawsweeper.ts`.
- Tests: `test/clawsweeper.test.mjs`.
- Workflow: `.github/workflows/sweep.yml`.
- Dashboard and explainer: `README.md`.
- Open/reviewed records: flat `items/<number>.md`.
- Archived records: flat `closed/<number>.md`.
- Scratch/generated output: `.artifacts/`, `artifacts/`, `apply-report.json`.

Preserve the flat `items/` and `closed/` report layout. Do not split reports into
issue/PR subtrees.

## Operating Model

- Review lane is proposal-only. It never closes GitHub items.
- Apply lane mutates GitHub by syncing the durable Codex review comment and then
  closing only unchanged, high-confidence proposals.
- Worker concurrency is shard-level: each shard processes its selected items
  sequentially. Maximum parallel Codex sessions equals `shard_count`, not
  `batch_size * shard_count`.
- The README dashboard is the live status surface. Check current Actions and the
  remote README before trusting local dashboard timestamps.

## Safety Rules

- Do not run live apply/close commands unless Peter explicitly asks.
- For apply-path repros, copy one report into a temp `items/` dir and pass
  `--skip-dashboard`, `--item-number`, and a temp `--closed-dir`.
- Treat maintainer-authored and protected-label items as non-closeable.
- Snapshot or `updated_at` drift blocks apply unless the only change is the
  existing ClawSweeper review comment.
- Open-but-locked issues can exist when stale automation locked a closed issue
  and the author later reopened it. These must be skipped, not allowed to crash
  the apply run.
- Locked-comment 403s from GitHub are terminal apply skips, not retryable API
  failures.

## Commands

```bash
npm install
npm run build
npm run test:unit
npm run format
npm run check
```

Use `npm run check` before handoff for code/test/workflow changes.

## GitHub Checks

Useful live probes:

```bash
gh run list --repo openclaw/clawsweeper --limit 20 --json databaseId,displayTitle,status,conclusion,createdAt,updatedAt
gh api repos/openclaw/clawsweeper/readme --jq '.content' | base64 --decode
gh api graphql -f query='query { repository(owner:"openclaw", name:"openclaw") { issues(states: OPEN) { totalCount } pullRequests(states: OPEN) { totalCount } } }'
```

For throughput/default tuning, inspect and update both `src/clawsweeper.ts` and
`.github/workflows/sweep.yml`; continuation paths can otherwise keep stale
defaults.
