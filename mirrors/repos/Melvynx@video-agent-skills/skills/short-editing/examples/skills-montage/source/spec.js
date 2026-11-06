// Short: "J'ai construit mon propre skill de montage". All times are SOURCE seconds (files/words.md).
const CLAUDE = 'assets/logos/claude.png';
window.SPEC = {
  title: 'Mon propre skill de montage',
  media: {},
  cam: { crop: [264, 0, 1200, 1080], eyes: [600, 739] },
  cut: [],
  layout: { keys: [[0, 1160]] },
  zoom: { keys: [[0, 1]] },
  actors: [],
  scenes: [
    // 1. hook: every editing skill fails in Claude Code
    { type: 'board', from: 0, to: 5.9, pre: .5, items: [
      { k: 'term', cmd: '/montage-video', w: 960, h: 640, size: 48, logo: CLAUDE, name: 'Claude Code', x: 540, y: 560, at: 0, pre: .5, shown: true,
        typeFrom: 0.3, typeTo: 1.3, sendAt: 1.5,
        out: [{ text: '✗ render failed', at: 2.2 }, { text: '✗ ffmpeg: no such file', at: 3.2 }, { text: '✗ timeline is empty', at: 4.6 }] },
    ] },
    // 2. "ils n'hésitent pas à te les vendre": the price, struck on "énervé"
    { type: 'board', from: 6.0, to: 8.4, items: [
      { k: 'counter', value: 97, suffix: ' €', size: 260, x: 540, y: 500, at: 6.1, countFrom: 6.4, countTo: 7.0, strikeAt: 7.7, strikeW: 560 },
      { k: 'chip', text: 'Skill de montage', size: 46, x: 540, y: 760, at: 6.85 },
    ] },
    // 3. "j'ai construit le mien": the folder appears line by line
    { type: 'tree', from: 8.5, to: 11.3, rect: [90, 280, 900], size: 66, lines: [
      { text: 'short-editing/', at: 8.6 },
      { text: '├── engine/', at: 9.4 },
      { text: '├── references/', at: 9.9 },
      { text: '└── SKILL.md', at: 10.15 },
    ] },
    // 4. payoff: this video was edited with it
    { type: 'board', from: 11.36, items: [
      { k: 'logo', logo: CLAUDE, s: 150, x: 540, y: 330, at: 11.36 },
      { k: 'text', text: 'Cette vidéo', size: 96, x: 540, y: 560, at: 11.40 },
      { k: 'text', text: 'montée avec.', emph: 'avec.', emphAt: 12.85, size: 96, x: 540, y: 690, at: 12.69 },
      { k: 'check', s: 90, x: 540, y: 880, at: 13.80 },
    ] },
  ],
  music: { bed: 'arpege', offset: 0 },
  sfx: { swish: 0, accents: 0, extra: [[7.7, 'thud', -6], [13.8, 'thud', -4]] },
  captions: {
    replace: [['clics cloud', 'skills Claude'], ['montées', 'de montage']],
    emph: ['marchent', 'vendre', 'mien.', 'marche.'],
    hide: [[11.36, 13.3]],
  },
};
