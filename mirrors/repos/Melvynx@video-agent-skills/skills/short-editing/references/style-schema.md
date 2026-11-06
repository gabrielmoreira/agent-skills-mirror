# Creator profile: style.json

In this free pack the profile folder is `<project>/video-agent/` (it plays the role of `.short-editing/` below): `video-agent/styles/<name>/style.json`, edited by hand. `profile.mjs` and `preview.mjs` belong to the paid kit; check a change with `short.mjs stills`.

`<project>/.short-editing/styles/<name>/style.json`: one per style, the default one included; `<project>/.short-editing/style.json` only names the default, `{"default": "<name>"}` (an older profile keeps its default style right there). LOCAL only, the nearest `.short-editing/` from cwd up (home folder excluded, `$SHORT_EDITING_HOME` forces one). Never `~/.short-editing/`. Written only through `scripts/profile.mjs set [--style <name>]` (validates, backs up to the style's `history/`, rewrites its `STYLE.md`). Every key is optional: a missing key keeps the engine default.

Layer order at render: engine defaults < `<project>/source/style.json` (snapshot copied by `short.mjs init`) < the project's `spec.js`. A spec value always wins, and a short made before a profile change keeps its old snapshot.

## Full example

```json
{
  "version": 1,
  "name": "Craft",
  "creator": {
    "name": "Léa", "handle": "@lea.ia", "lang": "fr",
    "niche": "IA et productivité pour les indépendants, 25-40 ans",
    "cta": { "sub": "Plus de tests IA", "button": "S'abonner", "done": "Abonné" }
  },
  "colors": { "paper": "#EFE7DA", "ink": "#1F1A17", "accent": "#E8590C" },
  "font": { "family": "Satoshi", "src": "~/my-project/.short-editing/fonts/Satoshi-Variable.ttf" },
  "paper": { "grain": 1 },
  "captions": { "style": "pill", "size": 84, "weight": 800, "maxWords": 3 },
  "pace": { "speed": 1.15, "tighten": { "sentence": 0.08, "comma": 0.05, "word": 0.03, "lead": 0.03, "tail": 0.8 } },
  "visual": "mix",
  "music": { "bpm": 112, "drive": false },
  "mix": { "music": -28, "sfx": -28.5, "duck": 0.5 },
  "folders": { "aroll": "~/Movies/A-roll", "broll": ["~/Movies/B-roll", "~/Pictures/Screens"], "shorts": "~/Movies/Shorts" },
  "camera": { "w": 1920, "h": 1080, "crop": [360, 0, 1200, 1080], "eyes": [600, 380] },
  "images": { "provider": "codex", "model": null, "style": "flat editorial illustration, soft paper texture", "palette": true },
  "notes": ["Jamais de B-roll stock générique", "Toujours un chiffre clé en grand dans les 5 premières secondes"]
}
```

## Keys

| Key | Values | Used by |
|---|---|---|
| `version` | `1` | |
| `name` | label of the style ("Craft", "Night") | STYLE.md |
| `creator.name` | name on the CTA card | `cta` scene (`withStyle`) |
| `creator.handle` | `@handle`, no spaces | preview hook chip, agent copy |
| `creator.lang` | ISO code `fr`, `en`, `es`... | `short.mjs words` (transcription language), default CTA words, agent copy |
| `creator.niche` | one sentence: topic and audience | agent (hooks, titles, examples) |
| `creator.cta.sub` / `button` / `done` | CTA card texts. Missing ones default by `lang` (fr: "Plus de vidéos", "S'abonner", "Abonné"; en, es, pt, de, it built in) | `cta` scene |
| `colors.paper` / `ink` / `accent` | hex. Everything else (sheets, grays, lines, accent dark and tint) derives from these. Optional pins: `sheet`, `ink2`, `ink3`, `line`, `dim`, `accent2`, `tint`. `onAccent`: text color on the accent (caption blocks, `blue` chips, accent labels), default ink on a light accent and white otherwise. `pop`: a second label color (board `label` with `bg: 'pop'`, default ink), e.g. the podcast violet next to its yellow accent | `kit.setTheme` |
| `font.family` | CSS family. Built in: `Inter`. A system font works on this Mac only; for anything else give `src` | every text |
| `font.src` | `.ttf` / `.otf` / `.woff2`, copied into `$SHORT_EDITING_HOME/fonts/` by `profile.mjs font` | served as `/style-font` |
| `paper.grain` | 0 (flat) to 1.5, default 1 | paper texture |
| `paper.tooth` | 0 (none, default) to 1.5: embossed paper relief (fine tooth + soft waves of a real sheet) | background, sheets |
| `paper.toothCell` | tooth bump size in px, default 2.5; 1 to 1.5 = a crisp fine tooth instead of a soft stucco | background, sheets |
| `paper.waves` | 0 to 1.5, defaults to `tooth`: the large soft cockle of a real sheet (0 = off, it reads as blur on 16:9) | background |
| `paper.mottle` | 0 to 1.5, defaults to `grain`: the large soft light/dark blotches (low = crisp grain and fibers only) | background, sheets |
| `paper.depth` | 0 (flat) to 2, default 1: every shadow scales with it; above 1 adds an ambient shadow, a contact line, sheets lit from above and a key light on the paper | shadows, sheets, captions, seam |
| `paper.bg` | `paper` (default, textured sheet), `clean` (flat light gradient + a soft accent glow) or `flat` (the paper color alone, no grain, relief or vignette: a solid color background like the nico-slowdown orange) | background |
| `paper.dots` | `true` or `{pitch, r, alpha, color}` (40 px, 2 px, .07, white), `bg: 'flat'` only: a faint dot grid over the flat color, centered on the frame (a dark dotted UI panel over the camera) | background |
| `paper.shadow` | `'r,g,b'` tint for every shadow and hairline, e.g. `'16,40,64'` (cool) for the clean look | shadows |
| `layout.frame` | `true` or `{m, gap, bottom, r, border}`: in split the camera is a framed photo pinned on the paper (margins, rounded corners, white border, deep shadow); the window moves grow it to full screen | layout |
| `layout.seam` | a number (e.g. `1240`): the camera card keeps ONE size for the whole short. `init` writes `layout.keys: [[0, <seam>]]` in the starter spec; never add a move between two seams or a `zoom.keys` punch-in. Only 1920 (camera hidden) or 0 (full camera) when the style notes allow it | init, layout |
| `grade` | e.g. nico-slowdown's moody look `"eq=contrast=1.08:saturation=0.95:gamma=0.97,vignette=angle=PI/3,unsharp=5:5:0.6:5:5:0"`; `true` (default grade fitted to the take's face exposure: a dim room gets brighter, less saturated, solid blacks; a well lit take keeps its exposure, only less orange and a bit less saturated; a touch of clarity) or an ffmpeg filter chain; baked into the camera at `prepare` | grade |
| `layout.card` | `true` or `{x, y, w, h, r, zoom, bias, capY}`: the camera in one fixed rounded card at the bottom, stage on top (clean `slide` scenes) | layout |
| `header` | `{brand, mark, tagline}`: a heavy italic wordmark top left (mark in the accent) and a gray tagline top right, on every frame of a card layout | header |
| `captions.style` | one of `sticker pill box caps karaoke underline serif chip highlight outline punch light split tiles tilted typing accent stacked brackets bar clean rise hard stack band dim`, or 1 to 26 (board order). `dim` (speedy-devv): the phrase builds word by word on centered lines, spoken words in `captions.color` at `captions.dimWeight` (500), the current word in `captions.hi` at `captions.weight`, an `emph` word keeps a full-radius dark pill (`captions.pill`, default `#2B2B2B`) once said, each word blurs in. `band` (justyn-ai): the whole line on one flat block (`captions.bg`, default ink) in `captions.font` / `weight`, words white (`captions.color`), `emph` words in `captions.hi` (default the tint), hard in and out, no motion. `captions.bg: 'none'` (aiwithremy): no block at all, the white words sit on the video with a soft shadow (`captions.shadow: false` drops it), e.g. small lowercase Geist Pixel on the chest. `rise` and `hard` are block looks: the word being said sits on an accent block (`rise` blurs it in, sharp in ~.15 s, and fades it out in place, `hard` fades it in and out with a hard ink offset shadow); in split the line sits on the paper just above the camera (ink words), full screen on the video (white words). `captions.block: false` (rise only): no accent block, each white word appears when said and blurs in on its own (benkimball.ai). `stack` (nico-slowdown): full camera = a column of small bold words on short staggered lines with the key word huge in condensed Archivo 900 caps, white with a soft shadow, words popping in as said; paper only = the same column centered; split = only the word being said, on a white label straddling the seam (keys below) | live captions |
| `captions.big` / `stretch` / `smallW` / `stagger` / `fullY` / `paperY` / `margin` / `color` | `stack` only: key word size as a multiple of `size` (3.2), its `font-stretch` (`extra-condensed`), max line width of the small words (380), horizontal stagger of the small lines (70), center y of the column on full camera (760) and on paper (960), side margin (90), word color (`#FFFFFF`) | live captions |
| `captions.labelFont` / `labelWeight` / `labelSize` | `stack` only: the split label (word being said, accent on a white rect at the seam), default the captions font, 500, `size` | live captions |
| `captions.size` | 32 to 130 px, default 84 (the style's own base, e.g. 42 for `clean`) | live captions |
| `captions.weight` | 300 to 1000, default 800 (`rise` 900, `hard` 800) | live captions |
| `captions.font` | CSS family for the captions only. Default: `font.family`, except `rise` (DM Sans) and `hard` (Bricolage Grotesque). Built in: Inter, DM Sans, Bricolage Grotesque, Archivo, Archivo Black, Poppins (600 only), Bowlby One SC (400 only, heavy wide small caps: lowercase letters draw as small capitals), Geist Pixel (the Square pixel cut of Geist, 400 only, monospaced bitmap look, aiwithremy captions) | live captions |
| `display.font` / `display.weight` | family and weight of the big numbers: board `counter`, `stat` values, `depth` texts and board texts of 100 px and more, e.g. `Archivo Black` / 400 (a single-weight face). Unset = Inter 800 | `kit.D` |
| `display.text` | family of the other board texts and counter units, e.g. `Archivo` | `kit.D` |
| `display.title` | color token for board texts of 64 px and less that set no color, e.g. `ink2` | `kit.D` |
| `display.flat` | `true` = drops the emboss of `depth` texts and counters (flat ink faces; counter suffix and unit stay in the accent) | `kit.D` |
| `captions.tracking` | letter spacing in em of `size`, e.g. `-.08` to tighten a monospaced face (Geist Pixel for aiwithremy's proportional pixel captions); default -.012 em for block looks, -1.5 px otherwise | live captions |
| `captions.space` | word gap as a multiple of the font's own space, e.g. `.6` for a pixel font whose space is too wide (aiwithremy); default 1 | live captions |
| `captions.bold` | `band` captions: faux bold for a single-weight face, a square stroke in the text colour of `bold` x `size` px, e.g. `.05` to thicken Geist Pixel into aiwithremy's chunky pixel captions | live captions |
| `captions.upper` | every caption word in capitals (any style), e.g. black Geist Mono chips | live captions |
| `captions.radius` | `band` captions: corner radius of the block as a multiple of `size` (default `.06`; `.2` = a rounded chip) | live captions |
| `captions.shadow` | `band` captions: `true` drops a soft shadow under the block (with `bg: 'none'`, `false` removes the shadow under the bare words) | live captions |
| `captions.maxWords` | 1 to 8 words per chunk, default 3 | caption chunking |
| `pace.speed` | 0.9 to 1.4, default 1.15 | timeline |
| `pace.tighten` | breath kept after a `sentence` / `comma` / `word`, and `lead` / `tail` (seconds) | timeline |
| `visual` | default visual mode: `motion` (motion design), `broll` (own footage full screen), `mix`; `ask` (old value) and absent = `motion`. Never asked: `/short-editing broll <source>` forces B-roll for one short | agent, STYLE.md |
| `music.bpm` | 60 to 180, default 112 (generated score, only for drum drops or a tape stop; the bed itself comes from the library, `spec.music.bed`) | score |
| `music.drive` | `true` = four-on-the-floor, punchier | score |
| `music.src` / `offset` | own track (mp3, wav, m4a) and start point in it (s). Replaces the generated bed, looped, ducked | `audio.mjs` |
| `music.mute` | `true` = no music | `audio.mjs` |
| `music.dropOn` / `dropLen` / `dropDepth` | `'punch'` / `'cut'` (or both): the bed drops out .3 s to 6 % under every punch-in / hard cut | `audio.mjs` |
| `sfx.kit` | `{cut, pop, punch, gain: {cut, pop, punch}, gap}`: sound files (project-relative, ship them in the style's `assets/sfx/`, `init` copies them) played automatically on every cut, sticker / logo entrance and punch-in | `audio.mjs` kitHits |
| `zoom.drift` | e.g. `.008`: slow push per shot (0.8 %/s, restarts on each cut and punch; 2 %/s read as aggressive) | `runtime.js` |
| `zoom.wideOnly` | `true`: only the wide shots push (keyed zoom 1.02 or less), the punched-in shots hold still | `runtime.js` |
| `captions.outline` | `{color, width: .07, until}` (stack captions): the hook's big words get a thick colored outline, until source `until` (default the first chunk's end) | `runtime.js` |
| `captions.zoomDrop` | px (e.g. 320) per 1x of zoom: the full-camera stack slides down on a punch-in so it stays under the mouth | `runtime.js` |
| `captions.tall` / `smallDisplay` / `snap` / `paperBig` | `stack` only: vertical stretch of the letters (1.5 = Nico's tall poster caps), small words in the same condensed display face (`true`), each word cuts in whole on its start with no fade (`true`), and on bare paper the words pack into full-width poster lines at `paperBig` x `size` (4.6) instead of one big word per line | `runtime.js` |
| `cuts` | `'hard'`: every board, cutout and full-screen B-roll appears and leaves in one frame (a straight cut, no .26 s fade out, the next board does not wait); a scene, cutout or B-roll opts out with `hard: false` | `runtime.js`, `scenes.js` |
| `mix.music` / `mix.sfx` | -45 to -10 LUFS (defaults -28 / -28.5) | mixer |
| `sfx.accents` | 0 to 1.5 (default 0 = off) | a few glassy blips on key moments (logo or icon landing, blue bar full, speaker tag, strike), at most one every `sfx.accentGap` s (default 1.5) |
| `mix.duck` | 0 to 1, how much the music dips under the voice (default 0.5) | mixer |
| `folders.aroll` | folder of talking-head takes | `init --source latest` (newest video there) |
| `folders.broll` | folder or list of folders of B-roll (own footage, screen recordings, photos), indexed into `broll/broll.db` | `broll.mjs scan`, agent |
| `folders.shorts` | where new short projects go (`<folder>/short-<slug>/`) | agent |
| `camera` | `{w, h, crop: [x, y, w, h], eyes: [x, y]}` for takes of that size, from `profile.mjs camera <take>` | `init` (other sizes: face detection) |
| `images.provider` | `auto` (codex, then openai, then gemini, whichever works), `codex`, `openai`, `gemini`, `none` | `engine/images.mjs` |
| `images.model` | provider model override (openai default `gpt-image-2.5-flare`, gemini `gemini-3.1-flash-image`) | `images.mjs` |
| `images.style` | style suffix added to every prompt | `images.mjs` |
| `images.palette` | `true` (default): the profile colors are named in prompts | `images.mjs` |
| `notes` | list of short rules the agent follows in every short | STYLE.md, agent |

Keys: `ELEVEN_KEY` (transcription), `OPENAI_API_KEY`, `GEMINI_API_KEY` live in `$SHORT_EDITING_HOME/.env` (mode 600), never in style.json.

## Validation

`profile.mjs set` refuses a write with an error (bad hex, out-of-range number, unknown caption style, missing font or music file, bad camera shape, unknown image provider). It saves with warnings for weak contrast (ink on paper under 7, text on the accent under 3, accent on paper under 2.2: fine for a light accent like yellow used only as a fill, never as text on the paper) and folders that do not exist yet.
