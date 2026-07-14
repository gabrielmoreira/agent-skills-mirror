// Pulls each arrowhead out to ~8px from the box edge (the skill's current convention) — for
// arrows drawn under an older, tighter convention. Does NOT change the line's direction (only
// slides the endpoint further out along the exact vector of its final segment, away from the
// box). Use on legacy files that don't yet follow the 8px rule; run this ONCE before generating
// dots/pings.
const fs = require('fs');
const file = process.argv[2];
if (!file) { console.error('Usage: node fix-arrow-gaps.js <file.html>'); process.exit(1); }
let html = fs.readFileSync(file, 'utf8');

function attrs(tag) {
  const out = {}; const re = /([a-zA-Z0-9-]+)="([^"]*)"/g; let m;
  while ((m = re.exec(tag))) out[m[1]] = m[2];
  return out;
}

// Boxes: from <g data-flows="..."><rect .../>...
const boxes = [];
for (const m of html.matchAll(/<g data-flows="[^"]*">\s*<rect\b[^>]*\/>/g)) {
  const rm = m[0].match(/<rect\b[^>]*\/>/);
  const a = attrs(rm[0]);
  if (a.x === undefined) continue;
  boxes.push({ x: +a.x, y: +a.y, w: +a.width, h: +a.height });
}
function nearestGap(px, py) {
  let best = null, bestGap = Infinity;
  for (const b of boxes) {
    const dx = Math.max(b.x - px, px - (b.x + b.w), 0), dy = Math.max(b.y - py, py - (b.y + b.h), 0);
    const gap = Math.hypot(dx, dy);
    if (gap < bestGap) { bestGap = gap; best = b; }
  }
  return bestGap;
}
const TARGET = 8;
let fixedCount = 0;

// <line ... x1 y1 x2 y2 ... marker-end>
html = html.replace(/<line\b[^>]*marker-end="[^"]*"[^>]*\/>/g, (tag) => {
  const a = attrs(tag);
  if (!a.x1) return tag;
  const x1 = +a.x1, y1 = +a.y1, x2 = +a.x2, y2 = +a.y2;
  const gap = nearestGap(x2, y2);
  if (gap >= 6 || gap === Infinity) return tag; // already compliant, or no box nearby — skip
  const dx = x2 - x1, dy = y2 - y1, len = Math.hypot(dx, dy);
  if (!len) return tag;
  const need = TARGET - gap; // how much further back to pull, opposite the travel direction (toward x1,y1)
  const nx2 = +(x2 - (dx / len) * need).toFixed(2);
  const ny2 = +(y2 - (dy / len) * need).toFixed(2);
  fixedCount++;
  return tag.replace(`x2="${a.x2}"`, `x2="${nx2}"`).replace(`y2="${a.y2}"`, `y2="${ny2}"`);
});

// <path ... d="...L lastX,lastY" ... marker-end>
html = html.replace(/<path\b[^>]*marker-end="[^"]*"[^>]*\/>/g, (tag) => {
  const a = attrs(tag);
  if (!a.d) return tag;
  const toks = a.d.match(/[MLA][^MLA]*/g);
  if (!toks || toks.length < 2) return tag;
  const last = toks[toks.length - 1];
  const cmd = last[0];
  const nums = last.slice(1).trim().split(/[\s,]+/).map(Number);
  const x2 = nums[nums.length - 2], y2 = nums[nums.length - 1];
  const gap = nearestGap(x2, y2);
  if (gap >= 6 || gap === Infinity) return tag;
  // Take the previous point to get the direction — for an A (arc) command, use the point right
  // before the final command.
  const prev = toks[toks.length - 2];
  const prevNums = prev.slice(1).trim().split(/[\s,]+/).map(Number);
  const x1 = prevNums[prevNums.length - 2], y1 = prevNums[prevNums.length - 1];
  const dx = x2 - x1, dy = y2 - y1, len = Math.hypot(dx, dy);
  if (!len) return tag;
  const need = TARGET - gap;
  const nx2 = +(x2 - (dx / len) * need).toFixed(2);
  const ny2 = +(y2 - (dy / len) * need).toFixed(2);
  nums[nums.length - 2] = nx2; nums[nums.length - 1] = ny2;
  const newLast = cmd + nums.join(',');
  const newD = [...toks.slice(0, -1), newLast].join(' ');
  fixedCount++;
  return tag.replace(`d="${a.d}"`, `d="${newD}"`);
});

fs.writeFileSync(file, html);
console.log(`${file}: pulled ${fixedCount} arrowhead(s) out to ~8px`);
