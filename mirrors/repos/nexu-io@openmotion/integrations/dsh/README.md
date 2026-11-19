# OpenMotion for DSH

An optional local plugin that brings the OpenMotion workspace into DeepSeek Harness (DSH). Browse projects, templates, Brand Kits and Assets, then edit in Studio alongside the native Agent conversation. DSH keeps its native sidebar, composer, resizable right-hand pane and open/close/fullscreen controls; the plugin only contributes its workspace, cards and embedded pages.

This source-checkout integration targets DSH **0.2.2-rc.1**. It is separate from the OpenMotion npm application and Agent-plugin ZIPs. Building a tarball does not publish it to npm.

## Prerequisites

- Node 26 (the OpenMotion CI runtime), npm and a working OpenMotion source checkout with this integration.
- Run `npm ci` and `npm run build:studio` at the OpenMotion repository root.
- A model configured in DSH. The plugin neither supplies model access nor copies credentials from another Agent. Media generation additionally needs an OpenMotion media provider.

## Install into the current DSH session

From the intended source checkout, run one command with the actual existing profile and workspace:

```sh
node integrations/dsh/install.ts --profile PROFILE --data-dir /absolute/workspace/data --language en
```

The installer checks the environment once, reuses matching locked dependencies and Studio fingerprints, builds the plugin directly, and enables its workspace plus the two native action-card components when absent. Existing inherited card components are reused without enabling unrelated recommendation features. Set `DSH_HOME` or pass `--dsh-home` for a custom profile home. `--url` takes the current local `DSH_WEB_URL`. It also attempts the official main Skill installation with `--agent universal`, scoped to this profile, and returns a compact presentation handoff. Existing onboarding selections are reused; `--resume` can preserve a receipt created by earlier installation commands.

The profile can activate while DSH remains running. **Do not kill or restart the host from its own conversation.** If the old browser has not loaded the new frontend, refresh that page once; server/MCP readiness does not imply that the client UI loaded. Then load `cardPresentation.skill` and call `propose_action` with the returned `cardPresentation.arguments`. The native card opens the template library to the right of Agent chat, with the shared welcome and exactly three recommendations on the left. It does not open or create a sample project. A file, status endpoint or tool list alone is not visible onboarding. Keep a missing refresh/card display pending, or use the shared text fallback with the same IDs when native display is unavailable.

The downloaded tarball route below remains useful for a pinned published release. Do not mix that route into an existing source installation or search multiple channels to finish a local build.

## Try from source

From the OpenMotion checkout:

```sh
npm ci --prefix integrations/dsh
npm start --prefix integrations/dsh
```

Open the authenticated URL printed by DSH. Its isolated profile, configuration and project data default to `~/.openmotion-dsh/`; existing DSH profiles remain separate. Choose a workspace folder in DSH before using **Create with agent**. The action prepares an unsent draft and preserves an existing draft. Pick a project to open Studio, or use **Studio** in a conversation.

The host plugin uses OpenMotion's maintained `preview.ts` entrypoint to discover or start the local service on each platform, then connects DSH's maintained stdio MCP adapter to the same data directory. Discovery reuses a compatible, healthy service for that directory and leaves unrelated occupied ports alone. When the host exposes DSH action cards, the plugin also lets the Agent show the shared localized welcome and exactly three installation recommendations, or ordinary template recommendations, as playable conversation cards with Preview and Recreate template actions; the latter records a selection and still requires Agent confirmation before project creation. Load `openmotion-template-recommendations` before proposing the card. Installation uses the exact three IDs/order from `node scripts/install-onboarding.mjs --host deepseek` in the matching checkout and data directory; use the request language and do not resample. Hosts without action cards can use another supported card surface; only when none is supported or display fails should the Agent show the same three names, summaries and preview links as text. Preview opens a local enlarged video dialog with playback controls and Escape/close support; it never sends a prompt or invokes the Agent. The workspace gallery alone is not the installation recommendations. Use **Refresh** on the workspace after an Agent creates a project, then select it. New projects do not automatically replace the selected Studio tab. DSH and Studio retain their own theme preferences.

Press Ctrl+C to stop this DSH instance and disconnect its MCP child. The shared OpenMotion editor can remain running and projects are retained. If the launcher crashed, confirm its DSH process has stopped before removing `launch.lock` from the configured integration home.

Optional environment variables:

| Variable | Meaning |
| --- | --- |
| `OPENMOTION_DSH_HOME` | Isolated integration state/profile home. |
| `OPENMOTION_DSH_PORT` | DSH loopback port; defaults to `3080`, refuses an occupied port. |
| `MOTION_DATA_DIR` | Existing OpenMotion data directory to share; otherwise uses the integration home's `data/`. |
| `MOTION_TEMPLATE_SOURCE` | Optional OpenMotion template source override, e.g. `hosted`. Unset uses OpenMotion's normal source-checkout behavior. |

## Download and install the plugin

Users do not need to build the plugin themselves. The default public entry follows the verified stable OpenMotion release:

<https://releases.open-design.ai/open-motion/integrations/dsh/stable/latest.json>

| Channel | Download manifest | Updated by |
| --- | --- | --- |
| Stable (default) | `integrations/dsh/stable/latest.json` under the public releases origin | Successful stable publication, after both native application checks. |
| Test | `integrations/dsh/test/latest.json` under the public releases origin | Successful test publication. |
| Main development | `integrations/dsh/main/latest.json` under the public releases origin | The independent DSH integration workflow on main. |

For stable/test, the plugin version matches the OpenMotion release version; main retains the development package version. This small JSON records the plugin version, supported DSH version, exact OpenMotion `sourceCommit`, immutable `tarballUrl`, byte length and SHA-256. Download the `.tgz` at `tarballUrl`; no GitHub login is required. For a new installation, use a separate OpenMotion checkout at `sourceCommit`, install its root dependencies and build Studio as described in Prerequisites. Preserve an existing checkout and use the local build below when you want to keep its version. The tarball still requires that built source runtime; it does not contain the full OpenMotion application.

From a prepared checkout, this helper downloads and verifies the published package before writing it to a new file:

```sh
node integrations/dsh/download.ts /absolute/path/to/downloads
# Explicit test or development installation:
node integrations/dsh/download.ts /absolute/path/to/downloads --channel=test
node integrations/dsh/download.ts /absolute/path/to/downloads --channel=main
```

Use the returned `filename` with the DSH installation command below. It also returns `sourceCommit` and `dshVersion` so the Agent can check the runtime and host before enabling. A checksum, network or version mismatch must be reported rather than silently switching an existing installation. Existing downloads are not overwritten.

**Availability:** the stable/test entries appear after their first coordinated release containing DSH. Before that, explicitly choose the main development channel, build locally, or download the `openmotion-dsh` artifact from a successful [DSH integration run](https://github.com/nexu-io/openmotion/actions/workflows/dsh-integration.yml). GitHub artifact downloads require sign-in and expire. The helper reports unavailable channels without silently substituting another version.

### Build locally instead

After the prerequisites, install the optional build dependencies and pack:

```sh
npm ci --prefix integrations/dsh
npm run pack --prefix integrations/dsh
```

This produces `integrations/dsh/dist/openmotion-dsh-0.1.0.tgz`. It can also be copied to another machine with the matching source runtime.

### Install and enable in DSH

With DSH installed, install the downloaded or locally built tarball in the desired profile:

```sh
dsh plugin --profile web add /absolute/path/to/the-downloaded-plugin.tgz
```

Add this entry to that profile's `cordis.patch.yml`, preserving existing entries:

```yaml
- insert:
    - id: action-cards
      name: '@deepseek-ai/dsh-action-cards'
    - id: client-ui-action-cards
      name: '@deepseek-ai/dsh-client-ui-action-cards'
    - id: openmotion-workspace
      name: openmotion-dsh
      config:
        root: /absolute/path/to/openmotion
        dataDirectory: /absolute/path/to/your/openmotion-data
```

If the profile already inherits either native action-card component, omit that component from the insert list rather than registering another provider. Replace both paths with your local locations. `root` must be a built source checkout containing this integration; the plugin does not download OpenMotion. `dataDirectory` chooses the shared project/asset store. Optional `node` selects the Node executable for OpenMotion; by default it uses DSH's Node. Optional `templateSource` selects `repository` or `hosted`.

Allow the watched profile to activate, then refresh the browser once if its OpenMotion frontend is missing. Enabling this one plugin mounts its workspace UI, starts/reuses OpenMotion, and connects the MCP tools. Remove an existing `mcp-openmotion` entry before enabling it: two adapters cannot reserve the same `openmotion` tool namespace. Model configuration remains in DSH's normal settings/profile. Do not commit generated patches, model credentials, authenticated URLs or user data.

### Distribution maintenance

**Motion candidate build** checks the optional integration at the frozen application source, packs a plugin with the same application version, scans it and seals its archive, download metadata and scan into the candidate. The candidate artifact includes `openmotion-dsh-<version>.tgz` and `dsh-plugin.json` for isolated DSH testing. Set the plugin root to a built source checkout at that manifest's `sourceCommit`; the npm application package is a separate installation surface.

**Motion npm publication** reuses those exact plugin bytes after application publication and archival. It verifies the immutable public tarball before advancing only `stable/latest.json` or `test/latest.json`. A newer main commit does not invalidate an already frozen release. Superseded releases and snapshot-only recovery may restore immutable downloads but never move plugin channels. Retained older candidates without DSH remain publishable and do not rebuild a plugin from newer source. No plugin npm publication is performed.

The path-scoped **DSH integration** workflow continues to check, pack and retain a development plugin for PR testing. Trusted main pushes/manual main runs publish only `main/latest.json`; they cannot change the stable or test entries. Both paths use the existing release-bucket settings, with R2 credentials supplied only to the final publishing steps.

## Verify and recover

```sh
npm run typecheck --prefix integrations/dsh
npm run test --prefix integrations/dsh
node --experimental-strip-types --test tests/dsh-integration.test.ts
```

In DSH, confirm the OpenMotion sidebar entry, project/template browsing, Studio + Agent layout, focus toggle and narrow-window switching. Read-only host diagnostics are available at `/openmotion-dsh/status`; confirm the discovered names include `mcp__openmotion__openmotion_get_project` and `mcp__openmotion__openmotion_list_templates`.

After configuring a model, ask: “Read my current OpenMotion project and list three templates. Do not modify, create or export anything.” Actual tool calls confirm a model connection; they do not establish video creation or export acceptance.

If activation fails, inspect DSH's log for the failing source path, Node executable or MCP startup. Each dashboard list loads independently, reserves placeholder cards while loading and offers its own **Retry** on failure. A failed template request does not hide projects, and a failed project request does not hide templates. Cards omit unknown duration badges. The host only proxies the two read-only listing APIs; editing remains in Studio and existing MCP tools. Standalone Studio retains its navigation. The integration uses DSH's native extension slots and tab controls; retest before upgrading DSH. Desktop DSH and other DSH versions have not been validated.

## Acknowledgements

Uses DSH's native plugin, slot and MCP-client interfaces. DSH and its dependencies retain their respective licenses. OpenMotion UI tokens, controls, icons and artwork come from the repository's maintained design system.

Bundled Remix Icon artwork retains its upstream terms in `remix-icon-LICENSE.txt` and `remix-icon-NOTICE.txt`, included in the installable plugin alongside OpenMotion's `LICENSE`. In the source checkout, those originals are maintained in `packages/design-system/`.
