---
name: video-frames
description: Extract frames or short clips from videos using ffmpeg.
homepage: https://ffmpeg.org
metadata:
  {
    "emoji": "🎬",
    "requires": { "bins": ["ffmpeg"] }
  }
---

# Video Frames (ffmpeg)

Extract a single frame from a video, or create quick thumbnails for inspection.

## Quick start

First frame:

```bash
ffmpeg -hide_banner -loglevel error -y \
  -i /path/to/video.mp4 \
  -vf "select=eq(n\,0)" \
  -vframes 1 \
  /tmp/frame.jpg
```

At a timestamp:

```bash
ffmpeg -hide_banner -loglevel error -y \
  -ss 00:00:10 \
  -i /path/to/video.mp4 \
  -frames:v 1 \
  /tmp/frame-10s.jpg
```

By frame index:

```bash
ffmpeg -hide_banner -loglevel error -y \
  -i /path/to/video.mp4 \
  -vf "select=eq(n\,42)" \
  -vframes 1 \
  /tmp/frame42.jpg
```

## Notes

- Prefer `-ss` + timestamp for "what is happening around here?".
- Use `.jpg` for quick sharing; use `.png` for crisp UI frames.
- Use `-hide_banner -loglevel error` to suppress verbose ffmpeg output.
