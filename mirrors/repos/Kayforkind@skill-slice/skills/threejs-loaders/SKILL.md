---
name: threejs-loaders
description: "Loads Three.js assets: GLTFLoader/GLB, TextureLoader, RGBE/EXR, OBJ/FBX/STL/PLY, Draco/KTX2/Meshopt, LoadingManager, and dispose/cache. Use when loading models, HDR environments, compressed glTF, or progress/retry orchestration. Not for scene/camera/renderer bootstrap (threejs-fundamentals), materials/shaders, or authoring geometry. Never skip decoder/transcoder paths for Draco/KTX2 or leak GPU memory by omitting dispose()."
version: 1.0.1
risk: unknown
source: community
---

# Three.js Loaders

## When to Use
- You need to load models, textures, HDR/EXR assets, or other external resources in Three.js.
- The task involves `GLTFLoader`, `TextureLoader`, `RGBELoader`, `EXRLoader`, `DRACOLoader`, `KTX2Loader`, `MeshoptDecoder`, `LoadingManager`, or async asset orchestration.
- You are managing scene assets (loading, caching, disposing) rather than authoring geometry or shaders directly.
- You need loading progress bars, retry/fallback logic, or batched asset loading with `Promise.all`.

## Prerequisites
- A Three.js project with `three` installed (import paths assume `three/addons/...` or `three/examples/jsm/...`).
- A renderer instance is required before using `PMREMGenerator`, `KTX2Loader.detectSupport(renderer)`, or `renderer.capabilities.getMaxAnisotropy()`.
- For Draco-compressed GLB: a decoder path must be configured (CDN or local copy).
- For KTX2 textures: a transcoder path must be configured and renderer support detected.
- For Meshopt (r183+): import `MeshoptDecoder` and pass it to the GLTF loader.

## Procedure

### 1. Basic GLTF/GLB Loading

```javascript
import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

const loader = new GLTFLoader();

loader.load("model.glb", (gltf) => {
  const model = gltf.scene;
  scene.add(model);

  // Animations
  const animations = gltf.animations;
  if (animations.length > 0) {
    const mixer = new THREE.AnimationMixer(model);
    animations.forEach((clip) => {
      mixer.clipAction(clip).play();
    });
  }

  // Cameras and asset info from the file
  const cameras = gltf.cameras;
  console.log(gltf.asset);   // Version, generator, etc.
  console.log(gltf.userData); // Custom data from Blender/etc.
});
```

### 2. Coordinate Multiple Loaders with LoadingManager

Use a `LoadingManager` to track aggregate progress across multiple loaders and fire a single `onLoad` when all assets are done.

```javascript
const manager = new THREE.LoadingManager();

manager.onStart = (url, loaded, total) => {
  console.log(`Started loading: ${url}`);
};

manager.onLoad = () => {
  console.log("All assets loaded!");
  startGame();
};

manager.onProgress = (url, loaded, total) => {
  const progress = (loaded / total) * 100;
  console.log(`Loading: ${progress.toFixed(1)}%`);
  updateProgressBar(progress);
};

manager.onError = (url) => {
  console.error(`Error loading: ${url}`);
};

const textureLoader = new THREE.TextureLoader(manager);
const gltfLoader = new GLTFLoader(manager);

textureLoader.load("texture1.jpg");
textureLoader.load("texture2.jpg");
gltfLoader.load("model.glb");
// onLoad fires when ALL are complete
```

### 3. Texture Loading and Configuration

```javascript
const loader = new THREE.TextureLoader();

// Callback style
loader.load(
  "texture.jpg",
  (texture) => {
    material.map = texture;
    material.needsUpdate = true;
  },
  undefined, // onProgress is NOT supported for image loading
  (error) => {
    console.error("Error loading texture", error);
  },
);

// Synchronous return (loads async internally)
const texture = loader.load("texture.jpg");
material.map = texture;
```

Configure color space, wrapping, filtering, and anisotropy:

```javascript
const texture = loader.load("texture.jpg", (tex) => {
  // Color space — critical for accuracy
  tex.colorSpace = THREE.SRGBColorSpace;          // For color/albedo maps
  // tex.colorSpace = THREE.LinearSRGBColorSpace; // For data maps (normal, roughness)

  // Wrapping
  tex.wrapS = THREE.RepeatWrapping;
  tex.wrapT = THREE.RepeatWrapping;
  // Alternatives: ClampToEdgeWrapping, MirroredRepeatWrapping

  // Repeat / offset / rotation
  tex.repeat.set(2, 2);
  tex.offset.set(0.5, 0.5);
  tex.rotation = Math.PI / 4;
  tex.center.set(0.5, 0.5);

  // Filtering
  tex.minFilter = THREE.LinearMipmapLinearFilter; // Default
  tex.magFilter = THREE.LinearFilter;             // Default
  // NearestFilter — pixelated; LinearFilter — smooth; LinearMipmapLinearFilter — smooth + mipmaps

  // Anisotropic filtering (sharper at grazing angles)
  tex.anisotropy = renderer.capabilities.getMaxAnisotropy();

  tex.flipY = true; // Usually true for standard textures
  tex.needsUpdate = true;
});
```

### 4. CubeTextureLoader (Skybox / Environment)

```javascript
const loader = new THREE.CubeTextureLoader();

const cubeTexture = loader.load([
  "px.jpg", "nx.jpg", // +X / -X
  "py.jpg", "ny.jpg", // +Y / -Y
  "pz.jpg", "nz.jpg", // +Z / -Z
]);

scene.background = cubeTexture;
scene.environment = cubeTexture;
material.envMap = cubeTexture;
```

### 5. HDR / EXR Environment Loading

```javascript
import { RGBELoader } from "three/addons/loaders/RGBELoader.js";
import { EXRLoader } from "three/addons/loaders/EXRLoader.js";

// HDR
new RGBELoader().load("environment.hdr", (texture) => {
  texture.mapping = THREE.EquirectangularReflectionMapping;
  scene.environment = texture;
  scene.background = texture;
});

// EXR
new EXRLoader().load("environment.exr", (texture) => {
  texture.mapping = THREE.EquirectangularReflectionMapping;
  scene.environment = texture;
});
```

### 6. PMREMGenerator (Prefiltered PBR Environment)

```javascript
import { RGBELoader } from "three/addons/loaders/RGBELoader.js";

const pmremGenerator = new THREE.PMREMGenerator(renderer);
pmremGenerator.compileEquirectangularShader();

new RGBELoader().load("environment.hdr", (texture) => {
  const envMap = pmremGenerator.fromEquirectangular(texture).texture;

  scene.environment = envMap;
  scene.background = envMap;

  texture.dispose();
  pmremGenerator.dispose();
});
```

### 7. GLTF with Draco Compression

```javascript
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { DRACOLoader } from "three/addons/loaders/DRACOLoader.js";

const dracoLoader = new DRACOLoader();
dracoLoader.setDecoderPath("https://www.gstatic.com/draco/versioned/decoders/1.5.6/");
dracoLoader.preload();

const gltfLoader = new GLTFLoader();
gltfLoader.setDRACOLoader(dracoLoader);

gltfLoader.load("compressed-model.glb", (gltf) => {
  scene.add(gltf.scene);
});
```

### 8. GLTF with KTX2 Textures

```javascript
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { KTX2Loader } from "three/addons/loaders/KTX2Loader.js";

const ktx2Loader = new KTX2Loader();
ktx2Loader.setTranscoderPath(
  "https://cdn.jsdelivr.net/npm/three@0.183.0/examples/jsm/libs/basis/",
);
ktx2Loader.detectSupport(renderer);

const gltfLoader = new GLTFLoader();
gltfLoader.setKTX2Loader(ktx2Loader);

gltfLoader.load("model-with-ktx2.glb", (gltf) => {
  scene.add(gltf.scene);
});
```

### 9. GLTF with Meshopt Compression (r183+)

`KHR_meshopt_compression` is an alternative to Draco that often provides better compression for animated meshes and preserves mesh topology.

```javascript
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { MeshoptDecoder } from "three/addons/libs/meshopt_decoder.module.js";

const gltfLoader = new GLTFLoader();
gltfLoader.setMeshoptDecoder(MeshoptDecoder);

gltfLoader.load("compressed-model.glb", (gltf) => {
  scene.add(gltf.scene);
});
```

### 10. Process GLTF Content (Shadows, Centering, Scaling)

```javascript
loader.load("model.glb", (gltf) => {
  const model = gltf.scene;

  // Enable shadows on all meshes
  model.traverse((child) => {
    if (child.isMesh) {
      child.castShadow = true;
      child.receiveShadow = true;
    }
  });

  // Find a specific named object
  const head = model.getObjectByName("Head");

  // Adjust material envMap intensity
  model.traverse((child) => {
    if (child.isMesh && child.material) {
      child.material.envMapIntensity = 0.5;
    }
  });

  // Center and normalize scale
  const box = new THREE.Box3().setFromObject(model);
  const center = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3());

  model.position.sub(center);
  const maxDim = Math.max(size.x, size.y, size.z);
  model.scale.setScalar(1 / maxDim);

  scene.add(model);
});
```

### 11. Other Model Formats

**OBJ + MTL:**

```javascript
import { OBJLoader } from "three/addons/loaders/OBJLoader.js";
import { MTLLoader } from "three/addons/loaders/MTLLoader.js";

const mtlLoader = new MTLLoader();
mtlLoader.load("model.mtl", (materials) => {
  materials.preload();

  const objLoader = new OBJLoader();
  objLoader.setMaterials(materials);
  objLoader.load("model.obj", (object) => {
    scene.add(object);
  });
});
```

**FBX** (often has large scale — adjust accordingly):

```javascript
import { FBXLoader } from "three/addons/loaders/FBXLoader.js";

const loader = new FBXLoader();
loader.load("model.fbx", (object) => {
  object.scale.setScalar(0.01);

  const mixer = new THREE.AnimationMixer(object);
  object.animations.forEach((clip) => {
    mixer.clipAction(clip).play();
  });

  scene.add(object);
});
```

**STL** (returns geometry, not a scene object):

```javascript
import { STLLoader } from "three/addons/loaders/STLLoader.js";

const loader = new STLLoader();
loader.load("model.stl", (geometry) => {
  const material = new THREE.MeshStandardMaterial({ color: 0x888888 });
  const mesh = new THREE.Mesh(geometry, material);
  scene.add(mesh);
});
```

**PLY** (returns geometry; compute vertex normals if needed):

```javascript
import { PLYLoader } from "three/addons/loaders/PLYLoader.js";

const loader = new PLYLoader();
loader.load("model.ply", (geometry) => {
  geometry.computeVertexNormals();
  const material = new THREE.MeshStandardMaterial({ vertexColors: true });
  const mesh = new THREE.Mesh(geometry, material);
  scene.add(mesh);
});
```

### 12. Async / Promise-Based Loading

Promisify a loader for `async/await` usage:

```javascript
function loadModel(url) {
  return new Promise((resolve, reject) => {
    loader.load(url, resolve, undefined, reject);
  });
}

async function init() {
  try {
    const gltf = await loadModel("model.glb");
    scene.add(gltf.scene);
  } catch (error) {
    console.error("Failed to load model:", error);
  }
}
```

Load multiple assets in parallel:

```javascript
async function loadAssets() {
  const [modelGltf, envTexture, colorTexture] = await Promise.all([
    loadGLTF("model.glb"),
    loadRGBE("environment.hdr"),
    loadTexture("color.jpg"),
  ]);

  scene.add(modelGltf.scene);
  scene.environment = envTexture;
  material.map = colorTexture;
}

function loadGLTF(url) {
  return new Promise((resolve, reject) => {
    new GLTFLoader().load(url, resolve, undefined, reject);
  });
}

function loadRGBE(url) {
  return new Promise((resolve, reject) => {
    new RGBELoader().load(
      url,
      (texture) => {
        texture.mapping = THREE.EquirectangularReflectionMapping;
        resolve(texture);
      },
      undefined,
      reject,
    );
  });
}

function loadTexture(url) {
  return new Promise((resolve, reject) => {
    new THREE.TextureLoader().load(url, resolve, undefined, reject);
  });
}
```

### 13. Caching

Built-in cache:

```javascript
THREE.Cache.enabled = true;
THREE.Cache.clear();
THREE.Cache.add("key", data);
THREE.Cache.get("key");
THREE.Cache.remove("key");
```

Custom asset manager with deduplication and cloning:

```javascript
class AssetManager {
  constructor() {
    this.textures = new Map();
    this.models = new Map();
    this.gltfLoader = new GLTFLoader();
    this.textureLoader = new THREE.TextureLoader();
  }

  async loadTexture(key, url) {
    if (this.textures.has(key)) return this.textures.get(key);
    const texture = await new Promise((resolve, reject) => {
      this.textureLoader.load(url, resolve, undefined, reject);
    });
    this.textures.set(key, texture);
    return texture;
  }

  async loadModel(key, url) {
    if (this.models.has(key)) return this.models.get(key).clone();
    const gltf = await new Promise((resolve, reject) => {
      this.gltfLoader.load(url, resolve, undefined, reject);
    });
    this.models.set(key, gltf.scene);
    return gltf.scene.clone();
  }

  dispose() {
    this.textures.forEach((t) => t.dispose());
    this.textures.clear();
    this.models.clear();
  }
}

const assets = new AssetManager();
const texture = await assets.loadTexture("brick", "brick.jpg");
const model = await assets.loadModel("tree", "tree.glb");
```

### 14. Loading from Different Sources

**Data URL / Base64:**

```javascript
const texture = new THREE.TextureLoader().load("data:image/png;base64,iVBORw0KGgo...");
```

**Blob URL** (revoke after use):

```javascript
async function loadFromBlob(blob) {
  const url = URL.createObjectURL(blob);
  const texture = await loadTexture(url);
  URL.revokeObjectURL(url);
  return texture;
}
```

**ArrayBuffer** (parse directly without a network request):

```javascript
const response = await fetch("model.glb");
const buffer = await response.arrayBuffer();

const loader = new GLTFLoader();
loader.parse(buffer, "", (gltf) => {
  scene.add(gltf.scene);
});
```

**Custom path / URL modifier:**

```javascript
loader.setPath("assets/models/");
loader.load("model.glb"); // Loads from assets/models/model.glb

loader.setResourcePath("assets/textures/"); // For textures referenced inside model

manager.setURLModifier((url) => `https://cdn.example.com/${url}`);
```

### 15. Error Handling (Fallback, Retry, Timeout)

```javascript
// Graceful fallback
async function loadWithFallback(primaryUrl, fallbackUrl) {
  try {
    return await loadModel(primaryUrl);
  } catch (error) {
    console.warn(`Primary failed, trying fallback: ${error}`);
    return await loadModel(fallbackUrl);
  }
}

// Retry with backoff
async function loadWithRetry(url, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await loadModel(url);
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await new Promise((r) => setTimeout(r, 1000 * (i + 1)));
    }
  }
}

// Timeout via AbortController
async function loadWithTimeout(url, timeout = 30000) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);
  try {
    const response = await fetch(url, { signal: controller.signal });
    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    if (error.name === "AbortError") throw new Error("Loading timed out");
    throw error;
  }
}
```

### 16. Progressive Loading with Placeholder

```javascript
const placeholder = new THREE.Mesh(
  new THREE.BoxGeometry(1, 1, 1),
  new THREE.MeshBasicMaterial({ wireframe: true }),
);
scene.add(placeholder);

loadModel("model.glb").then((gltf) => {
  scene.remove(placeholder);
  scene.add(gltf.scene);
});
```

## Pitfalls

1. **TextureLoader does not support `onProgress`** — the third argument to `load()` is ignored for image loading. Use `LoadingManager.onProgress` for aggregate progress instead.
2. **Color space mismatch** — color/albedo maps must use `THREE.SRGBColorSpace`; data maps (normal, roughness, metallic) must use `THREE.LinearSRGBColorSpace`. Wrong assignment causes washed-out or incorrect lighting.
3. **Forgetting `needsUpdate`** — after changing texture properties (wrap, filter, colorSpace) post-load, set `texture.needsUpdate = true` or changes won't apply.
4. **DRACOLoader decoder path mismatch** — the path must end with a `/` and point to the correct versioned decoder directory. A wrong path silently fails on load.
5. **KTX2Loader requires renderer support detection** — call `ktx2Loader.detectSupport(renderer)` before loading or transcoding will fail.
6. **FBX scale is often huge** — FBX files frequently import at 100x expected scale; set `object.scale.setScalar(0.01)` or similar.
7. **STL/PLY return geometry, not objects** — you must create a `Mesh` with a material yourself; there is no embedded material or scene graph.
8. **PMREMGenerator and source texture must be disposed** — after `fromEquirectangular()`, dispose both the source HDR texture and the PMREMGenerator to avoid GPU memory leaks.
9. **Blob URLs must be revoked** — call `URL.revokeObjectURL(url)` after loading or memory leaks accumulate.
10. **`THREE.Cache` is disabled by default** — set `THREE.Cache.enabled = true` explicitly if you rely on it.
11. **Meshopt requires r183+** — `MeshoptDecoder` import path and `setMeshoptDecoder` API are only available in r183 and later.
12. **VRMLLoader camera support is r183+** — cameras defined in VRML files are only loaded starting r183.

## Verification

1. **Confirm loader imports resolve:**

```powershell
# Check that the addons path exists in your node_modules
Test-Path "node_modules/three/examples/jsm/loaders/GLTFLoader.js"
Test-Path "node_modules/three/examples/jsm/loaders/DRACOLoader.js"
Test-Path "node_modules/three/examples/jsm/loaders/KTX2Loader.js"
```

Expected output: `True` for each.

2. **Verify a model loads without errors** — open browser DevTools Console and check for:

```
All assets loaded!
```

(from `LoadingManager.onLoad`) with no `Error loading:` messages.

3. **Verify texture color space at runtime:**

```javascript
console.log(texture.colorSpace === THREE.SRGBColorSpace); // true for albedo
```

4. **Verify Draco decoder loaded** — in DevTools Network tab, confirm requests to the decoder path (e.g., `draco_decoder.wasm`) returned HTTP 200.

5. **Verify no GPU memory leak** — after disposing a model:

```javascript
model.traverse((child) => {
  if (child.isMesh) {
    child.geometry.dispose();
    if (child.material.map) child.material.map.dispose();
    child.material.dispose();
  }
});
renderer.info.memory; // geometries and textures counts should drop
```

6. **Verify Meshopt availability (r183+):**

```powershell
# Check three.js version
node -e "console.log(require('three/package.json').version)"
```

Expected: `0.183.0` or higher.

## Performance Tips

1. **Use compressed formats** — DRACO for geometry, KTX2/Basis for textures.
2. **Load progressively** — show placeholder geometry while real assets load.
3. **Lazy load** — only load assets needed for the current scene/view.
4. **Use a CDN** — faster asset delivery and caching.
5. **Enable cache** — `THREE.Cache.enabled = true` to avoid re-fetching.

## Related Skills

- `threejs-textures` — Texture configuration and advanced sampling
- `threejs-animation` — Playing and blending loaded animations
- `threejs-materials` — Working with materials from loaded models

## Limitations
- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
