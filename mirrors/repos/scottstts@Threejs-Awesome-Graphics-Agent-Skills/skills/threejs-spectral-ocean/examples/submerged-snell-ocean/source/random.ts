function hashLabel(label: string): number {
  let hash = 1779033703 ^ label.length
  for (let index = 0; index < label.length; index++) {
    hash = Math.imul(hash ^ label.charCodeAt(index), 3432918353)
    hash = (hash << 13) | (hash >>> 19)
  }
  hash = Math.imul(hash ^ (hash >>> 16), 2246822507)
  hash = Math.imul(hash ^ (hash >>> 13), 3266489909)
  return (hash ^ (hash >>> 16)) >>> 0
}

/** Deterministic splitmix32 stream with draw-order-independent forks. */
export class Rng {
  readonly seed: number
  private state: number

  constructor(seed: number) {
    this.seed = seed >>> 0
    this.state = this.seed === 0 ? 0x9e3779b9 : this.seed
  }

  next(): number {
    this.state = (this.state + 0x9e3779b9) >>> 0
    let value = this.state
    value = Math.imul(value ^ (value >>> 16), 0x21f0aaad)
    value = Math.imul(value ^ (value >>> 15), 0x735a2d97)
    value ^= value >>> 15
    return (value >>> 0) / 4294967296
  }

  fork(label: string): Rng {
    return new Rng((hashLabel(label) ^ this.seed) >>> 0)
  }
}
