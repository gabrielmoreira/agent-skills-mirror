---
name: threejs-textures
description: Configures Three.js textures via TextureLoader, colorSpace (sRGB vs data maps), wrap/repeat/anisotropy, PBR maps, UVs, cubemaps, and HDR environment maps. Use when loading images onto materials, fixing washed colors, or optimizing texture memory. Not for scene, camera, or renderer scaffolding (threejs-fundamentals) and not for routing to other Three.js specialists (threejs-skill-router). Do not set SRGBColorSpace on normal, roughness, or metalness maps.
version: 1.0.1
---

## When to Use
- You need to load, configure, or optimize textures in Three.js.
- The task involves UV mapping, texture settings, cubemaps, environment maps, or HDR texture workflows.
- You are working on surface detail and material inputs rather than geometry or animation.

## Prerequisites
- Three.js installed in the project (`npm install three`).
- Basic understanding of Three.js scenes, meshes, and materials.

## Procedure

### 1. Load Textures
Use `TextureLoader` for standard image formats. For multiple textures, wrap in a Promise or use `LoadingManager`.

```javascript
import * as THREE from "three";

const loader = new THREE.TextureLoader();

// Async with callbacks
loader.load(
  "texture.jpg",
  (texture) => console.log("Loaded"),
  (progress) => console.log("Progress"),
  (error) => console.error("Error"),
);

// Promise wrapper for parallel loading
function loadTexture(url) {
  return new Promise((resolve, reject) => {
    new THREE.TextureLoader().load(url, resolve, undefined, reject);
  });
}

const [colorMap, normalMap, roughnessMap] = await Promise.all([
  loadTexture("color.jpg"),
  loadTexture("normal.jpg"),
  loadTexture("roughness.jpg"),
]);
```

### 2. Configure Color Space
Set `colorSpace` correctly to ensure accurate color reproduction.

```javascript
// Color/albedo textures - use sRGB
colorTexture.colorSpace = THREE.SRGBColorSpace;

// Data textures (normal, roughness, metalness, AO) - leave as default
// Do NOT set colorSpace for data textures (NoColorSpace is default)
```

### 3. Set Wrapping, Repeat, and Filtering
Configure how textures tile across surfaces and how they are sampled.

```javascript
// Wrapping
texture.wrapS = THREE.RepeatWrapping; // Horizontal
texture.wrapT = THREE.RepeatWrapping; // Vertical

// Repeat/Offset
texture.repeat.set(4, 4); // Tile 4x4
texture.offset.set(0.5, 0.5);
texture.rotation = Math.PI / 4; // Radians
texture.center.set(0.5, 0.5); // Rotation pivot

// Filtering
texture.minFilter = THREE.LinearMipmapLinearFilter; // Default, smooth
texture.magFilter = THREE.LinearFilter; // Smooth (default)
texture.anisotropy = renderer.capabilities.getMaxAnisotropy(); // Sharper at angles
```

### 4. Apply PBR Texture Maps
Assign textures to `MeshStandardMaterial` properties.

```javascript
const material = new THREE.MeshStandardMaterial({
  map: colorTexture, // sRGB
  normalMap: normalTexture, // Linear
  normalScale: new THREE.Vector2(1, 1),
  roughnessMap: roughnessTexture, // Linear
  metalnessMap: metalnessTexture, // Linear
  aoMap: aoTexture, // Linear, requires UV2
  aoMapIntensity: 1,
  emissiveMap: emissiveTexture, // sRGB
  emissive: 0xffffff,
  emissiveIntensity: 1,
});

// Don't forget UV2 for AO
geometry.setAttribute("uv2", geometry.attributes.uv);
```

### 5. Load HDR and Environment Maps
Use `RGBELoader` or `EXRLoader` for HDR environments. Use `PMREMGenerator` for cubemaps.

```javascript
import { RGBELoader } from "three/examples/jsm/loaders/RGBELoader.js";

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

### 6. Compressed Textures (KTX2)
Use `KTX2Loader` for GPU-compressed textures to save memory and bandwidth.

```javascript
import { KTX2Loader } from "three/examples/jsm/loaders/KTX2Loader.js";

const ktx2Loader = new KTX2Loader();
ktx2Loader.setTranscoderPath("path/to/basis/");
ktx2Loader.detectSupport(renderer);

ktx2Loader.load("texture.ktx2", (texture) => {
  material.map = texture;
});
```

### 7. Manage Texture Memory
Dispose of textures when they are no longer needed to prevent memory leaks.

```javascript
// Single texture
texture.dispose();

// Material textures
function disposeMaterial(material) {
  const maps = [
    "map", "normalMap", "roughnessMap", "metalnessMap", "aoMap",
    "emissiveMap", "displacementMap", "alphaMap", "envMap",
    "lightMap", "bumpMap", "specularMap",
  ];

  maps.forEach((mapName) => {
    if (material[mapName]) {
      material[mapName].dispose();
    }
  });

  material.dispose();
}
```

## Pitfalls
- **Incorrect Color Space**: Forgetting to set `THREE.SRGBColorSpace` on color maps results in washed-out or dark textures. Do not set it for data maps (normal, roughness).
- **Missing UV2 for AO**: `aoMap` requires a second UV channel. Always run `geometry.setAttribute("uv2", geometry.attributes.uv);` if using AO maps.
- **Memory Leaks**: Failing to call `.dispose()` on textures and materials when removing objects from the scene causes GPU memory leaks.
- **Non-Power-of-Two (NPOT) Textures**: NPOT textures cannot use mipmaps and repeat wrapping in WebGL1. Use power-of-2 dimensions (256, 512, 1024, 2048) for compatibility and performance.
- **PMREMGenerator Cleanup**: Always dispose of the `PMREMGenerator` and the source HDR texture after generating the environment map.
- **KTX2 Transcoder Path**: Ensure the `setTranscoderPath` points to the correct directory containing the Basis Universal transcoder files.

## Verification
1. **Check Texture Memory**: Monitor active textures in the renderer info.
   ```javascript
   console.log(renderer.info.memory.textures);
   ```
2. **Visual Inspection**: Ensure color maps appear correctly saturated (not too dark/bright) and normal maps create the expected surface relief.
3. **UV Verification**: If using AO maps, verify that the ambient occlusion aligns correctly with the geometry's lighting.
4. **Capabilities Check**: Verify max texture size and anisotropy support.
   ```javascript
   console.log(renderer.capabilities.maxTextureSize);
   console.log(renderer.capabilities.getMaxAnisotropy());
   ```

## Related skills
- `threejs-materials` - Applying textures to materials
- `threejs-loaders` - Loading texture files
- `threejs-shaders` - Custom texture sampling
