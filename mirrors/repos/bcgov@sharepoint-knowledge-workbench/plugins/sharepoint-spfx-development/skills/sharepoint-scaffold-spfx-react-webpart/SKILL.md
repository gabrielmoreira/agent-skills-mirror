---
name: sharepoint-scaffold-spfx-react-webpart
plugin: sharepoint-spfx-development
description: Scaffolds an enterprise-grade React 17/18 SPFx Web Part with Fluent UI 8/9, PnPjs v4 cross-site context, Tailwind CSS, self-healing migration GUID recovery and robust state management. Use for complex, interactive components such as document catalogues, favourites portals, multi-list dashboards or cross-site aggregators.
allowed-tools: Bash, Read, Write
examples:
  - "python3 scripts/scaffold_spfx_react_app.py --spec app_spec.json --output-dir path/to/spfx-project/src/webparts/documentCatalogue"
---

# Scaffold SPFx React App

Scaffold an Enterprise React SPFx web part with PnPjs v4, Tailwind and self-healing list-GUID recovery.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- The generator is local (Python 3.8+) and writes only to `--output-dir`. The surrounding project needs Node.js LTS (v18 or v22) and SPFx 1.20+ (Heft / Webpack).
- Tailwind must be compiled before the SPFx build; add the `build:tailwind` step to `package.json` so `npm run build` runs it first.
- For lists promoted across DEV, TEST and PROD, rely on the self-healing GUID recovery (fall back to list titles); do not hardcode list GUIDs.
- Run from this skill's root.

## Quick start

```bash
python3 scripts/scaffold_spfx_react_app.py --spec path/to/app_spec.json --output-dir path/to/spfx-project/src/webparts/documentCatalogue
```

## Workflow

1. Write `app_spec.json` with `webPartName`, `title` and `description`.
2. Run the generator.
3. Add the Tailwind pre-build command to `package.json` (see the details reference).
4. Run `npm run build`.

## Verification

The output holds the web part `.ts` and manifest, `components/` (the React component and `pnpjsConfig.ts`) and `style/` (Tailwind input and output). `npm run build` succeeds.

## References

- [React app details](references/react-app-scaffold-details.md): read for the architecture, the spec, the outputs and the Tailwind `package.json` snippet.
- [Tailwind integration](references/SPFX-TAILWIND-INTEGRATION-GUIDE.md): read for the full Tailwind CLI setup.
- [PnPjs v4 cross-site architecture](references/SPFX-PNPJS-V4-CROSS-SITE-ARCHITECTURE.md): read for hub-and-spoke data patterns.
- [Self-healing migration](references/SPFX-SELF-HEALING-MIGRATION-GUIDE.md): read for list GUID recovery strategies.
