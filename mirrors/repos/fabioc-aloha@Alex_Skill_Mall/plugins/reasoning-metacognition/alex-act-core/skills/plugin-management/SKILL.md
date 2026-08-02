---
name: plugin-management
description: "General Copilot CLI plugin operations: install / list / update / remove / marketplace add + remove, scope precedence (user vs repo), the enabledPlugins + extraKnownMarketplaces settings shape, and safe merge-not-overwrite settings edits. Use when a heir asks to install / update / remove any plugin from any Mall, or when auditing what plugins are installed at what scope. Generic — the install-constellation and update-plugins skills delegate to this one for the mechanical commands."
lastReviewed: 2026-08-01
---

# Plugin Management

General Copilot CLI plugin operations skill. Every install / list / update / remove / marketplace-manage action routes through here; specialized skills (`install-constellation`, `update-plugins`) delegate to this one for the mechanical commands and safety rules.

## When to fire

- Heir asks "install X plugin" / "add Y plugin from Z mall"
- Heir asks "list my plugins" / "what plugins do I have installed"
- Heir asks "update X plugin" / "keep X current" (delegate to `update-plugins` for the diff / breaking-change flow; use this skill for the raw update commands)
- Heir asks "remove X plugin" / "uninstall Y"
- Heir asks about a marketplace: "add the Alex mall" / "register a new plugin source"
- Heir invokes `/plugin-status` (audit mode)
- Auditing whether a plugin is at user scope vs repo scope

## Command reference

Every command below is a `copilot plugin ...` subcommand. Ordered by frequency of use.

| Command | Purpose | Example |
|---|---|---|
| `list` | Show currently installed plugins with versions and marketplaces | `copilot plugin list` |
| `install <name>@<marketplace>` | Install a plugin from a registered marketplace | `copilot plugin install alex-act-core@alex-mall` |
| `install <owner>/<repo>` | Direct install from GitHub (no marketplace) | `copilot plugin install fabioc-aloha/org-report` |
| `update <name>` | Update one plugin to its latest stable version | `copilot plugin update alex-act-core` |
| `update --all` | Update every installed plugin | `copilot plugin update --all` |
| `uninstall <name>` | Uninstall a plugin (removes files + drops marketplace entries from `enabledPlugins`) | `copilot plugin uninstall alex-act-msft` |
| `marketplace add <owner>/<repo>` | Register a marketplace so `<plugin>@<marketplace>` resolves | `copilot plugin marketplace add fabioc-aloha/Alex_Skill_Mall` |
| `marketplace list` | Show registered marketplaces | `copilot plugin marketplace list` |
| `marketplace browse <name>` | List plugins published by a registered marketplace | `copilot plugin marketplace browse alex-mall` |
| `marketplace remove <name>` | Deregister a marketplace | `copilot plugin marketplace remove alex-mall` |

Copilot CLI 1.0.77 has no `info`, `remove`, or `search` plugin subcommands. Use
`list` for installed versions and status, `marketplace browse` for discovery,
and `uninstall` for removal. When `list` is insufficient, read the installed
plugin's `plugin.json` as a filesystem fallback:

- Marketplace install: `~/.copilot/installed-plugins/<marketplace>/<plugin>/plugin.json`
- Direct install: find the plugin under `~/.copilot/installed-plugins/_direct/`

## Scope precedence

Copilot CLI reads settings from two locations. Both can define `enabledPlugins` and `extraKnownMarketplaces`; the CLI merges them and applies precedence per the [official spec](https://docs.github.com/copilot/reference/copilot-cli-reference).

| File | Scope | Committed to git? | Cloud agent sees it? |
|---|---|---|---|
| `~/.copilot/settings.json` | User (every workspace on this machine) | No — user's home | No |
| `.github/copilot/settings.json` | Repo (only this workspace) | Yes — belongs in source control | Yes — Copilot cloud agent reads it |

When the same plugin appears in both files, **repo wins** — a project can override user-scope defaults for its own workspace. That is the intended behavior: user scope declares "who the heir is", repo scope declares "what this project needs".

Skill precedence within a workspace (first-loaded wins, dedup by skill name):

1. `<workspace>/.github/skills/` (highest priority)
2. `<workspace>/.agents/skills/`
3. `<workspace>/.claude/skills/`
4. Inherited `.github/skills/` from parent repos (monorepo)
5. `~/.copilot/skills/` (user personal)
6. `~/.agents/skills/`
7. **Plugin `skills/` directories** (any installed plugin)
8. `COPILOT_SKILLS_DIRS` env + config

Plugin-shipped skills sit at position 7 — a heir's workspace or personal skill of the same name silently defeats the plugin's. This is intentional (heirs can override) but easy to trip over during debugging.

MCP servers use **last-loaded-wins** (opposite direction) by server name: user-scope → plugin → command-line flag. Register with a namespace-prefixed server name to avoid collision.

## Settings shape

The two files share a schema. Minimal example (`.github/copilot/settings.json`):

```json
{
  "extraKnownMarketplaces": {
    "alex-mall": {
      "source": { "source": "github", "repo": "fabioc-aloha/Alex_Skill_Mall" }
    }
  },
  "enabledPlugins": {
    "alex-act-core@alex-mall": true,
    "alex-act-illustrator-plugin@alex-mall": true
  }
}
```

Key shape rules:

- `enabledPlugins` is a map from `<plugin>@<marketplace>` to `true` / `false`. Setting a plugin to `false` disables it without uninstalling.
- `extraKnownMarketplaces` is a map from marketplace nickname to `{ source: { source: "github", repo: "<owner>/<repo>" } }`. The two default marketplaces (`copilot-plugins`, `awesome-copilot`) do not need registration.
- Direct-installed plugins (from `<owner>/<repo>` with no marketplace) live in `~/.copilot/installed-plugins/_direct/<source-id>/`. On Copilot CLI 1.0.77, install does not add an `enabledPlugins` entry. After explicit consent, merge the plugin's bare manifest name (for example, `"alex-act-msft": true`) into user settings, then verify settings, `plugin list`, and the direct-install tree.

## Safe settings edits

**Never overwrite `~/.copilot/settings.json` or `.github/copilot/settings.json` without explicit consent.** Every edit must merge — preserve existing keys, add or update only what the user requested. If the target has an unrelated `enabledPlugins` entry, keep it.

Standard merge algorithm:

1. Read the current file. If it does not exist, start from `{}`.
2. Deep-merge the desired changes into the current object. For maps (`enabledPlugins`, `extraKnownMarketplaces`), add or update keys — do not replace the whole map.
3. Preserve top-level keys the user has that we do not touch.
4. Write the result back with 2-space indentation and a trailing newline.

If the file is malformed JSON, stop and report the parse error — do not attempt to "clean it up" without consent.

## Install modes (three)

Whenever the heir asks to install a plugin, ask which mode. Default to (1).

### 1. Emit only (safest)

Print the settings block the heir needs to paste, plus any `copilot plugin install` commands they should run. Do not touch the filesystem. Do not run CLI commands.

Use when: the heir wants a preview, or is off-network, or wants to review before applying.

### 2. Consent-gated apply

Only after explicit "yes, apply it" from the heir:

1. Merge the target block into the destination `settings.json` (user or repo scope, per the heir's choice or the caller's default).
2. Run `copilot plugin install` for each newly-enabled plugin.
3. Run `copilot plugin marketplace add` for any new marketplace.
4. Report what was added and what pre-existing entries were preserved.

Use when: the heir has reviewed and approved the target state.

### 3. Audit only

Read the current state via `copilot plugin list` + both settings files. Compare against the target. Produce a table with columns: **Plugin**, **Currently enabled?**, **Currently installed?**, **Marketplace registered?**, **Action needed**. Do not modify anything.

Use when: the heir wants to know the delta before choosing (1) or (2).

## Scope decision — when to use user vs repo

Copilot CLI does not decide for you. The heuristic per `constellation/PLUGIN-INTEGRATION.md` § 2:

> **"Am I this?" → user scope. "Am I working on this?" → repo scope.**

Concrete calls:

| Plugin type | Default scope | Reasoning |
|---|---|---|
| Alex ACT constellation (Core, Illustrator, Enterprise, MSFT) | **User** | Identity-scoped; the heir wants these in every workspace |
| Microsoft ecosystem plugins (azure, fabric-*, powerbi-authoring, m365-agents-toolkit) | **Repo** | Project-specific; only Azure workspaces need Azure skills loaded |
| Microsoft-internal signal plugins (workiq, workiq-productivity, org-report) | **User** | Heir-scoped signals; apply across every internal workspace |
| Domain-specific tooling (any Fabric / Azure / Power BI / GraphQL / language-specific plugin) | **Repo** | Same rule as Microsoft ecosystem — project-specific tools |
| Personal preference plugins (spellcheckers, style enforcers) | **User** | Heir preference, not project policy |

If a heir is unsure, ask: "Is this plugin about you or about this project?"

## Instruction bootstrap files (user scope)

Plugins deliver skills, prompts, and agents. They do **not** deliver instructions: `plugin.json` has no `instructions` component field, and the CLI's loading-order model covers only agents, skills, and MCP servers. Claude Code and the Open Plugin Spec draw the same boundary, so treat it as architecture rather than a bug.

The workaround is to copy instruction files into `~/.copilot/instructions/`, which the Copilot CLI and VS Code Chat both read at user scope. `install-constellation` § Step 6 does this for Core's seventeen load-bearing always-on files. This section owns the shared rules any plugin bootstrap must follow.

### Rules

1. **Prefix every written file** with the owning plugin's name, for example `alex-act-act-pass.instructions.md`. The folder is shared with the heir's own instructions; an unprefixed write can clobber their work.
2. **Write a receipt** at `~/.copilot/instructions/.<plugin-name>-bootstrap.json` listing `files`, the source plugin, its version, and a timestamp.
3. **Never glob-delete.** Removal reads the receipt and deletes only the files it names.
4. **Scan for overlap first.** Instruction scopes compose rather than replace. If the current workspace's `.github/instructions/` already defines a same-named rule, both copies load and both cost tokens. Report the overlap and let the heir decide.
5. **Consent separately from install.** User scope reaches every workspace on the machine, which is a broader blast radius than a plugin install. It gets its own yes.

### Reading a receipt

```powershell
$r = "$env:USERPROFILE\.copilot\instructions\.alex-act-bootstrap.json"
if (Test-Path $r) { (Get-Content $r -Raw | ConvertFrom-Json) } else { "no bootstrap receipt" }
```

### Removing a bootstrap

```powershell
$dir = "$env:USERPROFILE\.copilot\instructions"
$r = Join-Path $dir ".alex-act-bootstrap.json"
$m = Get-Content $r -Raw | ConvertFrom-Json
foreach ($f in $m.files) { Remove-Item (Join-Path $dir $f) -Force -ErrorAction SilentlyContinue }
Remove-Item $r -Force
```

Confirm with the heir before running it, then verify from a directory with no `.github/`:

```powershell
copilot -p "Do you have an instruction named act-pass available in this session? One sentence."
```

A "no" means the removal took. Running that check inside a workspace that has its own brain proves nothing, because a repo-scope file can answer.

## Session-state hint file

Added 2026-08-01 to support the `greeting-checkin` instruction's proactive session-start orientation. Not a bootstrap file — it lives in the same folder for co-location convenience but is not managed by the bootstrap receipt.

**Location**: `~/.copilot/instructions/.alex-act-session-hint.json`

**Purpose**: cache the last constellation health-check result so the `greeting-checkin` instruction can avoid nagging within a session (60-minute cache window). Also records the last-known state classification so subsequent greetings can use the cached verdict without re-running the full check.

**Schema**:

```json
{
  "lastCheckAt": "2026-08-01T14:23:00Z",
  "state": "healthy",
  "installedCoreVersion": "0.3.1",
  "installedPlugins": [
    "alex-act-core@alex-mall",
    "alex-act-illustrator-plugin@alex-mall"
  ],
  "updatesAvailable": [
    { "plugin": "alex-act-illustrator-plugin", "installed": "0.6.0", "latest": "0.6.1" }
  ]
}
```

**Field semantics**:

| Field | Meaning |
|---|---|
| `lastCheckAt` | ISO 8601 UTC timestamp of last full state check. If read + within 60 min of current time, treat as cache hit — skip the check. |
| `state` | One of `healthy` \| `incomplete` \| `drifted` \| `updates-available`. Highest-severity classification wins if multiple apply. |
| `installedCoreVersion` | Version from `copilot plugin list`, with the installed `plugin.json` as fallback. Used to detect drift on subsequent checks. |
| `installedPlugins` | Array of `<plugin>@<marketplace>` identifiers currently in `enabledPlugins`. |
| `updatesAvailable` | Array of pending updates. Empty when healthy. |

**Write pattern**: atomic — write to `.tmp` sibling then rename. This prevents partial reads when the check-in fires mid-write on a slow disk.

**Not touched by uninstall.** The `uninstall-constellation` skill removes the bootstrap receipt (`.alex-act-bootstrap.json`) as part of its sweep, but leaves the hint file. Reason: after uninstall, on next greeting the hint file's stale `installedCoreVersion` triggers a re-check that correctly classifies state as `incomplete` and offers reinstall. Removing the hint file would leave no evidence for that discrimination.

## Safety rules

- **Emit before apply.** Print the target settings block and the exact command list *before* running anything. Filesystem writes and CLI invocations happen only after explicit heir consent. Applying first and reporting after is a P0 violation, not a shortcut.
- **Never** overwrite a settings file without explicit consent.
- **Never** disable a plugin the heir did not ask to disable — merge, don't replace.
- **Never** silently install a plugin without naming it in the consent prompt.
- **Never** write into `~/.copilot/instructions/` without the owning plugin's name as a filename prefix and a matching receipt.
- **Never** remove bootstrap files by globbing the folder — read the receipt.
- **Never** modify `.github/copilot/settings.json` in a heir's workspace without also telling them the file gets committed (it belongs in source control; teammates will pull the change).
- **Do** verify the CLI version (`copilot --version` >= 1.0.75) before offering any install / update / marketplace command that depends on newer syntax.
- **Do** run `copilot plugin list` before install operations to detect duplicates (installing the same plugin from two marketplaces).
- **Do** verify that a plugin actually exists in its claimed marketplace before running `copilot plugin install` — especially when the plugin name came from an external agent (LLM, sub-agent, another AI, or an untrusted doc). Use `copilot plugin marketplace browse <marketplace>` and grep for the plugin name. Cheap check; catches CLI-authored install commands pointing at hallucinated plugins. Same anti-hallucination discipline as verifying CLI command syntax before running.
- **Do** warn if the heir is off-network when installing a plugin whose skills require network at invocation time (WorkIQ, `azure`, etc.).

## Anti-patterns

| Anti-pattern | Correction |
|---|---|
| Install without consent | Emit is always safe; install is always gated. |
| Overwrite `settings.json` instead of merging | Merge, preserve unrelated entries. |
| Assume user scope by default for every plugin | Apply the "am I this? vs. am I working on this?" heuristic. |
| Install `alex-act-msft` on a machine off Microsoft's corporate network | Fail closed. WorkIQ endpoints will fail every invocation. |
| Install a plugin at user scope when the heir asked "for this project only" | Repo scope. Read the request. |
| Skip the CLI-version check | Older CLIs miss `marketplace add`; install commands silently fail. |
| Uninstall a plugin without confirming it is not referenced by another installed plugin's SKILL body | Composition breakage. Check first. |
| Run `copilot plugin install <name>@<marketplace>` on an external-agent-recommended plugin without verifying it exists in the marketplace | External agents can hallucinate plugin names. Verify with `marketplace browse` first; install-time failures are noisier than a 2-second pre-check. |

## Composes with

- `install-constellation` — Alex ACT-specific install list; delegates to this skill for the mechanical commands.
- `update-plugins` — safe `copilot plugin update --all` wrap; delegates to this skill for the raw update commands.
- `configure-vscode` (Batch 10) — VS Code user settings; complementary but distinct — this skill covers CLI plugins, that skill covers VS Code settings.
- `ai-memory-setup` (Batch 10) — Alex_ACT_Memory sibling repo; independent of plugin management (Memory is a Git repo, not a plugin).

## Falsifiability

Sunset or revise this skill by **2027-01-30** (6 months) if:

- The Copilot CLI plugin-management CLI syntax changes materially (`plugin install`, `plugin update`, `marketplace add`) — this skill's Command reference table goes stale on emit.
- Copilot CLI adds a plugin auto-update mechanism — the manual-update premise in `update-plugins` sibling skill collapses; may consolidate skills.
- The scope precedence rules change (e.g., user starts winning over repo) — this skill's Scope precedence table is wrong; must be updated with the new precedence.
- ≥3 heirs report that a settings edit made by this skill lost their pre-existing entries (merge failed) — the merge algorithm needs a regression fix.

Track outcomes in the maintaining repo's curation log.

## Related

- `/plugin-status` prompt — read-only audit-mode entry point
- [install-constellation](../install-constellation/SKILL.md) — Alex ACT-specific install list
- [update-plugins](../update-plugins/SKILL.md) — safe update flow with breaking-change detection
- Constellation doc: `constellation/PLUGIN-INTEGRATION.md` in Steward (or your project's equivalent) — the design decisions that ground this skill's scope defaults
