import * as THREE from 'three/webgpu'
import { texture, uv } from 'three/tsl'
import { createFilmFoamMaterial, createFoamMaterial } from './tsl.js'

const SIZE = 512

function makeFullscreenGeometry() {
  const geometry = new THREE.PlaneGeometry(2, 2)
  // Match the explicit V flip in the legacy fullscreen-triangle vertex
  // shaders so ping-pong state keeps the same texture-space orientation.
  const texcoord = geometry.getAttribute('uv')
  for (let i = 0; i < texcoord.count; i++) texcoord.setY(i, 1 - texcoord.getY(i))
  texcoord.needsUpdate = true
  return geometry
}

function makeTarget(width, height) {
  const target = new THREE.RenderTarget(width, height, {
    type: THREE.HalfFloatType,
    format: THREE.RGBAFormat,
    depthBuffer: false,
    stencilBuffer: false,
  })
  target.texture.wrapS = target.texture.wrapT = THREE.RepeatWrapping
  target.texture.magFilter = THREE.LinearFilter
  target.texture.minFilter = THREE.LinearFilter
  target.texture.generateMipmaps = false
  target.texture.colorSpace = THREE.NoColorSpace
  return target
}

function makeCopyMaterial(source) {
  const material = new THREE.MeshBasicNodeMaterial()
  material.depthTest = false
  material.depthWrite = false
  material.fragmentNode = texture(source, uv())
  return material
}

// Persistent accumulation uses two ping-pong targets. A third stable display
// target mirrors the newest result so the ocean materials can keep one texture
// binding instead of being rebuilt every time the ping-pong index flips.
export class FoamSim {
  constructor(renderer, uniforms, resources, kind = 'world', size = [SIZE, SIZE]) {
    this.renderer = renderer
    this.index = 0
    this.targets = [makeTarget(size[0], size[1]), makeTarget(size[0], size[1])]
    this.displayTarget = makeTarget(size[0], size[1])
    this.texture = this.displayTarget.texture

    this.camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 2)
    this.camera.position.z = 1
    this.scene = new THREE.Scene()
    this.quad = new THREE.Mesh(makeFullscreenGeometry())
    this.quad.frustumCulled = false
    this.scene.add(this.quad)

    const create = kind === 'film' ? createFilmFoamMaterial : createFoamMaterial
    this.materials = [0, 1].map(src => create(uniforms, resources, this.targets[src].texture))
    this.copyMaterials = this.targets.map(target => makeCopyMaterial(target.texture))
  }

  render() {
    const dst = this.index ^ 1

    this.quad.material = this.materials[this.index]
    this.renderer.setRenderTarget(this.targets[dst])
    this.renderer.setClearColor(0x000000, 0)
    this.renderer.clear()
    this.renderer.render(this.scene, this.camera)

    this.quad.material = this.copyMaterials[dst]
    this.renderer.setRenderTarget(this.displayTarget)
    this.renderer.setClearColor(0x000000, 0)
    this.renderer.clear()
    this.renderer.render(this.scene, this.camera)

    this.renderer.setRenderTarget(null)
    this.index = dst
  }
}
