---
name: threejs-postprocessing
description: "Sets up Three.js screen-space post-processing: EffectComposer/RenderPass, UnrealBloom, DOF, SSAO, FXAA, vignette, glitch, outline, custom ShaderPass, and WebGPU TSL PostProcessing. Use when adding glow, blur, AA, or grading on the final image rather than scene lighting. Not for modeling, materials, or shadows in the scene graph; never call renderer.render() in the loop once a composer owns the frame."
version: 1.0.1
risk: unknown
source: community
---

# Three.js Post-Processing

## When to Use

- You need screen-space visual effects in a Three.js render pipeline.
- The task involves `EffectComposer`, bloom, depth of field, color grading, blur, or custom passes.
- You are enhancing the final rendered image rather than base scene setup alone.
- You are migrating a WebGL `EffectComposer` pipeline to WebGPU TSL `PostProcessing`.
- You need selective bloom, outline selection, pixelation, glitch, halftone, or chromatic aberration.

## Prerequisites

- Three.js installed in the project (`three` npm package, version r150+ recommended; WebGPU TSL post-processing requires r183+).
- A working `WebGLRenderer` (or `WebGPURenderer` for TSL path) with an active scene and camera.
- Basic familiarity with GLSL fragment/vertex shaders for custom `ShaderPass` effects.
- For WebGPU path: a browser with WebGPU support and `three/addons/renderers/webgpu/WebGPURenderer.js`.

## Procedure

### 1. Core EffectComposer Setup (WebGL)

The minimal pipeline: create an `EffectComposer`, add a `RenderPass` first, then effect passes, then call `composer.render()` instead of `renderer.render()`.

```javascript
import * as THREE from "three";
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/addons/postprocessing/UnrealBloomPass.js";

const composer = new EffectComposer(renderer);

// First pass: render the scene
const renderPass = new RenderPass(scene, camera);
composer.addPass(renderPass);

// Effect pass
const bloomPass = new UnrealBloomPass(
  new THREE.Vector2(window.innerWidth, window.innerHeight),
  1.5, // strength
  0.4, // radius
  0.85, // threshold
);
composer.addPass(bloomPass);

// Animation loop — use composer.render(), NOT renderer.render()
function animate() {
  requestAnimationFrame(animate);
  composer.render();
}
```

**HARD RULE:** Always call `composer.render()` in the animation loop. Calling `renderer.render(scene, camera)` will bypass all post-processing.

### 2. Handle Resize

Every pass that depends on screen resolution must be updated on resize.

```javascript
function onWindowResize() {
  const width = window.innerWidth;
  const height = window.innerHeight;
  const pixelRatio = renderer.getPixelRatio();

  camera.aspect = width / height;
  camera.updateProjectionMatrix();

  renderer.setSize(width, height);
  composer.setSize(width, height);

  // Update pass-specific resolutions
  if (fxaaPass) {
    fxaaPass.material.uniforms["resolution"].value.set(
      1 / (width * pixelRatio),
      1 / (height * pixelRatio),
    );
  }

  if (bloomPass) {
    bloomPass.resolution.set(width, height);
  }
}

window.addEventListener("resize", onWindowResize);
```

### 3. Add Common Effects

Each effect is a pass added after `RenderPass`. The last pass added automatically renders to screen.

#### Bloom (Glow)

```javascript
import { UnrealBloomPass } from "three/addons/postprocessing/UnrealBloomPass.js";

const bloomPass = new UnrealBloomPass(
  new THREE.Vector2(window.innerWidth, window.innerHeight),
  1.5, // strength — intensity of glow
  0.4, // radius — spread of glow
  0.85, // threshold — brightness threshold (only brighter pixels bloom)
);
composer.addPass(bloomPass);

// Adjust at runtime
bloomPass.strength = 2.0;
bloomPass.threshold = 0.5;
bloomPass.radius = 0.8;
```

#### Selective Bloom

Apply bloom only to specific objects using layers and a dark-material swap technique.

```javascript
import { UnrealBloomPass } from "three/addons/postprocessing/UnrealBloomPass.js";
import { ShaderPass } from "three/addons/postprocessing/ShaderPass.js";

const BLOOM_LAYER = 1;
const bloomLayer = new THREE.Layers();
bloomLayer.set(BLOOM_LAYER);

// Mark objects to bloom
glowingMesh.layers.enable(BLOOM_LAYER);

// Dark material for non-blooming objects
const darkMaterial = new THREE.MeshBasicMaterial({ color: 0x000000 });
const materials = {};

function darkenNonBloomed(obj) {
  if (obj.isMesh && !bloomLayer.test(obj.layers)) {
    materials[obj.uuid] = obj.material;
    obj.material = darkMaterial;
  }
}

function restoreMaterial(obj) {
  if (materials[obj.uuid]) {
    obj.material = materials[obj.uuid];
    delete materials[obj.uuid];
  }
}

// Custom render loop
function render() {
  scene.traverse(darkenNonBloomed);
  composer.render();
  scene.traverse(restoreMaterial);

  // Render final scene over bloom
  renderer.render(scene, camera);
}
```

#### FXAA (Anti-Aliasing)

```javascript
import { ShaderPass } from "three/addons/postprocessing/ShaderPass.js";
import { FXAAShader } from "three/addons/shaders/FXAAShader.js";

const fxaaPass = new ShaderPass(FXAAShader);
fxaaPass.material.uniforms["resolution"].value.set(
  1 / window.innerWidth,
  1 / window.innerHeight,
);
composer.addPass(fxaaPass);
```

**HARD RULE:** Update `fxaaPass.material.uniforms["resolution"]` on resize or edges will shimmer.

#### SMAA (Better Anti-Aliasing)

```javascript
import { SMAAPass } from "three/addons/postprocessing/SMAAPass.js";

const smaaPass = new SMAAPass(
  window.innerWidth * renderer.getPixelRatio(),
  window.innerHeight * renderer.getPixelRatio(),
);
composer.addPass(smaaPass);
```

#### SSAO (Ambient Occlusion)

```javascript
import { SSAOPass } from "three/addons/postprocessing/SSAOPass.js";

const ssaoPass = new SSAOPass(
  scene,
  camera,
  window.innerWidth,
  window.innerHeight,
);
ssaoPass.kernelRadius = 16;
ssaoPass.minDistance = 0.005;
ssaoPass.maxDistance = 0.1;
composer.addPass(ssaoPass);

// Output modes for debugging
ssaoPass.output = SSAOPass.OUTPUT.Default;
// Options: Default, SSAO, Blur, Depth, Normal
```

#### Depth of Field (Bokeh)

```javascript
import { BokehPass } from "three/addons/postprocessing/BokehPass.js";

const bokehPass = new BokehPass(scene, camera, {
  focus: 10.0, // Focus distance
  aperture: 0.025, // Smaller = more DOF
  maxblur: 0.01, // Max blur amount
});
composer.addPass(bokehPass);

// Update focus dynamically
bokehPass.uniforms["focus"].value = distanceToTarget;
```

#### Film Grain

```javascript
import { FilmPass } from "three/addons/postprocessing/FilmPass.js";

const filmPass = new FilmPass(
  0.35, // noise intensity
  0.5, // scanline intensity
  648, // scanline count
  false, // grayscale
);
composer.addPass(filmPass);
```

#### Vignette

```javascript
import { ShaderPass } from "three/addons/postprocessing/ShaderPass.js";
import { VignetteShader } from "three/addons/shaders/VignetteShader.js";

const vignettePass = new ShaderPass(VignetteShader);
vignettePass.uniforms["offset"].value = 1.0; // Vignette size
vignettePass.uniforms["darkness"].value = 1.0; // Vignette intensity
composer.addPass(vignettePass);
```

#### Color Correction

```javascript
import { ShaderPass } from "three/addons/postprocessing/ShaderPass.js";
import { ColorCorrectionShader } from "three/addons/shaders/ColorCorrectionShader.js";

const colorPass = new ShaderPass(ColorCorrectionShader);
colorPass.uniforms["powRGB"].value = new THREE.Vector3(1.2, 1.2, 1.2);
colorPass.uniforms["mulRGB"].value = new THREE.Vector3(1.0, 1.0, 1.0);
composer.addPass(colorPass);
```

#### Gamma Correction

```javascript
import { GammaCorrectionShader } from "three/addons/shaders/GammaCorrectionShader.js";

const gammaPass = new ShaderPass(GammaCorrectionShader);
composer.addPass(gammaPass);
```

#### Pixelation

```javascript
import { RenderPixelatedPass } from "three/addons/postprocessing/RenderPixelatedPass.js";

const pixelPass = new RenderPixelatedPass(6, scene, camera); // 6 = pixel size
composer.addPass(pixelPass);
```

#### Glitch Effect

```javascript
import { GlitchPass } from "three/addons/postprocessing/GlitchPass.js";

const glitchPass = new GlitchPass();
glitchPass.goWild = false; // Set true for continuous glitching
composer.addPass(glitchPass);
```

#### Halftone

```javascript
import { HalftonePass } from "three/addons/postprocessing/HalftonePass.js";

const halftonePass = new HalftonePass(window.innerWidth, window.innerHeight, {
  shape: 1, // 1 = dot, 2 = ellipse, 3 = line, 4 = square
  radius: 4, // Dot size
  rotateR: Math.PI / 12,
  rotateB: (Math.PI / 12) * 2,
  rotateG: (Math.PI / 12) * 3,
  scatter: 0,
  blending: 1,
  blendingMode: 1,
  greyscale: false,
});
composer.addPass(halftonePass);
```

#### Outline

```javascript
import { OutlinePass } from "three/addons/postprocessing/OutlinePass.js";

const outlinePass = new OutlinePass(
  new THREE.Vector2(window.innerWidth, window.innerHeight),
  scene,
  camera,
);

outlinePass.edgeStrength = 3;
outlinePass.edgeGlow = 0;
outlinePass.edgeThickness = 1;
outlinePass.pulsePeriod = 0;
outlinePass.visibleEdgeColor.set(0xffffff);
outlinePass.hiddenEdgeColor.set(0x190a05);

// Select objects to outline
outlinePass.selectedObjects = [mesh1, mesh2];
composer.addPass(outlinePass);
```

### 4. Custom ShaderPass

Create custom screen-space effects. The `tDiffuse` uniform is required — it receives the previous pass output.

```javascript
import { ShaderPass } from "three/addons/postprocessing/ShaderPass.js";

const CustomShader = {
  uniforms: {
    tDiffuse: { value: null }, // Required: input texture from previous pass
    time: { value: 0 },
    intensity: { value: 1.0 },
  },
  vertexShader: `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    uniform sampler2D tDiffuse;
    uniform float time;
    uniform float intensity;
    varying vec2 vUv;

    void main() {
      vec2 uv = vUv;
      uv.x += sin(uv.y * 10.0 + time) * 0.01 * intensity;
      vec4 color = texture2D(tDiffuse, uv);
      gl_FragColor = color;
    }
  `,
};

const customPass = new ShaderPass(CustomShader);
composer.addPass(customPass);

// Update in animation loop
customPass.uniforms.time.value = clock.getElapsedTime();
```

#### Invert Colors Shader

```javascript
const InvertShader = {
  uniforms: {
    tDiffuse: { value: null },
  },
  vertexShader: `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    uniform sampler2D tDiffuse;
    varying vec2 vUv;
    void main() {
      vec4 color = texture2D(tDiffuse, vUv);
      gl_FragColor = vec4(1.0 - color.rgb, color.a);
    }
  `,
};
```

#### Chromatic Aberration

```javascript
const ChromaticAberrationShader = {
  uniforms: {
    tDiffuse: { value: null },
    amount: { value: 0.005 },
  },
  vertexShader: `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    uniform sampler2D tDiffuse;
    uniform float amount;
    varying vec2 vUv;
    void main() {
      vec2 dir = vUv - 0.5;
      float dist = length(dir);
      float r = texture2D(tDiffuse, vUv - dir * amount * dist).r;
      float g = texture2D(tDiffuse, vUv).g;
      float b = texture2D(tDiffuse, vUv + dir * amount * dist).b;
      gl_FragColor = vec4(r, g, b, 1.0);
    }
  `,
};
```

### 5. Combining Multiple Effects (Recommended Order)

```javascript
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/addons/postprocessing/UnrealBloomPass.js";
import { ShaderPass } from "three/addons/postprocessing/ShaderPass.js";
import { FXAAShader } from "three/addons/shaders/FXAAShader.js";
import { VignetteShader } from "three/addons/shaders/VignetteShader.js";
import { GammaCorrectionShader } from "three/addons/shaders/GammaCorrectionShader.js";

const composer = new EffectComposer(renderer);

// 1. Render scene (always first)
composer.addPass(new RenderPass(scene, camera));

// 2. Bloom
const bloomPass = new UnrealBloomPass(
  new THREE.Vector2(window.innerWidth, window.innerHeight),
  0.5, 0.4, 0.85,
);
composer.addPass(bloomPass);

// 3. Vignette
const vignettePass = new ShaderPass(VignetteShader);
vignettePass.uniforms["offset"].value = 0.95;
vignettePass.uniforms["darkness"].value = 1.0;
composer.addPass(vignettePass);

// 4. Gamma correction
composer.addPass(new ShaderPass(GammaCorrectionShader));

// 5. Anti-aliasing (always last before output)
const fxaaPass = new ShaderPass(FXAAShader);
fxaaPass.uniforms["resolution"].value.set(
  1 / window.innerWidth,
  1 / window.innerHeight,
);
composer.addPass(fxaaPass);
```

**HARD RULE:** `RenderPass` must always be the first pass. Anti-aliasing (FXAA/SMAA) should be the last pass.

### 6. Render to Texture

```javascript
const renderTarget = new THREE.WebGLRenderTarget(512, 512);

renderer.setRenderTarget(renderTarget);
renderer.render(scene, camera);
renderer.setRenderTarget(null);

// Use the rendered texture
const texture = renderTarget.texture;
otherMaterial.map = texture;
```

### 7. Multi-Pass Rendering (Multiple Composers)

```javascript
const bgComposer = new EffectComposer(renderer);
bgComposer.addPass(new RenderPass(bgScene, camera));

const fgComposer = new EffectComposer(renderer);
fgComposer.addPass(new RenderPass(fgScene, camera));
fgComposer.addPass(bloomPass);

function animate() {
  renderer.autoClear = false;
  renderer.clear();
  bgComposer.render();

  renderer.clearDepth();
  fgComposer.render();
}
```

### 8. WebGPU Post-Processing (Three.js r183+)

The WebGPU renderer uses a node-based `PostProcessing` class instead of `EffectComposer`. `EffectComposer` is **WebGL-only**.

```javascript
import * as THREE from "three";
import { pass, bloom, dof } from "three/tsl";
import { WebGPURenderer } from "three/addons/renderers/webgpu/WebGPURenderer.js";

const renderer = new WebGPURenderer({ antialias: true });
await renderer.init();

const postProcessing = new THREE.PostProcessing(renderer);

// Scene pass
const scenePass = pass(scene, camera);

// Add bloom
const bloomPass = bloom(scenePass, 0.5, 0.4, 0.85);

// Set output node
postProcessing.outputNode = bloomPass;

// Render
renderer.setAnimationLoop(() => {
  postProcessing.render();
});
```

**Key differences:**

| EffectComposer (WebGL)           | PostProcessing (WebGPU)     |
| -------------------------------- | --------------------------- |
| `addPass(new RenderPass(...))`  | `pass(scene, camera)`        |
| `addPass(new UnrealBloomPass)`  | `bloom(scenePass, ...)`      |
| `composer.render()`             | `postProcessing.render()`   |
| Chain of passes                  | Node graph with `outputNode` |
| GLSL shader passes               | TSL node-based effects       |

### 9. Performance Tuning

1. **Limit passes** — each pass is a full-screen render call.
2. **Lower resolution for blur passes** — use half-resolution render targets for bloom.
3. **Disable unused effects** — toggle `pass.enabled = false`.
4. **Prefer FXAA over MSAA** — less expensive, works with post-processing.
5. **Profile with DevTools** — check GPU usage in the Performance tab.

```javascript
// Disable a pass at runtime
bloomPass.enabled = false;

// Reduce bloom resolution
const bloomPass = new UnrealBloomPass(
  new THREE.Vector2(window.innerWidth / 2, window.innerHeight / 2),
  strength, radius, threshold,
);

// Conditionally apply expensive effects
const isMobile = /iPhone|iPad|Android/i.test(navigator.userAgent);
if (!isMobile) {
  composer.addPass(expensivePass);
}
```

## Pitfalls

- **Using `renderer.render()` instead of `composer.render()`**: This bypasses all post-processing. Always use `composer.render()` once the composer is set up.
- **Missing `tDiffuse` uniform in custom shaders**: Every `ShaderPass` shader must declare `tDiffuse: { value: null }` — it receives the previous pass output. Without it, the screen will be black.
- **Forgetting to update pass resolutions on resize**: FXAA and other resolution-dependent passes will produce shimmering or incorrect results if their uniforms are not updated.
- **`RenderPass` not first**: The first pass must always be `RenderPass` to populate the composer's input texture with the scene.
- **Anti-aliasing not last**: FXAA/SMAA should be the final pass so it anti-aliases the composited result.
- **Selective bloom material leak**: If `restoreMaterial` is not called for every object that had its material swapped, materials will be permanently replaced with the dark material. Always pair `darkenNonBloomed` with `restoreMaterial` in the render loop.
- **WebGPU `EffectComposer` confusion**: `EffectComposer` is WebGL-only. WebGPU requires `THREE.PostProcessing` with TSL nodes. Do not mix the two APIs.
- **`renderToScreen` on wrong pass**: Only the last pass should render to screen. Setting it on an intermediate pass will discard subsequent passes.
- **Pixel ratio not accounted for**: SMAA and FXAA passes need pixel-ratio-adjusted dimensions. Failing to multiply by `renderer.getPixelRatio()` causes blurry or jagged output on high-DPI displays.
- **Too many passes on mobile**: Each pass is a full-screen quad render. On mobile, limit to 2–3 passes and skip expensive effects like SSAO.

## Verification

1. **Verify composer is rendering** — open browser console and check no errors; the canvas should show the scene with effects applied.

2. **Verify pass order** — log the passes:
   ```javascript
   console.log(composer.passes.map(p => p.constructor.name));
   // Expected: ["RenderPass", "UnrealBloomPass", "ShaderPass", "ShaderPass", ...]
   ```

3. **Verify resize handler works** — resize the browser window and confirm the canvas and effects scale without distortion:
   ```javascript
   // After resize, check:
   console.log(renderer.getSize(new THREE.Vector2())); // Should match window
   console.log(composer.passes[0].setSize); // Confirm method exists
   ```

4. **Verify custom shader receives input** — add a debug line in the fragment shader:
   ```glsl
   gl_FragColor = texture2D(tDiffuse, vUv); // Should show the scene unmodified
   ```
   If the screen is black, `tDiffuse` is not connected.

5. **Verify WebGPU path** — check renderer type:
   ```javascript
   console.log(renderer.isWebGPURenderer); // true for WebGPU
   console.log(postProcessing.outputNode); // Should be a valid node, not null
   ```

6. **Performance check** — use Chrome DevTools Performance tab to confirm frame time stays under 16ms (60fps). If exceeding, disable passes one by one to find the bottleneck:
   ```javascript
   bloomPass.enabled = false; // Toggle and observe FPS change
   ```

## Related Skills

- `threejs-shaders` — Custom shader development (GLSL and TSL)
- `threejs-textures` — Render targets and texture management
- `threejs-fundamentals` — Renderer, scene, and camera setup

## Limitations

- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
