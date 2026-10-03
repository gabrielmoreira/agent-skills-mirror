---
name: sharepoint-scaffold-spfx-webpart
plugin: sharepoint-spfx-authoring
description: Guides scaffolding of any new, generic SPFx web part from scratch by confirming toolchain dependencies, interactively gathering the web part's requirements (name, purpose, data source, framework, configurability), running the official Yeoman generator, and customizing the generated files. Use when no more specific scaffold skill fits.
allowed-tools: Bash, Read, Write
examples:
  - "pwsh -File scripts/check-spfx-toolchain.ps1"
---

# Scaffold SPFx Web Part

A generic, interactive workflow for a new SPFx web part. It assumes no specific layout, data source or content shape.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Do not guess the web part's shape. Ask the clarifying questions, one at a time with defaults, before running the generator, and do not proceed with unstated assumptions about layout or data source.
- Do not scaffold on an unsupported Node version: require Node v18 or v22 (`scripts/check-spfx-toolchain.ps1` checks Node, npm, `yo` and `@microsoft/generator-sharepoint`).
- Escape any user-editable or list-sourced string before inserting it into `this.domElement.innerHTML` (XSS).
- For a master-detail dashboard, a React app or a form, use the more specific scaffold skills. Local work only; nothing is written to the tenant.

## Quick start

```powershell
pwsh -File scripts/check-spfx-toolchain.ps1
```

## Workflow

1. Confirm the toolchain.
2. Ask what the web part is called, what it does, where its data comes from, whether it needs a property pane, whether it needs React, and where the project lives.
3. Create the folder and run `yo @microsoft/sharepoint` (SharePoint Online only, WebPart, a PascalCase name, a one-line description, the framework from step 2, `Minimal` template).
4. Customize the web part `.ts`, `.module.scss`, `.manifest.json` and `loc/` strings to match the requirements.
5. `npm install` and `npm run build`; then package and deploy with the packaging and deployment skills.

## Verification

The build exits 0 and produces `sharepoint/solution/<solution-name>.sppkg`. The manifest title and description match the intended toolbox entry.

## References

- [Web part details](references/webpart-scaffold-details.md): read for the questions to ask, the exact Yeoman prompts and the customization steps.
- [Naming and versioning](references/spfx-naming-and-versioning.md): read for the solution name versus the toolbox title authors see.
