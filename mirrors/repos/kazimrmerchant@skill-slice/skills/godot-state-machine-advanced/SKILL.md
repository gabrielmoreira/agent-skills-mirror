---
name: godot-state-machine-advanced
description: "Implements Godot 4.7+ hierarchical FSMs and pushdown automata: state stacks, transition_to/push_state, transition guards, concurrent Move+Combat machines, and re-entry flags. Use when Pause/Stun interrupts or layered AI outgrow a flat FSM. Do not use for Has-A orchestrator splits (godot-composition) or AnimationTree BlendSpace locomotion. Never skip exit() before enter() or nest deeper than three levels."
version: 1.0.1
---

## Overview

Production-grade patterns for hierarchical finite state machines (HSM), pushdown automata, context passing, transition validation, and concurrent state orchestration in Godot 4.7+. Covers state stacks, sub-states, transition guards, animation syncing, and data-driven state loading.

## When to Use

- Basic FSMs are insufficient for your character/AI complexity
- Implementing layered AI with interruptive states (Pause, Menu, Stun)
- You need transition validation to prevent illegal state changes
- You need parallel state machines (e.g., movement + combat simultaneously)
- You need data-driven state definitions via `.tres` Resources
- You need re-entry-aware states that distinguish fresh entry from stack-pop resume
- Keywords: state machine, HSM, hierarchical, pushdown automata, state stack, FSM, AI behavior, transition guard, concurrent states

## Prerequisites

- **Godot 4.7+** (stable, 2026-06-18). Consult the [Godot 4.7 migration guide](https://docs.godotengine.org/en/4.7/tutorials/migrating/upgrading_to_godot_4.7.html) when upgrading from 4.6.
- **NEVER** assume 4.6 defaults (stretch mode, audio area_mask, RichTextLabel percent flags) without checking 4.7 migration notes.
- Windows host is primary (PowerShell). All paths use Windows conventions.
- This folder is the skill. Prefer `scripts/` here over any private cache path.
- **MANDATORY**: Read `scripts/hsm_hierarchical_base.gd` before implementing hierarchical AI behaviors. This is the foundational delegator script.

## Available Scripts

Load each reference file from `scripts/` when the corresponding pattern is needed:

| Script | Load When |
|---|---|
| `scripts/hsm_hierarchical_base.gd` | **Always load first.** HSM base delegator for propagating physics/input to sub-states. |
| `scripts/hsm_pushdown_stack.gd` | Implementing interruptive state stacking (Pause/Menu overlays). |
| `scripts/hsm_state_context.gd` | Passing persistent data between states without global singletons. |
| `scripts/hsm_transition_guard.gd` | Preventing illegal state transitions via validation rules. |
| `scripts/hsm_animation_syncer.gd` | Syncing logic state changes to AnimationTree travel logic. |
| `scripts/hsm_concurrent_logic.gd` | Running parallel state machines (e.g., Move + Attack simultaneously). |
| `scripts/hsm_resource_state_loader.gd` | Data-driven state definitions using custom Godot Resources (`.tres`). |
| `scripts/hsm_reentry_aware_state.gd` | Distinguishing resume-from-stack-pop vs fresh entry events. |
| `scripts/hsm_state_history_logger.gd` | Debug ring-buffer for tracking transition history and stack depth. |
| `scripts/hsm_state_timer_component.gd` | Auto-transition for finite-duration states (Stun, Dash, Cooldown). |

## Procedure

### 1. Core HSM Setup

1. Create `hierarchical_state.gd` as the state machine root:

```gdscript
# hierarchical_state.gd
class_name HierarchicalState
extends Node

signal transitioned(from_state: String, to_state: String)

var current_state: Node
var state_stack: Array[Node] = []

func _ready() -> void:
    for child in get_children():
        child.state_machine = self

    if get_child_count() > 0:
        current_state = get_child(0)
        current_state.enter()

func transition_to(state_name: String) -> void:
    if not has_node(state_name):
        return

    var new_state := get_node(state_name)

    if current_state:
        current_state.exit()

    transitioned.emit(current_state.name if current_state else "", state_name)
    current_state = new_state
    current_state.enter()

func push_state(state_name: String) -> void:
    if current_state:
        state_stack.append(current_state)
        current_state.exit()

    transition_to(state_name)

func pop_state() -> void:
    if state_stack.is_empty():
        return

    var previous_state := state_stack.pop_back()
    transition_to(previous_state.name)
```

2. Create the base `State` class — one state per file:

```gdscript
# state.gd
class_name State
extends Node

var state_machine: HierarchicalState

func enter() -> void:
    pass

func exit() -> void:
    pass

func update(delta: float) -> void:
    pass

func physics_update(delta: float) -> void:
    pass

func handle_input(event: InputEvent) -> void:
    pass
```

3. Add state nodes as children of the `HierarchicalState` node in the scene tree. The first child becomes the initial state automatically.

### 2. Pushdown Automaton (Interruptive States)

1. Load `scripts/hsm_pushdown_stack.gd` for the full implementation.
2. Use `push_state("Pause")` when an interruptive state begins — the current state is saved to the stack and `exit()` is called.
3. Use `pop_state()` when the interruptive state ends — the previous state is restored via `transition_to()`.
4. **Every `push_state` MUST have a retirement plan (`pop_state`)** — unbounded pushes cause stack overflow.

### 3. Context Passing (Decoupled Data)

1. Load `scripts/hsm_state_context.gd`.
2. Create a context object holding shared data (health, target, input vector, etc.).
3. Pass the context into `enter()` / `update()` / `physics_update()` instead of reading global singletons.
4. States remain reusable across different characters because they depend on the context interface, not global state.

### 4. Transition Guards

1. Load `scripts/hsm_transition_guard.gd`.
2. Define allowed transitions as a dictionary or adjacency map: `{"Idle": ["Move", "Attack"], "Attack": ["Idle", "Hit"]}`.
3. In `transition_to()`, check the guard before proceeding. Reject illegal transitions silently or with a debug warning.

### 5. Re-entry-Aware States

1. Load `scripts/hsm_reentry_aware_state.gd`.
2. Override `enter()` to accept a `is_reentry: bool` parameter (or check a flag).
3. On fresh entry: play entry SFX/VFX, initialize timers.
4. On re-entry from stack pop: skip entry SFX/VFX, resume from where the state was interrupted.

### 6. Concurrent State Machines

1. Load `scripts/hsm_concurrent_logic.gd`.
2. Run two or more state machines as siblings (e.g., `MovementStateMachine` + `CombatStateMachine`).
3. Each machine processes its own states independently. Coordinate via signals or a shared context object.

### 7. Animation Syncing

1. Load `scripts/hsm_animation_syncer.gd`.
2. Connect the state machine's `transitioned` signal to the syncer.
3. Map state names to AnimationTree travel conditions or animation names.
4. The syncer drives `AnimationTree` travel without hardcoding `play()` calls inside state `enter()` methods.

### 8. Data-Driven State Loading

1. Load `scripts/hsm_resource_state_loader.gd`.
2. Define custom `Resource` classes for state definitions (name, transitions, properties).
3. Save as `.tres` files. The loader instantiates state nodes from resource definitions at runtime.

### 9. State Timer Component

1. Load `scripts/hsm_state_timer_component.gd`.
2. Attach to finite-duration states (Stun, Dash, Cooldown).
3. Configure duration. On timeout, the component triggers `transition_to()` to the next state automatically.

### 10. Debug History Logger

1. Load `scripts/hsm_state_history_logger.gd`.
2. Attach to the state machine node. It maintains a ring-buffer of recent transitions.
3. Query the buffer at runtime or print to console for debugging unexpected state sequences.

## Expert Patterns

### HSM Visualizer (Debug Tool)

Use a `Control` node with `_draw()` to visualize the current state stack/hierarchy in the viewport:

```gdscript
class_name HSMVisualizer extends Control
@export var state_machine: Node

func _draw() -> void:
    var font := ThemeDB.fallback_font
    var pos := Vector2(20, 20)
    draw_string(font, pos, "Active: " + state_machine.current_state.name)
```

### State-Based Audio (Decoupled)

Use a syncer that listens to `transitioned` and maps state names to `AudioStream` resources — never hardcode `audio.play()` inside `enter()`:

```gdscript
class_name StateAudioSyncer extends Node
@export var state_machine: Node
@export var audio_map: Dictionary # { "Jump": preload("jump.wav") }

func _ready() -> void:
    state_machine.transitioned.connect(_on_state_changed)

func _on_state_changed(_old, new_state: String):
    if audio_map.has(new_state):
        $AudioPlayer.stream = audio_map[new_state]
        $AudioPlayer.play()
```

### Transition Cost (Utility AI)

Enable states to evaluate their own weight based on context. The state machine polls sibling costs and transitions to the lowest-cost behavior:

```gdscript
# CostState.gd (Base)
func get_cost(context: Dictionary) -> float:
    return 10.0 # Default weight

# UtilityStateMachine.gd
func _physics_process(_d: float) -> void:
    var best_state: Node = current_state
    var low_cost: float = INF
    for child in get_children():
        var cost = child.get_cost(context)
        if cost < low_cost:
            low_cost = cost
            best_state = child
    if best_state != current_state:
        transition_to(best_state.name)
```

## Pitfalls

### Hierarchy & Delegation

- **NEVER forget to propagate physics/input to children** — In an HSM, failing to call `child.physics_update()` from the parent's `_physics_process` orphans child logic. The child's update never runs.
- **NEVER use deep nesting (>3 levels)** — Extreme hierarchy creates "State Spaghetti." If logic is that complex, consider a Behavior Tree or Utility AI instead.

### Transitions & Lifecycle

- **NEVER call `enter()` without a preceding `exit()`** — Skipping exit logic leaves timers, tweens, or audio loops running in the background, causing resource leaks.
- **NEVER modify state during a transition frame** — Re-entrant `transition_to()` calls inside `enter()` cause recursion crashes. Use `call_deferred("transition_to", state_name)` if immediate sub-transitioning is required.
- **NEVER hardcode state names as strings** — Typos like `transition_to("Idel")` are silent killers. Use `class_name`-based checks OR string constants.

### Architecture & Context

- **NEVER use global singletons for state data** — Coupling states to `GameManager.player_health` makes them non-reusable. Pass a `Context` object instead.
- **NEVER push states indefinitely** — In a Pushdown Automaton, every `push_state` MUST have a retirement plan (`pop_state`) to avoid stack overflow.
- **NEVER assume state re-entry is always a fresh start** — Resuming from a stack pop should often bypass "Entry SFX/VFX"; use re-entry flags.

### Engine Version

- **NEVER assume 4.6 defaults** without checking 4.7 migration notes (stretch mode, audio area_mask, RichTextLabel percent flags).

## Verification

1. **Confirm state propagation works** — add a print in each child state's `physics_update()`:
   ```gdscript
   func physics_update(delta: float) -> void:
       print(name, " physics_update running")
   ```
   Run the scene and verify child state prints appear each physics frame.

2. **Verify push/pop balance** — instrument the stack:
   ```gdscript
   print("Stack depth: ", state_machine.state_stack.size())
   ```
   After a full push/pop cycle, stack depth must return to its original value. If it grows unboundedly, a `pop_state` is missing.

3. **Verify transition guards reject illegal transitions** — attempt a disallowed transition and confirm it is blocked (no state change, no crash, debug warning logged).

4. **Verify no resource leaks on exit** — after 50+ transitions, check for orphaned tweens/timers:
   ```gdscript
   print("Tween count: ", get_tree().get_processed_tweens().size())
   ```
   The count should not grow over time if `exit()` properly cleans up.

5. **Verify re-entry flag** — push a state, pop it, and confirm the resumed state's `enter()` receives `is_reentry = true` and skips entry SFX/VFX.

6. **Verify concurrent machines** — with two state machines active, confirm both `physics_update()` methods run independently each frame without interfering with each other's `current_state`.

## Related Skills

- `godot-characterbody-2d` — character body controller that pairs with this state machine
- `godot-animation-player` — animation playback integration for state-driven animation
- Master Skill: `godot-master`
