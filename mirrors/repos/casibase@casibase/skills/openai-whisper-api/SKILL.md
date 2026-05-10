---
name: openai-whisper-api
description: Transcribe audio via OpenAI Audio Transcriptions API (Whisper).
homepage: https://platform.openai.com/docs/guides/speech-to-text
metadata:
  {
    "emoji": "🌐",
    "requires": { "bins": ["curl"], "env": ["OPENAI_API_KEY"] },
    "primaryEnv": "OPENAI_API_KEY"
  }
---

# OpenAI Whisper API (curl)

Transcribe an audio file via OpenAI's `/v1/audio/transcriptions` endpoint. Set `OPENAI_BASE_URL` to use an OpenAI-compatible proxy or local gateway.

## Quick start

```bash
curl -sS "https://api.openai.com/v1/audio/transcriptions" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F "file=@/path/to/audio.m4a" \
  -F "model=whisper-1" \
  -F "response_format=text" \
  > transcript.txt
```

Defaults:

- Model: `whisper-1`
- Output format: `text`

## Options

```bash
# With language hint
curl -sS "https://api.openai.com/v1/audio/transcriptions" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F "file=@audio.ogg" \
  -F "model=whisper-1" \
  -F "response_format=text" \
  -F "language=en" \
  > transcript.txt

# With speaker hint (prompt)
curl -sS "https://api.openai.com/v1/audio/transcriptions" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F "file=@audio.m4a" \
  -F "model=whisper-1" \
  -F "response_format=text" \
  -F "prompt=Speaker names: Peter, Daniel" \
  > transcript.txt

# JSON output
curl -sS "https://api.openai.com/v1/audio/transcriptions" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F "file=@audio.m4a" \
  -F "model=whisper-1" \
  -F "response_format=json" \
  > transcript.json
```

## Custom base URL

Set `OPENAI_BASE_URL` to use an OpenAI-compatible proxy or local gateway:

```bash
API_BASE="${OPENAI_BASE_URL:-https://api.openai.com/v1}"
curl -sS "${API_BASE}/audio/transcriptions" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F "file=@audio.m4a" \
  -F "model=whisper-1" \
  -F "response_format=text" \
  > transcript.txt
```

## API key

Set `OPENAI_API_KEY` environment variable before running commands.
