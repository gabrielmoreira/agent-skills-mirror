---
name: video-downloader
description: Downloads videos from YouTube and other platforms for offline viewing, editing, or archival. Handles various formats and quality options.
---

# Video Downloader

This skill downloads videos from YouTube and other platforms directly to your computer.

## Prerequisites

- **Python 3.7+**: Required for video download scripts
- **yt-dlp or yt-dlp**: Video download utility (install via pip)
- **FFmpeg**: For video format conversion (optional but recommended)

## When to Use This Skill

- Downloading YouTube videos for offline viewing
- Saving educational content for reference
- Archiving important videos
- Getting video files for editing or repurposing
- Downloading your own content from platforms
- Saving conference talks or webinars

## What This Skill Does

1. **Downloads Videos**: Fetches videos from YouTube and other platforms
2. **Quality Selection**: Lets you choose resolution (480p, 720p, 1080p, 4K)
3. **Format Options**: Downloads in various formats (MP4, WebM, audio-only)
4. **Batch Downloads**: Can download multiple videos or playlists
5. **Metadata Preservation**: Saves title, description, and thumbnail

## How to Use

### Basic Download

```
Download this YouTube video: https://youtube.com/watch?v=...
```

```
Download this video in 1080p quality
```

### Audio Only

```
Download the audio from this YouTube video as MP3
```

### Playlist Download

```
Download all videos from this YouTube playlist: [URL]
```

### Batch Download

```
Download these 5 YouTube videos:
1. [URL]
2. [URL]
...
```

## Example

**User**: "Download this YouTube video: https://youtube.com/watch?v=abc123"

**Output**:
```
Downloading from YouTube...

Video: "How to Build Products Users Love"
Channel: Lenny's Podcast
Duration: 45:32
Quality: 1080p

Progress: ████████████████████ 100%

✓ Downloaded: how-to-build-products-users-love.mp4
✓ Saved thumbnail: how-to-build-products-users-love.jpg
✓ Size: 342 MB

Saved to: ~/Downloads/
```

**Inspired by:** Lenny's workflow from his newsletter

## Important Notes

⚠️ **Copyright & Fair Use**
- Only download videos you have permission to download
- Respect copyright laws and platform terms of service
- Use for personal, educational, or fair use purposes
- Don't redistribute copyrighted content

## Tips

- Specify quality if you need lower file size (720p vs 1080p)
- Use audio-only for podcasts or music to save space
- Download to a dedicated folder to stay organized
- Check file size before downloading on slow connections

## Common Use Cases

- **Education**: Save tutorials and courses for offline learning
- **Research**: Archive videos for reference
- **Content Creation**: Download your own content from platforms
- **Backup**: Save important videos before they're removed
- **Offline Viewing**: Watch videos without internet access

## Quick Start

The simplest way to download a video:

```bash
python scripts/download_video.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

This downloads the video in best available quality as MP4 to `/mnt/user-data/outputs/`.

## Options

### Quality Settings

Use `-q` or `--quality` to specify video quality:

- `best` (default): Highest quality available
- `1080p`: Full HD
- `720p`: HD
- `480p`: Standard definition
- `360p`: Lower quality
- `worst`: Lowest quality available

Example:
```bash
python scripts/download_video.py "URL" -q 720p
```

### Format Options

Use `-f` or `--format` to specify output format (video downloads only):

- `mp4` (default): Most compatible
- `webm`: Modern format
- `mkv`: Matroska container

Example:
```bash
python scripts/download_video.py "URL" -f webm
```

### Audio Only

Use `-a` or `--audio-only` to download only audio as MP3:

```bash
python scripts/download_video.py "URL" -a
```

### Custom Output Directory

Use `-o` or `--output` to specify a different output directory:

```bash
python scripts/download_video.py "URL" -o /path/to/directory
```

## Complete Examples

1. Download video in 1080p as MP4:
```bash
python scripts/download_video.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -q 1080p
```

2. Download audio only as MP3:
```bash
python scripts/download_video.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -a
```

3. Download in 720p as WebM to custom directory:
```bash
python scripts/download_video.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -q 720p -f webm -o /custom/path
```

## How It Works

The skill uses `yt-dlp`, a robust YouTube downloader that:
- Automatically installs itself if not present
- Fetches video information before downloading
- Selects the best available streams matching your criteria
- Merges video and audio streams when needed
- Supports a wide range of YouTube video formats
