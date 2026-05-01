# Phaser Game Checklist

Use this checklist for Phaser 2D HTML5 games.

## Scenes And Lifecycle

- Scene keys are unique and scene transitions use start, stop, sleep, wake, pause, and resume intentionally.
- Assets are loaded in preload or a dedicated loading scene with progress/error handling.
- Timers, tweens, events, input handlers, and physics callbacks are cleaned up on scene shutdown where needed.
- HUD, pause, modal, and gameplay scenes have clear layering and persistence rules.

## Physics And Gameplay

- Arcade, Matter, or no physics is chosen based on actual gameplay needs.
- Body sizes, offsets, collision categories, overlaps, colliders, world bounds, and gravity are tuned.
- Animation state changes are explicit and do not fight physics or input.
- Data and tuning values are separated from sprite construction when content will grow.

## Input And UI

- Keyboard, pointer/touch, and gamepad flows are tested where supported.
- Mobile hit targets, orientation, scale mode, and safe areas are considered.
- Focus loss, pause, audio unlock, fullscreen, and browser back/refresh behavior are handled.
- HUD text and UI fit the target resolution and scale cleanly.

## Performance And Publishing

- Sprite count, particles, tilemap layers, physics bodies, tweens, and per-frame allocations are checked.
- Texture atlases and spritesheets are used when they reduce load overhead and draw churn.
- Asset paths are relative and case-correct.
- Production build runs from a static server and uploaded host preview.
