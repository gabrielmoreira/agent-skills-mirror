---
name: webcpu-easel
description: >
  Precise, source-grounded guide for AI agents building CPU-rendered Canvas2D 3D scenes with @xsyetopz/easel (EASEL.js), including browser, Deno, Bun/Node bundler setup, renderer setup, scene graph, cameras, geometry buffers, materials, textures, lighting, fog, animation, picking, voxel worlds, performance, and migration from THREE.js/CreateJS/WebGPU assumptions. Use when working with @xsyetopz/easel, easeljs.org, EASEL.js CPU rasterizer, software rendering, Canvas2D 3D, retro 3D, Deno browser apps, or browser CPU graphics.
user-invocable: true
---
# WebCPU EASEL.js

Use this skill for `@xsyetopz/easel` EASEL.js: a CPU software renderer and Canvas2D rasterizer with a THREE.js-style scene graph API.

This skill is written for LLMs and AI coding agents. Treat it as an execution contract, not background prose. Prefer verified references over memory.

## Agent Grounding Protocol

Before writing code:

1. Identify runtime: browser, Deno-managed browser, Bun/Node bundler, React, Astro, or existing app.
2. Identify import mode: npm package, JSR package, Deno import map, or existing project alias.
3. Identify installed `@xsyetopz/easel` version. If absent, use bundled baseline `@xsyetopz/easel@0.5.0`.
4. Pick one task recipe from `REFERENCE.md`.
5. Verify symbols in `reference/api-index.md` and shapes in `reference/class-signatures.md`.
6. If a needed API is absent, inspect installed declarations under `node_modules/@xsyetopz/easel/dist/` or Deno cache/types.
7. If still absent, state `UNKNOWN` with exact missing symbol or behavior. Do not invent.

## Agent Anti-Rules

Do not work around these rules.

- Do not use WebGL, WebGPU, GPU buffers, shaders, or `navigator.gpu` for EASEL.js rendering.
- Do not use CreateJS EaselJS APIs such as `createjs.Stage`, `Ticker`, `Bitmap`, or display-list code.
- Do not use THREE.js APIs unless translating from THREE.js into verified EASEL.js equivalents.
- Do not invent constructor options, material properties, loader callbacks, or renderer methods.
- Do not import from package subpaths unless `reference/module-imports.md` or installed package exports prove the path.
- Do not claim server-side/headless Deno rendering unless a DOM/canvas-compatible environment is supplied.
- Do not skip disposal when replacing chunk meshes, textures, geometries, or renderers.

## Runtime Decision Table

| Runtime/task             | Use first                             | Verify                               |
| ------------------------ | ------------------------------------- | ------------------------------------ |
| npm/Bun/browser setup    | `reference/setup.md`                  | `EASEL.REVISION`                     |
| Deno-managed browser app | `reference/deno-runtime.md`           | `deno check`, browser canvas         |
| Imports/install          | `reference/module-imports.md`         | package version and import mode      |
| Renderer loop            | `reference/renderer-framebuffer.md`   | `renderer.render(scene, camera)`     |
| Manual geometry          | `reference/geometry-manual.md`        | positions, normals, UVs, indices     |
| Texture atlas            | `reference/texture-atlas-pipeline.md` | `DataTexture`, `needsUpdate`         |
| Picking/input            | `reference/input-picking.md`          | canvas pixel scaling                 |
| Voxel chunks             | `reference/chunked-voxel-terrain.md`  | chunk replacement disposal           |
| Animation                | `reference/animation.md`              | `Animator`, `AnimationClip`, `Track` |
| Performance              | `reference/performance.md`            | CPU budget and object reuse          |

## Capability Map

| Area         | Verified EASEL.js surface                                                                                              |
| ------------ | ---------------------------------------------------------------------------------------------------------------------- |
| Renderer     | `Renderer`, `RenderTimings`, `setSize`, `setPixelRatio`, `setClearColor`, `render`, `dispose`                          |
| Scene graph  | `Scene`, `Node`, `Group`, `Mesh`, `Line`, `LineSegments`, `Points`, `Sprite`, `Bone`, `SkinnedMesh`                    |
| Cameras      | `PerspectiveCamera`, `OrthographicCamera`, `Camera` base via concrete subclasses                                       |
| Geometry     | `Geometry`, `Attribute`, built-in primitives, manual buffers: positions, normals, UVs, colors, index                   |
| Materials    | `Material`, `BasicMaterial`, `LambertMaterial`, `ToonMaterial`, `LineMaterial`, `PointsMaterial`, `DashedLineMaterial` |
| Textures     | `Texture`, `DataTexture`, `CanvasTexture`, `FramebufferTexture`, `VideoTexture`, loaders                               |
| Lighting/fog | `AmbientLight`, `DirectionalLight`, `PointLight`, `SpotLight`, `HemisphereLight`, `Fog`                                |
| Animation    | `AnimationClip`, `Animator`, `Track`, typed tracks, `LoopOnce`, `LoopRepeat`, `LoopPingPong`                           |
| Picking      | `Raycaster`, custom ray/voxel DDA recipes                                                                              |
| Pipeline     | `SceneTraversal`, `FogCuller`, `PainterSort`, `LightBaker`, `Rasterizer`, `FramebufferUpload`                          |

## Task Recipe Index

- Setup/imports: `reference/setup.md`, `reference/module-imports.md`, `reference/deno-runtime.md`
- Renderer/canvas loop: `reference/renderer-framebuffer.md`, `reference/render-loop-recipes.md`
- Scene graph/transforms: `reference/core-concepts.md`
- Cameras/controls: `reference/cameras-controls.md`
- Built-in geometry: `reference/geometry-builtins.md`
- Manual geometry: `reference/geometry-manual.md`
- Materials/shading/side/opacity: `reference/materials.md`
- Textures/atlases: `reference/textures-assets.md`, `reference/texture-atlas-pipeline.md`
- Lights/fog: `reference/lights-fog.md`
- Animation: `reference/animation.md`, `reference/hierarchical-voxel-rigging.md`
- Picking/input: `reference/input-picking.md`, `reference/pointer-input-and-grid-picking.md`
- Voxel worlds: `reference/voxel-worlds.md`, `reference/chunked-voxel-terrain.md`
- Performance: `reference/performance.md`, `reference/cpu-rasterizer-constraints.md`
- Migration/comparison: `reference/threejs-migration.md`, `reference/createjs-easeljs-comparison.md`, `reference/webgl-webgpu-comparison.md`

## Minimal Verified Setup

```ts
import * as EASEL from "@xsyetopz/easel";

const renderer = new EASEL.Renderer({ width: 320, height: 180, canvas });
const scene = new EASEL.Scene();
const camera = new EASEL.PerspectiveCamera({ fov: 60, aspect: 320 / 180, near: 0.1, far: 100 });

camera.position.set(2, 2, 4);
camera.lookAt(0, 0, 0);
scene.add(new EASEL.AmbientLight(0xffffff, 0.35));

const mesh = new EASEL.Mesh(
	new EASEL.BoxGeometry(1, 1, 1),
	new EASEL.LambertMaterial({ color: 0xff5533 }),
);
scene.add(mesh);

function frame() {
	mesh.rotation.y += 0.02;
	scene.updateMatrixWorld();
	renderer.render(scene, camera);
	requestAnimationFrame(frame);
}
frame();
```

## Source Lookup Order

1. Current project code and installed package version.
2. Bundled `reference/api-index.md` and `reference/class-signatures.md`.
3. Bundled recipe matching the task.
4. Installed package declarations under `node_modules/@xsyetopz/easel/dist/` or Deno type cache.
5. Installed package source under `node_modules/@xsyetopz/easel/src/` when available.
6. Official package/docs links from `reference/version-provenance.md`.

Keep implementations close to these references. Prefer verified recipes over improvised APIs.
