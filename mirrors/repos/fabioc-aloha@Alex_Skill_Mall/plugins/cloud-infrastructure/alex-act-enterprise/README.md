# alex-act-enterprise

Alex ACT config-template plugin for the **public Microsoft ecosystem**. Ships a single scaffolding skill (`setup-enterprise-stack`) that generates a repo-scoped `.github/copilot/settings.json` block for 7 Microsoft plugins any tenant can use, with an explicit `--user` opt-in.

**Status**: v0.1.2, published through `alex-mall`. Repository created 2026-07-30. Content lands through evidence-gated Steward proposals per [`Alex_ACT_Steward/architecture/act/CURATION-RULES.md`](https://github.com/fabioc-aloha/Alex_ACT_Steward/blob/main/architecture/act/CURATION-RULES.md).

**Maintainer**: [`Alex_ACT_Steward`](https://github.com/fabioc-aloha/Alex_ACT_Steward) (top-of-chain in the plugin-architecture lineage since 2026-07-26 fork-and-freeze).

## What this is

`alex-act-enterprise` is a **config-template plugin** — it ships one skill, not a large surface. The skill emits a paste-ready `enabledPlugins` + `extraKnownMarketplaces` block for the seven public Microsoft ecosystem plugins:

| Plugin | Marketplace | Marketplace source | Purpose |
|---|---|---|---|
| `azure` | `azure-skills` | `microsoft/azure-skills` | Azure resource authoring + ops + diagnostics + RBAC + storage + compute |
| `fabric-consumption` | `copilot-plugins` (default) | (built-in) | Fabric semantic model / warehouse / SQL / dataflow consumption |
| `fabric-skills` | `copilot-plugins` (default) | (built-in) | Cross-Fabric workload utility skills |
| `fabric-operations` | `copilot-plugins` (default) | (built-in) | Fabric admin + capacity + governance ops |
| `fabric-authoring` | `copilot-plugins` (default) | (built-in) | Fabric pipeline / dataflow / eventhouse / semantic-model / spark authoring |
| `powerbi-authoring` | `fabric-collection` | `microsoft/skills-for-fabric` | Power BI report design + authoring + planning + management |
| `microsoft-365-agents-toolkit` | `copilot-plugins` (default) | (built-in) | Declarative agent authoring, Teams app dev, UI widget dev |

Every entry is **public**. Any tenant with the corresponding Microsoft subscription (Azure, Fabric workspace, M365) can enable them.

## What this is NOT

- **Not the Copilot CLI itself** — this plugin rides on top of Copilot CLI + Chat.
- **Not the underlying plugins** — this is a config template. The actual plugins (`azure`, `fabric-*`, `powerbi-authoring`, `microsoft-365-agents-toolkit`) live in their upstream Microsoft repos and marketplaces. This plugin points a heir at the right block to paste.
- **Not Microsoft-internal** — everything here is publicly available. Microsoft-internal services (WorkIQ, Agency framework, `org-report`) live in a separate private plugin, `alex-act-msft` (not published to public Mall).
- **Not opinionated about which subset to enable** — the target block enables all 7. Heirs edit their local `enabledPlugins` after the initial paste to drop plugins they don't need.

## Where this sits

Three-layer constellation stack:

| Layer | Plugin | Role |
|---|---|---|
| **Baseline** | [`alex-act-core`](https://github.com/fabioc-aloha/Alex_ACT_Core) | Always-on epistemic discipline every heir needs |
| **Specialization — visual authoring** | [`alex-act-illustrator-plugin`](https://github.com/fabioc-aloha/Alex_ACT_Illustrator_Plugin) | Charts, print figures, SVG banners, AI imagery |
| **Specialization — Microsoft ecosystem** | **`alex-act-enterprise`** (this repo) | Config template for the public Microsoft plugin set |
| **Specialization — Microsoft-internal** | `alex-act-msft` (private) | Agency framework + WorkIQ + `org-report` scaffolding |

Heirs enable whichever specializations apply to their workspace.

## Target settings block

Invoking `setup-enterprise-stack` produces:

```json
{
  "extraKnownMarketplaces": {
    "azure-skills":       { "source": { "source": "github", "repo": "microsoft/azure-skills" } },
    "fabric-collection":  { "source": { "source": "github", "repo": "microsoft/skills-for-fabric" } }
  },
  "enabledPlugins": {
    "azure@azure-skills":                            true,
    "fabric-consumption@copilot-plugins":            true,
    "fabric-skills@copilot-plugins":                 true,
    "fabric-operations@copilot-plugins":             true,
    "fabric-authoring@copilot-plugins":              true,
    "powerbi-authoring@fabric-collection":           true,
    "microsoft-365-agents-toolkit@copilot-plugins": true
  }
}
```

Heirs merge this into `.github/copilot/settings.json` by default. Pass `--user` to target `~/.copilot/settings.json` instead.

## Layout

```text
alex-act-enterprise/
├── manifest.json               # Mall-side plugin metadata
├── README.md                   # (this file)
├── CHANGELOG.md                # Keep a Changelog format
├── LICENSE                     # MIT
├── .gitignore
├── .markdownlint.json
├── .github/                    # Copilot Chat + CLI discovery surface
│   ├── copilot-instructions.md
│   ├── skills/                 # setup-enterprise-stack
│   └── prompts/                # setup-enterprise command
└── .vscode/                    # workspace settings for self-dogfooding
```

Same layout as [`alex-act-core`](https://github.com/fabioc-aloha/Alex_ACT_Core) and [`alex-act-illustrator-plugin`](https://github.com/fabioc-aloha/Alex_ACT_Illustrator_Plugin) — the proven Steward-authored CLI plugin pattern.

## Install

**Prerequisites** (once per machine):

- **Copilot CLI ≥ 1.0.75** — [install docs](https://docs.github.com/copilot/how-tos/set-up/install-copilot-cli). Update with `winget upgrade --id GitHub.CopilotCLI` on Windows.
- **GitHub CLI authenticated** — `gh auth login` and confirm with `gh auth status`.
- **Alex ACT Core installed first** — `alex-act-enterprise` composes on top of Core's plugin-management framework.

Full brand-new-user walkthrough (four personas, five install stages, anti-patterns): see [`Alex_ACT_Steward/constellation/USER-EXPERIENCE.md`](https://github.com/fabioc-aloha/Alex_ACT_Steward/blob/main/constellation/USER-EXPERIENCE.md).

### Install from the Alex ACT Mall

Register the mall as a marketplace (one-time, per machine):

```powershell
copilot plugin marketplace add fabioc-aloha/Alex_Skill_Mall
```

Then install Enterprise:

```powershell
copilot plugin install alex-act-enterprise@alex-mall
```

Installs at user scope — Enterprise's `setup-enterprise-stack` skill and `/alex-act-enterprise setup-enterprise` prompt become available in every workspace.

### Verify the install

```powershell
copilot plugin list
```

You should see `alex-act-enterprise@alex-mall` with the current version. From Copilot Chat, `/alex-act-enterprise setup-enterprise` should appear in the slash-command picker.

## Use — configure the Microsoft ecosystem in a workspace

The Microsoft ecosystem plugins (Azure, Fabric-*, Power BI, M365 Agents Toolkit) are **project-specific** per [`PLUGIN-INTEGRATION.md` § 2](https://github.com/fabioc-aloha/Alex_ACT_Steward/blob/main/constellation/PLUGIN-INTEGRATION.md). Enterprise defaults to **repo scope** — the target block gets written to `.github/copilot/settings.json` in whatever workspace you're in, so teammates inherit the setup on next `git pull`.

Open your Microsoft-ecosystem workspace and invoke:

```text
/alex-act-enterprise setup-enterprise
```

The skill has three modes:

1. **Emit only** (safe default) — prints the target settings block for review; you paste it yourself.
2. **Consent-gated auto-install** — after your explicit yes, merges the block into `.github/copilot/settings.json` and runs `copilot plugin install` for each entry.
3. **Audit only** — read-only comparison against the current state; reports which plugins are enabled, missing, or at the wrong scope.

Pass `--user` to write to user scope instead (`~/.copilot/settings.json`) — useful if you work in the Microsoft ecosystem across every workspace.

## Update Enterprise

```powershell
copilot plugin update alex-act-enterprise
```

Read the [CHANGELOG](CHANGELOG.md) before applying breaking updates. Core's `/alex-act-core update-plugins` prompt reads the CHANGELOG for you and consent-gates breaking changes.

## Uninstall

```powershell
copilot plugin uninstall alex-act-enterprise
```

Uninstalling Enterprise **does not** remove the downstream Microsoft plugins it configured. Those stay enabled in their respective `settings.json` files until you uninstall them individually (`copilot plugin uninstall azure@azure-skills`, etc.) or edit the `enabledPlugins` block.

**Troubleshooting.** If uninstall fails with `Access is denied` (close VS Code first) or `Plugin "..." is not installed` while the plugin still shows in `plugin list` (zombie entry in `~/.copilot/config.json`), see [`USER-EXPERIENCE.md § Optional — start from a clean slate`](https://github.com/fabioc-aloha/Alex_ACT_Steward/blob/main/constellation/USER-EXPERIENCE.md) for the two-file cleanup pattern.

## Roadmap

Growth happens through evidence-gated proposals per [`Alex_ACT_Steward/architecture/act/CURATION-RULES.md`](https://github.com/fabioc-aloha/Alex_ACT_Steward/blob/main/architecture/act/CURATION-RULES.md).

Future candidates (evaluated per proposal):

- Composition skills that call across the enabled plugins (e.g., "author a Fabric semantic-model driven by an Azure Data Lake source").
- Diagnostic skills that check whether the target subscriptions are actually configured before invoking the underlying plugins.

Each proposal requires explicit Fabio approval before landing.

## Related

- [`Alex_ACT_Steward`](https://github.com/fabioc-aloha/Alex_ACT_Steward) — authoring authority and top-of-chain
- [`Alex_ACT_Core`](https://github.com/fabioc-aloha/Alex_ACT_Core) — the baseline plugin every heir installs
- [`alex-act-illustrator-plugin`](https://github.com/fabioc-aloha/Alex_ACT_Illustrator_Plugin) — sibling specialization (visual authoring)
- `alex-act-msft` — sibling specialization (Microsoft-internal Agency + WorkIQ), private-only
- [`Alex_ACT_Plugin_Mall`](https://github.com/fabioc-aloha/Alex_Skill_Mall) — distribution surface

## License

[MIT](LICENSE)
