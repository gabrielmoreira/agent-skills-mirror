# Post-processing (load on demand)

Use this companion when the user asks for bloom, depth-of-field, or an EffectComposer chain on a scene already built in `SKILL.md`. It is a short overlay, not a game visual pipeline and not a specialist catalog of every pass.

## WebGL: EffectComposer

Call `composer.render()` in the animation loop. `renderer.render(scene, camera)` skips every pass.

```javascript
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/addons/postprocessing/UnrealBloomPass.js";

const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));
composer.addPass(
  new UnrealBloomPass(
    new THREE.Vector2(window.innerWidth, window.innerHeight),
    1.5,  // strength
    0.4,  // radius
    0.85, // threshold
  ),
);

renderer.setAnimationLoop(() => {
  composer.render();
});
```

On resize, update camera aspect, `renderer.setSize`, and `composer.setSize`. Bloom resolution must match the new viewport.

## WebGPU (r183+)

`EffectComposer` is WebGL-only. With `WebGPURenderer`, compose TSL nodes and render through `THREE.PostProcessing` (node graph / `outputNode`). Do not mix the two APIs on one renderer.

```javascript
import { pass, bloom } from "three/tsl";

const postProcessing = new THREE.PostProcessing(renderer);
const scenePass = pass(scene, camera);
postProcessing.outputNode = bloom(scenePass, 0.5, 0.4, 0.85);

renderer.setAnimationLoop(() => {
  postProcessing.render();
});
```

## Pitfalls

- First pass must be `RenderPass` (WebGL) so later effects have a scene texture.
- Limit passes on mobile; each pass is a full-screen draw.
- For a full pass catalog (SSAO, FXAA, selective bloom), load a dedicated post-processing specialist if it is installed. This file stays the overlay for the vanilla canvas in `SKILL.md`.
