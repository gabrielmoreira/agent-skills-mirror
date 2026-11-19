# Install OpenMotion

<!-- source-only:start -->
For an Agent asked to install OpenMotion from this repository, use the source installation below. Commands run from the checkout root even though this guide lives under docs/. This is the default repository installation route. Only use npm installation when the user explicitly selects it; follow the [published application guide](#published-npm-application) instead of mixing source and package setup. npm remains required to install this checkout's locked dependencies and build Studio.
<!-- source-only:end -->

## Install the main OpenMotion Skill

Install the main `openmotion` Skill once through the official Skills CLI as part of setup:

```sh
npx --yes skills@1.9.0 add nexu-io/openmotion --skill openmotion --global --agent AGENT --copy --yes
```

Use `codex` for Codex and `claude-code` for Claude Code. For DSH, use `universal`: install this extra entry even when DSH reads its production Skills from its own plugin bundle. Other hosts use their supported Skills CLI target, or `universal` if none exists. Select only the intended host; custom/isolated profiles use an explicitly selected project/profile scope instead of the daily global profile.

<!-- source-only:start -->
For the DSH source-workspace route below, the one-command installer performs this official CLI step in the selected profile's scope. Do not run the global command separately before it.
<!-- source-only:end -->

Reuse an existing official installation. Preserve unrelated Skills, a foreign same-name entry and the CLI's telemetry opt-outs. `OPENMOTION_SKIP_PUBLIC_SKILL=1` skips this optional step. A CLI failure does not block Studio/MCP setup or onboarding; report it and continue. An owned legacy bundle must migrate through setup before the main Skill can occupy its path. Do not reinstall merely to generate another install event.

Derive `OPENMOTION_ONBOARDING_LANGUAGE` from the latest user request before running any onboarding preparation: `zh`, `en`, `ja`, `ko`, `fr`, `es` or `pt` (otherwise `en`). Do this for every host, independently of the OS language.

Skills CLI installs instructions only. Continue the chosen runtime setup below in this conversation, reusing an existing installation. Do not wait for the new Skill to hot-load or register a second MCP connection.

<!-- source-only:start -->
## DSH: workspace plugin

When the current host is DSH and the user wants the integrated workspace, use the single source-checkout installer below. Do not apply the Codex or generic MCP route, register a second adapter, start another DSH instance or restart this conversation.

Collect the existing checkout, current profile, `DSH_HOME`, workspace data directory and request language once from the host context. Reuse an intended checkout after checking its remote and local changes; do not inspect installer internals, rescan processes or repeatedly read the same guides. For a new source installation, shallow-clone the selected branch once with optional LFS downloads disabled as shown under [Other local hosts](#other-local-hosts-source-and-mcp). Run this from that checkout using Node.js 26.11.1 and the actual existing profile:

```sh
node integrations/dsh/install.ts --profile PROFILE --data-dir /absolute/workspace/data --language zh
```

Replace the profile/data arguments with this host's actual values and derive the language from the latest request. Pass `--dsh-home /absolute/dsh/home` when the current profile uses a custom home not already in `DSH_HOME`; `--url` accepts the actual local `DSH_WEB_URL`. The installer preserves model settings and unrelated profile entries, reuses matching locked dependencies and Studio build fingerprints, builds the local plugin directly without a tarball/profile package-install round trip, enables the workspace and the two native card components when absent and prepares the shared welcome/cards once. Reruns preserve the same selected IDs. An existing prepared receipt can be retained with `--resume /absolute/onboarding-receipt.json`. Official `npx skills add` installs the main Skill with `--agent universal` in this selected profile's project scope; do not separately reinstall it globally for an isolated DSH trial. A Skill CLI failure is reported without blocking the workspace.

**Finish presentation in this same turn.** Follow the compact result's `nextActions`. The profile is watched: probe activation rather than assuming a host restart is needed. If the browser still shows the old DSH interface, refresh that page once through the host's supported browser surface; otherwise report this one manual refresh as pending. Never kill DSH, invent a restart command or silently declare completion. Load `cardPresentation.skill`, then invoke **`propose_action`** with exactly `cardPresentation.arguments`. The native recommendation card opens the template library on the right of the current conversation and shows the shared localized welcome above the same three IDs. Do not open the default sample project instead, or call `openmotion_show_template_recommendations` when that separate MCP App tool is unavailable. Do not replace the welcome with a technical installation report. `onboardingComplete:false` and `awaiting_host_delivery` explicitly mean the visible welcome/cards are still pending; a healthy status route or a prepared file is not completion. When card presentation is unavailable or fails, show the same welcome and three names, summaries and preview links as text, and state the display limitation.

Published tarballs remain available through [OpenMotion for DSH](../integrations/dsh/README.md#download-and-install-the-plugin) and [DSH plugin downloads](https://releases.open-design.ai/open-motion/integrations/dsh/stable/latest.json). This is the separate pinned-release route; preserve its source commit and checksum. Do not probe stable/test/main manifests or switch releases during the existing-checkout route. Stable becomes available after the first coordinated publication containing DSH; earlier explicit development installs can select `--channel=main`. Installation does not authorize creating or exporting a video.

## Codex: automatic source installation

Collect OS/CPU, Git, Node.js/npm and the current host once. Source validation uses Node.js 26.11.1. Codex must support `codex plugin add`. Preserve projects, credentials, unrelated plugins and MCP configuration. Configure only the current host.

Before running the installer, including setup from an existing checkout, export `OPENMOTION_ONBOARDING_LANGUAGE` in the same shell. Derive it from the latest user request's language, not the OS or host UI language. Supported codes are `zh`, `en`, `ja`, `ko`, `fr`, `es` and `pt`; normalize locale tags to their lowercase primary code and use `en` for unsupported languages. For a Chinese request, run `export OPENMOTION_ONBOARDING_LANGUAGE=zh` before the commands below so the welcome/cards are prepared in Chinese.

```sh
curl -fsSL https://raw.githubusercontent.com/nexu-io/openmotion/main/install.sh -o /tmp/openmotion-source-install.sh
bash /tmp/openmotion-source-install.sh
```

`OPENMOTION_INSTALL_DIR` selects a persistent empty absolute destination. The script downloads one shallow snapshot, installs locked dependencies, builds Studio, registers the local plugin, probes MCP and prepares the template library. Do not separately run npm start, install dependencies again or inspect unrelated repositories.

If the intended checkout already exists, inspect its remote, version and local changes first, then run `bash scripts/install-motion.command` from that checkout. Preserve an active or foreign source; never overwrite it or silently switch installations. Preserve an existing `MOTION_DATA_DIR` and use the same workspace for Studio and MCP. Source reinstallation checks content fingerprints for the build inputs and generated outputs, rather than only the presence of index.html. Matching builds are reused; source-only changes rebuild without reinstalling matching dependencies, while a changed lockfile or missing installation reruns npm ci. A checkout without a prior fingerprint needs one initial rebuild. Prebuilt ZIPs retain their sealed editor. Keep projects and credentials outside the checkout. Read the checkout's AGENTS.md before repository changes.

Command-local Git LFS overrides keep optional media as pointers even when global LFS configuration is stale. No global Git configuration is changed. A read-only source check runs before dependency work; unknown inventory or installed-source conflicts stop with a concrete recovery instruction. See [clone size and optional media](repository-storage.md).

The installer saves phase timings and an immutable onboarding receipt under `.artifacts/install/`. Complete onboarding in the same turn: open the real library once, publish the prepared HTML into the current chat's permitted visualization directory, then emit the publication result's complete `finalReplyMarkdown` verbatim (maintained welcome followed by the card reference). Do not summarize the welcome or replace it with a status report; keep connection diagnostics in progress updates. If recovery confirms the welcome was actually delivered earlier, publish with `--welcome-delivered` to return cards only. Only the three frozen selections are embedded, with complete silent project previews and posters. Open the library once and use that call's result or initial page state; do not add visibility, screenshot, inventory or playback audits. If opening fails or is unconfirmed, replace the library-visible heading with the actual result and usable link; installation remains installed. A queued host refresh uses the saved recovery command without reinstalling or resampling. Presentation and automatic current-chat MCP activation are independent: missing host control does not block the HTML cards, and visible cards do not prove automatic activation. Never enqueue internal instructions as another user message. Download time depends on the network.

## Other local hosts: source and MCP

Use Git, npm and Node.js 26.11.1:

```sh
git -c filter.lfs.process= -c filter.lfs.smudge= -c filter.lfs.required=false clone --depth 1 --single-branch --branch main https://github.com/nexu-io/openmotion.git
cd openmotion
npm ci
npm run build:studio
npm start
```

Open the actual studioUrl or previewUrl printed at startup. Follow [manual MCP configuration](../README.md#manual-mcp) and the [host adapter guide](agent-adapters.md) to connect this checkout's mcp.ts and the same data directory. Source preview/export also need working Chrome/Chromium and FFmpeg/ffprobe; see [runtime setup](usage.md). Merely starting Studio does not register an Agent connection. Once connected, run `node scripts/install-onboarding.mjs --host HOST` from the checkout using this connection's `MOTION_DATA_DIR`, replacing `HOST` with the actual host name such as `claude`. Then follow the shared onboarding below using the returned three IDs and presentation arguments.

After source setup, follow [Installation-success reply](#installation-success-reply) below. Do not run the npm setup as well.

## Published npm application

Use this alternative only when the user selects npm. Read the [stable guide](https://releases.open-design.ai/motion) or the explicitly selected [test guide](https://releases.open-design.ai/open-motion/dev/install.md). Do not guess a package version or execute unresolved placeholders below. The release generator fills this section and the shared onboarding contract from this same file. Generated npm guides also pin the public Skill source to the application's release commit; source readers use main. Do not fetch main's Skill as an extra step for a pinned release.

Codex can also use a pinned bootstrap: run `bash install.sh --package EXACT_PACKAGE_SPEC` from the checkout, using the exact published `@openmotion/app@VERSION`. A reviewed HTTPS candidate or an absolute local `.tgz` requires `OPENMOTION_INSTALLER_SHA256` from its matching manifest before this command. With no arguments `install.sh` still uses source; other hosts use the published guide's `openmotion setup --host` command.
<!-- source-only:end -->

This guide pins the complete npm application `{{PACKAGE_SPEC}}` on the **{{CHANNEL}}** software channel. It includes MCP, the built Studio and production Skills. The default template environment is **{{TEMPLATE_ENVIRONMENT}}**: new test versions embed DEV defaults, stable versions embed prod, and previously published versions keep their original environment.

If you are reading this file in the source repository and see `{{...}}`, it is a template, not a published installation instruction. Do not guess a package name or version.

## Instructions for the Agent

1. Collect OS/CPU, Node.js/npm versions and the current Agent identity together, using the host's supplied context where available. Node.js 22.18+ with npm and the Agent must already be installed. Supported native targets: {{TARGETS}}. If a macOS target has no declared minimum version, proceed with setup and native executable checks; do not infer a minimum from the build/test machine's OS version. Do not claim support for another target from package-download success.
2. Select the current host explicitly: `codex` (Codex), `claude` (Claude Code), `deepseek` (DeepSeek Harness) or `workbuddy` (WorkBuddy) have registration adapters. Any other local Agent, such as OpenCode, Cursor Agent or Gemini CLI, passes its own lowercase name (for example `opencode`); setup installs the same application and Skills, leaves that host's configuration unchanged and returns `agentRegistration` for the Agent to add to its own MCP configuration. Never borrow another host's adapter. An explicit user selection takes precedence. Do not infer the current host from which CLIs happen to be installed. Ask only when the current host or required profile cannot be established. Configure only that host; preserve projects, credentials and unrelated MCP/Skills settings.
3. For a test candidate, use a separate host profile, application home, project data and Skills directory. Keep those paths and reuse them for prepare and future reconnects. The [platform installation recipes]({{DETAILS_URL}}) describe the actual supported options. Do not run a test candidate into the user's daily profile by default.
4. Choose exactly one setup command below, applying the test isolation paths first when required. Setup starts checked video-component downloads in the background. Do not wait for prepare to connect MCP, create/edit projects or open ordinary preview. Studio shows preparation status and retry; media import, automated capture and export require their respective components. Compatible phase-one updates can keep existing connections; reconnect closed or incompatible transports. Verify the selected installation/workspace with one actual `openmotion_get_project` call, reusing setup's successful same-chat read when available. Complete Tool/Skill inventory comparison belongs to development/release acceptance, not ordinary installation. If this chat has not loaded them or still points at another installation, use `onboarding.directAccess` below; registration alone does not prove native loading. Do not postpone the installation reply or template library opening until a new chat or the first MCP call.
5. On successful setup, follow the installation-success reply below in this same conversation. Open the template library without creating a project. Installation does not authorize downloading template project source, rendering or calling a paid model. Report a failed installation honestly; do not claim success until it is fixed.

For npm network failures, automatically try `https://registry.npmjs.org` then `https://registry.npmmirror.com`, at most once per registry, counting the initial failed attempt. Respect an explicitly selected registry and host policy. Set `npm_config_registry` and `npm_config_fetch_retries=0` only for that attempt, including setup's npm child process. Keep the exact version; verify any mirrored tgz against the matching immutable guide's SHA256 before executing it. If both fail, follow [npm download recovery]({{DETAILS_URL}}#npm-download-failures) for network checks and a terminal handoff. Permission or checksum failures stop immediately. A local tgz still needs npm access for setup's production dependencies.

<!-- installation-onboarding:start -->
## Installation-success reply

Accept presentation and automatic MCP activation independently.

### Presentation acceptance

1. Open the actual local template library once, without creating a project. Detailed library inspection is unnecessary.
2. On every Agent, deliver the maintained localized welcome and exactly three full-duration project-preview cards. Choose a supported native MCP App, DSH action-card component, or host HTML surface; host identity alone is not a reason to use text. On Codex, publish the self-contained HTML fragment and place its returned content reference directly after the welcome in the final reply. Native MCP Apps remain an alternative for original reference films when native tools are available. Claude and other hosts use their supported card surface; DSH uses its action cards. If no card surface is supported or a real presentation attempt fails, show the same three template names, summaries and preview links as text in the same order. Retain the shared welcome/introduction and explain the card limitation briefly; do not claim that a card was displayed. A general DSH workspace gallery is not a substitute for the three installation recommendations.
3. Preserve the three IDs/order sampled without replacement from the four-entry pool in `shared/onboarding-templates.ts` (the catalog IDs referenced by PR #472). Use the presentation tool's result or the host's normal rendering; do not start an additional visibility audit. Publication or a queued operation alone is not confirmed display. Image decoding, advancing video playback and enlarged-preview checks belong to development/release acceptance; do not run or wait for them during installation. Record media failures separately without invalidating installation, connection or confirmed card visibility. Human audiovisual review remains separate.

`onboardingStatus` and `onboardingComplete` describe presentation only. Setup and connection recovery leave it `awaiting_host_delivery` and incomplete until visible delivery is confirmed; library preparation failure remains `preview_unavailable`. `hostHandoff.automaticActivation`, its reason and `hostSessionVerified` report the independent connection check. A working native connection can present the component even when the installer's control socket is unavailable. Visible cards do not prove that installation loaded MCP automatically, and activation failure does not invalidate an otherwise verified presentation.

### Self-contained project previews (default)

Default preparation freezes three IDs/order once across `catalog`, `inlinePresentation`, `hostHandoff` and recovery. It returns `prepared` with an integrity-locked HTML path, SHA256 and the selected IDs. The fragment embeds only those three projects' prebuilt WebM (VP9)/JPEG bytes. Complete silent videos retain 12 fps, with widths up to 512 px and two-pass VP9 encoding at 28–48 kbit/s per template. A CRF 16 intermediate avoids compounding compression loss; JPEG posters come directly from that intermediate. The builder reserves a media budget for the longest three-film combination, and regression tests render all four three-of-four combinations in every supported language. The renderer enforces the complete document's 1,000,000-byte limit; changing codecs does not guarantee fine-text or full-screen fidelity. Explicit builtin examples retain their existing MP4 previews. It needs neither external media origins nor current-chat MCP activation. Publish it with `scripts/inline-onboarding.mjs --publish-from PATH --sha256 SHA256 --host-directory DIRECTORY` using the current chat's explicitly permitted visualization directory. Publication reads the frozen language from the hash-verified document and returns `finalReplyMarkdown`, containing the complete maintained welcome followed by `contentReference`. After successful library opening, emit that complete field verbatim as normal final reply text (use the truthful heading exception below otherwise); do not summarize it or replace the introduction with an installation-status report. Report connection diagnostics separately in progress updates. If the welcome was actually delivered earlier, publish with `--welcome-delivered` to return only the card reference. The document itself contains cards only. A prepared/published file does not establish visible delivery.

These are **silent renders of the repository's editable projects**, not original reference films or a claim of verified recreation fidelity. All four previews are prebuilt by maintainers with `node scripts/build-onboarding-previews.mjs`; installation does no rendering or media download. The builder uses pinned Hyperframes, Chrome and FFmpeg, strips audio only in scratch copies, preserves complete project duration, and records source/media hashes. `--hydrate-fonts` may retrieve hash-verified project fonts missing from a source checkout. Original reference videos are never downloaded for embedding. No source project is changed by the build. HTML project-card descriptions use a localized introduction label followed by the localized summary: `简介：` (zh), `Summary: ` (en), `概要：` (ja), `소개: ` (ko), `Présentation : ` (fr), `Resumen: ` (es) and `Resumo: ` (pt). The typed `inlineDescriptionPrefixes` dictionary in `mcp-ui/template-recommendations/i18n.ts` covers every supported language; rendered-card regression checks enforce the labels in all seven languages. Media provenance is documented here rather than repeated in card descriptions. Always pass the user request language explicitly when preparing installation HTML; the renderer default is English.

### Native original reference cards (alternative)

Native MCP Apps retain the original reference films and their declared media origin. For hosts using a supported native MCP App route and a working native connection, call `openmotion_show_template_recommendations` with the exact prepared IDs/order, request language and `onboarding:true`. After successful library opening this displays the maintained welcome above the three cards; do not duplicate it in the final reply. If library opening failed or is unconfirmed, use `onboarding:false` and a truthful reply as described below. Use `onboarding:false` after a welcome already delivered. Explicit `renderInlineOnboarding({previewSource:'reference', ...})` returns `native_required`, since the document renderer cannot inherit native App media policy. Preserve the selection; do not substitute builtins or alter host security. A shell presentation call does not mount a native component. Original reference playback requires network access.

### DSH conversation cards

For the integrated DSH workspace, load `openmotion-template-recommendations` before calling `propose_action` with action `openmotion_template_recommendation`. On installation, use `details.onboarding=true`, the request language, `libraryOpened` only after confirmed opening, and exactly the three prepared IDs/order. Read each selected template to fill truthful title, summary and preview/poster links; do not infer editable source from the card's provenance. Do not resample. Use the maintained welcome in the card, or stream it once above the card without duplicating it. Card preview and selection never create a project; continue only after the user's creation brief. If this host lacks action-card support, try another supported card surface, otherwise give the same three text recommendations.

### Automatic current-chat activation

Reuse setup’s successful same-chat workspace read; do not repeat it in the Agent. This is a separate acceptance track: installation must automatically load the native tools and verify the installed workspace in the installing chat. Registration, an independent handshake, a queued refresh or a later connected chat does not establish that result. Record the installation/chat identities and actual host recovery path; do not infer automatic activation from presentation acceptance.

Source and npm setup use `prepareInstallationFlow`. After registration, an existing supported Codex control connection checks `thread/loaded/list` for the calling `CODEX_THREAD_ID`. A healthy native connection is reused. Missing/stale tool discovery, an outdated application version or a mismatching immutable card resource requests one `config/mcpServer/reload`. The refresh is queued for a host tool boundary; an immediate status read is not its completion.

After that tool step finishes, execute the returned `recovery.command`/`recovery.args` in this same turn. The private immutable receipt preserves the chat, application, workspace, language, three IDs/order and library URL. Recovery performs verification only: no reinstall, library startup, resampling or additional reload. Native discovery and `openmotion_get_project` must verify the expected workspace through the calling thread before `hostSessionVerified` is true. They do not prove visible welcome/cards.

Use `OPENMOTION_CODEX_SOCKET` for an explicitly known existing control entry, otherwise use the current profile's default entry. Resolve that entry with `realpath`; current-user-owned symlinks are supported when the resolved target is a current-user-owned socket in a current-user-owned directory that is not group- or world-writable. Pass the verified canonical path to the CLI proxy, then verify that the existing host has this chat loaded before any reload. Resolving this known entry is supported discovery, not endpoint guessing. Missing, dangling, cyclic, foreign-owned and unsafe targets remain blocked.

Do not scan unrelated paths for endpoints, start another app-server to simulate this chat, alter host listeners/security, inject instructions through `codex queue` or automatically restart Codex. If the user explicitly chooses to reconnect, record it as manual recovery; it does not establish automatic activation in the original installing chat. A private-stdio host with no supported reload capability blocks automatic-activation acceptance. Retain that reason independently in diagnostics and the receipt. Use already working native tools directly to deliver the welcome/cards; do not withhold presentation because the script control socket is missing.

Codex plugin setup reaches this contract through `extensions.com.openai.onboardingSkill`. Its directory must also be in the plugin's `skills` roots. CLI registration alone does not invoke the desktop install callback or create a current-chat refresh capability. Installed files, current-chat connection and visible native delivery are separate outcomes.

### Open the library

Use `openmotion_open_preview({target:"templates"})` when loaded, otherwise setup's exact `preview.previewUrl`. Open it using the current Agent's supported browser surface (Codex's right-hand browser or DSH's workspace template view), preserving embedding parameters and reusing its tab. With CUA, create it using `cua.createBrowserTab('iab', previewUrl, {visible:true})`, mark it as a deliverable and complete mandatory browser bookkeeping. Otherwise use the supported `open_in_codex` browser target with `placement:"right"` and no other thread ID. Use only the opening call's result or initial page state; do not add hidden-tab/reveal choreography, snapshots, screenshots, inventory, layout or media checks. If the call fails, is only queued or cannot confirm opening, report the actual result and a usable URL without claiming visibility. Library-opening failure does not invalidate installation or block the welcome/cards; change the library-visible heading as described below. Never create a placeholder project or submit project display receipts for the library.

### Welcome copy and blocked delivery

The native component uses the shared localized welcome dictionary. The Chinese welcome begins:

```text
🎉 OpenMotion 安装好啦，右侧就是模板库！

我是你的开源视频创作搭档，我有丰富的高水准视频模板，也支持从参考视频或一个灵感出发，和你一起创作精彩的视频。

模板库支持搜索，也可以随意浏览，找到喜欢的点击「复刻模板」就能开始你的创作！

不想自己找？先看看我挑的这 3 个 👇
```

If no supported card route can be displayed and the library opening succeeded, use these three maintained paragraphs for Chinese requests, then list the same three prepared template names, summaries and preview links as text:

```text
🎉 OpenMotion 安装好啦，右侧就是模板库！

我是你的开源视频创作搭档，我有丰富的高水准视频模板，也支持从参考视频或一个灵感出发，和你一起创作精彩的视频。

模板库支持搜索，也可以随意浏览，找到喜欢的点击「复刻模板」就能开始你的创作！
```

Use the same localized introduction/discovery wording across Codex, Claude, DSH and other Agents; adapt only the location of the library and whether recommendations are cards or text. Never claim a right-hand library opened in a host without one. The top-level `welcomeMarkdown` supplies these paragraphs in the request language. After a successful library opening, use the maintained copy without an extra status report. If the opening failed, was only queued or cannot be confirmed, replace its library-visible heading with a concise statement of the actual result and the usable library URL when available. Retain the introduction; deliver prepared cards when possible. This exception also applies to the library-visible heading in published `finalReplyMarkdown` and native welcome copy: do not emit it as a success claim after a failed opening. If native copy cannot be adapted, use the cards-only native arguments (`onboarding:false`) and provide the truthful welcome as reply text.

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

## Choose the selected host's setup command

The commands below show normal installations. For test candidates, apply the separate configuration/profile, home, data and Skills paths from the [platform recipes]({{DETAILS_URL}}) first. Run only the selected row.

| Current Agent | Setup command | Host-specific selection |
| --- | --- | --- |
| Codex | `npx --yes --package "{{PACKAGE_SPEC}}" openmotion setup --host codex` | Preserve the selected `CODEX_HOME` and Skills root. |
| Claude Code | `npx --yes --package "{{PACKAGE_SPEC}}" openmotion setup --host claude` | Preserve the selected `CLAUDE_CONFIG_DIR` and Skills root. |
| DeepSeek Harness | `npx --yes --package "{{PACKAGE_SPEC}}" openmotion setup --host deepseek --profile PROFILE` | Replace `PROFILE` with the actual selected profile from the host context; do not guess `web` or `desktop`. The standard macOS Desktop CLI is detected even when `dsh` is absent from PATH; use `--dsh` for another executable location. |
| WorkBuddy | `npx --yes --package "{{PACKAGE_SPEC}}" openmotion setup --host workbuddy` | Preserve the selected `WORKBUDDY_CONFIG_DIR` and Skills root. |
| Any other local Agent | `npx --yes --package "{{PACKAGE_SPEC}}" openmotion setup --host AGENT` | Replace `AGENT` with the current Agent's lowercase name, such as `opencode`. Skills default to `~/.agents/skills`; use `--skills-dir` if this Agent reads another root. Add `agentRegistration.transport.command` and `args` exactly as returned to this Agent's documented local stdio MCP configuration, refresh MCP, then call `openmotion_get_project`. Until the native tools load, use `onboarding.directAccess`. [Other local Agents]({{DETAILS_URL}}#other-local-agents) |

Optional: explicitly wait for all video components or retry preparation for the same installation:

```sh
npx --yes --package "{{PACKAGE_SPEC}}" openmotion prepare
```

Repeat an explicit `--home` from setup on prepare. Setup installs the selected host's MCP and Skills; a second installer or application/manifest download is unnecessary. Use `openmotion --help`, `setup --help` or `prepare --help` from this exact package for supported options. Inspect installer source or host internals only to investigate a concrete failure; a missing CLI on PATH alone is not a reason to create a wrapper.

## Runtime and environment

Setup copies the checked application into a managed writable directory and installs its locked production npm dependencies. The application and user projects do not run from the temporary npx cache. Setup starts a detached preparation worker for the platform's independent native archives concurrently: browser/FFmpeg/ffprobe separately on macOS, browser/combined media on Windows. The local backend and Studio start without waiting. Studio displays per-component download/verification/extraction/checking status and retries failed components. Installers, MCP and Studio join shared cache locks rather than downloading again. An explicit prepare waits for all components and reports failure; successful checked components remain reusable. No export starts automatically after preparation. This is not an offline package.

There is no persisted switch-environment command in this version. Test versions embed DEV defaults and use an environment-specific installation; stable versions embed prod. DEV access still requires the service network/authentication. A public npm package does not grant access or bundle private catalog contents. When changing environment, use a separate home/data/profile; merely setting an environment variable while running setup does not configure a later desktop Agent. Do not silently fall back from one environment to another.

## Upgrade, recovery and feedback

Pin this exact version when reproducing an issue. Before an upgrade, back up project data and preserve the same installation/data paths. Compatible phase-one updates retain existing connections and active exports. For an incompatible protocol, finish active exports before updating only this installation's connection and idle backend together; reconnect after setup/prepare. Refresh host discovery for new Tools or Skills, and preserve unrelated settings. Older applications may not read newer data formats: compatible reinstall or backup restoration requires separate verification. Moving a server-side default does not downgrade installed clients.

Include the exact version, OS/CPU, Node/Agent versions, template environment, project/revision, reproduction and redacted logs in a report. Installation, real Agent creation, technical MP4 export and human audiovisual acceptance are separate results.

Release identity: source `{{COMMIT}}`; npm tgz SHA256 `{{TGZ_SHA256}}`. [Source and installation details]({{DETAILS_URL}}).
