---
name: seedance-2-5
description: |
  Generate 4-30 second cinematic video with ByteDance Seedance 2.5 through fal.ai, Volcengine Ark, Runway, or ComfyUI Partner Nodes. Use for long single generations, synchronized audio, and large multimodal reference sets (up to 30 images, 10 videos, and 10 audio clips).
---

# Seedance 2.5

Seedance 2.5 extends the Seedance 2 family to 4–30 second 480p/720p clips and
larger multimodal reference sets. It is hosted; there are no local model
weights in OpenMontage.

## Choose a supported route

| Route | Tool call | Notes |
|-------|-----------|-------|
| fal.ai | `seedance_video`, `model_version: "2.5"` | T2V, I2V, and reference-to-video |
| Volcengine Ark | `seedance_ark`, `model: "2.5"` | First-party model ID `doubao-seedance-2-5-260628`; custom token price required for cost estimates |
| Runway | `runway_video`, `model: "seedance2_5"` | T2V, I2V, V2V; 480p/720p |
| ComfyUI Partner Node | `comfyui_video`, `model_family: "seedance_2.5"` | Hosted and paid despite running in a ComfyUI graph |

Do not invent a Replicate, HeyGen, or Higgsfield identifier when their current
public API schema does not list Seedance 2.5.

## Reference limits

- Up to 30 reference images.
- Up to 10 reference videos.
- Up to 10 reference audio clips.
- Keep combined reference video/audio duration within the provider's documented
  ceiling; Runway caps it at 30 seconds.
- For Runway video-to-video, the source video consumes one video slot.

Reference inputs are provider-specific. fal.ai uses `image_urls`, `video_urls`,
and `audio_urls` internally. Runway uses `references`, `referenceVideos`, and
`referenceAudio`. Ark uses typed content entries with roles. Always call the
OpenMontage tool instead of constructing a provider payload manually.

## Prompting

Lead with the shot structure, then subject, action, camera, lighting, and audio.
For multi-shot work, give each beat an explicit time range and use quoted text
for dialogue. Reference each supplied asset by a stable role in the prompt.
Thirty seconds is a ceiling, not a target: use a shorter generation when the
scene has only one meaningful action.

## Cost and verification

All supported routes are paid. Confirm the exact provider/model before calling
and review the result for identity continuity, cuts, lip sync, audio artifacts,
and prompt adherence. ComfyUI Partner Nodes use prepaid Comfy credits and are
not an offline fallback.
