// Short: "La librairie UI la plus premium" (remake of @adrien.ninet DeO7DugISSR), style hard-cuts + mix.
// Kitchen by dqnamo (dqnamo.com/kitchen), every component shown in its real capture (source/rec/rec.mjs).
// Hard cuts between split 1160 (a component on the paper), full camera 0 (link phrases, dry punch-in on the strong
// word) and paper alone 1920 (the big objects: the grid, the toque, the receipt printer, the tactile button, the
// GitHub repo, Claude Code). One B-roll on « trop facile » (the creator walking into a kitchen, laughing). CTA = full camera
// + the Instagram Reels overlay with KITCHEN typed. All times are SOURCE seconds (files/words.md).
const clip = (src) => ({ src, width: 1080, alpha: true });
const cap = (src, dur) => ({ src: `assets/media/${src}.mp4`, from: 0, dur, width: 1080 });
const P = 400;   // spring stiffness of an instant punch-in
const IMG = n => `assets/images/paper/${n}.png`;
window.SPEC = {
  title: 'La librairie UI la plus premium',
  media: {
    receipt: cap('receipt-c', 7.5), grid: cap('grid-c', 8), cassette: cap('cassette', 7), hold: cap('hold-c', 6.5),
    tactile: cap('tactile-c', 4.5), home: cap('home-c', 4.5), ghrepo: cap('ghrepo-c', 5.5), code: cap('code-c', 4.5),
    igcta: clip('assets/ig-cta.mov'),
    // B-roll library: b0374ad47 (the creator walks into a bright kitchen, laughing)
    easy: { src: 'B-roll/kitchen-walk.mp4', from: .4, dur: 2.0, fill: true },
  },
  broll: [{ media: 'easy', from: 37.42, to: 39.30, zoom: .03 }],
  cam: { crop: [348, 0, 1200, 1080], eyes: [599, 391] },
  cut: [],
  // one shot every 1.2-2.8 s (short time)
  layout: { keys: [
    [0, 1160], [8.06, 1920], [9.72, 1160], [11.16, 0], [13.00, 1920], [14.78, 1160], [24.40, 1920],
    [27.88, 0], [30.78, 1920], [33.94, 1160], [35.12, 1920], [39.30, 0]] },
  zoom: { keys: [[0, 1],
    [11.16, 1.08, P], [12.46, 1.12, P], [13.00, 1, P],
    [27.88, 1.08, P], [29.70, 1.13, P], [30.78, 1, P],
    [39.30, 1.04, P], [43.58, 1.1, P], [44.64, 1.04, P]] },
  actors: [
    // hook: the ticket already printing on frame 0, under « Des boutons comme de vrais objets »
    { id: 'receipt0', media: 'receipt', offset: 2.6, from: 0, to: 8.06, pre: 0, ar: 1.409, keys: [[0, [230, 280, 620]]] },
    { id: 'grid', media: 'grid', offset: 1.2, from: 8.06, to: 9.72, pre: 0, ar: .951, keys: [[8.06, [40, 420, 1000]]] },
    { id: 'home', media: 'home', offset: .2, from: 9.72, to: 11.16, pre: 0, ar: .705, keys: [[9.72, [40, 330, 1000]]] },
    { id: 'cassette', media: 'cassette', offset: .6, from: 14.78, to: 20.86, pre: 0, ar: .643, keys: [[14.78, [60, 270, 960]]] },
    // the fill ends on « confirmer »
    { id: 'hold', media: 'hold', offset: .8, from: 20.86, to: 24.40, pre: 0, ar: .391, keys: [[20.86, [30, 480, 1020]]] },
    // « mon préféré » big: the print starts on « imprime »
    { id: 'receipt', media: 'receipt', offset: 1.28, from: 24.40, to: 27.88, pre: 0, ar: 1.409, keys: [[24.40, [90, 170, 900]]] },
    // re-hook « ultra simple »: the Tactile Button pressed
    { id: 'tactile', media: 'tactile', offset: .4, from: 30.78, to: 32.56, pre: 0, ar: .56, keys: [[30.78, [40, 520, 1000]]] },
    { id: 'ghrepo', media: 'ghrepo', offset: .3, from: 32.56, to: 33.94, pre: 0, ar: .98, keys: [[32.56, [40, 300, 1000]]] },
    // the Copy click lands on « copies »
    { id: 'code', media: 'code', offset: 2.0, from: 33.94, to: 35.12, pre: 0, ar: .597, keys: [[33.94, [20, 400, 1040]]] },
  ],
  scenes: [
    { type: 'board', from: 0, to: 9.72, push: 0, items: [
      { k: 'text', text: 'Des boutons comme', at: 0, shown: true, x: 540, y: 130, size: 78, quiet: true, slot: false },
      { k: 'text', text: 'de vrais objets', at: 0, shown: true, x: 540, y: 225, size: 78, emph: 'vrais objets', emphAt: .9, quiet: true, slot: false }] },
    // « aux petits oignons »: the paper toque puts a button on a plate, a chef's kiss on « oignons »
    { type: 'board', from: 13.00, to: 14.78, items: [
      { k: 'img', img: IMG('chef-plate'), at: 13.00, shown: true, x: 470, y: 760, s: 1080, rot: -.03, slot: false },
      { k: 'img', img: IMG('chefs-kiss'), at: 14.12, x: 850, y: 330, s: 360, rot: .1, slot: false }] },
    // the link pasted into Claude Code (real logo)
    { type: 'board', from: 35.12, to: 37.42, push: 0, items: [
      { k: 'term', at: 35.12, x: 540, y: 760, w: 1000, h: 640, size: 28, logo: 'assets/logos/claude.png', name: 'Claude Code',
        cmd: 'Ajoute dqnamo.com/experiments/receipt-printer', focusAt: 35.12, typeFrom: 35.20, typeTo: 36.40,
        sendAt: 36.62, out: [{ text: 'Receipt Printer ajouté', at: 36.95 }], quiet: true, slot: false }] },
    // CTA full camera: KITCHEN typed in the real Reels comments
    { type: 'overlay', layer: 'over', media: 'igcta', from: 39.30, offset: 1.30, to: 99, fade: .15 },
  ],
  music: { bed: 'code-noir', offset: 9.8 },
  glitch: { keys: [[9.72, .4]] },
  sfx: {
    files: [{ at: 9.72, src: 'assets/sfx/zhhh-transition.wav', peak: true, gain: -6 }],
    // the ticket drops (discreet), the tactile presses
    extra: [[27.15, 'pop', .07]],
  },
  captions: {
    style: 'rise', phrase: true, maxWords: 4, maxChars: 18, paperY: 1560,
    replace: [['Cloud Code', 'Claude Code'], ['Commande Kitchen', 'Commente KITCHEN'], ['commande Kitchen', 'commente KITCHEN']],
    hide: [],
    hook: {
      spans: [[0, 9.70], [29.54, 32.56], [39.30, 99]],
      style: 'stack', size: 60, font: 'DM Sans', weight: 900, bigFont: 'Bricolage Grotesque', bigWeight: 800,
      stretch: 'semi-condensed', bigBlock: 'emph', blurIn: true, tuck: true, keyMin: 6, maxWords: 5, maxChars: 32,
      big: 2.4, smallW: 580, stagger: 60, margin: 130,
      fullY: 1250, zoomDrop: 320, paperScale: 1.35, paperColor: '#14161B', split: 'stack', splitScale: .75, splitDy: 110,
      emph: ['premium', 'simple', 'KITCHEN'], yKeys: [[39.30, 1000]],
    },
  },
};
