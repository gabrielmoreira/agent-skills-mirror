---
name: threejs-shaders
description: "Authors Three.js custom shaders: ShaderMaterial vs RawShaderMaterial, GLSL uniforms/varyings, vertex deformation, fragment effects, onBeforeCompile hooks, and TSL for WebGPU. Use when writing or migrating Three.js shaders or extending built-in materials. Not for scene/camera/renderer scaffold (threejs-fundamentals) or picking a specialist via threejs-skill-router."
version: 1.0.1
risk: unknown
source: community
---

# Three.js Shaders

## When to Use

- You need custom shader logic in Three.js using `ShaderMaterial` or `RawShaderMaterial`.
- The task involves GLSL vertex deformation, fragment-based effects, uniforms, varyings, or custom rendering passes.
- You are extending built-in material behavior beyond what `MeshStandardMaterial` and friends provide.
- You need to inject custom logic into built-in materials via `onBeforeCompile`.
- You are migrating or authoring shaders for WebGPU using TSL (Three.js Shading Language).

## Prerequisites

- Three.js installed in the project (`npm install three` or via CDN).
- A running Three.js scene with a `WebGLRenderer` (or `WebGPURenderer` for TSL).
- Basic familiarity with GLSL syntax and the WebGL pipeline.
- For external `.glsl` shader files: a bundler (Vite, webpack) configured to import GLSL as strings.

## Procedure

### 1. Choose ShaderMaterial vs RawShaderMaterial

**ShaderMaterial** — Three.js auto-injects built-in uniforms and attributes. Use this for 90% of cases.

```javascript
import * as THREE from "three";

const material = new THREE.ShaderMaterial({
  uniforms: {
    time: { value: 0 },
    color: { value: new THREE.Color(0xff0000) },
  },
  vertexShader: `
    // Built-in uniforms available (auto-injected):
    // uniform mat4 modelMatrix;
    // uniform mat4 modelViewMatrix;
    // uniform mat4 projectionMatrix;
    // uniform mat4 viewMatrix;
    // uniform mat3 normalMatrix;
    // uniform vec3 cameraPosition;

    // Built-in attributes available (auto-injected):
    // attribute vec3 position;
    // attribute vec3 normal;
    // attribute vec2 uv;

    void main() {
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    uniform vec3 color;
    void main() {
      gl_FragColor = vec4(color, 1.0);
    }
  `,
});
```

**RawShaderMaterial** — You define everything manually, including `precision`, attributes, and uniforms. Use when you need full control or are porting raw GLSL.

```javascript
const material = new THREE.RawShaderMaterial({
  uniforms: {
    projectionMatrix: { value: camera.projectionMatrix },
    modelViewMatrix: { value: new THREE.Matrix4() },
  },
  vertexShader: `
    precision highp float;
    attribute vec3 position;
    uniform mat4 projectionMatrix;
    uniform mat4 modelViewMatrix;
    void main() {
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    precision highp float;
    void main() {
      gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);
    }
  `,
});
```

### 2. Define Uniforms

Uniforms bridge JavaScript and GLSL. Each uniform is an object with a `value` property.

```javascript
const material = new THREE.ShaderMaterial({
  uniforms: {
    floatValue: { value: 1.5 },
    intValue: { value: 1 },
    vec2Value: { value: new THREE.Vector2(1, 2) },
    vec3Value: { value: new THREE.Vector3(1, 2, 3) },
    vec4Value: { value: new THREE.Vector4(1, 2, 3, 4) },
    colorValue: { value: new THREE.Color(0xff0000) }, // becomes vec3 in GLSL
    mat3Value: { value: new THREE.Matrix3() },
    mat4Value: { value: new THREE.Matrix4() },
    textureValue: { value: texture },
    cubeTextureValue: { value: cubeTexture },
    floatArray: { value: [1.0, 2.0, 3.0] },
    vec3Array: {
      value: [new THREE.Vector3(1, 0, 0), new THREE.Vector3(0, 1, 0)],
    },
  },
});
```

Corresponding GLSL declarations:

```glsl
uniform float floatValue;
uniform int intValue;
uniform vec2 vec2Value;
uniform vec3 vec3Value;
uniform vec3 colorValue;
uniform vec4 vec4Value;
uniform mat3 mat3Value;
uniform mat4 mat4Value;
uniform sampler2D textureValue;
uniform samplerCube cubeTextureValue;
uniform float floatArray[3];
uniform vec3 vec3Array[2];
```

### 3. Update Uniforms in the Animation Loop

```javascript
// Direct scalar assignment
material.uniforms.time.value = clock.getElapsedTime();

// Vector / Color updates (mutate in place to avoid GPU re-upload overhead)
material.uniforms.position.value.set(x, y, z);
material.uniforms.color.value.setHSL(hue, 1, 0.5);

// Matrix updates
material.uniforms.matrix.value.copy(mesh.matrixWorld);
```

### 4. Pass Data Between Shaders with Varyings

Declare the same `varying` in both vertex and fragment shaders. The GPU interpolates values across the primitive.

```javascript
const material = new THREE.ShaderMaterial({
  vertexShader: `
    varying vec2 vUv;
    varying vec3 vNormal;
    varying vec3 vPosition;

    void main() {
      vUv = uv;
      vNormal = normalize(normalMatrix * normal);
      vPosition = (modelViewMatrix * vec4(position, 1.0)).xyz;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    varying vec2 vUv;
    varying vec3 vNormal;
    varying vec3 vPosition;

    void main() {
      gl_FragColor = vec4(vNormal * 0.5 + 0.5, 1.0);
    }
  `,
});
```

### 5. Implement Common Shader Patterns

#### Texture Sampling

```javascript
const material = new THREE.ShaderMaterial({
  uniforms: { map: { value: texture } },
  vertexShader: `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    uniform sampler2D map;
    varying vec2 vUv;
    void main() {
      gl_FragColor = texture2D(map, vUv);
    }
  `,
});
```

#### Vertex Displacement

```javascript
const material = new THREE.ShaderMaterial({
  uniforms: { time: { value: 0 }, amplitude: { value: 0.5 } },
  vertexShader: `
    uniform float time;
    uniform float amplitude;
    void main() {
      vec3 pos = position;
      pos.z += sin(pos.x * 5.0 + time) * amplitude;
      pos.z += sin(pos.y * 5.0 + time) * amplitude;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
    }
  `,
  fragmentShader: `
    void main() {
      gl_FragColor = vec4(0.5, 0.8, 1.0, 1.0);
    }
  `,
});
```

#### Fresnel Effect

```javascript
const material = new THREE.ShaderMaterial({
  vertexShader: `
    varying vec3 vNormal;
    varying vec3 vWorldPosition;
    void main() {
      vNormal = normalize(normalMatrix * normal);
      vWorldPosition = (modelMatrix * vec4(position, 1.0)).xyz;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    varying vec3 vNormal;
    varying vec3 vWorldPosition;
    void main() {
      vec3 viewDirection = normalize(cameraPosition - vWorldPosition);
      float fresnel = pow(1.0 - dot(viewDirection, vNormal), 3.0);
      vec3 baseColor = vec3(0.0, 0.0, 0.5);
      vec3 fresnelColor = vec3(0.5, 0.8, 1.0);
      gl_FragColor = vec4(mix(baseColor, fresnelColor, fresnel), 1.0);
    }
  `,
});
```

#### Noise-Based Effects

```glsl
float random(vec2 st) {
  return fract(sin(dot(st.xy, vec2(12.9898, 78.233))) * 43758.5453);
}

float noise(vec2 st) {
  vec2 i = floor(st);
  vec2 f = fract(st);
  float a = random(i);
  float b = random(i + vec2(1.0, 0.0));
  float c = random(i + vec2(0.0, 1.0));
  float d = random(i + vec2(1.0, 1.0));
  vec2 u = f * f * (3.0 - 2.0 * f);
  return mix(a, b, u.x) + (c - a) * u.y * (1.0 - u.x) + (d - b) * u.x * u.y;
}

// Usage in fragment shader
float n = noise(vUv * 10.0 + time);
```

#### Gradients

```glsl
// Linear
vec3 color = mix(colorA, colorB, vUv.y);

// Radial
float dist = distance(vUv, vec2(0.5));
vec3 color = mix(centerColor, edgeColor, dist * 2.0);

// Smoothstep curve
float t = smoothstep(0.0, 1.0, vUv.y);
vec3 color = mix(colorA, colorB, t);
```

#### Rim Lighting

```javascript
const material = new THREE.ShaderMaterial({
  vertexShader: `
    varying vec3 vNormal;
    varying vec3 vViewPosition;
    void main() {
      vNormal = normalize(normalMatrix * normal);
      vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
      vViewPosition = mvPosition.xyz;
      gl_Position = projectionMatrix * mvPosition;
    }
  `,
  fragmentShader: `
    varying vec3 vNormal;
    varying vec3 vViewPosition;
    void main() {
      vec3 viewDir = normalize(-vViewPosition);
      float rim = 1.0 - max(0.0, dot(viewDir, vNormal));
      rim = pow(rim, 4.0);
      vec3 baseColor = vec3(0.2, 0.2, 0.8);
      vec3 rimColor = vec3(1.0, 0.5, 0.0);
      gl_FragColor = vec4(baseColor + rimColor * rim, 1.0);
    }
  `,
});
```

#### Dissolve Effect

```glsl
uniform float progress;
uniform sampler2D noiseMap;
varying vec2 vUv;

void main() {
  float noise = texture2D(noiseMap, vUv).r;
  if (noise < progress) {
    discard;
  }
  float edge = smoothstep(progress, progress + 0.1, noise);
  vec3 edgeColor = vec3(1.0, 0.5, 0.0);
  vec3 baseColor = vec3(0.5);
  gl_FragColor = vec4(mix(edgeColor, baseColor, edge), 1.0);
}
```

### 6. Extend Built-in Materials with onBeforeCompile

Use this when you want lighting, shadows, and fog from `MeshStandardMaterial` but need custom shader modifications.

```javascript
const material = new THREE.MeshStandardMaterial({ color: 0x00ff00 });

material.onBeforeCompile = (shader) => {
  shader.uniforms.time = { value: 0 };
  material.userData.shader = shader; // store reference for updates

  // Inject uniform declaration
  shader.vertexShader = "uniform float time;\n" + shader.vertexShader;

  // Inject displacement after position is calculated
  shader.vertexShader = shader.vertexShader.replace(
    "#include <begin_vertex>",
    `
    #include <begin_vertex>
    transformed.y += sin(position.x * 10.0 + time) * 0.1;
    `
  );
};

// Update in animation loop
if (material.userData.shader) {
  material.userData.shader.uniforms.time.value = clock.getElapsedTime();
}
```

**Common injection points:**

| Shader | Chunk | Description |
|--------|-------|-------------|
| Vertex | `#include <begin_vertex>` | After `transformed` (local position) is calculated |
| Vertex | `#include <project_vertex>` | After `gl_Position` is set |
| Vertex | `#include <beginnormal_vertex>` | Normal calculation start |
| Fragment | `#include <color_fragment>` | After diffuse color is computed |
| Fragment | `#include <output_fragment>` | Final output (pre-fog) |
| Fragment | `#include <fog_fragment>` | After fog is applied |

### 7. Configure Material Properties

```javascript
const material = new THREE.ShaderMaterial({
  uniforms: { /* ... */ },
  vertexShader: "/* ... */",
  fragmentShader: "/* ... */",

  // Rendering
  transparent: true,
  opacity: 1.0,
  side: THREE.DoubleSide,
  depthTest: true,
  depthWrite: true,

  // Blending
  blending: THREE.NormalBlending, // AdditiveBlending, SubtractiveBlending, MultiplyBlending

  // Wireframe
  wireframe: false,
  wireframeLinewidth: 1, // >1 has no effect on most platforms (WebGL limitation)

  // Extensions
  extensions: {
    derivatives: true,    // fwidth, dFdx, dFdy
    fragDepth: true,      // gl_FragDepth
    drawBuffers: true,    // Multiple render targets
    shaderTextureLOD: true, // texture2DLod
  },

  // GLSL version
  glslVersion: THREE.GLSL3, // For WebGL2 features
});
```

### 8. Use Three.js Shader Chunks

```javascript
import { ShaderChunk } from "three";

const fragmentShader = `
  ${ShaderChunk.common}
  ${ShaderChunk.packing}

  uniform sampler2D depthTexture;
  varying vec2 vUv;

  void main() {
    float depth = texture2D(depthTexture, vUv).r;
    float linearDepth = perspectiveDepthToViewZ(depth, 0.1, 1000.0);
    gl_FragColor = vec4(vec3(-linearDepth / 100.0), 1.0);
  }
`;
```

### 9. Load External Shader Files

```javascript
// With Vite or webpack (requires glsl loader plugin)
import vertexShader from "./shaders/vertex.glsl";
import fragmentShader from "./shaders/fragment.glsl";

const material = new THREE.ShaderMaterial({
  vertexShader,
  fragmentShader,
  uniforms: { /* ... */ },
});
```

### 10. Set Up Instanced Shaders

```javascript
const offsets = new Float32Array(instanceCount * 3);
// Fill offsets...
geometry.setAttribute("offset", new THREE.InstancedBufferAttribute(offsets, 3));

const material = new THREE.ShaderMaterial({
  vertexShader: `
    attribute vec3 offset;
    void main() {
      vec3 pos = position + offset;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
    }
  `,
  fragmentShader: `
    void main() {
      gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);
    }
  `,
});
```

### 11. Migrate to TSL (Three.js Shading Language)

TSL is the new shader authoring system for Three.js, designed for both WebGL and WebGPU renderers. GLSL `ShaderMaterial` patterns are **WebGL-only** and will not work with `WebGPURenderer`.

```javascript
import { MeshStandardNodeMaterial } from "three/addons/nodes/Nodes.js";
import {
  uv, sin, timerLocal, positionLocal, normalLocal,
} from "three/addons/nodes/Nodes.js";

const material = new MeshStandardNodeMaterial();

// Animated color
const time = timerLocal();
material.colorNode = uv().x.add(time).sin().mul(1.0);

// Vertex displacement
material.positionNode = positionLocal.add(
  normalLocal.mul(positionLocal.x.add(time).sin().mul(0.1))
);
```

**Key differences:**

| GLSL (WebGL only) | TSL (WebGL + WebGPU) |
|---|---|
| `ShaderMaterial` | `MeshStandardNodeMaterial` |
| String-based shaders | JavaScript node graph |
| `onBeforeCompile` | Node composition |
| Manual uniforms | `uniform()` node |
| `texture2D()` | `texture()` node |
| `gl_Position` | `positionNode` |
| `gl_FragColor` | `colorNode` / `outputNode` |

**When to use which:**
- **GLSL ShaderMaterial**: Existing WebGL projects, maximum shader control, porting existing GLSL shaders.
- **TSL NodeMaterial**: New projects, WebGPU support needed, cross-renderer compatibility.

## Pitfalls

- **RawShaderMaterial requires `precision` declarations**: Unlike `ShaderMaterial`, `RawShaderMaterial` does not auto-inject `precision highp float;`. Omitting it causes silent compile failures on some drivers.
- **RawShaderMaterial requires manual attribute/uniform declarations**: `position`, `normal`, `uv`, `modelViewMatrix`, `projectionMatrix`, etc. are NOT auto-injected. You must declare them yourself.
- **GLSL3 changes syntax**: When using `glslVersion: THREE.GLSL3`, use `texture()` instead of `texture2D()`, and `out vec4 fragColor` instead of `gl_FragColor`.
- **`wireframeLinewidth > 1` is ignored**: This is a WebGL platform limitation, not a Three.js bug.
- **`onBeforeCompile` shader reference is fragile**: The `shader` object passed to the callback is only valid for that compile. If the material recompiles (e.g., lights change), the stored reference becomes stale. Always check `material.userData.shader` exists before updating.
- **Uniform updates must mutate `.value` in place**: Replacing `material.uniforms.x.value` with a new object can cause the uniform to not update on the GPU. Use `.set()` for vectors/colors and `.copy()` for matrices.
- **Varying name mismatch**: The `varying` declaration must be identical in vertex and fragment shaders. A typo in one causes a link error.
- **`cameraPosition` is only auto-injected in ShaderMaterial**: If using `RawShaderMaterial`, you must pass `cameraPosition` as a uniform yourself.
- **GLSL is type-strict**: `1` vs `1.0` matters. Integer literals in float contexts cause compile errors.
- **Avoid branching in fragment shaders**: `if/else` can cause performance issues on some GPUs. Prefer `mix()`, `step()`, and `smoothstep()` for conditional logic.
- **TSL is not a drop-in replacement for GLSL**: TSL uses a JavaScript node graph API, not string-based shaders. Existing GLSL code must be rewritten as node compositions.
- **WebGPU renderer does not support GLSL ShaderMaterial**: If the project uses `WebGPURenderer`, you must use TSL or the GLSL-to-TSL transpiler.

## Verification

### Check Shader Compilation

```javascript
// Enable shader error checking (default is true in dev, false in production)
renderer.debug.checkShaderErrors = true;

// Log compiled shaders for inspection
material.onBeforeCompile = (shader) => {
  console.log("Vertex Shader:", shader.vertexShader);
  console.log("Fragment Shader:", shader.fragmentShader);
};
```

### Visual Debugging in Fragment Shader

```glsl
// Debug UVs — should show a rainbow gradient
gl_FragColor = vec4(vUv, 0.0, 1.0);

// Debug normals — should show pastel colors
gl_FragColor = vec4(vNormal * 0.5 + 0.5, 1.0);

// Debug position — should show spatial gradient
gl_FragColor = vec4(vPosition * 0.1 + 0.5, 1.0);
```

### Verify Uniform Updates

```javascript
// In animation loop
console.assert(
  material.uniforms.time.value > 0,
  "time uniform is not being updated"
);
```

### Verify Material Type

```javascript
console.assert(material.isShaderMaterial, "Expected ShaderMaterial");
console.assert(material.isRawShaderMaterial, "Expected RawShaderMaterial");
```

### Verify onBeforeCompile Injection

```javascript
// After first render, check that shader reference is stored
console.assert(
  material.userData.shader,
  "onBeforeCompile has not run yet — material may not have been rendered"
);
console.assert(
  material.userData.shader.uniforms.time,
  "custom uniform 'time' was not injected"
);
```

## Related Skills

- `threejs-materials` — Built-in material types and their properties
- `threejs-postprocessing` — Full-screen shader effects and render passes
- `threejs-textures` — Texture creation, loading, and sampling in shaders

## Limitations

- Use this skill only when the task clearly involves Three.js shader authoring or modification.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
