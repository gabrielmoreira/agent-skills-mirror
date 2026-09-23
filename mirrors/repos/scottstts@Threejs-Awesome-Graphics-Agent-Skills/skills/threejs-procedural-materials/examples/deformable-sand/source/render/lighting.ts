import { checkedShader } from '../platform/shader'
import type { SandSolver } from '../simulation/solver'

export const lightingShader = `
struct View { eye: vec4f, forward: vec4f, right: vec4f, up: vec4f, light: vec4f, grid: vec4f, pointer: vec4f }
@group(0) @binding(0) var<uniform> view: View;
@group(0) @binding(1) var<storage, read> bed: array<vec4f>;
@group(0) @binding(2) var<storage, read_write> lighting: array<vec4f>;
fn heightAt(cell: vec2i) -> f32 {
  let bounded = vec2u(clamp(cell, vec2i(0), vec2i(i32(view.grid.x) - 1)));
  return bed[bounded.y * u32(view.grid.x) + bounded.x].x;
}
fn sampleHeight(coordinate: vec2f) -> f32 {
  let cell = vec2i(floor(coordinate));
  let blend = fract(coordinate);
  return mix(mix(heightAt(cell), heightAt(cell + vec2i(1, 0)), blend.x),
    mix(heightAt(cell + vec2i(0, 1)), heightAt(cell + vec2i(1, 1)), blend.x), blend.y);
}
@compute @workgroup_size(8, 8)
fn illuminate(@builtin(global_invocation_id) invocation: vec3u) {
  if (any(invocation.xy >= vec2u(u32(view.grid.x)))) { return; }
  let cell = vec2i(invocation.xy);
  let coordinate = vec2f(cell);
  let spacing = view.grid.y / view.grid.x;
  let height = heightAt(cell);
  let gradient = vec2f(heightAt(cell + vec2i(1, 0)) - heightAt(cell - vec2i(1, 0)),
    heightAt(cell + vec2i(0, 1)) - heightAt(cell - vec2i(0, 1))) / (2.0 * spacing);
  let light = normalize(view.light.xyz);
  var visibility = 1.0;
  for (var sampleIndex = 1; sampleIndex <= 14; sampleIndex++) {
    let distance = spacing * (0.8 * f32(sampleIndex) + 0.38 * f32(sampleIndex * sampleIndex));
    let probe = coordinate + light.xz * distance / spacing;
    if (any(probe < vec2f(0.0)) || any(probe > vec2f(view.grid.x - 1.0))) { break; }
    let blocker = sampleHeight(probe) - height - light.y * distance;
    visibility = min(visibility, 1.0 - smoothstep(-0.0002 - distance * 0.035, 0.0004 + distance * 0.045, blocker));
  }
  let directions = array<vec2f, 8>(vec2f(1.0, 0.0), vec2f(-1.0, 0.0), vec2f(0.0, 1.0), vec2f(0.0, -1.0),
    vec2f(0.70710678, 0.70710678), vec2f(-0.70710678, -0.70710678),
    vec2f(0.70710678, -0.70710678), vec2f(-0.70710678, 0.70710678));
  let radii = array<f32, 6>(1.0, 2.0, 4.0, 8.0, 16.0, 32.0);
  var obscured = 0.0;
  for (var axis = 0u; axis < 8u; axis++) {
    let direction = directions[axis];
    let tangentAngle = atan(dot(gradient, direction));
    var horizon = 0.0;
    for (var sampleIndex = 0u; sampleIndex < 6u; sampleIndex++) {
      let distance = radii[sampleIndex] * spacing;
      let probe = coordinate + direction * radii[sampleIndex];
      if (any(probe < vec2f(0.0)) || any(probe > vec2f(view.grid.x - 1.0))) { break; }
      let angle = atan((sampleHeight(probe) - height - 0.00008) / distance);
      horizon = max(horizon, angle - tangentAngle);
    }
    let blocked = sin(min(horizon, 1.57079633));
    obscured += blocked * blocked;
  }
  lighting[invocation.y * u32(view.grid.x) + invocation.x] = vec4f(visibility, clamp(1.0 - obscured / 8.0, 0.0, 1.0), 0.0, 0.0);
}
`

export class BedLighting {
  readonly buffer: GPUBuffer
  private pipeline!: GPUComputePipeline
  private groups: GPUBindGroup[] = []
  private revision = -1
  private angle = NaN

  private readonly device: GPUDevice
  private readonly solver: SandSolver
  private readonly uniform: GPUBuffer

  constructor(device: GPUDevice, solver: SandSolver, uniform: GPUBuffer) {
    this.device = device; this.solver = solver; this.uniform = uniform
    this.buffer = device.createBuffer({ label: 'Bed-space illumination', size: solver.byteLength, usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_SRC })
  }

  async initialize() {
    const module = await checkedShader(this.device, 'Bed horizon lighting WGSL', lightingShader)
    this.pipeline = await this.device.createComputePipelineAsync({ layout: 'auto', compute: { module, entryPoint: 'illuminate' } })
    this.groups = this.solver.buffers.map((buffer) => this.device.createBindGroup({ layout: this.pipeline.getBindGroupLayout(0), entries: [
      { binding: 0, resource: { buffer: this.uniform } }, { binding: 1, resource: { buffer } },
      { binding: 2, resource: { buffer: this.buffer } },
    ] }))
  }

  encode(encoder: GPUCommandEncoder, angle: number) {
    if (this.revision === this.solver.revision && this.angle === angle) return
    const pass = encoder.beginComputePass({ label: 'Bed horizon lighting' })
    pass.setPipeline(this.pipeline)
    pass.setBindGroup(0, this.groups[this.solver.stateIndex])
    pass.dispatchWorkgroups(Math.ceil(this.solver.resolution / 8), Math.ceil(this.solver.resolution / 8))
    pass.end()
    this.revision = this.solver.revision
    this.angle = angle
  }

  dispose() { this.buffer.destroy() }
}
