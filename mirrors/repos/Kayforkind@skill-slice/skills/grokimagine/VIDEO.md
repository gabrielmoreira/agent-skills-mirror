# Grok Imagine — Video (SuperHeavy UI)

Verified **2026-08-10** on `https://grok.com/imagine` (account-label / SuperHeavy).  
Prompt craft: also read vault skill `grok-imagine-video-prompting` (shot grammar).  
Automation: `scripts/generate-video.mjs` + `ui-mode.mjs`.

## Goal for YT / essay packs

Ship **engaging motion clips**, not Ken Burns stills. Prefer:

1. **I2V** — strong full-body / action still → Video + Upload → motion prompt  
2. **T2V** — text-only Video when no lock exists (weaker identity)  
3. **Post tools** — Extend / Upscale / Regenerate on `/imagine/post/{uuid}`  
4. **Agent start** — brand-new multi-panel film only (New Generation → Agent)  
5. **Agent continue** — extra beats on an **existing** character film. Stay on `/imagine/agent/{uuid}?conversation=`. Never home Video / New Generation (face drift).

## Composer (Video mode)

Radiogroup `aria-label="Generation mode"` → **Video** (often the home default).

| Control | Aria / role | Values |
|---------|-------------|--------|
| Resolution | `Video resolution` radios | **480p** · **720p** · **1080p** |
| Duration | `Video duration` radios | **6s** · **10s** · **15s** |
| Native audio | `Video audio` (`aria-pressed`) | ON = SFX/dialogue/room tone; OFF when Remotion owns VO |
| Aspect | `Aspect Ratio` | e.g. **16:9** (long) / set 9:16 for Shorts |
| Upload | `Upload` + hidden `input[type=file]` | Images only (`jpeg/png/gif/webp/…`), **multiple** allowed |
| Submit | `Submit` | Starts generate |

### Recommended defaults (engaging ship)

| Phase | Res | Dur | Audio | Notes |
|-------|-----|-----|-------|-------|
| Iterate | 720p | 6s | off or on | Fast quota burn check |
| Essay / YT long B-roll | **1080p** | **10s** (or 15s hero) | **off** if Piper/Remotion VO | I2V from suit lock |
| Host talking head | 1080p | 6–10s | **on** | Quoted dialogue in prompt |

## Parallel fire (multiple clips)

Do **not** wait for each MP4 to finish before starting the next.

```
For each shot:
  New Generation → Video (+ Upload if I2V) → prefs → prompt → Submit
  Confirm generation started (progress / post URL / history thumb spinning)
  Close that Imagine tab  OR  New Generation
  Log expected shot id + prompt + any post UUID
Then (harvest wave):
  Open completed posts from History
  UUID download → midframe QA → promote keepers
```

| Phase | Behavior |
|-------|----------|
| **Fire** | Submit → gen started → **close tab** → next clip |
| **Harvest** | Later: download finished UUIDs; Read midframe QA |

Automation: `GROK_FIRE_ONLY=1` on `generate-video.mjs` = submit + confirm start + exit (no long wait). Default still waits when harvesting a single clip.

Avoid: dozens of *empty* leftover home tabs — close after fire; `_dedupe-tabs` for cleanup.

## Three video paths

### A) Text-to-video (T2V)

1. New Generation → Video  
2. Set res/dur/aspect/audio  
3. Motion prompt (one subject, one action, one camera move)  
4. Submit → confirm gen started → **close tab / New Generation** (parallel fire)  
5. Harvest later: UUID download + midframe QA  

```powershell
$env:GROK_PROMPT = "..."
# no GROK_IMAGE
$env:GROK_VIDEO_RES = "1080p"; $env:GROK_VIDEO_DUR = "10s"; $env:GROK_VIDEO_AUDIO = "0"
$env:GROK_FIRE_ONLY = "1"   # parallel fire; omit to wait+download one clip
node generate-video.mjs
```

### B) Image-to-video (I2V) — preferred for engagement + identity

1. Have a **full-figure / clear action** still (not macro chest crop)  
2. Video mode → Upload still(s) → motion-only prompt (do not contradict still)  
3. 1080p / 10–15s  
4. Submit → confirm gen started → close tab → next shot (parallel)  
5. Harvest: UUID download + Read midframe (suit ID, no melt, no plate text)

```powershell
$env:GROK_IMAGE = "D:\...\lock.png"
$env:GROK_PROMPT = "Camera tracking beside subject as they leap; fabric wind; preserve suit from reference. One continuous move."
$env:GROK_VIDEO_RES = "1080p"; $env:GROK_VIDEO_DUR = "10s"; $env:GROK_VIDEO_AUDIO = "0"
$env:GROK_FIRE_ONLY = "1"
node generate-video.mjs
```

### C) Post page tools (`/imagine/post/{uuid}`)

Open a finished still **or** video from History. Controls observed:

| Aria | Use |
|------|-----|
| **Make video** | Animate a still post → video |
| **Extend** | Continue clip from end (longer beat) |
| **Upscale** / **Video quality** (HD) | Quality pass |
| **Regenerate** | Re-roll same brief |
| **Download** | Manual save (prefer script UUID GET) |
| **Expand video** | UI expand |

Do **not** treat other videos listed on the same post/history as “this” clip without UUID match.

### D) Agent continue — existing character project (required for series)

Home Video I2V / New Generation **mints a new Imagine project** and re-rolls faces.  
xAI Video 1.5 **multi-ref** (up to 7 stills + optional voice-ref) is a separate one-off I2V path — it does **not** replace an Agent canvas that already holds the characters.

1. Open the pack `agent_url.txt` **with** `?conversation=` (workspace UUID alone can be reused across films)
2. Nudge on that page: same character bible + two new 10s clips (user-gated waves)
3. Wait for **new** video UUIDs (not sidebar history)
4. UUID download + midframe QA vs the locked look

```powershell
$env:GROK_AGENT_URL = "https://grok.com/imagine/agent/<uuid>?conversation=<id>"
$env:GROK_OUT = "<pack>\raw\agent_continue"
$env:GROK_NUDGE_FILE = "<pack>\prompts\agent_nudge.txt"
$env:GROK_EXPECT_PANELS = "2"
node scripts/agent-continue.mjs
```

`generate-video.mjs` **refuses** if the pack has `agent_url.txt` unless `GROK_ALLOW_HOME_VIDEO=1`.

## Engaging motion prompts (UI)

Mirror `grok-imagine-video-prompting` golden formula:

```
[Subject locked from still] + [ONE visible action] + [environment energy] + [ONE camera move] + [lighting] + photoreal
```

**Do:** tracking, freefall streak, dust kick, rain streaks, fabric wind, lens flare accents.  
**Don’t:** stack 3 camera moves; ask for readable logos/text; macro-only seeds for “action” essay beats.

## Export

Same as Agent videos:

`https://assets.grok.com/users/{uid}/generated/{uuid}/generated_video.mp4`

Dedupe UUID · `page.request.get` · ffmpeg midframe QA · promote keepers only.

## Probes (no generate)

```powershell
node scripts/probe-imagine-video.mjs
node scripts/probe-imagine-video-history.mjs
```

## Anti-patterns

- Using Image mode + Ken Burns in Remotion and calling it “video”
- I2V from extreme macro crops → more macros
- Submitting Video while counting Image assets (or vice versa)
- Grabbing sidebar history MP4s as the new clip (`newUuidsSinceStart: 0`)
- Blocking on full MP4 download before firing the next clip (use parallel fire)
- Leaving piles of empty Imagine home tabs (close after gen starts)
- xAI API spend without asking (SuperHeavy UI first)
- Extra story beats via home Video / New Generation when an Agent project already exists (character drift)
