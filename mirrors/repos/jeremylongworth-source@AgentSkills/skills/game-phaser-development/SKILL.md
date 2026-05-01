---
name: game-phaser-development
description: Build, debug, optimize, and review 2D HTML5 games with Phaser. Use when Codex is asked about Phaser scenes, game config, preload/create/update, sprites, animations, tilemaps, cameras, Arcade Physics, Matter Physics, input, particles, UI overlays, asset loading, scaling, mobile browser support, or publishing Phaser games as HTML5 builds.
license: MIT
---

# Phaser Game Development

## Core Workflow

1. Identify the 2D game genre, target browsers/devices, orientation, resolution strategy, input methods, physics model, asset style, and publishing target.
2. Structure the game around Phaser scenes: boot/preload, main menu, gameplay, UI/HUD, pause, transitions, game over, and results where needed.
3. Use Phaser lifecycle methods deliberately: preload assets, create stable scene objects, update only active simulation, and clean up events/timers/listeners on scene shutdown.
4. Choose physics by gameplay need: Arcade for simple fast AABB/circle motion, Matter for richer bodies/constraints, or no physics for grid/turn/menu games.
5. Keep gameplay rules, data, and tuning values separate from raw sprite setup when the project will grow.
6. Verify in real browsers with responsive scaling, focus loss, audio unlock, mobile touch, fullscreen, and itch.io iframe behavior when publishing.

## Phaser Priorities

- Scenes: use scene keys consistently, avoid conflicting scene registration, and choose start/stop/sleep/wake intentionally.
- Assets: preload with clear keys, use atlases/spritesheets where appropriate, handle load progress and failure states, and keep paths case-correct.
- Physics: tune gravity, body sizes, collision categories, overlap/collider callbacks, velocity, drag, bounce, and world bounds explicitly.
- Cameras: use follow, bounds, zoom, shake, fade, dead zones, and multiple cameras for HUD/game separation where useful.
- Input: support keyboard, pointer/touch, gamepad, focus loss, pause, remapping where needed, and mobile hit target sizing.
- Animation: define animation keys, frame rates, repeat rules, state transitions, and cancellation behavior.
- UI: separate HUD and menus from gameplay scenes when layering, persistence, or pause behavior matters.
- Performance: watch active sprites, particles, physics bodies, tilemap layers, texture sizes, object churn, and expensive per-frame callbacks.

## Architecture Guidance

- Use data-driven configs for levels, enemies, items, waves, tuning, and dialogue where content iteration matters.
- Use composition from `game-3d-development` conceptually for Phaser entities: small controllers/components for health, input, movement, attack, interaction, inventory, and AI.
- Use `game-content-design`, `game-ui-design`, `game-sound-design`, and `game-music-soundtrack-design` for player-facing 2D game polish.
- Use `game-sprite-design` for sprite sheets, animation frames, tile sets, UI icons, VFX sprites, atlases, and sprite import readiness.
- Use `itch-html5-game-publishing` when preparing a Phaser build for itch.io.

## Freshness Rule

Verify current Phaser documentation before making version-sensitive recommendations about Scene lifecycle, Scale Manager, Arcade/Matter Physics APIs, renderer behavior, input plugins, build tooling, or mobile/browser support.

## Deliverable Shape

For Phaser work, provide:

- Target resolution/orientation and scale mode
- Scene map and lifecycle plan
- Physics choice and collision plan
- Asset preload/key strategy
- Input and UI plan
- Performance and browser QA checklist
- Packaging/publishing notes

## References

- Read `references/phaser-game-checklist.md` when building, reviewing, or publishing a Phaser game.
