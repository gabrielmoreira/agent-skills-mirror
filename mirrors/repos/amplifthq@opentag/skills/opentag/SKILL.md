---
name: opentag
description: Set up, run, and troubleshoot OpenTag with the published CLI across Slack, GitHub, GitLab, Linear, Lark / Feishu, Codex, Claude Code, OpenClaw, local config, platform credentials, and callback delivery.
---

# OpenTag

OpenTag connects collaboration platforms to a local coding agent. Use this skill when a user wants help with `opentag setup`, `opentag start`, Slack, GitHub, GitLab, Linear, Lark / Feishu, Codex, Claude Code, OpenClaw, local OpenTag config, or end-to-end setup verification.

## Default Path

Use the published CLI first. Do not start from repo-internal apps, old shell scripts, or private package binaries unless the user is explicitly doing core development.

Recommended user path:

```bash
npm install -g @opentag/cli
opentag setup
opentag start
```

No global install:

```bash
npx @opentag/cli setup
npx @opentag/cli start
```

## Route The Request

Read only the reference needed for the user's path:

- First setup or Echo test loop: `references/local-echo.md`
- Slack setup: `references/slack-setup.md`
- GitHub setup: `references/github-setup.md`
- ACP coding-agent execution: `references/codex-runner.md`
- Broken setup, missing callbacks, rejected runs, or auth errors: `references/troubleshooting.md`

For platform credential steps, use the repository docs as the source of truth:

- Slack: `docs/platforms/slack.en.md`
- GitHub: `docs/platforms/github.en.md`
- GitLab: `docs/platforms/gitlab.en.md`
- Linear: `docs/platforms/linear.en.md`
- Lark / Feishu: `docs/platforms/lark.en.md`

## Working Rules

- Keep setup user-led. Never invent tokens, app IDs, Slack team/channel IDs, GitHub owner/repo names, or local project paths.
- Prefer Slack, then GitHub, then GitLab, then Linear, then Lark / Feishu when listing platforms.
- Ask the user which platform and coding agent they want if it is not already clear outside Codex.
- In Codex Plan mode, use `request_user_input` / askhuman to collect non-secret setup choices before running `opentag setup`, then pass those choices as CLI flags so the terminal wizard does not silently choose defaults.
- Codex Default mode cannot render askhuman choice cards. If setup choices are needed and the current host does not expose a runtime transition into Plan mode, stop and explain that askhuman cannot render from Default mode in this run. Do not claim a Plan-mode handoff happened, do not ask the user to switch modes, do not ask the same choices in plain text, do not continue with CLI defaults, and do not run `opentag setup` until the choices are explicitly collected.
- Never request secrets through askhuman. Tokens, app secrets, signing secrets, app IDs, channel IDs, repository names, and any non-recommended project path still need explicit user confirmation before they are entered into the CLI or config.
- Prefer Codex or Claude Code when the corresponding local login is ready, Hermes when its ACP profile and provider are ready, OpenClaw when its Gateway is ready, and Echo only for dev/test verification.
- Do not ask setup users to invoke an agent directly. OpenTag provides built-in Generic ACP launches for Codex, Claude Code, Cursor, OpenCode, Hermes, and OpenClaw; diagnose them with `opentag doctor` and the built-in ACP conformance gate.
- OpenClaw currently reports `cancel=no`. A cancellation request stops OpenTag's local bridge, but Gateway-owned tool subprocess termination is not guaranteed; inspect provider-owned processes before starting conflicting follow-up work.
- Treat `opentag start` as a foreground process. Tell the user to keep it running and stop it with Ctrl-C.
- Do not expose secrets in responses. Use `opentag config show` for redacted config.
- When credentials are needed, point the user to the matching platform guide and walk them through the official setup.

## Npm Registry And Network Failures

If `npm install -g @opentag/cli` or `npx @opentag/cli ...` fails before the OpenTag CLI starts, keep the exact npm error and diagnose the package delivery path before giving up. Treat errors such as `ENOTFOUND`, `EAI_AGAIN`, `ETIMEDOUT`, `ECONNRESET`, `fetch failed`, proxy connection failures, and TLS certificate errors as network or npm-environment issues, not as OpenTag setup failures.

Use safe, non-secret checks first:

```bash
node --version
npm config get registry
npm config get proxy
npm config get https-proxy
env | grep -i proxy
node -e "require('dns').lookup('registry.npmjs.org', (e, a, f) => console.log(e ? e.code + ' ' + e.message : a + ' ' + f))"
curl -I --max-time 15 https://registry.npmjs.org/@opentag%2fcli
npm view @opentag/cli version --fetch-timeout=15000
```

If DNS or registry access is flaky, say that the published CLI could not be reached yet and retry once after checking connectivity. If the user has a VPN or proxy, compare direct npm metadata access with a one-command proxy-scoped npm registry retry, but do not permanently change `npm config` without explicit user confirmation:

```bash
HTTPS_PROXY="<proxy-url>" HTTP_PROXY="<proxy-url>" npm view @opentag/cli version --fetch-timeout=15000
```

Only after npm registry metadata is reachable, retry the CLI help command:

```bash
npx --yes @opentag/cli --help
```

Only use a proxy URL the user provides or that is already active in the environment. Do not invent proxy hosts, tokens, certificates, or registry credentials. If npm cache metadata exists but `npx --offline` or `npm pack --offline` still fails, do not claim the CLI is available offline; report that the cache is not executable and wait for registry access to recover.

## Codex Plan Mode Askhuman Setup Choices

When helping a Codex user install or configure OpenTag, collect these non-secret choices with `request_user_input` / askhuman only when the current Codex host is actually in Plan mode and the tool is available:

- Platform: Slack, GitHub, GitLab, Linear, Lark / Feishu, Telegram, or Discord.
- Coding agent: Codex, Claude Code, Cursor, OpenCode, Hermes, OpenClaw, or Echo, using local detection from `opentag executors` when available.
- Local project: the current working directory as the recommended option, plus a free-form path option inside askhuman for another path.
- Platform mode choices that are not credentials, such as Slack Socket Mode vs Events API, Lark / Feishu tenant for manual app setup, Lark scan vs manual setup, and default project binding vs bind later.

If the run is still in Codex Default mode, first look for an actual runtime-provided Plan-mode transition. If none exists, stop and report that the current Codex host cannot render askhuman from Default mode. Do not claim a Plan-mode handoff is complete, do not ask the user to switch modes, do not present a plain-text fallback for the same choices, do not run `opentag setup`, and do not continue with guessed defaults.

After the user chooses, run `opentag setup` with matching flags, for example `--platform`, `--executor`, `--project`, `--slack-mode`, `--tenant`, `--lark-setup`, and `--binding`. Stop before entering any credential, token, app ID, app secret, signing secret, channel ID, repository name, or unconfirmed project path.

## Setup Workflow

1. Check prerequisites.
   Completion: Node.js 22+ is available and the user has a local project path.

2. Install or run the CLI.
   If npm cannot reach the published package, follow "Npm Registry And Network Failures" before treating setup as blocked.
   Completion: `opentag --help` or `npx @opentag/cli --help` works.

3. Run setup.
   Completion: `opentag setup` has collected platform, executor, project path, and credentials.

4. Start OpenTag.
   Completion: `opentag start` reports the dispatcher and selected platform listener.

5. Verify the setup.
   Completion: `opentag status` or `opentag doctor` explains the current state, and one platform mention creates a visible response or a specific actionable error.

6. Report next steps.
   Completion: tell the user what was configured, what still needs platform-side setup, and how to stop or uninstall.

## Local Paths

Default config:

```text
~/.config/opentag/config.json
```

Default state and isolated worktrees:

```text
~/.local/state/opentag
```

## Useful Commands

```bash
opentag setup
opentag start
opentag status
opentag doctor
opentag platforms
opentag executors
opentag config path
opentag config show
```

For local development inside the OpenTag repository:

```bash
corepack pnpm opentag-dev
opentag-dev setup
```
