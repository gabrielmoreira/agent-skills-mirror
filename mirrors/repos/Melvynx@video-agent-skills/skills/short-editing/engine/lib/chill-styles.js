// The procedural bed styles. prog: {b: bass midi, v: chord voicing[, l: left hand, p: pad voicing]}, cb = bars per chord.
// parts(S) builds the track part by part; db is the part loudness relative to the others, rv/dl are reverb and delay sends.
import { ep, piano, kal, mar, vib, bell, pad, sub, upright, syn, flute, kick, snare, rim, hat, shaker, brush, brushTap, ride, tick, hand, vinyl, hiss, wind, filt, drive, autopan, trem, crush, pump } from './chill-synth.js';

export const STYLES = {};

STYLES['lofi-nuit'] = {
  name: 'Nuit lo-fi', mood: 'chill', desc: 'Rhodes feutré, vinyle, kick doux, mélodie en écho',
  bpm: 74, swing: .6, cb: 1, tone: 10000, air: 7, mud: 2.5, wow: [.8, .45, .06],
  verb: { room: .8, damp: .55, db: -12 }, dly: { t: .75, fb: .38, db: -19 },
  prog: [{ b: 34, v: [50, 57, 60, 65] }, { b: 33, v: [48, 55, 59, 64] }, { b: 31, v: [46, 53, 57, 62] }, { b: 36, v: [46, 53, 55, 62] }],
  form: [['intro', 4, 'keys tex'], ['a', 8, '+bass kick'], ['b', 8, 'keys tex bass drums pad'], ['c', 8, '+mel'], ['brk', 4, 'keys tex pad'], ['d', 8, 'keys tex bass drums pad mel'], ['out', 4, 'keys tex pad']],
  parts(S) {
    const { beat, at, end, fin } = S;
    const A = [[0, .5, 1, 72], [0, 1.5, .5, 74], [0, 2, 2, 69], [1, .5, .5, 67], [1, 1, 1, 69], [1, 2.5, 1.5, 64], [2, .5, 1, 65], [2, 1.5, .5, 69], [2, 2, 1.5, 70], [3, 1, 3, 67]];
    const B2 = [[0, .5, 1, 72], [0, 1.5, .5, 74], [0, 2, 1, 77], [0, 3, 1, 76], [1, .5, 2, 72], [1, 2.5, 1.5, 71], [2, .5, 1, 70], [2, 1.5, .5, 69], [2, 2, 2, 65], [3, 0, .5, 67], [3, .5, 3, 65]];
    S.part({ db: -6, rv: .3, dl: .06, fx: B => { autopan(B, .35, .25); filt(B, 'lp', 4800); drive(B, 1.3); } }, B => {
      S.each('keys', b => {
        S.strum(B, at(b, 0, .012), b.ch.v, 3.4 * beat, .55, ep);
        if (b.k % 2 && b.has('bass')) S.strum(B, at(b, 2.5, .012), b.ch.v.slice(1), 1.3 * beat, .38, ep);
      });
      S.strum(B, end, fin.v, 5, .5, ep);
    });
    S.part({ db: -10, rv: .35, dl: .45, fx: B => filt(B, 'lp', 6500) }, B => S.play('mel', [A, B2], 4, (t, m, len, v) => ep(B, t, m, len, .5 * v, .15)));
    S.part({ db: -10, fx: B => filt(B, 'lp', 380) }, B => {
      S.each('bass', b => {
        const r = b.ch.b; sub(B, at(b, 0), r, 1.6 * beat, .9); sub(B, at(b, 2.5), b.k % 4 === 3 ? r + 7 : r, .9 * beat, .7);
        if (b.k % 2) sub(B, at(b, 3.5), r + 12, .4 * beat, .5);
      });
      sub(B, end, fin.b, 4, .8, { rel: .8 });
    });
    S.part({ db: -12, rv: .05, fx: B => { crush(B, 2, 12); filt(B, 'lp', 9000); drive(B, 1.6); } }, B => {
      for (const b of S.bars) {
        const full = b.has('drums'); if (!full && !b.has('kick')) continue;
        kick(B, at(b, 0), .95); kick(B, at(b, 2.5), .8); if (b.k % 4 === 3) kick(B, at(b, 3.75), .6);
        for (let i = 0; i < 8; i++) hat(B, at(b, i * .5), (i % 2 ? .45 : .7) * (full ? 1 : .7), .25);
        if (full) { snare(B, at(b, 1, .01), .8, { dk: 14 }); snare(B, at(b, 3, .01), .85, { dk: 14 }); }
      }
    });
    S.part({ db: -15, rv: .5 }, B => {
      for (const c of S.chords('pad')) pad(B, c.t0, c.t1, c.ch.v.map(m => m + 12), { wave: 'tri', cut: 2200, att: 1.2, rel: 1.6, vo: 2, det: 6 });
      pad(B, end, end + 3, fin.v.map(m => m + 12), { wave: 'tri', cut: 2200, att: .3, rel: 3, vo: 2, det: 6 });
    });
    S.part({ db: -22 }, B => { vinyl(B, 1); hiss(B, 6000); });
  },
};

STYLES.enquete = {
  name: 'Enquête', mood: 'tension', desc: 'Drone grave, pulse filtré, battement de coeur, piano feutré',
  bpm: 90, cb: 2,
  verb: { room: .88, damp: .5, db: -9 }, dly: { t: .75, fb: .45, db: -16 },
  prog: [{ b: 33, v: [57, 60, 64, 71] }, { b: 29, v: [57, 60, 64, 71] }, { b: 33, v: [57, 60, 64, 71] }, { b: 34, v: [57, 62, 64, 69] }],
  form: [['intro', 4, 'drone tick'], ['a', 12, '+pad pulse'], ['b', 16, '+heart keys'], ['brk', 8, 'drone pad keys'], ['c', 12, 'drone pad pulse tick heart keys high'], ['out', 4, 'drone pad keys']],
  parts(S) {
    const { beat, at, end, fin } = S;
    const A = [[0, 0, 2, 76], [1, 1, 3, 71], [2, 0, 2, 76], [2, 2.5, 1.5, 71], [3, 2, 2, 69], [4, 0, 2, 76], [4, 2, 2, 77], [5, 0, 4, 76], [6, 0, 2, 77], [6, 2, 2, 74], [7, 0, 3, 76]];
    const B2 = [[0, 0, 3, 72], [1, 2, 2, 71], [2, 0, 4, 69], [4, 0, 2, 72], [4, 2, 2, 76], [5, 2, 2, 77], [6, 0, 4, 74], [7, 2, 2, 76]];
    S.part({ db: -11, rv: .4 }, B => { for (const s of S.spans('drone')) pad(B, s.t0, s.t1, [45, 52], { cut: 420, depth: .45, lfo: .03, att: 3, rel: 4, vo: 3, det: 7 }); });
    S.part({ db: -13, rv: .5 }, B => {
      for (const c of S.chords('pad')) pad(B, c.t0, c.t1, c.ch.v, { cut: 950, att: 2.2, rel: 2.5, vo: 3 });
      pad(B, end, end + 3, fin.v, { cut: 900, att: 1, rel: 3 });
    });
    const pc = S.auto({ intro: 380, a: 420, b: 560, brk: 420, c: 680, out: 420 });
    S.part({ db: -11, rv: .2, dl: .25, fx: B => filt(B, 'hp', 90) }, B => S.each('pulse', b => {
      for (let i = 0; i < 8; i++) { const t = at(b, i * .5); syn(B, t, b.ch.b + 12, .4 * beat, i % 2 ? .6 : .85, i % 2 ? .2 : -.2, { cut: pc(t), env: 1.2, dk: 14, q: 1.3, sq: .3, sus: .1 }); }
    }));
    S.part({ db: -14 }, B => { for (const c of S.chords('pulse')) sub(B, c.t0, c.ch.b, c.t1 - c.t0, .8, { att: .3, rel: .4 }); });
    const H = { f0: 70, f1: 42, pd: 16, dk: 9, dr: 1.2 };
    S.part({ db: -15, fx: B => filt(B, 'lp', 180) }, B => S.each('heart', b => { for (const p of [0, 2]) { kick(B, at(b, p), .9, H); kick(B, at(b, p + .4), .6, H); } }));
    S.part({ db: -22 }, B => S.each('tick', b => { for (let i = 0; i < 4; i++) tick(B, at(b, i), i % 2 ? .6 : .8, i % 2 ? 1180 : 1520, i % 2 ? .3 : -.3); }));
    S.part({ db: -8, rv: .55, dl: .25 }, B => {
      S.play('keys', [A, B2], 8, (t, m, len, v) => piano(B, t, m, len, .42 * v, .1));
      S.strum(B, end, [45, 52, ...fin.v], 6, .35, piano, .03);
    });
    S.part({ db: -19, rv: .6 }, B => { for (const s of S.spans('high')) pad(B, s.t0, s.t1, [76, 81], { wave: 'glass', cut: 5000, att: 4, rel: 4, vo: 2, det: 4 }); });
    S.part({ db: -28 }, B => wind(B));
  },
};

STYLES.nappe = {
  name: 'Nappe', mood: 'ambient', desc: 'Nappes lentes, cloches lointaines, aucun rythme',
  bpm: 60, cb: 4, tail: 8, mud: 3,
  verb: { room: .92, damp: .45, db: -6 }, dly: { t: 1.5, fb: .5, db: -11 },
  prog: [{ b: 40, v: [52, 59, 63, 66, 68] }, { b: 37, v: [56, 59, 63, 64, 68] }, { b: 33, v: [56, 61, 63, 64, 71] }, { b: 35, v: [56, 59, 64, 66, 71] }],
  form: [['intro', 4, 'pad wind'], ['a', 12, '+sub low glass'], ['b', 16, '+bells'], ['out', 4, 'pad wind glass bells']],
  parts(S) {
    const { at, end, fin, rand, rnd } = S;
    S.part({ db: -8, rv: .6, dl: .1 }, B => { for (const c of S.chords('pad')) pad(B, c.t0, c.t1, c.ch.v, { cut: 800, att: 3, rel: 3.5, det: 10, vo: 3, lfo: .04, depth: .35 }); });
    S.part({ db: -13, rv: .4 }, B => { for (const c of S.chords('low')) pad(B, c.t0, c.t1, [c.ch.b + 12, c.ch.b + 19], { wave: 'tri', cut: 1200, att: 3, rel: 3, vo: 2, det: 5 }); });
    S.part({ db: -14 }, B => { for (const c of S.chords('sub')) sub(B, c.t0, c.ch.b, c.t1 - c.t0, .7, { att: 1.5, rel: 1.2 }); });
    S.part({ db: -16, rv: .7 }, B => { for (const c of S.chords('glass')) pad(B, c.t0, c.t1, c.ch.v.slice(-2).map(m => m + 12), { wave: 'glass', cut: 6000, att: 4, rel: 4, vo: 2, det: 4 }); });
    S.part({ db: -14, rv: .5, dl: .5 }, B => {
      S.each('bells', b => { for (let i = 0; i < 4; i++) if (rand() < .3) bell(B, at(b, i), b.ch.v[Math.floor(rand() * b.ch.v.length)] + 12, 3, .4 + .3 * rand(), rnd() * .5, { tau: 2.2 }); });
      fin.v.slice(1).forEach((m, i) => bell(B, end + i * .35, m + 12, 5, .45, (i % 2 ? .3 : -.3), { tau: 2.5 }));
    });
    S.part({ db: -24 }, B => wind(B));
  },
};

STYLES['piano-feutre'] = {
  name: 'Piano feutré', mood: 'chill', desc: 'Piano feutré intime, cordes douces, souffle de bande',
  bpm: 68, cb: 1, hum: .012, tone: 9000, tail: 7, air: 7, mud: 2.5,
  verb: { room: .82, damp: .5, db: -10 },
  prog: [{ b: 41, l: [41, 48], v: [56, 60, 63, 67] }, { b: 37, l: [37, 44], v: [56, 60, 63, 65] }, { b: 44, l: [44, 51], v: [58, 60, 63, 67] }, { b: 39, l: [39, 46], v: [56, 58, 63, 65] }],
  form: [['intro', 4, 'rh tex'], ['a', 8, 'lh rh tex'], ['b', 12, '+mel str'], ['brk', 4, 'lh tex str'], ['c', 8, 'lh rh mel str tex'], ['out', 4, 'lh rh tex']],
  parts(S) {
    const { beat, at, end, fin, rand } = S;
    const RH = [[.5, 0], [1, 1], [1.5, 2], [2, 3], [2.5, 2], [3, 1], [3.5, 2]], SOFT = [[.5, 0], [1.5, 2], [2.5, 1], [3.5, 3]];
    const A = [[0, 0, 1.5, 72], [0, 1.5, .5, 75], [0, 2, 2, 79], [1, 0, 2, 77], [1, 2, 1, 75], [1, 3, 1, 72], [2, 0, 3, 75], [2, 3, 1, 70], [3, 0, 4, 72]];
    const B2 = [[0, 0, 1.5, 72], [0, 1.5, .5, 75], [0, 2, 2, 80], [1, 0, 2, 79], [1, 2, 2, 77], [2, 0, 2, 75], [2, 2, 2, 72], [3, 0, 4, 70]];
    S.part({ db: -6, rv: .45, fx: B => { filt(B, 'lp', 2600); drive(B, 1.2); } }, B => {
      S.each('lh', b => { piano(B, at(b, 0), b.ch.l[0], 3.6 * beat, .4, -.2); piano(B, at(b, 2), b.ch.l[1], 1.6 * beat, .26, -.15); });
      S.each('rh', b => { for (const [p, i] of b.has('lh') ? RH : SOFT) piano(B, at(b, p), b.ch.v[i], 1.3 * beat, .24 + .06 * rand(), .2); });
      S.strum(B, end, [...fin.l, ...fin.v], 6, .32, piano, .035);
    });
    S.part({ db: -9, rv: .5 }, B => S.play('mel', [A, B2], 4, (t, m, len, v) => piano(B, t, m, len, .38 * v, .05)));
    S.part({ db: -15, rv: .5 }, B => { for (const c of S.chords('str')) pad(B, c.t0, c.t1, c.ch.v.map(m => m - 12), { cut: 1100, att: 2, rel: 2.5, vib: .0025 }); });
    S.part({ db: -30 }, B => hiss(B, 4500));
  },
};

STYLES.dub = {
  name: 'Dub', mood: 'stylé', desc: 'Accords dub en écho, sub rond, kick feutré',
  bpm: 112, cb: 8, tail: 7,
  verb: { room: .9, damp: .5, db: -10 }, dly: { t: .75, fb: .55, lp: 1800, db: -8 },
  prog: [{ b: 36, v: [51, 55, 58, 62] }, { b: 41, v: [51, 55, 56, 60] }],
  form: [['intro', 8, 'stab tex'], ['a', 16, '+kick sub'], ['b', 16, '+hat'], ['brk', 8, 'stab tex sub'], ['c', 16, 'stab tex kick sub hat'], ['out', 4, 'stab tex']],
  parts(S) {
    const { beat, at, end, fin, rand } = S;
    const STAB = [[.5, 2.5], [.5, 2.5], [.5, 1.75, 2.5], [.5, 2.5, 3.5]], sc = S.auto({ intro: 500, a: 650, b: 900, brk: 600, c: 1000, out: 550 });
    const o = t => ({ cut: sc(t), env: .9, dk: 22, q: 1.5, sq: .15, det: 9, sus: .15 });
    S.part({ db: -8, dl: .9, rv: .15, fx: B => filt(B, 'hp', 160) }, B => {
      S.each('stab', b => { for (const p of STAB[b.k % 4]) { const t = at(b, p); syn(B, t, b.ch.v, .28 * beat, .7 + .15 * rand(), 0, o(t)); } });
      syn(B, end, fin.v, .5 * beat, .8, 0, o(end));
    });
    const K = { f0: 85, f1: 46, pd: 26, dk: 7.5, dr: 1.3 };
    S.part({ db: -13, fx: B => filt(B, 'lp', 220) }, B => S.each('kick', b => { for (let i = 0; i < 4; i++) kick(B, at(b, i), i % 2 ? .85 : .95, K); }));
    S.part({ db: -21, rv: .1, dl: .1 }, B => S.each('hat', b => {
      for (let i = 0; i < 4; i++) hat(B, at(b, i + .5), .6, .3, true);
      for (let i = 0; i < 16; i++) shaker(B, at(b, i * .25), i % 2 ? .35 : .5, -.35);
      if (b.k % 8 === 7) rim(B, at(b, 3.75), .7, .2);
    }));
    S.part({ db: -11 }, B => { S.each('sub', b => sub(B, at(b, 0), b.ch.b, 3.7 * beat, .85)); sub(B, end, fin.b, 3, .8, { rel: .6 }); });
    S.part({ db: -27 }, B => { hiss(B, 5000); vinyl(B, .7); });
  },
};

STYLES.arpege = {
  name: 'Arpège sombre', mood: 'tension', desc: 'Arpège synthé qui s\'ouvre lentement, basse pulsée, lead lointain',
  bpm: 96, cb: 2, tone: 8500, tail: 7,
  verb: { room: .86, damp: .5, db: -10 }, dly: { t: .75, fb: .45, db: -14 },
  prog: [{ b: 38, v: [50, 57, 62, 65], p: [57, 62, 65, 69] }, { b: 34, v: [50, 53, 58, 62], p: [58, 62, 65, 70] }, { b: 31, v: [50, 55, 58, 62], p: [55, 62, 67, 70] }, { b: 33, v: [49, 52, 57, 61], p: [57, 61, 64, 69] }],
  form: [['intro', 4, 'arp pad'], ['a', 12, '+bass'], ['b', 16, '+kick'], ['brk', 4, 'arp pad'], ['c', 16, 'arp pad bass kick hat lead'], ['out', 4, 'arp pad']],
  parts(S) {
    const { beat, at, end, fin } = S;
    const ARP = [0, 1, 2, 3, 2, 1, 2, 3], ac = S.auto({ intro: 420, a: 600, b: 850, brk: 520, c: 1200, out: 450 });
    const LEAD = [[0, 0, 6, 74], [1, 2, 2, 76], [2, 0, 6, 77], [3, 2, 2, 74], [4, 0, 6, 74], [5, 2, 2, 70], [6, 0, 4, 73], [7, 0, 4, 76]];
    S.part({ db: -9, rv: .2, dl: .3, fx: B => filt(B, 'hp', 120) }, B => S.each('arp', b => {
      for (let i = 0; i < 16; i++) { const t = at(b, i * .25); syn(B, t, b.ch.v[ARP[i % 8]] + (i % 16 === 11 ? 12 : 0), .22 * beat, i % 4 ? .6 : .85, (i % 2 ? .25 : -.25), { cut: ac(t), env: 1.6, dk: 18, q: 1.7, sq: .5, sus: .1 }); }
    }));
    S.part({ db: -13, rv: .5 }, B => {
      for (const c of S.chords('pad')) pad(B, c.t0, c.t1, c.ch.p, { cut: 1400, att: 1.5, rel: 2, vo: 3 });
      pad(B, end, end + 3, fin.p, { cut: 1200, att: .5, rel: 3.5 });
    });
    S.part({ db: -11, fx: B => filt(B, 'lp', 900) }, B => S.each('bass', b => { for (let i = 0; i < 8; i++) syn(B, at(b, i * .5), b.ch.b, .4 * beat, i % 2 ? .65 : .85, 0, { cut: 260, env: .8, dk: 10, q: 1, sus: .2 }); }));
    S.part({ db: -14 }, B => { for (const c of S.chords('bass')) sub(B, c.t0, c.ch.b, c.t1 - c.t0, .7, { att: .2, rel: .3 }); sub(B, end, fin.b, 3, .7, { rel: .8 }); });
    S.part({ db: -14, rv: .05 }, B => {
      S.each('kick', b => { kick(B, at(b, 0), .95); kick(B, at(b, 2), .85); });
      S.each('hat', b => { for (let i = 0; i < 4; i++) hat(B, at(b, i + .5), .55, .3); });
    });
    S.part({ db: -11, rv: .4, dl: .35 }, B => S.play('lead', [LEAD], 8, (t, m, len, v) => syn(B, t, m, len, .7 * v, .1, { cut: 1800, env: .4, dk: 3, q: .8, att: .03, rel: .3, sus: .8, det: 4, vib: .004 })));
  },
};

STYLES['trip-hop'] = {
  name: 'Trip-hop', mood: 'tension douce', desc: 'Beat lent et lourd, Rhodes en tremolo, vibraphone sombre',
  bpm: 82, cb: 2, swing: .56, tone: 9500, air: 6, mud: 1.5, wow: [.9, .4, .05],
  verb: { room: .85, damp: .5, db: -10 }, dly: { t: 1.5, fb: .35, db: -18 },
  prog: [{ b: 40, v: [55, 59, 62, 66] }, { b: 36, v: [55, 59, 64, 66] }, { b: 33, v: [55, 59, 60, 64] }, { b: 35, v: [54, 57, 60, 63] }],
  form: [['intro', 4, 'keys tex'], ['a', 12, '+drums bass'], ['b', 16, '+vib'], ['brk', 8, 'keys tex str'], ['c', 8, 'keys tex drums bass vib str'], ['out', 4, 'keys tex']],
  parts(S) {
    const { beat, at, end, fin } = S;
    const VIB = [[0, 0, 1, 71], [0, 1, 1, 74], [0, 2, 2, 78], [1, 0, 3, 76], [1, 3, 1, 74], [2, 0, 2, 79], [2, 2, 1, 78], [2, 3, 1, 76], [3, 0, 4, 71], [4, 0, 1, 72], [4, 1, 1, 76], [4, 2, 2, 79], [5, 0, 2, 83], [5, 2, 2, 81], [6, 0, 2, 75], [6, 2, 2, 72], [7, 0, 2, 71], [7, 2, 2, 69]];
    S.part({ db: -7, rv: .3, fx: B => { autopan(B, 1.4, .3); filt(B, 'lp', 3000); drive(B, 1.4); } }, B => {
      S.each('keys', b => b.k % 2 ? S.strum(B, at(b, 2.5, .01), b.ch.v.slice(1), 1.4 * beat, .4, ep) : S.strum(B, at(b, 0, .01), b.ch.v, 7.4 * beat, .55, ep));
      S.strum(B, end, fin.v, 6, .5, ep);
    });
    const TK = { f0: 95, f1: 44, pd: 22, dk: 5.5, dr: 1.5 }, SN = { tone: 175, fc: 1500, dk: 11 };
    S.part({ db: -11, rv: .08, fx: B => { crush(B, 2, 11); filt(B, 'lp', 8500); drive(B, 1.8); } }, B => S.each('drums', b => {
      kick(B, at(b, 0), 1, TK); kick(B, at(b, 2.5), .85, TK); if (b.k % 2) kick(B, at(b, 2.75), .5, TK);
      snare(B, at(b, 1, .015), .85, SN); snare(B, at(b, 3, .015), .9, SN);
      for (let i = 0; i < 8; i++) hat(B, at(b, i * .5), i % 2 ? .35 : .55, .2);
    }));
    S.part({ db: -10, fx: B => filt(B, 'lp', 400) }, B => {
      S.each('bass', b => { sub(B, at(b, 0), b.ch.b, 2.2 * beat, .9); sub(B, at(b, 2.5), b.ch.b, 1.2 * beat, .75); });
      sub(B, end, fin.b, 4, .8, { rel: .8 });
    });
    S.part({ db: -11, rv: .4, dl: .3, fx: B => trem(B, 4.6, .25) }, B => S.play('vib', [VIB], 8, (t, m, len, v) => vib(B, t, m, len, .55 * v, .2)));
    S.part({ db: -14, rv: .5 }, B => { for (const c of S.chords('str')) pad(B, c.t0, c.t1, c.ch.v.map(m => m + 12), { cut: 1800, att: 2, rel: 2.5, vib: .003 }); });
    S.part({ db: -25 }, B => vinyl(B, 1.2));
  },
};

STYLES.nostalgie = {
  name: 'Nostalgie', mood: 'chill', desc: 'Synthés sur bande qui ondule, boîte à musique, batterie compressée',
  bpm: 88, cb: 2, swing: .55, tone: 8000, wow: [2.2, .33, .15],
  verb: { room: .84, damp: .5, db: -10 }, dly: { t: .75, fb: .4, db: -16 },
  prog: [{ b: 38, v: [54, 57, 61, 64] }, { b: 35, v: [54, 57, 61, 62] }, { b: 31, v: [54, 57, 59, 62] }, { b: 33, v: [52, 57, 59, 62] }],
  form: [['intro', 4, 'pad tex'], ['a', 12, '+bass box'], ['b', 16, '+drums lead'], ['brk', 4, 'pad tex box'], ['c', 12, 'pad tex bass drums lead box'], ['out', 4, 'pad tex']],
  parts(S) {
    const { beat, at, end, fin, rand } = S;
    const LEAD = [[0, 0, 1.5, 69], [0, 1.5, .5, 71], [0, 2, 2, 73], [1, 0, 2, 74], [1, 2, 2, 73], [2, 0, 1.5, 71], [2, 1.5, .5, 73], [2, 2, 2, 74], [3, 0, 4, 69], [4, 0, 1.5, 71], [4, 1.5, .5, 74], [4, 2, 2, 78], [5, 0, 2, 76], [5, 2, 2, 74], [6, 0, 3, 76], [6, 3, 1, 71], [7, 0, 4, 69]];
    const BOX = [[[0, 3], [.5, 2], [1, 1], [2, 0], [2.5, 1], [3, 2]], [[0, 3], [1, 2], [1.5, 1], [2, 3], [3, 0]]];
    S.part({ db: -7, rv: .35, fx: B => drive(B, 1.5) }, B => {
      for (const c of S.chords('pad')) pad(B, c.t0, c.t1, c.ch.v, { cut: 1500, att: 1.2, rel: 1.8, det: 15, vo: 3 });
      pad(B, end, end + 3, fin.v, { cut: 1300, att: .5, rel: 3.5, det: 15 });
    });
    S.part({ db: -9, rv: .3, dl: .3, fx: B => filt(B, 'lp', 2800) }, B => S.play('lead', [LEAD], 8, (t, m, len, v) => syn(B, t, m, len, .7 * v, -.1, { cut: 2000, env: .3, dk: 4, q: .8, att: .02, rel: .25, sus: .8, sq: .75, pw: .3, vib: .005 })));
    S.part({ db: -14, rv: .5, dl: .2 }, B => {
      S.each('box', b => { for (const [p, i] of BOX[b.k % 2]) bell(B, at(b, p), b.ch.v[i] + 24, 1.2, .35 + .15 * rand(), .3, { ratio: 4, idx: .7, tau: 1 }); });
      fin.v.forEach((m, i) => bell(B, end + i * .2, m + 24, 3, .4, .3, { ratio: 4, idx: .7, tau: 1.4 }));
    });
    S.part({ db: -11, fx: B => filt(B, 'lp', 450) }, B => {
      S.each('bass', b => { sub(B, at(b, 0), b.ch.b, 1.8 * beat, .9); sub(B, at(b, 2), b.ch.b, 1.5 * beat, .75); });
      sub(B, end, fin.b, 4, .8, { rel: .8 });
    });
    S.part({ db: -12, rv: .06, fx: B => { crush(B, 3, 10); filt(B, 'lp', 7000); drive(B, 2); } }, B => S.each('drums', b => {
      kick(B, at(b, 0), .95); kick(B, at(b, 2.5), .8);
      snare(B, at(b, 1, .01), .75, { tone: 200, dk: 16 }); snare(B, at(b, 3, .01), .8, { tone: 200, dk: 16 });
      for (let i = 0; i < 8; i++) hat(B, at(b, i * .5), i % 2 ? .35 : .55, .2);
    }));
    S.part({ db: -23 }, B => { hiss(B, 5000); vinyl(B, .8); });
  },
};

STYLES.bali = {
  name: 'Bali calme', mood: 'chill', desc: 'Kalimba, marimba, flûte douce, percussions à la main',
  bpm: 90, cb: 2, swing: .54, swingUnit: .25, tone: 9000,
  verb: { room: .85, damp: .5, db: -10 }, dly: { t: .75, fb: .35, db: -17 },
  prog: [{ b: 43, v: [59, 62, 66, 69] }, { b: 40, v: [59, 62, 66, 67] }, { b: 36, v: [59, 62, 64, 67] }, { b: 38, v: [57, 59, 62, 64] }],
  form: [['intro', 4, 'kal pad'], ['a', 12, '+bass shk'], ['b', 16, '+hand fl'], ['brk', 8, 'kal pad'], ['c', 12, 'kal pad bass shk hand fl'], ['out', 4, 'kal pad']],
  parts(S) {
    const { beat, at, end, fin, rand } = S;
    const KAL = [[0, 0], [.75, 2], [1.5, 1], [2, 3], [2.75, 2], [3.5, 1]], SOFT = [[0, 0], [1.5, 2], [2.75, 1]];
    const FL = [[0, 0, 1, 74], [0, 1, .5, 76], [0, 1.5, 2.5, 79], [1, 0, 2, 78], [1, 2, 2, 74], [2, 0, 1, 76], [2, 1, 1, 74], [2, 2, 2, 71], [3, 0, 3, 67], [3, 3, 1, 69], [4, 0, 1, 71], [4, 1, 1, 74], [4, 2, 2, 76], [5, 0, 2, 79], [5, 2, 2, 78], [6, 0, 2, 76], [6, 2, 2, 74], [7, 0, 4, 71]];
    S.part({ db: -8, rv: .3, dl: .25 }, B => {
      S.each('kal', b => { for (const [p, i] of b.has('bass') ? KAL : SOFT) kal(B, at(b, p), b.ch.v[i] + 12, 2 * beat, .5 + .2 * rand(), (i - 1.5) * .3); });
      S.strum(B, end, fin.v.map(m => m + 12), 4, .55, kal, .06);
    });
    S.part({ db: -10, rv: .15 }, B => {
      S.each('bass', b => { mar(B, at(b, 0), b.ch.b, 1.5 * beat, .8); mar(B, at(b, 1.5), b.ch.b + 7, 1.5 * beat, .6); mar(B, at(b, 3), b.ch.b + 12, beat, .55); });
      mar(B, end, fin.b, 3, .8);
    });
    S.part({ db: -22, rv: .1 }, B => S.each('shk', b => { for (let i = 0; i < 16; i++) shaker(B, at(b, i * .25), i % 4 === 2 ? .6 : i % 2 ? .3 : .45, .35); }));
    S.part({ db: -15, rv: .15 }, B => S.each('hand', b => { for (const [p, f] of [[0, 120], [1.5, 210], [2.5, 190], [3, 140]]) hand(B, at(b, p), f < 160 ? .9 : .6, f, f < 160 ? 0 : -.25); }));
    S.part({ db: -10, rv: .4, dl: .3 }, B => S.play('fl', [FL], 8, (t, m, len, v) => flute(B, t, m, len, .6 * v, .1)));
    S.part({ db: -14, rv: .5 }, B => {
      for (const c of S.chords('pad')) pad(B, c.t0, c.t1, c.ch.v, { wave: 'tri', cut: 1800, att: 2, rel: 2.5, vo: 2, det: 6 });
      pad(B, end, end + 3, fin.v, { wave: 'tri', cut: 1600, att: .5, rel: 3.5, vo: 2, det: 6 });
    });
    S.part({ db: -30 }, B => wind(B));
  },
};

STYLES['jazz-feutre'] = {
  name: 'Jazz feutré', mood: 'chill', desc: 'Rhodes, contrebasse, balais et ride, vibraphone',
  bpm: 72, cb: 1, swing: .64, tone: 8000, mud: 2,
  verb: { room: .8, damp: .5, db: -11 },
  prog: [{ b: 36, v: [51, 55, 58, 62] }, { b: 41, v: [51, 55, 57, 62] }, { b: 34, v: [50, 53, 57, 60] }, { b: 39, v: [50, 53, 55, 58] }],
  form: [['intro', 4, 'keys brush'], ['a', 8, '+bass'], ['b', 12, '+vib ride'], ['brk', 4, 'keys bass'], ['c', 12, 'keys bass brush vib ride'], ['out', 4, 'keys brush']],
  parts(S) {
    const { beat, at, end, fin, bars } = S;
    const A = [[0, .5, .5, 74], [0, 1, 1, 75], [0, 2, 1.5, 79], [0, 3.5, .5, 77], [1, 0, 1.5, 74], [1, 1.5, .5, 72], [1, 2, 2, 69], [2, .5, .5, 72], [2, 1, 1, 74], [2, 2, 1, 81], [2, 3, 1, 77], [3, 0, 3, 79], [3, 3, 1, 74]];
    const B2 = [[0, .5, .5, 74], [0, 1, 1, 75], [0, 2, 1, 79], [0, 3, 1, 82], [1, 0, 2, 81], [1, 2, 1, 79], [1, 3, 1, 77], [2, 0, 2, 74], [2, 2, 2, 72], [3, 0, 4, 70]];
    S.part({ db: -7, rv: .3, fx: B => filt(B, 'lp', 3600) }, B => {
      S.each('keys', b => {
        if (b.k % 4 === 3) return S.strum(B, at(b, 0, .01), b.ch.v, 3.8 * beat, .5, ep);
        S.strum(B, at(b, 0, .01), b.ch.v, 1.2 * beat, .5, ep); S.strum(B, at(b, 1.5, .01), b.ch.v, beat, .42, ep);
        if (b.k % 2) S.strum(B, at(b, 3, .01), b.ch.v.slice(1), .8 * beat, .35, ep);
      });
      S.strum(B, end, fin.v, 6, .5, ep);
    });
    S.part({ db: -9, rv: .1 }, B => {
      S.each('bass', b => {
        upright(B, at(b, 0), b.ch.b, 1.9 * beat, .85); upright(B, at(b, 2), b.ch.b + 7, 1.4 * beat, .7);
        if (b.k % 2) upright(B, at(b, 3.5), (bars[b.k + 1]?.ch.b ?? fin.b) + 1, .45 * beat, .55);
      });
      upright(B, end, fin.b, 4, .8);
    });
    S.part({ db: -17, rv: .1 }, B => S.each('brush', b => { for (let i = 0; i < 4; i++) brush(B, at(b, i), .9 * beat, i % 2 ? .6 : .8, -.2); brushTap(B, at(b, 1), .6, .1); brushTap(B, at(b, 3), .65, .1); }));
    S.part({ db: -19, rv: .15 }, B => S.each('ride', b => { for (const p of [0, 1, 1.5, 2, 3, 3.5]) ride(B, at(b, p), p % 1 ? .5 : .75, .35); }));
    S.part({ db: -10, rv: .35 }, B => S.play('vib', [A, B2], 4, (t, m, len, v) => vib(B, t, m, len, .55 * v, -.15)));
  },
};

// ---------- tension, in the vein of enquete and arpege ----------
STYLES.filature = {
  name: 'Filature', mood: 'tension', desc: 'Ostinato pincé en sourdine, contrebasse qui rôde, vibraphone de film noir',
  bpm: 92, cb: 2,
  verb: { room: .85, damp: .5, db: -10 }, dly: { t: .75, fb: .4, db: -16 },
  prog: [{ b: 40, v: [52, 55, 59, 62] }, { b: 36, v: [48, 52, 55, 59] }, { b: 33, v: [48, 52, 55, 57] }, { b: 35, v: [47, 51, 54, 57] }],
  form: [['intro', 4, 'pluck pad'], ['a', 12, '+bass rim'], ['b', 16, '+vib hat'], ['brk', 8, 'pluck pad vib'], ['c', 12, 'pluck pad bass rim hat vib high'], ['out', 4, 'pluck pad']],
  parts(S) {
    const { beat, at, end, fin } = S, OST = [0, 0, 2, 0, 1, 0, 2, 3], pc = S.auto({ intro: 600, a: 700, b: 900, brk: 650, c: 1100, out: 600 });
    const V = [[0, 0, 1.5, 71], [0, 1.5, .5, 70], [0, 2, 1, 69], [0, 3, 1, 67], [1, 0, 3, 64], [2, 0, 2, 67], [2, 2, 2, 71], [3, 0, 4, 72], [4, 0, 2, 72], [4, 2, 2, 69], [5, 0, 3, 64], [6, 0, 2, 66], [6, 2, 2, 63], [7, 0, 2, 66], [7, 2, 2, 71]];
    S.part({ db: -9, rv: .2, dl: .2, fx: B => filt(B, 'hp', 110) }, B => S.each('pluck', b => {
      for (let i = 0; i < 8; i++) { const t = at(b, i * .5); syn(B, t, b.ch.v[OST[i]], .25 * beat, i % 2 ? .55 : .8, i % 2 ? .3 : -.3, { cut: pc(t), env: 1.3, dk: 20, q: 1.2, sq: .4, sus: 0 }); }
    }));
    S.part({ db: -13, rv: .5 }, B => {
      for (const c of S.chords('pad')) pad(B, c.t0, c.t1, c.ch.v, { cut: 800, att: 2, rel: 2.5, vo: 3 });
      pad(B, end, end + 3, fin.v, { cut: 750, att: .6, rel: 3 });
    });
    S.part({ db: -11, fx: B => filt(B, 'lp', 700) }, B => S.each('bass', b => {
      for (const [p, d] of [[0, 0], [1.5, 0], [2, 7], [3.5, 12]]) upright(B, at(b, p), b.ch.b + d, .45 * beat, p ? .7 : .9, 0);
    }));
    S.part({ db: -21, rv: .2 }, B => S.each('rim', b => { rim(B, at(b, 3), .5, .2); if (b.k % 2) rim(B, at(b, 1.75), .3, -.2); }));
    S.part({ db: -22 }, B => S.each('hat', b => { for (let i = 0; i < 8; i++) hat(B, at(b, i * .5), i % 2 ? .45 : .3, .25); }));
    S.part({ db: -10, rv: .45, dl: .3 }, B => {
      S.play('vib', [V], 8, (t, m, len, v) => vib(B, t, m, len, .5 * v, -.15));
      S.strum(B, end, fin.v.map(m => m + 12), 5, .35, vib, .05);
    });
    S.part({ db: -20, rv: .6 }, B => { for (const s of S.spans('high')) pad(B, s.t0, s.t1, [71, 76], { wave: 'glass', cut: 4500, att: 4, rel: 4, vo: 2, det: 4 }); });
    S.part({ db: -28 }, B => wind(B));
  },
};

STYLES['compte-a-rebours'] = {
  name: 'Compte à rebours', mood: 'tension', desc: 'Horloge qui tique, basse pulsée qui s\'ouvre, nappe qui monte, impacts lointains',
  bpm: 100, cb: 2,
  verb: { room: .88, damp: .5, db: -10 }, dly: { t: 1.5, fb: .4, db: -17 },
  prog: [{ b: 36, v: [48, 51, 55, 58] }, { b: 32, v: [48, 51, 56, 60] }, { b: 29, v: [48, 53, 56, 60] }, { b: 31, v: [47, 50, 55, 62] }],
  form: [['intro', 4, 'clock pad'], ['a', 12, '+pulse'], ['b', 16, '+keys hit'], ['brk', 8, 'clock pad keys'], ['c', 16, 'clock pad pulse keys hit fast high'], ['out', 4, 'clock pad']],
  parts(S) {
    const { beat, at, end, fin } = S;
    const pc = S.auto({ intro: 300, a: 380, b: 520, brk: 400, c: 750, out: 380 }), padc = S.auto({ intro: 600, a: 700, b: 900, brk: 750, c: 1300, out: 650 });
    const K1 = [[0, 0, 4, 72], [2, 0, 4, 68], [4, 0, 4, 65], [6, 0, 4, 67]], K2 = [[0, 0, 2, 75], [0, 2, 2, 72], [2, 0, 4, 72], [4, 0, 2, 72], [4, 2, 2, 68], [6, 0, 2, 71], [6, 2, 2, 67]];
    S.part({ db: -17, rv: .15 }, B => S.each('clock', b => {
      for (let i = 0; i < 4; i++) tick(B, at(b, i), i % 2 ? .6 : .85, i % 2 ? 1250 : 1650, i % 2 ? .35 : -.35);
      if (b.has('fast')) for (let i = 0; i < 4; i++) tick(B, at(b, i + .5), .35, 2100, 0);
    }));
    S.part({ db: -13, rv: .45 }, B => {
      for (const c of S.chords('pad')) pad(B, c.t0, c.t1, c.ch.v, { cut: padc(c.t0), att: 2, rel: 2.5, vo: 3 });
      pad(B, end, end + 3, fin.v, { cut: 700, att: .6, rel: 3 });
    });
    S.part({ db: -11, rv: .15, fx: B => filt(B, 'hp', 60) }, B => S.each('pulse', b => {
      for (let i = 0; i < 8; i++) { const t = at(b, i * .5); syn(B, t, b.ch.b + 12, .35 * beat, i % 2 ? .6 : .9, 0, { cut: pc(t), env: 1, dk: 12, q: 1.1, sus: .15 }); }
    }));
    S.part({ db: -15 }, B => { for (const c of S.chords('pulse')) sub(B, c.t0, c.ch.b, c.t1 - c.t0, .7, { att: .3, rel: .4 }); });
    S.part({ db: -15, rv: .3, fx: B => filt(B, 'lp', 220) }, B => S.each('hit', b => { if (b.k % 4 === 0) kick(B, at(b, 0), 1, { f0: 62, f1: 34, pd: 9, dk: 2.6, dr: 2 }); }));
    S.part({ db: -9, rv: .55, dl: .3 }, B => {
      S.play('keys', [K1, K2], 8, (t, m, len, v) => piano(B, t, m, len, .45 * v, .1));
      S.strum(B, end, [36, 43, ...fin.v], 6, .35, piano, .03);
    });
    S.part({ db: -20, rv: .6 }, B => { for (const s of S.spans('high')) pad(B, s.t0, s.t1, [79, 84], { wave: 'glass', cut: 5000, att: 6, rel: 4, vo: 2, det: 4 }); });
  },
};

STYLES.sonar = {
  name: 'Sonar', mood: 'tension', desc: 'Pings de sonar en écho, drone profond, pouls lent sous la surface',
  bpm: 80, cb: 2, tone: 7000, tail: 8,
  verb: { room: .9, damp: .45, db: -9 }, dly: { t: 1.5, fb: .55, lp: 4500, db: -12 },
  prog: [{ b: 38, v: [50, 53, 57, 64] }, { b: 34, v: [50, 53, 57, 58] }, { b: 38, v: [50, 53, 57, 64] }, { b: 36, v: [48, 52, 55, 62] }],
  form: [['intro', 4, 'drone ping'], ['a', 12, '+pad pulse'], ['b', 12, '+arp'], ['brk', 4, 'drone ping pad'], ['c', 12, 'drone ping pad pulse arp high echo'], ['out', 4, 'drone ping pad']],
  parts(S) {
    const { beat, at, end, fin } = S, AR = [0, 2, 1, 3, 2, 1, 3, 2];
    S.part({ db: -11, rv: .4 }, B => { for (const s of S.spans('drone')) pad(B, s.t0, s.t1, [38, 45], { cut: 360, depth: .5, lfo: .025, att: 3, rel: 5, vo: 3, det: 6 }); });
    S.part({ db: -10, rv: .5, dl: .7 }, B => {
      S.each('ping', b => { if (b.k % 2 === 0) bell(B, at(b, 0), 81, 2.5, .8, -.2, { ratio: 2, idx: .25, tau: 1.2 }); });
      S.each('echo', b => { if (b.k % 2) bell(B, at(b, 1), 88, 1.5, .45, .3, { ratio: 2, idx: .2, tau: .9 }); });
    });
    S.part({ db: -13, rv: .55 }, B => {
      for (const c of S.chords('pad')) pad(B, c.t0, c.t1, c.ch.v, { cut: 1000, att: 2.5, rel: 3, vo: 3, wave: 'tri' });
      pad(B, end, end + 3.5, fin.v, { cut: 900, att: .8, rel: 4, wave: 'tri' });
    });
    S.part({ db: -14 }, B => S.each('pulse', b => { for (const p of [0, 2]) sub(B, at(b, p), b.ch.b, 1.2 * beat, p ? .6 : .8, { att: .04, rel: .35, dr: 1.2 }); }));
    S.part({ db: -12, rv: .5, dl: .3 }, B => S.each('arp', b => { for (let i = 0; i < 8; i++) vib(B, at(b, i * .5), b.ch.v[AR[i]] + 12, .5 * beat, i % 4 ? .45 : .6, i % 2 ? .4 : -.4); }));
    S.part({ db: -20, rv: .6 }, B => { for (const s of S.spans('high')) pad(B, s.t0, s.t1, [74, 81], { wave: 'glass', cut: 4500, att: 5, rel: 5, vo: 2, det: 4 }); });
    S.part({ db: -26 }, B => wind(B));
  },
};

STYLES.labo = {
  name: 'Labo', mood: 'tension', desc: 'Cloches de verre en arpège, sub qui pulse, clics de machine, piano grave',
  bpm: 88, cb: 2, tail: 7,
  verb: { room: .86, damp: .45, db: -10 }, dly: { t: .75, fb: .45, lp: 4500, db: -15 },
  prog: [{ b: 42, v: [54, 57, 61, 64] }, { b: 38, v: [54, 57, 61, 62] }, { b: 35, v: [54, 57, 59, 62] }, { b: 37, v: [53, 56, 59, 61] }],
  form: [['intro', 4, 'bell pad'], ['a', 12, '+sub'], ['b', 12, '+click low'], ['brk', 8, 'bell pad low'], ['c', 12, 'bell pad sub click low high'], ['out', 4, 'bell pad']],
  parts(S) {
    const { beat, at, end, fin } = S, AR = [0, 2, 1, 3, 2, 4, 3, 1], bv = S.auto({ intro: .5, a: .6, b: .75, brk: .55, c: .85, out: .5 });
    S.part({ db: -9, rv: .35, dl: .35, fx: B => filt(B, 'hp', 250) }, B => S.each('bell', b => {
      const N = [...b.ch.v.map(m => m + 12), b.ch.v[0] + 24];
      for (let i = 0; i < 8; i++) { const t = at(b, i * .5); bell(B, t, N[AR[i]], .6 * beat, bv(t) * (i % 4 ? .75 : 1), i % 2 ? .35 : -.35, { ratio: 3.5, idx: .5, tau: .7 }); }
    }));
    S.part({ db: -13, rv: .5 }, B => {
      for (const c of S.chords('pad')) pad(B, c.t0, c.t1, c.ch.v, { cut: 1100, att: 2, rel: 2.5, vo: 3, wave: 'tri' });
      pad(B, end, end + 3, fin.v, { cut: 1000, att: .6, rel: 3.5, wave: 'tri' });
    });
    S.part({ db: -13 }, B => S.each('sub', b => { for (let i = 0; i < 4; i++) sub(B, at(b, i), b.ch.b, .55 * beat, i % 2 ? .6 : .85, { att: .01, rel: .12 }); }));
    S.part({ db: -21, rv: .15 }, B => S.each('click', b => { for (const [p, f] of [[0, 3200], [.75, 2600], [1.5, 3200], [2.25, 2900], [3, 3200], [3.5, 2600]]) tick(B, at(b, p), p % 1 ? .5 : .75, f, p % 1 ? .45 : -.45); }));
    S.part({ db: -12, rv: .5 }, B => {
      for (const c of S.chords('low')) { piano(B, c.t0, c.ch.b + 12, c.t1 - c.t0, .4, -.1); piano(B, c.t0 + .02, c.ch.b + 24, c.t1 - c.t0, .3, .1); }
      S.strum(B, end, [fin.b + 12, fin.b + 24, ...fin.v], 6, .35, piano, .03);
    });
    S.part({ db: -20, rv: .6 }, B => { for (const s of S.spans('high')) pad(B, s.t0, s.t1, [78, 85], { wave: 'glass', cut: 5000, att: 5, rel: 4, vo: 2, det: 4 }); });
  },
};

STYLES['code-noir'] = {
  name: 'Code noir', mood: 'tension', desc: 'Techno minimale feutrée, kick sourd, accords dub en écho, basse qui pompe',
  bpm: 98, cb: 2, tone: 9000, tail: 7, mud: 1.5,
  verb: { room: .84, damp: .55, db: -11 }, dly: { t: .75, fb: .55, lp: 2600, db: -12 },
  prog: [{ b: 33, v: [57, 60, 64, 67] }, { b: 33, v: [57, 60, 64, 67] }, { b: 29, v: [57, 60, 64, 65] }, { b: 28, v: [55, 59, 62, 64] }],
  form: [['intro', 4, 'pad stab'], ['a', 12, '+bass'], ['b', 16, '+kick hat'], ['brk', 8, 'pad stab bass'], ['c', 16, 'pad stab bass kick hat shk rim'], ['out', 4, 'pad stab']],
  parts(S) {
    const { beat, at, end, fin } = S, sc = S.auto({ intro: 700, a: 800, b: 1000, brk: 800, c: 1250, out: 700 }), bc = S.auto({ intro: 250, a: 300, b: 420, brk: 320, c: 520, out: 300 });
    S.part({ db: -13, rv: .45, fx: B => pump(B, beat, .35, end) }, B => {
      for (const c of S.chords('pad')) pad(B, c.t0, c.t1, c.ch.v, { cut: 800, att: 1.5, rel: 2, vo: 3 });
      pad(B, end, end + 3, fin.v, { cut: 750, att: .5, rel: 3.5 });
    });
    S.part({ db: -10, rv: .25, dl: .55, fx: B => filt(B, 'hp', 200) }, B => S.each('stab', b => {
      for (const p of b.k % 2 ? [1.5] : [.5, 2.5]) { const t = at(b, p); syn(B, t, b.ch.v, .3 * beat, .7, 0, { cut: sc(t), env: .7, dk: 9, q: .9, sus: 0, det: 8 }); }
    }));
    S.part({ db: -11, fx: B => { filt(B, 'lp', 800); pump(B, beat, .3, end); } }, B => S.each('bass', b => {
      for (let i = 0; i < 4; i++) { const t = at(b, i + .5); syn(B, t, b.ch.b + 12, .35 * beat, .8, 0, { cut: bc(t), env: .9, dk: 10, q: 1.1, sus: .2 }); }
    }));
    S.part({ db: -17, fx: B => pump(B, beat, .5, end) }, B => { for (const c of S.chords('bass')) sub(B, c.t0, c.ch.b, c.t1 - c.t0, .6, { att: .3, rel: .4 }); sub(B, end, fin.b, 3, .6, { rel: .8 }); });
    S.part({ db: -15, fx: B => filt(B, 'lp', 170) }, B => S.each('kick', b => { for (let i = 0; i < 4; i++) kick(B, at(b, i), i % 2 ? .8 : .95, { f0: 85, f1: 45, pd: 24, dk: 8, dr: 1.4 }); }));
    S.part({ db: -21, rv: .1 }, B => {
      S.each('hat', b => { for (let i = 0; i < 4; i++) hat(B, at(b, i + .5), .55, .25); });
      S.each('shk', b => { for (let i = 0; i < 16; i++) if (i % 4) shaker(B, at(b, i * .25), i % 2 ? .35 : .5, -.3); });
    });
    S.part({ db: -21, rv: .4, dl: .3 }, B => S.each('rim', b => { if (b.k % 2) rim(B, at(b, 3.75), .5, .3); }));
  },
};

STYLES.thriller = {
  name: 'Thriller', mood: 'tension', desc: 'Ostinato staccato en 3-3-2, impacts graves lointains, piano sombre',
  bpm: 84, cb: 2, tail: 8,
  verb: { room: .9, damp: .5, db: -9 }, dly: { t: 1, fb: .35, db: -18 },
  prog: [{ b: 35, v: [50, 54, 59, 62] }, { b: 31, v: [50, 55, 59, 62] }, { b: 28, v: [52, 55, 59, 64] }, { b: 30, v: [49, 54, 58, 61] }],
  form: [['intro', 4, 'pad ost'], ['a', 12, '+hit low'], ['b', 12, '+keys'], ['brk', 8, 'pad keys high'], ['c', 12, 'pad ost hit low keys high'], ['out', 4, 'pad keys']],
  parts(S) {
    const { beat, at, end, fin } = S, oc = S.auto({ intro: 600, a: 750, b: 900, brk: 600, c: 1150, out: 600 });
    const K = [[0, 0, 3, 74], [1, 2, 2, 73], [2, 0, 4, 71], [4, 0, 2, 76], [4, 2, 2, 74], [5, 0, 4, 71], [6, 0, 4, 73], [7, 0, 2, 70], [7, 2, 2, 73]];
    S.part({ db: -9, rv: .25, fx: B => filt(B, 'hp', 120) }, B => S.each('ost', b => {
      for (let i = 0; i < 16; i++) { const acc = [0, 3, 6].includes(i % 8), t = at(b, i * .25); syn(B, t, b.ch.b + 24, .16 * beat, acc ? .85 : .4, acc ? -.15 : .15, { cut: oc(t), env: 1, dk: 22, q: 1, sq: .2, sus: 0, det: 9 }); }
    }));
    S.part({ db: -14, rv: .45 }, B => {
      for (const c of S.chords('pad')) pad(B, c.t0, c.t1, c.ch.v, { cut: 800, att: 2, rel: 2.5, vo: 3, vib: .002 });
      pad(B, end, end + 3, fin.v, { cut: 750, att: .6, rel: 3.5 });
    });
    S.part({ db: -14, rv: .3, fx: B => filt(B, 'lp', 200) }, B => S.each('hit', b => { if (b.k % 4 === 0) kick(B, at(b, 0), 1, { f0: 58, f1: 32, pd: 8, dk: 2.2, dr: 2.2 }); }));
    S.part({ db: -15 }, B => { for (const c of S.chords('low')) sub(B, c.t0, c.ch.b, c.t1 - c.t0, .7, { att: .5, rel: .5 }); });
    S.part({ db: -8, rv: .55, dl: .25 }, B => {
      S.play('keys', [K], 8, (t, m, len, v) => piano(B, t, m, len, .42 * v, .12));
      S.each('keys', b => { if (b.k % 2 === 0) piano(B, at(b, 0), b.ch.b + 12, 6 * beat, .4, -.15); });
      S.strum(B, end, [35, 47, ...fin.v], 6, .35, piano, .03);
    });
    S.part({ db: -20, rv: .6 }, B => { for (const s of S.spans('high')) pad(B, s.t0, s.t1, [78, 83], { wave: 'glass', cut: 4500, att: 4, rel: 4, vo: 2, det: 5 }); });
    S.part({ db: -28 }, B => wind(B));
  },
};

STYLES['nuit-blanche'] = {
  name: 'Nuit blanche', mood: 'tension', desc: 'Piano en ostinato lent, cordes sombres, battement discret',
  bpm: 76, cb: 2, tail: 8,
  verb: { room: .9, damp: .5, db: -9 }, dly: { t: .75, fb: .35, db: -18 },
  prog: [{ b: 43, v: [43, 50, 55, 58] }, { b: 39, v: [43, 51, 55, 58] }, { b: 36, v: [43, 51, 55, 60] }, { b: 38, v: [42, 50, 54, 57] }],
  form: [['intro', 4, 'ost'], ['a', 12, '+drone str'], ['b', 12, '+keys'], ['brk', 4, 'ost str'], ['c', 12, 'ost drone str keys heart high'], ['out', 4, 'ost drone']],
  parts(S) {
    const { beat, at, end, fin } = S, OS = [0, 1, 2, 3, 2, 1, 2, 3];
    const K = [[0, 0, 3, 74], [1, 2, 2, 70], [2, 0, 3, 75], [3, 0, 2, 74], [3, 2, 2, 70], [4, 0, 3, 72], [5, 0, 2, 70], [5, 2, 2, 67], [6, 0, 4, 69], [7, 0, 2, 66], [7, 2, 2, 69]];
    S.part({ db: -8, rv: .45, dl: .15 }, B => {
      S.each('ost', b => { for (let i = 0; i < 8; i++) piano(B, at(b, i * .5), b.ch.v[OS[i]], .9 * beat, i % 4 ? .32 : .42, (OS[i] - 1.5) * .15); });
      S.strum(B, end, fin.v, 6, .35, piano, .04);
    });
    S.part({ db: -12, rv: .4 }, B => { for (const s of S.spans('drone')) pad(B, s.t0, s.t1, [31, 43], { cut: 300, depth: .4, lfo: .03, att: 3, rel: 4, vo: 3, det: 6 }); });
    S.part({ db: -13, rv: .55 }, B => { for (const c of S.chords('str')) pad(B, c.t0, c.t1, [c.ch.v[1] + 12, c.ch.v[3] + 12], { cut: 1300, att: 2.5, rel: 3, vo: 4, det: 10, vib: .003 }); });
    S.part({ db: -8, rv: .55, dl: .3 }, B => S.play('keys', [K], 8, (t, m, len, v) => piano(B, t, m, len, .45 * v, .15)));
    const H = { f0: 70, f1: 42, pd: 16, dk: 9, dr: 1.2 };
    S.part({ db: -16, fx: B => filt(B, 'lp', 180) }, B => S.each('heart', b => { for (const p of [0, 2]) { kick(B, at(b, p), .9, H); kick(B, at(b, p + .4), .6, H); } }));
    S.part({ db: -20, rv: .6 }, B => { for (const s of S.spans('high')) pad(B, s.t0, s.t1, [74, 79], { wave: 'glass', cut: 4500, att: 5, rel: 5, vo: 2, det: 4 }); });
    S.part({ db: -28 }, B => wind(B));
  },
};

STYLES.neon = {
  name: 'Néon', mood: 'tension', desc: 'Arpège en 16e qui pompe, basse en octaves, lead lointain, ville de nuit',
  bpm: 104, cb: 2, tone: 8500, tail: 7,
  verb: { room: .86, damp: .5, db: -10 }, dly: { t: .75, fb: .45, db: -14 },
  prog: [{ b: 41, v: [53, 56, 60, 63], p: [56, 60, 63, 68] }, { b: 37, v: [53, 56, 60, 61], p: [56, 60, 61, 65] }, { b: 32, v: [51, 56, 60, 63], p: [56, 60, 63, 68] }, { b: 39, v: [51, 55, 58, 63], p: [55, 58, 63, 67] }],
  form: [['intro', 4, 'arp pad'], ['a', 12, '+bass'], ['b', 16, '+kick hat'], ['brk', 8, 'arp pad'], ['c', 20, 'arp pad bass kick hat snr lead'], ['out', 4, 'arp pad']],
  parts(S) {
    const { beat, at, end, fin } = S, ARP = [0, 2, 1, 3, 2, 0, 3, 1], ac = S.auto({ intro: 450, a: 650, b: 900, brk: 550, c: 1250, out: 480 });
    const LEAD = [[0, 0, 4, 72], [1, 0, 2, 75], [1, 2, 2, 72], [2, 0, 4, 73], [3, 0, 4, 72], [4, 0, 4, 72], [5, 0, 2, 75], [5, 2, 2, 77], [6, 0, 4, 70], [7, 0, 2, 67], [7, 2, 2, 70]];
    S.part({ db: -9, rv: .2, dl: .3, fx: B => { filt(B, 'hp', 140); pump(B, beat, .3, end); } }, B => S.each('arp', b => {
      for (let i = 0; i < 16; i++) { const t = at(b, i * .25); syn(B, t, b.ch.v[ARP[i % 8]] + (i % 8 === 7 ? 12 : 0), .2 * beat, i % 4 ? .55 : .85, i % 2 ? .3 : -.3, { cut: ac(t), env: 1.5, dk: 18, q: 1.6, sq: .5, pw: .3, sus: .1 }); }
    }));
    S.part({ db: -13, rv: .5, fx: B => pump(B, beat, .3, end) }, B => {
      for (const c of S.chords('pad')) pad(B, c.t0, c.t1, c.ch.p, { cut: 1500, att: 1.5, rel: 2, vo: 4 });
      pad(B, end, end + 3, fin.p, { cut: 1200, att: .5, rel: 3.5 });
    });
    S.part({ db: -11, fx: B => filt(B, 'lp', 900) }, B => S.each('bass', b => { for (let i = 0; i < 8; i++) syn(B, at(b, i * .5), b.ch.b + (i % 2 ? 12 : 0), .4 * beat, i % 2 ? .6 : .85, 0, { cut: 300, env: .8, dk: 10, q: 1, sus: .2 }); }));
    S.part({ db: -15, rv: .05 }, B => {
      S.each('kick', b => { kick(B, at(b, 0), .95); kick(B, at(b, 2.5), .75); });
      S.each('hat', b => { for (let i = 0; i < 4; i++) hat(B, at(b, i + .5), .5, .3); });
    });
    S.part({ db: -19, rv: .5 }, B => S.each('snr', b => snare(B, at(b, 2), .6, { tone: 180, fc: 1500, dk: 18 }, .05)));
    S.part({ db: -11, rv: .4, dl: .35 }, B => S.play('lead', [LEAD], 8, (t, m, len, v) => syn(B, t, m, len, .7 * v, -.1, { cut: 1700, env: .4, dk: 3, q: .8, att: .04, rel: .35, sus: .8, det: 5, vib: .004 })));
  },
};

// Drum-forward boom-bap for the nico-slowdown style (his reel DcJNevhtfuw: ~90 BPM hip-hop, the kit carries it,
// pads around 2 kHz). The beat is on from bar 1: the short lays it from the hook impact (music.start).
STYLES['boom-bap'] = {
  name: 'Boom bap', mood: 'énergie', desc: 'Beat hip-hop sec et en avant, Rhodes mineur, sub, nappe claire',
  bpm: 90, cb: 1, swing: .57, tone: 11000, air: 6, mud: 2,
  verb: { room: .7, damp: .55, db: -15 },
  prog: [{ b: 33, v: [57, 60, 64, 67] }, { b: 29, v: [57, 60, 64, 65] }, { b: 31, v: [55, 59, 62, 65] }, { b: 28, v: [55, 59, 60, 64] }],
  form: [['a', 8, 'drums bass keys'], ['b', 8, '+pad'], ['c', 8, '+bell'], ['brk', 2, 'keys pad'], ['d', 16, 'drums bass keys pad bell'], ['out', 4, 'keys pad']],
  parts(S) {
    const { beat, at, end, fin, rand } = S;
    const KK = { f0: 120, f1: 48, pd: 26, dk: 7.5, dr: 2.2 }, SN = { tone: 190, fc: 1900, dk: 13 };
    S.part({ db: -5, rv: .06, fx: B => { filt(B, 'lp', 12000); drive(B, 1.7); } }, B => S.each('drums', b => {
      kick(B, at(b, 0), 1, KK); kick(B, at(b, 1.75), .7, KK); kick(B, at(b, 2.5), .9, KK); if (b.k % 2) kick(B, at(b, 3.75), .55, KK);
      snare(B, at(b, 1, .008), 1, SN); snare(B, at(b, 3, .008), 1, SN); if (b.k % 4 === 3) snare(B, at(b, 3.75), .45, SN);
      for (let i = 0; i < 8; i++) hat(B, at(b, i * .5), (i % 2 ? .5 : .85) * (.85 + .15 * rand()), i % 2 ? .2 : -.1, b.k % 4 === 3 && i === 7);
    }));
    S.part({ db: -9, fx: B => filt(B, 'lp', 420) }, B => {
      S.each('bass', b => { sub(B, at(b, 0), b.ch.b, 1.4 * beat, 1); sub(B, at(b, 1.75), b.ch.b, .6 * beat, .7); sub(B, at(b, 2.5), b.ch.b + (b.k % 2 ? 7 : 0), 1.3 * beat, .85); });
      sub(B, end, fin.b, 3, .8, { rel: .8 });
    });
    S.part({ db: -10, rv: .25, fx: B => { filt(B, 'lp', 5200); drive(B, 1.3); } }, B => {
      S.each('keys', b => { S.strum(B, at(b, 0, .01), b.ch.v, 1.4 * beat, .55, ep); S.strum(B, at(b, 2.5, .01), b.ch.v.slice(1), .9 * beat, .42, ep); });
      S.strum(B, end, fin.v, 4, .5, ep);
    });
    S.part({ db: -15, rv: .4 }, B => { for (const c of S.chords('pad')) pad(B, c.t0, c.t1, c.ch.v.map(m => m + 12), { wave: 'tri', cut: 2400, att: .6, rel: 1.2, vo: 2, det: 7 }); });
    S.part({ db: -17, rv: .3 }, B => S.each('bell', b => { if (b.k % 2 === 0) [0, 1.5, 3].forEach((p, i) => bell(B, at(b, p), b.ch.v[(i + b.k) % 4] + 24, .8, .4, .25 * (i - 1), { ratio: 3, idx: .6, tau: .8 })); }));
  },
};

// Drum-led 123 BPM bed for the aiwithremy style (his demucs stems: low kick, snare, hats to 10 kHz, A minor bass,
// quiet 1 kHz pluck line). Straight and on the grid (hum 0) so bar 0 starts on the kick: the style's beat.mp3 is a whole-bar loop cut from it.
STYLES['remy-beat'] = {
  name: 'Remy beat', mood: 'énergie calme', desc: 'Beat moderne droit, kick grave, sub en la mineur, petit pluck à 1 kHz',
  bpm: 123, cb: 2, swing: .5, hum: 0, tone: 12000, air: 4, mud: 2,
  verb: { room: .72, damp: .55, db: -16 }, dly: { t: .75, fb: .3, lp: 2600, db: -20 },
  prog: [{ b: 33, v: [57, 60, 64] }, { b: 33, v: [57, 60, 65] }, { b: 33, v: [57, 60, 64] }, { b: 31, v: [55, 59, 62] }],
  form: [['pre', 4, 'drums bass pad pluck'], ['a', 16, 'drums bass pad pluck'], ['b', 8, 'drums bass pad'], ['c', 8, 'drums bass pad pluck'], ['out', 4, 'drums bass pad pluck']],
  parts(S) {
    const { beat, at, rand } = S;
    const P = [[0, 0, .5, 81], [0, .75, .5, 84], [0, 1.5, .75, 88], [1, 2, .5, 86], [1, 2.75, .75, 84]];
    const KK = { f0: 160, f1: 46, pd: 34, dk: 6, dr: 2 }, SN = { tone: 190, fc: 1800, dk: 15 };
    S.part({ db: -5, rv: .05, fx: B => { filt(B, 'lp', 9000); drive(B, 1.5); } }, B => S.each('drums', b => {
      kick(B, at(b, 0), .85, KK); kick(B, at(b, 2.5), .75, KK); if (b.k % 2) kick(B, at(b, 1.75), .5, KK);
      snare(B, at(b, 1), 1, SN); snare(B, at(b, 3), 1, SN);
      for (const p of [.5, 1.5, 3.5]) hat(B, at(b, p), (.85 + .15 * rand()), .2, b.k % 4 === 3 && p === 3.5);
    }));
    S.part({ db: -9, fx: B => filt(B, 'lp', 380) }, B => S.each('bass', b => { sub(B, at(b, 0), b.ch.b, 1.9 * beat, 1, { dr: 2 }); sub(B, at(b, 3), b.ch.b, .9 * beat, .8, { dr: 2 }); }));
    S.part({ db: -16, rv: .3 }, B => { for (const c of S.chords('pad')) pad(B, c.t0, c.t1, c.ch.v, { wave: 'tri', cut: 700, att: .4, rel: .8, vo: 2, det: 6 }); });
    S.part({ db: -18, rv: .2, dl: .3, fx: B => filt(B, 'hp', 500) }, B => S.play('pluck', [P], 2, (t, m, len, v) => syn(B, t, m, len, .6 * v, .15, { cut: 1300, env: 1.4, dk: 20, q: 1.2, sus: 0, rel: .08 })));
  },
};
