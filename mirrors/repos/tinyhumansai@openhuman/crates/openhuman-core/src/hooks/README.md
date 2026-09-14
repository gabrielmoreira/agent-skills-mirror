# Hooks

Configurable, file-based hooks: user-authored scripts (or model-evaluated
prompts) that observe or gate the agent at specific moments, discovered from
`hooks.json` files rather than compiled against the core. The contract is
Cursor's `hooks.json` (<https://cursor.com/docs/hooks>) — same event names,
stdin envelope, stdout decision object, and exit-code semantics — so a script
written for either host runs on the other unchanged.

This is a different "hook" from two other things in the codebase: the
in-process Rust traits an *embedding host* installs by compiling against the
core (`ToolHook` and `PostTurnHook` in `agent/hooks.rs`, `agent/stop_hooks.rs`),
and inbound webhook ingestion (`skills/webhooks/`, RPC namespace `webhooks`).
This module bridges onto the first via `bridge.rs`; it is unrelated to the
second.

## Submodule map

| Module | Owns |
| --- | --- |
| `types.rs` | Wire contract: events, the stdin envelope, the decision object (`HookOutput`, `HookPermission`) |
| `config.rs` | `hooks.json` parsing and the four-layer merge |
| `matcher.rs` | Which occurrences of an event reach a given hook |
| `exec.rs` | Running one hook: stdin, timeout, exit codes, fail-open/closed |
| `engine.rs` | Selection, ordering, aggregation, session state |
| `context.rs` | Assembling the envelope from ambient host facts |
| `bridge.rs` | Mounting the engine on the harness's existing tool/turn seams |
| `ops.rs` | `init` plus the lifecycle moments that have no tool seam (`prompt_submitted`, `subagent_starting`, and the not-yet-called session/compact/thought/subagent-stop entry points) |
| `prompt_eval.rs` | Model evaluation for `prompt`-kind hooks |
| `followup.rs` | Queueing what a `stop` hook asks for next |
| `schemas.rs` | RPC namespace `hooks`: `list`, `reload`, `test` |

## Two rules worth knowing before changing anything here

**The strictest verdict wins.** Layers concatenate rather than override, and
`types::HookOutput::merge` folds denial over ask over allow. Adding a hook can
therefore never loosen a policy another one set — an operator-managed
system-wide deny hook cannot be overridden by a repository shipping its own
`hooks.json`.

**Gating costs a turn's latency; observing does not.** `types::HookEvent::is_gating`
is the single place that split is encoded, and `engine.rs` reads it to decide
between running hooks sequentially in the turn's path and spawning them onto a
background task. Do not weaken this: an audit hook that hangs must not hang
the agent, and a gating hook must not be demoted to fire-and-forget.

`exec.rs` reads a command hook's exit code: `0` parses stdout as a
`HookOutput` (the last complete JSON object on stdout, so progress lines are
fine), `2` denies regardless of stdout with stderr as the reason, and anything
else — including a timeout, a missing interpreter, or unparseable stdout — is a
failure that fails open unless the definition sets `fail_closed`, in which case
it denies. Do not change this default without reading the configuration and
security section of `AGENTS.md`. A hook that answers `allow` only lets the call
continue to the autonomy policy and approval gate underneath it; both still
apply. A hook that answers `ask` reaches the harness as
`ToolHookDecision::Ask`, and `agent/tinyagents/middleware/embedder_hooks.rs` has no
approval channel, so today it denies rather than quietly allowing.

Not every event in `types::HookEvent::ALL` fires yet. `HookEvent::is_wired`
lists the ones without a call site (`sessionStart`, `sessionEnd`,
`preCompact`, `afterAgentThought`, `subagentStop`); the loader warns when a
`hooks.json` registers one. Move an event out of that list only when its call
site lands.

## Layering (`config.rs`)

Four `hooks.json` layers are read by `layer_paths` and concatenated, lowest
trust last:

| `HookLayer` | Path |
| --- | --- |
| `System` | `/etc/openhuman/hooks.json` (Linux), `/Library/Application Support/OpenHuman/hooks.json` (macOS), `%ProgramData%\OpenHuman\hooks.json` (Windows) |
| `User` | `~/.openhuman/hooks.json` |
| `Workspace` | `<workspace_dir>/hooks.json` |
| `Project` | `<action_dir>/.openhuman/hooks.json` |

This is the opposite of how `config.toml` merges (override, not concatenate)
— deliberately, since concatenation combined with `HookOutput::merge`'s
strictest-wins rule is the only composition that can't be used to loosen
policy. `HookDefinition::layer` and `source_dir` are `skip_deserializing` and
stamped from the file's own location, so a `hooks.json` cannot claim a more
trusted layer. Only `version: 1` is accepted; a missing file is silent, an
unreadable or malformed one becomes a `HookConfig::warnings` entry surfaced by
`hooks.list`.

## `prompt`-kind hooks

Most hooks are `command`: spawn a program, hand it the event JSON on stdin,
read a decision from stdout. A `prompt` hook is a policy written in English
instead — `prompt_eval.rs` asks the configured model to judge a condition,
via a one-shot `inference::ops::inference_prompt` call capped at 200 output
tokens. A hook definition may override the model; the override is applied to
the `Config` copy returned by `load_config_with_timeout` for that one call
(`default_model`), so nothing persists and a concurrent turn on the real
config is unaffected. Reserve `prompt` hooks for rare, high-stakes moments —
they cost a model call per event.

## Bridge (`bridge.rs`)

The harness already carries in-process hook seams (`ToolHook`, `PostTurnHook`
in `agent/hooks.rs`). Rather than adding a second set of call sites, the
engine registers itself through those seams once at bootstrap
(`ConfiguredHookBridge::install`/`uninstall`, registered under
`BRIDGE_HOOK_NAME` so a rebuilt core replaces rather than duplicates it).
Cursor's `beforeShellExecution`, `beforeReadFile`, and `afterFileEdit` are not
separate call sites here — `derived_event` maps tool names onto them
(`SHELL_TOOLS`: `shell`/`run_command`/`bash`/...; `READ_TOOLS`:
`file_read`/`read_diff`; `WRITE_TOOLS`: `file_write`/`edit`/...; MCP tools
get `beforeMCPExecution`/`afterMCPExecution`). On the pre side the bridge fires
`preToolUse` and then the derived `before*` event with a Cursor-shaped
payload, merging both verdicts; on the post side it fires `postToolUse` (or
`postToolUseFailure`) and then `afterShellExecution`/`afterFileEdit`. A write
therefore has no derived pre-event — denying it belongs to `preToolUse`. The
`PostTurnHook` impl fires `afterAgentResponse` and `stop`.

## Wiring

- `crate::hooks::init(&cfg)` is called from `core/jsonrpc.rs` during core
  boot: it sets host context, reads config, and installs or uninstalls the
  bridge. Disabled (`config::schema::hooks::HooksConfig::enabled = false`)
  or empty config uninstalls the bridge entirely so an unconfigured host pays
  no per-tool-call cost.
- `[hooks]` in `config/schema/hooks.rs` carries only host-level switches
  (`enabled`, `default_timeout_secs`) — the hooks themselves live in
  `hooks.json`, not in `config.toml`.
- RPC namespace `hooks` (`schemas.rs`) is registered via
  `all_hooks_registered_controllers` in `core/all.rs`.
- `web_chat/ops/start_chat.rs` calls `hooks::ops::prompt_submitted` before a
  submitted prompt reaches the agent.
- `agent/harness/subagent_runner/ops/runner.rs` calls
  `hooks::ops::subagent_starting` before spawning a sub-agent.

## Tests

`bridge_tests.rs`, `exec_tests.rs`, `followup_tests.rs`, and
`matcher_tests.rs` are attached with `#[path]` from their own module files;
`hooks_tests.rs` (config loading, engine, verdict merge) is attached from
`mod.rs`.

## Related docs

- [gitbooks/developing/hooks.md](../../../../gitbooks/developing/hooks.md) — user-facing `hooks.json` guide
- [gitbooks/developing/architecture/security.md](../../../../gitbooks/developing/architecture/security.md) — approval gate and autonomy policy that still applies after a hook allows
