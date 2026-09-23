import { SAND, type Stroke } from '../config'
import { checkedShader } from '../platform/shader'
import type { WaveResetState } from '../reset/effect'
import { idleWaveResetState } from '../reset/effect'
import type { SandSolver } from '../simulation/solver'
import { AirborneShadow } from './airborne-shadow'
import { SandCamera } from './camera'
import { CoconutShadow } from './coconut-shadow'
import { BedLighting } from './lighting'
import { GLINT_FORMAT, HDR_SCENE_FORMAT, SandPostProcess } from './postprocess'
import { surfaceShader } from './shaders'

const LIGHT_ANGLE = -0.8
const LIGHT_DIRECTION = [Math.cos(LIGHT_ANGLE), 0.65, Math.sin(LIGHT_ANGLE)] as const

export class SandRenderer {
  readonly camera = new SandCamera()
  private readonly uniform: GPUBuffer
  private readonly lighting: BedLighting
  private readonly shadow: CoconutShadow
  private readonly airborneShadow: AirborneShadow
  private readonly post: SandPostProcess
  private readonly indices: GPUBuffer
  private readonly indexCount: number
  private pipeline!: GPURenderPipeline
  private grainPipeline!: GPURenderPipeline
  private grainGroup!: GPUBindGroup
  private groups: GPUBindGroup[] = []
  private depth: GPUTexture | undefined
  private width = 0
  private height = 0
  private readonly data = new Float32Array(40)
  private debugMode = 0

  private readonly device: GPUDevice
  private readonly solver: SandSolver
  private readonly mobileGrainFiltering: boolean
  constructor(device: GPUDevice, solver: SandSolver, format: GPUTextureFormat, mobileGrainFiltering = false, treeUrl?: string) {
    this.device = device; this.solver = solver; this.mobileGrainFiltering = mobileGrainFiltering
    this.uniform = device.createBuffer({ label: 'Surface view', size: this.data.byteLength, usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST })
    this.lighting = new BedLighting(device, solver, this.uniform)
    this.shadow = new CoconutShadow(device, mobileGrainFiltering, treeUrl)
    this.airborneShadow = new AirborneShadow(device, solver)
    this.post = new SandPostProcess(device, format, format)
    const resolution = solver.resolution
    this.indexCount = (resolution - 1) ** 2 * 6
    const indices = new Uint32Array(this.indexCount)
    let offset = 0
    for (let row = 0; row < resolution - 1; row++) {
      for (let column = 0; column < resolution - 1; column++) {
        const vertex = row * resolution + column
        indices.set([vertex, vertex + resolution, vertex + 1, vertex + 1, vertex + resolution, vertex + resolution + 1], offset)
        offset += 6
      }
    }
    this.indices = device.createBuffer({ label: 'Sand grid topology', size: indices.byteLength, usage: GPUBufferUsage.INDEX | GPUBufferUsage.COPY_DST })
    device.queue.writeBuffer(this.indices, 0, indices)
  }

  async initialize() {
    await Promise.all([this.lighting.initialize(), this.shadow.initialize(), this.airborneShadow.initialize(), this.post.initialize()])
    const module = await checkedShader(this.device, 'Granular surface WGSL', surfaceShader)
    this.pipeline = await this.device.createRenderPipelineAsync({ label: 'Granular sand surface', layout: 'auto',
      vertex: { module, entryPoint: 'vertex' }, fragment: { module, entryPoint: this.mobileGrainFiltering ? 'fragmentMobile' : 'fragment', targets: [{ format: HDR_SCENE_FORMAT }, { format: GLINT_FORMAT }] },
      primitive: { topology: 'triangle-list', cullMode: 'none' },
      depthStencil: { format: 'depth24plus', depthWriteEnabled: true, depthCompare: 'less' },
    })
    this.groups = this.solver.buffers.map((buffer) => this.device.createBindGroup({ layout: this.pipeline.getBindGroupLayout(0), entries: [
      { binding: 0, resource: { buffer: this.uniform } },
      { binding: 1, resource: { buffer } },
      { binding: 3, resource: { buffer: this.lighting.buffer } },
      { binding: 4, resource: this.shadow.sampler },
      { binding: 5, resource: this.shadow.texture.createView() },
      { binding: 6, resource: this.airborneShadow.sampler },
      { binding: 7, resource: this.airborneShadow.texture.createView() },
    ] }))
    this.grainPipeline = await this.device.createRenderPipelineAsync({ label: 'Loose sand grains', layout: 'auto',
      vertex: { module, entryPoint: 'grainVertex' }, fragment: { module, entryPoint: 'grainFragment', targets: [
        { format: HDR_SCENE_FORMAT, blend: {
          color: { srcFactor: 'one', dstFactor: 'one-minus-src-alpha', operation: 'add' },
          alpha: { srcFactor: 'one', dstFactor: 'one-minus-src-alpha', operation: 'add' },
        } },
        { format: GLINT_FORMAT, blend: {
          color: { srcFactor: 'one', dstFactor: 'one', operation: 'add' },
          alpha: { srcFactor: 'one', dstFactor: 'one', operation: 'add' },
        } },
      ] },
      primitive: { topology: 'triangle-list' }, depthStencil: { format: 'depth24plus', depthWriteEnabled: false, depthCompare: 'less' },
    })
    this.grainGroup = this.device.createBindGroup({ layout: this.grainPipeline.getBindGroupLayout(0), entries: [
      { binding: 0, resource: { buffer: this.uniform } },
      { binding: 2, resource: { buffer: this.solver.particles } },
      { binding: 4, resource: this.shadow.sampler },
      { binding: 5, resource: this.shadow.texture.createView() },
    ] })
  }

  resize(width: number, height: number) {
    if (width === this.width && height === this.height) return
    this.depth?.destroy()
    this.width = width; this.height = height
    this.camera.aspect = width / height
    this.depth = this.device.createTexture({ label: 'Surface depth', size: [width, height], format: 'depth24plus', usage: GPUTextureUsage.RENDER_ATTACHMENT })
    this.post.resize(width, height)
    this.shadow.resize(width, height, (x, y) => this.camera.screenToBed(x, y, width, height))
  }

  setDebugMode(mode: string) {
    this.debugMode = ({ final: 0, height: 1, lighting: 2, grains: 3, shadows: 4 } as Record<string, number>)[mode] ?? 0
  }

  encode(encoder: GPUCommandEncoder, target: GPUTextureView, pointer: Stroke, now: number, showPointer = false, waveState: WaveResetState = idleWaveResetState()) {
    if (!this.depth) throw new Error('Renderer needs a nonzero drawing buffer')
    this.shadow.encode(encoder, now)
    this.data.set([
      ...this.camera.eye, this.camera.tanHalfFov,
      ...this.camera.forward, this.camera.aspect,
      ...this.camera.right, 0,
      ...this.camera.up, 0,
      ...LIGHT_DIRECTION, 0,
      this.solver.resolution, SAND.extent, this.width, this.height,
      pointer.to.x, pointer.to.y, pointer.radius, showPointer ? 1 : 0,
      this.shadow.centerX, this.shadow.centerZ, this.shadow.halfWidth, this.shadow.halfHeight,
      this.shadow.opacity, 0, 0, 0,
      this.debugMode, 0, 0, 0,
    ])
    this.device.queue.writeBuffer(this.uniform, 0, this.data)
    if (!waveState.active || !waveState.incoming) this.lighting.encode(encoder, LIGHT_ANGLE)
    if (waveState.justStarted) this.airborneShadow.clear(encoder)
    else if (!waveState.active) this.airborneShadow.encode(encoder, LIGHT_DIRECTION)
    const pass = encoder.beginRenderPass({ label: 'Sand image', colorAttachments: [
      { view: this.post.target, clearValue: { r: 0.1778341, g: 0.12052718, b: 0.06615726, a: 1 }, loadOp: 'clear', storeOp: 'store' },
      { view: this.post.glintTarget, clearValue: { r: 0, g: 0, b: 0, a: 0 }, loadOp: 'clear', storeOp: 'store' },
    ],
      depthStencilAttachment: { view: this.depth.createView(), depthClearValue: 1, depthLoadOp: 'clear', depthStoreOp: 'discard' },
    })
    pass.setPipeline(this.pipeline)
    pass.setBindGroup(0, this.groups[this.solver.stateIndex])
    pass.setIndexBuffer(this.indices, 'uint32')
    pass.drawIndexed(this.indexCount)
    if (!waveState.active && this.debugMode === 0) {
      pass.setPipeline(this.grainPipeline)
      pass.setBindGroup(0, this.grainGroup)
      pass.draw(6, this.solver.particleCount)
    }
    pass.end()
    this.post.setWaveState(waveState, this.camera)
    this.post.encode(encoder, target)
  }

  dispose() { this.lighting.dispose(); this.shadow.dispose(); this.airborneShadow.dispose(); this.post.dispose(); this.uniform.destroy(); this.indices.destroy(); this.depth?.destroy() }
}
