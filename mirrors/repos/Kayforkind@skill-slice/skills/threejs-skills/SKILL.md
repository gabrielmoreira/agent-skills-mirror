---
name: threejs-skills
description: "Scaffolds vanilla Three.js r183 canvases: import maps or Vite, PerspectiveCamera, WebGLRenderer, MeshStandardMaterial plus lights, setAnimationLoop, OrbitControls, Points particles, and GLTFLoader. Use when the user wants a WebGL scene, rotating mesh, or interactive 3D element rather than a game or specialist pipeline. Not for routing ambitious graphics (threejs-skill-router) and not a playable Vite+TypeScript web-game stack (three-js-web-game)."
version: 1.0.1
risk: safe
source: "https://github.com/CloudAI-X/threejs-skills"
date_added: "2026-02-27"
---

# Three.js Skills

Systematically create high-quality 3D scenes and interactive experiences using Three.js best practices. Targets Three.js r183+ with modern ES module patterns.

## When to Use

- User requests 3D visualizations or graphics ("create a 3D model", "show in 3D")
- User wants interactive 3D experiences ("rotating cube", "explorable scene")
- User needs WebGL or canvas-based rendering
- User asks for animations, particles, or visual effects
- User mentions Three.js, WebGL, or 3D rendering by name
- User wants to visualize data in 3D space
- User needs post-processing, shaders, or portfolio-grade rendering

## Prerequisites

- **Runtime**: Modern browser with WebGL support (Chrome, Firefox, Edge, Safari)
- **Three.js version**: r183 or later (pinned in examples below)
- **For production builds**: Node.js 18+ and a bundler (Vite recommended)
- **Windows host (primary)**: PowerShell as default terminal. Use forward slashes in import maps and URLs; use backslashes only for local filesystem paths in PowerShell commands.
- **Optional references**: Load `references/postprocessing.md` when the user requests bloom, depth-of-field, or EffectComposer. Load `references/shaders.md` when the user requests custom GLSL/TSL shaders. Load `references/r3f.md` when the user explicitly asks for React Three Fiber.

## Procedure

### 1. Choose Import Strategy

**Import maps (quick prototypes, demos, embedded artifacts — no build step):**

```html
<script type="importmap">
{
  "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.183.0/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.183.0/examples/jsm/"
  }
}
</script>
<script type="module">
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
</script>
```

**Production build (Vite/webpack — client projects, portfolios, complex apps):**

```javascript
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
```

To scaffold a Vite project on Windows PowerShell:

```powershell
npm create vite@latest my-threejs-app -- --template vanilla
cd my-threejs-app
npm install three
npm run dev
```

### 2. Initialize Scene, Camera, Renderer

Every Three.js artifact needs these core components:

```javascript
// Scene — contains all 3D objects
const scene = new THREE.Scene();

// Camera — defines viewing perspective
const camera = new THREE.PerspectiveCamera(
  75,                                    // Field of view (degrees)
  window.innerWidth / window.innerHeight, // Aspect ratio
  0.1,                                   // Near clipping plane
  1000                                   // Far clipping plane
);
camera.position.z = 5;

// Renderer — draws the scene to canvas
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace; // NOT outputEncoding (renamed in r152)
document.body.appendChild(renderer.domElement);
```

### 3. Build Geometry and Apply Materials

**Basic shapes:**

| Geometry | Use case |
|---|---|
| `BoxGeometry` | Cubes, rectangular prisms |
| `SphereGeometry` | Spheres, planets |
| `CylinderGeometry` | Cylinders, tubes |
| `PlaneGeometry` | Flat surfaces, ground planes |
| `TorusGeometry` | Donuts, rings |
| `CapsuleGeometry` | Capsules (stable since r142) |

```javascript
const geometry = new THREE.SphereGeometry(1, 32, 32);
const material = new THREE.MeshStandardMaterial({
  color: 0x00ff00,
  metalness: 0.5,
  roughness: 0.5,
});
const mesh = new THREE.Mesh(geometry, material);
scene.add(mesh);
```

**Material quick reference:**

| Material | Lighting required | Use case |
|---|---|---|
| `MeshBasicMaterial` | No | Unlit flat colors, wireframes |
| `MeshStandardMaterial` | Yes | Physically-based, realistic PBR |
| `MeshPhongMaterial` | Yes | Shiny specular highlights |
| `MeshLambertMaterial` | Yes | Matte diffuse surfaces |

### 4. Add Lighting (If Using Lit Materials)

If using `MeshStandardMaterial`, `MeshPhongMaterial`, or `MeshLambertMaterial`, you **must** add lights. Skip lighting only for `MeshBasicMaterial`.

```javascript
const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
directionalLight.position.set(5, 5, 5);
scene.add(directionalLight);
```

### 5. Implement Animation Loop

Prefer `renderer.setAnimationLoop()` (handles WebXR compatibility):

```javascript
const timer = new THREE.Timer(); // r183: preferred over THREE.Clock

renderer.setAnimationLoop(() => {
  timer.update();
  const delta = timer.getDelta();

  mesh.rotation.x += delta * 0.5;
  mesh.rotation.y += delta * 0.5;

  renderer.render(scene, camera);
});
```

Alternative with `requestAnimationFrame`:

```javascript
function animate() {
  requestAnimationFrame(animate);
  mesh.rotation.x += 0.01;
  mesh.rotation.y += 0.01;
  renderer.render(scene, camera);
}
animate();
```

### 6. Handle Window Resize

Always add resize handling — omitting this causes distorted rendering when the browser window changes size:

```javascript
window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
```

### 7. Add Interaction (As Needed)

**OrbitControls (preferred for user-controlled camera):**

```javascript
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;

renderer.setAnimationLoop(() => {
  controls.update();
  renderer.render(scene, camera);
});
```

**Custom drag controls (lightweight, no addon import):**

```javascript
let isDragging = false;
let previousMousePosition = { x: 0, y: 0 };

renderer.domElement.addEventListener("mousedown", () => { isDragging = true; });
renderer.domElement.addEventListener("mouseup", () => { isDragging = false; });

renderer.domElement.addEventListener("mousemove", (event) => {
  if (isDragging) {
    const deltaX = event.clientX - previousMousePosition.x;
    const deltaY = event.clientY - previousMousePosition.y;
    camera.position.x += deltaX * 0.005;
    camera.position.y -= deltaY * 0.005;
    camera.lookAt(scene.position);
  }
  previousMousePosition = { x: event.clientX, y: event.clientY };
});

renderer.domElement.addEventListener("wheel", (event) => {
  event.preventDefault();
  camera.position.z += event.deltaY * 0.01;
  camera.position.z = Math.max(2, Math.min(20, camera.position.z)); // Clamp zoom
});
```

**Raycasting for object selection:**

```javascript
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
const clickableObjects = []; // Populate with meshes

window.addEventListener("mousemove", (event) => {
  mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
  mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
});

window.addEventListener("click", () => {
  raycaster.setFromCamera(mouse, camera);
  const intersects = raycaster.intersectObjects(clickableObjects);
  if (intersects.length > 0) {
    intersects[0].object.material.color.set(0xff0000);
  }
});
```

**Mouse-driven camera parallax:**

```javascript
let mouseX = 0, mouseY = 0;
document.addEventListener("mousemove", (event) => {
  mouseX = (event.clientX / window.innerWidth) * 2 - 1;
  mouseY = -(event.clientY / window.innerHeight) * 2 + 1;
});

// In animation loop:
camera.position.x = mouseX * 2;
camera.position.y = mouseY * 2;
camera.lookAt(scene.position);
```

### 8. Add Visual Polish (Portfolio-Grade)

**Shadows:**

```javascript
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

directionalLight.castShadow = true;
directionalLight.shadow.mapSize.width = 2048;
directionalLight.shadow.mapSize.height = 2048;
directionalLight.shadow.camera.near = 0.5;
directionalLight.shadow.camera.far = 50;

mesh.castShadow = true;
mesh.receiveShadow = true;

// Ground plane receives shadows
const ground = new THREE.Mesh(
  new THREE.PlaneGeometry(20, 20),
  new THREE.MeshStandardMaterial({ color: 0x808080 })
);
ground.rotation.x = -Math.PI / 2;
ground.receiveShadow = true;
scene.add(ground);
```

**Tone mapping:**

```javascript
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;
renderer.outputColorSpace = THREE.SRGBColorSpace;
```

**Fog for depth:**

```javascript
scene.fog = new THREE.Fog(0xcccccc, 10, 50);        // Linear: color, near, far
// or
scene.fog = new THREE.FogExp2(0xcccccc, 0.02);       // Exponential: color, density
```

**Environment maps for reflections:**

```javascript
const loader = new THREE.CubeTextureLoader();
const envMap = loader.load(["px.jpg","nx.jpg","py.jpg","ny.jpg","pz.jpg","nz.jpg"]);
scene.environment = envMap;  // Affects all PBR materials
scene.background = envMap;   // Optional: use as skybox

const reflectiveMaterial = new THREE.MeshStandardMaterial({
  metalness: 1.0,
  roughness: 0.1,
  envMap: envMap,
});
```

### 9. Particle Systems

```javascript
const particlesGeometry = new THREE.BufferGeometry();
const particlesCount = 1000;
const posArray = new Float32Array(particlesCount * 3);

for (let i = 0; i < particlesCount * 3; i++) {
  posArray[i] = (Math.random() - 0.5) * 10;
}

particlesGeometry.setAttribute("position", new THREE.BufferAttribute(posArray, 3));

const particlesMaterial = new THREE.PointsMaterial({ size: 0.02, color: 0xffffff });
const particlesMesh = new THREE.Points(particlesGeometry, particlesMaterial);
scene.add(particlesMesh);
```

### 10. Load Textures and Models

**Textures:**

```javascript
const textureLoader = new THREE.TextureLoader();
const texture = textureLoader.load("texture-url.jpg");
const material = new THREE.MeshStandardMaterial({ map: texture });
```

**GLTF models:**

```javascript
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

const loader = new GLTFLoader();
loader.load("model.gltf", (gltf) => {
  scene.add(gltf.scene);
  gltf.scene.traverse((child) => {
    if (child.isMesh) {
      child.castShadow = true;
      child.receiveShadow = true;
    }
  });
});
```

### 11. Performance Optimization (Production)

**Level of Detail (LOD):**

```javascript
const lod = new THREE.LOD();
lod.addLevel(highDetailMesh, 0);    // Close up
lod.addLevel(mediumDetailMesh, 10); // Medium distance
lod.addLevel(lowDetailMesh, 50);    // Far away
scene.add(lod);
```

**Instanced meshes for many identical objects:**

```javascript
const geometry = new THREE.BoxGeometry();
const material = new THREE.MeshStandardMaterial();
const instancedMesh = new THREE.InstancedMesh(geometry, material, 1000);

const matrix = new THREE.Matrix4();
for (let i = 0; i < 1000; i++) {
  matrix.setPosition(Math.random() * 100, Math.random() * 100, Math.random() * 100);
  instancedMesh.setMatrixAt(i, matrix);
}
```

**Resource disposal (when removing objects):**

```javascript
geometry.dispose();
material.dispose();
texture.dispose();
```

### 12. GSAP Integration (Advanced Animations)

```javascript
import gsap from "gsap";

gsap.to(mesh.position, { x: 5, duration: 2, ease: "power2.inOut" });

// Complex timeline sequences:
const timeline = gsap.timeline();
timeline
  .to(mesh.rotation, { y: Math.PI * 2, duration: 2 })
  .to(mesh.scale, { x: 2, y: 2, z: 2, duration: 1 }, "-=1");
```

### 13. Scroll-Based Interactions

```javascript
let scrollY = window.scrollY;
window.addEventListener("scroll", () => { scrollY = window.scrollY; });

// In animation loop:
mesh.rotation.y = scrollY * 0.001;
camera.position.y = -(scrollY / window.innerHeight) * 10;
```

Advanced scroll libraries: ScrollTrigger (GSAP plugin), Locomotive Scroll, Lenis smooth scroll.

### 14. WebGPU Renderer (Alternative, r183+)

Three.js r183 includes a WebGPU renderer as an alternative to WebGL. WebGPU uses TSL (Three.js Shading Language) instead of GLSL for custom shaders.

```javascript
import { WebGPURenderer } from "three/addons/renderers/webgpu/WebGPURenderer.js";

const renderer = new WebGPURenderer({ antialias: true });
await renderer.init();
renderer.setSize(window.innerWidth, window.innerHeight);
```

Load `references/shaders.md` for TSL shader authoring details.

### 15. Group Objects

```javascript
const group = new THREE.Group();
group.add(mesh1);
group.add(mesh2);
group.rotation.y = Math.PI / 4;
scene.add(group);
```

### 16. Custom Geometry from Vertices

```javascript
const geometry = new THREE.BufferGeometry();
const vertices = new Float32Array([-1, -1, 0,  1, -1, 0,  1, 1, 0]);
geometry.setAttribute("position", new THREE.BufferAttribute(vertices, 3));
```

## Examples

### Example Workflow: Interactive 3D Sphere Responding to Mouse

User: "Create an interactive 3D sphere that responds to mouse movement"

1. **Setup**: Import Three.js via import map, create scene/camera/renderer
2. **Geometry**: `new THREE.SphereGeometry(1, 32, 32)` for smooth sphere
3. **Material**: `MeshStandardMaterial` for realistic look
4. **Lighting**: Add `AmbientLight` + `DirectionalLight`
5. **Interaction**: Track mouse position, update camera position in animation loop
6. **Animation**: Rotate sphere, render continuously with `setAnimationLoop`
7. **Responsive**: Add window resize handler
8. **Result**: Smooth, interactive 3D sphere

### Recommended Production Stack

```
Three.js r183 + Vite
├── GSAP (animations)
├── React Three Fiber (optional — React integration)
├── Drei (helper components)
├── Leva (debug GUI)
└── Post-processing effects
```

### When to Use Which Approach

| Approach | When |
|---|---|
| Import maps | Quick prototypes, demos, educational content, embedded artifacts, no build step |
| Production build (Vite) | Client projects, portfolios, complex apps, performance-critical, team collaboration |

## Pitfalls

- **Using `outputEncoding` instead of `outputColorSpace`**: Renamed in r152. Always use `renderer.outputColorSpace = THREE.SRGBColorSpace`.
- **Forgetting `scene.add()`**: Objects created but never added to scene will not render.
- **Using lit materials without lights**: `MeshStandardMaterial`, `MeshPhongMaterial`, and `MeshLambertMaterial` require lights. Without them, objects appear black.
- **Not handling window resize**: Causes distorted aspect ratios when the browser window changes.
- **Forgetting `renderer.render()` in animation loop**: The scene will never draw.
- **Using `THREE.Clock` without considering `THREE.Timer`**: `THREE.Timer` is recommended as of r183 — it pauses when tab is hidden and integrates better with `setAnimationLoop`.
- **Camera position inside objects**: If the camera is too close or inside a mesh, nothing will be visible. Verify camera position relative to object scale.
- **Camera far plane too small**: Objects beyond the far clipping plane won't render. Ensure `far` value includes all scene objects.
- **Excessive particle counts**: Start with 1,000–5,000 particles for 60fps. Higher counts require performance testing.
- **Not disposing resources**: When removing objects, call `.dispose()` on geometry, material, and texture to prevent memory leaks.
- **Overlapping bright lights**: Multiple high-intensity lights cause blown-out surfaces. Use ambient + one directional as a baseline.
- **Importing addons from wrong path**: Use `three/addons/` (import map) or `three/examples/jsm/` (npm). Mixing paths causes module resolution errors.

## Verification

1. **Check rendering**: Open the HTML file in a browser. The 3D scene should be visible immediately.

```powershell
# If using Vite, verify dev server starts:
npm run dev
# Expected: Vite prints "Local: http://localhost:5173" and serves without errors
```

2. **Check browser console**: Open DevTools (F12) → Console. No red errors should appear. Common errors to watch for:
   - `THREE.WebGLRenderer: outputEncoding is not a property` → Use `outputColorSpace`
   - `Failed to resolve module specifier "three"` → Import map is missing or malformed
   - `Cannot read properties of undefined (reading 'position')` → Object not added to scene

3. **Check responsiveness**: Resize the browser window. The canvas should resize without distortion.

4. **Check animation**: The scene should animate smoothly at ~60fps. Open DevTools → Performance tab to verify frame rate.

5. **Check interaction**: If OrbitControls or custom controls are implemented, verify mouse drag rotates the scene and scroll wheel zooms.

6. **Verify no memory leaks**: If objects are dynamically added/removed, check DevTools → Memory tab for growing heap usage (indicates missing `.dispose()` calls).

## Related Skills

- **threejs-postprocessing**: EffectComposer, bloom, depth-of-field, and post-processing effects. Load `references/postprocessing.md` when user requests these.
- **threejs-shaders**: Custom GLSL/WebGL shaders and TSL (Three.js Shading Language) for WebGPU. Load `references/shaders.md` when user requests custom shaders.
- **threejs-r3f**: React Three Fiber integration for React-based 3D apps. Load `references/r3f.md` when user explicitly asks for React Three Fiber.

## Limitations

- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
