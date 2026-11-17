# Reuse texture and particle rendering

Use these helpers when the reference contains moving detailed material, scrolling text, luminous marks or textured breakup. Choose other native representations for other mechanisms. Source images, masks, bounds, timing and movement come from the current reference. The helper contains the reusable rendering code.

## Add the runtime to the editable project

Read `assets/reconstruction.js` in this Skill and save its unchanged contents as `assets/reconstruction.js` through the current revision-protected project save, together with the authored composition. MCP-only clients can read the same source at `openmotion://workflow/recreate/rendercode`. The method reference is `openmotion://workflow/recreate/rendering`.

Load it with a normal script element before the composition script. Resolve its relative URL from that composition. Load images through the pinned engine's asset-readiness contract, then create layers once. Call their `draw(context, time)` methods from the composition's existing seek-safe renderer. Time can run forward, backward or jump. Preserve the engine's timeline, readiness and editable-variable bindings.

```html
<script src="../assets/reconstruction.js"></script>
```

## Move complete texture

Recover the full moving content region as an image or continuous material atlas. Include complete glyphs, line spacing, illumination and texture. Preserve its physical scale when choosing the destination box and `scale`. Select a content-only source region whose movement can be described independently of its surrounding frame. Masks restore stationary boundaries.

```js
const panel = OpenMotionReconstruction.createTextureLayer({
  image: loadedPanelAtlas,
  box: [panelX, panelY, panelWidth, panelHeight],
  scale: displayPixelsPerImagePixel,
  offset: [atlasOriginX, atlasOriginY],
  motion: [[sourceStart, 0, 0], [sourceEnd, travelX, travelY]],
  mask: loadedBoundaryMask,
  edgeFade: [leftFade, topFade, rightFade, bottomFade],
  composite: materialComposite,
  resolution: canvasPixelsPerSceneUnit
});
// In the existing render function:
panel.draw(context, time, visibility);
```

`box` is `[x, y, width, height]` in composition coordinates. `offset` places the image's top-left corner inside the box and preserves crop/padding offsets. `scale` converts image pixels into composition units. `motion` consists of `[seconds, dx, dy]` keys, linearly interpolated with held endpoints. For measured constant speed, use `velocity: [dxPerSecond, dyPerSecond]` and `timeOrigin` instead of motion keys. Positive displacement moves material right/down. Positions and rates use composition units.

`wrapX` and `wrapY` tile a genuinely repeating material. A finite text atlas can expose newly revealed lines by moving inside its clipped box. Use complete sampled letterforms for scrolling text. A content replacement uses the observed whole-region states or editable text content and its timing. Source sampling preserves spatial detail while the native controls supply its movement.

Keep stationary edges, junctions and foreground occluders in their own layers. Fit `mask` to the visible content boundary. `edgeFade: [left, top, right, bottom]` supplies measured soft entrance/exit widths in composition units and defaults to zero. It fades the clipped boundary while the material moves underneath. Use `composite: 'screen'` for a luminous texture that combines with a darker stationary structure when the reference shows that treatment. The default inherits the caller's composite mode. These controls preserve the native scene's depth ordering and prevent a moving crop edge from cutting across a fixed object. A repeated atlas needs a continuous seam in its direction of travel.

## Preserve particle texture and motion exposure

Recover a representative particle sprite with its core, glow, edge texture and streak shape. Isolate the participating source material with alpha where appropriate. Create the field from that material once. Its original colours seed sprite tints, and a shared release field drives the intact-to-fragment handoff.

For unknown mark sizes, brightness or transition timing, use the bundled source observer before choosing ranges. It batches the selected source times and can prepare representative sprite crops in the same call.

```sh
node "<skill directory>/scripts/vision-tools.mjs" observe reference.mp4 \
  --times <release,spread,decay-seconds> --roi <x,y,width,height> \
  --exclude <overlay-x,y,width,height> --sprites-at <clear-particle-seconds> \
  --out source-observations
```

Read the returned summary and source contact sheets. `observations.json` records actual decoded times, foreground coverage, luminance sum, core-size percentiles, connected-structure area and spatial extent. Coordinates and sizes are original source pixels. Set `--threshold`, `--min-area` and `--max-area-fraction` for the visible feature and keep them with the observation. `--matte white` observes dark marks on a light background. A fully blank tail is a valid observation. An unavailable sample or fully excluded region fails explicitly.

Choose a clean sprite from `sprite-candidates.jpg`. Each returned `box` is its thresholded core and `cropBox` includes padding/glow. The renderer's size is the complete sprite width. Convert a desired core width using `spriteWidth = coreWidth * cropBox[2] / box[2]`, then multiply by scene units per source pixel. Keep large coherent fragments distinct from typical marks. Select source times through release, peak spread and decay to set release/lifetime ranges. Use the observed decline in foreground coverage and light to avoid an invented late bloom. Luminance sum includes unexcluded static material, so account for its baseline. Spatial radius constrains the visible envelope. Individual travel needs adjacent-frame observation or the existing source-motion measurer.

```js
const breakup = OpenMotionReconstruction.createParticleField({
  image: loadedSubject,
  sprite: loadedParticle,
  box: [subjectX, subjectY, subjectWidth, subjectHeight],
  pitch: sampleSpacing,
  density: observedCoverage,
  size: [smallestSpriteWidth, largestSpriteWidth],
  release: [0, releaseSpread],
  lifetime: [shortestLife, longestLife],
  speed: [slowestTravel, fastestTravel],
  acceleration: observedAcceleration,
  origin: [localOriginX, localOriginY],
  trail: observedExposureSeconds,
  samples: 3,
  spriteMatte: 'black',
  seed: 17
});
// The editable breakupStart variable changes the whole event:
breakup.draw(context, time - variables.breakupStart, visibility);
```

Distances, sizes and speeds use composition units. `pitch` controls source sampling, `density` controls the fraction of eligible samples emitted, and `size` controls the entire sprite width including its glow. Choose them independently from the reference. `origin` is relative to the subject box. `speed` and `acceleration` move marks radially from it. Source alpha contributes to mark opacity.

`spriteMatte` converts a black or white sprite background to transparency. Use `alpha` for a prepared transparent sprite. `threshold` defaults to 0.04 of source maximum RGB brightness. Use 0 for alpha-isolated dark subjects. `composite` defaults to `lighter` for luminous marks and accepts `source-over` for ink or opaque fragments. `fadeIn`, `fadeOut` and `softness` are seconds. `sizeGrowth` is proportional width growth per second. `trail` and `samples` integrate the sprite along its actual trajectory with conserved sample opacity.

Sprite conversion preserves internal colour and antialiased edges, with the source material tint applied multiplicatively. `preserveEnergy` defaults to true and limits emitted sprite luminance to the sampled source cell's coverage/luminance estimate as sprite size changes. It shares the intact material's release mask. With `threshold: 0`, the estimate uses source alpha coverage for isolated dark material. Set `preserveEnergy: false` only for observed additive light generation. Source-derived release, travel and lifetime still determine where the light goes and when it disappears.

The field's default `dissolve: true` also renders the intact material and its release mask. Use `dissolve: false` when a separate native layer owns that material. Combine independently timed fields for distinct subjects or release regions. Use another native model for observed directional or deforming motion that radial travel cannot represent.

## Derive parameters together

Use the source observations already gathered for the current passage to choose the full content region, coordinate scale, motion keys, particle appearance and release timing. Preserve distinctive thin strokes and bright highlights in source materials. Choose parameter ranges from the visible size, density and movement distributions. Complete the native implementation with these inputs, then follow [export and requested review](verify.md).
