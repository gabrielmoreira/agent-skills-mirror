import * as THREE from "three";

const NOISE_FUNCTIONS = /* glsl */ `
vec3 permute(vec3 x) { return mod(((x * 34.0) + 1.0) * x, 289.0); }
float snoise(vec2 v) {
  const vec4 C = vec4(0.211324865405187, 0.366025403784439,
                     -0.577350269189626, 0.024390243902439);
  vec2 i  = floor(v + dot(v, C.yy));
  vec2 x0 = v - i + dot(i, C.xx);
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
  g.x = a0.x * x0.x + h.x * x0.y;
  g.yz = a0.yz * x12.xz + h.yz * x12.yw;
  return 130.0 * dot(m, g);
}
float fbm(vec2 p) {
  float value = 0.0;
  float amp = 0.5;
  for (int i = 0; i < 5; i++) {
    value += amp * snoise(p);
    p *= 2.0;
    amp *= 0.5;
  }
  return value;
}
vec2 hash22(vec2 p) {
  p = vec2(dot(p, vec2(127.1, 311.7)), dot(p, vec2(269.5, 183.3)));
  return fract(sin(p) * 43758.5453123);
}
vec2 worleyF1F2(vec2 x) {
  vec2 n = floor(x);
  vec2 f = fract(x);
  float f1 = 8.0, f2 = 8.0;
  for (int j = -1; j <= 1; j++) {
    for (int i = -1; i <= 1; i++) {
      vec2 g = vec2(float(i), float(j));
      vec2 o = hash22(n + g);
      vec2 r = g + o - f;
      float d = dot(r, r);
      if (d < f1) { f2 = f1; f1 = d; }
      else if (d < f2) { f2 = d; }
    }
  }
  return vec2(sqrt(f1), sqrt(f2));
}
`;

const HEIGHT_FUNCTIONS = /* glsl */ `
uniform float uMoundScale;
uniform vec2 uSeed;
uniform float uMoundDepth;
uniform float uMoundCoverage;
uniform float uMoundEdge;
uniform float uBumpScale;
uniform float uBumpStrength;
uniform float uMossEnabled;
uniform float uMossScale;
uniform vec2 uMossSeed;
uniform float uMossCoverage;
uniform float uMossEdge;
uniform float uMossDepth;
uniform float uMossBumpScale;
uniform float uMossBumpStrength;
float mossMaskAt(vec2 worldXZ) {
  if (uMossEnabled < 0.5) return 0.0;
  vec2 p = worldXZ * uMossScale + uMossSeed;
  float n = fbm(p) * 0.5 + 0.5;
  float threshold = mix(1.0 + uMossEdge, -uMossEdge, uMossCoverage);
  return smoothstep(threshold - uMossEdge, threshold + uMossEdge, n);
}
float mossHeightAt(vec2 worldXZ) {
  float mask = mossMaskAt(worldXZ);
  float drift = fbm(worldXZ * uMossBumpScale + 31.7) * 0.5 + 0.5;
  float h = mask * (1.0 - 0.4 * uMossBumpStrength
                    + 0.4 * uMossBumpStrength * drift);
  vec2 edge = smoothstep(10.0, 8.0, abs(worldXZ));
  return uMossDepth * h * edge.x * edge.y;
}
float groundHeightAt(vec2 worldXZ) {
  vec2 p = worldXZ * uMoundScale + uSeed;
  float base = fbm(p) * 0.5 + 0.5;
  float drift = fbm(worldXZ * uBumpScale + uSeed * 0.5) * 0.5 + 0.5;
  float h = base * (1.0 - 0.4 * uBumpStrength + 0.4 * uBumpStrength * drift);
  float mThresh = mix(1.0 + uMoundEdge, -uMoundEdge, uMoundCoverage);
  h *= smoothstep(mThresh - uMoundEdge, mThresh + uMoundEdge, base);
  vec2 edge = smoothstep(10.0, 8.0, abs(worldXZ));
  return uMoundDepth * h * edge.x * edge.y + mossHeightAt(worldXZ);
}
`;

const SHADE_FUNCTIONS = /* glsl */ `
uniform vec3 uSoilColor;
uniform float uVarScale;
uniform float uVarAmount;
uniform float uVarCoverage;
uniform float uVarEdge;
uniform vec2 uVarSeed;
uniform float uMoisture;
uniform float uMoistScale;
uniform float uMoistEdge;
uniform vec2 uMoistSeed;
uniform float uWetDarken;
uniform float uWetRoughness;
uniform float uCrackEnabled;
uniform float uCrackAmount;
uniform float uCrackScale;
uniform float uCrackWidth;
uniform float uCrackWarp;
uniform float uCrackDepth;
uniform vec2 uCrackSeed;
uniform float uReliefShading;
uniform int uDebugMode;
uniform sampler2D uMossMap;
uniform sampler2D uMossRoughnessMap;
uniform sampler2D uMossNormalMap;
uniform sampler2D uMossAoMap;
uniform vec3 uMossColor;
uniform float uMossRoughness;
uniform float uMossTextureScale;
uniform float uMossNormalScale;
uniform float uMossAoStrength;
float soilCrackAt(vec2 xz) {
  if (uCrackEnabled < 0.5) return 0.0;
  vec2 warp = vec2(fbm(xz * uCrackScale * 0.5 + uCrackSeed + 3.1),
                   fbm(xz * uCrackScale * 0.5 + uCrackSeed + 7.7)) * uCrackWarp;
  vec2 cp = xz * uCrackScale + uCrackSeed + warp;
  float w = max(uCrackWidth, 0.001);
  vec2 f = worleyF1F2(cp);
  float primary = 1.0 - smoothstep(0.0, w, f.y - f.x);
  vec2 f2 = worleyF1F2(cp * 2.7 + 13.0);
  float secondary = (1.0 - smoothstep(0.0, w * 1.6, f2.y - f2.x)) * 0.5;
  return clamp(max(primary, secondary), 0.0, 1.0);
}
vec3 groundSurfaceNormal(vec2 worldXZ) {
  float e = 0.08;
  float h0 = groundHeightAt(worldXZ);
  float hx = groundHeightAt(worldXZ + vec2(e, 0.0));
  float hz = groundHeightAt(worldXZ + vec2(0.0, e));
  vec2 grad = vec2(hx - h0, hz - h0) / e;
  return normalize(vec3(-grad.x, 1.0, -grad.y));
}
`;

const SOIL_INJECT = NOISE_FUNCTIONS + HEIGHT_FUNCTIONS + SHADE_FUNCTIONS;

export const defaultSoilUniforms = () => ({
  uMoundScale: { value: 0.12 },
  uSeed: { value: new THREE.Vector2(8.3, 2.1) },
  uMoundDepth: { value: 0.55 },
  uMoundCoverage: { value: 1.0 },
  uMoundEdge: { value: 0.15 },
  uBumpScale: { value: 0.7 },
  uBumpStrength: { value: 0.6 },
  uSoilColor: { value: new THREE.Color(0xffffff) },
  uVarScale: { value: 0.08 },
  uVarAmount: { value: 0.28 },
  uVarCoverage: { value: 1.0 },
  uVarEdge: { value: 0.15 },
  uVarSeed: { value: new THREE.Vector2(2.0, 7.0) },
  uMoisture: { value: 0.0 },
  uMoistScale: { value: 0.18 },
  uMoistEdge: { value: 0.12 },
  uMoistSeed: { value: new THREE.Vector2(5.0, 5.0) },
  uWetDarken: { value: 0.5 },
  uWetRoughness: { value: 0.35 },
  uCrackEnabled: { value: 0.0 },
  uCrackAmount: { value: 0.75 },
  uCrackScale: { value: 0.9 },
  uCrackWidth: { value: 0.06 },
  uCrackWarp: { value: 0.0 },
  uCrackDepth: { value: 0.7 },
  uCrackSeed: { value: new THREE.Vector2(11.0, 5.0) },
  uReliefShading: { value: 0.7 },
  uDebugMode: { value: 0 },
  uMossEnabled: { value: 0.0 },
  uMossScale: { value: 0.14 },
  uMossSeed: { value: new THREE.Vector2(4.2, 6.6) },
  uMossCoverage: { value: 0.55 },
  uMossEdge: { value: 0.14 },
  uMossDepth: { value: 0.14 },
  uMossBumpScale: { value: 0.9 },
  uMossBumpStrength: { value: 0.7 },
  uMossMap: { value: null },
  uMossRoughnessMap: { value: null },
  uMossNormalMap: { value: null },
  uMossAoMap: { value: null },
  uMossColor: { value: new THREE.Color(0xffffff) },
  uMossRoughness: { value: 1.0 },
  uMossTextureScale: { value: 0.35 },
  uMossNormalScale: { value: 1.0 },
  uMossAoStrength: { value: 1.0 },
});

export async function createHybridSoilMossSurface({
  textureBaseUrl,
  anisotropy = 4,
} = {}) {
  if (!textureBaseUrl) throw new Error("createHybridSoilMossSurface requires textureBaseUrl");
  const loader = new THREE.TextureLoader();
  const load = async (suffix, color = false) => {
    const texture = await loader.loadAsync(`${textureBaseUrl}/Ground103_1K-JPG_${suffix}.jpg`);
    if (color) texture.colorSpace = THREE.SRGBColorSpace;
    texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
    texture.repeat.set(3.5, 3.5);
    texture.anisotropy = anisotropy;
    return texture;
  };
  const [map, aoMap, roughnessMap, normalMap, displacementMap] = await Promise.all([
    load("Color", true), load("AmbientOcclusion"), load("Roughness"),
    load("NormalGL"), load("Displacement"),
  ]);
  const uniforms = defaultSoilUniforms();
  const loadMoss = async (suffix) => {
    const texture = await loader.loadAsync(
      `${textureBaseUrl}/moss/Moss002_1K-JPG_${suffix}.jpg`,
    );
    texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
    texture.anisotropy = anisotropy;
    return texture;
  };
  const [mossMap, mossRoughnessMap, mossNormalMap, mossAoMap] = await Promise.all([
    loadMoss("Color"),
    loadMoss("Roughness"),
    loadMoss("NormalGL"),
    loadMoss("AmbientOcclusion"),
  ]);
  uniforms.uMossMap.value = mossMap;
  uniforms.uMossRoughnessMap.value = mossRoughnessMap;
  uniforms.uMossNormalMap.value = mossNormalMap;
  uniforms.uMossAoMap.value = mossAoMap;
  const material = new THREE.MeshStandardMaterial({
    map, aoMap, roughnessMap, normalMap, displacementMap,
    normalMapType: THREE.TangentSpaceNormalMap,
    roughness: 1, metalness: 0, aoMapIntensity: 1,
    displacementScale: 0, displacementBias: 0, envMapIntensity: 1,
  });
  material.onBeforeCompile = (shader) => {
    Object.assign(shader.uniforms, uniforms);
    shader.vertexShader = shader.vertexShader
      .replace("#include <common>", `#include <common>\nvarying vec3 vWorldPosition;\n${SOIL_INJECT}`)
      .replace("#include <begin_vertex>", `#include <begin_vertex>
        vec2 groundXZ = (modelMatrix * vec4(transformed, 1.0)).xz;
        transformed += normalize(objectNormal) * groundHeightAt(groundXZ);
        vWorldPosition = (modelMatrix * vec4(transformed, 1.0)).xyz;`);
    shader.fragmentShader = shader.fragmentShader
      .replace("#include <common>", `#include <common>\nvarying vec3 vWorldPosition;\n${SOIL_INJECT}`)
      .replace("#include <map_fragment>", `#include <map_fragment>
        vec2 sXZ = vWorldPosition.xz;
        float tone = fbm(sXZ * uVarScale + uVarSeed) * 0.5 + 0.5;
        float tMaskN = fbm(sXZ * uVarScale * 0.7 + uVarSeed + 17.0) * 0.5 + 0.5;
        float tThresh = mix(1.0 + uVarEdge, -uVarEdge, uVarCoverage);
        float tMask = smoothstep(tThresh - uVarEdge, tThresh + uVarEdge, tMaskN);
        diffuseColor.rgb *= mix(1.0, mix(1.0 - uVarAmount, 1.0 + uVarAmount, tone), tMask);
        diffuseColor.rgb *= uSoilColor;
        float wn = fbm(sXZ * uMoistScale + uMoistSeed) * 0.5 + 0.5;
        float wThresh = mix(1.0 + uMoistEdge, -uMoistEdge, uMoisture);
        float wet = smoothstep(wThresh - uMoistEdge, wThresh + uMoistEdge, wn);
        diffuseColor.rgb *= mix(1.0, uWetDarken, wet);
        float cracks = soilCrackAt(sXZ) * uCrackAmount;
        diffuseColor.rgb *= (1.0 - 0.7 * cracks);
        float mossMask = mossMaskAt(sXZ);
        vec2 mossUv = sXZ * uMossTextureScale;
        vec3 mossAlb = pow(texture2D(uMossMap, mossUv).rgb, vec3(2.2)) * uMossColor;
        float mossAo = mix(1.0, texture2D(uMossAoMap, mossUv).r, uMossAoStrength);
        mossAlb *= mossAo;
        diffuseColor.rgb = mix(diffuseColor.rgb, mossAlb, mossMask);
        if (uDebugMode == 1) diffuseColor.rgb = vec3(groundHeightAt(sXZ) / max(uMoundDepth, 0.001));
        if (uDebugMode == 2) diffuseColor.rgb = vec3(wet);
        if (uDebugMode == 3) diffuseColor.rgb = vec3(cracks);
        if (uDebugMode == 4) diffuseColor.rgb = vec3(mossMask);`)
      .replace("#include <roughnessmap_fragment>", `#include <roughnessmap_fragment>
        roughnessFactor = mix(roughnessFactor, uWetRoughness, wet);
        roughnessFactor = mix(roughnessFactor, 1.0, cracks);
        float mossRough = texture2D(uMossRoughnessMap, sXZ * uMossTextureScale).g * uMossRoughness;
        roughnessFactor = mix(roughnessFactor, clamp(mossRough, 0.04, 1.0), mossMask);`)
      .replace("#include <normal_fragment_maps>", `#include <normal_fragment_maps>
        vec3 mossN = texture2D(uMossNormalMap, sXZ * uMossTextureScale).xyz * 2.0 - 1.0;
        mossN.xy *= uMossNormalScale;
        vec3 mossViewN = normalize(tbn * mossN);
        normal = normalize(mix(normal, mossViewN, mossMask));
        vec3 gN = groundSurfaceNormal(vWorldPosition.xz);
        vec3 gView = normalize((viewMatrix * vec4(gN, 0.0)).xyz);
        normal = normalize(mix(normal, gView, uReliefShading));
        float ce = 0.02;
        float c0 = soilCrackAt(sXZ);
        float cx = soilCrackAt(sXZ + vec2(ce, 0.0));
        float cz = soilCrackAt(sXZ + vec2(0.0, ce));
        vec2 cGrad = vec2(cx - c0, cz - c0) / ce;
        float cDepth = uCrackDepth * uCrackAmount;
        vec3 crackN = normalize(vec3(-cGrad.x * cDepth, 1.0, -cGrad.y * cDepth));
        vec3 crackView = normalize((viewMatrix * vec4(crackN, 0.0)).xyz);
        normal = normalize(mix(normal, crackView, smoothstep(0.02, 0.5, cracks)));`);
  };
  material.customProgramCacheKey = () => "soil-moss-v2";
  const geometry = new THREE.PlaneGeometry(20, 20, 256, 256);
  geometry.setAttribute("uv1", geometry.attributes.uv);
  const mesh = new THREE.Mesh(geometry, material);
  mesh.rotation.x = -Math.PI / 2;
  mesh.receiveShadow = true;
  mesh.userData.soilUniforms = uniforms;
  mesh.userData.disposeSoil = () => {
    geometry.dispose(); material.dispose();
    map.dispose(); aoMap.dispose(); roughnessMap.dispose(); normalMap.dispose(); displacementMap.dispose();
    mossMap.dispose(); mossRoughnessMap.dispose(); mossNormalMap.dispose(); mossAoMap.dispose();
  };
  return mesh;
}

export function setHybridSoilMossDebugMode(mesh, mode) {
  const uniforms = mesh.userData.soilUniforms;
  uniforms.uDebugMode.value = { final: 0, height: 1, moisture: 2, cracks: 3, moss: 4 }[mode] ?? 0;
  uniforms.uMoisture.value = mode === "moisture" ? 0.55 : 0.0;
  uniforms.uCrackEnabled.value = mode === "cracks" ? 1.0 : 0.0;
}
