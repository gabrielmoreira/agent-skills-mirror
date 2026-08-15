---
name: dedicated-server
version: 1.1.1
description: "Builds Godot 4.3+ dedicated servers: headless/server export templates, dedicated_server feature tag, boot autoload, lobby and match flow, config, and systemd/Docker deploy. Use when a headless authoritative simulation must host clients with no GPU or display. Not for listen-server host-migration peers or Godot below 4.3; never put gameplay authority on the client."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

## When to Use

Reach for this skill when you are building a **dedicated server** in Godot 4.3+ — a headless build whose only job is to run the authoritative simulation while every player connects as a client. The reason to invest in this architecture is trust: when a single server owns the world state, no client can fabricate hits, teleport, or rewrite the score, because clients only ever *propose* actions and *receive* results. That same central authority keeps everyone's view of the match consistent (no host-migration headaches, no "it was a hit on my screen" disputes) and lets you scale match capacity on hardware you control instead of on whatever machine a player happens to host on.

Concretely, use it when you need: low, predictable latency under load; deterministic simulation for replay/anti-cheat; or the ability to run many matches across cloud instances or containers that have no GPU, display, or audio device.

## Prerequisites

- **Godot 4.3 or later.** The headless export ("Export As Dedicated Server") and the `dedicated_server` feature tag are only dependable from 4.2/4.3 onward. Avoid Godot versions below 4.3 and their deprecated APIs.
- **Server export template installed.** Download it via the Godot editor's Template Manager so the "Export As Dedicated Server" option is available.
- **For C# projects:** .NET SDK installed locally for building; decide whether the export will bundle the runtime or rely on a system-installed `dotnet`.
- **Familiarity with ENet multiplayer.** See the **multiplayer-basics** skill for ENet setup, RPCs, and the authority model that underpins everything here.

## Procedure

Work through the sections below in order — they build on each other: boot detection → architecture → lobby → match flow → config → deployment.

### 1. Create the Headless Export Preset

A dedicated server runs with no display, GPU, or audio device. Godot supports this in two complementary ways:

#### `--headless` Flag (for quick local testing)

Pass `--headless` on the command line to suppress the display and audio drivers at runtime:

```bash
./my_game.x86_64 --headless
```

This works on *any* exported binary, which makes it handy for quick local testing. What it does **not** do is shrink the binary — the rendering code is still compiled in, just unused.

#### Server Export Preset (for production deployment)

For a real deployment you want the **server export template**, which strips rendering and audio code out of the binary entirely — smaller download, fewer native library dependencies, and no chance of accidentally touching GPU code paths.

1. Open **Project → Export**.
2. Add a **Linux/X11** preset and name it `Linux Server` so it is obvious which preset is the server.
3. Under **Options → Binary**, enable **Export As Dedicated Server** (Godot 4.2+). This selects the server template that omits rendering and audio and sets the `dedicated_server` feature tag automatically.
4. Under **Resources**, use the **Exclude** list to strip client-only assets (shaders, high-res textures, music, voice-over) from the server PCK. The server never draws or plays them, so shipping them only bloats the image and slows startup.
5. For C# projects, set the **.NET Runtime** option to `Bundled` or `System`. `Bundled` ships the runtime inside the export so the host needs nothing pre-installed — generally the easier choice for reproducible container builds; pick `System` only when you deliberately manage the `dotnet` runtime on the host.

**Feature tag summary:**

| Tag | Set by | Notes |
|-----|--------|-------|
| `dedicated_server` | Server export template | Baked into the binary, true regardless of launch flags. **Use this for server-specific logic.** |
| `headless` | `--headless` CLI flag | Runtime-only; absent if the flag is forgotten. Fine for diagnostics, risky for control flow. |
| Custom `server` | Your export preset's Custom Features | Useful when one binary plays multiple roles, or for finer-grained role flags. |

### 2. Write the Boot Autoload (Server/Client Detection)

The autoload below is the canonical "decide who I am, then configure accordingly" entry point. Detection order matters: `dedicated_server` first (reliable, baked into the binary), headless driver second (a fallback for forced-headless desktop runs).

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
    # Stop the renderer from doing per-frame work. The engine keeps ticking — _process and
    # _physics_process still fire — but nothing is drawn, so the server wastes no CPU/GPU
    # cycles on an invisible window.
    RenderingServer.set_render_loop_enabled(false)

    # Under the real headless driver there is no window at all, so the calls below would be
    # meaningless (and the headless driver already ignores input). Only touch the window
    # when one actually exists — a desktop export forced into headless-like behaviour with
    # `--headless`.
    if DisplayServer.get_name() != "headless":
        DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_MINIMIZED)
        DisplayServer.window_set_flag(DisplayServer.WINDOW_FLAG_BORDERLESS, true)
        DisplayServer.window_set_flag(DisplayServer.WINDOW_FLAG_NO_FOCUS, true)
```

C# equivalent:

```csharp
// Boot.cs — autoload, runs before any scene loads.
using Godot;

public partial class Boot : Node
{
    public override void _Ready()
    {
        if (IsDedicatedServer())
        {
            ConfigureHeadless();
            ServerBootstrap.Start();   // your server-side entry point
        }
        else
        {
            ClientBootstrap.Start();   // your client-side entry point
        }
    }

    private static bool IsDedicatedServer()
        => OS.HasFeature("dedicated_server") || DisplayServer.GetName() == "headless";

    private static void ConfigureHeadless()
    {
        RenderingServer.SetRenderLoopEnabled(false);

        if (DisplayServer.GetName() != "headless")
        {
            DisplayServer.WindowSetMode(DisplayServer.WindowMode.Minimized);
            DisplayServer.WindowSetFlag(DisplayServer.WindowFlags.Borderless, true);
            DisplayServer.WindowSetFlag(DisplayServer.WindowFlags.NoFocus, true);
        }
    }
}
```

> **API note:** earlier drafts of this pattern set `WINDOW_FLAG_NO_MOUSE` / `WINDOW_FLAG_NO_INPUT`, which **do not exist** in Godot 4 and would throw at runtime. They are intentionally omitted — the headless driver receives no input in the first place, and on a real window the borderless/no-focus flags are what you actually want.

### 3. Build the Server Game Loop

On a headless server, `_process` and `_physics_process` still run — the engine ticks normally, it just draws nothing. Put authoritative logic in `_physics_process` because it runs at a **fixed tick rate** (set by `Engine.physics_ticks_per_second`), so the same sequence of inputs produces the same simulation regardless of how loaded the server is. That determinism is what makes replays, lag compensation, and server-authoritative anti-cheat possible.

```gdscript
# server_main.gd — add as autoload named ServerMain.
extends Node

## Physics ticks per second; mirrors Project Settings → Physics → Common → Physics Ticks
## Per Second and can be overridden with --tick-rate at launch. Clamped to at least 1
## because a non-positive rate would stall the physics loop entirely.
@export var tick_rate: int = 60:
    set(value):
        tick_rate = maxi(value, 1)
        Engine.physics_ticks_per_second = tick_rate

## Physics ticks between client snapshots. At 60 Hz, a value of 3 sends ~20 snapshots per
## second — smooth enough for client interpolation while keeping bandwidth low.
@export var snapshot_interval: int = 3:
    set(value):
        snapshot_interval = maxi(value, 1)

## Monotonic tick counter; also used to timestamp and throttle snapshots.
var server_tick: int = 0

## Highest snapshot tick a client has applied, so stale packets can be dropped.
var _last_applied_tick: int = 0

## Authoritative per-player state. Shape: { peer_id (int): position (Vector2) }.
var _player_state: Dictionary = {}


func _ready() -> void:
    if not multiplayer.is_server():
        process_mode = PROCESS_MODE_DISABLED
        return

    Engine.physics_ticks_per_second = tick_rate
    multiplayer.peer_connected.connect(_on_peer_connected)
    multiplayer.peer_disconnected.connect(_on_peer_disconnected)
    print("[Server] Started — %d Hz, snapshot every %d ticks" % [tick_rate, snapshot_interval])


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

### 4. Separate Server-Only and Client-Only Logic

Split your scene so server-only systems (physics, AI, scoring) and client-only systems (camera, HUD, audio) live in separate branches, then remove the branch a given peer does not need. Freeing (rather than just disabling) reclaims memory and makes it impossible for those nodes to receive input, RPCs, or process callbacks by accident.

```gdscript
# world.gd
extends Node

@onready var server_systems: Node = $ServerSystems   # physics, AI, scoring
@onready var client_systems: Node = $ClientSystems   # camera, HUD, audio


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

### 5. Guard Side-Effect Scripts for Three Environments

Guard scripts that have side effects so they behave correctly in the **editor**, the **server**, and the **client**. Binding a socket is exactly the kind of operation that fails in the real world (port already in use, blocked by a firewall, server not yet up):

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
    print("[Server] Listening on UDP %d (max %d clients)" % [ServerConfig.port, ServerConfig.max_players])


func _client_init() -> void:
    var peer := ENetMultiplayerPeer.new()
    var err := peer.create_client("127.0.0.1", ServerConfig.port)
    if err != OK:
        push_error("[Client] Could not create client peer: %s" % error_string(err))
        return

    multiplayer.multiplayer_peer = peer
    multiplayer.connected_to_server.connect(_on_connected)
    multiplayer.connection_failed.connect(_on_connection_failed)
    print("[Client] Connecting to 127.0.0.1:%d…" % ServerConfig.port)


func _on_peer_connected(peer_id: int) -> void:
    print("[Server] Peer %d connected" % peer_id)


func _on_peer_disconnected(peer_id: int) -> void:
    print("[Server] Peer %d disconnected" % peer_id)


func _on_connected() -> void:
    print("[Client] Connected to server")


func _on_connection_failed() -> void:
    push_error("[Client] Connection failed — is the server running?")
    multiplayer.multiplayer_peer = null
```

### 6. Implement the Lobby System

Model the lobby as a **per-player state dictionary keyed by `peer_id`**, held authoritatively on the server; clients never mutate it directly, they receive updates via RPC. Enforce a `--max-players` cap before accepting a peer (otherwise a full match can be overrun), and use a ready-toggle RPC so every player must explicitly confirm before the match starts. Store a small `PlayerData` record per peer (name, ready flag, character selection) rather than loose fields, so the shape stays self-documenting.

> **Load `references/lobby-management.md`** when implementing the lobby. It contains the full GDScript and C# lobby implementation: `player_list` dict, max-players cap enforcement, ready-toggle RPC, and the broadcast-update pattern.

### 7. Implement the Match Flow State Machine

Drive the match lifecycle — lobby → countdown → in-game → results → back to lobby — with an explicit **state machine**. A single `enum` plus a `match`/`switch` makes the legal transitions obvious and keeps "what happens next" in one place. The server owns `current_state` and is the only thing that changes it; clients merely receive state-change RPCs and update their UI. Send state changes **reliably** so no client is left stuck in a stale screen, and reset per-round flags (like ready states) on the return to `LOBBY` so the next round requires fresh confirmation.

> **Load `references/match-flow.md`** when implementing match flow. It contains the full state machine with countdown/results timers and GDScript + C# implementations. The timers accumulate `_physics_process` delta rather than using `Timer` nodes.

### 8. Add Server Configuration

Read runtime settings from `OS.get_cmdline_args()` — `--port`, `--max-players`, `--tick-rate`, `--log-level` — so one binary can serve many configurations without a rebuild. **Critical ordering rule:** set `Engine.physics_ticks_per_second` **before the first physics frame** (i.e., in an autoload's `_ready`, ahead of any gameplay autoload), because changing the tick rate mid-simulation would make timing discontinuous. The reference helper layers three sources with a deliberate precedence — **config file → environment variables → CLI args**, each overriding the last.

> **Load `references/server-config.md`** when implementing configuration. It contains the GDScript and C# argument-parsing helper that reads all four flags safely at startup, plus the config-file and environment-variable layering.

### 9. Deploy the Server

The standard production layout is a **Linux VPS (or container host) running the headless export under a process supervisor**. A `Dockerfile` bundles the server binary, its PCK, and — for C# — the .NET runtime, giving you a reproducible image you can run anywhere. A `systemd` unit then supervises the process: `Restart=on-failure` brings it back after a crash, `journald` captures stdout/stderr for inspection, and resource limits keep one match from starving the host. Prefer a multi-stage Docker build so the final image carries only the runtime, not the build tooling. Open the UDP game port in the host firewall before your first connection test — a silently-dropped UDP handshake is a common and confusing first failure.

> **Load `references/deployment.md`** when deploying. It contains the Dockerfile, the Linux VPS setup steps, the systemd unit file, and log-inspection commands.

## Pitfalls

- **Do not branch critical server logic on `OS.has_feature("headless")` alone.** `headless` is a *runtime* flag set only when `--headless` is passed on the command line; it is not baked into the binary. A server binary launched without that flag (a misconfigured systemd unit, a teammate testing locally) would silently fall through to client code. Prefer `OS.has_feature("dedicated_server")`, which the server export template compiles into the binary itself, so it is true no matter how the process is launched.

- **Do not drive critical game timing with `Timer` nodes on the server.** `Timer` is coupled to the scene tree and the frame loop, so it pauses when the tree pauses, drifts with frame-rate hitches, and fires on a schedule you cannot reproduce deterministically. For authoritative timing, accumulate `delta` inside `_physics_process`, which runs at a fixed tick rate independent of rendering.

- **Do not use nonexistent window flags.** `WINDOW_FLAG_NO_MOUSE` and `WINDOW_FLAG_NO_INPUT` do not exist in Godot 4 and would throw at runtime. The headless driver receives no input in the first place; on a real window, use `WINDOW_FLAG_BORDERLESS` and `WINDOW_FLAG_NO_FOCUS`.

- **Do not put simulation logic in `_process`.** On a headless server with the render loop disabled, its cadence is undefined. Use `_physics_process` for all authoritative logic.

- **Do not forget the `Engine.is_editor_hint()` guard.** Running socket setup inside the editor would try to bind ports in the editor process itself. Place the guard at the top of every `_ready()` that has side effects (socket binding, signal wiring, global mutation).

- **Do not change `Engine.physics_ticks_per_second` mid-simulation.** Set it in an autoload's `_ready` before any gameplay autoload runs, or timing becomes discontinuous.

- **Do not send snapshots every tick.** Throttle them (e.g., every 3 ticks at 60 Hz ≈ 20 snapshots/second) and use unreliable transfer mode with a tick number so clients can drop stale packets.

- **Do not let clients mutate lobby state directly.** The server owns the `player_list` dictionary; clients receive updates via RPC. If a client could declare the match started, it could start one early or skip the countdown.

- **Do not forget to reset ready states on return to `LOBBY`.** Each new round requires fresh confirmation from every player.

- **Do not ship client-only assets in the server PCK.** Shaders, high-res textures, music, and voice-over bloat the image and slow startup. Use the export preset's Exclude list.

- **Do not forget to open the UDP game port in the VPS firewall.** A silently-dropped UDP handshake is a common and confusing first failure.

## Verification

Run through this checklist to confirm the dedicated server is correctly configured:

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

## Related Skills

- **multiplayer-basics** — ENet setup, RPCs, and the authority model that underpins everything here.
- **multiplayer-sync** — State synchronization and interpolation (the client side of the snapshot loop above).
- **network-security** — DDoS mitigation, encryption, and authentication for hardening a public-facing server.
