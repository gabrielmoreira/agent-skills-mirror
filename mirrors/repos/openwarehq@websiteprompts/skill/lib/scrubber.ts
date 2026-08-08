// Progressive scroll-scrubbed frame strip (Apple-keynote technique).
// Loads every 6th frame first so coarse scrubbing works immediately,
// then fills in the rest in batches; draws the nearest loaded frame.

// Set this to the number of files ffmpeg actually printed. A count lower than
// the strip silently makes the tail of the animation unreachable, with no error.
export const FRAME_COUNT = 113; // ~8s at 14fps

type UrlFn = (i: number) => string;
const defaultUrl: UrlFn = (i) => `/frames/frame-${String(i + 1).padStart(4, '0')}.webp`;

export class Scrubber {
  private bitmaps: Array<ImageBitmap | null>;
  private loading: boolean[];
  private canvas: HTMLCanvasElement;
  private ctx: CanvasRenderingContext2D;
  private current = 0;
  private lastDrawn = -1;
  readonly count: number;

  private url: UrlFn;

  constructor(canvas: HTMLCanvasElement, count: number, url: UrlFn = defaultUrl) {
    this.url = url;
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d')!;
    this.count = count;
    this.bitmaps = new Array(count).fill(null);
    this.loading = new Array(count).fill(false);
    this.loadSpine();
  }

  private async load(i: number) {
    if (i < 0 || i >= this.count || this.loading[i]) return;
    this.loading[i] = true;
    try {
      const res = await fetch(this.url(i));
      const blob = await res.blob();
      this.bitmaps[i] = await createImageBitmap(blob);
      this.lastDrawn = -1; // allow redraw with the better frame
    } catch {
      this.loading[i] = false;
    }
  }

  private async loadSpine() {
    const spine: number[] = [];
    for (let i = 0; i < this.count; i += 6) spine.push(i);
    spine.push(this.count - 1);
    await Promise.all(spine.map((i) => this.load(i)));
    // fill the gaps in batches of 12
    for (let start = 0; start < this.count; start += 12) {
      const batch: Promise<void>[] = [];
      for (let i = start; i < Math.min(start + 12, this.count); i++) batch.push(this.load(i));
      await Promise.all(batch);
    }
  }

  private nearestLoaded(i: number): number {
    if (this.bitmaps[i]) return i;
    for (let d = 1; d < this.count; d++) {
      if (this.bitmaps[i - d]) return i - d;
      if (this.bitmaps[i + d]) return i + d;
    }
    return -1;
  }

  /** target in [0,1] across the whole strip; call each rAF */
  tick(target01: number) {
    const target = target01 * (this.count - 1);
    this.current += (target - this.current) * 0.14;
    if (Math.abs(target - this.current) < 0.02) this.current = target;
    const idx = this.nearestLoaded(Math.round(this.current));
    if (idx < 0 || idx === this.lastDrawn) return;
    this.lastDrawn = idx;
    this.draw(this.bitmaps[idx]!);
  }

  resize() {
    const dpr = Math.min(2, window.devicePixelRatio || 1);
    this.canvas.width = window.innerWidth * dpr;
    this.canvas.height = window.innerHeight * dpr;
    this.lastDrawn = -1;
  }

  private draw(bmp: ImageBitmap) {
    const { width: cw, height: ch } = this.canvas;
    // cover fit
    const s = Math.max(cw / bmp.width, ch / bmp.height);
    const w = bmp.width * s;
    const h = bmp.height * s;
    this.ctx.drawImage(bmp, (cw - w) / 2, (ch - h) / 2, w, h);
  }
}
