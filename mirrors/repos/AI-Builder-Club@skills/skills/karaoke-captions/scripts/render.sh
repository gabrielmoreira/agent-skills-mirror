#!/usr/bin/env bash
# Render ASS captions onto a video with FFmpeg libass.
#
# Usage:
#   render.sh input.mp4 captions.ass output.mp4                    # Full video render
#   render.sh input.mp4 captions.ass preview.mp4 START DUR         # Preview video segment
#   render.sh frame input.mp4 captions.ass frame.png TIMESTAMP     # Single frame snapshot
set -euo pipefail

if [[ "${1:-}" == "frame" ]]; then
  shift
  IN="$1"; ASS="$2"; OUT="$3"; TIME="${4:?Missing timestamp for frame snapshot}"
  # Place -ss after -i so PTS preserves absolute timestamp matching ASS events
  ffmpeg -y -v error -i "$IN" -ss "$TIME" -vf "ass=$ASS" -frames:v 1 "$OUT"
  echo "frame snapshot -> $OUT"
  exit 0
fi

if [[ $# -lt 3 ]]; then
  echo "Usage:"
  echo "  $0 input.mp4 captions.ass output.mp4 [start_seconds] [duration_seconds]"
  echo "  $0 frame input.mp4 captions.ass frame.png timestamp"
  exit 1
fi

IN="$1"; ASS="$2"; OUT="$3"; START="${4:-}"; DUR="${5:-}"
SEEK=()
[ -n "$START" ] && SEEK+=(-ss "$START")
[ -n "$DUR" ] && SEEK+=(-t "$DUR")

if [ ${#SEEK[@]} -gt 0 ]; then
  ffmpeg -y -v error -i "$IN" "${SEEK[@]}" -vf "ass=$ASS" \
    -c:v libx264 -preset veryfast -crf 20 -c:a copy "$OUT"
else
  ffmpeg -y -v error -i "$IN" -vf "ass=$ASS" \
    -c:v libx264 -preset veryfast -crf 20 -c:a copy "$OUT"
fi

echo "rendered -> $OUT"
