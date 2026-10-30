---
name: app-demo-video
description: >-
  Turn a live web app into a narrated demo video and/or a punchy marketing video
  using the Remotion (React) rendering pipeline, from just a URL and a short
  brief. Explores and screenshots the app, writes why/how/value narration,
  generates Azure TTS voice-over, builds spring-animated scene components with
  crossfade transitions, and renders with `npx remotion render`. Ships a
  parameterized scene module, transition wrapper, assembly template and an Azure
  TTS script so it works in any repo. Use for "demo video", "product video",
  "marketing video", "feature-tour video", "app walkthrough video", "narrated
  screencast", "vidéo de démo", "vidéo marketing". Not for editing pre-existing
  footage or non-web apps.
---

# App Demo & Marketing Video Generator (Remotion pipeline)

Reusable end-to-end pipeline to turn a live web app into (a) a narrated
feature-tour **demo** video and/or (b) a short brand-styled **marketing** video,
rendered with **Remotion** (React components + `npx remotion render`/`still`,
not raw ffmpeg compositing).

This package is **self-contained**: copy the bundled `assets/` into your Remotion
`src/` and the `scripts/` TTS generator drives the voice-over. Everything is
project-agnostic — discover the app's real content instead of inventing it.

## Bundled files
- `assets/shared.jsx` — palette, `useCinematicIn` entrance hook, `CroppedVideo`.
- `assets/helpers.jsx` — `useKenBurns`, `useCountUp`, `SpotlightRing`,
  `LoadingBar`, optional `BrandLogo`.
- `assets/scene-components.jsx` — parameterized `HookScene`, `ContentScene`,
  `OutroScene` (one file serves every language and every app).
- `assets/TransitionWrapper.jsx` — crossfade + zoom + blur wrapper.
- `assets/MainVideo.template.jsx` — assembly template (Series + per-scene audio
  + ducked background-music envelope + `TOTAL_DURATION`).
- `assets/Root.jsx`, `assets/index.jsx`, `assets/package.json`,
  `assets/README.md` — turnkey Remotion project skeleton (copy in, `npm install`,
  render). `Root.jsx` auto-registers every scene + the assembly.
- `scripts/generate_tts.py` + `scripts/clips.example.json` — Azure Speech
  narration generator (one multilingual voice can speak several languages).
- `references/visual-language.md` — the house style spec.
- `references/screenshot-capture.md` — capture + crop workflow and gotchas.
- `references/animation-and-sound.md` — tunable motion/audio knobs + tone presets.

## 0. Gather the brief (ask only what's missing)
- **App URL** (+ login credentials if gated — ask, don't guess).
- **Video type(s)**: demo (feature tour; favor completeness) or marketing
  (short punchy, ~45–100s unless told otherwise).
- **Brand colors / logo** for a marketing video (ask for hex codes or a
  reference asset — never invent a brand identity; override `assets/shared.jsx`).
- **Language + voice** (see the `exec-demo-video` skill's voice catalog; a single
  multilingual voice can cover a FR+EN pair via SSML `<lang>`).
- **Reference video** (optional): fetch and study its cut rhythm before building.
- **Background music & animation intensity**: ask whether the user provides a
  music track (or wants none), and how energetic the motion should be (subtle /
  moderate / dynamic). Map both to concrete knobs via
  `references/animation-and-sound.md`. Never ship copyrighted audio.
- **Burned-in captions (optional)**: ask if on-screen captions are wanted and, if
  so, in which language (independent of the voice). Each scene takes a `caption`
  prop; see `references/animation-and-sound.md`.
- Any concrete "why this exists" business context — use it verbatim in the intro.

## 1. Explore & screenshot the app
Follow `references/screenshot-capture.md`. Fix the viewport to one resolution for
the whole project, tour every screen, capture full-page PNGs, then crop tight and
enlarge. Read real pixel dimensions before computing any crop rect. Handle
export/upload-gated screens and i18n bugs honestly (never fake a capture). Put
cropped cards in the Remotion `public/` folder.

## 2. Write the narration (why → how → value)
- Open with a dedicated intro scene (what the app is for, who uses it) before
  touring features.
- Each clip: why the feature exists, how it works (name the underlying tech), the
  value (time saved, risk caught, compliance gained). ~8–18s spoken per scene;
  one screenshot ↔ one narration beat. If a feature needs more, split into two
  scenes.
- Never let narration paraphrase text already on screen at that moment.
- Store narration per scene (a table or a JSON manifest) so it is reviewable and
  regeneratable, and so exact per-clip text drives durations later. See the
  standing content rules in `references/visual-language.md`.

## 3. Generate TTS narration — BEFORE building scenes
1. Refresh an AAD token (see header of `scripts/generate_tts.py`).
2. Fill a clips manifest (`scripts/clips.example.json` is the template) with
   `{id, lang, text}` per clip.
3. Run:
   ```
   python scripts/generate_tts.py --manifest clips.json \
     --endpoint https://<resource>.cognitiveservices.azure.com \
     --voice <voice-name> --out <remotion>/public
   ```
   The script writes one MP3 per clip and prints each clip's **real ffprobe
   duration** — this drives `durationInFrames`, never a guess. A near-empty file
   is an error body; the script surfaces it.

## 4. Build the Remotion scenes
- New project? Follow `assets/README.md` to stand up the turnkey skeleton (copy
  the `assets/` files into `src/`, rename `MainVideo.template.jsx` → `MainVideo.jsx`,
  `npm install`). `Root.jsx`/`index.jsx`/`package.json` are provided.
- Feed copy to `HookScene`/`ContentScene`/`OutroScene` via props — do **not**
  duplicate a component per language.
- Follow the layout, palette, entrance, `marginTop:28`, footer and Ken-Burns
  conventions in `references/visual-language.md`.
- `Root.jsx` already registers every scene AND the assembly as `<Composition>`s
  (individual scenes for still review; the assembly is the deliverable).

## 5. Wire transitions & audio
Adapt `assets/MainVideo.template.jsx`: one `Series.Sequence` per scene, each with
`offset={i===0?0:-TRANSITION_OVERLAP}`, `<TransitionWrapper>`, and a sibling
`<Audio>`. **Scene duration = `ceil(clipSeconds*fps) + ~20`** (the ~20-frame tail
avoids cutting off the last word). `TOTAL_DURATION = Σ duration − (n−1)·overlap`.
Set the music/motion knobs (`BGM_BASE`/`BGM_FLARE`, Ken-Burns strength, spotlight/
count-up/processing bars) from the brief per `references/animation-and-sound.md`.

## 6. Scene-by-scene review (don't batch)
Build one scene → register it → render a still
`npx remotion still src/index.jsx <SceneId> out_still.png --frame=150` → view it
and get approval before the next scene. Then render a transition-boundary still
to confirm the crossfade blends (keep overlap ~10 frames; 15+ garbles).

## 7. Full render & QA
- `npx remotion render src/index.jsx <Assembly> out.mp4 --codec=h264` (several
  minutes for 1500+ frames — wait for `Stitching N/N` + the `+ output` line).
- `ffprobe` the mp4 duration ≈ `TOTAL_DURATION/fps`.
- `ffmpeg -i out.mp4 -af volumedetect -f null -` — confirm narration present at a
  healthy mean level (silence/near-0KiB audio = a wiring mistake in the assembly).
- Extract and view the first frame, last frame, and one transition boundary.

## 8. Cleanup & deliver
Delete temporary stills and superseded versions. Report final file paths,
durations, and a short changelog. On request, print the full narration transcript
in playback order.

## Reusing for a NEW app
Redo steps 1–2 (never reuse another project's screenshots, colors or narration).
Reuse the mechanical pipeline (assets + steps 3–7) as-is. Ask for brand
colors/logo and duration constraints up front — never invent a brand identity.
