import * as THREE from 'three/webgpu'
import {
  Fn, If, Discard,
  attribute, varyingProperty, uniform, uv,
  float, int, vec2, vec3, vec4, ivec2,
  texture, textureLoad, textureSize,
  abs, clamp, cross, distance, dot, exp, floor, fract, fwidth, length, log,
  max, min, mix, normalize, pow, reflect, refract, select, smoothstep, sqrt,
} from 'three/tsl'

export const SIM_NODES = 64
export const SIM_COLS = 256
export const MAIN_COLS = 160
export const ISLAND_COLS = 96
export const SIM_SPAN = 24
export const SIM_BAND = 4
export const REST_DEPTH = 0.25
export const SDF_EXTENT = 384
export const BASE_SHORE_X = 10
export const MAIN_TABLE_N = 2048
export const MAIN_TABLE_STEP = 0.8

const COPY_FINE = 1.75
const WARP_CELL = 0.4
const WARP_LINEAR = 64
const WARP_GROWTH = 1.08
const SKIRT_W = 0.2
const SKIRT_DROP = 0.1
const SWEEP_K = 1.2
const SAND_TILE_METERS = 3

export function createOceanUniforms() {
  return {
    cameraPos: uniform(new THREE.Vector3()),
    time: uniform(0),
    sunDir: uniform(new THREE.Vector3(0, 1, 0)),
    islandArcStep: uniform(1),
    numLayers: uniform(5),
    choppiness: uniform(1.5),
    dGrad: uniform(1),
    hGrad: uniform(256),
    foamCX: uniform(0),
    foamCZ: uniform(0),
    foamDX: uniform(0),
    foamDZ: uniform(0),
    layers: Array.from({ length: 8 }, () => ({
      dirScaleAmp: uniform(new THREE.Vector4()),
      scroll: uniform(new THREE.Vector4()),
    })),
    capLayers: Array.from({ length: 6 }, () => ({
      dirScaleAmp: uniform(new THREE.Vector4()),
      scroll: uniform(new THREE.Vector4()),
    })),
    capHGrad: uniform(256),
    rippleBias: uniform(0.8),
    sssStrength: uniform(1.5),
    ampInv: uniform(5),
    seaDepth: uniform(8),
    causticStrength: uniform(1),
    causticScale: uniform(1),
    leanX: uniform(0),
    leanY: uniform(0),
    foamThreshold: uniform(0.6),
    foamRegion: uniform(80),
    foamDecay: uniform(1),
    foamDecayG: uniform(1),
    foamRise: uniform(1),
    foamLife: uniform(4),
    slope: uniform(0.15),
    foamDecaySwallow: uniform(1),
    simDt: uniform(0),
    waveK: uniform(2 * Math.PI / 10),
    foamScale: uniform(1),
    simZBase: uniform(0),
    simZShift: uniform(0),
    simTCam: uniform(0),
    debugMode: uniform(0),
  }
}

function activeLayer(u, i) {
  return select(u.numLayers.greaterThan(float(i)), 1, 0)
}

function tanhNode(x) {
  const e = exp(x.mul(2))
  return e.sub(1).div(e.add(1))
}

export function makeSharedTSL(u, resources) {
  const { waveTex, simTex, sdfTex } = resources

  const layerUV = (xz, i) => {
    const l = u.layers[i]
    const dir = l.dirScaleAmp.xy
    return vec2(
      dot(xz, dir),
      dot(xz, vec2(dir.y.negate(), dir.x)),
    ).mul(l.dirScaleAmp.z).add(l.scroll.xy)
  }

  const coastSDF = xz => {
    const baked = texture(sdfTex, xz.div(2 * SDF_EXTENT).add(0.5), 0).r
    const extent = max(abs(xz.x), abs(xz.y))
    const far = smoothstep(SDF_EXTENT - 48, SDF_EXTENT - 8, extent)
    return mix(baked, xz.x.sub(BASE_SHORE_X), far)
  }

  const terrainHeight = xz => min(max(u.slope.mul(coastSDF(xz)), u.seaDepth.negate()), 3)

  const simRestS = b => {
    const m = clamp(b, 0, SIM_SPAN)
    return float(-REST_DEPTH).div(u.slope).add(b).add(
      m.mul(float(REST_DEPTH).div(u.slope).div(SIM_SPAN).sub(1)),
    )
  }

  const wrapCol = col => {
    const island = float(MAIN_COLS).add(fract(col.sub(MAIN_COLS).div(ISLAND_COLS)).mul(ISLAND_COLS))
    return select(col.greaterThanEqual(MAIN_COLS), island, clamp(col, 0, MAIN_COLS - 1))
  }

  const nextCol = j0 => {
    const j1 = j0.add(1)
    const islandNext = select(j1.greaterThanEqual(SIM_COLS), int(MAIN_COLS), j1)
    return select(j0.greaterThanEqual(MAIN_COLS), islandNext, min(j1, MAIN_COLS - 1))
  }

  const simState = (b, col) => {
    const fx = clamp(b.div(SIM_SPAN / (SIM_NODES - 1)), 0, SIM_NODES - 1)
    const c = wrapCol(col)
    const i0 = int(floor(fx))
    const i1 = min(i0.add(1), SIM_NODES - 1)
    const j0 = int(floor(c))
    const j1 = nextCol(j0)
    const a = fx.sub(floor(fx))
    const fb = c.sub(floor(c))
    const s00 = textureLoad(simTex, ivec2(i0, j0), 0)
    const s10 = textureLoad(simTex, ivec2(i1, j0), 0)
    const s01 = textureLoad(simTex, ivec2(i0, j1), 0)
    const s11 = textureLoad(simTex, ivec2(i1, j1), 0)
    return mix(mix(s00, s10, a), mix(s01, s11, a), fb)
  }

  const simBlend = b => smoothstep(-SIM_BAND, 0, b)

  const colT = col => {
    const main = u.simZBase.add(col.div(MAIN_COLS - 1).sub(0.5).mul(160))
    const island = col.sub(MAIN_COLS).mul(u.islandArcStep)
    return select(col.lessThan(MAIN_COLS), main, island)
  }

  const waveSurface = xz => {
    let dxx = float(1)
    let dxz = float(0)
    let dzx = float(0)
    let dzz = float(1)
    let height = float(0)
    let gradH = vec2(0)

    for (let i = 0; i < 8; i++) {
      const l = u.layers[i]
      const dir = l.dirScaleAmp.xy
      const invL = l.dirScaleAmp.z
      const amp = l.dirScaleAmp.w.mul(activeLayer(u, i))
      const s = texture(waveTex, layerUV(xz, i), 0)
      const duvdx = vec2(dir.x, dir.y.negate()).mul(invL)
      const duvdz = vec2(dir.y, dir.x).mul(invL)
      const grad = s.zw.mul(u.hGrad)
      const dDdu = u.choppiness.mul(amp).mul(s.x).mul(u.dGrad)
      height = height.add(amp.mul(s.x))
      gradH = gradH.add(vec2(dot(grad, duvdx), dot(grad, duvdz)).mul(amp))
      dxx = dxx.add(dir.x.mul(dDdu).mul(duvdx.x))
      dxz = dxz.add(dir.y.mul(dDdu).mul(duvdx.x))
      dzx = dzx.add(dir.x.mul(dDdu).mul(duvdz.x))
      dzz = dzz.add(dir.y.mul(dDdu).mul(duvdz.x))
    }

    const eta = max(height.mul(u.ampInv), 0)
    const ls = eta.mul(eta).add(eta.mul(2)).div(eta.add(1).mul(eta.add(1)))
    dxx = dxx.add(u.leanX.mul(ls).mul(gradH.x))
    dxz = dxz.add(u.leanY.mul(ls).mul(gradH.x))
    dzx = dzx.add(u.leanX.mul(ls).mul(gradH.y))
    dzz = dzz.add(u.leanY.mul(ls).mul(gradH.y))
    return { jac: dxx.mul(dzz).sub(dxz.mul(dzx)), height }
  }

  return { layerUV, coastSDF, terrainHeight, simRestS, wrapCol, nextCol, simState, simBlend, colT, waveSurface }
}

export function createWaveFieldMaterial(noiseTextures, copies) {
  const mat = new THREE.MeshBasicNodeMaterial()
  mat.depthTest = false
  mat.depthWrite = false
  mat.fragmentNode = Fn(() => {
    const q = uv()
    let acc = vec4(0)
    for (let i = 0; i < 5; i++) {
      acc = acc.add(texture(noiseTextures[i], q.add(copies[i].xy), 0).mul(copies[i].z))
    }
    return acc
  })()
  return mat
}

export function createFoamMaterial(u, resources, prevFoam) {
  const shared = makeSharedTSL(u, resources)
  const mat = new THREE.MeshBasicNodeMaterial()
  mat.depthTest = false
  mat.depthWrite = false
  mat.fragmentNode = Fn(() => {
    const q = uv()
    const xz = vec2(u.foamCX, u.foamCZ).add(q.sub(0.5).mul(u.foamRegion.mul(2)))
    const s = shared.waveSurface(xz)
    const ty = shared.terrainHeight(xz)
    const waterGate = smoothstep(0, 0.3, s.height.sub(ty))
    const dNow = max(ty.negate(), 0.05)
    const genSurf = smoothstep(0.55, 0.9, s.height.div(dNow))
      .mul(smoothstep(0, 0.5, dNow)).mul(waterGate)
    const genR = max(smoothstep(u.foamThreshold, u.foamThreshold.sub(0.25), s.jac).mul(waterGate), genSurf)
    const genG = max(smoothstep(u.foamThreshold.sub(0.15), u.foamThreshold.sub(0.45), s.jac).mul(waterGate), genSurf)
    const prevUV = q.add(vec2(u.foamDX, u.foamDZ))
    const inBounds = prevUV.x.greaterThanEqual(0)
      .and(prevUV.y.greaterThanEqual(0))
      .and(prevUV.x.lessThanEqual(1))
      .and(prevUV.y.lessThanEqual(1))
    const prev = select(inBounds, texture(prevFoam, prevUV, 0), vec4(0))
    const smoothR = mix(genR, prev.b, u.foamRise)
    const smoothG = mix(genG, prev.a, u.foamRise)
    return vec4(
      max(prev.r.mul(u.foamDecay), smoothR),
      max(prev.g.mul(u.foamDecayG), smoothG),
      smoothR,
      smoothG,
    )
  })()
  return mat
}

export function createFilmFoamMaterial(u, resources, prevFoam) {
  const shared = makeSharedTSL(u, resources)
  const mat = new THREE.MeshBasicNodeMaterial()
  mat.depthTest = false
  mat.depthWrite = false
  mat.fragmentNode = Fn(() => {
    const q = uv()
    const b = q.x.mul(SIM_BAND + SIM_SPAN).sub(SIM_BAND)
    const col = q.y.mul(SIM_COLS).sub(0.5)
    const sim = shared.simState(b, col)
    const e = 0.8
    const restScale = float(REST_DEPTH).div(u.slope).div(SIM_SPAN)
    const b0 = max(b.sub(e), 0)
    const b1 = min(b.add(e), SIM_SPAN)
    const compress = shared.simState(b0, col).x.sub(shared.simState(b1, col).x)
      .div(max(b1.sub(b0), 0.01).mul(restScale))
    const sNow = shared.simRestS(b).add(sim.x)
    const sb = shared.simBlend(b)
    const inFilm = sb.mul(float(1).sub(smoothstep(sim.z.sub(0.3), sim.z.add(0.1), sNow)))
    const gen = inFilm.mul(smoothstep(0.25, 0.7, compress)).mul(smoothstep(0, 8, b))
    const sJ = float(-REST_DEPTH).div(u.slope).add(shared.simState(float(0), col).x)
    const tyM = u.slope.mul(shared.simRestS(b))
    const swallowed = sb.mul(smoothstep(0.3, -0.7, sNow.sub(sJ))).mul(smoothstep(-1.2, -0.3, tyM))
    const decayR = mix(u.foamDecay, u.foamDecaySwallow, swallowed)
    const prevY = select(col.lessThan(MAIN_COLS), q.y.add(u.simZShift.div(SIM_COLS)), q.y)
    const prevUV = vec2(q.x, prevY)
    let prev = texture(prevFoam, prevUV, 0)
    const pCol = prevUV.y.mul(SIM_COLS).sub(0.5)
    const invalidMain = col.lessThan(MAIN_COLS).and(pCol.lessThan(-0.5).or(pCol.greaterThanEqual(MAIN_COLS - 0.5)))
    prev = select(invalidMain, vec4(0), prev)
    const smoothR = mix(gen, prev.b, u.foamRise)
    const smoothG = mix(gen, prev.a, u.foamRise)
    return vec4(
      max(prev.r.mul(decayR), smoothR),
      max(prev.g.mul(u.foamDecayG), smoothG),
      smoothR,
      smoothG,
    )
  })()
  return mat
}

function sunWarmth(sunDir) {
  return float(1).sub(smoothstep(0.03, 0.5, clamp(sunDir.y, 0, 1)))
}

function sunTint(sunDir) {
  const w = sunWarmth(sunDir)
  return mix(vec3(1, 0.97, 0.9), vec3(1.25, 0.5, 0.18), w.mul(w))
}

export function coastalSkyRadiance(dir, sunDir) {
  const w = sunWarmth(sunDir)
  const t = pow(clamp(dir.y, 0, 1), mix(0.5, 0.65, w))
  const dh = normalize(dir.xz.add(vec2(1e-5, 0)))
  const sh = normalize(sunDir.xz)
  const facing = pow(float(0.5).add(dot(dh, sh).mul(0.5)), 3)
  const zenith = mix(vec3(0.11, 0.30, 0.60), vec3(0.08, 0.12, 0.30), w)
  const horizonWarm = mix(vec3(0.42, 0.36, 0.52), vec3(1.1, 0.45, 0.16), facing)
  const horizon = mix(vec3(0.62, 0.72, 0.83), horizonWarm, w)
  const g = max(dot(dir, sunDir), 0)
  return mix(horizon, zenith, t).add(
    sunTint(sunDir).mul(
      pow(g, mix(40, 10, w)).mul(mix(0.25, 0.6, w)).add(pow(g, 4000).mul(3)),
    ),
  )
}

function createSandSampler(sandBase, sandNormal, shared) {
  const sandUV = xz => xz.div(SAND_TILE_METERS)
  const sandColor = xz => texture(sandBase, sandUV(xz)).rgb

  const terrainNormal = xz => {
    const e = 0.5
    const hx = shared.terrainHeight(xz.add(vec2(e, 0))).sub(shared.terrainHeight(xz.sub(vec2(e, 0))))
    const hz = shared.terrainHeight(xz.add(vec2(0, e))).sub(shared.terrainHeight(xz.sub(vec2(0, e))))
    return normalize(vec3(hx.div(-2 * e), 1, hz.div(-2 * e)))
  }

  const sandSurfaceNormal = xz => {
    const baseN = terrainNormal(xz)
    const q = sandUV(xz)
    const sampled = texture(sandNormal, q).xyz.mul(2).sub(1)
    // Mips + anisotropy handle the base texture. For normals, additionally
    // fade the tangent perturbation once a pixel covers multiple source texels,
    // preventing high-frequency sparkling at long, grazing views.
    const size = vec2(textureSize(texture(sandNormal), int(0)))
    const footprint = max(length(fwidth(q).mul(size)), 1)
    const detail = clamp(float(2).div(footprint), 0.15, 1)
    const nm = normalize(vec3(sampled.xy.mul(detail), max(sampled.z, 0.05)))
    const tangent = normalize(vec3(1, 0, 0).sub(baseN.mul(baseN.x)))
    const bitangent = normalize(cross(tangent, baseN))
    return normalize(tangent.mul(nm.x).add(bitangent.mul(nm.y)).add(baseN.mul(nm.z)))
  }

  return { sandColor, terrainNormal, sandSurfaceNormal }
}

export function createOceanMaterials(u, resources) {
  const {
    waveTex, capTex, foamTex, filmFoamTex, foamPatTex,
    simTex, coastTex, sdfTex, mainTableTex, sandBase, sandNormal,
  } = resources
  const shared = makeSharedTSL(u, { waveTex, simTex, sdfTex })
  const sand = createSandSampler(sandBase, sandNormal, shared)

  const coastAt = col => {
    const c = shared.wrapCol(col)
    const j0 = int(floor(c))
    const j1 = shared.nextCol(j0)
    const a = c.sub(floor(c))
    return mix(textureLoad(coastTex, ivec2(j0, 0), 0), textureLoad(coastTex, ivec2(j1, 0), 0), a)
  }

  const filmFoamAt = (b, col) => {
    const fx = clamp(b.add(SIM_BAND).div(SIM_BAND + SIM_SPAN).mul(127), 0, 127)
    const c = shared.wrapCol(col)
    const j0 = int(floor(c))
    const j1 = shared.nextCol(j0)
    const i0 = int(floor(fx))
    const i1 = min(i0.add(1), 127)
    const a = fx.sub(floor(fx))
    const fb = c.sub(floor(c))
    return mix(
      mix(textureLoad(filmFoamTex, ivec2(i0, j0), 0), textureLoad(filmFoamTex, ivec2(i1, j0), 0), a),
      mix(textureLoad(filmFoamTex, ivec2(i0, j1), 0), textureLoad(filmFoamTex, ivec2(i1, j1), 0), a),
      fb,
    )
  }

  const sampleWaves = (xz, cell) => {
    let height = float(0)
    let disp = vec2(0)
    for (let i = 0; i < 8; i++) {
      const l = u.layers[i]
      const gate = activeLayer(u, i)
      const att = float(1).sub(smoothstep(2, 6, cell.mul(l.dirScaleAmp.z).mul(u.hGrad).mul(COPY_FINE)))
      const s = texture(waveTex, shared.layerUV(xz, i), 0)
      const amp = l.dirScaleAmp.w.mul(gate)
      height = height.add(amp.mul(s.x).mul(att))
      disp = disp.add(l.dirScaleAmp.xy.mul(u.choppiness.mul(amp).mul(s.y).mul(att)))
    }
    const eta = max(height.mul(u.ampInv), 0)
    disp = disp.add(vec2(u.leanX, u.leanY).mul(eta.mul(eta).div(eta.add(1)).div(u.ampInv)))
    const ty0 = shared.terrainHeight(xz)
    const wSea = float(1).sub(smoothstep(-0.6, 0.1, ty0))
    const kd = u.waveK.mul(max(ty0.negate(), 0.05))
    const shallowAmp = clamp(float(1).div(max(tanhNode(kd), 1e-4)), 1, 2.5)
    return { height, disp: disp.mul(shallowAmp).mul(wSea) }
  }

  const softClamp = (height, ty) => {
    const dy = height.sub(ty.add(0.1))
    return ty.add(0.1).add(dy.add(sqrt(dy.mul(dy).add(0.0225))).mul(0.5))
  }

  const warpVertex = p => {
    const snap = floor(u.cameraPos.xz.div(WARP_CELL).add(0.5)).mul(WARP_CELL)
    const r = length(p)
    const k = min(r.sub(WARP_LINEAR).div(WARP_CELL), 98)
    const g = pow(WARP_GROWTH, max(k, 0))
    const rw = float(WARP_LINEAR).add(float(WARP_CELL).mul(g.sub(1)).div(WARP_GROWTH - 1))
    const warped = snap.add(p.mul(rw.div(max(r, 1e-5))))
    const xz = select(r.lessThanEqual(WARP_LINEAR), snap.add(p), warped)
    const cell = select(r.lessThanEqual(WARP_LINEAR), WARP_CELL, g.mul(WARP_CELL))
    return { xz, cell }
  }

  const warpCellAt = dist => float(WARP_CELL).add(max(float(WARP_GROWTH - 1).mul(dist.sub(WARP_LINEAR)), 0))

  const mainCoastAt = t => {
    const f = t.div(MAIN_TABLE_STEP).add((MAIN_TABLE_N - 1) * 0.5)
    const fc = clamp(f, 0, MAIN_TABLE_N - 1)
    const j0 = min(int(floor(fc)), MAIN_TABLE_N - 2)
    const a = fc.sub(float(j0))
    const c = mix(
      textureLoad(mainTableTex, ivec2(j0, 0), 0),
      textureLoad(mainTableTex, ivec2(j0.add(1), 0), 0),
      a,
    )
    const n = normalize(c.zw)
    const over = f.sub(fc).mul(MAIN_TABLE_STEP)
    return vec4(c.xy.add(vec2(n.y.negate(), n.x).mul(over)), n)
  }

  const ribbonVertex = (b, col, coastP, coastN, cell) => {
    const matWorld = coastP.add(coastN.mul(float(-REST_DEPTH).div(u.slope).add(b)))
    const cellW = max(cell, warpCellAt(distance(u.cameraPos.xz, matWorld)))
    const w = sampleWaves(matWorld, cellW)
    const sb = shared.simBlend(b)
    const chain = shared.simState(b, col)
    const chainJ = shared.simState(float(0), col)
    const wS = smoothstep(0, 12, b)
    const chainWorld = coastP.add(coastN.mul(shared.simRestS(b).add(mix(chainJ.x, chain.x, wS))))
    const dispXZ = mix(matWorld.add(w.disp), chainWorld, sb)
    const ty = shared.terrainHeight(dispXZ)
    const yWave = softClamp(w.height, ty)
    const sJ = float(-REST_DEPTH).div(u.slope).add(chainJ.x)
    const tyJ = u.slope.mul(sJ)
    const tyF = max(ty, tyJ)
    const tTip = clamp(b.div(SIM_SPAN), 0, 1)
    let y = mix(yWave, tyF.add(float(REST_DEPTH).mul(float(1).sub(tTip))), sb)
    y = y.sub(float(SKIRT_DROP).mul(clamp(float(-SIM_BAND - SKIRT_W).sub(b).div(SKIRT_W), 0, 1)))
    const eS = 1
    const plus = shared.simRestS(b.add(eS)).add(
      mix(chainJ.x, shared.simState(b.add(eS), col).x, smoothstep(0, 12, b.add(eS))),
    )
    const minus = shared.simRestS(b.sub(eS)).add(
      mix(chainJ.x, shared.simState(b.sub(eS), col).x, smoothstep(0, 12, b.sub(eS))),
    )
    return {
      world: vec3(dispXZ.x, y, dispXZ.y),
      gridXZ: matWorld,
      cut: float(-1),
      st: vec2(b, col),
      waveXZ: mix(matWorld, coastP.add(coastN.mul(shared.simRestS(b))), sb),
      stretch: abs(plus.sub(minus)).div(2 * eS),
    }
  }

  const gridVertex = p => {
    const wv = warpVertex(p)
    const w = sampleWaves(wv.xz, wv.cell)
    const dispXZ = wv.xz.add(w.disp)
    const ty = shared.terrainHeight(dispXZ)
    const sOff = shared.coastSDF(wv.xz)
    const sJ0 = float(-REST_DEPTH).div(u.slope)
    return {
      world: vec3(dispXZ.x, softClamp(w.height, ty), dispXZ.y),
      gridXZ: wv.xz,
      cut: sOff.sub(sJ0.sub(SIM_BAND)),
      st: vec2(-1000, 0),
      waveXZ: wv.xz,
      stretch: float(1),
    }
  }

  const landVertex = p => {
    const wv = warpVertex(p)
    return {
      world: vec3(wv.xz.x, shared.terrainHeight(wv.xz), wv.xz.y),
      gridXZ: wv.xz,
      cut: float(-1),
      st: vec2(-1000, 0),
      waveXZ: wv.xz,
      stretch: float(1),
    }
  }

  const mainlandVertex = p => {
    const t = u.simTCam.add(p.y)
    const b = p.x.mul(SIM_SPAN + SIM_BAND + 2 * SKIRT_W).sub(SIM_BAND + 2 * SKIRT_W)
    const col = clamp(t.sub(u.simZBase).div(160).add(0.5).mul(MAIN_COLS - 1), 0, MAIN_COLS - 1)
    const c = mainCoastAt(t)
    return ribbonVertex(b, col, c.xy, c.zw, p.z)
  }

  const islandVertex = p => {
    const b = p.x.mul(SIM_SPAN + SIM_BAND + 2 * SKIRT_W).sub(SIM_BAND + 2 * SKIRT_W)
    const c = coastAt(p.y)
    return ribbonVertex(b, p.y, c.xy, normalize(c.zw), p.z)
  }

  const surfaceNormal = (xz, rippleXZ, dist, eta, hScale) => {
    let dPx = vec3(1, 0, 0)
    let dPz = vec3(0, 0, 1)
    let varC = float(0)
    let varP = float(0)
    const mpp = length(fwidth(xz))

    for (let i = 0; i < 8; i++) {
      const l = u.layers[i]
      const dir = l.dirScaleAmp.xy
      const invL = l.dirScaleAmp.z
      const gate = activeLayer(u, i)
      const attenuation = float(1).sub(smoothstep(5, 14, mpp.mul(l.dirScaleAmp.z).mul(u.hGrad).mul(COPY_FINE)))
      const amp = l.dirScaleAmp.w.mul(gate).mul(attenuation)
      const s = texture(waveTex, shared.layerUV(xz, i))
      const duvdx = vec2(dir.x, dir.y.negate()).mul(invL)
      const duvdz = vec2(dir.y, dir.x).mul(invL)
      const grad = s.zw.mul(u.hGrad).mul(hScale)
      const dDdu = u.choppiness.mul(amp).mul(s.x).mul(u.dGrad)
      dPx = dPx.add(vec3(
        dir.x.mul(dDdu).mul(duvdx.x),
        amp.mul(dot(grad, duvdx)),
        dir.y.mul(dDdu).mul(duvdx.x),
      ))
      dPz = dPz.add(vec3(
        dir.x.mul(dDdu).mul(duvdz.x),
        amp.mul(dot(grad, duvdz)),
        dir.y.mul(dDdu).mul(duvdz.x),
      ))
      const cAmp = u.choppiness.mul(amp).mul(u.dGrad).mul(invL)
      const cAmpP = u.choppiness.mul(l.dirScaleAmp.w).mul(gate).mul(u.dGrad).mul(invL)
      varC = varC.add(cAmp.mul(cAmp))
      varP = varP.add(cAmpP.mul(cAmpP))
    }

    const leanSlope = eta.mul(eta).add(eta.mul(2)).div(eta.add(1).mul(eta.add(1)))
    dPx = dPx.add(vec3(u.leanX.mul(leanSlope).mul(dPx.y), 0, u.leanY.mul(leanSlope).mul(dPx.y)))
    dPz = dPz.add(vec3(u.leanX.mul(leanSlope).mul(dPz.y), 0, u.leanY.mul(leanSlope).mul(dPz.y)))
    const jac = dPx.x.mul(dPz.z).sub(dPz.x.mul(dPx.z))
    const sigma = sqrt(varC)
    const sigmaP = sqrt(varP)
    const front = smoothstep(0, 0.15, dPx.y.negate())
    const squeeze = smoothstep(0, 0.3, float(2).sub(dPx.x).sub(dPz.z))
    const conc = front.add(squeeze)
    const fade = clamp(float(1).sub(dist.div(150)), 0, 1)
    const isoScale = mix(1, conc, u.rippleBias.mul(0.4)).mul(fade)
    const anisoScale = mix(1, conc, u.rippleBias).mul(fade)

    for (let i = 0; i < 6; i++) {
      const l = u.capLayers[i]
      const dir = l.dirScaleAmp.xy
      const invL = l.dirScaleAmp.z
      const uvc = vec2(
        dot(rippleXZ, dir),
        dot(rippleXZ, vec2(dir.y.negate(), dir.x)),
      ).mul(invL).add(l.scroll.xy)
      const isIso = i < 3
      const src = isIso ? capTex : waveTex
      const gradScale = isIso ? u.capHGrad : u.hGrad.mul(COPY_FINE)
      const s = texture(src, uvc)
      const aa = float(1).sub(smoothstep(5, 14, mpp.mul(invL).mul(gradScale)))
      const scale = isIso ? isoScale : anisoScale
      const amp = scale.mul(l.dirScaleAmp.w).mul(isIso ? u.capHGrad : u.hGrad).mul(aa)
      const grad = s.zw.mul(amp)
      dPx = dPx.add(vec3(0, dot(grad, vec2(dir.x, dir.y.negate()).mul(invL)), 0))
      dPz = dPz.add(vec3(0, dot(grad, vec2(dir.y, dir.x).mul(invL)), 0))
    }

    return { n: normalize(cross(dPz, dPx)), jac, sigma, sigmaP }
  }

  function makeVaryings(prefix) {
    return {
      world: varyingProperty('vec3', `${prefix}World`),
      gridXZ: varyingProperty('vec2', `${prefix}GridXZ`),
      cut: varyingProperty('float', `${prefix}Cut`),
      st: varyingProperty('vec2', `${prefix}ST`),
      waveXZ: varyingProperty('vec2', `${prefix}WaveXZ`),
      stretch: varyingProperty('float', `${prefix}Stretch`),
    }
  }

  function assignVaryings(v, out) {
    v.world.assign(out.world)
    v.gridXZ.assign(out.gridXZ)
    v.cut.assign(out.cut)
    v.st.assign(out.st)
    v.waveXZ.assign(out.waveXZ)
    v.stretch.assign(out.stretch)
  }

  const shadeWater = v => Fn(() => {
    If(v.cut.greaterThan(0), () => Discard())

    const dist = distance(u.cameraPos, v.world)
    const sbF = shared.simBlend(v.st.x)
    const rippleXZ = mix(v.gridXZ, v.world.xz, sbF)
    const ns = surfaceNormal(v.waveXZ, rippleXZ, dist, max(v.world.y.mul(u.ampInv), 0), float(1).sub(sbF))
    const ty = shared.terrainHeight(v.world.xz)
    const column = max(v.world.y.sub(ty), 0)
    const waterM = smoothstep(0.025, 0.09, column)
    const sandN = sand.sandSurfaceNormal(v.world.xz)
    let n = normalize(mix(sandN, ns.n, waterM))
    const view = normalize(u.cameraPos.sub(v.world))
    n = select(dot(n, view).lessThan(0), n.negate(), n)
    const fresnel = float(0.02).add(float(0.98).mul(pow(float(1).sub(max(dot(n, view), 0)), 5)))
    const r = reflect(view.negate(), n)
    const spec = sunTint(u.sunDir).mul(
      mix(8, 4.5, sunWarmth(u.sunDir)).mul(pow(max(dot(r, u.sunDir), 0), 600)),
    )

    const fCenter = vec2(u.foamCX, u.foamCZ)
    const fuv = v.waveXZ.sub(fCenter).div(u.foamRegion.mul(2)).add(0.5)
    const edgeFade = float(1).sub(smoothstep(0.85, 1, length(v.waveXZ.sub(fCenter)).div(u.foamRegion)))
    const foamRaw = texture(foamTex, fuv).rgb
    const foamAcc = foamRaw.mul(edgeFade)
    const sigmaR = max(ns.sigma, 1e-4)
    const pGen = float(1).div(float(1).add(exp(float(-1.702).mul(u.foamThreshold.sub(1)).div(max(ns.sigmaP, 1e-4)))))
    const period = float(6.2832).div(sqrt(float(9.81).mul(u.waveK)))
    const cover = clamp(float(1).sub(pow(float(1).sub(pGen), float(1).add(float(SWEEP_K).mul(u.foamLife).div(period)))), 1e-4, 0.6)
    const zQ = log(float(1).div(cover).sub(1)).negate().div(1.702)
    const zNow = ns.jac.sub(1).div(sigmaR)
    const waterGateF = smoothstep(0, 0.3, v.world.y.sub(ty))
    const depthF = max(ty.negate(), 0.05)
    const genSurfF = smoothstep(0.55, 0.9, v.world.y.div(depthF)).mul(smoothstep(0, 0.5, depthF)).mul(waterGateF)
    const tailW = float(1).div(float(1).add(abs(zQ)))
    const farJ = clamp(float(0.48).add(float(0.45).mul(float(1).sub(exp(zNow.sub(zQ).add(0.28).div(tailW))))), 0, 1)
    const farR = max(farJ.mul(waterGateF), genSurfF)
    const bufBlend = edgeFade.mul(float(1).sub(smoothstep(u.foamRegion, u.foamRegion.mul(2), dist)))
    const accR = mix(farR, foamRaw.r, bufBlend)
    const towardSun = max(dot(view, u.sunDir).negate(), 0)
    const sss = u.sssStrength.mul(float(0.55).add(towardSun.mul(towardSun).mul(0.45))).mul(foamAcc.g).mul(float(1).sub(sbF))
    const refr = refract(view.negate(), n, 0.752)
    const grazing = float(1).div(max(refr.y.negate(), 0.05))
    const lateral = mix(grazing, min(grazing, 2), sbF)
    const pathLen = column.mul(lateral.add(1.4))
    const trans = exp(vec3(0.25, 0.04, 0.02).mul(pathLen).negate())
    const bottomXZ = v.world.xz.add(refr.xz.mul(column.mul(lateral)))
    const cs = texture(capTex, bottomXZ.div(u.causticScale.mul(13)).add(vec2(0.023, 0.011).mul(u.time))).x
      .add(texture(capTex, bottomXZ.div(u.causticScale.mul(8.7)).add(vec2(-0.017, 0.019).mul(u.time))).x)
    const web = pow(max(float(1).sub(abs(cs).mul(0.6)), 0), 4)
    const focus = u.causticStrength.mul(exp(column.mul(-0.12)))
      .mul(clamp(float(1).sub(dist.div(120)), 0, 1)).mul(smoothstep(0.04, 0.25, column))
    const bottomBase = sand.sandColor(bottomXZ)
    const bottomN = sand.sandSurfaceNormal(bottomXZ)
    const bottomDiffuse = float(0.78).add(max(dot(bottomN, u.sunDir), 0).mul(0.22))
    const sandUnder = bottomBase.mul(bottomDiffuse).mul(float(0.85).add(focus.mul(web.mul(1.6).sub(0.18))))
    const lightTint = mix(vec3(1), sunTint(u.sunDir), 0.6)
    const sunLevel = mix(0.18, 1, smoothstep(0, 0.5, clamp(u.sunDir.y, 0, 1)))
    let water = mix(vec3(0.004, 0.02, 0.05), sandUnder, trans).mul(lightTint)
    water = water.add(vec3(0.05, 0.45, 0.38).mul(sss)).mul(sunLevel)
    let color = mix(water, coastalSkyRadiance(r, u.sunDir), fresnel).add(spec)
    const dryBase = sand.sandColor(v.world.xz)
    const dryDiffuse = float(0.55).add(max(sandN.y, 0).mul(0.45))
    const sandMatte = dryBase.mul(lightTint).mul(sunLevel).mul(dryDiffuse)
    color = mix(sandMatte, color, waterM)

    const filmAcc = filmFoamAt(v.st.x, v.st.y).rgb
    const patWave = texture(foamPatTex, v.waveXZ.div(u.foamScale.mul(5))).r
    const patFilmUV = vec2(v.st.x, shared.colT(v.st.y)).div(u.foamScale.mul(5))
    const patFine = texture(foamPatTex, vec2(patFilmUV.x.div(3), patFilmUV.y)).r
    const patCoarse = texture(foamPatTex, vec2(patFilmUV.x.div(9), patFilmUV.y)).r
    const patFilm = mix(patFine, patCoarse, float(1).sub(smoothstep(0.07, 0.4, v.stretch)))
    const junctionFade = float(1).sub(smoothstep(0, 6, v.st.x))
    const maskWave = smoothstep(0, 0.15, patWave.sub(float(1.05).sub(accR.mul(junctionFade).mul(1.15))))
    const wetAcc = filmAcc.b.add(filmAcc.r.mul(0.8)).mul(smoothstep(0.02, 0.08, column))
    const maskFilm = smoothstep(0, 0.15, patFilm.sub(float(1.05).sub(wetAcc.mul(1.15))))
    const foamMask = min(maskWave.add(maskFilm), 1)
    const foamColor = lightTint.mul(mix(0.45, 1, sunLevel)).mul(float(0.72).add(max(n.y, 0).mul(0.22)))
    color = mix(color, foamColor, foamMask)
    const fog = float(1).sub(exp(dist.mul(-3e-5)))
    color = mix(color, coastalSkyRadiance(normalize(vec3(view.x.negate(), 0.02, view.z.negate())), u.sunDir), fog)
    const coastDistance = shared.coastSDF(v.world.xz)
    const coastDebug = mix(
      vec3(0.02, 0.12, 0.24),
      vec3(0.76, 0.46, 0.20),
      smoothstep(-2, 2, coastDistance),
    ).add(vec3(float(1).sub(smoothstep(0, 0.18, abs(coastDistance))).mul(0.8)))
    color = select(u.debugMode.equal(1), n.mul(0.5).add(0.5), color)
    color = select(u.debugMode.equal(2), vec3(foamAcc.r, filmAcc.r, foamMask), color)
    color = select(u.debugMode.equal(3), coastDebug, color)
    color = float(1).sub(exp(color.mul(-1.8)))
    return vec4(pow(color, vec3(1 / 2.2)), 1)
  })()

  const shadeLand = v => Fn(() => {
    const n = sand.sandSurfaceNormal(v.gridXZ)
    const lightTint = mix(vec3(1), sunTint(u.sunDir), 0.6)
    const sunLevel = mix(0.18, 1, smoothstep(0, 0.5, clamp(u.sunDir.y, 0, 1)))
    let color = sand.sandColor(v.gridXZ).mul(lightTint).mul(sunLevel).mul(float(0.55).add(max(n.y, 0).mul(0.45)))
    const dist = distance(u.cameraPos, v.world)
    const view = normalize(u.cameraPos.sub(v.world))
    const fog = float(1).sub(exp(dist.mul(-3e-5)))
    color = mix(color, coastalSkyRadiance(normalize(vec3(view.x.negate(), 0.02, view.z.negate())), u.sunDir), fog)
    const coastDistance = shared.coastSDF(v.gridXZ)
    const coastDebug = mix(
      vec3(0.02, 0.12, 0.24),
      vec3(0.76, 0.46, 0.20),
      smoothstep(-2, 2, coastDistance),
    ).add(vec3(float(1).sub(smoothstep(0, 0.18, abs(coastDistance))).mul(0.8)))
    color = select(u.debugMode.equal(1), n.mul(0.5).add(0.5), color)
    color = select(u.debugMode.equal(2), vec3(0), color)
    color = select(u.debugMode.equal(3), coastDebug, color)
    color = float(1).sub(exp(color.mul(-1.8)))
    return vec4(pow(color, vec3(1 / 2.2)), 1)
  })()

  function makeMaterial(kind, prefix, isLand = false, line = false) {
    const v = makeVaryings(prefix)
    const mat = line ? new THREE.LineBasicNodeMaterial() : new THREE.MeshBasicNodeMaterial()
    mat.depthTest = true
    mat.depthWrite = true
    if (!line) mat.side = THREE.FrontSide
    mat.positionNode = Fn(() => {
      const p = attribute('position')
      let out
      if (kind === 'grid') out = gridVertex(p.xy)
      else if (kind === 'main') out = mainlandVertex(p)
      else if (kind === 'island') out = islandVertex(p)
      else out = landVertex(p.xy)
      assignVaryings(v, out)
      return out.world
    })()
    if (line) {
      mat.colorNode = Fn(() => {
        If(v.cut.greaterThan(0), () => Discard())
        return vec3(0.15, 0.85, 0.5)
      })()
    } else {
      mat.fragmentNode = isLand ? shadeLand(v) : shadeWater(v)
    }
    return mat
  }

  return {
    grid: makeMaterial('grid', 'grid'),
    ribbon: makeMaterial('main', 'ribbon'),
    island: makeMaterial('island', 'island'),
    land: makeMaterial('land', 'land', true),
    gridWire: makeMaterial('grid', 'gridWire', false, true),
    ribbonWire: makeMaterial('main', 'ribbonWire', false, true),
    islandWire: makeMaterial('island', 'islandWire', false, true),
    landWire: makeMaterial('land', 'landWire', true, true),
  }
}
