# Three.js Game Checklist

Use this checklist for Three.js 3D browser games.

## Project Structure

- The render loop, simulation update, input, camera, asset loading, UI bridge, and cleanup responsibilities are separated.
- Renderer sizing updates on viewport changes and device pixel ratio is capped where needed.
- The app handles pause, focus loss, route/page teardown, and browser visibility changes.
- Important scene objects are named or referenced directly rather than found through repeated per-frame traversal.

## Assets And Rendering

- GLB/GLTF assets are optimized for mesh count, material count, texture size, skeleton count, and animation clips.
- Textures use appropriate compression, mipmaps, color space, and power-of-two sizing where useful.
- Shadows, postprocessing, antialiasing, tone mapping, and lighting are justified by the target device budget.
- Removed objects dispose geometries, materials, textures, render targets, and event listeners.

## Gameplay

- Input supports the expected keyboard, mouse, touch, gamepad, pointer lock, and fullscreen flows.
- Physics and visual transforms stay synchronized if a physics engine is used.
- Raycasting is scoped by layers, object lists, or acceleration structures when scenes grow.
- Camera behavior is tested at gameplay speed and does not hide critical action.

## Browser QA

- The canvas is visible, nonblank, and correctly framed at desktop and mobile viewports.
- Frame time, draw calls, triangles, texture memory, shader cost, and garbage collection are checked.
- Audio starts only after a permitted user gesture where required.
- Relative paths work after production build and static hosting.
