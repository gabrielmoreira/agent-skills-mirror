---
name: linux-desktop
description: Use when the user asks Agent Zero to operate the built-in Linux Desktop, XFCE apps, LibreOffice GUI apps, file manager, terminal, or visual desktop workflows.
version: "0.3.0"
author: "Agent Zero Core Team"
tags: ["linux", "desktop", "xfce", "libreoffice", "gui", "files", "terminal"]
triggers:
  - "Linux desktop"
  - "Desktop GUI"
  - "XFCE"
  - "LibreOffice GUI"
  - "file manager"
  - "terminal app"
  - "use the OS"
allowed_tools:
  - document_artifact
  - code_execution_tool
---

# Linux Desktop Interface

Use the Desktop as a full Linux GUI when the user explicitly needs a visual workflow, an installed desktop app, or manual layout polish that is awkward through structured file edits alone. Agent Zero may warm the persistent Desktop runtime during initial startup, but visible Desktop/canvas use remains opt-in. The Desktop is opt-in at the UI level: do not open the canvas just because the user asks for a document. Use structured tools first for deterministic content changes, then use the Desktop for inspection, GUI-only actions, and final visual confirmation.

## Operating Model

1. Prefer `document_artifact` for creating, reading, and editing Markdown, DOCX, XLSX, and PPTX files.
2. Treat Markdown as first-class. For writing, notes, reports, and drafts with no explicit binary Office requirement, create Markdown and use the custom Markdown editor when the user opens the canvas.
3. Use the Desktop only when the user asks for the Desktop, a GUI app, binary Office visual work, or visual confirmation.
4. Never open the Desktop/canvas automatically from a tool result if the user has not opened it. Offer the explicit Open in canvas action instead.
5. Launch common apps from the Desktop icons, the header buttons, or `scripts/desktopctl.sh`.
6. Use the external Agent Zero Browser for web browsing. Do not launch an operating-system browser in this version.
7. Verify GUI work by observing the desktop state, checking window titles, and saving the file before reporting success.

## Control Flow

Use the helper script when the Desktop is already open and you need reliable app launches, clicks, keystrokes, or window checks from the agent shell:

```bash
plugins/_office/skills/linux-desktop/scripts/desktopctl.sh check
plugins/_office/skills/linux-desktop/scripts/desktopctl.sh launch calc
plugins/_office/skills/linux-desktop/scripts/desktopctl.sh windows LibreOffice
plugins/_office/skills/linux-desktop/scripts/desktopctl.sh focus LibreOffice
plugins/_office/skills/linux-desktop/scripts/desktopctl.sh key ctrl+s
```

The script targets the persistent `agent-zero-desktop` X display, sets `DISPLAY`, `XAUTHORITY`, and `HOME` to the XFCE profile, then uses `xdotool` for input. Startup normally prepares this session. If `check` fails during explicit Desktop work, report that the Desktop runtime is not ready instead of installing packages ad hoc.

For direct app launches without coordinates:

```bash
plugins/_office/skills/linux-desktop/scripts/desktopctl.sh launch writer
plugins/_office/skills/linux-desktop/scripts/desktopctl.sh launch calc
plugins/_office/skills/linux-desktop/scripts/desktopctl.sh launch impress
plugins/_office/skills/linux-desktop/scripts/desktopctl.sh launch terminal
plugins/_office/skills/linux-desktop/scripts/desktopctl.sh launch settings
plugins/_office/skills/linux-desktop/scripts/desktopctl.sh open-path /a0/usr/workdir
```

For live spreadsheet coworking, use the Calc helper instead of hand-written UNO snippets:

```bash
plugins/_office/skills/linux-desktop/scripts/desktopctl.sh calc-set-cell /a0/usr/workdir/example.xlsx Sheet1 B2 "Cowork verified live"
```

This opens the workbook in the visible Desktop Calc session if needed, changes the cell through LibreOffice, saves the workbook, and verifies the `.xlsx` on disk. Because the edit happens through the running LibreOffice session, the user can see the sheet update without refreshing the Desktop surface.

For coordinate actions after observing the Desktop:

```bash
plugins/_office/skills/linux-desktop/scripts/desktopctl.sh click 120 180
plugins/_office/skills/linux-desktop/scripts/desktopctl.sh dblclick 120 180
plugins/_office/skills/linux-desktop/scripts/desktopctl.sh type "Text to enter"
plugins/_office/skills/linux-desktop/scripts/desktopctl.sh location
```

When browser automation is available, the higher-level QA flow is:

1. Open `http://127.0.0.1:32080`.
2. Open the Desktop canvas from the UI or with `Alpine.store("rightCanvas").open("office")`.
3. Use browser mouse events into the Xpra iframe for real user-path testing.
4. Cross-check with `desktopctl.sh location` and `desktopctl.sh windows PATTERN`.
5. Capture the browser screenshot as visual evidence.

## Desktop Locations

The Desktop exposes stable folders for common user work:

- `Workdir` -> configured Agent Zero workdir (default `/a0/usr/workdir`)
- `Projects` -> `/a0/usr/projects`
- `Skills` -> `/a0/usr/skills`
- `Agents` -> `/a0/usr/agents`
- `Downloads` -> `/a0/usr/downloads`

Use these folders when the user asks to inspect or manipulate project files, skills, agent profiles, or downloaded artifacts from the GUI.

## App Map

- `LibreOffice Writer`: word processing and DOCX layout.
- `LibreOffice Calc`: spreadsheets, formulas, tables, charts.
- `LibreOffice Impress`: presentations and slide polish.
- `Workdir`: graphical file management with Thunar at the configured Agent Zero workdir (default `/a0/usr/workdir`).
- `Terminal`: shell work inside the Agent Zero runtime.
- `Settings`: XFCE system settings.

## Practical Rules

- Keep installs inside normal plugin hook or image install flows; do not install packages ad hoc just to complete one desktop action.
- The persistent Desktop can be running in the background while the canvas stays closed; that is expected and still respects user ownership of the visible UI.
- Do not treat closing a document tab as closing the whole Desktop. The Desktop is persistent while Agent Zero is running.
- Save before sync or final verification when the GUI app has edited a file.
- If a GUI action is flaky, switch to structured file editing for content and return to the Desktop only for visual confirmation.
- For live Calc edits that the user should see immediately, prefer `desktopctl.sh calc-set-cell FILE SHEET CELL VALUE`.
- For enterprise workflows, leave printing available.
