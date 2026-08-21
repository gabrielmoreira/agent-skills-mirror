# Content-type → effect matrix (Inspire to Rise)

Pick **primary**, **transition**, and **overlay** from the row matching the beat’s `contentType`. Override in timeline when a beat is mixed.

| Content type | Primary effect | Transition (must be real) | Overlay / caption | Example |
|---|---|---|---|---|
| `motivational` | `KineticQuote` cascade + power word | Whip / punch via `TransitionSeries` or PunchZoom | High-contrast | MJ belief |
| `biographical` | `ArchiveVideo` + `ArchiveStamp` | Soft `fade` | Chip / lower-third | Cold open stamp |
| `legacy` | `PhotoWall` + `ParticleRise` | `FilmBurn` | Warm gold | Coda |
| `struggle` | Subtle `GlitchOverlay` + portrait | Hard cut / match | Desat vignette | Childhood |
| `revelation` | `SpotlightReveal` | `fade` + `LightLeak` | Soft particles | Wish / heal |
| `lyrical` | Karaoke / timed words | Whip on chorus | LightLeak | Song Shorts |
| `news` | `NewspaperHeadline` | `slide` / wipe | Stamp | Announcement |
| `journey` | `SplitCompare` / parallax | Match cut | Stamp | Forge→Heal pivot |
| `identity` | Portrait punch | `fade` | Name plate | Intro identity |
| `chronological` | Timeline + stamps | `fade` | Year chips | Decade montage |
| `empowerment` | Kinetic cascade + scale | FilmBurn | Gold accents | Dare to hope |
| `vulnerability` | Soft vignette; Ken Burns ≤20% | Long `fade` | Whisper captions | Lonely |

## Hard rules

- Prefer **real archive video/photos** over AI stills when available.
- Mute all archive audio under VO.
- Ken Burns alone ≤ **20%** of cut density; kinetic captions on quote lines.
- **Transitions:** use `@remotion/transitions` `TransitionSeries` (or equivalent timed presentations) between beats — overlay-only flashes ≠ transitions.
- **Cut density:** inside beats longer than ~4s, change plate, punch, or caption at least every **1.5–3.5s** (except intentional vulnerability holds).
- **Quote chunking:** never leave a full multi-sentence paragraph on screen for an entire long beat.
- Never delete `keep/` or `final/`; write `*_vN.mp4` beside keepers.
- GPU Remotion: `--gl angle` + NVENC `bin-nvenc` + `--hardware-acceleration required` + `--concurrency 6` + Remotion **≥ 4.0.503**.
- After render: `/reviewresults` until PASS.

## Inference keywords (fallback)

| Type | Keywords |
|---|---|
| motivational | believe, best, dare, rise, dream, hope |
| struggle | lonely, hate, anger, despair, lack, pain |
| revelation | heal, wish, within, spirit, light |
| legacy | world, masters, education, remember, tribute |
| biographical | childhood, born, year, stage, tour |
| lyrical | lyrics, chorus, sing, song |
| news | announce, today, breaking |
| journey | from…to, other side, became, pivot |
