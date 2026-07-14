// Checks a rendered SVG diagram for collisions — run this whole file through a browser JS tool
// after opening the HTML file. Errors are reported in VIEWBOX COORDINATES → fix the numbers in
// the file directly. It also draws red (error) / yellow (warning) outline boxes on the page, so
// a screenshot shows exactly where the problem is.
// Re-running clears the previous highlights before checking again.
// Rule of thumb: a badge or box's solid background DELIBERATELY covering part of a line is by
// design — wherever a line is hidden behind something solid, that spot doesn't count as an error.
// Only what a human eye would actually see gets checked.
(() => {
  const svg = document.querySelector('svg');
  if (!svg) return 'No <svg> found on the page';
  svg.querySelectorAll('.__vc').forEach(e => e.remove());

  const inv = svg.getScreenCTM().inverse();
  const vb = (x, y) => { const p = new DOMPoint(x, y).matrixTransform(inv); return `${Math.round(p.x)},${Math.round(p.y)}`; };
  const short = s => (s || '').trim().replace(/\s+/g, ' ').slice(0, 40);
  const errors = [], warnings = [];
  const mark = (b, color) => {
    const r = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    const p1 = new DOMPoint(b.left - 2, b.top - 2).matrixTransform(inv);
    const p2 = new DOMPoint(b.right + 2, b.bottom + 2).matrixTransform(inv);
    r.setAttribute('class', '__vc'); r.setAttribute('fill', 'none');
    r.setAttribute('stroke', color); r.setAttribute('stroke-width', '1.5');
    r.setAttribute('x', p1.x); r.setAttribute('y', p1.y);
    r.setAttribute('width', p2.x - p1.x); r.setAttribute('height', p2.y - p1.y);
    svg.appendChild(r);
  };

  const texts = [...svg.querySelectorAll('text')].filter(t => t.textContent.trim());
  const tb = texts.map(t => ({ t, b: t.getBoundingClientRect() }));
  const solid = new Set([...svg.querySelectorAll('rect,circle')]
    .filter(r => { const f = r.getAttribute('fill'); return f && f !== 'none'; }));
  const boxes = [...solid].filter(r => r.tagName === 'rect' && r.getBoundingClientRect().width >= 60)
    .map(r => ({ r, b: r.getBoundingClientRect(), name: short(r.nextElementSibling?.textContent) }));

  // 1. TEXT OVERLAPS TEXT — never acceptable (the upper text's halo eats the lower text)
  const inset = 1.5;
  for (let i = 0; i < tb.length; i++) for (let j = i + 1; j < tb.length; j++) {
    const a = tb[i].b, b = tb[j].b;
    if (!(a.right - inset < b.left || b.right - inset < a.left || a.bottom - inset < b.top || b.bottom - inset < a.top)) {
      errors.push({ type: 'TEXT OVERLAPS TEXT', a: short(tb[i].t.textContent), b: short(tb[j].t.textContent), at: vb(a.left, a.top) });
      mark(a, '#ef4444'); mark(b, '#ef4444');
    }
  }

  // 2. BOX OVERLAPS BOX (large boxes only; a small badge sitting inside a box is expected)
  for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) {
    const a = boxes[i].b, b = boxes[j].b;
    if (!(a.right < b.left || b.right < a.left || a.bottom < b.top || b.bottom < a.top)) {
      errors.push({ type: 'BOX OVERLAPS BOX', a: boxes[i].name, b: boxes[j].name, at: vb(a.left, a.top) });
      mark(a, '#ef4444');
    }
  }

  // 3. Walk along every line, only checking points where the line is actually VISIBLE
  const lines = [...svg.querySelectorAll('line, path')].filter(e => !e.closest('marker') && e.getAttribute('stroke') && !e.classList.contains('__vc'));
  for (const ln of lines) {
    let len; try { len = ln.getTotalLength(); } catch (e) { continue; }
    if (!len) continue;
    const m = ln.getScreenCTM();
    const seen = new Set();
    for (let d = 9; d < len - 9; d += Math.max(3, len / 150)) {
      const p0 = ln.getPointAtLength(d);
      const p = { x: m.a * p0.x + m.c * p0.y + m.e, y: m.b * p0.x + m.d * p0.y + m.f };
      const stack = document.elementsFromPoint(p.x, p.y);
      const li = stack.indexOf(ln);
      if (li < 0) continue;
      // Something solid (a badge, a box) sits ON TOP of the line at this point → invisible here, skip
      if (stack.slice(0, li).some(e => solid.has(e))) continue;
      // A visible point that lands INSIDE a large box's interior → line runs through the box
      // (wrong layer order or bad layout)
      for (const bx of boxes) {
        const b = bx.b;
        if (p.x > b.left + 3 && p.x < b.right - 3 && p.y > b.top + 3 && p.y < b.bottom - 3 && !seen.has('B' + bx.name)) {
          seen.add('B' + bx.name);
          errors.push({ type: 'LINE RUNS THROUGH BOX', box: bx.name, color: ln.getAttribute('stroke'), at: vb(p.x, p.y) });
          mark(b, '#ef4444');
        }
      }
      // A visible point that lands inside a text label's bbox
      for (const { t, b } of tb) {
        if (p.x > b.left && p.x < b.right && p.y > b.top + 1 && p.y < b.bottom - 1) {
          const key = 'T' + short(t.textContent) + ln.getAttribute('stroke');
          if (seen.has(key)) continue;
          seen.add(key);
          const textAfterLine = !!(ln.compareDocumentPosition(t) & Node.DOCUMENT_POSITION_FOLLOWING);
          if (textAfterLine) {
            // Text drawn after the line (its halo covers the line around the glyphs) → acceptable,
            // but many of these mean the layout is getting cluttered
            warnings.push({ type: 'LINE RUNS NEAR TEXT', text: short(t.textContent), color: ln.getAttribute('stroke'), at: vb(p.x, p.y) });
            mark(b, '#f59e0b');
          } else {
            // Line drawn AFTER the text = the line paints OVER the text → wrong layer order
            errors.push({ type: 'LINE COVERS TEXT', text: short(t.textContent), color: ln.getAttribute('stroke'), at: vb(p.x, p.y) });
            mark(b, '#ef4444');
          }
        }
      }
    }
  }

  // 4. ARROWHEAD TOO CLOSE TO A BOX — the endpoint (marker-end) must sit ~8px from the box edge.
  // getPointAtLength returns VIEWBOX coordinates (the line has no transform); boxes read x/y/w/h
  // straight from their attributes.
  const GAP_MIN = 6; // under 6 viewBox units counts as glued to the box (rule: leave ~8)
  for (const ln of lines) {
    if (!ln.getAttribute('marker-end')) continue;
    let len; try { len = ln.getTotalLength(); } catch (e) { continue; }
    if (!len) continue;
    const p = ln.getPointAtLength(len);
    for (const bx of boxes) {
      const r = bx.r, x = +r.getAttribute('x'), y = +r.getAttribute('y'),
            w = +r.getAttribute('width'), h = +r.getAttribute('height');
      if ([x, y, w, h].some(Number.isNaN)) continue;
      const inside = p.x > x && p.x < x + w && p.y > y && p.y < y + h;
      const dx = Math.max(x - p.x, p.x - (x + w), 0), dy = Math.max(y - p.y, p.y - (y + h), 0);
      const gap = Math.hypot(dx, dy);
      if (inside || gap < GAP_MIN) {
        errors.push({ type: 'ARROWHEAD TOO CLOSE TO BOX', box: bx.name, color: ln.getAttribute('stroke'),
          gap: inside ? 'pierces into the box' : Math.round(gap) + 'px (need ~8)', at: `${Math.round(p.x)},${Math.round(p.y)}` });
        mark(bx.b, '#ef4444');
        break;
      }
    }
  }

  // 5. Does the viewBox actually contain everything?
  const bbox = svg.getBBox();
  const [vx, vy, vw, vh] = svg.getAttribute('viewBox').split(/\s+/).map(Number);
  if (bbox.x < vx - 2 || bbox.y < vy - 2 || bbox.x + bbox.width > vx + vw + 2 || bbox.y + bbox.height > vy + vh + 2)
    errors.push({ type: 'VIEWBOX OVERFLOW', detail: `getBBox ${Math.round(bbox.x)},${Math.round(bbox.y)} ${Math.round(bbox.width)}×${Math.round(bbox.height)} vs viewBox ${vx},${vy} ${vw}×${vh}` });

  return {
    summary: `${errors.length} error(s) to fix · ${warnings.length} warning(s) (halo-covered — but more than 5 means the layout is getting cluttered)`,
    errors, warnings: warnings.slice(0, 15),
  };
})()
