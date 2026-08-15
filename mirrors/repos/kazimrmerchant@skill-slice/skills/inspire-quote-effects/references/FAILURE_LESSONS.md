# Failure lessons — do not repeat (Inspire quote effects)

Source: MJ ForgeHeal long-form v1 (AI stills) + v2 (archive + weak motion), reviewed visually.

## Creative fails

| Fail | What happened | Required fix |
|------|----------------|--------------|
| Static quote cards | Full Oxford paragraphs left-aligned for 20–30s | Chunk to ≤3 lines; progressive KineticQuote; cut on phrase |
| Fake transitions | Only Sequence hard cuts + light glitch/vignette overlays | `@remotion/transitions` `TransitionSeries` between beats |
| Low cut density | One looping clip per long beat | 1.5–3.5s sub-cuts or punch/caption changes inside beat |
| Dark cold open | Near-black Wembley plate + gold text | Brighter select or lift exposure; subject must read at t=0.5s |
| Foreign watermark | “Ultimist…” etc. on archive | Reject plate; re-source Commons/IA clean |
| Mismatched B-roll | Heal line over unrelated stage kids | Match emotion/era to beat |
| Over-glitch confession | Heavy VHS/glitch on lonely | Soft vignette + whisper caption for vulnerability |
| AI silhouette hero | v1 stills only | Archive/portrait first |

## Technical fails

| Fail | Fix |
|------|-----|
| Remotion 4.0.311 on Windows | ≥4.0.503 + HA `required` |
| `public/` junctions | Real file copies into `remotion/public/` |
| HTML downloaded as `.jpg`/`.png` | Check magic bytes; delete corrupt |
| ffprobe-only QA | `/reviewresults` frame Reads |
| `if-possible` silent CPU | `required` + encode proof line |

## Definition of done (after /effects)

1. Gates G1–G8 in `/effects` command pass in code review  
2. GPU render in `final/*_vN.mp4`  
3. `/reviewresults` = PASS  
