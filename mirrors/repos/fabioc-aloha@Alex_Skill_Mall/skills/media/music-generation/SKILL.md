---
type: skill
lifecycle: stable
inheritance: inheritable
name: "music-generation"
description: AI music generation via Replicate — 5 models for background tracks, lyrics, and sound design
tier: extended
applyTo: '**/*music*,**/*generation*'
currency: 2026-04-22
lastReviewed: 2026-04-30
---

# Music Generation Skill


> **Domain**: AI Music Generation  
> **Version**: 1.0.0  
> **Last Updated**: 2026-04-15  
> **Author**: the AI assistant (your AI assistant)  
> **Source**: Patterns from AlexVideos CLI toolkit  
> **Related**: [text-to-speech](../text-to-speech/SKILL.md) (voice), [video-generation](../video-generation/SKILL.md) (video)

## Overview

Generate AI music and soundtracks via Replicate. 5 models covering lyrics-based songs, instrumental tracks, and professional sound design.

---

## Model Catalog (5 Models)

| Key | Model | Replicate ID | Cost | Features |
|-----|-------|--------------|------|----------|
| `music15` | **MiniMax Music 1.5** | `minimax/music-1.5` | $0.03/file | Lyrics with `[verse]`, `[chorus]` tags |
| `music01` | **MiniMax Music 01** | `minimax/music-01` | $0.035/file | Reference audio input |
| `stableaudio` | **Stable Audio 2.5** | `stability-ai/stable-audio-2.5` | $0.20/file | Diffusion-based, 1–190s |
| `elevenmusic` | **ElevenLabs Music** | `elevenlabs/music` | $8.30/1k sec | Professional, vocals toggle |
| `lyria2` | **Google Lyria 2** | `google/lyria-2` | $2/1k sec | Negative prompt support |

---

## Parameter Support Matrix

| Model | prompt | lyrics | duration | reference | negative | vocals |
|-------|:------:|:------:|:--------:|:---------:|:--------:|:------:|
| `music15` | ✅ | ✅ | — | — | — | ✅ auto |
| `music01` | ✅ | — | — | ✅ | — | — |
| `stableaudio` | ✅ | — | 1–190s | — | ✅ | — |
| `elevenmusic` | ✅ | — | variable | — | — | ✅ toggle |
| `lyria2` | ✅ | — | variable | — | ✅ | — |

---

## Model Selection Guide

| Need | Model | Why |
|------|-------|-----|
| **Song with lyrics** | music15 | Structured lyrics with verse/chorus |
| **Match existing style** | music01 | Reference audio input |
| **Budget instrumental** | stableaudio | Cheapest per-file |
| **Professional production** | elevenmusic | Highest quality, vocal toggle |
| **Exclude unwanted elements** | lyria2, stableaudio | Negative prompt support |

---

## Lyrics Format (MiniMax Music 1.5)

Use structured tags for song sections:

```text
[intro]
(Soft piano melody)

[verse]
Walking through the city lights at night
Every shadow tells a different story
Searching for a meaning in the dark
Finding hope in unexpected places

[chorus]
We rise above the noise
Breaking through the silence
Every heart beating as one
Together we are stronger

[bridge]
When the world falls apart around us
We'll find our way back home

[outro]
(Fade out with gentle strings)
```

---

## Generation Examples

### Song with Lyrics (MiniMax)

```javascript
const output = await replicate.run("minimax/music-1.5", {
  input: {
    prompt: "Uplifting pop rock song about finding hope",
    lyrics: `
[verse]
Walking through the rain...
[chorus]
We are the dreamers...
    `,
  },
});
```

### Instrumental (Stable Audio)

```javascript
const output = await replicate.run("stability-ai/stable-audio-2.5", {
  input: {
    prompt: "Epic cinematic orchestral score, heroic theme, brass and strings",
    duration: 60, // seconds
    negative_prompt: "vocals, singing, speech, drums",
  },
});
```

### Reference-Based (MiniMax 01)

```javascript
const output = await replicate.run("minimax/music-01", {
  input: {
    prompt: "Upbeat electronic dance track",
    reference_audio: referenceAudioDataURI, // Sample to match style
  },
});
```

### Professional with Vocals Toggle (ElevenLabs)

```javascript
const output = await replicate.run("elevenlabs/music", {
  input: {
    prompt: "Energetic pop song with catchy hook",
    include_vocals: true, // or false for instrumental
  },
});
```

---

## Prompt Engineering

| Element | Good Example | Avoid |
|---------|--------------|-------|
| Genre | "lo-fi hip hop", "orchestral cinematic" | "good music" |
| Mood | "melancholic", "uplifting", "tense" | "nice" |
| Instruments | "acoustic guitar, soft piano, strings" | "instruments" |
| Tempo | "slow ballad 60 BPM", "upbeat 120 BPM" | — |
| Structure | "builds to crescendo", "ambient loops" | — |

---

## Cost Comparison (60s track)

| Model | Cost | Quality | Notes |
|-------|------|---------|-------|
| stableaudio | ~$0.20 | Good | Budget, diffusion-based |
| music15 | ~$0.03 | Good | Best for lyrics |
| music01 | ~$0.035 | Good | Style matching |
| lyria2 | ~$0.12 | High | Negative prompts |
| elevenmusic | ~$0.50 | Premium | Professional quality |

---

## Integration with Studio Agents

- **Video Generation**: Background music for generated videos
- **Text-to-Speech**: Combine speech with background tracks
- **Video Editing**: Merge music with video via `avmerge`

---

## Common Use Cases

| Use Case | Recommended Flow |
|----------|------------------|
| **YouTube video music** | stableaudio → descriptive prompt → 60–120s |
| **Song demo** | music15 → structured lyrics → review |
| **Brand audio logo** | stableaudio → 5–10s → specific style prompt |
| **Podcast intro** | stableaudio → 15–30s → upbeat, no vocals |
| **Film score** | lyria2/elevenmusic → cinematic prompt → long form |

---

## Output Handling

```javascript
import { writeFileSync } from "fs";

// Music typically returns MP3 or WAV
const response = await fetch(output);
const buffer = await response.arrayBuffer();
writeFileSync("output.mp3", Buffer.from(buffer));
```
