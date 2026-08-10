# Migration notes: godot-animation-tree-mastery

Incremental upgrade for topics this skill covers. Apply **one hop**, stabilize/test, then next. Never skip hops.

If the project is still on Godot 3.x, use the official [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html) guide first, then continue from 4.0.

## 4.0 → 4.1

Official: [Upgrading to Godot 4.1](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.1.html)

- `AnimationNode._process` requires new `test_only` parameter; `blend_input`/`blend_node` gain optional `test_only`.
- `AnimationNodeStateMachinePlayback.get_travel_path` returns `Array[StringName]`.

## 4.1 → 4.2

Official: [Upgrading to Godot 4.2](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.2.html)

- Many `AnimationPlayer`/`AnimationTree` APIs moved to `AnimationMixer` base.
- `method_call_mode` → `callback_mode_method`; `playback_process_mode`/`process_callback` → `callback_mode_process`.
- `playback_active` → `active` on mixer; `AnimationTree.tree_root` typed as `AnimationRootNode`.
- `AnimationPlayer.seek` gains optional `update_only`.

## 4.2 → 4.3

Official: [Upgrading to Godot 4.3](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.3.html)

- `Animation` interpolate / `track_find_key` gain `backward`/`limit` options.
- `AnimationMixer._post_process_key_value` object arg is `uint64`.
- `Skeleton3D.bone_pose_changed` → `skeleton_updated`; `BoneAttachment3D.on_bone_pose_update` → `on_skeleton_update`.
- Capture mode replaced; see Migrating Animations 4.0→4.3 article for blend/time semantics.

## 4.3 → 4.4

Official: [Upgrading to Godot 4.4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.4.html)

*No skill-relevant breaking changes for this hop.*

## 4.4 → 4.5

Official: [Upgrading to Godot 4.5](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.5.html)

*No skill-relevant breaking changes for this hop.*

## 4.5 → 4.6

Official: [Upgrading to Godot 4.6](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.6.html)

- `AnimationPlayer` `assigned_animation` / `autoplay` / `current_animation` are `StringName` (C# binary break).
- `get_queue` returns `StringName[]`.

## 4.6 → 4.7

Official: [Upgrading to Godot 4.7](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.7.html)

- `Animation.length` uses double metadata (C# impact).
- `AnimationNodeBlendSpace1D/2D.add_blend_point` optional `name` for labeled blend positions.
- `LookAtModifier3D.relative` default is `false` (was `true`) — re-check aim/IK setups beside the tree ([skeleton_ik_lookat.gd](../scripts/animation_tree_mastery_skeleton_ik_lookat.gd)).
