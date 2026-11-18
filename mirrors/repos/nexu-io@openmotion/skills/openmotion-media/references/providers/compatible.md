# Compatible image, speech and transcription APIs

Checked on 2026-11-15 against the [OpenAI image API](https://developers.openai.com/api/reference/resources/images) and [speech API](https://developers.openai.com/api/reference/resources/audio/subresources/speech/methods/create). Compatibility depends on the selected provider implementing these contracts; a provider preset is not certification of every model or endpoint.

Configure a public HTTPS API base URL, protocol and key in **Settings → Model providers**. Keep the documented version/path prefix, such as `/v1`. The local service stores the key privately and injects `Authorization: Bearer …`; never read it or pass it to the Tool. User-configurable URLs retain public DNS validation and do not follow authenticated redirects. Localhost/private-network services require a dedicated integration.

Call `openmotion_media_use` with `action=inspect` to obtain the actual provider ID (custom IDs start with `custom-`). Read this reference, then call `action=models`, `provider=<that ID>`, `refresh=true`. Discovery uses `GET <base>/models` and reads `data[].id`; explicit output metadata establishes image/audio capability. Known documented OpenAI/Groq ASR IDs are classified as Transcription; other unknown models remain language models. In settings, add a model with its exact ID and Image or Audio capability when the provider's documentation confirms that operation. Language and embedding defaults are configuration for Agent integrations, not media generation.

Image request template (replace placeholders with discovered IDs):

```json
{"action":"generate","requestId":"image-one","model":"PROVIDER_ID:MODEL_ID","modality":"image","prompt":"A ceramic cup","parameters":{"size":"1024x1024"}}
```

The wire request is `POST <base>/images/generations` with JSON `{model,prompt,...parameters}`. Read the selected model's supported parameters first. Returned `data[].b64_json` or `data[].url` becomes validated project-owned media. This adapter does not implement an image-edit upload protocol or asynchronous video endpoints.

Speech request template:

```json
{"action":"generate","requestId":"speech-one","model":"PROVIDER_ID:MODEL_ID","modality":"audio","mode":"text-to-speech","prompt":"Welcome to the studio.","parameters":{"voice":"PROVIDER_VOICE_ID"}}
```

The wire request is `POST <base>/audio/speech` with JSON `{model,input:prompt,voice,...parameters}` and binary audio output. Voice is required; music and sound-effects protocols are not implemented by this adapter. Transcription uses the separate shared transcript service below.

The Tool returns a local queued job. Poll `action=status` with the original jobId until completion. A successful synchronous provider response has no separate remote task ID. Stable requestId prevents duplicate local submission. HTTP 401/403 means authorization or permissions were rejected; 400/422 needs a model/input correction; 429 means rate/quota limits; 5xx or timeout can have an uncertain paid outcome. Raw upstream bodies and keys are not exposed. No error automatically resubmits, changes model or changes provider. Local cancel cannot establish remote cancellation or refund; inspect provider history before intentionally retrying.


## Speech-to-text and editable captions

Checked on 2026-11-17 against the [OpenAI speech-to-text guide](https://developers.openai.com/api/docs/guides/speech-to-text) and [Groq speech-to-text reference](https://console.groq.com/docs/speech-to-text). Configure the same provider connection, add/sync an exact model with **Transcription** capability and choose its supported response format. This capability is distinct from audio generation and has its own default model. Discover it through the public asset Tool:

```json
{"action":"transcript","transcript":{"command":"models"}}
```

Import real source media to a project first, then submit through `openmotion_assets_use`:

```json
{"action":"transcript","transcript":{"command":"submit","projectId":"PROJECT_ID","sourcePath":"assets/interview.mp4","model":"PROVIDER_ID:MODEL_ID","language":"auto","requestId":"interview-asr-1","parameters":{"response_format":"verbose_json","timestamp_granularities":["word","segment"]}}}
```

The wire operation is one authenticated multipart `POST <base>/audio/transcriptions` per audio chunk: fields `file` (mono 16 kHz WAV), `model`, `response_format`, optional `language`, and repeated `timestamp_granularities[]`. The service extracts the first audio track and chunks long media into ten-minute windows below the 25 MB upload ceiling, preserving source-relative offsets. It does not follow authenticated redirects or retry uncertain paid POSTs. Poll `command=status` with the returned projectId/jobId; `cancel` stops local work without establishing a provider refund or remote stop.

Groq `whisper-large-v3` and `whisper-large-v3-turbo` document `verbose_json` with segment/word granularities. OpenAI `gpt-transcribe` is text-oriented and uses `json`; its optional language hints are sent as `languages[]`. Text-only responses remain untimed: do not derive invented subtitle timings. Provider-supported diarization uses `diarized_json` with `chunking_strategy=auto`, without prompts or word-granularity options. OpenAI's former Whisper/4o transcription models are documented as deprecated with a February 26, 2027 shutdown; their presence in a live catalogue is not a recommendation to adopt them for a new installation. Custom compatible models must use their own documented format/options.

Completed jobs expose a versioned transcript through `command=get`. `update` carries `expectedTranscriptRevision`, stable requestId and corrected segments. The original text remains available. `export` returns TXT/SRT/VTT/JSON; subtitle formats require actual timestamps. `captions` applies editable native text clips through project history with explicit composition/source/timeline mapping and all three transcript/project/version guards. Read [the complete workflow](../../../../docs/transcripts.md) for the command table, source-change protection, multilingual copies, platform handoff, user stories and limits.

401/403 directs the user to credentials/model access; 400/422 requires a corrected model or parameters; 429 requires checking quota/rate limits. 5xx and timeout are uncertain outcomes: inspect the original job/provider account before requesting new paid work. Raw upstream error bodies are never placed in the transcript job. There is no generic local Whisper backend, automatic translated dubbing or publishing integration.
