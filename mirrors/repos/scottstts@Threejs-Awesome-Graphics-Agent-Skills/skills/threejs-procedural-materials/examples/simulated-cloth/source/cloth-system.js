import * as THREE from "three/webgpu";
import {
  AIR_N, AIR_T, CELL, COUNT, DAMP, GROUND_Y, HASH, M, MAX_SUB, MU_GROUND, MU_SPHERE,
  N, RIGID_SWEEPS, SELF_THICK, SLOT, SPACING, SPHERE_GAP, SPHERE_R, STRAIN_ITERS,
  U_STRIDE, VMAX, buildConstraints, makeFabric, wgsl,
} from "./cloth-kernel.js";

/**
 * Creates the woven cloth material and its GPU XPBD state inside a host scene.
 * The host owns the renderer, scene, camera, rigid-collider meshes, and input
 * event listeners. Pointer methods consume normalized device coordinates.
 */
export async function createSimulatedCloth({ renderer, scene, camera }) {
  if (!renderer?.backend?.device) {
    throw new Error("Initialize a WebGPU renderer before creating the cloth system.");
  }

  const fabric = makeFabric();
  const built = buildConstraints();

  const geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.BufferAttribute(built.renderPos, 3));
  geo.setAttribute("normal", new THREE.BufferAttribute(built.renderN, 3));
  geo.setAttribute("tangent", new THREE.BufferAttribute(built.renderT, 4));
  geo.setAttribute("uv", new THREE.BufferAttribute(built.uvs, 2));
  geo.setAttribute("uv2", new THREE.BufferAttribute(built.uvs.slice(), 2));
  geo.setIndex(new THREE.BufferAttribute(built.indices, 1));
  geo.boundingSphere = new THREE.Sphere(new THREE.Vector3(0, 0.5, 0), 4);

  const clothMat = new THREE.MeshPhysicalNodeMaterial({
    color: 0xffffff,
    map: fabric.albedo,
    normalMap: fabric.normal,
    normalScale: new THREE.Vector2(0.8, 0.8),
    roughnessMap: fabric.rough,
    roughness: 1,
    aoMap: fabric.ao,
    aoMapIntensity: 0.75,
    metalness: 0,
    sheen: 0.62,
    sheenColor: new THREE.Color("#f3e6d2"),
    sheenRoughness: 0.42,
    anisotropy: 0.42,
    side: THREE.DoubleSide,
  });
  clothMat.shadowSide = THREE.DoubleSide;
  const cloth = new THREE.Mesh(geo, clothMat);
  cloth.castShadow = true;
  cloth.receiveShadow = true;
  cloth.frustumCulled = false;
  scene.add(cloth);

  let grabbing = false;
  let pointerDown = false;
  let grabGeneration = 0;
  let paused = false;
  let wire = false;
  let acc = 0;
  const device = renderer.backend.device;
  const onUncapturedError = (ev) => console.error(ev.error?.message || ev.error || 'WebGPU error');
  device.addEventListener('uncapturederror', onUncapturedError);
  renderer.backend.createAttribute(geo.attributes.position);
  renderer.backend.createAttribute(geo.attributes.normal);
  renderer.backend.createAttribute(geo.attributes.tangent);
  const positionBuf = renderer.backend.get(geo.attributes.position).buffer;
  const normalBuf = renderer.backend.get(geo.attributes.normal).buffer;
  const tangentBuf = renderer.backend.get(geo.attributes.tangent).buffer;

  const module = device.createShaderModule({ label: 'cloth-xpbd', code: wgsl() });
  const compiled = await module.getCompilationInfo();
  const errors = compiled.messages.filter((m) => m.type === 'error');
  if (errors.length) throw new Error(errors.map((m) => `L${m.lineNum}: ${m.message}`).join('\n'));

  const layout = device.createBindGroupLayout({
    entries: [
      { binding: 0, visibility: GPUShaderStage.COMPUTE, buffer: { type: 'uniform', hasDynamicOffset: true, minBindingSize: U_STRIDE } },
      { binding: 1, visibility: GPUShaderStage.COMPUTE, buffer: { type: 'storage' } },
      { binding: 2, visibility: GPUShaderStage.COMPUTE, buffer: { type: 'storage' } },
      { binding: 3, visibility: GPUShaderStage.COMPUTE, buffer: { type: 'storage' } },
      { binding: 4, visibility: GPUShaderStage.COMPUTE, buffer: { type: 'read-only-storage' } },
      { binding: 5, visibility: GPUShaderStage.COMPUTE, buffer: { type: 'storage' } },
      { binding: 6, visibility: GPUShaderStage.COMPUTE, buffer: { type: 'storage' } },
      { binding: 7, visibility: GPUShaderStage.COMPUTE, buffer: { type: 'storage' } },
    ],
  });
  const pipelineLayout = device.createPipelineLayout({ bindGroupLayouts: [layout] });
  const pipe = (name) => device.createComputePipeline({
    label: name,
    layout: pipelineLayout,
    compute: { module, entryPoint: name },
  });
  const pipelines = {
    integrate: pipe('integrate'),
    velocity: pipe('velocity'),
    strain: pipe('strain'),
    struct_h_even: pipe('struct_h_even'),
    struct_h_odd: pipe('struct_h_odd'),
    struct_v_even: pipe('struct_v_even'),
    struct_v_odd: pipe('struct_v_odd'),
    bend_h_0: pipe('bend_h_0'), bend_h_1: pipe('bend_h_1'), bend_h_2: pipe('bend_h_2'),
    bend_v_0: pipe('bend_v_0'), bend_v_1: pipe('bend_v_1'), bend_v_2: pipe('bend_v_2'),
    apply_delta: pipe('apply_delta'),
    apply_contact_delta: pipe('apply_contact_delta'),
    collide_rigid: pipe('collide_rigid'),
    clear_tri_hash: pipe('clear_tri_hash'),
    clear_edge_hash: pipe('clear_edge_hash'),
    insert_tris: pipe('insert_tris'),
    insert_edges: pipe('insert_edges'),
    solve_point_tri: pipe('solve_point_tri'),
    solve_edge_edge: pipe('solve_edge_edge'),
    collide_edge_sphere: pipe('collide_edge_sphere'),
    collide_tri_sphere: pipe('collide_tri_sphere'),
    pack: pipe('pack'),
  };

  const buffers = {
    pos: device.createBuffer({ label: 'pos', size: COUNT * 16, usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_SRC | GPUBufferUsage.COPY_DST }),
    state: device.createBuffer({ label: 'state', size: COUNT * 64, usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST }),
    delta: device.createBuffer({ label: 'delta', size: COUNT * 16, usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST }),
    cons: device.createBuffer({ label: 'cons', size: Math.max(16, built.cons.byteLength), usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST }),
    hcount: device.createBuffer({ label: 'hcount', size: (HASH * 2 + 4) * 4, usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST }),
    hdata: device.createBuffer({ label: 'hdata', size: 2 * HASH * SLOT * 4, usage: GPUBufferUsage.STORAGE }),
    out: device.createBuffer({ label: 'out', size: COUNT * 40, usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_SRC | GPUBufferUsage.COPY_DST }),
    uniform: device.createBuffer({ label: 'uniform', size: MAX_SUB * U_STRIDE, usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST }),
  };
  device.queue.writeBuffer(buffers.pos, 0, built.pos);
  device.queue.writeBuffer(buffers.cons, 0, built.cons);
  const nrmInit = new Float32Array(COUNT * 3);
  for (let i = 0; i < COUNT; i++) nrmInit[i * 3 + 1] = 1;
  device.queue.writeBuffer(buffers.out, 0, nrmInit);
  // Seed the previous-render position region used by full-frame self-contact
  // history; otherwise frame zero would compare the cloth against (0,0,0).
  device.queue.writeBuffer(buffers.out, COUNT * 12, built.renderPos);

  const bind = device.createBindGroup({
    layout,
    entries: [
      { binding: 0, resource: { buffer: buffers.uniform, size: U_STRIDE } },
      { binding: 1, resource: { buffer: buffers.pos } },
      { binding: 2, resource: { buffer: buffers.state } },
      { binding: 3, resource: { buffer: buffers.delta } },
      { binding: 4, resource: { buffer: buffers.cons } },
      { binding: 5, resource: { buffer: buffers.hcount } },
      { binding: 6, resource: { buffer: buffers.hdata } },
      { binding: 7, resource: { buffer: buffers.out } },
    ],
  });

  const uniformData = new Float32Array(MAX_SUB * (U_STRIDE / 4));
  function writeUniforms(frameDt, substeps) {
    const subDt = frameDt / substeps;
    for (let s = 0; s < substeps; s++) {
      const o = s * (U_STRIDE / 4);
      uniformData[o + 0] = subDt;
      uniformData[o + 1] = s + 1;
      uniformData[o + 2] = substeps;
      uniformData[o + 3] = -9.81;
      uniformData[o + 4] = 0;
      uniformData[o + 5] = SPHERE_R + SPHERE_GAP + GROUND_Y; // inflated collider tangent to the offset cove floor
      uniformData[o + 6] = 0;
      uniformData[o + 7] = SPHERE_R + SPHERE_GAP;
      uniformData[o + 8] = MU_SPHERE;
      uniformData[o + 9] = MU_GROUND;
      uniformData[o + 10] = SELF_THICK;
      uniformData[o + 11] = CELL;
      uniformData[o + 12] = GROUND_Y;
      uniformData[o + 13] = AIR_N;
      uniformData[o + 14] = AIR_T;
      uniformData[o + 15] = DAMP;
      uniformData[o + 16] = built.triCount;
      uniformData[o + 17] = built.bendCount;
      uniformData[o + 18] = built.edgeCount;
      uniformData[o + 19] = built.bendBase;
      uniformData[o + 20] = built.edgeBase;
      uniformData[o + 21] = HASH;
      uniformData[o + 22] = SLOT;
      uniformData[o + 23] = VMAX;
      uniformData[o + 24] = SPACING;
      uniformData[o + 25] = N;
      uniformData[o + 26] = M;
      uniformData[o + 27] = COUNT;
      uniformData[o + 28] = grabbing ? 1 : 0;
    }
    device.queue.writeBuffer(buffers.uniform, 0, uniformData.subarray(0, substeps * (U_STRIDE / 4)));
  }

  const readback = device.createBuffer({ size: COUNT * 16, usage: GPUBufferUsage.COPY_DST | GPUBufferUsage.MAP_READ });
  let readPending = false;
  async function readPositions() {
    if (readPending) return null;
    readPending = true;
    try {
      const enc = device.createCommandEncoder();
      enc.copyBufferToBuffer(buffers.pos, 0, readback, 0, COUNT * 16);
      device.queue.submit([enc.finish()]);
      await readback.mapAsync(GPUMapMode.READ);
      const copy = new Float32Array(readback.getMappedRange().slice(0));
      readback.unmap();
      return copy;
    } finally {
      readPending = false;
    }
  }

  function simulate(frameDt) {
    // The graph-coloured yarn solve uses 240 Hz positional integration. The
    // expensive spatial-hash self-contact is reserved for the final substep.
    let substeps = Math.round(frameDt / (1 / 240));
    substeps = Math.max(3, Math.min(6, substeps));
    if (grabbing) {
      pin0.set(committed);
      writePins();
      committed.set(pin1);
    }
    writeUniforms(frameDt, substeps);
    const enc = device.createCommandEncoder({ label: 'cloth-step' });
    const hashGroups = Math.ceil(HASH / 64);
    for (let s = 0; s < substeps; s++) {
      const off = [s * U_STRIDE];
      const pass = (name, count) => {
        const p = enc.beginComputePass();
        p.setPipeline(pipelines[name]);
        p.setBindGroup(0, bind, off);
        p.dispatchWorkgroups(Math.ceil(count / 64));
        p.end();
      };
      pass('integrate', COUNT);
      for (let it = 0; it < STRAIN_ITERS; it++) {
        pass('struct_h_even', COUNT);
        pass('struct_h_odd', COUNT);
        pass('struct_v_even', COUNT);
        pass('struct_v_odd', COUNT);
        // Shear and bending are both Jacobi corrections; accumulate them into
        // the same delta buffer and apply once. This saves a full global
        // read/write pass per solver iteration without changing their models.
        pass('strain', built.triCount);
        pass('apply_delta', COUNT);
        pass('bend_h_' + it, built.bendCount);
        pass('bend_v_' + it, built.bendCount);
      }
      pass('collide_rigid', COUNT);

      // Broad-phase self collision is the most expensive part of this demo.
      // It is position based, so solving it once after the final substep gives
      // the same visible 60 Hz contact result while avoiding rebuilding and
      // scanning two 3-D hashes four times per frame.
      {
        const hc = enc.beginComputePass();
        hc.setPipeline(pipelines.clear_tri_hash);
        hc.setBindGroup(0, bind, off);
        hc.dispatchWorkgroups(hashGroups);
        hc.end();
        pass('insert_tris', built.triCount);
        pass('solve_point_tri', COUNT);
        pass('apply_contact_delta', COUNT);

        const hc2 = enc.beginComputePass();
        hc2.setPipeline(pipelines.clear_edge_hash);
        hc2.setBindGroup(0, bind, off);
        hc2.dispatchWorkgroups(hashGroups);
        hc2.end();
        pass('insert_edges', built.edgeCount);
        pass('solve_edge_edge', built.edgeCount);
        pass('apply_contact_delta', COUNT);

        // Triangle/sphere is only needed as a final surface-level guard. Vertex
        // rigid collision already runs every substep; repeating the expensive
        // triangle test in every substep was redundant.
        for (let k = 0; k < RIGID_SWEEPS; k++) {
          pass('collide_rigid', COUNT);
          pass('collide_tri_sphere', built.triCount);
          pass('apply_delta', COUNT);
        }
      }
      pass('collide_rigid', COUNT);
      pass('velocity', COUNT);
    }
    const packPass = enc.beginComputePass();
    packPass.setPipeline(pipelines.pack);
    packPass.setBindGroup(0, bind, [0]);
    packPass.dispatchWorkgroups(Math.ceil(COUNT / 64));
    packPass.end();
    enc.copyBufferToBuffer(buffers.out, 0, normalBuf, 0, COUNT * 12);
    enc.copyBufferToBuffer(buffers.out, COUNT * 12, positionBuf, 0, COUNT * 12);
    enc.copyBufferToBuffer(buffers.out, COUNT * 24, tangentBuf, 0, COUNT * 16);
    device.queue.submit([enc.finish()]);
  }


  const pin0 = new Float32Array(COUNT * 4);
  const pin1 = new Float32Array(COUNT * 4);
  let pinnedIds = [];
  let grabOffsets = new Float32Array(0);
  const committed = new Float32Array(COUNT * 4);
  const grabPlane = new THREE.Plane();
  const mouseTarget = new THREE.Vector3();
  const planeN = new THREE.Vector3();
  const raycaster = new THREE.Raycaster();

  function writePins() {
    device.queue.writeBuffer(buffers.state, 2 * COUNT * 16, pin0);
    device.queue.writeBuffer(buffers.state, 3 * COUNT * 16, pin1);
  }
  function clearPins() {
    pin0.fill(0);
    pin1.fill(0);
    pinnedIds = [];
    grabbing = false;
    writePins();
  }
  function resetCloth() {
    pointerDown = false;
    grabGeneration++;
    device.queue.writeBuffer(buffers.pos, 0, built.pos);
    const zeros = new Float32Array(COUNT * 4);
    device.queue.writeBuffer(buffers.state, 0, zeros);
    device.queue.writeBuffer(buffers.state, COUNT * 16, zeros);
    device.queue.writeBuffer(buffers.out, COUNT * 12, built.renderPos);
    clearPins();
    acc = 0;
  }

  function mt(origin, dir, pos, i0, i1, i2) {
    const ax = pos[i0 * 4], ay = pos[i0 * 4 + 1], az = pos[i0 * 4 + 2];
    const bx = pos[i1 * 4], by = pos[i1 * 4 + 1], bz = pos[i1 * 4 + 2];
    const cx = pos[i2 * 4], cy = pos[i2 * 4 + 1], cz = pos[i2 * 4 + 2];
    const e1x = bx - ax, e1y = by - ay, e1z = bz - az;
    const e2x = cx - ax, e2y = cy - ay, e2z = cz - az;
    const px = dir.y * e2z - dir.z * e2y;
    const py = dir.z * e2x - dir.x * e2z;
    const pz = dir.x * e2y - dir.y * e2x;
    const det = e1x * px + e1y * py + e1z * pz;
    if (Math.abs(det) < 1e-8) return null;
    const inv = 1 / det;
    const tx = origin.x - ax, ty = origin.y - ay, tz = origin.z - az;
    const u = (tx * px + ty * py + tz * pz) * inv;
    if (u < 0 || u > 1) return null;
    const qx = ty * e1z - tz * e1y;
    const qy = tz * e1x - tx * e1z;
    const qz = tx * e1y - ty * e1x;
    const v = (tx * qx + ty * qy + tz * qz) * inv;
    if (v < 0 || u + v > 1) return null;
    const t = (e2x * qx + e2y * qy + e2z * qz) * inv;
    return t > 1e-4 ? t : null;
  }

  async function beginGrab(ndc) {
    const request = ++grabGeneration;
    pointerDown = true;
    raycaster.setFromCamera(ndc, camera);
    const positions = await readPositions();
    if (request !== grabGeneration || !pointerDown) return false;
    if (!positions) {
      pointerDown = false;
      return false;
    }

    const o = raycaster.ray.origin, d = raycaster.ray.direction;
    let bestT = 1e9, best = -1;
    const index = built.indices;
    const meshR2 = SPHERE_R * SPHERE_R * 0.985;
    for (let t = 0; t < index.length; t += 3) {
      const hit = mt(o, d, positions, index[t], index[t + 1], index[t + 2]);
      if (hit === null || hit >= bestT) continue;
      const hx = o.x + d.x * hit, hy = o.y + d.y * hit, hz = o.z + d.z * hit;
      const sx = hx, sy = hy - SPHERE_R, sz = hz;
      if (sx * sx + sy * sy + sz * sz < meshR2) continue;
      let bd = 1e9, bi = index[t];
      for (const id of [index[t], index[t + 1], index[t + 2]]) {
        const dx = positions[id * 4] - hx, dy = positions[id * 4 + 1] - hy, dz = positions[id * 4 + 2] - hz;
        const dd = dx * dx + dy * dy + dz * dz;
        if (dd < bd) { bd = dd; bi = id; }
      }
      if (bd > SPACING * SPACING * 4) continue;
      bestT = hit;
      best = bi;
    }
    if (!pointerDown || best < 0) {
      pointerDown = false;
      return false;
    }

    const ci = best % N, cj = (best / N) | 0;
    const cx = positions[best * 4], cy = positions[best * 4 + 1], cz = positions[best * 4 + 2];
    pinnedIds = [];
    pin0.fill(0);
    pin1.fill(0);
    const reach2 = SPACING * SPACING * 6.25;
    for (let dj = -1; dj <= 1; dj++) {
      for (let di = -1; di <= 1; di++) {
        const i = ci + di, j = cj + dj;
        if (i < 0 || j < 0 || i >= N || j >= M) continue;
        const id = j * N + i;
        const ox = positions[id * 4] - cx;
        const oy = positions[id * 4 + 1] - cy;
        const oz = positions[id * 4 + 2] - cz;
        if (ox * ox + oy * oy + oz * oz > reach2) continue;
        pinnedIds.push(id);
        pin0[id * 4] = positions[id * 4];
        pin0[id * 4 + 1] = positions[id * 4 + 1];
        pin0[id * 4 + 2] = positions[id * 4 + 2];
        pin0[id * 4 + 3] = 1;
        pin1[id * 4] = positions[id * 4];
        pin1[id * 4 + 1] = positions[id * 4 + 1];
        pin1[id * 4 + 2] = positions[id * 4 + 2];
        pin1[id * 4 + 3] = 1;
      }
    }
    grabOffsets = new Float32Array(pinnedIds.length * 3);
    pinnedIds.forEach((id, k) => {
      grabOffsets[k * 3] = positions[id * 4] - cx;
      grabOffsets[k * 3 + 1] = positions[id * 4 + 1] - cy;
      grabOffsets[k * 3 + 2] = positions[id * 4 + 2] - cz;
    });
    camera.getWorldDirection(planeN);
    grabPlane.setFromNormalAndCoplanarPoint(planeN, new THREE.Vector3(cx, cy, cz));
    mouseTarget.set(cx, cy, cz);
    committed.set(pin1);
    grabbing = true;
    writePins();
    return true;
  }

  function moveGrab(ndc) {
    if (!grabbing) return false;
    raycaster.setFromCamera(ndc, camera);
    if (!raycaster.ray.intersectPlane(grabPlane, mouseTarget)) return false;
    pinnedIds.forEach((id, k) => {
      pin1[id * 4] = mouseTarget.x + grabOffsets[k * 3];
      pin1[id * 4 + 1] = mouseTarget.y + grabOffsets[k * 3 + 1];
      pin1[id * 4 + 2] = mouseTarget.z + grabOffsets[k * 3 + 2];
      pin1[id * 4 + 3] = 1;
    });
    return true;
  }

  function endGrab() {
    pointerDown = false;
    grabGeneration++;
    if (grabbing) clearPins();
  }

  let lastMode = "final";
  const debugMaterials = {
    final: clothMat,
    albedo: new THREE.MeshBasicMaterial({ map: fabric.albedo, side: THREE.DoubleSide }),
    normal: new THREE.MeshBasicMaterial({ map: fabric.normal, side: THREE.DoubleSide }),
    roughness: new THREE.MeshBasicMaterial({ map: fabric.rough, side: THREE.DoubleSide }),
    occlusion: new THREE.MeshBasicMaterial({ map: fabric.ao, side: THREE.DoubleSide }),
  };
  function setDebugMode(mode) {
    if (!Object.hasOwn(debugMaterials, mode)) return;
    lastMode = mode;
    cloth.material = debugMaterials[mode];
  }

  function update(deltaSeconds) {
    const raw = Math.min(0.05, Math.max(0, deltaSeconds)) || 0.016;
    if (!paused) {
      acc += raw;
      let guard = 0;
      while (acc >= 1 / 60 && guard < 2) {
        simulate(1 / 60);
        acc -= 1 / 60;
        guard++;
      }
      if (acc > 1 / 30) acc = 1 / 30;
    }
  }

  function togglePaused() { paused = !paused; return paused; }
  function setPaused(value) { paused = Boolean(value); }
  function setWireframe(value) { wire = Boolean(value); clothMat.wireframe = wire; }
  function dispose() {
    device.removeEventListener('uncapturederror', onUncapturedError);
    scene.remove(cloth);
    geo.dispose();
    clothMat.dispose();
    for (const [name, material] of Object.entries(debugMaterials)) {
      if (name !== "final") material.dispose();
    }
    for (const texture of Object.values(fabric)) texture.dispose?.();
    for (const buffer of Object.values(buffers)) buffer.destroy?.();
    readback.destroy?.();
  }

  return {
    mesh: cloth,
    geometry: geo,
    material: clothMat,
    textures: fabric,
    update,
    beginGrab,
    moveGrab,
    endGrab,
    reset: resetCloth,
    togglePaused,
    setPaused,
    setWireframe,
    setDebugMode,
    get paused() { return paused; },
    get wireframe() { return wire; },
    get debugMode() { return lastMode; },
    dispose,
  };
}
