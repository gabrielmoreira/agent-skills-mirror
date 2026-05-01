---
slug: muapi-youtube-shorts
name: muapi-youtube-shorts
version: "1.0.0"
description: Auto-generate viral 9:16 YouTube Shorts (or TikTok/Reels clips) from a long-form YouTube URL or hosted video. Pipeline downloads the source, transcribes locally with Whisper, ranks highlights through a virality framework (hook / emotional peak / opinion bomb / revelation / conflict / quotable / story peak / practical value), dedupes overlapping candidates, and vertically auto-crops the top N as mp4s via `muapi edit clipping`.
acceptLicenseTerms: true
---

# YouTube Shorts Generator

**End-to-end pipeline: Long Video → Transcript → Ranked Highlights → Vertical Clips.**

Turns one long video into N viral-ready vertical mp4s. Each clip ships with a viral score (0–100), an opening hook line, and a one-sentence reason it should perform.

Reference implementation: https://github.com/SamurAIGPT/AI-Youtube-Shorts-Generator
Underlying API: https://muapi.ai/playground/ai-clipping

---

## Agent Execution Protocol

### Step 1 — Collect Inputs

Ask once, then proceed:

| Input | Default | Notes |
|:---|:---|:---|
| `source` | — | YouTube URL, or hosted mp4 URL, or local file path |
| `num_clips` | `3` | How many shorts to render |
| `aspect_ratio` | `9:16` | `9:16` for TikTok/Reels/Shorts, `1:1` square, `4:5` portrait |
| `whisper_model` | `base` | `tiny` / `base` / `small` / `medium` / `large` |
| `language` | auto | Whisper language code (e.g. `en`) |
| `output_json` | — | Optional path; if set, dump full result there |

If the user gave only a URL, use defaults and don't block on questions.

---

### Step 2 — Verify Prerequisites

- `muapi-cli` installed and authed (`muapi auth configure`)
- `ffmpeg` on PATH (Whisper needs it for audio decoding)
- Python 3.10+ with `openai-whisper` installed (only if running the local transcribe stage)

If `MUAPI_API_KEY` is missing, stop and ask the user. Never invent a key.

---

### Step 3 — Run the Pipeline

The standard path is the orchestrator script — it handles all eight stages in order:

```bash
bash library/social/youtube-shorts/scripts/run-youtube-shorts.sh \
  --source "<YOUTUBE_URL>" \
  --num-clips 5 \
  --aspect-ratio 9:16 \
  --whisper-model base \
  --output-json result.json \
  --view
```

The eight stages:

1. **Download** — pull the source video at the requested resolution (`360`/`480`/`720`/`1080`, default `720`). For local files, skip.
2. **Transcribe** — local Whisper produces timestamped segments. Audio stays on the machine.
3. **Classify content type** — LLM tags the video (podcast / interview / tutorial / vlog / lecture / monologue) and density. Tunes the highlight prompt per type.
4. **Chunk if long** — videos > `LONG_VIDEO_THRESHOLD` (1800s default) are split into `CHUNK_SIZE_SECONDS` (1200s default) windows with `CHUNK_OVERLAP_SECONDS` (60s default) overlap so cross-boundary highlights aren't missed.
5. **Rank highlights** — LLM scans each chunk through `VIRALITY_CRITERIA`:
   - **Hook moments** — strong opening line that stops the scroll
   - **Emotional peaks** — laughter, anger, vulnerability, awe
   - **Opinion bombs** — spicy, contrarian, debate-bait takes
   - **Revelation moments** — "wait, what?" reframes
   - **Conflict** — disagreement, tension, callouts
   - **Quotable lines** — tight, screenshot-worthy phrasing
   - **Story peaks** — climax of a narrative arc
   - **Practical value** — actionable insight a viewer will save
   Each candidate gets `start_time`, `end_time`, `score` 0–100, `title`, `hook_sentence`, `virality_reason`. Aim for 30–75s clips unless content dictates otherwise.
6. **Dedupe** — collapse overlaps. Rule: if two candidates overlap > 50%, keep the higher score, drop the other.
7. **Top-N selection** — sort surviving candidates by score, take `num_clips`.
8. **Vertical auto-crop** — render each highlight at `aspect_ratio` via `muapi edit clipping`. Auto-handles face tracking and screen recordings.

---

## Quick Invocation Patterns

**Single video, defaults:**
```bash
bash scripts/run-youtube-shorts.sh --source "https://youtube.com/watch?v=VIDEO_ID"
```

**Tuned for high-density podcast (more clips, larger Whisper model):**
```bash
bash scripts/run-youtube-shorts.sh \
  --source "<URL>" --num-clips 8 --whisper-model medium --view
```

**Square clips for Instagram feed:**
```bash
bash scripts/run-youtube-shorts.sh \
  --source "<URL>" --aspect-ratio 1:1 --num-clips 3
```

**Batch — `urls.txt` with one URL per line:**
```bash
xargs -a urls.txt -I{} bash scripts/run-youtube-shorts.sh --source "{}"
```

**Async submit (returns request_id, poll later):**
```bash
REQUEST_ID=$(bash scripts/run-youtube-shorts.sh \
  --source "<URL>" --async --output-json - --jq '.request_id' | tr -d '"')
muapi predict wait "$REQUEST_ID" --download ./outputs
```

---

## Platform Specs

| Platform | Aspect | Sweet-spot duration | Notes |
|:---|:---|:---|:---|
| YouTube Shorts | 9:16 | 30–60s | Hook in first 1s, max quality |
| TikTok | 9:16 | 30–75s | High energy; longer is fine if hook lands |
| Instagram Reels | 9:16 | 30–60s | Hook in first 1s |
| Instagram Feed | 1:1 | 15–45s | Static-feel works well |
| LinkedIn | 16:9 or 1:1 | 30–60s | Professional tone |
| Twitter/X | 16:9 | 15–60s | Punchy, direct |

---

## Output Schema

```json
{
  "source_video_url": "...",
  "transcript": { "duration": 1873.4, "segments": [...] },
  "highlights": [ /* every candidate, before top-N cut */ ],
  "shorts": [
    {
      "title": "The one mistake that cost me $50K",
      "start_time": 124.3,
      "end_time": 187.6,
      "score": 92,
      "hook_sentence": "Nobody talks about this, but it killed my first startup...",
      "virality_reason": "Opens with a number + regret, peaks on a contrarian lesson",
      "clip_url": "https://.../short_1.mp4"
    }
  ]
}
```

When reporting back to the user, surface for each clip: rank, score, time range, title, hook, and clip URL. Skip the raw transcript unless asked.

---

## Tunable Knobs

Edit defaults inside the orchestrator or pass via flags:

| Knob | Default | Purpose |
|:---|:---|:---|
| `CHUNK_SIZE_SECONDS` | `1200` | Chunk length for long videos |
| `LONG_VIDEO_THRESHOLD` | `1800` | Videos longer than this get chunked |
| `CHUNK_OVERLAP_SECONDS` | `60` | Overlap between chunks |
| `MUAPI_POLL_INTERVAL` | `5` | Seconds between job-status polls |
| `MUAPI_POLL_TIMEOUT` | `1800` | Give up after this long |
| `OVERLAP_DEDUPE_THRESHOLD` | `0.5` | Min IoU to collapse overlapping candidates |

---

## Whisper Model Selection

- `tiny` / `base` — fast, English-leaning, fine for clean studio audio
- `small` / `medium` — better for accents and music beds
- `large` — highest accuracy, much slower; only worth it on a GPU

Pick `base` unless transcript quality is poor, then bump to `medium`.

---

## Common Mistakes to Avoid

1. **Skipping the dedupe step** — without it, you ship near-duplicate clips that all came from the same hot moment.
2. **Generic virality prompt** — the highlight ranker must score against the eight signals above, not "interestingness."
3. **Wrong aspect ratio for the platform** — YouTube Shorts and TikTok are `9:16`; LinkedIn often `16:9`. Default to `9:16` only if the platform isn't specified.
4. **Crop without face tracking** — vertical crops on talking-head content must follow the speaker's face; static center-crop loses the subject.
5. **Padding to hit `num_clips`** — if dedupe leaves fewer survivors than requested, return what you have. Don't ship low-score filler.
6. **Re-running the full pipeline on a 404'd clip URL** — re-run only the crop stage for that highlight.

---

## Failure Modes

- **`ffmpeg not found on PATH`** — stop and tell the user to install (`brew install ffmpeg` / `apt install ffmpeg`).
- **Whisper produced no segments** — likely no detectable speech or a hard language. Retry with `--whisper-model medium --language <code>` before declaring failure.
- **API key missing or rejected** — surface the exact error; don't fabricate a key.
- **Job timed out** — bump `MUAPI_POLL_TIMEOUT` and retry; don't silently truncate.
- **Highlight ranker returned <`num_clips`** — return what survived dedupe with a note.

---

## Done Criteria

The skill is done when:
1. `result.shorts` has up to `num_clips` entries, each with a working `clip_url`.
2. The user has been shown the ranked list (score, time range, title, hook, URL).
3. If `--output-json` was set, the file exists and parses.
