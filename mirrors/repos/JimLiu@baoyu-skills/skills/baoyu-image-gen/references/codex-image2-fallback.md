---
name: codex-image2-fallback
description: Fallback behavior when OpenAI API credentials are absent but Codex/native image generation is available
---

# Codex Image2 Fallback

The `openai` provider can fail with:

```text
OPENAI_API_KEY is required. Codex/ChatGPT desktop login does not automatically grant OpenAI Images API access to this script.
```

This is expected. The `openai` provider uses the public OpenAI Images API and needs `OPENAI_API_KEY`. Codex / ChatGPT image2 entitlement is a separate runtime-native path.

## Practical fallback pattern

1. Try this skill when provider credentials are available.
2. If it fails only because `OPENAI_API_KEY` is missing, do not leave the user waiting.
3. Prefer a Codex/native raster backend in this order:
   - Codex runtime native `imagegen` skill/tool, if available.
   - Repo-level `scripts/codex-imagegen.sh`, if `codex` CLI is installed/logged in and the calling skill supports the wrapper.
   - Hermes native `image_generate`, if available.
4. Be transparent about reference-image behavior:
   - If the fallback backend accepts references, pass the reference images.
   - If it does not, derive a concise identity-preserving prompt from the references and state that it is a text-description fallback, not strict reference-image editing.
5. Return the generated media path or structured backend error promptly.
