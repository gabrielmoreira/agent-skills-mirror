// Inserts the "drag boxes to rearrange" feature (CSS + button + JS) into a diagram file that
// already uses the template's app shell but doesn't have it yet.
// Idempotent: if #edit-toggle already exists, it does nothing (never inserts it twice).
const fs = require('fs');
const file = process.argv[2];
if (!file) { console.error('Usage: node add-drag-to-rearrange.js <file.html>'); process.exit(1); }
let html = fs.readFileSync(file, 'utf8');

if (html.includes('id="edit-toggle"')) { console.log(`${file}: already present, skipping`); process.exit(0); }

const CSS = `  .theme-btn:hover { border-color: var(--line); }
  .edit-btn { flex: none; font-size: 12.5px; line-height: 1; padding: 8px 12px; border-radius: 10px;
              background: var(--panel); color: var(--text); border: 1px solid var(--line-soft); cursor: pointer; }
  .edit-btn:hover { border-color: var(--line); }
  .edit-btn.on { border-color: var(--di); color: var(--di); box-shadow: 0 0 0 1px var(--di) inset; }
  svg.edit-mode g[data-flows] { cursor: move; }
  svg.edit-mode .flow-dot { display: none; }`;
html = html.replace('  .theme-btn:hover { border-color: var(--line); }', CSS);

const BTN_OLD = '<button id="theme-toggle" class="theme-btn" aria-label="Toggle light/dark mode"></button>';
const BTN_NEW = `<div style="display:flex; gap:8px;">
      <button id="edit-toggle" class="edit-btn" title="Toggle drag-to-rearrange mode">✥ Rearrange</button>
      <button id="theme-toggle" class="theme-btn" aria-label="Toggle light/dark mode"></button>
    </div>`;
html = html.replace(BTN_OLD, BTN_NEW);

const JS = `
  const editBtn = document.getElementById('edit-toggle');
  const boxGs = [...svg.querySelectorAll('g[data-flows]')];
  const arrowEls = [...svg.querySelectorAll('line[data-flow][marker-end], path[data-flow][marker-end]')];
  const EDGE_THRESH = 14;
  boxGs.forEach(g => {
    const r = g.querySelector('rect');
    if (!r) return;
    g.__box0 = { x: +r.getAttribute('x'), y: +r.getAttribute('y'), w: +r.getAttribute('width'), h: +r.getAttribute('height') };
    g.__dx = 0; g.__dy = 0;
  });
  const edgeGap = (b, px, py) => {
    const dx = Math.max(b.x - px, px - (b.x + b.w), 0), dy = Math.max(b.y - py, py - (b.y + b.h), 0);
    return Math.hypot(dx, dy);
  };
  function endpointsOf(el) {
    if (el.__ep0) return el.__ep0;
    if (el.tagName === 'line') {
      el.__ep0 = [{ x: +el.getAttribute('x1'), y: +el.getAttribute('y1') }, { x: +el.getAttribute('x2'), y: +el.getAttribute('y2') }];
      el.__set = (i, nx, ny) => { el.setAttribute(i === 0 ? 'x1' : 'x2', nx); el.setAttribute(i === 0 ? 'y1' : 'y2', ny); };
    } else {
      const toks0 = el.getAttribute('d').match(/[MLA][^MLA]*/g);
      const first = toks0[0].slice(1).trim().split(/[\\s,]+/).map(Number);
      const lastN = toks0[toks0.length - 1].slice(1).trim().split(/[\\s,]+/).map(Number);
      el.__ep0 = [{ x: first[0], y: first[1] }, { x: lastN[lastN.length - 2], y: lastN[lastN.length - 1] }];
      el.__set = (i, nx, ny) => {
        const t = [...toks0];
        if (i === 0) { t[0] = \`M\${nx},\${ny}\`; }
        else {
          const last = t[t.length - 1], cmd = last[0];
          const n = last.slice(1).trim().split(/[\\s,]+/).map(Number);
          n[n.length - 2] = nx; n[n.length - 1] = ny;
          t[t.length - 1] = cmd + n.join(',');
        }
        el.setAttribute('d', t.join(' '));
      };
    }
    return el.__ep0;
  }
  const arrowAssoc = arrowEls.map(el => {
    const eps = endpointsOf(el);
    const assoc = eps.map(ep => {
      let best = null, bestGap = EDGE_THRESH;
      for (const g of boxGs) {
        if (!g.__box0) continue;
        const gap = edgeGap(g.__box0, ep.x, ep.y);
        if (gap < bestGap) { bestGap = gap; best = g; }
      }
      return best;
    });
    const dotWrap = el.nextElementSibling && el.nextElementSibling.classList.contains('flow-dot') ? el.nextElementSibling : null;
    return { el, assoc, dotWrap };
  });
  function pathDOf(el) {
    if (el.tagName === 'line') return \`M\${el.getAttribute('x1')},\${el.getAttribute('y1')} L\${el.getAttribute('x2')},\${el.getAttribute('y2')}\`;
    return el.getAttribute('d');
  }
  function refreshDots(dotWrap, d) {
    if (!dotWrap) return;
    dotWrap.querySelectorAll('animateMotion').forEach(am => am.setAttribute('path', d));
  }
  function moveArrowsFor(g) {
    for (const { el, assoc, dotWrap } of arrowAssoc) {
      const eps = endpointsOf(el);
      let touched = false;
      assoc.forEach((box, i) => {
        if (box !== g) return;
        touched = true;
        el.__set(i, eps[i].x + g.__dx, eps[i].y + g.__dy);
      });
      if (touched) refreshDots(dotWrap, pathDOf(el));
    }
  }
  let editMode = false;
  editBtn.addEventListener('click', () => {
    editMode = !editMode;
    editBtn.classList.toggle('on', editMode);
    svg.classList.toggle('edit-mode', editMode);
    if (editMode) focus(null);
  });
  boxGs.forEach(g => {
    let dragging = null;
    g.addEventListener('pointerdown', e => {
      if (!editMode || e.button !== 0 || !g.__box0) return;
      e.stopPropagation();
      dragging = { x: e.clientX, y: e.clientY, dx0: g.__dx, dy0: g.__dy };
      g.setPointerCapture(e.pointerId);
    });
    g.addEventListener('pointermove', e => {
      if (!dragging) return;
      const scale = vbW / (fitW * zoom);
      g.__dx = dragging.dx0 + (e.clientX - dragging.x) * scale;
      g.__dy = dragging.dy0 + (e.clientY - dragging.y) * scale;
      g.setAttribute('transform', \`translate(\${g.__dx},\${g.__dy})\`);
      moveArrowsFor(g);
    });
    const endDrag = () => { dragging = null; };
    g.addEventListener('pointerup', endDrag);
    g.addEventListener('pointercancel', endDrag);
  });
`;
const marker = '\n})();';
const idx = html.lastIndexOf(marker);
if (idx === -1) { console.error(`${file}: could not find the "})();" insertion point`); process.exit(1); }
html = html.slice(0, idx) + JS + marker + html.slice(idx + marker.length);

fs.writeFileSync(file, html);
console.log(`${file}: inserted the drag-to-rearrange feature`);
