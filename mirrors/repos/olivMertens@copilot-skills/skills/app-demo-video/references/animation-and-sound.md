# Animation & sound reference (contextualize by client answers)

Every questionnaire answer maps to a concrete knob in the bundled assets. Set
these BEFORE building scenes so the video matches the requested tone, instead of
hand-tuning at the end.

## Sound knobs (`assets/MainVideo.template.jsx`)
- **`BGM_FILE`** — the user's own `public/bgm.mp3`. Never ship copyrighted audio;
  if the user says "no music", delete the `<Audio src={staticFile(BGM_FILE)} />`
  line and ship narration only.
- **`BGM_BASE`** (~0.05) — ducked baseline volume; the voice always sits on top.
- **`BGM_FLARE`** (~0.07–0.11) — brief lift at each scene boundary so the music
  "breathes". Higher = more energetic.
- The envelope also fades in over the first 15 frames and out over the last 25.
- **QA target**: narration mean ≈ −24 to −28 dB
  (`ffmpeg -i out.mp4 -af volumedetect -f null -`). Silence = a wiring mistake.

## Motion knobs
- **Background breathing** (`assets/scene-components.jsx` `BreathingBg`) — always
  on: the radial gradient scales `1 → ~1.07` over ~210 frames. This supplies
  ambient motion, so real screen-recording clips need no Ken-Burns pan.
- **`useKenBurns(sceneDuration, from, to, driftPx, startFrame)`** — gentle zoom +
  drift on screenshot CARDS only (never on text/numbers). Pass the SCENE's own
  duration. Zoom strength `to`: subtle `1.03`, moderate `1.045` (default),
  dynamic `1.07`.
- **`useCinematicIn(delay, fps)`** — spring entrance (scale 1.18→1, blur 10→0).
  Staggered delays (kicker 0, headline 6, subtitle 12, pills 18, card 24) give a
  layered reveal. Keep as-is for calm; the spring already reads well.
- **`SpotlightRing({from,to,startFrame,endFrame})`** — a glowing ring that moves
  to the exact figure the narration is describing. Coordinates are in the
  overlaid screenshot's local pixel space.
- **`useCountUp(from,to,start,end,fps)`** — animate a KPI so it lands exactly when
  the voice says it (light overshoot-then-settle; never blur the digits).
- **`LoadingBar({startFrame,endFrame,label})`** — a processing bar to stage real
  compute time (ingesting a document, scoring) synced to narration, instead of
  cutting straight to the result.
- **Zoom rule**: always `transform-origin` centered on the point of interest —
  fast ramp to a moderate zoom, then a slow drift. Never a pan that pushes content
  out of frame. Vary the pattern between scenes.

## Presets (apply from questionnaire Q4 tone / Q11 intensity)
| Preset | Ken-Burns `to` | Entrance | `BGM_FLARE` | Spotlight / count-up |
| --- | --- | --- | --- | --- |
| **Subtle** (measured) | 1.03 | default spring | 0.07 | rarely |
| **Moderate** (dynamic, default) | 1.045 | default spring | 0.09 | spotlight the one key number |
| **Dynamic** (energetic) | 1.07 | default spring | 0.11 | count-ups + spotlights on KPIs |

## Accent badge (Q12 emphasis)
`ContentScene` accepts a `badge` prop — a small corner pill (e.g. `"+10%"`) on the
screenshot card to spotlight a figure the narration calls out. Use sparingly: one
badge per video usually lands harder than one per scene.

## Burned-in captions (Q13 accessibility / silent viewing / i18n)
All three scenes (`HookScene`, `ContentScene`, `OutroScene`) accept a **`caption`**
prop — one short line per scene rendered as a translucent band above the footer.
It fades in with the scene and does not collide with the screenshot card or footer.
- **Keep it short** — the spoken line or a trimmed version (scenes already map to
  one narration beat). Long captions wrap and crowd the frame.
- **Language is independent of the voice** — narrate in French and caption in
  English (or vice versa) for international/social feeds. Reuse the narration text
  for same-language captions, or supply separate caption text per scene.
- Omit the prop (or pass empty) to render no captions.
- Style knobs are in `CaptionBand` inside `assets/scene-components.jsx`
  (position `bottom: 74`, font size 26, translucent `rgba(6,10,26,0.72)` band).
