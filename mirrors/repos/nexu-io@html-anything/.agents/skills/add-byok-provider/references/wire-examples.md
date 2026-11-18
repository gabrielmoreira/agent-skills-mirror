# Provider wire examples

Shell equivalents of the requests the service sends for each built-in provider. They document the wire protocol for adapter work and user-run diagnostics; product Agents use the Tools and never call these endpoints. Use environment placeholders only; never paste a real key.

## fal.ai

Public catalogue (no authentication):

```bash
curl --fail-with-body --silent --show-error --get 'https://api.fal.ai/v1/models' \
  --data-urlencode 'status=active' --data-urlencode 'limit=100' --data-urlencode 'q=flux'
```

Image submission; the full model ID stays in the URL:

```bash
curl --fail-with-body --silent --show-error 'https://queue.fal.run/fal-ai/flux/schnell' \
  -H "Authorization: Key ${FAL_KEY:?Set FAL_KEY locally}" -H 'Content-Type: application/json' \
  --data '{"prompt":"A ceramic cup on a wooden table, soft morning light","image_size":"square_hd","num_images":1,"num_inference_steps":4,"output_format":"png"}'
```

Polling and result:

```bash
# Use original response URLs, verified to have origin https://queue.fal.run.
curl --fail-with-body --silent --show-error "${FAL_STATUS_URL:?Use returned status_url}" \
  -H "Authorization: Key ${FAL_KEY:?Set FAL_KEY locally}"
# Fetch only after status is COMPLETED; the result can still report a model error.
curl --fail-with-body --silent --show-error "${FAL_RESPONSE_URL:?Use returned response_url}" \
  -H "Authorization: Key ${FAL_KEY:?Set FAL_KEY locally}"
```

## Atlas Cloud

Public catalogue:

```bash
curl --fail-with-body --silent --show-error 'https://api.atlascloud.ai/api/v1/models'
```

Image submission:

```bash
curl --fail-with-body --silent --show-error 'https://api.atlascloud.ai/api/v1/model/generateImage' \
  -H "Authorization: Bearer ${ATLASCLOUD_API_KEY:?Set ATLASCLOUD_API_KEY locally}" \
  -H 'Content-Type: application/json' \
  --data '{"model":"google/nano-banana-2/text-to-image","prompt":"A ceramic cup on a wooden table, soft morning light","aspect_ratio":"1:1","resolution":"1k","output_format":"png"}'
```

Polling the original prediction:

```bash
curl --fail-with-body --silent --show-error \
  "https://api.atlascloud.ai/api/v1/model/prediction/${ATLAS_PREDICTION_ID:?Use original data.id}" \
  -H "Authorization: Bearer ${ATLASCLOUD_API_KEY:?Set ATLASCLOUD_API_KEY locally}"
```

## WaveSpeedAI

Authenticated catalogue:

```bash
curl --fail-with-body --silent --show-error 'https://api.wavespeed.ai/api/v3/models' \
  -H "Authorization: Bearer ${WAVESPEED_API_KEY:?Set WAVESPEED_API_KEY locally}"
```

Image submission; the model ID belongs in the path:

```bash
curl --fail-with-body --silent --show-error 'https://api.wavespeed.ai/api/v3/wavespeed-ai/z-image/turbo' \
  -H "Authorization: Bearer ${WAVESPEED_API_KEY:?Set WAVESPEED_API_KEY locally}" \
  -H 'Content-Type: application/json' \
  --data '{"prompt":"A ceramic cup on a wooden table, soft morning light","size":"1024*1024"}'
```

Polling the original task:

```bash
curl --fail-with-body --silent --show-error \
  "https://api.wavespeed.ai/api/v3/predictions/${WAVE_PREDICTION_ID:?Use original data.id}/result" \
  -H "Authorization: Bearer ${WAVESPEED_API_KEY:?Set WAVESPEED_API_KEY locally}"
```

## OpenDesign Cloud

Set `OPENDESIGN_MEDIA_ORIGIN` to the dashboard's HTTPS API origin without `/v1` or a trailing slash.

Authenticated catalogue:

```bash
curl --fail-with-body --silent --show-error \
  "${OPENDESIGN_MEDIA_ORIGIN:?Use dashboard API origin}/api/v1/media/models" \
  -H "Authorization: Bearer ${OPENDESIGN_API_KEY:?Set OPENDESIGN_API_KEY locally}"
```

Speech submission; speech text and options are nested under `parameters`:

```bash
# New intended task: choose a new idempotency token. An exact retry must reuse it.
curl --fail-with-body --silent --show-error \
  "${OPENDESIGN_MEDIA_ORIGIN:?Use dashboard API origin}/api/v1/media/audio/speech" \
  -H "Authorization: Bearer ${OPENDESIGN_API_KEY:?Set OPENDESIGN_API_KEY locally}" \
  -H "Idempotency-Key: ${CLOUD_IDEMPOTENCY_KEY:?Choose a stable token for this submission}" \
  -H 'Content-Type: application/json' \
  --data '{"model":"elevenlabs-v3","voice":"JBFqnCBsd6RMkjVDRZzb","parameters":{"text":"Welcome to a quiet morning."}}'
```

Speech polling:

```bash
curl --fail-with-body --silent --show-error \
  "${OPENDESIGN_MEDIA_ORIGIN:?Use dashboard API origin}/api/v1/media/audio/tasks/${CLOUD_TASK_ID:?Use original task_id}" \
  -H "Authorization: Bearer ${OPENDESIGN_API_KEY:?Set OPENDESIGN_API_KEY locally}"
```

Video content redirects to another origin; download it without forwarding Cloud credentials, and never use `--location-trusted`.
