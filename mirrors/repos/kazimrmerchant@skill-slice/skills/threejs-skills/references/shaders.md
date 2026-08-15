# Custom shaders (load on demand)

Use this companion when the user asks for custom GLSL or TSL on a scene already built in `SKILL.md`. Prefer `MeshStandardMaterial` until a built-in material cannot express the look.

## WebGL: ShaderMaterial

`ShaderMaterial` injects Three.js built-ins (`projectionMatrix`, `position`, `uv`). Update uniforms from `setAnimationLoop`.

```javascript
const material = new THREE.ShaderMaterial({
  uniforms: {
    uTime: { value: 0 },
    uColor: { value: new THREE.Color(0x00ff00) },
  },
  vertexShader: `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    uniform float uTime;
    uniform vec3 uColor;
    varying vec2 vUv;
    void main() {
      float pulse = 0.5 + 0.5 * sin(uTime + vUv.x * 6.28318);
      gl_FragColor = vec4(uColor * pulse, 1.0);
    }
  `,
});

renderer.setAnimationLoop(() => {
  timer.update();
  material.uniforms.uTime.value += timer.getDelta();
  renderer.render(scene, camera);
});
```

`RawShaderMaterial` requires an explicit `precision` line and every matrix/attribute. Use it only when porting standalone GLSL.

## WebGPU: TSL

`WebGPURenderer` does not run GLSL `ShaderMaterial`. Author nodes in JavaScript (TSL) and attach them to a node material. On r183+ the in-tree import path is `three/addons/nodes/Nodes.js` (same nodes are also exported from `three/tsl` in newer Three.js builds).

```javascript
import { MeshStandardNodeMaterial } from "three/addons/nodes/Nodes.js";
import { uv, sin, timerLocal, mix, color } from "three/addons/nodes/Nodes.js";

const material = new MeshStandardNodeMaterial();
material.colorNode = mix(color(0x112233), color(0x88ffaa), sin(timerLocal().add(uv().x)));
```

## Pitfalls

- Forgetting to write `uTime` (or equivalent) each frame freezes the shader.
- Mixing GLSL materials with `WebGPURenderer` fails silently or at init; pick one renderer path.
- For `onBeforeCompile` patches, instanced attributes, or a full TSL catalog, load a dedicated shaders specialist if it is installed.
