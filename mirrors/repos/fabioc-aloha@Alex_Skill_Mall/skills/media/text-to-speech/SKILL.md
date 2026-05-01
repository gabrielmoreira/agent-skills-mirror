---
type: skill
lifecycle: stable
inheritance: inheritable
name: "text-to-speech"
description: Cloud TTS via Replicate — 15 models, voice cloning, emotion control, and multi-language support
tier: extended
applyTo: '**/*text*,**/*speech*'
currency: 2026-04-22
lastReviewed: 2026-04-30
---

# Text-to-Speech Skill


> **Domain**: AI Audio Generation  
> **Version**: 4.0.0  
> **Last Updated**: 2026-04-15  
> **Author**: the AI assistant (your AI assistant)  
> **Source**: Patterns from AlexVideos CLI toolkit  
> **Staleness Watch**: See [EXTERNAL-API-REGISTRY.md](../../EXTERNAL-API-REGISTRY.md) for source URLs and recheck cadence

## Overview

Cloud-based speech synthesis via Replicate. 15 models spanning MiniMax, Resemble AI, ElevenLabs, Qwen, and Kokoro for narration, audiobooks, voice cloning, and content creation.

---

## Model Catalog (15 Models)

| Key | Model | Replicate ID | Cost | Cloning | Languages |
|-----|-------|--------------|------|---------|-----------|
| `mm28turbo` | **Speech 2.8 Turbo** | `minimax/speech-2.8-turbo` | $0.06/1k tokens | ❌ | 40+ |
| `mm28hd` | **Speech 2.8 HD** | `minimax/speech-2.8-hd` | $0.10/1k tokens | ❌ | 40+ |
| `mm02turbo` | **Speech 02 Turbo** | `minimax/speech-02-turbo` | $0.06/1k tokens | ❌ | 40+ |
| `mm02hd` | **Speech 02 HD** | `minimax/speech-02-hd` | $0.10/1k tokens | ❌ | 40+ |
| `mm26turbo` | **Speech 2.6 Turbo** | `minimax/speech-2.6-turbo` | $0.06/1k tokens | ❌ | 40+ |
| `mm26hd` | **Speech 2.6 HD** | `minimax/speech-2.6-hd` | $0.10/1k tokens | ❌ | 40+ |
| `mmclone` | **MiniMax Clone** | `minimax/voice-cloning` | $3/output | ✅ | — |
| `chatterbox` | **Chatterbox** | `resemble-ai/chatterbox` | $0.025/1k chars | ✅ | EN |
| `chatturbo` | **Chatterbox Turbo** | `resemble-ai/chatterbox-turbo` | $0.025/1k chars | ✅ | EN |
| `chatpro` | **Chatterbox Pro** | `resemble-ai/chatterbox-pro` | $0.04/1k chars | ✅ | EN |
| `chatmlang` | **Chatterbox Multilingual** | `resemble-ai/chatterbox-multilingual` | variable | ✅ | Multi |
| `qwentts` | **Qwen TTS** | `amphion/qwen3-tts` | $0.02/1k chars | ✅ | 10 |
| `elevenv3` | **ElevenLabs v3** | `elevenlabs/el-multilingual-v3` | $0.10/1k chars | ❌ | Multi |
| `eleventurbo` | **ElevenLabs Turbo** | `elevenlabs/el-turbo-v2.5` | $0.05/1k chars | ❌ | Multi |
| `kokoro` | **Kokoro 82M** | `jaaari/kokoro-82m` | per-second GPU | ❌ | EN |

---

## Parameter Support Matrix

| Model | text | voice | speed | pitch | volume | emotion | audio ref | language | temperature |
|-------|:----:|:-----:|:-----:|:-----:|:------:|:-------:|:---------:|:--------:|:-----------:|
| `mm28turbo` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — | ✅ | — |
| `mm28hd` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — | ✅ | — |
| `mm02turbo` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — | ✅ | — |
| `mm02hd` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — | ✅ | — |
| `mm26turbo` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — | ✅ | — |
| `mm26hd` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — | ✅ | — |
| `mmclone` | — | — | — | — | — | — | ✅ req | — | — |
| `chatterbox` | ✅ | — | — | — | — | — | ✅ | — | ✅ |
| `chatturbo` | ✅ | — | — | — | — | — | ✅ | — | ✅ |
| `chatpro` | ✅ | ✅ | — | ✅ | — | — | — | — | — |
| `chatmlang` | ✅ | — | — | — | — | — | ✅ | ✅ | ✅ |
| `qwentts` | ✅ | — | — | — | — | — | ✅ | — | ✅ |
| `elevenv3` | ✅ | ✅ | ✅ | — | — | — | — | ✅ | — |
| `eleventurbo` | ✅ | ✅ | ✅ | — | — | — | — | ✅ | — |
| `kokoro` | ✅ | ✅ | ✅ | — | — | — | — | — | — |

---

## Model Selection Guide

| Scenario | Model | Why |
|----------|-------|-----|
| **Default / Quick draft** | mm28turbo | Fast, cheapest per-token |
| **Studio-grade narration** | mm28hd | Highest fidelity, 40+ languages |
| **Clone a specific voice** | chatturbo, mmclone | 5-second sample, natural pauses |
| **Voice from description** | qwentts | No sample needed, describe the voice |
| **Emotion control** | mm28turbo/hd | happy, sad, angry, fearful, disgusted, surprised |
| **Non-English content** | mm28turbo, elevenv3 | Broadest language support |
| **ElevenLabs quality** | elevenv3 | Premium quality, fine-tuned controls |
| **Lightweight / local** | kokoro | Minimal model, fast |

---

## Voice Presets

**MiniMax Speech**: `Wise_Woman`, `Deep_Voice_Man`, `Casual_Guy`, `Lively_Girl`, `Young_Knight`, `Abbess`, `Childish_Girl`, `Friendly_Woman`, `Gentle_Man`, `Gentle_Woman`, `Inspirational_girl`, `Lovely_Girl`

**Chatterbox Pro**: `Andy`, `Luna`, `Ember`, `Aurora`, `Cliff`, `Josh`, `William`, `Orion`, `Ken`

**Kokoro**: `af_heart`, `af_star`, `af_sky`, `am_adam`, `am_michael`, `bf_emma`, `bf_isabella`, `bm_lewis`, `bm_george` (prefix: `af` = American female, `am` = American male, `bf` = British female, `bm` = British male)

---

## Emotion & Prosody Control (MiniMax)

```javascript
await replicate.run("minimax/speech-2.8-turbo", {
  input: {
    text: "I am absolutely thrilled with these results!",
    voice: "Lively_Girl",
    emotion: "happy",    // auto, happy, sad, angry, fearful, disgusted, surprised
    speed: 1.2,          // 0.5–2.0 (default 1.0)
    pitch: 5,            // -12 to +12 semitones (default 0)
    volume: 0,           // -6 to +6 dB (default 0)
    language: "en-US",   // 40+ language codes
  },
});
```

---

## Voice Cloning

### Chatterbox (5-second sample)

```javascript
await replicate.run("resemble-ai/chatterbox-turbo", {
  input: {
    text: "Content to speak in the cloned voice",
    audio_prompt: referenceAudioDataURI, // 5+ seconds WAV/MP3
    temperature: 0.7, // 0.1–1.0 (higher = more variation)
  },
});
```

### MiniMax Voice Cloning (Dedicated)

```javascript
await replicate.run("minimax/voice-cloning", {
  input: {
    audio_sample: referenceAudioDataURI, // High-quality sample
  },
}); // Returns custom voice_id for use in speech models
```

---

## Voice Design (Qwen TTS)

Create a voice from natural language description — no sample needed:

```javascript
await replicate.run("amphion/qwen3-tts", {
  input: {
    text: "Content to speak",
    tts_mode: "voice_design",
    voice_description: "A warm, friendly female voice with a slight British accent",
    temperature: 0.8,
  },
});
```

---

## ElevenLabs Parameters

```javascript
await replicate.run("elevenlabs/el-multilingual-v3", {
  input: {
    text: "Content to speak",
    voice_id: "21m00Tcm4TlvDq8ikWAM", // Rachel
    model_id: "eleven_multilingual_v2",
    stability: 0.5,        // 0–1 (higher = more consistent)
    similarity_boost: 0.5, // 0–1 (higher = closer to original voice)
    style: 0.0,            // 0–1 (style exaggeration)
    use_speaker_boost: true,
  },
});
```

---

## macOS Offline Fallback: `say`

macOS ships 30+ built-in neural voices via the `say` command. Instant, offline, zero-cost:

```bash
say "Hello from the AI assistant"
say -f document.txt
say -o output.m4a --data-format=aac "Dream state finished"
say -v the AI assistant "I am the AI assistant, reading your documentation"
```

---

## Integration with Studio Agents

- **Video Generation**: Generate narration → merge with `avmerge`
- **Audio Memory**: Store voice samples for consistent cloning
- **Music Generation**: Combine speech with background music

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 4.0.0 | 2026-04-15 | Expanded to 15 models from AlexVideos patterns |
| 3.0.0 | 2026-04-09 | Removed Edge TTS, Replicate-only focus |
| 2.5.0 | 2026-02-09 | Speak Prompt command (Edge TTS era) |
| 1.0.0 | 2026-02-04 | Initial implementation via MCP server |
