# Conventions — Naming & File Organization

**Scope**: `pds-vscode-extension/` module reference
**Last Updated**: 2026-05-27

> **→ Root [`.ai/conventions.md`](../../.ai/conventions.md)** — This file is authoritative for all directories in this project.

## Project-Specific Rules

### Directory Naming

- Dev documentation: `.dev-docs/`
- AI instructions: `.ai/`

### File Naming

| Context | Case | Example |
|---------|------|---------|
| JavaScript files | `camelCase.js` | `role-panel.js`, `build-panel.js` |

### Documentation

- User-facing guides: numbered `kebab-case.md`
- Root meta-files: `UPPER-KEBAB-CASE.md`

---

## Code Organization

| File | Responsibility |
|------|----------------|
| `extension.js` | VS Code extension activation, panel commands |
| `build-panel.js` | PDS Build panel (ESP-IDF wrapper) |
| `deploy-panel.js` | Flash and deploy panel |
| `role-panel.js` | Role editor command registration |
| `role-webview.js` | Role editor webview HTML assembly |
| `role-webview-script.js` | Role editor webview JavaScript logic |
| `role-webview-styles.js` | Role editor CSS styles |
| `role-actions.js` | Message handlers for role editor |
| `role-data.js` | Static data: PDS_FB_BLOCKS, COMPONENTS, PREFABS |
| `role-fs.js` | File system helpers (board scanning, saved roles) |
| `pipeline-panel.js` | Pipeline push panel |
| `publish-panel.js` | Publish Role command |
| `sidebar-provider.js` | Sidebar tree view |
| `utils.js` | Workspace utilities |

### Technology Stack

- **Primary**: Node.js + TypeScript for VS Code extension
- **UI Framework**: Webview HTML/CSS/JavaScript

---

## Credential Management

> **→ Root [`.ai/credentials.md`](../../.ai/credentials.md)** — Global credential rules apply.

| File | Commit? | Notes |
|------|---------|-------|
| `.env` | ❌ | Secrets (DATABASE_URL, JWT_SECRET) |
| `.env.example` | ✅ | Template with placeholder values |

---

## Webview Panel Architecture

The VS Code extension uses webviews for interactive panels:
- **Panel creation**: Registered in `extension.js`
- **HTML assembly**: Static strings in `role-webview.js`, `build-panel.js`, etc.
- **Logic**: Runs inside the webview iframe (isolated from extension context)

**Critical**: `role-webview-script.js` must be loaded via `fs.readFileSync`, NOT `require()`. The UI will render but have zero interactivity if this rule is violated.