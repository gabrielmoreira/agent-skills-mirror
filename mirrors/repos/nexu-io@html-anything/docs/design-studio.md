# OpenMotion Design Studio

Design Studio lets you create, preview, annotate, version, import and export HTML design deliverables while delegating all AI generation and code iteration to your external coding Agent (Codex, Claude Code or any MCP client) over OpenMotion's local MCP server. OpenMotion runs no internal design agent.

## Scenarios

| Scenario | Route | Output | Editor mode |
| --- | --- | --- | --- |
| `prototype` | `?page=design&scene=prototype` | Responsive interactive HTML (`index.html`) | Desktop / Tablet (`820×1180`) / Mobile (`390×844`) |
| `mobile-app` | `?page=design&scene=mobile-app` | Mobile-first interactive HTML app (`index.html`) | Defaults to Mobile (`390×844`) with Tablet / Desktop toggle |
| `deck` | `?page=design&scene=deck` | 1920×1080 single-file HTML presentation | Slide thumbnail rail, `od:slide` protocol, speaker notes, Present + Presenter popup |
| `document` | `?page=design&scene=document` | Print-ready semantic HTML (`@media print`) | Page/print preview, PDF export |
| `web-clone` | `?page=design&scene=web-clone` | Functional HTML rebuild from reference | Responsive HTML |
| `live-artifact` | `?page=design&scene=live-artifact` | `data.json`-backed HTML dashboard | Refreshable live preview |
| `webgl` | `?page=design&scene=webgl` | WebGL2 interactive shader/3D page | Sandboxed preview |
| `projects` | `?page=design&scene=projects` | All Design Studio projects + Trash | Grid with live thumbnails, import & export |

Image scenes (`text-to-image`, `image-edit`) remain available directly alongside these tabs in Design Studio. Motion design and HyperFrames route to Motion Studio; Video and Audio route to Cinema Studio and Sound Studio.

## Storage layout

Design Studio projects are stored independently of Motion Studio's HyperFrames catalog under `<workspace data dir>/design/`:

```text
<data>/design/
  projects.json          # catalog: id, title, scenario, entry, designSystemId, templateId, timestamps, trashedAt
  projects/<uuid>/       # plain HTML, CSS, JS, JSON and media files
  versions/<uuid>.json   # append-only vN snapshots (source: create | agent | manual | restore | import)
  blobs/<sha256>         # retained content-addressed file bytes
  comments/<uuid>.json   # element, region and pen annotations
  requests/<sha256>.json # requestId idempotency receipts
  design.lock            # cross-process write lock
```

Every write verifies `expectedRevision` (SHA-256 of sorted project files) and appends a new immutable `vN` version. Restoring `v3` while on `v5` writes `v3`'s bytes as `v6` and retains `v4` and `v5`.

## MCP tools & annotation loop

Four public MCP tools back Design Studio (using the same `DesignProjects` domain service as the `/motion-api/design/*` HTTP adapter):

1. `openmotion_design_catalog` (read-only): list/read scenarios, starter templates (`library/design/templates`), design systems (`library/design/systems`), design Skills (`library/design/skills`) and craft rules (`library/design/craft`).
2. `openmotion_design_project`: `create`, `list`, `get`, `rename`, `duplicate`, `trash`, `restore`, `delete` (trashed only), `open` (returns `previewUrl` and `editorUrl`), `open_in`, `export` and `import`.
3. `openmotion_design_edit`: `read_file` (paged), `write` (atomic multi-file + deletes with `expectedRevision` → new `vN`), `list_versions`, `restore_version`.
4. `openmotion_design_comments`: `list`, `create`, `update` (`open` → `resolved` with `expectedCommentRevision`), `delete`.

Workflow guide URI: `openmotion://workflow/design/start` (references: `scenarios`, `iterate`, `export`, `systems`).

**Annotation iteration loop:** open a project in the HTML editor → pick an element, drag a region or draw pen marks → click **Copy to Agent** → paste the `<attached-preview-comments>` brief into Codex or Claude Code. The Agent reads open comments, writes scoped HTML edits via `openmotion_design_edit`, resolves addressed comments and calls `openmotion_design_project(action="open")`. The editor polls `/motion-api/design/projects/:id/state` and refreshes automatically when the revision changes.

## Import, export & local editors

- **Export formats:** `zip` (visible project tree), `open-design` (Open Design compatible ZIP with `DESIGN-MANIFEST.json`, `DESIGN-HANDOFF.md` and `.open-design/project.json`), `html` (standalone single file with local CSS/JS/images inlined), `pdf` and `png` (rendered via headless Chrome / `puppeteer-core`), and `pptx` (deck slides captured at 1920×1080 with speaker notes via `pptxgenjs`).
- **Import:** accepts Open Design export ZIPs, Claude Design ZIPs, OpenMotion design ZIPs, or local project folders (reading `.open-design/project.json` and `DESIGN-MANIFEST.json` when present).
- **Open in:** detects Cursor, VS Code, Windsurf, Zed, Antigravity, WebStorm, Xcode, Finder/Explorer/File Manager, Terminal and Warp and opens the project folder directly.

## Current limits

- OpenMotion does not embed a chat/coding agent inside Design Studio; creation and AI iteration happen in your connected MCP Agent.
- Visual exports (`pdf`, `png`, `pptx`) require a local Chrome/Chromium executable (`browserExecutable()`).
- PPTX export renders each slide as a high-resolution image with attached speaker notes (editable shape conversion via `dom-to-pptx` is not bundled).
- Cloud public sharing and Vercel/Cloudflare deployment are not part of this local service.
