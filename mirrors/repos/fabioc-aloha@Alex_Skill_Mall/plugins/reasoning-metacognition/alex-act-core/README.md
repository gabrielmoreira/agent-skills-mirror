# Alex ACT Core

![Alex ACT Core](https://raw.githubusercontent.com/fabioc-aloha/Alex_ACT_Core/main/assets/banner.svg)

[Core](https://github.com/fabioc-aloha/Alex_ACT_Core) · [Manager](https://github.com/fabioc-aloha/Alex_ACT_Manager) · [Illustrator](https://github.com/fabioc-aloha/Alex_ACT_Illustrator_Plugin) · [Document Tools](https://github.com/fabioc-aloha/Alex_ACT_Document_Tools) · [Enterprise](https://github.com/fabioc-aloha/alex-act-enterprise)

Alex ACT Core gives every workspace the same reasoning floor: Alex Finch's identity, ACT's critical-thinking discipline, and reusable skills arrive as one plugin-native baseline. Projects add specialized capability without rebuilding the brain.

**Version**: 0.9.0. Install from the Alex Mall as `alex-act-core@alex-mall`.

**Current source shape**: 42 skills, 18 instructions (17 always-on bootstrapped to `~/.copilot/instructions/` + 1 pattern-applied), 14 slash-command prompts, plus a shared runtime for the bundled document converters.

**Public runtime source**: [Alex ACT Core](https://github.com/fabioc-aloha/Alex_ACT_Core) contains the shipped skills, prompts, instruction sources, release history, and installation contract. Changes remain evidence-gated before release.

**Public project home**: [Alex_ACT_Core](https://github.com/fabioc-aloha/Alex_ACT_Core).

**Personality and voice reference**: `ALEX-FINCH.md` is Core's public identity reference. It is not an automatically loaded plugin component; the separately bootstrapped personality instruction carries the runtime contract.

**Complete end-user installation**: [`INSTALL.md`](https://github.com/fabioc-aloha/Alex_ACT_Core/blob/main/INSTALL.md).

## Quick install (4 steps)

For a fresh install on any machine:

1. **Register the Alex Mall marketplace**:

   ```powershell
   copilot plugin marketplace add fabioc-aloha/Alex_Skill_Mall
   ```

2. **Install the brain spine**:

   ```powershell
   copilot plugin install alex-act-manager@alex-mall
   copilot plugin install alex-act-core@alex-mall
   ```

3. **Reload VS Code** (or restart if using CLI standalone) so Manager and Core activate.

4. **Open Copilot Chat and run**:

   ```text
   /alex-act-manager install-constellation
   ```

Step 4 keeps every selected plugin enabled and separately asks whether to
bootstrap the seventeen always-on ACT instructions. After that first bootstrap,
short greetings can use `greeting-checkin` for repair, drift, and updates. A greeting
cannot start first-time setup because the greeting instruction is delivered by
the bootstrap itself.

**Full walkthrough**: [`USER-EXPERIENCE.md` § Stage 1](https://github.com/fabioc-aloha/Alex_ACT_Core/blob/main/INSTALL.md) in Steward.

## Managing the Alex Mall marketplace

The Alex Mall is where Core, Illustrator, and Enterprise install from. Four commands cover its lifecycle (all user-scope; work from any workspace):

| Command | What it does |
| --- | --- |
| `copilot plugin marketplace add fabioc-aloha/Alex_Skill_Mall` | **Register** the Mall as `alex-mall`. Needed once per machine before any `<plugin>@alex-mall` install works. (Step 1 of Quick install above.) |
| `copilot plugin marketplace update alex-mall` | **Refresh** the local catalog cache from GitHub. The Mall self-curates weekly; the local cache doesn't auto-refresh. Run this when a new plugin was added to the Mall since your last install. Omit the name to update all registered marketplaces at once. |
| `copilot plugin marketplace browse alex-mall` | **List** every plugin available in the Mall with descriptions. Read-only. |
| `copilot plugin marketplace remove alex-mall` | **Unregister** the Mall. Refuses if any of its plugins are currently installed; add `--force` to also uninstall those plugins in one command. |

Also: `copilot plugin marketplace list` shows every registered marketplace, including the two built-in defaults (`copilot-plugins`, `awesome-copilot`) that don't need registration.

### Removing when plugins are installed

Two paths:

**Safe path** — uninstall plugins first, then unregister:

```powershell
# Option 1: uninstall the whole constellation cleanly (uses uninstall-constellation skill from Chat)
# From Copilot Chat: /alex-act-manager uninstall-constellation

# Option 2: uninstall individual plugins manually
copilot plugin uninstall alex-act-core@alex-mall
copilot plugin uninstall alex-act-illustrator-plugin@alex-mall
# ... and so on

# Then unregister the marketplace
copilot plugin marketplace remove alex-mall
```

**One-command teardown** — removes the marketplace AND uninstalls its plugins:

```powershell
copilot plugin marketplace remove alex-mall --force
```

> **Windows only**: if VS Code is running when you invoke either path, the CLI will hit `os error 5` on the plugin uninstalls because VS Code holds file handles on the installed plugin trees. Close all VS Code windows first (File → Exit), open a fresh PowerShell terminal (NOT VS Code's integrated terminal), and run the commands there. The `uninstall-constellation` skill's generated script bakes this guard in automatically.

## What this is

Alex ACT Core is the **baseline plugin** — the minimal always-on brain that every heir needs regardless of domain. It sits at the bottom of a three-layer stack:

| Layer | What it ships | Example |
| --- | --- | --- |
| **Baseline** (this plugin) | Always-on epistemic discipline + reusable framework skills, including document converters and a shared runtime | `act-pass`, `critical-thinking`, `problem-framing-audit`, `meditation`, `md-to-word`, `docx-to-md`, `lint-clean-markdown` |
| **Specialization** (Mall opt-in) | Domain plugins heirs install as needed | `alex-act-illustrator-plugin` (visual authoring), future Azure / Fabric / M365 plugins |
| **Local customization** (`.github/skills/local/` in each heir) | Heir-specific customizations | Whatever the heir invented for their own project |

**What Core is NOT**:

- Not the Copilot CLI itself — Core rides on top of Copilot CLI + Chat
- Not the shared Memory bus — that lives in [`Alex_ACT_Memory`](https://github.com/fabioc-aloha/Alex_ACT_Memory) as a Git-backed sibling repo (per Steward Plan)
- Not the Mall itself — the Mall lives in [`Alex_ACT_Plugin_Mall`](https://github.com/fabioc-aloha/Alex_Skill_Mall) and self-curates per ADR-008
- Not a visual-authoring bundle — chart authoring, SVG banners, print figures, and AI imagery live in [`alex-act-illustrator-plugin`](https://github.com/fabioc-aloha/Alex_ACT_Illustrator_Plugin), not Core

## Why the plugin?

Under the v1 heir-template model, [`Alex_ACT_Edition`](https://github.com/fabioc-aloha/Alex_ACT_Edition) was a template each heir bootstrapped into its own `.github/`. Upgrading meant N-heir manual bootstraps. Under the plugin-native model, Core lives in one place (this repo → Mall) and every heir picks it up on next session via `copilot plugin update alex-act-core`. Fork-and-freeze on 2026-07-26 established that the plugin-native lineage runs alongside the frozen v1 compatibility line rather than replacing it in place.

Full reasoning in the Steward Plan (private governance record) (twelve chapters: overview → distribution mechanism → topology → migration strategy → nomenclature).

## Layout

```text
Alex_ACT_Core/
├── manifest.json               # Mall-side plugin metadata (identity, assets, install paths)
├── README.md                   # (this file)
├── CHANGELOG.md                # Keep a Changelog format
├── LICENSE                     # MIT
├── .gitignore
├── .markdownlint.json
├── .github/                    # Copilot Chat + CLI discovery surface
│   ├── copilot-instructions.md
│   ├── config/                 # brand-palette.json, welcome-baseline.json
│   ├── scripts/shared/         # runtime helpers used by the converter skills
│   ├── skills/                 # 42 skills (framework + workspace bootstrap + craft + converters + plugin lifecycle)
│   ├── instructions/           # 18 instructions (17 always-on bootstrapped + 1 pattern-applied)
│   └── prompts/                # 14 slash-command prompts
└── .vscode/                    # workspace settings for self-dogfooding
```

Same layout as [`alex-act-illustrator-plugin`](https://github.com/fabioc-aloha/Alex_ACT_Illustrator_Plugin) — the proven Steward-authored CLI plugin pattern.

## Install

**Prerequisites** (once per machine):

- **Copilot CLI ≥ 1.0.75** — [install docs](https://docs.github.com/copilot/how-tos/set-up/install-copilot-cli). Verify with `copilot --version`. If already installed, update with `winget upgrade --id GitHub.CopilotCLI` (Windows).
- **GitHub CLI authenticated** — `gh auth login` and confirm with `gh auth status`.

Full brand-new-user walkthrough (four personas, six install stages, anti-patterns): see [Alex ACT Core install guide](https://github.com/fabioc-aloha/Alex_ACT_Core/blob/main/INSTALL.md).

### Install from the Alex ACT Mall

Register the mall as a marketplace (one-time, per machine):

```powershell
copilot plugin marketplace add fabioc-aloha/Alex_Skill_Mall
```

Then install Core:

```powershell
copilot plugin install alex-act-core@alex-mall
```

Installs at user scope — Core becomes active in every workspace on the machine. That's the correct behavior; Core is an identity plugin per [`PLUGIN-INTEGRATION.md` § 2](https://github.com/fabioc-aloha/Alex_ACT_Core/blob/main/INSTALL.md).

> **Publication status.** The Mall and Core entry are live and publicly available as `alex-act-core@alex-mall`.

### Verify the install

```powershell
copilot plugin list
```

You should see `alex-act-core@alex-mall` with the current version.

### VS Code 1.131 compatibility

Keep `chat.useAgentSkills` set to `true`, and set
`github.copilot.chat.skillTool.enabled` to `false`. This works around
[`microsoft/vscode#314772`](https://github.com/microsoft/vscode/issues/314772): it
disables only the experimental generic skill resolver, not Agent Skills. Start a
new Agent chat or reload VS Code after changing the setting.

## Lifecycle management

Use [`alex-act-manager@alex-mall`](https://github.com/fabioc-aloha/Alex_ACT_Manager)
for installation, status, updates, uninstallation, and configuration. Core's
namespaced lifecycle commands remain available as compatibility copies.

## Configure specializations (optional)

Use Manager's lifecycle commands from Copilot Chat for configuration and other
lifecycle work. Core retains these compatibility copies:

- **`/alex-act-manager install-constellation`** — installs selected plugins, repairs the brain spine, and enables installed plugins at user scope
- **`/alex-act-core bootstrap-workspace`** — previews and consent-gates repository-scoped Markdown Preview CSS, workspace settings, and selective `.gitignore` tracking
- **`/alex-act-core plugin-status`** — read-only inventory of what's installed at user + repo scope
- **`/alex-act-core update-plugins`** — safe update workflow with per-plugin CHANGELOG reading and consent for breaking changes

Full walkthrough with slash-command examples: [USER-EXPERIENCE Stages 3–5](https://github.com/fabioc-aloha/Alex_ACT_Core/blob/main/INSTALL.md).

## Update Core

Copilot CLI does not auto-update plugins — updates are manual and version-pinned.

```powershell
copilot plugin update alex-act-core
```

Read the [CHANGELOG](CHANGELOG.md) before applying a version that carries breaking changes. Prefer Manager for the safer update workflow; `/alex-act-core update-plugins` remains a compatibility copy that reads the CHANGELOG and consent-gates breaking updates.

## Uninstall

```powershell
copilot plugin uninstall alex-act-core
```

Prefer Manager for constellation removal; Core's `/alex-act-core uninstall-constellation` remains a compatibility copy.

**Troubleshooting.** If the uninstall fails with either:

- `Access is denied (os error 5)` on Windows — close every VS Code window first. Copilot Chat's active MCP servers hold file handles on plugin binaries.
- `Plugin "alex-act-core" is not installed` with the plugin still showing in `copilot plugin list [disabled]` — you have a zombie entry in `~/.copilot/config.json`'s `installedPlugins` array.

Both failure modes and their fixes (including a working two-file cleanup pattern) are documented in [`USER-EXPERIENCE.md § Optional — start from a clean slate`](https://github.com/fabioc-aloha/Alex_ACT_Core/blob/main/INSTALL.md).

## Runtime prerequisites for bundled converters

The document-conversion skills (`docx-to-md`, `html-to-md`, `md-to-word`, `md-to-html`, `md-to-txt`, `md-to-eml`) need supporting tools on PATH — heirs install these once:

- **pandoc** on PATH — required for all 6 converters
- **mermaid-cli** (`mmdc`) on PATH — required for `md-to-html` and `md-to-word` when the source contains Mermaid diagrams
- **jszip** in the workspace `node_modules` — optional; `md-to-word` uses it for a faster path and falls back to pandoc otherwise

## Roadmap

Growth continues through evidence-gated proposals per [Alex ACT Core](https://github.com/fabioc-aloha/Alex_ACT_Core). The Both-classified inventory (framework baseline shipped to Core) is complete as of Batch 10 (2026-07-30). Future additions come from Steward's brain plan Part II under **Both** classification or as new proposals. See Steward's [brain plan](https://github.com/fabioc-aloha/Alex_ACT_Core) Part II for the current candidate pipeline.

## Related

- [Alex_ACT_Core](https://github.com/fabioc-aloha/Alex_ACT_Core) — top-of-chain, author + curator of every shipped artefact
- [`Alex_ACT_Illustrator_Plugin`](https://github.com/fabioc-aloha/Alex_ACT_Illustrator_Plugin) — first shipped Steward CLI plugin; proves the transport
- [`Alex_ACT_Manager`](https://github.com/fabioc-aloha/Alex_ACT_Manager) — preferred lifecycle management for installation, status, updates, uninstallation, and configuration
- [`Alex_ACT_Plugin_Mall`](https://github.com/fabioc-aloha/Alex_Skill_Mall) — CLI-native plugin marketplace v3.0.0 GA (2026-07-28)
- [`Alex_ACT_Memory`](https://github.com/fabioc-aloha/Alex_ACT_Memory) — shared Git-backed memory bus (sibling, not a plugin)
- [`Alex_ACT_Edition`](https://github.com/fabioc-aloha/Alex_ACT_Edition) — frozen v1 heir-template compatibility surface (v4.2.0, 2026-07-28)
- Steward Plan Phase 3: [gap #1](https://github.com/fabioc-aloha/Alex_ACT_Core) — this repo's creation is the partial resolution

## License

[MIT](LICENSE) — same as sibling plugins.
