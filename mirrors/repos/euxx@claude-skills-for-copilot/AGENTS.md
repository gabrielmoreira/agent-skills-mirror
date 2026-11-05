# Project Conventions

## After Making Changes

After modifying code, run:

- `npm run ci` — syntax + lint + format + tests

See [DEVELOPMENT.md](DEVELOPMENT.md) for all available scripts.

See [RELEASE.md](RELEASE.md) for the release process.

<!-- END-SHARED -->

## Upstream Adaptation Tracking

Active upstream repos:

- **Anthropic**: `https://github.com/anthropics/claude-plugins-official` — local mirror at `~/projects/claude-plugins-official`
- **OpenAI Plugins**: `https://github.com/openai/plugins` — local mirror at `~/projects/openai-plugins`

Legacy source: `https://github.com/openai/skills` (local mirror at `~/projects/skills`) was deprecated on 2026-06-22. Its final checked snapshot is `49f948f`; retain it for attribution and historical comparisons, not as the active OpenAI update source.

Last upstream check: **2026-11-02**

- Anthropic checked up to commit `a7ba5b93`
- OpenAI Plugins initial catalog inventory at commit `0722921d`; this establishes a tracking baseline, not a completed adaptation review of every plugin.

### How to check for updates

1. **Sync local mirrors** — `cd ~/projects/claude-plugins-official && git pull --ff-only` and the same for `~/projects/openai-plugins`. Confirm `git status -sb` shows no drift before comparing.
2. **List commits since last check** — `git log --oneline <last-sha>..HEAD` in each active mirror. Do not compare SHAs across the old OpenAI Skills and new OpenAI Plugins repositories.
3. **Filter to adapted skills** — restrict the log with `-- <paths>` for plugins/folders that map to skills in this repo. Current mapping:
   - `plugins/code-review/` → `code-review`
   - `plugins/claude-md-management/` → `conventions-improver`
   - `plugins/pr-review-toolkit/` → `code-review`, `comment-analyzer`, `silent-failure-hunter`, `test-analyzer`, `type-design-analyzer`, `review-toolkit`
   - `plugins/code-simplifier/` → `code-simplifier`
   - `plugins/feature-dev/` → `feature-dev`
   - `plugins/frontend-design/` → `frontend-design`
   - `plugins/mcp-server-dev/` → `mcp-server-dev`
   - OpenAI mappings and related candidates are listed below. A related candidate is not an automatic replacement for an existing skill.
4. **Inspect each candidate commit** — read the diff (`git show <sha> -- <path>`) and decide whether it touches content we actually carry (our SKILL.md files are often condensed single-file versions, so deep-reference-only changes may be no-ops).
5. **Look for newly added skills** — `git log --diff-filter=A --name-only --pretty=format: <last-sha>..HEAD -- 'plugins/*/skills/*/SKILL.md'` in both active mirrors. Also inspect renames and deletions. Evaluate candidate content, host/tool dependencies, and its own license before adapting; do not infer a successor from a similar name.
6. **Record the new SHAs and date** above after the check completes, regardless of whether any sync was needed.

### OpenAI Source Migration

Verified on 2026-11-02 against OpenAI Plugins `0722921d`:

| Local skill             | Legacy source under `skills/.curated/` | Current tracking status                                                                                                                                                                                                                                                                                                    |
| ----------------------- | -------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `gh-address-comments`   | `gh-address-comments/`                 | No current same-name skill. `plugins/github/skills/gh-address-comments/` was deleted by `33bd9529` on 2026-08-26. Keep the legacy adaptation.                                                                                                                                                                              |
| `gh-fix-ci`             | `gh-fix-ci/`                           | No current same-name skill. `plugins/github/skills/gh-fix-ci/` was deleted by `33bd9529` on 2026-08-26. Keep the legacy adaptation.                                                                                                                                                                                        |
| `security-threat-model` | `security-threat-model/`               | Related candidate: `plugins/codex-security/skills/threat-model/` and `plugins/codex-security/references/`. The entrypoint depends on scan artifact storage, checkpoints, policy, and cache conventions; it is not a drop-in successor.                                                                                     |
| `frontend-layout`       | `frontend-skill/`                      | `plugins/build-web-apps/skills/frontend-skill/` was deleted by `ca0c87f6` on 2026-04-23. Related candidates: `plugins/build-web-apps/skills/frontend-app-builder/` and `plugins/product-design/`. They introduce Image Gen/browser workflows and plugin-specific dependencies; no direct replacement has been established. |

Monitor the related candidate paths for changes. This initial inventory identified the existing skills' status and inspected the related entrypoints; the rest of the new catalog has not yet received a full Copilot-fit review. Keep the legacy skill source links until a replacement is actually adapted, and preserve original license attribution.

### Skills evaluated and skipped

- `session-report` (Anthropic, added 2026-04) — depends on reading `~/.claude/projects` Claude Code transcripts; not portable to VS Code Copilot.
- `cardputer-buddy`, `m5-onboard` (Anthropic `cwc-makers`, added 2026-05) — M5Stack ESP32 hardware provisioning over USB serial / BLE; not applicable to VS Code Copilot.
- `define-goal` (OpenAI, added 2026-05) — depends on Codex `get_goal` / `create_goal` tools that have no Copilot equivalent.
- `hatch-pet` (OpenAI, added 2026-05) — Codex pet sprite-atlas workflow built on the `$imagegen` system skill; not applicable to VS Code Copilot.
- `project-artifact` (Anthropic, added 2026-06) — depends on Claude Code's built-in `Artifact` tool, `claude.ai/code/artifact/...` publishing, and `${CLAUDE_PLUGIN_DATA}` config state; not portable to VS Code Copilot.
- `claude-security` (Anthropic, added 2026-07) — depends on Claude Code's `Workflow`, `Agent`, and `AskUserQuestion` tools plus plugin-relative scripts and multi-agent orchestration; not portable as a standalone VS Code Copilot skill.
- `receipts` (Anthropic, added 2026-07) — mines Claude Code session transcripts under `~/.claude/projects` and reports Claude Code-specific usage; not portable to VS Code Copilot.
- `solo` (Anthropic `math-proof`, added 2026-09) — a pure research-mathematics proof workflow; technically adaptable, but outside this extension's current software-development scope.
- `siege` (Anthropic `math-proof`, added 2026-09) — a long-running mathematics protocol requiring plugin-scoped judge/worker agents, a bundled Python ledger, and Claude Code runtime settings; not suitable for a standalone Copilot skill port.
