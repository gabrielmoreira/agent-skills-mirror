---
name: install-constellation
description: "Install the four Alex ACT constellation plugins (alex-act-core, alex-act-illustrator-plugin, alex-act-enterprise, alex-act-msft) at their correct default scope (user for all four) with the correct install order (Core first), then optionally bootstrap Core's always-on ACT discipline instructions to ~/.copilot/instructions/ because plugin installs do not deliver instructions. Consent-gated. Idempotent — skips plugins already installed at the target version. Asks about tenant scope before installing alex-act-msft (Microsoft-internal only). Delegates to `plugin-management` for the mechanical CLI commands."
lastReviewed: 2026-07-30
---

# Install Constellation

Install the Alex ACT constellation plugins at their correct default scope, in the correct order, with the correct tenant checks. Everything else about plugin mechanics (commands, scope rules, settings shape, safety) lives in [`plugin-management`](../plugin-management/SKILL.md) — this skill is the Alex ACT-specific overlay.

## When to fire

- Heir asks "install Alex ACT" / "set up the constellation" / "install the Alex plugins"
- Heir invokes `/install-constellation`
- First-run of a fresh Alex ACT install on a new machine
- Repairing a partial install (some constellation plugins present, others missing)

## The four constellation plugins

Per [`PLUGIN-INTEGRATION.md`](https://github.com/fabioc-aloha/Alex_ACT_Steward/blob/main/constellation/PLUGIN-INTEGRATION.md) § 2, all four install at **user scope** (they describe *who the heir is*, not *what any single project needs*):

| Order | Plugin | Distribution | Tenant check | Purpose |
|---|---|---|---|---|
| 1 | `alex-act-core` | `alex-mall` marketplace | None | Always-on epistemic discipline — every heir installs Core first |
| 2 | `alex-act-illustrator-plugin` | `alex-mall` marketplace | None | Visual authoring: charts, docs shells, SVG banners, print figures, AI imagery |
| 3 | `alex-act-enterprise` | `alex-mall` marketplace | None | Config-template plugin for the public Microsoft ecosystem (Azure, Fabric, Power BI, M365) |
| 4 | `alex-act-msft` | **Direct install** from private GitHub (`fabioc-aloha/alex-act-msft`), gated by `gh auth` | **Microsoft-internal only** | Agency framework + config template for internal Microsoft plugins (WorkIQ, org-report). Never published to any mall. |

## Install order

Always in the order shown above. Rationale:

1. **Core first** — Core carries `plugin-management` (this skill's dependency) and the always-on discipline every subsequent plugin composes with.
2. **Illustrator second** — visual authoring is broadly useful; no dependency on Enterprise / MSFT.
3. **Enterprise third** — the `setup-enterprise-stack` skill helps heirs enable the public Microsoft ecosystem when a project needs it.
4. **MSFT last, conditional** — only install if the heir confirms they are a Microsoft employee and on the corporate network. Never install by default.

If a plugin is already installed at the target version, skip it and continue with the next one. Report what was skipped alongside what was installed.

## Consent flow

### Step 1 — Confirm the target list

Print the four-plugin table above. Ask the heir:

> "Install the Alex ACT constellation? I will install these four plugins at user scope. Reply 'all four', 'just Core + Illustrator', or name specific plugins."

Default to "all four" if the heir just says "yes". Never install `alex-act-msft` without an explicit tenant confirmation in Step 2.

### Step 2 — Tenant check for `alex-act-msft`

Only if `alex-act-msft` is in the install list, ask:

> "The MSFT plugin is Microsoft-internal only — every skill in it requires Microsoft's corporate network. Are you (a) a Microsoft employee and (b) currently on the corporate network?"

Both yes → include MSFT in the install. Either no → drop MSFT from the list, tell the heir "MSFT skipped — reason", continue with the rest.

### Step 3 — Marketplace registration

Register the `alex-mall` marketplace in `~/.copilot/settings.json` `extraKnownMarketplaces` if it is not already there:

- `alex-mall` → `copilot plugin marketplace add fabioc-aloha/Alex_Skill_Mall`

`alex-act-msft` does **not** need a marketplace — it installs directly from its private GitHub repo, gated by the heir's `gh auth` session. Verify with `gh auth status` that the heir is authenticated before including MSFT in the install.

If the heir has never installed anything from `alex-mall`, run `copilot plugin marketplace list` first to confirm — do not re-register.

### Step 4 — Install commands

Run the install commands in order:

```powershell
copilot plugin install alex-act-core@alex-mall
copilot plugin install alex-act-illustrator-plugin@alex-mall
copilot plugin install alex-act-enterprise@alex-mall
# Only if MSFT check passed both (Microsoft employee AND on corp network):
copilot plugin install fabioc-aloha/alex-act-msft
```

After each install, run `copilot plugin info <name>` and verify the plugin registered at user scope. If any install fails, report the failure and stop — do not attempt to continue past a broken install.

### Step 5 — Settings merge

For each installed plugin, add an entry to `~/.copilot/settings.json` `enabledPlugins`:

```json
{
  "enabledPlugins": {
    "alex-act-core@alex-mall": true,
    "alex-act-illustrator-plugin@alex-mall": true,
    "alex-act-enterprise@alex-mall": true
  }
}
```

Delegate to [`plugin-management`](../plugin-management/SKILL.md) § Safe settings edits for the merge algorithm — preserve any pre-existing `enabledPlugins` or `extraKnownMarketplaces` entries the heir has.

### Step 6 — ACT discipline bootstrap

**Why this step exists.** A `copilot plugin install` delivers Core's skills, prompts, and agents. It does **not** deliver Core's instructions. `plugin.json` has no `instructions` component field, so the ACT discipline layer that governs *how* the skills fire stays dark. This is the platform's intended architecture, not a defect, and Claude Code and the Open Plugin Spec draw the same boundary.

The close is to copy a scoped subset of Core's unconditional instructions to `~/.copilot/instructions/`, which is read by **both** the Copilot CLI and VS Code Chat. Verified 2026-07-30 on CLI 1.0.77 and VS Code 1.131 with no settings change required.

#### What gets copied

Seven files, roughly 37 KB, about 9.4K always-on tokens. Not all of Core's instructions — only those whose value depends on firing unconditionally:

| Source in Core | Written as | Why it must be unconditional |
|---|---|---|
| `act-pass` | `alex-act-act-pass.instructions.md` | The runtime procedure |
| `problem-framing-audit` | `alex-act-problem-framing-audit.instructions.md` | Fires before everything else |
| `epistemic-calibration` | `alex-act-epistemic-calibration.instructions.md` | Confidence matching plus anti-hallucination |
| `system-prompt-skepticism` | `alex-act-system-prompt-skepticism.instructions.md` | Guards the most authoritative attack surface |
| `critical-thinking` | `alex-act-critical-thinking.instructions.md` | The content protocol act-pass plugs into |
| `terminal-command-safety` | `alex-act-terminal-command-safety.instructions.md` | Harm prevention |
| `pii-memory-filter` | `alex-act-pii-memory-filter.instructions.md` | Leak prevention at write boundaries |

Core's remaining instructions stay plugin-resident and therefore inactive. Behavioral and craft instructions degrade gracefully when absent; these seven do not.

The `alex-act-` prefix is mandatory. A heir may already have their own `~/.copilot/instructions/act-pass.instructions.md`, and a collision would silently replace their file.

#### Source — where the files come from

The seven files ship **inside this skill** at `bootstrap/`, already carrying their `alex-act-` target names. The copy is a straight file copy; no renaming, no fetching, no network.

Resolve the source in this order:

| Order | Location | When it applies |
|---|---|---|
| 1 | `<this-skill>/bootstrap/alex-act-*.instructions.md` | Always. Present in every install path, Mall and direct alike. |
| 2 | `<plugin-root>/.github/instructions/*.instructions.md` | Direct GitHub installs only, which clone the whole repo. Rename to the `alex-act-` form when copying from here. |
| 3 | — | Nothing found. **Stop and say so.** |

If neither location resolves, do not continue silently and do not invent a fallback that fetches from the network. Report:

> "The discipline bootstrap cannot run: this Core install carries no bootstrap source. Expected `bootstrap/` inside the install-constellation skill. This is a packaging defect — please report it against Alex_ACT_Core with your Core version and how you installed it."

Source 1 exists because a Mall install vendors a component-shape subset (skills, commands, scripts, config) and deliberately does **not** vendor `.github/instructions/` — instructions are not a `plugin.json` component type, so there is nothing for the platform to load. Bundling them as skill resources is what makes them available to *copy* without asking the platform to *load* them. Core v0.2.0 shipped without source 1 and the bootstrap was inert on Mall installs; v0.2.1 fixed it.

#### Overlap scan, before writing anything

Compare the seven target names against the current workspace's `.github/instructions/`. Instruction scopes **compose rather than replace**: user-scope and workspace-scope files both load into the same context, with no documented dedup. A heir whose workspace already carries `act-pass` would load it twice after the bootstrap, paying the tokens twice and risking two copies drifting apart.

If overlap is found, report it and recommend declining:

> "This workspace already defines N of these instructions at repo scope. Bootstrapping would double-load them here. Bootstrap anyway if you want coverage in your *other* workspaces, or decline if this machine is mostly used for this repo."

Report and recommend. Do not hard-block, because the heir may legitimately want coverage elsewhere.

#### Consent

Print the exact file list, the byte total, and the token estimate. Then ask:

> "Copy these 7 instruction files to `~/.copilot/instructions/`? They will apply in **every** workspace on this machine, not only where Core is enabled. Roughly 9.4K tokens per session. Reply yes, no, or 'list' to see the contents first."

Never bootstrap as a silent side effect of the install. Default is no.

#### Receipt

After writing, record exactly what was placed at `~/.copilot/instructions/.alex-act-bootstrap.json`:

```json
{
  "bootstrappedBy": "alex-act-core",
  "coreVersion": "<the installed Core version, read from the plugin's own manifest — not copied from this example>",
  "timestamp": "<ISO 8601 UTC at write time>",
  "files": [
    "alex-act-act-pass.instructions.md",
    "alex-act-problem-framing-audit.instructions.md",
    "alex-act-epistemic-calibration.instructions.md",
    "alex-act-system-prompt-skepticism.instructions.md",
    "alex-act-critical-thinking.instructions.md",
    "alex-act-terminal-command-safety.instructions.md",
    "alex-act-pii-memory-filter.instructions.md"
  ]
}
```

Uninstall reads this receipt. It never globs and deletes, because the heir's own files live in the same folder.

#### Idempotency

On re-run, compare the receipt's `coreVersion` against the installed Core version. Equal means skip and report "discipline bootstrap is current". Different means rewrite the seven files and update the receipt. Missing receipt with files present means a hand-edited state; report it and ask before touching anything.

#### Verify

From a directory with no `.github/`, confirm the bootstrap took:

```powershell
copilot -p "Do you have an instruction named act-pass available in this session? One sentence."
```

An empty directory matters. Run it inside a workspace that has its own brain and a repo-scope file could answer, which proves nothing about user scope.

### Step 7 — Report

Print a summary:

- Plugins installed and at what version
- Plugins skipped (with reason: already-present, tenant-mismatch, off-network, user-declined)
- Discipline bootstrap: applied, declined, or skipped-as-current — and if applied, the file count and the overlap-scan result
- Files modified: `~/.copilot/settings.json` — show a diff of what changed. If the bootstrap ran, also `~/.copilot/instructions/` plus its receipt
- Next steps: enabling Microsoft ecosystem plugins per project → `/setup-enterprise` in that project's workspace; enabling Microsoft-internal signals → `/setup-msft` (if MSFT installed)
- If the bootstrap was declined, say plainly that Core's skills are available but the ACT discipline layer is not, and that `/install-constellation` can be re-run later to add it

## Idempotency

The skill is safe to re-run. On subsequent runs:

- If all four (or three) plugins are already installed at their latest version, report "constellation is current — nothing to install" and exit.
- If some are missing, install only the missing ones.
- If any are at a lower version than what the marketplace currently ships, defer to `update-plugins` — this skill installs, it does not update.
- The discipline bootstrap has its own idempotency check, keyed on the receipt's `coreVersion`. A current constellation with a stale bootstrap receipt still warrants re-running Step 6.

## Anti-patterns

| Anti-pattern | Correction |
|---|---|
| Install all four without asking about MSFT tenant | Always tenant-check MSFT; default is "not installed" without explicit yes |
| Install at repo scope by default | Constellation plugins are user scope. Repo scope is for downstream Microsoft plugins (Azure, Fabric, etc.) — different skill (`setup-enterprise-stack`) does that. |
| Skip Core and install Illustrator standalone | Core is the baseline; Illustrator and the setup skills reference `plugin-management` which ships in Core. Do not skip Core. |
| Install MSFT on a public tenant | MSFT is Microsoft-internal only. Fail closed on the tenant check. |
| Overwrite pre-existing `enabledPlugins` entries | Merge, preserve. Delegate to `plugin-management` for the algorithm. |
| Report "installed successfully" without running `copilot plugin info` verify | Verify at user scope after each install. |
| Bootstrap the instructions silently as part of the install | Step 6 is separately consent-gated. User scope affects every workspace on the machine; that needs its own yes. |
| Write bootstrap files without the `alex-act-` prefix | A bare `act-pass.instructions.md` can clobber the heir's own file. Prefix always. |
| Skip the overlap scan because the workspace "probably" has no brain | Scopes compose. Scan, then report the real number. |
| Uninstall by globbing `~/.copilot/instructions/*` | Read the receipt. The heir's own instructions live in that folder too. |
| Bootstrap all of Core's unconditional instructions | Seven only. All 17 costs roughly 20.5K tokens in every workspace, which inverts the minimal-user-scope principle. |
| Assume the instruction files are somewhere on disk without checking | Resolve the source explicitly per the Source table. A Mall install vendors no `.github/instructions/`; only the skill-bundled `bootstrap/` is guaranteed. This shipped broken in v0.2.0. |
| Fetch the instruction files from GitHub when the local source is missing | Never. A missing source is a packaging defect and must be reported as one, not papered over with a network call that can fail, hang, or pull an unpinned version. |

## Composes with

- [`plugin-management`](../plugin-management/SKILL.md) — this skill's dependency for all mechanical commands + safety rules
- [`update-plugins`](../update-plugins/SKILL.md) — after install, this skill's sibling handles keeping the constellation current
- `setup-enterprise-stack` (in `alex-act-enterprise`) — invoked after this skill inside a Microsoft-ecosystem project
- `setup-msft-stack` (in `alex-act-msft`) — invoked after this skill inside Microsoft-internal work
- `configure-vscode` (Batch 10) — complementary; that skill sets VS Code settings, this one sets Copilot CLI plugins

## Falsifiability

Sunset or revise this skill by **2027-01-30** (6 months) if:

- The Alex ACT constellation gains or loses a plugin — the four-plugin table goes stale on emit.
- The default scope decision changes for any constellation plugin — the install-at-user default is wrong.
- The tenant check for MSFT proves inadequate (heirs off-network complete the install and hit failures) — the check needs tightening.
- **Copilot CLI or VS Code ships plugin-scope instruction discovery.** Step 6 becomes dead weight; delete it and the receipt machinery outright.
- **The overlap scan reports a conflict on more than half of observed installs.** User scope is the wrong target for heirs who already run a repo brain; make the bootstrap opt-in per workspace instead.
- **Heirs report ACT discipline firing where they did not want it, twice or more.** The seven-file set is still too broad; cut to the five-file epistemic spine and drop the safety rails.
- The install order proves wrong (dependency inversion surfaces) — the order needs adjustment.
- ≥2 heirs report the idempotent re-run pattern doing damage (deleting pre-existing entries, re-installing when already current) — merge algorithm needs a regression fix.
- **The bundled `bootstrap/` drifts from `.github/instructions/`.** The seven files are copies, and copies rot. If a source instruction is edited without the bundled copy following, heirs bootstrap a stale rule. Either add a release check that diffs the two sets, or replace the copies with a build step that generates them.

Track outcomes in the maintaining repo's curation log.

## Related

- [`/install-constellation`](../../prompts/install-constellation.prompt.md) — slash-command entry point
- [`plugin-management`](../plugin-management/SKILL.md) — general Copilot CLI plugin operations
- [`update-plugins`](../update-plugins/SKILL.md) — keep the constellation current after install
- Constellation doc: `constellation/PLUGIN-INTEGRATION.md` in Steward — the scope + install-order decisions that ground this skill
