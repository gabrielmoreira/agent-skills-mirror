type Point2 = { x: number; y: number }
type Vec3 = [number, number, number]

type MeshGeometry = {
  vertex: GPUBuffer
  index: GPUBuffer
  indexCount: number
}

type ParsedMesh = {
  positions: Float32Array
  texcoords: Float32Array
  indices: Uint32Array
  wind?: Float32Array
}

type ParsedTree = {
  meshes: ParsedMesh[]
  image: Blob
  projectedCenter: Point2
  projectedHalfSize: Point2
}

type ShadowPlacement = {
  centerX: number
  centerZ: number
  halfWidth: number
  halfHeight: number
}

const LIGHT_X = Math.cos(-0.8)
const LIGHT_Y = 0.65
const LIGHT_Z = Math.sin(-0.8)
const SHADOW_RESOLUTION = 512
const SHADOW_OPACITY = 0.82

type Gltf = {
  scene: number
  scenes: Array<{ nodes: number[] }>
  nodes: Array<{ children?: number[]; mesh?: number; matrix?: number[]; translation?: number[]; scale?: number[]; name?: string }>
  meshes: Array<{ primitives: Array<{ attributes: { POSITION: number; TEXCOORD_0: number }; indices: number }> }>
  accessors: Array<{ bufferView: number; byteOffset?: number; componentType: number; count: number; type: string }>
  bufferViews: Array<{ byteOffset?: number; byteLength: number; byteStride?: number }>
  images: Array<{ bufferView: number; mimeType: string }>
}

const shadowShader = `
struct ShadowView {
  projected: vec4f,
  motion: vec4f,
}
@group(0) @binding(0) var<uniform> view: ShadowView;
@group(0) @binding(1) var colorSampler: sampler;
@group(0) @binding(2) var colorTexture: texture_2d<f32>;
struct VertexInput {
  @location(0) position: vec3f,
  @location(1) uv: vec2f,
  @location(2) frondAnchorProgress: vec4f,
  @location(3) frondDirectionLeaf: vec4f,
}
struct VertexOutput {
  @builtin(position) clip: vec4f,
  @location(0) uv: vec2f,
}
fn smoothCurve(value: f32) -> f32 {
  let t = clamp(value, 0.0, 1.0);
  return t * t * (3.0 - 2.0 * t);
}
@vertex fn vertex(input: VertexInput) -> VertexOutput {
  let height = clamp(input.position.y, 0.0, 1.0);
  let phase = view.motion.x;

  // Keep the trunk base planted and bend its centerline progressively. The
  // crown follows this same low-frequency motion instead of translating as a
  // rigid object.
  let bend = height * height * (0.35 + 0.65 * height * height);
  let wind = vec2f(
    sin(phase * 0.46) + sin(phase * 0.19 + 1.7) * 0.34,
    cos(phase * 0.39 + 0.55) + sin(phase * 0.16 + 2.4) * 0.28
  );
  let trunkSway = wind * vec2f(0.019, 0.014) * bend;
  let trunkTwist = (sin(phase * 0.31 + height * 1.9) * 0.010 + sin(phase * 0.13 + 0.8) * 0.006) * bend;
  let twistCos = cos(trunkTwist);
  let twistSin = sin(trunkTwist);
  let trunkXZ = vec2f(
    input.position.x * twistCos - input.position.z * twistSin,
    input.position.x * twistSin + input.position.z * twistCos
  ) + trunkSway;
  var position = vec3f(trunkXZ.x, input.position.y, trunkXZ.y);

  // Each authored palm frond is a disconnected mesh island. CPU-side metadata
  // supplies its attachment point, direction, and normalized distance from the
  // attachment. This lets the shadow-only tree flex individual fronds while
  // keeping every vertex in one frond coherent.
  let leaf = input.frondDirectionLeaf.w;
  let progress = smoothCurve(input.frondAnchorProgress.w);
  let anchor = input.frondAnchorProgress.xyz;
  let frondDirection = input.frondDirectionLeaf.xyz;
  let horizontalLength = max(length(frondDirection.xz), 1e-4);
  let horizontalDirection = frondDirection.xz / horizontalLength;
  let sideways = vec2f(-horizontalDirection.y, horizontalDirection.x);
  let windLength = max(length(wind), 1e-4);
  let windDirection = wind / windLength;
  let windStrength = clamp(windLength, 0.35, 1.25);
  let windAlignment = dot(horizontalDirection, windDirection);
  let frondSeed = dot(frondDirection, vec3f(4.73, 7.19, 3.11));

  // Fronds lag the trunk slightly and flex most strongly toward their tips.
  // The shared gust term keeps the whole crown in sync; direction-derived
  // phase offsets stop all leaves from moving as a single rigid plate.
  let gust = sin(phase * 0.58 + frondSeed) * 0.70 + sin(phase * 0.27 + frondSeed * 0.61 + 1.2) * 0.30;
  let tipLag = sin(phase * 0.82 + frondSeed * 1.37 + progress * 2.2);
  let drag = windDirection * (0.0065 + 0.0045 * abs(windAlignment)) * windStrength * (0.72 + 0.28 * gust);
  let lateral = sideways * tipLag * 0.0045;
  let ripple = sideways * sin(phase * 1.12 + frondSeed * 1.91 + progress * 4.6) * 0.0018;
  let frondOffset = (drag + lateral + ripple) * progress * leaf;
  position = vec3f(position.x + frondOffset.x, position.y, position.z + frondOffset.y);

  // Small elevation changes are important in a projected shadow: they make a
  // frond visibly bow rather than merely slide sideways across the sand.
  let lift = (gust * 0.0060 * windStrength - windAlignment * 0.0035 * windStrength + tipLag * 0.0022) * progress * leaf;
  position = vec3f(position.x, position.y + lift, position.z);

  // Keep the root of every frond attached to the trunk's bent crown.
  let anchorHeight = clamp(anchor.y, 0.0, 1.0);
  let anchorBend = anchorHeight * anchorHeight * (0.35 + 0.65 * anchorHeight * anchorHeight);
  let anchorSway = wind * vec2f(0.019, 0.014) * anchorBend;
  let vertexSway = wind * vec2f(0.019, 0.014) * bend;
  let rootCorrection = (anchorSway - vertexSway) * (1.0 - progress) * leaf;
  position = vec3f(position.x + rootCorrection.x, position.y, position.z + rootCorrection.y);

  let projected = position.xz - vec2f(${LIGHT_X.toFixed(9)}, ${LIGHT_Z.toFixed(9)}) * (position.y / ${LIGHT_Y.toFixed(9)});
  let normalized = (projected - view.projected.xy) / view.projected.zw;
  var output: VertexOutput;
  output.clip = vec4f(normalized.x, -normalized.y, 0.0, 1.0);
  output.uv = input.uv;
  return output;
}
@fragment fn fragment(input: VertexOutput) -> @location(0) vec4f {
  let texel = textureSample(colorTexture, colorSampler, input.uv);
  let alpha = smoothstep(0.10, 0.55, texel.a);
  if (alpha <= 0.002) { discard; }
  return vec4f(alpha, alpha, alpha, alpha);
}
`

const stabilizeShader = `
struct StabilizeView { settings: vec4f }
@group(0) @binding(0) var maskSampler: sampler;
@group(0) @binding(1) var rawMask: texture_2d<f32>;
@group(0) @binding(2) var historyMask: texture_2d<f32>;
@group(0) @binding(3) var<uniform> stabilize: StabilizeView;
struct VertexOutput { @builtin(position) clip: vec4f, @location(0) uv: vec2f }
@vertex fn vertex(@builtin(vertex_index) index: u32) -> VertexOutput {
  let positions = array<vec2f, 3>(vec2f(-1.0, -1.0), vec2f(3.0, -1.0), vec2f(-1.0, 3.0));
  let clip = positions[index];
  var output: VertexOutput;
  output.clip = vec4f(clip, 0.0, 1.0);
  output.uv = clip * vec2f(0.5, -0.5) + vec2f(0.5);
  return output;
}
fn filteredRaw(uv: vec2f) -> f32 {
  let texel = stabilize.settings.xy;
  let center = textureSampleLevel(rawMask, maskSampler, uv, 0.0).x * 0.36;
  let cardinals = (
    textureSampleLevel(rawMask, maskSampler, uv + vec2f(texel.x, 0.0), 0.0).x +
    textureSampleLevel(rawMask, maskSampler, uv - vec2f(texel.x, 0.0), 0.0).x +
    textureSampleLevel(rawMask, maskSampler, uv + vec2f(0.0, texel.y), 0.0).x +
    textureSampleLevel(rawMask, maskSampler, uv - vec2f(0.0, texel.y), 0.0).x
  ) * 0.12;
  let diagonals = (
    textureSampleLevel(rawMask, maskSampler, uv + texel, 0.0).x +
    textureSampleLevel(rawMask, maskSampler, uv + vec2f(texel.x, -texel.y), 0.0).x +
    textureSampleLevel(rawMask, maskSampler, uv - vec2f(texel.x, -texel.y), 0.0).x +
    textureSampleLevel(rawMask, maskSampler, uv - texel, 0.0).x
  ) * 0.04;
  return center + cardinals + diagonals;
}
@fragment fn fragment(input: VertexOutput) -> @location(0) vec4f {
  let raw = filteredRaw(input.uv);
  let history = textureSampleLevel(historyMask, maskSampler, input.uv, 0.0).x;
  let historyEnabled = stabilize.settings.z;
  let difference = abs(raw - history);
  let alpha = mix(1.0, mix(0.16, 0.46, smoothstep(0.025, 0.22, difference)), historyEnabled);
  let stable = mix(history, raw, alpha);
  return vec4f(stable, stable, stable, stable);
}
`

function identity4() {
  return new Float32Array([1, 0, 0, 0,
    0, 1, 0, 0,
    0, 0, 1, 0,
    0, 0, 0, 1])
}

function multiply4(left: Float32Array, right: Float32Array) {
  const result = new Float32Array(16)
  for (let column = 0; column < 4; column++) {
    for (let row = 0; row < 4; row++) {
      let sum = 0
      for (let k = 0; k < 4; k++) sum += left[k * 4 + row]! * right[column * 4 + k]!
      result[column * 4 + row] = sum
    }
  }
  return result
}

function matrixForNode(node: Gltf['nodes'][number]) {
  if (node.matrix?.length === 16) return new Float32Array(node.matrix)
  const matrix = identity4()
  if (node.scale?.length === 3) {
    matrix[0] = node.scale[0]!
    matrix[5] = node.scale[1]!
    matrix[10] = node.scale[2]!
  }
  if (node.translation?.length === 3) {
    matrix[12] = node.translation[0]!
    matrix[13] = node.translation[1]!
    matrix[14] = node.translation[2]!
  }
  return matrix
}

function transformPoint(matrix: Float32Array, x: number, y: number, z: number): Vec3 {
  return [
    matrix[0]! * x + matrix[4]! * y + matrix[8]! * z + matrix[12]!,
    matrix[1]! * x + matrix[5]! * y + matrix[9]! * z + matrix[13]!,
    matrix[2]! * x + matrix[6]! * y + matrix[10]! * z + matrix[14]!,
  ]
}

function componentCount(type: string) {
  if (type === 'SCALAR') return 1
  if (type === 'VEC2') return 2
  if (type === 'VEC3') return 3
  if (type === 'VEC4') return 4
  throw new Error(`Unsupported glTF accessor type: ${type}`)
}

function componentBytes(componentType: number) {
  if (componentType === 5126 || componentType === 5125) return 4
  if (componentType === 5123) return 2
  throw new Error(`Unsupported glTF component type: ${componentType}`)
}

function accessorFloats(gltf: Gltf, binary: ArrayBuffer, accessorIndex: number) {
  const accessor = gltf.accessors[accessorIndex]!
  const bufferView = gltf.bufferViews[accessor.bufferView]!
  const components = componentCount(accessor.type)
  const bytes = componentBytes(accessor.componentType)
  const stride = bufferView.byteStride ?? components * bytes
  const start = (bufferView.byteOffset ?? 0) + (accessor.byteOffset ?? 0)
  const data = new DataView(binary)
  const result = new Float32Array(accessor.count * components)
  for (let item = 0; item < accessor.count; item++) {
    for (let component = 0; component < components; component++) {
      const offset = start + item * stride + component * bytes
      const value = accessor.componentType === 5126 ? data.getFloat32(offset, true)
        : accessor.componentType === 5125 ? data.getUint32(offset, true)
          : data.getUint16(offset, true)
      result[item * components + component] = value
    }
  }
  return result
}

function accessorIndices(gltf: Gltf, binary: ArrayBuffer, accessorIndex: number) {
  const values = accessorFloats(gltf, binary, accessorIndex)
  const result = new Uint32Array(values.length)
  for (let index = 0; index < values.length; index++) result[index] = values[index]!
  return result
}

function buildWindData(positions: Float32Array, indices: Uint32Array) {
  const vertexCount = positions.length / 3
  const parent = new Uint32Array(vertexCount)
  for (let vertex = 0; vertex < vertexCount; vertex++) parent[vertex] = vertex

  const find = (vertex: number) => {
    let root = vertex
    while (parent[root] !== root) root = parent[root]!
    while (parent[vertex] !== vertex) {
      const next = parent[vertex]!
      parent[vertex] = root
      vertex = next
    }
    return root
  }
  const union = (a: number, b: number) => {
    const rootA = find(a)
    const rootB = find(b)
    if (rootA !== rootB) parent[rootB] = rootA
  }

  for (let index = 0; index < indices.length; index += 3) {
    const a = indices[index]!
    const b = indices[index + 1]!
    const c = indices[index + 2]!
    union(a, b); union(b, c); union(c, a)
  }

  const components = new Map<number, number[]>()
  for (let vertex = 0; vertex < vertexCount; vertex++) {
    const root = find(vertex)
    const component = components.get(root)
    if (component) component.push(vertex)
    else components.set(root, [vertex])
  }

  // Two vec4 attributes per vertex: attachment.xyz + progress, then the
  // attachment-to-tip direction.xyz + leaf flag. The palm asset has one
  // connected trunk island and many disconnected frond islands, so this
  // topology gives us stable per-frond motion without bones or skinning.
  const data = new Float32Array(vertexCount * 8)
  for (const vertices of components.values()) {
    let rootVertex = vertices[0]!
    let rootRadius = Infinity
    for (const vertex of vertices) {
      const x = positions[vertex * 3]!
      const z = positions[vertex * 3 + 2]!
      const radius = x * x + z * z
      if (radius < rootRadius) { rootRadius = radius; rootVertex = vertex }
    }

    const rootX = positions[rootVertex * 3]!
    const rootY = positions[rootVertex * 3 + 1]!
    const rootZ = positions[rootVertex * 3 + 2]!
    let tipVertex = rootVertex
    let lengthSquared = 0
    for (const vertex of vertices) {
      const dx = positions[vertex * 3]! - rootX
      const dy = positions[vertex * 3 + 1]! - rootY
      const dz = positions[vertex * 3 + 2]! - rootZ
      const distanceSquared = dx * dx + dy * dy + dz * dz
      if (distanceSquared > lengthSquared) { lengthSquared = distanceSquared; tipVertex = vertex }
    }

    const tipX = positions[tipVertex * 3]!
    const tipY = positions[tipVertex * 3 + 1]!
    const tipZ = positions[tipVertex * 3 + 2]!
    const length = Math.sqrt(lengthSquared)
    const isFrond = rootY > 0.60 && length > 0.14
    if (!isFrond) continue

    const invLength = length > 1e-6 ? 1 / length : 0
    const directionX = (tipX - rootX) * invLength
    const directionY = (tipY - rootY) * invLength
    const directionZ = (tipZ - rootZ) * invLength
    for (const vertex of vertices) {
      const dx = positions[vertex * 3]! - rootX
      const dy = positions[vertex * 3 + 1]! - rootY
      const dz = positions[vertex * 3 + 2]! - rootZ
      const progress = Math.min(1, Math.hypot(dx, dy, dz) * invLength)
      const offset = vertex * 8
      data[offset] = rootX
      data[offset + 1] = rootY
      data[offset + 2] = rootZ
      data[offset + 3] = progress
      data[offset + 4] = directionX
      data[offset + 5] = directionY
      data[offset + 6] = directionZ
      data[offset + 7] = 1
    }
  }
  return data
}

function parseGlb(buffer: ArrayBuffer) {
  const data = new DataView(buffer)
  if (data.getUint32(0, true) !== 0x46546c67 || data.getUint32(4, true) !== 2) throw new Error('Coconut tree is not a valid glTF 2.0 binary.')
  let offset = 12
  let gltf: Gltf | undefined
  let binary: ArrayBuffer | undefined
  while (offset < buffer.byteLength) {
    const length = data.getUint32(offset, true)
    const type = data.getUint32(offset + 4, true)
    offset += 8
    const chunk = buffer.slice(offset, offset + length)
    offset += length
    if (type === 0x4e4f534a) gltf = JSON.parse(new TextDecoder().decode(chunk)) as Gltf
    if (type === 0x004e4942) binary = chunk
  }
  if (!gltf || !binary) throw new Error('Coconut tree glTF is missing JSON or binary data.')
  return { gltf, binary }
}

async function loadTree(url: string): Promise<ParsedTree> {
  const response = await fetch(url)
  if (!response.ok) throw new Error(`Unable to load coconut tree (${response.status}).`)
  const { gltf, binary } = parseGlb(await response.arrayBuffer())

  const worldMatrices = gltf.nodes.map(() => identity4())
  const visit = (nodeIndex: number, parent: Float32Array) => {
    const world = multiply4(parent, matrixForNode(gltf.nodes[nodeIndex]!))
    worldMatrices[nodeIndex] = world
    for (const child of gltf.nodes[nodeIndex]!.children ?? []) visit(child, world)
  }
  for (const root of gltf.scenes[gltf.scene]!.nodes) visit(root, identity4())

  const rawMeshes: ParsedMesh[] = []
  let minX = Infinity; let minY = Infinity; let minZ = Infinity
  let maxX = -Infinity; let maxY = -Infinity; let maxZ = -Infinity
  for (const [nodeIndex, node] of gltf.nodes.entries()) {
    if (node.mesh === undefined) continue
    const primitive = gltf.meshes[node.mesh]!.primitives[0]!
    const sourcePositions = accessorFloats(gltf, binary, primitive.attributes.POSITION)
    const texcoords = accessorFloats(gltf, binary, primitive.attributes.TEXCOORD_0)
    const positions = new Float32Array(sourcePositions.length)
    for (let index = 0; index < sourcePositions.length; index += 3) {
      const point = transformPoint(worldMatrices[nodeIndex]!, sourcePositions[index]!, sourcePositions[index + 1]!, sourcePositions[index + 2]!)
      positions[index] = point[0]
      positions[index + 1] = point[1]
      positions[index + 2] = point[2]
      minX = Math.min(minX, point[0]); minY = Math.min(minY, point[1]); minZ = Math.min(minZ, point[2])
      maxX = Math.max(maxX, point[0]); maxY = Math.max(maxY, point[1]); maxZ = Math.max(maxZ, point[2])
    }
    rawMeshes.push({ positions, texcoords, indices: accessorIndices(gltf, binary, primitive.indices) })
  }

  const height = Math.max(maxY - minY, 1e-6)
  const centerX = (minX + maxX) * 0.5
  const centerZ = (minZ + maxZ) * 0.5
  const meshes = rawMeshes.map((mesh) => {
    const positions = new Float32Array(mesh.positions.length)
    for (let index = 0; index < mesh.positions.length; index += 3) {
      positions[index] = (mesh.positions[index]! - centerX) / height
      positions[index + 1] = (mesh.positions[index + 1]! - minY) / height
      positions[index + 2] = (mesh.positions[index + 2]! - centerZ) / height
    }
    return { ...mesh, positions, wind: buildWindData(positions, mesh.indices) }
  })

  let minProjectedX = Infinity; let minProjectedZ = Infinity
  let maxProjectedX = -Infinity; let maxProjectedZ = -Infinity
  for (const mesh of meshes) {
    for (let index = 0; index < mesh.positions.length; index += 3) {
      const x = mesh.positions[index]!
      const y = mesh.positions[index + 1]!
      const z = mesh.positions[index + 2]!
      const projectedX = x - LIGHT_X * y / LIGHT_Y
      const projectedZ = z - LIGHT_Z * y / LIGHT_Y
      minProjectedX = Math.min(minProjectedX, projectedX)
      maxProjectedX = Math.max(maxProjectedX, projectedX)
      minProjectedZ = Math.min(minProjectedZ, projectedZ)
      maxProjectedZ = Math.max(maxProjectedZ, projectedZ)
    }
  }
  const projectedCenter = { x: (minProjectedX + maxProjectedX) * 0.5, y: (minProjectedZ + maxProjectedZ) * 0.5 }
  const projectedHalfSize = { x: (maxProjectedX - minProjectedX) * 0.58, y: (maxProjectedZ - minProjectedZ) * 0.58 }

  const imageInfo = gltf.images[0]!
  const imageView = gltf.bufferViews[imageInfo.bufferView]!
  const imageStart = imageView.byteOffset ?? 0
  const image = new Blob([binary.slice(imageStart, imageStart + imageView.byteLength)], { type: imageInfo.mimeType })
  return { meshes, image, projectedCenter, projectedHalfSize }
}

function createVertexData(mesh: ParsedMesh) {
  const vertexCount = mesh.positions.length / 3
  const data = new Float32Array(vertexCount * 13)
  const wind = mesh.wind ?? new Float32Array(vertexCount * 8)
  for (let vertex = 0; vertex < vertexCount; vertex++) {
    const offset = vertex * 13
    data[offset] = mesh.positions[vertex * 3]!
    data[offset + 1] = mesh.positions[vertex * 3 + 1]!
    data[offset + 2] = mesh.positions[vertex * 3 + 2]!
    data[offset + 3] = mesh.texcoords[vertex * 2]!
    data[offset + 4] = mesh.texcoords[vertex * 2 + 1]!
    for (let component = 0; component < 8; component++) data[offset + 5 + component] = wind[vertex * 8 + component]!
  }
  return data
}

function placement(screenToBed: (x: number, y: number) => Point2, width: number, height: number, mobile: boolean, aspect: number): ShadowPlacement {
  const centerScreen = mobile ? { x: 0.98, y: 0.04 } : { x: 0.93, y: -0.04 }
  const halfScreenWidth = mobile ? 0.88 : 0.36
  const center = screenToBed(width * centerScreen.x, height * centerScreen.y)
  const left = screenToBed(width * (centerScreen.x - halfScreenWidth), height * centerScreen.y)
  const right = screenToBed(width * (centerScreen.x + halfScreenWidth), height * centerScreen.y)
  const halfWidth = Math.abs(right.x - left.x) * 0.5
  const halfHeight = halfWidth / Math.max(aspect, 0.25)
  return { centerX: center.x, centerZ: center.y, halfWidth, halfHeight }
}

export class CoconutShadow {
  readonly sampler: GPUSampler
  readonly texture: GPUTexture
  private readonly device: GPUDevice
  private readonly shadowUniform: GPUBuffer
  private readonly stabilizeUniform: GPUBuffer
  private readonly shadowData = new Float32Array(8)
  private readonly stabilizeData = new Float32Array(4)
  private shadowPipeline!: GPURenderPipeline
  private stabilizePipeline!: GPURenderPipeline
  private shadowGroup!: GPUBindGroup
  private stabilizeGroup!: GPUBindGroup
  private geometries: MeshGeometry[] = []
  private colorTexture?: GPUTexture
  private rawTexture: GPUTexture
  private historyTexture: GPUTexture
  private projectedCenter: Point2 = { x: 0, y: 0 }
  private projectedHalfSize: Point2 = { x: 1, y: 1 }
  private placement: ShadowPlacement = { centerX: 0.18, centerZ: -0.10, halfWidth: 0.11, halfHeight: 0.11 }
  private hasHistory = false
  private mobile = false
  private readonly treeUrl?: string

  constructor(device: GPUDevice, mobile = false, treeUrl?: string) {
    this.device = device
    this.mobile = mobile
    this.treeUrl = treeUrl
    this.shadowUniform = device.createBuffer({ label: 'Coconut shadow view', size: this.shadowData.byteLength, usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST })
    this.stabilizeUniform = device.createBuffer({ label: 'Coconut shadow stabilization', size: this.stabilizeData.byteLength, usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST })
    this.texture = device.createTexture({ label: 'Coconut tree shadow', size: [SHADOW_RESOLUTION, SHADOW_RESOLUTION], format: 'rgba8unorm', usage: GPUTextureUsage.RENDER_ATTACHMENT | GPUTextureUsage.TEXTURE_BINDING | GPUTextureUsage.COPY_SRC })
    this.rawTexture = device.createTexture({ label: 'Coconut tree shadow raw', size: [SHADOW_RESOLUTION, SHADOW_RESOLUTION], format: 'rgba8unorm', usage: GPUTextureUsage.RENDER_ATTACHMENT | GPUTextureUsage.TEXTURE_BINDING })
    this.historyTexture = device.createTexture({ label: 'Coconut tree shadow history', size: [SHADOW_RESOLUTION, SHADOW_RESOLUTION], format: 'rgba8unorm', usage: GPUTextureUsage.TEXTURE_BINDING | GPUTextureUsage.COPY_DST })
    this.sampler = device.createSampler({ label: 'Coconut tree shadow sampler', magFilter: 'linear', minFilter: 'linear', addressModeU: 'clamp-to-edge', addressModeV: 'clamp-to-edge' })
  }

  async initialize() {
    if (!this.treeUrl || typeof window === 'undefined' || typeof createImageBitmap !== 'function') return
    const tree = await loadTree(this.treeUrl)
    this.projectedCenter = tree.projectedCenter
    this.projectedHalfSize = tree.projectedHalfSize
    for (const mesh of tree.meshes) {
      const vertices = createVertexData(mesh)
      const vertex = this.device.createBuffer({ label: 'Coconut shadow vertices', size: vertices.byteLength, usage: GPUBufferUsage.VERTEX | GPUBufferUsage.COPY_DST })
      const index = this.device.createBuffer({ label: 'Coconut shadow indices', size: mesh.indices.byteLength, usage: GPUBufferUsage.INDEX | GPUBufferUsage.COPY_DST })
      this.device.queue.writeBuffer(vertex, 0, vertices)
      this.device.queue.writeBuffer(index, 0, mesh.indices)
      this.geometries.push({ vertex, index, indexCount: mesh.indices.length })
    }

    const bitmap = await createImageBitmap(tree.image)
    this.colorTexture = this.device.createTexture({ label: 'Coconut alpha texture', size: [bitmap.width, bitmap.height], format: 'rgba8unorm', usage: GPUTextureUsage.TEXTURE_BINDING | GPUTextureUsage.COPY_DST | GPUTextureUsage.RENDER_ATTACHMENT })
    this.device.queue.copyExternalImageToTexture({ source: bitmap }, { texture: this.colorTexture }, [bitmap.width, bitmap.height])
    bitmap.close()
    const colorSampler = this.device.createSampler({ label: 'Coconut alpha sampler', magFilter: 'linear', minFilter: 'linear', addressModeU: 'repeat', addressModeV: 'repeat' })
    const shadowModule = this.device.createShaderModule({ label: 'Coconut shadow WGSL', code: shadowShader })
    this.shadowPipeline = await this.device.createRenderPipelineAsync({ label: 'Coconut shadow mask', layout: 'auto',
      vertex: { module: shadowModule, entryPoint: 'vertex', buffers: [{ arrayStride: 52, attributes: [
        { shaderLocation: 0, offset: 0, format: 'float32x3' },
        { shaderLocation: 1, offset: 12, format: 'float32x2' },
        { shaderLocation: 2, offset: 20, format: 'float32x4' },
        { shaderLocation: 3, offset: 36, format: 'float32x4' },
      ] }] },
      fragment: { module: shadowModule, entryPoint: 'fragment', targets: [{ format: 'rgba8unorm', blend: {
        color: { operation: 'max', srcFactor: 'one', dstFactor: 'one' }, alpha: { operation: 'max', srcFactor: 'one', dstFactor: 'one' },
      } }] },
      primitive: { topology: 'triangle-list', cullMode: 'none' },
    })
    this.shadowGroup = this.device.createBindGroup({ layout: this.shadowPipeline.getBindGroupLayout(0), entries: [
      { binding: 0, resource: { buffer: this.shadowUniform } },
      { binding: 1, resource: colorSampler },
      { binding: 2, resource: this.colorTexture.createView() },
    ] })

    const stabilizeModule = this.device.createShaderModule({ label: 'Coconut shadow stabilize WGSL', code: stabilizeShader })
    this.stabilizePipeline = await this.device.createRenderPipelineAsync({ label: 'Coconut shadow stabilize', layout: 'auto',
      vertex: { module: stabilizeModule, entryPoint: 'vertex' },
      fragment: { module: stabilizeModule, entryPoint: 'fragment', targets: [{ format: 'rgba8unorm' }] },
      primitive: { topology: 'triangle-list' },
    })
    this.stabilizeGroup = this.device.createBindGroup({ layout: this.stabilizePipeline.getBindGroupLayout(0), entries: [
      { binding: 0, resource: this.sampler },
      { binding: 1, resource: this.rawTexture.createView() },
      { binding: 2, resource: this.historyTexture.createView() },
      { binding: 3, resource: { buffer: this.stabilizeUniform } },
    ] })
  }

  resize(width: number, height: number, screenToBed: (x: number, y: number) => Point2) {
    const aspect = this.projectedHalfSize.x / Math.max(this.projectedHalfSize.y, 1e-4)
    this.placement = placement(screenToBed, width, height, this.mobile, aspect)
  }

  encode(encoder: GPUCommandEncoder, now: number) {
    if (!this.shadowPipeline || !this.stabilizePipeline) return
    this.shadowData.set([this.projectedCenter.x, this.projectedCenter.y, this.projectedHalfSize.x, this.projectedHalfSize.y, now * 0.001, 0, 0, 0])
    this.stabilizeData.set([1 / SHADOW_RESOLUTION, 1 / SHADOW_RESOLUTION, this.hasHistory ? 1 : 0, 0])
    this.device.queue.writeBuffer(this.shadowUniform, 0, this.shadowData)
    this.device.queue.writeBuffer(this.stabilizeUniform, 0, this.stabilizeData)

    const shadowPass = encoder.beginRenderPass({ label: 'Coconut tree shadow raw', colorAttachments: [{ view: this.rawTexture.createView(), clearValue: { r: 0, g: 0, b: 0, a: 0 }, loadOp: 'clear', storeOp: 'store' }] })
    shadowPass.setPipeline(this.shadowPipeline)
    shadowPass.setBindGroup(0, this.shadowGroup)
    for (const geometry of this.geometries) {
      shadowPass.setVertexBuffer(0, geometry.vertex)
      shadowPass.setIndexBuffer(geometry.index, 'uint32')
      shadowPass.drawIndexed(geometry.indexCount)
    }
    shadowPass.end()

    const stabilizePass = encoder.beginRenderPass({ label: 'Coconut tree shadow stabilize', colorAttachments: [{ view: this.texture.createView(), clearValue: { r: 0, g: 0, b: 0, a: 0 }, loadOp: 'clear', storeOp: 'store' }] })
    stabilizePass.setPipeline(this.stabilizePipeline)
    stabilizePass.setBindGroup(0, this.stabilizeGroup)
    stabilizePass.draw(3)
    stabilizePass.end()

    encoder.copyTextureToTexture({ texture: this.texture }, { texture: this.historyTexture }, { width: SHADOW_RESOLUTION, height: SHADOW_RESOLUTION })
    this.hasHistory = true
  }

  get centerX() { return this.placement.centerX }
  get centerZ() { return this.placement.centerZ }
  get halfWidth() { return this.placement.halfWidth }
  get halfHeight() { return this.placement.halfHeight }
  get opacity() { return SHADOW_OPACITY }

  dispose() {
    for (const geometry of this.geometries) { geometry.vertex.destroy(); geometry.index.destroy() }
    this.colorTexture?.destroy()
    this.rawTexture.destroy()
    this.historyTexture.destroy()
    this.texture.destroy()
    this.shadowUniform.destroy()
    this.stabilizeUniform.destroy()
  }
}
