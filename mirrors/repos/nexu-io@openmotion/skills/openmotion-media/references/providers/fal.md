# fal.ai BYOK

Checked against official documentation on 2026-11-15. Sections: discovery, request templates, polling, errors, sources.

## Setup and discovery

Save the key in editor **Model providers**. `FAL_KEY` is the environment alternative; a saved key wins. The service injects `Authorization: Key ...` (not Bearer). Agents discover with `openmotion_media_use` and generate with `openmotion_assets_use`; never read credential files or put keys in tool arguments.

Call the tool with:

```json
{"action":"models","provider":"fal","refresh":true,"modality":"image","query":"flux","limit":20}
```

Discovery reads the public catalogue `GET https://api.fal.ai/v1/models?status=active` without authentication. Read `models` and use `next_cursor` as the next `cursor` query parameter. The adapter follows at most three pages. Remove or change the tool's modality/query for video or audio. The tool normalizes model metadata; consult the selected model's API page for its full schema. Public discovery does not validate the saved key, balance or account access; cached/built-in entries are not live entitlement checks.

## Request templates

These are `openmotion_assets_use` arguments, not provider HTTP bodies. Choose a new `requestId` for each intended generation. Models/fields below are starting points; check the current model schema before submission. Each generate call can incur charges.

Image — [FLUX Schnell schema](https://fal.ai/models/fal-ai/flux/schnell/api):

```json
{"action":"generate","requestId":"fal-image-01","model":"fal:fal-ai/flux/schnell","modality":"image","mode":"text-to-image","prompt":"A ceramic cup on a wooden table, soft morning light","parameters":{"image_size":"square_hd","num_images":1,"num_inference_steps":4,"output_format":"png"}}
```

Video — [Wan text-to-video schema](https://fal.ai/models/fal-ai/wan/v2.2-a14b/text-to-video/api):

```json
{"action":"generate","requestId":"fal-video-01","model":"fal:fal-ai/wan/v2.2-a14b/text-to-video","modality":"video","mode":"text-to-video","prompt":"Steam rises from a ceramic cup as the camera slowly moves closer","parameters":{"num_frames":81,"resolution":"720p","aspect_ratio":"16:9"}}
```

Speech — [Kokoro schema](https://fal.ai/models/fal-ai/kokoro/american-english/api):

```json
{"action":"generate","requestId":"fal-speech-01","model":"fal:fal-ai/kokoro/american-english","modality":"audio","mode":"text-to-audio","prompt":"Welcome to a quiet morning.","parameters":{"voice":"af_heart","speed":1}}
```

Kokoro expects **`prompt`**. The exact `fal-ai/kokoro/american-english` adapter preserves that field for both audio and speech modes. For a different speech model whose schema expects **`text`**, use `mode: "text-to-speech"`. This mode controls the input field, not whether the output contains speech. Do not assume every TTS model uses `text`.

Wire mapping: POST `https://queue.fal.run/{full model ID}` with `{...parameters,prompt}`; replace `prompt` with `text` for other `text-to-speech` endpoints. The full model ID stays in the URL, not the JSON body.

For fal models, reference-image/video/audio fields, if supported, belong in `parameters` under their exact schema names. Supply publicly reachable URLs or schema-supported data URIs. The new top-level `referenceAsset` is for adapters with implemented local image editing; fal local-path upload is not implemented. Arbitrary text, 3D and training outputs are outside the media-file adapter.

## Music and sound effects

Reviewed 2026-11-16 against the [ElevenLabs music schema](https://fal.ai/models/fal-ai/elevenlabs/music/api), [Sound Effects V2 schema](https://fal.ai/models/fal-ai/elevenlabs/sound-effects/v2/api) and [Sound Effects V3 OpenAPI](https://fal.ai/api/openapi/queue/openapi.json?endpoint_id=elevenlabs/sound-effects/v3). Audio output alone does not establish speech: choose the model’s actual operation.

```json
{"action":"generate","requestId":"music-01","model":"fal:fal-ai/elevenlabs/music","modality":"audio","mode":"text-to-audio","prompt":"Gentle piano background music, warm and calm","parameters":{"music_length_ms":10000,"force_instrumental":true}}
```

```json
{"action":"generate","requestId":"sfx-01","model":"fal:elevenlabs/sound-effects/v3","modality":"audio","mode":"text-to-audio","prompt":"A gentle wind chime tinkling in a soft breeze","parameters":{"duration_seconds":2,"loop":true}}
```

Music sends the brief in `prompt`. ElevenLabs Sound Effects, Sound Effects V2 and Sound Effects V3 send it in `text` while retaining `text-to-audio`; they are not relabeled as speech and require no voice. Other parameters pass through under their native keys. Do not apply music duration units or speech voice options to SFX. Availability, accepted options and billing remain model-specific; inspect the current catalogue and schema. These examples do not submit a request by themselves.

## Polling and result

Submission returns `request_id`, `status_url`, `response_url` and optionally `cancel_url`. Use those returned URLs: nested model paths may have different polling paths. The adapter accepts only the `https://queue.fal.run` origin and preserves the remote request ID.

`IN_QUEUE` / `IN_PROGRESS` mean wait. `COMPLETED` means retrieve the result, not that generation necessarily succeeded. Recognized `images`, `video` or `audio` URLs are imported. In the Agent workflow poll the local job, without another generate call:

```json
{"action":"status","jobId":"LOCAL_JOB_ID_FROM_GENERATE"}
```

Only local `completed` plus imported assets establishes media availability. Cancel uses the returned remote cancel URL on a best-effort basis; charges can continue. Polling errors/local deadlines do not prove remote cancellation. Submission is not automatically retried.

## Error interpretation

Distinguish HTTP status, provider error type and model validation detail. These are diagnostic categories, not a diagnosis from the status alone. See [request errors](https://fal.ai/docs/documentation/model-apis/request-errors) and [model errors](https://fal.ai/docs/documentation/model-apis/errors).

| Signal | Meaning / next action |
| --- | --- |
| HTTP 401 | Authentication did not succeed. Verify the `queue.fal.run` endpoint, `Key` scheme and configured credential source; a public catalogue success says nothing about authentication. Do not assert that the key expired without provider evidence. |
| HTTP 403 | Access was denied. Check the selected endpoint/account permission and actual provider detail; replacing the key is not a proven fix. |
| HTTP 400 / 422 | Inspect the selected model schema and validation detail: required field, type, allowed value or policy rejection. In particular, check `prompt` versus `text`. Correct the input before resubmitting. |
| HTTP 429 | Request/concurrency limits may apply. Reduce parallel work and follow provider retry guidance; do not repeatedly create paid jobs. |
| HTTP 5xx / network timeout | Transient failure or an uncertain submission outcome. If an ID exists, inspect that original request; otherwise check provider history before deciding on a new submission. |
| `error_type` / validation `detail` | Request errors can include a flat detail and `error_type`; model validation can include a detail array. `X-Fal-Error-Type` can add context when available. Preserve the distinction instead of calling every failure a key error. |

Current OpenMotion non-2xx handling does **not** expose the provider's raw body or response headers. `Provider HTTP 401: credentials or permissions rejected` is locally synthesized wording, not fal's confirmed explanation. Report missing detail as unknown; use provider-side request history/support for a definitive cause. Never include keys or authenticated headers in diagnostics.

## Sources

- [Key setup](https://fal.ai/dashboard/keys), [catalogue API](https://fal.ai/docs/platform-apis/v1/models)
- [Queue overview](https://fal.ai/docs/documentation/model-apis/inference/queue), [submit](https://fal.ai/docs/api-reference/inference-api/queue/submit), [status](https://fal.ai/docs/api-reference/inference-api/queue/status), [result](https://fal.ai/docs/api-reference/inference-api/queue/result), [cancel](https://fal.ai/docs/api-reference/inference-api/queue/cancel)

Maintained model discovery includes `generationOptions` for FLUX Schnell, Wan 2.2 and Kokoro. Studio and MCP use these same native keys and types; unspecified endpoints require their own current schema.
