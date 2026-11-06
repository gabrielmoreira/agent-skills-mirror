// Instruments, drums, textures and bus FX for the procedural chill beds (lib/chill.js).
// Every voice adds into a stereo bus [L, R] of Float32Array. Absolute gains do not matter: each part is LUFS-normalised later.
import { SR, TAU, clamp, hz, SVF } from './dsp.js';

export const rng = s => () => { s = s + 0x6D2B79F5 | 0; let t = Math.imul(s ^ s >>> 15, 1 | s); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
export const smooth = x => x <= 0 ? 0 : x >= 1 ? 1 : x * x * (3 - 2 * x);
export const dbg = db => Math.pow(10, db / 20);
export const PAN = p => { const a = (clamp(p, -1, 1) + 1) * Math.PI / 4; return [Math.cos(a) * Math.SQRT2, Math.sin(a) * Math.SQRT2]; };
let NR = rng(4242); const nz = () => NR() * 2 - 1;
export const reseedNoise = s => { NR = rng(s); }; // once per render, so a track never depends on what rendered before it in the process
const blep = (t, dt) => t < dt ? (t /= dt, t + t - t * t - 1) : t > 1 - dt ? (t = (t - 1) / dt, t * t + t + t + 1) : 0;
const dk = tau => Math.exp(-1 / (tau * SR)); // per-sample factor of an exponential decay with time constant tau (s)

export class Osc {
  constructor(p = NR()) { this.p = p; this.dt = 0; }
  step(f) { this.dt = f / SR; this.p += this.dt; if (this.p >= 1) this.p -= 1; return this.p; }
  sin(f) { return Math.sin(TAU * this.step(f)); }
  tri(f) { return 4 * Math.abs(this.step(f) - .5) - 1; }
  glass(f) { const a = TAU * this.step(f); return Math.sin(a) + .3 * Math.sin(2 * a) + .08 * Math.sin(3 * a); }
  vco(f, sq = 0, pw = .5) { // polyBLEP saw, blended toward a pulse of width pw
    const p = this.step(f), dt = this.dt, s = 2 * p - 1 - blep(p, dt);
    if (!sq) return s;
    const q = (p < pw ? 1 : -1) + blep(p, dt) - blep((p - pw + 1) % 1, dt);
    return s + (q - s) * sq;
  }
}

// Write one mono voice: fn(s) is called once per sample in order (so it may keep state), 10 ms fade at the end.
export function W(B, t, dur, pan, fn) {
  const n0 = Math.max(0, Math.round(t * SR)), n = Math.min(Math.round(dur * SR), B[0].length - n0), [gl, gr] = PAN(pan), fd = Math.round(.01 * SR), L = B[0], R = B[1];
  for (let i = 0; i < n; i++) { let x = fn(i / SR); if (i > n - fd) x *= (n - i) / fd; L[n0 + i] += x * gl; R[n0 + i] += x * gr; }
}

// Damped rotation oscillators packed as [re, im, cos*r, sin*r]: one complex multiply per partial per sample.
const rot = (P, np) => { let y = 0; for (let i = 0; i < np; i += 4) { const re = P[i], im = P[i + 1]; P[i] = re * P[i + 2] - im * P[i + 3]; P[i + 1] = re * P[i + 3] + im * P[i + 2]; y += P[i + 1]; } return y; };
const partial = (O, f, a, tau) => { const w = TAU * f / SR, r = dk(tau); O.push(a, 0, Math.cos(w) * r, Math.sin(w) * r); };

// ---------- keys ----------
export function ep(B, t, m, len, vel = .6, pan = 0) { // FM Rhodes
  const f = hz(m), c1 = new Osc(), c2 = new Osc(), mo = new Osc(), tn = new Osc(), dA = dk(.18), dB = dk(2.2 * Math.pow(261.6 / f, .4)), dI = dk(.2), dR = dk(.07), dT = dk(.05), g = vel * .5;
  let a = .3, b = .7, ix = .5 + 1.6 * vel, r = 1, ti = .3 * vel * Math.min(1, 3000 / (7 * f)); // ti: the tine's bell attack, softer up high
  W(B, t, len + .45, pan, s => {
    const md = Math.sin(TAU * mo.step(f)) * (ix + .2 * vel), y = Math.sin(TAU * c1.step(f) + md) + .6 * Math.sin(TAU * c2.step(f * 1.0017) + md * .8) + ti * Math.sin(TAU * tn.step(f * 7));
    const e = (a + b) * r * (s < .003 ? s / .003 : 1); a *= dA; b *= dB; ix *= dI; ti *= dT; if (s > len) r *= dR;
    return y * e * g;
  });
}

export function piano(B, t, m, len, vel = .5, pan = 0) { // felt piano: inharmonic partials, two detuned strings, soft hammer
  const f0 = hz(m), O = [], tau0 = 4.2 * Math.pow(261.6 / f0, .55);
  for (let k = 1; k <= 16; k++) {
    const fk = k * f0 * Math.sqrt(1 + .00038 * k * k); if (fk > 7000) break;
    const a = Math.pow(k, -1.25) * Math.exp(-(k - 1) * (.75 - .45 * vel)), tau = tau0 / (1 + .5 * (k - 1));
    partial(O, fk * .9996, a * .55, tau * .55); partial(O, fk * 1.0004, a * .45, tau * 1.6);
  }
  const P = Float64Array.from(O), np = P.length, lp = new SVF(), hc = 220 + 300 * vel, dH = dk(1 / 70), dR = dk(.1), g = Math.pow(vel, 1.3) * .5;
  let h = .6, r = 1;
  W(B, t, len + .45, pan, s => {
    const y = rot(P, np) + lp.run(nz() * h, hc); h *= dH; if (s > len) r *= dR;
    return y * r * g * (s < .005 ? s / .005 : 1);
  });
}

const BARS = { // [ratio, amp, decay scale], fundamental decay tau at ref Hz, mallet click [amp, Hz]
  kalimba: { p: [[1, 1, 1], [5.93, .16, .06], [16.2, .04, .02]], tau: 1.5, ref: 440, click: [.05, 2600] },
  marimba: { p: [[1, 1, 1], [3.93, .22, .12], [9.1, .05, .04]], tau: 1.0, ref: 261.6, click: [.03, 1100] },
  vibes: { p: [[1, 1, 1], [4, .16, .22], [10, .03, .07]], tau: 3.2, ref: 440, click: [.012, 2200] },
};
export function mallet(kind, B, t, m, len, vel = .6, pan = 0) {
  const K = BARS[kind], f = hz(m), tau = K.tau * Math.pow(K.ref / f, .5), O = [];
  for (const [ra, a, ts] of K.p) if (f * ra < 15000) partial(O, f * ra, a, tau * ts);
  const P = Float64Array.from(O), np = P.length, bp = new SVF(), dC = dk(.005), dR = dk(.06), g = vel * .5;
  let c = K.click[0] * 8, r = 1;
  W(B, t, len + .35, pan, s => {
    bp.run(nz(), K.click[1], 1.5); const y = rot(P, np) + bp.bp * c; c *= dC; if (s > len) r *= dR;
    return y * r * g * (s < .001 ? s / .001 : 1);
  });
}
export const kal = (...a) => mallet('kalimba', ...a), mar = (...a) => mallet('marimba', ...a), vib = (...a) => mallet('vibes', ...a);

export function bell(B, t, m, len, vel = .5, pan = 0, { ratio = 3.5, idx = 1.1, tau = 2 } = {}) { // FM bell
  const f = hz(m), c = new Osc(), mo = new Osc(), dE = dk(tau), dI = dk(tau * .5), dR = dk(.15);
  let e = 1, ix = idx, r = 1;
  W(B, t, len + .6, pan, s => {
    const y = Math.sin(TAU * c.step(f) + ix * Math.sin(TAU * mo.step(f * ratio))) * e * r; e *= dE; ix *= dI; if (s > len) r *= dR;
    return y * vel * .4 * (s < .002 ? s / .002 : 1);
  });
}

// Held chord from t0 to t1 plus release. Voices spread across the stereo field, cutoff breathes on an LFO in absolute time.
export function pad(B, t0, t1, notes, o = {}) {
  const { att = 1.6, rel = 2.2, cut = 900, q = .7, det = 9, vo = 3, wave = 'saw', lfo = .05, depth = .3, g = 1, vib = 0 } = o;
  const n0 = Math.max(0, Math.round(t0 * SR)), hold = t1 - t0, n = Math.min(Math.round((hold + rel) * SR), B[0].length - n0), L = B[0], R = B[1];
  const amp = g * .25 / Math.sqrt(notes.length * vo), fn = wave === 'saw' ? 'vco' : wave;
  notes.forEach((m, j) => {
    const f = hz(m), side = j % 2 ? -1 : 1, fl = new SVF(), fr = new SVF(), ph = j * 1.7;
    const V = Array.from({ length: vo }, (_, v) => { const x = vo > 1 ? v / (vo - 1) * 2 - 1 : 0, [gl, gr] = PAN(x * .7 * side); return { o: new Osc(), r: Math.pow(2, det * x / 1200), gl, gr }; });
    for (let i = 0; i < n; i++) {
      const s = i / SR, vb = vib ? 1 + vib * Math.sin(TAU * 5 * s + j) : 1; let l = 0, r = 0;
      for (const v of V) { const x = v.o[fn](f * v.r * vb); l += x * v.gl; r += x * v.gr; }
      const fc = cut * (1 + depth * Math.sin(TAU * lfo * (t0 + s) + ph)), e = (s < att ? smooth(s / att) : 1) * (s > hold ? 1 - smooth((s - hold) / rel) : 1);
      L[n0 + i] += fl.run(l, fc, q) * e * amp; R[n0 + i] += fr.run(r, fc, q) * e * amp;
    }
  });
}

// ---------- bass and leads ----------
export function sub(B, t, m, len, vel = .8, { att = .012, rel = .09, dr = 1.6 } = {}) {
  const f = hz(m), o = new Osc(0), k = Math.tanh(dr);
  W(B, t, len + rel * 4, 0, s => Math.tanh(dr * o.sin(f)) / k * vel * .5 * (s < att ? smooth(s / att) : 1) * (s > len ? Math.exp(-(s - len) / rel) : 1));
}

export function upright(B, t, m, len, vel = .7, pan = 0) {
  const f = hz(m), o = new Osc(0), lp = new SVF(), th = new SVF(), dE = dk(1 / 1.1), dT = dk(1 / 40), dR = dk(.04);
  let e = 1, h = 1.5, r = 1;
  W(B, t, len + .15, pan, s => {
    const p = o.step(f), x = Math.sin(TAU * p) + .45 * (4 * Math.abs(p - .5) - 1);
    const y = lp.run(x, 300 + 900 * Math.exp(-9 * s)) * e + th.run(nz() * h, 120); e *= dE; h *= dT; if (s > len) r *= dR;
    return y * r * vel * .5 * (s < .004 ? s / .004 : 1);
  });
}

export function syn(B, t, notes, len, vel = .7, pan = 0, o = {}) { // two detuned VCOs into a resonant low-pass with a decaying envelope
  const { cut = 1200, env = 1, dk: d = 8, q = .9, att = .005, rel = .15, det = 6, sq = 0, pw = .5, sus = .3, vib = 0, vd = .25 } = o;
  const ns = [].concat(notes), g = vel * .5 / Math.sqrt(ns.length), r1 = Math.pow(2, det / 1200), r2 = 1 / r1, dE = Math.exp(-d / SR), dA = Math.exp(-d * .35 / SR);
  for (const m of ns) {
    const f = hz(m), a = new Osc(), b = new Osc(), fl = new SVF(); let ee = 1, ea = 1;
    W(B, t, len + rel * 4, pan, s => {
      const ff = vib ? f * (1 + vib * Math.sin(TAU * 5.2 * s) * smooth((s - vd) / .4)) : f;
      const y = fl.run((a.vco(ff * r1, sq, pw) + b.vco(ff * r2, sq, pw)) * .5, cut * Math.pow(2, env * 2 * ee), q);
      const e = (s < att ? s / att : 1) * (sus + (1 - sus) * ea) * (s > len ? Math.exp(-(s - len) / rel) : 1); ee *= dE; ea *= dA;
      return y * e * g;
    });
  }
}

export function flute(B, t, m, len, vel = .7, pan = 0) {
  const f = hz(m), o = new Osc(), bp = new SVF(), lp = new SVF();
  W(B, t, len + .3, pan, s => {
    const p = TAU * o.step(f * (1 + .006 * Math.sin(TAU * 5 * s) * smooth((s - .25) / .4))), tone = Math.sin(p) + .25 * Math.sin(2 * p) + .08 * Math.sin(3 * p);
    const br = bp.run(nz(), f * 2, 2) * (.12 + .25 * Math.exp(-s / .08));
    return lp.run(tone + br, 4000) * vel * .4 * smooth(s / .06) * (s > len ? Math.exp(-(s - len) / .08) : 1);
  });
}

// ---------- drums ----------
export function kick(B, t, vel = 1, { f0 = 105, f1 = 47, pd = 22, dk: d = 6.5, dr = 1.5 } = {}) {
  let ph = 0; const k = Math.tanh(dr);
  W(B, t, .7, 0, s => {
    ph += (f1 + (f0 - f1) * Math.exp(-pd * s)) / SR;
    const x = Math.sin(TAU * ph) * Math.exp(-d * s) + (s < .004 ? nz() * .15 * (1 - s / .004) : 0);
    return Math.tanh(dr * x) / k * vel * .8;
  });
}
export function snare(B, t, vel = 1, { tone = 185, fc = 1700, dk: d = 15 } = {}, pan = 0) {
  let ph = 0; const f = new SVF();
  W(B, t, .45, pan, s => {
    ph += tone * (1 + .3 * Math.exp(-40 * s)) / SR; f.run(nz(), fc, .5);
    return (Math.sin(TAU * ph) * Math.exp(-25 * s) * .5 + (f.hp * .5 + f.bp) * Math.exp(-d * s)) * vel * .5;
  });
}
export function rim(B, t, vel = 1, pan = 0) {
  const f = new SVF();
  W(B, t, .12, pan, s => (Math.sin(TAU * 1720 * s) * .5 * Math.exp(-90 * s) + Math.sin(TAU * 520 * s) * .6 * Math.exp(-70 * s) + f.run(nz(), 3000, 1.2) * Math.exp(-120 * s)) * vel * .4);
}
export function hat(B, t, vel = 1, pan = 0, open = false) {
  const h = new SVF(), b = new SVF(), d = open ? 9 : 45;
  W(B, t, open ? .5 : .12, pan, s => { h.run(nz(), 5000); b.run(nz(), 8000, 1.2); return (h.hp + b.bp * .5) * Math.exp(-d * s) * vel * .3 * (s < .001 ? s / .001 : 1); });
}
export function shaker(B, t, vel = 1, pan = 0) {
  const b = new SVF();
  W(B, t, .15, pan, s => { b.run(nz(), 6000, 1.2); return b.bp * vel * .4 * (s < .008 ? s / .008 : Math.exp(-(s - .008) * 40)); });
}
export function brush(B, t, len, vel = 1, pan = 0) {
  const b = new SVF(), l = new SVF();
  W(B, t, len, pan, s => { b.run(nz(), 2800, .6); return l.run(b.bp, 6000) * vel * .3 * Math.pow(Math.sin(Math.PI * clamp(s / len)), 1.5); });
}
export function brushTap(B, t, vel = 1, pan = 0) {
  const b = new SVF();
  W(B, t, .2, pan, s => { b.run(nz(), 2500, .8); return b.bp * vel * .5 * Math.exp(-35 * s) * (s < .002 ? s / .002 : 1); });
}
const RIDE = [3120, 4310, 5170, 6830, 7570];
export function ride(B, t, vel = 1, pan = .3) {
  const h = new SVF(), ph = RIDE.map(() => NR());
  W(B, t, 1.2, pan, s => {
    h.run(nz(), 5000); let y = h.hp * .3 * Math.exp(-3 * s);
    for (let i = 0; i < 5; i++) y += Math.sin(TAU * (RIDE[i] * s + ph[i])) * .15 * Math.exp(-(2 + i) * s);
    return y * vel * .35 * (1 + 2 * Math.exp(-25 * s)) * (s < .001 ? s / .001 : 1);
  });
}
export function tick(B, t, vel = 1, f = 1500, pan = 0) {
  W(B, t, .06, pan, s => (Math.sin(TAU * f * s) + .4 * Math.sin(TAU * 2.7 * f * s)) * Math.exp(-120 * s) * vel * .4);
}
export function hand(B, t, vel = 1, f0 = 150, pan = 0) {
  let ph = 0; const b = new SVF(), d = f0 < 160 ? 7 : 10;
  W(B, t, .6, pan, s => {
    ph += f0 * (1 + .5 * Math.exp(-60 * s)) / SR; b.run(nz(), 1200, 1);
    return (Math.sin(TAU * ph) * Math.exp(-d * s) + b.bp * .4 * Math.exp(-60 * s)) * vel * .5 * (s < .002 ? s / .002 : 1);
  });
}

// ---------- textures (whole bus) ----------
export function vinyl(B, rate = 1) {
  const R = rng(91), hp = new SVF(), lp = new SVF(), nh = new SVF(), nl = new SVF(), [L, Rr] = B;
  let gl = 1, gr = 1;
  for (let i = 0; i < L.length; i++) {
    let c = 0; if (R() < rate * 7 / SR) { c = (R() * 2 - 1) * (R() < .1 ? 1 : .35); [gl, gr] = PAN(R() * 1.4 - .7); }
    hp.run(c, 900); nh.run(nz(), 1000); const x = lp.run(hp.hp, 7000), h = nl.run(nh.hp, 5000) * .02;
    L[i] += x * gl + h; Rr[i] += x * gr + h;
  }
}
export function hiss(B, lp = 6000) {
  for (const X of B) { const h = new SVF(), l = new SVF(); for (let i = 0; i < X.length; i++) { h.run(nz(), 400); X[i] += l.run(h.hp, lp) * .05; } }
}
export function wind(B) {
  B.forEach((X, c) => {
    const f = new SVF(), o = c * 2.1;
    for (let i = 0; i < X.length; i++) {
      const t = i / SR, fc = 700 + 450 * Math.sin(TAU * .031 * t + o) + 250 * Math.sin(TAU * .073 * t + 1 + o);
      X[i] += f.run(nz(), fc, .9) * (.6 + .4 * Math.sin(TAU * .05 * t + o)) * .3;
    }
  });
}

// ---------- bus FX ----------
function run(X, fc, q, out) { // fixed-cutoff TPT SVF over one channel; out(x, lp, bp, hp, k) gives the new sample
  const g = Math.tan(Math.PI * clamp(fc, 10, SR * .45) / SR), k = 1 / q, a1 = 1 / (1 + g * (g + k)), a2 = g * a1, a3 = g * a2; let s1 = 0, s2 = 0;
  for (let i = 0; i < X.length; i++) { const x = X[i], v3 = x - s2, v1 = a1 * s1 + a2 * v3, v2 = s2 + a2 * s1 + a3 * v3; s1 = 2 * v1 - s1; s2 = 2 * v2 - s2; X[i] = out(x, v2, v1, x - k * v1 - v2, k); }
}
export const filt = (B, mode, fc, q = .707) => B.forEach(X => run(X, fc, q, mode === 'lp' ? (x, l) => l : mode === 'hp' ? (x, l, b, h) => h : (x, l, b, h, k) => b * k));
export const eq = (B, fc, db, q = .707) => { const G = dbg(db) - 1; B.forEach(X => run(X, fc, q, (x, l, b, h, k) => x + G * k * b)); };
export const shelf = (B, fc, db) => { const G = dbg(db) - 1; B.forEach(X => run(X, fc, .707, (x, l, b, h) => x + G * h)); }; // high shelf
const peak = B => { let p = 1e-9; for (const X of B) for (let i = 0; i < X.length; i++) { const a = Math.abs(X[i]); if (a > p) p = a; } return p; };
export function drive(B, k) { const p = peak(B); for (const X of B) for (let i = 0; i < X.length; i++) X[i] = p * Math.tanh(k * X[i] / p) / k; }
export function autopan(B, rate, depth) { const [L, R] = B; for (let i = 0; i < L.length; i++) { const s = depth * Math.sin(TAU * rate * i / SR); L[i] *= 1 - s; R[i] *= 1 + s; } }
export function pump(B, period, depth, t1 = Infinity) { // sidechain-style duck once per period (s) that recovers over the period, until t1
  const n1 = Math.min(B[0].length, Math.round(t1 * SR));
  for (const X of B) for (let i = 0; i < n1; i++) X[i] *= 1 - depth * Math.pow(1 - (i / SR / period) % 1, 2.5);
}
export function trem(B, rate, depth) { for (const X of B) for (let i = 0; i < X.length; i++) X[i] *= 1 - depth * (.5 + .5 * Math.sin(TAU * rate * i / SR)); }
export function crush(B, k, bits) {
  const st = peak(B) / Math.pow(2, bits - 1);
  for (const X of B) { let h = 0; for (let i = 0; i < X.length; i++) { if (i % k === 0) h = Math.round(X[i] / st) * st; X[i] = h; } }
}
export function pingpong(In, time, fb, lpf = 3000) { // returns the wet signal only
  const N = In[0].length, D = Math.max(1, Math.round(time * SR)), bl = new Float32Array(D), br = new Float32Array(D), out = [new Float32Array(N), new Float32Array(N)];
  const fL = new SVF(), fR = new SVF(), hL = new SVF(), hR = new SVF(); let i = 0;
  for (let n = 0; n < N; n++) {
    const dl = bl[i], dr = br[i]; out[0][n] = dl; out[1][n] = dr;
    hL.run(fL.run(dr * fb + (In[0][n] + In[1][n]) * .5, lpf), 220); hR.run(fR.run(dl * fb, lpf), 220);
    bl[i] = hL.hp; br[i] = hR.hp; if (++i >= D) i = 0;
  }
  return out;
}
export function wow(B, ms, rate, fl) { // tape wow (slow) and flutter (7.3 Hz) as a modulated delay
  const N = B[0].length;
  for (const X of B) {
    const C = X.slice();
    for (let n = 0; n < N; n++) {
      const p = n - (6 + ms * Math.sin(TAU * rate * n / SR) + fl * Math.sin(TAU * 7.3 * n / SR)) * SR / 1000, i = Math.floor(p), fr = p - i;
      X[n] = i < 0 ? 0 : C[i] * (1 - fr) + C[Math.min(i + 1, N - 1)] * fr;
    }
  }
}
