import * as THREE from "three/webgpu";

const N = 96;
const M = 96;
const COUNT = N * M;
const SIZE = 1.46;
const SPACING = SIZE / (N - 1);
const RHO = 0.20;            // kg / m^2, medium cotton
const THICKNESS = 0.0004;    // m, membrane thickness used in the energy
const ET = 8.0e6;            // retained for rest-data compatibility; yarn length is enforced geometrically below
const EC = 8.0e2;            // Pa, compression (buckling)
const ES = 1.2e4;            // Pa, base woven shear response; low initially, rises as yarns lock
const BEND = 9.0e-5;         // N·m, linen-scale flexural rigidity without rubber-sheet stiffness
const SPHERE_R = 0.30;
const SPHERE_GAP = 0.0016;   // keep the rasterized sheet off the stone and hide sub-pixel interpenetration
const GROUND_Y = 0.0010;     // cloth centerline clearance above the visible cove
const COVE_Z_JOIN = -0.05;
const COVE_RADIUS = 1.20;
const COVE_Z_WALL = COVE_Z_JOIN - COVE_RADIUS;
const SELF_THICK = 0.0024;   // 2.4 mm two-sided contact shell; prevents rendered layers becoming depth-buffer coplanar
const CELL = SPACING * 1.5;
const MU_SPHERE = 0.20;
const MU_GROUND = 0.32;
const AIR_N = 1.15;
const AIR_T = 0.12;
const DAMP = 0.16;
const VMAX = 4.0;
const HASH = 131072;         // power of two
const SLOT = 32;
const MAX_SUB = 10;
const SCALE = 1000000.0;
// Fabric microstructure. A plain weave baked once: yarn cross-section as a
// height field, normals from that height, roughness high in the valleys,
// albedo varying per yarn. This is the shading detail the simulation
// resolution is not meant to carry.
// ---------------------------------------------------------------------------

function hash2(i, j) {
  let n = Math.imul(i, 374761393) + Math.imul(j, 668265263);
  n = Math.imul(n ^ (n >>> 13), 1274126177);
  return ((n ^ (n >>> 16)) >>> 0) / 4294967295;
}

function makeFabric() {
  const W = 2048;
  const YARNS = 72;
  const pitch = SIZE / YARNS;          // metres per yarn
  const yarnR = pitch * 0.34;
  const height = new Float32Array(W * W);

  function sampleH(u, v) {
    u = u - Math.floor(u);
    v = v - Math.floor(v);
    const fu = u * YARNS, fv = v * YARNS;
    const iu = Math.floor(fu), iv = Math.floor(fv);
    const au = fu - iu, av = fv - iv;
    const warpTop = ((iu + iv) & 1) === 0;
    const slubW = 1 + (hash2(iu, 3) - 0.5) * 0.18;
    const slubF = 1 + (hash2(7, iv) - 0.5) * 0.18;
    function profile(t, rad) {
      const d = (t - 0.5) * pitch;
      const r = yarnR * rad;
      if (Math.abs(d) >= r) return 0;
      const x = d / r;
      return Math.sqrt(Math.max(0, 1 - x * x)) * r;
    }
    const hw = profile(au, slubW);
    const hf = profile(av, slubF);
    // The buried yarn still contributes a low ridge so the cloth is not flat between crowns.
    const h = warpTop ? Math.max(hw, hf * 0.28) : Math.max(hf, hw * 0.28);
    const fiber = (hash2(iu * 13 + Math.floor(au * 48), iv * 17 + Math.floor(av * 48)) - 0.5) * yarnR * 0.08;
    return h + fiber;
  }

  for (let y = 0; y < W; y++) {
    const v = 1 - (y + 0.5) / W;
    for (let x = 0; x < W; x++) {
      const u = (x + 0.5) / W;
      height[y * W + x] = sampleH(u, v);
    }
  }

  const albedo = document.createElement('canvas');
  const normal = document.createElement('canvas');
  const rough = document.createElement('canvas');
  const ao = document.createElement('canvas');
  for (const c of [albedo, normal, rough, ao]) { c.width = W; c.height = W; }
  const ia = albedo.getContext('2d', { willReadFrequently: true }).createImageData(W, W);
  const inrm = normal.getContext('2d', { willReadFrequently: true }).createImageData(W, W);
  const ir = rough.getContext('2d', { willReadFrequently: true }).createImageData(W, W);
  const iao = ao.getContext('2d', { willReadFrequently: true }).createImageData(W, W);
  const du = 1 / W;

  for (let y = 0; y < W; y++) {
    for (let x = 0; x < W; x++) {
      const xm = (x + W - 1) % W, xp = (x + 1) % W;
      const ym = (y + W - 1) % W, yp = (y + 1) % W;
      const hL = height[y * W + xm], hR = height[y * W + xp];
      const hD = height[ym * W + x], hU = height[yp * W + x];
      // Canvas +y is down; v increases upward, so d/dv flips the image-y difference.
      const dHdX = (hR - hL) / (2 * du * SIZE);
      const dHdZ = (hD - hU) / (2 * du * SIZE);
      let nx = -dHdX, ny = -dHdZ, nz = 1;
      const nl = Math.hypot(nx, ny, nz);
      nx /= nl; ny /= nl; nz /= nl;
      const h = height[y * W + x];
      const u = (x + 0.5) / W;
      const v = 1 - (y + 0.5) / W;
      const fu = u * YARNS, fv = v * YARNS;
      const iu = Math.floor(fu), iv = Math.floor(fv);
      const warpTop = ((iu + iv) & 1) === 0;
      const nA = hash2(iu, iv);
      const nB = hash2(iu + 19, iv + 5);
      // Flax, slightly different dye on warp and weft, plus a slow unevenness.
      const slow = hash2(iu >> 3, iv >> 3);
      let r = warpTop ? 184 : 168;
      let g = warpTop ? 154 : 140;
      let b = warpTop ? 116 : 104;
      const dye = (nA - 0.5) * 18 + (slow - 0.5) * 14;
      r = Math.min(255, Math.max(0, r + dye));
      g = Math.min(255, Math.max(0, g + dye * 0.85));
      b = Math.min(255, Math.max(0, b + dye * 0.55));
      const hem = Math.min(u, 1 - u, v, 1 - v);
      const hemDark = hem < 0.012 ? 0.82 : 1;
      const shade = 0.72 + 0.28 * Math.min(1, h / (yarnR * 0.95));
      const o = (y * W + x) * 4;
      ia.data[o] = r * shade * hemDark;
      ia.data[o + 1] = g * shade * hemDark;
      ia.data[o + 2] = b * shade * hemDark;
      ia.data[o + 3] = 255;
      inrm.data[o] = (nx * 0.5 + 0.5) * 255;
      inrm.data[o + 1] = (ny * 0.5 + 0.5) * 255;
      inrm.data[o + 2] = (nz * 0.5 + 0.5) * 255;
      inrm.data[o + 3] = 255;
      const crown = Math.min(1, h / (yarnR * 0.9));
      const roughness = 0.93 - crown * 0.34 + (nB - 0.5) * 0.04;
      const rv = Math.min(255, Math.max(0, roughness * 255));
      ir.data[o] = ir.data[o + 1] = ir.data[o + 2] = rv;
      ir.data[o + 3] = 255;
      const aov = Math.min(255, Math.max(0, (0.48 + 0.52 * crown) * 255));
      iao.data[o] = iao.data[o + 1] = iao.data[o + 2] = aov;
      iao.data[o + 3] = 255;
    }
  }
  function upload(canvas, image, colorSpace) {
    canvas.getContext('2d').putImageData(image, 0, 0);
    const tex = new THREE.CanvasTexture(canvas);
    tex.colorSpace = colorSpace;
    tex.wrapS = tex.wrapT = THREE.ClampToEdgeWrapping;
    tex.anisotropy = 8;
    tex.generateMipmaps = true;
    tex.minFilter = THREE.LinearMipmapLinearFilter;
    tex.needsUpdate = true;
    return tex;
  }
  return {
    albedo: upload(albedo, ia, THREE.SRGBColorSpace),
    normal: upload(normal, inrm, THREE.NoColorSpace),
    rough: upload(rough, ir, THREE.NoColorSpace),
    ao: upload(ao, iao, THREE.NoColorSpace),
  };
}

function f2u(f) {
  const a = new Float32Array([f]);
  return new Uint32Array(a.buffer)[0];
}

function buildConstraints() {
  const vid = (i, j) => j * N + i;
  const rest = new Float32Array(COUNT * 3);
  const pos = new Float32Array(COUNT * 4);
  // Sit the sheet just above the top of the sphere. Starting at SPHERE_R
  // sliced the cloth through the middle of the ball.
  const y0 = SPHERE_R * 2.0 + 0.02;
  for (let j = 0; j < M; j++) {
    for (let i = 0; i < N; i++) {
      const id = vid(i, j);
      const edgeX = (i === 0 || i === N - 1) ? 0.5 : 1;
      const edgeZ = (j === 0 || j === M - 1) ? 0.5 : 1;
      const mass = RHO * SPACING * SPACING * edgeX * edgeZ;
      const x = (i / (N - 1) - 0.5) * SIZE + 0.012;
      const z = (j / (M - 1) - 0.5) * SIZE - 0.008;
      rest[id * 3] = x;
      rest[id * 3 + 1] = y0;
      rest[id * 3 + 2] = z;
      pos[id * 4] = x;
      pos[id * 4 + 1] = y0 + (hash2(i, j) - 0.5) * SPACING * 0.05;
      pos[id * 4 + 2] = z;
      pos[id * 4 + 3] = 1 / mass;
    }
  }
  function invDm(i0, i1, i2) {
    // Rest coordinates must follow the SAME warp (+X) and weft (+Z) on both
    // halves of a quad. A per-triangle edge-aligned frame rotated the second
    // triangle by 45 degrees, turning yarn shear into ignored diagonal strain.
    const x1 = rest[i1 * 3] - rest[i0 * 3];
    const z1 = rest[i1 * 3 + 2] - rest[i0 * 3 + 2];
    const x2 = rest[i2 * 3] - rest[i0 * 3];
    const z2 = rest[i2 * 3 + 2] - rest[i0 * 3 + 2];
    const det = x1 * z2 - x2 * z1;
    return {
      d: [z2 / det, -x2 / det, -z1 / det, x1 / det],
      area: 0.5 * Math.abs(det),
    };
  }
  const cons = [];
  const tris = [];
  for (let j = 0; j < M - 1; j++) {
    for (let i = 0; i < N - 1; i++) {
      const a = vid(i, j), b = vid(i + 1, j), c = vid(i + 1, j + 1), d = vid(i, j + 1);
      // +Y winding: (a, d, b), (b, d, c)
      for (const t of [[a, d, b], [b, d, c]]) {
        const dm = invDm(t[0], t[1], t[2]);
        const alphaBase = 1 / (THICKNESS * dm.area);
        cons.push(t[0], t[1], t[2], 0);
        cons.push(f2u(dm.d[0]), f2u(dm.d[1]), f2u(dm.d[2]), f2u(dm.d[3]));
        cons.push(f2u(alphaBase / ET), f2u(alphaBase / EC), f2u(alphaBase / ES), 0);
        tris.push(t);
      }
    }
  }
  const triCount = tris.length;
  const bendBase = cons.length;
  let bendCount = 0;
  function addBend(p0, p1, p2) {
    // A strip of width SPACING bends along each warp/weft yarn. Its dual
    // segment length is also SPACING, giving angular stiffness BEND.
    cons.push(p0, p1, p2, p1);
    cons.push(f2u(0), f2u(1 / BEND), f2u(SPACING), 0);
    bendCount++;
  }
  for (let j = 0; j < M; j++) for (let i = 1; i < N - 1; i++)
    addBend(vid(i - 1, j), vid(i, j), vid(i + 1, j));
  for (let j = 1; j < M - 1; j++) for (let i = 0; i < N; i++)
    addBend(vid(i, j - 1), vid(i, j), vid(i, j + 1));
  const edgeBase = cons.length;
  let edgeCount = 0;
  function addEdge(a, b) {
    cons.push(a, b, 0, 0);
    edgeCount++;
  }
  for (let j = 0; j < M; j++) for (let i = 0; i < N - 1; i++) addEdge(vid(i, j), vid(i + 1, j));
  for (let j = 0; j < M - 1; j++) for (let i = 0; i < N; i++) addEdge(vid(i, j), vid(i, j + 1));

  const renderPos = new Float32Array(COUNT * 3);
  const renderN = new Float32Array(COUNT * 3);
  const renderT = new Float32Array(COUNT * 4);
  const uvs = new Float32Array(COUNT * 2);
  const indices = new Uint32Array(triCount * 3);
  for (let i = 0; i < COUNT; i++) {
    renderPos[i * 3] = pos[i * 4];
    renderPos[i * 3 + 1] = pos[i * 4 + 1];
    renderPos[i * 3 + 2] = pos[i * 4 + 2];
    renderN[i * 3 + 1] = 1;
    renderT[i * 4] = 1;
    renderT[i * 4 + 3] = 1;
    const ix = i % N, iz = (i / N) | 0;
    uvs[i * 2] = ix / (N - 1);
    uvs[i * 2 + 1] = iz / (M - 1);
  }
  for (let t = 0; t < triCount; t++) {
    indices[t * 3] = tris[t][0];
    indices[t * 3 + 1] = tris[t][1];
    indices[t * 3 + 2] = tris[t][2];
  }
  return {
    pos, cons: new Uint32Array(cons), triCount, bendCount, edgeCount, bendBase, edgeBase,
    renderPos, renderN, renderT, uvs, indices,
  };
}

function wgsl() {
  return /* wgsl */ `
diagnostic(off, derivative_uniformity);

const SCALE: f32 = ${SCALE};
const HASH: u32 = ${HASH}u;
const SLOT: u32 = ${SLOT}u;
const STRUCTURAL_RELAX: f32 = ${STRUCTURAL_RELAX};
const SHEAR_FREE: f32 = ${SHEAR_FREE};
const WAKE_BIT: i32 = 16777216;

@group(0) @binding(0) var<uniform> U: array<vec4f, 16>;
@group(0) @binding(1) var<storage, read_write> pos: array<vec4f>;
@group(0) @binding(2) var<storage, read_write> state: array<vec4f>;
@group(0) @binding(3) var<storage, read_write> delta: array<atomic<i32>>;
@group(0) @binding(4) var<storage, read> cons: array<u32>;
@group(0) @binding(5) var<storage, read_write> hcount: array<atomic<i32>>;
@group(0) @binding(6) var<storage, read_write> hdata: array<u32>;
@group(0) @binding(7) var<storage, read_write> outPack: array<f32>;

fn dt() -> f32 { return U[0].x; }
fn substep_i() -> f32 { return U[0].y; }
fn substep_n() -> f32 { return U[0].z; }
fn gravity() -> f32 { return U[0].w; }
fn sphere() -> vec4f { return U[1]; }
fn mu_s() -> f32 { return U[2].x; }
fn mu_g() -> f32 { return U[2].y; }
fn thick() -> f32 { return U[2].z; }
fn cell_size() -> f32 { return U[2].w; }
fn ground_y() -> f32 { return U[3].x; }
fn air_n() -> f32 { return U[3].y; }
fn air_t() -> f32 { return U[3].z; }
fn damp() -> f32 { return U[3].w; }
fn tri_count() -> u32 { return u32(U[4].x); }
fn bend_count() -> u32 { return u32(U[4].y); }
fn edge_count() -> u32 { return u32(U[4].z); }
fn bend_base() -> u32 { return u32(U[4].w); }
fn edge_base() -> u32 { return u32(U[5].x); }
fn vmax() -> f32 { return U[5].w; }
fn spacing() -> f32 { return U[6].x; }
fn NUM() -> u32 { return u32(U[6].y); }
fn ROWS() -> u32 { return u32(U[6].z); }
fn COUNT() -> u32 { return u32(U[6].w); }

fn prev_of(i: u32) -> vec3f { return state[i].xyz; }
fn vel_of(i: u32) -> vec3f { return state[COUNT() + i].xyz; }
fn vel_tag(i: u32) -> f32 { return state[COUNT() + i].w; }
fn pin0(i: u32) -> vec4f { return state[2u * COUNT() + i]; }
fn pin1(i: u32) -> vec4f { return state[3u * COUNT() + i]; }
fn pinned(i: u32) -> bool { return pin1(i).w > 0.5; }
fn wake_requested() -> bool { return U[7].x > 0.5; }
fn asleep(i: u32) -> bool { return pos[i].w < 0.0 && !wake_requested(); }
fn inv_w(i: u32) -> f32 {
  if (pinned(i) || asleep(i)) { return 0.0; }
  return abs(pos[i].w);
}

// pack() writes the final simulated positions here every rendered frame. During
// the next simulation frame this is therefore a stable full-frame contact
// history, unlike prev_of(), which is overwritten at every 240 Hz substep.
fn frame_prev(i: u32) -> vec3f {
  let b = COUNT() * 3u + i * 3u;
  return vec3f(outPack[b], outPack[b + 1u], outPack[b + 2u]);
}

fn accum(i: u32, c: vec3f) {
  if (pinned(i)) { return; }
  let b = i * 4u;
  atomicAdd(&delta[b], i32(c.x * SCALE));
  atomicAdd(&delta[b + 1u], i32(c.y * SCALE));
  atomicAdd(&delta[b + 2u], i32(c.z * SCALE));
  atomicAdd(&delta[b + 3u], 1);
}

fn load_n(i: u32) -> vec3f {
  let b = i * 3u;
  return vec3f(outPack[b], outPack[b + 1u], outPack[b + 2u]);
}

// The visible backdrop is an extruded cyclorama: horizontal floor, exact
// quarter-cylinder transition, then vertical wall. It is a real rigid
// collider, not just scenery. Because the surface is invariant in X, the
// closest-point projection is analytic and much cheaper/more accurate than
// colliding cloth vertices against the render mesh.
const COVE_Z_JOIN: f32 = ${COVE_Z_JOIN};
const COVE_RADIUS: f32 = ${COVE_RADIUS};
const COVE_Z_WALL: f32 = ${COVE_Z_WALL};

fn cove_project(q_in: vec3f) -> vec3f {
  var q = q_in;
  let gap = ground_y();
  if (q.z >= COVE_Z_JOIN) {
    if (q.y < gap) { q.y = gap; }
    return q;
  }
  if (q.y >= COVE_RADIUS) {
    let zw = COVE_Z_WALL + gap;
    if (q.z < zw) { q.z = zw; }
    return q;
  }
  // Air is on the inside of the quarter circle. Offset the physical surface
  // inward by the gap, matching the floor/wall clearance continuously.
  let dy = q.y - COVE_RADIUS;
  let dz = q.z - COVE_Z_JOIN;
  let d = sqrt(dy * dy + dz * dz);
  let radialLimit = COVE_RADIUS - gap;
  if (d > radialLimit && d > 1e-8) {
    let k = radialLimit / d;
    q.y = COVE_RADIUS + dy * k;
    q.z = COVE_Z_JOIN + dz * k;
  }
  return q;
}

fn cove_normal(q: vec3f) -> vec3f {
  if (q.z >= COVE_Z_JOIN) { return vec3f(0.0, 1.0, 0.0); }
  if (q.y >= COVE_RADIUS) { return vec3f(0.0, 0.0, 1.0); }
  let dy = q.y - COVE_RADIUS;
  let dz = q.z - COVE_Z_JOIN;
  let d = sqrt(dy * dy + dz * dz);
  if (d < 1e-8) { return vec3f(0.0, 1.0, 0.0); }
  // Inward radial direction is the normal toward the open side of the cove.
  return vec3f(0.0, -dy / d, -dz / d);
}

fn cove_clearance(q: vec3f) -> f32 {
  let gap = ground_y();
  if (q.z >= COVE_Z_JOIN) { return q.y - gap; }
  if (q.y >= COVE_RADIUS) { return q.z - (COVE_Z_WALL + gap); }
  let dy = q.y - COVE_RADIUS;
  let dz = q.z - COVE_Z_JOIN;
  return (COVE_RADIUS - gap) - sqrt(dy * dy + dz * dz);
}

// Project against both rigid bodies. The inflated sphere is tangent to the
// offset cove floor, so the two projections no longer fight at the contact
// ring. Two alternating projections are enough for the sphere/cove junction.
fn project_legal(q_in: vec3f) -> vec3f {
  var q = q_in;
  let sc = sphere();
  for (var k = 0u; k < 2u; k++) {
    q = cove_project(q);
    let rel = q - sc.xyz;
    let d = length(rel);
    if (d < sc.w && d > 1e-8) {
      q = sc.xyz + rel / d * sc.w;
    }
  }
  q = cove_project(q);
  return q;
}

@compute @workgroup_size(64)
fn integrate(@builtin(global_invocation_id) gid: vec3u) {
  let i = gid.x;
  if (i >= COUNT()) { return; }

  // The tangent portion of outPack is scratch space while the simulation is
  // running. Self-collision only runs on the final substep, so clear this scratch
  // only there; the branch is uniform and avoids four extra stores on every
  // earlier substep. pack() overwrites the same region before rendering.
  {
    let contactBase = COUNT() * 6u + i * 4u;
    outPack[contactBase] = 0.0;
    outPack[contactBase + 1u] = 0.0;
    outPack[contactBase + 2u] = 0.0;
    outPack[contactBase + 3u] = 0.0;
  }

  var p = pos[i];

  let historyBase = COUNT() * 3u + i * 3u;
  outPack[historyBase] = p.x;
  outPack[historyBase + 1u] = p.y;
  outPack[historyBase + 2u] = p.z;

  // Sleeping is encoded by the sign of inverse mass, preserving the exact mass
  // without another buffer. Any grab wakes the whole sheet in this same pass.
  if (wake_requested() && p.w < 0.0) {
    p.w = -p.w;
    pos[i] = p;
    let wakeVel = state[COUNT() + i];
    state[COUNT() + i] = vec4f(wakeVel.xyz, 0.0);
  }
  if (pinned(i)) {
    let a = substep_i() / substep_n();
    let goal = project_legal(mix(pin0(i).xyz, pin1(i).xyz, a));
    state[i] = vec4f(p.xyz, 0.0);
    pos[i] = vec4f(goal, abs(p.w));
    return;
  }
  if (p.w < 0.0) {
    // A genuinely resting contact vertex is kinematic until an interaction
    // wakes the cloth. No gravity/project/constraint micro-cycle can crawl it.
    state[i] = vec4f(p.xyz, 0.0);
    state[COUNT() + i] = vec4f(0.0, 0.0, 0.0, -1.0);
    return;
  }
  let cached = state[COUNT() + i];
  var v = cached.xyz;
  let h = dt();
  v.y += gravity() * h;
  var n = load_n(i);
  let nl = length(n);
  if (nl > 1e-5) { n = n / nl; } else { n = vec3f(0.0, 1.0, 0.0); }
  let vn = dot(v, n);
  let vt = v - n * vn;
  let vtl = length(vt);
  v += (-air_n() * abs(vn) * vn) * n * h;
  if (vtl > 1e-8) { v += (-air_t() * vtl) * vt * h; }
  v *= max(0.0, 1.0 - damp() * h);
  state[i] = vec4f(p.xyz, 0.0);
  pos[i] = vec4f(p.xyz + v * h, p.w);
}

@compute @workgroup_size(64)
fn velocity(@builtin(global_invocation_id) gid: vec3u) {
  let i = gid.x;
  if (i >= COUNT()) { return; }
  let h = dt();
  var v = (pos[i].xyz - prev_of(i)) / h;
  let sp = length(v);
  let m = vmax();
  if (sp > m) { v *= m / sp; }
  if (pinned(i)) {
    state[COUNT() + i] = vec4f(v, 0.0);
    return;
  }

  // apply_contact_delta() leaves a cheap per-vertex separation direction in
  // scratch space. It is valid only on the final substep, which is also the only
  // substep that runs self-collision. Keeping the extra loads/ALU out of earlier
  // substeps makes the stabilization effectively free compared with broad phase.
  var selfContact = false;
  {
    let contactBase = COUNT() * 6u + i * 4u;
    let selfHits = outPack[contactBase + 3u];
    let selfVec = vec3f(
      outPack[contactBase],
      outPack[contactBase + 1u],
      outPack[contactBase + 2u]
    );
    let selfLen = length(selfVec);
    selfContact = selfHits > 0.5;
    if (selfContact && selfLen > 1e-9) {
      let n = selfVec / selfLen;
      let vn = dot(v, n);
      if (vn < 0.0) { v -= n * vn; }

      // Bounded cloth-on-cloth friction. This remains velocity based, so it does
      // not glue folds together and fast motion still breaks resting contact.
      let tang = v - n * dot(v, n);
      let ts = length(tang);
      let selfDv = 0.18 * abs(gravity()) * h;
      if (ts > 1e-8) {
        if (ts <= selfDv) { v -= tang; }
        else { v -= tang * (selfDv / ts); }
      }
    }
  }

  // Contact friction belongs in velocity space. The previous implementation
  // cancelled tangential *position* displacement using an artificial minimum
  // normal correction; that behaves like adhesion and makes folds cling to the
  // sphere/floor. Here normal non-penetration is positional, while Coulomb
  // friction only removes a bounded amount of tangential speed per substep.
  let g = abs(gravity());
  let sc = sphere();
  let rel = pos[i].xyz - sc.xyz;
  let dist = length(rel);
  var contact = selfContact;
  if (dist < sc.w + 0.0022 && dist > 1e-7) {
    contact = true;
    let n = rel / dist;
    let vn = dot(v, n);
    if (vn < 0.0) { v -= n * vn; }
    let tang = v - n * dot(v, n);
    let ts = length(tang);
    // Gravity supplies the support load on the upper hemisphere. On the
    // vertical sides there is deliberately almost no artificial sticking.
    let dv = mu_s() * g * max(n.y, 0.0) * h;
    if (ts > 1e-8) {
      if (ts <= dv) { v -= tang; }
      else { v -= tang * (dv / ts); }
    }
    let vn2 = dot(v, n);
    if (abs(vn2) < 0.004) { v -= n * vn2; }
  }
  let coveGap = cove_clearance(pos[i].xyz);
  if (coveGap < 0.0018) {
    contact = true;
    let n = cove_normal(pos[i].xyz);
    let vn = dot(v, n);
    if (vn < 0.0) { v -= n * vn; }
    let tang = v - n * dot(v, n);
    let ts = length(tang);
    // Only gravity-supported normal load contributes here. This keeps the
    // vertical wall and steep cove from becoming an adhesive surface.
    let dv = mu_g() * g * max(n.y, 0.0) * h;
    if (ts > 1e-8 && dv > 0.0) {
      if (ts <= dv) { v -= tang; }
      else { v -= tang * (dv / ts); }
    }
    let vn2 = dot(v, n);
    if (abs(vn2) < 0.004) { v -= n * vn2; }
  }
  // True contact deactivation. A dead-zone still lets constraint/projector
  // corrections recreate velocity on the next frame; after eight quiet rendered
  // frames we instead make this supported vertex kinematic. The sign of pos.w
  // stores the sleep bit, so there is no extra buffer or collision pass.
  var tag = vel_tag(i);
  if (substep_i() >= substep_n()) {
    let quiet = contact && length(v) < 0.024 && !wake_requested();
    if (quiet) {
      tag = select(tag + 1.0, 1.0, tag < 0.0);
      if (tag >= 8.0) {
        v = vec3f(0.0);
        var p = pos[i];
        p.w = -abs(p.w);
        pos[i] = p;
        tag = -1.0;
      }
    } else {
      tag = 0.0;
    }
  }
  if (contact && length(v) < 0.0045) { v = vec3f(0.0); }
  state[COUNT() + i] = vec4f(v, tag);
}

@compute @workgroup_size(64)
fn strain(@builtin(global_invocation_id) gid: vec3u) {
  let t = gid.x;
  if (t >= tri_count()) { return; }
  let base = t * 12u;
  let i0 = cons[base];
  let i1 = cons[base + 1u];
  let i2 = cons[base + 2u];
  let d00 = bitcast<f32>(cons[base + 4u]);
  let d01 = bitcast<f32>(cons[base + 5u]);
  let d10 = bitcast<f32>(cons[base + 6u]);
  let d11 = bitcast<f32>(cons[base + 7u]);
  let aS = bitcast<f32>(cons[base + 10u]);
  let x0 = pos[i0].xyz;
  let x1 = pos[i1].xyz;
  let x2 = pos[i2].xyz;
  let e1 = x1 - x0;
  let e2 = x2 - x0;
  let f0 = e1 * d00 + e2 * d10;
  let f1 = e1 * d01 + e2 * d11;
  let l0 = length(f0);
  let l1 = length(f1);
  if (l0 < 1e-7 || l1 < 1e-7) { return; }

  // Woven cloth is not a linear rubber membrane. Small in-plane shear is
  // mostly yarn rotation/crimp release, then the weave becomes rapidly stiffer
  // as neighbouring yarns approach locking. Structural yarn length is solved
  // separately by graph-coloured distance constraints.
  let raw = dot(f0, f1) / (l0 * l1);
  let ar = abs(raw);
  if (ar <= SHEAR_FREE) { return; }
  let sgn = select(-1.0, 1.0, raw >= 0.0);
  let C = (ar - SHEAR_FREE) * sgn;
  let lockT = clamp((ar - SHEAR_FREE) / max(0.60 - SHEAR_FREE, 1e-4), 0.0, 1.0);
  let stiffMul = 0.30 + 7.70 * lockT * lockT;

  // Differentiate the actual normalized shear above. Using the gradient of
  // dot(f0, f1) instead introduces forces along the yarns, fighting the length
  // solve as a compressed element approaches a degenerate triangle.
  let invLengths = 1.0 / (l0 * l1);
  let shear0 = f1 * invLengths - f0 * (raw / (l0 * l0));
  let shear1 = f0 * invLengths - f1 * (raw / (l1 * l1));
  let g1 = shear0 * d00 + shear1 * d01;
  let g2 = shear0 * d10 + shear1 * d11;
  let g0 = -(g1 + g2);
  let w0 = inv_w(i0);
  let w1 = inv_w(i1);
  let w2 = inv_w(i2);
  var denom = w0 * dot(g0, g0) + w1 * dot(g1, g1) + w2 * dot(g2, g2);
  denom += (aS / stiffMul) / (dt() * dt());
  if (denom < 1e-12) { return; }
  let dL = -C / denom;
  accum(i0, g0 * (w0 * dL));
  accum(i1, g1 * (w1 * dL));
  accum(i2, g2 * (w2 * dL));
}

// Warp and weft yarn segments are nearly inextensible in real woven cloth.
// Solve them as graph-coloured bilateral distance constraints so compression
// creates out-of-plane buckling instead of shortening the surface like rubber.
fn solve_structural_pair(i0: u32, i1: u32) {
  // Quiet sleep is persistent; only an arriving dynamic load can wake it.
  if ((pos[i0].w < 0.0) != (pos[i1].w < 0.0)) {
    let separation = length(pos[i1].xyz - pos[i0].xyz);
    if (abs(separation - spacing()) > spacing() * 0.04 && length(vel_of(i0) - vel_of(i1)) > 0.20) {
      if (!pinned(i0) && pos[i0].w < 0.0) { pos[i0].w = -pos[i0].w; }
      if (!pinned(i1) && pos[i1].w < 0.0) { pos[i1].w = -pos[i1].w; }
    }
  }
  let w0 = inv_w(i0);
  let w1 = inv_w(i1);
  let ws = w0 + w1;
  if (ws < 1e-12) { return; }
  var p0 = pos[i0];
  var p1 = pos[i1];
  let d = p1.xyz - p0.xyz;
  let l = length(d);
  if (l < 1e-8) { return; }
  let C = l - spacing();
  if (abs(C) < spacing() * 0.00015) { return; }
  let corr = (d / l) * (STRUCTURAL_RELAX * C / ws);
  if (w0 > 0.0) { p0 = vec4f(p0.xyz + corr * w0, p0.w); }
  if (w1 > 0.0) { p1 = vec4f(p1.xyz - corr * w1, p1.w); }
  pos[i0] = p0;
  pos[i1] = p1;
}

fn solve_h(id: u32, parity: u32) {
  if (id >= COUNT()) { return; }
  let i = id % NUM();
  let j = id / NUM();
  if (i + 1u >= NUM() || (i & 1u) != parity) { return; }
  let a = j * NUM() + i;
  solve_structural_pair(a, a + 1u);
}
fn solve_v(id: u32, parity: u32) {
  if (id >= COUNT()) { return; }
  let i = id % NUM();
  let j = id / NUM();
  if (j + 1u >= ROWS() || (j & 1u) != parity) { return; }
  let a = j * NUM() + i;
  solve_structural_pair(a, a + NUM());
}
@compute @workgroup_size(64)
fn struct_h_even(@builtin(global_invocation_id) gid: vec3u) { solve_h(gid.x, 0u); }
@compute @workgroup_size(64)
fn struct_h_odd(@builtin(global_invocation_id) gid: vec3u) { solve_h(gid.x, 1u); }
@compute @workgroup_size(64)
fn struct_v_even(@builtin(global_invocation_id) gid: vec3u) { solve_v(gid.x, 0u); }
@compute @workgroup_size(64)
fn struct_v_odd(@builtin(global_invocation_id) gid: vec3u) { solve_v(gid.x, 1u); }

fn solve_yarn(t: u32) {
  if (t >= bend_count()) { return; }
  let base = bend_base() + t * 8u;
  let i0 = cons[base];
  let i1 = cons[base + 1u];
  let i2 = cons[base + 2u];
  let alpha = bitcast<f32>(cons[base + 5u]);
  let w0 = inv_w(i0);
  let w1 = inv_w(i1);
  let w2 = inv_w(i2);
  if (w0 + w1 + w2 == 0.0) { return; }
  let e0 = pos[i1].xyz - pos[i0].xyz;
  let e1 = pos[i2].xyz - pos[i1].xyz;
  let l0 = length(e0);
  let l1 = length(e1);
  if (min(l0, l1) < 1e-7) { return; }
  let u = e0 / l0;
  let v = e1 / l1;
  let axis = cross(u, v);
  let sine = length(axis);
  let cosine = clamp(dot(u, v), -1.0, 1.0);
  let C = atan2(sine, cosine);
  if (C < 0.02) { return; }
  var n = axis;
  if (sine < 1e-6) {
    n = cross(frame_prev(i1) - frame_prev(i0), frame_prev(i2) - frame_prev(i1));
    if (length(n) < 1e-8) { n = cross(u, load_n(i1)); }
    if (length(n) < 1e-8) { return; }
  }
  n = normalize(n);
  let d0 = cross(n, u) / l0;
  let d2 = cross(n, v) / l1;
  let d1 = -(d0 + d2);
  var denom = w0 * dot(d0, d0) + w1 * dot(d1, d1) + w2 * dot(d2, d2);
  denom += alpha / (dt() * dt());
  if (denom < 1e-20) { return; }
  let dL = -C / denom;
  pos[i0] = vec4f(pos[i0].xyz + d0 * (w0 * dL), pos[i0].w);
  pos[i1] = vec4f(pos[i1].xyz + d1 * (w1 * dL), pos[i1].w);
  pos[i2] = vec4f(pos[i2].xyz + d2 * (w2 * dL), pos[i2].w);
}

fn yarn_color(t: u32, axis: u32, color: u32) {
  if (t >= bend_count()) { return; }
  let horizontal = ROWS() * (NUM() - 2u);
  if ((axis == 0u) != (t < horizontal)) { return; }
  let mid = cons[bend_base() + t * 8u + 1u];
  let coord = select(mid / NUM(), mid % NUM(), axis == 0u);
  if ((coord - 1u) % 3u != color) { return; }
  solve_yarn(t);
}
@compute @workgroup_size(64)
fn bend_h_0(@builtin(global_invocation_id) gid: vec3u) { yarn_color(gid.x, 0u, 0u); }
@compute @workgroup_size(64)
fn bend_h_1(@builtin(global_invocation_id) gid: vec3u) { yarn_color(gid.x, 0u, 1u); }
@compute @workgroup_size(64)
fn bend_h_2(@builtin(global_invocation_id) gid: vec3u) { yarn_color(gid.x, 0u, 2u); }
@compute @workgroup_size(64)
fn bend_v_0(@builtin(global_invocation_id) gid: vec3u) { yarn_color(gid.x, 1u, 0u); }
@compute @workgroup_size(64)
fn bend_v_1(@builtin(global_invocation_id) gid: vec3u) { yarn_color(gid.x, 1u, 1u); }
@compute @workgroup_size(64)
fn bend_v_2(@builtin(global_invocation_id) gid: vec3u) { yarn_color(gid.x, 1u, 2u); }

@compute @workgroup_size(64)
fn apply_delta(@builtin(global_invocation_id) gid: vec3u) {
  let i = gid.x;
  if (i >= COUNT()) { return; }
  let b = i * 4u;
  let c = atomicLoad(&delta[b + 3u]);
  let dx = atomicLoad(&delta[b]);
  let dy = atomicLoad(&delta[b + 1u]);
  let dz = atomicLoad(&delta[b + 2u]);
  atomicStore(&delta[b], 0);
  atomicStore(&delta[b + 1u], 0);
  atomicStore(&delta[b + 2u], 0);
  atomicStore(&delta[b + 3u], 0);
  if (c <= 0 || pinned(i) || pos[i].w <= 0.0) { return; }
  var corr = vec3f(f32(dx), f32(dy), f32(dz)) * (1.0 / (SCALE * f32(c)));
  let cl = length(corr);
  let lim = spacing() * 1.0;
  if (cl > lim) { corr *= lim / cl; }
  var p = pos[i];
  p.x += corr.x; p.y += corr.y; p.z += corr.z;
  pos[i] = p;
}

// Self-contact needs different numerics from elastic Jacobi corrections.
// Dense contacts should not be diluted into near-zero repairs, and positional
// depenetration should not be reconstructed as free kinetic energy. This pass
// replaces apply_delta after self-collision, so it adds no GPU dispatch.
@compute @workgroup_size(64)
fn apply_contact_delta(@builtin(global_invocation_id) gid: vec3u) {
  let i = gid.x;
  if (i >= COUNT()) { return; }
  let b = i * 4u;
  let packedCount = atomicLoad(&delta[b + 3u]);
  let c = packedCount & (WAKE_BIT - 1);
  let dx = atomicLoad(&delta[b]);
  let dy = atomicLoad(&delta[b + 1u]);
  let dz = atomicLoad(&delta[b + 2u]);
  atomicStore(&delta[b], 0);
  atomicStore(&delta[b + 1u], 0);
  atomicStore(&delta[b + 2u], 0);
  atomicStore(&delta[b + 3u], 0);
  if ((packedCount & WAKE_BIT) != 0 && !pinned(i)) {
    pos[i].w = abs(pos[i].w);
    state[COUNT() + i].w = 0.0;
  }
  if (c <= 0 || pinned(i) || pos[i].w <= 0.0) { return; }

  let cf = f32(c);
  var corr = vec3f(f32(dx), f32(dy), f32(dz)) * (1.0 / (SCALE * cf));

  // The normal Jacobi average scales as 1/N and becomes too weak in a pile.
  // A capped sqrt(N) gain improves convergence without another collision sweep.
  corr *= 1.0;
  var cl = length(corr);
  let lim = min(spacing() * 0.16, thick() * 1.10);
  if (cl > lim && cl > 1e-12) { corr *= lim / cl; }

  let p0 = pos[i];
  var corrected = corr;

  // Do not let self-contact push a load-bearing layer into a rigid support and
  // then make the rigid projection push it back. Remove only inward motion.
  if (cove_clearance(p0.xyz) < thick() * 1.75) {
    let n = cove_normal(p0.xyz);
    let inward = dot(corrected, n);
    if (inward < 0.0) { corrected -= n * inward; }
  }
  let sc = sphere();
  let rel = p0.xyz - sc.xyz;
  let dist = length(rel);
  if (dist > 1e-8 && dist < sc.w + thick() * 1.75) {
    let n = rel / dist;
    let inward = dot(corrected, n);
    if (inward < 0.0) { corrected -= n * inward; }
  }

  let contactBase = COUNT() * 6u + i * 4u;
  outPack[contactBase + 3u] += 1.0;

  cl = length(corrected);
  if (cl <= 1e-12) { return; }

  pos[i] = vec4f(p0.xyz + corrected, p0.w);

  // Depenetration is stabilization, not an impulse. Remove 90% of it from the
  // velocity reconstruction while retaining a small dynamic separation response.
  let prev = state[i];
  state[i] = vec4f(prev.xyz + corrected, prev.w);

  // Net separation direction is consumed by velocity() later in this substep.
  outPack[contactBase] += corrected.x;
  outPack[contactBase + 1u] += corrected.y;
  outPack[contactBase + 2u] += corrected.z;
}

@compute @workgroup_size(64)
fn collide_rigid(@builtin(global_invocation_id) gid: vec3u) {
  let i = gid.x;
  if (i >= COUNT()) { return; }
  let p = pos[i];
  if (asleep(i)) { return; }
  if (pinned(i)) {
    let a = substep_i() / substep_n();
    let goal = project_legal(mix(pin0(i).xyz, pin1(i).xyz, a));
    pos[i] = vec4f(goal, p.w);
    return;
  }
  pos[i] = vec4f(project_legal(p.xyz), p.w);
}

fn hash_cell(c: vec3i) -> u32 {
  let x = bitcast<u32>(c.x) * 73856093u;
  let y = bitcast<u32>(c.y) * 19349663u;
  let z = bitcast<u32>(c.z) * 83492791u;
  return (x ^ y ^ z) & (HASH - 1u);
}
fn cell_of(p: vec3f) -> vec3i {
  return vec3i(floor(p / cell_size()));
}
fn cheb(a: u32, b: u32) -> i32 {
  let cols = NUM();
  let ai = i32(a % cols);
  let aj = i32(a / cols);
  let bi = i32(b % cols);
  let bj = i32(b / cols);
  return max(abs(ai - bi), abs(aj - bj));
}

@compute @workgroup_size(64)
fn clear_tri_hash(@builtin(global_invocation_id) gid: vec3u) {
  let i = gid.x;
  if (i < HASH) { atomicStore(&hcount[i], 0); }
  if (i == 0u) { atomicStore(&hcount[HASH * 2u], 0); }
}

@compute @workgroup_size(64)
fn clear_edge_hash(@builtin(global_invocation_id) gid: vec3u) {
  let i = gid.x;
  if (i < HASH) { atomicStore(&hcount[HASH + i], 0); }
  if (i == 0u) { atomicStore(&hcount[HASH * 2u + 1u], 0); }
}

@compute @workgroup_size(64)
fn insert_tris(@builtin(global_invocation_id) gid: vec3u) {
  let t = gid.x;
  if (t >= tri_count()) { return; }
  let base = t * 12u;
  let i0 = cons[base];
  let i1 = cons[base + 1u];
  let i2 = cons[base + 2u];
  let centroid = (pos[i0].xyz + pos[i1].xyz + pos[i2].xyz) * (1.0 / 3.0);
  let h = hash_cell(cell_of(centroid));
  let slot = atomicAdd(&hcount[h], 1);
  if (slot < i32(SLOT)) {
    hdata[h * SLOT + u32(slot)] = t;
  } else {
    atomicAdd(&hcount[HASH * 2u], 1);
  }
}

@compute @workgroup_size(64)
fn insert_edges(@builtin(global_invocation_id) gid: vec3u) {
  let e = gid.x;
  if (e >= edge_count()) { return; }
  let base = edge_base() + e * 4u;
  let a = cons[base];
  let b = cons[base + 1u];
  let mid = (pos[a].xyz + pos[b].xyz) * 0.5;
  let h = hash_cell(cell_of(mid));
  let slot = atomicAdd(&hcount[HASH + h], 1);
  if (slot < i32(SLOT)) {
    hdata[HASH * SLOT + h * SLOT + u32(slot)] = e;
  } else {
    atomicAdd(&hcount[HASH * 2u + 1u], 1);
  }
}

fn closest_bary(p: vec3f, a: vec3f, b: vec3f, c: vec3f) -> vec3f {
  let ab = b - a;
  let ac = c - a;
  let ap = p - a;
  let d1 = dot(ab, ap);
  let d2 = dot(ac, ap);
  if (d1 <= 0.0 && d2 <= 0.0) { return vec3f(1.0, 0.0, 0.0); }
  let bp = p - b;
  let d3 = dot(ab, bp);
  let d4 = dot(ac, bp);
  if (d3 >= 0.0 && d4 <= d3) { return vec3f(0.0, 1.0, 0.0); }
  let vc = d1 * d4 - d3 * d2;
  if (vc <= 0.0 && d1 >= 0.0 && d3 <= 0.0) {
    let v = d1 / (d1 - d3);
    return vec3f(1.0 - v, v, 0.0);
  }
  let cp = p - c;
  let d5 = dot(ab, cp);
  let d6 = dot(ac, cp);
  if (d6 >= 0.0 && d5 <= d6) { return vec3f(0.0, 0.0, 1.0); }
  let vb = d5 * d2 - d1 * d6;
  if (vb <= 0.0 && d2 >= 0.0 && d6 <= 0.0) {
    let w = d2 / (d2 - d6);
    return vec3f(1.0 - w, 0.0, w);
  }
  let va = d3 * d6 - d5 * d4;
  if (va <= 0.0 && (d4 - d3) >= 0.0 && (d5 - d6) >= 0.0) {
    let w = (d4 - d3) / ((d4 - d3) + (d5 - d6));
    return vec3f(0.0, 1.0 - w, w);
  }
  let denom = 1.0 / (va + vb + vc);
  let v = vb * denom;
  let w = vc * denom;
  return vec3f(1.0 - v - w, v, w);
}

// Exact discrete surface contact for the rendered triangle against the sphere.
// Vertex-only and edge-only tests can still leave the interior of a stretched
// triangle cutting through a convex collider; closest-point triangle/sphere
// contact closes that hole.
@compute @workgroup_size(64)
fn collide_tri_sphere(@builtin(global_invocation_id) gid: vec3u) {
  let t = gid.x;
  if (t >= tri_count()) { return; }
  let base = t * 12u;
  let i0 = cons[base];
  let i1 = cons[base + 1u];
  let i2 = cons[base + 2u];
  let a = pos[i0].xyz;
  let b = pos[i1].xyz;
  let c = pos[i2].xyz;
  let sc = sphere();
  let center = sc.xyz;
  let R = sc.w;
  let bary = closest_bary(center, a, b, c);
  let q = a * bary.x + b * bary.y + c * bary.z;
  let rel = q - center;
  let dist = length(rel);
  if (dist >= R || dist < 1e-8) { return; }
  let nrm = rel / dist;
  let w0 = inv_w(i0);
  let w1 = inv_w(i1);
  let w2 = inv_w(i2);
  let denom = w0 * bary.x * bary.x + w1 * bary.y * bary.y + w2 * bary.z * bary.z;
  if (denom < 1e-12) { return; }
  let lam = (R - dist) / denom;
  accum(i0, nrm * (lam * w0 * bary.x));
  accum(i1, nrm * (lam * w1 * bary.y));
  accum(i2, nrm * (lam * w2 * bary.z));
}

fn respond_point_tri(point: u32, pnt: vec3f, i0: u32, i1: u32, i2: u32, a: vec3f, b: vec3f, c: vec3f) {
  if (point == i0 || point == i1 || point == i2) { return; }

  let bary = closest_bary(pnt, a, b, c);
  let q = a * bary.x + b * bary.y + c * bary.z;
  let diff = pnt - q;
  let dist = length(diff);
  let th = thick();
  let targetSep = th * 0.92;

  // Keep full-frame history work confined to genuinely nearby geometry. The
  // broad phase is unchanged, so this does not turn every hash candidate into
  // a CCD calculation. The wider history band still catches the tiny crossings
  // that create coplanar resting layers.
  if (dist > max(targetSep * 2.5, spacing() * 0.55)) { return; }

  // closest_bary clamps to the triangle. At an edge/vertex, distance to the
  // face plane is NOT distance to the surface: two disjoint coplanar features
  // have zero plane separation. Only the face interior can use the wider
  // signed-history band; boundary features must be within the contact shell.
  let boundary = any(bary <= vec3f(1e-6));
  if (boundary && dist > targetSep + th * 0.35) { return; }

  // Current and previous-frame oriented face normals. Self collision is solved
  // only once per rendered frame, so substep history is the wrong reference: a
  // layer may already have crossed during an earlier 240 Hz substep. The packed
  // previous-render position survives the whole frame and preserves topology.
  let faceRaw = cross(b - a, c - a);
  let faceLen = length(faceRaw);
  if (faceLen < 1e-10) { return; }
  var faceN = faceRaw / faceLen;

  let pa = frame_prev(i0);
  let pb = frame_prev(i1);
  let pc = frame_prev(i2);
  let pp = frame_prev(point);
  let prevFaceRaw = cross(pb - pa, pc - pa);
  let prevFaceLen = length(prevFaceRaw);
  var prevFaceN = faceN;
  if (prevFaceLen > 1e-10) {
    prevFaceN = prevFaceRaw / prevFaceLen;
    if (dot(faceN, prevFaceN) < 0.0) { faceN = -faceN; }
  }

  let prevQ = pa * bary.x + pb * bary.y + pc * bary.z;
  var prevSide = dot(pp - prevQ, prevFaceN);
  let nowSide = dot(pnt - q, faceN);

  // If the previous frame was numerically coplanar, choose the current side;
  // if both are coplanar use the triangle's oriented normal deterministically.
  var side = 1.0;
  if (abs(prevSide) > 1e-6) {
    side = select(-1.0, 1.0, prevSide >= 0.0);
  } else if (abs(nowSide) > 1e-7) {
    side = select(-1.0, 1.0, nowSide >= 0.0);
  }
  var nrm = faceN * side;
  // The closest-feature gradient at the boundary points from q to the point,
  // not perpendicular to the face. Otherwise a point beside a triangle gets
  // lifted as though it pierced its interior, corrugating a resting sheet.
  // Retain the oriented fallback when the closest points coincide.
  if (boundary && dist > 1e-8) { nrm = diff / dist; }
  let sep = dot(diff, nrm);

  // Contact must persist when the layers are merely touching, not only while
  // they are penetrating. Otherwise cloth-on-cloth friction/sleep disappears
  // the instant depenetration succeeds and the pile starts creeping again.
  if (sep < targetSep + th * 0.35) {
    let contactBase = COUNT() * 6u + point * 4u;
    outPack[contactBase] += nrm.x;
    outPack[contactBase + 1u] += nrm.y;
    outPack[contactBase + 2u] += nrm.z;
    outPack[contactBase + 3u] += 1.0;
  }

  // Unlike an unsigned closest-distance test this also catches a same-frame
  // crossing: after crossing sep is negative, so the constraint remains active
  // instead of accepting the point on the wrong side of the sheet.
  if (sep >= targetSep) { return; }
  let C = sep - targetSep;

  let relative = vel_of(point) - (vel_of(i0) * bary.x + vel_of(i1) * bary.y + vel_of(i2) * bary.z);
  let impact = dot(relative, nrm) < -0.20;
  let wP = impact_weight(point, impact);
  let w0 = impact_weight(i0, impact);
  let w1 = impact_weight(i1, impact);
  let w2 = impact_weight(i2, impact);
  let denom = wP + w0 * bary.x * bary.x + w1 * bary.y * bary.y + w2 * bary.z * bary.z;
  if (denom < 1e-12) { return; }
  let lam = -C / denom;
  accum(point, nrm * (lam * wP));
  accum(i0, nrm * (-lam * w0 * bary.x));
  accum(i1, nrm * (-lam * w1 * bary.y));
  accum(i2, nrm * (-lam * w2 * bary.z));
}

fn impact_weight(i: u32, impact: bool) -> f32 {
  if (pinned(i)) { return 0.0; }
  if (pos[i].w < 0.0) {
    if (!impact) { return 0.0; }
    atomicOr(&delta[i * 4u + 3u], WAKE_BIT);
  }
  return abs(pos[i].w);
}

@compute @workgroup_size(64)
fn solve_point_tri(@builtin(global_invocation_id) gid: vec3u) {
  let i = gid.x;
  if (i >= COUNT()) { return; }
  if (pinned(i)) { return; }
  let p = pos[i].xyz;
  let c0 = cell_of(p);
  for (var dz = -1; dz <= 1; dz++) {
    for (var dy = -1; dy <= 1; dy++) {
      for (var dx = -1; dx <= 1; dx++) {
        let qc = c0 + vec3i(dx, dy, dz);
        let h = hash_cell(qc);
        let cnt = min(atomicLoad(&hcount[h]), i32(SLOT));
        for (var s = 0; s < cnt; s++) {
          let t = hdata[h * SLOT + u32(s)];
          let base = t * 12u;
          let i0 = cons[base];
          let i1 = cons[base + 1u];
          let i2 = cons[base + 2u];
          let a = pos[i0].xyz;
          let b = pos[i1].xyz;
          let c = pos[i2].xyz;
          // Hash buckets are not cell identities. Reject entries from a
          // different spatial cell that merely alias to the same hash; the old
          // code treated those as real contacts and produced non-local
          // 'static charge' attraction/jitter.
          let tc = cell_of((a + b + c) * (1.0 / 3.0));
          if (any(tc != qc)) { continue; }
          respond_point_tri(i, p, i0, i1, i2, a, b, c);
        }
      }
    }
  }
}

fn seg_seg(p1: vec3f, q1: vec3f, p2: vec3f, q2: vec3f) -> vec2f {
  let d1 = q1 - p1;
  let d2 = q2 - p2;
  let r = p1 - p2;
  let a = dot(d1, d1);
  let e = dot(d2, d2);
  let f = dot(d2, r);
  var s = 0.0;
  var t = 0.0;
  // a/e are squared lengths (m^2); the parallel determinant below is m^4.
  // A shared absolute epsilon incorrectly classified shallow crossings of
  // these 15 mm edges as parallel and tested an endpoint instead.
  let eps = 1e-12;
  if (a <= eps && e <= eps) { return vec2f(0.0, 0.0); }
  if (a <= eps) {
    s = 0.0;
    t = clamp(f / e, 0.0, 1.0);
  } else {
    let c = dot(d1, r);
    if (e <= eps) {
      t = 0.0;
      s = clamp(-c / a, 0.0, 1.0);
    } else {
      let b = dot(d1, d2);
      let denom = a * e - b * b;
      if (denom > 1e-6 * a * e) { s = clamp((b * f - c * e) / denom, 0.0, 1.0); }
      t = (b * s + f) / e;
      if (t < 0.0) {
        t = 0.0;
        s = clamp(-c / a, 0.0, 1.0);
      } else if (t > 1.0) {
        t = 1.0;
        s = clamp((b - c) / a, 0.0, 1.0);
      }
    }
  }
  return vec2f(s, t);
}

@compute @workgroup_size(64)
fn solve_edge_edge(@builtin(global_invocation_id) gid: vec3u) {
  let e = gid.x;
  if (e >= edge_count()) { return; }
  let base = edge_base() + e * 4u;
  let i0 = cons[base];
  let i1 = cons[base + 1u];
  let mid = (pos[i0].xyz + pos[i1].xyz) * 0.5;
  let c0 = cell_of(mid);
  let region = HASH * SLOT;
  for (var dz = -1; dz <= 1; dz++) {
    for (var dy = -1; dy <= 1; dy++) {
      for (var dx = -1; dx <= 1; dx++) {
        let qc = c0 + vec3i(dx, dy, dz);
        let h = hash_cell(qc);
        let cnt = min(atomicLoad(&hcount[HASH + h]), i32(SLOT));
        for (var s = 0; s < cnt; s++) {
          let o = hdata[region + h * SLOT + u32(s)];
          if (o <= e) { continue; }
          let ob = edge_base() + o * 4u;
          let j0 = cons[ob];
          let j1 = cons[ob + 1u];
          let oc = cell_of((pos[j0].xyz + pos[j1].xyz) * 0.5);
          if (any(oc != qc)) { continue; }
          if (i0 == j0 || i0 == j1 || i1 == j0 || i1 == j1) { continue; }
          let p0 = pos[i0].xyz;
          let p1 = pos[i1].xyz;
          let q0 = pos[j0].xyz;
          let q1 = pos[j1].xyz;
          let st = seg_seg(p0, p1, q0, q1);
          let c1 = p0 + (p1 - p0) * st.x;
          let c2 = q0 + (q1 - q0) * st.y;
          let diff = c1 - c2;
          var dist = length(diff);
          let th = thick();
          let slop = th * 0.08;
          if (dist >= th - slop) { continue; }

          // Exact/nearly exact intersections are the contacts that most need a
          // stable normal. Recover it from previous-substep geometry instead of
          // silently dropping the pair when distance approaches zero.
          let pp0 = frame_prev(i0);
          let pp1 = frame_prev(i1);
          let pq0 = frame_prev(j0);
          let pq1 = frame_prev(j1);
          let pc1 = pp0 + (pp1 - pp0) * st.x;
          let pc2 = pq0 + (pq1 - pq0) * st.y;
          let prevDiff = pc1 - pc2;
          let prevLen = length(prevDiff);
          var nrm = vec3f(0.0, 1.0, 0.0);
          if (dist > 1e-8) {
            nrm = diff / dist;
            if (prevLen > 1e-8 && dot(nrm, prevDiff) < 0.0) { nrm = -nrm; }
          } else if (prevLen > 1e-8) {
            nrm = prevDiff / prevLen;
            dist = 0.0;
          } else {
            let crossN = cross(p1 - p0, q1 - q0);
            let crossLen = length(crossN);
            if (crossLen < 1e-10) { continue; }
            nrm = crossN / crossLen;
            let prevCross = cross(pp1 - pp0, pq1 - pq0);
            if (dot(nrm, prevCross) < 0.0) { nrm = -nrm; }
            dist = 0.0;
          }
          // History can reverse nrm after a crossing. Measure the constraint
          // along that same normal: unsigned distance under-corrects a crossed
          // pair by twice its distance from the retained contact side.
          let C = dot(diff, nrm) - (th - slop);
          let b0 = 1.0 - st.x;
          let b1 = st.x;
          let b2 = 1.0 - st.y;
          let b3 = st.y;
          let w0 = inv_w(i0);
          let w1 = inv_w(i1);
          let w2 = inv_w(j0);
          let w3 = inv_w(j1);
          let denom = w0 * b0 * b0 + w1 * b1 * b1 + w2 * b2 * b2 + w3 * b3 * b3;
          if (denom < 1e-12) { continue; }
          let lam = C / denom;
          accum(i0, nrm * (-lam * w0 * b0));
          accum(i1, nrm * (-lam * w1 * b1));
          accum(j0, nrm * (lam * w2 * b2));
          accum(j1, nrm * (lam * w3 * b3));
        }
      }
    }
  }
}

// An edge with both ends outside the sphere can still cut through it.
// Translate that edge until its closest point sits on the surface.
// Sub-millimetre sagitta of a short edge lying on the ball is ignored.
@compute @workgroup_size(64)
fn collide_edge_sphere(@builtin(global_invocation_id) gid: vec3u) {
  let e = gid.x;
  if (e >= edge_count()) { return; }
  let base = edge_base() + e * 4u;
  let i0 = cons[base];
  let i1 = cons[base + 1u];
  let w0 = inv_w(i0);
  let w1 = inv_w(i1);
  if (w0 == 0.0 && w1 == 0.0) { return; }
  let a = pos[i0].xyz;
  let b = pos[i1].xyz;
  let ab = b - a;
  let ab2 = dot(ab, ab);
  let sc = sphere();
  let center = sc.xyz;
  let R = sc.w;
  var t = 0.5;
  if (ab2 > 1e-12) {
    t = clamp(dot(center - a, ab) / ab2, 0.0, 1.0);
  }
  let q = a + ab * t;
  let rel = q - center;
  let dist = length(rel);
  if (dist >= R - 0.0006 || dist < 1e-6) { return; }
  let nrm = rel / dist;
  let push = nrm * (R - dist);
  if (w0 > 0.0 && w1 > 0.0) {
    accum(i0, push);
    accum(i1, push);
  } else if (w0 > 0.0) {
    accum(i0, push / max(1.0 - t, 0.25));
  } else {
    accum(i1, push / max(t, 0.25));
  }
}

fn grid_pos(ix: i32, iy: i32) -> vec3f {
  let cols = NUM();
  return pos[u32(iy) * cols + u32(ix)].xyz;
}

@compute @workgroup_size(64)
fn pack(@builtin(global_invocation_id) gid: vec3u) {
  let id = gid.x;
  if (id >= COUNT()) { return; }
  let cols = NUM();
  let rows = u32(U[6].z);
  let i = i32(id % cols);
  let j = i32(id / cols);
  let Ni = i32(cols);
  let Nj = i32(rows);
  var nrm = vec3f(0.0);
  // Incident faces, same winding as the constraint triangles (rest normal +Y).
  if (i > 0 && j > 0) {
    let a = grid_pos(i, j - 1);
    let b = grid_pos(i - 1, j);
    let c = grid_pos(i, j);
    nrm += cross(b - a, c - a);
  }
  if (i + 1 < Ni && j > 0) {
    let a = grid_pos(i, j - 1);
    let bv = grid_pos(i, j);
    let c = grid_pos(i + 1, j - 1);
    nrm += cross(bv - a, c - a);
    let d = grid_pos(i + 1, j);
    nrm += cross(bv - c, d - c);
  }
  if (i > 0 && j + 1 < Nj) {
    let a = grid_pos(i - 1, j);
    let b = grid_pos(i - 1, j + 1);
    let c = grid_pos(i, j);
    nrm += cross(b - a, c - a);
    let d = grid_pos(i, j + 1);
    nrm += cross(b - c, d - c);
  }
  if (i + 1 < Ni && j + 1 < Nj) {
    let a = grid_pos(i, j);
    let b = grid_pos(i, j + 1);
    let c = grid_pos(i + 1, j);
    nrm += cross(b - a, c - a);
  }
  let nl = length(nrm);
  if (nl > 1e-10) { nrm = nrm / nl; } else { nrm = vec3f(0.0, 1.0, 0.0); }
  var tng = vec3f(0.0);
  if (i + 1 < Ni) { tng += grid_pos(i + 1, j) - grid_pos(i, j); }
  if (i > 0) { tng += grid_pos(i, j) - grid_pos(i - 1, j); }
  tng = tng - nrm * dot(nrm, tng);
  let tl = length(tng);
  if (tl > 1e-8) { tng = tng / tl; } else { tng = vec3f(1.0, 0.0, 0.0); }
  var weft = vec3f(0.0);
  if (j + 1 < Nj) { weft += grid_pos(i, j + 1) - grid_pos(i, j); }
  if (j > 0) { weft += grid_pos(i, j) - grid_pos(i, j - 1); }
  var hand = 1.0;
  if (dot(cross(nrm, tng), weft) < 0.0) { hand = -1.0; }
  let nb = id * 3u;
  outPack[nb] = nrm.x; outPack[nb + 1u] = nrm.y; outPack[nb + 2u] = nrm.z;
  let pb = COUNT() * 3u + id * 3u;
  let p = pos[id].xyz;
  outPack[pb] = p.x; outPack[pb + 1u] = p.y; outPack[pb + 2u] = p.z;
  let tb = COUNT() * 6u + id * 4u;
  outPack[tb] = tng.x; outPack[tb + 1u] = tng.y; outPack[tb + 2u] = tng.z; outPack[tb + 3u] = hand;
}
`;
}

const STRAIN_ITERS = 3;
const RIGID_SWEEPS = 2;
const STRUCTURAL_RELAX = 0.96;  // graph-coloured yarn length solve; 1 = fully inextensible per colour sweep
const SHEAR_FREE = 0.10;       // woven yarns rotate freely at small shear before the weave starts to lock
const U_STRIDE = 256;


export {
  AIR_N,
  AIR_T,
  BEND,
  CELL,
  COUNT,
  COVE_RADIUS,
  COVE_Z_JOIN,
  COVE_Z_WALL,
  DAMP,
  EC,
  ES,
  GROUND_Y,
  HASH,
  M,
  MAX_SUB,
  MU_GROUND,
  MU_SPHERE,
  N,
  RHO,
  RIGID_SWEEPS,
  SCALE,
  SELF_THICK,
  SHEAR_FREE,
  SIZE,
  SLOT,
  SPACING,
  SPHERE_GAP,
  SPHERE_R,
  STRAIN_ITERS,
  STRUCTURAL_RELAX,
  THICKNESS,
  U_STRIDE,
  VMAX,
  buildConstraints,
  makeFabric,
  wgsl,
};
