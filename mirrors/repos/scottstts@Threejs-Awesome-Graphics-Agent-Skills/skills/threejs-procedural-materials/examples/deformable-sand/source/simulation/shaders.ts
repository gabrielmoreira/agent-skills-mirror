import { SAND } from '../config'
import { fluxLayout } from './flux'

const paramsLayout = `
struct ToolContact {
  start: vec4f,
  end: vec4f,
  motion: vec4f,
}
struct Params {
  grid: vec4f,
  physics: vec4f,
  tool: vec4f,
  contacts: array<ToolContact, ${SAND.maxContacts}>,
}
`

export const simulationShader = `
${fluxLayout}
${paramsLayout}
@group(0) @binding(0) var<uniform> params: Params;
@group(0) @binding(1) var<storage, read> source: array<vec4f>;
@group(0) @binding(2) var<storage, read_write> destination: array<vec4f>;
@group(0) @binding(3) var<storage, read_write> flux: array<Flux>;
@group(0) @binding(4) var<storage, read_write> exchange: array<atomic<i32>>;
@group(0) @binding(5) var<storage, read_write> contactField: array<vec4f>;
@group(0) @binding(6) var<storage, read_write> contactPressure: array<f32>;
@group(0) @binding(7) var<storage, read_write> impactBudget: array<atomic<i32>>;

fn hash(position: vec2f) -> f32 {
  return fract(sin(dot(position, vec2f(127.1, 311.7))) * 43758.5453);
}
fn address(cell: vec2i) -> u32 {
  let bounded = clamp(cell, vec2i(0), vec2i(i32(params.grid.x) - 1));
  return u32(bounded.y) * u32(params.grid.x) + u32(bounded.x);
}
fn location(cell: vec2i) -> vec2f {
  return (vec2f(cell) + 0.5) * params.grid.y - params.grid.z * 0.5;
}
struct ContactSample {
  field: vec4f,
  pressure: f32,
}
fn sampleTool(position: vec2f) -> ContactSample {
  var strongest = 0.0;
  var coverage = 0.0;
  var shell = 0.0;
  var motion = vec2f(0.0);
  var pressure = 0.0;
  for (var index = 0u; index < ${SAND.maxContacts}u; index++) {
    if (f32(index) >= params.tool.x) { break; }
    let tool = params.contacts[index];
    let segment = tool.end.xy - tool.start.xy;
    let along = clamp(dot(position - tool.start.xy, segment) / max(dot(segment, segment), 1e-10), 0.0, 1.0);
    let offset = position - tool.start.xy - along * segment;
    let distance = length(offset) / max(tool.start.z, 1e-7);
    let envelope = max(0.0, 1.0 - distance * distance);
    let localCoverage = envelope * envelope;
    let strength = localCoverage * tool.start.w;
    shell = max(shell, 1.0 - smoothstep(0.9, 1.55, distance));
    if (strength > strongest) {
      strongest = strength;
      coverage = localCoverage;
      motion = tool.motion.xy;
      pressure = tool.start.w;
    }
  }
  return ContactSample(vec4f(coverage, shell, motion), pressure);
}
fn contactAt(cell: vec2i) -> vec4f {
  if (params.tool.x <= 0.0) { return vec4f(0.0); }
  return contactField[address(cell)];
}
fn pressureAt(cell: vec2i) -> f32 {
  if (params.tool.x <= 0.0) { return 0.0; }
  return contactPressure[address(cell)];
}
fn impactResponse(speed: f32) -> f32 {
  return smoothstep(${SAND.impactSpeedStart}, ${SAND.impactSpeedFull}, speed);
}
fn impactCore(contact: vec4f, pressure: f32) -> f32 {
  return impactResponse(length(contact.zw)) * pressure * pow(contact.x, 1.75);
}
fn penetrationFor(contact: vec4f, pressure: f32) -> f32 {
  return contact.x * pressure * params.tool.y + impactCore(contact, pressure) * ${SAND.impactIndentation};
}
@compute @workgroup_size(8, 8)
fn initialize(@builtin(global_invocation_id) invocation: vec3u) {
  if (any(invocation.xy >= vec2u(u32(params.grid.x)))) { return; }
  let cell = vec2i(invocation.xy);
  let position = location(cell);
  let height = params.physics.x + 0.00015 * (hash(vec2f(cell)) - 0.5)
    + 0.0004 * sin(position.x * 31.0 + sin(position.y * 23.0)) * sin(position.y * 27.0);
  destination[address(cell)] = vec4f(height, 0.0, 0.0, 0.0);
}
@compute @workgroup_size(8, 8)
fn contact(@builtin(global_invocation_id) invocation: vec3u) {
  if (any(invocation.xy >= vec2u(u32(params.grid.x)))) { return; }
  let cell = vec2i(invocation.xy);
  let sample = sampleTool(location(cell));
  contactField[address(cell)] = sample.field;
  contactPressure[address(cell)] = sample.pressure;
}
@compute @workgroup_size(8, 8)
fn transport(@builtin(global_invocation_id) invocation: vec3u) {
  if (any(invocation.xy >= vec2u(u32(params.grid.x)))) { return; }
  let cell = vec2i(invocation.xy);
  let position = location(cell);
  let center = source[address(cell)];
  let toolContact = contactAt(cell);
  let toolPressure = pressureAt(cell);
  let penetration = penetrationFor(toolContact, toolPressure);
  let effectiveHeight = center.x + penetration;
  let toolSpeed = length(toolContact.zw);
  let motionDirection = toolContact.zw / max(toolSpeed, 1e-8);
  let speedResponse = toolSpeed / (toolSpeed + 0.35);
  let impact = impactCore(toolContact, toolPressure);
  let centerShell = toolContact.y;
  var outgoing = Flux(vec4f(0.0), vec4f(0.0));
  var escape = Flux(vec4f(0.0), vec4f(0.0));
  var coverageGradient = vec2f(0.0);
  for (var axis = 0u; axis < 8u; axis++) {
    let neighbor = cell + neighbors[axis];
    if (any(neighbor < vec2i(0)) || any(neighbor >= vec2i(i32(params.grid.x)))) { continue; }
    let other = source[address(neighbor)];
    let otherContact = contactAt(neighbor);
    if (axis == 0u) { coverageGradient += vec2f(-otherContact.x * 0.5, 0.0); }
    if (axis == 1u) { coverageGradient += vec2f(otherContact.x * 0.5, 0.0); }
    if (axis == 2u) { coverageGradient += vec2f(0.0, -otherContact.x * 0.5); }
    if (axis == 3u) { coverageGradient += vec2f(0.0, otherContact.x * 0.5); }
    let otherPenetration = penetrationFor(otherContact, pressureAt(neighbor));
    let friction = mix(params.physics.z, params.physics.w, clamp(max(center.y, other.y) * 35.0, 0.0, 1.0));
    let linkLength = select(1.0, 1.41421356, axis >= 4u);
    let weight = select(0.66666667, 0.16666667, axis >= 4u);
    let axisDirection = vec2f(neighbors[axis]) / linkLength;
    let forward = max(0.0, dot(axisDirection, motionDirection));
    let neighborShell = otherContact.y;
    let contactYield = max(toolContact.x, otherContact.x);
    let disturbedShell = max(centerShell, neighborShell);
    let thresholdScale = min(mix(1.0, 0.08, contactYield), mix(1.0, 0.45, disturbedShell));
    let threshold = friction * params.grid.y * linkLength * thresholdScale;
    let excess = max(0.0, effectiveHeight - other.x - otherPenetration - threshold);
    let physicalThreshold = friction * params.grid.y * linkLength * mix(1.0, 0.45, disturbedShell);
    let physicalExcess = max(0.0, center.x - other.x - physicalThreshold);
    let supercritical = smoothstep(params.grid.y * 1.5, params.grid.y * 5.0, physicalExcess);
    let avalancheBoost = 1.0 + supercritical * mix(0.35, 0.85, max(contactYield, disturbedShell));
    var amount = excess * params.grid.w * params.tool.z * weight * avalancheBoost;
    amount *= 1.0 + toolContact.x * speedResponse * forward * 0.55 + impact * forward * 0.95;
    let edge = max(0.0, penetration - otherPenetration) / max(penetration, 1e-7);
    let sideways = toolContact.x * (1.0 - abs(dot(axisDirection, motionDirection))) * 0.06;
    let escapeWeight = (edge + sideways) * (1.0 + speedResponse * forward * 0.8 + impact * forward * 1.35) * weight;
    if (axis < 4u) {
      outgoing.axial[axis] = amount;
      escape.axial[axis] = escapeWeight;
    } else {
      outgoing.diagonal[axis - 4u] = amount;
      escape.diagonal[axis - 4u] = escapeWeight;
    }
  }
  let frontier = clamp(max(0.0, -dot(coverageGradient, motionDirection)) / max(toolContact.x, 0.1), 0.0, 1.0);
  let targetHeight = params.physics.x - penetration;
  let overlap = max(0.0, center.x - targetHeight);
  let existing = totalFlux(outgoing);
  let escapeTotal = totalFlux(escape);
  let evacuationFraction = mix(mix(0.32, 0.46, speedResponse), ${SAND.impactEvacuation}, impact);
  let extra = max(0.0, overlap * evacuationFraction - existing);
  if (extra > 0.0 && escapeTotal > 1e-8) {
    outgoing.axial += escape.axial * (extra / escapeTotal);
    outgoing.diagonal += escape.diagonal * (extra / escapeTotal);
  }
  let total = totalFlux(outgoing);
  let available = max(0.0, center.x - params.physics.y);
  let limiter = min(1.0, available / max(total, 1e-10));
  let limited = Flux(outgoing.axial * limiter, outgoing.diagonal * limiter);
  flux[address(cell)] = limited;
  let remaining = max(0.0, center.x - params.physics.y - totalFlux(limited));
  let desiredEjection = totalFlux(limited) * ${SAND.impactEjectionFraction} * impact * clamp(frontier * 1.4, 0.0, 1.0);
  atomicStore(&impactBudget[address(cell)], i32(round(min(remaining, desiredEjection) * 1e9)));
}
@compute @workgroup_size(8, 8)
fn integrate(@builtin(global_invocation_id) invocation: vec3u) {
  if (any(invocation.xy >= vec2u(u32(params.grid.x)))) { return; }
  let cell = vec2i(invocation.xy);
  let index = address(cell);
  let current = source[index];
  let outgoing = flux[index];
  var incoming = Flux(vec4f(0.0), vec4f(0.0));
  for (var axis = 0u; axis < 8u; axis++) {
    let neighbor = cell + neighbors[axis];
    if (any(neighbor < vec2i(0)) || any(neighbor >= vec2i(i32(params.grid.x)))) { continue; }
    let amount = component(flux[address(neighbor)], axis ^ 1u);
    if (axis < 4u) { incoming.axial[axis] = amount; }
    else { incoming.diagonal[axis - 4u] = amount; }
  }
  let transferred = f32(atomicExchange(&exchange[index], 0)) * 1e-9;
  let height = current.x + totalFlux(incoming) - totalFlux(outgoing) + transferred;
  let moved = totalFlux(incoming) + totalFlux(outgoing);
  let toolContact = contactAt(cell);
  let toolSpeed = length(toolContact.zw);
  let toolPressure = pressureAt(cell);
  let contactActivity = toolContact.x * toolPressure * toolSpeed * 0.004;
  let activity = max(max(current.y * exp(-params.grid.w * 10.0), moved / params.grid.w), contactActivity);
  let transportVelocity = (fluxVector(outgoing) - fluxVector(incoming)) * params.grid.y / max(height * params.grid.w, 1e-7);
  let slipCoupling = 0.38 / (1.0 + toolSpeed * 0.30);
  let toolVelocity = toolContact.zw * toolContact.x * toolPressure * slipCoupling;
  let velocity = transportVelocity + toolVelocity;
  destination[index] = vec4f(height, activity, mix(current.zw, velocity, 0.4));
}
`;

export const particleShader = `
${fluxLayout}
${paramsLayout}
struct Grain { position: vec4f, velocity: vec4f }
@group(0) @binding(0) var<uniform> params: Params;
@group(0) @binding(1) var<storage, read> bed: array<vec4f>;
@group(0) @binding(2) var<storage, read> flux: array<Flux>;
@group(0) @binding(3) var<storage, read_write> grains: array<Grain>;
@group(0) @binding(4) var<storage, read_write> exchange: array<atomic<i32>>;
@group(0) @binding(5) var<storage, read> contactField: array<vec4f>;
@group(0) @binding(6) var<storage, read> contactPressure: array<f32>;
@group(0) @binding(7) var<storage, read_write> impactBudget: array<atomic<i32>>;
fn random(seed: u32) -> f32 {
  var value = seed * 747796405u + 2891336453u;
  value = ((value >> ((value >> 28u) + 4u)) ^ value) * 277803737u;
  return f32((value >> 22u) ^ value) / 4294967295.0;
}
fn address(position: vec2f) -> u32 {
  let cell = vec2u(clamp((position / params.grid.z + 0.5) * params.grid.x, vec2f(0.0), vec2f(params.grid.x - 1.0)));
  return cell.y * u32(params.grid.x) + cell.x;
}

fn impactResponse(speed: f32) -> f32 {
  return smoothstep(${SAND.impactSpeedStart}, ${SAND.impactSpeedFull}, speed);
}
fn claimImpactMass(cell: u32, requestedMass: f32) -> f32 {
  let requestedUnits = max(1, i32(round(requestedMass * 1e9)));
  let previous = atomicSub(&impactBudget[cell], requestedUnits);
  if (previous <= 0) {
    atomicAdd(&impactBudget[cell], requestedUnits);
    return 0.0;
  }
  let claimed = min(previous, requestedUnits);
  if (claimed < requestedUnits) { atomicAdd(&impactBudget[cell], requestedUnits - claimed); }
  return f32(claimed) * 1e-9;
}
fn cellCenter(cell: u32) -> vec2f {
  return (vec2f(f32(cell % u32(params.grid.x)), f32(cell / u32(params.grid.x))) + 0.5) * params.grid.y - params.grid.z * 0.5;
}
fn heightAt(cell: vec2i) -> f32 {
  let bounded = vec2u(clamp(cell, vec2i(0), vec2i(i32(params.grid.x) - 1)));
  return bed[bounded.y * u32(params.grid.x) + bounded.x].x;
}
fn contactAt(position: vec2f) -> vec3f {
  let coordinate = (position / params.grid.z + 0.5) * params.grid.x - 0.5;
  let cell = vec2i(floor(coordinate));
  let blend = fract(coordinate);
  let lowerLeft = heightAt(cell);
  let lowerRight = heightAt(cell + vec2i(1, 0));
  let upperLeft = heightAt(cell + vec2i(0, 1));
  let upperRight = heightAt(cell + vec2i(1, 1));
  if (blend.x + blend.y <= 1.0) {
    let gradient = vec2f(lowerRight - lowerLeft, upperLeft - lowerLeft);
    return vec3f(lowerLeft + dot(gradient, blend), gradient / params.grid.y);
  }
  let gradient = vec2f(upperRight - upperLeft, upperRight - lowerRight);
  return vec3f(upperRight + dot(gradient, blend - 1.0), gradient / params.grid.y);
}
@compute @workgroup_size(64)
fn animate(@builtin(global_invocation_id) invocation: vec3u) {
  let index = invocation.x;
  if (index >= arrayLength(&grains)) { return; }
  var grain = grains[index];
  if (grain.position.w > 0.0) {
    let impactGrain = grain.velocity.w < 0.0;
    var age = abs(grain.velocity.w);
    if (impactGrain) {
      let radiusScale = pow(max(grain.position.w, 1e-9) / ${SAND.airborneReferenceMass}, 1.0 / 3.0);
      let dragCoefficient = 2.35 / max(radiusScale, 0.55);
      let speed = length(grain.velocity.xyz);
      let drag = max(0.0, 1.0 - dragCoefficient * speed * params.grid.w);
      grain.velocity = vec4f(grain.velocity.xyz * drag, grain.velocity.w);
    }
    grain.velocity.y -= 9.81 * params.grid.w;
    grain.position = vec4f(grain.position.xyz + grain.velocity.xyz * params.grid.w, grain.position.w);
    age += params.grid.w;
    grain.velocity.w = select(age, -age, impactGrain);
    let limit = params.grid.z * 0.5 - params.grid.y;
    grain.position.x = clamp(grain.position.x, -limit, limit);
    grain.position.z = clamp(grain.position.z, -limit, limit);
    let cell = address(grain.position.xz);
    let surface = contactAt(grain.position.xz);
    if (grain.position.y <= surface.x + 0.00014) {
      let normal = normalize(vec3f(-surface.y, 1.0, -surface.z));
      let normalSpeed = dot(grain.velocity.xyz, normal);
      if (normalSpeed < -0.08 && age < 0.22) {
        grain.position.y = surface.x + 0.00018;
        let tangent = grain.velocity.xyz - normal * normalSpeed;
        let friction = max(0.0, 1.0 - params.physics.w * 1.22 * abs(normalSpeed) / max(length(tangent), 1e-7));
        grain.velocity = vec4f(tangent * friction - normal * normalSpeed * 0.22, grain.velocity.w);
      } else {
        atomicAdd(&exchange[cell], i32(round(grain.position.w * 1e9)));
        grain.position.w = 0.0;
        grain.velocity.w = 0.0;
      }
    }
  } else {
    grain.velocity.w += 1.0;
    let seed = index * 991u + u32(grain.velocity.w);
    var launched = false;
    let contactCount = u32(params.tool.x);
    if (contactCount > 0u) {
      let contactIndex = index % contactCount;
      let tool = params.contacts[contactIndex];
      let toolSpeed = length(tool.motion.xy);
      let toolImpact = impactResponse(toolSpeed);
      if (toolImpact > 0.0) {
        let direction = tool.motion.xy / max(toolSpeed, 1e-8);
        let side = vec2f(-direction.y, direction.x);
        let candidate = index / contactCount;
        let sampleIndex = candidate % 256u;
        let sampleCycle = candidate / 256u;
        let column = sampleIndex % 16u;
        let row = sampleIndex / 16u;
        let forward = (mix(-0.08, 1.08, (f32(column) + random(seed + sampleCycle * 17u + 3u)) / 16.0)) * tool.start.z;
        let lateral = (mix(-1.05, 1.05, (f32(row) + random(seed + sampleCycle * 23u + 11u)) / 16.0)) * tool.start.z;
        let candidatePosition = tool.end.xy + direction * forward + side * lateral;
        let cell = address(candidatePosition);
        let localContact = contactField[cell];
        let localSpeed = length(localContact.zw);
        let localImpact = impactResponse(localSpeed) * contactPressure[cell] * pow(localContact.x, 1.75);
        let requestedMass = mix(${SAND.impactParticleMassMin}, ${SAND.impactParticleMassMax}, random(seed + 13u));
        var mass = 0.0;
        if (localImpact > 0.0) { mass = claimImpactMass(cell, requestedMass); }
        if (mass > 0.0) {
          let surfacePosition = cellCenter(cell);
          let surface = contactAt(surfacePosition);
          let motionDirection = localContact.zw / max(localSpeed, 1e-8);
          let transport = fluxVector(flux[cell]);
          let transportDirection = transport / max(length(transport), 1e-9);
          let launchDirection = normalize(motionDirection + transportDirection * 0.28);
          let launchSide = vec2f(-launchDirection.y, launchDirection.x);
          let spread = (random(seed + 31u) - 0.5) * localSpeed * 0.26;
          let horizontalSpeed = localSpeed * (0.42 + random(seed + 5u) * 0.38);
          let horizontal = launchDirection * horizontalSpeed + launchSide * spread;
          let uphill = max(0.0, dot(surface.yz, motionDirection));
          let loft = pow(random(seed + 7u), 2.0);
          let rareBurst = pow(random(seed + 41u), 9.0);
          let lift = 0.12 + localSpeed * (0.16 + loft * 0.45 + rareBurst * 0.62 + min(uphill, 0.8) * 0.30);
          grain.position = vec4f(surfacePosition.x, surface.x + 0.0003, surfacePosition.y, mass);
          grain.velocity = vec4f(horizontal.x, lift, horizontal.y, -1e-6);
          atomicSub(&exchange[cell], i32(round(mass * 1e9)));
          launched = true;
        }
      }
    }
    if (!launched) {
      let stride = max(1u, u32(params.grid.x * params.grid.x) / arrayLength(&grains));
      let cell = min(index * stride + u32(grain.velocity.w) % stride, arrayLength(&bed) - 1u);
      let flow = flux[cell];
      let moved = totalFlux(flow);
      let reserve = bed[cell].x - moved - params.physics.y;
      let bedVelocity = bed[cell].zw;
      let speed = length(bedVelocity);
      let agitation = smoothstep(0.055, 0.24, speed);
      let sourceMoved = max(moved, bed[cell].y * params.grid.w * 0.35);
      let mass = mix(0.0000025, 0.0000055, random(seed + 13u));
      let launchMass = sourceMoved * f32(stride) * agitation * 0.004;
      let launchChance = min(1.0, launchMass / mass);
      let contactSpeed = length(contactField[cell].zw);
      let activeImpactContact = params.tool.x > 0.0 && contactField[cell].x > 0.001 && impactResponse(contactSpeed) > 0.0;
      if (!activeImpactContact && reserve > mass * 1.2 && random(seed) < launchChance) {
        let position = cellCenter(cell);
        let transport = fluxVector(flow);
        let direction = select(transport / max(length(transport), 1e-9), bedVelocity / max(speed, 1e-9), speed > 0.01);
        let side = vec2f(-direction.y, direction.x);
        let scatter = (random(seed + 31u) - 0.5) * (0.02 + speed * 0.12);
        let horizontal = bedVelocity * (0.68 + random(seed + 5u) * 0.22) + direction * (0.018 + speed * 0.12) + side * scatter;
        let lift = 0.018 + sqrt(max(speed, 0.0)) * (0.16 + random(seed + 7u) * 0.055);
        grain.position = vec4f(position.x, bed[cell].x + 0.0003, position.y, mass);
        grain.velocity = vec4f(horizontal.x, lift, horizontal.y, 0.0);
        atomicSub(&exchange[cell], i32(round(mass * 1e9)));
      }
    }
  }
  grains[index] = grain;
}
`;
