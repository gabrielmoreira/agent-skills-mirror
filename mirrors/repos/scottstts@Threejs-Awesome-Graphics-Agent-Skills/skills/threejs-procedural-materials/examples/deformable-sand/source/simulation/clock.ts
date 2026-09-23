export class FixedClock {
  private previous: number | undefined
  private accumulator = 0
  droppedSeconds = 0
  readonly step: number
  readonly maxSteps: number
  constructor(step: number, maxSteps: number) { this.step = step; this.maxSteps = maxSteps }
  advance(now: number) {
    if (this.previous === undefined) { this.previous = now; return 0 }
    const elapsed = Math.max(0, (now - this.previous) / 1000)
    this.previous = now
    const budget = this.step * this.maxSteps
    this.droppedSeconds += Math.max(0, elapsed - budget)
    this.accumulator += Math.min(elapsed, budget)
    const count = Math.min(this.maxSteps, Math.floor((this.accumulator + 1e-9) / this.step))
    this.accumulator -= count * this.step
    return count
  }
  reset(now?: number) { this.previous = now; this.accumulator = 0 }
}
