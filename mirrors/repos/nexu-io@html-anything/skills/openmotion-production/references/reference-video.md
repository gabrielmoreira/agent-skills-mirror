# Read and measure a reference video

This is the shared method for entries that rebuild an actual reference video. It covers obtaining and reading the reference, measuring it with the pinned CLI, choosing an editable representation and checking fidelity to the source. The selected entry owns its intent judgement, the extent of comparison and repair, where observations are recorded and how the result is delivered. Learn from observable behaviour rather than guessing the original author's code.

## Obtain the reference

For a link, obtain a local decodable copy using the host's available capabilities; no particular downloader is a prerequisite. Keep the URL and the file's checksum. Links and local files then take the same route. If the video cannot be obtained or decoded, report that specific blocker instead of guessing from a cover, thumbnail or description. A cover image or an unreachable link is not a viewed video; never claim to have watched it.

A catalog guidance package returned by `openmotion_get_template` without editable project files links its reference video in the instructions; obtain that video as above. Its motionDocument and the `manifest.json`, `timeline.json`, `tracks.json` and `style.json` files in its source (local paths for repository entries, the Studio `/api/template-source/<id>/<file>` route for hosted ones) record canvas, fps, stages, palette, objects and sampled tracks, each marked with a status such as fitted, inferred or unknown. Start from fitted values instead of measuring them again and treat inferred or unknown values as hints; confirm either against decoded frames where a decision depends on it. The decoded video stays authoritative.

## Read the whole reference

Read the reference as a whole before choosing an implementation. Inspect representative frames and consecutive frames around every cut, entrance, exit and transition. Explain what persists, enters, changes, holds and exits; keep an object's identity across cuts when it is the same object.

Keep extracted sound as a local file and use a supported player or dedicated file-based audio analyzer for listening. For model-side listening, require documented audio-input support for the active model and connection before sending an audio attachment. A tool's audio-output helper only describes that tool's output. Keep encoded audio, including base64, out of shell and generic tool results. If model audio input is unavailable or unknown, use `measure events --map` for candidate cues and compare decoded audio for precise onset or offset checks. Continue the visual and timing work and record the listening status using the [shared audiovisual evidence rules](verification.md#verification-scope).

At each change, read four things: where an element comes from and how (pop, scale, fade, type, word by word, wipe); how it changes on screen (colour, fill, counting, morphing); how it leaves; and whether its edges are solid, stroked, gradient or glowing.

A one-per-second or half-second overview is for navigation only and is never evidence of motion: it drops 1–3 frame differences, entry directions, blur and flashes at cuts. Judging motion requires consecutive native frames of that range.

For fast montages, inventory distinct shots and brief events from consecutive decoded-frame chunks through the passage before assigning units. The CLI's `measure frames --range` and `--events` can thin long windows according to `--max`. Check `every_nth_frame` for range output and the `thinned` notices on event strips. Shorten the windows or raise `--max` until the frames needed for this inventory are consecutive. Keep each brief shot's visible peak and entry/exit frames in its local comparison.

When an interaction changes the scene, identify both the actor and the affected content. Inspect the state before contact, the response during the action and the settled result. For a pointer dragging a module, reconstruct the module following the pointer, neighbouring modules making room and the final ordering; animating the pointer alone or sliding one module over a stationary neighbour does not reproduce the interaction. Keep these coupled changes together in the editable timing model.

If decoding, frame extraction or seeking fails, recover the media tools through the [runtime paths](#locate-the-pinned-cli-and-media-tools), or use another available method that exposes the required frames. Confirm the actual timestamps and inspect the resulting images; a successful command or a screenshot of an unverified playback position does not establish coverage. Keep any unresolved interval or detail explicitly unverified, and continue work that does not depend on it. Report a concrete blocker if the missing evidence cannot be recovered; do not silently replace it with an approximation.

## Locate the pinned CLI and media tools

Measurement uses the pinned native CLI: `node <hyperframesCli> measure …`. For a managed project, `openmotion_get_project({projectId})` returns `hyperframesCli` and `authoringGuide`; resources/read `openmotion://engine/SKILL.md` returns the guide without opening Studio. These commands require host shell and file capabilities.

For an independent folder, resolve the native CLI and guide from the active OpenMotion installation. Use the full plugin's registered working directory or the installed adapter's recorded `runtimeRoot`. Confirm `node_modules/hyperframes/bin/hyperframes.mjs` and `node_modules/hyperframes/dist/skills/hyperframes/SKILL.md` there before authoring.

Commands you run yourself (`node <hyperframesCli>`, an entry's measurement helper, `ffmpeg`) use `node` and `ffmpeg` from `PATH`. The self-contained package does not put them on `PATH`: its directory is the one holding `node_modules/hyperframes` in the `hyperframesCli` path, with Node at `runtime/node/bin/node` (Windows `runtime\node\node.exe`) and FFmpeg/ffprobe in `runtime/media/bin`. For an npm installation there is no bundled `runtime/` directory: the application root is the directory containing `node_modules/hyperframes`, and `scripts/npm-runtime.mjs` exports `ensureNativeRuntime(appRoot)` and `nativeConfiguration(appRoot)`. Prepare through the former when needed; the latter returns `paths.HYPERFRAMES_FFMPEG_PATH` and `paths.HYPERFRAMES_FFPROBE_PATH` for the verified cache. Pass these as environment variables to measurement helpers or direct media commands. When neither is available, record the affected check as blocked with the reason; never as passed.

## Measure specific questions

These commands answer specific questions; running every one is not mandatory. Images go to `.hyperframes/measure/` by default; write them with `--out` into a working directory outside the live project, then read them with the host's image reading. Record the values where the selected entry keeps its working record.

| Question | Command | Use |
|---|---|---|
| Canvas, fps, duration | `measure probe <ref>` | Root `data-width`, `data-height`, `data-fps`, `data-duration`. Keep a constant source's rational rate, such as `30000/1001`. For a variable-rate source, inspect timestamps and choose and record a suitable supported output rate rather than copying the advertised maximum. Use the measured picture duration, not a longer audio container |
| Hard cuts | `measure cuts <ref>` | `shots` is a first draft of the segmentation; verify each candidate against adjacent source frames. Films built on gradients, growth and morphing have few cuts, so segment further by picture content |
| What changes when | `measure events <ref> --map --out <dir>` | Appearance, disappearance, change and hold times, sound onsets and beats; shows which windows need frame-by-frame reading |
| Frame samples | `measure frames <ref> --range a,b --roi x,y,w,h --max 16 --out <dir>`, or `--events --out <dir>` | Entry direction and style, on-screen change, exit, edge treatment |
| Motion curve | `measure curve <ref> --start a --end b --roi x,y,w,h` | The ROI frames the whole move, including overshoot, and contains only one moving thing. Returns start, end, duration, overshoot and the closest GSAP ease as a starting estimate; multiple phases, constraints or procedural motion can need a richer representation than one tween |
| Text size | `measure ink <ref> --at t --roi x,y,w,h` | Ink width and height in the original and the render, to adjust size, tracking or layout. Substitute fonts are usually wider; compare numerals too |
| Background and colour | `measure look <ref> --at t --grid 8x6` | The background fills most of the frame. Sample it at several moments and match the gradient direction and light-to-dark falloff |
| Crop an asset | `measure extract <ref> --at t --roi x,y,w,h --out <dir>/logo.png` | Photos, screenshots, logos and avatars from their largest, sharpest frame; then bring the file into the project through the entry's asset path |

Use actual source timestamps, or the zero-based frame index divided by the exact rational fps for constant-rate footage. For variable-rate footage, map actual presentation timestamps onto the recorded output rate. Keep enough precision for the runtime's sampling convention, and check adjacent rendered frames around sensitive boundaries instead of applying one truncation rule to every timeline.

Look for texture where the reference has it:

- **Depth layering:** how much blurrier and darker a back layer is than the front at the same moment; `measure frames --roi <back layer>` shows it.
- **Highlights:** how bright the brightest part is (near pure white, or grey); `measure ink` or the colour values of one frame show it.
- **Motion blur:** direction and length on fast-moving frames; consecutive `measure frames` show it.

Reproduce what is there; do not add effects for polish.

## Choose an editable representation

Choose source and component boundaries through shared behaviour. Objects sharing geometry, state, layout or motion can form one SVG, Canvas, Three.js scene or native composition; independent contributions can stay separate. There is no requirement for one clip per object, one composition per cut, one tween per move or a fixed number of poses. Keep relative scene time distinct from the root timeline.

Choose the representation from the appearance and behaviour that make each region recognizable. Use clear source views and adjacent frames to obtain visible bounds, texture, typical and extreme feature sizes, motion direction and travel, holds and event timing. Keep these observations next to the source controls they drive, in the record the selected entry keeps.

A stationary boundary can contain scrolling content, changing illumination or a deforming surface. Preserve recovered texture with local-coordinate transport, masks, aligned content fields or deformation, according to that source behaviour. Derive procedural marks from observed shape, size, spacing, colour and exposure, and carry these properties through movement and transitions. A material crop has a source position and visible pixel bounds; preserve its crop offset and transparent padding when placing, scaling and reusing it in scene coordinates.

Keep content the user will change easy to locate: wording, brand, images, named objects and their motion. Use meaningful source names and declare common edits as root variables so the Studio Variables panel shows them. Variables are shortcuts, not an editing whitelist; HTML/CSS/JS source remains authoritative.

Use code for controlled text, geometry and motion. Consider supplied or recovered photos, artwork, rendered imagery, environment detail, logos, screenshots and textures as local spatial materials when their appearance stays unchanged, and distinguish editable text from artwork that needs an asset replacement. Compare recoverable material and proposed geometry at a clear pose, including contour, surface detail and surrounding structure, before choosing the representation. Drive observed changes with editable paths, masks, camera, deformation or content controls, and check the newly exposed areas. Choose 2D, perspective layers or real 3D according to the observed behaviour and the needed edits, not the number of perspective shots. Canvas/WebGL follows the pinned runtime's seek and readiness contract: derive the picture from input time and settings, including deterministic randomness, so the same time always renders the same frame.

For small objects whose shape carries meaning, inspect a close crop before choosing the geometry. Match the silhouette, concavities, orientation, proportions, stroke and attachment to nearby labels, not just the colour and bounding box. For example, a mouse pointer with an inset is not a solid triangle; rotating the triangle cannot restore the missing contour. Use an editable vector path or the appropriate local asset when a CSS primitive cannot represent the observed shape. Check repeated instances and changed states against the reference.

Do not pass off playback of the entire reference, a full-frame image sequence, editable content baked into a background, or an unadaptable per-frame contour transcription as a rebuild. Judge independent assets by their purpose and effect on intended edits, not crop area alone. Time-driven functions, loops, arrays, simulations and shape interpolation are valid when the content stays reasonably editable.

## Text and fonts

- Preserve type character: geometric shapes, contrast, x-height and stroke terminals. Start with the faces the pinned authoring guide lists and the [curated catalog](fonts.md); when none fits, use another available font whose license permits the use. Import or bundle it through the project's supported asset path with its license, as [Typography](typography.md#use-the-face-that-was-chosen) describes. Record any substitution where the selected entry keeps its record.
- When replaceable text uses distinctive lettering (pixel, stencil, wide or hand-built wordmark), make any new word settable in that same style: the closest face of the same kind, or lettering built so other words can be set with it. Vectorising only the reference's own word leaves every later edit in a plain fallback font.
- Keep editable wording as addressable text. A calligraphic logo or stylized artwork can be an image or vector asset instead; note where it is replaced. Do not build a new font just to keep everything as text when an independent asset meets the task.

## Check fidelity and edit dependencies

When the selected entry's scope includes comparing with the reference, compare source and rendered frames at the same actual timestamps. Fix concrete issues such as omitted content, wrong text, broken assets and incorrect timing. When two consecutive fixes for the same issue do not visibly reduce the difference at the same moment, change the approach once; if that also fails, record the issue in the entry's record and move on. Recording a remaining defect is not evidence that it passed.

Verify hard cuts against adjacent source frames, then inspect the rendered boundaries. Restore a missing original hard cut unless the user requested a change; do not accept accidental smoothing or a detector's false positive as intended behaviour.

When an image changes, inspect its crop, masks and coupled effects. When wording changes, inspect wrapping and reading time. When a scene's duration changes, update dependent scene starts and media timing. When a brand or named object appears several times, check all relevant appearances. Preserve unrelated content.
