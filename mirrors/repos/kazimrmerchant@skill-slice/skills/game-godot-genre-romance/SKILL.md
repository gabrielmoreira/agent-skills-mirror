---
name: game-godot-genre-romance
version: 1.1.1
description: "Architects Godot 4 romance and dating-sim loops: multi-axis affection (attraction/trust/comfort), signal-driven TimeManager, date events, and route branching. Use when building otome, Persona-style social links, or relationship-centric Godot games. Not for other Godot genres, binary love/hate meters, action/puzzle games without romance systems, or Dialogic dialogue-box rendering."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

## Overview

Romance games are built on the **Affection Economy**—the management of player time and resources to influence NPC attraction, trust, and intimacy. This skill provides a complete architectural blueprint for Godot 4.x (2026 syntax) covering multi-axis affection tracking, signal-driven scheduling, variety-aware date events, route branching, and emotional UI feedback.

**Core Loop:** Meet → Date → Deepen → Branch → Resolve.

## When to Use

Use this skill when building:

- Romance-focused games, dating simulators, or otome titles.
- Social simulations requiring multi-stat affection systems.
- Games with scheduled dates, branching character routes, and nuanced NPC autonomy.
- Persona-style social links or Tokimeki Memorial-style stat-driven romance.

**Trigger keywords:** romance, dating sim, affection system, relationship stats, date events, character routes, love interest, otome, social simulation, social link.

## Do Not Use

- Genres without relationship mechanics.
- Simple binary "love/hate" systems (this skill enforces a multi-axial model).
- Pure action or puzzle games without narrative romance elements.

## Prerequisites

- **Godot 4.x** (2026 stable or later) with GDScript 2.0 typed syntax support.
- Core Godot development patterns — see [godot-master](../godot-master/SKILL.md).
- For dialogue rendering, the **Dialogic** plugin is highly recommended (this skill handles *systems*, not dialogue box rendering).
- Windows host is primary. PowerShell commands are provided where relevant. Project paths use `res://` Godot conventions.

## Procedure

### Step 1: Set Up the Signal-Driven TimeManager (Autoload)

Create a global autoload that broadcasts hour/day changes. **Never** poll schedules in `_process`.

1. In your project, create `time_manager.gd` as an autoload:

```gdscript
# time_manager.gd
extends Node

signal hour_changed(hour: int)
signal day_changed(day: int)

var current_hour: int = 8
var current_day: int = 1

func advance_hour() -> void:
    current_hour += 1
    if current_hour >= 24:
        current_hour = 0
        current_day += 1
        day_changed.emit(current_day)
    hour_changed.emit(current_hour)
```

2. Register as an autoload named `TimeManager` via **Project → Project Settings → Autoload** (or edit `project.godot`):

```ini
[autoload]
TimeManager="*res://autoload/time_manager.gd"
```

### Step 2: Create CharacterProfile Resources

Use custom `Resource` classes for each love interest. **Never** hardcode character data in scripts.

```gdscript
# character_profile.gd
class_name CharacterProfile extends Resource

@export var display_name: String = ""
@export var base_attraction: int = 0
@export var base_trust: int = 0
@export var base_comfort: int = 0
@export var gift_preferences: Dictionary = {}  # item_id -> multiplier
@export var sprite: Texture2D
```

Create `.tres` files per character in `res://resources/characters/`.

### Step 3: Attach AffectionManager as a Global Autoload

Load and integrate [scripts/affection_manager.gd](scripts/affection_manager.gd) — the multi-axis (Attraction / Trust / Comfort) tracking and gift logic component.

```gdscript
# affection_manager.gd
class_name AffectionManager
extends Node

signal milestone_reached(character_id: String, level: int)

var relationship_data: Dictionary = {}

func add_affection(char_id: String, type: String, amount: int) -> void:
    if not relationship_data.has(char_id):
        relationship_data[char_id] = {"attraction": 0, "trust": 0, "comfort": 0}
    relationship_data[char_id][type] = clamp(relationship_data[char_id][type] + amount, -100, 100)
    check_milestones(char_id)

func check_milestones(char_id: String) -> void:
    var stats = relationship_data.get(char_id, {})
    var attraction = stats.get("attraction", 0)
    if attraction >= 50:
        milestone_reached.emit(char_id, 1)

func get_gift_effect(char_id: String, item_id: String) -> int:
    return 10
```

Register as autoload `AffectionManager`.

**Example — giving a gift:**

```gdscript
func give_gift(npc_id: String, gift_id: String) -> void:
    var amt = AffectionManager.get_gift_effect(npc_id, gift_id)
    AffectionManager.add_affection(npc_id, "attraction", amt)
```

### Step 4: Integrate the DateEventSystem

Load [scripts/date_event_system.gd](scripts/date_event_system.gd) — variety-aware dating logic with repetition penalties.

```gdscript
# date_location.gd
class_name DateLocation extends Resource

@export var name: String = "Park"
@export var chemistry_mod: float = 1.0
@export var safety_mod: float = 1.0
@export var success_threshold: float = 50.0

# date_event_system.gd
extends Node

signal date_outcome(result: String, character_id: String)

func run_date(character_id: String, location_res: DateLocation) -> void:
    var score: float = 0.0
    var affection_mgr = get_node_or_null("/root/AffectionManager")
    if affection_mgr:
        var stats = affection_mgr.relationship_data.get(character_id, {"attraction": 0, "trust": 0, "comfort": 0})
        score += stats["attraction"] * location_res.chemistry_mod
        score += stats["trust"] * location_res.safety_mod
    if score > location_res.success_threshold:
        date_outcome.emit("SUCCESS", character_id)
    else:
        date_outcome.emit("FAILURE", character_id)
```

**Example — starting a date:**

```gdscript
func _on_date_button_pressed(npc_id: String) -> void:
    var dm = get_node_or_null("/root/DateEventSystem")
    if dm:
        var location = load("res://scenes/DateLocations/park.tres") as DateLocation
        dm.run_date(npc_id, location)
```

### Step 5: Wire Up the RouteManager

Load [scripts/route_manager.gd](scripts/route_manager.gd) — flag-based route branching and CG gallery persistence.

```gdscript
# route_manager.gd
extends Node

var unlocked_routes: Array[String] = []
var current_route: String = ""
var unlocked_cgs: Array[String] = []
var is_on_route: bool = false

func lock_in_route(char_id: String) -> void:
    if is_on_route:
        push_warning("Player is already locked into a route.")
        return
    current_route = char_id
    is_on_route = true
    unlocked_cgs.append(char_id + "_prologue")
```

### Step 6: Implement NPC Daily Schedules (Signal-Driven)

**Never** use `_process` for NPC schedule checks. Connect to `TimeManager.hour_changed`.

```gdscript
# npc_schedule.gd
class_name NPCSchedule extends Resource
@export var daily_routine: Dictionary = {8: "TownSquare", 12: "Tavern", 18: "Home"}

# npc_controller.gd
extends Node2D

@export var schedule: NPCSchedule

func _ready() -> void:
    var time_mgr = get_node_or_null("/root/TimeManager")
    if time_mgr:
        time_mgr.hour_changed.connect(_on_hour_changed)

func _on_hour_changed(hour: int) -> void:
    if not schedule:
        return
    var dest = schedule.daily_routine.get(hour, "")
    if dest != "":
        _navigate_to(dest)

func _navigate_to(dest: String) -> void:
    print("NPC navigating to destination: ", dest)
```

### Step 7: Add Emotional UI Feedback (Juice)

Load [scripts/romance_patterns.gd](scripts/romance_patterns.gd) — reusable UI helpers for typewriter tweens and heart-burst pulses.

```gdscript
# ui_feedback.gd
extends Control

@export var heart_scene: PackedScene

func play_heart_burst(pos: Vector2) -> void:
    if not heart_scene:
        return
    var heart = heart_scene.instantiate() as Control
    add_child(heart)
    heart.global_position = pos
    var tween = create_tween().set_parallel(true)
    tween.tween_property(heart, "scale", Vector2(1.5, 1.5), 0.5).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
    tween.tween_property(heart, "modulate:a", 0.0, 0.5)
    tween.finished.connect(heart.queue_free)
```

### Step 8: Implement Jealousy Broadcasting via Groups

**Never** hardcode character references for jealousy logic. Use `add_to_group` and `SceneTree.call_group()`.

```gdscript
# player_romance_manager.gd
extends Node

func start_date(npc_name: String) -> void:
    get_tree().call_group("romantic_interests", "on_player_date_started", npc_name)

# npc_jealousy.gd
extends Node

@export var affection: float = 0.0

func _ready() -> void:
    add_to_group("romantic_interests")

func on_player_date_started(dating_name: String) -> void:
    if dating_name != self.name and affection > 30.0:
        var affection_mgr = get_node_or_null("/root/AffectionManager")
        if affection_mgr:
            affection_mgr.add_affection(self.name, "trust", -10)
```

### Step 9: Seasonal / Contextual Dialogue

Inject world state into dialogue using `.format()` and `Resource` mapping. **Never** hardcode dialogue strings — always wrap in `tr()` for localization.

```gdscript
# seasonal_dialogue.gd
class_name SeasonalDialogue extends Resource

enum Season { SPRING, SUMMER, AUTUMN, WINTER }
@export var season_lines: Dictionary = { Season.WINTER: "Stay warm near the fire, {player_name}." }

func get_seasonal_line(season: Season) -> String:
    return tr(season_lines.get(season, "Hello, {player_name}."))
```

### Step 10: Threaded Asset Loading for Large Narrative Files

**Never** parse massive narrative files on the main thread. Use `ResourceLoader.load_threaded_request()` to prevent transition stutters.

```gdscript
func load_narrative_async(path: String) -> void:
    ResourceLoader.load_threaded_request(path)

func _process(_delta: float) -> void:
    var status = ResourceLoader.load_threaded_get_status("res://dialogue/act3.tres")
    if status == ResourceLoader.THREAD_LOAD_LOADED:
        var res = ResourceLoader.load_threaded_get("res://dialogue/act3.tres")
        # use res
```

## NEVER Do (Expert Anti-Patterns)

### Romance & NPC Logic

- **NEVER** create "Vending Machine" romance. Incorporate **NPC Mood**, **Timing**, and **Multi-Stat Thresholds** to ensure characters feel autonomous.
- **NEVER** use binary Affection (Love/Hate). Use a **Multi-Axial Model** (Attraction, Trust, Comfort) for believable psychological depth.
- **NEVER** make stats 100% opaque. Provide **Visible Indicators** (heart UI, blushing text, pulsing hearts) to help players make informed choices.
- **NEVER** use the "Same Date Order" trap. Implement a **Repetition Penalty** (~30%) for visiting the same location twice in a row.
- **NEVER** forget "Missable" Milestones. Ensure meaningful consequences (e.g., missing events due to poor scheduling) to add weight to the experience.
- **NEVER** ignore NPC Autonomy. Allow NPCs to have their own **Schedules** and the ability to **Reject** the player based on low trust or conflicting events.
- **NEVER** use polling (`_process`) for NPC schedule checks. Use a **Signal-Driven TimeManager** (Autoload) to broadcast hour/day changes for performant state updates.
- **NEVER** hardcode character references for jealousy logic. Use **Groups (`add_to_group`)** to broadcast romantic events across the scene for decoupled, autonomous NPC reactions.

### Technical & UI

- **NEVER** use `_process` for typewriter text. Use **Tweens on `visible_ratio`** for frame-independent, smooth reveals.
- **NEVER** parse massive narrative files on the main thread. Use **`ResourceLoader.load_threaded_request()`** to prevent transition stutters.
- **NEVER** use exact float math for affection checks. Use **`is_equal_approx()`** to avoid jitter-based logic failures.
- **NEVER** structure complex dialogue purely in code. Design dialogue trees as **Custom `Resource` classes** to decouple narrative data from logic.
- **NEVER** rely on the global OS clock for timed choices. Use **`SceneTreeTimer`** which respects `Engine.time_scale` and pause states.
- **NEVER** leave invisible controls with `MOUSE_FILTER_STOP`. Set to `IGNORE` or `PASS` on non-opaque layers to avoid blocking dialogue progression.
- **NEVER** hardcode dialogue strings. Map text to **Localization Keys** and retrieve via `tr()` for internationalization.
- **NEVER** use absolute pixel positioning for interfaces. Rely on **Anchoring & Containers** for responsive scaling across devices.
- **NEVER** store sensitive player relationship flags in plain text files. Use **encrypted save files** or checksums to prevent trivial save-editing of affection stats.

## Pitfalls

1. **The "Pervert" Trap**: Forcing the player to always pick the flirtiest option to win. **Fix**: Allow "Trust" and "Friendship" paths to lead to romance eventually.
2. **Opaque Success**: Failing a date without knowing why. **Fix**: Use character dialogue to hint at preferences ("I'm not really a fan of loud places...").
3. **Route Conflict**: Accidentally dating two people with zero consequences. **Fix**: Implement a "Jealousy" or "Conflict Detection" system in the RouteManager using group broadcasting.
4. **Float Jitter**: Affection threshold checks failing intermittently. **Fix**: Always use `is_equal_approx()` for float comparisons.
5. **Save Scumming**: Players editing save files to max affection. **Fix**: Use encrypted save files or checksums.
6. **Invisible UI Blocking**: Dialogue won't advance because an invisible control has `MOUSE_FILTER_STOP`. **Fix**: Set non-interactive layers to `MOUSE_FILTER_IGNORE`.

## Godot-Specific Tips

- **Resources for Characters**: Use `CharacterProfile` resources to store base stats, sprites, and gift preferences.
- **RichTextLabel Animations**: Use custom BBCode for "blushing" text (pulsing pink) or "nervous" text (shaking).
- **Dialogic Integration**: Pair these systems with the **Dialogic** plugin for dialogue box rendering.
- **Typed Arrays**: Use `Array[String]` or `Array[CharacterProfile]` to ensure type safety and better IDE autocomplete.

## Component Reference (scripts/)

| File | Purpose |
|------|---------|
| [scripts/affection_manager.gd](scripts/affection_manager.gd) | Multi-axis (Attraction/Trust/Comfort) tracking and gift logic |
| [scripts/date_event_system.gd](scripts/date_event_system.gd) | Variety-aware dating logic with repetition penalties |
| [scripts/route_manager.gd](scripts/route_manager.gd) | Flag-based route branching and CG gallery persistence |
| [scripts/romance_patterns.gd](scripts/romance_patterns.gd) | Reusable UI helpers: Typewriter tweens and heart-burst pulses |

**When to load each reference file:**
- `affection_manager.gd` — Load during Step 3 (core relationship stat tracking).
- `date_event_system.gd` — Load during Step 4 (date event execution and scoring).
- `route_manager.gd` — Load during Step 5 (route locking and CG persistence).
- `romance_patterns.gd` — Load during Step 7 (UI feedback and tween helpers).

## Skill Phase Map

| Phase | Skills | Purpose |
|-------|--------|---------|
| 1. Stats | `dictionaries`, `resources` | Tracking multi-axis affection, character profiles |
| 2. Timeline | `autoload-architecture`, `signals` | Managing time/days, triggering scheduled dates |
| 3. Narrative | `godot-dialogue-system`, `visual-novel` | Conversational branching and choice consequence |
| 4. Persistence | `godot-save-load-systems` | Saving relationship states, CG gallery, flags |
| 5. Aesthetics | `ui-theming`, `godot-tweening` | Heart-themed UI, blushing effects, emotive icons |

## Verification

- [ ] Run the test suite for `AffectionManager`, `DateEventSystem`, and `RouteManager`.
- [ ] Verify that UI heart bursts appear on affection increase via signal connection.
- [ ] Confirm that schedule signals trigger NPC movement **without** using `_process`.
- [ ] Validate that `ResourceLoader.load_threaded_request()` is used for large narrative assets to prevent frame drops.
- [ ] Ensure all dialogue strings are wrapped in `tr()` for localization.
- [ ] Confirm affection threshold checks use `is_equal_approx()` for float comparisons.
- [ ] Verify invisible UI controls are set to `MOUSE_FILTER_IGNORE`, not `MOUSE_FILTER_STOP`.
- [ ] Confirm save files use encryption or checksums for relationship flags.

**Quick check (PowerShell):**

```powershell
# Verify autoloads are registered in project.godot
Select-String -Path "project.godot" -Pattern "TimeManager|AffectionManager|DateEventSystem|RouteManager"

# Verify no _process polling in NPC schedule scripts
Select-String -Path "scripts\npc_controller.gd" -Pattern "_process" -Quiet
# Expected output: False (no matches)
```

## Related Skills

- [godot-master](../godot-master/SKILL.md) — Core Godot development patterns.
- [godot-genre-visual-novel](../godot-genre-visual-novel/SKILL.md) — Visual novel dialogue systems that complement romance mechanics.
