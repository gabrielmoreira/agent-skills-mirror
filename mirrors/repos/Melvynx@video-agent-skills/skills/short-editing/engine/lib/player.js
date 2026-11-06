// Live preview (short.mjs preview): plays the short in a normal tab with the same render(t) as the export.
// Clock = the mix (WebAudio, so seeking is exact); every animation frame draws render(clock) when the last one is done.
// Side panel: SHORT and SOURCE time, the spoken word, and the spec.js entries alive at that instant (source times).
// Keys: space play/pause, left/right 1 s, ,/. one frame, M mute, R reload (re-reads spec.js).

export async function play() {
  const { render, spec, tl, canvas, FPS } = window.LIVE, RAW = window.SPEC, DUR = tl.duration, sp = tl.speed || 1;
  const toSource = t => { for (const [a, b, o] of tl.keeps) if (t < o + (b - a) / sp) return a + Math.max(0, t - o) * sp; return tl.source; };
  const q = new URLSearchParams(location.search);

  document.head.insertAdjacentHTML('beforeend', `<style>
    body { display: flex; gap: 24px; padding: 20px; font: 13px/1.45 -apple-system, system-ui, sans-serif; color: #2b261d; }
    #side { width: 460px; display: flex; flex-direction: column; gap: 12px; }
    #bar { display: flex; gap: 10px; align-items: center; }
    #bar button { font: 600 13px system-ui; padding: 7px 14px; border: 0; border-radius: 8px; background: #2b261d; color: #F1EEE6; cursor: pointer; }
    #bar button.ghost { background: #e2ddd1; color: #2b261d; }
    #seek { width: 100%; accent-color: #2563eb; }
    .clock { font: 600 22px "JetBrains Mono", ui-monospace, monospace; }
    .muted { color: #8a8273; }
    .card { background: #fff; border-radius: 10px; padding: 10px 12px; box-shadow: 0 1px 3px rgba(0,0,0,.08); }
    .card b { font-weight: 650; }
    .tag { display: inline-block; font: 600 11px ui-monospace, monospace; padding: 1px 6px; border-radius: 5px; background: #e8eefc; color: #1d4ed8; margin-right: 6px; }
    pre { margin: 6px 0 0; font: 11px/1.4 ui-monospace, monospace; white-space: pre-wrap; max-height: 150px; overflow: auto; color: #5d5547; }
    #list { display: flex; flex-direction: column; gap: 8px; overflow: auto; max-height: 560px; }
  </style>`);
  document.body.insertAdjacentHTML('beforeend', `<div id="side">
    <div id="bar"><button id="pp">▶ Play</button><button id="mute" class="ghost"></button><span class="muted" id="fps"></span></div>
    <input id="seek" type="range" min="0" max="${DUR}" step="${1 / FPS}" value="0">
    <div><span class="clock" id="tShort"></span> <span class="muted">short</span> &nbsp; <span class="clock muted" id="tSrc"></span> <span class="muted">source (spec.js)</span></div>
    <div class="card"><b>Mot prononcé</b> <span id="word" class="muted"></span><br><b>Seam</b> <span id="seam" class="muted"></span></div>
    <div class="muted">Ce qui est vivant dans spec.js à cet instant (temps source) :</div>
    <div id="list"></div>
    <div class="muted">Espace play/pause · ← → 1 s · , . une image · M son · R recharge spec.js</div>
  </div>`);
  const $ = id => document.getElementById(id);

  // audio clock: the final mix when it exists, else the spliced voice; silent shorts run on performance.now
  const ac = new AudioContext(), gain = ac.createGain(); gain.connect(ac.destination);
  let buf = null;
  for (const u of ['/p/assets/mix.wav', '/p/assets/voice.wav']) {
    const r = await fetch(u); if (!r.ok) continue;
    buf = await ac.decodeAudioData(await r.arrayBuffer()); break;
  }
  let muted = q.has('mute'), playing = false, t = +q.get('t') || 0, t0 = 0, c0 = 0, src = null;
  const now = () => buf ? ac.currentTime : performance.now() / 1000;
  const clock = () => playing ? Math.min(DUR, t0 + now() - c0) : t;
  const setMute = m => { muted = m; gain.gain.value = m ? 0 : 1; $('mute').textContent = m ? '🔇 Son coupé' : '🔊 Son'; };
  const start = () => {
    if (t >= DUR - .05) t = 0;
    t0 = t; c0 = now(); playing = true; $('pp').textContent = '❚❚ Pause';
    if (buf) { ac.resume(); src = ac.createBufferSource(); src.buffer = buf; src.connect(gain); src.start(0, t); }
  };
  const stop = () => { t = clock(); playing = false; $('pp').textContent = '▶ Play'; src?.stop(); src = null; };
  const seek = x => { const was = playing; if (was) stop(); t = Math.max(0, Math.min(DUR, x)); if (was) start(); };
  setMute(muted);

  $('pp').onclick = () => playing ? stop() : start();
  $('mute').onclick = () => setMute(!muted);
  $('seek').oninput = e => seek(+e.target.value);
  addEventListener('keydown', e => {
    const k = e.key;
    if (k === ' ') { e.preventDefault(); playing ? stop() : start(); }
    else if (k === 'ArrowLeft' || k === 'ArrowRight') seek(clock() + (k === 'ArrowLeft' ? -1 : 1));
    else if (k === ',' || k === '.') { if (playing) stop(); seek(Math.round(t * FPS + (k === ',' ? -1 : 1)) / FPS); }
    else if (k === 'm' || k === 'M') setMute(!muted);
    else if (k === 'r' || k === 'R') location.href = location.pathname + location.search.replace(/&t=[\d.]+/, '') + `&t=${clock().toFixed(2)}`;
  });

  // the spec entries alive at t: actors and scenes keep their index after mapSpec, so RAW[i] holds the source times
  const live = (t) => {
    const out = [];
    const add = (kind, list, raw) => (list || []).forEach((s, i) => {
      const a = s.from - (s.pre || 0), b = s.to ?? Infinity;
      if (t >= a && t <= b) out.push({ kind, type: s.type || s.kind || s.media || '', raw: raw?.[i] || s, from: s.from, to: s.to });
    });
    add('scene', spec.scenes, RAW.scenes); add('actor', spec.actors, RAW.actors); add('broll', spec.broll, RAW.broll);
    return out;
  };
  const fmt = x => (x ?? 0).toFixed(2).padStart(6, ' ');
  const brief = o => JSON.stringify(o, (k, v) => typeof v === 'number' ? +v.toFixed(2) : v, 1).replace(/\n\s*/g, ' ').slice(0, 900);
  let lastKey = '';
  const panel = (t) => {
    $('tShort').textContent = fmt(t) + ' s'; $('tSrc').textContent = fmt(toSource(t)) + ' s';
    if (document.activeElement !== $('seek')) $('seek').value = t;
    const w = tl.words.find(w => t >= w.start - .03 && t <= w.end + .12);
    $('word').textContent = w ? `« ${w.text} »  (source ${w.s0.toFixed(2)})` : '';
    const keys = RAW.layout?.keys || [], k = keys.filter(([s]) => s <= toSource(t)).at(-1);
    $('seam').textContent = k ? `y = ${k[1]} depuis ${k[0]} s source (${k[1] === 0 ? 'caméra plein écran' : k[1] >= 1900 ? 'papier plein écran' : 'papier en haut, caméra en bas'})` : 'défaut';
    const L = live(t), key = L.map(x => x.kind + x.from).join('|');
    if (key === lastKey) return; lastKey = key;
    $('list').innerHTML = L.length ? '' : '<div class="muted">rien, juste la caméra et les sous-titres</div>';
    for (const x of L) {
      const el = document.createElement('div'); el.className = 'card';
      el.innerHTML = `<span class="tag">${x.kind}</span><b>${x.type}</b> <span class="muted">${x.raw.from ?? ''} → ${x.raw.to ?? ''} s source · layer ${x.raw.layer || 'stage'}</span><pre></pre>`;
      el.querySelector('pre').textContent = brief(x.raw);
      $('list').appendChild(el);
    }
  };

  // draw loop: one render(t) in flight at a time; a slow frame is skipped, never queued, so the picture stays on the audio
  let busy = false, n = 0, tf = performance.now();
  const loop = () => {
    requestAnimationFrame(loop);
    const tc = clock();
    if (playing && tc >= DUR) stop();
    panel(tc);
    if (busy) return;
    busy = true;
    render(Math.round(tc * FPS) / FPS).finally(() => { busy = false; n++; });
    const dt = performance.now() - tf;
    if (dt > 1000) { $('fps').textContent = `${Math.round(n * 1000 / dt)} images/s dessinées`; n = 0; tf = performance.now(); }
  };
  loop();
}
