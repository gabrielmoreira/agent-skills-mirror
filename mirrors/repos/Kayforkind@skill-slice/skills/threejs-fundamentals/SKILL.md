---
name: threejs-fundamentals
description: "Teaches Three.js scene/camera/WebGLRenderer, Object3D hierarchy, transforms, resize, setAnimationLoop, and Vector3/Quaternion/Euler math. Use when scaffolding or explaining core Three.js structure before specialists. Not for vanilla r183 canvas kits (threejs-skills), ambitious visual routing (threejs-skill-router), shaders/postprocessing, or playable web games (threejs-game-development)."
version: 1.0.1
---

## When to Use

- You need to scaffold the core structure of a Three.js application (scene, camera, renderer, animation loop).
- The task involves scenes, cameras, renderers, transforms, resize handling, or object hierarchy basics.
- You need guidance on Three.js coordinate systems, math utilities (Vector3, Matrix4, Quaternion, Euler, Color), or common patterns like cleanup and loading managers.
- You want foundational Three.js guidance before working on specialized topics like shaders, post-processing, or advanced geometry manipulation.

## Prerequisites

- A JavaScript/TypeScript project with `three` installed (`npm install three`).
- Three.js r152+ for `outputColorSpace`; r183+ for `Timer` and experimental WebGPU renderer.
- A browser with WebGL support (or WebGPU for the experimental renderer path).

## Procedure

### 1. Create the Core Scene Structure

Set up scene, camera, renderer, a sample mesh, lighting, and the animation loop.

```javascript
import * as THREE from "three";

// Create scene, camera, renderer
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(
  75,
  window.innerWidth / window.innerHeight,
  0.1,
  1000,
);
const renderer = new THREE.WebGLRenderer({ antialias: true });

renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
document.body.appendChild(renderer.domElement);

// Add a mesh
const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshStandardMaterial({ color: 0x00ff00 });
const cube = new THREE.Mesh(geometry, material);
scene.add(cube);

// Add light
scene.add(new THREE.AmbientLight(0xffffff, 0.5));
const dirLight = new THREE.DirectionalLight(0xffffff, 1);
dirLight.position.set(5, 5, 5);
scene.add(dirLight);

camera.position.z = 5;

// Animation loop — prefer setAnimationLoop over manual requestAnimationFrame
renderer.setAnimationLoop(() => {
  cube.rotation.x += 0.01;
  cube.rotation.y += 0.01;
  renderer.render(scene, camera);
});

// Handle resize
window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
```

### 2. Configure the Scene

The `Scene` is the container for all 3D objects, lights, and cameras.

```javascript
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x000000); // Solid color
scene.background = texture;                   // Skybox texture
scene.background = cubeTexture;               // Cubemap
scene.environment = envMap;                   // Environment map for PBR
scene.fog = new THREE.Fog(0xffffff, 1, 100);  // Linear fog
scene.fog = new THREE.FogExp2(0xffffff, 0.02); // Exponential fog
```

### 3. Choose and Configure a Camera

**PerspectiveCamera** — most common, simulates human eye.

```javascript
// PerspectiveCamera(fov, aspect, near, far)
const camera = new THREE.PerspectiveCamera(
  75,                                      // Field of view (degrees)
  window.innerWidth / window.innerHeight,  // Aspect ratio
  0.1,                                     // Near clipping plane
  1000,                                    // Far clipping plane
);

camera.position.set(0, 5, 10);
camera.lookAt(0, 0, 0);
camera.updateProjectionMatrix(); // Call after changing fov, aspect, near, far
```

**OrthographicCamera** — no perspective distortion, good for 2D/isometric.

```javascript
// OrthographicCamera(left, right, top, bottom, near, far)
const aspect = window.innerWidth / window.innerHeight;
const frustumSize = 10;
const camera = new THREE.OrthographicCamera(
  (frustumSize * aspect) / -2,
  (frustumSize * aspect) / 2,
  frustumSize / 2,
  frustumSize / -2,
  0.1,
  1000,
);
```

**ArrayCamera** — multiple viewports with sub-cameras.

```javascript
const cameras = [];
for (let i = 0; i < 4; i++) {
  const subcamera = new THREE.PerspectiveCamera(40, 1, 0.1, 100);
  subcamera.viewport = new THREE.Vector4(
    Math.floor(i % 2) * 0.5,
    Math.floor(i / 2) * 0.5,
    0.5,
    0.5,
  );
  cameras.push(subcamera);
}
const arrayCamera = new THREE.ArrayCamera(cameras);
```

**CubeCamera** — renders environment maps for reflections.

```javascript
const cubeRenderTarget = new THREE.WebGLCubeRenderTarget(256);
const cubeCamera = new THREE.CubeCamera(0.1, 1000, cubeRenderTarget);
scene.add(cubeCamera);

// Use for reflections
material.envMap = cubeRenderTarget.texture;

// Update each frame (expensive!)
cubeCamera.position.copy(reflectiveMesh.position);
cubeCamera.update(renderer, scene);
```

### 4. Configure the WebGLRenderer

```javascript
const renderer = new THREE.WebGLRenderer({
  canvas: document.querySelector("#canvas"), // Optional existing canvas
  antialias: true,        // Smooth edges
  alpha: true,            // Transparent background
  powerPreference: "high-performance", // GPU hint
  preserveDrawingBuffer: true, // For screenshots
});

renderer.setSize(width, height);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

// Tone mapping
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;

// Color space (Three.js r152+)
renderer.outputColorSpace = THREE.SRGBColorSpace;

// Shadows
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

// Clear color
renderer.setClearColor(0x000000, 1);

// Render
renderer.render(scene, camera);
```

### 5. Work with Object3D, Group, and Mesh

**Object3D** is the base class for all 3D objects. `Mesh`, `Group`, `Light`, and `Camera` all extend `Object3D`.

```javascript
const obj = new THREE.Object3D();

// Transform
obj.position.set(x, y, z);
obj.rotation.set(x, y, z);           // Euler angles (radians)
obj.quaternion.set(x, y, z, w);      // Quaternion rotation
obj.scale.set(x, y, z);

// Local vs World transforms
obj.getWorldPosition(targetVector);
obj.getWorldQuaternion(targetQuaternion);
obj.getWorldDirection(targetVector);

// Hierarchy
obj.add(child);
obj.remove(child);
obj.parent;
obj.children;

// Visibility
obj.visible = false;

// Layers (for selective rendering/raycasting)
obj.layers.set(1);
obj.layers.enable(2);
obj.layers.disable(0);

// Traverse hierarchy
obj.traverse((child) => {
  if (child.isMesh) child.material.color.set(0xff0000);
});

// Matrix updates
obj.matrixAutoUpdate = true;     // Default: auto-update matrices
obj.updateMatrix();              // Manual matrix update
obj.updateMatrixWorld(true);     // Update world matrix recursively
```

**Group** — empty container for organizing objects.

```javascript
const group = new THREE.Group();
group.add(mesh1);
group.add(mesh2);
scene.add(group);

// Transform entire group
group.position.x = 5;
group.rotation.y = Math.PI / 4;
```

**Mesh** — combines geometry and material.

```javascript
const mesh = new THREE.Mesh(geometry, material);

// Multiple materials (one per geometry group)
const mesh = new THREE.Mesh(geometry, [material1, material2]);

// Useful properties
mesh.geometry;
mesh.material;
mesh.castShadow = true;
mesh.receiveShadow = true;

// Frustum culling
mesh.frustumCulled = true; // Default: skip if outside camera view

// Render order
mesh.renderOrder = 10; // Higher = rendered later
```

### 6. Understand the Coordinate System

Three.js uses a **right-handed coordinate system**:

- **+X** points right
- **+Y** points up
- **+Z** points toward viewer (out of screen)

```javascript
// Axes helper
const axesHelper = new THREE.AxesHelper(5);
scene.add(axesHelper); // Red=X, Green=Y, Blue=Z
```

### 7. Use Math Utilities

**Vector3**

```javascript
const v = new THREE.Vector3(x, y, z);
v.set(x, y, z);
v.copy(otherVector);
v.clone();

// Operations (modify in place)
v.add(v2);
v.sub(v2);
v.multiply(v2);
v.multiplyScalar(2);
v.divideScalar(2);
v.normalize();
v.negate();
v.clamp(min, max);
v.lerp(target, alpha);

// Calculations (return new value)
v.length();
v.lengthSq(); // Faster than length()
v.distanceTo(v2);
v.dot(v2);
v.cross(v2); // Modifies v
v.angleTo(v2);

// Transform
v.applyMatrix4(matrix);
v.applyQuaternion(q);
v.project(camera);    // World to NDC
v.unproject(camera);  // NDC to world
```

**Matrix4**

```javascript
const m = new THREE.Matrix4();
m.identity();
m.copy(other);
m.clone();

// Build transforms
m.makeTranslation(x, y, z);
m.makeRotationX(theta);
m.makeRotationY(theta);
m.makeRotationZ(theta);
m.makeRotationFromQuaternion(q);
m.makeScale(x, y, z);

// Compose/decompose
m.compose(position, quaternion, scale);
m.decompose(position, quaternion, scale);

// Operations
m.multiply(m2);    // m = m * m2
m.premultiply(m2); // m = m2 * m
m.invert();
m.transpose();

// Camera matrices
m.makePerspective(left, right, top, bottom, near, far);
m.makeOrthographic(left, right, top, bottom, near, far);
m.lookAt(eye, target, up);
```

**Quaternion**

```javascript
const q = new THREE.Quaternion();
q.setFromEuler(euler);
q.setFromAxisAngle(axis, angle);
q.setFromRotationMatrix(matrix);

q.multiply(q2);
q.slerp(target, t); // Spherical interpolation
q.normalize();
q.invert();
```

**Euler**

```javascript
const euler = new THREE.Euler(x, y, z, "XYZ"); // Order matters!
euler.setFromQuaternion(q);
euler.setFromRotationMatrix(m);

// Rotation orders: 'XYZ', 'YXZ', 'ZXY', 'XZY', 'YZX', 'ZYX'
```

**Color**

```javascript
const color = new THREE.Color(0xff0000);
const color = new THREE.Color("red");
const color = new THREE.Color("rgb(255, 0, 0)");
const color = new THREE.Color("#ff0000");

color.setHex(0x00ff00);
color.setRGB(r, g, b); // 0-1 range
color.setHSL(h, s, l); // 0-1 range

color.lerp(otherColor, alpha);
color.multiply(otherColor);
color.multiplyScalar(2);
```

**MathUtils**

```javascript
THREE.MathUtils.clamp(value, min, max);
THREE.MathUtils.lerp(start, end, alpha);
THREE.MathUtils.mapLinear(value, inMin, inMax, outMin, outMax);
THREE.MathUtils.degToRad(degrees);
THREE.MathUtils.radToDeg(radians);
THREE.MathUtils.randFloat(min, max);
THREE.MathUtils.randInt(min, max);
THREE.MathUtils.smoothstep(x, min, max);
THREE.MathUtils.smootherstep(x, min, max);
```

### 8. Implement Proper Cleanup

Always dispose geometries, materials, textures, and the renderer when tearing down a scene to avoid GPU memory leaks.

```javascript
function dispose() {
  // Dispose geometries
  mesh.geometry.dispose();

  // Dispose materials
  if (Array.isArray(mesh.material)) {
    mesh.material.forEach((m) => m.dispose());
  } else {
    mesh.material.dispose();
  }

  // Dispose textures
  texture.dispose();

  // Remove from scene
  scene.remove(mesh);

  // Dispose renderer
  renderer.dispose();
}
```

### 9. Use Timer or Clock for Frame-Rate-Independent Animation

**Timer (recommended in r183)** — pauses when tab is hidden, cleaner API:

```javascript
const timer = new THREE.Timer();

renderer.setAnimationLoop(() => {
  timer.update();
  const delta = timer.getDelta();
  const elapsed = timer.getElapsed();

  mesh.rotation.y += delta * 0.5;
  renderer.render(scene, camera);
});
```

**Clock (legacy, still works):**

```javascript
const clock = new THREE.Clock();

function animate() {
  const delta = clock.getDelta();        // Time since last frame (seconds)
  const elapsed = clock.getElapsedTime(); // Total time (seconds)

  mesh.rotation.y += delta * 0.5; // Consistent speed regardless of framerate

  requestAnimationFrame(animate);
  renderer.render(scene, camera);
}
```

### 10. Handle Responsive Canvas

```javascript
function onWindowResize() {
  const width = window.innerWidth;
  const height = window.innerHeight;

  camera.aspect = width / height;
  camera.updateProjectionMatrix();

  renderer.setSize(width, height);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
}
window.addEventListener("resize", onWindowResize);
```

### 11. Track Asset Loading with LoadingManager

```javascript
const manager = new THREE.LoadingManager();

manager.onStart = (url, loaded, total) => console.log("Started loading");
manager.onLoad = () => console.log("All loaded");
manager.onProgress = (url, loaded, total) => console.log(`${loaded}/${total}`);
manager.onError = (url) => console.error(`Error loading ${url}`);

const textureLoader = new THREE.TextureLoader(manager);
const gltfLoader = new GLTFLoader(manager);
```

### 12. Apply Performance Optimizations

1. **Limit draw calls**: Merge geometries, use instancing, atlas textures.
2. **Frustum culling**: Enabled by default; ensure bounding boxes are correct.
3. **LOD (Level of Detail)**: Use `THREE.LOD` for distance-based mesh switching.
4. **Object pooling**: Reuse objects instead of creating/destroying.
5. **Avoid `getWorldPosition` in loops**: Cache results.

```javascript
// Merge static geometries
import { mergeGeometries } from "three/examples/jsm/utils/BufferGeometryUtils.js";
const merged = mergeGeometries([geo1, geo2, geo3]);

// LOD
const lod = new THREE.LOD();
lod.addLevel(highDetailMesh, 0);
lod.addLevel(medDetailMesh, 50);
lod.addLevel(lowDetailMesh, 100);
scene.add(lod);
```

### 13. (Optional) Use the WebGPU Renderer (r183+)

Three.js includes an experimental WebGPU renderer as an alternative to WebGL:

```javascript
import { WebGPURenderer } from "three/addons/renderers/webgpu/WebGPURenderer.js";

const renderer = new WebGPURenderer({ antialias: true });
await renderer.init();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);
```

WebGPU uses TSL (Three.js Shading Language) instead of GLSL. The WebGL renderer remains the default and is fully supported.

## Pitfalls

- **Forgetting `updateProjectionMatrix()`**: After changing `fov`, `aspect`, `near`, or `far` on a camera, you must call `camera.updateProjectionMatrix()` or the change will not take effect.
- **Not capping pixel ratio**: Always use `renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))` — uncapped DPR on high-DPI devices causes severe performance degradation.
- **Memory leaks from missing disposal**: Failing to call `.dispose()` on geometries, materials, textures, and the renderer causes GPU memory leaks. This is critical in SPA route changes or scene rebuilds.
- **Euler rotation order**: Euler rotation order matters. Changing the default `"XYZ"` order can produce different results. Prefer quaternions for complex rotational interpolation.
- **`cross()` modifies in place**: `Vector3.cross(v2)` modifies the calling vector, not `v2`. Use `v.clone().cross(v2)` if you need to preserve the original.
- **CubeCamera is expensive**: Calling `cubeCamera.update(renderer, scene)` every frame is costly. Only update when the environment changes or throttle updates.
- **WebGPU is experimental**: The WebGPU renderer uses TSL, not GLSL. Existing GLSL shaders will not work. The WebGL renderer remains the default.
- **`preserveDrawingBuffer: true`** has a performance cost — only enable it when you need screenshots via `canvas.toDataURL()`.
- **`matrixAutoUpdate`**: If you set `obj.matrixAutoUpdate = false` for performance, you must manually call `obj.updateMatrix()` and `obj.updateMatrixWorld(true)` or transforms will not apply.

## Verification

1. **Confirm Three.js is installed and check version**:

   ```powershell
   npm list three
   ```

   Expected output shows `three@x.x.x` installed. Verify `x.x.x` meets your feature requirements (r152+ for `outputColorSpace`, r183+ for `Timer`/WebGPU).

2. **Verify the scene renders**: Open the page in a browser. You should see a green cube rotating on both X and Y axes against a black background.

3. **Check for console errors**: Open DevTools Console — no errors or warnings should appear. Common warnings to watch for:
   - `THREE.WebGLRenderer: ... is not a property of renderer` — indicates a typo or deprecated API.
   - Material/light mismatch causing a black mesh — `MeshStandardMaterial` requires lights; `MeshBasicMaterial` does not.

4. **Verify resize handling**: Resize the browser window. The canvas should fill the viewport and the cube should not distort (aspect ratio is corrected).

5. **Verify cleanup (if implemented)**: After calling your `dispose()` function, check that:
   - The canvas is removed or blank.
   - No `WebGL: CONTEXT_LOST` errors appear.
   - GPU memory is released (check via browser DevTools Memory tab or `performance.memory` in Chromium).

## Related Skills

- `threejs-geometry` — Geometry creation and manipulation
- `threejs-materials` — Material types and properties
- `threejs-lighting` — Light types and shadows
