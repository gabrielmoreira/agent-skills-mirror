---
name: game-hud-system
version: 1.1.1
description: "Implements Godot 4.3+ screen-space HUDs on CanvasLayer: health bars, score, minimap, damage numbers, toasts, and interaction prompts. Use when building in-game HUD widgets that must stay fixed to the viewport. Not for Control layout and themes (godot-ui) and never parent HUD under world or player nodes without a CanvasLayer."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

# HUD Systems in Godot 4.3+

All examples target Godot 4.3+ with no deprecated APIs. GDScript is shown first, then C#. The code uses Godot 4.3 best-practice APIs (`CanvasItemMaterial` for shader-based masking, `Tween`-based easing with `Tween.EASE_OUT_IN`, new `Signal` syntax).

> **Related skills:** **godot-ui** for Control node layout and themes, **component-system** for HealthComponent integration, **event-bus** for score/notification signals, **inventory-system** for inventory UI patterns, **2d-essentials** for CanvasLayer setup and draw order.

---

## When to Use

Use this skill when you need to create on-screen user interfaces that stay fixed relative to the player's view — health bars, score counters, minimaps, damage numbers, notifications, and interaction prompts. Ideal for Godot 4.3+ projects requiring clean separation between world space and screen space UI.

**Trigger keywords:** HUD, health bar, score display, minimap, damage numbers, floating combat text, notifications, toast, interaction prompt, CanvasLayer, screen-space UI.

---

## Prerequisites

- Godot 4.3 or later (no deprecated APIs).
- A `HealthComponent` class with a `health_changed(current: int, maximum: int)` signal (see **component-system** skill).
- An `EventBus` autoload with a `score_changed(new_score: int)` signal (see **event-bus** skill).
- Basic familiarity with `CanvasLayer`, `Control` nodes, and `Tween` API.

### Hard Rules — Do NOT Violate

1. **Never** embed HUD elements under game world nodes (`World`, `Player`, etc.) without a `CanvasLayer` — they will inherit camera transforms and move with the world.
2. **Never** use deprecated APIs: `TextureProgress` → use `TextureProgressBar`; `AnimationPlayer` for simple value interpolation → use `Tween`.
3. **Security:** Never expose internal game state (raw health values, score) through public `@export` variables on HUD nodes. Bind via signals only to prevent tampering.
4. **Never** use `await get_tree().create_timer()` for UI timing in performance-critical HUDs. Use a dedicated `Timer` node or built-in `Tween` callbacks.
5. **Never** forget to set `mouse_filter = Control.MOUSE_FILTER_IGNORE` on HUD elements that should not block input to the game world.
6. **Always** kill an existing Tween (`_tween.kill()`) before starting a new one so rapid events do not stack animations.
7. **Always** set `ProgressBar.step = 0.0` for smooth tween animation rather than integer snapping.

---

## Procedure

### 1. HUD Architecture — CanvasLayer Setup

A `CanvasLayer` renders children in fixed screen-space independent of any `Camera2D` or `Camera3D` transform. Without it, HUD nodes attached to the scene root move with the camera on pan/zoom.

#### Scene Tree

```
World (Node2D / Node3D)
├── TileMapLayer          ← game world
├── Player (CharacterBody2D)
│   ├── Camera2D
│   ├── HealthComponent
│   └── HurtboxComponent
├── Enemies
└── HUD (CanvasLayer — layer: 1)
    ├── MarginContainer (anchor: Full Rect — edge padding)
    │   ├── TopBar (HBoxContainer)
    │   │   ├── HealthBarPanel (PanelContainer)
    │   │   │   └── HealthBar (TextureProgressBar or ProgressBar)
    │   │   └── ScoreLabel (Label)
    │   └── BottomBar (HBoxContainer)
    │       └── InteractionPrompt (Label — hidden by default)
    ├── DamageNumbersLayer (Node2D — world-space spawning point)
    ├── MinimapContainer (SubViewportContainer)
    │   └── MinimapViewport (SubViewport)
    │       ├── MinimapCamera (Camera2D)
    │       └── MinimapWorld (mirrors or references world nodes)
    └── NotificationStack (VBoxContainer — anchored top-right)
```

**Key rules:**
- Keep all HUD scenes under a single `CanvasLayer`. Do not mix HUD nodes into the game world tree.
- Use `layer = 1` for the main HUD. Use higher values (e.g. `10`) for overlays or pause menus that must appear above the HUD.
- Damage numbers are an exception — they live in a `Node2D` child of the `CanvasLayer` and use `get_viewport().get_canvas_transform()` to convert world positions to screen positions.
- For high-DPI displays, set `ProjectSettings.display/window/stretch/mode = "viewport"` and `stretch_aspect = "keep"` for consistent HUD scaling.

### 2. Health Bar

#### ProgressBar vs TextureProgressBar

| Node | When to use |
|---|---|
| `ProgressBar` | Prototyping, plain-colour bars |
| `TextureProgressBar` | Pixel-art or stylised bars using sprite sheets |

Both expose `min_value`, `max_value`, and `value`. Set `step = 0` so tweening produces smooth animation rather than snapping to integer steps.

#### GDScript — `health_bar.gd`

Attach to a `ProgressBar` or `TextureProgressBar`:

```gdscript
class_name HealthBar
extends ProgressBar

## Reference to the HealthComponent this bar tracks.
## Assign in the Inspector or connect programmatically from the HUD root.
@export var health_component: HealthComponent

## Duration (seconds) for the smooth tween on health change.
@export var tween_duration: float = 0.25

var _tween: Tween


func _ready() -> void:
    step = 0.0  # allow fractional values for smooth animation
    if health_component:
        _connect_component(health_component)


## Call this if the HealthComponent is not available at _ready time
## (e.g. the player spawns after the HUD).
func bind(component: HealthComponent) -> void:
    if health_component:
        health_component.health_changed.disconnect(_on_health_changed)
    health_component = component
    _connect_component(component)


func _connect_component(component: HealthComponent) -> void:
    max_value = component.max_health
    value     = component.current_health
    component.health_changed.connect(_on_health_changed)


func _on_health_changed(current: int, maximum: int) -> void:
    max_value = maximum
    _animate_to(current)


func _animate_to(target_value: float) -> void:
    if _tween:
        _tween.kill()
    _tween = create_tween()
    _tween.set_ease(Tween.EASE_OUT_IN)  # smoother start/end
    _tween.set_trans(Tween.TRANS_QUAD)
    _tween.tween_property(self, "value", target_value, tween_duration)
```

#### C# — `HealthBar.cs`

```csharp
using Godot;

public partial class HealthBar : ProgressBar
{
    [Export] public HealthComponent HealthComponent { get; set; }
    [Export] public float TweenDuration { get; set; } = 0.25f;

    private Tween _tween;

    public override void _Ready()
    {
        Step = 0.0;
        if (HealthComponent != null)
            ConnectComponent(HealthComponent);
    }

    /// <summary>Call this when the HealthComponent is not available at _Ready time.</summary>
    public void Bind(HealthComponent component)
    {
        if (HealthComponent != null)
            HealthComponent.HealthChanged -= OnHealthChanged;
        HealthComponent = component;
        ConnectComponent(component);
    }

    private void ConnectComponent(HealthComponent component)
    {
        MaxValue = component.MaxHealth;
        Value    = component.CurrentHealth;
        component.HealthChanged += OnHealthChanged;
    }

    private void OnHealthChanged(int current, int maximum)
    {
        MaxValue = maximum;
        AnimateTo(current);
    }

    private void AnimateTo(float targetValue)
    {
        _tween?.Kill();
        _tween = CreateTween();
        _tween.SetEase(Tween.EaseType.OutIn);
        _tween.SetTrans(Tween.TransitionType.Quad);
        _tween.TweenProperty(this, "value", targetValue, TweenDuration);
    }
}
```

**TextureProgressBar tip:** Set `fill_mode` to `FILL_LEFT_TO_RIGHT` and assign your bar texture to `texture_progress`. The `value` / `max_value` ratio drives how much of the texture is revealed. For HDR support, enable `CanvasItemMaterial` with `blend_mode = CanvasItemMaterial.BLEND_MODE_PREMULT_ALPHA`.

### 3. Score / Label Display

#### GDScript — `score_display.gd`

Attach to a `Label`:

```gdscript
class_name ScoreDisplay
extends Label

## Duration (seconds) to count from old to new score value.
@export var count_duration: float = 0.4

var _displayed_score: int = 0
var _tween: Tween


func _ready() -> void:
    EventBus.score_changed.connect(_on_score_changed)
    text = "0"


func _on_score_changed(new_score: int) -> void:
    _animate_counter(_displayed_score, new_score)


func _animate_counter(from: int, to: int) -> void:
    if _tween:
        _tween.kill()

    _tween = create_tween()
    _tween.set_ease(Tween.EASE_OUT_IN)
    _tween.set_trans(Tween.TRANS_QUAD)
    # Tween an intermediate float; update the label text each step.
    _tween.tween_method(_set_counter_value, float(from), float(to), count_duration)


func _set_counter_value(value: float) -> void:
    _displayed_score = int(value)
    text = str(_displayed_score)
```

#### C# — `ScoreDisplay.cs`

```csharp
using Godot;

public partial class ScoreDisplay : Label
{
    [Export] public float CountDuration { get; set; } = 0.4f;

    private int _displayedScore = 0;
    private Tween _tween;

    public override void _Ready()
    {
        EventBus.Instance.ScoreChanged += OnScoreChanged;
        Text = "0";
    }

    private void OnScoreChanged(int newScore)
    {
        AnimateCounter(_displayedScore, newScore);
    }

    private void AnimateCounter(int from, int to)
    {
        _tween?.Kill();
        _tween = CreateTween();
        _tween.SetEase(Tween.EaseType.OutIn);
        _tween.SetTrans(Tween.TransitionType.Quad);
        _tween.TweenMethod(
            Callable.From<double>(SetCounterValue),
            (double)from,
            (double)to,
            CountDuration
        );
    }

    private void SetCounterValue(double value)
    {
        _displayedScore = (int)value;
        Text = _displayedScore.ToString();
    }
}
```

#### EventBus Signal Definition

```gdscript
# autoloads/event_bus.gd
signal score_changed(new_score: int)
```

```csharp
// EventBus.cs (partial — score signal)
[Signal] public delegate void ScoreChangedEventHandler(int newScore);
```

Emit from wherever points are awarded:

```gdscript
# Inside a collectible or enemy death handler
EventBus.score_changed.emit(GameState.score)
```

```csharp
// Inside a collectible or enemy death handler
EventBus.Instance.EmitSignal(EventBus.SignalName.ScoreChanged, GameState.Score);
```

### 4. Damage Numbers

Floating "−25" labels that rise and fade above the hit point. Pooled in a HUD-side spawner; world position converted to screen via `get_viewport().get_canvas_transform()`. Uses `CanvasItemMaterial` for fade-out and a `Tween` with `TRANS_SINE` for a natural rise curve. Optional crit colorization before spawn.

> **Load `references/damage-numbers.md`** when implementing damage numbers — it contains the full GDScript and C# `DamageNumber` scene script, the pooled spawner, and the `CanvasItemMaterial` fade configuration.

### 5. Notification System

Toast / notification stack — a `VBoxContainer` anchored top-right with `max_visible` clamping and queue-driven dismissal. New toasts wait for an old one to expire before showing. Uses `Tween` for slide-in/out and a `Timer` node for auto-dismiss (never `await`).

> **Load `references/notifications.md`** when implementing toast notifications — it contains the full GDScript and C# stack implementation with auto-dismiss `Timer` nodes and queue management.

### 6. Minimap

Render a top-down view via a dedicated `SubViewport` + `Camera2D` that follows the player. Display the SubViewport texture in a `TextureRect` inside the HUD. Optional circular mask via a lightweight `CanvasItemMaterial` shader (no heavy `ViewportTexture` processing). Set `render_target_update_mode = SubViewport.UPDATE_ALWAYS` and enable `render_target_v_flip = true` for correct orientation on high-DPI screens.

> **Load `references/minimap.md`** when implementing a minimap — it contains the SubViewport setup, `MinimapCamera` GDScript + C#, and the circular-mask shader code.

### 7. Interaction Prompts

Screen-space "Press [E] to interact" prompt — a `Label` inside the HUD that follows an interactable's screen position each frame. Driven by `body_entered` / `body_exited` on the interactable's `Area2D`. Use `InputMap.action_get_events(name)` to display the correct key for the player's current binding, and cache the result only when the binding changes (not every frame).

> **Load `references/interaction-prompts.md`** when implementing interaction prompts — it contains the full GDScript and C# prompt + `Interactable` `Area2D` pair.

---

## Pitfalls

1. **HUD moves with camera** — Caused by placing HUD nodes under `World` or `Player` instead of a `CanvasLayer`. Always wrap HUD in a `CanvasLayer` with `layer >= 1`.

2. **Health bar snaps instead of animating** — `ProgressBar.step` defaults to `1`. Set `step = 0.0` to allow fractional tween values.

3. **Rapid damage stacks Tweens** — Forgetting to call `_tween.kill()` before creating a new Tween causes overlapping animations and visual jitter. Always kill first.

4. **Score jumps instead of counting** — Using direct assignment (`text = str(new_score)`) instead of `tween_method` produces a hard cut. Always interpolate via `tween_method`.

5. **Damage numbers appear at wrong screen position** — Forgetting to convert world → screen space with `get_viewport().get_canvas_transform()` places them at raw world coordinates.

6. **Damage number pool too small** — Labels recycled before their Tween completes causes numbers to vanish mid-animation. Size the pool to cover the maximum concurrent damage events.

7. **Notifications use `await get_tree().create_timer()`** — This causes hidden frame-rate spikes in performance-critical HUDs. Use a dedicated `Timer` node instead.

8. **Notification stack exceeds `max_visible`** — Forgetting to re-check the queue after each dismissal leaves pending toasts stuck forever. Always re-check queue on dismissal.

9. **Minimap renders upside-down** — Missing `render_target_v_flip = true` on the `SubViewport` causes incorrect orientation on high-DPI screens.

10. **Minimap shows wrong layers** — `Camera2D` cull mask not configured. Set the cull mask so only intended layers are visible.

11. **Interaction prompt shows stale key binding** — Caching `InputMap.action_get_events()` at spawn time. Re-cache only when the binding changes, not every frame, but also not once at spawn.

12. **HUD blocks game clicks** — Forgetting `mouse_filter = Control.MOUSE_FILTER_IGNORE` on non-interactive HUD elements prevents world-space input from reaching the game.

13. **Security: raw game state exposed via `@export`** — Exporting health or score values on HUD nodes allows malicious scripts to tamper with them. All data must flow through signals.

14. **Using deprecated `TextureProgress`** — In Godot 4.3+ the node is `TextureProgressBar`. Using the old name causes load errors.

---

## Verification

Run through this checklist after implementing any HUD component:

- [ ] All HUD nodes are children of a `CanvasLayer` with `layer >= 1` — verify in the scene tree that no HUD node is under `World` or `Player`.
- [ ] `ProgressBar.step` is set to `0.0` — check in the Inspector or via script.
- [ ] Health bar binds to `HealthComponent.health_changed` signal — does not poll in `_process`.
- [ ] Tween is killed (`_tween.kill()`) before starting a new one — rapid damage does not stack animations.
- [ ] Score counter uses `tween_method` to interpolate the displayed integer — not a jump cut.
- [ ] Damage number positions are converted from world space to screen space using `get_viewport().get_canvas_transform()`.
- [ ] Damage number pool size is large enough that labels are not recycled before their tween completes.
- [ ] Notification stack enforces `max_visible` and re-checks the queue after each dismissal.
- [ ] Toast auto-dismiss uses a `Timer` node — not `await get_tree().create_timer()`.
- [ ] `SubViewport` for minimap has `render_target_update_mode = SubViewport.UPDATE_ALWAYS`.
- [ ] Minimap `Camera2D` zoom and cull mask are configured so only the intended layers are visible.
- [ ] Interaction prompt converts the interactable's world position each frame — not cached at spawn time.
- [ ] `InputMap.action_get_events()` is used to display the correct key for the player's current binding.
- [ ] HUD nodes that do not need input set `mouse_filter = Control.MOUSE_FILTER_IGNORE` to avoid blocking game clicks.
- [ ] No exported variables expose mutable game state; all data flows through signals for security compliance.

### Quick Smoke Test (GDScript console or `_ready`)

```gdscript
# Temporarily add to HUD root _ready() to verify signal wiring
func _ready() -> void:
    print("HUD CanvasLayer layer: ", get_parent().layer if get_parent() is CanvasLayer else "NOT CanvasLayer")
    # Emit a test score change — the ScoreDisplay should count up smoothly
    EventBus.score_changed.emit(100)
    # Emit a test health change — the HealthBar should tween smoothly
    # (requires health_component to be assigned)
```

---

## Related Skills

- **godot-ui** — Control node layout and theming
- **component-system** — HealthComponent integration
- **event-bus** — Score/notification signals
- **inventory-system** — Inventory UI patterns
- **2d-essentials** — CanvasLayer setup and draw order
