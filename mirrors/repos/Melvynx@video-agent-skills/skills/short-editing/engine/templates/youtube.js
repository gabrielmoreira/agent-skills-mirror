// YouTube long-form (16:9, 1920x1080): "<one-line promise>". All times are SOURCE seconds (files/words.md).
// Runtime: lib/runtime-yt.js. Scenes draw on a 1080x1080 paper stage (same coordinates as format 'square': x 0..1080,
// centre 540, y 0..1080) that sits LEFT of the camera. Parameters: references/scene-library.md, rhythm: the
// youtube-editing skill's references/motion-design.md.
const L = n => `assets/logos/${n}.png`;   // real logos only (official site / app icon), drawn flat
const IC = n => `assets/icons/${n}.png`;  // house icons (bare Google Noto emoji): copy from <skill>/assets/icons/, never another pack
// frosted glass panel LEFT of the speaker on full camera ('over' layer, output px): x 48..648, centre CX, y 150..930.
// The default way to show a source, a quote or a list while he talks: no layout move at all.
const GX = 48, GW = 600, CX = GX + GW / 2;
const glass = (from, to, items) => ({ type: 'board', layer: 'over', from, to, pre: .4, items: [
  { k: 'glass', x: GX, y: 150, w: GW, h: 780, at: from, pre: .4, rise: 0, tint: .8 }, ...items] });

window.SPEC = {
  format: 'youtube',
  title: '<title>',
  media: {
    // article: { src: 'assets/sources/fortune.png' },                     // a captured source (still, Ken Burns)
    // demo: { src: '~/path/to/clip.mp4', from: 0, dur: 10, fill: true },  // full-screen B-roll (fill crops to 16:9)
  },
  cam: { crop: [0, 0, 1920, 1080], eyes: [960, 400] },   // the whole take; eyes = the face (source px), set by init
  cut: [],                                               // [[a, b]] retakes, false starts, dead air to drop

  // Long-form pace: only real pauses go (budget per boundary in s), breathing stays, no speed-up.
  speed: 1,
  tighten: { sentence: .36, comma: .22, word: .12, lead: .15, tail: 1.2 },

  // [t, x], x = the camera's left edge: 0 full camera, 1080 split (paper 1080 left, camera 840 right), 1920 paper only
  // (the stage glides to the centre). layout.w: spring stiffness (9 = a calm half-second move).
  // Default 0 + glass panels. 1920 for any schema / board / tree. 1080 only for a long run of sources (10 s+).
  // Never split -> full -> split: one move per idea, 2.5 s apart at least.
  layout: { keys: [[0, 0]] },
  // zoom.keys [[t, z]] slow punch-ins; jump cuts alternate 1 / zoom.punch automatically (zoom.jumps: false to stop it).
  zoom: { keys: [[0, 1]], punch: 1.1 },

  actors: [],
  scenes: [
    // glass(40, 48, [{ k: 'text', text: 'C\'est du bullshit.', size: 62, x: CX, y: 250, at: 40.2, emph: 'bullshit.', emphAt: 40.6, maxW: 540 },
    //               { k: 'img', img: IC('skull'), s: 110, x: CX, y: 420, at: 42.0 }]),
    // { type: 'tweet', layer: 'over', from: 60, to: 66, rect: [GX, 250, GW], size: 30, photo: true, ... },   // a tweet LEFT of him on full camera
    // { type: 'title', from: 70, to: 74, lines: [{ text: 'Chapitre 1', at: 70 }, { text: 'Le sujet', at: 70.6, emph: 'sujet' }] },
    // { type: 'cta', layer: 'over', from: 400, clickAt: 401.4, y: 900 },
  ],
  broll: [],   // [{ media, from, to, offset, focus, zoom }] full-screen 1920x1080 over everything

  music: { chapters: [[0, 'enquete']] },   // [[at, bedId]] one bed per chapter, 2 s crossfade at each `at`
  mix: { music: -30 },   // long-form: the bed sits further under the voice

  captions: { on: false, size: 52, replace: [], emph: [], hide: [] },   // YouTube CC carries the words; on: true for small stickers
};
// house icon tiles carry their own depth: no drop shadow
for (const s of window.SPEC.scenes) for (const it of s.items || []) if (it.k === 'img' && it.img.startsWith('assets/icons/')) it.shadow = false;
