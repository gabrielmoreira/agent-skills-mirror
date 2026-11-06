// Short: "Annule ton abonnement Codex : Anthropic donne 5,6x plus de valeur". All times are SOURCE seconds (files/words.md).
// Proof = the SemiAnalysis charts posted by @scaling01 ("this is brutal", Oct 5 2026): the real image is shown in a
// `screen` window with zooms and rings on the numbers the creator reads, and a big native counter under it for mobile.
const L = { codex: 'assets/logos/codex.png', claude: 'assets/logos/claude.png', openai: 'assets/logos/openai.png', spacex: 'assets/logos/spacex-word.png', ferrari: 'assets/logos/ferrari.png', semi: 'assets/images/av-semianalysis.jpg' };
const CHART = 'assets/images/value-by-plan.jpg';   // 2048 x 1161, rects below are in these px
const R = {
  claude200: [1753, 473, 236, 49],   // $11,726 58.6x
  gpt200: [635, 389, 205, 41],       // $2,084 10.4x
  gpt100: [517, 620, 205, 41],       // $1,055 10.6x
  claude100: [1058, 707, 205, 41],   // $5,725 57.3x
};

window.SPEC = {
  title: 'Annule ton abonnement Codex',
  media: {
    avScaling: { src: 'assets/images/av-scaling01.jpg', width: 176 },
    chart: { src: 'assets/images/value-by-plan.jpg', width: 1080 },
  },
  cam: { crop: [532, 0, 1200, 1080], eyes: [575, 445], splitZoom: 1.25 },   // eyes +20 px and a tighter card: the red and green wall poster stays out of the card edge
  grade: true,                                            // cooler, brighter face (the room light is warm and dim)
  cut: [[78.0, 80.36]],                                   // "c'est devenu Space-- c'est, c'est," stutter

  layout: { frame: true, keys: [
    [0, 960],        // hook: Codex subscription, struck
    [12.70, 1240],   // the tweet, then the real chart with zooms
    [33.88, 960],    // native bars: 5,6x more
    [43.50, 1240],   // the $100 plan on the chart
    [56.34, 0],      // full screen, direct address: "il faut à tout prix utiliser un abonnement Anthropic, les amis"
    [62.84, 1240],   // the ostrich buries its head, then wakes up
    [70.80, 1240],   // Codex = Ferrari, Claude Code = SpaceX rocket
  ] },

  actors: [],

  scenes: [
    // 1. hook: a study, cancel your Codex plan
    { type: 'board', from: 4.70, to: 12.60, pre: .8, items: [
      { k: 'logo', logo: L.semi, s: 84, x: 360, y: 300, at: 4.70, pre: .8 },
      { k: 'text', text: 'SemiAnalysis', size: 54, align: 'left', x: 420, y: 300, at: 4.70, pre: .75 },
      { k: 'card', x: 140, y: 400, w: 800, h: 400, at: 4.70, pre: .7 },
      { k: 'logo', logo: L.codex, s: 170, x: 540, y: 535, at: 4.70, pre: .65, dimAt: 7.74 },
      { k: 'text', text: 'Abonnement Codex', size: 64, x: 540, y: 710, at: 4.70, pre: .6, strikeAt: 7.42, strikeW: 620 },
    ] },

    // 2. the tweet with the real chart
    { type: 'tweet', from: 12.70, to: 15.62, rect: [60, 230, 960], avatar: 'avScaling', name: 'Lisan al Gaib', handle: '@scaling01',
      text: 'this is brutal', size: 44, media: 'chart', mediaAr: 1161 / 2048,
      footer: '8:33 PM · Oct 5, 2026 · **138.2K** Views' },

    // 3. $200 plans on the real chart: Claude 11 726 $ (58,6x), then ChatGPT 2 084 $ (10x)
    { type: 'board', from: 15.70, to: 33.80, items: [
      { k: 'screen', img: CHART, x: 540, y: 540, w: 960, h: 600, at: 15.70, morph: true,   // grows out of the tweet's image
        viewKeys: [[15.70, [1024, 580, 1]], [16.46, [1180, 455, 1.25]], [18.04, [1500, 480, 1.9]], [26.78, [1100, 455, 1.25]], [28.54, [760, 430, 1.9]]],
        rings: [{ at: 18.04, to: 26.70, rect: R.claude200 }, { at: 29.42, rect: R.gpt200 }] },
      { k: 'logo', logo: L.claude, s: 110, x: 150, y: 1010, at: 16.46, to: 26.70,   // enters centered on "à deux cents euros", glides left for the count
        posKeys: [[16.46, [540, 1010]], [17.10, [150, 1010]]], scaleKeys: [[16.46, 1.3], [17.10, 1]], posW: 12 },
      { k: 'counter', value: 11726, suffix: ' $', size: 150, depth: 1, align: 'left', x: 240, y: 1010, at: 18.04, to: 22.8, countFrom: 18.04, countTo: 20.08 },
      { k: 'text', text: '×58,6', size: 150, depth: 1, color: 'blue', align: 'left', x: 240, y: 1010, at: 23.08, to: 26.70 },
      { k: 'logo', logo: L.openai, s: 110, x: 150, y: 1010, at: 28.10,   // same move on "l'abonnement OpenAI"
        posKeys: [[28.10, [540, 1010]], [28.85, [150, 1010]]], scaleKeys: [[28.10, 1.3], [28.85, 1]], posW: 14 },
      { k: 'counter', value: 2084, suffix: ' $', size: 150, depth: 1, align: 'left', x: 240, y: 1010, at: 29.42, to: 32.6, countFrom: 29.42, countTo: 31.04 },
      { k: 'text', text: '×10', size: 150, depth: 1, align: 'left', x: 240, y: 1010, at: 33.08 },
    ] },

    // 4. native bars: Opus 5.5 gives 5,6x more usage
    { type: 'board', from: 33.88, to: 43.40, items: [
      { k: 'text', text: 'Valeur pour 200 $/mois', size: 56, x: 540, y: 260, at: 33.88 },
      { k: 'bar', x: 90, y: 415, w: 900, h: 90, value: 1, blue: true, logo: L.claude, label: 'Opus 5.5', valueText: '11 726 $', at: 34.50, fillFrom: 34.60, fillTo: 35.60 },
      { k: 'bar', x: 90, y: 605, w: 900, h: 90, value: 2084 / 11726, dark: true, logo: L.openai, label: 'GPT-6.1 Sol', valueText: '2 084 $', at: 34.70, fillFrom: 34.90, fillTo: 35.60 },
      { k: 'text', text: "5,6× plus d'usage", emph: '5,6×', size: 84, x: 540, y: 775, at: 38.94 },
    ] },

    // 5. same on the $100 plan
    { type: 'board', from: 43.50, to: 57.10, items: [
      { k: 'screen', img: CHART, x: 540, y: 540, w: 960, h: 600, at: 43.50,
        viewKeys: [[43.50, [1024, 580, 1]], [45.42, [1100, 680, 1.3]], [49.30, [890, 684, 1.9]]],
        rings: [{ at: 50.48, to: 52.70, rect: R.gpt100 }, { at: 52.74, rect: R.claude100 }] },
      // one hero number at a time in the same slot, like the $200 plan: OpenAI, then Claude
      { k: 'logo', logo: L.openai, s: 110, x: 150, y: 1010, at: 50.20, to: 52.50 },
      { k: 'counter', value: 1055, suffix: ' $', size: 150, depth: 1, align: 'left', x: 240, y: 1010, at: 50.48, to: 52.50, countFrom: 50.48, countTo: 51.36 },
      { k: 'logo', logo: L.claude, s: 110, x: 150, y: 1010, at: 52.74 },
      { k: 'counter', value: 5725, suffix: ' $', size: 150, depth: 1, align: 'left', x: 240, y: 1010, at: 52.74, countFrom: 52.74, countTo: 54.34 },
    ] },

    // 6. "arrêtez de faire les autruches": head in the sand, then "réveillez-vous et switchez" -> Claude
    { type: 'board', from: 62.84, to: 70.70, items: [
      { k: 'ostrich', s: 1, x: 455, y: 1010, at: 63.04, downFrom: 64.70, downTo: 65.70, upAt: 66.56 },
      { k: 'logo', logo: L.claude, s: 150, x: 830, y: 400, at: 67.88 },
    ] },

    // 7. Codex was the Ferrari, Claude Code is the SpaceX rocket: one column each, the object over its brand
    { type: 'board', from: 70.80, items: [
      // Codex opens as the hero, centered, then steps into its column when the Ferrari arrives
      { k: 'logo', logo: L.codex, s: 140, x: 290, y: 290, at: 70.80, dimAt: 76.58,
        posKeys: [[70.80, [540, 560]], [74.02, [290, 290]]], scaleKeys: [[70.80, 1.7], [74.02, 1]] },
      { k: 'text', text: 'Codex', size: 52, x: 290, y: 430, at: 70.90, dimAt: 76.58,
        posKeys: [[70.80, [540, 800]], [74.02, [290, 430]]], scaleKeys: [[70.80, 1.5], [74.02, 1]] },
      { k: 'ferrari', s: .82, x: 290, y: 930, at: 74.20 },
      { k: 'logo', logo: L.ferrari, s: 96, x: 290, y: 1060, at: 74.40 },
      { k: 'logo', logo: L.claude, s: 140, x: 790, y: 290, at: 77.30 },
      { k: 'text', text: 'Claude Code', size: 52, x: 790, y: 430, at: 77.30 },
      { k: 'starship', s: .6, x: 790, y: 755, at: 77.66, igniteAt: 80.96, liftFrom: 82.18, liftTo: 84.0, liftY: 100 },
      { k: 'img', img: L.spacex, s: 330, h: 50, x: 790, y: 1060, at: 81.26 },
    ] },
  ],

  music: { bed: 'enquete', offset: 10.7 },

  captions: {
    replace: [
      ['deux cents euros', '200 €'],
      ['onze mille sept cent vingt-six dollars', '11 726 $'],
      ['cinquante-huit virgule six fois', '58,6 fois'],
      ['deux mille quatre-vingt-quatre dollars', '2 084 $'],
      ['dix', '10'],
      ['au plus cinq point cinq', 'Opus 5.5'],
      ['cinq virgule six fois', '5,6 fois'],
      ['cent dollars', '100 $'],
      ['mille cinquante-cinq', '1 055 $'],
      ['cinq mille sept cent vingt-cinq dollars', '5 725 $'],
    ],
    emph: ['Codex', '11 726 $', '58,6 fois', '5,6 fois', '5 725 $', 'switchez', 'SpaceX'],
    hide: [[18.0, 20.4], [23.0, 25.1], [29.4, 31.4], [33.0, 33.8], [50.4, 51.4], [52.7, 54.6]],   // the big number on screen already says it
  },
};
