# Export and Open Design Round-Trip

## Exporting a design project

Call `openmotion_design_project` with `action="export"`, `projectId`, `format`, and optional `versionId` / `filePath` / `outputPath`:

| Format | Output | Notes |
| --- | --- | --- |
| `zip` | Standard ZIP of visible project files | Portable source archive |
| `open-design` | Open Design compatible ZIP | Includes visible files plus `DESIGN-MANIFEST.json` (`open-design.design-manifest.v1`), `DESIGN-HANDOFF.md` and `.open-design/project.json` for direct import into Open Design |
| `html` | Standalone single `.html` file | Local stylesheets, scripts and images inlined |
| `pdf` | Rendered PDF via headless Chrome | Decks render at `1920×1080` per slide; documents honor `@media print` |
| `png` | Rendered PNG screenshot via headless Chrome | Full page for prototypes/documents, `1920×1080` for decks |
| `pptx` | PowerPoint `.pptx` for slide decks | Captures every slide via the deck protocol and attaches speaker notes |

## Importing from Open Design or local ZIP/folders

Call `openmotion_design_project` with `action="import"` and `sourcePath` pointing to a `.zip` archive (Open Design export ZIP, Claude Design ZIP, or OpenMotion design ZIP) or a local project folder (including `.open-design/project.json`). Import creates a new independent project with an initial `v1` snapshot and infers its scenario and entry file.

## Opening in external editors

Call `openmotion_design_project` with `action="open_in"`, `projectId` and optional `editorId` (`cursor`, `vscode`, `windsurf`, `zed`, `antigravity`, `webstorm`, `xcode`, `finder`, `terminal`, `warp`). Omitting `editorId` lists detected local apps.
