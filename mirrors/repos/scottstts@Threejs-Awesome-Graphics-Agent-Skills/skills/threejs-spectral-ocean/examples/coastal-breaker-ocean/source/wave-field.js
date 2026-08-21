import * as THREE from 'three/webgpu'
import { uniform } from 'three/tsl'
import { createWaveFieldMaterial } from './tsl.js'

function makeFullscreenGeometry() {
  const geometry = new THREE.PlaneGeometry(2, 2)
  // The legacy fullscreen triangle used uv.y = 1 - clipUV.y. Keep
  // that convention so the generated wave field has identical orientation.
  const texcoord = geometry.getAttribute('uv')
  for (let i = 0; i < texcoord.count; i++) texcoord.setY(i, 1 - texcoord.getY(i))
  texcoord.needsUpdate = true
  return geometry
}

// Blend the noise copies scrolling at different speeds into one texture per
// frame. A comb noise set supplies its own physical per-copy speeds and
// weights; single-texture noises (capillary) use the in-band fallbacks.
const COPY_FACTORS = [-0.65, -0.3, 0.1, 0.4, 0.7]
const DISPERSION_JITTER = [0.55, -0.45, 0.3, -0.6, -0.37]
const COPY_FACTORS_Y = [0.5, -0.35, -0.65, 0.2, 0.35]
const COPY_OFFSETS = [[0.13, 0.71], [0.53, 0.29], [0.87, 0.61], [0.31, 0.07], [0.67, 0.43]]

export class WaveField {
  // The input noise is band-limited. The ocean shader applies the same
  // analytic per-layer attenuation as before instead of relying on mipmaps.
  constructor(renderer, noise) {
    this.renderer = renderer
    this.size = noise.size
    this.target = new THREE.RenderTarget(this.size, this.size, {
      type: THREE.HalfFloatType,
      format: THREE.RGBAFormat,
      depthBuffer: false,
      stencilBuffer: false,
    })
    this.target.texture.wrapS = this.target.texture.wrapT = THREE.RepeatWrapping
    this.target.texture.magFilter = THREE.LinearFilter
    this.target.texture.minFilter = THREE.LinearFilter
    this.target.texture.generateMipmaps = false
    this.target.texture.colorSpace = THREE.NoColorSpace
    this.texture = this.target.texture

    const texs = noise.textures ?? COPY_FACTORS.map(() => noise.texture)
    this.copyUniforms = COPY_FACTORS.map(() => uniform(new THREE.Vector4()))
    this.material = createWaveFieldMaterial(texs, this.copyUniforms)
    this.scene = new THREE.Scene()
    this.camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 2)
    this.camera.position.z = 1
    this.quad = new THREE.Mesh(makeFullscreenGeometry(), this.material)
    this.quad.frustumCulled = false
    this.scene.add(this.quad)

    this.base = noise.copySpeeds ?? COPY_FACTORS.map(() => 0)
    this.jitter = noise.copySpeeds ? DISPERSION_JITTER : COPY_FACTORS
    this.weights = noise.copyWeights ?? COPY_FACTORS.map(() => 1 / Math.sqrt(COPY_FACTORS.length))
    this.phases = COPY_FACTORS.map(() => 0)
    this.phasesY = COPY_FACTORS.map(() => 0)
    // Kept as CPU-visible state because the breaker-chain sampler uses the
    // exact same copy offsets/weights as the GPU composition pass.
    this.data = new Float32Array(COPY_FACTORS.length * 4)
  }

  update(dt, texFreq, dispersion) {
    for (let i = 0; i < COPY_FACTORS.length; i++) {
      this.phases[i] += (this.base[i] + dispersion * this.jitter[i]) * texFreq * dt
      this.phasesY[i] += COPY_FACTORS_Y[i] * dispersion * texFreq * dt
      const x = COPY_OFFSETS[i][0] - this.phases[i]
      const y = COPY_OFFSETS[i][1] - this.phasesY[i]
      const w = this.weights[i]
      this.data.set([x, y, w, 0], i * 4)
      this.copyUniforms[i].value.set(x, y, w, 0)
    }
  }

  render() {
    this.renderer.setRenderTarget(this.target)
    this.renderer.setClearColor(0x000000, 0)
    this.renderer.clear()
    this.renderer.render(this.scene, this.camera)
    this.renderer.setRenderTarget(null)
  }
}
