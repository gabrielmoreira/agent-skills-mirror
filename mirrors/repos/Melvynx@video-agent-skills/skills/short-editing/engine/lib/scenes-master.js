// Masterclass scene: the creator's masterclass card (ported from the adMaster ads of short-tella-cmuqep / short-monteur-arc-fleche),
// reusable by any short. Same contract as scenes.js, times already mapped to SHORT time.
//   masterCard  a sheet with a dark head (eyebrow, title, logo + subline, round avatar, duration badge), the lessons, then
//               the bottom row that tells the story of the CTA, every step optional and keyed on a word:
//               arrowAt   "Premier lien sous la vidéo" + an arrow down out of the card
//               btnAt     the row becomes the blue button, a cursor flies in (cursorFrom [x, y])
//               clickAt   the cursor presses it, the button runs "Inscription" with a filling bar
//               unlockAt  "Accès débloqué" with a drawn check
//               playAt..playTo  the masterclass plays: a progress bar and timer in the head, the current lesson lights
//                         up and every finished one gets its check
//               {from, to, pre, y 236, eyebrow, title, sub, logo, avatar (image path, never the creator's real face in
//                faceless), badge, badgeAt, lessons [[label, 'N min']], chaptersFrom, chapterStep, linkText, btnText,
//                busyText, unlockText, total (seconds shown by the timer, default sum of the lesson minutes), outDx}
import { C, W, clamp, lerp, seg, E, S, leave, press, track, sheet, shadow, text, measure, midBase, chip, cursor, cover, checkIcon } from './kit.js';

const TAU = Math.PI * 2, MONO = 'JetBrains Mono';
const hex = c => [1, 3, 5].map(i => parseInt(c.slice(i, i + 2), 16));
const mix = (a, b, p) => { const x = hex(a), y = hex(b); return `rgb(${x.map((v, i) => Math.round(lerp(v, y[i], clamp(p)))).join(',')})`; };
function alpha(ctx, a, fn) { if (a <= .002) return; ctx.save(); ctx.globalAlpha *= a; fn(); ctx.restore(); }
const live = (s, t) => t >= s.from - (s.pre || 0) - 1.5 && t <= (s.to ?? 1e9) + 1;
const at = v => v ?? 1e9;
const mmss = x => `${Math.floor(x / 60)}:${String(Math.floor(x % 60)).padStart(2, '0')}`;
function logoImg(R, ctx, src, x, y, size, r = size * .22) {
  const im = R.img('/p/' + src); if (!im) return;
  const k = Math.min(size / im.width, size / im.height), w = im.width * k, h = im.height * k;
  ctx.save(); ctx.beginPath(); ctx.roundRect(x, y, size, size, r); ctx.clip();
  ctx.imageSmoothingQuality = 'high'; ctx.drawImage(im, x + (size - w) / 2, y + (size - h) / 2, w, h); ctx.restore();
}
function arrow(ctx, x, y0, y1, p, o = {}) {
  if (p <= .002) return; const y = lerp(y0, y1, E.out(p)), hl = o.head || 24;
  ctx.save(); ctx.strokeStyle = o.color || C.blue; ctx.lineWidth = o.lw || 9; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  ctx.beginPath(); ctx.moveTo(x, y0); ctx.lineTo(x, y); ctx.moveTo(x - hl * .8, y - hl); ctx.lineTo(x, y); ctx.lineTo(x + hl * .8, y - hl); ctx.stroke(); ctx.restore();
}
function spinner(ctx, cx, cy, r, t, col) {
  ctx.save(); ctx.strokeStyle = col; ctx.lineWidth = r * .32; ctx.lineCap = 'round';
  const a = t * 7.5; ctx.beginPath(); ctx.arc(cx, cy, r, a, a + 4.2); ctx.stroke(); ctx.restore();
}

const masterCard = {
  needs(s, t) { return live(s, t) ? [s.logo, s.avatar].filter(Boolean).map(p => '/p/' + p) : []; },
  draw(R, s, t) {
    const { ctx } = R, x = 60, w = 960, y = s.y ?? 236, h = 900;
    const out = s.to != null ? leave(t - s.to) : 0, pin = S(t - s.from + (s.pre || 0), 11);
    if (pin <= .002 || out >= 1) return;
    const lessons = s.lessons || [], total = s.total ?? lessons.reduce((a, [, d]) => a + parseFloat(d) * 60, 0);
    // play: 0..1 across playAt..playTo, the lesson boundaries come from their durations
    const pT = s.playTo ?? at(s.playAt) + 4, play = s.playAt != null ? clamp((t - s.playAt) / (pT - s.playAt)) : 0, playing = t >= at(s.playAt);
    const bounds = []; let acc = 0; for (const [, d] of lessons) { bounds.push([acc / total, (acc += parseFloat(d) * 60) / total]); }
    const cur = playing ? Math.max(0, bounds.findIndex(([a, b]) => play >= a && play < b)) : -1, curI = playing && play >= 1 ? lessons.length - 1 : cur;
    alpha(ctx, (1 - out) * Math.min(1, pin * 1.35), () => {
      ctx.translate((s.outDx ?? -820) * out * out, 70 * (1 - pin));
      sheet(ctx, x, y, w, h, 42, { elev: 1.5 });
      // ---- head panel
      const hx = x + 16, hy = y + 16, hw = w - 32, hh = 300;
      ctx.beginPath(); ctx.roundRect(hx, hy, hw, hh, 30); ctx.fillStyle = C.ink; ctx.fill();
      text(ctx, s.eyebrow || 'MASTERCLASS', hx + 44, hy + 74, { size: 32, weight: 700, ls: 3, color: '#7FB6FF', fam: MONO });
      // the title shrinks to fit the room left of the avatar, never slides under it
      const title = s.title || 'Ton monteur IA', room = hw - 44 - (s.avatar ? 112 + 76 + 30 : 44), tw = measure(ctx, title, 78, 800, -2.4);
      const ts = tw > room ? Math.floor(78 * room / tw) : 78;
      text(ctx, title, hx + 44, hy + 166, { size: ts, weight: 800, ls: -2.4 * ts / 78, color: C.white });
      if (s.logo) logoImg(R, ctx, s.logo, hx + 44, hy + 200, 50, 12);
      if (s.sub) text(ctx, s.sub, hx + (s.logo ? 110 : 44), midBase(hy + 225, 36), { size: 36, weight: 600, color: '#A9ABB2' });
      // avatar, with a blue ring that closes while the masterclass plays
      const ax = hx + hw - 112, ay = hy + 122, ar = 76, im = s.avatar && R.img('/p/' + s.avatar);
      ctx.save(); ctx.beginPath(); ctx.arc(ax, ay, ar, 0, TAU); ctx.fillStyle = '#2A2D35'; ctx.fill(); ctx.clip();
      if (im) cover(ctx, im, ax - ar, ay - ar, ar * 2, ar * 2, 0, [.5, .4]); ctx.restore();
      ctx.save(); ctx.beginPath(); ctx.arc(ax, ay, ar + 2, 0, TAU); ctx.lineWidth = 5; ctx.strokeStyle = '#FFFFFF'; ctx.stroke();
      if (playing) { ctx.beginPath(); ctx.arc(ax, ay, ar + 12, -Math.PI / 2, -Math.PI / 2 + TAU * play); ctx.lineWidth = 9; ctx.lineCap = 'round'; ctx.strokeStyle = C.blue; ctx.stroke(); }
      ctx.restore();
      const bp = S(t - at(s.badgeAt), 11);
      if (bp > .002) { ctx.save(); ctx.translate(ax, hy + hh - 8); ctx.rotate(-.05); chip(ctx, 0, 0, s.badge || '10 min', { size: 42, fill: C.blue, color: C.white, scale: 1 + .3 * (1 - bp), alpha: Math.min(1, bp * 1.5), elev: 1 }); ctx.restore(); }
      // play bar + timer along the bottom of the head
      const pp = S(t - at(s.playAt), 12);
      if (pp > .002) alpha(ctx, Math.min(1, pp * 1.4), () => {
        const bx = hx + 44, bw = hw - 400, byy = hy + hh - 30;
        ctx.beginPath(); ctx.roundRect(bx, byy - 5, bw, 10, 5); ctx.fillStyle = '#3A3D45'; ctx.fill();
        ctx.beginPath(); ctx.roundRect(bx, byy - 5, Math.max(10, bw * play), 10, 5); ctx.fillStyle = C.blue; ctx.fill();
        ctx.beginPath(); ctx.arc(bx + bw * play, byy, 13, 0, TAU); ctx.fillStyle = C.white; ctx.fill();
        text(ctx, mmss(total * play), bx + bw + 24, midBase(byy, 30), { size: 30, weight: 700, color: C.white, fam: MONO });
      });
      // ---- lessons
      const top = y + 392, lh = 100;
      if (curI >= 0) {   // the current lesson's tint glides from row to row
        const ry = track(t, [[0, top], ...bounds.slice(1).map(([a], i) => [s.playAt + a * (pT - s.playAt), top + (i + 1) * lh])], 16);
        const hp = S(t - s.playAt, 12);
        ctx.save(); ctx.globalAlpha *= hp; ctx.beginPath(); ctx.roundRect(x + 24, ry - lh / 2 + 6, (w - 48) * E.out(hp), lh - 12, 22); ctx.fillStyle = C.tint; ctx.fill(); ctx.restore();
      }
      lessons.forEach(([lab, dur], i) => {
        const p = S(t - (at(s.chaptersFrom) + i * (s.chapterStep || .3)), 14), ry = top + i * lh;
        const hot = playing && i === curI ? 1 : 0, doneAt = playing && i < curI ? s.playAt + bounds[i][1] * (pT - s.playAt) : null;
        alpha(ctx, Math.min(1, p * 1.4), () => {
          ctx.translate(40 * (1 - p), 0);
          if (i) { ctx.fillStyle = C.line; ctx.fillRect(x + 48, ry - lh / 2, w - 96, 2); }
          if (doneAt != null) checkIcon(ctx, x + 74, ry, 38, C.blue, E.out(seg(t, doneAt, doneAt + .3)), 6.5);
          else text(ctx, String(i + 1).padStart(2, '0'), x + 56, midBase(ry, 36), { size: 36, weight: 700, color: hot ? C.blue : C.ink3, fam: MONO });
          text(ctx, lab, x + 140, midBase(ry, 42), { size: 42, weight: 700, ls: -.6, color: hot ? C.blue2 : doneAt != null ? C.ink2 : C.ink });
          text(ctx, dur, x + w - 56, midBase(ry, 34), { size: 34, weight: 500, align: 'right', color: hot ? C.blue2 : C.ink3, fam: MONO });
        });
      });
      // ---- bottom row: link + arrow, then the button that gets clicked
      const by = y + h - 92, bx = x + 40, bw = w - 80, bh = 116, bcx = bx + bw / 2;
      ctx.fillStyle = C.line; ctx.fillRect(x + 48, by - 82, w - 96, 2);
      const lp = S(t - at(s.arrowAt), 12), btn = S(t - at(s.btnAt), 12);
      alpha(ctx, Math.min(1, lp * 1.4) * (1 - btn), () => {
        const lab = s.linkText || 'Premier lien sous la vidéo', tw = measure(ctx, lab, 46, 800, -1);
        text(ctx, lab, bcx - 30, midBase(by, 46), { size: 46, weight: 800, ls: -1, align: 'center' });
        arrow(ctx, bcx - 30 + tw / 2 + 40, by - 34, by + 34, seg(t, at(s.arrowAt) + .08, at(s.arrowAt) + .4));
      });
      if (btn > .002) {
        const pr = press(t, at(s.clickAt), .2), busy = S(t - at(s.clickAt), 16), done = S(t - at(s.unlockAt), 14);
        ctx.save(); ctx.globalAlpha *= Math.min(1, btn * 1.4); ctx.translate(bcx, by); const k = (.94 + .06 * btn) * (1 - .05 * pr); ctx.scale(k, k); ctx.translate(-bcx, -by);
        shadow(ctx, bx, by - bh / 2, bw, bh, bh / 2, 30, .28 * (1 - done), 12);
        ctx.beginPath(); ctx.roundRect(bx, by - bh / 2, bw, bh, bh / 2); ctx.fillStyle = mix(C.blue, '#EDEAE2', done); ctx.fill();
        // "Inscription": the bar fills the button between the click and the unlock
        if (busy > .002 && done < 1) {
          const f = clamp((t - at(s.clickAt)) / Math.max(.3, at(s.unlockAt) - at(s.clickAt)));
          ctx.save(); ctx.beginPath(); ctx.roundRect(bx, by - bh / 2, bw, bh, bh / 2); ctx.clip();
          ctx.globalAlpha *= busy * (1 - done); ctx.fillStyle = C.blue2; ctx.fillRect(bx, by - bh / 2, bw * E.cubic(f), bh); ctx.restore();
        }
        alpha(ctx, 1 - S(t - at(s.clickAt), 40), () => text(ctx, s.btnText || 'Rejoindre la masterclass', bcx, midBase(by, 46), { size: 46, weight: 800, ls: -.8, align: 'center', color: C.white }));
        alpha(ctx, S(t - at(s.clickAt) - .12, 16) * (1 - S(t - at(s.unlockAt), 40)), () => { const lab = s.busyText || 'Inscription', tw = measure(ctx, lab, 46, 800, -.8) + 64;
          spinner(ctx, bcx - tw / 2 + 18, by, 18, t, C.white); text(ctx, lab, bcx - tw / 2 + 64, midBase(by, 46), { size: 46, weight: 800, ls: -.8, color: C.white }); });
        alpha(ctx, S(t - at(s.unlockAt) - .1, 16), () => { const lab = s.unlockText || 'Accès débloqué', tw = measure(ctx, lab, 46, 800, -.8) + 60;
          checkIcon(ctx, bcx - tw / 2 + 18, by, 36, C.blue, E.out(seg(t, at(s.unlockAt) + .06, at(s.unlockAt) + .4)), 6);
          text(ctx, lab, bcx - tw / 2 + 60, midBase(by, 46), { size: 46, weight: 800, ls: -.8 }); });
        ctx.restore();
        // the cursor: flies in from the mascot's side, hesitates, clicks, leaves after the unlock
        const c0 = s.cursorFrom || [W + 80, by + 320], b0 = at(s.btnAt), c1 = at(s.clickAt);
        const [mx, my] = track(t, [[0, c0], [b0 + .2, [bcx + 250, by + 60]], [b0 + .7, [bcx + 170, by + 30]], [c1 - .45, [bcx + 120, by + 18]], [c1 + .1, [bcx + 120, by + 18]], [at(s.unlockAt) + .5, c0]], 9);
        cursor(ctx, mx, my, { alpha: S(t - b0, 10) * (1 - S(t - at(s.unlockAt) - .7, 8)), press: pr });
      }
    });
  },
};

export const MASTER = { masterCard };
