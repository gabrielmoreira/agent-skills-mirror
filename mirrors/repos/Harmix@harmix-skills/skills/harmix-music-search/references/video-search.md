# Video-Based Music Search

Find music that matches video content by extracting frames and using visual analysis.

## Prerequisites

- **ffmpeg** must be installed for frame extraction

## Workflow

1. Extract 5 frames from the video (at 0%, 25%, 50%, 75%, 100% of duration)
2. Upload frames to `/upload` endpoint to get an `upload_id`
3. Search with `video_reference` using the `upload_id`

## Frame Requirements

- **Count**: 5 frames equally distributed across video duration
- **Format**: JPEG (must use `.jpeg` extension, not `.jpg`)
- **Size**: 226x226 pixels

## Step 1: Extract Frames with ffmpeg

Get video duration and extract 5 JPEG frames at equal intervals:

```bash
# Get video duration in seconds
DURATION=$(ffprobe -v error -show_entries format=duration -of csv=p=0 video.mp4)

# Calculate timestamps (0%, 25%, 50%, 75%, 100%)
T1=0
T2=$(echo "$DURATION * 0.25" | bc)
T3=$(echo "$DURATION * 0.5" | bc)
T4=$(echo "$DURATION * 0.75" | bc)
T5=$(echo "$DURATION - 0.1" | bc)

# Extract and resize frames to 226x226 as JPEG (must use .jpeg extension)
ffmpeg -ss $T1 -i video.mp4 -vframes 1 -vf "scale=226:226" frame1.jpeg
ffmpeg -ss $T2 -i video.mp4 -vframes 1 -vf "scale=226:226" frame2.jpeg
ffmpeg -ss $T3 -i video.mp4 -vframes 1 -vf "scale=226:226" frame3.jpeg
ffmpeg -ss $T4 -i video.mp4 -vframes 1 -vf "scale=226:226" frame4.jpeg
ffmpeg -ss $T5 -i video.mp4 -vframes 1 -vf "scale=226:226" frame5.jpeg
```

## Step 2: Upload Frames

Upload the extracted JPEG frames to get an `upload_id`:

**Endpoint**: `POST https://api.harmix.ai/upload`

```bash
curl -X POST "https://api.harmix.ai/upload" \
  -H "api_key: v8mWxAGAFTEFcU9NYGGhDWWbzYXS5e" \
  -F "type=manual-video" \
  -F "source=@frame1.jpeg" \
  -F "source=@frame2.jpeg" \
  -F "source=@frame3.jpeg" \
  -F "source=@frame4.jpeg" \
  -F "source=@frame5.jpeg"
```

**Response**:

```json
{
  "status": "success",
  "upload_id": "abc123-def456"
}
```

## Step 3: Search with Video Reference

Use the `upload_id` to search for matching music:

**Endpoint**: `POST https://api.harmix.ai/search`

```bash
curl -X POST "https://api.harmix.ai/search?limit=5" \
  -H "api_key: v8mWxAGAFTEFcU9NYGGhDWWbzYXS5e" \
  -H "Content-Type: application/json" \
  -d '{"video_reference": {"upload_id": "abc123-def456"}}'
```

**Response**:

```json
{
  "tracks_number": 5,
  "tracks": [
    {
      "metadata": {
        "track_title": "Cinematic Adventure",
        "artists": ["Composer Name"],
        "extra_parameters": {
          "url": "https://open.spotify.com/track/xyz789"
        }
      }
    }
  ]
}
```

## Complete Example

For a complete Python implementation, see [scripts/video_search.py](../scripts/video_search.py).
