import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

/**
 * Drop-a-model-in-the-moss system. The settled layer is living moss with
 * displaced thickness and a shared material identity.
 *
 *  - Loads a default GLB and lets the user import any .glb at runtime.
 *  - Sits the model on the ground plane, centered, with scale/pos/rot controls.
 *  - Injects a "moss accumulation" shader into every mesh material:
 *      • upward-facing faces grow a real, displaced layer of moss whose
 *        THICKNESS, COVERAGE, SCALE and SEED are all tunable (so flat tops and
 *        shoulders cap with moss on any model, with no mesh analysis);
 *      • the capped area is shaded with the SAME moss texture set the ground
 *        uses (colour / roughness / normal / AO), plus a soft mounded relief
 *        normal so it reads as a raised, organic carpet.
 *
 * The texture maps, tint and the master `uMossEnabled` gate are shared BY
 * REFERENCE with the ground moss uniforms, so the model mosses over exactly
 * when the ground moss is active and stays visually consistent with it.
 *
 * @param {object} o
 * @param {THREE.Scene}  o.scene
 * @param {object} o.sharedUniforms   { uTime } (shared by reference)
 * @param {object} o.mossUniforms     the ground moss uniforms (maps/tint/enabled shared in)
 * @param {string} [o.defaultUrl]     GLB to load on start
 */
export function createModelMossAccumulation({ scene, sharedUniforms, mossUniforms, defaultUrl }) {
  const loader = new GLTFLoader();

  // Transform wrapper — user controls live here; the GLB is recentered inside.
  const group = new THREE.Group();
  group.visible = false; // hidden until the user toggles it on
  scene.add(group);
  let current = null; // the loaded GLB scene
  const processed = new Set(); // materials we've already made mossy
  let ready = Promise.resolve();

  /* ---- moss-accumulation uniforms (shared bits + own knobs) -------------- */
  const moss = {
    uMossEnabled: mossUniforms.uMossEnabled, // shared master on/off gate
    uModelInv: { value: new THREE.Matrix4() }, // world -> model space (locks the pattern)
    uMossSeed: { value: new THREE.Vector2(3.0, 7.0) }, // pan the coverage noise
    uMossScale: { value: 0.9 }, // coverage noise frequency
    uMossCoverage: { value: 0.7 }, // 0 = bare model, 1 = fully capped
    uMossEdge: { value: 0.15 }, // coverage shoreline softness
    uMossThickness: { value: 0.05 }, // displaced layer depth (world units)
    uMossFlatThreshold: { value: 0.35 }, // how upward a face must be to collect
    // --- texture & look (maps + tint shared from the ground moss) ----------
    uMossMap: mossUniforms.uMossMap,
    uMossRoughnessMap: mossUniforms.uMossRoughnessMap,
    uMossNormalMap: mossUniforms.uMossNormalMap,
    uMossAoMap: mossUniforms.uMossAoMap,
    uMossColor: mossUniforms.uMossColor,
    uMossTexScale: { value: 2.0 }, // model-space moss tiling (finer than the ground)
    uMossRoughness: { value: 1.0 }, // scales the sampled moss roughness
    uMossAoStrength: { value: 1.0 }, // moss ambient-occlusion strength
    uMossBump: { value: 0.5 }, // micro surface relief strength
    uMossBumpScale: { value: 3.0 }, // micro relief frequency
  };

  // Shared GLSL (uniforms + noise + the coverage/relief helpers), injected into
  // BOTH stages: the vertex stage grows the layer, the fragment stage shades it.
  const MOSS_GLSL = /* glsl */ `
  varying vec3 vWorldNormalW;
  varying vec3 vModelPosW;
  uniform float uMossEnabled;
  uniform mat4  uModelInv;
  uniform vec2  uMossSeed;
  uniform float uMossScale;
  uniform float uMossCoverage;
  uniform float uMossEdge;
  uniform float uMossThickness;
  uniform float uMossFlatThreshold;
  uniform sampler2D uMossMap;
  uniform sampler2D uMossRoughnessMap;
  uniform sampler2D uMossNormalMap;
  uniform sampler2D uMossAoMap;
  uniform vec3  uMossColor;
  uniform float uMossTexScale;
  uniform float uMossRoughness;
  uniform float uMossAoStrength;
  uniform float uMossBump;
  uniform float uMossBumpScale;

  vec3 permute(vec3 x) { return mod(((x * 34.0) + 1.0) * x, 289.0); }
  float snoise(vec2 v) {
    const vec4 C = vec4(0.211324865405187, 0.366025403784439,
                       -0.577350269189626, 0.024390243902439);
    vec2 i  = floor(v + dot(v, C.yy));
    vec2 x0 = v -   i + dot(i, C.xx);
    vec2 i1 = (x0.x > x0.y) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
    vec4 x12 = x0.xyxy + C.xxzz;
    x12.xy -= i1;
    i = mod(i, 289.0);
    vec3 p = permute(permute(i.y + vec3(0.0, i1.y, 1.0)) + i.x + vec3(0.0, i1.x, 1.0));
    vec3 m = max(0.5 - vec3(dot(x0, x0), dot(x12.xy, x12.xy), dot(x12.zw, x12.zw)), 0.0);
    m = m * m; m = m * m;
    vec3 x = 2.0 * fract(p * C.www) - 1.0;
    vec3 h = abs(x) - 0.5;
    vec3 ox = floor(x + 0.5);
    vec3 a0 = x - ox;
    m *= 1.79284291400159 - 0.85373472095314 * (a0 * a0 + h * h);
    vec3 g;
    g.x  = a0.x * x0.x + h.x * x0.y;
    g.yz = a0.yz * x12.xz + h.yz * x12.yw;
    return 130.0 * dot(m, g);
  }
  float fbm(vec2 p) {
    float value = 0.0;
    float amp = 0.5;
    for (int i = 0; i < 5; i++) { value += amp * snoise(p); p *= 2.0; amp *= 0.5; }
    return value;
  }

  // Patchy coverage from a top-down model-space noise (0 bare .. 1 covered).
  float mossCoverageMask(vec2 modelXZ) {
    float n = fbm(modelXZ * uMossScale + uMossSeed) * 0.5 + 0.5;
    float threshold = 1.0 - uMossCoverage;
    return smoothstep(threshold - uMossEdge, threshold + uMossEdge, n);
  }

  // How much moss sits at a point, given its world-space normal: only upward-ish
  // faces collect, modulated by the patchy coverage and the master gate. 0..1.
  float mossAccumAt(vec3 worldNormal, vec2 modelXZ) {
    if (uMossEnabled < 0.5) return 0.0;
    float up = clamp(worldNormal.y, 0.0, 1.0);
    float top = smoothstep(uMossFlatThreshold, 1.0, up);
    return top * mossCoverageMask(modelXZ);
  }

  // Soft moss surface normal (world up nudged by fine relief).
  vec3 mossReliefNormal(vec2 modelXZ) {
    float e = 0.04;
    float h0 = fbm(modelXZ * uMossBumpScale);
    float hx = fbm(modelXZ * uMossBumpScale + vec2(e, 0.0));
    float hz = fbm(modelXZ * uMossBumpScale + vec2(0.0, e));
    vec2 grad = vec2(hx - h0, hz - h0) / e;
    return normalize(vec3(-grad.x * uMossBump, 1.0, -grad.y * uMossBump));
  }
  `;

  function makeMossy(material) {
    if (!material || processed.has(material)) return;
    processed.add(material);

    material.onBeforeCompile = (shader) => {
      Object.assign(shader.uniforms, moss);

      // Vertex: grow the moss layer on upward faces by displacing along the
      // surface normal. The displacement is converted from world units to local
      // units per-mesh (dividing by the world length of the mapped normal) so it
      // stays a consistent thickness regardless of the model/mesh scale.
      shader.vertexShader = shader.vertexShader
        .replace('#include <common>', '#include <common>\n' + MOSS_GLSL)
        .replace(
          '#include <beginnormal_vertex>',
          '#include <beginnormal_vertex>\nvWorldNormalW = normalize(mat3(modelMatrix) * objectNormal);'
        )
        .replace(
          '#include <begin_vertex>',
          `#include <begin_vertex>
          vec3 wPos = (modelMatrix * vec4(transformed, 1.0)).xyz;
          vModelPosW = (uModelInv * vec4(wPos, 1.0)).xyz; // model-locked coords
          vec3 wN = mat3(modelMatrix) * objectNormal;
          float ms = max(length(wN), 1e-4);
          float accum = mossAccumAt(wN / ms, vModelPosW.xz);
          transformed += normalize(objectNormal) * (uMossThickness * accum / ms);`
        );

      shader.fragmentShader = shader.fragmentShader
        .replace('#include <common>', '#include <common>\n' + MOSS_GLSL)
        // Cap the upward faces with the moss texture (colour + AO).
        .replace(
          '#include <map_fragment>',
          `#include <map_fragment>
          vec3 wn = normalize(vWorldNormalW);
          float mossAmt = mossAccumAt(wn, vModelPosW.xz);
          vec2  mUv = vModelPosW.xz * uMossTexScale;
          vec3  mAlb = pow(texture2D(uMossMap, mUv).rgb, vec3(2.2)) * uMossColor;
          float mAo  = mix(1.0, texture2D(uMossAoMap, mUv).r, uMossAoStrength);
          mAlb *= mAo;
          diffuseColor.rgb = mix(diffuseColor.rgb, mAlb, mossAmt);`
        )
        .replace(
          '#include <roughnessmap_fragment>',
          `#include <roughnessmap_fragment>
          float mRough = texture2D(uMossRoughnessMap, vModelPosW.xz * uMossTexScale).g * uMossRoughness;
          roughnessFactor = mix(roughnessFactor, clamp(mRough, 0.04, 1.0), mossAmt);`
        )
        // Re-normal the capped area with soft moss relief (world up + bumps).
        .replace(
          '#include <normal_fragment_maps>',
          `#include <normal_fragment_maps>
          vec3 mN = mossReliefNormal(vModelPosW.xz);
          vec3 mView = normalize((viewMatrix * vec4(mN, 0.0)).xyz);
          normal = normalize(mix(normal, mView, mossAmt));`
        );
    };
    material.customProgramCacheKey = () => 'moss-model-v1';
    material.needsUpdate = true;
  }

  function disposeMaterial(mat) {
    if (!mat) return;
    // Only dispose textures this model owns — the shared moss maps live in the
    // ground uniforms and must survive a model swap.
    const shared = new Set([
      moss.uMossMap.value,
      moss.uMossRoughnessMap.value,
      moss.uMossNormalMap.value,
      moss.uMossAoMap.value,
    ]);
    for (const v of Object.values(mat)) {
      if (v && v.isTexture && !shared.has(v)) v.dispose();
    }
    mat.dispose();
  }

  function setModel(root) {
    if (current) {
      group.remove(current);
      current.traverse((o) => {
        if (o.geometry) o.geometry.dispose();
        if (Array.isArray(o.material)) o.material.forEach(disposeMaterial);
        else disposeMaterial(o.material);
      });
    }
    processed.clear();

    // Recenter on XZ and rest on the ground (y = 0) before the user transform.
    const box = new THREE.Box3().setFromObject(root);
    const center = box.getCenter(new THREE.Vector3());
    root.position.x -= center.x;
    root.position.z -= center.z;
    root.position.y -= box.min.y;

    root.traverse((o) => {
      if (!o.isMesh) return;
      o.castShadow = true;
      o.receiveShadow = true;
      if (Array.isArray(o.material)) o.material.forEach(makeMossy);
      else makeMossy(o.material);
    });

    current = root;
    group.add(root);
    refreshMatrix();
  }

  // Keep the world->model matrix current so the moss pattern stays locked to the
  // model when it's moved, rotated or scaled.
  function refreshMatrix() {
    group.updateMatrixWorld(true);
    moss.uModelInv.value.copy(group.matrixWorld).invert();
  }

  function loadURL(url, onError) {
    ready = loader.loadAsync(url)
      .then((gltf) => setModel(gltf.scene))
      .catch((err) => {
        if (onError) onError(err);
        else throw err;
      });
    return ready;
  }

  if (defaultUrl) loadURL(defaultUrl);

  return {
    group,
    moss,
    get ready() {
      return ready;
    },
    /** Load a GLB from a user File object. */
    importFile(file) {
      const url = URL.createObjectURL(file);
      loadURL(url, (e) => console.error('Failed to load GLB:', e));
    },
    /** Swap to one of the bundled models by URL. */
    loadModel(url) {
      return loadURL(url, (e) => console.error('Failed to load GLB:', e));
    },
    /** Re-sync the world->model matrix after a transform change. */
    refreshMatrix,
    /** Show/hide the model. */
    setVisible(v) {
      group.visible = v;
    },
    get isVisible() {
      return group.visible;
    },
    dispose() {
      if (current) {
        current.traverse((o) => {
          if (o.geometry) o.geometry.dispose();
          if (Array.isArray(o.material)) o.material.forEach(disposeMaterial);
          else disposeMaterial(o.material);
        });
      }
      group.removeFromParent();
      processed.clear();
    },
  };
}
