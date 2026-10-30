# Screenshot capture & crop reference (Playwright + image tooling)

Real screenshots of the running app beat any recreation. Capture with browser
automation (Playwright or equivalent), then crop tight.

## Capture
1. **Log in if gated** — ask for credentials, don't guess. Demo-app sessions
   expire fast: a cached-looking screen can still render while live endpoints
   401. If data looks stale, sign out and back in, then re-verify.
2. **Fix the viewport** to one resolution for the WHOLE project (e.g. 1600×1000).
   Every crop-rect number below assumes a fixed source resolution — mixing
   resolutions breaks every downstream crop.
3. **Tour every screen/tab** systematically. Capture full-page PNGs with
   descriptive names (e.g. `en_transcript.png`, `fr_decision.png`). If the app's
   UI has changed a lot since a prior pass, do a full fresh re-tour — never reuse
   stale screenshots.
4. Identify the single most business-relevant flow and the newest/most
   impressive features — these get priority screen time. Skip About/settings
   unless asked.

## The scale-mismatch gotcha
A screenshot taken at `scale:"css"` can have real pixel dimensions that differ
from what it looks like. **Always read the real dimensions before cropping**:

```powershell
Add-Type -AssemblyName System.Drawing
$img=[System.Drawing.Image]::FromFile($path); "$($img.Width)x$($img.Height)"; $img.Dispose()
```

Then iterate the crop rect against the *real* pixels.

## Crop tight, then enlarge
Remove the top browser-chrome strip and dead bottom whitespace, then size the
card generously in the scene (commonly 1150–1350px wide). Cramped screenshots
are the #1 complaint — go bigger and crop tighter rather than shrinking to fit.

```powershell
Add-Type -AssemblyName System.Drawing
function Crop($src,$dst,$x,$y,$w,$h){
  $img=[System.Drawing.Bitmap]::FromFile($src)
  $rect=New-Object System.Drawing.Rectangle($x,$y,$w,$h)
  $c=$img.Clone($rect,$img.PixelFormat)
  $c.Save($dst,[System.Drawing.Imaging.ImageFormat]::Png); $c.Dispose(); $img.Dispose()
}
Crop "shots\full.png" "public\feature_card.png" 175 250 1235 480
```

## Awkward cases (handle honestly, don't fake)
- **Export/download disabled** (PDF, etc.): replay the export's underlying
  request via `page.evaluate(fetch(url,{...,credentials:'include'}))`, turn the
  response into a Blob, `window.open` it, and screenshot the native viewer.
- **Upload-gated screens** with uploads disabled: substitute a different, genuinely
  real screen that covers the same narrative beat (e.g. a static "How it works"
  panel), and note the substitution in the deliverable summary.
- **i18n bug leaking a raw key** (e.g. `wb.alertes.title`): cosmetically patch it
  by drawing a background-matched rectangle + correct label with
  `System.Drawing.Graphics`, then verify the patch blends before use.

## Placement
Put every cropped card the scenes reference into the Remotion project's
`public/` folder; scenes load them with `staticFile("<name>.png")`.
