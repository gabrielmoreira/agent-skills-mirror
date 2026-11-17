# Offline project sharing

Use **All projects** at the bottom of the project sidebar to search and open projects. Check any rows to export that selection as one ZIP, or use Export all projects with no rows checked. The header checkbox selects the currently visible search results. A project's action menu also offers **Export project**. **Import projects** accepts a ZIP and adds independent copies after validation. The import does not select a project, overwrite existing files or merge edits. Open a copy from the list to continue editing it.

Project ZIPs contain editable source, local media, fonts and their licenses, and Studio manual-edit/motion manifests. Export waits for Studio saves and snapshots the checked source revisions. It then parses the finished ZIP and validates its projects in a clean folder using the same rules as import. Building and validating the ZIP does not hold the workspace lock, so other project saves can proceed. If validation fails, no download is created. ZIP sharing is separate from rendering MP4 and does not require cloud collaboration or a model account. Current-project export and multi-project export use the same format.

## Import from HyperFrames

Already have an editable HyperFrames project? Import its ZIP into OpenMotion, then continue editing in Studio or with your connected Agent. You can reuse the existing composition, timing and local assets to get started without rebuilding the project.

1. **Prepare the project folder.** Include `index.html` and the local assets referenced by the composition. Include the project configuration when one exists. Keep relative paths intact, including CSS, JavaScript, images, video, audio, fonts and their licenses.
2. **Compress it as a ZIP.** In Finder, right-click the project folder and choose **Compress**; on Windows, use **Compress to ZIP file**. Include one project, either directly at the ZIP root or inside one enclosing folder. The ZIP and its expanded contents must each fit within 500 MB.
3. **Import into OpenMotion.** Open **All projects** at the bottom of the sidebar, choose **Import projects**, and select the ZIP. The sidebar's **Import projects** button uses the same flow. OpenMotion validates the package and adds an independent copy to the list.
4. **Open the imported project.** Select the new copy from the list, play the preview, and check media, fonts and sound. Continue editing in Studio or ask your connected Agent to make changes. The original folder and existing OpenMotion projects remain unchanged. Use **Export** for a finished video or **Export project** for another editable ZIP.

### Required folder structure

For example, compress this folder as `My film.zip`:

```text
My film/
  index.html
  hyperframes.json
  assets/
    image.png
    soundtrack.mp3
  fonts/
    display.woff2
    LICENSE.txt
```

`index.html` is required. A native marker file (`hyperframes.json`, `meta.json` or `project.json`) is recommended, but HyperFrames also treats an index-only composition folder as openable; OpenMotion adds its default `hyperframes.json` paths when a marker is absent. Asset directories above are examples; preserve the paths used by your source. The enclosing folder supplies the imported title; a root-level ZIP uses “Imported project”, which you can rename from its project menu. Composition source must pass OpenMotion's pinned native validation.

### Compatibility and troubleshooting

- Import the editable project folder. A rendered MP4 or a repository ZIP containing multiple examples is not a single native project package.
- OpenMotion uses the pinned HyperFrames engine, currently 0.9.7. Projects that require newer engine features or a separate build may need changes before importing. Import does not execute installation scripts or install dependencies. Package required browser scripts as local project files, outside `node_modules`, with their licenses and matching source references.
- External URLs remain external. Include resources locally and use relative paths for offline playback. If the preview is missing media or fonts, check their paths and availability before exporting a video.
- If the ZIP is rejected, check the entry file, configuration, folder nesting and [package limits](#contents-and-limits). Source must be a valid native composition; simply renaming an unrelated HTML file does not convert it. A failed import leaves existing projects intact.
- If project validation is temporarily unavailable during import, export or duplication, retry once the local runtime is ready. This error does not mean the ZIP or the project is invalid.

Native ZIP recognition follows [the upstream project markers](https://github.com/heygen-com/hyperframes/blob/main/packages/core/src/projectRule.ts). Import validation checks structure; playing the imported project is still necessary to confirm its appearance, animation and sound.

## OpenMotion format, version 1

The ZIP uses ordinary STORE or DEFLATE entries, UTF-8 names and relative forward-slash paths. A re-compressed copy may use one enclosing folder. Finder system metadata is ignored. Its root contains `openmotion-projects.json`:

```json
{
  "format": "openmotion.project-archive",
  "version": 1,
  "projects": [{
    "title": "My film",
    "root": "projects/7e95293d-362f-476c-b886-84c077ac4b52",
    "revision": "<source revision>",
    "files": [
      {"path": "index.html", "bytes": 1234, "sha256": "<SHA-256 of file bytes>"},
      {"path": "hyperframes.json", "bytes": 123, "sha256": "<SHA-256 of file bytes>"}
    ]
  }]
}
```

Each file is located under its project's root, with exact byte counts and SHA-256 hashes. Every non-directory ZIP entry must be listed, except the manifest itself. `revision` records the source snapshot for provenance; imports receive fresh identities and establish their own version history. Projects must contain `index.html` and pass the pinned native composition linter. A missing `hyperframes.json` receives the installation's native default paths. Configuration paths must remain inside the project.

## Contents and limits

- At most 500,000,000 bytes for the ZIP and its expanded contents, 5,000 files including the manifest, and 100 projects per operation.
- Common web source, data, media, model, font, subtitle and license files are included. The maintained extension allowlist is `portableProjectFile` in [the archive service](../project-archive.ts).
- Hidden files, `node_modules`, `renders`, `dist`, `output`, macOS metadata and OpenMotion's project/asset bookkeeping are excluded. Only `.hyperframes/studio-manual-edits.json` and `.hyperframes/studio-motion.json` are retained from hidden directories. Raw native imports discard excluded files; OpenMotion manifests must list only supported files.
- Workspace provider credentials, chat records, export jobs, caches and version histories are not bundled. Authored source is shared as written; do not put private keys or private content in source files intended for sharing.
- External URLs stay external. Fully offline playback requires every necessary resource to be stored locally and referenced by a relative project path. Missing external resources are not downloaded or substituted. Native lint checks do not establish visual quality or playback fidelity.
- Unsafe paths, normalized/case collisions, symbolic links, encrypted archives, ZIP64, invalid checksums, missing listed files and unsupported formats are rejected. A failed import leaves existing projects intact; the UI shows a floating error with retry.
- Export-all excludes Trash. It skips an uninitialized built-in sample project and reports its ID; other unavailable projects cause an error. Very large workspaces should export projects individually.

## Shared API

The public `openmotion_project_archive` Tool exposes `action=export|import`. Use `openmotion_get_project` to page through available projects first. Both actions require a stable `requestId`. Export accepts `projectIds` or `all=true` and optional `expectedRevisions`; it returns the immutable ZIP path, same-origin download URL, checksum and source revisions. Import takes an absolute local `sourcePath` and returns new project/session identities. Reusing a request with different inputs is rejected. Importing the same file with a new request deliberately creates another copy.

Studio calls the same service through `/motion-api/phase1/call`. Browser import streams a ZIP to `/motion-api/project-archives/import?requestId=…` with `Content-Type: application/zip`; download uses `/motion-api/project-archives/<archiveId>/file`. These routes retain the installation's loopback and same-origin protections. Private ZIPs and receipts stay under the workspace's `project-archives` directory, outside the checkout; automatic retention cleanup is not implemented.

`tests/project-archive.test.ts` covers ZIP parsing, source/assets/font roundtrips, independent editing, all-project bundles, HTTP/MCP parity, request deduplication, revision conflicts and rejected inputs. Browser layout, native playback and human visual acceptance are separate checks.

## Project menus

The sidebar and All projects list expose Rename project, Duplicate project, Export project, Reveal in Finder (or the platform file manager), Copy path and Move to trash. Rename uses a shared dialog and checks the saved title before writing. Duplicate waits for pending Studio saves and snapshots the portable source and assets into an independent project/session. It leaves the original and current editor selection unchanged; the completion Toast offers Open project. Copy path returns the managed project directory, not an export file. Action feedback uses floating Toasts.

These operations are also exposed through `openmotion_manage_project`; see the [public contract](mcp-phase1-tools.md#openmotion_manage_project). Duplicate reuses an immutable archive snapshot and import validation with stable request receipts, so retrying cannot create another copy. It shares archive limits and exclusions, including no conversation or version history. Its internal ZIP snapshot remains in workspace archive storage. Remote resources still need the internet. Reveal operates on the server machine; a headless environment may not provide a file manager.

## Trash and recovery

Move one project to Trash from its menu, or select several in All projects and choose **Move to trash**. Trashed projects disappear from the sidebar and are excluded from exports. Recent conversations hides conversations whose projects are all in Trash; drafts and conversations with available projects stay visible. If you trash the project you are editing, Studio switches to another available project. Keep at least one project outside Trash.

The **Trash** tab in All projects is always available. Select one or more projects to **Restore** them or choose **Delete permanently** and confirm the selected set. Permanent deletion removes the managed project folders and their catalog entries. Copies you imported separately and ZIPs or videos you already exported remain independent. A mutation retry keeps its original request identity. If adding or removing a project from Trash is interrupted, OpenMotion completes the saved request before applying another lifecycle action. Retrying the old request cannot undo a later decision.
