# Sound effects

Every sound an edit needs ships with the skill: no account, no API key, no download. Two sources, in this order:

1. **The engine's own sounds**, synthesized in code during the mix. Call them by name: `sfx.extra: [[t, 'thud', gain?]]` (SOURCE time).
2. **The bundled files** in `assets/sfx/` (this skill): the 5 base sounds. Copy the ones a short uses into the project's `assets/sfx/` (or the style's `assets/sfx/`, `init` copies those), then reference them in `sfx.files` or `sfx.kit`.

Generating a new sound with an AI service (ElevenLabs sound effects, ...) is a last resort: only when the creator asks for a sound none of these covers, after telling them it uses their credits.

## The house rule

Hits only on real payoffs. No movement noise on every entrance (whooshes, slides, clicks, tap runs): viewers hate them and so do creators after one listen. A typical short has 2 to 4 sounds besides the music.

## 1. Engine sounds (`sfx.extra`)

| name | sound | when |
|---|---|---|
| `thud` | paper set down on a desk, soft and low | a number lands or dies, a strike, the payoff |
| `pop` | soft woody blip | a real arrival: the logo or the result that matters |
| `bell` | FM bell | a success, a check |
| `tap` | trackpad click | a click shown on screen |
| `tom` | low tom | a heavy beat, a step |
| `slide`, `swish` | paper slide, layout move | movement noise: off by default (`sfx.swish: 0`) |

The scenes add their own cues (a `term` types with key clicks, a `counter` ticks); `sfx.accents` (default 0) adds glassy blips on key moments.

## 2. Bundled files (`assets/sfx/`)

Levelled on their own in the mix: `gain` = dB under the voice (default -10). `peak: true` puts the loudest instant on `at` (impacts). `endAt` makes a riser land on the payoff.

| file | length | use it for | spec |
|---|---|---|---|
| `impact-boom.mp3` | 1.8 s | THE payoff, a big number, a hook verdict | `{at, src, peak: true, gain: -8}` |
| `zhhh.mp3` | 1.1 s | the hook → content cut, with a `glitch` on the same `t` (once or twice a short) | `{at, src, peak: true, gain: -6}` |
| `riser.mp3` | 2.6 s | build-up to a reveal | `{endAt: <reveal>, src, gain: -12}` |
| `glass-shatter.mp3` | 1.6 s | a screen or a logo that breaks (`shatter` item) | `{at: <breakAt>, src, peak: true}` |
| `pop-back.mp3` | 1.0 s | an Instagram UI coming back, a vanish ending | |

The full library (about 20 sounds: coin, unlock, mail ding, stamp, slam, crumple, dust, snip, gears, a hard-cut kit for fast styles...) comes with Editing IA Pro.

## Example

```js
sfx: {
  swish: 0, accents: 0,
  extra: [[7.7, 'thud', -6]],
  files: [
    { at: 2.0, src: 'assets/sfx/zhhh.mp3', peak: true, gain: -6 },
    { at: 13.8, src: 'assets/sfx/impact-boom.mp3', peak: true, gain: -8 },
  ],
},
glitch: { keys: [[2.0, .4, 1]] },
```

Copy the two files first: `cp <skill>/assets/sfx/{zhhh,impact-boom}.mp3 <project>/assets/sfx/`.
