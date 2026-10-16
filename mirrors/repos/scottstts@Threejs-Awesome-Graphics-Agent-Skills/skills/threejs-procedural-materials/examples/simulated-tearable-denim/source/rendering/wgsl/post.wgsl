// Resolve HDR with one tone map and one output encoding.

struct PostU {
  // Reserved grade slots and time (s); grade controls stay zero.
  grade: vec4<f32>,
  // glitch amount, its seed (held over a few frames), unused
  glitch: vec4<f32>,
};

@group(0) @binding(0) var<uniform> F: FrameU;
@group(0) @binding(1) var hdr: texture_2d<f32>;
@group(0) @binding(2) var<uniform> PU: PostU;

struct FsIn {
  @builtin(position) pos: vec4<f32>,
};

@vertex
fn vsFull(@builtin(vertex_index) vi: u32) -> FsIn {
  let p = vec2<f32>(f32((vi << 1u) & 2u), f32(vi & 2u));
  var o: FsIn;
  o.pos = vec4<f32>(p * 2.0 - 1.0, 0.0, 1.0);
  return o;
}

// ACES fitted curve (Narkowicz)
fn aces(x: vec3<f32>) -> vec3<f32> {
  let a = 2.51;
  let b = 0.03;
  let c = 2.43;
  let d = 0.59;
  let e = 0.14;
  return clamp((x * (a * x + b)) / (x * (c * x + d) + e), vec3<f32>(0.0), vec3<f32>(1.0));
}

fn linearToSrgb(c: vec3<f32>) -> vec3<f32> {
  let lo = c * 12.92;
  let hi = 1.055 * pow(c, vec3<f32>(1.0 / 2.4)) - 0.055;
  return select(hi, lo, c <= vec3<f32>(0.0031308));
}

@fragment
fn fsTonemap(in: FsIn) -> @location(0) vec4<f32> {
  let c = textureLoad(hdr, vec2<i32>(in.pos.xy), 0).rgb * F.params.x;
  if (F.keyShape.z > 0.0) { return vec4<f32>(linearToSrgb(c / F.params.x), 1.0); }
  return vec4<f32>(linearToSrgb(aces(c)), 1.0);
}
