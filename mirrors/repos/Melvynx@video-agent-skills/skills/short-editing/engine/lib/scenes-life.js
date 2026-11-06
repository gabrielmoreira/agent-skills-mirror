// Life scenes: a composable `board` for narrative / opinion shorts (first used by the "live IA" shorts).
// One scene, many small items, each with its own spoken `at`, so a beat is authored as data instead of a new scene.
//   {type: 'board', from, to, pre, layer, items: [{k, at, to, x, y, ...}]}
// Common item params: at (enter), to (exit), rise (px, default 40), dx (enter slide), posKeys [[t, [x, y]]],
// scaleKeys [[t, s]], rotKeys [[t, rad]], pop (enter scale, e.g. .6, springs to 1), spin (enter rotation in rad, settles to rot),
// dimAt (fade to 35% + desaturate to ink3), cut (in and out on the frame), still (never translates on enter/exit).
// Board: push (slow zoom over its life, e.g. .06, around pushAt [x, y]; 0 = off),
// outDx (exit slides sideways by outDx px instead of rising: a whip to the next board). Kinds:
//   text     {text, size 64, weight 800, color, align 'center', words: true (stagger), emph, emphAt, lh, maxW}
//   chip     {text, size 42, blue, dark, dot, dotColor (default the accent)}
//   nametag  {text, size 28, weight 600, liveSpans [[a, b]]}: paper name tag, (x, y) = bottom-left, accent while live
//   label    {text ('\n' = new line), size 90, bg 'blue' | 'pop' | 'ink' | hex, color, rot -.035, skew .2, caps true, align, border}   slanted thumbnail label box
//   stamp    {text, size 70, rot -.07, solid true}
//   counter  {value, fromValue 0, countFrom, countTo, size 200, prefix, suffix (blue, suffixColor 'ink' on a marker line), sep ' ', unit (small blue tail), decimals, decSep ',', clock (value in s shown m:ss, fixed digit slots)}
//   bar      {w, h 96, value, fromValue 0, fillFrom, fillTo, label, valueText, blue, dark}
//   bubble   {text, side 'me' | 'them', w 760, size 44, typeFrom, typeTo, name}
//   card     {w, h, r 36, elev 1, fill 'ink' | 'tint' | null}
//   line     {x2, y2, lw 8, color, dash, dur .45, head (arrow), bend (curve, e.g. .25)}   x/y = start, drawn on over `dur`
//   circle   {r, lw 6, color, dash, fill 'tint'}
//   dots     {cols, rows, gap 56, r 18, color 'ink3', groups: [{i0, n, at, color}]}
//   thumbs   {cols, rows, w 190, h 107, gap 18, stagger .05}
//   agents   {cols 5, rows 5, w 168, h 112, gap 16, stagger .03, workFrom, workTo}
//   diverge  {w 900, h 560, splitX .38, drawFrom, drawTo, upLabel, downLabel, meAt, meLabel}
//   check    {s 80, color}
//   logo     {logo: 'assets/logos/x.png', s 140, gray}   a real app icon, centered
//   (any item) strikeAt + strikeW: a hand-drawn strike across the item, centered on (x, y), drawn left to right in .35 s; strikeColor (default 'blue',
//   'pop' or 'ink' when the accent is a light yellow). A strike-only item (k 'text', text ' ') never rises in.
//   bar      also takes logo (real icon left of the label)
//   img      {img: 'assets/images/x.png', s 200 (max w), h (max h, default s), r (corner clip), frame (white print border px), shadow true}   contain, centered
//   shatter  {logo, s 260, breakAt, hit [x, y] (-1..1 of the icon, impact point), n 10 (rays), seed, tight}   a real logo that holds, then
//            breaks into glass shards at breakAt (outward, gravity, spin) with a blue shockwave and spark lines; tight: the
//            shards are only the icon's own pieces (no white glass wedges around it, for a colored flat paper)
//   screen   {img | imgKeys [[t, img]] (content swaps in place), w 900, h 620, r 30, viewKeys [[t, [cx, cy, zoom]]] (image px center, zoom 1 = fit width), viewW 7,
//            rings: [{at, to, rect: [x, y, w, h] image px, pad 10, dim true, dur .5}], arrows: [{at, to, tip: [x, y] image px, dx 160, dy -160, bend .18, label}]}
//            marks: [{at, rects|rect: [x, y, w, h] image px, dur .7, color, pad 8}] (highlighter swept over article text),
//            a real UI screenshot in a dark window; rings and arrows ride the zoom, arrows may start outside the window
//   glass    {w, h, r 34, tint .62, blur 22}   frosted panel over whatever is under it (camera), x/y = top-left
//   gauge    {r 170, value .9, sweepFrom, sweepTo, unit}   speedometer dial, needle + blue arc sweep with a motion trail
//   pixelate {img, w 300, h (from the image), r 26, sharpFrom, sharpTo, block 44}   blocks resolve to sharp, then a light sweep
//   render   {w 900, h 420, title, imgs: [frames], progFrom, progTo, prog 1, total (frames), elapsed (s)}   a render crawling:
//            dark window, film strip developing frame by frame, striped progress bar, "Frame n / total", m:ss timer
//   edit     {imgs: [clip frames], w 960, vh 150, markAt, cutAt, capsAt, fxAt, playFrom, playTo, steps: [{text, at}]}   a timeline that
//            edits itself: the silences between real clips get boxed (markAt) and close (cutAt), "Aa" caption pills drop on each
//            clip (capsAt), blue animation blocks with a sparkle land (fxAt), a playhead runs; steps = blue chips checking one by one
//   term     {w 960, h 640, size 52, title, logo, name 'Claude Code', sub, cmd, placeholder, focusAt, typeFrom, typeTo, suggest: [[name, desc]],
//            sendAt, out: [{text, at, dim}]}   a Claude Code terminal: the slash command types in the prompt box with its
//            autocomplete list, Enter moves it to the history and the output lines land one by one
//   yt       {img (thumbnail), title, channel, avatarImg, meta, dur, w 760}   a YouTube video card, centered
//   toggle   {label, onAt, size 40}   a settings switch that flips to blue at onAt, centered
//   icon     {name, s 1, color, accent, ...}  names: robot, tomb, person, brain, gamepad, laptop, phone, coins, sun,
//            crown, hourglass, play, msg, trash, card, cap, clock, bulb, rocket, chart, bug
import { C, D, W, clamp, lerp, seg, E, S, leave, track, sheet, shadow, text, measure, midBase, wrap, chip, checkIcon, hash, noise1, lift, gloss, groove, deepness, drop, logoFinish, zoomAt, famCss } from './kit.js';

const TAU = Math.PI * 2;
const PIX = typeof document !== 'undefined' ? document.createElement('canvas') : null;   // scratch canvas for pixelate
const hex = c => [1, 3, 5].map(i => parseInt(c.slice(i, i + 2), 16));
const mix = (a, b, p) => { const x = hex(a), y = hex(b); return `rgb(${x.map((v, i) => Math.round(lerp(v, y[i], clamp(p)))).join(',')})`; };
const col = c => (c && C[c]) || c || C.ink;
function alpha(ctx, a, fn) { if (a <= .002) return; ctx.save(); ctx.globalAlpha *= a; fn(); ctx.restore(); }

// ---------------------------------------------------------------- icons (line art, centered on 0,0, ~200 px at s = 1)
function stroke(ctx, c, lw) { ctx.strokeStyle = c; ctx.lineWidth = lw; ctx.lineCap = 'round'; ctx.lineJoin = 'round'; }
const ICONS = {
  robot(ctx, o, t) {
    const c = col(o.color), b = col(o.accent || 'blue'); stroke(ctx, c, 9);
    ctx.beginPath(); ctx.moveTo(0, -96); ctx.lineTo(0, -130); ctx.stroke();
    ctx.beginPath(); ctx.arc(0, -140, 12, 0, TAU); ctx.fillStyle = b; ctx.fill();
    ctx.beginPath(); ctx.roundRect(-110, -96, 220, 180, 46); ctx.fillStyle = C.sheet; ctx.fill(); ctx.stroke();
    ctx.beginPath(); ctx.roundRect(-128, -30, 18, 56, 8); ctx.roundRect(110, -30, 18, 56, 8); ctx.fillStyle = c; ctx.fill();
    const blink = o.blinkAt != null ? 1 - .9 * Math.sin(Math.PI * clamp((t - o.blinkAt) / .18)) : 1;
    for (const ex of [-46, 46]) { ctx.beginPath(); ctx.ellipse(ex, -18, 22, 22 * blink, 0, 0, TAU); ctx.fillStyle = b; ctx.fill(); }
    ctx.beginPath(); ctx.roundRect(-56, 32, 112, 26, 10); ctx.stroke();
    stroke(ctx, c, 5); for (const gx of [-28, 0, 28]) { ctx.beginPath(); ctx.moveTo(gx, 34); ctx.lineTo(gx, 56); ctx.stroke(); }
    if (o.reticleAt != null) {   // targeting reticle closing in
      const p = S(t - o.reticleAt, 9); if (p > .002) alpha(ctx, p, () => {
        const r = lerp(260, 170, p); stroke(ctx, b, 6);
        ctx.beginPath(); ctx.arc(0, -10, r, 0, TAU); ctx.stroke();
        for (let k = 0; k < 4; k++) { const a = k * TAU / 4; ctx.beginPath(); ctx.moveTo(Math.cos(a) * (r - 30), -10 + Math.sin(a) * (r - 30)); ctx.lineTo(Math.cos(a) * (r + 34), -10 + Math.sin(a) * (r + 34)); ctx.stroke(); }
      });
    }
  },
  tomb(ctx, o) {
    const c = col(o.color); stroke(ctx, c, 9);
    ctx.beginPath(); ctx.moveTo(-90, 100); ctx.lineTo(-90, -40); ctx.arc(0, -40, 90, Math.PI, 0); ctx.lineTo(90, 100); ctx.closePath();
    ctx.fillStyle = C.sheet; ctx.fill(); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(-150, 100); ctx.lineTo(150, 100); ctx.stroke();
    text(ctx, o.label || 'FIN', 0, midBase(-6, 52), { size: 52, weight: 800, ls: 2, align: 'center', color: c });
    stroke(ctx, C.dim, 7); ctx.beginPath(); ctx.moveTo(-44, 52); ctx.lineTo(44, 52); ctx.stroke();
  },
  person(ctx, o) {
    const c = col(o.color); ctx.fillStyle = c;
    ctx.beginPath(); ctx.arc(0, -52, 46, 0, TAU); ctx.fill();
    ctx.beginPath(); ctx.moveTo(-86, 96); ctx.bezierCurveTo(-86, 12, -48, 6, 0, 6); ctx.bezierCurveTo(48, 6, 86, 12, 86, 96); ctx.closePath(); ctx.fill();
  },
  brain(ctx, o) {
    const c = col(o.color), b = col(o.accent || 'blue'); stroke(ctx, c, 9);
    ctx.beginPath();
    ctx.moveTo(0, -92); ctx.bezierCurveTo(-40, -118, -96, -100, -100, -56); ctx.bezierCurveTo(-140, -40, -134, 24, -100, 34);
    ctx.bezierCurveTo(-100, 80, -48, 96, -20, 76); ctx.bezierCurveTo(-10, 86, 10, 86, 20, 76); ctx.bezierCurveTo(48, 96, 100, 80, 100, 34);
    ctx.bezierCurveTo(134, 24, 140, -40, 100, -56); ctx.bezierCurveTo(96, -100, 40, -118, 0, -92); ctx.closePath();
    ctx.fillStyle = C.sheet; ctx.fill(); ctx.stroke();
    stroke(ctx, c, 6);
    ctx.beginPath(); ctx.moveTo(0, -92); ctx.lineTo(0, 78); ctx.stroke();
    for (const sg of [-1, 1]) { ctx.beginPath(); ctx.moveTo(sg * 18, -40); ctx.bezierCurveTo(sg * 60, -50, sg * 70, -10, sg * 40, 4); ctx.stroke(); ctx.beginPath(); ctx.moveTo(sg * 24, 40); ctx.bezierCurveTo(sg * 56, 30, sg * 80, 44, sg * 84, 10); ctx.stroke(); }
    if (o.fill != null) { ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.fillStyle = 'rgba(37,142,255,.22)'; ctx.fillRect(-140, 90 - 200 * o.fill, 280, 200 * o.fill); ctx.restore(); void b; }
  },
  gamepad(ctx, o) {
    const c = col(o.color), b = col(o.accent || 'blue'); stroke(ctx, c, 9);
    ctx.beginPath(); ctx.moveTo(-60, -50); ctx.lineTo(60, -50); ctx.bezierCurveTo(130, -50, 150, 70, 110, 76); ctx.bezierCurveTo(80, 80, 66, 30, 40, 30);
    ctx.lineTo(-40, 30); ctx.bezierCurveTo(-66, 30, -80, 80, -110, 76); ctx.bezierCurveTo(-150, 70, -130, -50, -60, -50); ctx.closePath();
    ctx.fillStyle = C.sheet; ctx.fill(); ctx.stroke();
    stroke(ctx, c, 8); ctx.beginPath(); ctx.moveTo(-82, -10); ctx.lineTo(-42, -10); ctx.moveTo(-62, -30); ctx.lineTo(-62, 10); ctx.stroke();
    for (const [bx, by] of [[52, -22], [80, 2]]) { ctx.beginPath(); ctx.arc(bx, by, 11, 0, TAU); ctx.fillStyle = b; ctx.fill(); }
  },
  laptop(ctx, o, t) {
    const c = col(o.color), b = col(o.accent || 'blue'); stroke(ctx, c, 9);
    ctx.beginPath(); ctx.roundRect(-130, -110, 260, 170, 16); ctx.fillStyle = C.sheet; ctx.fill(); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(-170, 84); ctx.lineTo(170, 84); ctx.lineTo(150, 60); ctx.lineTo(-150, 60); ctx.closePath(); ctx.fillStyle = C.sheet; ctx.fill(); ctx.stroke();
    if (o.cpuFrom != null) {   // CPU meter filling to red-line (ink), label
      const v = E.io(seg(t, o.cpuFrom, o.cpuTo ?? o.cpuFrom + 1.2));
      ctx.beginPath(); ctx.roundRect(-100, -20, 200, 30, 15); ctx.fillStyle = C.line; ctx.fill();
      ctx.beginPath(); ctx.roundRect(-100, -20, Math.max(30, 200 * v), 30, 15); ctx.fillStyle = v > .97 ? C.ink : b; ctx.fill();
      text(ctx, `CPU ${Math.round(v * 100)}%`, 0, -50, { size: 36, weight: 800, align: 'center', color: c });
    }
  },
  phone(ctx, o) {
    const c = col(o.color); stroke(ctx, c, 9);
    ctx.beginPath(); ctx.roundRect(-64, -120, 128, 240, 26); ctx.fillStyle = C.sheet; ctx.fill(); ctx.stroke();
    stroke(ctx, c, 7); ctx.beginPath(); ctx.moveTo(-18, -96); ctx.lineTo(18, -96); ctx.stroke();
  },
  coins(ctx, o) {
    const c = col(o.color), b = col(o.accent || 'blue'); stroke(ctx, c, 8);
    for (let i = 0; i < 4; i++) { const y = 60 - i * 34; ctx.beginPath(); ctx.ellipse(0, y, 96, 28, 0, 0, TAU); ctx.fillStyle = i === 3 ? b : C.sheet; ctx.fill(); ctx.stroke(); }
    text(ctx, o.label || '€', 0, midBase(-42, 40), { size: 40, weight: 800, align: 'center', color: C.white });
  },
  sun(ctx, o) {
    const c = col(o.color); stroke(ctx, c, 9);
    ctx.beginPath(); ctx.arc(0, 0, 56, 0, TAU); ctx.fillStyle = C.sheet; ctx.fill(); ctx.stroke();
    for (let i = 0; i < 8; i++) { const a = i * TAU / 8; ctx.beginPath(); ctx.moveTo(Math.cos(a) * 82, Math.sin(a) * 82); ctx.lineTo(Math.cos(a) * 110, Math.sin(a) * 110); ctx.stroke(); }
  },
  crown(ctx, o) {
    const c = col(o.color), b = col(o.accent || 'blue'); stroke(ctx, c, 9);
    ctx.beginPath(); ctx.moveTo(-110, 60); ctx.lineTo(-120, -50); ctx.lineTo(-56, 0); ctx.lineTo(0, -80); ctx.lineTo(56, 0); ctx.lineTo(120, -50); ctx.lineTo(110, 60); ctx.closePath();
    ctx.fillStyle = C.sheet; ctx.fill(); ctx.stroke();
    for (const [bx, by] of [[-120, -50], [0, -80], [120, -50]]) { ctx.beginPath(); ctx.arc(bx, by - 6, 13, 0, TAU); ctx.fillStyle = b; ctx.fill(); }
  },
  hourglass(ctx, o, t) {
    const c = col(o.color), b = col(o.accent || 'blue'); stroke(ctx, c, 9);
    const v = o.flowFrom != null ? E.io(seg(t, o.flowFrom, o.flowTo ?? o.flowFrom + 1.5)) : .5;
    ctx.save(); ctx.beginPath(); ctx.moveTo(-70, -96); ctx.lineTo(70, -96); ctx.lineTo(8, 0); ctx.lineTo(70, 96); ctx.lineTo(-70, 96); ctx.lineTo(-8, 0); ctx.closePath(); ctx.clip();
    ctx.fillStyle = b; ctx.fillRect(-80, lerp(-60, 0, v), 160, 60 * (1 - v) + 2); ctx.fillRect(-80, 96 - 60 * v, 160, 60 * v); ctx.restore();
    ctx.beginPath(); ctx.moveTo(-70, -96); ctx.lineTo(70, -96); ctx.lineTo(8, 0); ctx.lineTo(70, 96); ctx.lineTo(-70, 96); ctx.lineTo(-8, 0); ctx.closePath(); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(-96, -96); ctx.lineTo(96, -96); ctx.moveTo(-96, 96); ctx.lineTo(96, 96); ctx.stroke();
  },
  play(ctx, o) {
    const c = col(o.accent || 'blue');
    ctx.beginPath(); ctx.roundRect(-100, -70, 200, 140, 40); ctx.fillStyle = c; ctx.fill();
    ctx.beginPath(); ctx.moveTo(-26, -36); ctx.lineTo(40, 0); ctx.lineTo(-26, 36); ctx.closePath(); ctx.fillStyle = C.white; ctx.fill();
  },
  msg(ctx, o) {
    const c = col(o.color); stroke(ctx, c, 9);
    ctx.beginPath(); ctx.roundRect(-100, -76, 200, 130, 36); ctx.fillStyle = C.sheet; ctx.fill(); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(-50, 54); ctx.lineTo(-64, 92); ctx.lineTo(-10, 54); ctx.stroke();
    for (const dx of [-40, 0, 40]) { ctx.beginPath(); ctx.arc(dx, -10, 10, 0, TAU); ctx.fillStyle = c; ctx.fill(); }
  },
  trash(ctx, o) {
    const c = col(o.color); stroke(ctx, c, 9);
    ctx.beginPath(); ctx.moveTo(-76, -50); ctx.lineTo(-62, 96); ctx.lineTo(62, 96); ctx.lineTo(76, -50); ctx.closePath(); ctx.fillStyle = C.sheet; ctx.fill(); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(-100, -56); ctx.lineTo(100, -56); ctx.moveTo(-30, -56); ctx.lineTo(-24, -84); ctx.lineTo(24, -84); ctx.lineTo(30, -56); ctx.stroke();
    stroke(ctx, c, 6); for (const dx of [-26, 0, 26]) { ctx.beginPath(); ctx.moveTo(dx, -20); ctx.lineTo(dx * .9, 66); ctx.stroke(); }
  },
  card(ctx, o) {
    const c = col(o.color), b = col(o.accent || 'blue'); stroke(ctx, c, 9);
    ctx.beginPath(); ctx.roundRect(-130, -80, 260, 160, 24); ctx.fillStyle = C.sheet; ctx.fill(); ctx.stroke();
    ctx.fillStyle = c; ctx.fillRect(-130, -42, 260, 30);
    ctx.beginPath(); ctx.roundRect(-96, 22, 60, 36, 8); ctx.fillStyle = b; ctx.fill();
  },
  cap(ctx, o) {   // graduation cap (a school)
    const c = col(o.color), b = col(o.accent || 'blue'); stroke(ctx, c, 9);
    ctx.beginPath(); ctx.moveTo(-60, -10); ctx.lineTo(-60, 50); ctx.bezierCurveTo(-30, 76, 30, 76, 60, 50); ctx.lineTo(60, -10); ctx.fillStyle = C.sheet; ctx.fill(); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(0, -80); ctx.lineTo(140, -30); ctx.lineTo(0, 20); ctx.lineTo(-140, -30); ctx.closePath(); ctx.fillStyle = C.sheet; ctx.fill(); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(110, -20); ctx.lineTo(110, 50); ctx.stroke(); ctx.beginPath(); ctx.arc(110, 58, 12, 0, TAU); ctx.fillStyle = b; ctx.fill();
  },
  clock(ctx, o, t) {
    const c = col(o.color), b = col(o.accent || 'blue'); stroke(ctx, c, 9);
    ctx.beginPath(); ctx.arc(0, 0, 96, 0, TAU); ctx.fillStyle = C.sheet; ctx.fill(); ctx.stroke();
    const a = o.spinFrom != null ? E.io(seg(t, o.spinFrom, o.spinTo ?? o.spinFrom + 1.5)) * TAU * (o.turns || 4) : 0;
    stroke(ctx, c, 9); ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(Math.sin(a / 12) * 50, -Math.cos(a / 12) * 50); ctx.stroke();
    stroke(ctx, b, 7); ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(Math.sin(a) * 74, -Math.cos(a) * 74); ctx.stroke();
  },
  bulb(ctx, o) {
    const c = col(o.color), b = col(o.accent || 'blue'); stroke(ctx, c, 9);
    ctx.beginPath(); ctx.moveTo(-34, 50); ctx.bezierCurveTo(-34, 10, -84, -10, -84, -50); ctx.arc(0, -50, 84, Math.PI, 0); ctx.bezierCurveTo(84, -10, 34, 10, 34, 50); ctx.closePath();
    ctx.fillStyle = o.on ? C.tint : C.sheet; ctx.fill(); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(-30, 76); ctx.lineTo(30, 76); ctx.moveTo(-22, 100); ctx.lineTo(22, 100); ctx.stroke();
    if (o.on) { stroke(ctx, b, 7); for (const a of [-2.4, -1.57, -.74]) { ctx.beginPath(); ctx.moveTo(Math.cos(a) * 112, -50 + Math.sin(a) * 112); ctx.lineTo(Math.cos(a) * 140, -50 + Math.sin(a) * 140); ctx.stroke(); } }
  },
  rocket(ctx, o) {
    const c = col(o.color), b = col(o.accent || 'blue'); stroke(ctx, c, 9);
    ctx.beginPath(); ctx.moveTo(0, -120); ctx.bezierCurveTo(56, -80, 56, 10, 40, 60); ctx.lineTo(-40, 60); ctx.bezierCurveTo(-56, 10, -56, -80, 0, -120); ctx.closePath(); ctx.fillStyle = C.sheet; ctx.fill(); ctx.stroke();
    ctx.beginPath(); ctx.arc(0, -40, 18, 0, TAU); ctx.fillStyle = b; ctx.fill();
    ctx.beginPath(); ctx.moveTo(-40, 20); ctx.lineTo(-76, 70); ctx.lineTo(-36, 60); ctx.moveTo(40, 20); ctx.lineTo(76, 70); ctx.lineTo(36, 60); ctx.stroke();
    stroke(ctx, b, 8); ctx.beginPath(); ctx.moveTo(-16, 80); ctx.lineTo(-16, 112); ctx.moveTo(16, 80); ctx.lineTo(16, 112); ctx.stroke();
  },
  chart(ctx, o) {
    const c = col(o.color), b = col(o.accent || 'blue'); stroke(ctx, c, 9);
    ctx.beginPath(); ctx.moveTo(-110, -90); ctx.lineTo(-110, 90); ctx.lineTo(120, 90); ctx.stroke();
    stroke(ctx, b, 10); ctx.beginPath(); ctx.moveTo(-80, 50); ctx.lineTo(-20, 10); ctx.lineTo(20, 30); ctx.lineTo(96, -60); ctx.stroke();
  },
  bug(ctx, o) {
    const c = col(o.color); stroke(ctx, c, 8);
    ctx.beginPath(); ctx.ellipse(0, 16, 58, 76, 0, 0, TAU); ctx.fillStyle = C.sheet; ctx.fill(); ctx.stroke();
    ctx.beginPath(); ctx.arc(0, -70, 30, Math.PI, 0); ctx.stroke(); ctx.beginPath(); ctx.moveTo(0, -56); ctx.lineTo(0, 92); ctx.stroke();
    for (const sg of [-1, 1]) for (const y of [-20, 20, 60]) { ctx.beginPath(); ctx.moveTo(sg * 56, y); ctx.lineTo(sg * 96, y - 18); ctx.stroke(); }
    for (const sg of [-1, 1]) { ctx.beginPath(); ctx.moveTo(sg * 14, -96); ctx.lineTo(sg * 36, -126); ctx.stroke(); }
  },
};

// ---------------------------------------------------------------- item drawers. (0, 0) is already the item position.
const DRAW = {
  text(ctx, it, t) {
    // style.display (kit D): big texts (100 px and more, or depth) take the display family, the others its text family;
    // it.font (+ it.weight, default 400) overrides both, e.g. a brand serif on the end card
    const size = it.size || 64, big = !it.font && D.font && (it.depth || size >= 100), fam = it.font ? famCss(it.font) : big ? D.font : D.text || undefined;
    const wt = it.font ? it.weight || 400 : big ? D.weight : it.weight || 800, ls = it.ls ?? -size * .03, lh = it.lh || size * 1.12, depth = D.flat ? 0 : it.depth;
    const c = col(it.color || (D.title && !big && size <= 64 ? D.title : null));
    const lines = it.maxW ? wrap(ctx, it.text, it.maxW, size, wt, ls, fam) : String(it.text).split('\n');
    const emph = new Set(String(it.emph || '').split(' ').filter(Boolean));
    lines.forEach((ln, li) => {
      const base = midBase((li - (lines.length - 1) / 2) * lh, size), words = ln.split(' ');
      const ws = words.map(w => measure(ctx, w, size, wt, ls, fam)), sp = measure(ctx, ' ', size, wt, ls, fam), tw = ws.reduce((a, b) => a + b, 0) + sp * (words.length - 1);
      let x = it.align === 'left' ? 0 : it.align === 'right' ? -tw : -tw / 2;
      words.forEach((w, i) => {
        const p = it.words ? S(t - it.at - (li * words.length + i) * .055, 14) : 1, isE = emph.has(w);
        const cc = isE ? (it.emphAt != null ? mix(C.ink, C.blue, S(t - it.emphAt, 14)) : C.blue) : c, wx = x;
        if (p > .002) alpha(ctx, Math.min(1, p * 1.4), () => text(ctx, w, wx, base + (1 - p) * 40, { size, weight: wt, ls, fam, color: cc, halo: it.halo, depth }));
        x += ws[i] + sp;
      });
    });
  },
  chip(ctx, it) { chip(ctx, 0, 0, it.text, { size: it.size || 42, h: Math.round((it.size || 42) * 2), fill: it.blue ? C.blue : it.dark ? C.ink : undefined, color: it.blue ? C.onBlue : it.dark ? C.white : C.ink, border: !(it.blue || it.dark), dot: it.dot && (it.dotColor ? col(it.dotColor) : C.blue), align: it.align }); },
  // Name tag on a camera tile: a flat paper sheet, ink name, (x, y) = its BOTTOM-LEFT corner so tags line up on the
  // tile edges. liveSpans: [[a, b], ...] time ranges where it turns accent (the speaker), a 120 ms colour swap in
  // place (an edge on the tag's own at/to is instant: the camera cut already carries it).
  // imgs: [paper, live] PNGs of a name tag (CSS torn paper, 2x, 14 px margin
  // around the paper body): drawn instead of the canvas sheet.
  nametag(ctx, it, t, R) {
    const size = it.size || 28, h = Math.round(size * 1.8), padX = Math.round(size * .62), wt = it.weight || 600, r = Math.round(size * .18);
    const at = it.at ?? -1e9, to = it.to ?? 1e9;
    const on = (it.liveSpans || []).reduce((m, [a, b]) => Math.max(m, Math.min(a <= at + .05 ? +(t >= a) : clamp((t - a) / .12), b >= to - .05 ? +(t < b) : clamp((b - t) / .12))), 0);
    const [p0, p1] = (it.imgs || []).map(u => R?.img('/p/' + u));
    if (p0) {
      const M = 14, dw = p0.width / 2, dh = p0.height / 2, draw = (im, a) => { if (im && a > .002) { ctx.save(); ctx.globalAlpha *= a; ctx.imageSmoothingQuality = 'high'; ctx.drawImage(im, -M, M - dh, dw, dh); ctx.restore(); } };
      draw(p0, p1 ? 1 - on : 1); draw(p1, on); return;
    }
    const w = Math.round(measure(ctx, it.text, size, wt, -.2) + padX * 2);
    sheet(ctx, 0, -h, w, h, r, { elev: .3 });
    if (on > .002) sheet(ctx, 0, -h, w, h, r, { fill: C.blue, alpha: on, shadow: false, border: false });
    text(ctx, it.text, padX, midBase(-h / 2, size), { size, weight: wt, ls: -.2, color: C.ink });
  },
  // Slanted label box (the podcast thumbnail look): heavy condensed italic caps on a flat color block, tilted a few
  // degrees. bg: 'blue' (accent), 'pop' (style.colors.pop), 'ink', 'sheet' or a hex; the text color follows (ink on a
  // light fill, white on a dark one) unless color is set. The block wipes in from the left over .26 s with its text.
  // size 90, rot -.035, skew .2 (italic slant), stretch 'extra-condensed', caps true, align center|left|right
  label(ctx, it, t) {
    const size = it.size || 90, bg = it.bg === 'blue' || it.bg == null ? C.blue : col(it.bg), txt = it.caps === false ? String(it.text) : String(it.text).toUpperCase();
    const light = (h => { const m = String(h).match(/^#?([0-9a-f]{6})$/i); if (!m) return true; const v = parseInt(m[1], 16); return (.2126 * (v >> 16) + .7152 * (v >> 8 & 255) + .0722 * (v & 255)) / 255 > .55; })(bg);
    const fg = it.color ? col(it.color) : bg === C.blue ? C.onBlue : light ? C.ink : C.white;
    ctx.save(); ctx.font = `900 ${size}px Archivo`; ctx.fontStretch = it.stretch || 'extra-condensed'; ctx.letterSpacing = (it.ls ?? size * .005) + 'px';
    const lines = txt.split('\n'), lh = size * .98, tw = Math.max(...lines.map(l => ctx.measureText(l).width));
    const px = size * .3, py = size * .16, w = tw + px * 2, h = lines.length * lh + py * 2 - (lh - size * .9), x0 = it.align === 'left' ? 0 : it.align === 'right' ? -w : -w / 2;
    const q = E.out(seg(t, it.at, it.at + .26));
    ctx.rotate(it.rot ?? -.035);
    if (q < .999) { ctx.beginPath(); ctx.rect(x0 - 40, -h / 2 - 40, (w + 80) * q, h + 80); ctx.clip(); }
    ctx.save(); drop(ctx, .26, 18, 8); ctx.fillStyle = bg; ctx.fillRect(x0, -h / 2, w, h); ctx.restore();
    if (it.border) { ctx.lineWidth = it.border; ctx.strokeStyle = C.ink; ctx.strokeRect(x0, -h / 2, w, h); }
    ctx.fillStyle = fg; ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
    const sk = it.skew ?? .2;
    lines.forEach((l, i) => {
      const by = -h / 2 + py + size * .82 + i * lh;   // caps height ~.72 em: optically centered in the block
      ctx.save(); ctx.translate(x0 + w / 2, by); ctx.transform(1, 0, -sk, 1, 0, 0); ctx.fillText(l, 0, 0); ctx.restore();
    });
    ctx.restore();
  },
  stamp(ctx, it, t) {
    const p = S(t - it.at, 11), size = it.size || 70, w = measure(ctx, it.text, size, 800, -1) + 76, h = size + 54;
    ctx.rotate(it.rot ?? -.07); const k = 1 + .3 * (1 - p); ctx.scale(k, k);
    if (it.solid !== false) shadow(ctx, -w / 2, -h / 2, w, h, 22, 22, .2, 8);
    ctx.beginPath(); ctx.roundRect(-w / 2, -h / 2, w, h, 22); ctx.fillStyle = it.solid !== false ? C.sheet : 'rgba(37,142,255,.08)'; ctx.fill();
    ctx.lineWidth = 8; ctx.strokeStyle = C.blue; ctx.stroke();
    ctx.beginPath(); ctx.roundRect(-w / 2 + 12, -h / 2 + 12, w - 24, h - 24, 14); ctx.lineWidth = 2.5; ctx.stroke();
    text(ctx, it.text, 0, midBase(0, size), { size, weight: 800, ls: -1, align: 'center', color: C.blue });
  },
  counter(ctx, it, t) {
    const size = it.size || 200, k = E.out(seg(t, it.countFrom ?? it.at, it.countTo ?? (it.countFrom ?? it.at) + .9));
    const fam = D.font || undefined, wt = D.font ? D.weight : 800, ls = -size * (D.font ? .03 : .035), depth = D.flat ? 0 : it.depth;
    const v = lerp(it.fromValue || 0, it.value, k), dec = it.decimals || 0;
    if (it.clock) {   // stopwatch m:ss (value in seconds), every digit in the same slot so the timer never jitters while it runs
      const sec = Math.round(v), str = `${String(Math.floor(sec / 60)).padStart(2, '0')}:${String(sec % 60).padStart(2, '0')}`;
      const dw = Math.max(...'0123456789'.split('').map(d => measure(ctx, d, size, wt, ls, fam))), cw = measure(ctx, ':', size, wt, ls, fam);
      const adv = c => c === ':' ? cw : dw, tw = [...str].reduce((a, c) => a + adv(c), 0);
      let x = it.align === 'left' ? 0 : -tw / 2;
      for (const c of str) { text(ctx, c, x + adv(c) / 2, midBase(0, size), { size, weight: wt, ls, fam, color: col(it.color), depth, align: 'center' }); x += adv(c); }
      return;
    }
    let s = v.toFixed(dec); if (dec && it.decSep) s = s.replace('.', it.decSep); if (it.sep !== false && !dec) s = s.replace(/\B(?=(\d{3})+(?!\d))/g, it.sep ?? ' ');
    const pre = it.prefix || '', suf = it.suffix || '', unit = it.unit || '', ufam = D.text || undefined;
    const sw = measure(ctx, pre + s + suf, size, wt, ls, fam), uw = unit ? measure(ctx, unit, size * .42, 800, -1, ufam) + size * .08 : 0;
    const x0 = it.align === 'left' ? 0 : -(sw + uw) / 2;
    text(ctx, pre + s, x0, midBase(0, size), { size, weight: wt, ls, fam, color: col(it.color), depth });
    if (suf) text(ctx, suf, x0 + measure(ctx, pre + s, size, wt, ls, fam), midBase(0, size), { size, weight: wt, ls, fam, color: it.suffixColor ? col(it.suffixColor) : C.blue, depth });
    if (unit) text(ctx, unit, x0 + sw + size * .08, midBase(size * .18, size * .42), { size: size * .42, weight: 800, ls: -1, fam: ufam, color: C.blue });
  },
  bar(ctx, it, t, R) {
    const w = it.w || 900, h = it.h || 96, g = E.out(seg(t, it.fillFrom ?? it.at + .05, it.fillTo ?? (it.fillFrom ?? it.at + .05) + .8));
    const v = lerp(it.fromValue || 0, it.value, g), ls = (it.labelSize || 46);
    if (it.logo) logoAt(R, ctx, it.logo, ls * .65, -24 - ls * .36, ls * 1.3);
    if (it.label) text(ctx, it.label, it.logo ? ls * 1.55 : 0, -24, { size: ls, weight: 800, ls: -.8, color: it.blue ? C.ink : C.ink2 });
    ctx.beginPath(); ctx.roundRect(0, 0, w, h, h / 2); ctx.fillStyle = 'rgba(40,30,10,.06)'; ctx.fill(); groove(ctx, 0, 0, w, h, h / 2);
    if (v > .001) { const fw = Math.max(h, w * v); lift(ctx, 0, 0, fw, h, h / 2, .5); ctx.beginPath(); ctx.roundRect(0, 0, fw, h, h / 2); ctx.fillStyle = it.blue ? C.blue : it.dark ? C.ink : C.ink3; ctx.fill(); gloss(ctx, 0, 0, fw, h, h / 2); }
    if (it.valueText) text(ctx, it.valueText, w, -24, { size: it.labelSize || 46, weight: 800, align: 'right', color: it.blue ? C.blue : C.ink2 });
  },
  bubble(ctx, it, t) {
    const me = it.side === 'me', size = it.size || 44, w = it.w || 760, padX = 40, padY = 30;
    const lines = wrap(ctx, it.text, w - padX * 2, size, 600, -.3), lh = size * 1.28, h = lines.length * lh + padY * 2 - (lh - size) + 6;
    const bw = Math.min(w, Math.max(...lines.map(l => measure(ctx, l, size, 600, -.3))) + padX * 2), x0 = me ? -bw : 0;
    sheet(ctx, x0, 0, bw, h, 36, { fill: me ? C.blue : undefined, elev: .8, border: !me });
    let n = Infinity;
    if (it.typeFrom != null) { const tot = it.text.split(' ').length; n = Math.round(tot * seg(t, it.typeFrom, it.typeTo ?? it.typeFrom + 1)); }
    let k = 0;
    lines.forEach((ln, i) => {
      const ws = ln.split(' '), vis = ws.slice(0, Math.max(0, n - k)).join(' '); k += ws.length;
      if (vis) text(ctx, vis, x0 + padX, padY + size * .8 + i * lh, { size, weight: 600, ls: -.3, color: me ? C.onBlue : C.ink });
    });
    if (it.name) text(ctx, it.name, me ? 0 : 6, -20, { size: 34, weight: 700, align: me ? 'right' : 'left', color: C.ink3 });
  },
  card(ctx, it, t) {
    const r = it.r ?? 36;
    sheet(ctx, 0, 0, it.w, it.h, r, { elev: it.elev ?? 1, fill: it.fill === 'ink' ? C.ink : it.fill === 'tint' ? C.tint : undefined, border: !it.fill });
    if (it.ringAt != null) { const q = S(t - it.ringAt, 12); if (q > .002) alpha(ctx, q, () => { ctx.beginPath(); ctx.roundRect(-10, -10, it.w + 20, it.h + 20, r + 10); stroke(ctx, C.blue, 7); ctx.stroke(); }); }
  },
  reticle(ctx, it, t) {   // a sight closing on (x, y): ring shrinks from 1.7 r to r, four ticks, a blue dot when locked
    const p = E.io(seg(t, it.closeFrom ?? it.at, it.closeTo ?? (it.closeFrom ?? it.at) + .8)), r = lerp(it.r * 1.7, it.r, p);
    stroke(ctx, C.blue, it.lw || 7); ctx.beginPath(); ctx.arc(0, 0, r, 0, TAU); ctx.stroke();
    for (let k = 0; k < 4; k++) { const a = k * TAU / 4; ctx.beginPath(); ctx.moveTo(Math.cos(a) * (r - 34), Math.sin(a) * (r - 34)); ctx.lineTo(Math.cos(a) * (r + 40), Math.sin(a) * (r + 40)); ctx.stroke(); }
    if (p > .98) { ctx.beginPath(); ctx.arc(0, 0, 12, 0, TAU); ctx.fillStyle = C.blue; ctx.fill(); }
  },
  line(ctx, it, t) {
    const d = E.out(seg(t, it.at, it.at + (it.dur ?? .45))), X = it.x2 - it.x, Y = it.y2 - it.y;
    stroke(ctx, col(it.color), it.lw || 8); if (it.dash) ctx.setLineDash(it.dash);
    if (it.bend) {   // hand-drawn curve: quadratic bezier bowed sideways by bend (fraction of the length), drawn on along the curve
      const mx = X / 2 - Y * it.bend, my = Y / 2 + X * it.bend, bz = u => [2 * (1 - u) * u * mx + u * u * X, 2 * (1 - u) * u * my + u * u * Y];
      ctx.beginPath(); ctx.moveTo(0, 0); for (let u = .04; u < d; u += .04) ctx.lineTo(...bz(u)); ctx.lineTo(...bz(d)); ctx.stroke(); ctx.setLineDash([]);
      if (it.head && d > .6) { const [x2, y2] = bz(d), [xa, ya] = bz(Math.max(0, d - .05)), a = Math.atan2(y2 - ya, x2 - xa), L = 30; ctx.beginPath(); ctx.moveTo(x2 - Math.cos(a - .5) * L, y2 - Math.sin(a - .5) * L); ctx.lineTo(x2, y2); ctx.lineTo(x2 - Math.cos(a + .5) * L, y2 - Math.sin(a + .5) * L); ctx.stroke(); }
      return;
    }
    const x2 = lerp(0, X, d), y2 = lerp(0, Y, d);
    ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(x2, y2); ctx.stroke(); ctx.setLineDash([]);
    if (it.head && d > .6) { const a = Math.atan2(Y, X), L = 30; ctx.beginPath(); ctx.moveTo(x2 - Math.cos(a - .5) * L, y2 - Math.sin(a - .5) * L); ctx.lineTo(x2, y2); ctx.lineTo(x2 - Math.cos(a + .5) * L, y2 - Math.sin(a + .5) * L); ctx.stroke(); }
  },
  circle(ctx, it) {
    ctx.beginPath(); ctx.arc(0, 0, it.r, 0, TAU);
    if (it.fill) { ctx.fillStyle = it.fill === 'tint' ? 'rgba(37,142,255,.08)' : col(it.fill); ctx.fill(); }
    stroke(ctx, col(it.color || 'blue'), it.lw || 6); if (it.dash) ctx.setLineDash(it.dash); ctx.stroke(); ctx.setLineDash([]);
  },
  rect(ctx, it) {   // outline zone (a "bubble" around a group); x, y = top-left
    ctx.beginPath(); ctx.roundRect(0, 0, it.w, it.h, it.r ?? it.h / 2);
    if (it.fill) { ctx.fillStyle = it.fill === 'tint' ? 'rgba(37,142,255,.08)' : col(it.fill); ctx.fill(); }
    stroke(ctx, col(it.color || 'blue'), it.lw || 6); if (it.dash) ctx.setLineDash(it.dash); ctx.stroke(); ctx.setLineDash([]);
  },
  dots(ctx, it, t) {
    const cols = it.cols, rows = it.rows, g = it.gap || 56, r = it.r || 18, n = cols * rows, x0 = -(cols - 1) * g / 2, y0 = -(rows - 1) * g / 2;
    for (let i = 0; i < n; i++) {
      const a = S(t - it.at - i * (it.stagger ?? .008), 14); if (a <= .002) continue;
      let c = col(it.color || 'ink3');
      for (const gr of it.groups || []) if (i >= (gr.i0 || 0) && i < (gr.i0 || 0) + gr.n) { const q = S(t - gr.at - (i - (gr.i0 || 0)) * .006, 13); if (q > .002) c = mix(typeof c === 'string' && c[0] === '#' ? c : C.ink3, col(gr.color), q); }
      alpha(ctx, Math.min(1, a * 1.4), () => { ctx.beginPath(); ctx.arc(x0 + (i % cols) * g, y0 + Math.floor(i / cols) * g + (1 - a) * 20, r, 0, TAU); ctx.fillStyle = c; ctx.fill(); });
    }
  },
  thumbs(ctx, it, t) {
    const cols = it.cols, rows = it.rows, w = it.w || 190, h = it.h || 107, g = it.gap || 18, n = cols * rows;
    const X0 = -(cols * w + (cols - 1) * g) / 2, Y0 = -(rows * h + (rows - 1) * g) / 2;
    for (let i = 0; i < n; i++) {
      const a = S(t - it.at - i * (it.stagger ?? .05), 14); if (a <= .002) continue;
      const x = X0 + (i % cols) * (w + g), y = Y0 + Math.floor(i / cols) * (h + g), hh = hash(i * 7.3 + 2);
      alpha(ctx, Math.min(1, a * 1.4), () => {
        ctx.save(); ctx.translate(0, (1 - a) * 24);
        sheet(ctx, x, y, w, h, 14, { elev: .5 });
        ctx.save(); ctx.beginPath(); ctx.roundRect(x, y, w, h, 14); ctx.clip();
        ctx.fillStyle = hh > .7 ? C.tint : hh > .35 ? C.line : '#EFEBE2'; ctx.fillRect(x, y, w, h);
        ctx.fillStyle = hh > .5 ? C.ink : C.blue; ctx.fillRect(x + 14, y + 16, w * (.35 + .3 * hash(i + 9)), 14); ctx.fillRect(x + 14, y + 38, w * (.2 + .2 * hash(i + 3)), 14);
        ctx.beginPath(); ctx.arc(x + w * .74, y + h * .62, h * .28, 0, TAU); ctx.fillStyle = C.ink3; ctx.fill();
        ctx.restore(); ctx.restore();
      });
    }
  },
  agents(ctx, it, t) {
    const cols = it.cols || 5, rows = it.rows || 5, w = it.w || 168, h = it.h || 112, g = it.gap || 16, n = cols * rows;
    const X0 = -(cols * w + (cols - 1) * g) / 2, Y0 = -(rows * h + (rows - 1) * g) / 2;
    for (let i = 0; i < n; i++) {
      const a = S(t - it.at - i * (it.stagger ?? .03), 14); if (a <= .002) continue;
      const x = X0 + (i % cols) * (w + g), y = Y0 + Math.floor(i / cols) * (h + g);
      const sp = .25 + .75 * hash(i * 3.1 + 1), wf = it.workFrom ?? it.at, wt = it.workTo ?? wf + 4;
      const v = clamp(((t - wf) / (wt - wf)) * sp * 1.4 + hash(i) * .15), done = v >= 1;
      alpha(ctx, Math.min(1, a * 1.4), () => {
        ctx.save(); ctx.translate(0, (1 - a) * 24);
        sheet(ctx, x, y, w, h, 18, { elev: .5 });
        ctx.beginPath(); ctx.arc(x + 30, y + 32, 11, 0, TAU); ctx.fillStyle = done ? C.blue : C.ink; ctx.fill();
        ctx.beginPath(); ctx.roundRect(x + 52, y + 24, w - 76, 16, 8); ctx.fillStyle = C.line; ctx.fill();
        ctx.beginPath(); ctx.roundRect(x + 20, y + h - 40, w - 40, 16, 8); ctx.fillStyle = C.line; ctx.fill();
        ctx.beginPath(); ctx.roundRect(x + 20, y + h - 40, Math.max(16, (w - 40) * v), 16, 8); ctx.fillStyle = done ? C.blue : C.ink3; ctx.fill();
        if (done) checkIcon(ctx, x + w - 34, y + 32, 30, C.blue, 1, 6);
        ctx.restore();
      });
    }
  },
  diverge(ctx, it, t) {
    const w = it.w || 900, h = it.h || 560, sx = w * (it.splitX ?? .38), my = h / 2, d = E.io(seg(t, it.drawFrom ?? it.at, it.drawTo ?? (it.drawFrom ?? it.at) + 1.6));
    stroke(ctx, C.ink3, 4); ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(0, h); ctx.lineTo(w, h); ctx.stroke();
    text(ctx, it.xLabel || 'Avec l\'IA', w, h + 56, { size: 36, weight: 700, align: 'right', color: C.ink3 });
    const curve = (sg, u) => { const x = u * w; if (x <= sx) return [x, my]; const k = (x - sx) / (w - sx); return [x, my - sg * (h * .44) * Math.pow(k, 1.6)]; };
    for (const [sg, c, lw] of [[-1, C.ink3, 12], [1, C.blue, 14]]) {
      stroke(ctx, c, lw); ctx.beginPath();
      for (let i = 0; i <= 60 * d; i++) { const [x, y] = curve(sg, i / 60); i ? ctx.lineTo(x, y) : ctx.moveTo(x, y); }
      ctx.stroke();
    }
    const lab = (txt, sg, c, at) => { const q = S(t - at, 13); if (q > .002 && txt) alpha(ctx, q, () => { const [x, y] = curve(sg, 1); text(ctx, txt, x - 10, y + (sg > 0 ? -40 : -34), { size: 44, weight: 800, align: 'right', color: c }); }); };
    lab(it.upLabel, 1, C.blue, it.upAt ?? (it.drawTo ?? it.at + 1.6));
    lab(it.downLabel, -1, C.ink2, it.downAt ?? (it.drawTo ?? it.at + 1.6));
    if (it.meAt != null) { const q = S(t - it.meAt, 12); if (q > .002) { const [x, y] = curve(1, .92); alpha(ctx, q, () => { ctx.beginPath(); ctx.arc(x, y, 22, 0, TAU); ctx.fillStyle = C.blue; ctx.fill(); ctx.lineWidth = 6; ctx.strokeStyle = C.sheet; ctx.stroke(); chip(ctx, x - 40, y + 70, it.meLabel || 'Moi', { size: 40, h: 80, align: 'right', fill: C.ink, color: C.white, border: false }); }); } }
  },
  check(ctx, it, t) { checkIcon(ctx, 0, 0, it.s || 80, col(it.color || 'blue'), E.out(seg(t, it.at, it.at + .35)), (it.s || 80) * .16); },
  logo(ctx, it, t, R) { logoAt(R, ctx, it.logo, 0, 0, it.s || 140, it.gray); },
  img(ctx, it, t, R) {
    const im = R?.img('/p/' + it.img); if (!im) return;
    const mw = it.s || 200, mh = it.h || mw, k = Math.min(mw / im.width, mh / im.height), w = im.width * k, h = im.height * k;
    ctx.save(); ctx.imageSmoothingQuality = 'high';
    if (it.frame) {   // white print border around the photo
      const f = it.frame, R0 = (it.r || 0) + f * .6;
      if (it.shadow !== false) lift(ctx, -w / 2 - f, -h / 2 - f, w + 2 * f, h + 2 * f, R0, w > 300 ? 1 : .5);
      ctx.beginPath(); ctx.roundRect(-w / 2 - f, -h / 2 - f, w + 2 * f, h + 2 * f, R0); ctx.fillStyle = C.white; ctx.fill();
      ctx.beginPath(); ctx.roundRect(-w / 2, -h / 2, w, h, it.r || 0); ctx.clip();
    } else if (it.r) { if (it.shadow !== false) lift(ctx, -w / 2, -h / 2, w, h, it.r, w > 300 ? 1 : .5); ctx.beginPath(); ctx.roundRect(-w / 2, -h / 2, w, h, it.r); ctx.clip(); }
    else if (it.shadow !== false) drop(ctx, .2, 26, 12);
    ctx.drawImage(im, -w / 2, -h / 2, w, h); ctx.restore();
  },
  screen(ctx, it, t, R) {   // a real UI screenshot in a dark window, with spring zooms, blue rings and arrows that follow the zoom
    let ki = 0; if (it.imgKeys) while (ki + 1 < it.imgKeys.length && it.imgKeys[ki + 1][0] <= t) ki++;   // imgKeys: the content swaps in place
    const im = R?.img('/p/' + (it.imgKeys ? it.imgKeys[ki][1] : it.img)); if (!im) return;
    const prev = ki > 0 && R?.img('/p/' + it.imgKeys[ki - 1][1]), swap = prev ? S(t - it.imgKeys[ki][0], 18) : 1;
    const w = it.w || 900, h = it.h || 620, r = it.r ?? 30, x0 = -w / 2, y0 = -h / 2;
    const [vx, vy, z] = it.viewKeys ? track(t, it.viewKeys, it.viewW || 7) : [im.width / 2, im.height / 2, 1];
    const k = (w / im.width) * z, hw = w / 2 / k, hh = h / 2 / k;
    const cx = im.width > hw * 2 ? clamp(vx, hw, im.width - hw) : im.width / 2;
    const cy = im.height > hh * 2 ? clamp(vy, hh, im.height - hh) : im.height / 2;
    const P = (ix, iy) => [(ix - cx) * k, (iy - cy) * k];
    const lit = it.lit ?? 1;   // morph: the window lifts off the page as it grows
    if (it.shadow !== false && lit > .002) { ctx.save(); ctx.globalAlpha *= lit; lift(ctx, x0, y0, w, h, r, 1.2); ctx.restore(); }
    ctx.save(); if (it.shadow !== false) drop(ctx, .28 * lit, 40, 18);
    ctx.beginPath(); ctx.roundRect(x0, y0, w, h, r); ctx.fillStyle = it.bg || '#1B1B1D'; ctx.fill(); ctx.restore();
    ctx.save(); ctx.beginPath(); ctx.roundRect(x0, y0, w, h, r); ctx.clip(); ctx.imageSmoothingQuality = 'high';
    if (swap < 1) ctx.drawImage(prev, -cx * k, -cy * k, im.width * k, im.height * k);
    alpha(ctx, swap, () => ctx.drawImage(im, -cx * k, -cy * k, im.width * k, im.height * k));
    for (const g of it.rings || []) {   // focus ring: dims the rest of the window, then draws a blue outline on
      const q = S(t - g.at, 12) * (g.to != null ? 1 - leave(t - g.to) : 1); if (q <= .002) continue;
      const pad = g.pad ?? 10, [ax, ay] = P(g.rect[0], g.rect[1]), rw = g.rect[2] * k + pad * 2, rh = g.rect[3] * k + pad * 2, rr = Math.min(g.r ?? 18, rh / 2);
      if (g.dim !== false) { const m = new Path2D(); m.rect(x0, y0, w, h); m.roundRect(ax - pad, ay - pad, rw, rh, rr); ctx.fillStyle = `rgba(8,8,10,${.5 * q})`; ctx.fill(m, 'evenodd'); }
      const d = E.out(seg(t, g.at, g.at + (g.dur ?? .5))), L = 2 * (rw + rh);
      alpha(ctx, q, () => { ctx.beginPath(); ctx.roundRect(ax - pad, ay - pad, rw, rh, rr); stroke(ctx, C.blue, g.lw || 7); ctx.setLineDash([L * d, L]); ctx.stroke(); ctx.setLineDash([]); });
    }
    for (const m of it.marks || []) {   // highlighter over the text (multiply keeps the words ink), swept rect by rect, rides the zoom
      const rs = m.rects || [m.rect], tot = rs.reduce((a, q) => a + q[2], 0); let left = tot * E.cubic(seg(t, m.at, m.at + (m.dur ?? .7)));
      if (left <= .5) continue;
      ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.fillStyle = m.color || 'rgba(37,142,255,.3)'; const px = m.pad ?? 8;
      for (const q of rs) { if (left <= 0) break; const gw = Math.min(left, q[2]); left -= q[2]; const [ax, ay] = P(q[0] - px, q[1] - px * .6);
        ctx.beginPath(); ctx.roundRect(ax, ay, (gw + 2 * px) * k, (q[3] + 1.2 * px) * k, 8); ctx.fill(); }
      ctx.restore();
    }
    ctx.restore();
    ctx.beginPath(); ctx.roundRect(x0, y0, w, h, r); ctx.lineWidth = 2; ctx.strokeStyle = 'rgba(255,255,255,.14)'; ctx.stroke();
    for (const a of it.arrows || []) {   // arrow drawn on from (tip + dx, dy) to the tip, tip in image px; may start outside the window
      const q = a.to != null ? 1 - leave(t - a.to) : 1, d = E.out(seg(t, a.at, a.at + (a.dur ?? .5))); if (d <= .002 || q <= .002) continue;
      const [tx, ty] = P(a.tip[0], a.tip[1]), sx = tx + (a.dx ?? 160), sy = ty + (a.dy ?? -160), bend = a.bend ?? .18;
      const mx = (sx + tx) / 2 - (ty - sy) * bend, my = (sy + ty) / 2 + (tx - sx) * bend;
      const bz = u => [(1 - u) ** 2 * sx + 2 * (1 - u) * u * mx + u * u * tx, (1 - u) ** 2 * sy + 2 * (1 - u) * u * my + u * u * ty];
      alpha(ctx, q, () => {
        ctx.save(); drop(ctx, .22, 10, 4); stroke(ctx, a.color ? col(a.color) : C.blue, a.lw || 10);
        ctx.beginPath(); ctx.moveTo(sx, sy); for (let u = .04; u <= d + 1e-6; u += .04) { const [px, py] = bz(Math.min(u, d)); ctx.lineTo(px, py); } ctx.stroke();
        if (d > .7) { const [ex, ey] = bz(d), [bx, by] = bz(d - .06), an = Math.atan2(ey - by, ex - bx), H = 34 * S(d - .7, 18) / S(.3, 18);
          ctx.beginPath(); ctx.moveTo(ex - Math.cos(an - .55) * H, ey - Math.sin(an - .55) * H); ctx.lineTo(ex, ey); ctx.lineTo(ex - Math.cos(an + .55) * H, ey - Math.sin(an + .55) * H); ctx.stroke(); }
        ctx.restore();
        if (a.label) { const qq = S(t - a.at - .25, 13); if (qq > .002) alpha(ctx, qq, () => chip(ctx, sx, sy + (a.dy > 0 ? 50 : -50), a.label, { size: a.labelSize || 40, h: Math.round((a.labelSize || 40) * 2), fill: C.blue, color: C.white, border: false })); }
      });
    }
  },
  glass(ctx, it) {   // frosted glass: the frame under it, blurred, then a white tint and a bright hairline
    const w = it.w, h = it.h, r = it.r ?? 34, m = ctx.getTransform(), cv = ctx.canvas;
    const q0 = m.transformPoint(new DOMPoint(0, 0)), q1 = m.transformPoint(new DOMPoint(w, h)), pad = 60 * m.a;
    const sx = Math.max(0, Math.floor(Math.min(q0.x, q1.x) - pad)), sy = Math.max(0, Math.floor(Math.min(q0.y, q1.y) - pad));
    const sw = Math.min(cv.width, Math.ceil(Math.max(q0.x, q1.x) + pad)) - sx, sh = Math.min(cv.height, Math.ceil(Math.max(q0.y, q1.y) + pad)) - sy;
    ctx.save(); const out = new Path2D(); out.rect(-300, -300, w + 600, h + 600); out.roundRect(0, 0, w, h, r); ctx.clip(out, 'evenodd');
    shadow(ctx, 0, 0, w, h, r, 44, .2, 16); ctx.restore();
    if (sw > 0 && sh > 0) { ctx.save(); ctx.beginPath(); ctx.roundRect(0, 0, w, h, r); ctx.clip(); ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.filter = `blur(${Math.round((it.blur ?? 22) * m.a)}px)`; ctx.drawImage(cv, sx, sy, sw, sh, sx, sy, sw, sh); ctx.restore(); }
    ctx.beginPath(); ctx.roundRect(0, 0, w, h, r); ctx.fillStyle = `rgba(250,249,246,${it.tint ?? .62})`; ctx.fill();
    ctx.lineWidth = 2; ctx.strokeStyle = 'rgba(255,255,255,.9)'; ctx.stroke();
    ctx.beginPath(); ctx.roundRect(-1, -1, w + 2, h + 2, r + 1); ctx.lineWidth = 1; ctx.strokeStyle = 'rgba(20,22,27,.08)'; ctx.stroke();
  },
  gauge(ctx, it, t) {   // speedometer: a 270° dial, the blue arc and the needle sweep to value (0..1) with a motion trail, centered
    const r = it.r || 170, a0 = Math.PI * .75, span = Math.PI * 1.5, f0 = it.sweepFrom ?? it.at + .1, f1 = it.sweepTo ?? f0 + .8;
    const vAt = tt => (it.value ?? .9) * E.out(seg(tt, f0, f1)), v = vAt(t), R0 = r - 22;
    sheet(ctx, -r - 26, -r - 26, 2 * r + 52, 2 * r + 52, r + 26, { elev: .9 });
    ctx.save(); ctx.lineCap = 'round';
    ctx.beginPath(); ctx.arc(0, 0, R0, a0, a0 + span); ctx.lineWidth = 24; ctx.strokeStyle = 'rgba(40,30,10,.07)'; ctx.stroke();
    if (v > .002) { ctx.beginPath(); ctx.arc(0, 0, R0, a0, a0 + span * v); ctx.strokeStyle = C.blue; ctx.stroke(); }
    for (let i = 0; i <= 20; i++) {
      const a = a0 + span * i / 20, big = i % 5 === 0, r1 = R0 - 30, r2 = R0 - (big ? 62 : 46);
      ctx.beginPath(); ctx.moveTo(Math.cos(a) * r1, Math.sin(a) * r1); ctx.lineTo(Math.cos(a) * r2, Math.sin(a) * r2);
      ctx.lineWidth = big ? 6 : 3; ctx.strokeStyle = i / 20 <= v + .001 ? C.ink : C.ink3; ctx.stroke();
    }
    const needle = (an, op) => alpha(ctx, op, () => { ctx.save(); ctx.rotate(an); ctx.beginPath(); ctx.moveTo(-24, -9); ctx.lineTo(R0 - 58, -2.5); ctx.lineTo(R0 - 58, 2.5); ctx.lineTo(-24, 9); ctx.closePath(); ctx.fillStyle = C.ink; ctx.fill(); ctx.restore(); });
    for (const [lag, op] of [[.12, .1], [.08, .16], [.04, .26]]) { const lv = vAt(t - lag); if (v - lv > .015) needle(a0 + span * lv, op); }   // trail while it sweeps fast
    ctx.save(); drop(ctx, .22, 10, 4); needle(a0 + span * v, 1); ctx.restore();
    ctx.beginPath(); ctx.arc(0, 0, 20, 0, TAU); ctx.fillStyle = C.blue; ctx.fill(); ctx.beginPath(); ctx.arc(0, 0, 7, 0, TAU); ctx.fillStyle = C.white; ctx.fill();
    ctx.restore();
    if (it.unit) text(ctx, it.unit, 0, r * .62, { size: 32, weight: 800, align: 'center', color: C.ink3 });
  },
  pixelate(ctx, it, t, R) {   // a real image that resolves from big pixel blocks to sharp (sharpFrom..sharpTo), then a light sweep, centered
    const im = R?.img('/p/' + it.img); if (!im) return;
    const w = it.w || 300, h = it.h || Math.round(w * im.height / im.width), r = it.r ?? 26, x0 = -w / 2, y0 = -h / 2;
    const f0 = it.sharpFrom ?? it.at + .3, f1 = it.sharpTo ?? f0 + .9, p = seg(t, f0, f1);
    const steps = [it.block || 44, 30, 20, 12, 7, 3], blk = p >= 1 ? 1 : steps[Math.min(steps.length - 1, Math.floor(p * steps.length))];
    lift(ctx, x0, y0, w, h, r, 1);
    ctx.save(); ctx.beginPath(); ctx.roundRect(x0, y0, w, h, r); ctx.clip();
    if (blk <= 1) { ctx.imageSmoothingQuality = 'high'; ctx.drawImage(im, x0, y0, w, h); }
    else {
      const m = Math.hypot(ctx.getTransform().a, ctx.getTransform().b), cw = Math.max(2, Math.round(w * m / blk)), ch = Math.max(2, Math.round(h * m / blk));
      PIX.width = cw; PIX.height = ch; const pc = PIX.getContext('2d'); pc.imageSmoothingQuality = 'high'; pc.drawImage(im, 0, 0, cw, ch);
      ctx.imageSmoothingEnabled = false; ctx.drawImage(PIX, 0, 0, cw, ch, x0, y0, w, h); ctx.imageSmoothingEnabled = true;
    }
    const g = seg(t, f1, f1 + .55); if (g > 0 && g < 1) {   // sheen: a soft white band crossing once when it lands
      const bx = lerp(x0 - w * .6, x0 + w * 1.2, E.io(g)), gr = ctx.createLinearGradient(bx, y0, bx + w * .45, y0 + h * .25);
      gr.addColorStop(0, 'rgba(255,255,255,0)'); gr.addColorStop(.5, 'rgba(255,255,255,.42)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
      ctx.fillStyle = gr; ctx.fillRect(x0, y0, w, h);
    }
    ctx.restore();
    ctx.beginPath(); ctx.roundRect(x0, y0, w, h, r); ctx.lineWidth = 2; ctx.strokeStyle = 'rgba(20,22,27,.1)'; ctx.stroke();
  },
  render(ctx, it, t, R) {   // a render crawling: dark window, film strip of real frames developing one by one, striped bar, frame counter, timer; centered
    const w = it.w || 900, h = it.h || 420, r = 30, x0 = -w / 2, y0 = -h / 2, f0 = it.progFrom ?? it.at, f1 = it.progTo ?? f0 + 4;
    const p = (it.prog ?? 1) * clamp((t - f0) / (f1 - f0)), imgs = it.imgs || [], n = imgs.length, pad = 30;
    lift(ctx, x0, y0, w, h, r, 1.2);
    ctx.save(); drop(ctx, .28, 40, 18); ctx.beginPath(); ctx.roundRect(x0, y0, w, h, r); ctx.fillStyle = '#1B1B1D'; ctx.fill(); ctx.restore();
    ['#FF5F57', '#FEBC2E', '#28C840'].forEach((c, i) => { ctx.beginPath(); ctx.arc(x0 + 36 + i * 28, y0 + 36, 8, 0, TAU); ctx.fillStyle = c; ctx.fill(); });
    if (it.title) text(ctx, it.title, x0 + 130, y0 + 46, { size: 28, weight: 600, fam: 'JetBrains Mono', color: 'rgba(255,255,255,.55)' });
    ctx.save(); ctx.translate(x0 + w - 44, y0 + 36); ctx.rotate(t * 7); ctx.beginPath(); ctx.arc(0, 0, 12, 0, TAU * .72); stroke(ctx, C.blue, 4); ctx.stroke(); ctx.restore();
    const sy = y0 + 72, sh = h - 72 - 126, gap = 12, fw = n ? (w - pad * 2 - gap * (n - 1)) / n : 0, done = p * n;
    imgs.forEach((src, i) => {
      const im = R?.img('/p/' + src), fx = x0 + pad + i * (fw + gap), q = clamp(done - i);
      ctx.save(); ctx.beginPath(); ctx.roundRect(fx, sy, fw, sh, 12); ctx.fillStyle = '#2A2A2E'; ctx.fill(); ctx.clip();
      if (q < 1) { const sx = fx + ((t * 260 + i * 70) % (fw * 2.2)) - fw * .6, gr = ctx.createLinearGradient(sx, 0, sx + fw * .6, 0);   // waiting: a dim shimmer
        gr.addColorStop(0, 'rgba(255,255,255,0)'); gr.addColorStop(.5, 'rgba(255,255,255,.06)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); ctx.fillStyle = gr; ctx.fillRect(fx, sy, fw, sh); }
      if (im && q > 0) {   // developing: revealed top to bottom behind a blue scan line
        ctx.save(); ctx.beginPath(); ctx.rect(fx, sy, fw, sh * q); ctx.clip(); ctx.imageSmoothingQuality = 'high';
        const k = Math.max(fw / im.width, sh / im.height), iw = im.width * k, ih = im.height * k; ctx.drawImage(im, fx + (fw - iw) / 2, sy + (sh - ih) / 2, iw, ih); ctx.restore();
        if (q < 1) { ctx.fillStyle = C.blue; ctx.fillRect(fx, sy + sh * q - 2, fw, 4); }
      }
      ctx.restore();
    });
    const by = y0 + h - 100, bw = w - pad * 2, bh = 22;
    ctx.beginPath(); ctx.roundRect(x0 + pad, by, bw, bh, bh / 2); ctx.fillStyle = 'rgba(255,255,255,.08)'; ctx.fill();
    if (p > .002) {
      const fwd = Math.max(bh, bw * p); ctx.save(); ctx.beginPath(); ctx.roundRect(x0 + pad, by, fwd, bh, bh / 2); ctx.fillStyle = C.blue; ctx.fill(); ctx.clip();
      ctx.fillStyle = 'rgba(255,255,255,.18)'; const o = (t * 60) % 36; for (let sx = x0 + pad - 40 + o; sx < x0 + pad + fwd; sx += 36) { ctx.beginPath(); ctx.moveTo(sx, by + bh); ctx.lineTo(sx + 14, by + bh); ctx.lineTo(sx + 28, by); ctx.lineTo(sx + 14, by); ctx.closePath(); ctx.fill(); }
      ctx.restore();
    }
    const tot = it.total || 0, el = (it.elapsed || 0) * p / (it.prog ?? 1), mm = Math.floor(el / 60), ss = String(Math.floor(el % 60)).padStart(2, '0');
    if (tot) text(ctx, `Frame ${Math.round(p * tot)} / ${tot}`, x0 + pad, by + 66, { size: 30, weight: 600, fam: 'JetBrains Mono', color: 'rgba(255,255,255,.7)' });
    if (it.elapsed) text(ctx, `${mm}:${ss}`, x0 + w - pad, by + 68, { size: 40, weight: 800, fam: 'JetBrains Mono', align: 'right', color: C.white });
  },
  term(ctx, it, t, R) {   // a Claude Code terminal, centered: header (logo, name, sub), a prompt box where `cmd` types (typeFrom..typeTo)
    // with the matching slash commands listed under it (suggest: [[name, desc]], first one highlighted), Enter at sendAt
    // moves the command into the history, then out: [{text, at}] lines land one by one with a dot
    const w = it.w || 960, h = it.h || 640, r = 30, x0 = -w / 2, y0 = -h / 2, pad = 44, M = 'JetBrains Mono', fs = it.size || 52;
    lift(ctx, x0, y0, w, h, r, 1.2);
    ctx.save(); drop(ctx, .28, 40, 18); ctx.beginPath(); ctx.roundRect(x0, y0, w, h, r); ctx.fillStyle = '#1B1B1D'; ctx.fill(); ctx.restore();
    ['#FF5F57', '#FEBC2E', '#28C840'].forEach((c, i) => { ctx.beginPath(); ctx.arc(x0 + 36 + i * 28, y0 + 36, 8, 0, TAU); ctx.fillStyle = c; ctx.fill(); });
    if (it.title) text(ctx, it.title, x0 + w / 2, y0 + 48, { size: 34, weight: 600, fam: M, align: 'center', color: 'rgba(255,255,255,.5)' });
    const hy = y0 + 160;
    if (it.logo) logoAt(R, ctx, it.logo, x0 + pad + 50, hy, 100);
    text(ctx, it.name || 'Claude Code', x0 + pad + 130, hy - 4, { size: 60, weight: 800, color: C.white });
    if (it.sub) text(ctx, it.sub, x0 + pad + 130, hy + 48, { size: 36, weight: 500, fam: M, color: 'rgba(255,255,255,.5)' });
    const cmd = it.cmd || '', tf = it.typeFrom ?? it.at, tt = it.typeTo ?? tf + cmd.length * .05, sent = it.sendAt != null && t >= it.sendAt;
    const n = Math.round(cmd.length * clamp((t - tf) / Math.max(.05, tt - tf))), typed = cmd.slice(0, n);
    const line = (s, y, c, cur) => {   // "> " + mono text, blue block cursor while it types
      text(ctx, '>', x0 + pad + 26, midBase(y, fs), { size: fs, weight: 700, fam: M, color: 'rgba(255,255,255,.45)' });
      const cx = x0 + pad + 80; text(ctx, s, cx, midBase(y, fs), { size: fs, weight: 600, fam: M, color: c });
      if (cur && Math.sin(t * 11) > -.3) { ctx.fillStyle = C.blue; ctx.fillRect(cx + measure(ctx, s, fs, 600, 0, M) + 4, y - fs * .55, fs * .55, fs * 1.1); }
    };
    let by = hy + 150;
    if (sent) {   // history: the sent command, then the output lines
      const q = E.out(seg(t, it.sendAt, it.sendAt + .3));
      line(cmd, by + (1 - q) * 60, C.white, false);
      (it.out || []).forEach((o, i) => {
        const p = S(t - o.at, 13); if (p <= .002) return; const oy = by + 100 + i * 84;
        alpha(ctx, Math.min(1, p * 1.4), () => {
          ctx.beginPath(); ctx.arc(x0 + pad + 36, oy + (1 - p) * 20, 11, 0, TAU); ctx.fillStyle = o.dim ? 'rgba(255,255,255,.4)' : C.blue; ctx.fill();
          text(ctx, o.text, x0 + pad + 80, midBase(oy + (1 - p) * 20, 42), { size: 42, weight: 500, fam: M, color: o.dim ? 'rgba(255,255,255,.55)' : C.white });
        });
      });
      return;
    }
    const bh = fs * 2.1;
    ctx.beginPath(); ctx.roundRect(x0 + pad, by - bh / 2, w - pad * 2, bh, 18); ctx.lineWidth = 3; ctx.strokeStyle = 'rgba(255,255,255,.22)'; ctx.stroke();
    if (!typed && it.placeholder) text(ctx, it.placeholder, x0 + pad + 80, midBase(by, fs), { size: fs * .8, weight: 500, fam: M, color: 'rgba(255,255,255,.3)' });
    line(typed, by, C.white, t >= (it.focusAt ?? tf - .3));
    const sg = it.suggest || []; if (!sg.length || n < 1) return;
    const shown = sg.filter(([nm]) => nm.startsWith(typed) || typed.startsWith(nm.slice(0, typed.length)));
    shown.slice(0, 4).forEach(([nm, desc], i) => {
      const sy = by + bh / 2 + 60 + i * 74, hi = i === 0;
      if (hi) { ctx.beginPath(); ctx.roundRect(x0 + pad, sy - 34, w - pad * 2, 68, 14); ctx.fillStyle = 'rgba(37,142,255,.16)'; ctx.fill(); }
      text(ctx, nm, x0 + pad + 26, midBase(sy, 40), { size: 40, weight: 700, fam: M, color: hi ? C.blue : 'rgba(255,255,255,.6)' });
      if (desc) text(ctx, desc, x0 + w - pad - 22, midBase(sy, 36), { size: 36, weight: 500, align: 'right', color: hi ? 'rgba(255,255,255,.8)' : 'rgba(255,255,255,.4)' });
    });
  },
  edit(ctx, it, t, R) {   // a timeline that edits itself, centered: real clips with their silences (boxed at markAt, closed at cutAt),
    // "Aa" caption pills dropping on each clip (capsAt), blue animation blocks with a sparkle (fxAt), a playhead (playFrom..playTo),
    // then steps [{text, at}] as blue chips that check one by one under the sheet
    const imgs = it.imgs || [], n = Math.max(1, imgs.length), w = it.w || 960, hw = 92, pad = 26, vh = it.vh || 150, th = 62, gap = 14;
    const h = pad * 2 + vh + (th + gap) * 2, x0 = -w / 2, y0 = -h / 2, lx = x0 + hw, lw = w - hw - pad;
    const cu = i => [1.25, .95, 1.15, .9, 1.05][i % 5], gu = i => i < n - 1 ? [.42, .3, .5, .36][i % 4] : 0;
    const mk = it.markAt != null ? S(t - it.markAt, 12) : 0, cl = it.cutAt != null ? E.io(seg(t, it.cutAt, it.cutAt + .45)) : 0;
    let U = 0; for (let i = 0; i < n; i++) U += cu(i) + gu(i);
    const unit = lw / U, xs = []; let acc = lx;
    for (let i = 0; i < n; i++) { xs.push(acc); acc += (cu(i) + gu(i) * (1 - cl)) * unit; }
    const span = acc - lx, ph = it.playFrom != null ? E.io(seg(t, it.playFrom, it.playTo ?? it.playFrom + 1.2)) : -1, phx = lx + span * ph;
    const vy = y0 + pad, ty = vy + vh + gap, fy = ty + th + gap;
    const spark = (x, y, r, c) => { ctx.beginPath(); for (let k = 0; k < 8; k++) { const a = k * TAU / 8 - TAU / 4, rr = k % 2 ? r * .32 : r; ctx[k ? 'lineTo' : 'moveTo'](x + Math.cos(a) * rr, y + Math.sin(a) * rr); } ctx.closePath(); ctx.fillStyle = c; ctx.fill(); };
    sheet(ctx, x0, y0, w, h, 34, { elev: 1.2 });
    [ty - gap / 2, fy - gap / 2].forEach(yy => { ctx.fillStyle = C.line; ctx.fillRect(x0 + 24, yy, w - 48, 1.5); });
    const hx = x0 + hw / 2;   // track heads: play, Aa, sparkle
    ctx.beginPath(); ctx.moveTo(hx - 13, vy + vh / 2 - 17); ctx.lineTo(hx + 17, vy + vh / 2); ctx.lineTo(hx - 13, vy + vh / 2 + 17); ctx.closePath(); ctx.fillStyle = C.ink; ctx.fill();
    text(ctx, 'Aa', hx, midBase(ty + th / 2, 32), { size: 32, weight: 800, align: 'center', color: C.ink });
    spark(hx, fy + th / 2, 19, C.ink);
    for (let i = 0; i < n; i++) {
      const cx = xs[i], cw = cu(i) * unit - 6, im = R?.img('/p/' + imgs[i]), on = ph > 0 && ph < 1 && phx >= cx && phx <= cx + cw;
      ctx.save(); ctx.beginPath(); ctx.roundRect(cx, vy, cw, vh, 12); ctx.fillStyle = C.dim; ctx.fill(); ctx.clip();
      if (im) { const k = Math.max(cw / im.width, vh / im.height); ctx.imageSmoothingQuality = 'high'; ctx.drawImage(im, cx + (cw - im.width * k) / 2, vy + (vh - im.height * k) / 2, im.width * k, im.height * k); }
      ctx.restore();
      ctx.beginPath(); ctx.roundRect(cx, vy, cw, vh, 12); ctx.strokeStyle = on ? C.blue : 'rgba(20,22,27,.12)'; ctx.lineWidth = on ? 5 : 2; ctx.stroke();
      const gw = gu(i) * (1 - cl) * unit, gx = cx + cu(i) * unit - 6;   // the silence after this clip: flat dashes, boxed, then closed
      if (gw > 1) {
        alpha(ctx, 1 - cl, () => { for (let q = gx + 10; q < gx + gw - 8; q += 16) { ctx.beginPath(); ctx.roundRect(q, vy + vh / 2 - 4, 9, 8, 4); ctx.fillStyle = C.ink3; ctx.fill(); } });
        alpha(ctx, mk * (1 - cl), () => {
          ctx.beginPath(); ctx.roundRect(gx + 4, vy + 10, Math.max(2, gw - 2), vh - 20, 12); ctx.fillStyle = 'rgba(37,142,255,.12)'; ctx.fill();
          ctx.setLineDash([10, 8]); ctx.strokeStyle = C.blue; ctx.lineWidth = 3; ctx.stroke(); ctx.setLineDash([]);
        });
      }
      if (it.capsAt != null) { const p = S(t - it.capsAt - i * .07, 13); if (p > .002) alpha(ctx, Math.min(1, p * 1.4), () => {
        const yy = ty + 6 - 26 * (1 - p), pw = Math.max(40, cw - 8);
        ctx.beginPath(); ctx.roundRect(cx + 4, yy, pw, th - 12, 12); ctx.fillStyle = on ? C.blue : C.tint; ctx.fill(); ctx.strokeStyle = C.blue; ctx.lineWidth = 2; ctx.stroke();
        text(ctx, 'Aa', cx + 18, midBase(yy + (th - 12) / 2, 26), { size: 26, weight: 800, color: on ? C.white : C.blue });
        if (pw > 110) { ctx.beginPath(); ctx.roundRect(cx + 66, yy + (th - 12) / 2 - 5, Math.min(pw - 84, 90), 10, 5); ctx.fillStyle = on ? 'rgba(255,255,255,.8)' : 'rgba(37,142,255,.45)'; ctx.fill(); }
      }); }
      if (it.fxAt != null) { const p = S(t - it.fxAt - i * .07, 13); if (p > .002) alpha(ctx, Math.min(1, p * 1.4), () => {
        const bw = cw * (.45 + .3 * hash(i * 5.1 + 2)), bx = cx + 4 + (cw - 8 - bw) * hash(i * 2.7 + 9), yy = fy + 6, bh = th - 12, k = .6 + .4 * p;
        ctx.save(); ctx.translate(bx + bw / 2, yy + bh / 2); ctx.scale(k, k);
        ctx.beginPath(); ctx.roundRect(-bw / 2, -bh / 2, bw, bh, 12); ctx.fillStyle = C.blue; ctx.fill();
        spark(-bw / 2 + 24, 0, 14, C.white); ctx.restore();
      }); }
    }
    if (ph >= 0 && t > it.playFrom - .2) alpha(ctx, clamp((t - it.playFrom + .2) / .2), () => {
      ctx.fillStyle = C.ink; ctx.fillRect(phx - 2.5, y0 + 8, 5, h - 16);
      ctx.beginPath(); ctx.moveTo(phx - 15, y0 - 6); ctx.lineTo(phx + 15, y0 - 6); ctx.lineTo(phx, y0 + 14); ctx.closePath(); ctx.fill();
    });
    const st = it.steps || []; if (st.length) {
      const sz = 34, ws = st.map(s => measure(ctx, s.text, sz, 700, -.3) + Math.round(sz * .72) * 2 + sz * .95), sg = 16;
      let sx = -(ws.reduce((a, b) => a + b, 0) + sg * (st.length - 1)) / 2;
      st.forEach((s, i) => { const p = S(t - s.at, 12);
        if (p > .002) { ctx.save(); ctx.translate(0, 22 * (1 - p)); chip(ctx, sx, y0 + h + 58, s.text, { size: sz, align: 'left', fill: C.blue, color: C.onBlue, check: true, checkP: E.out(seg(t, s.at + .08, s.at + .4)), alpha: Math.min(1, p * 1.4) }); ctx.restore(); }
        sx += ws[i] + sg; });
    }
  },
  yt(ctx, it, t, R) {   // YouTube video card: thumbnail (duration chip, red play), avatar, two-line title, channel + meta
    const w = it.w || 760, pad = 24, tw = w - pad * 2, th = Math.round(tw * 9 / 16), ts = it.titleSize || 36;
    const lines = wrap(ctx, it.title || '', tw - 96, ts, 700, -.4).slice(0, 2), h = pad + th + 26 + lines.length * ts * 1.25 + 48 + pad;
    const x0 = -w / 2, y0 = -h / 2, im = it.img ? R?.img('/p/' + it.img) : null, av = it.avatarImg ? R?.img('/p/' + it.avatarImg) : null;
    sheet(ctx, x0, y0, w, h, 30, { elev: 1.1 });
    ctx.save(); ctx.beginPath(); ctx.roundRect(x0 + pad, y0 + pad, tw, th, 18); ctx.clip();
    if (im) { const k = Math.max(tw / im.width, th / im.height); ctx.imageSmoothingQuality = 'high'; ctx.drawImage(im, x0 + pad + (tw - im.width * k) / 2, y0 + pad + (th - im.height * k) / 2, im.width * k, im.height * k); }
    else { ctx.fillStyle = C.ink; ctx.fillRect(x0 + pad, y0 + pad, tw, th); }
    ctx.restore();
    const px = 0, py = y0 + pad + th / 2;
    ctx.save(); drop(ctx, .3, 18, 6); ctx.beginPath(); ctx.roundRect(px - 52, py - 36, 104, 72, 20); ctx.fillStyle = '#FF0033'; ctx.fill(); ctx.restore();
    ctx.beginPath(); ctx.moveTo(px - 13, py - 18); ctx.lineTo(px + 20, py); ctx.lineTo(px - 13, py + 18); ctx.closePath(); ctx.fillStyle = '#FFFFFF'; ctx.fill();
    if (it.dur) { const dw = measure(ctx, it.dur, 26, 700) + 22; ctx.beginPath(); ctx.roundRect(x0 + pad + tw - dw - 12, y0 + pad + th - 50, dw, 38, 8); ctx.fillStyle = 'rgba(0,0,0,.8)'; ctx.fill();
      text(ctx, it.dur, x0 + pad + tw - dw / 2 - 12, y0 + pad + th - 22, { size: 26, weight: 700, align: 'center', color: '#FFFFFF' }); }
    const ay = y0 + pad + th + 26, ax = x0 + pad + 34;
    ctx.save(); ctx.beginPath(); ctx.arc(ax, ay + 34, 34, 0, TAU); ctx.clip(); if (av) ctx.drawImage(av, ax - 34, ay, 68, 68); else { ctx.fillStyle = C.ink2; ctx.fill(); } ctx.restore();
    lines.forEach((ln, i) => text(ctx, ln, x0 + pad + 96, ay + ts * .9 + i * ts * 1.25, { size: ts, weight: 700, ls: -.4 }));
    text(ctx, [it.channel, it.meta].filter(Boolean).join(' · '), x0 + pad + 96, ay + lines.length * ts * 1.25 + 34, { size: 28, weight: 500, color: C.ink3 });
  },
  toggle(ctx, it, t) {   // settings switch: label, then a pill whose knob slides right and turns blue at onAt
    const size = it.size || 40, lw = measure(ctx, it.label || '', size, 700, -.4), sw = size * 2.6, sh = size * 1.5, gap = size * .8, x0 = -(lw + gap + sw) / 2;
    const on = it.onAt != null ? S(t - it.onAt, 12) : 0;
    text(ctx, it.label || '', x0, midBase(0, size), { size, weight: 700, ls: -.4 });
    const bx = x0 + lw + gap; ctx.beginPath(); ctx.roundRect(bx, -sh / 2, sw, sh, sh / 2); ctx.fillStyle = mix('#D9D5CC', C.blue, on); ctx.fill();
    ctx.save(); drop(ctx, .25, 8, 3); ctx.beginPath(); ctx.arc(bx + sh / 2 + (sw - sh) * on, 0, sh / 2 - 6, 0, TAU); ctx.fillStyle = '#FFFFFF'; ctx.fill(); ctx.restore();
  },
  shatter(ctx, it, t, R) {   // a real logo that breaks into glass shards at breakAt (hit [x, y] = impact point, -1..1 of the icon), with a blue shockwave
    const sz = it.s || 260, im = R?.img('/p/' + it.logo), tau = t - (it.breakAt ?? 1e9);
    if (tau < 0) return logoAt(R, ctx, it.logo, 0, 0, sz, it.gray);
    if (!im) return;
    const sh = it._shards || (it._shards = shards(sz, it.hit || [-.35, -.1], it.n || 10, it.seed || 7)), h = sz / 2, rr = sz * .22;
    const icon = new Path2D(); icon.roundRect(-h, -h, sz, sz, rr);
    for (const q of sh) {
      const a = 1 - seg(tau, .42, .95); if (a <= .002) break;
      const ox = q.vx * tau, oy = q.vy * tau + 1300 * tau * tau, k = 1 - .25 * seg(tau, .2, .95);
      ctx.save(); ctx.globalAlpha *= a; ctx.translate(q.cx + ox, q.cy + oy); ctx.rotate(q.w * tau); ctx.scale(k, k); ctx.translate(-q.cx, -q.cy);
      ctx.save(); if (it.tight) ctx.clip(icon); drop(ctx, .22, 16, 8); ctx.fillStyle = C.white; ctx.fill(q.path); ctx.restore();
      ctx.clip(q.path); ctx.clip(icon); ctx.imageSmoothingQuality = 'high'; ctx.drawImage(im, -h, -h, sz, sz);
      ctx.lineWidth = 2.5; ctx.strokeStyle = 'rgba(255,255,255,.85)'; ctx.stroke(q.path); ctx.restore();
    }
    const [hx, hy] = (it.hit || [-.35, -.1]).map(v => v * h), w = E.out(seg(tau, 0, .5));   // shockwave + spark lines from the impact
    if (w < 1) alpha(ctx, 1 - w, () => {
      ctx.beginPath(); ctx.arc(hx, hy, lerp(sz * .2, sz * 1.25, w), 0, TAU); stroke(ctx, C.blue, lerp(18, 3, w)); ctx.stroke();
      for (let i = 0; i < 12; i++) { const an = i / 12 * TAU + hash(i + 3) * .4, r0 = lerp(sz * .3, sz * 1.1, w), r1 = r0 + lerp(70, 10, w);
        ctx.beginPath(); ctx.moveTo(hx + Math.cos(an) * r0, hy + Math.sin(an) * r0); ctx.lineTo(hx + Math.cos(an) * r1, hy + Math.sin(an) * r1); stroke(ctx, i % 3 ? C.blue : C.ink, 7); ctx.stroke(); }
    });
  },
  icon(ctx, it, t) { const f = ICONS[it.name]; if (!f) return; const s = it.s || 1; ctx.scale(s, s); if (deepness() > 0) drop(ctx, .16, 18, 8); f(ctx, it, t); },
  starship(ctx, it, t) { drawStarship(ctx, it, t); },
  ferrari(ctx, it, t) { drawFerrari(ctx, it, t); },
  ostrich(ctx, it, t) { drawOstrich(ctx, it, t); },
};

// ---------------------------------------------------------------- illustrated actors (drawn, no image assets)
// starship {s 1, igniteAt (default at + .3), liftFrom, liftTo, liftY 160}: a stainless Starship (heat tiles, flaps, three
// bells) on a paper launch pad; the blue-white flame flickers from igniteAt, smoke puffs spread on the pad, and between
// liftFrom and liftTo the ship climbs liftY px while the smoke stays on the ground. (0, 0) = ship centre at rest.
function drawStarship(ctx, it, t) {
  const s = it.s || 1, ign = it.igniteAt ?? it.at + .3, r = 48, top = -170, bot = 236, tip = -306;
  ctx.scale(s, s);
  const lift = it.liftFrom != null ? (u => u * u * u)(seg(t, it.liftFrom, it.liftTo ?? it.liftFrom + 1.4)) * (it.liftY ?? 160) / s : 0;
  const fire = S(t - ign, 9), pad = bot + 54;
  // smoke on the pad (stays put while the ship climbs)
  if (fire > .002) for (let i = 0; i < 18; i++) {   // a billowing cloud that rolls out both ways along the pad
    const side = i % 2 ? 1 : -1, u = Math.floor(i / 2) / 8, age = Math.max(0, t - ign - u * .35);
    const grow = 1 - Math.exp(-age * 2.2), reach = (1 - Math.exp(-age * 1.1)) * (60 + 230 * u) * (1 + .25 * hash(i + 3));
    const rad = (30 + 46 * (1 - u * .55) * (.7 + .6 * hash(i + 11))) * (.25 + .75 * grow) * (1 + .5 * seg(lift, 0, 120));
    const x = side * (22 + reach) + 6 * noise1(t * .9 + i), y = pad - rad * .5 - 30 * u * grow - 8 * hash(i + 5);
    ctx.save(); drop(ctx, .1, 22, 8); ctx.beginPath(); ctx.arc(x, y, rad, 0, TAU);
    const g = ctx.createRadialGradient(x - rad * .35, y - rad * .45, rad * .1, x, y, rad);
    g.addColorStop(0, '#FFFFFF'); g.addColorStop(.7, '#F1EEE8'); g.addColorStop(1, '#DDD8CD'); ctx.fillStyle = g; ctx.globalAlpha *= Math.min(1, fire * 1.2) * (1 - .35 * u); ctx.fill(); ctx.restore();
  }
  ctx.save(); ctx.translate(0, -lift);
  // flame
  if (fire > .002) {
    const fl = (130 + 46 * noise1(t * 13) + lift * .35) * fire, w = 34 + 5 * noise1(t * 17 + 4);
    const g = ctx.createLinearGradient(0, bot, 0, bot + fl);
    g.addColorStop(0, '#FFFFFF'); g.addColorStop(.22, '#CFE4FF'); g.addColorStop(.55, 'rgba(37,142,255,.85)'); g.addColorStop(1, 'rgba(37,142,255,0)');
    ctx.beginPath(); ctx.moveTo(-w, bot + 8); ctx.bezierCurveTo(-w * 1.15, bot + fl * .35, -w * .35, bot + fl * .8, 0, bot + fl);
    ctx.bezierCurveTo(w * .35, bot + fl * .8, w * 1.15, bot + fl * .35, w, bot + 8); ctx.closePath(); ctx.fillStyle = g; ctx.fill();
    ctx.beginPath(); ctx.ellipse(0, bot + 18 + fl * .16, w * .42, fl * .2, 0, 0, TAU); ctx.fillStyle = 'rgba(255,255,255,.9)'; ctx.fill();
  }
  // bells
  for (const bx of [-24, 0, 24]) { ctx.beginPath(); ctx.moveTo(bx - 8, bot - 2); ctx.lineTo(bx + 8, bot - 2); ctx.lineTo(bx + 12, bot + 16); ctx.lineTo(bx - 12, bot + 16); ctx.closePath(); ctx.fillStyle = '#3A3E46'; ctx.fill(); }
  // flaps (behind the hull edge)
  const flap = (pts) => { ctx.beginPath(); pts.forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)); ctx.closePath(); ctx.fillStyle = '#2C2F36'; ctx.fill(); ctx.strokeStyle = 'rgba(255,255,255,.18)'; ctx.lineWidth = 2; ctx.stroke(); };
  for (const sg of [-1, 1]) {
    flap([[sg * (r - 4), -226], [sg * (r + 26), -204], [sg * (r + 28), -164], [sg * (r - 4), -150]]);
    flap([[sg * (r - 4), 104], [sg * (r + 50), 160], [sg * (r + 52), bot - 4], [sg * (r - 4), bot - 4]]);
  }
  // hull
  const hull = new Path2D(); hull.moveTo(-r, bot); hull.lineTo(-r, top); hull.bezierCurveTo(-r, top - 78, -16, tip + 22, 0, tip);
  hull.bezierCurveTo(16, tip + 22, r, top - 78, r, top); hull.lineTo(r, bot); hull.closePath();
  ctx.save(); drop(ctx, .22, 34, 16); ctx.fillStyle = '#C9CED6'; ctx.fill(hull); ctx.restore();
  ctx.save(); ctx.clip(hull);
  const steel = ctx.createLinearGradient(-r, 0, r, 0);
  steel.addColorStop(0, '#8E949E'); steel.addColorStop(.2, '#DDE1E7'); steel.addColorStop(.42, '#FFFFFF'); steel.addColorStop(.68, '#CBD0D8'); steel.addColorStop(1, '#858B95');
  ctx.fillStyle = steel; ctx.fillRect(-r, tip, 2 * r, bot - tip);
  const tiles = ctx.createLinearGradient(-r, 0, -r * .1, 0); tiles.addColorStop(0, '#1E2026'); tiles.addColorStop(1, '#3B3F48');   // heat shield
  ctx.fillStyle = tiles; ctx.fillRect(-r, tip, r * .9, bot - tip);
  ctx.strokeStyle = 'rgba(255,255,255,.07)'; ctx.lineWidth = 1;
  for (let y = tip + 30; y < bot; y += 14) { ctx.beginPath(); ctx.moveTo(-r, y); ctx.lineTo(-r * .1, y); ctx.stroke(); }
  ctx.strokeStyle = 'rgba(30,34,42,.12)'; ctx.lineWidth = 1.5;   // weld rings
  for (let y = top + 20; y < bot; y += 42) { ctx.beginPath(); ctx.moveTo(-r, y); ctx.lineTo(r, y); ctx.stroke(); }
  ctx.fillStyle = 'rgba(255,255,255,.75)'; ctx.fillRect(r * .12, tip + 40, 3, bot - tip - 50);   // specular line
  ctx.restore();
  ctx.strokeStyle = 'rgba(20,22,27,.28)'; ctx.lineWidth = 2; ctx.stroke(hull);
  ctx.restore();
}

// ostrich {s 1, downFrom, downTo, upAt, mound 300, dir 1}: an ostrich on a sand strip; between downFrom and downTo it
// bends its neck and buries its head in the mound (sand burst), at upAt it pulls out with a burst and three blue
// "wake up" ticks. (0, 0) = the ground under its body; it faces +x (dir -1 mirrors).
// A red Ferrari in side view, facing right, wheels on y = 0. It rolls in from the left on `at` (spinning wheels and speed
// lines while it brakes to a stop). {s, roll: px travelled on entry (default 260), rollDur (default .9)}.
function drawFerrari(ctx, it, t) {
  const s = it.s || 1; ctx.scale(s, s);
  const k = E.out(seg(t, it.at, it.at + (it.rollDur ?? .9))), roll = it.roll ?? 260, x0 = -roll * (1 - k), v = 1 - k;
  ctx.translate(x0, 0);
  // ground shadow
  ctx.save(); ctx.beginPath(); ctx.ellipse(0, 4, 300, 16, 0, 0, TAU); ctx.fillStyle = 'rgba(20,16,8,.16)'; ctx.filter = 'blur(6px)'; ctx.fill(); ctx.restore();
  // speed lines while it is still moving
  if (v > .02) { ctx.save(); ctx.lineCap = 'round'; ctx.strokeStyle = `rgba(23,25,30,${(.35 * v).toFixed(3)})`; ctx.lineWidth = 6;
    for (const [y, l] of [[-120, 120], [-80, 170], [-40, 110]]) { ctx.beginPath(); ctx.moveTo(-300 - 30, y); ctx.lineTo(-300 - 30 - l * v, y); ctx.stroke(); }
    ctx.restore(); }
  const body = new Path2D();
  body.moveTo(-268, -34); body.lineTo(-272, -78); body.quadraticCurveTo(-268, -100, -238, -104);
  body.lineTo(-150, -108); body.quadraticCurveTo(-110, -112, -78, -140); body.quadraticCurveTo(-48, -164, 10, -164);
  body.quadraticCurveTo(60, -164, 96, -128); body.quadraticCurveTo(116, -110, 160, -102);
  body.quadraticCurveTo(250, -90, 278, -66); body.quadraticCurveTo(290, -54, 284, -32); body.lineTo(226, -30);
  body.arc(166, -32, 58, 0, Math.PI, true); body.lineTo(-108, -30); body.arc(-168, -32, 58, 0, Math.PI, true); body.closePath();
  ctx.save(); drop(ctx, .22, 24, 10);
  const g = ctx.createLinearGradient(0, -164, 0, -30); g.addColorStop(0, '#F0383E'); g.addColorStop(.55, '#D41820'); g.addColorStop(1, '#8E0C12');
  ctx.fillStyle = g; ctx.fill(body); ctx.restore();
  ctx.save(); ctx.clip(body);
  // shoulder highlight and lower sill shade
  ctx.beginPath(); ctx.moveTo(-250, -96); ctx.quadraticCurveTo(0, -112, 270, -70); ctx.lineWidth = 7; ctx.strokeStyle = 'rgba(255,255,255,.35)'; ctx.stroke();
  ctx.fillStyle = 'rgba(40,0,4,.28)'; ctx.fillRect(-300, -46, 600, 20);
  // side intake
  ctx.beginPath(); ctx.moveTo(-60, -66); ctx.quadraticCurveTo(-20, -88, 30, -84); ctx.quadraticCurveTo(0, -64, -60, -66); ctx.fillStyle = '#1A1215'; ctx.fill();
  ctx.restore();
  // glasshouse
  ctx.beginPath(); ctx.moveTo(-96, -112); ctx.quadraticCurveTo(-60, -152, 8, -154); ctx.quadraticCurveTo(54, -154, 84, -122); ctx.quadraticCurveTo(60, -116, -96, -112); ctx.closePath();
  const gl = ctx.createLinearGradient(-90, -154, 80, -112); gl.addColorStop(0, '#2B3038'); gl.addColorStop(1, '#0F1115'); ctx.fillStyle = gl; ctx.fill();
  ctx.beginPath(); ctx.moveTo(-40, -146); ctx.lineTo(-8, -150); ctx.lineTo(-44, -116); ctx.lineTo(-72, -116); ctx.closePath(); ctx.fillStyle = 'rgba(255,255,255,.16)'; ctx.fill();
  ctx.fillStyle = '#C8121A'; ctx.fillRect(-14, -152, 9, 40);   // B pillar
  // mirror, lights
  ctx.beginPath(); ctx.ellipse(96, -126, 16, 8, -.3, 0, TAU); ctx.fillStyle = '#B5121A'; ctx.fill();
  ctx.beginPath(); ctx.moveTo(240, -84); ctx.quadraticCurveTo(268, -76, 276, -64); ctx.lineTo(250, -70); ctx.closePath(); ctx.fillStyle = '#F4F1EA'; ctx.fill();
  ctx.beginPath(); ctx.roundRect(-272, -92, 18, 12, 4); ctx.fillStyle = '#5A0408'; ctx.fill();
  // wheels: tyre, five-spoke rim, yellow caliper
  const spin = t * 2 + (it.roll ?? 260) * (1 - k) / 40;
  for (const wx of [-168, 166]) {
    ctx.save(); ctx.translate(wx, -32);
    ctx.beginPath(); ctx.arc(0, 0, 46, 0, TAU); ctx.fillStyle = '#16181C'; ctx.fill();
    ctx.beginPath(); ctx.arc(0, 0, 31, 0, TAU); const rg = ctx.createRadialGradient(-8, -10, 4, 0, 0, 31); rg.addColorStop(0, '#E9ECEF'); rg.addColorStop(1, '#8A9098'); ctx.fillStyle = rg; ctx.fill();
    ctx.beginPath(); ctx.roundRect(8, -22, 12, 26, 4); ctx.fillStyle = '#F2C200'; ctx.fill();
    ctx.rotate(spin); ctx.fillStyle = '#2A2E35';
    for (let i = 0; i < 5; i++) { ctx.rotate(TAU / 5); ctx.beginPath(); ctx.moveTo(-6, -6); ctx.lineTo(-4, -29); ctx.lineTo(4, -29); ctx.lineTo(6, -6); ctx.closePath(); ctx.globalAlpha *= .9; ctx.fill(); ctx.globalAlpha /= .9; }
    ctx.beginPath(); ctx.arc(0, 0, 7, 0, TAU); ctx.fillStyle = '#C9CDD2'; ctx.fill();
    ctx.restore();
  }
}

const OS = { skin: '#D6B8A8', skin2: '#B9998A', beak: '#E6C9A2', sand: '#E3DBCB', sand2: '#CDBFA6', ink: '#17191E' };
function drawOstrich(ctx, it, t) {
  const s = it.s || 1, hx = it.mound ?? 300; ctx.scale(s * (it.dir || 1), s);
  const down = it.downFrom != null ? E.io(seg(t, it.downFrom, it.downTo ?? it.downFrom + .8)) : 0;
  const up = it.upAt != null ? S(t - it.upAt, 10) : 0, P = clamp(down * (1 - up));
  const buried = it.downTo != null && t > it.downTo && (it.upAt == null || t < it.upAt);
  const wig = buried ? Math.sin((t - it.downTo) * 9) * 4 : 0;
  // legs
  const leg = (hip, tw) => {
    const knee = [hip[0] + 34 + 10 * P, -150 + 12 * P], foot = [hip[0] + 6, -6];
    ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.strokeStyle = OS.skin2;
    ctx.lineWidth = 24; ctx.beginPath(); ctx.moveTo(...hip); ctx.lineTo(...knee); ctx.stroke();
    ctx.lineWidth = 15; ctx.beginPath(); ctx.moveTo(...knee); ctx.lineTo(...foot); ctx.stroke();
    ctx.lineWidth = 12; ctx.beginPath(); ctx.moveTo(foot[0] - 8, -4); ctx.lineTo(foot[0] + 46, -2); ctx.stroke();
    ctx.lineWidth = 8; ctx.beginPath(); ctx.moveTo(foot[0], -4); ctx.lineTo(foot[0] + 28 + tw, -12); ctx.stroke();
  };
  ctx.save(); ctx.translate(wig, 0);
  leg([-96, -262], 0); ctx.globalAlpha *= .92; leg([-18, -262], 6); ctx.globalAlpha /= .92;
  // body (pitches forward as the head goes down)
  const bx = -50, by = -340, rot = lerp(-.1, .3, P);
  ctx.save(); ctx.translate(bx, by); ctx.rotate(rot);
  // tail plume
  const sway = Math.sin(t * 3.1) * .05 + (buried ? Math.sin((t - it.downTo) * 7) * .12 : 0);
  for (let i = 0; i < 6; i++) {
    const a = -2.55 + i * .2 + sway, L = 120 + 18 * Math.sin(i * 1.7);
    ctx.save(); ctx.translate(-150, -20); ctx.rotate(a);
    ctx.beginPath(); ctx.moveTo(0, 0); ctx.quadraticCurveTo(L * .5, -26, L, -4); ctx.quadraticCurveTo(L * .5, 16, 0, 0);
    ctx.fillStyle = i % 2 ? '#FFFFFF' : '#F1EEE8'; ctx.fill(); ctx.strokeStyle = 'rgba(20,22,27,.14)'; ctx.lineWidth = 1.5; ctx.stroke(); ctx.restore();
  }
  ctx.save(); drop(ctx, .24, 36, 18);
  ctx.beginPath(); ctx.ellipse(0, 0, 170, 112, 0, 0, TAU);
  const g = ctx.createRadialGradient(-30, -60, 20, 0, 0, 190); g.addColorStop(0, '#3A3E46'); g.addColorStop(1, OS.ink);
  ctx.fillStyle = g; ctx.fill(); ctx.restore();
  ctx.save(); ctx.beginPath(); ctx.ellipse(0, 0, 170, 112, 0, 0, TAU); ctx.clip();   // feather scallops
  ctx.strokeStyle = 'rgba(255,255,255,.08)'; ctx.lineWidth = 3;
  for (let row = 0; row < 4; row++) for (let i = 0; i < 9; i++) { const x = -150 + i * 38 + (row % 2) * 19, y = -50 + row * 34; ctx.beginPath(); ctx.arc(x, y, 22, .2, Math.PI - .2); ctx.stroke(); }
  ctx.restore();
  for (let i = 0; i < 5; i++) {   // white wing plumes on the flank
    const a = .25 + i * .12; ctx.save(); ctx.translate(-30 + i * 12, 40); ctx.rotate(Math.PI - a);
    ctx.beginPath(); ctx.moveTo(0, 0); ctx.quadraticCurveTo(60, -18, 118, 0); ctx.quadraticCurveTo(60, 14, 0, 0); ctx.fillStyle = '#FFFFFF'; ctx.fill(); ctx.restore();
  }
  ctx.restore();
  // neck from the shoulder to the head, clipped at the ground line so the buried head disappears under the sand
  ctx.save(); ctx.beginPath(); ctx.rect(-3000, -3000, 6000, 3000); ctx.clip();
  const sh = [bx + Math.cos(rot) * 128 - Math.sin(rot) * -58, by + Math.sin(rot) * 128 + Math.cos(rot) * -58];
  const H = [lerp(sh[0] + 66, hx - wig, P), lerp(-760, 34, P)], Cc = [lerp(sh[0] + 22, sh[0] + 250, P), lerp(-560, sh[1] - 230, P)];
  const q = u => [(1 - u) ** 2 * sh[0] + 2 * (1 - u) * u * Cc[0] + u * u * H[0], (1 - u) ** 2 * sh[1] + 2 * (1 - u) * u * Cc[1] + u * u * H[1]];
  ctx.lineCap = 'round';
  for (let i = 0; i < 24; i++) { const a = q(i / 24), b = q((i + 1) / 24); ctx.beginPath(); ctx.moveTo(...a); ctx.lineTo(...b); ctx.lineWidth = lerp(40, 20, i / 24); ctx.strokeStyle = OS.skin; ctx.stroke(); }
  ctx.save(); ctx.beginPath(); ctx.ellipse(sh[0] - 6, sh[1] + 8, 40, 30, rot, 0, TAU); ctx.fillStyle = OS.ink; ctx.fill(); ctx.restore();   // feather collar
  // head along the neck tangent
  const tg = Math.atan2(H[1] - Cc[1], H[0] - Cc[0]), hd = lerp(.12, tg, P);   // upright: beak forward; buried: along the neck
  ctx.save(); ctx.translate(...H); ctx.rotate(hd);
  ctx.beginPath(); ctx.moveTo(22, -10); ctx.quadraticCurveTo(62, -8, 70, 2); ctx.quadraticCurveTo(58, 12, 20, 10); ctx.closePath(); ctx.fillStyle = OS.beak; ctx.fill();
  ctx.strokeStyle = OS.skin2; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(26, 1); ctx.lineTo(64, 2); ctx.stroke();
  ctx.beginPath(); ctx.ellipse(0, 0, 34, 27, 0, 0, TAU); ctx.fillStyle = OS.skin; ctx.fill();
  const wide = 1 + .35 * (it.upAt != null ? Math.max(0, 1 - Math.abs(t - it.upAt - .5) / 1.2) * up : 0);
  const blink = (t * 1.3 + .4) % 3.1 < .12 ? .15 : 1;
  ctx.beginPath(); ctx.ellipse(6, -7, 11 * wide, 11 * wide * blink, 0, 0, TAU); ctx.fillStyle = '#FFFFFF'; ctx.fill(); ctx.strokeStyle = OS.ink; ctx.lineWidth = 2.5; ctx.stroke();
  if (blink > .5) { ctx.beginPath(); ctx.arc(9, -7, 5.5, 0, TAU); ctx.fillStyle = OS.ink; ctx.fill(); }
  ctx.lineWidth = 2.5; ctx.beginPath(); for (const a of [-2.2, -1.85, -1.5]) { ctx.moveTo(6 + Math.cos(a) * 11 * wide, -7 + Math.sin(a) * 11 * wide); ctx.lineTo(6 + Math.cos(a) * 18 * wide, -7 + Math.sin(a) * 18 * wide); } ctx.stroke();
  ctx.restore();
  ctx.restore();
  ctx.restore();
  // sand strip and mound (drawn over the buried head)
  ctx.save(); drop(ctx, .1, 14, 4);
  ctx.beginPath(); ctx.roundRect(-430, -4, 900, 26, 13); ctx.fillStyle = OS.sand; ctx.fill(); ctx.restore();
  ctx.beginPath(); ctx.moveTo(hx - 120, 2); ctx.bezierCurveTo(hx - 80, -62, hx + 80, -62, hx + 120, 2); ctx.closePath();
  const mg = ctx.createLinearGradient(0, -50, 0, 4); mg.addColorStop(0, '#EAE3D5'); mg.addColorStop(1, OS.sand2); ctx.fillStyle = mg; ctx.fill();
  ctx.fillStyle = 'rgba(120,100,70,.25)'; for (let i = 0; i < 14; i++) { ctx.beginPath(); ctx.arc(hx - 90 + 180 * hash(i + 1), -6 - 34 * hash(i + 9) * (1 - Math.abs(hash(i + 1) - .5) * 1.6), 2.4, 0, TAU); ctx.fill(); }
  // sand bursts (head in, head out)
  for (const [bt, n] of [[it.downTo, 14], [it.upAt, 18]]) {
    if (bt == null || t < bt || t > bt + 1.1) continue; const age = t - bt;
    for (let i = 0; i < n; i++) {
      const vx = (hash(i * 3 + n) - .5) * 520, vy = -(260 + 420 * hash(i * 5 + n)), x = hx + vx * age, y = -40 + vy * age + 1500 * age * age;
      if (y > 10) continue; ctx.globalAlpha = 1 - age / 1.1; ctx.beginPath(); ctx.arc(x, y, 4 + 7 * hash(i + n * 7), 0, TAU); ctx.fillStyle = i % 3 ? OS.sand2 : '#A89878'; ctx.fill();
    }
    ctx.globalAlpha = 1;
  }
  // wake-up ticks (the blue accent)
  if (it.upAt != null && t > it.upAt + .15) {
    const k = S(t - it.upAt - .15, 12), hxu = H[0], hyu = H[1];
    ctx.strokeStyle = C.blue; ctx.lineCap = 'round'; ctx.lineWidth = 9; ctx.globalAlpha = k;
    for (const a of [-2.3, -1.6, -.9]) { ctx.beginPath(); ctx.moveTo(hxu + Math.cos(a) * 70, hyu + Math.sin(a) * 70); ctx.lineTo(hxu + Math.cos(a) * (70 + 44 * k), hyu + Math.sin(a) * (70 + 44 * k)); ctx.stroke(); }
    ctx.globalAlpha = 1;
  }
}

// glass shards of a size x size icon centered on 0: rays from the impact point cut by 3 jittered rings, each shard with
// an outward velocity (faster near the impact), an upward kick and a spin. Deterministic per seed.
function shards(size, hit, n, seed) {
  const h = size / 2, ix = hit[0] * h, iy = hit[1] * h, rings = [size * .28, size * .62, size * 1.6], rnd = i => hash(i * 7.13 + seed * 31.7);
  const ang = Array.from({ length: n }, (_, i) => (i + .5 * (rnd(i) - .5)) / n * TAU);
  const pt = (r, i) => { const j = ((i % n) + n) % n, rj = r * (.82 + .36 * rnd(j * 3 + r)); return [ix + Math.cos(ang[j] + (i >= n ? TAU : 0)) * rj, iy + Math.sin(ang[j] + (i >= n ? TAU : 0)) * rj]; };
  const out = [];
  for (let ri = 0; ri < rings.length; ri++) for (let i = 0; i < n; i++) {
    const r0 = ri ? rings[ri - 1] : 0, r1 = rings[ri], poly = ri ? [pt(r0, i), pt(r1, i), pt(r1, i + 1), pt(r0, i + 1)] : [[ix, iy], pt(r1, i), pt(r1, i + 1)];
    const path = new Path2D(); poly.forEach(([x, y], k) => path[k ? 'lineTo' : 'moveTo'](x, y)); path.closePath();
    const cx = poly.reduce((a, p) => a + p[0], 0) / poly.length, cy = poly.reduce((a, p) => a + p[1], 0) / poly.length;
    const dx = cx - ix, dy = cy - iy, d = Math.hypot(dx, dy) || 1, sp = (1500 + 1100 * rnd(ri * n + i + 50)) / (1 + d / size);
    out.push({ path, cx: clamp(cx, -h, h), cy: clamp(cy, -h, h), vx: dx / d * sp, vy: dy / d * sp - 520 - 380 * rnd(i + 90), w: (rnd(i + ri * 17 + 7) - .5) * 9 });
  }
  return out;
}
function logoAt(R, ctx, src, cx, cy, size, gray) {   // real app icon centered on (cx, cy), rounded like an app icon
  const im = R?.img('/p/' + src); if (!im) return;
  const flat = logoFinish() === 'flat';
  if (!flat) lift(ctx, cx - size / 2, cy - size / 2, size, size, size * .22, size > 100 ? 1 : .35);
  ctx.save(); ctx.beginPath(); ctx.roundRect(cx - size / 2, cy - size / 2, size, size, size * .22); ctx.clip();
  if (gray) ctx.filter = `grayscale(${gray})`; ctx.imageSmoothingQuality = 'high'; ctx.drawImage(im, cx - size / 2, cy - size / 2, size, size); ctx.restore();
  if (flat) { ctx.beginPath(); ctx.roundRect(cx - size / 2, cy - size / 2, size, size, size * .22); ctx.strokeStyle = C.line; ctx.lineWidth = Math.max(1.5, size / 90); ctx.stroke(); }
}
const smoother = x => x <= 0 ? 0 : x >= 1 ? 1 : x * x * x * (x * (x * 6 - 15) + 10);
function drawItem(ctx, it, t, R) {
  const f = DRAW[it.k]; if (!f) return;
  // morph: the item (a screen) grows out of the previous scene's media rect instead of rising in (shared-element move)
  const mo = it._morph, mq = mo ? smoother(seg(t, mo.at, mo.at + (it.morphDur ?? .62))) : 1, mr = mo && mq < 1 ? mo.rect(R) : null;
  // cut: in and out on the frame (badges that follow hard camera cuts); still: never translates on enter or exit
  const p = mr || mo && t >= mo.at ? 1 : it.shown || it.cut ? +(t >= it.at) : S(t - it.at, it.w8 || 13), out = it.to == null ? 0 : it.cut ? +(t >= it.to) : leave(t - it.to);
  if (mo && t < mo.at) return;
  const a = Math.min(1, p * 1.35) * (1 - out); if (a <= .002) return;
  let [x, y] = it.posKeys ? track(t, it.posKeys, it.posW || 10) : [it.x ?? W / 2, it.y ?? 600];
  if (mr) {   // rect lerp: center, size and radius from the source rect to the item's own
    const w = it.w || 900, h = it.h || 620;
    x = lerp(mr[0] + mr[2] / 2, x, mq); y = lerp(mr[1] + mr[3] / 2, y, mq);
    it = { ...it, w: lerp(mr[2], w, mq), h: lerp(mr[3], h, mq), r: lerp(mo.r ?? 22, it.r ?? 30, mq), lit: mq };
  }
  const sc = (it.scaleKeys ? track(t, it.scaleKeys, it.posW || 10) : 1) * (it.pop != null ? lerp(it.pop, 1, p) : 1), dim = it.dimAt != null ? S(t - it.dimAt, 12) : 0;
  const rot = (it.rotKeys ? track(t, it.rotKeys, it.posW || 10) : it.k !== 'stamp' ? it.rot || 0 : 0) + (it.spin || 0) * (1 - p);
  ctx.save(); ctx.globalAlpha *= a * (1 - .62 * dim);
  const bare = it.strikeAt != null && it.k === 'text' && !String(it.text ?? '').trim();   // strike-only item: never rises in
  if (it.still) ctx.translate(x, y);
  else ctx.translate(x + (it.dx || 0) * (1 - p), y + (it.rise ?? (bare ? 0 : 40)) * (1 - p) - 28 * out * out);   // exits lift away, accelerating
  if (rot) ctx.rotate(rot);
  if (sc !== 1) ctx.scale(sc, sc);
  f(ctx, it, t, R);
  if (it.strikeAt != null) { const q = E.io(seg(t, it.strikeAt, it.strikeAt + .35)), sw = it.strikeW || 400; if (q > .002) {
    // the drawn part is the first q of the final curve (de Casteljau), so the stroke draws left to right and never bends
    const x0 = -sw / 2, y0 = 6, x1 = 0, y1 = -6, x2 = sw / 2, y2 = -2, u = 1 - q;
    ctx.beginPath(); ctx.moveTo(x0, y0); ctx.quadraticCurveTo(x0 + (x1 - x0) * q, y0 + (y1 - y0) * q, u * u * x0 + 2 * u * q * x1 + q * q * x2, u * u * y0 + 2 * u * q * y1 + q * q * y2);
    stroke(ctx, col(it.strikeColor || 'blue'), 9); ctx.stroke(); } }
  ctx.restore();
}

// Entrance times, resolved once per board (times are short seconds). The choreography rules live here so every spec
// gets them for free:
//   - gate: after a previous scene's exit (s._gate, set by linkScenes), nothing enters before the old beat is mostly gone.
//   - counters enter with their count (countFrom - .12), never parked on "0" while the voice has not said the number;
//     hold: true keeps the authored entrance.
//   - same slot: an item entering where another one just left (within .6 s, |dx| < 300, |dy| < 90) waits for it to be
//     gone (to + .24, leave() lasts .26 s), so swaps read as one leaves, the next arrives, never two values stacked
//     in a crossfade. slot: false opts an item out.
const SLOT = .24;
const slotXY = it => it.posKeys ? it.posKeys[0][1] : [it.x ?? W / 2, it.y ?? 600];
function boardItems(s) {
  if (s._items) return s._items;
  const items = s.items.map(it => {
    let at = (it.at ?? s.from) - (it.pre ?? 0);
    if (it.k === 'counter' && !it.hold && it.countFrom != null && it.countFrom - at > .3) at = it.countFrom - .12;
    if (!it._morph && s._gate != null) at = Math.max(at, s._gate);
    return { ...it, at };
  });
  for (const b of items) for (const a of items) {
    if (a === b || a.to == null || b._morph || b.slot === false) continue;
    const [ax, ay] = slotXY(a), [bx, by] = slotXY(b);
    if (b.at > a.to - .3 && b.at < a.to + .6 && Math.abs(ax - bx) < 300 && Math.abs(ay - by) < 90) b.at = Math.max(b.at, a.to + SLOT);
  }
  return (s._items = items);
}

// slow push-in over the board's life, so a held beat never sits still (default 2.5% on boards of 3 s and more; push: 0 = off)
const boardEnd = (R, s) => s.to ?? R.tl?.duration ?? s.from + 4;
const boardPush = (R, s) => s.push ?? (boardEnd(R, s) - s.from >= 3 ? .025 : 0);
const board = {
  zooms: (R, s) => boardPush(R, s) > 0 && !boardItems(s).some(it => it.k === 'glass'),   // glass samples the frame under it: plain transform
  draw(R, s, t) {
    const { ctx } = R, out = s.to == null ? 0 : s.hard ? +(t >= s.to) : leave(t - s.to), items = boardItems(s);
    alpha(ctx, 1 - out, () => {
      if (s.outDx) ctx.translate(s.outDx * out * out, 0); else ctx.translate(0, -36 * out * out);   // outDx: whip out sideways
      const end = boardEnd(R, s), push = boardPush(R, s);
      if (push) {
        const [px, py] = s.pushAt || [W / 2, 700], k = 1 + push * clamp((t - s.from) / Math.max(.5, end - s.from));
        zoomAt(ctx, k, px, py);
      }
      for (const it of items) drawItem(ctx, it, t, R); });
  },
};

export const LIFE = { board };
