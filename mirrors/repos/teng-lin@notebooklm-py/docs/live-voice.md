# Android Live Voice

`client.live.connect(notebook_id)` opens an experimental, notebook-bound Live Voice
session using Android bearer authentication. Unlike Interactive Audio Overviews,
this protocol sends audio bytes over bidirectional gRPC and requires no WebRTC or
existing Audio Overview. Install the library's `android` extra and authenticate
with an Android master token as described in [Android setup](android/README.md).

```python
import asyncio
from notebooklm import NotebookLMClient, LiveAudio, LiveInterrupted, LiveTranscript


async def send_microphone(session, chunks):
    async for pcm in chunks:
        await session.send_audio(pcm, mime_type="audio/pcm;rate=16000")


async def consume(session):
    async for event in session.events():
        if isinstance(event, LiveAudio):
            ...  # caller-owned playback of event.data using event.mime_type
        elif isinstance(event, LiveTranscript):
            ...  # replace displayed text for event.segment_id with event.text
        elif isinstance(event, LiveInterrupted):
            ...  # immediately clear caller-owned queued playback


async def talk(notebook_id, microphone_chunks):
    async with NotebookLMClient.from_storage(backend="android") as client:
        async with client.live.connect(notebook_id, transcribe=True) as session:
            tasks = [
                asyncio.create_task(send_microphone(session, microphone_chunks)),
                asyncio.create_task(consume(session)),
            ]
            try:
                done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                for task in done:
                    task.result()
            finally:
                for task in tasks:
                    task.cancel()
                await asyncio.gather(*tasks, return_exceptions=True)
```

The caller owns capture, playback, codecs and resampling. The SDK neither opens a
microphone nor plays sound. Audio input was qualified with mono PCM16 at 16 kHz;
output was observed as PCM at 24 kHz. Inspect each output event's MIME type.

Entry waits for session establishment, with a configurable 30-second timeout.
The client-wide operation timeout does not cap the stream lifetime; an explicit
enclosing operation deadline still applies.
`source_ids=None` omits the filter; a nonempty sequence supplies explicit source
IDs. Empty filters are rejected rather than guessing their server meaning.
`transcribe=False` omits both transcription flags. No public usage-counter or
reconnection-token parameter is exposed.

Events include establishment, audio, user/model transcript, interruption,
turn-complete and go-away. All have increasing local sequence numbers and a
connection epoch (currently zero, since reconnect is disabled). Optional
`generation_id` is observed server correlation data. Text is a full replacement
for its segment, including revisions; never append transcript events to each
other. `final` is true only when explicitly supplied by the server. Turn-complete
and interruption retire model segments without inventing finality. They do not
retire a still-open input segment.

There is one session per client, one event consumer and one audio write in flight.
Concurrent writers or consumers raise `RuntimeError`. A completed send means the
gRPC write completed, not that the server acknowledged it. Backpressure applies
to the in-flight write; canceling that send closes the session to prevent an
orphan write. Canceling or explicitly closing the event iterator also closes the
session. Always retain the surrounding session context for cleanup when breaking
out of consumption.

Default limits are 256 KiB per in-flight input chunk, 512 KiB queued output audio,
256 pending events and 1 MiB per response and aggregate pending transcript text.
Configure them with `max_input_bytes`, `max_audio_bytes`, `max_events` and
`max_response_bytes`. Oversized input is rejected before serialization. A stalled
consumer that exceeds output bounds fails with `LiveBufferOverflowError`; valid
audio is never silently dropped to make room. Interruption invalidates queued
audio before publishing its control event. Already delivered playback remains the
caller's responsibility.

A response exceeding `max_response_bytes` raises `DecodingError` when it reaches
the SDK. gRPC also applies a finite transport receive cap of the larger of twice
that limit or 4 MiB. Responses beyond the transport cap can instead surface as
`RateLimitError`: gRPC reports the same `RESOURCE_EXHAUSTED` status used for server
quota refusals, and the SDK does not inspect private status text to distinguish
them.

A terminal error discards pending events, wakes blocked sends/receives and remains
available on subsequent operations. Clear playback on failure as well as
interruption. Context exit raises an unobserved terminal failure when its body
has no exception; handled failures are not raised again at exit. Explicit close
is normal termination and future sends raise `LiveSessionClosedError`. Clean
server EOF drains pending events; it does not synthesize turn completion.

Session exit and parent client drain/close cancel the stream and join SDK workers.
They do not depend on consuming events and do not use gRPC half-close. A session
belongs to one parent generation and cannot revive after parent reopen. It does
not occupy an ordinary RPC concurrency slot for its lifetime.

Automatic reconnection remains disabled: `reconnect=True` raises
`UnsupportedOperationError` before dispatch. Go-away is delivered and closes the
session; transport failures are terminal, with no input replay. `RESOURCE_EXHAUSTED`
uses the existing `RateLimitError`; finer quota details remain unqualified.

Web selection rejects Live Voice immediately. Use
the [protocol evidence](android/live-session-static-evidence.md#web-interactive-audio-overviews)
for the separate Web artifact-bound voice path, whose SDK interface is deferred.
MCP and REST do not expose a media path. The observed Android behavior and SDK live
validation are recorded in [the evidence](android/live-session-static-evidence.md).
Additional accounts, natural go-away/resume continuity, bearer expiry during an
established stream and native media quality remain unqualified.
