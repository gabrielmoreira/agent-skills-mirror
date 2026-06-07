# Remove Codex provider

Idempotent — safe to run even if some steps were never applied. Reverses both the host (`src/providers/`) and container (`container/agent-runner/src/providers/`) trees, plus the Dockerfile CLI install.

## 1. Delete the barrel import lines (both trees)

Delete (do not comment out) the `import './codex.js';` line from each barrel:

- `src/providers/index.ts`
- `container/agent-runner/src/providers/index.ts`

This unregisters the provider from both `listProviderContainerConfigNames()` (host) and `listProviderNames()` (container).

## 2. Delete the copied files (both trees)

```bash
rm -f src/providers/codex.ts \
      src/providers/codex-registration.test.ts \
      container/agent-runner/src/providers/codex.ts \
      container/agent-runner/src/providers/codex-app-server.ts \
      container/agent-runner/src/providers/codex.factory.test.ts \
      container/agent-runner/src/providers/codex-registration.test.ts \
      container/agent-runner/src/providers/codex-dockerfile.test.ts
```

## 3. Revert the Dockerfile CLI install

In `container/Dockerfile`, remove both Codex edits (skip whichever is already gone):

**(a)** Delete the version ARG from the "Pin CLI versions" block:

```dockerfile
ARG CODEX_VERSION=0.124.0
```

**(b)** Delete the standalone Codex install layer:

```dockerfile
RUN --mount=type=cache,target=/root/.cache/pnpm \
    pnpm install -g "@openai/codex@${CODEX_VERSION}"
```

Leave the other per-CLI install layers (claude-code, agent-browser, vercel) untouched.

## 4. Dependency

Codex is a CLI binary installed via the Dockerfile — there is no agent-runner package dependency to uninstall. Step 3 removes the only install surface; no `bun remove` / `pnpm uninstall` is needed.

## 5. Unset Codex env vars

Remove any Codex-specific lines you added to `.env` (`OPENAI_API_KEY`, `OPENAI_BASE_URL`, `CODEX_MODEL`) if no other integration uses them, then re-sync to the container:

```bash
mkdir -p data/env && cp .env data/env/env
```

Switch any group still on Codex back to the default provider — set `"provider": "claude"` in `groups/<folder>/container.json` and clear `agent_provider` on the group/session in the DB.

## 6. Rebuild and restart

Run from your NanoClaw project root:

```bash
pnpm run build && ./container/build.sh
source setup/lib/install-slug.sh

# macOS
launchctl kickstart -k gui/$(id -u)/$(launchd_label)

# Linux
systemctl --user restart $(systemd_unit)
```

## Verification

After removal, the registration guards no longer apply (their files are gone). Confirm the provider is fully unwired:

```bash
grep -R "codex.js" src/providers/index.ts container/agent-runner/src/providers/index.ts   # no output
grep "@openai/codex" container/Dockerfile                                                  # no output
```

In a wired agent, requesting `agent_provider = 'codex'` should fall back to the default provider since `codex` is no longer in the registry.
