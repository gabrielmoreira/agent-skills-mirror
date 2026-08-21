import * as THREE from 'three/webgpu'
import { SLOPE } from './chain.js'
import { COPY_RATIO } from './noise.js'
import { createOceanMaterials } from './tsl.js'

const GRAVITY = 9.81
const ISLAND_COLS = 96
const MAIN_COLS = 160
const CAPILLARY_SIGMA_RHO = 7.4e-5
const GRID_N = 512
const CELL = 0.4
const LINEAR_CELLS = 160
const CELL_GROWTH = 1.12
const LAYER_RATIO = (0.68 ** 7 / COPY_RATIO ** 4) ** 0.25
const MAX_LAYERS = 8
const DIR_FRACS = [0, 0.9, -0.75, 0.45, -0.35, 0.7, -1, 0.2]
const UV_OFFSETS = [
  [0.11, 0.63], [0.42, 0.17], [0.78, 0.55], [0.05, 0.91],
  [0.33, 0.4], [0.66, 0.08], [0.9, 0.77], [0.24, 0.31],
]
const CAP_ANGLES = [0.4, -0.8, 1.7]
const CAP_ANISO_FRACS = [0, 0.45, -0.35]
const CAP_SCALES = [1, 0.72, 0.52]
const CAP_UV_OFFSETS = [
  [0.19, 0.47], [0.61, 0.83], [0.07, 0.29],
  [0.37, 0.71], [0.83, 0.13], [0.53, 0.59],
]
const FOAM_REGION = 80
const RIBBON_SPAN = 28
const RIBBON_CELLS = 140
const FOAM_RISE = 0.08

export class Ocean {
  constructor(uniforms, resources) {
    this.uniforms = uniforms
    this.gridN = GRID_N
    this.materials = createOceanMaterials(uniforms, resources)

    const grid = makeGeometry(buildVertices(GRID_N), GRID_N, GRID_N)
    const ribbon = makeGeometry(buildRibbonVertices(RIBBON_CELLS, GRID_N), RIBBON_CELLS, GRID_N)
    const island = makeGeometry(buildIslandVertices(RIBBON_CELLS, ISLAND_COLS), RIBBON_CELLS, ISLAND_COLS * 4)

    this.group = new THREE.Group()
    this.fillGroup = new THREE.Group()
    this.wireGroup = new THREE.Group()
    this.group.add(this.fillGroup, this.wireGroup)

    addMesh(this.fillGroup, grid.tri, this.materials.grid, 0)
    addMesh(this.fillGroup, ribbon.tri, this.materials.ribbon, 1)
    addMesh(this.fillGroup, island.tri, this.materials.island, 2)
    addMesh(this.fillGroup, grid.tri, this.materials.land, 3)

    addLines(this.wireGroup, grid.line, this.materials.gridWire, 0)
    addLines(this.wireGroup, ribbon.line, this.materials.ribbonWire, 1)
    addLines(this.wireGroup, island.line, this.materials.islandWire, 2)
    addLines(this.wireGroup, grid.line, this.materials.landWire, 3)
    this.wireGroup.visible = false

    this.time = 0
    this.phases = new Float64Array(MAX_LAYERS)
    this.capPhases = new Float64Array(CAP_ANGLES.length + CAP_ANISO_FRACS.length)
    this.layerCache = []
  }

  update(dt, params, noise, capNoise, eye, sunDir) {
    const u = this.uniforms
    this.time += dt
    u.cameraPos.value.set(eye[0], eye[1], eye[2])
    u.time.value = this.time
    u.sunDir.value.set(sunDir[0], sunDir[1], sunDir[2])

    const count = Math.round(params.layers)
    u.numLayers.value = count
    u.choppiness.value = params.choppiness
    u.dGrad.value = noise.size * noise.dispGradPerTexel
    u.hGrad.value = noise.size

    const spread = params.spread * Math.PI / 180
    const ratio = LAYER_RATIO
    let sq = 0
    for (let i = 0; i < count; i++) sq += ratio ** (2 * i)
    const ampNorm = params.amplitude / Math.sqrt(Math.max(sq, 1e-12))
    let meanX = 0
    let meanZ = 0

    for (let i = 0; i < MAX_LAYERS; i++) {
      if (i < count) {
        const lambda = params.wavelength * ratio ** i
        const tile = lambda * noise.wavesPerTile
        this.phases[i] += Math.sqrt(GRAVITY * lambda / (2 * Math.PI)) / tile * dt
        const angle = params.waveDir * Math.PI / 180 + DIR_FRACS[i] * spread
        const dx = Math.cos(angle)
        const dz = Math.sin(angle)
        const invL = 1 / tile
        const amp = ampNorm * ratio ** i
        const su = UV_OFFSETS[i][0] - this.phases[i]
        const sv = UV_OFFSETS[i][1]
        meanX += ratio ** (2 * i) * dx
        meanZ += ratio ** (2 * i) * dz
        u.layers[i].dirScaleAmp.value.set(dx, dz, invL, amp)
        u.layers[i].scroll.value.set(su, sv, 0, 0)
        this.layerCache[i] = { dx, dz, invL, amp, su, sv }
      } else {
        u.layers[i].dirScaleAmp.value.set(1, 0, 1, 0)
        u.layers[i].scroll.value.set(0, 0, 0, 0)
      }
    }
    this.layerCache.length = count

    const capNorm = params.ripple / Math.sqrt(CAP_SCALES.length) / (2 * Math.PI)
    const isoWeight = Math.sqrt(1 - params.rippleAniso)
    const anisoWeight = Math.sqrt(params.rippleAniso)
    for (let i = 0; i < this.capPhases.length; i++) {
      const aniso = i >= CAP_ANGLES.length
      const j = i % CAP_SCALES.length
      const lambda = params.rippleScale * CAP_SCALES[j]
      const sourceNoise = aniso ? noise : capNoise
      const tile = lambda * sourceNoise.wavesPerTile
      const k = 2 * Math.PI / lambda
      this.capPhases[i] += Math.sqrt(GRAVITY / k + CAPILLARY_SIGMA_RHO * k) / tile * dt
      const angle = aniso
        ? params.waveDir * Math.PI / 180 + CAP_ANISO_FRACS[j] * spread
        : CAP_ANGLES[j]
      const amp = capNorm * lambda * (aniso ? anisoWeight : isoWeight)
      u.capLayers[i].dirScaleAmp.value.set(Math.cos(angle), Math.sin(angle), 1 / tile, amp)
      u.capLayers[i].scroll.value.set(CAP_UV_OFFSETS[i][0] - this.capPhases[i], CAP_UV_OFFSETS[i][1], 0, 0)
    }

    u.capHGrad.value = capNoise.size
    u.rippleBias.value = params.rippleBias
    u.sssStrength.value = params.sss
    u.ampInv.value = 1 / Math.max(params.amplitude, 0.01)
    u.seaDepth.value = params.depth
    u.causticStrength.value = params.caustics
    u.causticScale.value = params.rippleScale / 0.6

    const meanLen = Math.hypot(meanX, meanZ) || 1
    u.leanX.value = params.lean * meanX / meanLen
    u.leanY.value = params.lean * meanZ / meanLen
    u.foamThreshold.value = params.foam
    u.foamRegion.value = FOAM_REGION
    u.foamDecay.value = Math.exp(-dt / params.foamLife)
    u.foamDecayG.value = Math.exp(-dt / (params.foamLife * 0.25))
    u.foamRise.value = Math.exp(-dt / FOAM_RISE)
    u.foamLife.value = params.foamLife
    u.slope.value = SLOPE

    // Keep the world-space accumulation window snapped to exact foam texels,
    // preserving exact carry-over behavior and avoiding resampling drift.
    const texel = 2 * FOAM_REGION / 512
    if (!this.foamC) {
      this.foamC = [
        Math.round(eye[0] / texel) * texel,
        Math.round(eye[2] / texel) * texel,
      ]
    }
    let fdx = 0
    let fdz = 0
    if (dt > 0) {
      const cx = Math.round(eye[0] / texel) * texel
      const cz = Math.round(eye[2] / texel) * texel
      fdx = (cx - this.foamC[0]) / (2 * FOAM_REGION)
      fdz = (cz - this.foamC[1]) / (2 * FOAM_REGION)
      this.foamC = [cx, cz]
    }
    u.foamCX.value = this.foamC[0]
    u.foamCZ.value = this.foamC[1]
    u.foamDX.value = fdx
    u.foamDZ.value = fdz

    if (this.chain) {
      u.islandArcStep.value = this.chain.islandArcStep
      u.simZBase.value = this.chain.zBase
      u.simZShift.value = this.chain.lastShift
      u.simTCam.value = this.chain.tCamSnap
    }
    u.foamDecaySwallow.value = Math.exp(-dt / 0.5)
    u.simDt.value = Math.min(dt, 0.033)
    u.waveK.value = 2 * Math.PI / params.wavelength
    u.foamScale.value = params.foamScale

    this.fillGroup.visible = !params.wireframe
    this.wireGroup.visible = !!params.wireframe
  }
}

function addMesh(group, geometry, material, renderOrder) {
  const mesh = new THREE.Mesh(geometry, material)
  mesh.frustumCulled = false
  mesh.renderOrder = renderOrder
  group.add(mesh)
  return mesh
}

function addLines(group, geometry, material, renderOrder) {
  const lines = new THREE.LineSegments(geometry, material)
  lines.frustumCulled = false
  lines.renderOrder = renderOrder
  group.add(lines)
  return lines
}

function makeGeometry(vertices, nx, nz) {
  const [triIndex, lineIndex] = buildIndices(nx, nz)
  const position = new THREE.BufferAttribute(vertices, 3)

  const tri = new THREE.BufferGeometry()
  tri.setAttribute('position', position)
  tri.setIndex(new THREE.BufferAttribute(triIndex, 1))

  const line = new THREE.BufferGeometry()
  line.setAttribute('position', position)
  line.setIndex(new THREE.BufferAttribute(lineIndex, 1))

  return { tri, line }
}

function warpAxis(i) {
  const a = Math.abs(i)
  const sign = Math.sign(i)
  if (a <= LINEAR_CELLS) return sign * a * CELL
  return sign * (LINEAR_CELLS * CELL + CELL * (CELL_GROWTH ** (a - LINEAR_CELLS) - 1) / (CELL_GROWTH - 1))
}

// Uniform lattice in pre-warp space; the TSL vertex node warps it around the
// camera, so the buffer itself remains static.
function buildVertices(n) {
  const half = n / 2
  const data = new Float32Array((n + 1) * (n + 1) * 3)
  let p = 0
  for (let iz = 0; iz <= n; iz++) {
    for (let ix = 0; ix <= n; ix++) {
      data[p++] = (ix - half) * CELL
      data[p++] = (iz - half) * CELL
      data[p++] = 0
    }
  }
  return data
}

function buildRibbonVertices(nx, nz) {
  const half = nz / 2
  const cellAt = i => {
    const a = Math.min(Math.abs(i - half), half - 1)
    return warpAxis(a + 1) - warpAxis(a)
  }
  const dxMaterial = RIBBON_SPAN / nx
  const data = new Float32Array((nx + 1) * (nz + 1) * 3)
  let p = 0
  for (let iz = 0; iz <= nz; iz++) {
    for (let ix = 0; ix <= nx; ix++) {
      data[p++] = ix / nx
      data[p++] = warpAxis(iz - half)
      data[p++] = Math.max(dxMaterial, cellAt(iz))
    }
  }
  return data
}

function buildIslandVertices(nx, cols) {
  const SUB = 4
  const rows = cols * SUB
  const data = new Float32Array((nx + 1) * (rows + 1) * 3)
  let p = 0
  for (let r = 0; r <= rows; r++) {
    for (let ix = 0; ix <= nx; ix++) {
      data[p++] = ix / nx
      data[p++] = MAIN_COLS + r / SUB
      data[p++] = 1.4 / SUB
    }
  }
  return data
}

function buildIndices(nx, nz) {
  const tri = new Uint32Array(nx * nz * 6)
  let t = 0
  for (let z = 0; z < nz; z++) {
    for (let x = 0; x < nx; x++) {
      const a = z * (nx + 1) + x
      const b = a + 1
      const c = a + nx + 1
      const d = c + 1
      tri[t++] = a; tri[t++] = c; tri[t++] = b
      tri[t++] = b; tri[t++] = c; tri[t++] = d
    }
  }

  const line = new Uint32Array(2 * (nx * (nz + 1) + nz * (nx + 1)))
  let l = 0
  for (let z = 0; z <= nz; z++) {
    for (let x = 0; x < nx; x++) {
      const a = z * (nx + 1) + x
      line[l++] = a; line[l++] = a + 1
    }
  }
  for (let x = 0; x <= nx; x++) {
    for (let z = 0; z < nz; z++) {
      const a = z * (nx + 1) + x
      line[l++] = a; line[l++] = a + nx + 1
    }
  }
  return [tri, line]
}
