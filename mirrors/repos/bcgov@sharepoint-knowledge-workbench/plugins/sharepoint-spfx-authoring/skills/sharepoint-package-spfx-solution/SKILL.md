---
name: sharepoint-package-spfx-solution
plugin: sharepoint-spfx-authoring
description: Automates production SPFx solution builds using Heft/Webpack and verifies .sppkg package integrity.
allowed-tools: Bash, Read, Write
---

# package-spfx-solution

## Overview

This skill provides step-by-step instructions for compiling, testing, and packaging an SPFx solution into a production `.sppkg` package ready for deployment to a SharePoint App Catalog.

It applies to both:
- SPFx web parts
- SPFx Form Customizers (including the form customizer package we just built successfully)

## Prerequisites

- **Node.js**: v18 or v22 LTS
- **Terminal Pathing**: Ensure Node.js v22/v18 is active in your terminal session (`nvm use 22`).

## Core Workflow

### Step 1: Navigate to the SPFx Project Directory

```bash
cd path/to/spfx-solution-root
```


> [!WARNING]
> **Do NOT run `npm audit fix --force`**: SPFx projects use strictly pinned toolchain packages (`@rushstack/heft`, `@microsoft/spfx-web-build-rig`). Running forced dependency upgrades will break the Heft build toolchain.

### Step 2: Execute Production Build, Package & Verify

Run the bundled helper script, pointing it at the SPFx solution root:

Use the same flow for a web part or a Form Customizer solution. The packaging command is the same:

```powershell
pwsh -File scripts/package-spfx-solution.ps1 -SolutionPath path/to/spfx-solution-root
```

The script runs the same Heft/Webpack production build and package steps for both component types.

```powershell
pwsh -File scripts/package-spfx-solution.ps1 -SolutionPath path/to/spfx-solution-root
```

This runs `npx heft test --clean --production` followed by
`npx heft package-solution --production`, then confirms a non-empty `.sppkg` file exists under
`sharepoint/solution/`, printing PASS/FAIL for each stage.

*(Equivalently, if you prefer to run the underlying commands directly instead of the script):*
```powershell
npx heft test --clean --production && npx heft package-solution --production
```

*(Or via npm script defined in package.json):*
```bash
npm run build
```

### Step 3: Verify Output Artifacts

The helper script in Step 2 already verifies the package; if running the commands manually instead,
confirm the command completed with exit code 0 and generated the final `.sppkg` file at:

```text
sharepoint/solution/<solution-name>.sppkg
```

Check that the generated package size is >0 KB and contains no build or linting errors.

## SPFx Naming & Versioning Architecture

Before building and packaging, verify that all three naming levels and versions are aligned.

This applies equally to web parts and Form Customizers; the only difference is the manifest location and component type:
- Web part: `src/webparts/<name>/<Name>WebPart.manifest.json`
- Form Customizer: `src/extensions/<name>/<Name>.manifest.json`


| Layer | Configuration File | Purpose & Impact |
| :--- | :--- | :--- |
| **Package File** | `config/package-solution.json` (`paths.zippedPackage`) | Physical `.sppkg` file name generated in `sharepoint/solution/`. |
| **Solution Name** | `config/package-solution.json` (`solution.name`) | Display title in **App Catalog** and **Site Contents > Add an App**. |
| **Solution Version** | `config/package-solution.json` (`solution.version`) | Increment version (e.g. `1.0.6.0` -> `1.0.7.0`) whenever updating code or manifests so SharePoint prompts for upgrade. |
| **Web Part Title** | `src/webparts/<name>/<Name>WebPart.manifest.json` (`preconfiguredEntries[0].title.default`) | 🌟 **The actual name displayed to authors in the SharePoint page `+` toolbox selector.** |
| **Web Part Description** | `src/webparts/<name>/<Name>WebPart.manifest.json` (`preconfiguredEntries[0].description.default`) | Subtitle/tooltip shown under the title in the toolbox. |
| **Toolbox Category** | `src/webparts/<name>/<Name>WebPart.manifest.json` (`preconfiguredEntries[0].group.default`) | Group header in the toolbox (e.g., `Advanced`). |

## Pre-Packaging Code & Configurability Pre-Flight Checklist

Because SPFx production compilation and bundling is a compute-intensive operation (typically taking 4–6 minutes), **always perform a pre-flight code and configuration audit before initiating a build** to avoid costly rebuild cycles:

### 1. Dynamic Site Path Resolution (No Hardcoded URLs)
- Audit `*WebPart.ts` and `*Props.ts` for hardcoded site relative URLs (e.g. `/sites/AG-BCPS-CrownNET`).
- **Standard**: Site paths must default dynamically to the current hosting web (`this.context.pageContext.web.serverRelativeUrl`) or be fully configurable via property pane fields.

### 2. Unlocked Property Pane Configuration
- Verify that configuration fields in `getPropertyPaneConfiguration()` (such as `sourceSiteUrl`, list dropdowns, view filters) are **editable** and not permanently set to `disabled: true`.
- Implement `onPropertyPaneFieldChanged` handlers to reload dynamic dropdowns whenever site path or list sources are modified.

### 3. Self-Healing Auto-Binding
- Ensure web parts implement auto-binding fallbacks on mount/initialization:
  - If a required list GUID property (`applicationsListId`, `libraryId`, etc.) is empty or invalid, query the target site's lists and automatically bind to matching default list names (`Applications`, `Documents`, etc.).

### 4. Semantic Version Bump
- Always increment `solution.version` in `config/package-solution.json` (e.g. `1.0.8.0` -> `1.0.9.0`) so SharePoint recognizes and prompts for the updated package immediately upon deployment.

### 5. Web Part UI Selector Title Check
- Confirm that `preconfiguredEntries[0].title.default` in `<WebPart>.manifest.json` matches the intended user-facing title (what authors see when clicking `+` in SharePoint).

### 6. Relational Lookup & PnPjs Schema Alignment
- When web parts read/write to SharePoint **Lookup Columns** (such as join tables like `My Favourite Apps -> ApplicationId`):
  - **Write discipline**: SharePoint REST API / PnPjs requires writing to `<LookupInternalName>Id` (e.g. `ApplicationIdId: 100`). Always implement dual-mode write (`ApplicationIdId` first, fallback to `ApplicationId` for numeric schemas).
  - **Read discipline**: Ensure expand queries select both ID and text fields (`items.select('Id', 'ApplicationId/ID', 'ApplicationId/Title', 'ApplicationIdId').expand('ApplicationId')`).
  - **Relational Integrity**: Enforce `RelationshipDeleteBehavior = Restrict` and `Indexed = $true` on lookup column definitions to protect catalog integrity.


