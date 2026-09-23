import { SAND, idleStroke, type Point, type Stroke } from '../config'

type TimedPoint = Point & { time: number }
type Track = {
  held: boolean
  pressure: number
  start: TimedPoint
  latest: TimedPoint
  latestTime: number | undefined
  segments: Stroke[]
}

const minimumSampleSeconds = 0.0001
const nonAdvancingSampleSeconds = SAND.step * 0.5
const minimumMovement = 1e-7
// Keep enough queued geometry for a legitimate fast stroke while still bounding
// pathological replay after a GPU stall. The solver can consume maxContacts per
// substep and maxSteps per rendered frame, so this caps a pointer at four
// rendered frames of pending contact work rather than a single frame.
export const maxQueuedSegmentsPerPointer = SAND.maxContacts * SAND.maxSteps * 4

export class StrokeQueue {
  private readonly tracks = new Map<number, Track>()
  private roundRobin = 0
  private currentPressure = 0.7
  position: Point = { x: 0, y: 0 }
  radius: number = SAND.radius

  begin(point: Point, pressure: number, time?: number, pointerId = 0) {
    const bounded = this.bound(point)
    const existing = this.tracks.get(pointerId)
    const timestamp = this.timestamp(existing, time)
    const start = { ...bounded, time: timestamp }
    this.position = bounded
    this.currentPressure = this.clampPressure(pressure)
    this.tracks.set(pointerId, {
      held: true,
      pressure: this.currentPressure,
      start,
      latest: start,
      latestTime: timestamp,
      segments: existing?.segments ?? [],
    })
  }

  move(point: Point, pressure: number, time?: number, pointerId = 0) {
    const bounded = this.bound(point)
    this.position = bounded
    this.currentPressure = this.clampPressure(pressure)
    const track = this.tracks.get(pointerId)
    if (!track || !track.held) return
    const timestamp = this.timestamp(track, time)
    track.pressure = this.currentPressure
    track.latestTime = timestamp
    track.latest = { ...bounded, time: timestamp }
    this.subdivide(track)
  }

  end(pointerId = 0) {
    const track = this.tracks.get(pointerId)
    if (!track) return
    track.held = false
    this.flush(track)
    this.prune(pointerId, track)
  }

  cancel(pointerId?: number) {
    if (pointerId === undefined) {
      this.tracks.clear()
      this.roundRobin = 0
      return
    }
    this.tracks.delete(pointerId)
    if (this.roundRobin >= this.tracks.size) this.roundRobin = 0
  }

  private clampPressure(pressure: number) { return Math.max(0.1, Math.min(1, pressure)) }

  private bound(point: Point) {
    const limit = SAND.extent / 2 - 0.03
    return { x: Math.max(-limit, Math.min(limit, point.x)), y: Math.max(-limit, Math.min(limit, point.y)) }
  }

  private timestamp(track: Track | undefined, time?: number) {
    const previous = track?.latestTime
    const fallback = (previous ?? -SAND.step * 1000) + SAND.step * 1000
    const candidate = time !== undefined && Number.isFinite(time) ? time : fallback
    return previous === undefined ? candidate : Math.max(previous, candidate)
  }

  private spacing() { return Math.max(SAND.extent / SAND.resolution * 1.5, this.radius * 0.5) }

  private makeStroke(from: TimedPoint, to: TimedPoint, pressure: number): Stroke {
    const rawDuration = (to.time - from.time) / 1000
    // WebKit can deliver coalesced samples with the same timestamp after a
    // scheduling hitch. Treat that as missing timing data rather than a
    // near-zero-duration impact, which would inject an enormous fake speed.
    const duration = rawDuration > 0 ? Math.max(minimumSampleSeconds, rawDuration) : nonAdvancingSampleSeconds
    return {
      from: { x: from.x, y: from.y }, to: { x: to.x, y: to.y },
      velocity: { x: (to.x - from.x) / duration, y: (to.y - from.y) / duration },
      radius: this.radius, pressure, active: true,
    }
  }

  private subdivide(track: Track) {
    const spacing = this.spacing()
    let distance = Math.hypot(track.latest.x - track.start.x, track.latest.y - track.start.y)
    while (distance >= spacing) {
      const fraction = spacing / distance
      const to: TimedPoint = {
        x: track.start.x + (track.latest.x - track.start.x) * fraction,
        y: track.start.y + (track.latest.y - track.start.y) * fraction,
        time: track.start.time + (track.latest.time - track.start.time) * fraction,
      }
      track.segments.push(this.makeStroke(track.start, to, track.pressure))
      this.trimBacklog(track)
      track.start = to
      distance = Math.hypot(track.latest.x - track.start.x, track.latest.y - track.start.y)
    }
  }

  private flush(track: Track) {
    const distance = Math.hypot(track.latest.x - track.start.x, track.latest.y - track.start.y)
    if (distance > minimumMovement) {
      track.segments.push(this.makeStroke(track.start, track.latest, track.pressure))
      this.trimBacklog(track)
    }
    track.start = track.latest
  }

  private trimBacklog(track: Track) {
    const overflow = track.segments.length - maxQueuedSegmentsPerPointer
    if (overflow > 0) track.segments.splice(0, overflow)
  }

  private prune(pointerId: number, track: Track) {
    if (!track.held && track.segments.length === 0) this.tracks.delete(pointerId)
  }

  private drain(limit: number): Stroke[] {
    for (const track of this.tracks.values()) if (track.held) this.flush(track)
    const entries = [...this.tracks.entries()]
    if (!entries.length) return []
    const result: Stroke[] = []
    let emptyPasses = 0
    let cursor = this.roundRobin % entries.length
    while (result.length < limit && emptyPasses < entries.length) {
      const [pointerId, track] = entries[cursor]
      const stroke = track.segments.shift()
      if (stroke) {
        result.push(stroke)
        emptyPasses = 0
        this.prune(pointerId, track)
      } else {
        emptyPasses++
      }
      cursor = (cursor + 1) % entries.length
    }
    this.roundRobin = cursor
    return result
  }

  nextBatch(): Stroke[] { return this.drain(SAND.maxContacts) }

  next(): Stroke { return this.drain(1)[0] ?? { ...idleStroke(), from: this.position, to: this.position, radius: this.radius, pressure: this.currentPressure } }

  get cursor(): Stroke { return { ...idleStroke(), from: this.position, to: this.position, radius: this.radius } }
}
