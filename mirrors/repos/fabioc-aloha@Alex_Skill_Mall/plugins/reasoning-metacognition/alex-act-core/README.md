# Alex ACT Core

Alex Finch is the runtime identity and relational center of the constellation. Core is Alex's baseline runtime body: the plugin-native successor to [`Alex_ACT_Edition`](https://github.com/fabioc-aloha/Alex_ACT_Edition) v4.2.0, distributing the shared identity contract, always-on ACT discipline, and reusable framework skills through the [Alex ACT Plugin Mall](https://github.com/fabioc-aloha/Alex_Skill_Mall).

**Version**: 0.6.6. Install from the Alex Mall as `alex-act-core@alex-mall`.

**Current source shape**: 42 skills, 18 instructions (17 always-on bootstrapped to `~/.copilot/instructions/` + 1 pattern-applied), 14 slash-command prompts, plus a shared runtime for the bundled document converters.

**Content pipeline**: every skill, instruction, and prompt lands through evidence-gated Steward proposals per [`Alex_ACT_Steward/architecture/act/CURATION-RULES.md`](https://github.com/fabioc-aloha/Alex_ACT_Steward/blob/main/architecture/act/CURATION-RULES.md). No content ships without an approved proposal.

**Maintainer**: [`Alex_ACT_Steward`](https://github.com/fabioc-aloha/Alex_ACT_Steward) (top-of-chain in the plugin-architecture lineage since 2026-07-26 fork-and-freeze).

**Personality and voice reference**: `ALEX-FINCH.md` is Core's stable pointer to the canonical, self-contained [`Alex_ACT_Steward/brain/alex-finch.md`](https://github.com/fabioc-aloha/Alex_ACT_Steward/blob/main/brain/alex-finch.md). Neither document is an automatically loaded plugin component.

**Complete end-user installation**: [`INSTALL.md`](https://github.com/fabioc-aloha/Alex_ACT_Core/blob/main/INSTALL.md).

## Quick install (4 steps)

For a fresh install on any machine:

1. **Register the Alex Mall marketplace**:

   ```powershell
   copilot plugin marketplace add fabioc-aloha/Alex_Skill_Mall
   ```

2. **Install Core**:

   ```powershell
   copilot plugin install alex-act-core@alex-mall
   ```

3. **Reload VS Code** (or restart if using CLI standalone) so Core's prompts and skills activate.

4. **Open Copilot Chat and run**:

   ```text
   /alex-act-core install-constellation
   ```

Step 4 installs the selected constellation plugins, activates the direct MSFT
install when applicable, and separately asks whether to bootstrap the seventeen
always-on ACT instructions. After that first bootstrap, short greetings can use
`greeting-checkin` for repair, drift, and update reminders. A greeting cannot
start first-time setup because the greeting instruction is delivered by the
bootstrap itself.

**Full walkthrough**: [`USER-EXPERIENCE.md` § Stage 1](https://github.com/fabioc-aloha/Alex_ACT_Steward/blob/main/constellation/USER-EXPERIENCE.md) in Steward.

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
# From Copilot Chat: /alex-act-core uninstall-constellation

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

Full reasoning in the [Steward Plan](https://github.com/fabioc-aloha/Alex_ACT_Steward/blob/main/constellation/steward-plan.md) (twelve chapters: overview → distribution mechanism → topology → migration strategy → nomenclature).

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

Full brand-new-user walkthrough (four personas, six install stages, anti-patterns): see [`Alex_ACT_Steward/constellation/USER-EXPERIENCE.md`](https://github.com/fabioc-aloha/Alex_ACT_Steward/blob/main/constellation/USER-EXPERIENCE.md).

### Install from the Alex ACT Mall

Register the mall as a marketplace (one-time, per machine):

```powershell
copilot plugin marketplace add fabioc-aloha/Alex_Skill_Mall
```

Then install Core:

```powershell
copilot plugin install alex-act-core@alex-mall
```

Installs at user scope — Core becomes active in every workspace on the machine. That's the correct behavior; Core is an identity plugin per [`PLUGIN-INTEGRATION.md` § 2](https://github.com/fabioc-aloha/Alex_ACT_Steward/blob/main/constellation/PLUGIN-INTEGRATION.md).

> **Publication status.** The Mall and Core entry are live and publicly available as `alex-act-core@alex-mall`.

### Verify the install

```powershell
copilot plugin list
```

You should see `alex-act-core@alex-mall` with the current version.

## Configure specializations (optional)

Once Core is in, invoke one of Core's plugin-management prompts from Copilot Chat:

- **`/alex-act-core install-constellation`** — installs the four-plugin constellation flow (Core + Illustrator + Enterprise + MSFT with tenant-check)
- **`/alex-act-core bootstrap-workspace`** — previews and consent-gates repository-scoped Markdown Preview CSS, workspace settings, and selective `.gitignore` tracking
- **`/alex-act-core plugin-status`** — read-only inventory of what's installed at user + repo scope
- **`/alex-act-core update-plugins`** — safe update workflow with per-plugin CHANGELOG reading and consent for breaking changes

Full walkthrough with slash-command examples: [USER-EXPERIENCE Stages 3–5](https://github.com/fabioc-aloha/Alex_ACT_Steward/blob/main/constellation/USER-EXPERIENCE.md).

## Update Core

Copilot CLI does not auto-update plugins — updates are manual and version-pinned.

```powershell
copilot plugin update alex-act-core
```

Read the [CHANGELOG](CHANGELOG.md) before applying a version that carries breaking changes. The safer path is to invoke `/alex-act-core update-plugins`, which reads the CHANGELOG for you and consent-gates breaking updates.

## Uninstall

```powershell
copilot plugin uninstall alex-act-core
```

**Troubleshooting.** If the uninstall fails with either:

- `Access is denied (os error 5)` on Windows — close every VS Code window first. Copilot Chat's active MCP servers hold file handles on plugin binaries.
- `Plugin "alex-act-core" is not installed` with the plugin still showing in `copilot plugin list [disabled]` — you have a zombie entry in `~/.copilot/config.json`'s `installedPlugins` array.

Both failure modes and their fixes (including a working two-file cleanup pattern) are documented in [`USER-EXPERIENCE.md § Optional — start from a clean slate`](https://github.com/fabioc-aloha/Alex_ACT_Steward/blob/main/constellation/USER-EXPERIENCE.md).

## Runtime prerequisites for bundled converters

The document-conversion skills (`docx-to-md`, `html-to-md`, `md-to-word`, `md-to-html`, `md-to-txt`, `md-to-eml`) need supporting tools on PATH — heirs install these once:

- **pandoc** on PATH — required for all 6 converters
- **mermaid-cli** (`mmdc`) on PATH — required for `md-to-html` and `md-to-word` when the source contains Mermaid diagrams
- **jszip** in the workspace `node_modules` — optional; `md-to-word` uses it for a faster path and falls back to pandoc otherwise

## Roadmap

Growth continues through evidence-gated proposals per [`Alex_ACT_Steward/architecture/act/CURATION-RULES.md`](https://github.com/fabioc-aloha/Alex_ACT_Steward/blob/main/architecture/act/CURATION-RULES.md). The Both-classified inventory (framework baseline shipped to Core) is complete as of Batch 10 (2026-07-30). Future additions come from Steward's brain plan Part II under **Both** classification or as new proposals. See Steward's [brain plan](https://github.com/fabioc-aloha/Alex_ACT_Steward/blob/main/brain/plan.md) Part II for the current candidate pipeline.

## Related

- [`Alex_ACT_Steward`](https://github.com/fabioc-aloha/Alex_ACT_Steward) — top-of-chain, author + curator of every shipped artefact
- [`Alex_ACT_Illustrator_Plugin`](https://github.com/fabioc-aloha/Alex_ACT_Illustrator_Plugin) — first shipped Steward CLI plugin; proves the transport
- [`Alex_ACT_Plugin_Mall`](https://github.com/fabioc-aloha/Alex_Skill_Mall) — CLI-native plugin marketplace v3.0.0 GA (2026-07-28)
- [`Alex_ACT_Memory`](https://github.com/fabioc-aloha/Alex_ACT_Memory) — shared Git-backed memory bus (sibling, not a plugin)
- [`Alex_ACT_Edition`](https://github.com/fabioc-aloha/Alex_ACT_Edition) — frozen v1 heir-template compatibility surface (v4.2.0, 2026-07-28)
- Steward Plan Phase 3: [gap #1](https://github.com/fabioc-aloha/Alex_ACT_Steward/blob/main/constellation/steward-plan.md) — this repo's creation is the partial resolution

## License

[MIT](LICENSE) — same as sibling plugins.
