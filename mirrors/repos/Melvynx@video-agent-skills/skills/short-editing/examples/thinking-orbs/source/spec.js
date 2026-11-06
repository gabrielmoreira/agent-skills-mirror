// Thinking Orbs (style hard-cuts): hard cuts between full camera (0), split (1160) and paper alone (1920).
// Every time is SOURCE seconds (files/words.md maps them to the short). Components: source/<name>.html -> assets/<name>.mov.
window.SPEC = {
  title: 'Thinking Orbs',
  media: {
    hookOrb: { src: 'assets/hook-orb.mov', width: 1080, alpha: true },
    repoCard: { src: 'assets/repo-card.mov', width: 1080, alpha: true },
    orbGrid: { src: 'assets/orb-grid.mov', width: 1080, alpha: true },
    orbChips: { src: 'assets/orb-chips.mov', width: 1080, alpha: true },
    claudeRows: { src: 'assets/claude-rows.mov', width: 1080, alpha: true },
    summaryPill: { src: 'assets/summary-pill.mov', width: 1080, alpha: true },
    perf: { src: 'assets/perf-60fps.mov', width: 1080, alpha: true },
    reduceMotion: { src: 'assets/reduce-motion.mov', width: 1080, alpha: true },
    mit: { src: 'assets/mit-license.mov', width: 1080, alpha: true },
    proCard: { src: 'assets/pro-card.mov', width: 1080, alpha: true },
    igCta: { src: 'assets/ig-cta.mov', width: 1080, alpha: true },
  },
  cam: { crop: [322, 0, 1200, 1080], eyes: [601, 443] },
  cut: [[0, 3.40], [24.0, 26.85], [35.78, 36.38], [42.95, 99]],

  layout: { keys: [
    [0, 1160],        // A hook: the big orb, "Ton spinner est mort"
    [5.88, 0],        // B "vient de les passer en open source"
    [7.68, 1160],     // C repo card + npm
    [9.94, 1920],     // D grid of the 9 orbs
    [12.46, 1160],    // E ton app / ton site / ton produit
    [15.20, 0],       // F "Dès que ton interface fait attendre"
    [17.74, 1160],    // G Claude rows, spinners -> orbs
    [21.48, 1920],    // H Generating summary, light then dark
    [26.90, 1160],    // I 60 fps
    [28.98, 1920],    // J reduced motion freezes the orb
    [32.36, 1160],    // K MIT, sell copies
    [34.88, 0],       // L "Donc tu peux les mettre dans un produit"
    [37.04, 1160],    // M Pro 29 €/mois, En prod
    [39.86, 0],       // N CTA: face + Instagram
  ] },
  zoom: { keys: [[0, 1],
    [5.88, 1.08, 400], [6.76, 1.13, 400], [7.68, 1, 400],      // "open"
    [15.20, 1.08, 400], [16.30, 1.13, 400], [17.74, 1, 400],   // "attendre"
    [34.88, 1.08, 400], [36.70, 1.13, 400], [37.04, 1, 400],   // "produit"
    [39.86, 1, 400],
  ] },

  actors: [],
  scenes: [
    { type: 'overlay', media: 'hookOrb', from: 0, to: 5.88 },
    { type: 'overlay', media: 'repoCard', from: 7.68, to: 9.94 },
    { type: 'overlay', media: 'orbGrid', from: 9.94, to: 12.46 },
    { type: 'overlay', media: 'orbChips', from: 12.46, to: 15.20 },
    { type: 'overlay', media: 'claudeRows', from: 17.74, to: 21.48 },
    { type: 'overlay', media: 'summaryPill', from: 21.48, to: 26.90 },
    { type: 'overlay', media: 'perf', from: 26.90, to: 28.98 },
    { type: 'overlay', media: 'reduceMotion', from: 28.98, to: 32.36 },
    { type: 'overlay', media: 'mit', from: 32.36, to: 34.88 },
    { type: 'overlay', media: 'proCard', from: 37.04, to: 39.86 },
    { type: 'overlay', media: 'igCta', from: 39.86, to: 42.95, layer: 'over' },
  ],

  // Arpège sombre: default bed for AI tool demos (previous short used code-noir)
  music: { bed: 'arpege', offset: 10.0, breaks: [] },
  mix: { music: -25.5, sfx: -25, duck: .5 },

  sfx: {
    // quiet cues on what each component does (no slide, no whoosh: no movement noise)
    extra: [
      // A hook-orb: 4 state chips
      [3.73, 'pop', .08], [4.13, 'pop', .08], [4.51, 'pop', .08], [4.86, 'pop', .08],
      // C repo-card: name, star, npm keys, MIT badge
      [8.30, 'tap', .04], [8.95, 'tap', .03], [9.06, 'pop', .10], [9.22, 'tap', .03], [9.39, 'tap', .03], [9.60, 'pop', .08],
      // D orb-grid: ring on Searching, Thinking, Listening
      [11.72, 'tap', .05], [11.96, 'tap', .05], [12.26, 'tap', .05],
      // E orb-chips: orb drops in the site, then the product
      [13.94, 'pop', .10], [14.45, 'pop', .10],
      // G claude-rows: 3 cursor clicks, halos
      [18.57, 'tap', .06], [19.32, 'tap', .06], [20.11, 'tap', .06], [20.52, 'pop', .06],
      // H summary-pill: dark wipe, check
      [22.43, 'tap', .04], [23.41, 'pop', .10],
      // I perf: bullets
      [27.29, 'pop', .08], [27.72, 'pop', .08], [27.83, 'pop', .05],
      // J reduce-motion: toggle, ring
      [31.16, 'tap', .07], [31.63, 'pop', .05],
      // K mit: pill
      [33.70, 'tap', .05],
      // M pro-card: Payer click, En prod
      [38.58, 'tap', .06], [38.88, 'pop', .10],
      // N ig-cta: tap, ORBES typed, Publier, posted, DM banner, Suivre
      [39.92, 'tap', .06], [40.34, 'tap', .03], [40.41, 'tap', .03], [40.48, 'tap', .03], [40.55, 'tap', .03], [40.62, 'tap', .03],
      [40.72, 'tap', .06], [40.80, 'pop', .12], [41.04, 'bell', .10], [42.10, 'tap', .06],
    ],
    // designed hits on the payoffs only
    files: [
      { src: 'assets/sfx/impact-boom.mp3', at: 5.20, gain: -15, peak: true },   // A: the spinner is struck ("mort")
      { src: 'assets/sfx/impact-boom.mp3', at: 33.47, gain: -16, peak: true },  // K: "sell copies" highlighted
      { src: 'assets/sfx/unlock.mp3', at: 38.88, gain: -13, peak: true },       // M: "En prod"
    ],
  },

  captions: {
    scaleKeys: [[0, 1.35], [5.88, 1]],
    replace: [['Thinking Orb', 'Thinking Orbs'], ['Commande Orb', 'Commente ORBES'], ['Commande', 'Commente']],
    emph: ['orbes', 'open', 'source.', 'Orbs', 'chaque', 'état', 'spinner', 'orbe', 'design', 'ralentit', 'réduit', 'MIT.', 'payant', 'ORBES', 'repo'],
    hide: [],
  },
};
