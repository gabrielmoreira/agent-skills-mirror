# Shared installation onboarding

Used by source installation, npm application installation and plugin setup.

<!-- installation-onboarding:start -->
## Installation-success reply

Accept presentation and automatic MCP activation independently.

### Presentation acceptance

1. Open the actual local template library once, without creating a project. Detailed library inspection is unnecessary.
2. Deliver the maintained welcome and exactly three full-duration project-preview cards. On Codex, publish the self-contained HTML fragment and place its returned content reference directly after the welcome in the final reply. Native MCP Apps remain an alternative for original reference films when native tools are available.
3. Preserve the three IDs/order sampled without replacement from the four-entry pool in `shared/onboarding-templates.ts` (the catalog IDs referenced by PR #472). Use the presentation tool's result or the host's normal rendering; do not start an additional visibility audit. Publication or a queued operation alone is not confirmed display. Image decoding, advancing video playback and enlarged-preview checks belong to development/release acceptance; do not run or wait for them during installation. Record media failures separately without invalidating installation, connection or confirmed card visibility. Human audiovisual review remains separate.

`onboardingStatus` and `onboardingComplete` describe presentation only. Setup and connection recovery leave it `awaiting_host_delivery` and incomplete until visible delivery is confirmed; library preparation failure remains `preview_unavailable`. `hostHandoff.automaticActivation`, its reason and `hostSessionVerified` report the independent connection check. A working native connection can present the component even when the installer's control socket is unavailable. Visible cards do not prove that installation loaded MCP automatically, and activation failure does not invalidate an otherwise verified presentation.

### Self-contained project previews (default)

Default preparation freezes three IDs/order once across `catalog`, `inlinePresentation`, `hostHandoff` and recovery. It returns `prepared` with an integrity-locked HTML path, SHA256 and the selected IDs. The fragment embeds only those three projects' prebuilt WebM (VP9)/JPEG bytes. Complete silent videos retain 12 fps, with widths up to 512 px and two-pass VP9 encoding at 28–48 kbit/s per template. A CRF 16 intermediate avoids compounding compression loss; JPEG posters come directly from that intermediate. The builder reserves a media budget for the longest three-film combination, and regression tests render all four three-of-four combinations in every supported language. The renderer enforces the complete document's 1,000,000-byte limit; changing codecs does not guarantee fine-text or full-screen fidelity. Explicit builtin examples retain their existing MP4 previews. It needs neither external media origins nor current-chat MCP activation. Publish it with `scripts/inline-onboarding.mjs --publish-from PATH --sha256 SHA256 --host-directory DIRECTORY` using the current chat's explicitly permitted visualization directory. Publication reads the frozen language from the hash-verified document and returns `finalReplyMarkdown`, containing the complete maintained welcome followed by `contentReference`. After successful library opening, emit that complete field verbatim as normal final reply text (use the truthful heading exception below otherwise); do not summarize it or replace the introduction with an installation-status report. Report connection diagnostics separately in progress updates. If the welcome was actually delivered earlier, publish with `--welcome-delivered` to return only the card reference. The document itself contains cards only. A prepared/published file does not establish visible delivery.

These are **silent renders of the repository's editable projects**, not original reference films or a claim of verified recreation fidelity. All four previews are prebuilt by maintainers with `node scripts/build-onboarding-previews.mjs`; installation does no rendering or media download. The builder uses pinned Hyperframes, Chrome and FFmpeg, strips audio only in scratch copies, preserves complete project duration, and records source/media hashes. `--hydrate-fonts` may retrieve hash-verified project fonts missing from a source checkout. Original reference videos are never downloaded for embedding. No source project is changed by the build. HTML project-card descriptions use a localized introduction label followed by the localized summary: `简介：` (zh), `Summary: ` (en), `概要：` (ja), `소개: ` (ko), `Présentation : ` (fr), `Resumen: ` (es) and `Resumo: ` (pt). The typed `inlineDescriptionPrefixes` dictionary in `mcp-ui/template-recommendations/i18n.ts` covers every supported language; rendered-card regression checks enforce the labels in all seven languages. Media provenance is documented here rather than repeated in card descriptions. Always pass the user request language explicitly when preparing installation HTML; the renderer default is English.

### Native original reference cards (alternative)

Native MCP Apps retain the original reference films and their declared media origin. Only for this explicitly selected native route and a working native connection, call `openmotion_show_template_recommendations` with the exact prepared IDs/order, request language and `onboarding:true`. After successful library opening this displays the maintained welcome above the three cards; do not duplicate it in the final reply. If library opening failed or is unconfirmed, use `onboarding:false` and a truthful reply as described below. Use `onboarding:false` after a welcome already delivered. Explicit `renderInlineOnboarding({previewSource:'reference', ...})` returns `native_required`, since the document renderer cannot inherit native App media policy. Preserve the selection; do not substitute builtins or alter host security. A shell presentation call does not mount a native component. Original reference playback requires network access.

### Automatic current-chat activation

Reuse setup’s successful same-chat workspace read; do not repeat it in the Agent. This is a separate acceptance track: installation must automatically load the native tools and verify the installed workspace in the installing chat. Registration, an independent handshake, a queued refresh or a later connected chat does not establish that result. Record the installation/chat identities and actual host recovery path; do not infer automatic activation from presentation acceptance.

Source and npm setup use `prepareInstallationFlow`. After registration, an existing supported Codex control connection checks `thread/loaded/list` for the calling `CODEX_THREAD_ID`. A healthy native connection is reused. Missing/stale tool discovery, an outdated application version or a mismatching immutable card resource requests one `config/mcpServer/reload`. The refresh is queued for a host tool boundary; an immediate status read is not its completion.

After that tool step finishes, execute the returned `recovery.command`/`recovery.args` in this same turn. The private immutable receipt preserves the chat, application, workspace, language, three IDs/order and library URL. Recovery performs verification only: no reinstall, library startup, resampling or additional reload. Native discovery and `openmotion_get_project` must verify the expected workspace through the calling thread before `hostSessionVerified` is true. They do not prove visible welcome/cards.

Use `OPENMOTION_CODEX_SOCKET` for an explicitly known existing control entry, otherwise use the current profile's default entry. Resolve that entry with `realpath`; current-user-owned symlinks are supported when the resolved target is a current-user-owned socket in a current-user-owned directory that is not group- or world-writable. Pass the verified canonical path to the CLI proxy, then verify that the existing host has this chat loaded before any reload. Resolving this known entry is supported discovery, not endpoint guessing. Missing, dangling, cyclic, foreign-owned and unsafe targets remain blocked.

Do not scan unrelated paths for endpoints, start another app-server to simulate this chat, alter host listeners/security, inject instructions through `codex queue` or automatically restart Codex. If the user explicitly chooses to reconnect, record it as manual recovery; it does not establish automatic activation in the original installing chat. A private-stdio host with no supported reload capability blocks automatic-activation acceptance. Retain that reason independently in diagnostics and the receipt. Use already working native tools directly to deliver the welcome/cards; do not withhold presentation because the script control socket is missing.

Codex plugin setup reaches this contract through `extensions.com.openai.onboardingSkill`. Its directory must also be in the plugin's `skills` roots. CLI registration alone does not invoke the desktop install callback or create a current-chat refresh capability. Installed files, current-chat connection and visible native delivery are separate outcomes.

### Open the library

Use `openmotion_open_preview({target:"templates"})` when loaded, otherwise setup's exact `preview.previewUrl`. Open it in this chat's right-hand browser, preserving embedding parameters and reusing its tab. With CUA, create it using `cua.createBrowserTab('iab', previewUrl, {visible:true})`, mark it as a deliverable and complete mandatory browser bookkeeping. Otherwise use the supported `open_in_codex` browser target with `placement:"right"` and no other thread ID. Use only the opening call's result or initial page state; do not add hidden-tab/reveal choreography, snapshots, screenshots, inventory, layout or media checks. If the call fails, is only queued or cannot confirm opening, report the actual result and a usable URL without claiming visibility. Library-opening failure does not invalidate installation or block the welcome/cards; change the library-visible heading as described below. Never create a placeholder project or submit project display receipts for the library.

### Welcome copy and blocked delivery

The native component uses the shared localized welcome dictionary. The Chinese welcome begins:

```text
🎉 OpenMotion 安装好啦，右侧就是模板库！

我是你的开源视频创作搭档，我有丰富的高水准视频模板，也支持从参考视频或一个灵感出发，和你一起创作精彩的视频。

模板库支持搜索，也可以随意浏览，找到喜欢的点击「复刻模板」就能开始你的创作！

不想自己找？先看看我挑的这 3 个 👇
```

If neither card route can be displayed and the library opening succeeded, use these three maintained paragraphs for Chinese requests:

```text
🎉 OpenMotion 安装好啦，右侧就是模板库！

我是你的开源视频创作搭档，我有丰富的高水准视频模板，也支持从参考视频或一个灵感出发，和你一起创作精彩的视频。

模板库支持搜索，也可以随意浏览，找到喜欢的点击「复刻模板」就能开始你的创作！
```

The top-level `welcomeMarkdown` supplies these paragraphs in the request language. After a successful library opening, use the maintained copy without an extra status report. If the opening failed, was only queued or cannot be confirmed, replace its library-visible heading with a concise statement of the actual result and the usable library URL when available. Retain the introduction; deliver prepared cards when possible. This exception also applies to the library-visible heading in published `finalReplyMarkdown` and native welcome copy: do not emit it as a success claim after a failed opening. If native copy cannot be adapted, use the cards-only native arguments (`onboarding:false`) and provide the truthful welcome as reply text.

Keep installation, presentation and automatic activation separate. A card/library failure does not invalidate an installed application. Record unresolved results in diagnostics and the receipt, and report a relevant failure briefly rather than hiding it behind success copy. Do not run page/media audits, repeat installation or wait indefinitely for presentation. For recovery after an actually delivered welcome, use `--welcome-delivered` so it is not repeated.

### Explicit builtin compatibility

Explicit builtin examples can still use the same prepared document route. They never replace the four-entry pool's selected projects. Automatic MCP activation is assessed separately for either route.

### Accepted template selection

After a user submits the brief, retrieve the accepted ID with `openmotion_get_template` and read its instructions and motion document. When `hasHtmlProject` is true, use `openmotion-template-to-video` to reuse the editable source; preserve unchanged content when no customization was requested. Use `openmotion-recreate` only when the source has no editable project. Presentation provenance and preview rendering do not determine source capability or authorize creation.

Use the exact accepted ID and scope through [accepted template selection](../skills/openmotion-production/references/templates.md#accepted-template-selection). A named choice retains that recommendation; a generic agreement to several equal choices still needs a selection. Recreate only fills an unsent editable brief through a negotiated composer bridge, or copies it to the clipboard with a floating Toast. Browsing, playback and copying do not authorize creation/export; the user-sent brief does. Preserve customized requirements and any existing GUI-created project, and never create a duplicate during recovery.
<!-- installation-onboarding:end -->

## Maintained recommendation selection

`shared/onboarding-templates.ts` owns a curated pool of four references: **Bolt Skills｜团队能力展示**, **Glean Agents 发布**, **Dia 开放给 Arc 会员**, and **免费语音输入**. Each onboarding preparation samples three distinct entries without replacement. Inline cards, native handoff and the fallback catalog share that exact selection and order. The prepared document keeps its selection while playing, returning from detail or changing host context; only a new preparation draws again. Independent preparations may overlap.

Use the three prepared IDs returned in `inlinePresentation.templateIds`, the ordered `catalog.templates`, or the native handoff arguments. Do not draw a separate set for another surface. Cards reuse the same localized creation brief as the template library through `shared/template-prompts.ts`, including the exact title and ID. Their `reference` presentation kind does not assert that editable source is unavailable; resolve source capabilities only after the user submits the brief.

Default inline cards embed prebuilt project previews from `mcp-ui/template-recommendations/project-previews`, with the same playback controls, visibility pauses and error fallback as native cards. The separate native adapter retains original reference films at their immutable public `r.open-design.ai` URLs. Installation preparation performs no media download or generation. The three previous builtin examples remain available for explicit recommendations and never replace the current default selection. Existing chats retain their frozen presentation; source changes do not update an installed host or previously prepared onboarding document.

Cards show the selected reference's localized `original.promotionalUseCases` value in a persistent top-left media badge, without a field-name prefix. This purpose category stays visible while the video plays and at narrow widths; the bottom-right preview action remains separate. Empty/missing values are omitted. The category does not use the separate `visualPresentation` field or infer a value from the title. The shared design-system media-label recipe supplies its translucent surface and typography.
