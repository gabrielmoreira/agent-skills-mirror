# OpenMotion runtime adapter · phase one

Use only the OpenMotion MCP Tools actually returned by tools/list. Read [Native authoring](native.md) and the pinned engine guide before authoring. Keep one native project and one renderer; creative code is authored by the host Agent.

| Responsibility | Public Tool / supported scope |
| --- | --- |
| Create | openmotion_create_project: independent project, saved requirements, optional builtin template/reference; returns IDs and initial version |
| Read | openmotion_get_project: project list page5, explicit details, bounded text file reads, associated export status |
| Import | openmotion_import_assets: real local image/audio/video attachments, per-item results, immutable asset IDs, no automatic placement |
| Save | openmotion_edit_project: revision + version check, one atomic text batch and optional requirements, one content version |
| Preview | openmotion_open_preview: explicit project or bound session, native lint, exact editable Studio URL; host opens browser |
| Version | openmotion_list_versions / openmotion_restore_version: page5 history, restore as a new version, retain later history/resources |
| Export | openmotion_export_request: immutable snapshot, background MP4, automatic lint and technical verification |
| Cancel | openmotion_export_cancel: explicit owned job, distinguish cancelling/cancelled/completed |

When selecting, obtaining or replacing media, apply the [shared material policy](materials.md) within the selected workflow and existing authorization.

## Final video delivery

### Delivery scope

The current request selects the delivery stage. Editor-only, draft, review and existing-link requests do not create an export. Requested HTML/project files need packaging and source/editor checks; an MP4 request also needs the completed export's technical and actual-file playback checks under [verification scope](verification.md#verification-scope).

File-only delivery of already accepted content follows [source pinning](native.md#pin-source-for-independent-deliverables), without creating an authoring work round or loading creative design. Begin a work round with `generation:false` only if the discovered final-video presentation Tool requires a workId. The selected creative entry composes these operations; it does not override shared version, verification or display requirements. Actual creation/content editing follows the work-round flow below.

During generation and editing, do not create an inline progress or video component and do not open the right-hand editor for intermediate saves. Begin a business work round silently with `openmotion_open_preview({action:"begin",projectId,requestId,mode:"create"|"modify"})`; retain `inlineWork.id` as `workId` through saves and the final export. This call presents no UI.

Once the requested video artifact is complete, call `openmotion_open_preview({action:"complete_generation",projectId,workId,requestId,expectedRevision,expectedVersionId})` immediately, including background work. This independently validates the current native video artifact and records its first completion. It performs no save, preview opening or export. Use the current identities from `openmotion_get_project` after direct filesystem authoring. Intermediate source changes and metadata-only edits do not establish completion.

Once the final authored video is ready, complete the [editable preview handoff](native.md#editable-preview-handoff) on the right.

For an actual video creation/content-edit turn, render the final version once. Wait for its MP4 export to complete and pass technical verification before presenting it. Explicit editor-only work, unchanged template opening, reviews and existing-link requests do not start an unwanted render.

### Choose one final-video preview

Prefer the host's own video preview whenever it can play the verified export. In Codex, the default is one video embed in the final reply, for example `![Final video](/absolute/path/to/version-specific.mp4)`; do not call `openmotion_show_video` on this route. Use the completed job's file, or a version-specific delivery copy with the same SHA-256. Never overwrite a path already embedded for an earlier version. This preview does not require an explicit download request. Ordinary HTML, ZIP and MP4 download links may accompany the preview when requested; a plain download link alone does not establish video playback.

For another host, check its actual video/file capabilities first. Use its native preview when usable. Only when native preview is unavailable and the connection exposes the MCP Apps presentation Tool, choose `openmotion_show_video({projectId,workId})`. Tool discovery alone is not a reason to prefer the plugin player. If neither route is usable, deliver an accessible verified file/link and state that inline playback is unavailable. Do not upload local media to another service merely to obtain a preview.

The native preview and plugin player are mutually exclusive for the same completed export in one delivery. Never emit both, call the plugin after embedding the file, or add a second embed after invoking the plugin as reassurance. A queued Tool acknowledgment, hidden panel or uncertain rendering result does not authorize another preview. Keep the selected route and report unresolved presentation; change routes only after confirming the first failed without mounting a player. Later edits may deliver their own distinct final export, while prior videos retain their fixed versions. The editable Studio is separate from this one-video rule.

When the plugin route is needed, call `openmotion_show_video` in its own host tool call, not in a script/batch with other commands. Bound this final presentation wait to about 60 seconds. If it has not returned, immediately give the already verified MP4's absolute file path and finish, stating that chat presentation is pending. Use a plain link, not another video embed. Do not inspect plugin source, build a custom playback page or repeatedly retry presentation. Keep the completed export identity and prior checks; this timeout does not waive actual-file playback checks or prove the player is visible.

Keep editor display evidence separate: only submit `record_display` for a current editor state actually observed under the [shared handoff](native.md#continuing-edits). A presentation timeout cannot turn a pending/hidden/unavailable editor into confirmed delivery. Report the latest observed editor limitation alongside the file; do not start a new presentation recovery loop after this deadline.

The final player and the editable Studio are separate delivery surfaces. Verify the actual final player and the current editor handoff; source save, a Tool success or a completed render does not prove either surface is visible or playable.

## Execution

### Tool transport and workspace readiness

Use the host's connected OpenMotion MCP tools for project creation, reads, saves, previews, export requests and status checks. A shell HTTP request carrying the same tool name reaches shared business code but is not a host MCP tool invocation; report that distinction and its reason explicitly when a development fallback is necessary.

Before opening a project for an Agent workflow, call `openmotion_get_project` through that connection and verify its `dataDirectory`, project/session identity and current version. Create new work through `openmotion_create_project`, then save and open the returned project through MCP. A browser URL or a matching project ID alone does not bind the connection to that workspace. A repository-only UI fixture can remain isolated, but must be identified as such; exporting it through MCP requires a matching connection or an explicitly scoped project import/copy, not an implicit data-directory change.

Existing phase-one MCP connections automatically reuse a compatible backend after plugin updates, keeping the same workspace and running exports. Version/build differences alone do not require reconnecting: the backend must advertise the same phase-one API protocol and the requested Tool. For `EDITOR_RUNTIME_INCOMPATIBLE`, compare the expected/actual identity and update the incompatible components together when idle; internal legacy connections may also return `MCP_RUNTIME_RELOAD_REQUIRED`. A transport already closed by the host requires host reconnection. Do not stop a compatible backend or silently substitute shell/HTTP exports for failed MCP calls. Preserve existing projects and completed jobs, and query an applicable export before creating another.

When OpenMotion tools are missing or a connection fails:

1. Read the selected host's server status and startup output. An empty tool search does not distinguish an unregistered server, a disabled connection, startup failure or discovery still in progress. Keep the actual error; do not infer the cause from a browser URL or a running backend.
2. For an npm installation, read `runtimeRoot`, `installHome` and `host` from the installed Skill's `openmotion-install.json` or `scope.json`. Run `node <runtimeRoot>/scripts/npm-installer.mjs diagnose --host <host> --home <installHome>` with argument-safe paths; preserve the selected profile and CLI overrides where needed. It checks that host's owned configuration, initializes an independent MCP process, checks the installed tool list and reads the expected data directory. It does not verify or reconnect the current chat. For a source/plugin installation without `installHome`, inspect the host's actual registered command and output; do not guess an npm home or run setup over an unrelated installation.
3. For an npm installation with permitted shell access, use the returned `directAccess` commands to continue in this chat before requesting a host handoff. A successful direct call proves installed access only; do not claim native host reconnection. If direct access is unavailable or fails, correct the reported cause before retrying. Missing runtimes, invalid paths, disabled servers and incompatible versions need their specific fix. Use the host's supported refresh/reconnect action; in Claude Code's interactive session use the server's Reconnect action in `/mcp`. If the host exposes no recovery capability, give that concrete user action. Do not claim to reconnect by starting a separate shell process or repeatedly reinstalling. Allow one safe read retry after a transient failure or completed recovery; if it still fails, report the error and recovery action rather than looping.
4. Through the recovered host MCP connection, call `openmotion_get_project`, confirm its data directory and the original project's identity/current version, then resume this task. A passed independent probe is not host recovery. Query existing jobs and preserve request IDs before deciding whether a mutation needs retrying; never create replacement work to hide a connection failure.

If only an independent folder can be produced, state that the editable Studio handoff is unavailable. Continue that delivery only within the user's accepted scope; do not report the project as open or directly editable in Studio without observing it.

1. Reuse complete guidance already read. Installed Skills and MCP resources/read provide the same documents; production start only routes a task that lacks a specialist. Changes to existing content use [edit workflow](edit.md). Missing instructions/source reads return to the model before dependent writes.
2. Reuse the target projectId or explicitly create a new one. Read its current revision and content version. No global most-recent project fallback. Five is a list page size, not a retention policy.
3. Use returned asset paths and native HTML/CSS/JS. Import and file save are separate operations. Follow the shared [generation boundary](materials.md#generation-boundary) before entering media generation, and the [material policy](materials.md#tool-selection-and-discovery) to select matching sources and capabilities.
4. Follow the [native loop](native.md), preserve locked content and existing Studio manifests. Inspect actual frames, motion and sound. A saved source file or successful lint is not creative acceptance.
5. Export for a requested finished video or content-edit delivery; do not export explicit draft, editor-only or review-only work. Reuse an applicable job before submitting another. Save a stable requestId per action: exact retry returns the original outcome; changed input with the same requestId is rejected. Failed request correction uses a new requestId.
6. Poll the named job through project details. Only completed exposes its real MP4 and technical verification. Inspect [final playback and evidence](verification.md) separately; record unavailable checks as not_run.

## Handoff

Preserve index.html, referenced compositions/media/scripts, hyperframes.json and native Studio manifests. A copied folder is a handoff artifact, not proof it is active. Never edit projects.json, workspace.json or export.json to simulate project selection or task completion. Documents/evidence belong outside the live project. Do not publish or upload as an incidental step.
