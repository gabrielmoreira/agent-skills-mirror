---
name: sharepoint-package-spfx-solution
plugin: sharepoint-spfx-authoring
description: Automates production SPFx solution builds using Heft and Webpack and verifies .sppkg package integrity, for both web parts and Form Customizers. Use when an SPFx solution is ready to be built into a deployable package.
allowed-tools: Bash, Read, Write
examples:
  - "pwsh -File scripts/package-spfx-solution.ps1 -SolutionPath path/to/spfx-solution-root"
---

# Package SPFx Solution

Compile, test and package an SPFx solution into a production `.sppkg` ready for an App Catalog.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Do not run `npm audit fix --force`: SPFx pins its toolchain (`@rushstack/heft`, `@microsoft/spfx-web-build-rig`) and forced upgrades break the build.
- Run the pre-flight checklist before building; a production build takes about 4 to 6 minutes, so avoid rebuild cycles.
- Always bump `solution.version` in `config/package-solution.json` before packaging an update, or SharePoint will not prompt for the upgrade.
- Requires Node.js v18 or v22 LTS active in the session (`nvm use 22`). The script builds locally and writes nothing to the tenant.

## Quick start

```powershell
pwsh -File scripts/package-spfx-solution.ps1 -SolutionPath path/to/spfx-solution-root
```

## Workflow

1. Run the pre-flight checklist and bump the solution version.
2. Run the script. It executes `npx heft test --clean --production`, then `npx heft package-solution --production`, then checks for a non-empty `.sppkg`, printing PASS or FAIL per stage.
3. Confirm `sharepoint/solution/<solution-name>.sppkg` exists, then deploy with `sharepoint-deploy-spfx-solution` or `sharepoint-publish-spfx-package`.

## Verification

Both stages report PASS and the `.sppkg` is above 0 KB with no build or linting errors. If you ran the commands directly instead of the script, confirm exit code 0.

## References

- [Pre-flight and build](references/spfx-package-preflight.md): read before building, for the six-point checklist and the direct commands.
- [Naming and versioning](references/spfx-naming-and-versioning.md): read for package, solution and toolbox names and the version rule.
