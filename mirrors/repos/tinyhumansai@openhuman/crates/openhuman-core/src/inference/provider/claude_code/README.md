# claude_code

`ChatModel<()>` implementation that drives Anthropic's `claude` CLI as a
subprocess instead of calling the Messages API directly. Selected by the
`claude-code:<model>` provider string (`PROVIDER_PREFIX`) — see
[Selection](#selection).

`mod.rs`'s module doc still describes the original Phase 2 cut ("native CC
built-ins disabled at the caller; v2 will expose OpenHuman's tools back over
MCP"). `driver.rs` has since moved past that: the loopback MCP bridge is in
place, and CC's built-in tools do run — under a user-chosen permission
posture (below).

## CLI invocation

`ClaudeCodeProvider::run_chat` acquires one of `MAX_CONCURRENT_TURNS` (4)
`Semaphore` permits, then `driver::run_turn` spawns
`claude -p --input-format stream-json --output-format stream-json --verbose
--include-partial-messages --add-dir <action_dir> --permission-mode
<acceptEdits|bypassPermissions> --session-id <uuid>|--resume <uuid> --model
<model>`, plus `--append-system-prompt` (written to a per-turn scratch file),
`--mcp-config <scratch>/openhuman-mcp-config.json --strict-mcp-config` when the
loopback MCP server started, and `--disallowedTools Bash,BashOutput,KillShell,
WebFetch,WebSearch,Task` (`DISALLOWED_CC_BUILTINS`) unless full access is on.
`--session-id` is used on a new CC session and `--resume` afterwards; the UUID
comes from `session_store.rs`, keyed by a SHA-256 hash of the conversation's
first user message (`thread_key_from_messages`) because the real OpenHuman
thread id is not yet plumbed through `ChatRequest`. `cwd` is
`config.action_dir` (the project root the CLI's file tools operate in).

## File map

| File | Role |
| --- | --- |
| `mod.rs` | `ClaudeCodeProvider` (`ChatModel<()>` impl), `PROVIDER_PREFIX`, `MAX_CONCURRENT_TURNS`, `workspace_dir_from_config` (= parent of `config.config_path`, i.e. `~/.openhuman` — deliberately *not* `Config::workspace_dir` or `action_dir`), `from_env` (CLI discovery + version gate + key resolution), `run_chat`, `thread_key_from_messages`. |
| `auth.rs` | `resolve()` → `(AuthSource, Option<key>)`: which credential the spawned CLI will use. |
| `auth_status.rs` | `probe()` — the CLI's own auth state (API key env / subscription login / signed out / unknown) for the settings UI, via `claude auth status --json`. |
| `driver.rs` | `run_turn`: per-turn scratch dir, permission posture, macOS Seatbelt jail, MCP config, argv, stdin/stdout piping, `DEFAULT_TURN_TIMEOUT_SECS` (900, override `OPENHUMAN_CLAUDE_CODE_TURN_TIMEOUT_SECS`), stderr diagnostics cap. |
| `event_mapper.rs` | `ClaudeCodeEvent` → `ProviderDelta` / aggregated `ChatResponse`. `tool_use` blocks are tracked only to keep their `input_json_delta`s out of the visible text and are **not** surfaced as `ToolCall`s: the CLI is self-executing, so a tool block in the stream has already run; surfacing it would make the tinyagents harness try to dispatch `Read`/`Bash`/… and loop on "unknown tool". |
| `input_builder.rs` | `build_stdin`: JSONL user turns for `--input-format stream-json` — full history on a new session, only the last user turn on `--resume`; inline images re-hydrated from `agent::multimodal` markers (5 MiB cap). |
| `session_store.rs` | `SessionStore`: thread key → CC session UUID v4, persisted in `<workspace>/claude-code-sessions.json`. |
| `settings.rs` | `ClaudeCodeSettings { full_access }` persisted in `<workspace>/claude_code_settings.json` next to `config.toml`; written by the `inference.claude_code_set_full_access` RPC. |
| `stream_parser.rs` | Line-buffered JSONL parser for `--output-format stream-json`; permissive `serde_json::Value` payloads so a minor CLI schema bump does not break parsing. |
| `types.rs` | `MIN_CLI_VERSION` (`2.0.0`), `CliStatus`, `BRAND_LABEL`. |
| `version_check.rs` | `resolve_binary` (`OPENHUMAN_CLAUDE_CLI` env → `PATH` → well-known install dirs, because GUI launches inherit a stripped launchd `PATH`) and `probe()` against `MIN_CLI_VERSION`. |

## Auth resolution order

1. Process env `ANTHROPIC_API_KEY` (highest precedence) — `auth.rs::resolve`
   returns `AuthSource::EnvApiKey` and the key is set on the child at spawn.
2. Otherwise `AuthSource::CliCredentials`: the env var is *not* set and the
   CLI uses its own login (`~/.claude/.credentials.json`, or the Keychain on
   macOS).
3. `auth_status.rs` reports the richer state for the UI by spawning
   `claude auth status --json` (bounded by `AUTH_STATUS_TIMEOUT` = 10 s)
   rather than reading the credentials file, because on macOS the CLI stores
   credentials in the Keychain (service `Claude Code-credentials`) — a
   logged-in macOS user would otherwise be misreported as signed out. Older
   CLIs without `auth status` map to `AuthSource::Unknown`, never to
   "signed out".
4. Picking up an Anthropic key from OpenHuman's auth-profile store and
   Claude Pro/Max OAuth are both future work (v1.1 / v2 per `auth.rs`).

Tests that touch `ANTHROPIC_API_KEY` / `OPENHUMAN_CLAUDE_CODE_*` serialize
through `mod.rs::ENV_TEST_LOCK`.

## Permission posture, sandbox, and loopback MCP

The user opts into Claude Code explicitly, so its toolset is not restricted
beyond a permission posture that is the user's choice
(`driver.rs::claude_code_full_access`):

- default: `--permission-mode acceptEdits` plus `--disallowedTools` for
  shell, network, and `Task` fan-out — file reads/edits in `action_dir` only;
- full access (`settings.rs` toggle, or `OPENHUMAN_CLAUDE_CODE_PERMISSION_MODE=
  bypass|bypassPermissions|full`): `--permission-mode bypassPermissions` and
  the entire CC toolset including Bash.

On macOS the spawn is additionally wrapped in a Seatbelt jail
(`sandbox-exec -p <profile>`, on by default when `/usr/bin/sandbox-exec`
exists; opt out with `OPENHUMAN_CLAUDE_CODE_SANDBOX=0`). The profile allows
everything the user can do *except* reads and writes under the entire
`~/.openhuman[-staging]` tree — the whole root, not just the per-user
workspace subdir, because `workspace_dir` is a subdirectory of it and a
narrower deny would leave siblings readable. This is the OS-level counterpart
of `is_workspace_internal_path`. Linux and Windows have no OS wall yet; CC
runs unconfined there.

That deny would also cut the coding agent off from OpenHuman's memory and
tools, so `driver.rs` calls `crate::mcp::server::ensure_local_http()` and
writes a per-turn `--mcp-config` pointing at the in-process HTTP MCP server
(`crate::mcp::server::local`). The MCP server runs in the **unjailed core
process**, not as a child of the sandboxed `claude`, and is reached over
loopback with a per-process bearer token carried in the config's
`Authorization` header, so it keeps full access to `~/.openhuman` while CC's
raw tools stay denied that path. If `ensure_local_http` fails (for example a
build without the `http-server` feature), CC runs without OpenHuman MCP tools
and the turn still proceeds.

## Selection

`../factory/chat_model.rs` (`create_chat_model*`) calls
`try_create_claude_code_chat_model`, defined in `../factory/subprocess_providers.rs`: it
strips `PROVIDER_PREFIX` from the resolved provider string, rejects an empty
model id, runs `enforce_local_only_inference` and `verify_session_active`,
emits the inference egress descriptor, and builds
`ClaudeCodeProvider::from_env(model, workspace_dir_from_config(config),
config.action_dir)`. An `@<temp>` suffix is accepted but ignored (logged).
`from_env` fails fast with an actionable error when the CLI is missing,
outdated (`MIN_CLI_VERSION`), or unusable. `../factory/routing.rs` and
`../factory/access_gates.rs` also special-case the prefix in
`route_has_usable_credentials` (a CC route carries its own credentials) and
`external_provider_label` ("Claude Code CLI" in Privacy-Mode messages).

## Tests

Per-file `*_tests.rs` alongside each module (`auth_tests.rs`,
`auth_status_tests.rs`, `driver_tests.rs`, `event_mapper_tests.rs`,
`input_builder_tests.rs`, `session_store_tests.rs`, `settings_tests.rs`,
`stream_parser_tests.rs`, `version_check_tests.rs`) plus `mod_tests.rs` for
the `ModelProfile` and session-key hashing.
