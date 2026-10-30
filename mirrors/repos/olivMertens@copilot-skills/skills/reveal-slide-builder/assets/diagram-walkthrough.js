/*
 * Guided diagram walkthrough for reveal.js 5/6.
 *
 * Walks an INLINE SVG diagram one step at a time. Each step is a reveal.js fragment (.dw-step) that names the
 * diagram parts to show. The script dims everything else, zooms the SVG viewBox on the named parts and runs a
 * moving flow along the active connectors. Before the first step, in PDF export (?print-pdf) and without
 * JavaScript, the whole diagram shows.
 *
 * Diagram sources (the SVG must be inline in the slide: <img> or <object> cannot be driven):
 *   1. Id contract: <svg class="dw-svg" data-diagram="KEY" viewBox="…"> whose DIRECT children carry ids
 *        KEY-<node>        a component (a <g> holding its shape and labels)
 *        KEY-c-<name>      a container / boundary (kept as context when it holds a focused node)
 *        KEY-e-<name>      a connector <path>; optional data-from / data-to = node ids
 *        KEY-legend…       legend items (always kept as context)
 *   2. A Mermaid flowchart pre-rendered to SVG (no data-diagram): node, subgraph and edge ids are read from
 *      Mermaid's own markup; an edge lights up when both of its ends are focused.
 *
 * Step attributes (on .dw-step):
 *   data-focus     ids to highlight and zoom on (connectors light up when named, or when both ends are named)
 *   data-fail      ids shown as failed, with a label ("unavailable" by default)
 *   data-alert     ids outlined as at risk, without a label
 *   data-zoom      "full" keeps the whole diagram in view (highlight without zoom)
 *   data-edges     "named" lights only the connectors listed in data-focus
 *   data-evidence  image shown beside the diagram for this step (+ data-evidence-caption); select it to enlarge
 *   data-fail-label  overrides the failure label for this step
 *   A step whose data-focus, data-fail and data-alert are all empty shows the whole diagram (recap).
 * Slide attributes (on the <section class="dw-slide">):
 *   data-keep          ids always kept as context while stepping
 *   data-fail-label    failure label for the slide (localise it: "indisponible", "nicht verfügbar"…)
 *   data-evidence-tag  tag shown above evidence images (default "From a real run")
 *
 * QA helper: window.DiagramWalkthrough.audit() lists unknown ids per slide and step.
 */
(function () {
  'use strict';

  const Reveal = window.Reveal;
  if (!Reveal) return;

  const NS = 'http://www.w3.org/2000/svg';
  const reduceMotion = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  const printing = /print-pdf/.test(window.location.search);
  const DURATION = 700;
  const MIN_H = 0.42;
  const MIN_W = 0.4;
  const STATES = ['dw-on', 'dw-ctx', 'dw-dim', 'dw-fail', 'dw-alert'];
  const store = new WeakMap();
  const warned = new Set();

  const words = (s) => (s || '').split(/\s+/).filter(Boolean);

  // ---------------------------------------------------------------- diagram model

  function contractModel(svg, key) {
    const parts = new Map();
    const edges = [];
    svg.querySelectorAll(':scope > g[id], :scope > path[id]').forEach((el) => {
      if (!el.id.startsWith(key + '-')) return;
      const id = el.id.slice(key.length + 1);
      if (id.startsWith('e-')) {
        edges.push({ id, el, from: el.dataset.from || null, to: el.dataset.to || null, label: null });
      } else {
        const kind = id.startsWith('c-') ? 'container' : id.startsWith('legend') ? 'legend' : 'node';
        parts.set(id, { el, kind });
      }
    });
    return { parts, edges };
  }

  function stripPrefix(svg, id) {
    return svg.id && id.startsWith(svg.id + '-') ? id.slice(svg.id.length + 1) : id;
  }

  function mermaidModel(svg) {
    const parts = new Map();
    const edges = [];
    svg.querySelectorAll('g.node[id]').forEach((el) => {
      const m = el.id.match(/flowchart-(.+)-\d+$/);
      if (m) parts.set(m[1], { el, kind: 'node' });
    });
    svg.querySelectorAll('g.cluster[id]').forEach((el) => {
      parts.set(stripPrefix(svg, el.id), { el, kind: 'container' });
    });
    svg.querySelectorAll('path.flowchart-link').forEach((el) => {
      const raw = stripPrefix(svg, el.getAttribute('data-id') || el.id || '');
      const core = raw.replace(/^L[_-]/, '').replace(/[_-]\d+$/, '');
      let from = null;
      let to = null;
      // Node ids may contain "_" or "-": split where both halves are known nodes.
      for (let i = 1; i < core.length - 1; i++) {
        if (core[i] !== '_' && core[i] !== '-') continue;
        const a = core.slice(0, i);
        const b = core.slice(i + 1);
        if (parts.has(a) && parts.has(b)) { from = a; to = b; break; }
      }
      const dataId = el.getAttribute('data-id');
      const labelEl = dataId ? svg.querySelector('.edgeLabel .label[data-id="' + CSS.escape(dataId) + '"]') : null;
      edges.push({ id: raw, el, from, to, label: labelEl ? labelEl.closest('.edgeLabel') : null });
    });
    return { parts, edges };
  }

  function model(svg) {
    let m = store.get(svg);
    if (m) return m;
    const key = svg.dataset.diagram;
    const built = key ? contractModel(svg, key) : mermaidModel(svg);
    const vb = svg.viewBox.baseVal;
    if (!vb || !vb.width || !vb.height) console.warn('[diagram-walkthrough] the diagram needs a viewBox', svg);
    const full = [vb.x, vb.y, vb.width, vb.height];
    m = Object.assign(built, { full, current: full.slice(), anim: 0 });
    store.set(svg, m);
    return m;
  }

  function knownIds(m) {
    const ids = new Set(m.parts.keys());
    m.edges.forEach((e) => ids.add(e.id));
    return ids;
  }

  // ---------------------------------------------------------------- geometry

  // Boxes in the diagram's user units, measured against the FULL view so they do not depend on the zoom.
  function measure(svg, m, els) {
    if (!els.length) return [];
    const saved = svg.getAttribute('viewBox');
    svg.setAttribute('viewBox', m.full.join(' '));
    const ctm = svg.getScreenCTM();
    const boxes = [];
    if (ctm) {
      const inv = ctm.inverse();
      const p = svg.createSVGPoint();
      const map = (x, y) => { p.x = x; p.y = y; return p.matrixTransform(inv); };
      els.forEach((el) => {
        const r = el.getBoundingClientRect();
        if (!r.width && !r.height) { boxes.push(null); return; }
        const a = map(r.left, r.top);
        const b = map(r.right, r.bottom);
        boxes.push([Math.min(a.x, b.x), Math.min(a.y, b.y), Math.max(a.x, b.x), Math.max(a.y, b.y)]);
      });
    }
    svg.setAttribute('viewBox', saved);
    return boxes;
  }

  function setViewBox(svg, m, target, instant) {
    cancelAnimationFrame(m.anim);
    const write = (v) => { m.current = v; svg.setAttribute('viewBox', v.map((n) => n.toFixed(1)).join(' ')); };
    if (instant || reduceMotion) { write(target); return; }
    const from = m.current.slice();
    const t0 = performance.now();
    const tick = (now) => {
      const t = Math.min(1, (now - t0) / DURATION);
      const e = t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
      write(from.map((f, i) => f + (target[i] - f) * e));
      if (t < 1) m.anim = requestAnimationFrame(tick);
    };
    m.anim = requestAnimationFrame(tick);
  }

  function zoomTarget(svg, m, boxes) {
    const valid = boxes.filter(Boolean);
    if (!valid.length) return m.full;
    const x0 = Math.min(...valid.map((b) => b[0]));
    const y0 = Math.min(...valid.map((b) => b[1]));
    const x1 = Math.max(...valid.map((b) => b[2]));
    const y1 = Math.max(...valid.map((b) => b[3]));
    const [fx, fy, fw, fh] = m.full;
    const pad = Math.max(24, fw * 0.035);
    const ratio = svg.clientWidth && svg.clientHeight ? svg.clientWidth / svg.clientHeight : fw / fh;
    let h = Math.max(y1 - y0 + 2 * pad, fh * MIN_H);
    const w = Math.max(x1 - x0 + 2 * pad, h * ratio, fw * MIN_W);
    h = w / ratio;
    const cx = (x0 + x1) / 2;
    const cy = (y0 + y1) / 2;
    const x = w >= fw ? fx + (fw - w) / 2 : Math.min(Math.max(cx - w / 2, fx), fx + fw - w);
    const y = h >= fh ? fy + (fh - h) / 2 : Math.min(Math.max(cy - h / 2, fy), fy + fh - h);
    return [x, y, w, h];
  }

  // ---------------------------------------------------------------- rendering

  function reset(svg, m) {
    svg.querySelectorAll('.dw-flow, .dw-fail-label').forEach((n) => n.remove());
    m.parts.forEach((p) => p.el.classList.remove(...STATES));
    m.edges.forEach((e) => {
      e.el.classList.remove(...STATES);
      if (e.label) e.label.classList.remove(...STATES);
    });
  }

  // Label above the failed shape's top-right corner, so it never covers the node's own text.
  function failLabel(el, text) {
    const shape = el.querySelector(':scope > rect, :scope > polygon, :scope > circle, :scope > ellipse, :scope > path');
    if (!shape) return;
    const b = shape.getBBox();
    const t = document.createElementNS(NS, 'text');
    t.setAttribute('x', b.x + b.width);
    t.setAttribute('y', b.y - 7);
    t.setAttribute('text-anchor', 'end');
    t.setAttribute('class', 'dw-fail-label');
    t.textContent = text;
    el.appendChild(t);
  }

  function evidence(section, step) {
    const stage = section.querySelector('.dw-stage');
    if (!stage) return;
    const src = step ? step.dataset.evidence || '' : '';
    stage.classList.toggle('has-evidence', !!src);
    let fig = stage.querySelector('.dw-evidence');
    if (!src) { if (fig) fig.hidden = true; return; }
    if (!fig) {
      fig = document.createElement('figure');
      fig.className = 'dw-evidence';
      fig.innerHTML = '<span class="dw-evidence-tag"></span><img alt="" tabindex="0" role="button"><figcaption></figcaption>';
      // reveal.js only binds its lightbox to images present at start-up, so open it through the API.
      const img = fig.querySelector('img');
      const open = () => {
        const url = img.getAttribute('src');
        if (typeof Reveal.previewImage === 'function') Reveal.previewImage(url);
        else window.open(url, '_blank', 'noopener');
      };
      img.addEventListener('click', open);
      img.addEventListener('keydown', (ev) => {
        if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); ev.stopPropagation(); open(); }
      });
      stage.appendChild(fig);
    }
    const caption = step.dataset.evidenceCaption || '';
    const tag = section.dataset.evidenceTag || 'From a real run';
    const img = fig.querySelector('img');
    if (img.getAttribute('src') !== src) img.setAttribute('src', src);
    img.alt = tag + (caption ? ': ' + caption : '');
    fig.querySelector('.dw-evidence-tag').textContent = tag;
    fig.querySelector('figcaption').textContent = caption;
    fig.hidden = false;
  }

  function warnUnknown(section, step, m, lists) {
    const ids = knownIds(m);
    const where = section.id || String(Reveal.getIndices(section).h);
    lists.forEach((list) => list.forEach((id) => {
      const k = where + ':' + id;
      if (ids.has(id) || warned.has(k)) return;
      warned.add(k);
      console.warn('[diagram-walkthrough] unknown id "' + id + '" in step', step);
    }));
  }

  function apply(section, instant) {
    const svg = section.querySelector('svg.dw-svg');
    if (!svg) return;
    const m = model(svg);
    reset(svg, m);

    const shown = section.querySelectorAll('.dw-step.visible');
    const step = shown.length ? shown[shown.length - 1] : null;
    section.classList.toggle('dw-started', !!step);
    // Evidence first: it changes the stage width, hence the zoom ratio.
    evidence(section, step);
    if (!step) { setViewBox(svg, m, m.full, instant); return; }

    const focus = new Set(words(step.dataset.focus));
    const fail = new Set(words(step.dataset.fail));
    const alert = new Set(words(step.dataset.alert));
    const keep = new Set(words(section.dataset.keep));
    warnUnknown(section, step, m, [focus, fail, alert, keep]);
    if (!focus.size && !fail.size && !alert.size) { setViewBox(svg, m, m.full, instant); return; }

    const lit = new Set([...focus, ...fail, ...alert]);
    const namedOnly = step.dataset.edges === 'named';
    const litParts = [...m.parts].filter(([id, p]) => lit.has(id) && p.kind !== 'legend');
    const litNodes = litParts.filter(([, p]) => p.kind === 'node');
    const containers = [...m.parts].filter(([id, p]) => p.kind === 'container' && !lit.has(id));

    const boxes = measure(svg, m, [...litParts, ...litNodes, ...containers].map(([, p]) => p.el));
    const partBoxes = boxes.slice(0, litParts.length);
    const nodeBoxes = boxes.slice(litParts.length, litParts.length + litNodes.length).filter(Boolean);
    const containerBox = new Map(containers.map(([id], i) => [id, boxes[litParts.length + litNodes.length + i]]));
    const centres = nodeBoxes.map((b) => [(b[0] + b[2]) / 2, (b[1] + b[3]) / 2]);
    const holdsFocus = (b) => !!b && centres.some(([x, y]) => x > b[0] && x < b[2] && y > b[1] && y < b[3]);

    m.parts.forEach((p, id) => {
      let state = 'dw-dim';
      if (lit.has(id)) state = 'dw-on';
      else if (keep.has(id) || p.kind === 'legend') state = 'dw-ctx';
      else if (p.kind === 'container' && holdsFocus(containerBox.get(id))) state = 'dw-ctx';
      p.el.classList.add(state);
      if (fail.has(id)) {
        p.el.classList.add('dw-fail');
        failLabel(p.el, step.dataset.failLabel || section.dataset.failLabel || 'unavailable');
      } else if (alert.has(id)) {
        p.el.classList.add('dw-alert');
      }
    });

    const litEdges = [];
    m.edges.forEach((e) => {
      const byEnds = !namedOnly && e.from && e.to && lit.has(e.from) && lit.has(e.to);
      const on = lit.has(e.id) || byEnds;
      e.el.classList.add(on ? 'dw-on' : 'dw-dim');
      if (e.label) e.label.classList.add(on ? 'dw-on' : 'dw-dim');
      if (!on) return;
      litEdges.push(e);
      const toFailed = fail.has(e.id) || alert.has(e.id) || fail.has(e.from) || fail.has(e.to);
      if (toFailed) { e.el.classList.add('dw-fail'); return; }
      const flow = document.createElementNS(NS, 'path');
      flow.setAttribute('d', e.el.getAttribute('d'));
      const tf = e.el.getAttribute('transform');
      if (tf) flow.setAttribute('transform', tf);
      flow.setAttribute('class', 'dw-flow');
      e.el.after(flow);
    });

    if (step.dataset.zoom === 'full') { setViewBox(svg, m, m.full, instant); return; }
    let target = partBoxes.filter(Boolean);
    if (!target.length) target = measure(svg, m, litEdges.map((e) => e.el)).filter(Boolean);
    setViewBox(svg, m, zoomTarget(svg, m, target), instant);
  }

  // ---------------------------------------------------------------- wiring

  function refresh(instant) {
    const section = Reveal.getCurrentSlide();
    if (section) apply(section, instant === true);
  }

  function audit() {
    const report = [];
    document.querySelectorAll('.reveal .slides section.dw-slide').forEach((section) => {
      const svg = section.querySelector('svg.dw-svg');
      const where = section.id || section.getAttribute('aria-label') || '(untitled)';
      if (!svg) { report.push({ slide: where, problem: 'no inline svg.dw-svg' }); return; }
      const ids = knownIds(model(svg));
      section.querySelectorAll('.dw-step').forEach((step, i) => {
        const unknown = ['focus', 'fail', 'alert'].flatMap((k) => words(step.dataset[k])).filter((id) => !ids.has(id));
        if (unknown.length) report.push({ slide: where, step: i + 1, unknown });
      });
      const keep = words(section.dataset.keep).filter((id) => !ids.has(id));
      if (keep.length) report.push({ slide: where, keep });
    });
    return report;
  }

  window.DiagramWalkthrough = { refresh: () => refresh(true), audit };

  if (printing) return;
  Reveal.on('ready', () => refresh(true));
  Reveal.on('slidechanged', () => refresh(true));
  Reveal.on('fragmentshown', () => refresh(false));
  Reveal.on('fragmenthidden', () => refresh(false));
  Reveal.on('resize', () => refresh(true));
  if (Reveal.isReady()) refresh(true);
})();
