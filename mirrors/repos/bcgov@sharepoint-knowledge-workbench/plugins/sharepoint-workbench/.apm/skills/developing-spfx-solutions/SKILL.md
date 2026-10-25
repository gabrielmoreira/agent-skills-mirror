---
name: developing-spfx-solutions
plugin: sharepoint-spfx-development
description: Develop, scaffold, test, package, deploy, and activate SharePoint Framework web parts and extensions using the local SPFx toolchain.
allowed-tools: Bash, Read, Write
---

# Developing SPFx Solutions

Use this hub for all SharePoint Framework development work. Select one mode
below, then read its detailed instructions in `references/modes/` before
running a script. All scripts and references in this skill are self-contained.

## Quick start

Run from the skill root:

```powershell
pwsh -File scripts/check-spfx-toolchain.ps1
```

For tenant-facing work, validate SharePoint connectivity first and have the
user run interactive authentication and write operations in their own terminal.
Build locally, package, then choose either App Catalog deployment or direct
package publication as the delivery route.

## Constraints

- Require Node.js 18 or 22 LTS, PowerShell 7, and the project's compatible SPFx
  toolchain; do not force-upgrade pinned SPFx dependencies.
- Ask the mode-specific questions before scaffolding and preserve the generated
  project’s manifest and solution versioning conventions.
- Treat deployment, publication, registration, association, and sample-schema
  provisioning as live tenant operations; confirm target and scope first.
- Use dry-run and confirmation-token safeguards where the selected script
  provides them. Never create ad-hoc replacement scripts.

## Modes

| Mode | Use | Primary command or workflow |
|---|---|---|
| `toolchain-check` | Validate Node, Gulp, Yeoman, and SPFx prerequisites | `pwsh -File scripts/check-spfx-toolchain.ps1` |
| `scaffold-webpart` | Scaffold basic, React, or Master-Detail web parts | Read `references/modes/sharepoint-scaffold-spfx-webpart.md`, `...react-webpart.md`, or `...master-detail-webpart.md` |
| `scaffold-extension` | Scaffold Application Customizer, Form Customizer, or ListView Command Set | Read the matching `references/modes/sharepoint-develop-spfx-*.md` |
| `serve-workbench` | Configure and launch the hosted SharePoint workbench | Read `references/modes/sharepoint-setup-spfx-hosted-workbench.md` |
| `package` | Build and package an `.sppkg` solution | `pwsh -File scripts/package-spfx-solution.ps1 -SolutionPath <path>` |
| `deploy` | Deploy an `.sppkg` to a tenant or site App Catalog | Read the deploy or publish mode instructions before running the selected script |
| `request-catalog` | Request or provision a Site Collection App Catalog | Read `references/modes/sharepoint-request-site-collection-app-catalog.md` |

Detailed mode documents preserve the original flags, examples, prompts, and
acceptance criteria. The mode documents are guidance; the scripts are the
executable source of truth.
