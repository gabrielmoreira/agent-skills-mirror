# OpenMotion 一期 MCP Tool 契约与实现范围


## 结论与本次落地范围

本地候选包版本为0.6.3，避免误复用缺少模板目录接口的旧服务和宿主缓存；尚未发布。源码和默认导出均使用 `phase1`，只公开以下 16 个注册名称（含一个资产兼容名）。发现、调用门禁、接入元数据和构建使用同一注册表；旧名不可绕过调用。原有领域服务、Studio、渲染器和内部兼容 handler 保留。适配不只是改名：补了项目身份、批量导入、请求去重、版本和保存保护、取消终态、自动导出校验。

Skill 是指导文档，与公开 Tool 数量分开。本次后续命名与分发对齐后，一期装入 openmotion-production、openmotion-director、openmotion-template-to-video、openmotion-recreate、openmotion-video-to-template 五个创作入口及其参考，以及按需支撑多模态素材生成的 openmotion-media。模板使用与视频转模板保留已有实际流程；openmotion-recreate 包含实际复刻流程，规则与测量脚本随 Skill 分发，不新增自动创作算法或 Tool。原九个工程 Tool 保留，本次新增目录获取和模板详情入口；详见 [Skill 路由与能力边界](skills.md)。

## Optional native template presentation

The sixteen registered domain names (including one asset compatibility alias) share the same HTTP authority; `openmotion_assets_use` with its `openmotion_assets` compatibility name provides workspace assets without changing existing project calls. A phase-one stdio connection may additionally discover `openmotion_show_template_recommendations` when its `initialize` capabilities declare `extensions["io.modelcontextprotocol/ui"].mimeTypes` containing `text/html;profile=mcp-app`, the feature is enabled and the local presentation assets are valid. Do not infer this capability from a client name or protocol date. Clients without that declaration, including the installed direct CLI client, still discover exactly sixteen names; the legacy profile remains twenty-eight.

This read-only adapter extension accepts exactly three distinct `templateIds` from the twelve approved IDs in `shared/onboarding-templates.ts` (the three original builtin examples and nine curated catalog references), preserving their supplied order. It neither enters the shared HTTP backend nor creates/selects a project. Cards stay in a compact three-column layout, with visible complete previews muted and looping. Current installation onboarding passes `onboarding: false` for cards only, after observing the right-hand library. Installation preparation returns separate `welcomeMarkdown`; the Agent streams it once as ordinary final-reply text after the native Tool result, with pointers to the cards above. The welcome must not live in the App, collapsed commentary or a typewriter animation. Legacy explicit `onboarding: true` remains compatible and includes a component-owned, non-streamed welcome; current installation guidance must not select it. Ordinary calls can omit the flag and retain the same cards-only structured payload. Both modes add result `_meta.ui.resourceUri` for the negotiated immutable resource and `_meta["openai/widgetSessionId"]` for the recommendation identity; this additive binding prevents reuse of an older mounted widget. The Recreate template button uses the negotiated OpenAI `ui/message` extension with `_meta["openai/message"]: {target: "active", send: false}` to append an editable brief with the actual template title/ID; it never submits a task. Unsupported hosts receive no message and show a copyable prompt. Only a pending append temporarily disables the buttons. Completion restores every template button and clears transient feedback; no persistent success message or composer-submission observer is used. Only a later user-submitted brief authorizes the Agent's existing workflow. The returned frozen `createArgs` remain compatible with explicitly accepted unchanged samples; customized requirements/attachments and requested HTML/MP4 delivery use their actual intent, never those sample defaults. Unknown write outcomes still require reconciliation before retrying.

The Agent always supplies `language` from the latest user request or their explicit output-language preference: `zh`, `en`, `ja`, `ko`, `fr`, `es` or `pt`. This explicit per-result language overrides host context for the welcome, descriptions, all controls/status labels and the editable composer prompt. Template names and IDs remain canonical identifiers, and previews are unchanged. Descriptions are localized at render time; canonical payload/media validation remains intact. Regional host locales (including `pt-BR` and `pt-PT`) map to the base language. Omitted `language` preserves compatibility with older callers by falling back to the host locale, then Chinese when absent; unsupported host languages fall back to English. The Agent uses English for unsupported request languages. The component does not read or classify chat messages itself.

Default curated-reference preparation returns `native_required` with the frozen three-of-nine selection, cards-only native arguments and separate welcome text. A fixed-CSP visualization fragment cannot inherit the native resource media policy, so it must not be published for remote references. Self-contained builtin examples retain the fragment route. Preparation, shell RPC and registration do not establish native delivery; stale discovery needs the supported host refresh. See the [shared onboarding contract](install-onboarding.md#installation-success-reply).

UI-capable connections list and read one immutable `ui://openmotion/template-recommendations/<contentHash>/index.html` resource. Its CSP permits Blob media and the exact public media origin `https://r.open-design.ai` for catalog video/poster elements; script/network connections remain disabled. Existing workflow and engine resources retain their original semantics. Resource identities include the browser bundle, approved media, source fingerprints and presentation metadata; an old connection keeps the old bytes after a compatible installation update. Missing/corrupt optional presentation assets disable only the extension, not the domain tools. `OPENMOTION_TEMPLATE_CARDS=0` disables the presentation on new connections without changing projects or stopping exports.

Production reads a prebuilt browser bundle, three integrity-locked builtin MP4 previews and nine metadata-locked catalog references. Reference cards stream the complete original films from their existing content-addressed public CMS URLs, require network access and do not claim to be OpenMotion-generated editable projects. Reference results include `templateKind: reference` without `createArgs`; their prompts retrieve the exact ID with `openmotion_get_template` and follow `openmotion-recreate`. First-run preparation samples three distinct references from the curated pool in `shared/onboarding-templates.ts` and shares that ordered selection across presentation routes. Mounted cards never redraw on playback, return or host-context changes. It does not depend on the browser SDK package at runtime, render previews on installation, download template media or use online catalog credentials. Source packaging rejects missing or stale browser builds using the shipped build identity, and verifies the full media/source manifest and response budget before accepting an artifact. The 1.5 MiB final response budget is a build constraint, not a general host limit. Publication metadata records this optional extension separately from the fifteen domain capabilities. Native host discovery, visible presentation, actual playback and project creation require separate evidence.

## Public MCP names (16, including one compatibility alias)


| 公开 Tool | 复用来源 | 本次实现到的边界 |
| --- | --- | --- |
| openmotion_manage_project | Shared project management service | Read saved title/path, rename with conflict protection, duplicate independently, or reveal the local directory |
| openmotion_project_archive | Shared project archive service | Export selected/all projects and import ZIP copies with bounded validation and request deduplication; see [Project archives](project-archives.md) |
| openmotion_assets_use | Workspace assets, Brand Kits and Model Gateway | Style-only Brand Kit commands, list/get, bounded media read, upload, generate/jobs/status/cancel/retry_save, rename/trash/restore, immutable versions/references and explicit version import into projects; see [Assets](assets.md) |
| openmotion_assets | Compatibility name | The original operations plus save-only recovery, shared records and request identities |
| openmotion_media_use | Shared Model Gateway | Discovery and references for new assets_use generation; project-direct generate (optional project referenceAsset; audio mode follows the selected model)/status/cancel retained for compatibility with dedicated media adapters, OpenDesign account models and registered compatible image/speech APIs; service-owned keys, explicit project, stable request ID, automatic local asset-library saving and original project paths, save-only recovery; does not edit the composition |
| openmotion_list_templates | Repository, hosted CDN or configured CMS catalog | No query arguments; returns source, a local JSONL index, count and catalog version for local search |
| openmotion_get_template | Same repository/hosted/CMS reader | Exact ID; repository entries return local instructions, motionDocument content and absolute localSource paths |
| openmotion_media_use | Fixture-based provider references, discovery, authenticated requests, job ownership, output validation and import, and rejection without paid retries | tests/byok.test.ts, tests/provider-settings.test.ts |
| openmotion_create_project | 项目目录、空白工程、模板复制、会话归属 | 新建独立载体、保存需求/来源、返回初始内容版本；宿主 Agent 制作影片 |
| openmotion_open_preview | 原预览、项目选择、原生 lint | 打开指定已有工程；仅明确绑定的 OpenMotion 会话可省 projectId；返回真实 URL |
| openmotion_import_assets | 素材目录、FFprobe/FFmpeg | 实际本机媒体批量持久化、逐项结果、稳定素材 ID、去重；不自动排入时间线 |
| openmotion_get_project | 项目目录与原生文件读取、导出记录 | 项目分页5条、显式工程详情、分段文本读取、当前版本、具名导出任务状态 |
| openmotion_edit_project | 原写文件职责、Studio 原生 history | 双重版本校验；文本批量保存及需求一起写入；失败恢复保护；通知原生文件监听 |
| openmotion_export_request | 原 request/get/verify export、原生渲染器 | 冻结工程版本和本地素材、后台 MP4、自动 lint/规格/完整解码校验；同请求找回任务 |
| openmotion_list_versions | Studio history/checkpoint | 内容快照、稳定 ID/vN、来源/摘要、可恢复标记；每页5条，不限制只留5条 |
| openmotion_restore_version | Studio history 与保留的媒体内容 | 旧快照恢复成新版本；保留后续历史；历史资源缺失或并发冲突时拒绝覆盖 |
| openmotion_export_cancel | 现有导出队列、进程生命周期 | 指定项目/任务；排队取消、运行中 cancelling、进程退出后 cancelled；完成竞态保持 completed |

## WebMCP access from Studio

Studio registers five `openmotion_studio_*` tools for observation and navigation: `openmotion_studio_look`, `openmotion_studio_select`, `openmotion_studio_seek`, `openmotion_studio_frame` and `openmotion_studio_inspect`. Selection and seeking change editor state, not project source. Video content changes use `openmotion_get_project` followed by `openmotion_edit_project`, which saves native source files with revision/version checks. The seven content-writing editor tools (`set_text`, `set_style`, `transform`, `add_animation`, `update_animation`, `add_keyframe` and `delete_animation`) are not registered or callable through WebMCP. Studio's manual editing handlers remain available. The `can` flags returned by observation tools describe manual editor capabilities, not additional WebMCP tools. Old `studio_*` names are not aliases. Refresh the page and rediscover its tools after upgrading.

While Studio is open, its Motion host registers the same sixteen registered domain `openmotion_*` tools using the shared definitions, for twenty-one page tools in total. Browser Agents can discover and call them through WebMCP. Native WebMCP is preferred, with the existing Studio fallback for browsers without it. The `agentToolsEnabled` preference controls both sets and takes effect after reloading Studio. Closing or navigating away unregisters the page tools. Ordinary MCP discovery, resources and negotiated MCP App presentation are unchanged.

WebMCP calls forward to the existing same-origin `/motion-api/phase1/call` service. Names, input schemas and successful existing service payloads are preserved; the new asset read action returns native content blocks plus metadata-only structuredContent, including request deduplication, explicit project/session binding, revision/version checks and export job identities. The adapter does not infer the target from the globally active project. Import `sourcePath` and template `indexPath`/`localSource` retain their host-filesystem meaning; browser-only clients need host file access for those paths. The asset library accepts user-selected image/video/audio uploads through its bounded same-origin endpoint; MCP imports still require real host file paths. No arbitrary filesystem reader or private service credential is exposed to the page.

Failures resolve with `{isError:true,error:{code,message,applied}}`, because rejected WebMCP callbacks can lose their error messages. Local validation and cancellation before dispatch report `applied=false`; a lost reply or cancellation after dispatch reports `applied="unknown"`. Cancellation does not roll back a committed edit or cancel a queued render; use `openmotion_export_cancel` for the named export. No automatic retry is performed: inspect the project/history or original job, and retain the original request ID when recovering an uncertain mutation. Browser/Agent permission and real end-to-end acceptance remain separate from page registration.


The shared WebMCP registrar measures all twenty-one page tools through the existing Studio tracking transport. `webmcp_tool_started` and `webmcp_tool_finished` correlate one invocation by `call_id`, with the public `tool_name`, `transport=webmcp`, observed outcome and elapsed milliseconds. `webmcp_registration_result` measures each attempted registration, including refusal and cleanup cancellation. Collection remains asynchronous and respects existing privacy settings and Do Not Track; analytics failures never retry a tool or replace its result. No tool arguments, returned content, handles, paths or raw errors are recorded. These browser events are separate from unchanged stdio MCP events and existing domain-operation results; a failed or cancelled invocation does not establish whether a mutation was applied or rolled back. See [tracking coverage and limits](../tracking/README.md#implemented-signals-and-limits).

## 共用约束

- projectId 是作品身份；sessionId 是 OpenMotion 内部会话，不能把宿主聊天 ID 自动当成它。Project writes require explicit project identity; workspace asset operations use asset/version identity and need no project until import_to_project.新 MCP 客户端未绑定时，默认预览报 PROJECT_NOT_BOUND，不猜全局最近工程。
- versionId 是历史身份；versionNumber 显示 vN；revision 是内容哈希。恢复后哈希可与旧版相同，版本身份仍是新的。GUI 的已保存改动也进入原生历史。
- 有副作用的保存使用稳定 requestId。同 ID 同输入找回原结果（导出/取消同时刷新同一任务状态）；异输入报 REQUEST_ID_CONFLICT。修正失败输入时使用新 ID。对进程中断但无法确认结果的请求返回 REQUEST_STATE_UNKNOWN，不自动重复写入。
- 编辑/恢复以 Studio 原生独占窗口协调 GUI 写入，暂存文件和恢复日志保护整批写入。进程重启先恢复未完成写入；发现外部第三种内容报 RECOVERY_CONFLICT 并保留副本。普通文件系统的多文件提交不等于断电级数据库事务；macOS共享后台持有系统所有权锁后才回收旧私有锁；独立旧服务的workspace.lock仍明确阻塞，不能自动强删。
- 素材成功项与索引作为一次项目保存；无效素材逐项失败并保留有效项。不覆盖已导入资源。At most 500 MB (500000000 bytes) per file and 100 items per call; local absolute paths only, not a cloud attachment upload protocol. Studio enforces the same decimal byte threshold for the entire multipart request, including form overhead, so a batch may need separate uploads. 500.5 MB (500500000 bytes) is rejected; sizes are never rounded down.
- 源码最多100个文本文件、总计8 MiB；可仅更新 requirements；分段读取上限2 MiB/次，offset 是 UTF-8 字节边界。HTTP JSON 请求另受9 MiB传输体积限制。只允许项目内白名单路径，拒绝符号链接、越界及保留元数据路径。
- 错误通过 MCP isError 和 error.code/message/applied 返回原因；来源读取/版本/路径/媒体/任务错误不返回空成功。无法确认写入或丢失回复时，先读取项目/历史/原任务，不盲目重试。服务错误的 applied=unknown 表示无法替调用方推断是否生效。
- 技术验证、视觉/声音/播放审阅和用户采用分开。record_review 只保存所声明的真实依据，verifiedUserAdoption 固定为 false，不证明用户实际采用。

## 各 Tool 的输入、返回与失败边界

### openmotion_manage_project

Every action requires an explicit `projectId`. `info` returns the persisted `title`, absolute project `path` and server `platform`; clients can copy that path to their own clipboard. `rename` requires `title`, `expectedTitle` from info and a stable `requestId`. A changed title returns `PROJECT_NAME_CONFLICT`; a reused request with different inputs returns `REQUEST_ID_CONFLICT`. Renaming clears the built-in localized title without moving the directory or changing source versions.

`duplicate` requires a stable `requestId` and accepts `title` and `expectedRevision`. It snapshots the source through the archive service, validates the same portable files and creates new project/session identities without selecting them. Repeating the request returns the same copy. Archive limits and exclusions apply; conversations, versions and renders are not duplicated. `reveal` opens the managed directory in the server machine's Finder, File Explorer or Linux file manager. It accepts no caller-supplied paths or shell commands; unavailable directories and launch failures return explicit errors. Studio and MCP call the same domain service.

List trashed projects with `openmotion_get_project({ trashed: true })`. Use `trash`, `restore` and `delete` with explicit project IDs and stable request IDs. Trash is reversible; delete requires the project to already be in Trash and removes its managed project folder and catalog entry. The result identifies the remaining active project. The service preserves at least one available project and replays confirmed operations without deleting twice. Studio composes these operations for checked rows and confirms permanent deletion.

### openmotion_project_archive

`action=export` accepts `projectIds` or `all=true`, a stable `requestId`, and optional `expectedRevisions`. The result includes `archiveId`, absolute `archivePath`, `downloadUrl`, `filename`, `bytes`, `sha256` and source project revisions. Export-all excludes Trash and skips an uninitialized built-in welcome project, reporting `skippedProjectIds`. Export requires saved source and validates the finished ZIP with the import rules before returning it; it does not render a video.

`action=import` accepts an absolute local ZIP `sourcePath` and stable `requestId`. It validates all projects before registration and returns new project/session identities without selecting them. Repeating the same request returns the same copies; reusing the ID with different bytes fails. OpenMotion packages and one native HyperFrames folder are supported. See [the format, exclusions and limits](project-archives.md). Browser uploads and MCP call the same implementation; the browser supplies file bytes through the upload adapter. Current host stdio configuration is unchanged.

### openmotion_assets_use / openmotion_assets

The preferred `openmotion_assets_use` and compatible `openmotion_assets` names share the same protocol-1 asset service, which manages a workspace library independently of projects. The preferred tool actions are `list`, `get`, `import`, `update`, `generate`, `jobs`, `status`, `cancel`, `retry_save`, `import_to_project` and `read`, plus `brand_kit` for the shared Brand Kit library; the compatibility name retains the original operations and also supports save-only recovery. `get` remains metadata-only. `read` requires an explicit assetId/versionId and returns bounded native image/audio content, including timestamped video frame previews; see [read limits](assets.md#reading-a-fixed-version). Import and generation use stable request IDs. Versions preserve bytes, hashes, prompt/model/parameters and pinned references; changing the current version does not rewrite historical files. Trash is reversible. Project import requires explicit projectId and versionId and reuses the ordinary project import/history transaction. Model support and costs remain gateway-owned; image models that report supportsImageReference edit with up to their maxInputImages references (one for local Codex and OpenDesign account models; OpenDesign Cloud models publish their own maximum), and Cloud video models that report maxInputImages take one first-frame reference. See [asset architecture and limits](assets.md).

With `action=brand_kit`, supply a nested `brandKit` command. This is the Studio Brand Kit library, not the template catalogue. It supports official discovery/import, website extraction with a stable request ID, status, cancellation, revision-checked edits and a style-only package handoff. See [Brand Kits through MCP](brand-kits.md#agent-access-through-mcp).

### openmotion_list_templates / openmotion_get_template

List has no arguments and returns source, indexPath, total and catalogVersion. Search the local JSONL index; repository rows include localSource paths. Get requires templateId and reads the selected template's instructions. Repository mode also returns motionDocument={path,content} and localSource paths for metadata, guide, manifest and examples, without requiring an editor/backend or CMS request; hosted catalog entries return motionDocument without localSource paths, and built-in examples stay answerable without a catalog request. Source checkouts default to repository; NPM distributions without catalog files default to the latest hosted `main` catalog, while explicit CMS mode retains publication caching. See [startup and source selection](template-repository.md#run-from-a-local-clone). Guidance-only examples require authoring a new project; direct projectType=template copying still requires actual editable project files.

### openmotion_create_project

必填 requestId、projectType、title、requirements；可选 sessionId 归入已有会话。projectType 为 natural_language/template/reference_video。template 必须给实际可复制的 builtin 或 Prism templateId；reference_video 必须给已知目录 referenceVideoId 或 HTTP(S) referenceUrl。

返回 projectId、sessionId、project（directory、html、files）、revision、version、currentVersionId/currentVersionNumber、需求/来源、previewUrl，以及 creationComplete=true、filmComplete=false。参考只记录来源，不在创建时假装看片或生成成片；外部 URL 可达性/内容由宿主实际检查。输入不符、模板不可复制或 ID 不存在时明确失败，保留旧项目。

### openmotion_open_preview

For user-facing catalog browsing, comparison or recommendation, prepare `target=templates` and complete its host page handoff in the same turn unless the user requested text-only/no opening. Recommendations do not authorize creation. Use the shared [browsing policy](../skills/openmotion-production/references/templates.md#browsing-and-recommendations); background directory queries retain their read-only behavior. Verify actual native panel visibility and library content, retry failed presentation once, and report persistent display failures separately from unavailable host capability. Do not count a prepared URL or queued acknowledgment as display success.

`target=templates` opens the editor template library without a project/session binding, native project initialization, lint, template-source download or active-project switch. It accepts only action=open (or omitted), embedded and presentation; project, session, revision and review/display fields are rejected. The result contains target, previewUrl, projectCreated=false and a page previewHandoff without revision/version. The host presents and observes this page; project record_display receipts do not apply. Studio creates an independent project only after the user selects an editable template's Open and edit action. Template details and playback alone do not create projects.

Default action=open accepts an explicit projectId or bound sessionId, optional embedded, presentation, expectedRevision and expectedVersionId. When supplied, both identities are checked before and after lint/open. The only compatible change during opening is the immediate next content version whose complete file inventory exactly matches the pinned engine's deterministic editor-ID stamping of the checked source. The result and previewHandoff then identify that new current version. Other source changes, extra versions and same-content restores remain conflicts. The result includes previewHandoff, previewUrl, preflight, selectionSource and openedByHost=false; the host must present the existing project. No project is created implicitly.

Preview and export preflight use the same pinned native `host:"studio"` lint policy as the editor. Structural errors return `PROJECT_VALIDATION_FAILED` before preview opening, or a failed export before rendering, with native code/file/location/fix hints. Warnings do not fail the check. See the [shared lint command](hyperframes.md).

The handoff preserves the current chat by default (presentation=foreground): reuse its native Tab and queue while inactive. On return, resolve the latest project version without replaying the queued version. Codex actions include a calling-chat-only visibilitySync and bounded observation instructions; queued alone is neither confirmation nor proof that the calling chat is inactive. First delivery follows the same checks as continued edits. A separate hidden automation tab, markDeliverable or completed MP4 export does not satisfy editor delivery. Retry a missing native tab presentation once, then report the display gap. Only an explicit presentation=now request allows switching back for this turn; background skips presentation. See the shared [continuing-edit workflow](../skills/openmotion-production/references/native.md#continuing-edits).

action=record_display requires projectId, requestId and display={revision,versionId,previewUrl,visibility,contentVerified,evidence}; optional hostStatus and hostTabId retain the acknowledgment and actual native providerTabId independently. Only visible plus inspected latest content returns confirmed. Hidden/queued/unavailable or unverified content remains pending. visibility=queued explicitly reports host-confirmed inactive-chat deferral and returns wait_for_calling_chat; hostStatus=queued with visibility=hidden/unavailable retains present_preview recovery rather than assuming inactivity. Reject foreign project/session/origin URLs and stale revision/version identities, including same-hash restores and retries. Records are host_reported; openmotion_get_project.previewDisplay exposes isCurrentVersion and liveVisibilityVerified=false, never a live visibility claim.

openmotion_edit_project and openmotion_restore_version accept the same optional presentation and return a fresh version-bound previewHandoff after each save or replay. The host owns persistent background preferences; show-now permission does not persist. Stored native Tab IDs are reuse hints that must be validated against the current host inventory. A host queue can open on return without another model turn; absent a new observation the service receipt stays pending.

可选 action=record_review，须 projectId、requestId、review，记录已观察对象/versionId/结论/依据/来源与可选时间范围，不修改源码。

### Curated font resources

`resources/read openmotion://fonts/index` returns a compact 40-family index; the returned `openmotion://fonts/<id>` URIs expose only the requested metadata and the installed preparation command. The command downloads size/hash-pinned upstream font bytes and license into a user cache, never a project. Existing `openmotion_import_assets` then persists chosen local files through its normal version transaction. Catalog metadata ships with the Skills; the full font collection does not.

### openmotion_import_assets

必填 projectId、requestId、items；每项 itemId、sourcePath，可选 name。Font items may also provide an absolute licensePath (UTF-8 text, at most 128 KiB), copied with the font in the same version.支持探测并首帧解码的 PNG/JPEG/WebP/GIF、MP4/WebM 及 WAV/MP3/OGG/FLAC/AAC/M4A。格式以实际媒体流/容器为准。TTF/OTF/TTC/WOFF/WOFF2 font files are parsed through the existing font metadata reader, without FFmpeg for font-only batches. They return actual family/weight/style, project-relative fontFaceCss and optional license path/hash. Collections select the nearest upright regular face; choose a standalone or variable resource for an explicit weight. SVG/PDF and arbitrary URL downloads remain outside this Tool.

返回 status=completed/partial/failed、items 中的素材 ID、相对 path、MIME、大小、SHA256、实际可得规格或单项错误，以及发生保存时的新版本。相同 itemId/输入复用现有素材；同 itemId 改输入冲突；纠正失败项使用新 requestId。导入不自动替换元素或放进时间线。

### openmotion_get_project

无 projectId：当前数据目录中按 createdAt 倒序列项目，每页5条，nextCursor 翻页，可按 sessionId 限定；旧项目无创建时间返回 null。不选择/创建 GUI 项目。

有 projectId：返回工程原生目录、入口源码/文件清单、需求/来源、assets、revision、当前版本、所属 sessionId、导出及审阅记录。读取会 flush 已保存原生历史的 metadata，不修改源文件。file={path,offset?,length?} 分段读文本；expectedRevision 可固定读取快照；exportJobId 查指定历史导出。导出结果包含真实状态/阶段、错误和校验；完成后才有 path/downloadUrl。错误项目、版本冲突或不属于该项目的任务明确失败。

### openmotion_edit_project

必填 projectId、requestId、expectedRevision、expectedVersionId、files=[{path,content}]；可选 requirements、summary。只保存宿主已生成的文本，不启动第二个创作 Agent。requirements 存在工程受版本管理的元数据中，与文件一起提交。

返回 projectId、version、revision、changed、changedFiles、previewSync。无内容变化返回 changed=false，不造空版本。Studio 已打开时返回 file_watcher_notified，这不是已观测到每个画面刷新完成的证明。路径/类型/体积/并发失败时拒绝或回滚整批；恢复冲突保留现场并阻塞覆盖。

### openmotion_export_request

默认 action=request，必填 projectId、requestId、expectedRevision、versionId，可选 audio=required/silent/optional。仅允许导出当前经双重校验的版本；先恢复历史版本，再导出它。局部文件冻结成私有快照，外部 URL 仍是外部依赖。

返回原 job（id/projectId/versionId/revision/expected/state/stage 等）和自动技术校验说明。用 openmotion_get_project 的 exportJobId 追踪。只输出 MP4；自动执行 lint、原生 render、FFprobe 规格、视频/音频全解码和代表时间点 seek。检查失败返回 failed，不把渲染退出0当成功。队列一期同数据目录只允许一个待执行/运行中的导出。

action=record_review 要求 projectId/requestId/jobId/review；只能对本项目已完成任务及其 versionId 记录依据，不重新渲染。

### openmotion_list_versions

必填 projectId，可选 cursor。返回 currentVersionId/currentVersionNumber、versions、pageSize=5、hasMore、nextCursor。每条有 versionId、versionNumber、createdAt、source、summary、revision、restorable/unavailableFiles；filePaths 是完整文件路径清单，不等同精确逐行 diff。首次读取建立现有工程基线；仅实际内容变化产生后续 vN。

Availability is checked against the current native and retained blob contents, including SHA-256 verification. Missing, unreadable or corrupt files set `restorable=false` and appear in `unavailableFiles` by project-relative path. Restoring the original blob bytes makes the version available again; capture-time flags are not authoritative.

### openmotion_restore_version

必填 projectId、requestId、versionId（目标）、expectedRevision、expectedVersionId（当前）。校验目标属于该项目及历史资源完整，再恢复原生源文件、样式、时间/效果数据及媒体为新内容版本。v5→v3 得到 v6；v4/v5 仍可查/恢复。目标本就等同当前内容时 changed=false。

返回 version/revision、restoredFromVersionId、changed、previewSync。完整媒体恢复保证适用于本Tool，Studio自身GUI历史恢复仍沿用原生行为。不自动混合两个版本，不替换/删除已有导出成片；缺资源、并发改变或恢复冲突时明确报错。

Restore repeats the availability check and verifies staged files before changing the project. Unavailable resources return `VERSION_NOT_RESTORABLE` with the affected paths and `applied=false`; current source files, revision/version identity and asset index remain unchanged. A successful list response cannot guarantee that files will remain available until a later restore.

The open editor also shows these restore refusals through its shared dismissible error toast, including the affected paths and unchanged-project message. Existing project-status polling delivers the latest failure only to that project; each request is shown once per editor mount. This transient notice is cleared from server status after a successful restore or backend restart. Native history panel action errors use the same toast component; native restoration semantics are unchanged.

### openmotion_export_cancel

必填 projectId、requestId、jobId。只能操作项目自己的任务；返回 job 最新状态。pending 直接 cancelled；running 先 cancelling，发出停止信号并在执行进程退出后 cancelled。执行器被异常杀死/超时返回 failed，不谎报取消成功。completed 保持 completed，历史视频保留。宿主停止对话不自动调用本 Tool。

## 注册、构建与兼容

- shared/mcp-profiles.json 是14个注册名称的唯一公开清单，shared/mcp-release.json 默认 phase1；mcpRegistry 同时控制发现与调用，禁止运行时环境变量扩大列表。新增/缺失实现由构建完整性检查拦截。
- npm run package:phase1 构建 Studio 并生成 dist/openmotion-0.6.3-phase1.zip；npm run package:plugin 默认也沿用 phase1。该插件 ZIP 不带原生 Node/浏览器/FFmpeg：使用支持的本机 Node、首次安装锁定依赖，FFmpeg/ffprobe 需本机可用。
- 四宿主薄适配器从同一运行时导出，scope.json 记录 profile，复制上述5个创作入口及支撑 Skill `openmotion-media`；不另维护 allowlist。数据目录放在 runtime/插件缓存之外。资源指导通过本地文件或 resources/list、resources/read 取得，不另增加 workflow Tool。
- 完整原生测试包的 build <target> <beta-version> [phase1|legacy] 使用同表检查并写 release.json；本次不声称重新制作/验收各平台原生安装包。
- Internal compatibility handlers and explicit legacy development builds remain separate; hidden calls return MCP_TOOL_NOT_EXPOSED in phase-one packages. Existing supported phase-one calls continue across compatible updates. Newly added Tools, changed discovery metadata and Skills require host refresh before use.

### Phase-one API compatibility

`shared/phase1-tools.ts` defines API protocol 1 and the available Tool names. Both editor and preview health advertise these capabilities. A phase-one stdio adapter can forward to another version/build only when the backend explicitly supports the same API protocol and requested Tool; the backend validates the complete input again before execution. Release channels do not impose an additional tracking-policy compatibility gate. DEV packages retain their separate data directories and template routing. Service, workspace, instance and authority protocol checks still apply. Internal legacy calls retain exact version/build checks.

Protocol 1 preserves existing request/response shapes and semantics. New Tools and optional fields are additive; incompatible required fields, removed fields or changed semantics must increment the protocol. A supported older connection keeps its project binding, stable request IDs and existing export queries through a compatible plugin or backend replacement without another MCP initialization. Running exports stay with the live authority; recovery does not terminate it or replay an uncertain mutation. An already-closed host transport and an incompatible protocol cannot be repaired by this negotiation.

## 开发顺序与放行

先明确项目/版本，再导入/保存、打开预览、按实际范围导出和审阅。源码、本地运行、ZIP协议检查、完整平台/宿主和业务验收分别记录。

## 尚需对齐的产品口径

本次采用：P0 自然语言“创建”是工程载体+需求，影片仍由宿主制作；项目排序用创建时间；当前会话须显式绑定；历史5条是分页；媒体不自动清理。容量/清理、云附件传输、远程认证、四宿主完整模型任务体验及 Windows/macOS 安装验收后续单独推进。

## 原九工具版本的历史验证范围

已通过本地一期业务检查和真实运行闭环：创建/分页/请求去重、保存与 UTF-8 读取、v5→v3→v6、跨重启保留历史/媒体、失败与中断恢复保护、排队取消；真实 Studio 的原生历史、MCP 绑定与保存、运行中取消、320×180/10fps MP4 的自动技术验证。

合入最新主干后，后端完整回归124项通过；另含真实多MCP连接的项目隔离、并发冲突与断开续用；Studio类型检查通过，单元/DOM测试8098项通过，保留原有1个跳过文件/16项todo；check和后端类型检查通过。实际ZIP从独立目录启动、首次安装锁定运行时后，9项Tool均实际调用通过，含音轨MP4自动校验、运动帧变化、版本恢复、取消与历史结果读取。四宿主薄适配器已导出；安装配置的发现检查与完整模型体验分别验收。上述历史结果应按对应提交解读。独立播放器听看、四宿主端到端模型任务、Windows 实机、CI、发布与业务验收均未据此宣布通过。

## 源码定位与验证记录

公开 schema 在 shared/phase1-tools.ts，注册在 shared/mcp-registry.ts；业务适配在 phase1.ts，原生历史及文件保护在 phase1-versions.ts，导出状态在 workspace.ts/server.ts。核心回归为 tests/phase1.test.ts、tests/phase1-runtime.test.ts、tests/mcp-registry.test.ts、tests/workflow.test.ts、tests/adapters.test.ts。旧逻辑通过内部兼容回归继续保护。

## Public Tool verification

以下是已执行的本地主流程与异常检查，不等于覆盖所有输入组合、平台或人工验收。自动检查调用真实实现及临时隔离项目；示例命名不是新增需求编号。

| Tool | 已执行的检查 | 测试入口 |
| --- | --- | --- |
| openmotion_list_templates | 本地 JSONL 索引、与界面同版本、ETag/304、离线缓存、环境隔离；不接受查询参数 | tests/prism-templates.test.ts |
| openmotion_get_template | 精确 ID、文件清单与编辑指南；实际模板下载、哈希失败清理、内置模板离线读取 | tests/prism-templates.test.ts |
| openmotion_create_project | 自然语言载体、实际内置模板、参考ID载体；同请求找回、异输入冲突、来源类型不符拒绝 | tests/phase1.test.ts |
| openmotion_open_preview | 真实Studio URL、同会话绑定、未绑定拒绝、多连接各自选项目 | tests/phase1-runtime.test.ts、tests/phase1-shared.test.ts |
| openmotion_import_assets | PNG/WAV/MP4真实探测/解码、坏文件部分失败、重复去重、恢复历史媒体 | tests/phase1.test.ts |
| openmotion_get_project | 每页5条/游标、显式项目/会话归属、UTF-8分段读取、历史导出、无GUI切换 | tests/phase1.test.ts |
| openmotion_edit_project | 文本批量、仅需求保存、无变化不造版本、过期版本/路径冲突拒绝、多连接并发一成一拒 | tests/phase1.test.ts、tests/phase1-shared.test.ts |
| openmotion_export_request | 不开Studio的冷导出；实际静音/带音轨MP4、自动规格/解码/运动帧、原请求去重、审阅不重渲染 | tests/integration.test.ts、tests/phase1-runtime.test.ts、tests/phase1-package.mjs |
| openmotion_list_versions | 最近5条/更早页、当前版本标识、跨重启历史仍可读 | tests/phase1.test.ts |
| openmotion_restore_version | v5恢复v3产生v6并保留v4/v5；历史音视频；中断恢复及外部第三种内容保护 | tests/phase1.test.ts |
| openmotion_export_cancel | 排队取消、运行中确认停止、跨项目拒绝、已完成不改状态、旧结果保留 | tests/phase1.test.ts、tests/phase1-runtime.test.ts、tests/phase1-package.mjs |

复测命令：后端 `node --experimental-strip-types --test --test-concurrency=1 tests/*.test.ts`；实际包 `node tests/phase1-package.mjs /absolute/path/openmotion-0.6.3-phase1.zip /absolute/path/evidence`。完整测试包和四宿主真实模型任务另行验收。


### 测试代码与CI范围

| 层级 | 代码 | 当前执行方式 |
| --- | --- | --- |
| 业务/协议自动化 | tests/phase1.test.ts、tests/mcp-registry.test.ts | PR CI执行；真实临时文件/原生历史，覆盖主流程与关键异常 |
| 实际运行集成 | tests/phase1-runtime.test.ts、tests/phase1-shared.test.ts | 本机全量执行；真实Studio/渲染与多个MCP进程，部分场景限定macOS |
| 独立ZIP端到端 | tests/phase1-package.mjs | 每次PR创建/更新及main推送自动执行独立phase1-package-e2e任务；重新打包、独立解包/首次锁定依赖安装、真实stdio MCP、Chromium与FFmpeg；断言成功调用的Tool集合与公开清单一致 |

各Tool的用例按用户场景复用，不要求每项单独一个文件。原九个工程工具及两个模板工具均进入ZIP端到端链路；预览部分检查实际服务和URL，尚未覆盖完整GUI点击操作。宿主模型对话、Windows实机、播放器人工听看和所有参数组合不在当前完成范围。独立ZIP E2E已加入普通PR CI；完整GUI点击和macOS共享后台集成仍是单独验证范围。

CI不按路径过滤、不跳过渲染、无失败重试或continue-on-error；缺浏览器、依赖安装失败、任一Tool失败或视频校验失败均使任务失败。每次在独立临时数据目录安装，使用Linux临时容器与自带Chromium，不接入宿主共享浏览器。CI保留14天的HEAD、ZIP校验和、Tool调用结果、MCP/预览日志及通过时的MP4。基础构建失败时以该任务日志为准。

**合并门禁还依赖仓库配置：** 管理员需为main开启分支保护，启用必需状态检查，并将实际CI产生的phase1-package-e2e检查上下文（以及现有assemble检查）设为必需；禁止跳过检查合并。工作流文件不能自行修改仓库权限。2026-11-05用户确认先不配置分支保护：本期先交付自动E2E与失败标红，按CI全绿才合并执行；平台暂不会强制锁住合并按钮。后续启用硬门禁仍需管理员配置，不能把CI接入等同于“服务端已禁止失败合并”。

参数拒绝另有回归：顶层/嵌套的constructor、__proto__、toString等未声明字段，以及类型不正确的分页游标，必须明确失败。不能把schema中的additionalProperties=false单独当作运行时校验已完成。

## BYOK media-use extension

New completed media results are saved to the local workspace asset library as well as the original project paths. `job.libraryAssets` pins each immutable `assetId/versionId`; `job.assets` retains project-relative paths. When `savePending` is true, call `action=retry_save` with the original `projectId`, `jobId` and a stable `requestId`. This retries local saving only, does not invoke a provider and cannot overwrite changed project files. The same action is available through `openmotion_assets` and Studio task recovery. Historical completed jobs are not backfilled.


**Project-direct compatibility contract:** new generation uses the preferred asset route below; existing jobs retain this contract. Read action=reference for the selected provider, or `openmotion://workflow/production/{fal,opendesign,atlascloud,wavespeed,account,compatible}`. The provider references belong to the existing production guidance; the supporting `openmotion-media` Skill (`openmotion://workflow/media/start`) carries the generation workflow, and the retired `openmotion-debug-media` Skill is not distributed. `action=generate` requires provider, provider-native model ID, projectId, requestId, modality and prompt. Provider parameters use the selected model API schema; no key argument is accepted. The queued job is polled with action=status and the same projectId/jobId; completed means actual validated files were imported under assets/generated. Cancellation is local and best effort remotely, without a refund promise. Edits still require a fresh project revision/version. Settings → Model providers (`模型供应商` in Chinese UI) manages keys, compatible endpoints, catalogues and defaults. Account authorization registers a separate provider and its entitled models. OpenDesign Cloud retains its separate workspace key and public HTTPS gateway origin. The inspect result includes configured defaults and supported reference URIs. See [provider settings](provider-settings.md) for protocol and execution boundaries; configuration and live discovery are not proof of paid generation success.

## Final video presentation

Creation and content edits use `openmotion_open_preview(action=begin)` as silent business state, carrying workId through saves and final export. Production saves defer editor presentation until the final authored video is ready to preview. Only then open the right-hand Studio. After the MP4 completes and passes verification, call the discovered read-only `openmotion_show_video({projectId,workId})` once. Only this negotiated presentation extension binds the final-video App; ordinary open/save/review/display operations do not mount chat video areas. It reads the existing fixed work result and private media, rejects unfinished or unavailable exports and creates no project or render. Non-App clients discover sixteen domain names, including the asset compatibility alias; the template-card extension stays independent. See [final video playback and limits](inline-video.md).

## Media setup handoff

The media example in the MCP handbook starts with provider inspection. An available provider continues the existing brief or leads to a question about the desired generated content or reference. With no available provider, `openmotion_open_preview({ target: "providers" })` returns the Model providers page handoff, independently of any project; the Agent guides the user to sign in with an OpenDesign account (a paid plan provides multimodal generation) or save another provider's key. When several providers are available, OpenDesign (account, then Cloud) is used first and the Agent picks among the others without asking, stating the chosen provider and model. It accepts only `action: "open"`, `embedded` and `presentation`, with the same host focus policy as template browsing. The host presents the page and verifies visibility. The user saves credentials in settings and reports completion, then the Agent re-inspects and resumes the original request. Setup and discovery do not submit generation jobs. The `inspect` response includes `settingsHandoff` with this public call.

### Preferred generation

For NEW generated media, use openmotion_media_use inspect/reference/models to discover configured capabilities, then openmotion_assets_use generate with the full model ID, status with the original jobId, get/read at a pinned assetId/versionId, and import_to_project only for selected film assets. No project is required for standalone generation. Use openmotion_assets only when tools/list lacks the preferred name; it has no read, so inspect adopted local media with available tools. Keep old media_use jobs on their original Tool/projectId/jobId and never import their project files twice. Image references pin exact image versions: image models with supportsImageReference edit with up to their maxInputImages (one for local Codex and OpenDesign account models), and video models that report maxInputImages take one image as the first frame; first-and-last-frame video is unavailable. Use resume with the original jobId and a stable requestId to check a failed/interrupted Cloud task with a known remoteId, without uploading inputs or submitting another paid generation. Cancelled jobs and confirmed remote failures cannot resume. Use retry_save only for retained local outputs (savePending); regeneration is a separate paid request requiring authorization. Studio offers Check original task on eligible failed jobs. Reference counts follow the selected model before any reference file is read; there is no fixed library count ceiling. Local Codex/account editing remains one image, video remains one first frame, and project referenceAsset remains image-only. Follow the shared generation boundary in production/materials. Keep credentials in Settings, obtain missing spend consent, explain unsupported capabilities and proposed alternatives, and do not silently downgrade. Regenerate only within the asset count and spend the user explicitly approved, including any retries they approved; otherwise ask before another paid request; unknown outcomes require original-job inspection, not a new paid submission.
