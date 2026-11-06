// Sound design cues derived from the (already SHORT-time) spec. Every visual event that the viewer sees gets a
// matching soft paper/UI sound, so a new short needs zero audio authoring. spec.sfx = {mute: true} disables it,
// spec.sfx.extra = [[t, 'tap' | 'pop' | 'slide' | 'bell' | 'thud', gain?]] adds manual hits (SOURCE time, mapped).
// Noise whooshes ("squish": swish/slide/air) stay rare and quiet. A paper slide plays only when the paper sheet comes
// back over a full-camera frame (or for the very first sheet), never on a card swapping in place, and at most one every
// spec.sfx.slideGap s (default 8), scaled by spec.sfx.swish (default .35). Highlights are a soft felt `marker`, not a
// scratch, at most one per .9 s, scaled by spec.sfx.marker (default 1, 0 = silent). Layout moves, card moves, dims,
// exits and title words are silent or use a tick/pop.
// spec.sfx.accents (default 0 = off, profile `sfx.accents`) adds a few glassy blips on key moments only: a logo or icon
// landing, a blue bar reaching its value, a speaker tag or blue chip, a strike. At most one every spec.sfx.accentGap s
// (default 1.5). Clicks on every text, swells on every bar and typing sounded like noise.
// spec.sfx.appear = 'slide' (soft mode, review 2026-10-06 "trop de bruit, toujours le même bruit"): every actor and
// board item appearing gets one very quiet paper slide (spec.sfx.appearGain, default .1), at most one every
// spec.sfx.appearGap s (default 1.2); board pops, bells, blips, zips and tick runs are dropped. Pair it with a lower
// spec.mix.sfx, the SFX bus is normalized to that level.
// spec.sfx.only = ['slide', 'shutter', ...] keeps only those sounds, spec.sfx.minGap s then thins every hit left (hits
// within .3 s count as one) to at most one per minGap, keeping tweet shutters and paper slides first. Long-form
// (format youtube) gets this by default, see LONG_SFX in lib/style.js (YouTube comments 2026-10-08 on the Mistral
// video: "les tings", "les clochettes c'est fini", 17 hits/min). Manual spec.sfx.extra hits bypass both.
import { typing } from './timeline.js';
import { hz } from './dsp.js';

const KEEP = { shutter: 3, slide: 2, thud: 1, marker: 1 };   // which hit survives the minGap thinning first

export function sfxCues(spec, tl, X0) {
  if (spec.sfx?.mute) return;
  const ONLY = spec.sfx?.only && new Set(spec.sfx.only), GAPS = spec.sfx?.minGap ?? 0, rec = [];
  const X1 = ONLY || GAPS ? new Proxy(X0, { get: (o, k) => typeof o[k] === 'function' && k !== 'rand'
    ? (...a) => { if (!ONLY || ONLY.has(k)) rec.push([k, a]); } : o[k] }) : X0;
  // spec.sfx.tick (profile sfx.tick): 'tick' (default) keeps the clock ticks; 0 drops them; 'mallet' turns every tick run
  // (counters, rows, lists) into a rising marimba arpeggio, one note per .14 s at most (the creator 2026-10-16 on the podcast
  // counters: « le tick est insupportable »). Four notes per run at most, one per .22 s, well under the voice
  // (2026-10-16 on vendre-saas v3: « pourquoi tu mutes ce qu'il dit avec des bruits »)
  const TK = spec.sfx?.tick ?? 'tick', ARP = [0, 4, 7, 12], tk = { t: -9, k: 0, n: 0, at: [] };
  const X = TK === 'tick' ? X1 : new Proxy(X1, { get: (o, k) => k !== 'tick' ? o[k] : (t, f, g = .03, p = 0) => {
    if (!TK || tk.at.some(u => Math.abs(u - t) < .22)) return;
    if (t - tk.t > .45) { tk.k = 0; tk.n = 0; } else tk.k = Math.min(tk.k + 1, ARP.length - 1);
    tk.t = t; if (++tk.n > ARP.length) return; tk.at.push(t);
    o.mallet(t, hz(79 + ARP[tk.k]), Math.min(.035, g), p, o.SFX);
  } });
  const T = tl.duration, SW = spec.sfx?.swish ?? .35, MK = spec.sfx?.marker ?? 1, A = spec.sfx?.accents ?? 0, ST = spec.sfx?.strike ?? 1;
  const scratch = (t, len, g, p) => { if (ST > 0) X.scratch(t, len, g * ST, p); };       // hand-drawn strikes (0 = silent)
  const lands = [], marks = [], accs = [], apps = [], SOFT = spec.sfx?.appear === 'slide';
  const appear = (t, p = 0) => apps.push([t, p]);
  const acc = (t, fn) => accs.push([t, fn]);                                              // modern accent (spaced below)
  const land = (t, g = .2, p = 0) => lands.push([t, g, p]);                               // quiet paper landing (gated below)
  const mark = (t, dur = .6) => marks.push([t, dur]);                                     // highlighter sweep (spaced below)
  const whoosh = (t, len, g, o) => { if (SW > 0) X.swish(t, len, g * SW, o); };           // UI send / big reveal only

  // layout: the paper sheet moving over the camera is silent. It moves every 2-4 s and a whoosh on each move was
  // the main source of "squish"; the music bed and the entering card already carry the change.

  for (const a of spec.actors || []) {
    const t0 = a.from - (a.pre || 0);
    if (SOFT) { appear(t0 + .05, a.enter === 'right' ? .5 : 0); for (const m of [].concat(a.mark || [], a.marks || [])) mark(m.at, m.dur ?? .6); continue; }
    if (t0 > .05) land(t0 + .05, .22, a.enter === 'right' ? .5 : 0); else X.thud(0.02, .25);
    for (const [t] of (a.labelKeys || []).slice(1)) X.tick(t, 2200, .035);
    for (const m of [].concat(a.mark || [], a.marks || [])) mark(m.at, m.dur ?? .6);
    if (a.ringAt != null) X.pop(a.ringAt, 640, .1);
    if (a.badge) { X.pop(a.badge.at + .1, 760, .12, .4); X.bell(a.badge.at + .15, hz(88), .045, .4); }
  }

  for (const s of spec.scenes || []) {
    const f = s.from;
    if (s.type === 'stat') {
      land(f + .06, .18);
      const n = 16; for (let k = 0; k < n; k++) { const u = k / (n - 1), e = 1 - Math.pow(1 - u, 2.2); X.tick(s.countFrom + (s.countTo - s.countFrom) * e, 1600 + k * 70, .04); }
      X.thud(s.countTo, .3); X.bell(s.countTo + .01, hz(84), .05); X.bell(s.countTo + .04, hz(91), .035, .3);
    }
    if (s.type === 'race') {   // quiet count ticks while the meters run, a pop when each model finishes, a bell on the winner
      land(f + .06, .2);
      const maxT = Math.max(...s.panels.map(p => p.time || 1));
      const ends = s.panels.map(p => s.countFrom + (s.countTo - s.countFrom) * Math.max(.35, (p.time || maxT) / maxT));
      const n = 12; for (let k = 0; k < n; k++) { const u = k / (n - 1); X.tick(s.countFrom + (Math.max(...ends) - s.countFrom) * u, 1700 + k * 60, .028); }
      ends.forEach((e, i) => X.pop(e, 560 + i * 90, .1, -.35 + .7 * i));
      if (s.winnerAt != null) { X.thud(s.winnerAt, .22); X.bell(s.winnerAt + .02, hz(84), .045); X.bell(s.winnerAt + .06, hz(91), .03, .3); }
      if (s.chip) X.pop(s.chip.at + .03, 640, .1);
    }
    if (s.type === 'bars') {
      (s.tags || []).forEach((g, i) => X.pop(g.at, 560 + i * 90, .1, -.3 + .6 * i));
      s.rows.forEach((r, i) => { X.tick(r.at + .02, 1500 + i * 120, .03); X.pop(r.at + .08, 420 + i * 60, .08); });
      if (s.gapAt != null) { X.pop(s.gapAt, 380, .08); X.marker(s.gapAt + .15, .32, .1 * MK); }
    }
    if (s.type === 'tiles') {
      if (s.header) X.tick(s.header.at + .05, 2000, .03);
      s.items.forEach((it, i) => { X.pop(it.at + .05, 520 + i * 70, .1, -.4 + .4 * i); if (it.strikeAt != null) scratch(it.strikeAt, .3, .12, -.4 + .4 * i); });
    }
    if (s.type === 'title') {
      s.lines.forEach((ln, i) => X.pop(ln.at + .04, 560 + i * 80, .06));
      s.lines.forEach(ln => { if (ln.emphAt != null) { X.bell(ln.emphAt, hz(86), .04); X.bell(ln.emphAt + .03, hz(93), .03, .3); } });
    }
    if (s.type === 'slide') {   // clean slides: one hit for the headline, one per item (soft: a quiet paper slide each)
      const t0 = f - (s.pre || 0);
      const items = (s.items || []).flatMap((it, i) => it.k === 'bars' ? it.rows.map((r, j) => ({ ...r, x: it.x + it.w / 2, at: r.at ?? (it.at ?? t0 + .25 + i * .12) + j * .12 })) : [{ ...it, at: it.at ?? t0 + .25 + i * .12 }]);
      if (SOFT) { if (t0 > .05) appear(t0 + .02); for (const it of items) if (!it.ghost) appear(it.at + .04, it.x != null ? (it.x - 540) / 900 : 0); continue; }
      if (t0 > .05) X.tick(t0 + .04, 2000, .03);
      for (const it of items) {
        const pan = it.x != null ? (it.x - 540) / 900 : 0;
        if (!it.ghost) X.pop(it.at + .04, it.k === 'pill' ? 680 : 560, .06, pan);
        if (it.countAt != null) { const a = it.countAt, b = it.until ?? a + 1.2, n = 12; for (let k = 0; k < n; k++) X.tick(a + (b - a) * (1 - Math.pow(1 - k / (n - 1), 2.2)), 1600 + k * 70, .028, pan); if (it.win) X.bell(b + .01, hz(84), .035, pan); }
        if (it.strikeAt != null) scratch(it.strikeAt, .3, .1, pan);
        if (it.badgeAt != null) X.pop(it.badgeAt + .03, 700, .07, pan);
        if (it.ringAt != null) X.bell(it.ringAt + .02, hz(86), .035, pan);
      }
      continue;
    }
    if (s.type === 'board') {   // one quiet hit per item entering, keyed by kind; same-time items share a single hit
      const seen = new Set();
      for (const it of s.items) {
        if (it.quiet || it.k === 'rect' || it.k === 'glass') continue;   // a plain rect has no sound and must not claim the slot of the item it backs
        const t = (it.at ?? f) - (it.pre ?? 0), key = Math.round(t * 8);
        const pan = it.x != null ? (it.x - 540) / 900 : 0;
        if (SOFT) { appear(t + .05, pan); continue; }
        if (A > 0) {   // accents on their own timing, never deduped
          if (it.k === 'bar' && it.blue && it.fillTo != null) acc(it.fillTo, () => X.blip(it.fillTo, 1560, .032 * A));
          if (it.strikeAt != null) acc(it.strikeAt, () => X.zip(it.strikeAt, .26, .04 * A, pan));
        }
        if (it.k === 'shatter' && it.breakAt != null) { X.thud(it.breakAt, .34); X.pop(it.breakAt + .01, 420, .12, pan); }   // + a glass file in sfx.files
        if (seen.has(key) && it.k !== 'stamp' && it.k !== 'counter') continue; seen.add(key);
        if (A > 0 && (it.k === 'logo' || it.k === 'icon' || it.k === 'shatter')) acc(t, () => X.blip(t + .07, it.k === 'icon' ? 1180 : 1320, .032 * A, pan));
        const tagChip = A > 0 && it.k === 'chip' && (it.dot || it.blue);
        if (tagChip) acc(t, () => X.blip(t + .06, 1560, .03 * A, pan));
        if (it.k === 'stamp') { X.thud(t + .02, .24); X.pop(t + .04, 480, .1, pan); }
        else if (it.k === 'counter') {
          const a = it.countFrom ?? t, b = it.countTo ?? a + .9, n = 14;
          for (let k = 0; k < n; k++) { const u = k / (n - 1), e = 1 - Math.pow(1 - u, 2.2); X.tick(a + (b - a) * e, 1600 + k * 70, .035); }
          if (TK === 'tick') { X.thud(b, .24); X.bell(b + .01, hz(84), .04); } else if (TK) X.bell(b + .01, hz(91), .025);
        }
        else if (it.k === 'label') X.pop(t + .03, 520, (it.size || 90) >= 110 ? .1 : .08, pan);
        else if (it.k === 'chip') { if (!tagChip) X.pop(t + .04, it.blue ? 680 : 600, .09, pan); }   // accents: a blip instead
        else if (it.k === 'text') X.pop(t + .04, 560, (it.size || 64) >= 90 ? .07 : .05, pan);
        else if (it.k === 'bubble') X.tap(t + .04, it.side === 'me' ? .3 : .24);
        else if (it.k === 'icon' || it.k === 'card' || it.k === 'img' || it.k === 'yt') land(t + .05, .18, pan);
        else if (it.k === 'term') {   // keys while the command types, Enter, a tick per output line
          land(t + .05, .18, pan);
          const c = it.cmd || '', a = it.typeFrom ?? t, b = it.typeTo ?? a + c.length * .05;
          for (let k = 0; k < c.length; k++) X.key(a + (b - a) * k / c.length, .05 + .02 * X.rand(), .1);
          if (it.sendAt != null) X.tap(it.sendAt, .32, .1);
          for (const o of it.out || []) X.tick(o.at + .04, 1700, .028);
        }
        else if (it.k === 'screen') { land(t + .05, .18, pan); for (const g of [...(it.rings || []), ...(it.arrows || [])]) if (g.at != null) X.tick(g.at + .06, 1650, .03); }
        else if (it.k === 'toggle') { X.pop(t + .04, 560, .05, pan); if (it.onAt != null) X.tap(it.onAt, .3, pan); }
        else if (it.k === 'check') { X.bell(t + .1, hz(88), .04, pan); X.bell(t + .14, hz(95), .03, pan); }
        else if (it.k === 'bar') X.tick(t + .05, 1500, .03);
        else if (it.k === 'dots' || it.k === 'thumbs' || it.k === 'agents') { for (let k = 0; k < 6; k++) X.tick(t + .04 + k * .07, 1900 + k * 90, .025); }
        else if (it.k === 'diverge') X.tick(t + .05, 1700, .03);
        else if (it.k === 'reticle') { const a = it.closeFrom ?? t, b = it.closeTo ?? a + .8; for (let k = 0; k < 5; k++) X.tick(a + (b - a) * k / 4, 2200 + k * 120, .03); X.pop(b, 700, .09); }
        else if (it.k === 'edit') {   // the timeline edits itself: a tick on the marks, a snap when the silences close, ticks per caption, a chime on the animations
          land(t + .05, .18, pan);
          if (it.markAt != null) X.tick(it.markAt + .04, 2100, .03);
          if (it.cutAt != null) { X.tick(it.cutAt, 2500, .035); X.pop(it.cutAt + .4, 520, .08); }
          if (it.capsAt != null) for (let k = 0; k < Math.min(6, (it.imgs || []).length); k++) X.tick(it.capsAt + .04 + k * .07, 1800 + k * 90, .025);
          if (it.fxAt != null) { X.bell(it.fxAt + .08, hz(88), .03, pan); X.bell(it.fxAt + .12, hz(95), .022, pan); }
        }
        if (it.ringAt != null) X.pop(it.ringAt, 640, .09);
        if (it.emphAt != null) { X.bell(it.emphAt, hz(86), .035); X.bell(it.emphAt + .03, hz(93), .025, .3); }
        for (const g of it.groups || []) X.pop(g.at + .03, 600, .07);
        if (it.reticleAt != null) { X.tick(it.reticleAt, 2400, .04); X.thud(it.reticleAt + .3, .18); }
      }
    }
    if (s.type === 'chat') {
      land(f + .08, .22);
      X.tap(s.newChatAt, .3, .3);
      X.tap(s.focusAt, .28, -.1);
      const toks = typing(s.prompt.text, tl.words, s.prompt.from, s.prompt.to);
      let last = -1;
      toks.forEach(k => {
        const d = Math.min(.26, Math.max(.08, k.end - k.start)), n = k.tok.length + 1;
        for (let c = 0; c < n; c++) { const t = k.start + d * c / n; if (t - last > .05) { X.key(t, .06 + .03 * X.rand(), -.2 + .4 * X.rand()); last = t; } }
      });
      X.tap(s.sendAt, .32, .2); whoosh(s.sendAt + .02, .45, .2, { f0: 700, f1: 3000, pk: .35 });
      if (s.workFrom != null) for (let t = s.workFrom + .2, k = 0; t < s.workTo; t += .32, k++) X.tick(t, 1800 + (k % 2) * 400, .018, .2);
      if (s.result) { land(s.result.at + .05, .22); X.bell(s.result.at + .1, hz(84), .045); X.bell(s.result.at + .16, hz(88), .035, .25); }
    }
    if (s.type === 'convo') {   // the voices carry the words: only a soft tap per bubble, a pop per reply, a bell on the image
      land(f + .08, .22);
      for (const m of s.msgs) {
        if (m.who === 'me') X.tap(m.from - .1, .2, .25);
        else if (m.image) { X.pop(m.at + .04, 560, .08); X.air(m.genFrom, m.sharpAt - m.genFrom, .1); X.thud(m.sharpAt, .16); X.bell(m.sharpAt, hz(84), .05); X.bell(m.sharpAt + .05, hz(91), .035, .25); }
        else X.pop(m.at + .02, 620, .06, -.25);
      }
    }
    if (s.type === 'scatter') {
      land(f + .06, .2);
      s.points.forEach((p, i) => p.label ? X.pop(p.at + .03, 520 + i * 80, p.color === 'gray' ? .07 : .11, -.4 + .1 * i) : X.tick(p.at, 1700 + i * 60, .025));
      for (const a of s.arrows || []) { X.marker(a.at, .32, .08 * MK, .2); if (a.card) X.pop(a.card.at, 640, .09, .3); if (a.card?.sub) X.tick(a.card.sub.at, 2200, .035); }
      if (s.dyAt != null) X.marker(s.dyAt + .15, .32, .09 * MK);
      if (s.dyChip) X.pop(s.dyChip.at, 640, .09, .4);
      if (s.dxAt != null) X.marker(s.dxAt, .32, .09 * MK);
      if (s.dxChip) X.pop(s.dxChip.at, 700, .09);
      if (s.ringAt != null) { X.pop(s.ringAt, 760, .1); X.bell(s.ringAt + .05, hz(86), .045); X.bell(s.ringAt + .09, hz(91), .035, .3); }
    }
    if (s.type === 'switch') {
      land(f + .06, .18);
      (s.headerKeys || []).slice(1).forEach(([t]) => X.tick(t, 2100, .03));
      (s.sideKeys || []).slice(1).forEach(([t], i) => { X.tap(t, .3, i % 2 ? .25 : -.25); X.pop(t + .1, 640 + (i % 2) * 90, .07); });
      (s.chips || []).forEach((c, i) => X.pop(c.at, 560 + i * 70, .09, c.side ? .35 : -.35));
      if (A > 0) (s.chips || []).forEach(c => acc(c.at, () => X.blip(c.at + .06, 1560, .03 * A, c.side ? .35 : -.35)));
    }
    if (s.type === 'tree') {
      land(f + .06, .2);
      s.lines.forEach((ln, i) => { X.tick(ln.at, 1900 + i * 90, .035); if (ln.link) X.pop(ln.link.at + .06, 700, .08, .3); });
    }
    if (s.type === 'snap') { X.snap(f, .55, -.3); X.bell(f + .08, hz(96), .03, .3); }
    if (s.type === 'xylo') {
      land(f + .06, .18); s.notes.forEach((_, i) => X.tick(f + .1 + i * .08, 1500 + i * 120, .03, -.3 + .2 * i));
      (s.hitKeys || []).forEach(([t, i]) => { const m = (s.midi || [76, 79, 81, 84])[i]; X.mallet(t, hz(m), .32, -.45 + .3 * i, X.SFX); X.bell(t + .005, hz(m + 12), .03, -.45 + .3 * i); });
    }
    if (s.type === 'sfxtrack') {
      land(f + .06, .2); if (s.tag) X.pop(s.tag.at, 700, .09, .4);
      s.rows.forEach((r, i) => X.tick(r.at, 1700 + i * 110, .035));
      if (s.playFrom != null) whoosh(s.playFrom, Math.max(.4, s.playTo - s.playFrom), .06, { f0: 400, f1: 1600, pk: .5, p0: -.6, p1: .6 });
    }
    if (s.type === 'popover') {
      X.pop(f + .02, 560, .12);
      const toks = typing(s.message.text, tl.words, s.message.from, s.message.to); let last = -1;
      toks.forEach(k => { const d = Math.min(.26, Math.max(.08, k.end - k.start)), n = k.tok.length + 1;
        for (let c = 0; c < n; c++) { const t = k.start + d * c / n; if (t - last > .05) { X.key(t, .05 + .03 * X.rand(), -.2 + .4 * X.rand()); last = t; } } });
      if (s.clickAt != null) { X.tap(s.clickAt, .34, .2); X.pop(s.clickAt + .06, 700, .09, .2); }

    }
    if (s.type === 'pause') { X.stop(f - .02, .55, .22); X.thud(f, .18); if (s.to != null) { X.start(s.to - .36, .38, .16); X.tap(s.to - .02, .3); } }
    if (s.type === 'pipeline') {
      land(f + .06, .2); if (s.header) X.tick(s.header.at, 2000, .03);
      s.rows.forEach((r, i) => { X.pop(r.at + .03, 520 + i * 60, .09, -.3 + .12 * i); X.tick(r.at + .45, 2400 + i * 80, .03, .4); });
    }
    if (s.type === 'comment') {
      land(f + .06, .22); X.tap(s.clickAt, .3, .1);
      if (s.typed) { const n = s.typed.length; for (let c = 0; c < n; c += 1) X.key(s.typeFrom + (s.typeTo - s.typeFrom) * c / n, .05 + .02 * X.rand(), .1); }
      if (s.sendAt != null) { X.tap(s.sendAt, .32, .3); whoosh(s.sendAt + .02, .4, .18, { f0: 700, f1: 3000, pk: .35 }); X.bell(s.sendAt + .1, hz(84), .045, .3); }
    }
    if (s.type === 'tweet') { if (s.photo) X.shutter(f - (s.pre || 0) + .02, .3); else land(f + .06, .2); for (const m of s.marks || []) mark(m.at, m.dur ?? .7); }
    if (s.type === 'columns') {
      let k = 0; for (const g of s.groups) {
        for (const c of g.cols) { X.tick(c.at + .02, 1500 + k * 120, .03); X.pop(c.at + .08, 420 + k * 60, .06, -.3 + .2 * k); k++; }
        if (g.ghost) { X.marker(g.ghost.at + .05, .3, .08 * MK, .2); if (g.ghost.chip) X.pop(g.ghost.chip.at, 640, .08, .3); }
      }
    }
    if (s.type === 'recap') {
      if (s.header) X.pop(s.header.at + .03, 560, .06);
      s.rows.forEach((r, i) => X.tick(r.at + .02, 1700 + i * 70, .025, -.3 + .07 * i));
    }
    if (s.type === 'usage') {
      land(f + .06, .2);
      s.rows.forEach((r, i) => { if (r.fill) { X.marker(r.fill.at, .4, .08 * MK, .2); X.thud(r.fill.at + .55, .16); } if (r.mark) X.tick(r.mark.at, 2000 + i * 150, .035); });
    }
    // motion-design film beats: each one enters with a swish and lands, then its own event sounds
    if (s.type?.startsWith('md') && s.type !== 'mdGrid') { whoosh(f - .12, .32, .5, { p0: .5, p1: -.3 }); land(f + .1, .18); }
    if (s.type === 'mdIntro') { X.thud(f + .08, .2); X.bell(f + .15, hz(84), .05, 0); X.bell(f + .3, hz(91), .035, .2); }
    if (s.type === 'mdRec') { X.tick(f + .3, 2600, .03); if (s.stamp) { X.thud(s.stamp.at, .2); X.pop(s.stamp.at + .02, 520, .1); } }
    if (s.type === 'mdWave') {
      scratch(s.sweepFrom, Math.min(1.2, s.sweepTo - s.sweepFrom), .05, .1);
      s.words.forEach((_, i) => X.tick(s.sweepFrom + (s.sweepTo - s.sweepFrom) * ((i + .5) / s.words.length) * .92, 2000 + i * 120, .03, -.3 + .12 * i));
      if (s.markAt != null) X.bell(s.markAt, hz(93), .04, .3);
    }
    if (s.type === 'mdVision') {
      whoosh(s.scanFrom, s.scanTo - s.scanFrom, .45, { f0: 300, f1: 1400 });
      if (s.flipAt != null) for (let k = 0; k < 10; k++) X.tick(s.flipAt + k * .07, 2800 + k * 40, .022, -.2 + .04 * k);
    }
    if (s.type === 'mdDiffuse') {
      if (s.prompt) { let last = -1; for (let t = s.prompt.from; t < s.prompt.to; t += .065 + .03 * X.rand()) { if (t - last > .05) { X.key(t, .045 + .02 * X.rand(), -.1 + .2 * X.rand()); last = t; } } X.tap(s.prompt.to + .02, .25); }
      X.air(s.genFrom, s.sharpAt - s.genFrom, .12);
      X.bell(s.sharpAt, hz(88), .05, 0); X.thud(s.sharpAt, .16);
    }
    if (s.type === 'mdCode') s.lines.forEach(ln => {
      const d = ln.dur ?? ln.text.length * .03, e = ln.at + d;
      for (let c = 0; c < ln.text.length; c += 2) X.key(ln.at + d * c / ln.text.length, .035 + .02 * X.rand(), -.1 + .2 * X.rand());
      if (ln.fx === 'xylo') [76, 79, 81, 84].forEach((m, i) => X.mallet(e + .05 + i * .13, hz(m), .09, -.2 + .13 * i));
      else if (ln.fx === 'snap') X.snap(e + .05, .4, .2);
      else if (ln.fx === 'birds') { X.chirp(e + .05, 3200, 4200, .09, .04, .3); X.chirp(e + .2, 3600, 4600, .08, .035, -.2); X.chirp(e + .32, 3000, 4000, .1, .03, .1); }
      else if (ln.fx === 'tom') [0, .15, .3].forEach((d, i) => X.tom(e + .05 + d, .35, 100 + 18 * i, -.3 + .3 * i));
      else if (ln.fx === 'swish') X.swish(e, .45, .12, { f0: 400, f1: 3200, pk: .4 });
      else if (ln.fx === 'bass') X.bass(e + .05, hz(40), .45, .6);
      else X.pop(e + .04, 640, .07);
    });
    if (s.type === 'mdAssemble') {
      let k = 0; s.tracks.forEach(tr => tr.clips.forEach(() => { const at = s.flyFrom + k * (s.stagger ?? .075) + .22; if (k % 2 === 0) X.pop(at, 500 + (k % 7) * 70, .06, -.3 + .06 * (k % 10)); k++; }));
      whoosh(s.playFrom, s.playTo - s.playFrom, .35, { f0: 500, f1: 900 });
      if (s.stamp) { X.thud(s.stamp.at, .22); X.pop(s.stamp.at + .02, 480, .1); }
    }
    if (s.type === 'mdCut') {
      if (s.markAt != null) [0, 1, 2, 3].forEach(i => X.tick(s.markAt + i * .07, 2200 + i * 150, .03, -.3 + .2 * i));
      if (s.closeAt != null) { whoosh(s.closeAt, .5, .3, { f0: 1000, f1: 300 }); X.thud(s.closeAt + .5, .16); }
      if (s.speedAt != null) { X.thud(s.speedAt, .2); X.pop(s.speedAt + .02, 520, .1); }
      if (s.clock) { for (let t = s.clock.at; t < s.clock.endAt; t += .11) X.tick(t, 2600, .02); X.bell(s.clock.endAt, hz(91), .045, 0); }
    }
    if (s.type === 'mdStills') {
      for (let i = 0; i < 8; i++) X.tick((s.enterAt ?? f + .1) + i * .06 + .1, 1800 + i * 90, .025, -.3 + .08 * i);
      if (s.scanFrom != null) whoosh(s.scanFrom, Math.max(.4, (s.flagAt ?? s.scanFrom + 1.5) - s.scanFrom), .25, { f0: 400, f1: 900 });
      if (s.flagAt != null) { X.pop(s.flagAt, 420, .1); X.thud(s.flagAt, .14); }
      if (s.fixAt != null) { X.bell(s.fixAt + .05, hz(88), .045, .1); X.bell(s.fixAt + .17, hz(95), .035, .2); }
    }
    if (s.type === 'mdRender') {
      for (let t = s.renderFrom; t < s.renderTo; t += .09) X.tick(t, 2400 + 600 * ((t - s.renderFrom) / (s.renderTo - s.renderFrom)), .018);
      X.bell(s.renderTo, hz(91), .045, 0);
      (s.bars || []).forEach(b => { X.thud(b.at + .05, .15); if (b.blue) X.bell(b.at + .3, hz(96), .04, .2); });
    }
    if (s.type === 'chip') X.pop(f + .03, 600, .1);
    if (s.type === 'cta') {
      land(f + .08, .22);
      X.tap(s.clickAt, .34, .3); X.pop(s.clickAt + .08, 700, .1, .3); X.bell(s.clickAt + .14, hz(84), .05, .2); X.bell(s.clickAt + .2, hz(91), .04, .3);
    }
  }
  const cu = [].concat(spec.cutout || []).find(c => c.mode === 'cam');
  if (cu?.mode === 'cam') for (const L of [...(cu.bg || []), { at: cu.to }]) if (L.at != null && L.at < T) {
    whoosh(L.at - .04, .42, .2, { f0: 500, f1: 3600, pk: .35 });
    if (L.birds) for (let k = 0, t = L.at + .35; t < (L.birdsTo ?? L.at + 4) && k < 12; k++, t += .45 + .5 * X.rand()) X.chirp(t, 2600 + 1400 * X.rand(), 3800 + 1600 * X.rand(), .06 + .06 * X.rand(), .022, -.6 + 1.2 * X.rand());
  }
  // paper slides: only when the sheet re-enters over a full-camera frame (seam 0 just before, paper visible just
  // after) or for the first thing on paper, then thinned to one per slideGap. Card swaps on visible paper are silent.
  const seam = spec.layout?.keys || [], GAP = spec.sfx?.slideGap ?? 8;
  const seamAt = t => { let v = seam.length ? seam[0][1] : 960; for (const [k, y] of seam) if (k <= t) v = y; return v; };
  const first = Math.min(...(spec.actors || []).map(a => a.from - (a.pre || 0)), ...(spec.scenes || []).filter(s => s.layer !== 'over' && s.layer !== 'top').map(s => s.from));
  let lastLand = -1e9;
  for (const [t, g, p] of lands.sort((a, b) => a[0] - b[0])) {
    const enters = (seamAt(t - .2) <= 0 && seamAt(t + .4) > 0) || t <= first + .15;
    if (SW > 0 && enters && t - lastLand >= GAP) { X.slide(t, g * SW, p); lastLand = t; }
  }
  let lastApp = -1e9; const APG = spec.sfx?.appearGap ?? 1.2, APV = spec.sfx?.appearGain ?? .1;
  for (const [t, p] of apps.sort((a, b) => a[0] - b[0])) if (t - lastApp >= APG) { X.slide(t, APV, Math.max(-.5, Math.min(.5, p))); lastApp = t; }
  let lastAcc = -1e9; const AG = spec.sfx?.accentGap ?? 1.5;
  for (const [t, fn] of accs.sort((a, b) => a[0] - b[0])) if (t - lastAcc >= AG) { fn(); lastAcc = t; }
  let lastMark = -1e9;
  for (const [t, dur] of marks.sort((a, b) => a[0] - b[0])) if (MK > 0 && t - lastMark >= .9) { X.marker(t, Math.min(.32, dur * .5), .1 * MK, .2); lastMark = t; }

  if (X !== X0) {   // group hits into events (.3 s), keep the best ones at least GAPS s apart, replay them
    const ev = []; for (const h of rec.sort((a, b) => a[1][0] - b[1][0])) {
      const e = ev[ev.length - 1]; if (e && h[1][0] - e.t < .3) e.hits.push(h); else ev.push({ t: h[1][0], hits: [h] });
    }
    const pr = e => Math.max(...e.hits.map(([k]) => KEEP[k] || 0)), kept = [];
    for (const e of [...ev].sort((a, b) => pr(b) - pr(a) || a.t - b.t)) if (kept.every(k => Math.abs(k.t - e.t) >= GAPS)) kept.push(e);
    for (const e of kept) for (const [k, a] of e.hits) X0[k](...a);
  }

  const m = spec._map;
  for (const [t, kind, g] of spec.sfx?.extra || []) {
    const tt = m ? m(t) : t;
    const X = X0;
    ({ tap: () => X.tap(tt, g ?? .3), pop: () => X.pop(tt, 600, g ?? .1), slide: () => X.slide(tt, g ?? .22), bell: () => X.bell(tt, hz(84), g ?? .05), thud: () => X.thud(tt, g ?? .3), tom: () => X.tom(tt, g ?? .5, 95 + 40 * X.rand(), -.3 + .6 * X.rand()), swish: () => X.swish(tt - .1, .45, g ?? .12, { f0: 400, f1: 3200, pk: .4 }) })[kind]?.();
  }
}

// spec.sfx.kit: a hard-cut style's own sound files (profile sfx.kit, e.g. nico-slowdown), laid on the edit by itself:
// {cut, pop, punch, gain: {cut: -13, pop: -11, punch: -9}, gap: .12}. cut = every seam change, every B-roll and cutout
// start or end; pop = every board img / logo / icon landing (sticker heads, swaps through imgKeys); punch = every instant
// zoom (a zoom key with a spring of 60 or more, e.g. [t, 1.39, 400]). Same kind closer than gap s plays once; a cut that
// lands with a pop or a punch gives way to it. Files are levelled like sfx.files, their loudest sample on the event.
export function kitHits(spec, T) {
  const K = spec.sfx?.kit; if (!K || spec.sfx?.mute) return { files: [] };
  const ev = { cut: [], pop: [], punch: [] }, G = { cut: -13, pop: -11, punch: -9, ...(K.gain || {}) }, gap = K.gap ?? .12;
  const lk = spec.layout?.keys || []; lk.forEach(([t, y], i) => { if (i && t > .05 && y !== lk[i - 1][1]) ev.cut.push(t); });
  for (const b of [].concat(spec.broll || [], spec.cutout || [])) for (const t of [b.from, b.to]) if (t > .05 && t < T - .05) ev.cut.push(t);
  for (const t of spec._jumps || []) if (t > .05 && t < T - .05) ev.cut.push(t);   // spec.cut joins: a jump cut clicks too
  // punch = an instant zoom IN away from a cut; a snap back out or a reframe on a cut keeps the cut's click
  const zk = spec.zoom?.keys || []; zk.forEach(([t, z, w], i) => { if ((w ?? 0) >= 60 && t > .02 && i && z > zk[i - 1][1] * 1.04 && !ev.cut.some(u => Math.abs(u - t) < .08)) ev.punch.push(t); });
  for (const s of spec.scenes || []) if (s.type === 'board') for (const it of s.items || []) {
    if (it.quiet || !['img', 'logo', 'icon'].includes(it.k)) continue;
    ev.pop.push((it.at ?? s.from) - (it.pre ?? 0)); for (const [t] of (it.imgKeys || []).slice(1)) ev.pop.push(t);
  }
  const busy = [...ev.pop, ...ev.punch], files = [];
  for (const kind of ['punch', 'pop', 'cut']) {
    if (!K[kind]) continue; let last = -1e9;
    for (const t of ev[kind].sort((a, b) => a - b)) {
      if (t - last < gap || t < 0 || t >= T) continue;
      if (kind === 'cut' && busy.some(u => Math.abs(u - t) < .08)) continue;
      files.push({ kit: kind, at: t, src: K[kind], gain: G[kind], peak: true }); last = t;
    }
  }
  return { files };
}

// Music bed: 4-chord loop, soft kick/rim/hats, bass, mallet arpeggio. spec.music = {bpm, breaks: [[a, b]] (drums
// drop out), end, drive (punchier groove)} in SOURCE time (mapped by the caller). Levels here are relative; the mixer sets the bed level.
export function score(spec, tl, X) {
  const M = spec.music || {}, T = tl.duration, end = Math.min(T, M.end ?? T), st = M.start ?? 0;
  // music.start: the bed enters later (e.g. after an on-camera count-in). tl.pause: the bed stops dead (tape stop)
  // and restarts from bar 1 on the resume, so the downbeat lands with the video coming back.
  const pz = tl.pause, segs = pz && pz.t0 > st && pz.t0 < end ? [[st, pz.t0, 0], [pz.t0 + pz.dur, end, 1]] : [[st, end, 0]];
  segs.forEach(([a, c, i]) => bed(M, X, a, c, T, i === segs.length - 1));
  if (segs.length > 1) X.pad(pz.t0 + .4, pz.t0 + pz.dur - .1, [52, 55, 59, 62], .45, 1.4, .3);   // soft hold under the narrator
}
function bed(M, X, st, end, T, last) {
  const bpm = M.bpm || 112, b = 60 / bpm;
  const breaks = M.breaks || [], inBreak = t => breaks.some(([a, c]) => t >= a && t < c);
  // Cmaj9 | Am9 | Fmaj7#11 | G6sus: bright, open, never sad
  const CH = [
    { root: 36, pad: [55, 59, 62, 64], arp: [72, 76, 79, 83, 86] },
    { root: 33, pad: [55, 60, 64, 67], arp: [69, 72, 76, 79, 83] },
    { root: 29, pad: [57, 60, 64, 71], arp: [69, 72, 77, 79, 83] },
    { root: 31, pad: [55, 60, 62, 64], arp: [67, 71, 74, 76, 79] },
  ];
  const bar = 4 * b, bars = Math.ceil((end - st) / bar);
  for (let k = 0; k < bars; k++) {
    const t0 = st + k * bar, c = CH[k % 4], t1 = Math.min(end, t0 + bar);
    X.pad(t0, t1 + (last ? .05 : .02), c.pad, 1, k ? .08 : (st ? .02 : .4), last ? .5 : .08);
    for (let j = 0; j < 8; j++) {
      const t = t0 + j * b / 2; if (t >= end - .05) break;
      const br = inBreak(t);
      if (!br && M.drive) {   // music.drive: four-on-the-floor, clap backbeat, 16th hats, pumping 8th bass, fill every 4 bars
        const fill = k % 4 === 3 || inBreak(t0 + bar + .01);
        if (j % 2 === 0) X.kick(t, .95); else if (j === 7 && k % 2) X.kick(t, .45);
        if (j === 2 || j === 6) X.clap(t, .95);
        X.hat(t, j % 2 ? .8 : .45, j % 2 ? .25 : .1); X.hat(t + b / 4, .4, -.2);
        X.bass(t, hz(c.root + (j % 2 ? 12 : 0)), b * .36, j % 2 ? .7 : .95);
        if (fill && j >= 6) { X.rim(t + b / 4, .75); X.clap(t + b / 4, .5); }
      } else if (!br) {
        if (j === 0 || j === 4 || (j === 7 && k % 2 === 1)) X.kick(t, j === 7 ? .5 : .9);
        if (j === 2 || j === 6) X.rim(t, .7);
        X.hat(t, j % 2 ? .55 : .9, j % 2 ? .25 : .1);
        if (j === 0 || j === 3 || j === 4 || j === 6) X.bass(t, hz(c.root + 12 * (j === 6 ? 1 : 0)), b * .42, .9);
      }
      const n = c.arp[[0, 2, 1, 3, 2, 4, 3, 1][j]];
      X.mallet(t + .004, hz(n), br ? .05 : .065, -.35 + .7 * (j / 7));
      if (M.drive && !br && k % 2) X.mallet(t + b / 4 + .004, hz(c.arp[[4, 3, 2, 1, 0, 1, 2, 3][j]]), .035, .35 - .7 * (j / 7));   // 16th answer
    }
  }
  // resolve: single held chord to the end so the short can loop cleanly
  if (last && end < T - .1) X.pad(end, T, CH[0].pad, .9, .05, .6);
}
