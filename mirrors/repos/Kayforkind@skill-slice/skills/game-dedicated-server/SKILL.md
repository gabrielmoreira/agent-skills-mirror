---
name: game-dedicated-server
version: 1.1.1
description: "Builds Godot 4.3+ dedicated servers: headless export, dedicated_server feature tag, lobby/match state machines, CLI config, Linux/systemd deploy. Use when exporting a headless authoritative server, lobby management, or container/VPS hosting. Not for client HUD/UI (game-hud-system, godot-ui) and not a general Godot hub (game-godot)."
---

## When to Use
Reach for this skill when you are building a **dedicated server** in Godot 4.3+ — a headless build whose only job is to run the authoritative simulation while every player connects as a client. The reason to invest in this architecture is trust: when a single server owns the world state, no client can fabricate hits, teleport, or rewrite the score, because clients only ever *propose* actions and *receive* results. That same central authority keeps everyone's view of the match consistent (no host-migration headaches, no "it was a hit on my screen" disputes) and lets you scale match capacity on hardware you control instead of on whatever machine a player happens to host on.

Concretely, use it when you need: low, predictable latency under load; deterministic simulation for replay/anti-cheat; or the ability to run many matches across cloud instances or containers that have no GPU, display, or audio device.

## Prerequisites
- Godot 4.3 or later (headless export and feature tags are only dependable from 4.2/4.3 onward).
- For C# projects, .NET SDK installed on the build machine.
- A Linux VPS or container host for deployment (Windows PowerShell is primary for local development/testing).

## Procedure

### 1. Headless Export
A dedicated server runs with no display, GPU, or audio device. Godot supports this in two complementary ways:

**`--headless` Flag**
Pass `--headless` on the command line to suppress the display and audio drivers at runtime:
```powershell
.\my_game.exe --headless
```
This works on *any* exported binary, which makes it handy for quick local testing on Windows. What it does **not** do is shrink the binary — the rendering code is still compiled in, just unused.

**Server Export Preset**
For a real deployment you want the **server export template**, which strips rendering and audio code out of the binary entirely.

1. Open **Project → Export**.
2. Add a **Linux/X11** preset and name it `Linux Server` so it is obvious which preset is the server.
3. Under **Options → Binary**, enable **Export As Dedicated Server** (Godot 4.2+). This selects the server template that omits rendering and audio and sets the `dedicated_server` feature tag automatically.
4. Under **Resources**, use the **Exclude** list to strip client-only assets (shaders, high-res textures, music, voice-over) from the server PCK.
5. For C# projects, set the **.NET Runtime** option to `Bundled` or `System`. `Bundled` ships the runtime inside the export so the host needs nothing pre-installed.

**Feature Tags**
Use `OS.has_feature()` to branch between server and client code at runtime. Create an autoload (`boot.gd` or `Boot.cs`) that runs before any scene loads:

```gdscript
# boot.gd — autoload, runs before any scene loads.
extends Node

func _ready() -> void:
    if _is_dedicated_server():
        _configure_headless()
        ServerBootstrap.start()   # your server-side autoload entry point
    else:
        ClientBootstrap.start()   # your client-side autoload entry point

## True when this process should act as the authoritative server.
func _is_dedicated_server() -> bool:
    # `dedicated_server` is compiled into the server export template, so it is the most
    # reliable signal and stays true even if someone forgets the CLI flags. The headless
    # display-driver check is a fallback for the common case of running a *normal* export
    # with `--headless` during local testing.
    return OS.has_feature("dedicated_server") or DisplayServer.get_name() == "headless"

func _configure_headless() -> void:
    # Stop the renderer from doing per-frame work.
    RenderingServer.set_render_loop_enabled(false)

    # Under the real headless driver there is no window at all, so the calls below would be
    # meaningless. Only touch the window when one actually exists.
    if DisplayServer.get_name() != "headless":
        DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_MINIMIZED)
        DisplayServer.window_set_flag(DisplayServer.WINDOW_FLAG_BORDERLESS, true)
        DisplayServer.window_set_flag(DisplayServer.WINDOW_FLAG_NO_FOCUS, true)
```

### 2. Server Architecture
On a headless server, `_process` and `_physics_process` still run — the engine ticks normally, it just draws nothing. Put authoritative logic in `_physics_process` because it runs at a **fixed tick rate** (set by `Engine.physics_ticks_per_second`), ensuring determinism for replays, lag compensation, and anti-cheat.

Create a `ServerMain` autoload to own the tick loop and authoritative state. It should disable its process callbacks on clients.

```gdscript
# server_main.gd — add as autoload named ServerMain.
extends Node

@export var tick_rate: int = 60:
    set(value):
        tick_rate = maxi(value, 1)
        Engine.physics_ticks_per_second = tick_rate

@export var snapshot_interval: int = 3:
    set(value):
        snapshot_interval = maxi(value, 1)

var server_tick: int = 0
var _last_applied_tick: int = 0
var _player_state: Dictionary = {}

func _ready() -> void:
    if not multiplayer.is_server():
        process_mode = PROCESS_MODE_DISABLED
        return

    Engine.physics_ticks_per_second = tick_rate
    multiplayer.peer_connected.connect(_on_peer_connected)
    multiplayer.peer_disconnected.connect(_on_peer_disconnected)

func _physics_process(_delta: float) -> void:
    server_tick += 1
    _tick_game_logic()

func _on_peer_connected(peer_id: int) -> void:
    _player_state[peer_id] = Vector2.ZERO

func _on_peer_disconnected(peer_id: int) -> void:
    _player_state.erase(peer_id)

func _tick_game_logic() -> void:
    if _player_state.is_empty():
        return
    _advance_world_state()
    if server_tick % snapshot_interval == 0:
        _broadcast_snapshot()

func _advance_world_state() -> void:
    const STEP := Vector2(1.0, 0.0)
    for peer_id: int in _player_state:
        _player_state[peer_id] += STEP

func _broadcast_snapshot() -> void:
    _receive_snapshot.rpc(server_tick, _player_state)

@rpc("authority", "unreliable_ordered")
func _receive_snapshot(tick: int, state: Dictionary) -> void:
    if tick <= _last_applied_tick:
        return
    _last_applied_tick = tick
    _player_state = state.duplicate()
```

**Server-Only Logic Separated from Client**
Split your scene so server-only systems (physics, AI, scoring) and client-only systems (camera, HUD, audio) live in separate branches, then remove the branch a given peer does not need.

```gdscript
# world.gd
extends Node

@onready var server_systems: Node = $ServerSystems
@onready var client_systems: Node = $ClientSystems

func _ready() -> void:
    if Engine.is_editor_hint():
        return

    var is_server := multiplayer.is_server()
    var keep: Node = server_systems if is_server else client_systems
    var discard: Node = client_systems if is_server else server_systems

    keep.process_mode = PROCESS_MODE_INHERIT
    if is_instance_valid(discard):
        discard.queue_free()
```

**Network Bootstrap**
Guard scripts that have side effects so they behave correctly in the editor, server, and client. Binding a socket is exactly the kind of operation that fails in the real world.

```gdscript
# net_bootstrap.gd — autoload that establishes the multiplayer peer.
extends Node

func _ready() -> void:
    if Engine.is_editor_hint():
        return

    if multiplayer.is_server():
        _server_init()
    else:
        _client_init()

func _server_init() -> void:
    var peer := ENetMultiplayerPeer.new()
    var err := peer.create_server(ServerConfig.port, ServerConfig.max_players)
    if err != OK:
        push_error("[Server] Could not bind UDP %d: %s" % [ServerConfig.port, error_string(err)])
        get_tree().quit(1)
        return

    multiplayer.multiplayer_peer = peer
    multiplayer.peer_connected.connect(_on_peer_connected)
    multiplayer.peer_disconnected.connect(_on_peer_disconnected)

func _client_init() -> void:
    var peer := ENetMultiplayerPeer.new()
    var err := peer.create_client("127.0.0.1", ServerConfig.port)
    if err != OK:
        push_error("[Client] Could not create client peer: %s" % error_string(err)])
        return

    multiplayer.multiplayer_peer = peer
```

### 3. Lobby System
Model the lobby as a **per-player state dictionary keyed by `peer_id`**, held authoritatively on the server; clients never mutate it directly, they receive updates via RPC. Enforce a `--max-players` cap before accepting a peer, and use a ready-toggle RPC so every player must explicitly confirm before the match starts.

**WHEN to load:** Load `references/lobby-management.md` when you need the full GDScript and C# lobby implementation (player_list dict, max-players cap, ready-toggle RPC, broadcast pattern).

### 4. Match Flow
Drive the match lifecycle — lobby → countdown → in-game → results → back to lobby — with an explicit **state machine**. A single `enum` plus a `match`/`switch` makes the legal transitions obvious. The server owns `current_state` and is the only thing that changes it; clients merely receive state-change RPCs and update their UI. Send state changes **reliably** so no client is left stuck in a stale screen, and reset per-round flags (like ready states) on the return to `LOBBY`.

**WHEN to load:** Load `references/match-flow.md` when you need the full state machine with countdown/results timers and GDScript + C# implementations.

### 5. Server Configuration
Read runtime settings from `OS.get_cmdline_args()` — `--port`, `--max-players`, `--tick-rate`, `--log-level` — so one binary can serve many configurations without a rebuild. Set `Engine.physics_ticks_per_second` **before the first physics frame** (i.e., in an autoload's `_ready`, ahead of any gameplay autoload). The reference helper layers three sources with a deliberate precedence — **config file → environment variables → CLI args**, each overriding the last.

**WHEN to load:** Load `references/server-config.md` when you need the GDScript and C# argument-parsing helper that reads all four flags safely at startup, plus the config-file and environment-variable layering.

### 6. Deployment
The standard production layout is a **Linux VPS (or container host) running the headless export under a process supervisor**. A `Dockerfile` bundles the server binary, its PCK, and — for C# — the .NET runtime. A `systemd` unit then supervises the process: `Restart=on-failure` brings it back after a crash, `journald` captures stdout/stderr for inspection, and resource limits keep one match from starving the host. Open the UDP game port in the host firewall before your first connection test.

**WHEN to load:** Load `references/deployment.md` when you need the Dockerfile, the Linux VPS setup steps, the systemd unit file, and log-inspection commands.

## Pitfalls
- **Do not branch critical server logic on `OS.has_feature("headless")`.** `headless` is a *runtime* flag set only when `--headless` is passed on the command line; it is not baked into the binary. A server binary launched without that flag would silently fall through to client code. Prefer `OS.has_feature("dedicated_server")`, which the server export template compiles into the binary itself.
- **Do not drive critical game timing with `Timer` nodes on the server.** `Timer` is coupled to the scene tree and the frame loop, so it pauses when the tree pauses, drifts with frame-rate hitches, and fires on a schedule you cannot reproduce deterministically. For authoritative timing, accumulate `delta` inside `_physics_process`.
- **Do not use nonexistent window flags.** Earlier drafts of this pattern set `WINDOW_FLAG_NO_MOUSE` / `WINDOW_FLAG_NO_INPUT`, which **do not exist** in Godot 4 and would throw at runtime. They are intentionally omitted.
- **Do not put simulation logic in `_process`.** On a headless server with the render loop disabled its cadence is undefined.
- **Do not forget `Engine.is_editor_hint()` guards.** Running socket setup inside the editor would try to bind ports in the editor process itself.
- **Avoid Godot versions below 4.3.** The headless export ("Export As Dedicated Server") and the feature tags this skill relies on are only dependable from 4.2/4.3 onward.

## Verification
- [ ] Export preset uses the **server** export template (the `dedicated_server` feature is set automatically)
- [ ] Client-only assets (shaders, audio, high-res textures) are excluded from the server PCK
- [ ] Boot script branches on `OS.has_feature("dedicated_server")` (with `DisplayServer.get_name() == "headless"` as a fallback), **not** on `OS.has_feature("headless")` alone
- [ ] `RenderingServer.set_render_loop_enabled(false)` is called on the server so no render work happens
- [ ] Window mode/flags are only adjusted when a real window exists (correctly skipped under the headless display driver); no nonexistent flags like `WINDOW_FLAG_NO_MOUSE` are used
- [ ] Server-only nodes are freed (or set to `PROCESS_MODE_DISABLED`) on clients, and client-only nodes are freed/disabled on the server
- [ ] `Engine.is_editor_hint()` guard sits at the top of every `_ready()` that has side effects (socket binding, signal wiring, global mutation)
- [ ] `ServerConfig` parses `--port`, `--max-players`, `--tick-rate` before any gameplay autoload's `_ready()`, and `Engine.physics_ticks_per_second` is set before the first physics frame
- [ ] Config-file loading falls back gracefully (defaults retained) when `server.cfg` does not exist
- [ ] Settings are layered config file → environment variables → CLI args, in that precedence order
- [ ] `LobbyManager.player_list` size is checked against `max_players` *before* a new peer is accepted
- [ ] A peer that arrives to a full lobby is kicked via RPC before its connection is closed
- [ ] Ready states are reset when `MatchState` returns to `LOBBY`, so players re-confirm each round
- [ ] `MatchManager`/`ServerMain` run their tick logic only on the server (process disabled on clients)
- [ ] Countdown and results timers accumulate `_physics_process` delta rather than using `Timer` nodes (no scene-tree coupling, deterministic)
- [ ] Snapshots are throttled (sent every N ticks, not every tick) and use an unreliable transfer mode with a tick number so clients can drop stale packets
- [ ] Dockerfile copies both the binary and the `.pck` file, and (for C#) includes the matching .NET runtime
- [ ] The UDP game port is opened in the VPS firewall before the first connection test
- [ ] The `systemd` unit sets `Restart=on-failure` so the server recovers from crashes automatically
- [ ] Logs are routed to the `systemd` journal and inspectable with `journalctl -u my-game-server -f`
- [ ] For C# servers, the matching .NET runtime is bundled in the export or installed on the host, so the binary actually starts

## Related skills
See **multiplayer-basics** for ENet setup, RPCs, and the authority model that underpins everything here. See **multiplayer-sync** for state synchronization and interpolation (the client side of the snapshot loop above). For hardening a public-facing server, see **network-security** for DDoS mitigation, encryption, and authentication.
