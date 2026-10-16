import { Renderer, DEFAULT_CAMERA, cameraMatrices, type CameraState } from './rendering/renderer';
import { add, dot, normalize, scale, sub, transformPoint, type Vec3 } from './rendering/math';
import { Interaction, MAX_GRIPS } from './simulation/gpu/interaction';
import { Hand, PointerTrack } from './simulation/hand';
import { GPU_DEFAULTS, GpuSolver, RELEASE_REFINEMENT } from './simulation/gpu/solver';
import { loadDrape, settleDrape } from './simulation/gpu/settle';
import { Topology } from './simulation/gpu/topology';
import { compileScene, defaultSceneSpecs } from './simulation/fabric-config';

const H = GPU_DEFAULTS.h;
const MAX_SUBSTEPS_PER_FRAME = 5;
const REST_SPEED = 0.003;
const REST_TIME = 0.4;
const WHEEL_DEPTH = 0.00006;
const ALL_POINTERS = -1;

export interface PointerCommand {
  phase: 'down' | 'move' | 'up' | 'cancel';
  id: number;
  /** Milliseconds on the same clock as update(now). */
  time: number;
  x: number;
  y: number;
}

interface GripState {
  slot: number;
  node: number;
  hand: Hand;
  track: PointerTrack;
  /** The drag plane: through the picked point, facing the camera (normal = camera forward). */
  plane: Vec3;
  normal: Vec3;
  /** Where the pointer's ray met the plane when it went down (drag origin). */
  downPoint: Vec3;
}

/** Yarn mechanics, gripping and rendering. The caller owns device and frame scheduling. */
export class TearableDenim {
  readonly scene = compileScene(defaultSceneSpecs());
  readonly solver: GpuSolver;
  readonly interaction: Interaction;
  readonly topology: Topology;
  readonly renderer: Renderer;
  camera: CameraState = { ...DEFAULT_CAMERA, target: [...DEFAULT_CAMERA.target] };
  private width = 1;
  private height = 1;
  private cssWidth = 1;
  private cssHeight = 1;
  private ready = false;
  private simBacklog = 0;
  private refineSteps = 0;
  private releaseEpoch = 0;
  private topologyEvents = 0;
  private readonly grips = new Map<number, GripState>();
  private readonly down = new Map<number, PointerTrack>();
  private readonly picking = new Map<number, number>();
  private pickToken = 0;
  private snapshot: { x: GPUBuffer; segs: GPUBuffer; tails: GPUBuffer; field: GPUBuffer } | null = null;
  private asleep = true;
  private restFor = 0;
  private speedProbe: GPUBuffer;
  private probeBusy = false;
  private probeSteps = 0;
  private dirty = true;

  constructor(readonly device: GPUDevice, format: GPUTextureFormat) {
    this.solver = new GpuSolver(device, this.scene, { ...GPU_DEFAULTS });
    this.interaction = new Interaction(device, this.solver, this.scene);
    this.solver.preSubstep = pass => this.interaction.encodeSubstep(pass);
    this.solver.preAssemble = dispatch => this.interaction.encode(dispatch);
    this.topology = new Topology(device, this.solver, this.scene, () => this.interaction.coreNodes);
    this.renderer = new Renderer(device, format, this.solver, this.scene);
    this.speedProbe = device.createBuffer({ label: 'speedProbe', size: 16, usage: GPUBufferUsage.COPY_DST | GPUBufferUsage.MAP_READ });
  }

  async initialize(drape: ArrayBuffer | null = null): Promise<void> {
    await this.settle(drape);
    await this.topology.request();
    this.ready = true;
    this.asleep = true;
  }

  setSize(width: number, height: number, cssWidth: number, cssHeight: number): void {
    this.width = width; this.height = height;
    this.cssWidth = cssWidth; this.cssHeight = cssHeight;
    this.renderer.resize(width, height);
  }

  get gripping(): boolean { return this.grips.size > 0; }
  get sleeping(): boolean { return this.asleep; }
  setDebugMode(mode: string): void {
    this.renderer.debugMode = ({ normals: 1, wear: 2, presence: 3 } as Record<string, number>)[mode] ?? 0;
  }
  cancelPointers(): void { this.releaseAll(); }

  /** Load (or compute) the settled drape, then keep the validated state as the reset snapshot. */
  private async settle(drape: ArrayBuffer | null): Promise<void> {
    const loaded = drape !== null && loadDrape(this.solver, drape);
    if (!loaded) await settleDrape(this.device, this.solver);
    const copy = (src: GPUBuffer, label: string) => this.device.createBuffer({ label, size: src.size, usage: GPUBufferUsage.COPY_SRC | GPUBufferUsage.COPY_DST });
    this.snapshot = { x: copy(this.solver.x, 'snap.x'), segs: copy(this.solver.segs, 'snap.segs'), tails: copy(this.solver.tails, 'snap.tails'), field: copy(this.solver.field, 'snap.field') };
    const enc = this.device.createCommandEncoder();
    enc.copyBufferToBuffer(this.solver.x, 0, this.snapshot.x, 0, this.solver.x.size);
    enc.copyBufferToBuffer(this.solver.segs, 0, this.snapshot.segs, 0, this.solver.segs.size);
    enc.copyBufferToBuffer(this.solver.tails, 0, this.snapshot.tails, 0, this.solver.tails.size);
    enc.copyBufferToBuffer(this.solver.field, 0, this.snapshot.field, 0, this.solver.field.size);
    this.device.queue.submit([enc.finish()]);
    await this.device.queue.onSubmittedWorkDone();
  }


  reset(): void {
    if (!this.snapshot) return;
    this.releaseAll();
    this.releaseEpoch++;
    this.interaction.releaseAll();
    const enc = this.device.createCommandEncoder({ label: 'reset' });
    enc.copyBufferToBuffer(this.snapshot.x, 0, this.solver.x, 0, this.solver.x.size);
    enc.copyBufferToBuffer(this.snapshot.segs, 0, this.solver.segs, 0, this.solver.segs.size);
    enc.copyBufferToBuffer(this.snapshot.tails, 0, this.solver.tails, 0, this.solver.tails.size);
    enc.copyBufferToBuffer(this.snapshot.field, 0, this.solver.field, 0, this.solver.field.size);
    enc.clearBuffer(this.solver.v);
    enc.clearBuffer(this.solver.ext);
    enc.clearBuffer(this.solver.counters);
    enc.clearBuffer(this.solver.acousticSources);
    this.renderer.resetTopology(enc);
    this.device.queue.submit([enc.finish()]);
    this.topology.reset();
    void this.topology.request();
    this.topologyEvents = 0;
    this.simBacklog = 0;
    this.refineSteps = 0;
    this.asleep = true;
    this.dirty = true;
  }


  private wake(): void {
    if (this.asleep) {
      this.asleep = false;
      this.restFor = 0;
      this.simBacklog = 0;
    }
  }

  private ray(cssX: number, cssY: number): { origin: Vec3; dir: Vec3 } {
    const m = cameraMatrices(this.camera, this.width / this.height);
    const nx = (cssX / this.cssWidth) * 2 - 1;
    const ny = 1 - (cssY / this.cssHeight) * 2;
    const a = transformPoint(m.invViewProj, [nx, ny, 0]);
    const b = transformPoint(m.invViewProj, [nx, ny, 1]);
    const p0: Vec3 = [a[0] / a[3], a[1] / a[3], a[2] / a[3]];
    const p1: Vec3 = [b[0] / b[3], b[1] / b[3], b[2] / b[3]];
    return { origin: p0, dir: normalize(sub(p1, p0)) };
  }

  pointer(c: PointerCommand): void {
    if (!this.ready) return;
    const sample = { time: c.time, x: c.x, y: c.y };
    if (c.phase === 'cancel' && c.id === ALL_POINTERS) {
      this.releaseAll();
    } else if (c.phase === 'down') {
      // a release still waiting for its substep ends now: the finger is down again
      if ((this.grips.get(c.id)?.track.upTime ?? Infinity) < Infinity) this.endGrip(c.id);
      // one grip per finger, as many fingers as there are grip slots
      if (this.down.has(c.id) || this.down.size >= MAX_GRIPS) return;
      this.down.set(c.id, new PointerTrack(sample));
      void this.beginGrip(c.id, sample);
    } else if (c.phase === 'move') {
      this.down.get(c.id)?.add(sample);
    } else if (c.phase === 'up' && this.grips.has(c.id)) {
      // the grip ends at the substep that reaches the release in input time (stepHandles)
      this.down.get(c.id)?.add(sample);
      this.grips.get(c.id)!.track.upTime = sample.time;
    } else {
      this.down.delete(c.id);
      this.picking.delete(c.id);
      this.endGrip(c.id);
    }
  }

  private async beginGrip(id: number, at: { x: number; y: number }): Promise<void> {
    const token = ++this.pickToken;
    this.picking.set(id, token);
    const m = cameraMatrices(this.camera, this.width / this.height);
    const px = (at.x / this.cssWidth) * this.width;
    const py = (at.y / this.cssHeight) * this.height;
    // larger than the projected node spacing (~3.5 mm cells, ~1.1% of the view height)
    const radius = Math.max(8, 0.016 * this.height);
    const hit = await this.interaction.pickAt(m.viewProj, px, py, this.width, this.height, radius);
    if (this.picking.get(id) !== token) return;
    this.picking.delete(id);
    const track = this.down.get(id);
    if (!hit || !track) return;
    // a finger on material another finger already pinches holds nothing more
    if (this.interaction.holder(hit.node) >= 0) return;
    const slot = this.interaction.freeSlot();
    const p = hit.position as Vec3;
    if (slot < 0 || !this.interaction.attach(hit.node, p, slot, hit.window)) return;
    const forward = normalize(sub(this.camera.target, m.eye));
    const g: GripState = { slot, node: hit.node, hand: new Hand(p, scale(forward, -1)), track, plane: p, normal: forward, downPoint: p };
    g.downPoint = this.planePoint(g, track.first) ?? p;
    this.grips.set(id, g);
    this.wake();
  }

  /** Where the pointer's ray at CSS (x, y) meets the grip's drag plane. */
  private planePoint(g: GripState, at: { x: number; y: number }): Vec3 | null {
    const { origin, dir } = this.ray(at.x, at.y);
    const denom = dot(dir, g.normal);
    if (Math.abs(denom) < 1e-6) return null;
    return add(origin, scale(dir, dot(sub(g.plane, origin), g.normal) / denom));
  }

  private endGrip(id: number): void {
    this.down.delete(id);
    const g = this.grips.get(id);
    if (!g) return;
    this.grips.delete(id);
    // a released finger is silent at once (only a held tear is heard)
    // pieces held only by this grip are freed first; the fingers open once that has applied (at most a
    // frame later), with the solve refined over the snap that follows
    this.interaction.letGo(g.slot);
    const epoch = this.releaseEpoch;
    void this.topology.request().then(() => {
      if (epoch !== this.releaseEpoch) return;
      this.interaction.release(g.slot);
      this.refineSteps = Math.round(RELEASE_REFINEMENT.duration / H);
    });
  }

  /** Release every grip and forget every pointer (cancel, reset, hidden page). */
  private releaseAll(): void {
    this.pickToken++;
    this.picking.clear();
    for (const id of [...this.grips.keys()]) this.endGrip(id);
    this.down.clear();
  }

  wheel(deltaY: number): void {
    if (this.grips.size > 0) {
      for (const g of this.grips.values()) g.hand.wheel(-deltaY * WHEEL_DEPTH);
    } else {
      this.camera.distance = Math.max(0.3, Math.min(1.15, this.camera.distance * Math.exp(deltaY * 0.0008)));
      this.dirty = true;
    }
  }

  /** Newton iterations the next substep must run at least (0: the schedule's own). */
  private substepIterations(): number {
    if (this.refineSteps <= 0) return 0;
    this.refineSteps--;
    return RELEASE_REFINEMENT.newtonIterations;
  }

  /**
   * Advance every grip's handle by one substep toward its pointer at input time `t` (shared clock);
   * a pointer that went up by then releases its grip before the substep.
   */
  private stepHandles(h: number, t: number): void {
    for (const [id, g] of [...this.grips]) {
      if (g.track.upTime <= t) {
        this.endGrip(id);
        continue;
      }
      const p = this.planePoint(g, g.track.at(t));
      g.track.prune(t);
      g.hand.step(h, p ? sub(p, g.downPoint) : [0, 0, 0]);
      this.interaction.setTarget(g.hand.target, g.slot);
      this.interaction.setPinch(g.hand.pinch, g.slot);
    }
  }



  /** Asynchronously read the largest nodal speed since the last probe (rest detection). */
  private probeRest(steps: number): void {
    if (this.probeBusy || !this.speedProbe) {
      this.probeSteps += steps;
      return;
    }
    const probe = this.speedProbe;
    const window = (this.probeSteps + steps) * H;
    this.probeSteps = 0;
    this.probeBusy = true;
    const enc = this.device.createCommandEncoder({ label: 'restProbe' });
    enc.copyBufferToBuffer(this.solver.counters, 0, probe, 0, 16);
    enc.clearBuffer(this.solver.counters, 8, 4);
    this.device.queue.submit([enc.finish()]);
    probe.mapAsync(GPUMapMode.READ).then(
      () => {
        const range = probe.getMappedRange();
        const speed = new Float32Array(range)[2];
        const c = new Uint32Array(range, 0, 2);
        const events = c[0] + c[1];
        probe.unmap();
        if (events !== this.topologyEvents) {
          this.topologyEvents = events;
          void this.topology.request();
        }
        this.probeBusy = false;
        if (this.grips.size > 0 || this.asleep) {
          this.restFor = 0;
          return;
        }
        this.restFor = speed < REST_SPEED ? this.restFor + window : 0;
        if (this.restFor >= REST_TIME) this.asleep = true;
      },
      () => (this.probeBusy = false),
    );
  }


  /** Fixed 1/120 s substeps; overload drops backlog beyond five substeps per frame. */
  update(delta: number, now: number): void {
    if (!this.ready || delta <= 0 || this.asleep) return;
    const dt = Math.min(0.1, delta);
    this.simBacklog += dt;
    let steps = Math.floor(this.simBacklog / H);
    if (steps > MAX_SUBSTEPS_PER_FRAME) { steps = MAX_SUBSTEPS_PER_FRAME; this.simBacklog = 0; }
    else this.simBacklog -= steps * H;
    for (let k = 0; k < steps; k++) {
      this.stepHandles(H, now - 1000 * dt * (1 - (k + 1) / steps));
      const encoder = this.device.createCommandEncoder({ label: 'substep' });
      this.solver.encodeSubstep(encoder, this.substepIterations());
      this.device.queue.submit([encoder.finish()]);
    }
    if (steps > 0) this.probeRest(steps);
  }

  encode(encoder: GPUCommandEncoder, target: GPUTextureView, time: number): void {
    this.renderer.encode(encoder, this.camera, time, target);
  }

  /** Release only owned readback/snapshot state; the caller disposes its dedicated device. */
  dispose(): void {
    this.ready = false;
    this.releaseEpoch++;
    this.pickToken++;
    this.topology.reset();
    this.grips.clear(); this.down.clear(); this.picking.clear();
    this.speedProbe.destroy();
    if (this.snapshot) for (const buffer of Object.values(this.snapshot)) buffer.destroy();
  }
}
