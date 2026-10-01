# always_on

Phase 2 of dictation: instead of a hotkey gating each recording, always-on mode keeps the microphone open continuously and uses voice-activity detection (VAD) to carve the audio stream into utterances. An utterance opens when energy rises above an onset threshold and closes after a configurable run of silence (the "hangover"). Each finished utterance is transcribed and pushed onto the dictation bus, so it reaches the agent and the notch pill exactly like a hotkey dictation.

Always-on is opt-in (`config.voice_server.always_on_enabled`, default `false`) and pauses while the screen is locked, so nothing spoken at the lock screen is ever transcribed.

## Where the work happens

Everything that is not device I/O runs in the `tinyvoice` module: the segmenter, the downmix, the resample, the per-frame energies, the WAV framing, the wake-word gate, and the intent classifier. This directory owns the `cpal` stream, the thread discipline around it, and the policy decisions (what to transcribe, when to pause, what to tell the notch).

The split follows the audio callback, not the cost of a call. A module call is about 15 microseconds against a 20 ms frame, so the bus is not the constraint. The constraint is that `cpal` delivers audio on a realtime thread where blocking is a dropout, so the callback does the least it can (convert the sample format and forward raw interleaved samples) and every transform happens in the async processor.

## Key files

| File | Role |
| --- | --- |
| `capture.rs` | Host microphone-permission policy over `tinyvoice::capture`, which owns the `cpal` stream and its realtime callback. `spawn_capture_thread` builds the input stream on a dedicated thread and blocks on a readiness handshake; each callback converts the device sample format to `f32` and forwards the interleaved buffer untouched via `try_send` (never blocking `send`), dropping the newest chunk and counting drops when the processor falls behind. |
| `lock_watcher.rs` | The macOS screen-lock privacy hook. `spawn_lock_watcher` polls `CGSessionCopyCurrentDictionary` every two seconds and flips `PAUSED` on lock/unlock transitions. Other platforms log that the watcher is unavailable and never pause (no lock signal yet). |
| `processor.rs` | The async pipeline: owns the `ENABLED`/`PAUSED`/`RUNNING` gates, opens and retries the `tinyvoice::VadSession`, turns raw capture chunks into segmented utterances, and hands finished ones to `transcribe_and_deliver`. `start_if_enabled` is safe to call at boot and at runtime (the Settings toggle calls it through the config RPC); `stop` flips `ENABLED` off for logout without tearing down the microphone stream. |
| `transcribe.rs` | Transcribes a finished utterance through the configured STT provider (the same factory dispatch `voice.stt_dispatch` uses), applies the wake-word gate (`tinyvoice::extract_command`), and routes recognized commands either to a local fast path (`execute_intent`, media transport and volume via `osascript` on macOS) or, for `VoiceIntent::Unknown` or a failed local execution, to the agent via `crate::voice::dictation_listener::publish_transcription`. |

`always_on.rs` (one level up, in `voice/`) is the module entry point: it declares these four submodules, re-exports `start_if_enabled`/`stop`, and holds the shared `LOG_PREFIX` constant.

## Key types and constants

- `capture::RawChunk` / `capture::CaptureFormat`: one chunk of raw, interleaved capture at the device's own sample rate and channel count, plus the format learned once when the stream is built.
- `processor::ENABLED`, `processor::PAUSED`, `processor::RUNNING`: process-wide atomics gating capture, privacy, and single-instance start.
- `processor::SESSION_RETRY_INTERVAL` (30s), `processor::CAPTURE_QUEUE_CHUNKS` (256), `processor::FRAME_MS` (20), `processor::MAX_UTTERANCE_SAMPLES` (60s worth of samples): tuning constants for VAD session retry, the capture channel's bounded queue, VAD frame size, and a defensive cap on a buffered utterance.
- `transcribe::deliver_command` / `execute_intent`: fast-path routing for `VoiceIntent` (pause/resume/next/previous/volume/mute via AppleScript); anything unroutable defers to the agent.

## Wake word and privacy

Transcription is forced to English (`Some("en")`) because auto-detect rendered the wake word in non-Latin scripts that could never match. The wake-word gate fails closed: if `tinyvoice::extract_command` errors, the utterance is dropped rather than delivered unaddressed to the agent. Logs never include the raw transcript or spoken command, only lengths and intent kinds, per the PII-safe logging rule.

## Configuration

- `config.voice_server.always_on_enabled` (bool, default `false`): the on/off switch, applied live by `start_if_enabled` without a restart.
- `config.voice_server.wake_word` (string): the phrase that must prefix a command for it to reach the agent.
- `config.voice_server.vad_*` fields (onset threshold, hangover, min speech, max utterance): mapped into `tinyvoice::VadTuning` by `tinyvoice::vad_config_from_server_config`.

## Notes and gotchas

- The microphone stream is spawned once per process and stays open for the process lifetime once started; toggling `always_on_enabled` off only stops processing, it does not close the stream. Toggling back on reuses it.
- A VAD session that fails to open (for example, the module has not finished downloading) does not stop the capture thread. Audio is dropped and the open is retried on `SESSION_RETRY_INTERVAL` so the feature self-heals without a restart.
- `tinyvoice::capture` (via `capture.rs`) never blocks the realtime audio callback: a full queue drops the newest chunk, which is deliberately the newer end to lose, since the queue ahead of it is older speech closer to being transcribed.

## See also

- [../README.md](../README.md): the voice domain overview, including the RPC surface and the dictation server that hotkey-based dictation uses.
- [../audio_toolkit/README.md](../audio_toolkit/README.md): the sibling podcast-generation toolkit under the same `voice` feature gate.
