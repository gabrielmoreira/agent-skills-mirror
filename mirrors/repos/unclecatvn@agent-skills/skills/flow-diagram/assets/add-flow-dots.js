// Adds a "traveling dot" along every arrow that has marker-end — replaces marching-ants.
// Based on the Kiali/Istio convention (a dot moving along the edge signals traffic) — see
// SKILL.md for the source.
// Run: node add-flow-dots.js <path-to-html>  (overwrites the file in place)
const fs = require('fs');
const file = process.argv[2];
if (!file) { console.error('Usage: node add-flow-dots.js <path-to-html>'); process.exit(1); }
let html = fs.readFileSync(file, 'utf8');

// Re-runnable (idempotent): strip any existing dots first so re-running (e.g. after tweaking
// speed) never doubles them up.
// IMPORTANT: require the tag to be immediately followed by "<circle" (real generated markup has
// zero characters between the g-tag and its first circle). Without this, the match would also
// trigger on any HTML COMMENT that mentions `<g class="flow-dot" data-flow="...">` as prose (e.g.
// the instructional comment in template.html) — the regex would then greedily eat everything up
// to the first REAL </g> below the comment, silently deleting real content. Confirmed by hand: this
// exact bug existed in the original script and was never caught because it had never been run
// against template.html itself before.
html = html.replace(/<g class="flow-dot" data-flow="[^"]*"><circle(?:(?!<\/g>)[\s\S])*<\/g>/g, '');

function attrs(tag) {
  const out = {};
  const re = /([a-zA-Z0-9-]+)="([^"]*)"/g;
  let m;
  while ((m = re.exec(tag))) out[m[1]] = m[2];
  return out;
}

function pathLen(d) {
  const toks = d.match(/[MLA][^MLA]*/g) || [];
  let x = 0, y = 0, len = 0;
  for (const t of toks) {
    const cmd = t[0];
    const nums = t.slice(1).trim().split(/[\s,]+/).filter(Boolean).map(Number);
    if (cmd === 'M') { x = nums[0]; y = nums[1]; }
    else if (cmd === 'L') { const nx = nums[0], ny = nums[1]; len += Math.hypot(nx - x, ny - y); x = nx; y = ny; }
    else if (cmd === 'A') { const nx = nums[5], ny = nums[6]; len += Math.hypot(nx - x, ny - y); x = nx; y = ny; }
  }
  return len;
}

function dotsFor(flow, color, d, len) {
  // Speed ≈130px/s (well slower than the old marching-ants) — slow enough for the eye to track
  // the dot without it whipping past.
  const dur = Math.min(3.5, Math.max(1.2, len / 130)).toFixed(2);
  const n = 2;
  let out = `<g class="flow-dot" data-flow="${flow}">`;
  for (let i = 0; i < n; i++) {
    const begin = (dur / n * i).toFixed(2);
    out += `<circle r="3.4" fill="${color}"><animateMotion dur="${dur}s" begin="${begin}s" repeatCount="indefinite" path="${d}"/></circle>`;
  }
  out += `</g>`;
  return out;
}

let count = 0;

// <line data-flow="..." ... marker-end="...">
html = html.replace(/<line\b[^>]*marker-end="[^"]*"[^>]*\/>/g, (tag) => {
  const a = attrs(tag);
  if (!a['data-flow']) return tag;
  const d = `M${a.x1},${a.y1} L${a.x2},${a.y2}`;
  const len = Math.hypot(+a.x2 - +a.x1, +a.y2 - +a.y1);
  count++;
  return tag + dotsFor(a['data-flow'], a.stroke, d, len);
});

// <path data-flow="..." ... marker-end="...">
html = html.replace(/<path\b[^>]*marker-end="[^"]*"[^>]*\/>/g, (tag) => {
  const a = attrs(tag);
  if (!a['data-flow'] || !a.d) return tag;
  const len = pathLen(a.d);
  count++;
  return tag + dotsFor(a['data-flow'], a.stroke, a.d, len);
});

fs.writeFileSync(file, html);
console.log(`${file}: added traveling dots to ${count} arrow(s)`);
