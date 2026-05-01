---
name: extract-video-frames
description: Extracts frames and timestamped audio segments from video files (GIF, MP4, MOV) at configurable intervals and stores them in a directory with a manifest file. Use when analyzing video content, preparing frames for visual review, extracting audio for transcription, or creating frame+audio sequences for another agent to process.
argument-hint: [video-path] [interval-seconds] [output-dir]
---

<objective>
Extract frames and aligned audio segments from video files (GIF, MP4, MOV) at specified intervals using ffmpeg. Outputs PNG frames, per-segment AAC audio clips, a full continuous audio track, and a JSON manifest containing timestamps and paths -- ready for handoff to another agent for visual and audio analysis.
</objective>

<quick_start>
Extract frames and audio from a video:

```bash
# Extract 1 frame + audio segment per second (default)
~/.claude/skills/extract-video-frames/scripts/extract-frames.sh input.mp4

# Extract 1 frame + audio segment every 2 seconds
~/.claude/skills/extract-video-frames/scripts/extract-frames.sh input.mp4 2

# Specify custom output directory
~/.claude/skills/extract-video-frames/scripts/extract-frames.sh input.mp4 1 ./my-frames
```

The script creates:
- `frames/` directory with PNG files named `frame_001.png`, `frame_002.png`, etc.
- `frames/audio_001.aac`, `audio_002.aac`, etc. (when audio exists, aligned 1:1 with frames)
- `frames/full_audio.aac` (complete audio track, when audio exists)
- `frames/manifest.json` with frame and audio metadata for the reviewing agent
</quick_start>

<workflow>
1. **Verify ffmpeg is available**
   ```bash
   which ffmpeg || echo "ffmpeg not found - install with: brew install ffmpeg"
   ```

2. **Run extraction script**
   ```bash
   ~/.claude/skills/extract-video-frames/scripts/extract-frames.sh <video-path> [interval-seconds] [output-dir]
   ```

   - `video-path`: Path to GIF, MP4, or MOV file (required)
   - `interval-seconds`: Extract one frame every N seconds (default: 1)
   - `output-dir`: Where to store frames and audio (default: `./frames`)

3. **Review manifest**
   The manifest.json contains:
   ```json
   {
     "source": "recording.mp4",
     "source_path": "/path/to/recording.mp4",
     "interval_seconds": 5,
     "total_frames": 12,
     "has_audio": true,
     "audio_codec": "aac",
     "total_audio_segments": 12,
     "full_audio_path": "full_audio.aac",
     "output_directory": "./frames",
     "frames": [
       {
         "index": 1,
         "timestamp": "00:00:00",
         "timestamp_seconds": 0,
         "path": "frame_001.png",
         "audio_path": "audio_001.aac"
       },
       {
         "index": 2,
         "timestamp": "00:00:05",
         "timestamp_seconds": 5,
         "path": "frame_002.png",
         "audio_path": "audio_002.aac"
       }
     ]
   }
   ```

4. **Hand off to reviewing agent**
   Pass the output directory path to the reviewing agent. The agent can read `manifest.json` to understand the frame sequence with audio alignment and use the Read tool to analyze individual frames.
</workflow>

<supported_formats>
- **GIF**: Animated GIFs (extracts frames; no audio stream, gracefully skipped)
- **MP4**: Standard video format (frames + audio)
- **MOV**: QuickTime format (frames + audio)
- **Other**: Any format ffmpeg supports (AVI, WebM, MKV, etc.)
</supported_formats>

<output_structure>
```
output-dir/
├── manifest.json        # Frame + audio metadata for reviewing agent
├── full_audio.aac       # Complete audio track (when audio exists)
├── frame_001.png        # First extracted frame
├── frame_002.png        # Second extracted frame
├── audio_001.aac        # Audio segment for frame 1 (when audio exists)
├── audio_002.aac        # Audio segment for frame 2
└── ...
```
</output_structure>

<audio_details>
**Format**: AAC (.aac) -- chosen for universal compatibility, small file size, and broad tooling support.

**Codec strategy**:
- If the source audio is already AAC, segments are stream-copied (no re-encoding) for speed and quality preservation.
- If the source audio is any other codec (e.g., PCM, MP3, Opus), segments are re-encoded to AAC at 128kbps.

**Alignment semantics**: Each `audio_NNN.aac` segment covers the same time window as its corresponding `frame_NNN.png`. For a 5-second interval, `audio_001.aac` covers 0:00-0:05, `audio_002.aac` covers 0:05-0:10, etc.

**No-audio handling**: When the source has no audio stream (GIFs, silent videos), `has_audio` is `false`, no audio files are created, and all `audio_path` fields in the manifest are `null`. The frame extraction works identically regardless.

**Full audio track**: `full_audio.aac` contains the entire audio from the source file as a single continuous track, useful for full transcription or background listening.
</audio_details>

<agent_handoff>
When passing frames and audio to another agent, include:

1. **Output directory path**: Where frames and audio are stored
2. **Manifest location**: `{output-dir}/manifest.json`
3. **Context**: What the reviewing agent should look for

Example prompt for reviewing agent:
```
Analyze the frames and audio extracted from the screen recording at ./frames.
The manifest at ./frames/manifest.json lists all frames with timestamps and paired audio segments.
The full audio track is at ./frames/full_audio.aac for continuous listening or transcription.
Look for: [specific things to identify or analyze]
```

Example prompt for audio-focused agent:
```
Transcribe the audio segments from the recording at ./frames.
Read ./frames/manifest.json to get the list of audio files with timestamps.
For each audio_NNN.aac segment, provide a timestamped transcript.
The full continuous audio is also available at ./frames/full_audio.aac.
```
</agent_handoff>

<success_criteria>
Frame and audio extraction is complete when:
- Output directory contains PNG frames
- `manifest.json` exists with valid frame and audio metadata
- Frame count matches expected based on video duration and interval
- Frames are readable by the Read tool for visual analysis
- When source has audio: audio segments exist (1:1 with frames), `full_audio.aac` exists, `has_audio` is `true`
- When source has no audio: `has_audio` is `false`, `audio_path` values are `null`, no audio files created
</success_criteria>
