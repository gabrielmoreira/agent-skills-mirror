---
name: threejs-lighting
version: 1.2.1
description: "Sets up Three.js lights, shadow maps, IBL/PMREM, and light probes (Ambient, Directional, Point, Spot, RectArea). Use when adding lights, configuring shadows, or optimizing lighting cost. Not for Godot lighting (godot-3d-lighting), first-canvas scaffold (threejs-skill-router), or materials/postprocessing chairs."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-14
---

# Three.js Lighting

## When to Use

- You need to add or tune lighting in a Three.js scene.
- The task involves light types, shadows, environment lighting (IBL), or lighting performance tradeoffs.
- You want to improve scene readability, realism, or mood through Three.js lighting setup.
- Trigger keywords: `AmbientLight`, `DirectionalLight`, `PointLight`, `SpotLight`, `RectAreaLight`, `HemisphereLight`, shadow map, IBL, environment map, PMREM, light probe, three-point lighting.

## Prerequisites

- Three.js r165+ installed (`npm install three` or via CDN). APIs referenced here target r165–r166.
- A `WebGLRenderer` instance and at least one `Scene` with meshes using `MeshStandardMaterial` or `MeshPhysicalMaterial` for PBR-correct light response.
- For HDR environment maps: an `.hdr` file accessible at a known URL or local path.
- Windows host is primary (PowerShell). When running local dev servers, use PowerShell-compatible commands (e.g., `npx vite` rather than POSIX-only shell scripts).

## Procedure

### 1 — Choose Light Types

| Light            | Description            | Shadow Support | Cost     |
| ---------------- | ---------------------- | -------------- | -------- |
| AmbientLight     | Uniform everywhere     | No             | Very Low |
| HemisphereLight  | Sky/ground gradient    | No             | Very Low |
| DirectionalLight | Parallel rays (sun)    | Yes            | Low      |
| PointLight       | Omnidirectional (bulb) | Yes            | Medium   |
| SpotLight        | Cone-shaped            | Yes            | Medium   |
| RectAreaLight    | Area light (window)    | No*            | High     |

\*RectAreaLight shadows require custom solutions; as of Three.js r166 they can be approximated with `RectAreaLightUniformsLib` and a custom shader.

### 2 — Add Base Lighting

```javascript
import * as THREE from "three";

// AmbientLight(color, intensity) — uniform fill, no shadows
const ambient = new THREE.AmbientLight(0xffffff, 0.5);
scene.add(ambient);

// HemisphereLight(skyColor, groundColor, intensity) — outdoor gradient
const hemi = new THREE.HemisphereLight(0x87ceeb, 0x8b4513, 0.6);
hemi.position.set(0, 50, 0);
scene.add(hemi);

// DirectionalLight(color, intensity) — parallel rays (sun)
const dirLight = new THREE.DirectionalLight(0xffffff, 1);
dirLight.position.set(5, 10, 5);
dirLight.target.position.set(0, 0, 0);
scene.add(dirLight.target);
scene.add(dirLight);
```

### 3 — Add Point or Spot Lights

```javascript
// PointLight(color, intensity, distance, decay)
const pointLight = new THREE.PointLight(0xffffff, 1, 100, 2);
pointLight.position.set(0, 5, 0);
scene.add(pointLight);

// SpotLight(color, intensity, distance, angle, penumbra, decay)
const spotLight = new THREE.SpotLight(0xffffff, 1, 100, Math.PI / 6, 0.5, 2);
spotLight.position.set(0, 10, 0);
spotLight.target.position.set(0, 0, 0);
scene.add(spotLight.target);
scene.add(spotLight);
```

### 4 — Add RectAreaLight (requires uniforms init)

```javascript
import { RectAreaLightHelper } from "three/examples/jsm/helpers/RectAreaLightHelper.js";
import { RectAreaLightUniformsLib } from "three/examples/jsm/lights/RectAreaLightUniformsLib.js";

// Initialize uniforms (WebGLRenderer only)
RectAreaLightUniformsLib.init();

// RectAreaLight(color, intensity, width, height)
const rectLight = new THREE.RectAreaLight(0xffffff, 5, 4, 2);
rectLight.position.set(0, 5, 0);
rectLight.lookAt(0, 0, 0);
scene.add(rectLight);

// Helper
const helper = new RectAreaLightHelper(rectLight);
rectLight.add(helper);
```

RectAreaLight works with `MeshStandardMaterial`, `MeshPhysicalMaterial` (including clearcoat).

### 5 — Enable and Configure Shadows

```javascript
// 1. Enable on renderer
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap; // Preferred for soft edges

// 2. Enable on light
light.castShadow = true;

// 3. Enable on objects
mesh.castShadow = true;
mesh.receiveShadow = true;

// Ground plane
floor.receiveShadow = true;
floor.castShadow = false;
```

#### DirectionalLight shadow camera (orthographic)

```javascript
dirLight.castShadow = true;
dirLight.shadow.mapSize.width = 2048;
dirLight.shadow.mapSize.height = 2048;

dirLight.shadow.camera.near = 0.5;
dirLight.shadow.camera.far = 50;
dirLight.shadow.camera.left = -10;
dirLight.shadow.camera.right = 10;
dirLight.shadow.camera.top = 10;
dirLight.shadow.camera.bottom = -10;

// Shadow softness (requires PCFSoftShadowMap)
dirLight.shadow.radius = 4;

// Shadow bias (fixes shadow acne)
dirLight.shadow.bias = -0.0001;
dirLight.shadow.normalBias = 0.02;

// Helper to visualize shadow camera
const helper = new THREE.CameraHelper(dirLight.shadow.camera);
scene.add(helper);
```

#### PointLight shadow camera (perspective — 6 faces for cube map)

```javascript
pointLight.castShadow = true;
pointLight.shadow.mapSize.width = 1024;
pointLight.shadow.mapSize.height = 1024;
pointLight.shadow.camera.near = 0.5;
pointLight.shadow.camera.far = 50;
pointLight.shadow.bias = -0.005;
```

#### SpotLight shadow camera (perspective)

```javascript
spotLight.castShadow = true;
spotLight.shadow.mapSize.width = 1024;
spotLight.shadow.mapSize.height = 1024;
spotLight.shadow.camera.near = 0.5;
spotLight.shadow.camera.far = 50;
spotLight.shadow.camera.fov = 30;
spotLight.shadow.bias = -0.0001;
spotLight.shadow.focus = 1;
```

### 6 — Optimize Shadows

```javascript
// Tight shadow camera frustum
const d = 10;
dirLight.shadow.camera.left = -d;
dirLight.shadow.camera.right = d;
dirLight.shadow.camera.top = d;
dirLight.shadow.camera.bottom = -d;
dirLight.shadow.camera.near = 0.5;
dirLight.shadow.camera.far = 30;

// Shadow map size (balance quality vs performance)
const mapSize = 2048; // 1024 for most mobile, 4096 for high-end desktop
dirLight.shadow.mapSize.set(mapSize, mapSize);
```

#### Contact Shadows (fast approximation)

```javascript
import { ContactShadows } from "three/examples/jsm/objects/ContactShadows.js";

const contactShadows = new ContactShadows({
  resolution: 512,
  blur: 2,
  opacity: 0.5,
  scale: 10,
  position: [0, 0, 0],
});
scene.add(contactShadows);
```

### 7 — Add Light Helpers

```javascript
import { RectAreaLightHelper } from "three/examples/jsm/helpers/RectAreaLightHelper.js";

const dirHelper = new THREE.DirectionalLightHelper(dirLight, 5);
scene.add(dirHelper);

const pointHelper = new THREE.PointLightHelper(pointLight, 1);
scene.add(pointHelper);

const spotHelper = new THREE.SpotLightHelper(spotLight);
scene.add(spotHelper);

const hemiHelper = new THREE.HemisphereLightHelper(hemi, 5);
scene.add(hemiHelper);

const rectHelper = new RectAreaLightHelper(rectLight);
rectLight.add(rectHelper);

// Update helpers when light changes
dirHelper.update();
spotHelper.update();
```

### 8 — Set Up Environment Lighting (IBL)

#### HDR via RGBELoader

```javascript
import { RGBELoader } from "three/examples/jsm/loaders/RGBELoader.js";

const rgbeLoader = new RGBELoader();
rgbeLoader.load("environment.hdr", (texture) => {
  texture.mapping = THREE.EquirectangularReflectionMapping;

  // Set as scene environment (affects all PBR materials)
  scene.environment = texture;

  // Optional: also use as background
  scene.background = texture;
  scene.backgroundBlurriness = 0; // 0-1
  scene.backgroundIntensity = 1;
});
```

#### PMREM for Accurate Reflections (Three.js r165+)

```javascript
const pmremGenerator = new THREE.PMREMGenerator(renderer);
pmremGenerator.compileEquirectangularShader();

rgbeLoader.load("environment.hdr", (texture) => {
  const envMap = pmremGenerator.fromEquirectangular(texture).texture;
  scene.environment = envMap;
  texture.dispose();
  pmremGenerator.dispose();
});
```

#### Cube Texture Environment

```javascript
const cubeLoader = new THREE.CubeTextureLoader();
const envMap = cubeLoader.load([
  "px.jpg",
  "nx.jpg",
  "py.jpg",
  "ny.jpg",
  "pz.jpg",
  "nz.jpg",
]);

scene.environment = envMap;
scene.background = envMap;
```

### 9 — Light Probes (Advanced)

Capture lighting from a point in space for ambient lighting.

```javascript
import { LightProbeGenerator } from "three/examples/jsm/lights/LightProbeGenerator.js";

const lightProbe = new THREE.LightProbe();
scene.add(lightProbe);

// From cube texture
lightProbe.copy(LightProbeGenerator.fromCubeTexture(cubeTexture));

// Or from render target
const cubeCamera = new THREE.CubeCamera(
  0.1,
  100,
  new THREE.WebGLCubeRenderTarget(256)
);
cubeCamera.update(renderer, scene);
lightProbe.copy(
  LightProbeGenerator.fromCubeRenderTarget(renderer, cubeCamera.renderTarget)
);
```

### 10 — Use Common Lighting Setups

#### Three-Point Lighting

```javascript
// Key light (main)
const keyLight = new THREE.DirectionalLight(0xffffff, 1);
keyLight.position.set(5, 5, 5);
scene.add(keyLight);

// Fill light (softer, opposite side)
const fillLight = new THREE.DirectionalLight(0xffffff, 0.5);
fillLight.position.set(-5, 3, 5);
scene.add(fillLight);

// Back light (rim)
const backLight = new THREE.DirectionalLight(0xffffff, 0.3);
backLight.position.set(0, 5, -5);
scene.add(backLight);

// Ambient fill
const ambient = new THREE.AmbientLight(0x404040, 0.3);
scene.add(ambient);
```

#### Outdoor Daylight

```javascript
const sun = new THREE.DirectionalLight(0xffffcc, 1.5);
sun.position.set(50, 100, 50);
sun.castShadow = true;
scene.add(sun);

const hemi = new THREE.HemisphereLight(0x87ceeb, 0x8b4513, 0.6);
scene.add(hemi);
```

#### Indoor Studio

```javascript
RectAreaLightUniformsLib.init();

const light1 = new THREE.RectAreaLight(0xffffff, 5, 2, 2);
light1.position.set(3, 3, 3);
light1.lookAt(0, 0, 0);
scene.add(light1);

const light2 = new THREE.RectAreaLight(0xffffff, 3, 2, 2);
light2.position.set(-3, 3, 3);
light2.lookAt(0, 0, 0);
scene.add(light2);

const ambient = new THREE.AmbientLight(0x404040, 0.2);
scene.add(ambient);
```

### 11 — Animate Lights

```javascript
const clock = new THREE.Clock();

function animate() {
  const time = clock.getElapsedTime();

  // Orbit light around scene
  light.position.x = Math.cos(time) * 5;
  light.position.z = Math.sin(time) * 5;

  // Pulsing intensity
  light.intensity = 1 + Math.sin(time * 2) * 0.5;

  // Color cycling
  light.color.setHSL((time * 0.1) % 1, 1, 0.5);

  // Update helpers if using
  lightHelper.update();
}
```

### 12 — Optimize Performance

1. **Limit light count** — each additional light adds shader complexity.
2. **Prefer baked lighting** for static geometry (lightmaps, ambient occlusion).
3. **Shadow map size** — 512–1024 is sufficient for most web targets; use 2048+ only when high fidelity is required.
4. **Tight shadow frustums** — keep the camera volume as small as possible.
5. **Disable unused shadows** — not every light needs a shadow map.
6. **Use light layers** — exclude objects from specific lights to reduce calculations.
7. **Leverage `WebGLRenderer`'s `physicallyCorrectLights` flag** for realistic decay (`renderer.physicallyCorrectLights = true;`).

```javascript
// Light layers example
light.layers.set(1);           // Light only affects layer 1
mesh.layers.enable(1);         // Mesh is on layer 1
otherMesh.layers.disable(1);   // Excluded from this light
```

## Pitfalls

- **Deprecated `THREE.Light` base class** — removed in r165; use concrete subclasses.
- **`RectAreaLightHelper` from older examples** — replaced by the modern helper in `three/examples/jsm/helpers/RectAreaLightHelper.js`.
- **`THREE.BasicShadowMap`** — provides poor quality and is discouraged for production.
- **Hard-coded shadow bias values** without testing — can cause acne or peter-panning on different hardware. Always tune per scene.
- **Loading HDR files without `RGBELoader`** — leads to incorrect color space handling.
- **Enabling shadows on `AmbientLight` or `HemisphereLight`** — they never cast shadows and waste GPU cycles.
- **Forgetting to add `light.target` to the scene** — DirectionalLight and SpotLight targets must be explicitly added or the light direction will not update.
- **Forgetting `RectAreaLightUniformsLib.init()`** — RectAreaLight will render incorrectly without it.
- **Shadow camera frustum too large** — shadows appear pixelated; tighten the frustum to the scene bounds.
- **Not disposing PMREMGenerator or textures** — causes GPU memory leaks on scene reload.

## Verification

- [ ] Verify that the renderer has `shadowMap.enabled = true` and uses `THREE.PCFSoftShadowMap`.
- [ ] Confirm each light that should cast shadows has `castShadow = true` and appropriate `shadow.mapSize`.
- [ ] Check that objects intended to receive shadows have `receiveShadow = true`.
- [ ] Ensure environment maps are loaded with `RGBELoader` (HDR) or `CubeTextureLoader` and assigned to `scene.environment`.
- [ ] Run the scene on at least two browsers (Chrome 130+, Firefox 130+) and verify no console warnings about deprecated APIs.
- [ ] Profile frame time; shadows should not exceed 30 ms on a mid-range device (e.g., Pixel 7a) for a scene with ≤4 shadow-casting lights.
- [ ] Validate that light layers correctly isolate lights from objects by toggling `layers.enable/disable` and observing shadow/render changes.

## Related skills

- `threejs-materials` — Material light response
- `threejs-textures` — Lightmaps and environment maps
- `threejs-postprocessing` — Bloom and other light effects

## Limitations

- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
