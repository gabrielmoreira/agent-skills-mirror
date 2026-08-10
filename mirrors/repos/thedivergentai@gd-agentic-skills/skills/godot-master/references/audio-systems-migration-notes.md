# Migration notes: godot-audio-systems

Incremental upgrade for topics this skill covers. Apply **one hop**, stabilize/test, then next. Never skip hops.

If the project is still on Godot 3.x, use the official [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html) guide first, then continue from 4.0.

## 4.0 → 4.1

Official: [Upgrading to Godot 4.1](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.1.html)

*No skill-relevant breaking changes for this hop.*

## 4.1 → 4.2

Official: [Upgrading to Godot 4.2](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.2.html)

*No skill-relevant breaking changes for this hop.*

## 4.2 → 4.3

Official: [Upgrading to Godot 4.3](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.3.html)

- `AudioStreamPlaybackPolyphonic.play_stream()` gains `playback_type` and `bus` optionals — route layered SFX without extra player nodes.

## 4.3 → 4.4

Official: [Upgrading to Godot 4.4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.4.html)

*No skill-relevant breaking changes for this hop.*

## 4.4 → 4.5

Official: [Upgrading to Godot 4.5](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.5.html)

*No skill-relevant breaking changes for this hop.*

## 4.5 → 4.6

Official: [Upgrading to Godot 4.6](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.6.html)

*No skill-relevant breaking changes for this hop.*

## 4.6 → 4.7

Official: [Upgrading to Godot 4.7](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.7.html)

- `AudioEffectSpectrumAnalyzer.tap_back_pos` **removed** — migrate visualizer/equalizer tutorials to current analyzer tap APIs.
- `AudioStreamPlayer.area_mask` default is **`0`** (disabled; was layer 1) — explicitly set `area_mask` to your Area audio layer when using `Area2D`/`Area3D` `audio_bus_override`.
