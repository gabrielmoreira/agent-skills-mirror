// v3 — a gentle "breathing" ping ring at each arrow's DESTINATION box (replaces an earlier v1 that
// pulsed hard and made eyes tired after a while).
// v2→v3: the ring's color now comes from the DESTINATION BOX'S OWN BORDER (not the incoming
// arrow's color) — a neutral gray-bordered box gets a soft gray ring, a focal box with a blue/red
// border gets a ring in that same color — consistent with the design system's "role shown via
// border" rule, without inventing a new color layer just for this animation.
// Uses ONE SHARED CSS @keyframes (transform:scale, ease-out, peak opacity only 0.35, with a rest
// period) instead of every box computing its own dur/begin via SMIL — easier on the eyes, and the
// generated markup is much shorter too.
// Placed as a CHILD of the destination box's <g data-flows> so it follows the box's transform
// automatically when the box is dragged.
const fs = require('fs');
const file = process.argv[2];
if (!file) { console.error('Usage: node add-flow-ping.js <file.html>'); process.exit(1); }
let html = fs.readFileSync(file, 'utf8');

// Strip any existing ping markup before regenerating — idempotent, safe to re-run.
// Same defensive fix as add-flow-dots.js: require immediate adjacency to "<rect" so this can
// never accidentally match an HTML comment that happens to mention `<g class="flow-ping"...>` as
// prose (real generated markup always has zero characters between the g-tag and its rect).
html = html.replace(/<g class="flow-ping" data-flow="[^"]*"><rect(?:(?!<\/g>)[\s\S])*<\/g>/g, '');

function attrs(tag) {
  const out = {}; const re = /([a-zA-Z0-9-]+)="([^"]*)"/g; let m;
  while ((m = re.exec(tag))) out[m[1]] = m[2];
  return out;
}
function pathEndpoint(d) {
  const toks = d.match(/[MLA][^MLA]*/g) || []; let x = 0, y = 0;
  for (const t of toks) {
    const cmd = t[0]; const nums = t.slice(1).trim().split(/[\s,]+/).filter(Boolean).map(Number);
    if (cmd === 'M' || cmd === 'L') { x = nums[nums.length - 2]; y = nums[nums.length - 1]; }
    else if (cmd === 'A') { x = nums[5]; y = nums[6]; }
  }
  return { x, y };
}

// 1. Collect boxes: a <g data-flows="..."> that directly contains 1 <rect> (no nested <g> inside).
const boxes = [];
const GBOX_RE = /<g data-flows="([^"]*)">((?:(?!<\/g>)[\s\S])*?)<\/g>/g;
let gm;
while ((gm = GBOX_RE.exec(html))) {
  const inner = gm[2];
  const rm = inner.match(/<rect\b[^>]*\/>/);
  if (!rm) continue;
  const a = attrs(rm[0]);
  if (a.x === undefined || a.width === undefined) continue;
  boxes.push({
    x: +a.x, y: +a.y, w: +a.width, h: +a.height, rx: a.rx || '10', stroke: a.stroke || '#d1d5db',
    closeTagIdx: gm.index + gm[0].length - 4,
    pings: [],
  });
}

// 2. For every arrow, find the nearest box to its END point within a ~14-unit threshold and
//    assign it one ping ring, COLORED FROM THE DESTINATION BOX'S OWN BORDER (not the arrow) —
//    see the file-header note.
const EDGE_THRESH = 14;
let count = 0;
function assignPing(ex, ey, flow) {
  let best = null, bestGap = EDGE_THRESH;
  for (const b of boxes) {
    const dx = Math.max(b.x - ex, ex - (b.x + b.w), 0), dy = Math.max(b.y - ey, ey - (b.y + b.h), 0);
    const gap = Math.hypot(dx, dy);
    if (gap < bestGap) { bestGap = gap; best = b; }
  }
  if (!best) return;
  best.pings.push(
    `<g class="flow-ping" data-flow="${flow}"><rect class="flow-ping-ring" x="${best.x}" y="${best.y}" width="${best.w}" height="${best.h}" rx="${best.rx}" fill="none" stroke="${best.stroke}" stroke-width="1.5"/></g>`
  );
  count++;
}

for (const m of html.matchAll(/<line\b[^>]*marker-end="[^"]*"[^>]*\/>/g)) {
  const a = attrs(m[0]);
  if (!a['data-flow']) continue;
  assignPing(+a.x2, +a.y2, a['data-flow']);
}
for (const m of html.matchAll(/<path\b[^>]*marker-end="[^"]*"[^>]*\/>/g)) {
  const a = attrs(m[0]);
  if (!a['data-flow'] || !a.d) continue;
  const p = pathEndpoint(a.d);
  assignPing(p.x, p.y, a['data-flow']);
}

// 3. Insert from the END of the string toward the START so earlier insertion points don't shift.
boxes.sort((a, b) => b.closeTagIdx - a.closeTagIdx);
for (const b of boxes) {
  if (!b.pings.length) continue;
  html = html.slice(0, b.closeTagIdx) + b.pings.join('') + html.slice(b.closeTagIdx);
}

fs.writeFileSync(file, html);
console.log(`${file}: added a ping ring (v3, border-matched color) to ${count} arrow(s) across ${boxes.filter(b => b.pings.length).length} destination box(es)`);
