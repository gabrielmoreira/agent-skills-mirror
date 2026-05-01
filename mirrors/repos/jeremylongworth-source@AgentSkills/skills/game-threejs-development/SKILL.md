---
name: game-threejs-development
description: Build, debug, optimize, and review 3D browser games with Three.js. Use when Codex is asked about Three.js scenes, cameras, render loops, WebGLRenderer, asset loading, GLTF/GLB, AnimationMixer, controls, raycasting, shaders, postprocessing, physics integrations, responsive canvas sizing, WebGL performance, mobile browser support, or publishing Three.js games as HTML5 builds.
license: MIT
---

# Three.js Game Development

## Core Workflow

1. Identify the game genre, target browsers/devices, input methods, camera style, asset format, physics needs, and publishing target.
2. Structure the app around a clear game loop: input sampling, fixed or semi-fixed simulation, animation mixers, world update, camera update, render, and cleanup.
3. Keep Three.js scene concerns separate from gameplay state where practical. Avoid hiding game rules inside mesh traversal or material callbacks.
4. Use the scene graph deliberately: name important objects, group related transforms, avoid excessive per-frame searches, and dispose geometries/materials/textures when removed.
5. Load assets through explicit loaders and loading states. Prefer GLB/GLTF for 3D assets, texture compression where appropriate, and predictable relative paths for HTML5 hosting.
6. Verify with browser screenshots and canvas checks across desktop and mobile viewports. Confirm the canvas is nonblank, framed correctly, interactive, and performant.

## Three.js Priorities

- Renderer: configure pixel ratio, antialiasing, tone mapping, color management, shadows, and resize behavior intentionally.
- Camera: define FOV, near/far planes, aspect updates, follow behavior, collision/occlusion rules, and motion-sickness risks.
- Assets: optimize meshes, texture size, material count, draw calls, skeleton count, animation clips, and loading order.
- Controls and input: support keyboard, mouse, touch, gamepad, pointer lock, focus loss, pause, and browser gesture requirements for audio/fullscreen.
- Physics: use a proven browser physics library when collision or rigid bodies matter; keep visual transforms and physics bodies synchronized.
- Picking: use raycasting carefully, with layers or acceleration structures when needed.
- Performance: monitor frame time, shader cost, draw calls, memory, texture uploads, garbage collection, and device pixel ratio.
- Lifecycle: cancel animation loops, remove listeners, dispose GPU resources, and handle route/page teardown in app frameworks.

## Architecture Guidance

- Prefer small systems/components for input, player control, camera, physics, asset loading, audio, UI bridge, and rendering effects.
- Keep reusable game rules independent of Three.js classes unless visual objects are the actual source of truth.
- Use composition from `game-3d-development` when entities need mix-and-match capabilities.
- Use `game-3d-asset-design` and `game-3d-model-design` when creating or reviewing GLB/GLTF assets.
- Use `itch-html5-game-publishing` when preparing a browser build for itch.io.

## Freshness Rule

Verify current Three.js documentation and relevant browser/WebGL guidance before making version-sensitive recommendations about loaders, color management, WebGPU/WebGLRenderer behavior, examples modules, postprocessing, controls, or build/import patterns.

## Deliverable Shape

For Three.js work, provide:

- Target browsers/devices and controls
- Scene/camera/render-loop structure
- Asset and loading plan
- Physics/collision plan if needed
- Performance budget and debug hooks
- Browser/mobile QA checklist
- Packaging/publishing notes

## References

- Read `references/threejs-game-checklist.md` when building, reviewing, or publishing a Three.js game.
