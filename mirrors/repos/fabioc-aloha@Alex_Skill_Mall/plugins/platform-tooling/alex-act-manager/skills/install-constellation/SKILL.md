---
name: install-constellation
description: "Install and repair the Alex ACT brain spine and optional plugins, bootstrap Core's instructions, configure stable host settings, and offer workspace-scoped optional capability defaults. Use for first setup, greeting-time repair, or partial-install recovery. Manager and Core can never be disabled by workspace configuration."
lastReviewed: 2026-08-01
---

# Install Constellation

Install the Alex ACT constellation plugins at their correct default scope, in the correct order, with the correct tenant checks. Everything else about plugin mechanics (commands, scope rules, settings shape, safety) lives in [`plugin-management`](../plugin-management/SKILL.md) — this skill is the Alex ACT-specific overlay.

## When to fire

- Heir asks "install Alex ACT" / "set up the constellation" / "install the Alex plugins"
- Heir invokes `/alex-act-manager install-constellation`
- First run after a fresh Core install on a new machine. The heir must invoke `/alex-act-manager install-constellation` explicitly because `greeting-checkin` is not available until Step 7 has run once.
- Repairing a partial install (some constellation plugins present, others missing)
- **Auto-invoked from `greeting-checkin` instruction** on session start when constellation state is incomplete (added 2026-08-01)

## Invocation modes

The skill runs in one of three modes depending on how it was invoked:

| Mode | Trigger | Behavior |
|---|---|---|
| **Manual** (default) | Heir types `/alex-act-manager install-constellation` explicitly | Full consent flow: install selection, tenant check, user settings, bootstrap, repository CSS, and verification. All Steps 1-9 fire. |
| **Auto-invoked from greeting-checkin** | Greeting detected incomplete brain state and user approved repair | Greeting Y covers brain-spine repair only. User settings, bootstrap, and repository files retain separate consent gates because they affect different scopes. |
| **Repair** | Heir invoked manually AND state check finds partial residue (bootstrap files without matching plugin, orphan receipt) | Confirm intent to complete partial install; skip installs of plugins already present at target version. |
| **Bootstrap-only repair** | All plugin versions, enabled keys, manifests, stable user settings, and current-workspace files match, but the receipt or one of its seventeen files is missing, stale, or hash-mismatched | Skip plugin selection, marketplace registration, installation, user-settings audit, and workspace bootstrap. Show the bootstrap delta and go directly to the separate Step 7 consent gate. |

The three modes converge on the same underlying steps. What differs is which consent gates fire and how the report frames the outcome.

`greeting-checkin` is a post-bootstrap convenience, not a first-install entry
point. It is one of the seventeen files copied by Step 7, so a machine with no
prior bootstrap cannot route a greeting through this skill.

For greeting-time brain repair, do not treat optional plugins as missing brain
components. Manager, Core, and the seventeen-file bootstrap are the spine.
Optional plugins selected by the user remain installed and enabled at user
scope. Alex ACT does not manage per-workspace plugin activation.

## The four constellation plugins

Per [`PLUGIN-INTEGRATION.md`](https://github.com/fabioc-aloha/Alex_ACT_Core/blob/main/INSTALL.md) § 2, all four install at **user scope** (they describe *who the heir is*, not *what any single project needs*):

| Order | Plugin | Distribution | Tenant check | Purpose |
|---|---|---|---|---|
| 1 | `alex-act-core` | `alex-mall` marketplace | None | Always-on epistemic discipline — every heir installs Core first |
| 2 | `alex-act-illustrator-plugin` | `alex-mall` marketplace | None | Visual authoring: charts, docs shells, SVG banners, print figures, AI imagery |
| 3 | `alex-act-enterprise` | `alex-mall` marketplace | None | Config-template plugin for the public Microsoft ecosystem (Azure, Fabric, Power BI, M365) |
| 4 | `alex-act-msft` | **Direct install** from private GitHub (`fabioc_microsoft/alex-act-msft`), gated by `gh auth` | **Microsoft-internal only** | Agency framework + config template for internal Microsoft plugins (WorkIQ, org-report). Never published to any mall. |

## Install order

Always in the order shown above. Rationale:

1. **Core first** — Core carries `plugin-management` (this skill's dependency) and the always-on discipline every subsequent plugin composes with.
2. **Illustrator second** — visual authoring is broadly useful; no dependency on Enterprise / MSFT.
3. **Enterprise third** — the `setup-enterprise-stack` skill helps heirs enable the public Microsoft ecosystem when a project needs it.
4. **MSFT last, conditional** — only install if the heir confirms they are a Microsoft employee and on the corporate network. Never install by default.

If a plugin is already installed at the target version, skip it and continue with the next one. Report what was skipped alongside what was installed.

Resolve target versions deterministically before deciding that a marketplace plugin is current:

```powershell
node <plugin-management-skill>/scripts/manager-operations.cjs marketplace-versions `
  --plugins alex-act-core,alex-act-illustrator-plugin,alex-act-enterprise
```

This reads exact records from `alex-mall`'s `.github/plugin/marketplace.json`. `marketplace browse` proves reachability and supports discovery; it is not authoritative for versions. For private MSFT, use its authenticated source `plugin.json` through `gh api`.

## Optional: visual workflow companions

Nine marketplace plugins compose to deliver visual-authoring workflows (chart rendering, screenshot verification, whiteboard iteration, PR annotation). **Ownership of the install offer for these companions moved from this skill to `alex-act-illustrator-plugin`'s `install-visual-companions` skill in Illustrator v0.6.0 (2026-08-01)** — the visual-workflow shelf now lives with the visual-authoring plugin that anchors it, per Fabio directive ("The visual companions should be bundled with the illustrator"). This reverses the 2026-07-31 Option A (route-only) decision recorded in Steward's illustrator/plan.md (private governance record).

**How to offer them now**: after `install-constellation` completes and Illustrator is installed, invoke `/alex-act-illustrator-plugin install-visual-companions` or ask Illustrator's `install-visual-companions` skill directly. That skill carries the 9-plugin catalog, the vision-loop composition pattern (`storytelling-requirements → visual-artifact-qa → chart-interpretation → eyeball`), the install-time caveats (Playwright downloads, Python-vs-Node independence, OneDrive-redirect on Windows), and the consent flow.

**Do not** attempt to offer the companions from this skill — the catalog + caveats + verified-status list are maintained in one place (Illustrator) to avoid drift.

**Discovery + verification history**: the 9-plugin catalog + vision-loop composition were discovered and Round-4 verified via the Steward GH-APP-SUPPORT feedback loop (private governance record) on 2026-07-31 (ledger row `[GH-APP-FEEDBACK]` closure). This skill originally shipped the catalog in Core v0.3.0 (via commit `a2de9d4`); Illustrator v0.6.0 took ownership 2026-08-01.

## Consent flow

### Step 1 — Confirm the target list

Print the four-plugin table above. Ask the heir:

> "Install the Alex ACT constellation? I will install these four plugins at user scope. Reply 'all four', 'just Core + Illustrator', or name specific plugins."

Default to "all four" if the heir just says "yes". Never install `alex-act-msft` without an explicit tenant confirmation in Step 2.

**Do not** offer visual-workflow companions in Step 1 — they are a Step 9 follow-up **via Illustrator's `/alex-act-illustrator-plugin install-visual-companions` command (owner: `alex-act-illustrator-plugin` v0.6.0+)**. Bundling them into the constellation install dilutes the consent flow.

### Step 2 — Tenant check for `alex-act-msft`

Only if `alex-act-msft` is in the install list, ask:

> "The MSFT plugin is Microsoft-internal only — every skill in it requires Microsoft's corporate network. Are you (a) a Microsoft employee and (b) currently on the corporate network?"

Both yes → include MSFT in the install. Either no → drop MSFT from the list, tell the heir "MSFT skipped — reason", continue with the rest.

### Step 3 — Marketplace registration

Register the `alex-mall` marketplace in `~/.copilot/settings.json` `extraKnownMarketplaces` if it is not already there:

- `alex-mall` → `copilot plugin marketplace add fabioc-aloha/Alex_Skill_Mall`

`alex-act-msft` does **not** need a marketplace — it installs directly from the private `fabioc_microsoft` managed-user repository. Verify with `gh auth status` that the active account is the heir's Microsoft-managed identity, then require `gh api repos/fabioc_microsoft/alex-act-msft` to succeed before including MSFT. If another account is active, use `gh auth switch -u <managed-login>`; never fall back to an external personal account.

If the heir has never installed anything from `alex-mall`, run `copilot plugin marketplace list` first to confirm — do not re-register.

### Step 4 — Install commands

Run the install commands in order:

```powershell
copilot plugin install alex-act-core@alex-mall
copilot plugin install alex-act-illustrator-plugin@alex-mall
copilot plugin install alex-act-enterprise@alex-mall
# Only if MSFT check passed both (Microsoft employee AND on corp network):
copilot plugin install fabioc_microsoft/alex-act-msft
```

After each install, run `copilot plugin list` and verify the plugin name, version,
and status. If the output is ambiguous, read the installed `plugin.json` from
the marketplace tree or `_direct` tree. If any install fails, report the failure
and stop. Do not attempt to continue past a broken install.

### Step 5 — Settings merge

Enable every selected installed constellation plugin at user scope:

```json
{
  "enabledPlugins": {
    "alex-act-manager@alex-mall": true,
    "alex-act-core@alex-mall": true,
    "alex-act-illustrator-plugin@alex-mall": true,
    "alex-act-enterprise@alex-mall": true,
    "alex-act-document-tools@alex-mall": true,
    "alex-act-msft": true
  }
}
```

The bare `alex-act-msft` key is required on Copilot CLI 1.0.77 because direct
installs do not populate `enabledPlugins` automatically. Verify the explicit
`true` after the merge so MSFT remains active after restart.

Delegate to [`plugin-management`](../plugin-management/SKILL.md) § Safe settings edits for the merge algorithm — preserve any pre-existing `enabledPlugins` or `extraKnownMarketplaces` entries the heir has.

### Step 6 — VS Code user baseline

Audit the current VS Code user settings against
`../plugin-management/resources/welcome-baseline.json`, the same source used by
`/alex-act-manager configure-vscode-verify` and
`/alex-act-manager configure-vscode`.

The baseline contains only stable Alex ACT host settings, including the
framework-required local skill, prompt, agent, and hook discovery roots. It does
not contain Fabio-specific editor preferences, extension-version paths, Azure
identifiers, credentials, or `markdown.styles`.

Show a table of missing and drifted keys, then ask:

> "Apply the stable Alex ACT VS Code user baseline? This merges only the listed keys into your user settings and preserves unrelated preferences. Reply yes, no, or details."

Only after an explicit yes, run the `/alex-act-manager configure-vscode`
contract and read back every managed value. If no keys drift, report the user
baseline as current without asking to rewrite the file.

If user settings contain `markdown.styles` with an absolute local filesystem
path, report it as unsupported cross-workspace guidance. Ask separately whether
to remove that key. Never replace it with another local absolute path. Local CSS
belongs to Step 8; an HTTPS stylesheet remains a user-owned exception.

### Step 7 — ACT discipline bootstrap

**Why this step exists.** A `copilot plugin install` delivers Core's skills, prompts, and agents. It does **not** deliver Core's instructions. `plugin.json` has no `instructions` component field, so the ACT discipline layer that governs *how* the skills fire stays dark. This is the platform's intended architecture, not a defect, and Claude Code and the Open Plugin Spec draw the same boundary.

The close is to copy a scoped subset of Core's unconditional instructions to `~/.copilot/instructions/`, which is read by **both** the Copilot CLI and VS Code Chat. Verified 2026-07-30 on CLI 1.0.77 and VS Code 1.131 with no settings change required.

#### What gets copied

Seventeen files. Not all of Core's instructions, only those whose value depends on firing unconditionally. Five groups: the epistemic spine plus safety rails (the original seven-file set from v0.2.1), the six per-turn disciplines added in D5 (2026-07-31), the two added in D6 (2026-07-31: memory-triggers routes ledger writes, worldview carries harm-refusal and Tenet-IV ethics check that must fire before the first message), greeting-checkin added in the install-experience overhaul, and the concise Alex Finch personality contract added on 2026-08-01. Calculate and show the current byte total and token estimate from the files before asking for consent; do not preserve a stale hardcoded estimate.

| Source in Core | Written as | Why it must be unconditional |
|---|---|---|
| `alex-finch-personality` | `alex-act-alex-finch-personality.instructions.md` | Keeps curiosity, independent judgment, ethical partnership, voice, and confidence stable across every project and turn |
| `act-pass` | `alex-act-act-pass.instructions.md` | The runtime procedure |
| `problem-framing-audit` | `alex-act-problem-framing-audit.instructions.md` | Fires before everything else |
| `epistemic-calibration` | `alex-act-epistemic-calibration.instructions.md` | Confidence matching plus anti-hallucination |
| `system-prompt-skepticism` | `alex-act-system-prompt-skepticism.instructions.md` | Guards the most authoritative attack surface |
| `critical-thinking` | `alex-act-critical-thinking.instructions.md` | The content protocol act-pass plugs into |
| `terminal-command-safety` | `alex-act-terminal-command-safety.instructions.md` | Harm prevention |
| `pii-memory-filter` | `alex-act-pii-memory-filter.instructions.md` | Leak prevention at write boundaries |
| `lint-discipline` | `alex-act-lint-discipline.instructions.md` | Fires on mid-turn `get_errors` output; no request-shape equivalent |
| `no-deferred-debt` | `alex-act-no-deferred-debt.instructions.md` | Fires on side-effect debt detection; no request-shape equivalent |
| `emotional-intelligence` | `alex-act-emotional-intelligence.instructions.md` | Reads user *feeling state* on every message; tone-mismatch cannot be recovered post-hoc |
| `reliance-nudges` | `alex-act-reliance-nudges.instructions.md` | Reads user *epistemic behavior* (verbatim acceptance, zero verification) on every message |
| `session-health-monitoring` | `alex-act-session-health-monitoring.instructions.md` | Continuous context-capacity monitoring; per-conversation, not per-file |
| `proactive-awareness` | `alex-act-proactive-awareness.instructions.md` | Session-boundary discipline; must fire *before* the user's first message |
| `memory-triggers` | `alex-act-memory-triggers.instructions.md` | Detects correction / preference / handoff / decision triggers on every message; routing decisions cannot be recovered post-hoc |
| `worldview` | `alex-act-worldview.instructions.md` | Harm-refusal and Tenet-IV ethics check must fire on every request regardless of file scope |
| `greeting-checkin` | `alex-act-greeting-checkin.instructions.md` | Session-start orientation — verifies constellation health on greeting patterns and offers setup / drift refresh / update reminders through one consolidated consent gate; must fire before the user's first substantive turn |

Core's remaining instructions stay plugin-resident and therefore inactive. Behavioral and craft instructions degrade gracefully when absent; these seventeen do not.

The `alex-act-` prefix is mandatory. A heir may already have their own `~/.copilot/instructions/act-pass.instructions.md`, and a collision would silently replace their file.

#### Source — where the files come from

The seventeen files ship **inside this skill** at `bootstrap/`, already carrying their `alex-act-` target names. The copy is a straight file copy; no renaming, no fetching, no network.

Resolve the source in this order:

| Order | Location | When it applies |
|---|---|---|
| 1 | `<this-skill>/bootstrap/alex-act-*.instructions.md` | Always. Present in every install path, Mall and direct alike. |
| 2 | `<installed-core-root>/.github/instructions/*.instructions.md` | Direct GitHub Core installs only, which clone the whole Core repo. Rename to the `alex-act-` form when copying from here. |
| 3 | — | Nothing found. **Stop and say so.** |

If neither location resolves, do not continue silently and do not invent a fallback that fetches from the network. Report:

> "The discipline bootstrap cannot run: this Core install carries no bootstrap source. Expected `bootstrap/` inside the install-constellation skill. This is a packaging defect — please report it against Alex_ACT_Core with your Core version and how you installed it."

Source 1 exists because a Mall install vendors a component-shape subset (skills, commands, scripts, config) and deliberately does **not** vendor `.github/instructions/` — instructions are not a `plugin.json` component type, so there is nothing for the platform to load. Bundling them as skill resources is what makes them available to *copy* without asking the platform to *load* them. Core v0.2.0 shipped without source 1 and the bootstrap was inert on Mall installs; v0.2.1 fixed it.

#### Overlap scan, before writing anything

Compare the seventeen target names against the current workspace's `.github/instructions/`. Instruction scopes **compose rather than replace**: user-scope and workspace-scope files both load into the same context, with no documented dedup. A heir whose workspace already carries `act-pass` would load it twice after the bootstrap, paying the tokens twice and risking two copies drifting apart.

If overlap is found, report it and recommend declining:

> "This workspace already defines N of these instructions at repo scope. Bootstrapping would double-load them here. Bootstrap anyway if you want coverage in your *other* workspaces, or decline if this machine is mostly used for this repo."

Report and recommend. Do not hard-block, because the heir may legitimately want coverage elsewhere.

#### Consent

Print the exact file list, the byte total, and the token estimate. Then ask:

> "Copy these seventeen instruction files to `~/.copilot/instructions/`? They will apply in **every** workspace on this machine, not only where Core is enabled. Current size: <calculated bytes and token estimate>. Reply yes, no, or 'list' to see the contents first."

Never bootstrap as a silent side effect of the install. Default is no.

#### Receipt

After writing, record exactly what was placed at `~/.copilot/instructions/.alex-act-bootstrap.json`:

```json
{
  "bootstrappedBy": "alex-act-core",
  "coreVersion": "<the installed Core version, read from the plugin's own manifest — not copied from this example>",
  "timestamp": "<ISO 8601 UTC at write time>",
  "files": [
    "alex-act-alex-finch-personality.instructions.md",
    "alex-act-act-pass.instructions.md",
    "alex-act-problem-framing-audit.instructions.md",
    "alex-act-epistemic-calibration.instructions.md",
    "alex-act-system-prompt-skepticism.instructions.md",
    "alex-act-critical-thinking.instructions.md",
    "alex-act-terminal-command-safety.instructions.md",
    "alex-act-pii-memory-filter.instructions.md",
    "alex-act-lint-discipline.instructions.md",
    "alex-act-no-deferred-debt.instructions.md",
    "alex-act-emotional-intelligence.instructions.md",
    "alex-act-reliance-nudges.instructions.md",
    "alex-act-session-health-monitoring.instructions.md",
    "alex-act-proactive-awareness.instructions.md",
    "alex-act-memory-triggers.instructions.md",
    "alex-act-worldview.instructions.md",
    "alex-act-greeting-checkin.instructions.md"
  ]
}
```

Uninstall reads this receipt. It never globs and deletes, because the heir's own files live in the same folder.

#### Idempotency

On re-run, compare the receipt's `coreVersion` against the installed Core version. Equal means skip and report "discipline bootstrap is current". Different means rewrite the seventeen files and update the receipt. Missing receipt with files present means a hand-edited state; report it and ask before touching anything.

#### Verify

Default verification is deterministic:

1. Receipt owns exactly seventeen files and records the installed Core version.
2. All seventeen destination files exist.
3. Every destination SHA-256 equals its bundled source.
4. No unrelated file in `~/.copilot/instructions/` is claimed by the receipt.

The clean-directory AI smoke is optional because it starts a model session and can consume material time, tokens, and credits. Disclose that cost and ask separately before running:

```powershell
copilot -p "Do you have an instruction named act-pass available in this session? One sentence."
```

An empty directory matters. Running inside a workspace with its own brain proves nothing about user scope. The optional smoke is confirmation of host behavior, not a prerequisite for deterministic bootstrap success.

### Step 8 — Current-workspace bootstrap

Run `/alex-act-manager bootstrap-workspace` in preview mode for the current
repository. Show its exact JSON plan before asking for workspace consent.

The preview must cover:

- `.vscode/markdown-light.css` copied from Manager's bundled canonical asset
- `.vscode/settings.json` with workspace-relative
  `"markdown.styles": [".vscode/markdown-light.css"]` set only when absent
- `.gitignore` narrowing only when a broad `.vscode` rule hides the two managed
  workspace files

If an existing workspace CSS file differs from the bundled source, preserve it
by default and report the SHA-256 drift. Ask explicitly whether to refresh that
file from the canonical bundled CSS. Custom CSS is never overwritten merely
because it differs.

Apply only after a separate workspace consent, then verify the destination CSS
hash, settings value, and idempotent second preview. If the current directory is
not the intended project, ask for the target path instead of guessing.

### Step 9 — Report

Print a summary with six activation planes:

| Plane | Evidence | Status vocabulary |
|---|---|---|
| **installed** | `copilot plugin list` plus installed `plugin.json` at the exact target version | pass / fail |
| **enabled** | exact user or repo `enabledPlugins` key is true | pass / fail |
| **instruction-loaded** | receipt, file count, Core version, and source-to-target hashes | pass / declined / stale / fail |
| **skill-invokable** | namespaced command executes; generic skill tool is probed only when available | pass / host-limited / fail |
| **user-settings** | stable baseline comparison and read-back | pass / declined / drift / fail |
| **workspace** | CSS hash, relative `markdown.styles`, and idempotent preview | pass / declined / custom-preserved / fail |

Then report:

- Plugins installed and at what version
- Plugins skipped (with reason: already-present, tenant-mismatch, off-network, user-declined)
- Discipline bootstrap: applied, declined, or skipped-as-current — and if applied, the file count and the overlap-scan result
- Files modified: `~/.copilot/settings.json` and VS Code user settings — show a diff of what changed. If the instruction bootstrap ran, also `~/.copilot/instructions/` plus its receipt. If workspace bootstrap ran, list `.vscode/markdown-light.css`, `.vscode/settings.json`, and `.gitignore` actions separately
- Next steps: enabling Microsoft ecosystem plugins per project → `/alex-act-enterprise setup-enterprise` in that project's workspace; enabling Microsoft-internal signals → `/alex-act-msft setup-msft` (if MSFT installed)
- **Visual-workflow companions** (see § "Optional: visual workflow companions" above for ownership + rationale): if the heir mentioned chart authoring, dashboards, reports with visuals, PR screenshots, or any workload involving visual verification, tell them to invoke `/alex-act-illustrator-plugin install-visual-companions` after this install completes. Do NOT list the 9 plugins from here — the catalog + install-time caveats + verified-status list live in Illustrator's `install-visual-companions` skill to keep them from drifting across two plugins.
- If the bootstrap was declined, say plainly that Core's skills are available but the ACT discipline layer is not, and that `/alex-act-manager install-constellation` can be re-run later to add it
- If user settings or workspace bootstrap were declined, name the corresponding namespaced repair command instead of calling setup fully complete
- If all plugin, user-settings, and workspace checks passed before Step 7, label the run `bootstrap-only repair`; do not replay or narrate skipped installation work as if it ran

## Idempotency

The skill is safe to re-run. On subsequent runs:

- If all four (or three) plugins are already installed at their latest version, report "constellation is current — nothing to install" and exit.
- If some are missing, install only the missing ones.
- If any are at a lower version than what the marketplace currently ships, defer to `update-plugins` — this skill installs, it does not update.
- The discipline bootstrap has its own idempotency check, keyed on the receipt's `coreVersion`. A current constellation with a stale bootstrap receipt still warrants re-running Step 7.
- The VS Code user baseline and current-workspace bootstrap have independent idempotency checks. A current plugin set does not imply either settings scope is current.

## Anti-patterns

| Anti-pattern | Correction |
|---|---|
| Install all four without asking about MSFT tenant | Always tenant-check MSFT; default is "not installed" without explicit yes |
| Install at repo scope by default | Constellation plugins are user scope. Repo scope is for downstream Microsoft plugins (Azure, Fabric, etc.) — different skill (`setup-enterprise-stack`) does that. |
| Skip Core and install Illustrator standalone | Core is the baseline; Illustrator and the setup skills reference `plugin-management` which ships in Core. Do not skip Core. |
| Install MSFT on a public tenant | MSFT is Microsoft-internal only. Fail closed on the tenant check. |
| Overwrite pre-existing `enabledPlugins` entries | Merge, preserve. Delegate to `plugin-management` for the algorithm. |
| Report "installed successfully" without checking `copilot plugin list`, settings, and the install tree | Verify all three signals after each install. |
| Bootstrap the instructions silently as part of the install | Step 7 is separately consent-gated. User scope affects every workspace on the machine; that needs its own yes. |
| Write bootstrap files without the `alex-act-` prefix | A bare `act-pass.instructions.md` can clobber the heir's own file. Prefix always. |
| Skip the overlap scan because the workspace "probably" has no brain | Scopes compose. Scan, then report the real number. |
| Uninstall by globbing `~/.copilot/instructions/*` | Read the receipt. The heir's own instructions live in that folder too. |
| Bootstrap all of Core's unconditional instructions | Seventeen only. The remaining instructions do not earn unconditional user-scope cost. |
| Assume the instruction files are somewhere on disk without checking | Resolve the source explicitly per the Source table. A Mall install vendors no `.github/instructions/`; only the skill-bundled `bootstrap/` is guaranteed. This shipped broken in v0.2.0. |
| Fetch the instruction files from GitHub when the local source is missing | Never. A missing source is a packaging defect and must be reported as one, not papered over with a network call that can fail, hang, or pull an unpinned version. |
| Copy Steward's entire `.vscode/settings.json` into every user's profile | Apply only the portable baseline. Fabio-specific editor preferences and extension paths are not constellation policy. |
| Put a local absolute CSS path in user `markdown.styles` | Remove it with consent or leave it user-owned. Copy local CSS into each repository and use the workspace-relative path instead. |
| Call setup complete after plugin installation alone | Report user-settings and workspace scopes independently; offer the namespaced repair commands when either is declined. |

## Composes with

- [`plugin-management`](../plugin-management/SKILL.md) — this skill's dependency for all mechanical commands + safety rules
- [`update-plugins`](../update-plugins/SKILL.md) — after install, this skill's sibling handles keeping the constellation current
- `setup-enterprise-stack` (in `alex-act-enterprise`) — invoked after this skill inside a Microsoft-ecosystem project
- `setup-msft-stack` (in `alex-act-msft`) — invoked after this skill inside Microsoft-internal work
- `configure-vscode` — Step 6 applies the portable VS Code user baseline after separate consent
- `bootstrap-workspace` — Step 8 provisions repository-relative CSS and Markdown settings after separate consent

## Falsifiability

Sunset or revise this skill by **2027-01-30** (6 months) if:

- The Alex ACT constellation gains or loses a plugin — the four-plugin table goes stale on emit.
- The default scope decision changes for any constellation plugin — the install-at-user default is wrong.
- The tenant check for MSFT proves inadequate (heirs off-network complete the install and hit failures) — the check needs tightening.
- **Copilot CLI or VS Code ships plugin-scope instruction discovery.** Step 7 becomes dead weight; delete it and the receipt machinery outright.
- **The overlap scan reports a conflict on more than half of observed installs.** User scope is the wrong target for heirs who already run a repo brain; make the bootstrap opt-in per workspace instead.
- **Heirs report ACT discipline or personality firing where they did not want it, twice or more.** The seventeen-file set is too broad; remove the lowest-value unconditional additions or make personality opt-in.
- The install order proves wrong (dependency inversion surfaces) — the order needs adjustment.
- ≥2 heirs report the idempotent re-run pattern doing damage (deleting pre-existing entries, re-installing when already current) — merge algorithm needs a regression fix.
- **The bundled `bootstrap/` drifts from `.github/instructions/`.** The seventeen files are copies, and copies rot. If a source instruction is edited without the bundled copy following, heirs bootstrap a stale rule. Either add a release check that diffs the two sets, or replace the copies with a build step that generates them.
- **Direct GitHub installs stop working or are removed by Copilot CLI.** The interim MSFT distribution path must move before the breaking release; do not wait for users to discover it during setup.
- A workspace profile disables Manager or Core even once, or private identifiers are written without explicit acknowledgement.

Track outcomes in the maintaining repo's curation log.

## Related

- `/install-constellation` — slash-command entry point
- [`plugin-management`](../plugin-management/SKILL.md) — general Copilot CLI plugin operations
- [`update-plugins`](../update-plugins/SKILL.md) — keep the constellation current after install
- Constellation doc: `constellation/PLUGIN-INTEGRATION.md` in Steward — the scope + install-order decisions that ground this skill
