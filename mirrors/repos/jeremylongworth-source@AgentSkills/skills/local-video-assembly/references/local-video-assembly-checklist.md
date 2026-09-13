# Local Video Assembly Checklist

## Backlog Input

Minimum topic backlog fields:

- `id`
- `topic`
- `audience`
- `promise`
- `angle`
- `source_notes`
- `target_length`
- `status`
- `risk_flags`
- `review_owner`

## Episode Package

Expected package contents:

- `SCRIPT.md`
- `STORYBOARD.md`
- `VOICEOVER.txt` or narration audio
- `RENDER_MANIFEST.json` or `RENDER_MANIFEST.md`
- source media folder
- `captions.srt` or equivalent caption file
- title and thumbnail brief
- publishing checklist
- `final.mp4` or review draft
- `FFPROBE.txt`
- `REVIEW_NOTES.md`

## Render Manifest Checks

- Episode id, topic, audience, promise, target length, and review owner are
  present.
- Output profile states aspect ratio, resolution, frame rate, codecs, caption
  mode, and destination path.
- Every scene has a visual asset, duration, narration segment, caption range,
  transition, and fallback note.
- Every asset has a provenance or rights status.
- Missing files and placeholders are explicit blockers, not silent defaults.

## FFMPEG Plan Checks

- Inputs are normalized before final assembly when dimensions, frame rates, or
  audio formats differ.
- Still images or slides are scaled and padded without distortion.
- Narration is aligned to scene durations before music or effects are mixed.
- Captions are generated as a sidecar file and burned in only when requested or
  useful for review.
- Final MP4 uses broadly compatible settings such as H.264, AAC, 48 kHz stereo,
  progressive frames, `yuv420p`, and fast-start metadata unless the user chooses
  another profile.

## Validation Checks

- `ffprobe` confirms one video stream and one audio stream.
- Resolution, frame rate, duration, audio sample rate, and codecs match the
  manifest or are explained.
- Video duration and narration duration are within the agreed tolerance.
- Captions are readable, synced, and not covering critical visuals.
- Audio is intelligible, balanced, and free of obvious clipping.
- The review notes include `go`, `revise`, or `hold`.

## Human Review Gates

- Factual claims and source notes reviewed.
- Rights, provenance, AI assistance, and synthetic-media disclosure reviewed.
- Title and thumbnail are truthful to the video payoff.
- Accessibility checks cover captions, contrast, motion, and audio clarity.
- Publishing, scheduling, upload, sponsor, legal, medical, financial, political,
  crisis, or reputation-sensitive decisions remain human-approved.
