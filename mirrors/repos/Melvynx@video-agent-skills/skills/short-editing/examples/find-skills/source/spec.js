// Short: "Le skill Claude que personne utilise" (remake of @jackroberts___ DePtyBoAOPd, same beats): Find Skills, the skill
// that searches the skills.sh library (1M+ skills) and installs the right one for you. #1 on skills.sh, 3.8M installs.
// Style hard-cuts since review v1 (« utilise le style hard-cuts pour la vidéo entière »): the papier look edited in hard
// cuts, one shot every 1.5 to 3 s (split 1160 for the cards, full camera with dry punch-ins on the link phrases, paper alone
// for the big number and the find-skills card), a click / pop / boom kit, bare Phosphor glyphs, real logos.
// Paper components are 960x840 cards captured from source/*.html (sub-agents), the CTA is the Instagram overlay.
// All times are SOURCE seconds (files/words.md); 'o+X' = X s into the outro.
const CARD = [60, 200, 960], AR = 840 / 960;
const L = { claude: 'assets/logos/claude.png', codex: 'assets/logos/codex.png', skills: 'assets/logos/skills-sh.png' };
const G = n => `assets/icons/glyph/${n}.png`, I = n => `assets/images/${n}.png`;

// a composite card (sheet + glyph or logo + label) that moves and scales as one: the children ride the card's origin
// O and scale s (child at O + s * d), so a card can leave its grid slot and grow in the middle of the stage
function unit({ at, to, O, w, h, keys, icon, logo, label, size = 38, layout = 'col', dimAt, ringAt, pop = .8, extra = {} }) {
  const ks = keys || [[at, O, 1]];
  const pos = d => ks.map(([t, o, s]) => [t, [o[0] + s * d[0], o[1] + s * d[1]]]);
  const sc = ks.map(([t, , s]) => [t, s]);
  const base = { at, to, pop, rise: 0, slot: false, quiet: true, dimAt, scaleKeys: sc, posW: 12, ...extra };
  const dI = layout === 'col' ? [w / 2, h * .38] : [h * .5, h / 2], dT = layout === 'col' ? [w / 2, h * .78] : [h * .95, h / 2];
  return [
    { k: 'card', ...base, x: O[0], y: O[1], w, h, r: 30, ringAt, posKeys: pos([0, 0]) },
    icon ? { k: 'img', ...base, img: G(icon), s: h * .36, h: h * .36, shadow: false, x: O[0] + dI[0], y: O[1] + dI[1], posKeys: pos(dI) }
      : { k: 'logo', ...base, logo, s: h * .56, x: O[0] + dI[0], y: O[1] + dI[1], posKeys: pos(dI) },
    { k: 'text', ...base, text: label, size, align: layout === 'col' ? 'center' : 'left', x: O[0] + dT[0], y: O[1] + dT[1], posKeys: pos(dT) },
  ];
}

// C. the skills grid: 3x3 cells 290x170, the video cell (top left) leaves the grid on "celui" and lands in the middle x1.8
const GRID = [['camera', 'video'], ['envelope', 'emails'], ['ant', 'debug'], ['search', 'seo'], ['check', 'tests'],
  ['file', 'pdf'], ['pencil', 'design'], ['shield', 'sécu'], ['folder', 'fichiers']];
const cell = i => [80 + (i % 3) * 315, 300 + Math.floor(i / 3) * 195];

window.SPEC = {
  title: 'Le skill Claude que personne utilise',
  media: {
    skillsPage: { src: 'assets/skills-page.mp4', width: 960 },     // source/skills-page.html: skills.sh/vercel-labs/skills, find-skills types in
    promptDemo: { src: 'assets/prompt-demo.mp4', width: 960 },     // source/prompt-demo.html: Claude prompt box, the best skill rises to the top
    installTerm: { src: 'assets/install-term.mp4', width: 960 },   // source/install-term.html: Claude Code runs npx skills add, check
    leaderboard: { src: 'assets/leaderboard.mp4', width: 960 },    // source/leaderboard.html: skills.sh All Time, find-skills #1, 3.8M
    // source/security.html: SKILL.md read by Claude and Codex, "send data" struck; the 960x840 alpha clip padded to the
    // frame at the card's place (60, 200) for the overlay scene (assets/security.mov -> security-full.mov)
    security: { src: 'assets/security-full.mov', width: 1080, alpha: true },
    igreel: { src: 'assets/ig-reel.mov', width: 1080, alpha: true },   // source/ig-reel.html: FINDER typed in the comments, DMs fall
  },
  cam: { crop: [328, 0, 1200, 1080], eyes: [600, 345] },   // face detected on this take
  // 13.30-15.18 "Claude" restart; 27.90-37.25 the retakes of "le plus fou"; 38.22-38.48 a stumble
  cut: [[13.30, 15.18], [27.90, 37.25], [38.22, 38.48]],
  outro: 2,   // the DMs keep falling on the held last frame

  // hard cuts (style dur 0): split 1160 when a card plays, full camera on the link phrases (punch on the strong word),
  // paper alone (1920) for the million counter and the find-skills card; full camera from "Y a plein de hackers" to the end
  layout: { keys: [
    [0, 1160], [6.02, 0], [7.88, 1160], [10.48, 1920], [15.20, 1160], [17.60, 0], [19.30, 1160], [37.28, 0], [39.14, 1160],
    [42.88, 0], [44.38, 1920], [46.32, 0], [47.98, 1160], [51.24, 0]] },
  zoom: { keys: [[0, 1],
    [6.02, 1.08, 400], [6.46, 1.13, 400], [7.88, 1, 400],          // "presque PERSONNE ne l'utilise"
    [17.60, 1.08, 400], [19.00, 1.12, 400], [19.30, 1, 400],       // "sur quoi tu BOSSES"
    [37.28, 1.08, 400], [37.70, 1.13, 400], [39.14, 1, 400],       // "Et le plus FOU"
    [42.88, 1.08, 400], [43.46, 1.12, 400], [44.38, 1, 400],       // "si tu dois INSTALLER qu'un seul"
    [46.32, 1.08, 400], [47.34, 1.13, 400], [47.98, 1, 400],       // "installe JAMAIS un skill"
    [51.24, 1.08, 400], [51.72, 1.13, 400], [52.44, 1, 400],       // "plein de HACKERS"
    [55.24, 1.08, 400]] },                                         // "du moment que tu me suis"

  // hard cut in and out (cuts: 'hard'); offset = clip seconds skipped when a full-camera shot takes the clip's start
  actors: [
    { id: 'skillsPage', media: 'skillsPage', from: 7.88, to: 10.48, keys: [[7.88, CARD]], ar: AR },
    // starts on the first typed prompt (clip 1.20) right on "genre monter tes vidéos"
    { id: 'promptDemo', media: 'promptDemo', from: 19.30, offset: 1.20, to: 23.74, keys: [[19.30, CARD]], ar: AR },
    { id: 'installTerm', media: 'installTerm', from: 23.74, to: 37.28, keys: [[23.74, CARD]], ar: AR },
    // cut in on "numéro" (clip 1.38, the blue band on row 1), the scroll plays under the full-camera "Et le plus fou"
    { id: 'leaderboard', media: 'leaderboard', from: 39.14, offset: 1.38, to: 42.88, keys: [[39.14, CARD]], ar: AR },
  ],

  scenes: [
    // A. hook, frame 0 = the on-screen hook + the Claude logo as hero (also the cover). The task cards land on
    // "créé le meilleur skill", the magnifier sweeps them (one per beat) and comes back to rest on the logo
    { type: 'board', from: 3.20, to: 6.02, pre: 0, push: 0, items: [
      { k: 'text', text: '1 million de skills,\nun seul.', emph: 'un', at: 3.20, shown: true, x: 540, y: 190, size: 92, slot: false },
      { k: 'logo', logo: L.claude, at: 3.20, shown: true, x: 540, y: 470, s: 210, slot: false },
      ...unit({ at: 3.68, O: [170, 640], w: 740, h: 112, icon: 'camera', label: 'Monter ma vidéo', size: 46, layout: 'row', dimAt: 5.10 }),
      ...unit({ at: 3.84, O: [170, 772], w: 740, h: 112, icon: 'envelope', label: 'Écrire un email', size: 46, layout: 'row', dimAt: 5.36 }),
      ...unit({ at: 4.00, O: [170, 904], w: 740, h: 112, icon: 'ant', label: 'Corriger un bug', size: 46, layout: 'row', dimAt: 5.62 }),
      { k: 'img', img: G('search'), at: 4.46, x: 980, y: 696, s: 150, h: 150, shadow: false, pop: .6, rise: 0, slot: false, quiet: true, posW: 10,
        posKeys: [[4.46, [800, 696]], [4.80, [800, 696]], [5.10, [800, 828]], [5.36, [800, 960]], [5.70, [660, 520]]] },
    ] },

    // A2 (6.02-7.88) "presque personne ne l'utilise": full camera, punch on "personne" (review v1: the empty-shop
    // illustration is gone)

    // B (7.88-10.48): skills-page card. B2. "une bibliothèque de plus d'un million de skills Claude": paper alone, the
    // Claude logo and the flat counter big
    { type: 'board', from: 10.48, to: 15.20, pre: 0, push: 0, items: [
      { k: 'logo', logo: L.claude, at: 10.48, x: 540, y: 520, s: 300, rise: 0, shown: true },
      { k: 'counter', value: 1000000, fromValue: 0, suffix: '+', sep: ' ', at: 10.48, countFrom: 11.06, countTo: 11.90,
        x: 540, y: 960, size: 190, rise: 0, hold: true },
    ] },

    // C. "tu récupères direct celui dont t'as besoin": the grid lands, the video cell leaves it on "celui" and grows in
    // the middle; the others dim
    { type: 'board', from: 15.20, to: 17.60, pre: 0, push: 0, items: [
      // the video cell is drawn last so it rides over the dimmed grid when it grows
      ...[1, 2, 3, 4, 5, 6, 7, 8, 0].flatMap(i => { const [icon, label] = GRID[i]; return unit({
        at: 15.20 + i * .04, O: cell(i), w: 290, h: 170, icon, label, dimAt: i ? 16.32 : undefined,
        keys: i ? null : [[15.20, cell(0), 1], [16.32, cell(0), 1], [16.70, [279, 407], 1.8]], ringAt: i ? undefined : 16.80,
      }); }),
    ] },

    // D (17.60-23.74): prompt-demo card. E (23.74-37.28): install-term card. F (37.28-42.88): leaderboard card.

    // G (review v1: "le motion design ici est moyen"). 42.88 "Donc, si tu dois installer qu'un" full camera, punch on
    // "installer"; 44.38 "seul skill, installe celui-ci" paper alone: the find-skills card slams in big with its
    // 3.8M installs, on "installe" the blue check stamps its corner and the card rings
    { type: 'board', from: 44.38, to: 46.32, pre: 0, push: 0, items: [
      ...unit({ at: 44.38, O: [90, 640], w: 900, h: 240, logo: L.skills, label: 'find-skills', size: 96, layout: 'row', pop: .55,
        ringAt: 45.26 }),
      { k: 'text', text: '3,8M installs', at: 44.38, x: 540, y: 990, size: 64, rise: 0, quiet: true, slot: false },
      { k: 'img', img: G('check'), at: 45.26, x: 960, y: 640, s: 210, h: 210, shadow: false, pop: .45, spin: -.4, rise: 0, slot: false },
    ] },

    // H. 46.32 "Mais surtout, installe jamais un skill" full camera, punch on "jamais"; 47.98 "sans l'avoir fait relire
    // avec Claude, Codex, pour vérifier que c'est safe": the SKILL.md check (clip from 1.36, the sheet already landed);
    // 51.24 "Y a plein de hackers" full camera, punch on "hackers"
    { type: 'overlay', media: 'security', from: 47.98, offset: 1.36, to: 51.24 },

    // I. "Tu le veux ? Commente FINDER": full camera + the Instagram overlay over it (comments, FINDER typed, DMs fall)
    { type: 'overlay', layer: 'over', media: 'igreel', from: 52.75 },
  ],

  // tension, curiosity: "the best skill nobody uses" is a secret; the last shorts used arpege and filature-soft
  music: { bed: 'code-noir', offset: 9.8 },

  sfx: {
    swish: 0, accents: 0,
    // the hook whoosh the creator picked (podcast style's zhhh), on frame 1 only (review v2)
    files: [{ at: 0, src: 'assets/sfx/zhhh_ref_transition.wav', gain: -6 }],
    extra: [
      // A: the three task cards, the magnifier
      [3.68, 'pop', .08], [3.84, 'pop', .08], [4.00, 'pop', .08],
      // B2: the counter tops out on "million" (cuts, punch-ins and landed glyphs: the style's sfx.kit)
      [11.90, 'thud', .12],
      // C: the video cell lands in the middle
      [16.70, 'pop', .10],
      // B skills-page: the command block selected
      [9.59, 'tap', .05],
      // D prompt-demo: the video skill rises, the email skill rises, "Meilleur skill"
      [20.51, 'pop', .08], [21.40, 'pop', .08], [22.39, 'pop', .10],
      // E install-term: the payoff check
      [26.66, 'pop', .10],
      // F leaderboard: the #1 pill on "un", the 3.8M counter lands
      [39.64, 'pop', .10], [41.97, 'thud', .12],
      // G: the check stamps the find-skills card
      [45.26, 'thud', .12],
      // H security: the shield on "safe" (the skull is cut: "hackers" is a full-camera punch)
      [50.75, 'pop', .10],
      // I CTA: taps (comments, field, Publier), FINDER lands, the DM bells
      [53.25, 'tap', .05], [53.65, 'tap', .04], [54.38, 'tap', .05], [54.46, 'pop', .10],
      [55.71, 'bell', .05], [56.74, 'bell', .04], ['o+0.67', 'bell', .04],
    ],
  },

  captions: {
    replace: [['Skill', 'Skills'], ['Commande', 'Commente'], ['Finder', 'FINDER']],
    emph: ['Claude', 'personne', 'million', 'besoin.', 'vidéos', 'emails', "l'installe", 'numéro', 'quatre', 'seul',
      'Codex', 'safe.', 'hackers.', 'FINDER'],
    hide: [],
    yKeys: [[52.75, 1125]],   // above the comments sheet (top edge ~1210)
  },
};
