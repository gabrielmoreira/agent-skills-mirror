---
name: sharepoint-scaffold-spfx-webpart
plugin: sharepoint-spfx-authoring
description: Guides scaffolding of any new, generic SPFx web part from scratch -- confirming toolchain dependencies, interactively gathering the web part's requirements (name, purpose, data source, framework, configurability), running the official Yeoman generator, and customizing the generated files accordingly.
allowed-tools: Bash, Read, Write
---

# scaffold-spfx-webpart

## Overview

This skill is a generic, interactive scaffolding workflow for a new SPFx web part: confirm the
toolchain is ready, ask the requester what the web part needs to do, run the official Yeoman SPFx
generator with the answers, and then guide customization of the generated boilerplate to match.
It intentionally does not assume any specific layout, data source, or content shape.

## Toolchain Requirements

- **Node.js**: LTS version (v18 or v22)
- **Yeoman + SPFx generator**: `yo` and `@microsoft/generator-sharepoint`
- **SPFx**: 1.20+ (Heft / Webpack build toolchain)
- **PowerShell 7** (`pwsh`) with `PnP.PowerShell` — only needed later, for the
  `deploy-spfx-solution` skill.

## Core Workflow

### Step 1: Confirm Dependencies

Before scaffolding anything, verify the toolchain is present and at a compatible version:

```powershell
pwsh -File scripts/check-spfx-toolchain.ps1
```

This checks Node.js (expects v18.x or v22.x), npm, `yo`, and
`@microsoft/generator-sharepoint`, printing PASS/FAIL per dependency and exiting non-zero if any
required dependency is missing. If Node is missing or on an incompatible major version,
install/select it first (e.g. via `nvm install 22 && nvm use 22`) and re-run the check before
proceeding — do not attempt to scaffold on an unsupported Node version.

### Step 2: Ask Clarifying Questions About the Web Part

Do not guess the web part's shape. Ask the requester (one question at a time, offering sensible
defaults) enough to decide the generator prompts and the initial code structure, for example:

- What should the web part be called (solution name and web part name)?
- What is its purpose / what should it display or do, in a sentence or two?
- Where does its content come from — a static/config-driven list, a SharePoint list via REST,
  an external API, or purely static markup?
- Does it need to be user-configurable after deployment (property pane fields), or is a fixed
  layout fine?
- Does the UI need component state/interactivity complex enough to warrant **React**, or is
  plain DOM manipulation (`No JavaScript framework`) sufficient?
- Where should the new project live on disk (target directory)?

Use the answers to fill in the Yeoman prompts and the customization step below — do not proceed
past this step with unstated assumptions about layout or data source.

### Step 3: Create the Project Directory and Run the Generator

```powershell
md path/to/<solution-folder>
cd path/to/<solution-folder>
yo @microsoft/sharepoint
```

Answer the prompts using Step 2's answers:
- **Solution name**: defaults to the folder name — accept, or provide a kebab-case name.
- **Target for deployment**: `SharePoint Online only (latest)`.
- **Component type**: `WebPart`.
- **Web part name**: PascalCase name for the web part.
- **Web part description**: short one-line description from Step 2.
- **Framework**: `No JavaScript framework` or `React`, per Step 2's answer.
- **Template**: `Minimal` unless a richer starting template was explicitly requested.

This generates the full solution shell (`package.json`, `config/`, `tsconfig.json`,
`src/webparts/<webPartName>/`) under the target directory.

### Step 4: Customize the Generated Web Part

Edit the generated files under `src/webparts/<webPartFolder>/` to implement Step 2's requirements:
1. `<WebPartName>WebPart.ts` — implement `render()` for the described content/behavior, and
   `getPropertyPaneConfiguration()` if the requester wants post-deployment configurability.
2. `<WebPartName>WebPart.module.scss` — style the rendered markup using CSS module classes
   (avoid inline styles; keep class names scoped to the module).
3. `<WebPartName>WebPart.manifest.json` — set `preconfiguredEntries[0].title`, `.description`,
   and `officeFabricIconFontName` to match the web part's purpose.
4. `loc/en-us.js` / `loc/mystrings.d.ts` — add any user-facing strings referenced from the
   property pane or rendered markup.

> [!NOTE]
> Escape any user-editable or list-sourced string values before inserting them into
> `this.domElement.innerHTML` (XSS mitigation).

### Step 5: Verify the Solution Builds

```powershell
cd path/to/<solution-folder>
npm install
npm run build
```

Confirm the build exits 0 and produces `sharepoint/solution/<solution-name>.sppkg`.

### Step 6: SPFx Naming Architecture (Solution vs. Web Part Selector)

Ensure clarity across the three naming levels:
- **Package / Solution Name** (`config/package-solution.json` -> `solution.name`): Displayed in the App Catalog and Site Contents.
- **Web Part UI Selector Title** (`src/webparts/<name>/<Name>WebPart.manifest.json` -> `preconfiguredEntries[0].title.default`): 🌟 This is the exact name authors see when clicking `+` in the SharePoint page editor.
- **Toolbox Category** (`preconfiguredEntries[0].group.default`): Defaults to `Advanced` or custom category.

### Step 7: Next Steps

Proceed to `package-spfx-solution` (if not already covered by Step 5's `npm run build`) and then
`deploy-spfx-solution` / `publish-spfx-package` to upload and enable the package in a Site Collection or Tenant App
Catalog.

