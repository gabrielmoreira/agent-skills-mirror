---
name: local-media-router
description: >-
  Lays out local gen packs (prompts, raw, keep, final, qa), encodes NVENC
  h264_nvenc masters, runs ffprobe plus identity stranger-test, and keeps
  immutable keepers. Use when LongCat or ComfyUI output must land in a pack
  after a successful gen. Not for LongCat I2V itself (localvideo) or Flux/Krea
  still routing (localimage-stills). Never Remove-Item keep/ or final/.
---

# local-media-router

## Model discovery (before gen)

```powershell
powershell -File ".\discover.ps1"
```

Writes `models_discovered.json` (installed ComfyUI checkpoints, LongCat runners, `style_map`).  
`/localimage` and `/localvideo` must route style words from that map and log `model`+`style` in the pack manifest. Never silent style mismatch (e.g. Pixar prompt file vs Flux photoreal run).

## When

Called by **localvideo** / **localimage-stills** after a successful gen or edit.

## Pack root

| Workspace | Pack path |
|-----------|-----------|
| Shorts / video workspace | `<workspace>\<slug>\` (standard Shorts layout) |
| Anything else | `<workspace>\_localmedia\<yyyy-MM-dd_HHmmss>_<slug>\` |

### Layout (always)

```
prompts/   script.txt (optional)
raw/       model output (immutable once written)
keep/      promoted keepers — NEVER delete
final/     NVENC / delivery masters — NEVER delete
qa/        frames, thumbs, probes
.reviews/  formal review reports when /reviewresults used
manifest.json
run.log
```

Slugify prompt: keep `[A-Za-z0-9\-_]`, max 40 chars.

## Video finals (NVENC)

```powershell
ffmpeg -y -i "$rawMp4" -c:v h264_nvenc -preset p5 -rc vbr -cq 19 -b:v 8M -maxrate 12M -pix_fmt yuv420p -movflags +faststart -an "$finalMp4"
```

Prefer `hevc_nvenc` only when user asks. Proof: encode log must mention `h264_nvenc` / `hevc_nvenc`.

## QA gate

### Video
1. `ffprobe` → `qa/ffprobe.txt`
2. Extract **start / mid / end** (minimum 3 frames; prefer 6 even-spaced)
3. **Read** every frame with the Read tool
4. Content must match prompt
5. **Identity stranger test** (if pack has `refs/hero.png` or prompt is a named person/character):  
   Would a stranger say the frames match the intended person/character?  
   - **FAIL → BLOCKER** — do not ship; keep raw; ask before re-run  
   - Do not mark PASS on “nice stage lighting” alone
6. Optional: `/reviewresults` for ship bar

### Image
1. Copy best to `keep/` + `final/` (and `refs/hero.png` if marked hero)
2. **Read** every still
3. Hero/likeness stills: face must be clear enough to drive I2V
4. Write short note in `qa/notes.md`

## Never-delete

- Never `Remove-Item` on `keep/`, `final/`, `finals/`, or keeper files under `raw/`
- Re-runs → new pack folder or `raw/rerun_N/`
- Cleanup only temp under `qa/tmp/`

## Manifest (`manifest.json`)

```json
{
  "type": "video|image",
  "command": "/localvideo|/localimage",
  "prompt": "...",
  "model": "LongCat-Video|Flux-fp8|Krea",
  "params": {},
  "ref": null,
  "mode": "t2v|i2v|edit",
  "quality": "draft|best",
  "identity_qa": "pass|fail|n/a",
  "files": [{ "path": "...", "role": "raw|keep|final" }],
  "created": "ISO-8601",
  "elapsed_s": null
}
```
