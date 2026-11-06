// Short: "Claude vient de tuer Instagram (Insta Skills)". One promise, Instagram from start to finish: Claude as the
// community manager of your account, the free insta-skills (script, edit, DM), then the viral skill on real numbers
// (Treg fetch, my reel's retention drop at 10 s, the competitor reel x31) and the comment CTA « INSTA ».
// style "papier" (paper blue, framed camera, fixed seam 1160), full camera only for the CTA.
// All times are SOURCE seconds (files/words.md).
const WHIP = -1150;
const L = { claude: 'assets/logos/claude.png', ig: 'assets/logos/instagram.png', treg: 'assets/logos/treg.png' };
const I = n => `assets/images/${n}`;
const G = n => `assets/icons/glyph/${n}.png`;

window.SPEC = {
  title: 'Claude vient de tuer Instagram',
  media: {
    githubRepo: { src: 'assets/github-repo.mov', width: 1080, alpha: true },
    staffBadge: { src: 'assets/staff-badge.mov', width: 1080, alpha: true },
    scriptHook: { src: 'assets/script-hook.mov', width: 1080, alpha: true },
    tregFetch: { src: 'assets/treg-fetch.mov', width: 1080, alpha: true },
    igDm: { src: 'assets/ig-dm.mov', width: 1080, alpha: true },
    insights: { src: 'assets/insights-competitor.mov', width: 1080, alpha: true },
    igCta: { src: 'assets/ig-cta.mov', width: 1080, alpha: true },
  },
  cam: { crop: [376, 0, 1200, 1080], eyes: [601, 392] },
  // camera grade for this warm take (wood + lamp): highlights cooled, yellows and a bit of the reds desaturated,
  // brighter mids, solid blacks, natural skin (review: "couleur gradient de ma caméra pas top")
  grade: "colorbalance=rm=-.02:bm=.02:rh=-.05:gh=-.01:bh=.05,huesaturation=saturation=-.35:colors=y,huesaturation=saturation=-.12:colors=r,"
    + "curves=master='0/0 .1/.09 .25/.28 .5/.56 .75/.8 1/1',eq=saturation=.92,unsharp=5:5:.45",
  // 0-3.85 count-in; 30.85-39.08 the "dix mille vues" retake; 48.70-52.15 dead air (the prompter line was not said);
  // 57.38-57.94 doubled "directement"; 61.75+ tail
  cut: [[0, 3.85], [30.85, 39.08], [48.70, 52.15], [57.38, 57.94], [61.75, 99]],

  layout: { keys: [[0, 1160], [48.45, 0]] },
  zoom: { keys: [[0, 1]] },
  shake: { keys: [[4.58, 26, .5]] },

  actors: [],

  scenes: [
    // A. hook, frame 0 = the Instagram logo (also the cover): Claude flies in from the top right and smashes it on "tuer"
    { type: 'board', from: 3.5, to: 5.62, pre: 0, outDx: WHIP, items: [
      { k: 'shatter', logo: L.ig, at: 3.5, x: 540, y: 560, s: 440, breakAt: 4.58, hit: [.28, -.28], shown: true, to: 5.7 },
      { k: 'logo', logo: L.claude, at: 3.98, rise: 0, s: 250, slot: false,
        posKeys: [[3.98, [1260, -240]], [4.04, [324, 800], 5], [4.58, [540, 560], 6], [5.30, [540, 330], 12]],
        scaleKeys: [[3.98, .8], [4.04, 1, 5], [5.30, .8]], rotKeys: [[3.98, -1.6], [4.04, 0, 5]] },
    ] },

    // B. "transformer Claude en community manager de ton compte Instagram": the STAFF badge drops in on its lanyard
    { type: 'overlay', media: 'staffBadge', from: 5.62, to: 9.80 },

    // C. "Ça s'appelle Insta Skills et c'est complètement gratuit": the ink title card turns into the public GitHub repo
    // (drawn, toncompte/insta-skills is not published yet), "gratuit" stamped in blue
    { type: 'overlay', media: 'githubRepo', from: 9.80, to: 12.80 },

    // D. "Un skill écrit tes scripts de reels avec des accroches qui font plus de vues": the hook types and gets highlighted
    { type: 'overlay', media: 'scriptHook', from: 12.80, to: 16.40 },

    // E. "Un autre monte tes rushs dans ton style": the timeline edits itself under Claude
    { type: 'board', from: 16.40, to: 18.75, outDx: WHIP, items: [
      { k: 'logo', logo: L.claude, at: 16.46, x: 540, y: 300, s: 170, pop: .5, slot: false },
      { k: 'edit', at: 16.52, x: 540, y: 700, slot: false,
        imgs: [I('rush-1.jpg'), I('rush-2.jpg'), I('rush-3.jpg'), I('rush-4.jpg'), I('rush-5.jpg')],
        markAt: 17.06, cutAt: 17.45, capsAt: 17.80, fxAt: 18.16, playFrom: 16.60, playTo: 18.75,
        steps: [{ text: 'Rushs coupés', at: 17.45 }, { text: 'Sous-titres', at: 17.80 }, { text: 'Ton style', at: 18.16 }] },
    ] },

    // F. "et un autre répond en DM automatiquement à chaque commentaire": the Instagram DMs that send themselves
    { type: 'overlay', media: 'igDm', from: 18.75, to: 23.55 },

    // G. "Mais le plus fou, c'est le skill de viralité": the 4th skill named big
    // review v3: a big torn paper collage (rocket out of a reel phone) instead of the Phosphor rocket glyph
    { type: 'board', from: 23.55, to: 26.30, outDx: WHIP, items: [
      { k: 'img', img: I('viral-rocket-phone.png'), at: 23.68, x: 540, y: 470, s: 540, h: 806, pop: .6, spin: -.2, rot: -.04, slot: false },
      { k: 'text', text: 'viralité', at: 25.46, x: 540, y: 975, size: 170, color: 'blue', ls: -3, dx: 380, slot: false },
    ] },

    // H. "Il récupère tes vraies stats avec Treg et te compare aux reels qui explosent": Treg in a terminal, toi vs niche x31
    { type: 'overlay', media: 'tregFetch', from: 26.30, to: 39.10 },

    // I+J. "Mon dernier reel : 2 600 vues, les gens partaient à la dixième seconde ... trente fois plus":
    // the real reel stats, the retention drop at 10 s, then the competitor row x31 (handle blurred)
    { type: 'overlay', media: 'insights', from: 39.10, to: 47.50 },

    // K. "et réécrit mon script": the real Recorder on this very script, the view dives onto line 01
    { type: 'board', from: 47.50, to: 48.45, pre: .1, outDx: WHIP, items: [
      { k: 'screen', img: I('rec-prompter.png'), at: 47.52, x: 540, y: 600, w: 1000, h: 625, r: 30, dx: 380, slot: false,
        viewKeys: [[47.52, [720, 450, 1]], [47.84, [736, 228, 1.6]]],
        rings: [{ at: 47.95, to: 48.45, rect: [365, 160, 743, 135], pad: 8 }] },
    ] },

    // L. CTA full camera: "Commente INSTA" typed in the real Reels comments, the DM lands, Suivre -> Abonné(e), install in Claude
    { type: 'overlay', media: 'igCta', from: 48.45, to: 61.75, layer: 'over' },
  ],

  music: { bed: 'enquete', offset: 10.7 },
  // review v1: more dynamic sound (bed and cues up, designed hits on every payoff)
  mix: { music: -25.5, sfx: -25, duck: .5 },

  sfx: {
    extra: [
      // B staff-badge: drop, Claude in the photo slot, the Instagram sticker
      [5.64, 'slide', .10], [6.64, 'pop', .12], [8.72, 'thud', .18],
      // C github-repo: card in, title, card turns into the repo, files stagger, gratuit stamp
      [10.30, 'slide', .10], [10.44, 'pop', .12], [10.96, 'slide', .08], [11.31, 'tap', .04], [11.44, 'tap', .04], [11.53, 'tap', .04],
      [11.66, 'tap', .04], [12.10, 'thud', .16],
      // D script-hook: card in, hook types, marker, ACCROCHE label, views pill
      [12.84, 'slide', .10], [13.50, 'tap', .04], [13.80, 'tap', .04], [14.80, 'tap', .06], [15.10, 'pop', .12], [15.64, 'bell', .10],
      // H treg-fetch: panel in, typing, data rows, stamp, 2nd command, result card, avatars, x31
      [26.37, 'slide', .10], [26.62, 'tap', .04], [26.83, 'tap', .04], [27.42, 'thud', .12], [27.91, 'tap', .05],
      [28.45, 'tap', .04], [28.64, 'slide', .08], [29.09, 'tap', .04], [29.28, 'tap', .04], [30.16, 'pop', .14],
      // F ig-dm: panel in, comment banner, bubble, link card, plane, chip, banners stack, Automatique pill
      [18.80, 'slide', .10], [18.86, 'tap', .06], [19.43, 'slide', .06], [19.92, 'tap', .04], [20.24, 'pop', .12],
      [20.56, 'tap', .05], [21.52, 'tap', .05], [21.77, 'tap', .05], [22.01, 'tap', .05], [22.45, 'thud', .10],
      // I+J insights-competitor: card in, views stop on the ceiling, retention drop, 10 s marker, competitor row, x31
      [39.14, 'slide', .10], [41.06, 'thud', .14], [41.67, 'slide', .06], [43.11, 'tap', .06], [44.27, 'slide', .08],
      [44.79, 'tap', .04], [45.64, 'slide', .06], [46.63, 'pop', .14],
      // L ig-cta: bubble tap, sheet, INSTA typed, Publier, comment posts, like, DM ding, Suivre, 2nd DM, pill, Installé
      [52.95, 'tap', .06], [52.99, 'slide', .06], [53.35, 'tap', .04], [53.44, 'tap', .03], [53.52, 'tap', .03], [53.60, 'tap', .03],
      [53.68, 'tap', .03], [53.76, 'tap', .03], [53.99, 'tap', .06], [54.04, 'pop', .12], [54.25, 'tap', .04],
      [54.94, 'bell', .10], [56.12, 'tap', .06], [59.36, 'slide', .06], [60.59, 'pop', .12],
    ],
    files: [
      { src: 'assets/sfx/whoosh-in.mp3', at: 4.42, gain: -12, peak: true },
      { src: 'assets/sfx/glass-shatter.mp3', at: 4.58, gain: -6, peak: true },
      { src: 'assets/sfx/impact-boom.mp3', at: 4.58, gain: -8, peak: true },
      // a whip on every board / component exit
      ...[5.50, 9.20, 12.36, 15.80, 18.68, 22.90, 26.20, 30.49, 47.03, 48.40].map(at => ({ src: 'assets/sfx/whip.mp3', at, gain: -13, peak: true })),
      // designed hits on the payoffs
      { src: 'assets/sfx/impact-boom.mp3', at: 8.72, gain: -15, peak: true },            // B: the Instagram sticker slams on the badge
      { src: 'assets/sfx/unlock.mp3', at: 12.10, gain: -12, peak: true },                // C: "gratuit" stamp
      { src: 'assets/sfx/impact-boom.mp3', at: 12.10, gain: -14, peak: true },
      { src: 'assets/sfx/riser.mp3', endAt: 25.46, gain: -14 },                          // G: riser into "viralité"
      { src: 'assets/sfx/impact-boom.mp3', at: 25.46, gain: -11, peak: true },
      { src: 'assets/sfx/whoosh-in.mp3', at: 30.10, gain: -13, peak: true },             // H: "x31" lands on "explose"
      { src: 'assets/sfx/impact-boom.mp3', at: 30.16, gain: -11, peak: true },
      { src: 'assets/sfx/impact-boom.mp3', at: 41.06, gain: -16, peak: true },            // I: the views hit the ceiling
      { src: 'assets/sfx/riser.mp3', endAt: 46.63, gain: -15 },                          // J: competitor x31
      { src: 'assets/sfx/impact-boom.mp3', at: 46.63, gain: -11, peak: true },
      { src: 'assets/sfx/whoosh-in.mp3', at: 47.84, gain: -14, peak: true },             // K: dive onto line 01
      { src: 'assets/sfx/zhhh_ref_transition.wav', at: 48.45, gain: -13, peak: true },    // L: into the full-camera CTA
      { src: 'assets/sfx/pop-back.mp3', at: 58.20, gain: -17, peak: true },              // L: 2nd DM, a soft pop (review v2: the bell came back too often)
    ],
  },

  captions: {
    scaleKeys: [[0, 2.1], [5.6, 1]],   // giant hook
    replace: [['Instaskill', 'insta-skills'], ['Insta Skills', 'insta-skills']],
    emph: ['tuer', 'Instagram.', 'community', 'manager', 'Instaskill', 'gratuit.', 'accroches', 'style.', 'DM', 'automatique.',
      'viralité.', 'vraies', 'explose.', 'deux', 'mille', 'dixième', 'trente', 'script.', 'Insta', 'abonné.'],
    hide: [],
  },
};
