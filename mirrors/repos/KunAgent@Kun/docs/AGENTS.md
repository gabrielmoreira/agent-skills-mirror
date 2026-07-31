# Agent Runtime Notes

The Kun desktop app has one live agent runtime: the bundled **Kun** runtime.
The same runtime also serves the standalone Kun TUI and non-interactive
clients. GUI and TUI are independent clients that may be active at the same
time; neither client owns the runtime lifecycle or the canonical model
configuration.

Do not add a second live provider, provider switcher, runtime diagnostics panel,
or legacy CodeWhale/Reasonix process path. Code, Design, Write, and Connect
phone all enter the same Kun HTTP/SSE boundary. Connect phone still uses the
internal `claw` name in code for compatibility.

## Client Surface Boundary

- Every turn records its initiating surface (`gui`, `tui`, `cli`, `api`, `im`,
  or `extension`). Continuations and delegated child turns inherit it.
- Provider kind `gui` is reserved for capabilities that require the desktop
  workbench, such as Design canvas mutation or Computer Use. Those providers
  must not be advertised or executable on TUI/CLI/API/IM turns.
- Runtime-backed goals, todos, plans, Skills, MCP, attachments, approvals,
  structured input, and subagents are shared Kun capabilities, not GUI tools.
- Keep the immutable Kun system prompt client-neutral. Put interface-specific
  guidance in the dynamic per-turn context after the stable prefix.
- Never switch a process-global tool registry or prompt based on whichever
  client connected most recently; GUI and TUI can run concurrently.

## Allowed Extension Path

1. Add protocol fields in `kun/src/contracts/`.
2. Add agent behavior in `kun/src/loop/`, `kun/src/services/`, or a
   new port/adapter under `kun/src/ports/` and `kun/src/adapters/`.
3. Add HTTP endpoints under `kun/src/server/routes/`.
4. Map the endpoint/event in `src/renderer/src/agent/kun-runtime.ts` and
   `src/renderer/src/agent/kun-mapper.ts`.
5. Add settings only under `agents.kun`.

## Forbidden Paths

- No `AgentSwitcher`.
- No `ConnectionStatusBar`.
- No `RuntimeDiagnosticsDialog` or runtime self-check UI.
- No CodeWhale/Reasonix adapter, process manager, RPC bridge, updater, or
  importer.
- No legacy drawing/painting starter card outside the current Design mode.
- No `/usage` or `/runtime` slash command that opens a runtime control panel.
  The standalone TUI may expose `/usage` as a read-only report backed by
  `GET /v1/usage`; it must not add runtime diagnostics or control actions.

## Legacy Data Rule

Old persisted keys may be read only inside settings migration:

- `agentProvider: codewhale | reasonix | deepseek-runtime` maps to `kun`.
- `agents.codewhale`, `agents.reasonix`, and legacy `deepseek` values seed
  `agents.kun` once.
- Saved settings must contain only `agents.kun`.
- Old Connect phone (internal Claw) `agentThreadIds.codewhale/reasonix` fold into
  `agentThreadIds.kun`.

## Verification

Run:

```bash
npm run typecheck
npm test
npm run build
```

Manual smoke:

- Code can create a Kun thread, stream a reply, approve/deny tools, and
  interrupt a turn.
- CodeWhale parity endpoints still work through Kun: thread search/archive
  filters, fork, session resume, request_user_input submit/cancel, and usage.
- Cache telemetry uses DeepSeek native `prompt_cache_hit_tokens` /
  `prompt_cache_miss_tokens`; hot Kun turns should stay above 90% cache
  hit after the stable prefix is warm.
- Immutable prefix drift and malformed tool-call/tool-result history must be
  caught before a request reaches DeepSeek.
- Design can open the canvas, create or iterate an artifact, preview/export it,
  and hand the approved design to a fresh Code thread.
- Write can open the workspace, request inline completion, and use selected-text
  assistant actions.
- Connect phone can save settings and run a manual task through a Kun thread.
- Settings -> Agents shows only Kun.

The full plan is in
[`docs/kun-architecture.md`](./kun-architecture.md).
