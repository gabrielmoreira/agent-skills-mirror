# Distribution — publishing the plugin to every channel

This repo is the SSOT; it fans out to four distribution channels. Every publisher
is **owner-run, dry-run by default, and driven by the repo's committed state** —
no hardcoded queues, no guessing. The single source of truth for "are we fully
distributed?" is `scripts/registry-status.sh`.

> Note: `scripts/build-distribution.py`'s minimal *plugin* profile is the
> ClawHub package source via `publish-package.sh --from-build` — adopted at
> v17.0.0 when the full git archive first exceeded ClawHub's upload limit
> (413). The GitHub-source mode remains the default for as long as it fits.
> The profile's manifest and link-closure are CI-checked.

## Channels

| Channel | What ships | Tool | Cadence |
|---------|-----------|------|---------|
| Downstream repo family (15 repos) | benchmark mirrors + signpost READMEs | [`sync-family.sh`](../scripts/sync-family.sh) | release |
| SkillHub.cn | 120 skills (per-skill, 中文 community) | [`publish-registries.sh`](../scripts/publish-registries.sh) → `publish-skillhub.sh` | release / on-change |
| ClawHub — skills | 120 skills (per-skill, relicensed MIT-0) | [`publish-registries.sh`](../scripts/publish-registries.sh) → `publish-clawhub.sh` | release / on-change |
| ClawHub — bundle-plugin | the whole plugin as one installable package | [`publish-package.sh`](../scripts/publish-package.sh) | release |

`skills.sh` / Hermes / other SKILL.md hosts are **pull-based** (they read `.claude-plugin/plugin.json`); no publish step.

## The one command that tells the truth

```bash
bash scripts/registry-status.sh          # per-skill alignment matrix + package version
bash scripts/registry-status.sh --json   # machine-readable (drives the publisher)
```

Prints, for every manifest skill, `repo` vs `ClawHub` vs `SkillHub` published version, a per-platform current/stale/missing summary, and the bundle-plugin package version. Read-only — it never publishes.

## Release-time distribution (in order)

1. `bash scripts/registry-status.sh` — see what's behind.
2. `bash scripts/publish-registries.sh` → review → `bash scripts/publish-registries.sh --live` — publish **only the behind-set** to both registries.
3. `bash scripts/publish-package.sh` → review → `bash scripts/publish-package.sh --live` — publish the bundle-plugin from the pushed HEAD.
4. `bash scripts/sync-family.sh` → review → `bash scripts/sync-family.sh --live` — sync the downstream repo family.
5. `bash scripts/registry-status.sh` — confirm 120/120 current on both + package current.

## Gotchas (learned the hard way)

- **GitHub source, never the local folder, for the package** — `clawhub package publish .` ignores `.gitignore` and would bundle `.git`, local settings, and any stray `.claude/worktrees/` copy. `publish-package.sh` always publishes `owner/repo@<committed-sha>` (a git-archive of committed files only).
- **The manifest must be committed + pushed** before a package publish — `publish-package.sh` refuses otherwise.
- **SkillHub slug**: unprefixed `<name>` is preferred (when the account owns the short slug), else `aaron-<name>`. `validate-skill.sh` accepts both. Legacy `aaron-<name>` records from before a slug switch may linger as orphans (most registries can't delete).
- **SkillHub search recall**: `registry-status.sh` reads SkillHub via fuzzy search, so it can report a false `missing`. The publisher self-corrects — an idempotent publish of an already-current version returns `版本已存在` and counts as in-sync.
- **ClawHub rate limits**: brand-new skills are ~5/hour; **version updates to existing skills are not capped**. SkillHub throttles bursts (`发布频率过高`) — the publisher spaces 40s and backs off 5 min on 429. Both publishers are resumable.
- **ClawHub MIT-0**: per-skill publishes relicense to MIT-0 (`--i-accept-mit0`), broader than the repo's Apache-2.0.
- Requires the `clawhub` + `skillhub` CLIs logged in on the owner machine. **Never CI-automated** — pushes to public registries get a human glance.

> Historical note: `finish-registry-publish.sh` (removed) hard-coded its publish queue, which silently rotted out of date. `publish-registries.sh` computes the queue from live `registry-status.sh` output instead — the queue can no longer drift.
