# Install OpenMotion

For the local agent reading this guide: ordinary product installation uses a reviewed prebuilt package; source checkout is an explicit development route. Open the real template library and the complete welcome/cards presentation in the calling chat. Studio and Agent operations must use the same installation and workspace.

## Codex: prebuilt installation

To avoid dependency downloads during setup, select an artifact with prebuilt npm dependencies matching this machine. Lightweight packages still download dependencies during setup. See [target-specific package builds](docs/npm-installation.md).

Use the exact package specification and, for a candidate URL/file, SHA256 from its accepted installation guide or manifest. Do not guess an unpublished version or apply new installer flags to an older published package. This branch's local candidate is not a public release. A package containing `--onboarding-output` can use the current chat's existing inline renderer without MCP hot reload:

```sh
bash install.sh --package EXACT_PACKAGE_SPEC
```

`EXACT_PACKAGE_SPEC` is a pinned `@openmotion/app@VERSION`, a reviewed HTTPS candidate, or an absolute candidate `.tgz`; replace it from the actual artifact record. URL/file candidates additionally require `OPENMOTION_INSTALLER_SHA256` from that record. The remote entry verifies candidates before executing them. It downloads the prebuilt application rather than cloning or compiling the repository. Preserve a selected home/data/Skills root through the ordinary setup options; for acceptance use separate empty application, data, host configuration and npm cache directories.

Set `OPENMOTION_ONBOARDING_LANGUAGE` from the latest user request. Supported presentation languages are `zh`, `en`, `ja`, `ko`, `fr`, `es` and `pt`; locale tags use their lowercase primary language, and other languages fall back to `en`. The result reports the effective language. Codex setup prepares the welcome/cards document by default. Use `--onboarding-output` only as an optional path override when this host needs a specific readable artifact directory. On success, publish the prepared path/hash into this chat's explicitly permitted visualization directory using the installed inline-onboarding script. Open and verify the actual library, then emit the publisher's content reference once; never emit an application/data path directly. The installed production component owns the welcome and three complete video cards; no separate welcome, placeholder project, host restart or tool hot reload is needed. Its Recreate button uses the existing copyable brief when the inline context has no composer bridge. Use `directAccess` and its environment for subsequent domain operations.

## Source development: one installation command

For an explicitly selected source installation in Codex, collect platform/Node/host facts once, then run the source installer below. It downloads one shallow snapshot, installs locked dependencies, builds Studio once, registers the plugin, probes MCP and prepares the library. Do not separately run `npm start`, reinstall dependencies or inspect unrelated repositories/installed applications. Read this checkout's `AGENTS.md` before repository changes.

```sh
curl -fsSL https://raw.githubusercontent.com/nexu-io/openmotion/main/install.sh -o /tmp/openmotion-source-install.sh
bash /tmp/openmotion-source-install.sh
```

`OPENMOTION_INSTALL_DIR` selects a persistent empty destination. If the intended checkout already exists, verify its origin, version and local changes, then run its `bash scripts/install-motion.command` instead of cloning another copy. Never overwrite or update an unrelated checkout. The installer reuses a built Studio, checks source conflicts before dependency work, and can rebind a verified old `openmotion-local` source only when no plugin from it is installed. An active source is preserved and reported for an explicit upgrade decision.

An unregistered marketplace normally returns empty `installed` and `available` arrays and can be added. If listing fails, source preflight can read the selected host's effective configuration through the public `config/read` protocol in a short-lived stdio process. It recovers only a missing local `openmotion-local` root with no configured plugins in that marketplace, including disabled entries. This process never connects to or reloads the desktop host. Installed/cached entries remain protected. `OPENMOTION_INVENTORY_UNAVAILABLE` or `OPENMOTION_INVENTORY_INVALID` stops before configuration changes and gives the exact retry command; restore the old source or update the CLI when safe recovery cannot be established. Read failures and malformed output are never silently treated as an empty inventory.

Source download depends on network throughput and is measured separately; installation time is not guaranteed. The installer emits phase durations and saves local timings plus a concise onboarding result under `.artifacts/install/`; read that result once. Use bounded process waits instead of repeated status polls and guide/source reads. A prebuilt published application avoids source build/download work but is a separate, exact-version installation route; never silently substitute it for the requested main source.

## Other hosts: clone and start

Use Git, npm and Node.js 26.11.1, the version pinned for source validation. Choose a persistent parent directory for the checkout and run:

```sh
git -c filter.lfs.process= -c filter.lfs.smudge= -c filter.lfs.required=false clone --depth 1 --single-branch --branch main https://github.com/nexu-io/openmotion.git
cd openmotion
npm ci
npm run build:studio
npm start
```

`--depth 1` downloads only the latest snapshot and `--single-branch --branch main` selects main. Command-local LFS overrides keep optional reference videos and template archives as pointers, including on machines with stale global LFS configuration; no global Git setting changes. Download optional media only when needed. See [clone size and optional media](docs/repository-storage.md).

If the destination already exists, check its remote and local changes before reusing it, or choose another directory. Preserve existing work. Keep user projects and credentials outside the checkout, and preserve an existing `MOTION_DATA_DIR`. Studio and MCP must use the same data directory. Source preview and export use local Chrome/Chromium and FFmpeg/FFprobe; see [runtime setup](README.md#technical-guide) for requirements.

Use the actual `studioUrl` or `previewUrl` printed by startup. Keep this checkout in place after registration because the agent connection uses it.

## Connect the current agent

The Codex command above already registers this checkout and returns the connection handoff; do not run a second setup from the README. For another local stdio client, use [manual MCP configuration](README.md#manual-mcp). The [agent connection guide](docs/agent-adapters.md) describes other host integrations. Connect this checkout's `mcp.ts` and the same data directory as Studio; configure only the current host and preserve unrelated MCP servers, Skills and credentials.

Discover the OpenMotion tools and call `openmotion_get_project` to verify the workspace. Registration alone does not prove that this chat is connected; report any actual connection limitation honestly.

## First run

Open the startup URL and choose **Template library**, or call `openmotion_open_preview` with `{"target":"templates"}` when MCP is available.

Follow the [installation-success contract](docs/install.md#installation-success-reply): open the template library in the calling chat's right panel, then use the prepared inline presentation above, or the natively discovered recommendations with `onboarding: true` and the user's language. The component owns the persistent Agent welcome and three cards. **For Codex, `host_action_required` or `refresh_requested` means native onboarding is incomplete; use the supported inline route when available. Do not replace complete onboarding with a library-only success reply.** If neither presentation route is available, report that exact limitation and preserve this same chat/workspace for resumption. Reuse this installation rather than running setup again.

Library-only welcome copy is reserved for hosts without native presentation support, not an unfinished Codex handoff. The shared contract is authoritative; npm setup commands and release placeholders elsewhere in that document apply to published applications. A card button fills an unsent draft; wait for the user's submitted requirements before creating a project.
