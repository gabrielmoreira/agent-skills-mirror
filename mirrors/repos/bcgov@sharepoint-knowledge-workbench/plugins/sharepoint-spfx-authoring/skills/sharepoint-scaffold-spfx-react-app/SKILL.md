---
name: sharepoint-scaffold-spfx-react-app
plugin: sharepoint-spfx-authoring
description: Scaffolds an enterprise-grade React 17/18 SPFx Web Part with Fluent UI 8/9, PnPjs v4 cross-site context, Tailwind CSS, self-healing migration GUID recovery, and robust state management.
allowed-tools: Bash, Read, Write
---

# scaffold-spfx-react-app

## Overview

When building complex, interactive SharePoint Online components (such as document catalogues, personal favourites portals, multi-list dashboards, or cross-site data aggregators), this skill scaffolds an **Enterprise React SPFx Web Part**.

This architecture incorporates enterprise patterns:
- **PnPjs v4 (`@pnp/sp` 4.18+)**: Centralized singleton with cross-site collection query support (`getWeb(url)`).
- **Tailwind CSS 3**: Clean CLI preprocessing alongside Heft/Webpack without build ejecting.
- **Fluent UI 8/9 & Theme Adaptation**: Automatic adaptation to SharePoint section background colors.
- **Self-Healing GUID Recovery**: Resilient fallback to list titles when web parts are promoted across DEV/TEST/PROD environments.

---

## Toolchain Requirements

- **Node.js**: LTS version (v18 or v22)
- **SPFx**: 1.20+ (Heft / Webpack build toolchain)
- **Python**: 3.8+ (for manifest generator scripts)

---

## Core Workflow

### Step 1: Create Layout Specification (`app_spec.json`)

```json
{
  "webPartName": "DocumentCatalogue",
  "title": "Corporate Document Catalogue",
  "description": "Interactive document browser with personal favouriting and metadata filtering."
}
```

### Step 2: Run Generator

```bash
python ../scripts/scaffold_spfx_react_app.py --spec path/to/app_spec.json --output-dir path/to/spfx-project/src/webparts/documentCatalogue
```

### Step 3: Setup Tailwind CSS Build

Ensure your `package.json` contains the pre-build Tailwind compilation command:

```json
{
  "scripts": {
    "build:tailwind": "tailwindcss -i ./src/webparts/documentCatalogue/style/tailwind.css -o ./src/webparts/documentCatalogue/style/tailwind.output.css --minify",
    "build": "npm run build:tailwind && heft test --clean --production && heft package-solution --production"
  }
}
```

### Step 4: Verify & Build

```bash
npm run build
```

---

## References

- `references/SPFX-TAILWIND-INTEGRATION-GUIDE.md` — Complete Tailwind CLI setup.
- `references/SPFX-PNPJS-V4-CROSS-SITE-ARCHITECTURE.md` — Hub-and-Spoke data patterns.
- `references/SPFX-SELF-HEALING-MIGRATION-GUIDE.md` — List GUID recovery strategies.