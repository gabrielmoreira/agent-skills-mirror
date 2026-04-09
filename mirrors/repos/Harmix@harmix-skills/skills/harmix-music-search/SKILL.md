---
name: harmix-music-search
description: Search for music tracks using natural language prompts or video content via the Harmix AI API. Use when the user asks to find music, search for songs, discover tracks, needs music recommendations based on mood/genre/tempo/scene, or wants to find music for a video, video soundtrack, or music that matches video content.
---

# Harmix AI Music Search

[Harmix](https://www.harmix.ai/) is an AI-powered music search platform tailored for production music, TV and movie productions, record labels, and publishers. It enables accurate music discovery from large catalogs using natural language and visual content analysis.

## Features Available in This Skill

- **Prompt Search**: Search music using free text descriptions (mood, genre, tempo, scene, etc.)
- **Video Search**: Upload video frames to find music that matches the visual mood and content

## Documentation

- API Documentation: https://docs.harmix.ai/
- Web Platform: https://web.harmix.ai/

## Authentication

All requests require the `api_key` header:

```
api_key: v8mWxAGAFTEFcU9NYGGhDWWbzYXS5e
```

## Output Format for Users

When presenting search results to users, display each track with:

1. **Title**: The track title
2. **Artist(s)**: The artist name(s)
3. **URL**: Link to the track on its streaming service (Spotify, Apple Music, Deezer, etc.)

Extract these from the response:
- Title: `metadata.track_title`
- Artists: `metadata.artists`
- URL: `metadata.extra_parameters.url`

Example output format:
```
1. "Energy Boost" by Electric Dreams
   https://open.spotify.com/track/abc123

2. "Morning Run" by Fitness Beats
   https://music.apple.com/track/xyz789
```

## Search Methods

### 1. Prompt-Based Search

Search with a natural language description of the music you want.

```bash
curl -X POST "https://api.harmix.ai/search?limit=5" \
  -H "api_key: v8mWxAGAFTEFcU9NYGGhDWWbzYXS5e" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "upbeat electronic music for a workout"}'
```

For full documentation, see [references/prompt-search.md](references/prompt-search.md).

### 2. Video-Based Search

Find music that matches video content by analyzing visual frames.

**Requirements**: ffmpeg must be installed.

**Quick steps**:
1. Extract 5 JPEG frames (226x226) from video at equal intervals (must use `.jpeg` extension)
2. Upload frames to `/upload` endpoint
3. Search using the returned `upload_id`

```bash
# Upload frames (must use .jpeg extension)
curl -X POST "https://api.harmix.ai/upload" \
  -H "api_key: v8mWxAGAFTEFcU9NYGGhDWWbzYXS5e" \
  -F "type=manual-video" \
  -F "source=@frame1.jpeg" \
  -F "source=@frame2.jpeg" \
  -F "source=@frame3.jpeg" \
  -F "source=@frame4.jpeg" \
  -F "source=@frame5.jpeg"

# Search with upload_id from response
curl -X POST "https://api.harmix.ai/search?limit=5" \
  -H "api_key: v8mWxAGAFTEFcU9NYGGhDWWbzYXS5e" \
  -H "Content-Type: application/json" \
  -d '{"video_reference": {"upload_id": "YOUR_UPLOAD_ID"}}'
```

For full documentation, see [references/video-search.md](references/video-search.md).

## Response Format

Both methods return tracks with title, artists, and streaming URL:

```json
{
  "tracks_number": 5,
  "tracks": [
    {
      "metadata": {
        "track_title": "Track Name",
        "artists": ["Artist Name"],
        "extra_parameters": {
          "url": "https://open.spotify.com/track/abc123"
        }
      }
    }
  ]
}
```

## API Limits

The provided API key has usage limits. If you receive a **403 error with code 4005**, the limit has been reached.

**When limit is reached:**
1. Request your own API key by contacting support@harmix.ai
2. Or use the web platform directly at https://web.harmix.ai/

## Scripts

- [scripts/video_search.py](scripts/video_search.py) - CLI tool for video-based music search

## Resources

- [Prompt Search Reference](references/prompt-search.md)
- [Video Search Reference](references/video-search.md)
