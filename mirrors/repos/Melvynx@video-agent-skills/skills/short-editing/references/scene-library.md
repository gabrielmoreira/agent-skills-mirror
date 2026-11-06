# Scene library

Everything is authored in `source/spec.js` as `window.SPEC = {...}`, with all times in SOURCE seconds (from `files/words.md`).

## Time-key convention (how the engine knows what to map)

`mapSpec` walks the spec and converts SOURCE seconds to SHORT seconds for:

- any number whose key is `at`, `from`, `to`, `until`, or ends in `At`, `From` or `To` (`sendAt`, `countFrom`, `workTo`...)
- the FIRST element of each entry in any array whose key ends in `keys` (`keys`, `labelKeys`...)
- `[a, b]` pairs in `hide` and in any key ending in `spans`
- `'p+X'` strings anywhere a time goes: X seconds into `spec.pause` (the frozen narrator break)
- `'o+X'` strings anywhere a time goes: X seconds into the end card (`spec.outro`)

These are NOT mapped: `offset`, `dur`, sizes and positions, and everything under `media`, `cam`, `cut` and `tighten`. `music.breaks` and `music.end` are mapped by the audio step.

When you add a new time param, name it `somethingAt` / `somethingFrom` / `somethingTo`, or it will silently stay in source time. The reverse bites too: a non-time value named `to` (a target value, a percentage) gets mapped as a time. Call it `value`.

A time that falls inside a removed silence snaps to the start of the next kept segment. Prefer word start times.

## Style layer (creator profile)

`short.mjs init` snapshots the creator profile (the nearest local `.short-editing/style.json` from the short's folder up, never `~/.short-editing`, or `engine/templates/style.json` without one) into `source/style.json`. At load the engine layers engine defaults < `source/style.json` < `spec.js` (`engine/lib/style.js`): the profile sets `colors` and `font` (theme), `paper.grain`, and fills `speed`, `tighten`, `captions`, `music` and `mix` key by key, so the spec only writes what differs for this short. A `cta` scene gets `name` from `creator.name` and `sub` / `button` / `done` from `creator.cta`, else the defaults of `creator.lang` (fr: Plus de vidéos, S'abonner, Abonné). No `source/style.json` (older projects): the raw engine defaults below, unchanged. Schema: `../short-editing-setup/references/style-schema.md`.

## Top level

| key | meaning |
|---|---|
| `title` | free text |
| `format` | `'square'` renders 1080x1080 (1:1 for X), `'wide'` 1920x1080 (16:9, race videos), default 1080x1920. Most scenes centre on `W / 2`, but hand-placed x values assume 1080 wide: check stills on `wide`. Use seam `layout.keys: [[0, 1080]]` for paper only and keep every y under ~1000. |
| `silent` | `true` + `duration: <s>`: no Tella take, no voice, no camera, no captions. Times are plain seconds; music + SFX only. `prepare` just extracts `media`. |
| `media` | `{id: {src, from, dur, width, fill, focus}}` video clips (or one image) for cards and full-screen B-roll. `src` accepts `~`. Frames are extracted once and cached at `width` px (default 960, use 780 for phone-format portrait exports). `fill: true` crops the clip to the frame's aspect first (default width = frame width), around `focus: [x, y]` (0 to 1, default centre): use it for every `broll` media so a landscape clip fills a 9:16 frame without bars. `alpha: true` keeps the clip's transparency (a png-in-mov or ProRes 4444 rendered on a transparent background) as RGBA PNG frames, for the `overlay` scene. |
| `broll` | `[{media, from, to, offset, zoom: .05, focus: [x, y]}]` full-screen B-roll: the clip covers the whole frame (camera and paper) between `from` and `to`, with the voice and captions on top (captions take their over-video look there: white words with a soft shadow, never the straddle's ink half or the bare-paper ink). Quick fade and settle in, a slow push (`zoom`, 0 = still), quick fade out. `hard: true` (or the style's `cuts: 'hard'`) = a straight cut in and out. `offset` = seconds into the clip at `from` (start on the clip's `best_start`). See "Full-screen B-roll" below. |
| `cam` | `{crop: [x, y, w, h] in source px, eyes: [x, y] inside the crop, splitZoom: 1.2, keep: [[x, y, w, h, r]]}`. The card and full screen center on the eyes, so moving `crop` alone changes nothing on screen: to push a cut-off object (a poster sliver) out of the card edge, move `eyes` a few px toward the other side and/or raise `splitZoom` (1.25). `keep`: rounded rects in cam-crop px that every cutout always keeps, for props in front of him that the person matte drops (his mic and boom arm would otherwise leave a paper-coloured hole in his chest). `r` is a number or `[tl, tr, br, bl]`. Measure on `frames/cam` vs `frames/matte` alpha. `wb: false` turns off the automatic white point (see `grade`). |
| `speed` | playback speed of the whole short (voice atempo, camera and media retimed). `1.15` from the default profile (`pace.speed`), 1 with no style snapshot |
| `tighten` | breath kept per boundary after cutting the quiet run: `{sentence: .08, comma: .05, word: .03, lead: .03, tail: .8}` from the default profile (`pace.tighten`); with no snapshot `{.10, .06, .03, .03, .9}` |
| `cut` | `[[a, b]]` source ranges to drop (retakes, dead air) |
| `hold` | `[[a, b]]` source ranges kept verbatim, silences included: a sung rhythm ("tu, tu, tu"), a beat left for an effect |
| `bleep` | `[[a, b]]` source ranges censored: the voice is fully cut there and replaced by a 1 kHz bleep (about -18 LUFS), and those words never show in captions. Cover the whole word, its tail included: read the voice energy, not just the Scribe end time (`3.10, 3.68` for a word Scribe gave as 3.14 to 3.60). |
| `thump` | `[[a, b, dB]]` source ranges where a mic plosive ("p", "b") thumps: the voice is high-passed at 240 Hz there (24 dB/oct, 12 ms crossfades) and moved by `dB` (default -3). For a "bruitage trop fort" with no SFX at that time: measure the voice 80-160 Hz band, the burst jumps 15 dB or more over its neighbours. Cover the burst only (about .2 s). |
| `voices` | `[{at, src: 'assets/x.mp3', gain: 0}]` extra voice clips mixed into the voice bus at `at` WITHOUT freezing the video: an AI answering in the gaps the creator leaves on camera. They play at 1x, so `hold` each gap and size the clip to the gap's short length (gap / `speed`). Pair with a `convo` scene. Example: `shorts/short-opus-55-calin/` (`source/opus-voice.py` makes the clips + word offsets). |
| `outro` | seconds of end card added after the last kept word (e.g. `3.2`): the voice pads with silence, the camera holds its last frame, the music keeps going and fades out by the end. Author its items with `'o+X'` times (`'o+0'` = the end card starts), usually a layout key `['o+0', 1920]` and a `board` `from: 'o+0'`; end the previous board with `to: 'o+0'`. Typical use: a podcast extract that ends on "watch the full episode" + the episode thumbnail as a framed `img` + its short link as a `label`. |
| `pause` | `{at, voice: 'assets/x.mp3', words: 'assets/x.words.json', tail: .12, gain: 0}` the short STOPS at source `at` for the voice's length: frozen frame drains to grey, the voice (ElevenLabs TTS, word-timed via Scribe) plays, music tape-stops and restarts from bar 1 on the resume. Author times inside it as `'p+X'`. Pair with a `pause` scene. |
| `inserts` | `[{at, voice: 'assets/x.wav', tail: .12}]` short voice lines dropped between two sentences at SOURCE `at` (a chapter line: « Piège numéro deux »): the short makes room for each one, the camera holds its frame, the music runs on (no grey drain, no tape stop, unlike `pause`). Author times inside insert K as `'iK+X'`; resume the edit at `'iK+<its length>'` (the insert length is in `assets/timeline.json` `inserts`), never at the source `at`, which can fall in a cut and map before the insert. Typical card: layout `['iK+0', 1920]` + a `board` from `'iK+0'`, `captions.hide` over the same span (a caption line now stops where a hide span starts). Voice: ElevenLabs TTS of the creator's clone, x1.2. Example: `shorts/short-vibe-code-facture/`. |
| `layout.keys` | `[[t, seam]]`: y of the paper/camera seam. `960` = half, `1240` = paper-heavy, `0` = full-bleed camera, `1920` = paper only. A key going to or from `0` (from or to a split) is the window transition: the camera lifts into a rounded card that opens to full screen over the still paper (dim .22, margins and corners bulge mid-move), or closes back into the panel. It starts AT the key time, so put the key on the word. |
| `cutout` | `{from, to, scale: 1.15, x: 540, bottom: 1920}` the speaker cut out (no background) standing on the paper. Pair it with seam `1920` (paper only) for a hook: a card on top, the creator below. See "Speaker cutout" below. Ending on a split seam key hands off smoothly into the camera (see Hook). `{from, to, ride: true, scale: 1.3}`: head in front of the board (aiwithremy): over a split seam (~1000), the camera is bottom-aligned at `scale` (x zoom keys) and he is drawn unclipped, so his head pokes ~250 px up in front of the `stage` board above the seam; in and out on the frame. Put the board on `layer: 'stage'` (an 'over' scene would cover his head). |
| `zoom.keys` | `[[t, z]]` camera punch-in, `1` to `1.15` max. `[t, z, 400]` = an instant punch-in (third value = spring stiffness), still 1.15 max and about one every 4 s (1.3+ every second was rejected as far too aggressive); `sfx.kit.punch` only fires on a zoom IN away from a cut. `zoom.drift: .008` (usually from the style): a slow push of 0.8 %/s inside each shot, restarting on every seam change and every punch (w ≥ 60), capped at 4 s |
| `actors` | media cards (below) |
| `scenes` | stage/over scenes (below) |
| `captions` | `{replace: [['cent pour cent', '100%']], emph: ['Opus', ...], hide: [[a, b]], size: 84, maxWords: 3, maxChars: 16, paperY, style: 'sticker', weight: 800}`. `style`: one of the `capStyles` looks by name or number (21 = `clean`, the white pill of the card layout, base size 42; 22 = `rise`, 23 = `hard`, 24 = `stack`, 25 = `band`, 26 = `dim`) (profile `captions.style`). `dim` (speedy-devv): the phrase builds word by word on centered lines, spoken words in `color` (grey) at `dimWeight` (500), the current word in `hi` (white) at `weight`, an `emph` word keeps a full-radius dark pill (`pill`, default `#2B2B2B`) once said, each word blurs in; pair with `size` ~60, `yKeys: [[0, 300]]` on a dark flat paper. `rise` (DM Sans 900, the white paper style's default) and `hard` (Bricolage Grotesque 800, hard ink shadow) are block looks: the word being said sits on an accent block (`rise` blurs it in, blur to sharp with a 1.04 to 1 settle in about .15 s, then fades it out in place in .12 s when the next word starts; the line itself blurs in per chunk; `blur: false` (rise only, profile `captions.blur`) drops every blur and settle: the line snaps in and the block jumps word to word in .05 s cuts, for styles whose creator finds the blur hard on the eyes. `block: false` (rise only, profile `captions.block`) drops the accent block: each white word appears only when it is said and blurs in on its own (blur .16em to sharp), the line building up word by word, no background (the small chest captions of benkimball.ai; pair with `size` ~58, `font` 'Poppins' (SemiBold 600 only), `weight` 600, `lower: true`, `yKeys: [[0, 1600]]`). Never grow the block up from the bottom, shrink it or slide it: the creator rejected both). Block captions never straddle the seam: in split the line sits on the paper just above the camera card with ink words, full screen it sits on the video with white words, so keep stage items clear of the band just above the seam. `straddle: true` (rise only, profile `captions.straddle`) is the exception: in split the line's middle sits right on the camera card's top edge, ink words throughout, each word on a soft paper glow (no hard white outline: the creator found it dirty, and an outline on the video half only read as cut in two) so it reads on a light or dark background; move the speaker chips to the bottom of the card, out of the line's way. `straddleDy: 70` (with `straddle`): the line sits that many px below the camera's top edge, fully on the video, white words on a soft dark shadow instead of the paper halo (the creator 2026-10-14: shadows, never a white border); `shadow: 1.6` (rise) strengthens that shadow (alpha and blur) on a light background. `style: 'band'` (profile `captions.style`): the whole line on one flat block (`bg`, default ink), white words (`color`), `emph` words in `hi`, hard in and out; `bg: 'none'` drops the block (white words straight on the video with a soft shadow, `shadow: false` = none: the white Geist Pixel chest captions of aiwithremy). `tracking`: letter spacing in em of `size` (e.g. `-.08` tightens the monospaced Geist Pixel toward a proportional pixel face). `font`: caption family override (default: the style's own family, else `font.family`). `paperY`: caption y on full-paper frames (seam 1920), e.g. 860 to keep them off a hook cutout's face. `color: '#FFFFFF'` (rise only, profile `captions.color`): the words keep this color on every layout, never switching to ink on bare paper (white words on a dark flat paper). `lower: true` (profile `captions.lower`): every spoken word in lower case, `replace` values keep their case. `yKeys: [[t, y]]` force the caption y from `t` on (wins over every other rule), e.g. `[[103.72, 890]]` to sit them on a `camSplit` seam. `scaleKeys: [[t, k]]`: lines starting from `t` on are drawn `k` times bigger and hold `k` times fewer characters (the giant hook: `[[0, 2.1], [4.2, 1]]` = one or two huge words per line until 4.2), grown up from the bottom of the line so they never reach the camera card, capped to the frame width (format youtube: scaled lines are centred on the whole frame, across a split, the podcast clips cold open). `hook: {spans: [[a, b], ...], style: 'stack', ...}` (source time): two looks in one short, the base look (rise) everywhere and the `stack` pile (the creator x Nico: small words + one big key word) only inside the spans, drawn with the base captions overridden by the hook's own keys (size, font, maxWords, big, emph, yKeys...); keep the spans on the hook, the stat or promise that makes people stay, the re-hook and the CTA, about a third of the short (the creator: never the pile on the whole short) |
| `music` | `{bpm: 112, start, breaks: [[a, b]] (drums drop), end, mute, drive, bed, src, offset}`. `bed: '<id>'`: a library bed (`assets/music/<id>.mp3`, pick it and its `offset` with `references/music.md`). `src`: any other file, e.g. the creator's own track. Both replace the generated bed (read from `offset` s, looped, ducked under the voice; `breaks` and the `pause` tape stop only apply to the generated bed). `drive: true` = more dynamic bed (four-on-the-floor, clap backbeat, 16th hats, pumping bass, a fill every 4 bars); pair with bpm 120 to 124 and `mix.music` about -25. `start`: the bed enters late (after an on-camera count-in or a sung part). `dropOn: 'punch' | 'cut'` (or both in an array) + `drops: [t]`: the bed cuts out for `dropLen` (.3 s) down to `dropDepth` (.06) under every punch-in / every hard cut / each listed time (hip-hop drop-outs, nico-slowdown). Stock track validated by the creator for ads and tension pieces: `bed: 'tension-ad'` (ElevenLabs, 64 s, its break at 45.75 to 48 s; reference: `shorts/short-tella-cmuqep`, offset .95, `mix.music` -25, `mix.sfx` -34) |
| `layout.frame` | `true` or `{m: 40, gap: 26, bottom: 46, r: 40, border: 9}`: framed camera. In split the camera is a photo pinned on the paper (side margins `m`, `gap` under the seam, `bottom` margin, rounded corners `r`, a white paper `border` and the style's sheet shadow) instead of a full-width panel under the deckle edge. `layout.keys` work as usual: the window transition grows the photo to full screen (margins, corners and border melt to 0) and shrinks it back. Captions stay on the seam. `bleed: true`: the photo runs off the left, right and bottom edges (no margin, no border, square bottom corners), only its top edge keeps the rounded corners, the white border and the shadow (side and bottom margins look bad once platform UIs crop the frame). On in the white paper style. `border: 0` with `bleed`: no white border at all, a soft shadow cast up onto the paper above the camera instead (`shadow`: its height in px, default 40); the creator 2026-10-14 prefers shadows to white borders. |
| `grade` | `true` = the default camera grade, fitted to the take: `prepare` measures the face (median of 5 frames, box under `cam.eyes`) and logs `grade: face luma N`. A dim room (face luma 80 or less) gets the full lift (brighter face and mids, solid blacks, saturation 0.84 so the wood and lamps stop glowing orange, a slight cool shift). Every normal take (100 or more) gets the natural look: no colour shift at all (cutting the red greyed the skin), saturation 0.96, the black point stays, a gentle mids lift that fades out as the take gets brighter (full at face luma 108 or less, none at 128). 80 to 100 blends the two. Both add a touch of clarity. Never contrasty or saturated, never washed out or grey skin (all rejected). Or your own ffmpeg filter chain as a string. Every grade also starts with an automatic white point: `prepare` samples the near-white pixels under `cam.eyes` (cap, shirt) and pulls a cyan, green or warm cast back to neutral (each channel moved by at most 7 %, nothing done under a 1.2 % cast), logged `grade: white point R,G,B -> neutral`; `cam.wb: false` turns it off. Baked into the camera frames at `prepare` (and so into the cutout matte); rerun `prepare` after changing it. Each extraction writes `stills/grade.jpg`: the same frame raw (left) and graded (right); read it once per short. On in the white paper style. `border: 0` with `bleed`: no white border at all, a soft shadow cast up onto the paper above the camera instead (`shadow`: its height in px, default 40); the creator 2026-10-14 prefers shadows to white borders. |
| `layout.card` | Not used: the creator rejected this look (fixed camera, header, text slides). `true` or `{x: 66, y: 1082, w: 948, h: 715, r: 44, zoom: 1.08, bias: .27, capY}`: the clean layout (style the creator Clean). The camera sits in a fixed rounded card, the stage is everything above it (clipped at `y - 6`), and captions sit at `capY` (default `y - 114`). `layout.keys`, window transitions, cutouts and the seam are ignored; `zoom.keys` still punch in inside the card. Pair with `slide` scenes and `paper.bg: 'clean'`. See "Clean layout" below. |
| `header` | Not used (rejected with `layout.card`, "ça fait du bullshit"). `{brand: 'BRAND', mark: 'X', tagline, x: 62, y: 120, size: 42, tagSize: 27}`: a brand line drawn on every frame of the card layout (brand in ink, mark in blue, tagline right-aligned in ink3). From the style. |
| `shake` | `{keys: [[t, amp: 24, dur: .5]]}`: an impact shake of the whole frame (slightly zoomed so no edge shows), decaying over `dur`. Put it on the hit of a `shatter` or a reveal boom, never as a pulse. |
| `glitch` | `{keys: [[t, dur: .4, amp: 1]]}`: a digital glitch of the whole frame centred on `t` (RGB split + torn bands slid sideways, re-rolled every 2 frames, strongest at `t`). Only under a zhhh transition sound (`sfx.files` with `peak: true` on the same `t`), once or twice a short. |
| `vanish` | `{from, to, backAt, back: .45, cell: 12, plate, grow: 10}`: the camera turns to dust between `from` and `to` (blocks swept left to right drift up, shrink and fade, the paper shows through), then from `backAt` the dust flies back in. `plate: 'assets/images/x.png'` (an image of the empty room at the take's own size, the speaker removed) = only the speaker turns to dust and the room stays: `prepare` mattes the whole span (Apple Vision) and builds `frames/plate.jpg` through the same crop and grade, and his silhouette, dilated by `grow` px, is filled with the plate. Use the plate whenever the camera is on screen during the vanish (the creator: the room must never vanish with him). For "je disparais". Keep it clear of a split <-> full window transition; pair with `dust` and `pop-back` in `sfx.files`. |
| `layout.w` | seam spring stiffness (default 10) for split <-> split and paper <-> split moves. Split <-> full camera ignores it (window card). |
| `layout.dur` | window card length in seconds (default .62, smootherstep). |
| `mix` | `{music: -28, sfx: -29.5, duck: .5, ceil: -1.5}` LUFS targets (sfx measured on event hits only, not slides/highlights), duck depth, limiter ceiling |
| `sfx` | `{mute: true}`, `{swish: .35}` (gain of the paper slides, 0 = none), `{slideGap: 8}` (min s between slides; slides only play when the paper re-enters over full camera), `{marker: 1}` (highlight sound gain, 0 = silent), `{strike: 1}` (gain of the scratch on every hand-drawn strike, `strikeAt`; 0 = silent, the creator's styles: « ce bruit est dégueulasse ») or `{extra: [[t, 'tap' / 'pop' / 'slide' / 'bell' / 'thud', gain?]]}`. `files: [{at | endAt, src, gain: -10, pan: 0, peak, offset, len}]`: designed sound files (`assets/sfx/*.mp3`, project-relative, a missing file throws), each levelled on its own to (-16 + gain) LUFS and kept out of the SFX bus measurement. `at` = where it starts, `peak: true` puts its loudest sample on `at` (impacts, whooshes, glass), `endAt` = where it ends (a riser landing on the payoff), `offset` / `len` trim it. Build the hook and the payoff with them (whoosh + glass + boom on a shatter, riser + boom on the reveal, whip on each board whip, dust + pop on a vanish). `kit: {cut, pop, punch, gain: {cut: -13, pop: -11, punch: -9}, gap: .12}` (usually from the style, files project-relative): automatic hits, `cut` on every seam change, cutout / broll edge and `cut` join, `pop` on every board img / logo / icon `at` and `imgKeys` swap, `punch` on every zoom key with w ≥ 60; a cut within .08 s of a pop or punch is dropped |

Captions sit on the seam (clamped to 1400) or at 760 to 1180 when the camera is full-bleed. They hide automatically when there is no speech for more than .55 s.

### Speaker cutout, camera mode (magic backgrounds)

`cutout: {mode: 'cam', from, to, bg: [{at, kind: 'paper' | 'image' | 'cam', src, img, hard, origin: [x, y], w: 6, sticker, focus, birds, birdsTo}]}`

`cutout` can also be an ARRAY mixing one `mode: 'cam'` entry and any number of standard ones, e.g. a full-paper hook cutout `{from: 0, to: 5.2}` plus a cam-mode range later. `prepare` mattes the union range once.

The speaker stays where the camera puts him (any seam, zoom) and only the room changes. Each `bg` layer wipes in as a circle from `origin` (put it on the snapping hand) with a white rim; `paper` gets a white paper-cut sticker outline around him, `image` (project-relative `src`) slowly zooms, and a final `cam` layer at `to` wipes the real room back. `birds: true` sprinkles bird chirps until `birdsTo`. Pair each wipe with a `snap` scene. `hard: true` swaps the layer on a hard cut (no circle). **Text behind the head**: `img` = a full-frame 1080x1920 alpha PNG (a giant magazine word, rendered from an HTML page) drawn over that layer and under the person, so the head overlaps the title; on a `kind: 'cam'` layer the real room stays (e.g. `{at, kind: 'cam', img: 'assets/images/t-huge.png', hard: true}`, then a plain `{at, kind: 'cam', hard: true}` to drop it). At full bleed only about 600 source px around the eyes are visible: for a hand off to the side, drop to seam 960 with `zoom` .85 so the gesture is in frame.

## Full-screen B-roll

B-roll is footage shown over the voice to illustrate what is said: the creator's own clips (the street, the desk, the sunset, the app on the phone), screen recordings, photos. It has no voice of its own. Two ways to show it:

- **Full screen** (`spec.broll`): the clip replaces the whole frame for 2 to 5 s while the sentence plays. For a moment, a place, a feeling: "I moved to Bali" over the rice fields, "I worked every night" over the desk at night. It is the strongest way to illustrate and resets attention.
- **As a card** (`actors`): the clip sits on the paper above the camera, with a label. For proof the viewer must read: a screen recording, a result, a UI.

```js
media: {
  sunset: { src: '~/Movies/B-roll/IMG_2507.MOV', from: 0.3, dur: 5, fill: true },        // fill: cropped to 9:16
  desk:   { src: '~/Movies/B-roll/desk.mp4', fill: true, focus: [.5, .35] },             // keep the top of the frame
},
broll: [
  { media: 'sunset', from: 12.4, to: 15.8 },                   // SOURCE seconds, mapped like every time key
  { media: 'desk', from: 31.0, to: 34.2, offset: 1.5, zoom: 0 },
],
```

Rules:

- Method: `broll/references/use.md` (the `broll` skill). Find clips with the B-roll database, never by opening files: `node <skill>/../broll/scripts/broll.mjs search "<english words>" [--portrait] [--min-dur 3] [--json]` (tags are in English; emotions also work in French). Use the hit's `path` as `src` and its `best_start` as `from` (or `offset`). Then `broll.mjs look <ids>` and Read the sheet: a clip goes in only if the image fits the sentence. No good hit: the library does not have it, so use motion design or a generated image, never a random clip.
- Each `broll` entry covers at least the whole sentence it illustrates (2 to 5 s), starts on the word that names it, and leaves at least 5 s of camera or paper between two B-roll stretches unless the beat is a montage.
- Hide captions only if the clip has text of its own; otherwise captions stay on top (they are drawn after the B-roll).
- A clip with no people works anywhere; a clip with the creator on screen (`is_self`) fits "I", "my", "me" sentences.
- After the short is done: `broll.mjs used <slug> <id ...>` so the next shorts prefer fresh clips.
- `prepare` extracts the B-roll frames (they are `media`), so re-run it after adding or changing one.

## Actors (media cards on the paper stage)

```js
{ id, media, offset, from, to, pre, enter: 'right', keys: [[t, [x, y, w]]], labelKeys: [[t, 'Label']],
  dot: 'blue' | 'gray', ringAt, badge: { text, at }, dimAt, ar, mark: { at, dur, rect: [dx, dy, w, h] }, marks: [mark, ...] }
```

- `ar`: card height/width ratio, default `9 / 16`. Use `16 / 9` for phone-format app exports: two 450-wide cards side by side at x 60 and 570 (seam 1240).

- `offset`: seconds into the media clip at `from`. The clip then plays at the short's `speed`.
- `pre`: start the enter animation this many seconds before `from`, so the card is already settled when the word lands. A negative `pre` delays it, which staggers two cards that share a `from`.
- `keys`: position targets. The card is 16:9 (`h = w * 9/16`) and moves with a spring on each key. Keep `w` constant (800): a card that changes size reads as random.
- `labelKeys`: 42 px label above the card (with `dot`), cross-fading with a small slide between labels. Leave 70 px above the card for it.
- `mark`: blue highlighter that sweeps left to right over a phrase inside the card (multiply blend) when the word is spoken. `rect` is in canvas px from the card's top-left. Measure it on a still. `marks` takes several, each on its own spoken word.
- `ringAt`: blue selection ring. `badge`: blue check pill at the top-right corner. `dimAt`: desaturate and fade (the loser).
- Default enter is a rise from below. `enter: 'right'` slides in from the right.
- When one card waits alone for its rival, centre it first (`x = (1080 - w) / 2`) and add a key that moves it aside as the rival enters. Half an empty stage for several seconds reads as a bug.

### Hook: launch tweet + speaker cutout

For "X just came out" hooks, open on the official announcement with the speaker cut out underneath, from frame 1.

- Capture the tweet crisp: `DEV_BROWSER_ISOLATED=1 dev-browser --browser rec`, CDP `Emulation.setDeviceMetricsOverride` about 390 wide, then `Page.captureScreenshot {clip: {...boundingBox, scale: 3}, captureBeyondViewport: true}`. An element screenshot stays at 2x whatever the DPR. Crop out embedded video thumbnails (they are blurry) and keep the header, text and the views line. A single PNG as `media` gives one frame, which is fine.
- If the only capture is a desktop screenshot, the body text lands around 25 px on a 960 card: unreadable. Rebuild it with the native `tweet` scene instead (below), which sets the body at 40 px.
- Spec: `layout.keys: [[0, 1920], [<end>, 1240]]`, a tweet actor at `[60, 190, 960]` with `ar` = h/w of the PNG, `cutout: {from: 0, to: <end>}`, and a `mark` on the product name. Hide captions over the tweet's first seconds.
- Hand-off (automatic): when the cutout's `to` meets the seam key that leaves 1920 for a split, the camera band does not rise from the bottom. The seam switches at once, the room fades in around the creator, and the cutout glides onto the camera framing (same pixels), so he never leaves the screen. The creator: "je disparais par le bas et je réapparais par le bas, c'est étrange". Keep the cutout `to` equal to that seam key time. `cutout.handoff: false` restores the old drop-out exit.
- The cutout comes from `engine/matte.swift` (Apple Vision person segmentation, accurate, EMA-smoothed mask, soft edge). `prepare` runs it only on the cutout range and writes masks to `frames/matte/`; the runtime composites them over the cam frames. Nothing to install; about 30 fps on the Neural Engine, cached by frame content (`references/performance.md`).

### Media for app demos: phone-format exports, never desktop tool UIs

Shorts are watched on phones. Record each generated app directly at a mobile viewport, never through a compare dashboard or desktop UI.

- Use dev-browser headed (`DEV_BROWSER_ISOLATED=1 dev-browser --browser rec`), because WebGL needs a real window. Then send CDP `Emulation.setDeviceMetricsOverride` `{width: 390, height: 693, deviceScaleFactor: 2, mobile: true}`, which gives 780x1386 frames.
- Run a screenshot loop and log the timestamps. Assemble the frames with the ffmpeg concat demuxer using per-frame durations, then `fps=30`, crf 18. CDP screencast is throttled in a hidden window, so don't use it.
- Heavy 3D only reaches about 8 fps this way. Slow the app down (for example its 0.25x control), record 4x longer, and divide the timestamps by 4.

## Real logos (always)

Any `logo` (tiles item, pipeline header and rows) or actor `labelLogo` that is a project image path (`assets/logos/<name>.png`) draws the real icon, rounded like an app icon. Every named product, tool or app gets its real logo, never a letter glyph. Glyphs are only for generic ideas (CRM, infinity).
Where to find them: App Store icons first (`https://itunes.apple.com/search?term=<app>&entity=software` -> `artworkUrl512`, swap `.jpg` for `.png`), then the product's GitHub `assets/` (icon-master.svg), then the site's `apple-touch-icon` / favicon.svg. Rasterize SVGs to 512 px PNG. Check every icon on a contact sheet before using it (GitHub org avatars are often not the product logo).

## Scenes

Story scenes (`foilHat`, `stampOver`, `cheque`, `crowd`...) and the composable `board` (items: text, chip, stamp, counter, bar, icon, logo, check, any item with `strikeAt`...) are documented in the headers of `engine/lib/scenes-story.js` and `engine/lib/scenes-life.js`. Board item `rot` is in RADIANS (.05 to .1 for a slight tilt; `rot: -4` spins the item half a turn). Motion on any board item: `pop: .6` (enters scaled down and springs to full size), `spin: -.3` (enters rotated, settles to `rot`), `dx` (enter slide), `posKeys`/`scaleKeys` (moves later in the beat; `posW` sets the spring of both, 12 to 14 for a hero-to-slot glide); `morph: true` (the item grows out of the previous scene's `hand()` rect, e.g. the tweet's image, over `morphDur` .62 s); `hold: true` (a counter keeps its authored `at` instead of entering with its count); `shown: true` (no entrance: the item is already on screen at its `at`, e.g. the hook logo on frame 0, which is also the cover); `slot: false` (skips the same-slot handoff wait); scene `gate: false` (enters on its own `from` even right after another scene's exit). Choreography rules behind these: design-system "Premium choreography". Board `push` (slow zoom over the board's life around `pushAt`, so a held beat never sits still; default .025 on boards of 3 s or more, `push: 0` turns it off) and `outDx: -700` (the board whips out sideways instead of rising; pair it with the next board's items entering with a positive `dx`). Board `img` takes `frame: 14` for a white print border (a premium photo card). Board item `glass {x, y, w, h, tint}` is a frosted panel (silent, no SFX slot); on a `layer: 'over'` board it puts text and icons on the camera without a layout move (`glass()` helper in `templates/youtube.js`). Board item `screen {img | imgKeys, w, h, viewKeys, rings, arrows}` shows a real UI screenshot (a crop of the long-form's screen recording) in a dark window: `viewKeys` spring-zoom onto a region (image px center + zoom), `rings` dim the rest and outline one element, `arrows` draw on toward a tip in image px; use it whenever the creator asks for "la vraie interface" with zooms and arrows. `imgKeys: [[t, img]]` swaps the content in place (a short cross-fade) for a UI that changes state, e.g. the Recorder before / during / after recording, while `viewKeys` keep zooming. Board item `edit {imgs, w: 960, vh: 150, markAt, cutAt, capsAt, fxAt, playFrom, playTo, steps: [{text, at}]}` is an editing timeline that edits itself: real clip frames on a video track, the silences between them boxed in blue (`markAt`) then closed (`cutAt`), "Aa" caption pills dropping on each clip (`capsAt`), blue animation blocks with a sparkle (`fxAt`), a playhead over `playFrom..playTo`, and `steps` as blue chips checked one by one under the sheet (sheet 354 px tall + the chip row 60 px below it); for "l'IA monte tes rushs": rushes fly into a mascot (`img` items with `posKeys`/`scaleKeys` toward it, drawn before it), then the mascot moves up and the `edit` sheet appears under it. Board item `term {cmd, w: 960, h: 640, size: 52, title, logo, name: 'Claude Code', sub, placeholder, focusAt, typeFrom, typeTo, suggest: [[name, desc]], sendAt, out: [{text, at, dim}]}` is a Claude Code terminal (centered): the slash command types in the prompt box with its autocomplete row, Enter (`sendAt`) moves it to the history and the `out` lines land one by one (cues play a key per character, a tap on Enter and a tick per output line); use it to show the exact skill launched (`/short-editing`, `/publish`) and give it the real Claude logo. Board item `shatter {logo, s: 260, breakAt, hit: [x, y], n: 10, seed, tight}` (`tight: true` on a colored flat paper: only the icon's pieces, no white glass wedges) is a real logo that holds, then breaks into glass shards at `breakAt` (`hit` = impact point, -1..1 of the icon) with a blue shockwave and spark lines: the hook "X vient de tuer Y" (another logo flies in with `posKeys` and lands on `breakAt`, plus `shake` and whoosh + glass + boom `sfx.files`). Board `img` items from the house icon set (`assets/icons/<name>.png`) take `shadow: false`. The creator's look avoids `stamp` / `stampOver`: plain text with one blue word. Big numbers and board texts follow the style's `display` look (family, weight, title color, `flat`; the white paper style = Bricolage Grotesque 800 flat ink on every text, the suffix and unit in blue, see style-schema). Board `counter` takes `clock: true` for a stopwatch: `value` (and `fromValue`) in seconds shown as `mm:ss` (1200 = 20:00), every digit in a fixed slot so the running timer never jitters (pair it with a drawn stopwatch: a dial `img` plus a hand `img` on the same center turned by `rotKeys`, never a line icon). Board `text` takes `font` (+ `weight`, default 400) to override the display families for that text, e.g. `font: 'Instrument Serif'` (bundled serif, single weight 400, also usable as `captions.font`) on an end card. Board `text` and `counter` take `depth: 1` for an embossed big number (ignored when `display.flat`): the face stays flat in its own color, lifted off the paper by a white top edge and a soft cast shadow, never extruded or 3D (the creator rejected the extruded look); a higher number = a stronger shadow (pair it with `captions.hide` over the same span so the caption does not repeat it). Drawn characters: `ostrich {s, downFrom, downTo, upAt, mound, dir}` buries its head in a sand mound and pops it back out with blue wake-up ticks ("arrêtez de faire l'autruche"); `starship {s, igniteAt, liftFrom, liftTo, liftY}` is a stainless Starship with a blue flame and a pad smoke cloud that lifts off (pair it with the SpaceX wordmark as an `img`). `ferrari {s, roll, rollDur}` is a red side-view sports car (wheels on y) that rolls in from the left by `roll` px; set its `y` to the starship pad line to stand them side by side (Ferrari vs rocket).

Board `label {text, size 90, bg, color, rot -.035, skew .2, caps, align, border, stretch, ls}` is the slanted thumbnail label: heavy condensed italic caps (Archivo extra-condensed) on a flat color block, tilted a few degrees, wiping in from the left in .26 s with a pop SFX. `bg`: `'blue'` (the accent, default), `'pop'` (`colors.pop`), `'ink'` or a hex; the text follows (`colors.onAccent` on the accent, ink on a light fill, white on a dark one) unless `color` is set. `'\n'` stacks lines, `caps: false` keeps the case (short links). Box height is about `size * (.98 * lines + .32)`, width about `.5 * size` per character + `.6 * size`. Stack 2 or 3 of them in different colors like a thumbnail, never more than one per idea. Any item's strike takes `strikeColor` (default `'blue'`): use `'pop'` when the accent is a light yellow, a yellow strike disappears on the paper.

Rich board items (use them instead of line icons or toggles: the creator calls engine line icons such as hourglass, message, robot or play "infâme", and rejects switches for an idea like speed vs quality):
- `gauge {r: 170, value: .9, sweepFrom, sweepTo, unit}`: a round speedometer sheet (270° groove, 21 ticks); the ink needle sweeps to `value` with a lagging ghost trail and the blue arc fills. For "rapidité", "puissance", any speed or intensity.
- `pixelate {img, w: 300, h, r: 26, sharpFrom, sharpTo, block: 44}`: a real image that steps from big pixel blocks to sharp, then a white sheen passes. For "qualité", "netteté", "rendu final".
- `render {w: 900, h: 420, title, imgs: [...], progFrom, progTo, prog: .96, total, elapsed}`: a dark render window (traffic lights, mono title, spinner) whose film strip develops real frames one by one behind a blue scan line, with a striped progress bar, `Frame n / total` and an m:ss timer counting to `elapsed`. For "ça rame", "le rendu prend X s". `imgs` paths are preloaded like `img`.

Common: `{type, from, to, pre, layer: 'stage' (default) | 'over'}`. `pre` (seconds) makes the scene enter early, so a hook scene at `from: 0` is already on screen at frame 1. Leave `to` off the last scene (never a far-future value like 99: it maps to the end and fades the scene out under the CTA). Stage scenes ride with the paper, while `over` scenes float above the camera (CTA). Enter is a spring rise, and exit is a fade with a small lift.

### stat
`{value: 100, suffix: '%', countFrom, countTo, y, size: 300, chip?: {text, at, y}}`
An odometer count-up in tabular digits, with the suffix in blue. Keep `chip` off when the caption already says the number.

### race
```js
{ header: {text, at}, footer: {text, at, logo}, countFrom, countTo, winnerAt, chip: {text, at, y}, stack,
  panels: [{name, logo: 'openai' | 'claude' | 'codex', media, offset, cost, costSuffix: '+', time /* seconds */, ar: .625}] }
```
Model race, like the "GPT vs Claude" comparison videos on X: one paper panel per model, side by side (stacked on 9:16 or with `stack: true`). Each panel header shows the logo, the name, the elapsed time and a live cost meter; the generation plays below. Panel `effort` (e.g. `'Medium effort'`) is a dark pill pinned top-left on the media: always set it, a comparison without the reasoning effort is useless. Meters run from 0 between `countFrom` and each panel's own finish, scaled to its real `time`, so the faster model stops first and gets a check. At `winnerAt` the cheaper panel gets the blue ring and its price turns blue; `chip` (the verdict, e.g. "1.8× cheaper") lands under the panels, `footer` sits at the bottom in ink2. SFX are automatic (quiet ticks, a pop per finish, a bell on the winner). Build whole videos from `engine/templates/race.js` instead of writing race scenes by hand.

### bars
`{y, rows: [{label, value 0..1, at, blue, dark}], gapAt, gapChip?: {text, at}, tags?: [{text, at, blue}]}`
Horizontal comparison bars (900 px wide, 230 px per row). `gapAt` draws the ghost bar and a bracket showing the difference. `tags` are chips across the top. `dark` fills a non-blue row in ink3, because the default dim grey is too faint on the track. The first row should land within about .3 s of `from`, or the scene shows an empty sheet.

### columns
```js
{ header: {text, at}, sub: {text, at}, base: 1080, y0: 470, colW: 170, gapIn: 30, gapOut: 90, cx: 540, max,   // max auto
  groups: [{ cols: [{name, sub, value, text, at, blue}], ghost: {at, over: 0, of: 1, chip: {text, at}} }] }
```
Grouped vertical columns, like the Artificial Analysis "Cost per task" bar chart. The header sits at y 240 and the sub at y 300, with dotted grid lines and an ink baseline at `base`. Each column rises at `at` and shows its `text` value above it (46/800), its `name` (42/800) under the baseline and its `sub` (36/600 ink3) below that. A group's `ghost` draws the `of` column's height as a dashed blue outline over the `over` column, with a blue ratio chip (for example "5.7x"). Use seam 1320.

### recap
`{rect: [60, 210, 960], rh: 98, header: {text, count, at}, rows: [{title, sub, at}]}`
A numbered list sheet for outros ("the 9 changes"). The header text is 52/800 with `count` in blue on the right. Rows are 98 px each, with a blue number disc, the title at 44/800 and the sub at 36/600 right-aligned. Height is `118 + n*rh + 18`, so 9 rows end around y 1230: use seam 1300 and put the CTA over it at y 1420. Cascade the rows about .14 s apart.

### convo
```js
{ rect: [40, 200, 1000, 1000], title: 'Claude', model: 'Opus 5.5', size: 42, msgs: [
  { who: 'me', text, from, to },                         // blue bubble, words appear on the creator's spoken words
  { who: 'opus', text, at, offs: [0, .19, ...] },         // streamed reply, offs = word starts in its voice clip (1x s)
  { who: 'opus', image: 'assets/media/x.jpg', at, genFrom, sharpAt, size: 560, label: 'Pixel art' } ] }
```
A live Claude thread for "I talk to the AI" shorts. Every message has its final size from the moment it appears and the thread scrolls up as it grows. The image reply resolves from coarse pixels with a `label · N %` chip. Use seam 1240 and hide captions over the bubble ranges (the bubbles are the captions). Opus voices come from `spec.voices`.

### scatter
```js
{ header: {text, at}, sub: {text, at}, plot: {x0: 170, x1: 960, y0: 420, h: 680},
  xRange: [a, b], yRange: [a, b], xTicks, yTicks, xPrefix: '$', xSuffix: 'k', xLabel, yLabel,
  xLog: true,   // log cost axis, like Artificial Analysis
  points: [{label, sub, x, y, at, color: 'blue' | 'ink' | 'gray', side: 'left' | 'right', dx, dy}],   // no label = small grey context dot
  arrows: [{pair: [i, j], at, card: {text, at, dx, dy, w, sub: {text, at}}}],   // arrow from point i to j + fixed-size delta card
  ref, vs, dyAt, dyChip: {text, at}, dxAt, dxChip: {text, at}, ringAt }
```

An X/Y chart (for example intelligence vs cost). Axes grow in and points pop at `at`, with gray used for context points. `ref` and `vs` are point indexes. `dyAt` draws the vertical gap bracket and `dxAt` the horizontal one, each with a chip. `ringAt` rings the `ref` winner. Use seam 1320 so the plot has room.

When the video shows a real chart (Artificial Analysis, a board screenshot), reproduce **that** chart: the same models, the same effort variants and the same arrows. Take the numbers from the page's embedded data (`curl` the page, parse `intelligenceIndex` and `intelligenceIndexCostPerTask`). Never replace them with the headline defaults. Keep context models as unlabeled dots, and label only the models you talk about. Arrow keys must not be named `from`/`to`, because `mapSpec` would remap them as times.

### tiles
`{y, header: {text, at}, items: [{glyph | logo, label, at, strikeAt}]}`
`pre` also shifts the header and items, so a hook tiles scene with `pre: .5` is fully readable at frame 1.
App-icon tiles in a row, with a hand-drawn strike through each. Use them for "no more X, Y, Z".

### title
`{lines: [{text, at, emph, emphAt}]}`
Big centred statement lines. `emph` is the word that turns blue at `emphAt`. Pair it with a `music.breaks` range so the line lands in the air.

### chat
```js
{ rect: [x, y, w, h], newChatAt, focusAt, prompt: { text, from, to }, sendAt, workFrom, workTo,
  result: { media, offset, at, label } }
```
`result` is optional; `workText` sets the working line (default 'Opus 5.5 crée ta vidéo'). `greeting` (default « Qu'est-ce qu'on crée ? ») and `placeholder` (default « Décris ta vidéo… ») set the empty-chat texts. A Claude-style chat: greeting, "+ Nouveau chat" pointer click, focus the composer, word-synced typing over the spoken words between `prompt.from` and `prompt.to`, send, a working bar, then a result card playing `media`. Hide captions over the typing range.

### switch
```js
{ y: 420, tiles: [{logo: 'codex' | 'claude', label}, {glyph, label}], headerKeys: [[t, 'text']], sideKeys: [[t, 0 | 1]], w: 13,
  chips: [{text, at, side: 0 | 1, blue}] }
```
Two tool tiles (250 px) with a toggle between them. The blue knob slides to the active side on each `sideKeys` time, and the active tile gets a blue ring. `headerKeys` cross-fade the header line above. Chips stack under their side and dim with it. Use it for "X vs Y, now I switch". Built-in logos: `claude` (starburst), `codex` (`>_`), an image path (`assets/logos/x.png`, grayed while inactive), anything else via `glyph`. `y: 330` with the full-paper hook cutout, `y: 420` with seam 1240.

### tree
`{rect: [x, y, w], size: 46, lines: [{text: '├── CLAUDE.md', at, link: {text: 'AGENTS.md', at}}]}`
A project folder in JetBrains Mono on a sheet. Tree glyphs render grey, folders (ending in `/`) extra bold, and `link` slides in a blue `→ target` (symlinks). Lines may appear out of order to follow the voice.

### snap (over)
`{layer: 'over', from, origin: [x, y], r: 1}` a finger-snap burst (rays + ring) with a snap sound. Use it on every "je claque des doigts".

### xylo
`{y, notes: ['E', 'G', 'A', 'C'], midi: [76, 79, 81, 84], hitKeys: [[t, barIndex]], restAt}` a paper xylophone. A mallet springs to each bar, the bar lights blue, a note floats up, and a real mallet note plays (SFX bus). Put `hitKeys` on the sung syllables, and `hold` that range so the rhythm survives the silence cutter.

### sfxtrack
`{y, header: {text, at}, tag: {text, at}, rows: [{label, at, sound: 'snap', clips: [[a, b]] (0..1)}], playFrom, playTo}` an audio-editor lane per sound; a playhead sweeps and lights each clip. For "l'IA a créé les bruits".

### popover (over)
`{layer: 'over', from, to, w: 700, keys: [[t, [x, y]]], title, message: {text, from, to}, buttons: ['Annuler', 'OK'], clickAt}` a macOS alert that lands over the camera, follows where the speaker points (keys), types the spoken message word-synced, and the pointer clicks OK. Hide captions over the typing.

### overlay (over)
`{layer: 'over', media, from, to, offset, fade: 0}` a full-frame transparent clip (a `media` with `alpha: true`) drawn straight over the frame, under the captions. For an app UI animated over the full-screen camera: write the UI as an HTML page with a `window.setT(t)` that sets every style for an instant, then `short.mjs capture <project> source/<name>.html --dur <s> --alpha` (one screenshot per frame, png-in-mov + `stills/<name>-sheet.jpg`). Build these in parallel with sub-agents: `references/sub-agents.md`. Keep it inside a full-screen stretch (seam 0, at least 5 s): a window move draws the camera card over the `over` layer. Pin the captions above the UI with `captions.yKeys`. The media cache follows the file (size and date): a recaptured clip is re-extracted by the next `prepare`. Example: a comment CTA ("commente skill"): the Instagram Reels UI over the face, a finger taps the comments, types and posts the word, then the DM banners drop in, so the viewer feels they must do it now.

### pause (over)
`{layer: 'over', from: 'p+0', to: 'p+9.3', keys: [[t, [x, y, r]]]}` a paper pause badge with a blue ring that fills over the pause, morphing to play at `to`. Keep it off the face.

### Motion-design film (full paper, seam 1920): mdGrid, mdIntro, mdRec, mdWave, mdCut, mdVision, mdDiffuse, mdCode, mdStills, mdRender, mdAssemble
A narrated "how it was made" film, played during a `pause` with layout `[['p+0', 0], ['p+0.75', 1920], ['p+X', 0]]` and the pause badge parked top right (`[964, 296, 52]`) as a progress ring. Each beat slides in from the right and leaves to the left, back to back, so the beats read as one camera move. Every beat takes `step: {n, of: 5, title, sub, logo}` (blue disc + 80 px title at y 430, 5-segment progress rail at y 290, faint giant numeral) and `y: 600` for its content, which then fills about 600 to 1550. A `step.logo` image path draws the real icon right after the title (the giant numeral stays). The beats also work as a whole short with no pause (layout `[[0, 1920]]`). Time each beat on the narrator's words (`p+X` from words.md) and hide captions over the whole pause.
- `mdGrid {from, to}` drifting dot grid behind the film.
- `mdIntro {y: 700, title, sub: {text, at, to, emph}}` logo tile on a turning sunburst with rings, 150 px title, sub words landing on the narrator's words.
- `mdRec {media, offset, clock, stamp: {text, at}}` the raw take playing in a 960x540 card with REC pill and a running timecode up to `clock` s, then a stamp.
- `mdWave {sweepFrom, sweepTo, markAt, words: [[word, sourceSeconds]]}` waveform, sweeping playhead, each word drops into a timestamp list; `markAt` highlights the hundredths in blue.
- `mdCut {markAt, closeAt, speedAt, speed: '+15 %', factor, clock: {start, stop, at, endAt}}` waveform with silences: they get a dashed blue box at `markAt`, collapse at `closeAt`, the speech squashes by `1/factor` with the `speed` stamp at `speedAt`, then a big mono clock counts `start` to `stop` seconds (m:ss) from `at` to `endAt`. The clock keys are `start`/`stop`, never `from`/`to` (those would be time-mapped).
- `mdVision {frameAt, scanFrom, scanTo, flipAt, frames: [a, b]}` one camera frame; a scan line turns the room into a checkerboard with a blue-outlined cutout, then a flip-book counter. `w` (default 940) shrinks the card when captions sit below. `frameAt` (source time) must lie inside a `cutout` range so its matte exists; `frames` = the real matted frame count from the prepare log.
- `mdDiffuse {src, prompt: {text, from, to}, genFrom, sharpAt}` a typed prompt, then the image resolves from coarse noisy pixels to sharp with a flash.
- `mdCode {file, lines: [{text, at, dur, fx: 'xylo' | 'snap' | 'birds' | 'bass'}]}` an editor typing syntax-coloured lines; each finished line plays its `fx` (cues) with notes floating up, and an equaliser below grows with every line (`eq: false` hides it, `notes: false` drops the floating notes).
- `mdStills {enterAt, scanFrom, flagAt, flag, fixAt}` a 4x2 grid of mini shorts (paper card + camera + caption pill); a loupe snakes across them, at `flagAt` thumb `flag` (0 to 7) gets a blue ring and a "!" (its caption overflows), the others dim, and at `fixAt` the caption slides into place and the badge turns into a check.
- `mdRender {total, renderFrom, renderTo, url, bars: [{label, value, frac, at, blue}]}` a browser window rendering a mini short, image counter up to `total` with a progress bar, then comparison bars (e.g. video length vs render time).
- `mdAssemble {flyFrom, stagger, playFrom, playTo, stamp, tracks: [{label, clips: [[a, b]], cam | text}]}` clips fly in from everywhere and snap onto their tracks (cam thumbnails, waveforms, "Aa" caption pills), then a playhead runs.

### pipeline
`{y, header: {text, at, glyph | logo}, rows: [{glyph | logo, mono, title, sub, at, blue}]}` (`header.glyph` replaces the default Claude logo in the header tile) "who did what": a live voice meter in the header pulses while the narrator speaks, rows land on the narrator's words (`'p+X'` from words.md) with a check.

### comment (over)
`{layer: 'over', from, y: 1480, placeholder, typed, clickAt, typeFrom, typeTo, sendAt, button: 'Publier'}` a comment composer CTA with the camera avatar; the pointer focuses it, types `typed` and hits Publier. Use for "dis-moi en commentaire".

### tweet
```js
{ rect: [60, 230, 960], avatar: 'avatar', name, handle, verified: true, text, size: 40,
  footer: '2:41 PM · Sep 29, 2026 · **642.1K** Views', marks: [{ at, text, dur: .7 }],
  media: 'clip', offset: 0, mediaKeys: [[at, offset, 'clipB']], mediaAr: 9/16 }   // optional attached video/image
```
A native X post rebuilt on a paper sheet: 88 px avatar (a `media` key, 176 px PNG), name 40/800, verified badge, handle, X logo, body at `size` 40, hairline and footer. `**bold**` runs work in `text` and `footer`. Each `marks` entry sweeps a blue highlighter over the first occurrence of `text` (line by line) when it is spoken. Height comes from the text, so pick the seam from a still: about 960 for a 4-line post, 1100 to 1240 for 6 to 8 lines. Spread one long thread over several `tweet` scenes (one per point) with a shared base object.
`media` embeds the tweet's own video under the text, like X does. It runs full width with radius 22, at `mediaAr` = height/width (default 9/16, a 16:9 video). The clip plays from `offset` (clip seconds) when the scene starts. `mediaKeys` re-cues it on spoken words: each `[at, offset, id?]` restarts at `offset` and can swap to another media key. Split one long launch video into several `media` entries (`from`/`dur`) and cue the best shot for each sentence. With a 16/9 video the card is about 966 px for 3 lines of text and 1020 for 4, so use seam 1240 to 1300.

### article
```js
{ rect: [60, 0, 960], center: true, logo: 'assets/logos/fortune.png', outlet: 'Fortune', date: '21 juil. 2026',
  kicker: 'AI', headline, headSize: 54, hlMark: { at, dur: .8 }, quote, quoteSize: 38, by: 'Arthur Mensch, CEO de Mistral',
  marks: [{ at, text, dur: .7 }], read: { from, to } }
```
A press source rebuilt natively, never a page screenshot. The card holds an outlet row (64 px logo, name, optional kicker chip, date on the right), a hairline, the headline (a highlighter sweeps it at `hlMark.at`), an optional pulled quote behind a blue rule (`marks` highlight phrases as they are spoken, `read` greys the words not yet said), and the attribution. `center: true` centres the card vertically on the stage. Use the real outlet, headline, date and quote. Leave on screen 6 to 8 s, or 7 to 10 s with a quote.

### Audio ceiling
If the `final` QC shows a true peak above -1 dBTP (AAC overs on dense music), set `mix: { ceil: -2.5 }` (limiter ceiling in dBFS, default -1.5) and rerun `audio` + `final`.

### usage
```js
{ rect: [60, 250, 960], title: 'Plan usage limits · Max (20x)', logo: 'assets/logos/claude.png' /* optional, left of the title */,
  rows: [{ label, sub, value: .03, fill: { value: 1, at, sub: 'Limit reached' }, mark: { at, to } }] }
```
A settings popup of usage meters (label 44, sub 34, % right, 16 px bar). `fill` animates a row's bar and % to `fill.value` at `at` and cross-fades the sub to `fill.sub`; a full bar turns ink. `mark` tints and rings the row from `at` to `to`. 168 px per row, so 3 rows fit above seam 1100.

### chip
`{y, text, size: 44, blue}`: a standalone label. Rarely needed, since captions already do this job.

### cta
`{layer: 'over', name, sub, button, done, clickAt, y: 1420, avatar}`. Texts left out come from the profile (Style layer above). A long name or sub shrinks to stay clear of the button.
A profile card with the avatar cropped from the camera (`avatar: 'assets/images/mascot-avatar.jpg'` puts a picture there instead: faceless styles, never the camera face). The pointer flies in, and the button morphs to a check and `done`. Hide captions from `from` to the end.

### capStyles (over)
`{layer: 'over', from, to, cycleFrom, cycleTo, n: 20, y: 1180, counterY: 300}`. The live caption cycles through 20 caption styles (sticker, pill, karaoke, serif, mono, outline, stacked...) with a `Style 07 / 20` chip and a dot rail. Style 0 before `cycleFrom`; switches cut hard, the fade is per chunk. It draws the captions itself, so hide the normal captions over `[from, to]`.

### camTile (over)
`{layer: 'over', from, to, pre, w: 460, h: 580, keys: [[t, [cx, cy]]], labelKeys: [[t, 'En haut']]}`. The camera as a framed tile on full paper (seam 1920) that glides to each key; the label chip sits mirrored across the screen centre. For "put my camera top / bottom / left / right".

### camSplit (over)
`{layer: 'over', from, to, h: 820, enterFrom: 1240, dur: .7}`. On full paper (layout key `[from, 1920, 400]`), the camera panel rises from `enterFrom` to the top `0..h` with a torn bottom edge and a soft shadow, keeping the face framed. The paper below is free for an image (the masterclass, a product): put it on a `layer: 'over'` board after this scene, and `captions.yKeys` on the seam. For "split screen, moi en haut, X en dessous".

### Faceless (no camera)
For an audio-only video, the speaker is a die-cut sticker of their head (`engine/lib/scenes-faceless.js`, full parameters in its header). Layout `[[0, 1920]]`, `captions.paperY` ~1580.
- `paperFlow {from: 0, to: 99}` first in `scenes`: textured paper that drifts and breathes all video long, a few paper cut-outs floating near the edges.
- `talkHead {face, emo: [{from, to, img}], posKeys [[t, [x, top, w]]], body, crew}`: the head floats and nods on every word, livelier while words are spoken. No lip-sync: one face at a time, `emo` swaps it on emotional beats. `body {at, armsAt, danceAt, shirt, bpm}` grows a paper-cut body and starts a disco dance; `crew` adds friends' sticker heads that pop in and dance. Put it after the floor so dancers stand on it.
- `bgPattern {from, to, keys: [[t, 'squares' | 'diamonds' | 'stripes' | 'none']], x 540, y 1500, a 1}`: the paper background changes pattern on the beat (blue-tint checker, harlequin diamonds, vertical stripes, drifting slowly); each new one wipes in as a circle growing from (x, y). Put it right after `paperFlow`. For "change the background".
- `disco {from, at, y, r, spotsAt}` mirror ball lowering on its string, light spots on the paper. `dancefloor {from, at, y0, bpm}` perspective tiles lighting on the beat. Both need a `from`.
- `mascot {idle, talk: [imgs], poses: [{at, to, img, flip}], posKeys [[t, [x, footY, h]]], jumps: [{at}], headOnlySpans, hueSpans, dance: {at, to, imgs, bpm, beats 2}, crew: [{at, to, imgs, x, footY, h, phase}], sizes: {img: k}}`: a full-body cartoon mascot (preferred over photo heads, which look weird animated). One drawing per beat: `talk` drawings alternate per phrase, `poses` override them on gags, `dance` cycles drawings on the beat until its optional `to` (crew members also take `to` and sink back under the floor). Every swap lands with a squash and stretch, words nod it, `jumps` hop it. `headOnlySpans` cuts the body off at the chin (floating head gag), `hueSpans` cycles its colors. `posKeys` moves and resizes it (springs between keys): keep it alive, walking next to the card it talks about and growing or shrinking with the beat. Pointing poses (`m-point-side`, `m-present`, `m-point-up-side`) point to the right; `flip: true` on a pose mirrors it to point left. `teleport: true` (the Mascotte style default, the creator finds running and leaping weird): every posKeys move wider than 80 px is a teleport instead, he zips thin and vanishes in 0.1 s before the key, a paper poof cloud marks both spots, and he springs back at the new place (size and footY snap with him; smaller moves still spring). Move him only when the beat needs it (a reveal, an element that takes his spot, a hero moment) and let him point from where he stands the rest of the time. Without `teleport`, every move wider than 80 px is an automatic cartoon leap: crouch before, arc, lean into the move, marker speed lines, paper dust on landing; `travelPose` (a running drawing facing right, auto-flipped to the direction) replaces the pose mid-air. `airPose` shows during `jumps` that stay in place, `dust: false` turns the puffs and poofs off. Never put a `jump` just before a move. Pose PNGs are one 3:4 frame, feet at 95%. The `setup-faceless` skill makes them: `scripts/avatar.mjs poses` draws a pose pack from the avatar (engine `images.mjs --raw`, the design as `refs`) and cuts it (`scripts/cutout.mjs --canvas`), `avatar.mjs pose <m-name> "<acting>"` adds one pose to a style.
- `bills {from, at, to, n}` paper dollar bills flutter down (money gag). `confetti {from, at, to, x, y, n, power}` paper confetti burst.

### Clean layout: slide (stage)
Rejected by the creator on 2026-10-07 (camera always at the bottom, too much text): never use it for his shorts; his look is the paper stage with `layout.frame`. Kept only as engine code. With `layout.card` (style the creator Clean, reference `shorts/short-claude-5x-value-clean/`), one `slide` = one idea held 6 to 20 s. Full parameters in the header of `engine/lib/scenes-clean.js`.
- `{type: 'slide', from, to, pre, eyebrow, title: [l1, l2], hl: ['word'], size: 90, items: [...]}`: blue eyebrow at y 231, a heavy 2-line headline that auto-shrinks to 960 px (words in `hl` turn blue), then white glass cards in the zone y 500 to 890 (the caption pill sits at ~968, keep items above it). The slide blurs out at `to` while the next one blurs in.
- Items (absolute 1080 px coords), each with `at`, `outAt`, `dimAt`, `ringAt`:
  - `row`: logo, title, sub, pill; `strikeAt` strikes the title and swaps the pill for `pillAlt`.
  - `stat`: logo, name, plan, a big counter (`value`, `countAt`, `until`), sub, `badge` pill bottom right (`badgeAt`, `badgeTop`). `ghost: true` = a pale "?" card from `ghostAt` that fills in at `at`.
  - `bars`: one glass row per entry, with a track and a counter (`countAt`, `until`, `win` = blue).
  - Smaller kinds: `tweet` (one line), `logo` (`tile: true` = glass tile, `label`), `img`, `pill`, `text`, `arrow`, `card`.
- Name count times `countAt` / `until` (mapped). Never give a value field an `At` / `From` / `To` suffix.
- With `sfx.appear: 'slide'`, each slide and each item gets a soft paper slide and nothing else (no ticks, pops or bells).

## Adding a scene

Add `const myScene = { draw(R, s, t) {...} }` (optional `needs(s, t, U)` returns `[mediaId, clipTime]` pairs or raw URLs: `'/p/assets/…'`, `U.cam(t)`, `U.cut(t)`; read them back with `R.frame()` / `R.img()`) to `engine/lib/scenes.js` and register it in `SCENES`. Use `env()` for enter/exit, `rise()` for elements, and `S()` / `track()` for motion. Add matching sounds in `engine/lib/cues.js`. Name time params with the `At`/`From`/`To` convention.

### crashWall (scenes-crash.js)

A car rams a real 3D brick wall in perspective: road, wall built course by course (each brick a shaded 3D box with ink edges and a ground shadow), the car sticker arrives, revs, rams at `hitAt` and sinks into the hole; the bricks around the impact burst with rigid-body tumbling and settle on the road, the ones above collapse, dust, blue burst, camera shake + zoom punch. Use it for any "crashes into a wall" beat instead of a crash pose image.
`{ type: 'crashWall', from, to, car: 'assets/mascot/m-car.png' (front facing right, bumper at 0.95/0.9 of the image), carH 470, enterAt, buildAt, ramAt, hitAt, lane .8, rows 8, cols 6, brick [120, 56, 62], color '#C8603E', yaw .62, pitch .3, zoom, cx 560, cy 1250, outDx }`. Put a `board` after it for the BOUM text; a `confetti` at about (560, 1060) lands on the impact.

### masterCard (scenes-master.js)

The creator's masterclass card (port of the adMaster ads). Every step optional, keyed on a word: arrowAt (link + arrow), btnAt (button + cursor from cursorFrom), clickAt (press, "Inscription" bar), unlockAt ("Accès débloqué"), playAt..playTo (progress bar, timer, lessons lit then checked). Params: from, to, pre, y 236, eyebrow, title, sub, logo, avatar, badge, badgeAt, lessons [[label, "N min"]], chaptersFrom, chapterStep, linkText, btnText, busyText, unlockText, total, outDx. Faceless: avatar = the mascot image. A title too wide for the room left of the avatar shrinks to fit (never under the avatar). Board items also take rotKeys [[t, rad]].
