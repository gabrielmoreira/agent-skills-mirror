# Install OpenMotion from source

For an Agent asked to install OpenMotion from this repository, use the source installation below. This is the default repository installation route. Only use npm installation when the user explicitly selects it; follow the [published application guide](docs/install.md) instead of mixing source and package setup. npm remains required to install this checkout's locked dependencies and build Studio.

## Codex: automatic source installation

Collect OS/CPU, Git, Node.js/npm and the current host once. Source validation uses Node.js 26.11.1. Codex must support `codex plugin add`. Preserve projects, credentials, unrelated plugins and MCP configuration. Configure only the current host.

Before running the installer, including setup from an existing checkout, export `OPENMOTION_ONBOARDING_LANGUAGE` in the same shell. Derive it from the latest user request's language, not the OS or host UI language. Supported codes are `zh`, `en`, `ja`, `ko`, `fr`, `es` and `pt`; normalize locale tags to their lowercase primary code and use `en` for unsupported languages. For a Chinese request, run `export OPENMOTION_ONBOARDING_LANGUAGE=zh` before the commands below so the welcome/cards are prepared in Chinese.

```sh
curl -fsSL https://raw.githubusercontent.com/nexu-io/openmotion/main/install.sh -o /tmp/openmotion-source-install.sh
bash /tmp/openmotion-source-install.sh
```

`OPENMOTION_INSTALL_DIR` selects a persistent empty absolute destination. The script downloads one shallow snapshot, installs locked dependencies, builds Studio once, registers the local plugin, probes MCP and prepares the template library. Do not separately run npm start, install dependencies again or inspect unrelated repositories.

If the intended checkout already exists, inspect its remote, version and local changes first, then run `bash scripts/install-motion.command` from that checkout. Preserve an active or foreign source; never overwrite it or silently switch installations. Preserve an existing `MOTION_DATA_DIR` and use the same workspace for Studio and MCP. Keep projects and credentials outside the checkout. Read the checkout's AGENTS.md before repository changes.

Command-local Git LFS overrides keep optional media as pointers even when global LFS configuration is stale. No global Git configuration is changed. A read-only source check runs before dependency work; unknown inventory or installed-source conflicts stop with a concrete recovery instruction. See [clone size and optional media](docs/repository-storage.md).

The installer saves phase timings and full onboarding details under `.artifacts/install/`. Read the concise result once and complete onboarding in this same installation turn. Prepare the cards and separate welcome before opening the right-hand library. For native reference cards, use the exact prepared IDs with onboarding:false, then stream welcomeMarkdown as the ordinary final reply after the Tool result. For self-contained builtin fragments, publish before the library reveal and stream welcomeMarkdown followed by the ready cards reference. Never enqueue internal instructions as another user message or end early to await a callback. Download time depends on the network; no fixed installation duration is guaranteed.

## Other local hosts: source and MCP

Use Git, npm and Node.js 26.11.1:

```sh
git -c filter.lfs.process= -c filter.lfs.smudge= -c filter.lfs.required=false clone --depth 1 --single-branch --branch main https://github.com/nexu-io/openmotion.git
cd openmotion
npm ci
npm run build:studio
npm start
```

Open the actual studioUrl or previewUrl printed at startup. Follow [manual MCP configuration](README.md#manual-mcp) and the [host adapter guide](docs/agent-adapters.md) to connect this checkout's mcp.ts and the same data directory. Source preview/export also need working Chrome/Chromium and FFmpeg/ffprobe; see [runtime setup](docs/usage.md). Merely starting Studio does not register an Agent connection.

## Verify installation and deliver onboarding

For the default nine-reference pool, follow `inlinePresentation.status=native_required`: use its three frozen random selections with the compatible native presentation Tool. External posters/videos require the native App's declared media origin and cannot be published as a fixed-CSP visualization fragment. Refresh stale connection discovery through the supported host action when needed. Verify the actual in-conversation card resource and image/video playback; do not replace inline cards with a right-hand browser page or substitute builtin examples. Fragment publication below applies only to `status=prepared` with self-contained media.

Discover the installed tools and call openmotion_get_project to verify the expected workspace. Registration or an independent probe alone does not prove this chat loaded the tools. Keep installed files, MCP access and host presentation results distinct.

Follow the [shared onboarding contract](docs/install-onboarding.md#installation-success-reply) in this turn: finish preparing the welcome and three cards, open the real template library without creating a project, confirm visibility once and immediately stream the welcome as normal reply text followed by the cards-only content reference (or use the supported native fallback). Reuse this installation; do not reinstall to recover presentation. A CLI without a renderer reports that limitation and the real library link. Prepared files, queued host actions and printed URLs do not prove visible delivery. Do not create a video, export or call paid models as part of installation.
