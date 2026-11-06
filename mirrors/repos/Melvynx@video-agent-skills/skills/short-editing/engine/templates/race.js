// Race spec: model A vs model B on the same prompt(s), side by side, live cost + time meters, then the bill.
// Paper-only (silent) motion video. Fill MODELS, ROUNDS and the few strings below; everything else is generated.
// Copy to <project>/source/spec.js, then: prepare -> stills -> render --eco -> audio -> final.
const FORMAT = 'wide';            // 'wide' 1920x1080 (X / YouTube, like the reference race videos) | 'square' 1080x1080 | 'short' 1080x1920
const CLIPS = '~/Movies/Shorts/motion-<slug>/assets/clips/';   // absolute path (~ works) to this project's clips
const MODELS = [
  { name: 'GPT-6.1 Sol', logo: 'openai', effort: 'medium' },   // logos: 'openai' | 'claude' | 'codex'; effort = reasoning effort, always shown
  { name: 'Opus 5.5', logo: 'claude', effort: 'medium' },
];
// One round per test. clips = [modelA, modelB] (file names in CLIPS), cost in $, time in seconds (real run duration).
const ROUNDS = [
  { task: '3D car crash', clips: ['3d-car-crash-a.mp4', '3d-car-crash-b.mp4'], cost: [0.51, 0.90], time: [1149, 3118] },
];
const CLIP_W = 1440;              // clips must be recorded at >= 1440 wide (1440x900), smaller = blurry panels on 1920
const FOOTER = 'Same prompt · medium effort · API prices';
const ROUND = 8;                  // seconds per round (the clip keeps playing after the meters stop)
const OUTRO = true;               // total bill bars + closing question when there are 2+ rounds

// ---------------------------------------------------------------- generated
const media = {}, scenes = [];
const ratio = (a, b) => (Math.max(a, b) / Math.min(a, b)).toFixed(1).replace(/\.0$/, '') + '×';
let t = 0;
ROUNDS.forEach((r, i) => {
  const a = t, b = a + ROUND, cheap = r.cost[0] <= r.cost[1] ? 0 : 1;
  r.clips.forEach((c, j) => { media[`r${i}m${j}`] = { src: CLIPS + c, width: CLIP_W }; });
  scenes.push({
    type: 'race', from: a, to: b - .1, pre: i === 0 ? .5 : .15,
    header: { text: ROUNDS.length > 1 ? `${i + 1}/${ROUNDS.length} · ${r.task}` : r.task, at: a },
    footer: { text: FOOTER, at: a },
    countFrom: a + .5, countTo: a + ROUND * .5, winnerAt: a + ROUND * .5 + .4,
    chip: { text: `${MODELS[cheap].name}: ${ratio(...r.cost)} cheaper`, at: a + ROUND * .5 + .8 },
    panels: MODELS.map((m, j) => ({ ...m, effort: m.effort && `${m.effort[0].toUpperCase() + m.effort.slice(1)} effort`, media: `r${i}m${j}`, cost: r.cost[j], costSuffix: r.suffix?.[j] || '', time: r.time?.[j] })),
  });
  t = b;
});
if (OUTRO && ROUNDS.length > 1) {
  const tot = MODELS.map((_, j) => ROUNDS.reduce((s, r) => s + r.cost[j], 0)), max = Math.max(...tot), lo = tot.indexOf(Math.min(...tot));
  const a = t, H = FORMAT === 'short' ? 1920 : 1080;
  scenes.push(
    { type: 'bars', from: a, to: a + 5, y: H / 2 - 120,
      tags: [{ text: `Total bill · ${ROUNDS.length} tests`, at: a + .1 }],
      rows: MODELS.map((m, j) => ({ label: `${m.name}${m.effort ? ` (${m.effort})` : ''} · $${tot[j].toFixed(2)}`, value: tot[j] / max, at: a + .3 + j * .6, blue: j === lo, dark: j !== lo })),
      gapAt: a + 2, gapChip: { text: `${ratio(...tot)} cheaper`, at: a + 2.4 } },
    { type: 'title', from: a + 5.2, y: H / 2 - 60, size: 110, lines: [
      { text: 'Which one', at: a + 5.3 }, { text: 'would you ship?', at: a + 5.7, emph: 'ship?', emphAt: a + 6.2 }] },
  );
  t = a + 8.5;
}

window.SPEC = {
  title: `${MODELS[0].name} vs ${MODELS[1].name}`,
  format: FORMAT === 'short' ? undefined : FORMAT,
  silent: true,
  duration: t,
  media,
  layout: { keys: [[0, FORMAT === 'short' ? 1920 : 1080]] },
  scenes,
  music: { bpm: 112 },
  mix: { music: -24, sfx: -27, ceil: -2.2 },
};
