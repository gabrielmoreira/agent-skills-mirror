// Short: "<one-line promise>". All times are SOURCE seconds (read them from files/words.md).
// Parameters: references/scene-library.md. Delete what you don't use.
// Pace (speed, tighten), caption look, music bpm and mix come from source/style.json (the creator style snapshot
// written by `init`). Set a key here only to override it for this one short.
window.SPEC = {
  title: '<title>',
  media: {
    // demo: { src: '~/path/to/clip.mp4', from: 0, dur: 10 },
  },
  cam: { crop: [400, 0, 1200, 1080], eyes: [600, 400] },   // check a source frame, center the face
  cut: [],                                                // [[a, b]] retakes / dead air to drop

  // seam: 960 half, 1240 paper-heavy, 0 full camera. Change it every few seconds.
  layout: { keys: [[0, 960]] },
  zoom: { keys: [[0, 1]] },

  actors: [
    // { id: 'demo', media: 'demo', offset: 0, from: 0.5, to: 6, pre: .45,
    //   keys: [[0.5, [60, 250, 960]]], labelKeys: [[0.5, 'Label']], dot: 'blue' },
  ],

  scenes: [
    // { type: 'stat', from: 6, to: 9, value: 100, suffix: '%', countFrom: 6.4, countTo: 7.1, y: 760, size: 300 },
    // { type: 'title', from: 9, to: 11, lines: [{ text: 'Line one', at: 9 }, { text: 'line two.', at: 9.8, emph: 'two.', emphAt: 10.2 }] },
    // { type: 'cta', layer: 'over', from: 40, clickAt: 41.4, y: 1420 },   // name, sub, button, done: from style.creator; without a profile (or to override) set them here
  ],

  music: { breaks: [] },   // [[a, b]] drums drop (a punchline, a full-camera beat); a library bed instead: src + offset, see references/music.md

  captions: {
    replace: [],
    emph: [],
    hide: [],   // ranges where a scene already shows the words (title, typing, CTA -> [ctaFrom, 99])
  },
};
