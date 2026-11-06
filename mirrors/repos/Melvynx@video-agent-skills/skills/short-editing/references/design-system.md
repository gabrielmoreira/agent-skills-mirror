# Design system: paper, one blue, Apple-calm motion

## Palette (engine/lib/kit.js `C`)

| token | hex | use |
|---|---|---|
| paper | #F1EEE6 | stage background (grain + slow light drift) |
| sheet | #FCFBF8 | cards, chips, caption outline |
| ink | #14161B | text |
| ink2 / ink3 | #5C5F68 / #A19F98 | secondary text, muted labels |
| line / dim | #E3DED3 / #D8D3C7 | hairlines, ghost bars |
| blue | #258EFF | THE accent (codelynx.dev/aibuilder primary) |
| blue2 / tint | #1D6FD6 / #E6F0FD | pressed state, soft blue fills |

Use one blue per moment. There are no gradients, no neon, and no second accent color.

## Type

- Inter (variable). Headlines 800 with negative tracking (about -3.5% of size). UI 600/700. Captions 84/800. Card labels 42/700. Nothing under 34 px (mobile).
- JetBrains Mono only for code or prompts.
- Interfaces use the Apple system font (the creator 2026-10-18, review v2 of short-skills-montage-testes: « pour toutes les interfaces ... la font par défaut d'Apple rendrait mieux »). Every UI drawn in a captured component (a window, its title bar, an app, a sales page, a dashboard, a stats screen, a chat, a phone screen) sets `font-family: "SF Pro", -apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue", sans-serif`, and its monospace text (a transcript, a terminal, code) `"SF Mono", ui-monospace, Menlo, Consolas, monospace`. Name `"SF Pro"` / `"SF Mono"` FIRST: `capture` injects them from `engine/short.html` (`@font-face` on `/System/Library/Fonts/SFNS.ttf` and `SFNSMono.ttf`); headless Chrome ignores `-apple-system` and falls back to another face (review v3: the UI still came out in Bricolage and Menlo). Check a zoomed frame of the .mov, not the tiny sheet. Chrome text keeps the real browser weights: the address in a URL bar is regular (400), never semibold (review v4: « toujours dans l'url »). Since review v5 (« faut utiliser la font système dans toutes les UI et motion design »), the motion design texts of a component use it too: the big hook title over the boards, labels, encarts, tags, counters, the demo of a caption style inside a UI. Only the captions keep the font of their caption style. Audit a page before rendering with CDP `CSS.getPlatformFontsForNode` at several t: every text must report `.SF NS` (or `.SF NS Mono`); a text inserted by `setT` later in the clip is missed by a t=0 check. Optical size (review v6, « ce n'est pas la bonne fonte », after four rounds): SFNS.ttf is variable on `opsz` 17 to 96 and Chrome sets it to the px size, so UI text drawn at 34 to 42 px came out in the tight **Display** cut, which never looks like a real interface. Every UI text uses the **Text** cut with its natural spacing: `body, body * { font-variation-settings: "opsz" 17 !important; letter-spacing: 0 !important; }` at the top of the page's style; only big motion titles (60 px and up: the hook title, a hero word, a price tag) opt back into `font-variation-settings: normal` with their own negative tracking. Compare a zoomed frame with a native AppKit `NSFont.systemFont` render at 13 pt (Text cut), never at a big size.

## Motion

- Calm is the easing, never the content: springs that never overshoot, and on every beat an action (the creator 2026-10-21: no screenshot, no still illustration, no lone logo; a software idea is played in a recreated UI, the hook is a 2 or 3 act mini story). SKILL step 3 and the style's notes hold the bar.
- `S(x, w)` is a critically damped spring: it never overshoots and settles in about 4.7/w s. `w = 9..16` suits UI, and `w = 24..30` suits captions and typing.
- `track(t, keys, w)` retargets smoothly between keyframes.
- Enter: rise 20 to 90 px plus a fade. Exit: fade plus a 30 to 50 px lift. Scale changes stay within 0.965 to 1.

### Premium choreography (built into the engine, every spec gets it)

- **Exits are shorter than entrances and end clean.** Every scene, board item, cutout, ring and arrow leaves with `leave(x)` (kit.js): a .26 s smoothstep to exactly 0, translating on an accelerating curve. Never a spring exit: `S(x, 16)` leaves a 5 to 17% ghost for .2 to .4 s that muddies the next beat.
- **Beats are sequential, never an in-place crossfade.** A scene that starts within .35 s of the previous scene's exit on the same layer enters at `prev.to + .16` (`linkScenes` gate; `gate: false` opts out). Two board items in the same slot (within .6 s, |dx| < 300, |dy| < 90) hand off: the new one waits until the old is gone (`to + .24`; `slot: false` opts out). Two numbers never stack.
- **No parked zeros.** A counter enters with its count (`countFrom - .12`), never sits on "0 $" while the voice has not said the number (`hold: true` keeps the authored entrance).
- **Shared-element morphs between beats.** When the next beat shows the same object bigger (the tweet's chart becoming the zoomable chart window), the board item takes `morph: true` and grows out of the previous scene's `hand()` rect (`morphDur` .62, smootherstep) while the old chrome fades. Tweets expose their media block; add `hand(s, R)` to any scene that should hand something on.
- **Hero, then place.** A logo or object introduced by the voice enters big and centered (`posKeys` + `scaleKeys` 1.3 to 1.7), then glides to its slot (`posW` 12 to 14 drives both) before the number or the next object needs the room. The glide must land before the next item enters.
- **An idea the speaker develops is ONE tableau that stays and grows** (the creator 2026-10-16 on vendre-saas: « ça switch trop vite ; il développe une idée donc on peut afficher une animation qui reste et qui développe l'idée », then « les longues animations rendent beaucoup mieux »). Across the sentences of one idea (a marketplace, an example, a story), a single board carries it: a central object, then each sentence adds or moves one element (hero then place, travels between two places, a scale bump on its word, lines that tie them, a morph of the centre into the next state); nothing leaves unless the sentence drops it. Quick swaps (a new board every 1.5 to 2.5 s) only where the speech changes idea. Text is fine when clean (a counter with its unit, one straight label).
- **Holds breathe.** A board held 3 s or more gets a slow .025 push-in (default; `push: 0` freezes it, a number sets it).
- **Captions never sweep across the stage.** On a split to split move (960 to 1240) the caption fades out, waits while the card moves, and fades back in 14 px below its new line; split to full screen lerps between the two rest lines. The rise block blurs in and fades out in place, never grows, shrinks or slides; the rise line blurs in too (no slide).
- **One look per role.** The same kind of beat moves the same way all along the short (each hero number enters at the same slot with the same rise), so the eye learns the grammar.
- Forbidden: pulse, bounce, elastic, overshoot, glow, shake, "kiss" pops, spinning, confetti, emoji characters typed in text (icons are Noto images, below).
- Motion design over emojis (the creator 2026-10-16, review v1 of short-claude-tue-copywriting: « pourquoi autant d'émoji ... on utilise généralement motion design > emojis de con »): never illustrate a beat with emojis (hero, card bullet, check, decoration). Each beat is real motion design: a captured HTML component (the real app UI, pictograms drawn in SVG/CSS and lifted with a shadow, a check that draws as a stroke), real logos, typography or a paper illustration. In any card, graphic and text share one vertical center. References: shorts/short-claude-efface-internet, shorts/short-teste-ton-business-dans-claude. The Noto set below is a last resort, only when the creator asks for it.
- Icons (last resort, see above): the house set only, Google Noto Emoji in color (the creator 2026-10-15: "garde Noto comme librairie par défaut partout", after a side-by-side test with Fluent 3D and Phosphor on the Editing IA Pro VSL; it replaces the Phosphor rule of 2026-10-11). The bare emoji on transparent: `assets/icons/<name>.png` (the same image sits in `glyph/<name>.png` for older specs), copied into `<project>/assets/icons/`, an `img` item drawn with `shadow: false`, checks included: never the engine-drawn `check` item nor the line icons `k: 'icon'`, never a tile or a square around it (the creator called the tile around a check "un carré dégueulasse", 2026-10-11). Built by `assets/icons/build-icons.mjs` (Noto SVGs from the Iconify API, one request, kept in `svg/`): a missing icon is one line there (house name, Noto name from icon-sets.iconify.design/noto), never drawn by hand. Never Phosphor, Fluent 3D or Apple emoji. Money in euros = the 💶 banknote (`money`), never a `$`. Real logos keep `paper.logos: "flat"` (no soft halo, a hairline edge). No stamp badges as decoration: plain text with one blue emphasized word. A stamp only as an action that lands on its spoken word with a thud (REPLACED landing on an app in a hook, « Gratuit » on a price falling to 0). A style with its own illustration library (podcast: `styles/podcast/illustrations/library`) uses ONLY that library for objects and reactions, reused from short to short, never Noto (the creator 2026-10-16: « non faut utiliser des illustrations custom partout et les réutiliser si besoin »).
- Clicks are a 5% press (`press()`), never a bounce.

## Paper

- Background: fibre grain plus a very slow light drift. It is subtle and should read as texture, not noise.
- Sheets: layered soft shadow (pre-blurred 9-slice, no per-frame blur), a grain fill and a hairline edge. `elev` 0 to 2.
- Depth and paper come from the profile: `paper.depth` scales every shadow (above 1: ambient shadow, contact line, sheets lit from above, inset bar tracks, raised logos and fills, a key light on the paper) and `paper.tooth` embosses the paper. At their defaults (1 and 0) the look is the original one.
- Seam: a deckle-edge tear between paper and camera, with a soft shadow on the camera side.

## Layout (1080x1920)

- Paper stage on top, camera below, split at `seam`. Content scenes are authored for their seam, so keep them above it.
- Camera: crop around the face. `eyes` keeps the eyes in the upper third of the camera area.
- Captions follow the style's `captions` look, never a look picked by hand (e.g. `band`, one black #111 chip in Geist Mono 800 capitals, 58 px, 3 words max, emphasis in light blue #5EA8FF, straddling the seam; `rise`, the spoken word on a blue block that blurs in, only when a style or the creator asks for it; `captions.blur: false` makes rise crisp). In split they sit on the paper just above the camera card, full screen on the video. 3 words and 16 characters max, emphasis words in blue.
- Cards never change size. A card keeps one width (800) for its whole life; keys only move it. Its label sits ABOVE the card (dot + text), never straddling the edge. No stacked sheets behind cards.
