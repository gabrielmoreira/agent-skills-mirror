# Server lifecycle, authority, and plugin reload

Part of the Godot AI agent guide — see [AGENTS.md](../AGENTS.md) for the
always-loaded rules.

Godot AI v4 has one lifecycle owner:
`plugin/addons/godot_ai/utils/server_lifecycle.gd`. The plugin root captures an
immutable launch plan on the main thread, configures the owner without side
effects, completes composition, and only then activates it. When
`addons/.godot_ai_update/pending.json` exists, the root first hashes the live
tree against the marker and records the outcome
([self-update.md](self-update.md)); a `repair_required` outcome keeps the
plugin inactive. Otherwise the root may construct owners and UI but keeps
`_normal_start_released == false`: lifecycle start/restart/recover and all
other normal client, update, transport, and telemetry effects remain barred
until that post-restart tree verification and the pin-only client repin have
finished. Stop remains available so shutdown cannot be trapped behind the
release gate.

## One serialized episode

The lifecycle stores one tagged episode with these states:

```text
DORMANT -> STARTING -> READY
                    -> BLOCKED
READY   -> STOPPING -> DORMANT
BLOCKED -> RECOVERING -> STARTING
```

An authenticated endpoint that drops moves `READY -> BLOCKED(endpoint_lost)`
and revokes the connection, then re-probes on its own with a bounded backoff
(1, 2, 4, 8, 16 s; five attempts per outage), each attempt running the same
start path a dock Restart would, so the server must re-prove its capability.
After the last attempt the block stays until Restart. A server that holds for
a minute earns a fresh budget; one that flaps faster spends it and stops.

Startup effects are `PROBE`, `LAUNCH`, and `PROVE`; control effects are
`REPLACE` and `STOP`. Every effect carries the active episode ID. Completion
for an older or cancelled episode is discarded, so a late worker cannot revive
state from a superseded start/stop/replacement attempt. The lifecycle exposes
copied snapshots and narrow effect signals; it does not retain the plugin or
Dock and has no generic `_host.*` callback surface.

## Capabilities are not process authority

The three authority values are deliberately separate:

- `TransportAuthority` contains the HTTP/WS ports, server instance ID, and the
  two independent private capabilities. Its public snapshot omits both
  secrets. It permits authenticated communication, not process control.
- `OwnedProcessGrant` binds a PID to a process fingerprint captured after the
  launched backend publishes and proves its capability record. Stop/restart
  rechecks that exact identity before killing anything.
- `ReplacementAuthorization` is created only from an explicit Dock intent. It
  is short-lived, bound to one instance/version/port tuple, and spend-once.
  Re-probing must match that tuple before replacement proceeds.

Possessing transport metadata, seeing a branded status response, or occupying
the expected port never upgrades into kill authority. A foreign,
unauthenticated, changed, or otherwise unproven occupant leaves the lifecycle
in `BLOCKED`.

## Startup and adoption

1. Read the private per-port capability record.
2. Probe `/godot-ai/status` with its HTTP bearer and enforce the 8 KiB response
   bound.
3. If the authenticated endpoint has the expected version and WS port, adopt
   its transport authority. Adoption deliberately carries no process grant.
4. If the HTTP port is free, check the WebSocket port too: the server binds
   both before it publishes anything, so a held WebSocket port (a server moved
   off the HTTP port, another editor) blocks the start with `ws_occupied` and
   names `godot_ai/ws_port` instead of dying at the server's preflight. The
   dock's port picker moves both ports and keeps whichever one is free. Then
   launch the configured command with fresh independent HTTP and WebSocket
   capabilities.
5. Wait for the new capability record, authenticate status, and bind the live
   process fingerprint before publishing `READY`.

Two diagnostics sit around step 4. On Windows the plugin creates and probes
the capability directory before it spawns: the server would otherwise create
it with `mode=0o700`, which CPython renders as a DACL of SYSTEM, Administrators
and OWNER RIGHTS only, and a directory first created by an elevated process is
unusable from the user's unelevated editor, server and bridge (#988). A failed
probe blocks the start with the directory path and the elevated `Remove-Item`
repair; the server and the `attach` bridge report the same message from their
side. The plugin also passes `--startup-report <user://...json>` beside
`--pid-file` and removes any stale report before the spawn. A server that
fails before publishing its record writes `{pid, error, message, hint}` there
(a port already in use, an unwritable directory, an import error); the first
report wins and the record's publication disarms it. The dock appends that
text to "exited before publishing capabilities", to the proof timeout, and to
a launch whose process identity could not be captured (the process usually
died refusing to start, and the report says why). The report is quoted,
bounded and never interpreted. When the HTTP port is held and a capability
record exists for it but does not authenticate the occupant, the block names
the reason (a probe timeout, a different instance, a non-godot-ai listener).

The Python server owns the private record and a per-port launch claim. HTTP,
status, and lease routes require the HTTP bearer. The editor WebSocket stays on
IPv4 loopback and uses a transcript-bound challenge/response before the editor
reveals project metadata. There is no legacy v3 protocol fallback, tokenless
retry, or bare URL fallback in v4. One deliberately untrusted read exists
beside the probe:
when the port is bound and the authenticated probe finds no record, the
lifecycle performs a single bounded, tokenless GET of `/godot-ai/status`
and, only if the body claims `name: godot-ai` with a `3.x`
`server_version`, words the BLOCKED message as a pre-v4 server kept
alive by a client's old bridge. That result never enters the probe
outcome, never becomes a transport, and grants no replacement or kill
authority; the occupant stays `replaceable: false`. After an update the
plugin re-probes such a block slowly for about three and a half minutes,
long enough for the old bridge's lease and the server's idle backstop to
run out once the user quits and relaunches that client.

An adopted backend remains external. Ordinary teardown drops the transport and
leaves it running. A plugin-launched backend is stopped only with its matching
owned-process grant, except when `keep_server_on_exit` is enabled or a live
attach lease requires continuity; in either case the plugin deliberately
detaches. Lease counts are finite and authenticated like every other HTTP
route.

## Command discovery

The immutable plan uses one three-tier command order:

1. `.venv/bin/python -m godot_ai` for a nearby development checkout;
2. isolated/no-config/no-build `uvx --from godot-ai==VERSION godot-ai` with
   official PyPI explicit for an exact user version;
3. a matching `godot-ai` executable as the system fallback.

`PYTHONPATH`, ports, exclusions, allow-host ranges, telemetry preference,
keep-alive policy, PID-file path, and command argv are captured on the main
thread. Worker effects consume those copied values and do not read mutable
EditorSettings or environment state.

For Python auto-reload during development, start one explicit external server
from the intended worktree:

```bash
script/serve-this-worktree
```

The script prepends that worktree's `src/` and starts Uvicorn with `--reload`;
the editor adopts it through the same authenticated capability boundary. The
Dock does not own or kill this external reload supervisor.

## Headless and unsupported editors

Normal headless launches return before server composition. Set
`GODOT_AI_ALLOW_HEADLESS=1` only for intentional CI/editor sessions. Godot 4.5
and 4.6 are below the v4 floor and return even earlier: they emit the Godot 4.7
requirement and construct no lifecycle, exporter, updater, transport, or client
worker.

## Plugin reload

`editor_reload_plugin` disables and re-enables the plugin in the same editor.
All client threads are realized, dispatcher references are cleared, transport
is torn down, and the lifecycle either stops its exact owned process or detaches
according to the rules above. The Python handler waits for a distinct
authenticated replacement session; it never treats the old session entry as a
successful reload.

The editor tool first waits for the filesystem's main-thread completion
notification, not merely `is_scanning() == false`: that worker flag can clear
before Godot applies resource/script reloads. One bounded native-signal handoff
survives those script reloads without retaining a suspended handler coroutine.
A real-time five-second deadline leaves the plugin unchanged on timeout;
duplicate requests are refused, stale callbacks cannot consume a later request,
and direct reload cancels pending scan work. The script-work ledger remains
busy until this handoff actually completes or is cancelled. The transaction
coordinator already has its own notification-driven scan state and is unchanged.

Ordinary reloads from the editor tool, Dock, and pre-mutation update-abort
recovery share `utils/plugin_reload.gd`. It requires an enabled plugin, toggles
it, verifies re-enablement, then saves project settings **after** the engine's
enable call has completed. Startup/autoload callbacks may save the temporary
disabled list during that call; without the final save, a working reloaded
plugin can be disabled on the next editor start. Enable/save failures are
reported, not treated as persisted success. This helper does not replace or
relax the transaction coordinator's separate quiescence and readiness protocol.

The Dock's managed-server control is visible only in developer mode. It starts,
restarts, or stops only the lifecycle's exact fingerprinted child. If the port
belongs to any external process—including `serve-this-worktree`—the control
reads **External Server Running** and is disabled; stop that process at its
owner rather than transferring kill authority to the Dock.
