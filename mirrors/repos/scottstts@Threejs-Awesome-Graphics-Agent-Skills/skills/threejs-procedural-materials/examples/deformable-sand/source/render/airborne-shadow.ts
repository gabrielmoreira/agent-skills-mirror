import { SAND } from '../config'
import { checkedShader } from '../platform/shader'
import type { SandSolver } from '../simulation/solver'

const airborneShadowShader = `
struct ShadowParams {
  light: vec4f,
  bed: vec4f,
}
struct Grain { position: vec4f, velocity: vec4f }
@group(0) @binding(0) var<uniform> params: ShadowParams;
@group(0) @binding(1) var<storage, read> grains: array<Grain>;

struct ShadowVertexOutput {
  @builtin(position) clip: vec4f,
  @location(0) local: vec2f,
  @location(1) density: f32,
}

@vertex fn vertex(@builtin(vertex_index) vertex: u32, @builtin(instance_index) instance: u32) -> ShadowVertexOutput {
  let corners = array<vec2f, 6>(
    vec2f(-1.0, -1.0), vec2f(1.0, -1.0), vec2f(-1.0, 1.0),
    vec2f(-1.0, 1.0), vec2f(1.0, -1.0), vec2f(1.0, 1.0));
  let grain = grains[instance];
  var output: ShadowVertexOutput;
  if (grain.position.w <= 0.0) {
    output.clip = vec4f(2.0, 2.0, 2.0, 1.0);
    output.local = vec2f(0.0);
    output.density = 0.0;
    return output;
  }

  let light = normalize(params.light.xyz);
  let height = max(0.0, grain.position.y - params.bed.x);
  let shadowCenter = grain.position.xz - light.xz * (height / max(light.y, 0.08));
  let physicalRadius = ${SAND.airborneGrainRadius} * pow(max(grain.position.w, 1e-9) / ${SAND.airborneReferenceMass}, 1.0 / 3.0);
  let sunPenumbra = height * 0.00471;
  let physicalFootprint = physicalRadius + sunPenumbra;
  let texel = params.bed.y / params.bed.z;
  let opticalRadius = max(physicalFootprint, texel * 0.90);
  let areaRatio = physicalFootprint * physicalFootprint / max(opticalRadius * opticalRadius, 1e-12);
  let density = min(0.26, areaRatio * 7.0);
  let offset = corners[vertex] * opticalRadius;
  let world = shadowCenter + offset;

  output.clip = vec4f(world.x / (params.bed.y * 0.5), world.y / (params.bed.y * 0.5), 0.0, 1.0);
  output.local = corners[vertex];
  output.density = density;
  return output;
}

@fragment fn fragment(input: ShadowVertexOutput) -> @location(0) vec4f {
  let squared = dot(input.local, input.local);
  if (squared > 1.0) { discard; }
  let profile = 1.0 - smoothstep(0.08, 1.0, squared);
  let opticalDepth = input.density * profile;
  return vec4f(opticalDepth, 0.0, 0.0, opticalDepth);
}
`

export class AirborneShadow {
  readonly texture: GPUTexture
  readonly sampler: GPUSampler
  private readonly uniform: GPUBuffer
  private readonly data = new Float32Array(8)
  private pipeline!: GPURenderPipeline
  private group!: GPUBindGroup
  private readonly device: GPUDevice
  private readonly solver: SandSolver

  constructor(device: GPUDevice, solver: SandSolver) {
    this.device = device
    this.solver = solver
    this.texture = device.createTexture({
      label: 'Airborne sand optical depth',
      size: [SAND.airborneShadowResolution, SAND.airborneShadowResolution],
      format: 'rgba8unorm',
      usage: GPUTextureUsage.RENDER_ATTACHMENT | GPUTextureUsage.TEXTURE_BINDING | GPUTextureUsage.COPY_SRC,
    })
    this.sampler = device.createSampler({ minFilter: 'linear', magFilter: 'linear', addressModeU: 'clamp-to-edge', addressModeV: 'clamp-to-edge' })
    this.uniform = device.createBuffer({ label: 'Airborne shadow parameters', size: this.data.byteLength, usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST })
  }

  async initialize() {
    const module = await checkedShader(this.device, 'Airborne sand shadow WGSL', airborneShadowShader)
    this.pipeline = await this.device.createRenderPipelineAsync({
      label: 'Airborne sand optical-depth shadow',
      layout: 'auto',
      vertex: { module, entryPoint: 'vertex' },
      fragment: {
        module,
        entryPoint: 'fragment',
        targets: [{
          format: 'rgba8unorm',
          blend: {
            color: { srcFactor: 'one', dstFactor: 'one', operation: 'add' },
            alpha: { srcFactor: 'one', dstFactor: 'one', operation: 'add' },
          },
        }],
      },
      primitive: { topology: 'triangle-list' },
    })
    this.group = this.device.createBindGroup({
      layout: this.pipeline.getBindGroupLayout(0),
      entries: [
        { binding: 0, resource: { buffer: this.uniform } },
        { binding: 1, resource: { buffer: this.solver.particles } },
      ],
    })
  }

  encode(encoder: GPUCommandEncoder, light: readonly [number, number, number]) {
    this.data.set([
      light[0], light[1], light[2], 0,
      SAND.depth, SAND.extent, SAND.airborneShadowResolution, 0,
    ])
    this.device.queue.writeBuffer(this.uniform, 0, this.data)
    const pass = encoder.beginRenderPass({
      label: 'Airborne sand shadow',
      colorAttachments: [{
        view: this.texture.createView(),
        clearValue: { r: 0, g: 0, b: 0, a: 0 },
        loadOp: 'clear',
        storeOp: 'store',
      }],
    })
    pass.setPipeline(this.pipeline)
    pass.setBindGroup(0, this.group)
    pass.draw(6, this.solver.particleCount)
    pass.end()
  }

  clear(encoder: GPUCommandEncoder) {
    const pass = encoder.beginRenderPass({
      label: 'Clear airborne sand shadow',
      colorAttachments: [{
        view: this.texture.createView(),
        clearValue: { r: 0, g: 0, b: 0, a: 0 },
        loadOp: 'clear',
        storeOp: 'store',
      }],
    })
    pass.end()
  }

  dispose() {
    this.texture.destroy()
    this.uniform.destroy()
  }
}
