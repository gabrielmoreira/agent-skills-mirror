// Procedural chill beds (2 to 3 min) for shorts: a small bar sequencer over lib/chill-synth.js, styles in lib/chill-styles.js.
// Mixed blind by loudness: every part is normalised to a LUFS target relative to the others, then the master to -16 LUFS.
import { SR, lufs, limit, freeverb } from './dsp.js';
import { rng, dbg, smooth, filt, eq, shelf, drive, wow, pingpong, reseedNoise } from './chill-synth.js';
import { STYLES } from './chill-styles.js';

export { STYLES };

// form: [[section, bars, 'layer ...']]; '+a b' inherits the previous section's layers, '-a' drops one.
function song(st, seed) {
  const rand = rng(seed), rnd = () => rand() * 2 - 1, beat = 60 / st.bpm, barT = beat * 4, cb = st.cb || 1;
  const secs = []; let nb = 0, prev = new Set();
  for (const [name, n, layers] of st.form) {
    const L = new Set(layers.startsWith('+') ? prev : []);
    for (const w of layers.split(/\s+/).filter(Boolean)) w[0] === '-' ? L.delete(w.slice(1)) : L.add(w.replace(/^\+/, ''));
    secs.push({ name, b0: nb, n, L }); prev = L; nb += n;
  }
  const end = nb * barT, T = end + (st.tail ?? 6), N = Math.ceil(T * SR), bars = [];
  for (const s of secs) for (let j = 0; j < s.n; j++) { const k = s.b0 + j, ci = Math.floor(k / cb) % st.prog.length; bars.push({ k, j, t0: k * barT, sec: s, ci, ch: st.prog[ci], has: l => s.L.has(l) }); }
  const sw = st.swing ?? .5, su = (st.swingUnit || .5) * 2, hum = st.hum ?? .005;
  const swing = p => { const u = Math.floor(p / su), r = p / su - u; return (u + (r < .5 ? r * 2 * sw : sw + (r - .5) * 2 * (1 - sw))) * su; };
  const bus = () => [new Float32Array(N), new Float32Array(N)], M = bus(), RV = bus(), DL = bus();
  const add = (D, B, g) => { if (g) for (let c = 0; c < 2; c++) { const d = D[c], s = B[c]; for (let i = 0; i < N; i++) d[i] += s[i] * g; } };
  const spans = (layer, same) => {
    const out = []; let cur = null;
    for (const b of bars) {
      if (b.has(layer) && cur && cur.k1 === b.k && (!same || cur.ci === b.ci)) { cur.k1++; cur.t1 += barT; continue; }
      if (cur) out.push(cur); cur = b.has(layer) ? { ci: b.ci, ch: b.ch, k0: b.k, k1: b.k + 1, t0: b.t0, t1: b.t0 + barT } : null;
    }
    if (cur) out.push(cur); return out;
  };
  const S = {
    st, bars, secs, beat, barT, end, T, N, rand, rnd, fin: st.prog[0],
    at: (b, p, lag = 0) => Math.max(0, b.t0 + swing(p) * beat + lag + rnd() * hum),
    mix(B, { db = -10, rv = 0, dl = 0 } = {}) { const l = lufs(B); if (l < -90) return; const g = dbg(db - 20 - l); add(M, B, g); add(RV, B, g * rv); add(DL, B, g * dl); },
    part(o, fn) { const B = bus(); fn(B); o.fx?.(B); S.mix(B, o); },
    each(layer, fn) { for (const b of bars) if (b.has(layer)) fn(b); },
    chords: layer => spans(layer, true),
    spans: layer => spans(layer, false),
    auto(map) { // value per section, eased in over the section's first 4 bars
      const pts = []; let v = map[secs[0].name] ?? 0;
      for (const s of secs) { const nv = map[s.name] ?? v; pts.push([s.b0 * barT, v, nv, Math.min(4, s.n) * barT]); v = nv; }
      return t => { let p = pts[0]; for (const q of pts) if (q[0] <= t) p = q; return p[1] + (p[2] - p[1]) * smooth((t - p[0]) / p[3]); };
    },
    strum(B, t, notes, len, vel, inst, gap = .014, pan = 0) {
      notes.forEach((m, i) => inst(B, t + i * gap, m, len - i * gap, vel * (1 - i * .06), pan + (i / Math.max(1, notes.length - 1) - .5) * .5));
    },
    play(layer, phrases, L, fn) { // phrase notes [bar, pos, beats, midi, vel]; bars align to k % L so they follow the harmony
      for (const b of bars) {
        if (!b.has(layer)) continue;
        const off = b.k % L, n = phrases.length, ph = phrases[((Math.floor(b.k / L) - Math.floor(b.sec.b0 / L)) % n + n) % n];
        for (const [bar, pos, len, m, vel = 1] of ph) if (bar === off) fn(S.at(b, pos), m, len * beat, vel, b);
      }
    },
  };
  function finish() {
    const dry = lufs(M);
    if (st.dly) { const w = pingpong(DL, st.dly.t * beat, st.dly.fb, st.dly.lp ?? 3200), l = lufs(w); if (l > -90) { const g = dbg(dry + st.dly.db - l); add(M, w, g); add(RV, w, g * .3); } }
    if (st.verb) { const w = freeverb(RV[0], RV[1], N, st.verb), l = lufs(w); if (l > -90) add(M, w, dbg(dry + st.verb.db - l)); }
    filt(M, 'hp', 30); if (st.tone) filt(M, 'lp', st.tone, .6);
    if (st.mud) eq(M, 320, -st.mud, .8); // thin the low mids on pad-heavy styles
    shelf(M, 4500, st.air ?? 5); // air: synth beds come out darker than produced records
    eq(M, 2800, -3, .7); // leave room for the voice
    if (st.wow) wow(M, ...st.wow);
    drive(M, 1.25);
    const out = limit(M, dbg(-16 - lufs(M)), dbg(-1.5)), fi = Math.round(.02 * SR), fo = Math.round(2.5 * SR);
    for (let i = 0; i < N; i++) { const g = Math.min(1, i / fi) * (i > N - fo ? .5 + .5 * Math.cos(Math.PI * (i - (N - fo)) / fo) : 1); out[0][i] *= g; out[1][i] *= g; }
    return { L: out[0], R: out[1], T, lufs: lufs(out), bars: nb, end };
  }
  return { S, finish };
}

export function render(id, { seed = 11 } = {}) {
  const st = STYLES[id]; if (!st) throw new Error(`unknown style "${id}" (${Object.keys(STYLES).join(', ')})`);
  reseedNoise(4242 + seed); const { S, finish } = song(st, seed); st.parts(S); return finish();
}
