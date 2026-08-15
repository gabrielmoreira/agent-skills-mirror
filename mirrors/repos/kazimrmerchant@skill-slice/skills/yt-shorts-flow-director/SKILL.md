---
name: yt-shorts-flow-director
description: >-
  Router for YouTube/TikTok Shorts: local TTS, /localimage stills, Remotion
  assemble, optional cloud GPU, then /reviewresults. Use when the user starts
  any Shorts or long-form YouTube video job. Flow/Veo only if the user names
  Flow. Not for local LongCat I2V itself (localvideo) and not for SVG vault or GTM.
---

# YT Shorts director (cloud + local)

**Load this skill first** for any Shorts / long-form YouTube video job. Progressive disclosure only — route, then open the sibling skill you need.

Specialists in the route table that are **not** in this v1 pack live in later ROADMAP packs. After routing, Read the matching installed skill (`youtube`, `remotion-shorts`, `omni`, `story-to-video`, `video-ai-production`, Flow/ffmpeg siblings). Slash commands (`/youtube`, `/omni`, `/localvideo`) still apply.

**Also load `youtube` skill** (or honor `/youtube`) for format detect + packaging + Creator-docs gates. Produce path stays here; ship/package path is `/youtube`.

Operator card: the project's `CLOUD_STACK.md` / `AGENTS.md` when present.

## Hard defaults

| Rule | Value |
|------|--------|
| Generator | **No Flow by default.** AI video bursts via **`/cloudvideo`** on Vast/RunPod **4090/5090** (ask before rent). Draft/debug: **`/localvideo`** on local 3090 Ti |
| Images | **Local only** — `/localimage` (ComfyUI). `/cloudimage` redirects local |
| Narration | Local **Piper** deep voice; ElevenLabs only if approved |
| Assemble | **Remotion** + NVENC (`--gl angle`, concurrency ~6). Vault: `rule-007-gpu-video-render.md` |
| Orchestrator | **`/cloudgeneral`** for full gold-style short/long |
| OpenRouter / paid APIs / GPU rent | **Opt-in / ask first**; always **`stop`** cloud instances when done |
| Ship | `keep/` + `final/` only — never delete keepers/finals; never ship raw dumps |
| Exit gate | **`/reviewresults`** after Remotion/ffmpeg/`/effects` |
| Bulk N≥10 | **`/scale`** + per-wave **`/reviewresults --mode wave`** — no script-and-ship |

## Pack layout (`<slug>/`)

```
script.txt  storyboard.md  scenes.json  prompts/  audio/  raw/  keep/  final/
captions*.srt  cloud_session.json (when renting)
```

No-Flow canonical: `gold-asia-top-miner/`. Legacy Flow packs may still have `FLOW_PLAYBOOK.md` / `flow_project_url.txt`.

## Production order (audio-first)

1. **Format + goal** — via **`/youtube`** / `youtube` skill (shorts | long | both; reach | subs | revenue).  
2. **VO / narration** (Piper) before mass clip gen.  
3. **Stills** — `/localimage` heroes/refs; approve likeness.  
4. **Picture** — Remotion maps / Commons / stock first; queue only needed AI beats.  
5. **AI video** — `/cloudvideo` (best quality on 4090/5090) or `/localvideo` for local draft. Identity → I2V with ref.  
6. **Avatar** (optional) — `/cloudvideo avatar` on hooks/openers only unless user asks full talking head.  
7. **Assemble** — Remotion + NVENC → `final/`.  
8. **QA** — `/reviewresults` (format-aware: Shorts 0–2s; long 0/15/30s + end). Fix → re-render → re-review.  
9. **Package** — `/youtube` packaging gate (`youtube/` folder + UPLOAD_CHECKLIST + GenAI attributes).  
10. **Bulk** — if producing N≥10 similar units, switch to **`/scale`**: gold → waves → `/reviewresults --mode wave` each wave → ledger `done`. Never generate-all-then-review-once.

## Route table (load on demand)

| Need | Skill / command |
|------|------------------|
| YouTube Creator ops / packaging (Shorts + long) | **`youtube`** · `/youtube` |
| Full produce / cloud LLM | **`cloudgeneral`** · `/cloudgeneral` |
| Cloud LongCat / avatar | **`cloudvideo`** + **`cloud-gpu`** · `/cloudvideo` |
| Google Omni Flash (API video) | **`omni`** · `/omni` — load `reference.md`; persist `interaction_id` |
| Image redirect | **`cloudimage`** → `/localimage` |
| Local stills | **`localimage-stills`** · `/localimage` |
| Local LongCat | **`localvideo`** · `/localvideo` |
| Pack / NVENC / never-delete | **`local-media-router`** |
| Remotion assemble / captions / GPU render | `remotion-video` plus `local-media-router` (NVENC pack finals; this folder does not ship encoder scripts) |
| Quote kinetic captions / archive cuts / transitions | **`inspire-quote-effects`** + `transition` · `/effects` |
| Exit gate after any render | **`review-results`** · `/reviewresults` |
| Many unique units / mass produce | **`quality-at-scale`** · `/scale` (+ `/reviewresults --mode wave`) |
| Vehicle / underride / facing QA | `vehicle-physics-safety-video` |
| Flow UI / harvest (legacy) | `google-flow-automation` — **only if user names Flow** |
| CDP / Browser Hub (legacy Flow) | `flow-playwright` or Browser Hub `connect.mjs` |
| Broader story→video | `story-to-video` (override working root to YT pack) |
| Tool research | `video-ai-production` |
| Cut / concat / zoompan | `video-processing-pipeline` / `ffmpeg-video-editing` |

## Parallel jobs

If another agent owns a pack, **do not** overwrite its `raw/` / `keep/` / `final/` or its `cloud_session.json` rent. Prefer separate cloud instances per job.

## Quality bars (non-negotiable)

- Audio-first; images local  
- Likeness: still → I2V; T2V-only faces = FAIL  
- Start↔end facing QA for driving packs — rear→front or flipped travel = **FAIL**  
- Unique media per beat; no keeper/final deletes  
- Captions match VO  
- Prefer keepers + Ken Burns over unstable full clips; no gore  
- Cloud: ask before rent; GPU **4090/5090**; **stop** when done  
- **After any Remotion/ffmpeg/`/effects` render → `/reviewresults`**
- **N≥10 similar units → `/scale` + wave `/reviewresults --mode wave`** (script-and-ship = FAIL)

## Legacy Flow (only if user asks)

If the user explicitly wants Google Flow/Veo: load `google-flow-automation`, one Flow tab per job, Agent-first briefs, Browser Hub CDP `http://127.0.0.1:9222` only. Do **not** treat Flow as the default path.

## References

- Operator card: project `CLOUD_STACK.md` (if present)
- Parent rules: project `AGENTS.md`
