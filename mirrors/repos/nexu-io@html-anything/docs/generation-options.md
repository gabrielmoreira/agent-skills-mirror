# Generation options

Studio, external MCP callers and the embedded asset Agent receive the same optional `Model.generationOptions` from Model Gateway discovery. `shared/generation-options.ts` maintains exact provider/model profiles. The service validates known fields before queueing a new job; idempotent replay returns the original job. Unknown model IDs receive no guessed profile. Advanced JSON remains available for provider-specific fields, including custom FLUX image dimensions.

Quick controls override matching advanced fields; request parameters override saved model defaults. Unchanged fields are omitted and inherit saved/provider defaults. Studio preserves separate parameter drafts for each model while the creator is open. These drafts are not account settings. Returned jobs and asset versions record actual submitted parameters. Local Codex image preferences are appended to its instruction: they are creative requests, not guaranteed raster specifications.

## Maintained profiles

Checked on 2026-11-15 against the following official endpoint schemas and current adapters:

| Exact endpoint | Quick controls | Source |
| --- | --- | --- |
| `codex:image-generation` | Requested aspect ratio and background, delivered as prompt preferences | `gateway/agents.ts`, `gateway/service.ts` |
| `atlascloud:google/nano-banana-2/text-to-image` | Aspect ratio, resolution, format, thinking level, web search, seed | [Atlas schema](https://www.atlascloud.ai/docs/more-models/google/nano-banana-2-text-to-image/generateImage) |
| `atlascloud:bytedance/seedance-2.0/text-to-video` | Ratio, resolution, integer duration, audio, bitrate, seed | [Atlas schema](https://www.atlascloud.ai/docs/more-models/bytedance/seedance-2.0-text-to-video/generateVideo) |
| `atlascloud:suno/chirp-v4` | Instrumental-only and vocal gender; prompt remains an inspiration brief | [Atlas schema](https://www.atlascloud.ai/docs/more-models/suno/chirp-v4/generateAudio) |
| `fal:fal-ai/flux/schnell` | Image size, output count, format, seed | [fal schema](https://fal.ai/models/fal-ai/flux/schnell/api) |
| `fal:fal-ai/wan/v2.2-a14b/text-to-video` | Ratio, resolution, frames, frame rate, prompt expansion, negative prompt, seed | [fal schema](https://fal.ai/models/fal-ai/wan/v2.2-a14b/text-to-video/api) |
| `fal:fal-ai/kokoro/american-english` | Voice and speed; spoken input uses `prompt` | [fal schema](https://fal.ai/models/fal-ai/kokoro/american-english/api) |
| OpenDesign Cloud/account speech | Required voice ID | Current Cloud/account adapter contract |

These controls cover a maintained subset, not all models or all provider parameters. Custom model names and live catalogue labels do not establish wire compatibility. Provider-native types remain intact: Seedance duration is an integer, audio is a boolean, and Wan takes frames rather than a fabricated duration field. Local asset references remain limited to the implemented Codex image adapter. No local-upload support is inferred from a model accepting remote reference URLs.

The embedded Codex conversation separately exposes model selection and discovered reasoning efforts. Effort is passed as `turn/start.effort`, with `null` restoring the model default on subsequent turns. This field was checked against the installed Codex app-server JSON schema. Other Agents continue to use external MCP; selecting a local CLI in settings does not add an embedded runner.

## Interaction and validation

Generation settings use an anchored, non-modal popover with ratio tiles, selections, switches and bounded numeric controls. Known failures use the shared Toast layer. The asset navigation and creation pane have drag separators, keyboard arrows (Shift for larger steps), Home/End limits and double-click reset. Width preferences survive reloads; available content space bounds their rendered widths, and narrow creation uses the whole workspace.

Deterministic tests cover model discovery, invalid native parameter types, queued parameter identity, replay without another submission, Kokoro wire mapping, reasoning forwarding, JSON/control precedence and pane persistence/bounds. Browser inspection covers opened nested menus, actual drags, both themes and narrow layouts. Live paid generation, provider entitlement and human visual acceptance remain separate.
