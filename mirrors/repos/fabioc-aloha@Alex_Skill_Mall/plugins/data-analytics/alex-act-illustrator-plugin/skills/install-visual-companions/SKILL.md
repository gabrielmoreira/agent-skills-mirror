---
name: install-visual-companions
description: "Offer to install nine marketplace plugins that compose visual-authoring workflows around Illustrator (chart rendering, screenshot verification, whiteboard iteration, PR annotation). Consent-gated, per-plugin — never bundled without explicit heir approval. Use when the heir asks to enable visual-workflow tooling, or when the illustrator's chart / figure / print-SVG authoring produces artifacts that need runtime verification (multimodal vision loop). Companion to install-constellation in alex-act-core."
lastReviewed: 2026-08-01
---

# install-visual-companions

Nine marketplace plugins compose to deliver visual-authoring workflows around Illustrator: chart rendering, screenshot verification, whiteboard iteration, PR annotation, and the vision loop that closes what looks like a runtime-capability gap via composition rather than net-new authorship.

**None are part of Illustrator's baseline install** — heirs opt in per workload, one at a time. Delegate to Core's [`plugin-management`](https://github.com/fabioc-aloha/Alex_ACT_Core/blob/main/.github/skills/plugin-management/SKILL.md) skill for the mechanical `copilot plugin install / marketplace add` commands and safety rules.

## When to fire

- Heir asks: "install visual companions" / "add screenshot tooling" / "enable chart-rendering plugins" / "install eyeball" / "install the vision loop"
- Heir invokes `/install-visual-companions`
- Heir's declared workload involves any of:
  - Chart authoring, data storytelling, or dashboard rendering
  - Report / document generation that needs visual verification
  - PR review workflows with screenshots or annotations
  - Iterative chart design where seeing the render matters
- Illustrator's `render-verify` skill flags a claim that would benefit from screenshot audit

## When NOT to fire

- Pure-code work, non-visual data pipelines, backend / infra without UI — the companions add zero cost when not installed but non-trivial install-time friction when installed
- The heir hasn't installed Illustrator yet — install Core + Illustrator first; visual companions layer on top

## The nine companion plugins

Discovered and verified via the Steward GH-APP-SUPPORT feedback loop (private governance record) (4-round A/B test on user's brain, 2026-07-31; ledger row `[GH-APP-FEEDBACK]` closure). Ownership moved from `alex-act-core`'s `install-constellation` Step 7 to this skill in Illustrator v0.6.0 (2026-08-01) so the visual-workflow shelf lives with the visual-authoring plugin that anchors it.

| Plugin | Marketplace | Purpose | Round-4 verified? |
|---|---|---|---|
| `chromium-control-canvas` | `awesome-copilot` | Browser preview + screenshot | ✅ (see caveats) |
| `eyeball` | `awesome-copilot` | Screenshot audit with claim-proof output doc | ✅ (see caveats) |
| `diagram-viewer` | `awesome-copilot` | SVG / diagram drill-down preview | ✅ clean install |
| `napkin` | `awesome-copilot` | Whiteboard for iterative chart design | ⚪ Untested |
| `image-annotations` | `alex-mall` | PIL callouts + labels on screenshots | ✅ |
| `chart-interpretation` | `alex-mall` | Read charts, extract insights (reverse of authoring) | ✅ |
| `visual-artifact-qa` | `alex-mall` | Render-time verification (visual output that passes static checks can still fail to render) | ✅ |
| `visual-pr` | `awesome-copilot` | PR screenshot + annotation embed workflow | ⚪ Skills-only, needs real PR to exercise |
| `storytelling-requirements` | `alex-mall` | Guided Big Idea → chart discipline | ✅ |

## Vision loop composition

Discovered via GH-APP-SUPPORT Round 3:

```text
storytelling-requirements  →  visual-artifact-qa  →  chart-interpretation  →  eyeball
   (framing gate)              (render check)         (read-back audit)      (claim proof)
```

Composes end-to-end with zero conflicts. Closes what looks like a runtime-capability gap (multimodal vision on agent output) via composition, not net-new authorship. The vision loop is why the "canonical bundle" for the loop is the 4 skills above; the other 5 fill adjacent gaps.

## Consent flow

### Step 1 — Confirm the workload

Print the 9-plugin table. Ask the heir:

> "Which visual companions do you want? Reply 'vision loop' (storytelling-requirements + visual-artifact-qa + chart-interpretation + eyeball, ~4 plugins, the composition pattern from GH-APP-SUPPORT), 'all nine', or name specific plugins. Reply 'skip' to install nothing."

Default to no action if the heir says "skip" or does not respond. Never install without an explicit consent list per plugin.

### Step 2 — Verify each exists in its marketplace

Anti-hallucination discipline per Core's [`plugin-management`](https://github.com/fabioc-aloha/Alex_ACT_Core/blob/main/.github/skills/plugin-management/SKILL.md) skill § Safety rules. Marketplaces evolve, and plugin names discovered via description-match are LLM-inferred — must be verified before install.

For each plugin the heir named:

```pwsh
copilot plugin marketplace browse <marketplace>
```

Scan the output for the plugin name. If not found, report to the heir and drop it from the install list. Continue with the rest.

### Step 3 — Marketplace registration

Both `awesome-copilot` and `alex-mall` need to be registered in `~/.copilot/settings.json` `extraKnownMarketplaces`:

- `awesome-copilot` → typically pre-registered by Copilot CLI; verify with `copilot plugin marketplace list`
- `alex-mall` → `copilot plugin marketplace add fabioc-aloha/Alex_Skill_Mall` if not registered

### Step 4 — Install commands

Run the install commands in the heir's chosen order:

```pwsh
copilot plugin install <name>@<marketplace>
```

Example — install the vision-loop bundle:

```pwsh
copilot plugin install storytelling-requirements@alex-mall
copilot plugin install visual-artifact-qa@alex-mall
copilot plugin install chart-interpretation@alex-mall
copilot plugin install eyeball@awesome-copilot
```

Per-plugin, one at a time. If any install fails, report it to the heir and continue with the others (installs are independent).

### Step 5 — Install-time caveats

After the install commands complete, print the heir the caveats for the plugins they installed:

**`chromium-control-canvas`** — Needs 3 manual post-install steps:

1. `cd` to the extension dir + `npm install`
2. `npx playwright install chromium` (~112 MiB download)
3. A `python -m http.server` workaround for `file://` URLs (upstream limitation)

Node Playwright is required.

**`eyeball`** — Needs 2 manual post-install steps:

1. `pip install playwright`
2. `python -m playwright install chromium` (~100 MiB, independent from Node Playwright — installing one does not satisfy the other, per upstream recommendation 5 in GH-APP-SUPPORT)

Also: default output path is `~/Desktop`, which is OneDrive-redirected on many Windows setups. If audit artifacts must not sync to corporate OneDrive, override the output path.

**`napkin` and `visual-pr`** — Also Playwright-based; may hit the same first-launch friction pattern as chromium-control-canvas.

**Both browser-based plugins** — Re-download Chromium (~100 MiB each) rather than sharing a common install (upstream recommendation 6 in GH-APP-SUPPORT).

### Step 6 — Report

Print a summary:

- Plugins installed (with marketplace + version)
- Plugins skipped (with reason: marketplace-browse failed / heir declined / already installed)
- Manual post-install steps outstanding (per caveats above; the heir must run them)
- Vision loop status: if all 4 vision-loop plugins are installed, tell the heir "vision loop is complete — you can invoke the composition end-to-end via any of the render-verify workflows"

## Anti-patterns

| Anti-pattern | Correction |
|---|---|
| Bundle all 9 without asking | Consent-gated, per-plugin. The 9 are heir-workload-dependent. |
| Install without verifying marketplace-browse | Per Core's `plugin-management` Safety rule — plugin names can be LLM-hallucinated. Verify first. |
| Skip the caveats step | Chromium download + Python Playwright + OneDrive-redirect trip most heirs on first use. Print them proactively. |
| Install into `.github/copilot/settings.json` at repo scope | Visual companions are heir-scoped tools, not project-scoped. User scope only. |
| Offer visual companions to a heir doing pure backend work | Zero-cost when not installed, but not free. Only offer when the workload calls for them. |

## Composes with

- [`render-verify`](../render-verify/SKILL.md) — Illustrator's own visual-output audit skill; the vision loop extends this with cross-plugin composition
- [`chart-big-idea`](../chart-big-idea/SKILL.md) — Big Idea framing feeds into `storytelling-requirements` for the input side of the vision loop
- Core's [`install-constellation`](https://github.com/fabioc-aloha/Alex_ACT_Core/blob/main/.github/skills/install-constellation/SKILL.md) — installs the four constellation plugins; this skill installs the visual companions after Illustrator is available
- Core's [`plugin-management`](https://github.com/fabioc-aloha/Alex_ACT_Core/blob/main/.github/skills/plugin-management/SKILL.md) — delegated for all mechanical plugin operations + Safety rules

## Falsifiability

This skill is decorative if by 2026-11-01 (90 days):

- Heirs never invoke `/install-visual-companions` and always install companions ad-hoc
- The 9-plugin catalog goes stale (a plugin is retired or moved to a different marketplace) and is not refreshed
- The vision-loop composition pattern proves brittle in practice (Round 4 verified it on 2026-07-31, but sustained use may surface issues)
- The move from Core Step 7 to Illustrator produces reader confusion about where the install offer lives — heirs keep asking Core to install visual companions

Track outcomes in Steward's curation-log (private governance record) tagged `[INSTALL-VISUAL-COMPANIONS]`.

## Origin

Ownership moved from `alex-act-core`'s `install-constellation` Step 7 to this skill in Illustrator v0.6.0 (2026-08-01) per Fabio directive: *"The visual companions should be bundled with the illustrator."* Reverses the 2026-07-31 Option A (route-only) decision in Steward's illustrator/plan.md (private governance record) because "visual-workflow ownership belongs with the visual-authoring plugin" is a stronger fit than "constellation-installer offers all downstream companions".
