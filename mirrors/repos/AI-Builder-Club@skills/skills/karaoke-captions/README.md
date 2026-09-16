# karaoke-caption

Generate TikTok/Shorts-style karaoke captions with word-level highlight sweeps.

The pipeline uses MLX Whisper for word timestamps, ASS subtitles for the karaoke effect, and FFmpeg `libass` to burn captions into video.

```text
reference.png --------(match_style_from_image.py)--------> style.json --+
                                                                   +--(gen_ass.py)--> captions.ass --(render.sh)--> output.mp4
input.mp4 ---------------------------------->(extract_words.py)--> words.json --+
```

## Requirements

- macOS with Apple Silicon (MLX Whisper)
- Python 3.10+
- [FFmpeg](https://ffmpeg.org/) with `libass` (`brew install ffmpeg`)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
# 1. Extract word timestamps (add --language zh for Chinese)
python scripts/extract_words.py input.mp4 words.json \
  --model mlx-community/whisper-large-v3-turbo

# 2. Pick a style preset, or match from a screenshot
cp presets/style.json style.json
# python scripts/match_style_from_image.py reference.png style.json --video input.mp4

# 3. Generate ASS captions
python scripts/gen_ass.py words.json style.json captions.ass --video input.mp4

# 4. Render
scripts/render.sh input.mp4 captions.ass output.mp4
```

Preview a segment or a single frame:

```bash
scripts/render.sh input.mp4 captions.ass preview.mp4 3 8
scripts/render.sh frame input.mp4 captions.ass preview_frame.png 4.5
```

## Presets

| File | Highlight | Font |
|---|---|---|
| `presets/style.json` | neon green | Arial Black |
| `presets/yellow.json` | yellow | Arial Black |

See [references/style-guide.md](references/style-guide.md) for every style field.

Agent workflow details live in [SKILL.md](SKILL.md).
