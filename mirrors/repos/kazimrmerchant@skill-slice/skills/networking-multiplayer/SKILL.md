---
name: networking-multiplayer
description: "Implements Godot 4.x multiplayer: ENet, WebSocket, or WebRTC peers, @rpc, MultiplayerSpawner and MultiplayerSynchronizer, dedicated --headless servers, lobbies, and client-side prediction. Use when adding online or LAN play, RPCs, or Steam relay NAT traversal. Not for racing vehicle physics (game-godot-genre-racing) or generic REST backends outside Godot. Do not trust client RPCs without server validation."
version: 1.0.1
---

# Networking & Multiplayer (Godot 4.x)

Complete reference for building multiplayer games in Godot 4.x. Covers the high-level multiplayer API, RPCs, synchronization nodes, dedicated servers, and network architecture patterns.

## When to Use

Use this skill whenever you are:

- Adding **online multiplayer** or LAN play to a Godot 4.x project
- Implementing **RPCs** (`@rpc` annotation, `rpc()`, `rpc_id()`)
- Setting up **dedicated servers** (headless mode, `--server` CLI flag)
- Using **MultiplayerSpawner** or **MultiplayerSynchronizer** nodes
- Building **lobbies**, matchmaking, or ready-check systems
- Implementing **client-side prediction** or lag compensation
- Making **REST API calls** via `HTTPRequest` or **WebSocket** clients
- Integrating **GodotSteam** for Steam relay / NAT traversal
- **Debugging** desyncs, connection drops, or bandwidth issues

Trigger keywords: `multiplayer`, `networking`, `RPC`, `dedicated server`, `lobby`, `sync`, `ENet`, `WebSocket`, `WebRTC`, `peer`, `authority`, `client-side prediction`, `lag compensation`, `HTTPRequest`, `GodotSteam`, `NAT traversal`.

## Prerequisites

- **Godot 4.x** (4.0 or later). The `MultiplayerAPI` redesign is 4.x-only; Godot 3.x uses a different API.
- Basic familiarity with GDScript, scenes, and node architecture. See [gdscript](../gdscript/SKILL.md) and [scene-and-nodes](../scene-and-nodes/SKILL.md).
- For dedicated server deployment: a machine or VPS reachable on your chosen port with firewall rules opened.
- For Steam networking: the [GodotSteam](https://github.com/GodotSteam/GodotSteam) plugin compiled into your editor and export templates.
- **Windows host (primary):** Commands below assume PowerShell. On Windows, use `godot.exe` or add the Godot binary to your `PATH`. Example:

  ```powershell
  godot --headless --path ~\projects\my-game
  ```

## Procedure

### 1. Choose a transport peer

| Peer | Transport | Use Case |
|---|---|---|
| `ENetMultiplayerPeer` | UDP (ENet) | Desktop/mobile LAN and WAN games |
| `WebSocketMultiplayerPeer` | WebSocket | Web exports, firewall-friendly |
| `WebRTCMultiplayerPeer` | WebRTC (P2P) | Browser-to-browser, low latency |
| `SteamMultiplayerPeer` | Steam (GodotSteam) | Steam relay, NAT traversal |

### 2. Create a server

```gdscript
func create_server(port: int = 9999, max_clients: int = 32) -> void:
    var peer := ENetMultiplayerPeer.new()
    var error: Error = peer.create_server(port, max_clients)
    if error != OK:
        push_error("Failed to create server: %s" % error_string(error))
        return
    multiplayer.multiplayer_peer = peer
    print("Server started on port %d" % port)
```

### 3. Create a client

```gdscript
func join_server(address: String = "127.0.0.1", port: int = 9999) -> void:
    var peer := ENetMultiplayerPeer.new()
    var error: Error = peer.create_client(address, port)
    if error != OK:
        push_error("Failed to connect: %s" % error_string(error))
        return
    multiplayer.multiplayer_peer = peer
```

### 4. Wire up connection signals

```gdscript
func _ready() -> void:
    multiplayer.peer_connected.connect(_on_peer_connected)
    multiplayer.peer_disconnected.connect(_on_peer_disconnected)
    multiplayer.connected_to_server.connect(_on_connected_to_server)      # client only
    multiplayer.connection_failed.connect(_on_connection_failed)            # client only
    multiplayer.server_disconnected.connect(_on_server_disconnected)        # client only

func _on_peer_connected(id: int) -> void:
    print("Peer connected: %d" % id)

func _on_peer_disconnected(id: int) -> void:
    print("Peer disconnected: %d" % id)
    # Clean up the disconnected player's nodes
    var player_node: Node = get_node_or_null(str(id))
    if player_node:
        player_node.queue_free()

func _on_connected_to_server() -> void:
    print("Connected! My ID: %d" % multiplayer.get_unique_id())
```

### 5. Define RPCs with `@rpc`

```gdscript
# @rpc annotation parameters:
# authority mode: "any_peer" or "authority" (default)
# sync mode:     "call_local" or "call_remote" (default)
# transfer mode: "reliable" (default), "unreliable", "unreliable_ordered"
# channel:       0-255 (separate channels for independent ordering)

@rpc("any_peer", "call_local", "reliable")
func chat_message(message: String) -> void:
    var sender_id: int = multiplayer.get_remote_sender_id()
    display_chat(sender_id, message)

# Call an RPC:
chat_message.rpc("Hello everyone!")          # call on ALL peers
chat_message.rpc_id(1, "Hello server!")      # call on specific peer (1 = server)

# Authority-only RPC (only server can call):
@rpc("authority", "call_remote", "reliable")
func update_score(player_id: int, score: int) -> void:
    scores[player_id] = score
    update_scoreboard()

# Unreliable RPC for frequent updates:
@rpc("authority", "call_remote", "unreliable_ordered")
func sync_position(pos: Vector2) -> void:
    global_position = pos
```

### 6. Validate ALL client-sent RPCs on the server

**HARD RULE: Never trust the client.** Every `@rpc("any_peer", ...)` handler must validate the sender and the requested action on the server before executing or broadcasting.

```gdscript
@rpc("any_peer", "call_local", "reliable")
func request_action(action: String, target_id: int) -> void:
    if not multiplayer.is_server():
        return

    var sender: int = multiplayer.get_remote_sender_id()

    # Validate the sender is allowed to do this
    if not is_valid_action(sender, action, target_id):
        push_warning("Invalid action from peer %d" % sender)
        return

    # Execute on server, then broadcast result to all
    perform_action.rpc(sender, action, target_id)
```

### 7. Spawn players with MultiplayerSpawner

Scene structure (all peers):

```
World
  ├── MultiplayerSpawner
  └── Players (Node — spawn path)
```

MultiplayerSpawner configuration:
- **Spawn Path:** `../Players` (where spawned scenes are added)
- **Auto Spawn List:** add `PackedScene` resources that can be spawned
- OR use `spawn_function` for custom spawning

```gdscript
func _ready() -> void:
    if multiplayer.is_server():
        multiplayer.peer_connected.connect(_on_peer_connected)

func _on_peer_connected(id: int) -> void:
    spawn_player(id)

func spawn_player(id: int) -> void:
    var player: CharacterBody2D = preload("res://player.tscn").instantiate()
    player.name = str(id)  # name MUST be unique!
    $Players.add_child(player)  # spawner auto-replicates to clients
```

Custom spawn function:

```gdscript
@onready var spawner: MultiplayerSpawner = $MultiplayerSpawner

func _ready() -> void:
    spawner.spawn_function = custom_spawn

func custom_spawn(data: Variant) -> Node:
    var player_data: Dictionary = data as Dictionary
    var player: CharacterBody2D = preload("res://player.tscn").instantiate()
    player.name = str(player_data["id"])
    player.global_position = player_data["position"]
    player.set_multiplayer_authority(player_data["id"])
    return player

# Trigger spawn (server only):
func spawn_player(id: int, pos: Vector2) -> void:
    spawner.spawn({"id": id, "position": pos})
```

### 8. Sync properties with MultiplayerSynchronizer

Scene structure:

```
Player (CharacterBody2D)
  ├── MultiplayerSynchronizer
  ├── Sprite2D
  └── CollisionShape2D
```

Replication config — add properties with sync modes:

| Sync Mode | When it sends | Example properties |
|---|---|---|
| **Always** | Every tick | `position`, `rotation` |
| **On Change** | Only when value changes | `health`, `score` |
| **Spawn** | Only on initial spawn | `player_name`, `skin` |

Visibility filters (only sync to peers that can "see" this object):

```gdscript
@onready var sync: MultiplayerSynchronizer = $MultiplayerSynchronizer

func _ready() -> void:
    if multiplayer.is_server():
        sync.set_visibility_for(peer_id, true)   # enable for specific peer
        sync.set_visibility_for(peer_id, false)  # disable

# Custom visibility check:
sync.visibility_update_mode = MultiplayerSynchronizer.VISIBILITY_PROCESS_IDLE
sync.add_visibility_filter(func(peer: int) -> bool:
    var peer_pos: Vector2 = get_peer_position(peer)
    return global_position.distance_to(peer_pos) < 1000.0
)
```

### 9. Set authority correctly

```gdscript
# Set authority (who controls this node):
player_node.set_multiplayer_authority(peer_id)

# Check authority:
if is_multiplayer_authority():
    # This peer controls this node — process input, send updates
    handle_input()

# Transfer authority (e.g., player picks up object):
func pick_up(object: Node) -> void:
    if multiplayer.is_server():
        object.set_multiplayer_authority(multiplayer.get_unique_id())
```

### 10. Run a dedicated server (headless mode)

**Windows (PowerShell):**

```powershell
godot --headless --path ~\projects\my-game
```

**Linux/macOS:**

```bash
godot --headless --path /path/to/project
```

Detect headless mode in code:

```gdscript
func _ready() -> void:
    if DisplayServer.get_name() == "headless":
        # Headless mode — start as server
        create_server()
    else:
        # Graphical mode — show lobby UI
        show_lobby_menu()

# Alternative: use command-line arguments
func _ready() -> void:
    if "--server" in OS.get_cmdline_args():
        create_server()
```

### 11. Build a lobby system

```gdscript
# Autoload: LobbyManager
extends Node

signal player_list_updated(players: Dictionary)

var players: Dictionary = {}  # { peer_id: { "name": String, "ready": bool } }

func _ready() -> void:
    multiplayer.peer_connected.connect(_on_peer_connected)
    multiplayer.peer_disconnected.connect(_on_peer_disconnected)

@rpc("any_peer", "call_local", "reliable")
func register_player(player_name: String) -> void:
    var id: int = multiplayer.get_remote_sender_id()
    players[id] = {"name": player_name, "ready": false}
    sync_player_list.rpc(players)

@rpc("any_peer", "call_local", "reliable")
func set_ready(ready: bool) -> void:
    var id: int = multiplayer.get_remote_sender_id()
    if id in players:
        players[id]["ready"] = ready
        sync_player_list.rpc(players)
        check_all_ready()

@rpc("authority", "call_local", "reliable")
func sync_player_list(updated_players: Dictionary) -> void:
    players = updated_players
    player_list_updated.emit(players)

func check_all_ready() -> void:
    if not multiplayer.is_server():
        return
    if players.size() < 2:
        return
    for player_data: Dictionary in players.values():
        if not player_data["ready"]:
            return
    start_game.rpc()

@rpc("authority", "call_local", "reliable")
func start_game() -> void:
    get_tree().change_scene_to_packed(preload("res://game.tscn"))
```

### 12. Implement client-side prediction

Concept: client moves immediately, server validates, client corrects if wrong.

```gdscript
extends CharacterBody2D

var server_position: Vector2 = Vector2.ZERO
var correction_threshold: float = 5.0

func _physics_process(delta: float) -> void:
    if is_multiplayer_authority():
        # Local prediction — move immediately
        var input_dir: Vector2 = Input.get_vector("left", "right", "up", "down")
        velocity = input_dir * speed
        move_and_slide()

        # Send input to server
        send_input.rpc_id(1, input_dir)
    else:
        # Interpolate to last known position (other players)
        global_position = global_position.lerp(server_position, 10.0 * delta)

@rpc("any_peer", "call_remote", "unreliable_ordered")
func send_input(input_dir: Vector2) -> void:
    if not multiplayer.is_server():
        return
    # Server validates and applies movement
    velocity = input_dir * speed
    move_and_slide()
    # Broadcast authoritative position
    sync_position.rpc(global_position)

@rpc("authority", "call_remote", "unreliable_ordered")
func sync_position(pos: Vector2) -> void:
    server_position = pos
    # Snap if too far off (correction)
    if global_position.distance_to(pos) > correction_threshold:
        global_position = pos
```

### 13. Make REST API calls with HTTPRequest

```gdscript
@onready var http: HTTPRequest = $HTTPRequest

func _ready() -> void:
    http.request_completed.connect(_on_request_completed)

func fetch_leaderboard() -> void:
    var error: Error = http.request(
        "https://api.example.com/leaderboard",
        ["Authorization: Bearer %s" % api_key],
        HTTPClient.METHOD_GET
    )

func post_score(score: int) -> void:
    var body: String = JSON.stringify({"score": score})
    http.request(
        "https://api.example.com/scores",
        ["Content-Type: application/json"],
        HTTPClient.METHOD_POST,
        body
    )

func _on_request_completed(
    result: int,
    response_code: int,
    headers: PackedStringArray,
    body: PackedByteArray
) -> void:
    if result != HTTPRequest.RESULT_SUCCESS:
        push_error("HTTP request failed: %d" % result)
        return
    var json: Variant = JSON.parse_string(body.get_string_from_utf8())
    process_response(json)
```

> **Security:** Never hardcode API keys in source. Use `YOUR_KEY` placeholders in examples and load real keys from environment variables or a `.env` file excluded from version control.

### 14. Use a WebSocket client

```gdscript
var ws := WebSocketPeer.new()

func _ready() -> void:
    ws.connect_to_url("wss://echo.websocket.org")

func _process(_delta: float) -> void:
    ws.poll()
    var state: WebSocketPeer.State = ws.get_ready_state()

    if state == WebSocketPeer.STATE_OPEN:
        while ws.get_available_packet_count() > 0:
            var packet: PackedByteArray = ws.get_packet()
            handle_message(packet.get_string_from_utf8())

    elif state == WebSocketPeer.STATE_CLOSED:
        var code: int = ws.get_close_code()
        print("WebSocket closed: %d" % code)
        set_process(false)

func send_message(msg: String) -> void:
    ws.send_text(msg)
```

### 15. Test multiplayer locally

From the editor: **Debug > Run Multiple Instances >** set to 2, 3, or 4.

From command line (Windows PowerShell):

```powershell
# Instance 1 (server):
godot --path . -- --server

# Instance 2 (client):
godot --path . -- --client
```

Parse custom args:

```gdscript
func _ready() -> void:
    var args: PackedStringArray = OS.get_cmdline_user_args()
    if "--server" in args:
        create_server()
    elif "--client" in args:
        join_server()
```

## Pitfalls

| Anti-pattern | Why it's bad | Do this instead |
|---|---|---|
| **Client as authority for game state** | Clients can cheat freely | Use server-authoritative architecture |
| **`rpc("any_peer")` without validation** | Any client can call any function | Validate sender ID and permissions on server |
| **Sending full state every frame** | Bandwidth explosion | Use delta sync; `unreliable_ordered` for position |
| **Reliable RPCs for position updates** | Causes head-of-line blocking | Use `unreliable_ordered` for frequent updates |
| **Not cleaning up on disconnect** | Orphaned nodes, memory leaks | Remove player nodes in `peer_disconnected` handler |
| **Hardcoded IP addresses** | Breaks deployment | Use lobby/matchmaking system or config file |
| **Synchronizing input, not state** | Desyncs compound over time | Periodically sync authoritative state |
| **Duplicate node names for spawned players** | Replication conflicts, crashes | Always name spawned nodes by peer ID (`str(id)`) |
| **Forgetting to set multiplayer authority** | Input goes to wrong peer; no one controls the node | Call `set_multiplayer_authority(peer_id)` on spawn |
| **Not handling `server_disconnected`** | Clients hang silently when server dies | Show reconnect UI and clean up local state |
| **Using `call_local` on authority-only RPCs carelessly** | Server double-processes or clients execute server logic | Only use `call_local` when the caller should also run it |
| **No timeout for unresponsive peers** | Lobby stalls forever | Implement a heartbeat or timeout timer per peer |

## Verification

Run through this checklist to confirm your multiplayer implementation is correct and secure:

- [ ] **Server validates ALL client inputs** — never trust the client. Every `@rpc("any_peer")` handler checks `multiplayer.is_server()` and validates the sender.
- [ ] **Unique node names** for multiplayer-spawned nodes (use peer ID as the node name).
- [ ] **Authority set correctly** on player nodes via `set_multiplayer_authority(peer_id)`.
- [ ] **Connection signals** handle disconnection cleanup (`peer_disconnected` → `queue_free`).
- [ ] **RPCs use appropriate transfer mode** — `reliable` for important events, `unreliable_ordered` for position.
- [ ] **MultiplayerSynchronizer** uses visibility filters for large worlds.
- [ ] **Dedicated server** uses headless mode (`--headless`).
- [ ] **Port forwarding or relay service** configured for WAN play (default port `9999` in examples — change for production).
- [ ] **Lobby** waits for all players to be ready before starting.
- [ ] **Timeouts** handle unresponsive peers gracefully.

### Quick verification commands

**Check that a server is listening on port 9999 (Windows PowerShell):**

```powershell
netstat -an | findstr 9999
```

Expected output (server running):

```
TCP    0.0.0.0:9999    0.0.0.0:0    LISTENING
```

**Check that a client can reach the server:**

```powershell
Test-NetConnection -ComputerName 127.0.0.1 -Port 9999
```

Expected: `TcpTestSucceeded : True`

**Verify headless server starts without errors:**

```powershell
godot --headless --path ~\projects\my-game 2>&1 | Select-Object -First 20
```

Look for `Server started on port 9999` in the output.

**Run two instances locally for integration testing:**

```powershell
# Terminal 1 — server
godot --path . -- --server

# Terminal 2 — client
godot --path . -- --client
```

Confirm both terminals print `Peer connected: <id>` and the client prints `Connected! My ID: <id>`.

## Related Skills

- GDScript fundamentals → [gdscript](../gdscript/SKILL.md)
- Export for dedicated server → [export-and-deployment](../export-and-deployment/SKILL.md)
- Performance optimization → [performance-optimization](../performance-optimization/SKILL.md)
- Scene architecture → [scene-and-nodes](../scene-and-nodes/SKILL.md)
