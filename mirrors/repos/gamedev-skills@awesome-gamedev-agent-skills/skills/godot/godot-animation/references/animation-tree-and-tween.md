# AnimationTree & Tween reference (Godot 4.3+)

Depth companion to `godot-animation`.

## AnimationPlayer essentials

- Author clips in the editor's Animation panel; each clip keys node properties over time.
- Track types: **Property** (most common), **3D Position/Rotation/Scale**, **Method**
  (call a function at a keyframe), **Call** track, **Bezier** (curved value), **Audio**,
  **Animation** (play another AnimationPlayer's clip).
- Playback: `play("name")`, `play_backwards("name")`, `stop()`, `pause()`,
  `seek(time, true)`, `speed_scale`, `queue("next")`.
- Signals: `animation_finished(name)`, `animation_started(name)`,
  `current_animation_changed(name)`.
- Set a clip's loop mode in the panel (None / Linear / Ping-Pong).

A **method track** calls a function on the keyed node — great for spawning a hitbox at the
exact attack frame. A **call track** is similar via the editor's "Functions" track.

## AnimationTree nodes

Set `AnimationTree.tree_root` to one of:

- `AnimationNodeStateMachine` — named states with transitions. Drive via the playback
  object:
  ```gdscript
  var sm: AnimationNodeStateMachinePlayback = tree.get("parameters/playback")
  sm.travel("attack")          # finds a path through transitions to "attack"
  sm.start("idle")             # jump immediately, ignoring transitions
  sm.get_current_node()        # current state name
  ```
  Transitions can be set to **Immediate**, **Sync**, or **At End**, and gated by
  **advance conditions** (booleans you set: `tree.set("parameters/conditions/is_dead", true)`)
  or an advance expression.
- `AnimationNodeBlendSpace1D` / `BlendSpace2D` — place clips at points; set
  `"parameters/<name>/blend_position"` to blend between them (e.g. directional locomotion).
- `AnimationNodeBlendTree` — a graph of blend/add/one-shot nodes with named outputs.
- `AnimationNodeOneShot` — fire a one-off (e.g. a hit reaction) over a base animation:
  ```gdscript
  tree.set("parameters/Shot/request", AnimationNodeOneShot.ONE_SHOT_REQUEST_FIRE)
  ```

Parameter path rule: `"parameters/" + node_name + "/" + property`. The playback for the
root state machine is always `"parameters/playback"`.

## Root motion

For animations that move the character via the skeleton: set
`AnimationTree.root_motion_track` to the motion track, then each physics frame apply
`tree.get_root_motion_position()` (and rotation) to the body. Useful for cinematic,
animation-driven locomotion.

## AnimatedSprite2D (sprite sheets)

```gdscript
@onready var spr: AnimatedSprite2D = $AnimatedSprite2D   # uses a SpriteFrames resource

func face(dir: float) -> void:
    spr.flip_h = dir < 0.0
    spr.play("walk")          # animation names defined in the SpriteFrames editor
    # spr.frame, spr.speed_scale, signal animation_finished, frame_changed
```

`SpriteFrames` holds named animations, each a list of texture frames with an FPS and loop
flag. Alternatively, keyframe `frame` / `region_rect` in an `AnimationPlayer`.

## Tween (create_tween) details

```gdscript
var tw := create_tween()
tw.tween_property(obj, "position", target, 0.5)        # interpolate a property
tw.tween_property(obj, "modulate:a", 0.0, 0.3)         # sub-property
tw.tween_interval(0.2)                                 # wait
tw.tween_callback(func(): print("done"))               # call a function
tw.tween_method(_set_progress, 0.0, 1.0, 1.0)          # call setter over time

tw.set_parallel(true)        # subsequent tweens run together (default is sequential)
tw.set_loops(3)              # repeat (0 = infinite)
tw.set_trans(Tween.TRANS_SINE)
tw.set_ease(Tween.EASE_IN_OUT)
await tw.finished            # signal when complete
tw.kill()                    # cancel early
```

Transitions: `TRANS_LINEAR/SINE/QUINT/QUART/QUAD/EXPO/ELASTIC/CUBIC/CIRC/BOUNCE/BACK/SPRING`.
Eases: `EASE_IN/OUT/IN_OUT/OUT_IN`. Chain methods on the returned `PropertyTweener`:
`.set_delay(0.1)`, `.from(start)`, `.from_current()`, `.as_relative()`.

A tween created with `create_tween()` is bound to the node's tree and is killed if the
node leaves the tree. Use `get_tree().create_tween()` to outlive a specific node.
