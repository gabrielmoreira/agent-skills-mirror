/// <reference types="@webgpu/types" />

/**
 * Raw WebGPU flower field renderer.
 *
 * The field is virtual: a flower is reconstructed from its integer candidate
 * id in compute and vertex shaders. The CPU never allocates a placement or
 * transform record per flower. Compute compacts visible ids into three detail
 * tiers, then eight indirect draws render stems, curved petals, centres, and
 * the sub-pixel horizon representation.
 */

export type FlowerRenderMode = "compact" | "direct";
export type FlowerCullingMode = "hierarchical" | "flat";

export type FlowerLabOptions = {
  gridSize: number;
  mode: FlowerRenderMode;
  density: number;
  spacing: number;
  maxDistance: number;
  nearDistance: number;
  midDistance: number;
  wind: number;
  mixPetalVariants: boolean;
  cullingMode: FlowerCullingMode;
  seed: number;
  benchmark?: boolean;
};

export type FlowerLabMetrics = {
  ready: boolean;
  mode: FlowerRenderMode;
  cullingMode: FlowerCullingMode;
  candidateCount: number;
  visibleCount: number | null;
  visibleTiers: readonly [number, number, number] | null;
  visibleTileCount: number | null;
  candidateTests: number | null;
  spacing: number;
  density: number;
  maxDistance: number;
  frameMeanMs: number;
  frameP95Ms: number;
  frameP99Ms: number;
  frameMaxMs: number;
  submitMeanMs: number;
  fps: number;
  gpuRenderMeanMs: number | null;
  gpuRenderP95Ms: number | null;
  gpuCullMeanMs: number | null;
  gpuCullP95Ms: number | null;
  cullWallMs: number | null;
  drawCalls: number;
  proceduralCandidateBytes: number;
  compactedIndexBytes: number;
  expandedTransformBytes: number;
  compressionRatio: number | null;
  adapter: string;
  timestampQuery: boolean;
  error: string | null;
};

export type FlowerInteraction = {
  position: readonly [number, number];
  velocity: readonly [number, number];
  speed: number;
  grounded: boolean;
};

export type FlowerFieldAssets = {
  grassAtlasUrl: string;
  petalAtlasUrl: string;
};

export type FlowerFieldView = {
  viewProjection: Float32Array;
  cameraPosition: readonly [number, number, number];
  elapsedSeconds: number;
};

const WORKGROUP_SIZE = 256;
const TILE_SIZE = 32;
const CANDIDATES_PER_TILE = TILE_SIZE * TILE_SIZE;
const UNIFORM_BYTES = 160;
const DRAW_COUNT = 8;
const DRAW_ARGS_BYTES = DRAW_COUNT * 16;
const FRAME_HISTORY = 360;
// Each tier owns one id buffer. Keeping them at 16 MiB limits the full
// visibility working set to 48 MiB while still supporting 4.19M virtual
// candidates on baseline WebGPU limits.
const MAX_REQUESTED_VISIBLE_BYTES = 16 * 1024 * 1024;

// Draw order: near stem/petals/centre, mid stem/petals/centre, far stem/head.
export const FLOWER_DRAW_VERTEX_COUNTS = Object.freeze([
  60, 528, 48,
  24, 132, 18,
  6, 6,
] as const);

export function maximumFlowerGridSize(limits: {
  maxStorageBufferBindingSize: number;
  maxBufferSize: number;
  maxComputeWorkgroupsPerDimension: number;
}) {
  const maximumVisibleBytes = Math.min(
    MAX_REQUESTED_VISIBLE_BYTES,
    limits.maxStorageBufferBindingSize,
    limits.maxBufferSize,
  );
  return Math.max(64, Math.min(
    Math.floor(Math.sqrt(maximumVisibleBytes / Uint32Array.BYTES_PER_ELEMENT)),
    Math.floor(Math.sqrt(limits.maxComputeWorkgroupsPerDimension * WORKGROUP_SIZE)),
  ));
}

export function flowerStorageMetrics(candidateCount: number, visibleCount: number | null) {
  const compactedIndexBytes = visibleCount === null ? 0 : visibleCount * Uint32Array.BYTES_PER_ELEMENT;
  // A conventional expanded path retains a 4x4 matrix plus eleven
  // scalar/vector attributes. This conservative 112-byte comparison excludes
  // JS object and array overhead, so the reported compression is not inflated.
  const expandedTransformBytes = candidateCount * 112;
  return {
    proceduralCandidateBytes: 0,
    compactedIndexBytes,
    expandedTransformBytes,
    compressionRatio: compactedIndexBytes > 0 ? expandedTransformBytes / compactedIndexBytes : null,
  };
}

const FLOWER_SHADER_COMMON = /* wgsl */ `
struct Uniforms {
  viewProj: mat4x4<f32>,
  cameraTime: vec4<f32>,
  field: vec4<f32>,
  style: vec4<f32>,
  viewportContact: vec4<f32>,
  contactVelocity: vec4<f32>,
}

@group(0) @binding(0) var<uniform> uniforms: Uniforms;

fn hashU32(value: u32) -> u32 {
  var x = value;
  x = x ^ (x >> 16u);
  x = x * 0x7feb352du;
  x = x ^ (x >> 15u);
  x = x * 0x846ca68bu;
  return x ^ (x >> 16u);
}

fn hash01(value: u32) -> f32 {
  return f32(hashU32(value) & 0x00ffffffu) / 16777215.0;
}

fn noiseHash(cell: vec2<i32>, seed: u32) -> f32 {
  let x = bitcast<u32>(cell.x);
  let y = bitcast<u32>(cell.y);
  return hash01((x * 0x9e3779b9u) ^ (y * 0x85ebca6bu) ^ (seed * 0xc2b2ae35u));
}

fn valueNoise2(point: vec2<f32>, seed: u32) -> f32 {
  let cell = vec2<i32>(floor(point));
  let fraction = fract(point);
  let blend = fraction * fraction * (vec2<f32>(3.0) - 2.0 * fraction);
  let a = noiseHash(cell, seed);
  let b = noiseHash(cell + vec2<i32>(1, 0), seed);
  let c = noiseHash(cell + vec2<i32>(0, 1), seed);
  let d = noiseHash(cell + vec2<i32>(1, 1), seed);
  return mix(mix(a, b, blend.x), mix(c, d, blend.x), blend.y);
}

fn fractalNoise2(point: vec2<f32>, seed: u32) -> f32 {
  // Rotating every octave prevents the interpolation lattice from becoming a
  // visible axis-aligned pattern at meadow scale.
  let octave2 = vec2<f32>(point.x * 0.78 + point.y * 0.63, point.y * 0.78 - point.x * 0.63) * 2.07;
  let octave3 = vec2<f32>(octave2.x * 0.31 - octave2.y * 0.95, octave2.x * 0.95 + octave2.y * 0.31) * 1.91;
  return valueNoise2(point, seed) * 0.56
    + valueNoise2(octave2, seed + 17u) * 0.29
    + valueNoise2(octave3, seed + 43u) * 0.15;
}

fn organicField(world: vec2<f32>, scale: f32, salt: u32) -> f32 {
  let seed = u32(uniforms.style.y) + salt;
  let rotated = vec2<f32>(world.x * 0.819 + world.y * 0.574, world.y * 0.819 - world.x * 0.574);
  return fractalNoise2(rotated * scale + vec2<f32>(f32(seed & 255u) * 0.037, f32((seed >> 8u) & 255u) * 0.041), seed);
}

fn fieldSpan() -> f32 {
  return f32(u32(uniforms.field.x) - 1u) * uniforms.field.y;
}

fn candidateRoot(candidateId: u32) -> vec3<f32> {
  let grid = u32(uniforms.field.x);
  let gridX = candidateId % grid;
  let gridZ = candidateId / grid;
  // The lattice is only an address space. Independent jitter spans more than
  // eight cells, so neighbouring addresses overlap into a stable stochastic
  // point cloud instead of preserving rows, squares, or mathematical bands.
  let span = fieldSpan();
  let baseX = f32(gridX) * uniforms.field.y - span * 0.5;
  let baseZ = f32(gridZ) * uniforms.field.y - span * 0.5;
  let packedJitter = hashU32(candidateId * 11u + u32(uniforms.style.y));
  let jitterX = (f32(packedJitter & 0xffffu) / 65535.0 - 0.5) * uniforms.field.y * 8.60;
  let jitterZ = (f32(packedJitter >> 16u) / 65535.0 - 0.5) * uniforms.field.y * 8.60;
  let x = baseX + jitterX;
  let z = baseZ + jitterZ;
  // Root reconstruction runs for every rendered vertex. Relief therefore
  // belongs to the ground material, not to this hot path.
  return vec3<f32>(x, 0.0, z);
}

fn meadowPatch(root: vec3<f32>) -> f32 {
  let broad = organicField(root.xz, 0.024, 307u);
  let detail = organicField(root.xz, 0.071, 401u);
  // A small floor keeps scattered connectors between soft, irregular clumps—
  // never empty square cells or contour-like ribbons.
  return mix(0.10, 0.92, smoothstep(0.31, 0.73, broad * 0.78 + detail * 0.22));
}

fn candidateKept(candidateId: u32, root: vec3<f32>) -> bool {
  let distanceSquared = dot(root.xz - uniforms.cameraTime.xz, root.xz - uniforms.cameraTime.xz);
  let fullRadius = uniforms.field.z * 0.72;
  let distanceDensity = pow(1.0 - smoothstep(fullRadius * fullRadius, uniforms.field.z * uniforms.field.z, distanceSquared), 1.35);
  let ecology = meadowPatch(root);
  let keepProbability = uniforms.field.w * ecology * distanceDensity;
  return hash01(candidateId * 29u + u32(uniforms.style.y) * 3u) < keepProbability;
}

fn candidateAccepted(candidateId: u32, root: vec3<f32>) -> bool {
  let clip = uniforms.viewProj * vec4<f32>(root + vec3<f32>(0.0, 1.0, 0.0), 1.0);
  let margin = 1.15;
  return candidateKept(candidateId, root)
    && clip.w > 0.0
    && abs(clip.x) < clip.w * margin
    && clip.y > -clip.w * 1.2
    && clip.y < clip.w * 1.2;
}

fn candidateTier(root: vec3<f32>) -> u32 {
  let d = distance(root.xz, uniforms.cameraTime.xz);
  if (d < uniforms.contactVelocity.z) { return 0u; }
  if (d < uniforms.contactVelocity.w) { return 1u; }
  return 2u;
}

fn speciesFor(candidateId: u32, root: vec3<f32>) -> u32 {
  // Species is deliberately independent per flower. Ecology controls density;
  // colour never exposes an underlying spatial function at long range.
  let local = hash01(candidateId * 73u + u32(uniforms.style.y) * 7u);
  let selector = local;
  if (selector < 0.25) { return 0u; }
  if (selector < 0.41) { return 1u; }
  if (selector < 0.45) { return 2u; }
  if (selector < 0.56) { return 3u; }
  if (selector < 0.74) { return 4u; }
  if (selector < 0.89) { return 5u; }
  if (selector < 0.93) { return 6u; }
  return 7u;
}

fn variantFor(candidateId: u32) -> u32 {
  return hashU32(candidateId * 83u + u32(uniforms.style.y) * 11u) % 5u;
}

fn flowerScale(candidateId: u32, species: u32) -> f32 {
  let random = hash01(candidateId * 97u + u32(uniforms.style.y));
  var minimum = 0.72;
  var maximum = 1.28;
  if (species == 1u) { minimum = 0.68; maximum = 1.18; }
  if (species == 2u) { minimum = 0.70; maximum = 1.24; }
  if (species == 3u) { minimum = 0.66; maximum = 1.18; }
  if (species == 4u) { minimum = 0.42; maximum = 0.76; }
  if (species == 5u) { minimum = 0.46; maximum = 0.84; }
  if (species == 6u) { minimum = 0.52; maximum = 0.94; }
  if (species == 7u) { minimum = 0.48; maximum = 0.88; }
  return mix(minimum, maximum, random);
}

fn stemProperties(candidateId: u32, species: u32) -> vec4<f32> {
  let vigor = mix(0.68, 1.0, hash01(candidateId * 101u + u32(uniforms.style.y)));
  let scale = flowerScale(candidateId, species);
  var terminalScale = 1.0;
  if (species == 4u || species == 5u) { terminalScale = 0.84; }
  let height = mix(1.12, 1.48, vigor) * terminalScale * scale;
  let leanNoise = hash01(candidateId * 103u + u32(uniforms.style.y));
  let lean = mix(0.12, 0.62, pow(leanNoise, 0.72)) * mix(0.72, 1.05, vigor) * scale;
  let curvePower = mix(1.72, 2.48, hash01(candidateId * 107u + u32(uniforms.style.y)));
  let angle = hash01(candidateId * 109u + u32(uniforms.style.y)) * 6.28318530718;
  return vec4<f32>(height, lean, curvePower, angle);
}

fn interactionBend(root: vec3<f32>, along: f32) -> vec3<f32> {
  if (uniforms.style.w < 0.5) { return vec3<f32>(0.0); }
  let contact = uniforms.viewportContact.zw;
  let delta = root.xz - contact;
  let d = length(delta);
  let away = select(normalize(uniforms.contactVelocity.xy + vec2<f32>(0.001)), delta / max(d, 0.001), d > 0.001);
  let influence = (1.0 - smoothstep(0.34, 1.15, d)) * uniforms.style.w;
  let rooted = influence * along * along;
  return vec3<f32>(away.x * rooted * 0.82, -rooted * 0.28, away.y * rooted * 0.82);
}

fn stemPoint(candidateId: u32, root: vec3<f32>, along: f32, species: u32) -> vec3<f32> {
  let properties = stemProperties(candidateId, species);
  let leanDirection = vec2<f32>(cos(properties.w), sin(properties.w));
  let staticLean = leanDirection * properties.y * pow(along, properties.z);
  let phase = hash01(candidateId * 113u + u32(uniforms.style.y)) * 6.28318530718;
  let windSignal = sin(uniforms.cameraTime.w * 1.1 + phase)
    + sin(uniforms.cameraTime.w * 0.63 + phase * 0.4) * 0.32;
  let windDirection = normalize(vec2<f32>(0.72, 0.18));
  let windOffset = windDirection * windSignal * uniforms.style.x * 0.092 * along * along;
  return root + vec3<f32>(staticLean.x + windOffset.x, properties.x * along, staticLean.y + windOffset.y)
    + interactionBend(root, along);
}

fn headBasis(candidateId: u32, root: vec3<f32>, species: u32) -> mat3x3<f32> {
  let p0 = stemPoint(candidateId, root, 0.92, species);
  let p1 = stemPoint(candidateId, root, 1.0, species);
  let normal = normalize(p1 - p0);
  let yaw = hash01(candidateId * 127u + u32(uniforms.style.y)) * 6.28318530718;
  let seedAxis = vec3<f32>(cos(yaw), 0.0, sin(yaw));
  let axisX = normalize(seedAxis - normal * dot(seedAxis, normal));
  let axisZ = normalize(cross(normal, axisX));
  return mat3x3<f32>(axisX, normal, axisZ);
}

fn linearToSrgb(value: vec3<f32>) -> vec3<f32> {
  return mix(value * 12.92, 1.055 * pow(max(value, vec3<f32>(0.0)), vec3<f32>(1.0 / 2.4)) - 0.055, step(vec3<f32>(0.0031308), value));
}

fn fogAmount(root: vec3<f32>) -> f32 {
  let optical = max(distance(root.xz, uniforms.cameraTime.xz) - 28.0, 0.0);
  return clamp(1.0 - exp(-optical * 0.00115), 0.0, 0.84);
}
`;

const RESET_SHADER = /* wgsl */ `
struct DrawArgs { vertexCount: u32, instanceCount: atomic<u32>, firstVertex: u32, firstInstance: u32 }
struct DispatchArgs { workgroupCountX: atomic<u32>, workgroupCountY: u32, workgroupCountZ: u32, padding: u32 }
@group(0) @binding(0) var<storage, read_write> drawArgs: array<DrawArgs, ${DRAW_COUNT}>;
@group(0) @binding(1) var<storage, read_write> dispatchArgs: DispatchArgs;

@compute @workgroup_size(1)
fn reset() {
  let counts = array<u32, ${DRAW_COUNT}>(60u, 528u, 48u, 24u, 132u, 18u, 6u, 6u);
  for (var index = 0u; index < ${DRAW_COUNT}u; index += 1u) {
    drawArgs[index].vertexCount = counts[index];
    atomicStore(&drawArgs[index].instanceCount, 0u);
    drawArgs[index].firstVertex = 0u;
    drawArgs[index].firstInstance = 0u;
  }
  atomicStore(&dispatchArgs.workgroupCountX, 0u);
  dispatchArgs.workgroupCountY = 1u;
  dispatchArgs.workgroupCountZ = 1u;
  dispatchArgs.padding = 0u;
}
`;

const CULL_BINDINGS = /* wgsl */ `
struct DrawArgs { vertexCount: u32, instanceCount: atomic<u32>, firstVertex: u32, firstInstance: u32 }
@group(0) @binding(1) var<storage, read_write> nearIds: array<u32>;
@group(0) @binding(2) var<storage, read_write> midIds: array<u32>;
@group(0) @binding(3) var<storage, read_write> farIds: array<u32>;
@group(0) @binding(4) var<storage, read_write> drawArgs: array<DrawArgs, ${DRAW_COUNT}>;

fn appendCandidate(candidateId: u32, root: vec3<f32>) {
  let tier = candidateTier(root);
  if (tier == 0u) {
    let index = atomicAdd(&drawArgs[0].instanceCount, 1u);
    nearIds[index] = candidateId;
  } else if (tier == 1u) {
    let index = atomicAdd(&drawArgs[3].instanceCount, 1u);
    midIds[index] = candidateId;
  } else {
    let index = atomicAdd(&drawArgs[6].instanceCount, 1u);
    farIds[index] = candidateId;
  }
}
`;

const FLAT_CULL_SHADER = /* wgsl */ `${FLOWER_SHADER_COMMON}${CULL_BINDINGS}
@compute @workgroup_size(${WORKGROUP_SIZE})
fn compactCandidates(@builtin(global_invocation_id) invocation: vec3<u32>) {
  let candidateId = invocation.x;
  let candidateCount = u32(uniforms.field.x) * u32(uniforms.field.x);
  if (candidateId >= candidateCount) { return; }
  let root = candidateRoot(candidateId);
  if (candidateAccepted(candidateId, root)) { appendCandidate(candidateId, root); }
}
`;

const TILE_CULL_SHADER = /* wgsl */ `${FLOWER_SHADER_COMMON}
struct DispatchArgs { workgroupCountX: atomic<u32>, workgroupCountY: u32, workgroupCountZ: u32, padding: u32 }
@group(0) @binding(1) var<storage, read_write> visibleTiles: array<u32>;
@group(0) @binding(2) var<storage, read_write> dispatchArgs: DispatchArgs;

@compute @workgroup_size(${WORKGROUP_SIZE})
fn compactTiles(@builtin(global_invocation_id) invocation: vec3<u32>) {
  let grid = u32(uniforms.field.x);
  let tileGrid = (grid + ${TILE_SIZE - 1}u) / ${TILE_SIZE}u;
  let tileId = invocation.x;
  if (tileId >= tileGrid * tileGrid) { return; }
  let tileX = tileId % tileGrid;
  let tileZ = tileId / tileGrid;
  let centerX = min(tileX * ${TILE_SIZE}u + ${TILE_SIZE / 2}u, grid - 1u);
  let centerZ = min(tileZ * ${TILE_SIZE}u + ${TILE_SIZE / 2}u, grid - 1u);
  let span = fieldSpan();
  let center = vec2<f32>(f32(centerX) * uniforms.field.y - span * 0.5, f32(centerZ) * uniforms.field.y - span * 0.5);
  let radius = uniforms.field.y * f32(${TILE_SIZE}) * 0.96;
  let clip = uniforms.viewProj * vec4<f32>(center.x, 1.0, center.y, 1.0);
  let padding = radius * 2.5;
  let inFrustum = clip.w > -radius
    && abs(clip.x) < clip.w * 1.16 + padding
    && clip.y > -clip.w * 1.22 - padding
    && clip.y < clip.w * 1.22 + padding;
  if (distance(center, uniforms.cameraTime.xz) <= uniforms.field.z + radius && inFrustum) {
    let index = atomicAdd(&dispatchArgs.workgroupCountX, 1u);
    visibleTiles[index] = tileId;
  }
}
`;

const HIERARCHICAL_CULL_SHADER = /* wgsl */ `${FLOWER_SHADER_COMMON}${CULL_BINDINGS}
@group(0) @binding(5) var<storage, read> visibleTiles: array<u32>;

@compute @workgroup_size(${WORKGROUP_SIZE})
fn compactTileCandidates(@builtin(workgroup_id) workgroup: vec3<u32>, @builtin(local_invocation_index) lane: u32) {
  let grid = u32(uniforms.field.x);
  let tileGrid = (grid + ${TILE_SIZE - 1}u) / ${TILE_SIZE}u;
  let tileId = visibleTiles[workgroup.x];
  let tileX = tileId % tileGrid;
  let tileZ = tileId / tileGrid;
  for (var batch = 0u; batch < ${CANDIDATES_PER_TILE / WORKGROUP_SIZE}u; batch += 1u) {
    let localId = lane + batch * ${WORKGROUP_SIZE}u;
    let gridX = tileX * ${TILE_SIZE}u + localId % ${TILE_SIZE}u;
    let gridZ = tileZ * ${TILE_SIZE}u + localId / ${TILE_SIZE}u;
    if (gridX < grid && gridZ < grid) {
      let candidateId = gridZ * grid + gridX;
      let root = candidateRoot(candidateId);
      if (candidateAccepted(candidateId, root)) { appendCandidate(candidateId, root); }
    }
  }
}
`;

const FINALIZE_SHADER = /* wgsl */ `
struct DrawArgs { vertexCount: u32, instanceCount: atomic<u32>, firstVertex: u32, firstInstance: u32 }
@group(0) @binding(0) var<storage, read_write> drawArgs: array<DrawArgs, ${DRAW_COUNT}>;
@compute @workgroup_size(1)
fn finalize() {
  let nearCount = atomicLoad(&drawArgs[0].instanceCount);
  let midCount = atomicLoad(&drawArgs[3].instanceCount);
  let farCount = atomicLoad(&drawArgs[6].instanceCount);
  atomicStore(&drawArgs[1].instanceCount, nearCount);
  atomicStore(&drawArgs[2].instanceCount, nearCount);
  atomicStore(&drawArgs[4].instanceCount, midCount);
  atomicStore(&drawArgs[5].instanceCount, midCount);
  atomicStore(&drawArgs[7].instanceCount, farCount);
}
`;

const STEM_SHADER = /* wgsl */ `${FLOWER_SHADER_COMMON}
@group(0) @binding(1) var<storage, read> visibleIds: array<u32>;
@group(0) @binding(2) var fieldSampler: sampler;
@group(0) @binding(3) var grassAtlas: texture_2d<f32>;

struct StemOutput {
  @builtin(position) position: vec4<f32>,
  @location(0) color: vec3<f32>,
  @location(1) along: f32,
  @location(2) fog: f32,
  @location(3) visible: f32,
}

fn sampleGrass(root: vec3<f32>, seed: f32) -> vec3<f32> {
  let meadow = seed * 2.0 - 1.0;
  let variant = floor(hash01(u32(abs(root.x * 193.0 + root.z * 311.0)) + u32(seed * 101.0)) * 6.0);
  let tile = vec2<f32>(variant % 3.0, floor(variant / 3.0));
  let mirrored = vec2<f32>(1.0) - abs(fract(root.xz * 0.08) * 2.0 - vec2<f32>(1.0));
  let sampled = textureSampleLevel(grassAtlas, fieldSampler, (tile + mix(vec2<f32>(0.006), vec2<f32>(0.994), mirrored)) / vec2<f32>(3.0, 2.0), 1.5).rgb;
  let luma = dot(sampled, vec3<f32>(0.2126, 0.7152, 0.0722));
  var painted = mix(vec3<f32>(luma), sampled, 0.93);
  painted = mix(painted * vec3<f32>(0.76, 0.88, 0.92), painted * vec3<f32>(1.0, 0.96, 0.76), smoothstep(-0.58, 0.58, meadow));
  return painted;
}

fn makeStemVertex(candidateId: u32, vertexId: u32, segments: u32, accepted: bool) -> StemOutput {
  var output: StemOutput;
  if (!accepted) {
    output.position = vec4<f32>(2.0, 2.0, 2.0, 1.0);
    output.color = vec3<f32>(0.0);
    output.along = 0.0;
    output.fog = 0.0;
    output.visible = 0.0;
    return output;
  }
  let root = candidateRoot(candidateId);
  let species = speciesFor(candidateId, root);
  let verticesPerPlane = segments * 6u;
  let plane = vertexId / verticesPerPlane;
  let localVertex = vertexId % verticesPerPlane;
  let segment = localVertex / 6u;
  let corner = localVertex % 6u;
  var alongOffset = 0u;
  var sideSign = -1.0;
  if (corner == 1u || corner == 4u || corner == 5u) { alongOffset = 1u; }
  if (corner == 2u || corner == 3u || corner == 5u) { sideSign = 1.0; }
  let along = f32(segment + alongOffset) / f32(segments);
  let centre = stemPoint(candidateId, root, along, species);
  let leanAngle = stemProperties(candidateId, species).w + f32(plane) * 1.57079632679;
  let ribbonSide = normalize(vec2<f32>(-sin(leanAngle), cos(leanAngle)));
  let width = 0.029 * flowerScale(candidateId, species) * mix(1.12, 0.44, along);
  let world = centre + vec3<f32>(ribbonSide.x * width * sideSign, 0.0, ribbonSide.y * width * sideSign);
  let source = sampleGrass(root, hash01(candidateId * 131u));
  let paletteMatched = mix(vec3<f32>(0.18, 0.37, 0.055), source, 0.46);
  output.color = paletteMatched * mix(0.66, 0.76, smoothstep(0.0, 0.72, along));
  output.position = uniforms.viewProj * vec4<f32>(world, 1.0);
  output.along = along;
  output.fog = fogAmount(root);
  output.visible = 1.0;
  return output;
}

@vertex fn stemNear(@builtin(instance_index) instanceId: u32, @builtin(vertex_index) vertexId: u32) -> StemOutput {
  return makeStemVertex(visibleIds[instanceId], vertexId, 5u, true);
}
@vertex fn stemMid(@builtin(instance_index) instanceId: u32, @builtin(vertex_index) vertexId: u32) -> StemOutput {
  return makeStemVertex(visibleIds[instanceId], vertexId, 2u, true);
}
@vertex fn stemFar(@builtin(instance_index) instanceId: u32, @builtin(vertex_index) vertexId: u32) -> StemOutput {
  let candidateId = visibleIds[instanceId];
  let root = candidateRoot(candidateId);
  let species = speciesFor(candidateId, root);
  let properties = stemProperties(candidateId, species);
  let corners = array<vec2<f32>,6>(vec2<f32>(-1.0,0.0),vec2<f32>(1.0,0.0),vec2<f32>(-1.0,1.0),vec2<f32>(-1.0,1.0),vec2<f32>(1.0,0.0),vec2<f32>(1.0,1.0));
  let corner = corners[vertexId];
  let leanDirection = vec2<f32>(cos(properties.w), sin(properties.w));
  let sideDirection = vec2<f32>(-leanDirection.y, leanDirection.x);
  let along = corner.y;
  let centre = root + vec3<f32>(leanDirection.x * properties.y * along * along, properties.x * along, leanDirection.y * properties.y * along * along);
  let width = 0.018 * flowerScale(candidateId, species) * mix(1.0, 0.52, along);
  let world = centre + vec3<f32>(sideDirection.x * corner.x * width, 0.0, sideDirection.y * corner.x * width);
  var output: StemOutput;
  output.position = uniforms.viewProj * vec4<f32>(world, 1.0);
  output.color = vec3<f32>(0.24, 0.43, 0.095) * mix(0.72, 0.86, along);
  output.along = along;
  output.fog = fogAmount(root);
  output.visible = 1.0;
  return output;
}
@vertex fn stemDirect(@builtin(instance_index) instanceId: u32, @builtin(vertex_index) vertexId: u32) -> StemOutput {
  let root = candidateRoot(instanceId);
  return makeStemVertex(instanceId, vertexId, 5u, candidateAccepted(instanceId, root));
}

@fragment fn stemFragment(input: StemOutput, @builtin(front_facing) frontFacing: bool) -> @location(0) vec4<f32> {
  if (input.visible < 0.5) { discard; }
  let face = select(0.84, 1.0, frontFacing);
  let band = select(0.91, 1.04, input.along > 0.58);
  var color = input.color * face * band;
  color = mix(color, vec3<f32>(0.412, 0.658, 0.753), input.fog);
  return vec4<f32>(linearToSrgb(color), 1.0);
}
`;

const PETAL_SHADER = /* wgsl */ `${FLOWER_SHADER_COMMON}
@group(0) @binding(1) var<storage, read> visibleIds: array<u32>;
@group(0) @binding(2) var petalSampler: sampler;
@group(0) @binding(3) var petalAtlas: texture_2d<f32>;

struct PetalOutput {
  @builtin(position) position: vec4<f32>,
  @location(0) uv: vec2<f32>,
  @location(1) normal: vec3<f32>,
  @location(2) fog: f32,
  @location(3) visible: f32,
}

fn basePetalCount(species: u32) -> u32 {
  if (species == 1u || species == 2u || species == 5u || species == 7u) { return 5u; }
  if (species == 3u) { return 6u; }
  if (species == 6u) { return 9u; }
  return 8u;
}

fn variantDelta(variant: u32) -> u32 {
  if (variant == 0u) { return 0u; }
  if (variant == 2u) { return 2u; }
  return 1u;
}

fn profileA(species: u32) -> vec4<f32> {
  if (species == 1u || species == 7u) { return vec4<f32>(0.35, 0.16, 0.13, 0.055); }
  if (species == 3u) { return vec4<f32>(0.42, 0.13, 0.015, 0.04); }
  if (species == 2u || species == 5u) { return vec4<f32>(0.34, 0.15, -0.015, 0.07); }
  if (species == 6u) { return vec4<f32>(0.36, 0.09, 0.06, 0.045); }
  return vec4<f32>(0.37, 0.105, 0.005, 0.055);
}

fn profileB(species: u32) -> vec4<f32> {
  if (species == 1u || species == 7u) { return vec4<f32>(0.075, 0.095, 0.13, 0.0); }
  if (species == 3u) { return vec4<f32>(0.055, 0.085, 0.07, 0.0); }
  if (species == 2u || species == 5u) { return vec4<f32>(0.085, 0.065, 0.16, 0.0); }
  if (species == 6u) { return vec4<f32>(0.065, 0.10, 0.12, 0.0); }
  return vec4<f32>(0.055, 0.05, 0.09, 0.0);
}

fn variantShape(variant: u32) -> vec4<f32> {
  if (variant == 1u) { return vec4<f32>(0.95, 1.06, 1.18, 0.88); }
  if (variant == 2u) { return vec4<f32>(1.04, 1.02, 0.72, 1.18); }
  if (variant == 3u) { return vec4<f32>(0.98, 1.03, 1.24, 1.10); }
  if (variant == 4u) { return vec4<f32>(0.94, 1.08, 0.86, 0.84); }
  return vec4<f32>(1.0);
}

fn variantTwist(variant: u32) -> f32 {
  if (variant == 1u) { return 1.28; }
  if (variant == 2u) { return 0.76; }
  if (variant == 3u) { return 1.42; }
  if (variant == 4u) { return 1.16; }
  return 1.0;
}

fn speciesCalibration(species: u32, variant: u32) -> vec2<f32> {
  if (species != 5u) { return vec2<f32>(1.0); }
  let lengths = array<f32, 5>(1.04, 0.90, 1.14, 0.98, 1.12);
  let widths = array<f32, 5>(0.72, 0.56, 0.64, 0.78, 0.90);
  return vec2<f32>(lengths[variant], widths[variant]);
}

fn compatiblePair(species: u32, variant: u32) -> vec2<u32> {
  let moon = array<vec2<u32>,5>(vec2<u32>(1u,3u),vec2<u32>(0u,4u),vec2<u32>(0u,4u),vec2<u32>(0u,1u),vec2<u32>(1u,3u));
  let ember = array<vec2<u32>,5>(vec2<u32>(2u,3u),vec2<u32>(0u,3u),vec2<u32>(0u,4u),vec2<u32>(0u,1u),vec2<u32>(2u,3u));
  let frost = array<vec2<u32>,5>(vec2<u32>(2u,4u),vec2<u32>(0u,4u),vec2<u32>(0u,4u),vec2<u32>(0u,1u),vec2<u32>(1u,2u));
  let star = array<vec2<u32>,5>(vec2<u32>(1u,2u),vec2<u32>(0u,2u),vec2<u32>(3u,4u),vec2<u32>(2u,4u),vec2<u32>(2u,3u));
  let sun = array<vec2<u32>,5>(vec2<u32>(2u,3u),vec2<u32>(0u,4u),vec2<u32>(0u,3u),vec2<u32>(0u,2u),vec2<u32>(0u,1u));
  let flax = array<vec2<u32>,5>(vec2<u32>(1u,3u),vec2<u32>(0u,2u),vec2<u32>(1u,3u),vec2<u32>(0u,2u),vec2<u32>(0u,2u));
  let ice = array<vec2<u32>,5>(vec2<u32>(1u,2u),vec2<u32>(0u,4u),vec2<u32>(0u,4u),vec2<u32>(1u,4u),vec2<u32>(0u,2u));
  let coral = array<vec2<u32>,5>(vec2<u32>(1u,2u),vec2<u32>(0u,3u),vec2<u32>(0u,3u),vec2<u32>(1u,2u),vec2<u32>(0u,2u));
  if (species == 0u) { return moon[variant]; }
  if (species == 1u) { return ember[variant]; }
  if (species == 2u) { return frost[variant]; }
  if (species == 3u) { return star[variant]; }
  if (species == 4u) { return sun[variant]; }
  if (species == 5u) { return flax[variant]; }
  if (species == 6u) { return ice[variant]; }
  return coral[variant];
}

fn petalVariant(candidateId: u32, species: u32, dominant: u32, slot: u32, petalCount: u32) -> u32 {
  if (uniforms.style.z < 0.5) { return dominant; }
  let pair = compatiblePair(species, dominant);
  let dominantCount = u32(ceil(f32(petalCount) * 0.62));
  let compatibleACount = u32(ceil(f32(petalCount - dominantCount) * 0.64));
  let offset = hashU32(candidateId * 137u + u32(uniforms.style.y)) % petalCount;
  let stride = select(1u, petalCount - 1u, hash01(candidateId * 139u) < 0.5);
  let order = (slot * stride + offset) % petalCount;
  if (order < dominantCount) { return dominant; }
  if (order < dominantCount + compatibleACount) { return pair.x; }
  return pair.y;
}

fn petalSurface(species: u32, variant: u32, slot: u32, petalCount: u32, along: f32, across: f32) -> mat2x3<f32> {
  let a = profileA(species);
  let b = profileB(species);
  let shape = variantShape(variant);
  let calibration = speciesCalibration(species, variant);
  let phase = f32(slot) * 12.9898 + f32(petalCount) * 4.1414 + f32(variant) * 7.31;
  let variation = sin(phase) * b.x;
  let bendNoise = sin(phase * 1.731 + 0.8);
  let twistNoise = sin(phase * 0.913 - 0.4);
  let twistCoefficient = twistNoise * b.z * variantTwist(variant);
  let angle = f32(slot) / f32(petalCount) * 6.28318530718 + variation * 0.45 + twistCoefficient * pow(along, 1.35);
  let axis = vec2<f32>(cos(angle), sin(angle));
  let tangent = vec2<f32>(-axis.y, axis.x);
  let radialGrowth = a.x * shape.x * calibration.x * 0.84 + variation * 0.18;
  let radius = 0.004 + along * radialGrowth;
  let bend = bendNoise * b.y * shape.w;
  let liftFloor = -0.032 * pow(along, 1.5);
  let rawLift = a.z * shape.z * pow(along, 1.55) + a.w * shape.w * sin(3.14159265359 * along) + bend * pow(along, 1.7);
  let lift = max(liftFloor, rawLift);
  let width = a.y * shape.y * calibration.y * 1.32;
  let transverseCup = (1.0 - across * across) * 0.014 * sin(3.14159265359 * along);
  let position = vec3<f32>(axis.x * radius + tangent.x * across * width, lift + transverseCup, axis.y * radius + tangent.y * across * width);

  let angleDerivative = twistCoefficient * 1.35 * pow(max(along, 0.0001), 0.35);
  let floorDerivative = -0.048 * sqrt(max(along, 0.0));
  let rawDerivative = a.z * shape.z * 1.55 * pow(max(along, 0.0001), 0.55)
    + a.w * shape.w * 3.14159265359 * cos(3.14159265359 * along)
    + bend * 1.7 * pow(max(along, 0.0001), 0.7);
  let liftDerivative = select(floorDerivative, rawDerivative, rawLift > liftFloor);
  let transverseAlong = (1.0 - across * across) * 0.014 * 3.14159265359 * cos(3.14159265359 * along);
  let transverseAcross = -2.0 * across * 0.014 * sin(3.14159265359 * along);
  let alongDerivative = vec3<f32>(
    axis.x * (radialGrowth - angleDerivative * across * width) + tangent.x * angleDerivative * radius,
    liftDerivative + transverseAlong,
    axis.y * (radialGrowth - angleDerivative * across * width) + tangent.y * angleDerivative * radius
  );
  let acrossDerivative = vec3<f32>(tangent.x * width, transverseAcross, tangent.y * width);
  let normal = normalize(cross(acrossDerivative, alongDerivative));
  return mat2x3<f32>(position, normal);
}

fn petalSurfaceMid(species: u32, variant: u32, slot: u32, petalCount: u32, along: f32, across: f32) -> mat2x3<f32> {
  let a = profileA(species);
  let shape = variantShape(variant);
  let calibration = speciesCalibration(species, variant);
  let phase = f32(slot) * 12.9898 + f32(petalCount) * 4.1414 + f32(variant) * 7.31;
  let angle = f32(slot) / f32(petalCount) * 6.28318530718 + sin(phase) * profileB(species).x * 0.45;
  let axis = vec2<f32>(cos(angle), sin(angle));
  let tangent = vec2<f32>(-axis.y, axis.x);
  let radius = 0.004 + along * a.x * shape.x * calibration.x * 0.84;
  let width = a.y * shape.y * calibration.y * 1.32;
  let lift = max(-0.032 * pow(along, 1.5), a.z * shape.z * pow(along, 1.55) + a.w * shape.w * sin(3.14159265359 * along));
  let position = vec3<f32>(axis.x * radius + tangent.x * across * width, lift, axis.y * radius + tangent.y * across * width);
  return mat2x3<f32>(position, vec3<f32>(0.0, 1.0, 0.0));
}

fn triangleCoordinates(vertexInPetal: u32, radialSegments: u32, lateralSegments: u32) -> vec2<f32> {
  let triangle = vertexInPetal / 3u;
  let corner = vertexInPetal % 3u;
  let cell = triangle / 2u;
  let triangleInCell = triangle % 2u;
  let radial = cell / lateralSegments;
  let lateral = cell % lateralSegments;
  var radialOffset = 0u;
  var lateralOffset = 0u;
  if (triangleInCell == 0u) {
    if (corner == 1u) { radialOffset = 1u; }
    if (corner == 2u) { lateralOffset = 1u; }
  } else {
    if (corner == 0u) { lateralOffset = 1u; }
    if (corner == 1u || corner == 2u) { radialOffset = 1u; }
    if (corner == 2u) { lateralOffset = 1u; }
  }
  let along = f32(radial + radialOffset) / f32(radialSegments);
  let across = f32(lateral + lateralOffset) / f32(lateralSegments) * 2.0 - 1.0;
  return vec2<f32>(along, across);
}

fn makePetalVertex(candidateId: u32, vertexId: u32, radialSegments: u32, lateralSegments: u32, verticesPerPetal: u32, accepted: bool) -> PetalOutput {
  var output: PetalOutput;
  let root = candidateRoot(candidateId);
  let species = speciesFor(candidateId, root);
  let dominant = variantFor(candidateId);
  let petalCount = basePetalCount(species) + variantDelta(dominant);
  let slot = vertexId / verticesPerPetal;
  let visible = accepted && slot < petalCount;
  if (!visible) {
    output.position = vec4<f32>(2.0, 2.0, 2.0, 1.0);
    output.uv = vec2<f32>(0.0);
    output.normal = vec3<f32>(0.0, 1.0, 0.0);
    output.fog = 0.0;
    output.visible = 0.0;
    return output;
  }
  let coordinates = triangleCoordinates(vertexId % verticesPerPetal, radialSegments, lateralSegments);
  var surface: mat2x3<f32>;
  if (radialSegments <= 2u) {
    surface = petalSurfaceMid(species, dominant, slot, petalCount, coordinates.x, coordinates.y);
  } else {
    surface = petalSurface(species, dominant, slot, petalCount, coordinates.x, coordinates.y);
  }
  let basis = headBasis(candidateId, root, species);
  let head = stemPoint(candidateId, root, 1.0, species);
  var headScale = flowerScale(candidateId, species);
  if (species == 0u) { headScale *= 0.92; }
  if (species == 1u) { headScale *= 0.90; }
  if (species == 2u || species == 3u) { headScale *= 0.88; }
  if (species == 4u) { headScale *= 0.72; }
  if (species == 5u || species == 7u) { headScale *= 0.82; }
  if (species == 6u) { headScale *= 0.86; }
  headScale *= mix(0.94, 1.06, hash01(candidateId * 149u));
  let world = head + basis * (surface[0] * headScale);
  let worldNormal = normalize(basis * surface[1]);
  let paintedVariant = petalVariant(candidateId, species, dominant, slot, petalCount);
  let localUv = vec2<f32>(0.03 + (coordinates.y * 0.5 + 0.5) * 0.94, 0.025 + (1.0 - coordinates.x) * 0.95);
  output.uv = (vec2<f32>(f32(species), f32(paintedVariant)) + localUv) / vec2<f32>(8.0, 5.0);
  output.position = uniforms.viewProj * vec4<f32>(world, 1.0);
  output.normal = worldNormal;
  output.fog = fogAmount(root);
  output.visible = 1.0;
  return output;
}

@vertex fn petalNear(@builtin(instance_index) instanceId: u32, @builtin(vertex_index) vertexId: u32) -> PetalOutput {
  return makePetalVertex(visibleIds[instanceId], vertexId, 4u, 2u, 48u, true);
}
@vertex fn petalMid(@builtin(instance_index) instanceId: u32, @builtin(vertex_index) vertexId: u32) -> PetalOutput {
  return makePetalVertex(visibleIds[instanceId], vertexId, 2u, 1u, 12u, true);
}
@vertex fn petalDirect(@builtin(instance_index) instanceId: u32, @builtin(vertex_index) vertexId: u32) -> PetalOutput {
  let root = candidateRoot(instanceId);
  return makePetalVertex(instanceId, vertexId, 6u, 2u, 72u, candidateAccepted(instanceId, root));
}

@fragment fn petalFragment(input: PetalOutput, @builtin(front_facing) frontFacing: bool) -> @location(0) vec4<f32> {
  if (input.visible < 0.5) { discard; }
  let texel = textureSample(petalAtlas, petalSampler, input.uv);
  if (texel.a < 0.34) { discard; }
  let normal = select(-input.normal, input.normal, frontFacing);
  let light = max(dot(normalize(normal), normalize(vec3<f32>(-0.42, 0.82, 0.38))), 0.0);
  let toon = select(0.82, select(0.94, 1.05, light > 0.58), light > 0.16);
  var color = texel.rgb * toon + texel.rgb * 0.12;
  color = mix(color, vec3<f32>(0.412, 0.658, 0.753), input.fog);
  return vec4<f32>(linearToSrgb(color), 1.0);
}
`;

const CENTER_SHADER = /* wgsl */ `${FLOWER_SHADER_COMMON}
@group(0) @binding(1) var<storage, read> visibleIds: array<u32>;
struct CenterOutput { @builtin(position) position: vec4<f32>, @location(0) normal: vec3<f32>, @location(1) fog: f32 }

fn makeCenterVertex(candidateId: u32, vertexId: u32, wedges: u32, accepted: bool) -> CenterOutput {
  let root = candidateRoot(candidateId);
  let species = speciesFor(candidateId, root);
  let wedge = vertexId / 3u;
  let corner = vertexId % 3u;
  let angle0 = f32(wedge) / f32(wedges) * 6.28318530718;
  let angle1 = f32(wedge + 1u) / f32(wedges) * 6.28318530718;
  var local = vec3<f32>(0.0, 0.024, 0.0);
  if (corner == 1u) { local = vec3<f32>(cos(angle0) * 0.082, 0.006, sin(angle0) * 0.082); }
  if (corner == 2u) { local = vec3<f32>(cos(angle1) * 0.082, 0.006, sin(angle1) * 0.082); }
  let scale = flowerScale(candidateId, species);
  let basis = headBasis(candidateId, root, species);
  let world = stemPoint(candidateId, root, 1.0, species) + basis * (local * scale);
  var output: CenterOutput;
  if (!accepted) {
    output.position = vec4<f32>(2.0, 2.0, 2.0, 1.0);
    output.normal = vec3<f32>(0.0, 1.0, 0.0);
    output.fog = 0.0;
    return output;
  }
  output.position = uniforms.viewProj * vec4<f32>(world, 1.0);
  output.normal = basis[1];
  output.fog = fogAmount(root);
  return output;
}
@vertex fn centerNear(@builtin(instance_index) instanceId: u32, @builtin(vertex_index) vertexId: u32) -> CenterOutput { return makeCenterVertex(visibleIds[instanceId], vertexId, 16u, true); }
@vertex fn centerMid(@builtin(instance_index) instanceId: u32, @builtin(vertex_index) vertexId: u32) -> CenterOutput { return makeCenterVertex(visibleIds[instanceId], vertexId, 6u, true); }
@vertex fn centerDirect(@builtin(instance_index) instanceId: u32, @builtin(vertex_index) vertexId: u32) -> CenterOutput { let root = candidateRoot(instanceId); return makeCenterVertex(instanceId, vertexId, 16u, candidateAccepted(instanceId, root)); }
@fragment fn centerFragment(input: CenterOutput) -> @location(0) vec4<f32> {
  let light = max(dot(normalize(input.normal), normalize(vec3<f32>(-0.42, 0.82, 0.38))), 0.0);
  var color = vec3<f32>(0.72, 0.43, 0.055) * select(0.84, select(0.96, 1.06, light > 0.58), light > 0.16);
  color = mix(color, vec3<f32>(0.412, 0.658, 0.753), input.fog);
  return vec4<f32>(linearToSrgb(color), 1.0);
}
`;

const FAR_HEAD_SHADER = /* wgsl */ `${FLOWER_SHADER_COMMON}
@group(0) @binding(1) var<storage, read> visibleIds: array<u32>;
@group(0) @binding(2) var petalSampler: sampler;
@group(0) @binding(3) var petalAtlas: texture_2d<f32>;
struct FarOutput { @builtin(position) position: vec4<f32>, @location(0) local: vec2<f32>, @location(1) speciesVariant: vec2<f32>, @location(2) fog: f32 }

@vertex fn farHead(@builtin(instance_index) instanceId: u32, @builtin(vertex_index) vertexId: u32) -> FarOutput {
  let candidateId = visibleIds[instanceId];
  let root = candidateRoot(candidateId);
  let species = speciesFor(candidateId, root);
  let variant = variantFor(candidateId);
  let corners = array<vec2<f32>,6>(vec2<f32>(-1.0,-1.0),vec2<f32>(1.0,-1.0),vec2<f32>(-1.0,1.0),vec2<f32>(-1.0,1.0),vec2<f32>(1.0,-1.0),vec2<f32>(1.0,1.0));
  let local = corners[vertexId];
  let properties = stemProperties(candidateId, species);
  let leanDirection = vec2<f32>(cos(properties.w), sin(properties.w));
  let head = root + vec3<f32>(leanDirection.x * properties.y, properties.x, leanDirection.y * properties.y);
  let scale = flowerScale(candidateId, species) * select(0.34, 0.42, species == 3u || species == 6u);
  let world = head + vec3<f32>(local.x * scale, 0.0, local.y * scale);
  var output: FarOutput;
  output.position = uniforms.viewProj * vec4<f32>(world, 1.0);
  output.local = local;
  output.speciesVariant = vec2<f32>(f32(species), f32(variant));
  output.fog = fogAmount(root);
  return output;
}

fn farBaseCount(species: u32) -> f32 {
  if (species == 1u || species == 2u || species == 5u || species == 7u) { return 5.0; }
  if (species == 3u) { return 6.0; }
  if (species == 6u) { return 9.0; }
  return 8.0;
}

fn farSpeciesColor(species: u32, variant: u32) -> vec3<f32> {
  var color = vec3<f32>(0.78, 0.70, 0.56);
  if (species == 1u) { color = vec3<f32>(0.92, 0.36, 0.035); }
  if (species == 2u) { color = vec3<f32>(0.16, 0.52, 0.82); }
  if (species == 3u) { color = vec3<f32>(0.90, 0.15, 0.48); }
  if (species == 4u) { color = vec3<f32>(0.94, 0.65, 0.035); }
  if (species == 5u) { color = vec3<f32>(0.06, 0.25, 0.86); }
  if (species == 6u) { color = vec3<f32>(0.24, 0.78, 0.68); }
  if (species == 7u) { color = vec3<f32>(0.94, 0.22, 0.12); }
  return color * mix(0.92, 1.08, f32(variant) * 0.25);
}

@fragment fn farFragment(input: FarOutput) -> @location(0) vec4<f32> {
  let radius = length(input.local);
  let species = u32(input.speciesVariant.x + 0.5);
  let variant = u32(input.speciesVariant.y + 0.5);
  let petalCount = farBaseCount(species) + select(0.0, select(1.0, 2.0, variant == 2u), variant > 0u);
  let angle = atan2(input.local.y, input.local.x);
  let sector = fract(angle / 6.28318530718 * petalCount + 0.5) - 0.5;
  let angularWidth = 0.50 * (1.0 - smoothstep(0.08, 1.0, radius));
  let petalMask = 1.0 - smoothstep(angularWidth, angularWidth + 0.10, abs(sector));
  let silhouette = petalMask * (1.0 - smoothstep(0.80, 1.0, radius));
  let centerMask = 1.0 - smoothstep(0.15, 0.27, radius);
  if (max(silhouette, centerMask) < 0.34) { discard; }
  let petal = farSpeciesColor(species, variant);
  var color = mix(petal, vec3<f32>(0.72, 0.43, 0.055), centerMask);
  color = mix(color, vec3<f32>(0.412, 0.658, 0.753), input.fog);
  return vec4<f32>(sqrt(max(color, vec3<f32>(0.0))), 1.0);
}
`;

const GROUND_SHADER = /* wgsl */ `${FLOWER_SHADER_COMMON}
@group(0) @binding(1) var fieldSampler: sampler;
@group(0) @binding(2) var grassAtlas: texture_2d<f32>;
struct GroundOutput { @builtin(position) position: vec4<f32>, @location(0) world: vec2<f32> }
fn hash2(value: vec2<f32>) -> f32 { return fract(sin(dot(value, vec2<f32>(127.1,311.7))) * 43758.5453); }
@vertex fn groundVertex(@builtin(vertex_index) vertexId: u32) -> GroundOutput {
  let corners = array<vec2<f32>,6>(vec2<f32>(-1.0,-1.0),vec2<f32>(-1.0,1.0),vec2<f32>(1.0,-1.0),vec2<f32>(-1.0,1.0),vec2<f32>(1.0,1.0),vec2<f32>(1.0,-1.0));
  let extent = max(uniforms.field.z * 1.75, 120.0);
  let world = corners[vertexId] * extent;
  var output: GroundOutput;
  output.position = uniforms.viewProj * vec4<f32>(world.x, -0.025, world.y, 1.0);
  output.world = world;
  return output;
}
fn sampleTile(world: vec2<f32>, variant: f32) -> vec3<f32> {
  let tile = vec2<f32>(variant % 3.0, floor(variant / 3.0));
  let mirrored = vec2<f32>(1.0) - abs(fract(world * 0.08) * 2.0 - vec2<f32>(1.0));
  return textureSample(grassAtlas, fieldSampler, (tile + mix(vec2<f32>(0.006),vec2<f32>(0.994),mirrored)) / vec2<f32>(3.0,2.0)).rgb;
}
@fragment fn groundFragment(input: GroundOutput) -> @location(0) vec4<f32> {
  let variant = floor(hash2(floor(input.world * 0.045) + vec2<f32>(31.7,-17.9)) * 6.0);
  let sampled = sampleTile(input.world, variant);
  let luma = dot(sampled, vec3<f32>(0.2126,0.7152,0.0722));
  var color = mix(vec3<f32>(luma), sampled, 0.93);
  color = color * vec3<f32>(0.87,0.92,0.84) * 0.77;
  let d = distance(input.world, uniforms.cameraTime.xz);
  color = mix(color, vec3<f32>(0.412,0.658,0.753), clamp(1.0-exp(-max(d-28.0,0.0)*0.00115),0.0,0.94));
  return vec4<f32>(linearToSrgb(color),1.0);
}
`;

function percentile(values: readonly number[], fraction: number) {
  if (values.length === 0) return 0;
  const sorted = [...values].sort((left, right) => left - right);
  return sorted[Math.min(sorted.length - 1, Math.floor(sorted.length * fraction))];
}

function mean(values: readonly number[]) {
  return values.length === 0 ? 0 : values.reduce((sum, value) => sum + value, 0) / values.length;
}

async function shaderModule(device: GPUDevice, label: string, code: string) {
  const shader = device.createShaderModule({ label, code });
  const info = await shader.getCompilationInfo();
  const errors = info.messages.filter((message) => message.type === "error");
  if (errors.length > 0) {
    throw new Error(`${label}: ${errors.map((message) => `${message.lineNum}:${message.linePos} ${message.message}`).join(" | ")}`);
  }
  return shader;
}

async function textureFromUrl(device: GPUDevice, label: string, url: string, format: GPUTextureFormat) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`${label} failed to load (${response.status}).`);
  const bitmap = await createImageBitmap(await response.blob());
  const mipLevelCount = Math.floor(Math.log2(Math.max(bitmap.width, bitmap.height))) + 1;
  const texture = device.createTexture({
    label,
    size: [bitmap.width, bitmap.height],
    mipLevelCount,
    format,
    usage: GPUTextureUsage.TEXTURE_BINDING | GPUTextureUsage.COPY_DST | GPUTextureUsage.RENDER_ATTACHMENT,
  });
  const canvas = document.createElement("canvas");
  const context = canvas.getContext("2d");
  if (!context) {
    bitmap.close();
    texture.destroy();
    throw new Error(`Could not prepare ${label}.`);
  }
  for (let level = 0; level < mipLevelCount; level += 1) {
    const width = Math.max(1, bitmap.width >> level);
    const height = Math.max(1, bitmap.height >> level);
    canvas.width = width;
    canvas.height = height;
    context.clearRect(0, 0, width, height);
    context.imageSmoothingEnabled = true;
    context.imageSmoothingQuality = "high";
    context.drawImage(bitmap, 0, 0, width, height);
    device.queue.copyExternalImageToTexture({ source: canvas }, { texture, mipLevel: level }, [width, height]);
  }
  bitmap.close();
  return texture;
}

export class GpuCulledFlowerField {
  private readonly canvas: HTMLCanvasElement;
  private readonly assets: FlowerFieldAssets;
  private options: FlowerLabOptions;
  private adapter: GPUAdapter | null = null;
  private device: GPUDevice | null = null;
  private context: GPUCanvasContext | null = null;
  private format: GPUTextureFormat = "bgra8unorm";
  private uniformBuffer: GPUBuffer | null = null;
  private visibleBuffers: GPUBuffer[] = [];
  private visibleTiles: GPUBuffer | null = null;
  private drawArgs: GPUBuffer | null = null;
  private dispatchArgs: GPUBuffer | null = null;
  private countReadback: GPUBuffer | null = null;
  private depthTexture: GPUTexture | null = null;
  private grassTexture: GPUTexture | null = null;
  private petalTexture: GPUTexture | null = null;
  private sampler: GPUSampler | null = null;
  private pipelines: Record<string, GPURenderPipeline> = {};
  private renderBindGroups: Record<string, GPUBindGroup> = {};
  private resetPipeline: GPUComputePipeline | null = null;
  private flatCullPipeline: GPUComputePipeline | null = null;
  private tileCullPipeline: GPUComputePipeline | null = null;
  private hierarchicalCullPipeline: GPUComputePipeline | null = null;
  private finalizePipeline: GPUComputePipeline | null = null;
  private resetBindGroup: GPUBindGroup | null = null;
  private flatCullBindGroup: GPUBindGroup | null = null;
  private tileCullBindGroup: GPUBindGroup | null = null;
  private hierarchicalCullBindGroup: GPUBindGroup | null = null;
  private finalizeBindGroup: GPUBindGroup | null = null;
  private timestampQuery: GPUQuerySet | null = null;
  private timestampResolve: GPUBuffer | null = null;
  private timestampReadback: GPUBuffer | null = null;
  private cullTimestampQuery: GPUQuerySet | null = null;
  private cullTimestampResolve: GPUBuffer | null = null;
  private cullTimestampReadback: GPUBuffer | null = null;
  private timestampPending = false;
  private cullTimestampPending = false;
  private countPending = false;
  private frameTimes: number[] = [];
  private submitTimes: number[] = [];
  private gpuRenderTimes: number[] = [];
  private gpuCullTimes: number[] = [];
  private visibleTiers: [number, number, number] | null = null;
  private visibleTileCount: number | null = null;
  private cullWallMs: number | null = null;
  private cullStartedAt = 0;
  private ready = false;
  private disposed = false;
  private cullDirty = true;
  private error: string | null = null;
  private lastFrame = 0;
  private frameIndex = 0;
  private maxGridSize = 2048;
  private adapterLabel = "Unknown WebGPU adapter";
  private lastViewProjection: Float32Array | null = null;
  private interaction: FlowerInteraction = { position: [100000, 100000], velocity: [0, 0], speed: 0, grounded: false };

  constructor(canvas: HTMLCanvasElement, options: FlowerLabOptions, assets: FlowerFieldAssets) {
    this.canvas = canvas;
    this.options = { ...options };
    this.assets = { ...assets };
  }

  async init() {
    if (!navigator.gpu) throw new Error("WebGPU is unavailable in this browser.");
    this.adapter = await navigator.gpu.requestAdapter({ powerPreference: "high-performance" });
    if (!this.adapter) throw new Error("No WebGPU adapter was available.");
    const maximumVisibleBytes = Math.min(
      MAX_REQUESTED_VISIBLE_BYTES,
      Number(this.adapter.limits.maxStorageBufferBindingSize),
      Number(this.adapter.limits.maxBufferSize),
    );
    this.maxGridSize = maximumFlowerGridSize({
      maxStorageBufferBindingSize: Number(this.adapter.limits.maxStorageBufferBindingSize),
      maxBufferSize: Number(this.adapter.limits.maxBufferSize),
      maxComputeWorkgroupsPerDimension: Number(this.adapter.limits.maxComputeWorkgroupsPerDimension),
    });
    this.options.gridSize = Math.min(this.options.gridSize, this.maxGridSize);
    this.device = await this.adapter.requestDevice({
      requiredFeatures: this.adapter.features.has("timestamp-query") ? ["timestamp-query"] : [],
      requiredLimits: { maxStorageBufferBindingSize: maximumVisibleBytes },
    });
    this.device.lost.then((info) => { if (!this.disposed) this.fail(`WebGPU device lost: ${info.message || info.reason}`); });
    this.device.addEventListener("uncapturederror", (event) => this.fail(event.error.message));
    const info = this.adapter.info;
    this.adapterLabel = [info.vendor, info.architecture, info.device, info.description].filter(Boolean).join(" · ") || "WebGPU adapter";
    this.context = this.canvas.getContext("webgpu");
    if (!this.context) throw new Error("Could not create a WebGPU canvas context.");
    this.format = navigator.gpu.getPreferredCanvasFormat();
    this.context.configure({ device: this.device, format: this.format, alphaMode: "opaque" });

    this.uniformBuffer = this.device.createBuffer({ label: "flower field uniforms", size: UNIFORM_BYTES, usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST });
    this.drawArgs = this.device.createBuffer({ label: "flower indirect draw arguments", size: DRAW_ARGS_BYTES, usage: GPUBufferUsage.STORAGE | GPUBufferUsage.INDIRECT | GPUBufferUsage.COPY_SRC });
    this.dispatchArgs = this.device.createBuffer({ label: "flower indirect dispatch arguments", size: 16, usage: GPUBufferUsage.STORAGE | GPUBufferUsage.INDIRECT | GPUBufferUsage.COPY_SRC });
    this.countReadback = this.device.createBuffer({ label: "flower visibility readback", size: DRAW_ARGS_BYTES + 16, usage: GPUBufferUsage.COPY_DST | GPUBufferUsage.MAP_READ });
    this.sampler = this.device.createSampler({ label: "flower painted sampler", addressModeU: "clamp-to-edge", addressModeV: "clamp-to-edge", magFilter: "linear", minFilter: "linear", mipmapFilter: "linear", maxAnisotropy: 8 });
    [this.grassTexture, this.petalTexture] = await Promise.all([
      textureFromUrl(this.device, "painted grass atlas", this.assets.grassAtlasUrl, "rgba8unorm"),
      textureFromUrl(this.device, "individual petal atlas", this.assets.petalAtlasUrl, "rgba8unorm-srgb"),
    ]);

    if (this.device.features.has("timestamp-query")) {
      this.timestampQuery = this.device.createQuerySet({ type: "timestamp", count: 2 });
      this.timestampResolve = this.device.createBuffer({ size: 16, usage: GPUBufferUsage.QUERY_RESOLVE | GPUBufferUsage.COPY_SRC });
      this.timestampReadback = this.device.createBuffer({ size: 16, usage: GPUBufferUsage.COPY_DST | GPUBufferUsage.MAP_READ });
      this.cullTimestampQuery = this.device.createQuerySet({ type: "timestamp", count: 4 });
      this.cullTimestampResolve = this.device.createBuffer({ size: 32, usage: GPUBufferUsage.QUERY_RESOLVE | GPUBufferUsage.COPY_SRC });
      this.cullTimestampReadback = this.device.createBuffer({ size: 32, usage: GPUBufferUsage.COPY_DST | GPUBufferUsage.MAP_READ });
    }

    await this.createPipelines();
    this.rebuildVisibilityResources();
    this.ready = true;
    this.lastFrame = performance.now();
  }

  private async createPipelines() {
    if (!this.device) return;
    const [stem, petal, center, far, ground, reset, flat, tile, hierarchical, finalize] = await Promise.all([
      shaderModule(this.device, "procedural flower stems", STEM_SHADER),
      shaderModule(this.device, "procedural curved flower petals", PETAL_SHADER),
      shaderModule(this.device, "procedural flower centres", CENTER_SHADER),
      shaderModule(this.device, "procedural far flower heads", FAR_HEAD_SHADER),
      shaderModule(this.device, "flower field ground", GROUND_SHADER),
      shaderModule(this.device, "flower indirect reset", RESET_SHADER),
      shaderModule(this.device, "flower flat culling", FLAT_CULL_SHADER),
      shaderModule(this.device, "flower tile culling", TILE_CULL_SHADER),
      shaderModule(this.device, "flower hierarchical culling", HIERARCHICAL_CULL_SHADER),
      shaderModule(this.device, "flower indirect finalize", FINALIZE_SHADER),
    ]);
    const targets: GPUColorTargetState[] = [{ format: this.format }];
    const depthStencil: GPUDepthStencilState = { format: "depth24plus", depthWriteEnabled: true, depthCompare: "less" };
    const renderPipeline = (label: string, module: GPUShaderModule, entryPoint: string, fragmentEntry: string, cullMode: GPUCullMode = "none") => this.device!.createRenderPipelineAsync({
      label,
      layout: "auto",
      vertex: { module, entryPoint },
      fragment: { module, entryPoint: fragmentEntry, targets },
      primitive: { topology: "triangle-list", cullMode },
      depthStencil,
    });
    const entries = await Promise.all([
      renderPipeline("near flower stems", stem, "stemNear", "stemFragment"),
      renderPipeline("mid flower stems", stem, "stemMid", "stemFragment"),
      renderPipeline("far flower stems", stem, "stemFar", "stemFragment"),
      renderPipeline("direct flower stems", stem, "stemDirect", "stemFragment"),
      renderPipeline("near exact curved petals", petal, "petalNear", "petalFragment"),
      renderPipeline("mid reduced curved petals", petal, "petalMid", "petalFragment"),
      renderPipeline("direct exact curved petals", petal, "petalDirect", "petalFragment"),
      renderPipeline("near flower centres", center, "centerNear", "centerFragment"),
      renderPipeline("mid flower centres", center, "centerMid", "centerFragment"),
      renderPipeline("direct flower centres", center, "centerDirect", "centerFragment"),
      renderPipeline("far procedural flower heads", far, "farHead", "farFragment"),
      renderPipeline("painted flower field ground", ground, "groundVertex", "groundFragment", "back"),
    ]);
    [
      "stemNear", "stemMid", "stemFar", "stemDirect", "petalNear", "petalMid", "petalDirect",
      "centerNear", "centerMid", "centerDirect", "far", "ground",
    ].forEach((key, index) => { this.pipelines[key] = entries[index]; });
    this.resetPipeline = await this.device.createComputePipelineAsync({ layout: "auto", compute: { module: reset, entryPoint: "reset" } });
    this.flatCullPipeline = await this.device.createComputePipelineAsync({ layout: "auto", compute: { module: flat, entryPoint: "compactCandidates" } });
    this.tileCullPipeline = await this.device.createComputePipelineAsync({ layout: "auto", compute: { module: tile, entryPoint: "compactTiles" } });
    this.hierarchicalCullPipeline = await this.device.createComputePipelineAsync({ layout: "auto", compute: { module: hierarchical, entryPoint: "compactTileCandidates" } });
    this.finalizePipeline = await this.device.createComputePipelineAsync({ layout: "auto", compute: { module: finalize, entryPoint: "finalize" } });
  }

  private rebuildVisibilityResources() {
    if (!this.device || !this.uniformBuffer || !this.drawArgs || !this.dispatchArgs || !this.sampler || !this.grassTexture || !this.petalTexture || !this.resetPipeline || !this.flatCullPipeline || !this.tileCullPipeline || !this.hierarchicalCullPipeline || !this.finalizePipeline) return;
    this.visibleBuffers.forEach((buffer) => buffer.destroy());
    this.visibleTiles?.destroy();
    const candidateCount = this.options.gridSize * this.options.gridSize;
    const tileGrid = Math.ceil(this.options.gridSize / TILE_SIZE);
    this.visibleBuffers = [0, 1, 2].map((tier) => this.device!.createBuffer({ label: `visible flower ids tier ${tier}`, size: Math.max(4, candidateCount * 4), usage: GPUBufferUsage.STORAGE }));
    this.visibleTiles = this.device.createBuffer({ label: "visible flower tiles", size: Math.max(4, tileGrid * tileGrid * 4), usage: GPUBufferUsage.STORAGE });

    const stemGroup = (pipeline: GPURenderPipeline, buffer: GPUBuffer, direct = false) => this.device!.createBindGroup({ layout: pipeline.getBindGroupLayout(0), entries: [
      { binding: 0, resource: { buffer: this.uniformBuffer! } }, ...direct ? [] : [{ binding: 1, resource: { buffer } }], { binding: 2, resource: this.sampler! }, { binding: 3, resource: this.grassTexture!.createView() },
    ] });
    const petalGroup = (pipeline: GPURenderPipeline, buffer: GPUBuffer, direct = false) => this.device!.createBindGroup({ layout: pipeline.getBindGroupLayout(0), entries: [
      { binding: 0, resource: { buffer: this.uniformBuffer! } }, ...direct ? [] : [{ binding: 1, resource: { buffer } }], { binding: 2, resource: this.sampler! }, { binding: 3, resource: this.petalTexture!.createView() },
    ] });
    const centerGroup = (pipeline: GPURenderPipeline, buffer: GPUBuffer, direct = false) => this.device!.createBindGroup({ layout: pipeline.getBindGroupLayout(0), entries: [
      { binding: 0, resource: { buffer: this.uniformBuffer! } }, ...direct ? [] : [{ binding: 1, resource: { buffer } }],
    ] });
    this.renderBindGroups = {
      stemNear: stemGroup(this.pipelines.stemNear, this.visibleBuffers[0]), stemMid: stemGroup(this.pipelines.stemMid, this.visibleBuffers[1]), stemFar: centerGroup(this.pipelines.stemFar, this.visibleBuffers[2]), stemDirect: stemGroup(this.pipelines.stemDirect, this.visibleBuffers[0], true),
      petalNear: petalGroup(this.pipelines.petalNear, this.visibleBuffers[0]), petalMid: petalGroup(this.pipelines.petalMid, this.visibleBuffers[1]), petalDirect: petalGroup(this.pipelines.petalDirect, this.visibleBuffers[0], true),
      centerNear: centerGroup(this.pipelines.centerNear, this.visibleBuffers[0]), centerMid: centerGroup(this.pipelines.centerMid, this.visibleBuffers[1]), centerDirect: centerGroup(this.pipelines.centerDirect, this.visibleBuffers[0], true),
      far: centerGroup(this.pipelines.far, this.visibleBuffers[2]),
      ground: this.device.createBindGroup({ layout: this.pipelines.ground.getBindGroupLayout(0), entries: [{ binding: 0, resource: { buffer: this.uniformBuffer } }, { binding: 1, resource: this.sampler }, { binding: 2, resource: this.grassTexture.createView() }] }),
    };
    this.resetBindGroup = this.device.createBindGroup({ layout: this.resetPipeline.getBindGroupLayout(0), entries: [{ binding: 0, resource: { buffer: this.drawArgs } }, { binding: 1, resource: { buffer: this.dispatchArgs } }] });
    const cullEntries = [
      { binding: 0, resource: { buffer: this.uniformBuffer } },
      { binding: 1, resource: { buffer: this.visibleBuffers[0] } },
      { binding: 2, resource: { buffer: this.visibleBuffers[1] } },
      { binding: 3, resource: { buffer: this.visibleBuffers[2] } },
      { binding: 4, resource: { buffer: this.drawArgs } },
    ];
    this.flatCullBindGroup = this.device.createBindGroup({ layout: this.flatCullPipeline.getBindGroupLayout(0), entries: cullEntries });
    this.tileCullBindGroup = this.device.createBindGroup({ layout: this.tileCullPipeline.getBindGroupLayout(0), entries: [{ binding: 0, resource: { buffer: this.uniformBuffer } }, { binding: 1, resource: { buffer: this.visibleTiles } }, { binding: 2, resource: { buffer: this.dispatchArgs } }] });
    this.hierarchicalCullBindGroup = this.device.createBindGroup({ layout: this.hierarchicalCullPipeline.getBindGroupLayout(0), entries: [...cullEntries, { binding: 5, resource: { buffer: this.visibleTiles } }] });
    this.finalizeBindGroup = this.device.createBindGroup({ layout: this.finalizePipeline.getBindGroupLayout(0), entries: [{ binding: 0, resource: { buffer: this.drawArgs } }] });
    this.visibleTiers = null;
    this.visibleTileCount = null;
    this.cullDirty = true;
  }

  resize(width: number, height: number, dpr = 1) {
    if (!this.device) return;
    const pixelWidth = Math.max(1, Math.floor(width * dpr));
    const pixelHeight = Math.max(1, Math.floor(height * dpr));
    if (pixelWidth === this.canvas.width && pixelHeight === this.canvas.height) return;
    this.canvas.width = pixelWidth;
    this.canvas.height = pixelHeight;
    this.depthTexture?.destroy();
    this.depthTexture = this.device.createTexture({ label: "flower field depth", size: [pixelWidth, pixelHeight], format: "depth24plus", usage: GPUTextureUsage.RENDER_ATTACHMENT });
    this.cullDirty = true;
  }

  private writeUniforms(view: FlowerFieldView) {
    if (!this.device || !this.uniformBuffer) return;
    const eye = view.cameraPosition;
    const values = new Float32Array(UNIFORM_BYTES / 4);
    values.set(view.viewProjection, 0);
    values.set([eye[0], eye[1], eye[2], view.elapsedSeconds], 16);
    values.set([this.options.gridSize, this.options.spacing, this.options.maxDistance, this.options.density], 20);
    values.set([this.options.wind, this.options.seed, this.options.mixPetalVariants ? 1 : 0, this.interaction.grounded ? 1 : 0], 24);
    values.set([this.canvas.width, this.canvas.height, this.interaction.position[0], this.interaction.position[1]], 28);
    values.set([this.interaction.velocity[0], this.interaction.velocity[1], this.options.nearDistance, this.options.midDistance], 32);
    this.device.queue.writeBuffer(this.uniformBuffer, 0, values);
  }

  private encodeCompaction(encoder: GPUCommandEncoder, query: GPUQuerySet | null) {
    if (!this.resetPipeline || !this.resetBindGroup || !this.finalizePipeline || !this.finalizeBindGroup || !this.dispatchArgs) return 0;
    const reset = encoder.beginComputePass({ label: "reset flower indirect counts" });
    reset.setPipeline(this.resetPipeline);
    reset.setBindGroup(0, this.resetBindGroup);
    reset.dispatchWorkgroups(1);
    reset.end();
    let queryCount = 0;
    if (this.options.cullingMode === "flat") {
      if (!this.flatCullPipeline || !this.flatCullBindGroup) return 0;
      const pass = encoder.beginComputePass({ label: "flat flower candidate compaction", ...(query ? { timestampWrites: { querySet: query, beginningOfPassWriteIndex: 0, endOfPassWriteIndex: 1 } } : {}) });
      pass.setPipeline(this.flatCullPipeline);
      pass.setBindGroup(0, this.flatCullBindGroup);
      pass.dispatchWorkgroups(Math.ceil(this.options.gridSize * this.options.gridSize / WORKGROUP_SIZE));
      pass.end();
      queryCount = query ? 2 : 0;
    } else {
      if (!this.tileCullPipeline || !this.tileCullBindGroup || !this.hierarchicalCullPipeline || !this.hierarchicalCullBindGroup) return 0;
      const tileGrid = Math.ceil(this.options.gridSize / TILE_SIZE);
      const tilePass = encoder.beginComputePass({ label: "compact visible flower tiles", ...(query ? { timestampWrites: { querySet: query, beginningOfPassWriteIndex: 0, endOfPassWriteIndex: 1 } } : {}) });
      tilePass.setPipeline(this.tileCullPipeline);
      tilePass.setBindGroup(0, this.tileCullBindGroup);
      tilePass.dispatchWorkgroups(Math.ceil(tileGrid * tileGrid / WORKGROUP_SIZE));
      tilePass.end();
      const candidatePass = encoder.beginComputePass({ label: "compact flowers in visible tiles", ...(query ? { timestampWrites: { querySet: query, beginningOfPassWriteIndex: 2, endOfPassWriteIndex: 3 } } : {}) });
      candidatePass.setPipeline(this.hierarchicalCullPipeline);
      candidatePass.setBindGroup(0, this.hierarchicalCullBindGroup);
      candidatePass.dispatchWorkgroupsIndirect(this.dispatchArgs, 0);
      candidatePass.end();
      queryCount = query ? 4 : 0;
    }
    const finalize = encoder.beginComputePass({ label: "fan out flower tier counts" });
    finalize.setPipeline(this.finalizePipeline);
    finalize.setBindGroup(0, this.finalizeBindGroup);
    finalize.dispatchWorkgroups(1);
    finalize.end();
    return queryCount;
  }

  private draw(pass: GPURenderPassEncoder, pipelineKey: string, drawIndex: number) {
    if (!this.drawArgs) return;
    pass.setPipeline(this.pipelines[pipelineKey]);
    pass.setBindGroup(0, this.renderBindGroups[pipelineKey]);
    pass.drawIndirect(this.drawArgs, drawIndex * 16);
  }

  render(timestamp: number, view: FlowerFieldView) {
    if (this.disposed || !this.ready || !this.device || !this.context || !this.depthTexture || !this.drawArgs) return;
    if (
      this.lastViewProjection === null ||
      view.viewProjection.some((value, index) => value !== this.lastViewProjection![index])
    ) {
      this.cullDirty = true;
      this.lastViewProjection = new Float32Array(view.viewProjection);
    }
    const delta = timestamp - this.lastFrame;
    this.lastFrame = timestamp;
    if (delta > 0 && delta < 1000) {
      this.frameTimes.push(delta);
      if (this.frameTimes.length > FRAME_HISTORY) this.frameTimes.shift();
    }
    this.writeUniforms(view);
    const encoder = this.device.createCommandEncoder({ label: "WebGPU flower field frame" });
    const submitStarted = performance.now();
    const shouldTimestamp = this.frameIndex % 10 === 0 && !this.timestampPending && this.timestampQuery && this.timestampResolve && this.timestampReadback;
    const shouldCullTimestamp = this.options.mode === "compact" && this.cullDirty && !this.cullTimestampPending && this.cullTimestampQuery && this.cullTimestampResolve && this.cullTimestampReadback;
    const queryCount = this.options.mode === "compact" && this.cullDirty
      ? this.encodeCompaction(encoder, shouldCullTimestamp ? this.cullTimestampQuery : null)
      : 0;
    const shouldReadCounts = this.options.mode === "compact" && this.cullDirty && !this.countPending && this.countReadback;

    const pass = encoder.beginRenderPass({
      label: "procedural flower field render",
      colorAttachments: [{ view: this.context.getCurrentTexture().createView(), clearValue: { r: 0.643, g: 0.851, b: 0.906, a: 1 }, loadOp: "clear", storeOp: "store" }],
      depthStencilAttachment: { view: this.depthTexture.createView(), depthClearValue: 1, depthLoadOp: "clear", depthStoreOp: "store" },
      ...(shouldTimestamp ? { timestampWrites: { querySet: this.timestampQuery!, beginningOfPassWriteIndex: 0, endOfPassWriteIndex: 1 } } : {}),
    });
    pass.setPipeline(this.pipelines.ground);
    pass.setBindGroup(0, this.renderBindGroups.ground);
    pass.draw(6);
    if (this.options.mode === "compact") {
      this.draw(pass, "stemNear", 0);
      this.draw(pass, "petalNear", 1);
      this.draw(pass, "centerNear", 2);
      this.draw(pass, "stemMid", 3);
      this.draw(pass, "petalMid", 4);
      this.draw(pass, "centerMid", 5);
      this.draw(pass, "stemFar", 6);
      this.draw(pass, "far", 7);
    } else {
      const count = this.options.gridSize * this.options.gridSize;
      pass.setPipeline(this.pipelines.stemDirect);
      pass.setBindGroup(0, this.renderBindGroups.stemDirect);
      pass.draw(FLOWER_DRAW_VERTEX_COUNTS[0], count);
      pass.setPipeline(this.pipelines.petalDirect);
      pass.setBindGroup(0, this.renderBindGroups.petalDirect);
      pass.draw(FLOWER_DRAW_VERTEX_COUNTS[1], count);
      pass.setPipeline(this.pipelines.centerDirect);
      pass.setBindGroup(0, this.renderBindGroups.centerDirect);
      pass.draw(FLOWER_DRAW_VERTEX_COUNTS[2], count);
    }
    pass.end();

    if (shouldTimestamp && this.timestampQuery && this.timestampResolve && this.timestampReadback) {
      encoder.resolveQuerySet(this.timestampQuery, 0, 2, this.timestampResolve, 0);
      encoder.copyBufferToBuffer(this.timestampResolve, 0, this.timestampReadback, 0, 16);
      this.timestampPending = true;
    }
    if (queryCount > 0 && this.cullTimestampQuery && this.cullTimestampResolve && this.cullTimestampReadback) {
      const bytes = queryCount * 8;
      encoder.resolveQuerySet(this.cullTimestampQuery, 0, queryCount, this.cullTimestampResolve, 0);
      encoder.copyBufferToBuffer(this.cullTimestampResolve, 0, this.cullTimestampReadback, 0, bytes);
      this.cullTimestampPending = true;
    }
    if (shouldReadCounts && this.countReadback) {
      encoder.copyBufferToBuffer(this.drawArgs, 0, this.countReadback, 0, DRAW_ARGS_BYTES);
      if (this.dispatchArgs) encoder.copyBufferToBuffer(this.dispatchArgs, 0, this.countReadback, DRAW_ARGS_BYTES, 16);
      this.countPending = true;
      this.cullStartedAt = performance.now();
    }
    this.device.queue.submit([encoder.finish()]);
    this.submitTimes.push(performance.now() - submitStarted);
    if (this.submitTimes.length > FRAME_HISTORY) this.submitTimes.shift();
    if (shouldTimestamp) void this.resolveRenderTimestamp();
    if (queryCount > 0) void this.resolveCullTimestamp(queryCount);
    if (shouldReadCounts) void this.resolveCounts();
    this.cullDirty = false;
    this.frameIndex += 1;
  }

  private async resolveRenderTimestamp() {
    if (!this.device || !this.timestampReadback) return;
    try {
      await this.device.queue.onSubmittedWorkDone();
      await this.timestampReadback.mapAsync(GPUMapMode.READ);
      const values = new BigUint64Array(this.timestampReadback.getMappedRange());
      const elapsed = Number(values[1] - values[0]) / 1_000_000;
      this.timestampReadback.unmap();
      if (Number.isFinite(elapsed)) {
        this.gpuRenderTimes.push(elapsed);
        if (this.gpuRenderTimes.length > 120) this.gpuRenderTimes.shift();
      }
    } catch (error) { if (!this.disposed) this.fail(String(error)); }
    finally { this.timestampPending = false; }
  }

  private async resolveCullTimestamp(queryCount: number) {
    if (!this.device || !this.cullTimestampReadback) return;
    try {
      await this.device.queue.onSubmittedWorkDone();
      await this.cullTimestampReadback.mapAsync(GPUMapMode.READ, 0, queryCount * 8);
      const values = new BigUint64Array(this.cullTimestampReadback.getMappedRange(0, queryCount * 8));
      let elapsed = values[1] - values[0];
      if (queryCount === 4) elapsed += values[3] - values[2];
      const milliseconds = Number(elapsed) / 1_000_000;
      this.cullTimestampReadback.unmap();
      if (Number.isFinite(milliseconds)) {
        this.gpuCullTimes.push(milliseconds);
        if (this.gpuCullTimes.length > 120) this.gpuCullTimes.shift();
      }
    } catch (error) { if (!this.disposed) this.fail(String(error)); }
    finally { this.cullTimestampPending = false; }
  }

  private async resolveCounts() {
    if (!this.device || !this.countReadback) return;
    try {
      await this.device.queue.onSubmittedWorkDone();
      await this.countReadback.mapAsync(GPUMapMode.READ);
      const values = new Uint32Array(this.countReadback.getMappedRange());
      this.visibleTiers = [values[1], values[13], values[25]];
      this.visibleTileCount = this.options.cullingMode === "hierarchical" ? values[32] : null;
      this.countReadback.unmap();
      this.cullWallMs = performance.now() - this.cullStartedAt;
    } catch (error) { if (!this.disposed) this.fail(String(error)); }
    finally { this.countPending = false; }
  }

  private fail(message: string) {
    this.error = message;
    console.error(`[WebGPU flower field] ${message}`);
  }

  setMode(mode: FlowerRenderMode) { this.options.mode = mode; this.cullDirty = true; }
  setCullingMode(mode: FlowerCullingMode) { this.options.cullingMode = mode; this.visibleTiers = null; this.visibleTileCount = null; this.cullDirty = true; }
  setGridSize(gridSize: number) {
    const next = Math.min(this.maxGridSize, Math.max(64, Math.floor(gridSize)));
    if (next === this.options.gridSize) return;
    this.options.gridSize = next;
    this.rebuildVisibilityResources();
  }
  setDensity(density: number) { this.options.density = Math.min(1, Math.max(0.02, density)); this.cullDirty = true; }
  setSpacing(spacing: number) { this.options.spacing = Math.min(0.8, Math.max(0.12, spacing)); this.cullDirty = true; }
  setMaxDistance(distance: number) { this.options.maxDistance = Math.min(420, Math.max(30, distance)); this.cullDirty = true; }
  setWind(wind: number) { this.options.wind = Math.min(2, Math.max(0, wind)); }
  setMixPetalVariants(mix: boolean) { this.options.mixPetalVariants = mix; }
  setSeed(seed: number) { this.options.seed = Math.max(1, Math.floor(seed)); this.cullDirty = true; }
  setInteraction(interaction: FlowerInteraction) { this.interaction = interaction; }
  invalidateCulling() { this.visibleTiers = null; this.cullDirty = true; }

  getMetrics(): FlowerLabMetrics {
    const candidateCount = this.options.gridSize * this.options.gridSize;
    const visibleCount = this.visibleTiers?.reduce((sum, count) => sum + count, 0) ?? null;
    const frameMeanMs = mean(this.frameTimes);
    const storage = flowerStorageMetrics(candidateCount, visibleCount);
    return {
      ready: this.ready,
      mode: this.options.mode,
      cullingMode: this.options.cullingMode,
      candidateCount,
      visibleCount: this.options.mode === "direct" ? null : visibleCount,
      visibleTiers: this.options.mode === "direct" ? null : this.visibleTiers,
      visibleTileCount: this.options.mode === "direct" ? null : this.visibleTileCount,
      candidateTests: this.options.mode === "direct" ? candidateCount : this.options.cullingMode === "flat" ? candidateCount : this.visibleTileCount === null ? null : Math.min(candidateCount, this.visibleTileCount * CANDIDATES_PER_TILE),
      spacing: this.options.spacing,
      density: this.options.density,
      maxDistance: this.options.maxDistance,
      frameMeanMs,
      frameP95Ms: percentile(this.frameTimes, 0.95),
      frameP99Ms: percentile(this.frameTimes, 0.99),
      frameMaxMs: this.frameTimes.length ? Math.max(...this.frameTimes) : 0,
      submitMeanMs: mean(this.submitTimes),
      fps: frameMeanMs > 0 ? 1000 / frameMeanMs : 0,
      gpuRenderMeanMs: this.gpuRenderTimes.length ? mean(this.gpuRenderTimes) : null,
      gpuRenderP95Ms: this.gpuRenderTimes.length ? percentile(this.gpuRenderTimes, 0.95) : null,
      gpuCullMeanMs: this.gpuCullTimes.length ? mean(this.gpuCullTimes) : null,
      gpuCullP95Ms: this.gpuCullTimes.length ? percentile(this.gpuCullTimes, 0.95) : null,
      cullWallMs: this.cullWallMs,
      drawCalls: this.options.mode === "compact" ? 9 : 4,
      ...storage,
      adapter: this.adapterLabel,
      timestampQuery: Boolean(this.timestampQuery),
      error: this.error,
    };
  }

  dispose() {
    this.disposed = true;
    this.ready = false;
    this.depthTexture?.destroy();
    this.grassTexture?.destroy();
    this.petalTexture?.destroy();
    this.visibleBuffers.forEach((buffer) => buffer.destroy());
    this.visibleTiles?.destroy();
    this.uniformBuffer?.destroy();
    this.drawArgs?.destroy();
    this.dispatchArgs?.destroy();
    if (!this.countPending) this.countReadback?.destroy();
    this.timestampQuery?.destroy();
    this.timestampResolve?.destroy();
    if (!this.timestampPending) this.timestampReadback?.destroy();
    this.cullTimestampQuery?.destroy();
    this.cullTimestampResolve?.destroy();
    if (!this.cullTimestampPending) this.cullTimestampReadback?.destroy();
  }
}
