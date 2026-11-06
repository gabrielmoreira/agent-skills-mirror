// Pure timeline helpers shared by the browser runtime and the Node CLI (audio cues, QC).
// Two clocks exist: SOURCE time (seconds in assets/source.mp4, what spec.js is written in)
// and SHORT time (seconds in the tightened cut, what gets rendered). mapper() converts.

export const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));

export function mapper(tl) {
  const K = tl.keeps, sp = tl.speed || 1;
  return t => {
    // 'p+X' = X seconds into the inserted pause (spec.pause), e.g. a narrator word time
    if (typeof t === 'string' && /^p\+/.test(t)) return (tl.pause?.t0 ?? 0) + parseFloat(t.slice(2));
    // 'iK+X' = X seconds into insert K (spec.inserts, index in that list)
    if (typeof t === 'string' && /^i\d+\+/.test(t)) { const [k, x] = t.slice(1).split('+'); return (tl.inserts?.[+k]?.t0 ?? 0) + parseFloat(x); }
    // 'o+X' = X seconds into the outro (spec.outro, the end card after the last word); 'o-X' = X seconds before it
    if (typeof t === 'string' && /^o[+-]/.test(t)) return (tl.outro?.t0 ?? tl.duration) + parseFloat(t.slice(1));
    if (typeof t !== 'number') return t;
    for (const [a, b, o] of K) { if (t < a) return o; if (t < b) return o + (t - a) / sp; }
    return tl.duration;
  };
}

const norm = s => String(s).toLowerCase().replace(/[.,!?;:…]+$/, '');

// Word chunks for captions. words are in SHORT time: [{text, start, end}].
// cfg: {replace:[['cent pour cent','100%']], emph:['Opus 5.5'], maxWords, maxChars, gap, hide:[[a,b]] (short time),
// bleep:[[a,b]] (short time, spec.bleep: those words never show)}
export function captionChunks(words, cfg = {}) {
  const rep = (cfg.replace || []).map(([k, v]) => [k.toLowerCase().split(/\s+/), v]);
  const merged = [];
  for (let i = 0; i < words.length; i++) {
    let hit = null;
    for (const [ks, v] of rep) if (ks.every((k, j) => words[i + j] && norm(words[i + j].text) === norm(k))) { hit = [ks.length, v]; break; }
    if (hit) {
      const last = words[i + hit[0] - 1], p = last.text.match(/[.,!?;:]$/);
      merged.push({ text: hit[1] + (p ? p[0] : ''), start: words[i].start, end: last.end, rep: true });
      i += hit[0] - 1;
    } else merged.push({ text: words[i].text, start: words[i].start, end: words[i].end });
  }
  const hidden = t => [...(cfg.hide || []), ...(cfg.bleep || [])].some(([a, b]) => t >= a - .01 && t < b);
  const emph = new Set((cfg.emph || []).map(norm));
  const maxW = cfg.maxWords ?? 3, maxC = cfg.maxChars ?? 16, gap = cfg.gap ?? .35;
  // cfg.scaleKeys (captions drawn k times bigger from t on): such a line holds k times fewer characters
  const scaleAt = t => (cfg.scaleKeys || []).reduce((v, k) => t >= k[0] ? k[1] : v, 1);
  const chunks = []; let cur = null, prev = null;
  for (const w of merged) {
    if (hidden(w.start)) { cur = null; prev = null; continue; }
    // cfg.lower: every spoken word in lower case (benkimball.ai); captions.replace values keep their own case
    const text = (cfg.lower && !w.rep ? w.text.toLowerCase() : w.text).replace(/[.,;:]+$/, '').replace(/^["«“]|["»”]$/g, '');
    if (!text) { prev = w; continue; }   // a lone ':' or '.' token: no word, but it still breaks the line
    const word = { text, start: w.start, end: w.end, emph: emph.has(norm(text)) };
    const brk = !cur || !cfg.phrase && (cur.words.length >= maxW || cur.chars + 1 + text.length > maxC / scaleAt(cur.words[0]?.start ?? w.start))
      || /[.,!?;:]$/.test(prev?.text || '') || w.start - prev.end > gap;
    if (brk) { cur = { words: [], chars: 0 }; chunks.push(cur); }
    cur.chars += (cur.words.length ? 1 : 0) + text.length;
    cur.words.push(word); prev = w;
  }
  if (cfg.phrase) chunks.splice(0, chunks.length, ...chunks.flatMap(c => phraseSplit(c.words, maxW, maxC / scaleAt(c.words[0].start))));
  chunks.forEach((c, i) => { c.start = c.words[0].start; c.end = c.words.at(-1).end; c.next = chunks[i + 1]?.start ?? Infinity; });
  // a line never runs into a hide span after it (a word ending in a cut can map past a spec.inserts card)
  for (const c of chunks) c.stop = Math.min(Infinity, ...(cfg.hide || []).map(([a]) => a).filter(a => a > c.start));
  return chunks;
}

// cfg.phrase: a sentence (between punctuation and pauses) is cut where it reads, not where the line fills up. Every
// split of it into lines of 1 to maxW words is scored and the cheapest wins: a line over maxC characters, a line that
// ends on a word that leans on the next one (de, les, que, ton, the, of...), a lone word and a line of two all cost,
// a longer pause between two words makes a good cut, so lines run 3 to 5 words when the sentence allows it.
const LEAN = new Set(('le la les l un une des du de d à au aux et ou mais que qu qui ton ta tes son sa ses mon ma mes ce cet cette ' +
  'en sur pour avec par dans sans tu il elle on je me te se ne nous vous leur très plus tout vrais gros bonnes est sont va the a an of to and or in on for with my your is').split(' '));
function phraseSplit(words, maxW, maxC) {
  const n = words.length, best = [0], from = [0], len = w => w.text.length;
  for (let j = 1; j <= n; j++) {
    best[j] = Infinity;
    for (let i = Math.max(0, j - maxW); i < j; i++) {
      const ws = words.slice(i, j), k = ws.length, chars = ws.reduce((a, w) => a + len(w), k - 1);
      const last = norm(ws[k - 1].text).replace(/^.*'/, '').replace(/'$/, '');
      let c = best[i] + 3 + Math.max(0, chars - maxC) * 4 + (k === 1 && n > 1 ? 7 : k === 2 && n > 2 ? 2 : 0);
      if (j < n) c += (LEAN.has(last) || /'$/.test(ws[k - 1].text) ? 9 : 0) - Math.min(3, (words[j].start - words[j - 1].end) * 12);
      if (c < best[j]) { best[j] = c; from[j] = i; }
    }
  }
  const out = []; for (let j = n; j > 0; j = from[j]) out.unshift({ words: words.slice(from[j], j), chars: 0 });
  return out;
}

// Word-synced typing: display tokens mapped onto the spoken words between t0 and t1 (SHORT time).
export function typing(display, words, t0, t1) {
  const toks = display.split(' ');
  const sp = words.filter(w => w.start >= t0 - .02 && w.start < t1 + .02);
  if (!sp.length) return toks.map((tok, i) => ({ tok, start: t0 + i * .1, end: t0 + i * .1 + .1 }));
  return toks.map((tok, i) => {
    const j = Math.round(i * (sp.length - 1) / Math.max(1, toks.length - 1)), w = sp[j];
    return { tok, start: w.start, end: Math.max(w.end, w.start + .12) };
  });
}

// spec.js is authored in SOURCE time (read times straight from files/words.md). This deep-copies it into
// SHORT time. A number is a time when its key is at/from/to/until or ends with "At"/"From"/"To"
// (countFrom, workTo...); inside any array whose key ends in "keys" (keys, labelKeys...) the first element
// of each entry is a time; "hide", "bleep", "thump" and any key ending in "spans" hold [a, b, ...] time pairs. A string 'p+X' in a time
// slot means X seconds into the inserted pause (spec.pause), 'iK+X' X seconds into insert K (spec.inserts), 'o+X' X seconds into the outro (spec.outro). Everything else
// (durations, sizes, offsets into media clips) is left alone. "cut" and "tighten" stay in source time.
const TIME_KEY = /^(at|from|to|until)$|(At|From|To)$/;
export function mapSpec(spec, m) {
  const walk = (v, k) => {
    if (k === 'cut' || k === 'tighten' || k === 'media' || k === 'cam') return v;
    if (typeof v === 'number' || (typeof v === 'string' && /^(p\+|o[+-]|i\d+\+)[\d.]+$/.test(v))) return TIME_KEY.test(k) ? m(v) : v;
    if (Array.isArray(v)) {
      if (/keys$/i.test(k)) return v.map(e => [m(e[0]), ...e.slice(1).map(x => walk(x, ''))]);
      if (k === 'hide' || k === 'bleep' || k === 'thump' || /spans$/i.test(k)) return v.map(([a, b, ...r]) => [m(a), m(b), ...r]);
      return v.map(x => walk(x, ''));
    }
    if (v && typeof v === 'object') { const o = {}; for (const kk in v) o[kk] = walk(v[kk], kk); return o; }
    return v;
  };
  return walk(spec, '');
}
