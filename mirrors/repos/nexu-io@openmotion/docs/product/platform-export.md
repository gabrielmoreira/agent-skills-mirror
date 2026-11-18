# Platform export through an Agent

Platform export prepares a project-specific instruction for an external Agent. The Agent uses the existing public MCP operations to create independent editable versions, preview them and export verified MP4s. The Export panel defaults to Video, with separate Captions and Platform export choices. Copying a platform instruction waits for pending Studio saves; it does not create a project or start a render.

## User journey

1. Open a project in Studio and choose **Export → Platform export**.
2. Choose Douyin, Xiaohongshu, WeChat Channels, Bilibili, TikTok, Instagram Reels or YouTube Shorts. Choose **Adapt the full video** (default), **Make a short version** or **Extract highlights**, then set the canvas, target duration and caption policy. Highlights also offer a maximum clip count. Optionally enter subtitle languages or open Review captions to correct speech in Transcript. Expand Additional requirements for free-form notes. The summary shows the requested dimensions and duration; the copy action stays visible while the form scrolls.
3. Click **Copy for Agent**. Studio completes pending saves and copies the project ID, local workspace, project URL, connection guide and selected brief. Floating feedback confirms copying; clipboard denial exposes the exact instruction for manual selection.
4. Paste into a compatible connected Agent. **Connection help** opens the existing MCP handbook. Its **Prepare a platform version** example uses the same instruction builder, but asks the user to select the source project because the handbook has no editor identity.
5. The Agent reads the current project and plans from supplied media, captions, scripts or confirmed timecodes. It duplicates the source, edits each copy, opens its preview and obtains fresh revision/version identities before export.
6. The Agent tracks the original export job, reports technical verification and actual playback evidence, and returns the finished file plus editable project. The user uploads the file to the chosen platform.

## User stories and acceptance criteria

| Story | Acceptance criteria | Verification |
| --- | --- | --- |
| As an editor, I can keep my normal file-export workflow. | File export opens by default; native settings, queue and cancellation remain available. Switching tabs or closing the panel does not cancel existing jobs. | Browser default-tab assertion; existing export-panel and runtime regression tests. |
| As a creator, I can turn a longer project into a platform version. | Seven branded platform tiles and three goals produce the selected brief, explicit current project and optional requirements. Platform-default canvas follows the selected platform; explicit 9:16, 16:9, 1:1 or 4:5 overrides persist across platform changes. Short sources are not padded. | Prompt matrix for all 21 combinations; component selection test; browser clipboard read. |
| As a creator, I can extract several highlights. | The brief asks for one to three independently understandable clips, according to the selected maximum, one editable copy per output, and prefers fewer useful clips to filling a quota. | Prompt contract; actual selection quality remains model/user acceptance. |
| As an editor, I can adapt framing while keeping the full story. | The full-video goal explicitly preserves sequence, content and original duration, disables target-duration selection and excludes the hidden shortening/count settings from the instruction. | Prompt contract; selected-goal component test. |
| As a creator, I can specify duration and caption treatment. | Shortening/highlights offer 15–30, 30–60 or 60–90 second targets. Captions may be retained, added from real source text, or removed when editable; burned-in captions are explicitly disclosed. All options appear in the copied brief. | Configuration matrix and component tests; real browser custom-setting clipboard checks. |
| As an editor with unsaved changes, I can hand off the latest project safely. | Copy waits for saves, prevents duplicate clicks, rejects failed saves and abandons the pending handoff when project identity changes or the panel unmounts. Empty, switching or mismatched projects cannot copy. | Component save barrier, failure, readiness and project-switch tests. |
| As a user with a failed connection or clipboard, I can recover. | Integration loading reserves geometry; failure offers Retry and keeps copying disabled. Clipboard denial exposes selectable text and an error Toast. Retrying does not start an export. | Component tests; browser loading/error/retry and clipboard-denial checks. |
| As a user discovering MCP, I can find the same workflow in its handbook. | A scenario card explains the Export entry, provides a copyable example, and the FAQ describes content-analysis dependencies and manual upload. Unsupported cloud clients remain disabled. | MCP onboarding coverage; handbook component tests; browser card copying in both themes. |
| As an Agent user, I retain the original and can retry safely. | Duplicate uses explicit identity and revision protection; each output has its own project. Edits carry latest revision/version; stale edits fail. Duplicate/export retries reuse the original copy/job. | Real stdio MCP duplicate, edit, conflict and retry checks; project-management regression suite. |
| As a user receiving a file, I can play the output and resume editing. | The copy opens in Studio. Export uses a pinned version, finishes automatic technical verification and supplies the actual downloadable file. Playback checks cover decoded frames, audio signal, seeking and replay. Source revision and content remain unchanged. | Browser/MCP/render test with local audio fixture and confirmed 0–2 second selection. |
| As a keyboard or narrow-screen user, I can operate the controls and see feedback. | Shared tabs/selects and platform radio tiles retain keyboard behavior; local brand artwork loads without a CDN; opened menus and floating Toasts remain visible and accessible in both themes. Platform export has a 640px height capped by the space below its trigger. The title, tabs and action footer stay fixed; only the middle form scrolls, including expanded requirements and manual-copy recovery. | Component selection checks and real browser matrix at 1440px/390px, including a 600px-tall viewport, fixed-header/footer geometry, scrolling, screenshots and hit testing. |

## Maintained implementation

- [Platform instruction builder](../../shared/platform-export.ts) owns the scenarios and execution brief. [Project context](../../shared/project-agent-prompt.ts) supplies the same workspace and project identity as the editor's existing MCP handoff, without copying transport environment variables or credentials.
- [Export panel](../../studio/src/components/renders/PlatformExportPanel.tsx) owns form state and clipboard interaction. It uses the workspace save barrier, shared radio tiles, selects, buttons, Skeletons and Toast layer. Platform vectors and reusable selection/summary styles belong to the design system, including shipped provenance and licenses.
- [MCP handbook](../../studio/src/motion/McpConnectionPage.tsx) and [capability catalogue](../../studio/src/motion/mcpCapabilities.ts) expose the scenario separately from atomic tool coverage. No new public tool or execution backend is introduced.
- Existing `openmotion_get_project`, `openmotion_manage_project`, `openmotion_edit_project`, `openmotion_open_preview` and `openmotion_export_request` provide the execution path. Cancellation remains available through `openmotion_export_cancel`. See the [public MCP contract](../mcp-phase1-tools.md).
- [AGENTS.md](../../AGENTS.md#mcp-onboarding-and-capability-maintenance) and [CLAUDE.md](../../CLAUDE.md#mcp-onboarding) require the handbook to stay aligned with capability changes and scenarios composed from existing tools.

## Direct downloads and existing scenes

Video exports the current composition through the native queue, retaining existing format preferences. Export settings are collapsed until needed. If a project has several compositions, Export scene selects an existing HTML scene without navigating the editor or applying the current scene's variable overrides to it. A different scene uses its authored size; unsupported scaling is unavailable. The public `openmotion_export_request` accepts the equivalent optional `compositionPath` with its normal revision/version/request guards.

Captions downloads SRT/VTT from saved timeline cues via the shared `caption_export` operation. It includes manual captions and native text/timing edits, offers all visible captions or one track, and excludes hidden cues. Save failures block export; errors use floating Toasts and loading failures offer Retry. The full source-transcript download remains in Transcript.

Platform export defaults to full-video adaptation with retained captions. Platform and goal are the main choices. Customize version discloses canvas, duration, captions, highlight count, language presets and additional notes. Removing captions also removes a retained translation request from the brief. Selecting a platform updates its default canvas; explicit choices remain intact. Copy for Agent is an instruction handoff, not a completed download. The popup has stable geometry across all tabs and the platform/subtitle actions stay visible while their content scrolls.

## Scope and verification boundaries

Canvas sizes and selectable duration goals are editorial starting points, not maintained platform upload limits, encoder presets or a guarantee of distribution performance. This feature does not add account connections or direct publication. Speech transcription uses configured ASR models through the shared transcript operation, or supplied text/timecodes. Visual analysis, semantic highlight selection, face tracking and creative quality depend on the host's available tools, source material and Agent judgment. Missing analysis inputs must be requested rather than fabricated.

The deterministic end-to-end test exercises real Studio, clipboard, a separate stdio MCP process, independent project editing, native preview, the actual renderer and playback of the exact downloaded MP4 bytes. The attachment download route is not evaluated as a byte-range streaming API. Its synthetic film has confirmed timecodes and locally generated audio. It does not invoke a language model, validate editorial decisions on arbitrary long videos, establish a native Agent's connection, or provide human audiovisual acceptance. Those remain separate acceptance checks.

Run with the repository's pinned Node version and installed dependencies:

```sh
npm run check
npm run typecheck:studio
npm run design:check
npm run build:studio
node --test tests/platform-export.test.ts tests/mcp-onboarding.test.ts tests/project-management.test.ts tests/phase1-runtime.test.ts
npm run test:studio -- studio/src/components/renders/PlatformExportPanel.test.tsx studio/src/motion/ProjectAgentAction.test.tsx studio/src/motion/McpConnectionPage.test.tsx
node tests/platform-export-browser.mjs /absolute/path/outside-checkout/platform-export-evidence
```

The browser test needs the pinned native render tools and a Chromium executable (auto-discovered from the existing native cache, or `HYPERFRAMES_BROWSER_PATH`). It creates isolated temporary projects outside the checkout, closes its MCP/editor processes and removes the fixture afterward. Keep its screenshots, copied instructions, generated MP4 and JSON results outside published artifacts.
