---
name: voice-ai-development
description: Designs low-latency voice agents with OpenAI Realtime, Vapi, Deepgram STT, ElevenLabs TTS, and LiveKit. Use when the user mentions voice AI, speech-to-text, text-to-speech, or realtime voice. Not for text-only chat UIs (vercel-ai-sdk-expert) or local ComfyUI audio. Do not hardcode live API keys in examples.
version: 1.0.1
---

## When to Use

- User mentions or implies: voice ai, voice agent, speech to text, text to speech, realtime voice, vapi, deepgram, elevenlabs, livekit, openai realtime.
- Building low-latency, production-ready voice experiences.
- Need to choose the right combination of providers for each use case and optimize for perceived responsiveness.

## Prerequisites

- Async programming (Python or Node.js)
- WebSocket basics
- Audio concepts (sample rate, codec)
- API keys for providers (OpenAI, Vapi, Deepgram, ElevenLabs, LiveKit)
- Audio handling knowledge

## Procedure

### 1. OpenAI Realtime API (Native voice-to-voice with GPT-4o)

**When to use**: When you want integrated voice AI without separate STT/TTS.

```python
import asyncio
import websockets
import json
import base64

OPENAI_API_KEY = "sk-..."

async def voice_session():
    url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Beta": "realtime=v1"
    }

    async with websockets.connect(url, extra_headers=headers) as ws:
        # Configure session
        await ws.send(json.dumps({
            "type": "session.update",
            "session": {
                "modalities": ["text", "audio"],
                "voice": "alloy",  # alloy, echo, fable, onyx, nova, shimmer
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "input_audio_transcription": {
                    "model": "whisper-1"
                },
                "turn_detection": {
                    "type": "server_vad",  # Voice activity detection
                    "threshold": 0.5,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": 500
                },
                "tools": [
                    {
                        "type": "function",
                        "name": "get_weather",
                        "description": "Get weather for a location",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "location": {"type": "string"}
                            }
                        }
                    }
                ]
            }
        }))

        # Send audio (PCM16, 24kHz, mono)
        async def send_audio(audio_bytes):
            await ws.send(json.dumps({
                "type": "input_audio_buffer.append",
                "audio": base64.b64encode(audio_bytes).decode()
            }))

        # Receive events
        async for message in ws:
            event = json.loads(message)

            if event["type"] == "response.audio.delta":
                # Play audio chunk
                audio = base64.b64decode(event["delta"])
                play_audio(audio)

            elif event["type"] == "response.audio_transcript.done":
                print(f"Assistant said: {event['transcript']}")

            elif event["type"] == "input_audio_buffer.speech_started":
                print("User started speaking")

            elif event["type"] == "response.function_call_arguments.done":
                # Handle tool call
                name = event["name"]
                args = json.loads(event["arguments"])
                result = call_function(name, args)
                await ws.send(json.dumps({
                    "type": "conversation.item.create",
                    "item": {
                        "type": "function_call_output",
                        "call_id": event["call_id"],
                        "output": json.dumps(result)
                    }
                }))
```

### 2. Vapi Voice Agent (Phone-based agents, quick deployment)

**When to use**: Phone-based agents, quick deployment.

```python
# Vapi provides hosted voice agents with webhooks
from flask import Flask, request, jsonify
import vapi

app = Flask(__name__)
client = vapi.Vapi(api_key="...")

# Create an assistant
assistant = client.assistants.create(
    name="Support Agent",
    model={
        "provider": "openai",
        "model": "gpt-4o",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful support agent..."
            }
        ]
    },
    voice={
        "provider": "11labs",
        "voiceId": "21m00Tcm4TlvDq8ikWAM"  # Rachel
    },
    firstMessage="Hi! How can I help you today?",
    transcriber={
        "provider": "deepgram",
        "model": "nova-2"
    }
)

# Webhook for conversation events
@app.route("/vapi/webhook", methods=["POST"])
def vapi_webhook():
    event = request.json

    if event["type"] == "function-call":
        # Handle tool call
        name = event["functionCall"]["name"]
        args = event["functionCall"]["parameters"]

        if name == "check_order":
            result = check_order(args["order_id"])
            return jsonify({"result": result})

    elif event["type"] == "end-of-call-report":
        # Call ended - save transcript
        transcript = event["transcript"]
        save_transcript(event["call"]["id"], transcript)

    return jsonify({"ok": True})

# Start outbound call
call = client.calls.create(
    assistant_id=assistant.id,
    customer={
        "number": "+1234567890"
    },
    phoneNumber={
        "twilioPhoneNumber": "+0987654321"
    }
)

# Or create web call
web_call = client.calls.create(
    assistant_id=assistant.id,
    type="web"
)
# Returns URL for WebRTC connection
```

### 3. Deepgram STT + ElevenLabs TTS (Best-in-class transcription and synthesis)

**When to use**: High quality voice, custom pipeline.

```python
import asyncio
from deepgram import DeepgramClient, LiveTranscriptionEvents
from elevenlabs import ElevenLabs

# Deepgram real-time transcription
deepgram = DeepgramClient(api_key="...")

async def transcribe_stream(audio_stream):
    connection = deepgram.listen.live.v("1")

    async def on_transcript(result):
        transcript = result.channel.alternatives[0].transcript
        if transcript:
            print(f"Heard: {transcript}")
            if result.is_final:
                # Process final transcript
                await handle_user_input(transcript)

    connection.on(LiveTranscriptionEvents.Transcript, on_transcript)

    await connection.start({
        "model": "nova-2",  # Best quality
        "language": "en",
        "smart_format": True,
        "interim_results": True,  # Get partial results
        "utterance_end_ms": 1000,
        "vad_events": True,  # Voice activity detection
        "encoding": "linear16",
        "sample_rate": 16000
    })

    # Stream audio
    async for chunk in audio_stream:
        await connection.send(chunk)

    await connection.finish()

# ElevenLabs streaming synthesis
eleven = ElevenLabs(api_key="...")

def text_to_speech_stream(text: str):
    """Stream TTS audio chunks."""
    audio_stream = eleven.text_to_speech.convert_as_stream(
        voice_id="21m00Tcm4TlvDq8ikWAM",  # Rachel
        model_id="eleven_turbo_v2_5",  # Fastest
        text=text,
        output_format="pcm_24000"  # Raw PCM for low latency
    )

    for chunk in audio_stream:
        yield chunk

# Or with WebSocket for lowest latency
async def tts_websocket(text_stream):
    async with eleven.text_to_speech.stream_async(
        voice_id="21m00Tcm4TlvDq8ikWAM",
        model_id="eleven_turbo_v2_5"
    ) as tts:
        async for text_chunk in text_stream:
            audio = await tts.send(text_chunk)
            yield audio

        # Flush remaining audio
        final_audio = await tts.flush()
        yield final_audio
```

### 4. LiveKit Real-time Infrastructure (WebRTC infrastructure for voice apps)

**When to use**: Building custom real-time voice apps.

```python
from livekit import api, rtc
import asyncio

# Server-side: Create room and tokens
lk_api = api.LiveKitAPI(
    url="wss://your-livekit.livekit.cloud",
    api_key="...",
    api_secret="..."
)

async def create_room(room_name: str):
    room = await lk_api.room.create_room(
        api.CreateRoomRequest(name=room_name)
    )
    return room

def create_token(room_name: str, participant_name: str):
    token = api.AccessToken(
        api_key="...",
        api_secret="..."
    )
    token.with_identity(participant_name)
    token.with_grants(api.VideoGrants(
        room_join=True,
        room=room_name
    ))
    return token.to_jwt()

# Agent-side: Connect and process audio
async def voice_agent(room_name: str):
    room = rtc.Room()

    @room.on("track_subscribed")
    def on_track(track, publication, participant):
        if track.kind == rtc.TrackKind.KIND_AUDIO:
            # Process incoming audio
            audio_stream = rtc.AudioStream(track)
            asyncio.create_task(process_audio(audio_stream))

    token = create_token(room_name, "agent")
    await room.connect("wss://your-livekit.livekit.cloud", token)

    # Publish agent's audio
    source = rtc.AudioSource(sample_rate=24000, num_channels=1)
    track = rtc.LocalAudioTrack.create_audio_track("agent-voice", source)
    await room.local_participant.publish_track(track)

    # Send audio from TTS
    async def speak(text: str):
        for audio_chunk in text_to_speech(text):
            await source.capture_frame(rtc.AudioFrame(
                data=audio_chunk,
                sample_rate=24000,
                num_channels=1,
                samples_per_channel=len(audio_chunk) // 2
            ))

    return room, speak

# Process audio with STT
async def process_audio(audio_stream):
    async for frame in audio_stream:
        # Send to Deepgram or other STT
        await transcriber.send(frame.data)
```

### 5. Full Voice Agent Pipeline (Complete voice agent with all components)

**When to use**: Custom production voice agent.

```python
import asyncio
from dataclasses import dataclass
from typing import AsyncIterator

@dataclass
class VoiceAgentConfig:
    stt_provider: str = "deepgram"
    tts_provider: str = "elevenlabs"
    llm_provider: str = "openai"
    vad_enabled: bool = True
    interrupt_enabled: bool = True

class VoiceAgent:
    def __init__(self, config: VoiceAgentConfig):
        self.config = config
        self.is_speaking = False
        self.conversation_history = []

    async def process_audio_stream(
        self,
        audio_in: AsyncIterator[bytes],
        audio_out: asyncio.Queue
    ):
        """Main audio processing loop."""

        # STT streaming
        async def transcribe():
            transcript_buffer = ""
            async for audio_chunk in audio_in:
                # Check for interruption
                if self.is_speaking and self.config.interrupt_enabled:
                    if await self.detect_speech(audio_chunk):
                        await self.stop_speaking()

                result = await self.stt.transcribe(audio_chunk)
                if result.is_final:
                    yield result.transcript

        # Process transcripts
        async for user_text in transcribe():
            if not user_text.strip():
                continue

            self.conversation_history.append({
                "role": "user",
                "content": user_text
            })

            # Generate response with streaming
            self.is_speaking = True
            async for audio_chunk in self.generate_response(user_text):
                await audio_out.put(audio_chunk)
            self.is_speaking = False

    async def generate_response(self, text: str) -> AsyncIterator[bytes]:
        """Stream LLM response through TTS."""

        # Stream LLM tokens
        llm_stream = self.llm.stream_chat(self.conversation_history)

        # Buffer for TTS (need ~50 chars for good prosody)
        text_buffer = ""
        full_response = ""

        async for token in llm_stream:
            text_buffer += token
            full_response += token

            # Send to TTS when we have enough text
            if len(text_buffer) > 50 or token in ".!?":
                async for audio in self.tts.synthesize_stream(text_buffer):
                    yield audio
                text_buffer = ""

        # Flush remaining
        if text_buffer:
            async for audio in self.tts.synthesize_stream(text_buffer):
                yield audio

        self.conversation_history.append({
            "role": "assistant",
            "content": full_response
        })

    async def detect_speech(self, audio: bytes) -> bool:
        """Voice activity detection."""
        # Use WebRTC VAD or Silero VAD
        return self.vad.is_speech(audio)

    async def stop_speaking(self):
        """Handle interruption."""
        self.is_speaking = False
        # Clear audio queue
        # Stop TTS generation

# Latency optimization tips:
# 1. Use streaming everywhere (STT, LLM, TTS)
# 2. Start TTS before LLM finishes (~50 char buffer)
# 3. Use PCM audio format (no encoding overhead)
# 4. Keep WebSocket connections alive
# 5. Use regional endpoints close to users
```

## Pitfalls

- **Non-Streaming TTS (HIGH)**: Non-streaming TTS adds significant latency. Fix: Use `tts.synthesize_stream()` or `tts.convert_as_stream()`.
- **Hardcoded Sample Rate (MEDIUM)**: Hardcoded sample rate may cause format mismatches. Fix: Define sample rates as constants, document expected formats.
- **WebSocket Without Reconnection (HIGH)**: WebSocket connections need reconnection logic. Fix: Add retry loop with exponential backoff.
- **Missing VAD Configuration (MEDIUM)**: VAD needs tuning for good user experience. Fix: Configure threshold and silence_duration_ms.
- **Blocking Audio Processing (HIGH)**: Audio processing should be async to avoid blocking. Fix: Use `async def` and `await` for audio operations.
- **Missing Interruption Handling (MEDIUM)**: Voice agents should handle user interruptions. Fix: Add barge-in detection and cancel current response.
- **Audio Queue Without Clear (LOW)**: Audio queues should be clearable for interruptions. Fix: Add method to clear queue on interruption.
- **WebSocket Without Error Handling (HIGH)**: WebSocket operations need error handling. Fix: Wrap in try/except for ConnectionClosed.

## Verification

- **Check WebSocket Connection**: Ensure the WebSocket connection to the provider (e.g., OpenAI Realtime API) is established successfully. Look for `session.update` acceptance.
- **Audio Stream Test**: Verify that audio chunks are being received and decoded properly. Check `response.audio.delta` events.
- **VAD Configuration**: Confirm VAD events (`input_audio_buffer.speech_started`) are firing when expected.
- **Tool Call Execution**: Verify that function calls are received, executed, and results are sent back correctly.

## Related Skills

- `langgraph`: Need complex agent logic behind voice.
- `structured-output`: Need to extract structured data from voice.
- `langfuse`: Need to monitor voice agent quality.
- `twilio`: Connect to Twilio for PSTN.
- `nextjs-app-router`: Need web interface for voice agent.
