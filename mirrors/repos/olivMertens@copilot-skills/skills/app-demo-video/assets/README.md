# Remotion starter — wiring guide

These files are a **turnkey** Remotion project skeleton. Copy them into a folder,
add your generated audio + cropped screenshots, and render.

## One-time setup
```
mkdir my-demo && cd my-demo
mkdir src public
# copy every file from this assets/ folder into src/
#   shared.jsx  helpers.jsx  TransitionWrapper.jsx  scene-components.jsx
#   Root.jsx  index.jsx
# copy the assembly template and DROP the ".template" from its name:
#   MainVideo.template.jsx  ->  src/MainVideo.jsx
# copy package.json into the project root (my-demo/), then:
npm install
```

Folder layout after setup:
```
my-demo/
  package.json
  src/
    index.jsx  Root.jsx  MainVideo.jsx
    scene-components.jsx  shared.jsx  helpers.jsx  TransitionWrapper.jsx
  public/
    narr_*.mp3      # from scripts/generate_tts.py
    *.png           # cropped screenshots (references/screenshot-capture.md)
    bgm.mp3         # your OWN background-music track (never ship copyrighted audio)
```

## Fill in your content
1. Generate narration: `python <skill>/scripts/generate_tts.py ... --out public`.
   Note each clip's printed ffprobe duration.
2. Crop screenshots into `public/` (see `references/screenshot-capture.md`).
3. Edit `src/MainVideo.jsx`: one `SCENES` entry per scene — set `audio`, `img`,
   the copy props, and `duration = ceil(clipSeconds*fps) + ~20`.
4. Provide `public/bgm.mp3` (or set `BGM_FILE`/remove the `<Audio>` if no music).

## Render
```
npx remotion studio  src/index.jsx                                  # live preview
npx remotion still    src/index.jsx Hook out_hook.png --frame=150   # review one scene
npx remotion render   src/index.jsx MainVideo out.mp4 --codec=h264  # final video
```

`Root.jsx` auto-registers one composition per `SCENES` entry (by `id`) plus the
`MainVideo` assembly — no second list to maintain.

## Notes
- Composition is 1920×1080 @ 30 fps (change in `Root.jsx`).
- `.jsx` files use CommonJS/React 19; `package.json` pins the compatible Remotion 4.x.
- Do not commit generated `out*.png`/`out*.mp4` or copyrighted `bgm.mp3`.
