# Alex ACT Plugin Mall

![Alex ACT Plugin Mall](assets/banner.svg)

Alex ACT Plugin Mall lets users add trusted capabilities to GitHub Copilot without copying a whole AI setup into every project. Start with **Alex ACT Core** for a dependable working baseline, then add only the specializations that match your work.

The Mall publishes **358 curated plugins** for direct installation and maintains a **trust-scored discovery index** across **4178 plugins** in **48 stores**.

- Installation is **opt-in** and user-invoked. Publication does not mutate your projects.
- Current release: **[v3.0.0](https://github.com/fabioc-aloha/Alex_Skill_Mall/releases/tag/v3.0.0)**. Rollback anchor: annotated tag `v2.0.0`.

---

## Quick install (GitHub Copilot CLI)

**Prerequisite:** the [GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/set-up/install-copilot-cli). Confirm with `copilot --version`.

### 1. Register the marketplace (one-time)

```bash
copilot plugin marketplace add fabioc-aloha/Alex_Skill_Mall
```

This registers the `alex-mall` marketplace with the CLI. It reads `.github/plugin/marketplace.json` from this repo; no credentials required.

### 2. Browse and install a plugin

```bash
# Browse everything published by alex-mall
copilot plugin marketplace browse alex-mall

# Install a plugin (plugin@marketplace format)
copilot plugin install <plugin-name>@alex-mall

# Install the self-activating baseline
copilot plugin install alex-act-core@alex-mall
```

Plugins install into `~/.copilot/installed-plugins/alex-mall/<plugin-name>/`.

### 3. Verify and manage

```bash
copilot plugin list                              # what is installed
copilot plugin update <plugin-name>@alex-mall    # pull the latest version
copilot plugin uninstall <plugin-name>@alex-mall # remove a plugin
copilot plugin marketplace list                  # registered marketplaces
copilot plugin marketplace remove alex-mall      # unregister the marketplace
```

---

## Build an Alex ACT setup

Core is the self-activating baseline every Alex ACT installation needs. Native Copilot CLI commands provide plugin lifecycle; add the optional capabilities that match the work at hand.

| What you want to do | Plugin | Published version | What it adds |
| --- | --- | --- | --- |
| Give Copilot a reliable baseline across projects | [`alex-act-core`](https://github.com/fabioc-aloha/Alex_ACT_Core/tree/v4.0.1) | `4.0.1` | Critical thinking, planning, security and privacy guidance, project bootstrap, and plugin management |
| Create charts, print figures, banners, AI images, or browsable documentation | [`alex-act-illustrator-plugin`](https://github.com/fabioc-aloha/Alex_ACT_Illustrator_Plugin/tree/v2.5.1) | `2.5.1` | Visual framing, authoring, generation, and verification workflows |
| Convert Markdown, Word, HTML, and email deliverables | [`alex-act-document-tools`](https://github.com/fabioc-aloha/Alex_ACT_Document_Tools/tree/v1.1.1) | `1.1.1` | Portable document conversion and polished rich-email workflows |
| Set up public Microsoft tools for a project | [`alex-act-enterprise`](https://github.com/fabioc-aloha/alex-act-enterprise/tree/v1.1.1/packages/copilot) | `1.1.1` | Guided setup for Azure, Fabric, Power BI, and Microsoft 365 Agents Toolkit |
| Plan and govern an optional provider workflow | [`alex-act-ai-operations`](https://github.com/fabioc-aloha/Alex_ACT_AI_Operations/tree/v0.2.1) | `0.2.1` | Provider-neutral discovery, explicit consent, and execution evidence for Foundry, Hugging Face, and ElevenLabs |

### Recommended path

1. Install Core with `copilot plugin install alex-act-core@alex-mall`.
2. Reload VS Code, open Copilot Chat, and run `/alex-act-core bootstrap-core`.
3. Add an optional plugin when you know what you need:
   - Visual work: `copilot plugin install alex-act-illustrator-plugin@alex-mall`
   - Document production: `copilot plugin install alex-act-document-tools@alex-mall`
   - Public Microsoft tools: `copilot plugin install alex-act-enterprise@alex-mall`
   - Provider operations: `copilot plugin install alex-act-ai-operations@alex-mall`

> **Private specialization:** `alex-act-msft` is private and intended only for Microsoft-internal work. It is not published in this public Mall.

---

## Use in VS Code

The Copilot CLI plugins integrate with **GitHub Copilot Chat** in VS Code once installed.

1. **Install the [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) and [Copilot Chat](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot-chat) extensions** in VS Code (1.117 or later).
2. **Install plugins via the Copilot CLI** using the steps above. In VS Code 1.131, keep Agent Skills enabled, disable the broken generic plugin-skill resolver, and disable automatic next-change reveal to avoid editor conflicts:

   ```jsonc
   "chat.useAgentSkills": true,
   "github.copilot.chat.skillTool.enabled": false,
   "chat.editing.revealNextChangeOnResolve": false
   ```

   Namespaced commands and agents remain available while the resolver workaround is active.
3. **Reload VS Code** or run *Developer: Reload Window* so Copilot Chat re-scans the installed plugins.
4. In Chat, invoke a plugin's commands with `/`, agents with `@`, or skills by describing the task the skill's frontmatter is scoped to.

---

## Per-repo auto-install

To make a project auto-install specific plugins for every collaborator, commit a `.github/copilot/settings.json` that names the marketplace **and** the plugins:

```jsonc
{
  "extraKnownMarketplaces": {
    "alex-mall": {
      "type": "github",
      "repository": "fabioc-aloha/Alex_Skill_Mall"
    }
  },
  "enabledPlugins": {
    "alex-act-illustrator-plugin@alex-mall": true,
    "alex-act-enterprise@alex-mall": true
  }
}
```

- **`extraKnownMarketplaces`** registers the marketplace so the CLI knows where to fetch from. Without it, plugin specs referencing `@alex-mall` will not resolve unless the collaborator has already registered `alex-mall` at the user level.
- **`enabledPlugins`** is the declarative auto-install list. Keys are plugin specs (`<name>@<marketplace>`); values are `true` (enabled) or `false` (disabled).
- A plugin enabled only through the repository file is **scoped to that repository** — it auto-installs and activates there, but stays inactive in unrelated projects.
- Both keys are read by the [GitHub Copilot CLI](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference) **and** by **Copilot cloud agent**, so the same file drives both local sessions and cloud-run sessions.

### Settings tiers (precedence order)

| File | Scope | Commit? |
| --- | --- | --- |
| `~/.copilot/settings.json` | User (your defaults for every repo) | No — personal machine |
| `.github/copilot/settings.json` | Repository (shared with collaborators) | **Yes** |
| `.github/copilot/settings.local.json` | Local overrides for this checkout | No — add to `.gitignore` |

The three files are merged in that order; later wins. For `enabledPlugins` and `extraKnownMarketplaces`, repository entries override user entries per key.

---

## Publish a plugin

Contributors prepare a normalized plugin payload in their fork; automation validates it; the Mall CODEOWNER reviews and approves it. Contributor scripts never commit, push, merge, or publish on their own.

```bash
npm install --ignore-scripts
npm run submit:prepare -- --source ../my-plugin --category productivity --repository https://github.com/you/my-plugin --ref v1.0.0 --submitted-by @you --evidence "Used in a real project" --apply
npm run submit:validate -- --plugin productivity/my-plugin
npm test
npm run validate
```

Open a pull request using the plugin-submission template. Passing checks means the payload is structurally eligible for review; it does not mean acceptance. See [CONTRIBUTING.md](CONTRIBUTING.md) for evidence, licensing, and review requirements.
Repository admins must configure `main` branch protection to require the **Validate proposed plugins** check and CODEOWNER approval. CODEOWNERS requests review; branch protection enforces it.

## Maintainer operations

Maintainer commands default to dry-run where they write curated payloads:

```bash
# Import a new plugin or preview an upstream refresh
npm run vendor -- --source ../my-plugin --category productivity --repository https://github.com/owner/my-plugin --ref v1.0.0

# Apply after reviewing the dry-run; add --replace for an existing plugin
npm run vendor -- --source ../my-plugin --category productivity --repository https://github.com/owner/my-plugin --ref v1.0.0 --apply

# Refresh first-party catalog, trust, marketplace, README, and gates
npm run maintain -- --curated

# Preview, then enforce validation + CODEOWNER approval on main
npm run admin:configure-approval
npm run admin:configure-approval -- --apply

# Full 48-store network refresh (requires SOURCES_DIR plus GH_TOKEN or GITHUB_TOKEN)
npm run maintain -- --full
```

Review `git diff` before committing. `vendor` never commits or pushes; `maintain` never approves contributor PRs.

---

## Browse the catalog

- [Full catalog index](catalog/INDEX.md) — every plugin, sortable
- [By category](catalog/categories/) — 21 canonical categories plus uncategorized
- [By store](catalog/stores/) — per-source drilldown
- [Trust audit](scoring/TRUST-AUDIT.md) — score distribution and top plugins
- [Source registry](sources/SOURCES.md) — the 48 stores the discovery catalog aggregates

## Top 10 stores by trust

| Rank | Store | Trust | Plugins | Provenance |
| ---: | --- | ---: | ---: | --- |
| 1 | 🏆 [plugin-mall](catalog/stores/plugin-mall.md) | 82 | 358 | 🏆 first-party |
| 2 | [alirezarezvani-claude-skills](catalog/stores/alirezarezvani-claude-skills.md) | 35 | 43 | third-party |
| 3 | [antigravity-awesome-skills](catalog/stores/antigravity-awesome-skills.md) | 35 | 2008 | third-party |
| 4 | [awesome-copilot](catalog/stores/awesome-copilot.md) | 35 | 514 | third-party |
| 5 | [buildwithclaude](catalog/stores/buildwithclaude.md) | 35 | 114 | third-party |
| 6 | [claude-code-plugins-plus-skills](catalog/stores/claude-code-plugins-plus-skills.md) | 35 | 24 | third-party |
| 7 | [context-engineering-kit](catalog/stores/context-engineering-kit.md) | 35 | 13 | third-party |
| 8 | [daymade-claude-code-skills](catalog/stores/daymade-claude-code-skills.md) | 35 | 105 | third-party |
| 9 | [designer-skills](catalog/stores/designer-skills.md) | 35 | 9 | third-party |
| 10 | [dotnet-skills](catalog/stores/dotnet-skills.md) | 35 | 18 | third-party |

## Score distribution

| Range | Plugins | Share |
| --- | ---: | ---: |
| 0-19 | 14 | 0.3% |
| 20-39 | 565 | 13.5% |
| 40-59 | 3241 | 77.6% |
| 60-79 | 0 | 0.0% |
| 80-100 | 358 | 8.6% |

## How trust scoring works

Every plugin gets a 0–100 score from six published signals:

| Signal | Range | Source |
| --- | ---: | --- |
| Provenance | +50 | First-party `plugin-mall` entry |
| Store maintenance | 0–15 | Last upstream commit recency; first-party Mall is pinned to 15 as an editorial prior |
| Store adoption | 0–10 | GitHub stars + contributors; first-party Mall is pinned to 10 as an editorial prior |
| License clarity | 0–10 | OSI-approved=10, clear non-permissive=7 |
| Frontmatter completeness | 0–10 | description + version + lastReviewed presence |
| README presence | 0–5 | README excerpt ≥ 50 chars |

First-party plugins (🏆) rank highest because they earn the +50 provenance bonus. Third-party entries with `installable: true` retain an installation route; reference-only entries are discovery evidence, not install targets.

## Compatibility scope

- **[Alex_ACT_Edition](https://github.com/fabioc-aloha/Alex_ACT_Edition) v4.2.0** heirs install via the guided Mall 3 nested path with Mall 2 root-layout fallback and exact `.install.json` `component_paths`.
- **Edition 3.x and 4.1** heirs are explicitly outside the Mall 3 compatibility claim. Upgrade to Edition v4.2.0 first.
- **Standalone Copilot CLI / Copilot Chat users** (no Edition brain) use the plugin marketplace directly per the steps above.

Public runtime and installation reference: [Alex ACT Core](https://github.com/fabioc-aloha/Alex_ACT_Core). Historical Mall governance records are maintained privately.

## For Edition heirs (advanced)

If you use the Alex ACT Edition brain via Copilot Chat, these Edition prompts wrap the CLI for guided workflows:

| Prompt | Purpose |
| --- | --- |
| `/mall-search <query>` | Search the full trust-scored catalog |
| `/mall-show <name>` | Full metadata + signals for one plugin |
| `/mall-install <name>[@<version>]` | Guided install with `.install.json` component_paths |
| `/mall-refresh <name>` | Compare installed version against upstream default |
| `/mall-contribute` | Propose a local skill for adoption into the Mall |

The prompts live in Edition's `.github/prompts/` and route through `.github/instructions/mall-installation.instructions.md`.

---
*Generated by `scripts/render-catalog.cjs` at 2026-09-03T18:51:08.677Z. Source of truth: `catalog/*.json`. Never hand-edit this README.*
