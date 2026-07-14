// Offline SVG collision checker (no browser needed) — use when a headless/browser checker isn't
// available. Static analysis: reads the HTML, extracts <svg>, regexes out rect/circle/text/line/path,
// computes geometry by hand.
// Limitation: text width is ESTIMATED (not measured against a real font like a browser would) →
// the "text overlap" warning can be off and needs an eyeball check; but arrow gaps / box-overlap /
// viewBox overflow are EXACT (they come straight from the numeric coordinates).
const fs = require('fs');

const file = process.argv[2];
if (!file) { console.error('Usage: node check-svg.js <path-to-html>'); process.exit(1); }
const html = fs.readFileSync(file, 'utf8');
const svgMatch = html.match(/<svg[^>]*viewBox="([^"]+)"[\s\S]*?<\/svg>/);
if (!svgMatch) { console.error('No <svg> found'); process.exit(1); }
const svgBody = svgMatch[0];
const [vx, vy, vw, vh] = svgMatch[1].trim().split(/\s+/).map(Number);

function attrs(tag) {
  const out = {};
  const re = /([a-zA-Z0-9-]+)="([^"]*)"/g;
  let m;
  while ((m = re.exec(tag))) out[m[1]] = m[2];
  return out;
}

// --- Extract rects (excludes defs/markers/regions by the box filter below) ---
const rects = [];
for (const m of svgBody.matchAll(/<rect\b[^>]*\/?>/g)) {
  const a = attrs(m[0]);
  if (a.x === undefined || a.width === undefined) continue;
  rects.push({ x: +a.x, y: +a.y, w: +a.width, h: +a.height, fill: a.fill, stroke: a.stroke, raw: m[0], idx: m.index });
}
// A "box" = a rect with fill != 'none' and width >= 60 (matches the browser checker's criterion)
const boxes = rects.filter(r => r.fill && r.fill !== 'none' && r.w >= 60);

// --- Extract circles (round badges) ---
const circles = [];
for (const m of svgBody.matchAll(/<circle\b[^>]*\/?>/g)) {
  const a = attrs(m[0]);
  if (a.cx === undefined) continue;
  circles.push({ cx: +a.cx, cy: +a.cy, r: +a.r, fill: a.fill });
}

// --- Extract text (bbox estimated from text-anchor + font-size) ---
const texts = [];
for (const m of svgBody.matchAll(/<text\b([^>]*)>([^<]*)<\/text>/g)) {
  const a = attrs('<text ' + m[1] + '>');
  const content = m[2].replace(/&amp;/g, '&').replace(/&gt;/g, '>').replace(/&lt;/g, '<').trim();
  if (!content) continue;
  const fs_ = +(a['font-size'] || 10);
  const anchor = a['text-anchor'] || 'start';
  // Estimate: an average accented Latin character is ~0.56em wide (conservative — more likely to
  // false-positive than to miss a real overlap)
  const w = content.length * fs_ * 0.56;
  const h = fs_ * 1.25;
  let x0 = +a.x;
  if (anchor === 'middle') x0 = +a.x - w / 2;
  else if (anchor === 'end') x0 = +a.x - w;
  const y0 = +a.y - h * 0.8; // baseline → approximate top
  // KNOWN LIMITATION: does not account for transform="rotate(...)" — a vertically rotated label
  // (running along a corridor, rotate(-90 ...)) gets estimated with a HORIZONTAL bbox like normal
  // text, which usually reports a FALSE "viewBox overflow" / "text overlap".
  // If an error involves a rotated text element, eyeball it before touching any coordinates —
  // don't trust the blind estimator there.
  texts.push({ content, x: x0, y: y0, w, h, x1: x0 + w, y1: y0 + h, rotated: !!a.transform });
}

// --- Extract lines/paths with marker-end (arrows) to compute their endpoint ---
function pathEndpoint(d) {
  const toks = d.match(/[MLA][^MLA]*/g) || [];
  let x = 0, y = 0;
  for (const t of toks) {
    const cmd = t[0];
    const nums = t.slice(1).trim().split(/[\s,]+/).filter(Boolean).map(Number);
    if (cmd === 'M' || cmd === 'L') { x = nums[nums.length - 2]; y = nums[nums.length - 1]; }
    else if (cmd === 'A') { x = nums[5]; y = nums[6]; }
  }
  return { x, y };
}
const arrows = [];
for (const m of svgBody.matchAll(/<line\b[^>]*\/>/g)) {
  const a = attrs(m[0]);
  if (!a['marker-end']) continue;
  arrows.push({ x: +a.x2, y: +a.y2, stroke: a.stroke, raw: m[0] });
}
for (const m of svgBody.matchAll(/<path\b[^>]*\/>/g)) {
  const a = attrs(m[0]);
  if (!a['marker-end'] || !a.d) continue;
  const p = pathEndpoint(a.d);
  arrows.push({ x: p.x, y: p.y, stroke: a.stroke, raw: m[0] });
}

const errors = [], warnings = [];

// 1. BOX OVERLAPS BOX
for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) {
  const a = boxes[i], b = boxes[j];
  if (!(a.x + a.w < b.x || b.x + b.w < a.x || a.y + a.h < b.y || b.y + b.h < a.y)) {
    errors.push({ type: 'BOX OVERLAPS BOX', a: `(${a.x},${a.y})`, b: `(${b.x},${b.y})` });
  }
}

// 2. TEXT MAY OVERLAP TEXT (estimated — treated as a warning, not a hard error, since width is a guess)
for (let i = 0; i < texts.length; i++) for (let j = i + 1; j < texts.length; j++) {
  const a = texts[i], b = texts[j];
  const inset = 1.5;
  if (!(a.x1 - inset < b.x || b.x1 - inset < a.x || a.y1 - inset < b.y || b.y1 - inset < a.y)) {
    warnings.push({ type: 'TEXT MAY OVERLAP (estimated)', a: a.content, b: b.content, at: `${Math.round(a.x)},${Math.round(a.y)}` });
  }
}

// 3. ARROW TOO CLOSE TO / INSIDE A BOX, or FLOATING (no box nearby) — EXACT numeric distance
for (const ar of arrows) {
  let nearestGap = Infinity, nearestBox = null, inside = false;
  for (const b of boxes) {
    const isIn = ar.x > b.x && ar.x < b.x + b.w && ar.y > b.y && ar.y < b.y + b.h;
    const dx = Math.max(b.x - ar.x, ar.x - (b.x + b.w), 0);
    const dy = Math.max(b.y - ar.y, ar.y - (b.y + b.h), 0);
    const gap = Math.hypot(dx, dy);
    if (gap < nearestGap) { nearestGap = gap; nearestBox = `(${b.x},${b.y},${b.w}×${b.h})`; inside = isIn; }
  }
  if (nearestGap < Infinity) {
    if (inside || nearestGap < 6) {
      errors.push({ type: 'ARROW TOO CLOSE TO / INSIDE BOX', box: nearestBox, gap: inside ? 'inside the box' : Math.round(nearestGap) + 'px (need ~8)', at: `${Math.round(ar.x)},${Math.round(ar.y)}`, color: ar.stroke });
    } else if (nearestGap > 60) {
      errors.push({ type: 'FLOATING ARROW (touches no box)', nearest: nearestBox, distance: Math.round(nearestGap) + 'px', at: `${Math.round(ar.x)},${Math.round(ar.y)}`, color: ar.stroke });
    }
  }
}

// 4. VIEWBOX OVERFLOW — scan every extracted coordinate
let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
for (const r of rects) { minX = Math.min(minX, r.x); minY = Math.min(minY, r.y); maxX = Math.max(maxX, r.x + r.w); maxY = Math.max(maxY, r.y + r.h); }
for (const c of circles) { minX = Math.min(minX, c.cx - c.r); minY = Math.min(minY, c.cy - c.r); maxX = Math.max(maxX, c.cx + c.r); maxY = Math.max(maxY, c.cy + c.r); }
for (const t of texts) { minX = Math.min(minX, t.x); minY = Math.min(minY, t.y); maxX = Math.max(maxX, t.x1); maxY = Math.max(maxY, t.y1); }
if (minX < vx - 2 || minY < vy - 2 || maxX > vx + vw + 2 || maxY > vy + vh + 2) {
  errors.push({ type: 'VIEWBOX OVERFLOW', detail: `content ${Math.round(minX)},${Math.round(minY)} → ${Math.round(maxX)},${Math.round(maxY)} vs viewBox ${vx},${vy} ${vw}×${vh}` });
}

// 5. BOX TOO CLOSE TO REGION BORDER (rect fill=none stroke-dasharray) < 20px — soft warning per the design system
const regions = rects.filter(r => (!r.fill || r.fill === 'none') && /stroke-dasharray/.test(r.raw));
for (const reg of regions) {
  for (const b of boxes) {
    const inside = b.x > reg.x && b.x + b.w < reg.x + reg.w && b.y > reg.y && b.y + b.h < reg.y + reg.h;
    if (!inside) continue;
    const margins = [b.x - reg.x, (reg.x + reg.w) - (b.x + b.w), b.y - reg.y, (reg.y + reg.h) - (b.y + b.h)];
    const minM = Math.min(...margins);
    if (minM < 20) warnings.push({ type: 'BOX TOO CLOSE TO REGION BORDER', box: `(${b.x},${b.y})`, distance: Math.round(minM) + 'px (recommend ≥20)' });
  }
}

console.log(`=== ${file.split('/').pop()} ===`);
console.log(`${errors.length} error(s) to fix · ${warnings.length} warning(s)`);
console.log(`(extracted: ${rects.length} rects, ${boxes.length} large boxes, ${circles.length} circles, ${texts.length} text nodes, ${arrows.length} arrows)`);
if (errors.length) { console.log('\n--- ERRORS ---'); errors.forEach(l => console.log(JSON.stringify(l))); }
if (warnings.length) { console.log('\n--- WARNINGS ---'); warnings.slice(0, 20).forEach(l => console.log(JSON.stringify(l))); }
