# Customisation questionnaire

Ask these before building, **after** the content intake (topic, decision, audience, language,
duration). Group them in one message (or one multi-question prompt when the host offers a question
tool), show the recommended default first, and accept "defaults" as an answer for any block.
Skip a question when the user already answered it or supplied an authoritative asset.

Record the answers in `CONFIG.theme`, `CONFIG.motion`, `CONFIG.sound`, `CONFIG.links` and
`CONTENT.links`, and repeat the chosen settings in the delivery summary.

## 1. Colours

| # | Question | Options (default first) | Maps to |
|---|---|---|---|
| C1 | Which colour ambience? | **midnight** (blue/violet/pink) · ocean (blue/teal) · ember (orange/red) · forest (green) · graphite (neutral grey) · custom | `CONFIG.theme.preset` |
| C2 | Do you have approved brand colours? If yes, which hex values for primary, accent and highlight? | no (use the preset) · yes → hex values | `CONFIG.theme.tokens` (`--blue`, `--accent`, `--violet`, `--pink`, `--grad-text`, `--grad-ui`) |
| C3 | Should status colours keep their meaning (green healthy, amber watch, red alarm)? | **yes** · adjust for colour-blind audiences (blue/orange) | `--ok`, `--warn`, `--bad` |
| C4 | Logo or monogram in the top bar? | **neutral monogram** · approved logo file (SVG/PNG supplied by the user) | `.brand` markup |

Rules: never infer colours from a company name or guess them from a logo; ask for values or an
approved file. Check contrast of `--text` and `--muted` against `--bg` and `--panel` (aim for
WCAG AA). Light themes are not supported by the starter; say so if asked.

## 2. Animation

| # | Question | Options (default first) | Maps to |
|---|---|---|---|
| A1 | How much motion? | **full** (particles, travelling dots, pulses) · calm (static background, no looping effects, slower reveals) · none (final states only) | `CONFIG.motion.level` |
| A2 | Transition between slides? | **fade** · slide (horizontal) · zoom (subtle scale) | `CONFIG.motion.transition` |
| A3 | Pace of staged reveals and auto-cycling steps? | **standard** (110 ms stagger, 2.2 s cycle) · slower (160 ms, 3 s) · faster (80 ms, 1.6 s) | `stagger`, `autoCycleMs` |
| A4 | Simulation speed at 1×? | **standard** (0.42 s per day ≈ 35 s for 84 days) · slow (0.7 s) · fast (0.25 s) | `simSecondsPerDay` |
| A5 | Projected in a large room, streamed, or recorded? | **in-room projector** · video call (prefer calm, avoid fast flicker) · recording | informs A1–A4 |

Rules: `prefers-reduced-motion` always wins over these settings. Keep every slide readable on a
static frame.

## 3. Sound

| # | Question | Options (default first) | Maps to |
|---|---|---|---|
| S1 | Sound effects? | **off** (presenter can toggle with M) · on | `CONFIG.sound.enabled` |
| S2 | Which moments? | navigation · reveals · poll/vote clicks · **alert** · **decision** | `CONFIG.sound.events` |
| S3 | Volume? | **soft (0.35)** · very soft (0.2) · normal (0.6) | `CONFIG.sound.volume` |
| S4 | Synthesized tones or your own sounds? | **synthesized** (Web Audio, no files, offline) · approved audio files you supply | `CONFIG.sound.files` (embed as `data:` URIs) |

Rules: browsers only play audio after a user gesture, so the first sound happens after the first
click or key press. Use only audio the user owns or is licensed to use; never download sound
effects without approval. Remind the presenter that room audio must be connected.

## 4. Links and their context

| # | Question | Options (default first) | Maps to |
|---|---|---|---|
| L1 | Which links should the audience get? For each: label, URL, type (documentation, source, demo, repository, survey, contact) and **why it matters for this workshop** | none · list | `CONTENT.links` |
| L2 | Where should they appear? | **"Links & sources" slide + synthesis** · also cited in the notes of the slide that uses them · synthesis only (remove `s-links`) | `s-links`, `CONFIG.links.inSynthesis`, notes |
| L3 | Who can open them? | **public** · internal (requires an account or network) · mixed (say which on each card) | card context text |
| L4 | Open in a new tab? | **yes** · no | `CONFIG.links.newTab` |
| L5 | Are the figures in the hook or simulation sourced, or illustrative? | **illustrative** (keep disclaimers) · sourced → add the source link and date | link `kind:'Source'` + disclaimer text |

Rules: only `http(s):` and `mailto:` URLs are rendered. Use links the user supplied or explicitly
approved; do not invent URLs or add tracking parameters. Check that each URL resolves when
network access is allowed, and report links you could not verify. Keep the deck usable offline:
links are extras, never required to follow the workshop.
