---
name: update-plugins
description: "Safely update Copilot CLI plugins by wrapping `copilot plugin update` with per-plugin change summaries and breaking-change warnings. Reads each plugin's CHANGELOG between the installed version and the latest available version, extracts any Breaking sections, and presents them before running the update. Consent-gated. Idempotent — reports 'everything current' when nothing to update. Works for any installed plugin; adds extra CHANGELOG-reading logic for Alex ACT constellation plugins. Delegates to `plugin-management` for the raw commands."
lastReviewed: 2026-07-30
---

# Update Plugins

Wrap `copilot plugin update` with the diff-summary + consent-gate discipline every plugin update deserves. Copilot CLI does not auto-update plugins; this skill is how "always the latest stable version" is operationalized.

## When to fire

- Heir asks "update my plugins" / "keep plugins current" / "latest constellation"
- Heir invokes `/alex-act-manager update-plugins`
- Session-start reminder from `install-constellation` when it detects an existing install with available updates
- Auditing "what would update" without committing (audit mode)

## What the skill does

For each installed plugin, in order:

1. Read installed versions from `copilot plugin list`; use each installed `plugin.json` as the filesystem fallback.
2. Query the latest available stable version from the plugin's marketplace or GitHub source.
3. If installed == latest, skip.
4. If installed < latest, read the plugin's CHANGELOG.md between the two versions.
5. Extract any `### Breaking` / `### Removed` / `### Changed - breaking` sections.
6. Add a row to the diff summary.
7. After processing every plugin, present the full diff summary and ask for consent to proceed.
8. On consent, run `copilot plugin update <name>` for each plugin the heir approved.
9. Re-verify installed versions after update.
10. Report what changed.

## Mall catalog fetch (reusable helper)

Exposed for the `greeting-checkin` instruction (added 2026-08-01) to run its silent update-availability check on session greetings. Also used internally by this skill for the pre-update version diff.

**Endpoint**: `https://raw.githubusercontent.com/fabioc-aloha/Alex_Skill_Mall/main/catalog/index.json` (approximately 2 MB, refreshed weekly by the Mall's cron per ADR-008).

**Fetch pattern**:

```powershell
# PowerShell example — the actual invocation delegates to the LLM tool of choice (web_fetch, curl, etc.)
$catalog = Invoke-WebRequest -Uri "https://raw.githubusercontent.com/fabioc-aloha/Alex_Skill_Mall/main/catalog/index.json" -TimeoutSec 5 | Select-Object -ExpandProperty Content | ConvertFrom-Json
```

**Parse pattern**: the catalog's top-level structure is `{ "schema_version": ..., "plugin_count": ..., "plugins": [...] }`. Each `plugins[]` entry carries `{ name, store, version, ... }`. Look up the entry for each installed constellation plugin by name; the catalog's `version` field is the current latest.

**Timeout**: 5 seconds. If the fetch fails (network error, timeout, non-2xx response), treat as "no update info available" and skip the update-diff step entirely. Do NOT tell the user "couldn't check updates" — that's noise for a check they never asked for.

**Caching**: for the `greeting-checkin` use case, cache the result via the session-state hint file (see `plugin-management` skill § Session-state hint file). One fetch per hour per session tops.

**Fallback**: for the interactive `/alex-act-manager update-plugins` case, if the catalog fetch
fails, use the plugin's GitHub Releases page or source repository when known.
If no verified source is available, mark latest version as unavailable and stop
before offering an update. Copilot CLI 1.0.77 has no per-plugin `info` command.

## Version resolution

"Latest stable" means the highest release tag on the plugin's repo default branch that is:

- A GitHub Release (not just a git tag)
- Not marked prerelease
- Not marked draft
- Present in the registered marketplace catalog or the plugin's verified GitHub Releases feed

Prerelease tags (`v1.2.0-rc.1`, `v1.2.0-beta`) do not qualify. This skill does not opt into prereleases. If a heir explicitly asks to test a prerelease, do it manually via `copilot plugin install <name>@<marketplace>` with the specific version tag; this skill does not automate that path.

## CHANGELOG reading

For each constellation plugin (`alex-act-core`, `alex-act-illustrator-plugin`, `alex-act-enterprise`, `alex-act-msft`), fetch the CHANGELOG.md from the plugin's GitHub repo default branch. Parse in Keep-a-Changelog format:

```
## [Unreleased]
### Added
### Changed
### Breaking
### Removed

## [X.Y.Z] - YYYY-MM-DD
### Added
### Breaking
...
```

Between installed and latest, aggregate all `### Breaking` and `### Removed` bullets. If any exist, mark the plugin as "breaking-change-pending" in the diff summary.

For third-party plugins (Microsoft ecosystem, community), CHANGELOG format varies. Best-effort: try `CHANGELOG.md`, `CHANGES.md`, `RELEASES.md`, or the GitHub Releases API. If no CHANGELOG can be read, mark the plugin's row as "changelog unavailable — review manually before update".

## Diff summary format

Before running any update, present:

| Plugin | Installed | Latest | Breaking? | Summary |
|---|---|---|---|---|
| `alex-act-core` | 0.1.0 | 0.2.0 | No | Added 3 skills, 2 instructions per Batch 11 |
| `alex-act-illustrator-plugin` | 0.6.0 | 0.6.0 | — | Current — skip |
| `alex-act-enterprise` | 0.1.0 | 0.2.0 | **Yes** | setup-enterprise-stack now defaults to repo scope (was user); heir workflow may need `--user` flag |
| `azure@azure-skills` | 1.4.2 | 1.5.0 | No | Added Fabric-side integration + M365 tooling |
| ... | | | | |

Breaking-change plugins are highlighted. Ask the heir to confirm before proceeding, and offer to defer any specific plugin ("skip Enterprise this round, update the others").

## Consent flow

### Mode 1 — Audit only (default when not sure)

Print the diff summary and stop. No CLI writes, no filesystem changes. Report:

- N plugins current, no update needed
- M plugins have updates available
- K plugins have breaking changes worth reviewing
- Next step: run `/alex-act-manager update-plugins` again with an explicit mode choice

### Mode 2 — Update non-breaking only

Update every plugin where `Breaking? == No` in the diff summary. Skip breaking-change plugins and report them for manual review. Safe for regular scheduled updates.

### Mode 3 — Update all (with per-breaking consent)

For each breaking-change plugin, ask individually: "Update `<plugin>` from `<installed>` to `<latest>`? Breaking changes: <bullet list>. Reply yes / no / skip". Then update every yes plus every non-breaking. Report skipped plugins.

Default to Mode 1 if the heir does not specify. Never run Mode 3 without individual per-plugin consent for the breaking-change ones.

## Update commands

Delegate to [`plugin-management`](../plugin-management/SKILL.md) for the raw commands. Common patterns:

```powershell
# Update one plugin
copilot plugin update alex-act-core

# Update every installed plugin (dangerous — no per-plugin consent)
copilot plugin update --all

# After update, re-verify
copilot plugin list
```

This skill's Mode 3 always uses per-plugin `update <name>` rather than `update --all` — the `--all` flag bypasses the per-breaking consent step.

## Idempotency

Safe to re-run at any time:

- All current → report "everything current — no updates available today" and exit.
- Some available → run the standard flow.
- Failed previous run → detect the specific plugin(s) that failed and offer to retry only those.

The skill maintains no state file. Every invocation queries live state.

## Session-start reminder pattern

If `install-constellation` detects the constellation is installed but has updates available, it can print a one-line hint:

> "Constellation plugins have updates available: 3 non-breaking, 1 breaking. Run `/alex-act-manager update-plugins` for the diff summary."

The hint is read-only — it does not itself update anything. The heir invokes this skill (or `/alex-act-manager update-plugins`) to see the details.

## Safety rules

- **Never** run `copilot plugin update --all` without the per-plugin diff summary.
- **Never** update a breaking-change plugin without individual per-plugin consent.
- **Never** update a plugin whose CHANGELOG cannot be read without warning the heir "no changelog — cannot preview changes; proceed anyway?"
- **Never** update on a machine off the corporate network for `alex-act-msft` — its update fetch may work, but the update might change WorkIQ endpoint expectations that need network to verify. Fail closed on off-network updates for internal-only plugins.
- **Do** re-verify installed version after each update. If the reported version does not match the expected latest, report the discrepancy and stop.
- **Do** offer rollback only when the prior source is verified and supported by the current `copilot plugin install --help`. Copilot CLI 1.0.77 has no marketplace version-pin syntax; never invent one.

## Anti-patterns

| Anti-pattern | Correction |
|---|---|
| Run `copilot plugin update --all` and report "done" | Diff summary + per-breaking consent first |
| Skip CHANGELOG reading for constellation plugins | Constellation CHANGELOGs are the canonical source of what changed; always read them |
| Silently skip a plugin because its CHANGELOG can't be read | Tell the heir; offer to proceed without preview |
| Update breaking-change plugins by default | Default to non-breaking-only; ask per-plugin for breaking |
| Report success without re-verifying installed version | Verify — post-update version must match expected latest |
| Ignore off-network state for internal-only plugins | Fail closed for `alex-act-msft` when off-network |

## Composes with

- [`plugin-management`](../plugin-management/SKILL.md) — this skill's dependency for the raw commands + safety rules
- [`install-constellation`](../install-constellation/SKILL.md) — the sibling that installs; this one keeps them current
- `no-deferred-debt` (Batch 4 instruction) — plugin updates that surface stale content are fixed in the same session
- `problem-framing-audit` (Batch 1) — before running Mode 3 on a heir's system, frame-check whether the heir actually wants breaking-change updates or would prefer to hold

## Falsifiability

Sunset or revise this skill by **2027-01-30** (6 months) if:

- Copilot CLI adds a plugin auto-update mechanism (`plugins.autoUpdate` setting or similar) — the manual-update premise collapses.
- The Keep-a-Changelog format falls out of use across the constellation plugins — CHANGELOG parsing fails; must switch to another source (GitHub Releases API).
- ≥3 heirs report a plugin update introduced a regression this skill's diff summary should have caught but did not — the CHANGELOG reading is missing something.
- The per-breaking consent flow proves too noisy (heirs report update fatigue and start skipping legitimate updates) — the noise threshold needs tightening.

Track outcomes in the maintaining repo's curation log.

## Related

- `/update-plugins` — slash-command entry point
- [`plugin-management`](../plugin-management/SKILL.md) — general Copilot CLI plugin operations
- [`install-constellation`](../install-constellation/SKILL.md) — install-time sibling
- `constellation/PLUGIN-INTEGRATION.md` § 3 in Steward — the update model that grounds this skill
