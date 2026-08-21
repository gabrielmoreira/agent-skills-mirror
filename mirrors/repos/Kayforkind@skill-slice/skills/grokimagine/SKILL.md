---
name: grokimagine
version: 2.2.2
description: >-
  Grok Imagine via SuperGrok Heavy in real Chrome (Playwright CDP). Prefer Video
  I2V with parallel fire (submit→close tab→next; harvest later); Image locks;
  Agent films; UUID export. Trigger on /grokimagine. Never Cursor IDE browser.
  Ask before xAI API credits. Existing character films: continue the Agent
  conversation — never New Generation / home Video (face drift).
last_updated: 2026-08-13
---

# grokimagine — SuperHeavy + real Chrome

**Slash:** `/grokimagine`  
**Video UI deep-dive:** [`VIDEO.md`](VIDEO.md)  
**Also:** `reference.md` · `examples.md` · `QA-CHECKLIST.md`

## Hard rules

1. **Real Chrome only** — Playwright `connectOverCDP` to owned hub (`browser-connection` v3+).
2. **Never** `cursor-ide-browser` for Grok Imagine.
3. Prefer **SuperHeavy membership** over xAI Imagine API; **ask** before API spend.
4. Default batch **≤4** stills (standing); ask above that. **Video parallel fire:** submit on a tab, **leave that `/post/` tab generating**, open a **new** Imagine home tab for the next job. Harvest later. **Do not** click New Generation / close the generating post tab (that cancels the job — posts then 404 back to `/imagine`).
5. After proven change: update this skill **and** vault.
6. Agent films: UUID download + story-order concat — do not assume UI Stitch.
7. One owned Chrome: `$env:CHROME_USER_DATA` or `~/Chrome/UserData`, CDP `http://127.0.0.1:9222`, already-signed-in account.
8. Attach `contexts()[0]` — never `chromium.launch()` / invent `--user-data-dir`.
9. Signed out or `#subscribe` paywall → **stop**; human fixes in owned window.
10. Readable words on finals = Remotion/SVG/real UI capture — not AI typography plates.
11. **Don't leave idle duplicate Imagine homes** — after a clip is *generating*, open a fresh home tab for the next fire; leave generating posts alone. Dedupe leftover empties with `_dedupe-tabs.mjs` (never close `/post/` tabs still generating).
12. **Engaging picture = Video**, not Image+Ken Burns. Prefer **I2V** from full-body locks; Image is for locks/refs only.
13. Harvest: require video `src` tied to the post (or midframe QA). Never grab the largest sidebar/history video on `/imagine` home — that is how perfume/nurse contamination happens.
14. **Character series / extra beats:** If the pack has `agent_url.txt` or the user pastes `/imagine/agent/{uuid}?conversation=…`, generate **only** by continuing that Agent conversation (`agent-continue.mjs` / `agent-short-film.mjs nudge`). **Never** New Generation and **never** home Video I2V (`generate-video.mjs`) for extra story beats — that mints a new Imagine project and **drifts faces**. `conversation=` is the film identity (workspace UUID can be reused across films). Video 1.5 multi-ref is a separate one-off I2V path, not a substitute for an existing Agent canvas.

## What to use when (YT / essay)

| Need | Mode | Notes |
|------|------|--------|
| Suit / hero lock still | **Image** | ≤4; Quality; 16:9 or 9:16 |
| Engaging B-roll / action | **Video I2V** | Upload lock; 1080p; 10–15s; motion prompt |
| No lock yet | **Video T2V** | Weaker identity; still motion-first |
| Longer beat from a keeper | Post **Extend** | `/imagine/post/{uuid}` |
| Multi-panel short film | **Agent start** | New Generation → Agent **only for a brand-new film** |
| Extra beats on an existing character film | **Agent continue** | Same `/imagine/agent/{uuid}?conversation=` — never home Video |

## Live UI contract (verified 2026-08-10)

Composer radiogroup **`aria-label="Generation mode"`**: Image · Video · Agent.  
Unselected radios often have **empty text** → click `[role=radio][aria-label="…"]`.

**Video controls:** 480p/720p/1080p · 6s/10s/15s · `Video audio` · `Aspect Ratio` · `Upload` (image file input, multiple) · `Submit`  
**Post page:** Make video · Extend · Upscale · Regenerate · Download · Expand video · Video quality (HD)

Helpers: `scripts/ui-mode.mjs` · Video guide: `VIDEO.md` · Probes: `probe-imagine-video*.mjs`

## Modes (scripts)

| Mode | Script | Success |
|------|--------|---------|
| **status** | `check-and-generate.mjs status` | Signed in, composer |
| **image** | `generate-stills-clean.mjs` | Durable stills |
| **video** | `generate-video.mjs` | T2V/I2V. Use `GROK_FIRE_ONLY=1` to submit→close→next; harvest later |
| **agent start** | `agent-short-film.mjs start` | Brand-new film only (clicks New Generation) |
| **agent continue** | `agent-continue.mjs` | Existing `/imagine/agent/{uuid}?conversation=` + new UUIDs |
| **export** | `export-agent-film.mjs` | UUID MP4s + frames QC (harvest wave) |

```powershell
# Parallel fire one I2V shot (no wait for MP4)
$env:GROK_OUT = "<pack>\raw\...\videos"
$env:GROK_IMAGE = "<lock.png>"
$env:GROK_PROMPT = "..."
$env:GROK_VIDEO_RES = "1080p"
$env:GROK_VIDEO_DUR = "10s"
$env:GROK_VIDEO_AUDIO = "0"
$env:GROK_FIRE_ONLY = "1"
$env:GROK_CLOSE_TAB = "0"   # prefer New Generation; closing sole tab can kill CDP hub
node "...\generate-video.mjs"
```

```powershell
# Extra beats on an EXISTING character film (never home Video)
$env:GROK_AGENT_URL = "https://grok.com/imagine/agent/<uuid>?conversation=<id>"
$env:GROK_OUT = "<pack>\raw\agent_continue"
$env:GROK_NUDGE_FILE = "<pack>\prompts\agent_nudge.txt"
$env:GROK_EXPECT_PANELS = "2"
node "...\agent-continue.mjs"
```

## Failure patterns

| Symptom | Cause | Fix |
|---------|-------|-----|
| Still timeout / empty canvas | Submitted as Video while waiting for images | Force Image aria-radio |
| Boring essay picture | Image stills + slow playback | Use Video I2V 10s+ |
| Wrong identity | Macro lock / history grab | Full-body seed; UUID + midframe QA |
| Tab spray / CDP hang | Extra `newPage` / dual clients | Dedupe; kill stale node |
| Agent wait `newUuidsSinceStart: 0` | Sidebar history | Require new UUIDs after submit |
| Character faces drift across clips | Extra beats via home Video / New Generation | Continue the existing Agent `?conversation=` |

