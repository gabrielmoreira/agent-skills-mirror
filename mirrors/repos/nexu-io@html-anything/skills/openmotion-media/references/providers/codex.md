# Local Codex images

Codex generates images through the user's own local Codex CLI and its built-in image generation tool. OpenMotion invokes the installed CLI; it never reads, copies or refreshes Codex credentials, and it does not charge OpenDesign credits. Usage counts against the user's Codex plan.

`openmotion_media_use` `action=inspect` lists provider `codex` once the local Codex CLI is signed in. It is usable (`available: true`) only when Codex is signed in (`codex login`), the `image_generation` feature is enabled and the CLI supports ephemeral `exec`; otherwise its `reason` names the missing step. Selecting Codex in **Settings → Model providers** does not change these requirements.

Codex exposes one built-in image model, `image-generation` (Codex Image). Confirm it with `action=models, provider=codex`; other models cannot be added. Generate a new image with `openmotion_assets_use`:

```json
{"action":"generate","requestId":"codex-image-one","model":"codex:image-generation","modality":"image","prompt":"A ceramic cup on a linen tablecloth"}
```

To edit an image, add exactly one pinned `references` entry (`assetId` and `versionId`) of a PNG, JPEG or WebP image; the original asset is not modified. Codex does not generate video, speech or music, and it takes no size, quality or aspect-ratio parameters: describe framing in the prompt. The project-direct `openmotion_media_use` `generate` route does not accept Codex.

A run can take several minutes and stops after ten. Poll the original job as the [job procedure](../jobs.md) describes. Failures report the Codex service message when one is available; do not resubmit automatically.
