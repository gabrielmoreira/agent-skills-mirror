---
name: game-godot-genre-party
version: 1.1.1
description: "Architects Godot 4 local multiplayer party games: MinigameData .tres resources, PartyManager scoring, 2-4 player input mapping, 1v3 asymmetric balance, threaded minigame load/unload, and SubViewport split-screen. Use for Mario Party-style or WarioWare minigame collections. Not for online netcode, single-player campaign structure, or non-Godot engines."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

## Overview

This skill provides a production-grade architecture for building local multiplayer party games in Godot 4.x/2026. It covers the full pipeline: dynamic controller assignment, minigame metadata via `.tres` resources, scene orchestration with threaded preloading, persistent scoring via autoload singleton, asymmetric 1v3 balance, and split-screen rendering with `SubViewport` per player.

Target engine: **Godot 4.x (2026 stable)**. Primary host: **Windows (PowerShell)**. All paths use Windows conventions unless noted.

## When to Use

Use this skill when developing:

- Mario Party-style games with multiple minigames
- WarioWare-style microgame collections
- Local multiplayer games with 2–4 players
- Asymmetric gameplay (1v3 scenarios)
- Games requiring dynamic input mapping for multiple controllers
- Split-screen rendering and viewport management

**Trigger keywords:** `party_game`, `minigame_collection`, `local_multiplayer`, `asymmetric_gameplay`, `split_screen`, `dynamic_input_mapping`

## Prerequisites

- Godot 4.x (2026 stable) installed and on PATH or accessible via project path
- A Godot project initialized at a known path (e.g., `~\projects\party_game`)
- 2–4 physical gamepad controllers for full testing (keyboard fallback possible but not recommended for final QA)
- GDScript familiarity; this skill assumes Godot 4.x API names (`InputMap`, `InputEventJoypadButton`, `SubViewport`, `ResourceLoader.load_threaded_request`)

## Procedure

### 1. Define Minigame Metadata as Resources

Create a reusable `MinigameData` resource class so designers can author minigames as `.tres` files without touching code.

```gdscript
# minigame_data.gd — create this Resource class in the Godot project
class_name MinigameData extends Resource

@export var title: String
@export var scene_path: String
@export var instructions: String
@export var is_1v3: bool = false
@export var thumbnail: Texture2D
@export var time_limit: float = 60.0
```

**When to load:** Use the MinigameData class in this section whenever you need to create or inspect a minigame `.tres` file. Designers create instances in the Godot Inspector: `New Resource → MinigameData`, then save as `res://data/minigames/<name>.tres`.

### 2. Implement the Party Manager Singleton

This autoload persists between minigames to track global state: player roster, scores, round counter, and minigame lifecycle.

Register it in `project.godot` under `[autoload]`:

```
[autoload]
PartyManager="*res://autoload/party_manager.gd"
```

```gdscript
# party_manager.gd — project autoload (persistent scores / rounds)
extends Node

var players: Array[PlayerData] = []
var current_round: int = 1
var max_rounds: int = 10

func start_minigame(minigame: MinigameData) -> void:
    await show_instructions(minigame)
    get_tree().change_scene_to_file(minigame.scene_path)

func show_instructions(minigame: MinigameData) -> void:
    var inst_scene = load("res://scenes/instructions.tscn")
    if inst_scene:
        var inst_instance = inst_scene.instantiate()
        get_tree().root.add_child(inst_instance)
        if inst_instance.has_method("set_metadata"):
            inst_instance.set_metadata(minigame.title, minigame.instructions)
        await inst_instance.finished

func handle_minigame_end(results: Dictionary) -> void:
    var winner_id = results.get("winner_id", -1)
    for player in players:
        if player.player_id == winner_id:
            player.score += 10
    current_round += 1
```

**When to load:** Use the PartyManager autoload snippet in this section for score flow, round progression, or the minigame start/instructions/end lifecycle. For tournament persistence already in this chair, load `scripts/tournament_state.gd`.

### 3. Create the Minigame Base Class

Every minigame inherits from this to ensure a consistent API across the collection.

```gdscript
# minigame_base.gd — project base class every minigame extends
class_name Minigame extends Node

signal game_ended(results: Dictionary)

var active_players: Array[Node] = []

func _ready() -> void:
    setup_players(PartyManager.players)
    start_countdown()

func setup_players(players_data: Array[PlayerData]) -> void:
    for player_data in players_data:
        var player_scene = load("res://scenes/player.tscn")
        if player_scene:
            var player_instance = player_scene.instantiate()
            player_instance.player_id = player_data.player_id
            player_instance.device_id = player_data.device_id
            add_child(player_instance)
            active_players.append(player_instance)

func start_countdown() -> void:
    var timer = Timer.new()
    timer.wait_time = 3.0
    timer.one_shot = true
    add_child(timer)
    timer.start()
    await timer.timeout
    timer.queue_free()

func end_game() -> void:
    var results = {"winner_id": 0, "scores": {}}
    game_ended.emit(results)
    PartyManager.handle_minigame_end(results)
```

**When to load:** Use the Minigame base-class snippet in this section whenever you create a new minigame scene. Each minigame's root node should extend `Minigame`, not `Node` directly.

### 4. Implement Dynamic Input Router

Never hardcode device IDs. Build a runtime input router that maps per-player actions to the correct physical controller.

```gdscript
# party_input_manager.gd — project-side InputMap router (inline)
class_name PartyInputManager extends Node

func register_player_device(player_index: int, device_id: int) -> void:
    var base_actions: Array[String] = ["jump", "dash", "interact"]

    for action in base_actions:
        var player_action: StringName = StringName("p%d_%s" % [player_index, action])

        if not InputMap.has_action(player_action):
            InputMap.add_action(player_action)

        InputMap.action_erase_events(player_action)

        var joy_event := InputEventJoypadButton.new()
        joy_event.device = device_id
        match action:
            "jump":
                joy_event.button_index = JOY_BUTTON_A
            "dash":
                joy_event.button_index = JOY_BUTTON_X
            "interact":
                joy_event.button_index = JOY_BUTTON_B
            _:
                joy_event.button_index = JOY_BUTTON_Y

        InputMap.action_add_event(player_action, joy_event)
```

**When to load:** Use the inline PartyInputManager snippet during lobby/join. For device-ID isolation already in this chair, load `scripts/party_input_router.gd`.

### 5. Implement Player Controller with Dynamic Device Lookup

```gdscript
# player_controller.gd — project-side CharacterBody2D (inline)
extends CharacterBody2D

@export var player_id: int = 0

func _physics_process(delta: float) -> void:
    var device = PartyManager.players[player_id].device_id
    var direction = Input.get_vector(
        "p%s_left" % player_id,
        "p%s_right" % player_id,
        "p%s_up" % player_id,
        "p%s_down" % player_id
    )
    velocity = direction * 300.0
    move_and_slide()
```

**When to load:** Use the inline player snippet for 2D `Input.get_vector` routing. For device-polled 3D already in this chair, load `scripts/minigame_player_controller.gd`.

### 6. Implement Minigame Orchestrator (Scene Switching)

Use deferred transitions to avoid freeing the current scene mid-frame.

```gdscript
# scripts/minigame_orchestrator.gd
class_name MinigameOrchestrator extends Node

var _current_scene: Node

func _ready() -> void:
    _current_scene = get_tree().root.get_child(-1)

func transition_to_minigame(scene_path: String) -> void:
    call_deferred("_deferred_transition", scene_path)

func _deferred_transition(scene_path: String) -> void:
    if _current_scene:
        _current_scene.queue_free()

    var next_scene := ResourceLoader.load(scene_path) as PackedScene
    _current_scene = next_scene.instantiate()
    get_tree().root.add_child(_current_scene)
    get_tree().current_scene = _current_scene
```

### 7. Split-Screen Rendering with SubViewport

For split-screen minigames, use one `SubViewport` per player inside a `GridContainer` or `BoxContainer`. Never set absolute sizes manually.

```
SplitScreenRoot (Control)
└── GridContainer (columns = 2)
    ├── SubViewportContainer (player 0)
    │   └── SubViewport
    │       ├── Camera2D
    │       └── CanvasLayer (per-player HUD)
    ├── SubViewportContainer (player 1)
    │   └── SubViewport
    │       ├── Camera2D
    │       └── CanvasLayer (per-player HUD)
    ├── SubViewportContainer (player 2)
    │   └── ...
    └── SubViewportContainer (player 3)
        └── ...
```

Set `mouse_filter = MOUSE_FILTER_PASS` on each `SubViewportContainer` so overlapping containers do not block input for those beneath.

### 8. Threaded Preloading During Instructions Screen

While the instructions screen is visible, preload the next minigame scene on a background thread to avoid hitches.

```gdscript
# In PartyManager.show_instructions(), before await:
ResourceLoader.load_threaded_request(minigame.scene_path)

# After instructions screen finishes:
var status = ResourceLoader.load_threaded_get_status(minigame.scene_path)
if status == ResourceLoader.THREAD_LOAD_LOADED:
    var packed = ResourceLoader.load_threaded_get(minigame.scene_path)
    get_tree().change_scene_to_packed(packed)
```

### 9. Handle Controller Disconnects

Connect to `Input.joy_connection_changed` in the PartyManager `_ready()`:

```gdscript
func _ready() -> void:
    Input.joy_connection_changed.connect(_on_joy_connection_changed)

func _on_joy_connection_changed(device: int, connected: bool) -> void:
    if not connected:
        get_tree().paused = true
        # Show "Controller disconnected" overlay
```

## HARD RULES — Do Not Violate

### Multiplayer & Input

1. **NEVER** hardcode player inputs to specific device IDs (e.g., `device = 0`). Strictly use `Input.get_connected_joypads()` and dynamic assignment.
2. **NEVER** bake player-specific actions into the project's static Input Map (e.g., `p1_jump`). Strictly use a **Dynamic Input Router** to map actions at runtime.
3. **NEVER** use `Input.is_action_pressed()` for player joining logic. Strictly parse `InputEventJoypadButton` in `_unhandled_input()` to detect new device metadata.
4. **NEVER** allow inconsistent control schemes across minigames. Strictly standardize: **A = Action**, **B = Back**, **Joystick = Move**.
5. **NEVER** assume a connected joypad remains connected. Strictly connect to `Input.joy_connection_changed` to handle disconnects and pause the game.
6. **NEVER** use boolean polling for analog sticks. Strictly use `Input.get_vector()` to handle deadzones and precision.

### User Experience & Feedback

7. **NEVER** use long text-based tutorials. Strictly use a **3-second looping GIF/Animation** + a single-sentence overlay (e.g., "Mash A to fly!").
8. **NEVER** ignore asymmetric balance in 1v3 games. Strictly provide the "One" with unique abilities, higher HP, or increased speed to offset the numerical disadvantage.
9. **NEVER** neglect accessibility and handicap systems. Strictly implement optional modifiers (e.g., speed boosts for lower-skilled players) to maintain social cohesion.
10. **NEVER** leave UI `Control` nodes with `focus_mode = FOCUS_NONE` for gamepad menus. Strictly set to `FOCUS_ALL` with explicit `focus_neighbor` definitions for seamless navigation.

### Rendering & Architecture

11. **NEVER** use heavy scene transitions. Strictly keep minigame assets light and use `ResourceLoader.load_threaded_request()` while the instructions screen is active.
12. **NEVER** draw global `CanvasLayer` UI for individual split-screen players. Strictly use per-viewport `CanvasLayer` children.
13. **NEVER** manually set absolute sizes on `SubViewport` children. Strictly use `GridContainer` or `BoxContainer` for automatic split-screen layout.
14. **NEVER** store tournament state or scores inside minigame scenes. Strictly use a **Persistent Autoload (Singleton)**.
15. **NEVER** use a static `Camera2D` for shared-room games. Strictly use a **dynamic group camera** that zooms/pans to fit all active players in frame.
16. **NEVER** overlap `SubViewportContainer` nodes without setting `mouse_filter` to `MOUSE_FILTER_PASS`. Otherwise, top viewports will block input for those beneath.

## Examples

### Asymmetric Gameplay (1v3) Balance

- **The One**: Powerful, high HP, unique abilities (e.g., a "Boss" character with area attacks).
- **The Many**: Weak individually, must cooperate or use numbers to survive/win.
- Balance target: the "One" wins ~50% of the time. Tune HP, speed, and ability cooldowns until win rates converge.

### Core Game Loop

1. **Lobby**: Players join and select characters/colors.
2. **Meta**: Players move on a board or vote for the next game.
3. **Play**: Short, intense minigame (30s–2m).
4. **Score**: Winners get points/coins.
5. **Repeat**: Cycle continues until a turn limit or score limit is reached.

## Pitfalls

- **Input crosstalk with 4 controllers**: If you skip the Dynamic Input Router and rely on static InputMap entries, multiple controllers will trigger the same actions. Always register per-player actions at runtime with explicit `device` on the `InputEventJoypadButton`.
- **Scene transition null references**: Calling `queue_free()` on the current scene then immediately accessing it causes null dereferences. Use `call_deferred("_deferred_transition", scene_path)` to ensure the free happens after the current frame.
- **Split-screen input blocking**: Overlapping `SubViewportContainer` nodes without `MOUSE_FILTER_PASS` silently blocks input to lower viewports. This is hard to debug because no error is printed.
- **Controller disconnect mid-minigame**: If `joy_connection_changed` is not connected, the game continues running with stale device IDs and the disconnected player's character freezes. Always pause and show a reconnect prompt.
- **Scores lost on scene change**: If scores are stored in a minigame scene node, `queue_free()` destroys them. Always use the `PartyManager` autoload singleton.
- **Instructions screen hitch**: Loading a heavy minigame scene synchronously during the instructions screen causes a visible freeze. Use `ResourceLoader.load_threaded_request()` during the instructions display.
- **Analog stick drift**: Polling `Input.get_axis()` with manual deadzone checks is error-prone. Use `Input.get_vector()` which handles deadzones natively.

## Verification

Run these checks after implementing the skill:

1. **Syntax validation** — In PowerShell, run Godot headless to validate scripts:
   ```powershell
   & "C:\Program Files\Godot\Godot.exe" --headless --path "~\projects\party_game" --check-only --script party_manager.gd
   ```
   Expected: no parse errors.

2. **Null reference during scene transitions** — Run the test suite and transition between 3 minigames. Confirm no `Invalid access to property or key` errors in the output console.

3. **4-controller input crosstalk** — Connect 4 physical controllers. In a minigame, press A on controller 2 only. Confirm only player 2's character responds. Repeat for each controller.

4. **Split-screen rendering** — Launch a 4-player split-screen minigame. Confirm all 4 viewports render independently with no overlap and no input blocking. Resize the window and confirm the `GridContainer` reflows automatically.

5. **Asymmetric balance** — Play 10 rounds of a 1v3 minigame. Confirm the "One" wins approximately 4–6 out of 10 rounds. Adjust HP/speed if skewed.

6. **Controller disconnect** — During active gameplay, unplug one controller. Confirm the game pauses and a reconnect prompt appears. Reconnect and confirm the game resumes.

7. **Persistent scoring** — Complete a full minigame, return to the board, and confirm `PartyManager.players` retains updated scores. Transition to the next minigame and confirm scores persist.

## Related Skills

| Phase | Skill | Purpose |
|-------|-------|---------|
| 1. Input | `input-mapping` | Handling 2–4 local controllers dynamically |
| 2. Scene | `godot-scene-management` | Loading/unloading minigames cleanly |
| 3. Data | `godot-resource-data-patterns` | Defining minigames via Resource files |
| 4. UI | `godot-ui-containers` | Scoreboards, instructions screens |
| 5. Logic | `godot-turn-system` | Managing the "Board Game" phase |
