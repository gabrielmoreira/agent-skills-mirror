---
name: godot-dialogue-system
description: "Owns Godot 4.x branching conversation graphs: DialogueLine and DialogueChoice Resources, a DialogueManager AutoLoad, typewriter Tweens, tr() localization, and DisplayServer TTS. Trigger on DialogueGraph, portraits, flag-gated choices, GraphEdit authoring, or voice lines. Do not use for user:// save slots (godot-save-load-systems) or Control HUD layout (godot-ui). Never hardcode spoken text in GDScript or block with OS.delay_msec."
version: 1.0.1
---

# Dialogue System

Expert guidance for building flexible, data-driven dialogue systems in Godot 4.x. Covers Resource-based dialogue graphs, branching choices, conditional logic, typewriter effects, localization, voice acting, and visual authoring tools.

## When to Use

Activate this skill when the user is working on any of the following in a Godot 4.x project:

- Branching dialogue trees or conversation graphs (`DialogueLine`, `DialogueChoice`, `DialogueGraph`)
- A centralized `DialogueManager` AutoLoad for traversing dialogue state
- Typewriter / typebox text reveal effects
- Conditional dialogue gated by quest flags or player stats
- Character portraits, expressions, and entry animations
- Localization of dialogue text (CSV translation keys, `tr()`)
- Voice acting integration (pre-recorded audio or TTS via `DisplayServer`)
- Visual dialogue graph editors using `GraphEdit` / `GraphNode`
- Dialogue analytics or choice logging

Trigger keywords: `DialogueLine`, `DialogueChoice`, `DialogueGraph`, `dialogue_manager`, `typewriter_effect`, `branching_dialogue`, `dialogue_flags`, `localization`, `voice_acting`.

## Prerequisites

- Godot 4.x project (scripts target Godot 4.x APIs; Godot 4.7+ noted where relevant).
- An AutoLoad named `DialogueManager` registered in **Project Settings → Autoload**.
- `RichTextLabel` available for BBCode-formatted dialogue text.
- Optional: CSV translation files imported via Godot's translation system.
- Optional: `DisplayServer` TTS support for voice/lipsync (platform-dependent).

## Procedure

### 1. Define dialogue data resources

Create two Resource scripts to serialize dialogue lines and choices.

```gdscript
# dialogue_line.gd
class_name DialogueLine
extends Resource

@export var speaker: String
@export_multiline var text: String
@export var portrait: Texture2D
@export var choices: Array[DialogueChoice] = []
@export var conditions: Array[String] = []  # Quest flags, etc.
@export var next_line_id: String = ""
```

```gdscript
# dialogue_choice.gd
class_name DialogueChoice
extends Resource

@export var choice_text: String
@export var next_line_id: String
@export var conditions: Array[String] = []
@export var effects: Array[String] = []  # e.g. "set_flag:met_npc", "give_item:potion"
```

Create a graph container:

```gdscript
# dialogue_graph.gd
class_name DialogueGraph
extends Resource

@export var lines: Dictionary = {}  # line_id → DialogueLine

func _init() -> void:
    lines["start"] = create_line("Hero", "Hello!")
    lines["response"] = create_line("NPC", "Greetings, traveler!")

func create_line(speaker: String, text: String) -> DialogueLine:
    var line := DialogueLine.new()
    line.speaker = speaker
    line.text = text
    return line
```

### 2. Implement the DialogueManager AutoLoad

> **MANDATORY**: Read `scripts/dialogue_manager_singleton.gd` before implementing the central orchestrator. It contains the canonical signal set and traversal logic.

```gdscript
# dialogue_manager.gd (AutoLoad: DialogueManager)
extends Node

signal dialogue_started
signal dialogue_ended
signal line_displayed(line: DialogueLine)
signal choice_selected(choice: DialogueChoice)

var dialogues: Dictionary = {}
var flags: Dictionary = {}

func load_dialogue(path: String) -> void:
    var data := load(path)
    dialogues[path] = data

func start_dialogue(dialogue_id: String, start_line: String = "start") -> void:
    dialogue_started.emit()
    display_line(dialogue_id, start_line)

func display_line(dialogue_id: String, line_id: String) -> void:
    var line: DialogueLine = dialogues[dialogue_id].lines[line_id]

    if not check_conditions(line.conditions):
        if line.next_line_id:
            display_line(dialogue_id, line.next_line_id)
        else:
            end_dialogue()
        return

    line_displayed.emit(line)

    if line.choices.is_empty() and line.next_line_id:
        await get_tree().create_timer(0.1).timeout
    elif line.choices.is_empty():
        end_dialogue()

func select_choice(dialogue_id: String, choice: DialogueChoice) -> void:
    choice_selected.emit(choice)
    for effect in choice.effects:
        apply_effect(effect)
    if choice.next_line_id:
        display_line(dialogue_id, choice.next_line_id)
    else:
        end_dialogue()

func end_dialogue() -> void:
    dialogue_ended.emit()

func check_conditions(conditions: Array[String]) -> bool:
    for condition in conditions:
        if not flags.get(condition, false):
            return false
    return true

func apply_effect(effect: String) -> void:
    var parts := effect.split(":")
    match parts[0]:
        "set_flag":
            flags[parts[1]] = true
        "give_item":
            pass  # Integrate with inventory system
```

### 3. Build the dialogue UI controller

> **MANDATORY**: Read `scripts/dialogue_ui_controller.gd` before wiring UI. It maps dialogue data to labels, portraits, and dynamic choice buttons.

```gdscript
# dialogue_ui.gd
extends Control

@onready var speaker_label := $Panel/Speaker
@onready var text_label := $Panel/Text
@onready var portrait := $Panel/Portrait
@onready var choices_container := $Panel/Choices

var current_dialogue: String
var current_line: DialogueLine

func _ready() -> void:
    DialogueManager.line_displayed.connect(_on_line_displayed)
    DialogueManager.dialogue_ended.connect(_on_dialogue_ended)
    visible = false

func _on_line_displayed(line: DialogueLine) -> void:
    visible = true
    current_line = line
    speaker_label.text = line.speaker
    portrait.texture = line.portrait

    # Typewriter effect
    text_label.text = ""
    for char in line.text:
        text_label.text += char
        await get_tree().create_timer(0.03).timeout

    if line.choices.is_empty():
        pass  # Wait for input to continue
    else:
        show_choices(line.choices)

func show_choices(choices: Array[DialogueChoice]) -> void:
    for child in choices_container.get_children():
        child.queue_free()
    for choice in choices:
        if not DialogueManager.check_conditions(choice.conditions):
            continue
        var button := Button.new()
        button.text = choice.choice_text
        button.pressed.connect(func(): _on_choice_selected(choice))
        choices_container.add_child(button)

func _on_choice_selected(choice: DialogueChoice) -> void:
    DialogueManager.select_choice(current_dialogue, choice)

func _on_dialogue_ended() -> void:
    visible = false
```

### 4. Add the typewriter / typebox effect

> **MANDATORY**: Read `scripts/typebox_effect.gd` before implementing text reveal. It uses Godot's built-in `Tween` for smooth, non-blocking character reveal.

Key rules:
- Use `Tween` or `create_timer()` — **NEVER** `OS.delay_msec()`.
- Always provide a skip option (click to finish the line instantly).

### 5. Wire NPC interaction

```gdscript
# npc.gd
extends CharacterBody2D

@export var dialogue_path: String = "res://dialogues/npc_1.tres"
@export var start_line: String = "start"

func interact() -> void:
    DialogueManager.start_dialogue(dialogue_path, start_line)
```

### 6. Add conditional branching validation

> **MANDATORY**: Read `scripts/branching_condition_validator.gd` before implementing flag/stat-gated choices. It evaluates player stats or global flags to toggle choice availability.

### 7. Add portraits and expressions

> **MANDATORY**: Read `scripts/dialogue_portrait_manager.gd` before implementing portrait swapping. It manages character expressions and entry animations.

### 8. Trigger external game events from dialogue

> **MANDATORY**: Read `scripts/dialogue_event_bridge.gd` before wiring dialogue nodes to quests, cutscenes, or inventory. It is the bridge node for triggering external events from conversation nodes.

### 9. Localization

Use Godot's built-in CSV import for multi-language dialogue:

```csv
# dialogue_en.csv
dialogue_id,speaker,text
npc_1_start,Hero,"Hello!"
npc_1_response,NPC,"Greetings!"
```

```gdscript
func get_localized_line(line_id: String) -> String:
    return tr(line_id)
```

> **MANDATORY**: Read `scripts/localized_dialogue_resource.gd` before implementing multi-language support. It uses translation keys instead of hardcoded strings.

### 10. Voice acting integration

Pre-recorded audio:

```gdscript
@onready var voice_player := $AudioStreamPlayer

func play_voice_line(line_id: String) -> void:
    var audio := load("res://voice/" + line_id + ".mp3")
    if audio:
        voice_player.stream = audio
        voice_player.play()
```

TTS + lipsync via `DisplayServer`:

```gdscript
# dialogue_lipsync.gd
func start_speaking(text: String) -> void:
    var cb := Callable(self, "_on_tts_boundary")
    DisplayServer.tts_set_utterance_callback(DisplayServer.TTS_UTTERANCE_BOUNDARY, cb)
    var voices := DisplayServer.tts_get_voices_for_language("en")
    DisplayServer.tts_speak(text, voices[0])

func _on_tts_boundary(char_idx: int, _id: int) -> void:
    _update_mouth_shape(char_idx)
```

### 11. Advanced: visual dialogue graph editor

> **MANDATORY**: Read `scripts/dialogue_engine.gd` before implementing graph-based dialogue with BBCode signal tags. It parses `[trigger:event_id]` tags from text and loads external JSON dialogue graphs.

```gdscript
@tool
class_name DialogueGraphEditor extends GraphEdit

func link_nodes(from: StringName, from_port: int, to: StringName, to_port: int) -> void:
    var err := connect_node(from, from_port, to, to_port)
    if err == OK:
        print_rich("[color=green]Branch linked.[/color]")
```

### 12. Advanced: dialogue analytics logger

```gdscript
# dialogue_stat_logger.gd
class_name DialogueStatLogger extends Logger

func _log_message(msg: String, is_error: bool) -> void:
    if not is_error and msg.begins_with("[CHOICE]"):
        _record_analytics(msg)

static func initialize() -> void:
    OS.add_logger(DialogueStatLogger.new())
```

## Available Scripts

> **MANDATORY**: Read the appropriate script before implementing the corresponding pattern.

| Script | Purpose |
|---|---|
| `scripts/dialogue_resource.gd` | Data-driven conversation tree container using Resources for modular, branching narrative paths. |
| `scripts/dialogue_node_data.gd` | Serialized data structure for a single line of dialogue, including speaker metadata and portraits. |
| `scripts/dialogue_option_data.gd` | Interactive player choice definition with branching logic and scriptable availability conditions. |
| `scripts/dialogue_manager_singleton.gd` | Centralized AutoLoad orchestrator for traversing dialogue trees and broadcasting state signals. |
| `scripts/dialogue_ui_controller.gd` | Reactive UI bridge that maps dialogue data to visual labels and dynamic choice buttons. |
| `scripts/typebox_effect.gd` | Character-by-character text reveal effect using Godot's built-in Tweens. |
| `scripts/dialogue_event_bridge.gd` | Bridge node for triggering external game events (e.g. starting a quest) from conversation nodes. |
| `scripts/branching_condition_validator.gd` | Logic for evaluating player stats or global flags to toggle dialogue choices. |
| `scripts/localized_dialogue_resource.gd` | Multi-language conversation text via translation keys. |
| `scripts/dialogue_portrait_manager.gd` | Visual controller for managing character expressions and entry animations during dialogue. |
| `scripts/dialogue_engine.gd` | Graph-based dialogue with BBCode signal tags. Parses `[trigger:event_id]` tags, fires signals, loads external JSON dialogue graphs. |
| `scripts/dialogue_manager.gd` | Data-driven dialogue engine with branching, variable storage, and conditional choices. |

## Pitfalls

### NEVER do in dialogue systems

- **NEVER hardcode dialogue text directly in GDScript files** — Makes translation impossible. Store text in Resources or external JSON/CSV files.
- **NEVER display choices the player hasn't met criteria for** — Hidden choices should stay hidden unless intentionally "grayed out" to show a missed path.
- **NEVER use loose strings for node transitions without validation** — Typos in `next_node_id` will crash the dialogue mid-conversation. Use `assert()` or a central ID registry.
- **NEVER force a typewriter effect without a "Skip" option** — Always allow clicking to finish the line instantly.
- **NEVER store current dialogue state inside a UI node** — If the UI is closed or the scene changes, the player loses their place. Use an AutoLoad `DialogueManager`.
- **NEVER use `get_node()` to find dialogue UI from an NPC script** — Use signals like `DialogueManager.start_dialogue(res)` to maintain decoupled architecture.
- **NEVER use complex regex for simple text tags** — Godot's `RichTextLabel` supports BBCode tags natively. Use `[b]`, `[i]`, `[url]` for formatting.
- **NEVER perform save/load operations inside a dialogue node** — Conversation nodes should be pure data. Delegate persistence to a dedicated `SaveSystem`.
- **NEVER block the main thread for text reveal timing** — Never use `OS.delay_msec()`. Use `create_timer()` or `Tween` to maintain smooth 60fps.
- **NEVER hardcode portrait paths** — Assign textures directly to the `DialogueNode` resource in the inspector or use a central `PortraitDatabase`.

### Godot 4.7 note

- `RichTextLabel` `add_image` / `update_image` use `width_unit` / `height_unit` (`ImageUnit`) — update portrait and inline image helpers accordingly.

## Verification

1. **AutoLoad registered**: In **Project Settings → Autoload**, confirm `DialogueManager` is present and enabled.

2. **Resource compiles**: Open each `.gd` resource script in the Godot editor — no parse errors.

3. **Dialogue loads at runtime**: Run the project and trigger an NPC interaction. Confirm `dialogue_started` fires and the first line displays.

4. **Branching works**: Select a choice and confirm `choice_selected` fires and the correct `next_line_id` is reached.

5. **Conditions gate correctly**: Set a required flag to `false`, confirm the gated line/choice is skipped or hidden. Set it to `true`, confirm it appears.

6. **Typewriter is skippable**: Click during text reveal — the full line should appear instantly without blocking.

7. **No main-thread blocking**: During dialogue, confirm the game maintains smooth framerate (no `OS.delay_msec()` calls).

8. **Localization**: Switch locale via `TranslationServer.set_locale("en")` / `set_locale("fr")` and confirm `tr(line_id)` returns the correct translated string.

9. **No hardcoded strings**: Search the codebase for inline dialogue text in `.gd` files (excluding test scripts). All conversational text should live in Resources or CSV files.

10. **Signal decoupling**: Confirm NPC scripts call `DialogueManager.start_dialogue(...)` and never use `get_node()` to reach the UI directly.

## Related skills

- Master Skill: `godot-master`
