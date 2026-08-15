---
name: huggingface-lora-space-builder
description: "Publishes a Gradio Hugging Face Space that runs inference with a user-provided LoRA on ZeroGPU (diffusers pipelines for Qwen-Image, LTX, FLUX, SDXL, and similar). Use when the user wants a browser demo or playground for a LoRA. Not for training LoRAs, local Diffusers scripts (stable-diffusion), or ComfyUI graphs (comfyui)."
version: 1.0.1
risk: unknown
source: https://github.com/huggingface/skills/tree/main/skills/huggingface-lora-space-builder
source_repo: huggingface/skills
source_type: official
date_added: 2026-07-01
license: Apache-2.0
license_source: https://github.com/huggingface/skills/blob/main/LICENSE
---

# Gradio LoRA Space Builder

## When to Use

Use this skill when you need to build and publish a Gradio demo on Hugging Face Spaces that runs inference with a user-provided LoRA. Use whenever someone asks to create, generate, ship, or publish "a Space", "a demo", "a Gradio app", or "a playground" for a LoRA — whether the base model is Qwen-Image, Qwen-Image-Edit, LTX, Wan, FLUX, SDXL, or another diffusion model. The default target is ZeroGPU hardware and the default inference library is `diffusers` when the base model supports it.

The output is a real, published Space (private by default) that the user can try in the browser, not a local script.

## Prerequisites

- A Hugging Face account.
- A Hugging Face access token with **write** scope (to read the LoRA if it's private/gated, and to publish the Space). Create one at `https://huggingface.co/settings/tokens`.
- Python environment with `huggingface_hub`, `gradio`, and `diffusers` installed for local smoke-testing.

## Procedure

Work through these phases in order. Information gathered in one phase decides the next. Don't drip-feed questions across multiple turns; batch them.

### Phase 1: Gather LoRA Info

1. **Check for cached token first.** Do not immediately ask for a token. Check if the user is already authenticated.
   ```python
   from huggingface_hub import HfApi, get_token

   cached_token = get_token()  # picks up HF_TOKEN env var or cached CLI login
   if cached_token:
       try:
           info = HfApi().whoami(token=cached_token)
           username = info["name"]
       except Exception:
           cached_token = None  # token exists but is invalid/expired
   ```
2. **Ask for token only if needed.** If no cached token exists or it can't read a private repo, ask once: "I need a Hugging Face access token with **write** scope (to read the LoRA if it's private/gated, and to publish the Space). Create one at https://huggingface.co/settings/tokens. Paste it here."
3. **Read the LoRA repo.** List files (`HfApi().list_repo_files(repo_id)`) and fetch the model card (`ModelCard.load(repo_id)`).
4. **Pick the LoRA weights file.** If multiple `.safetensors` files exist: README-recommended file wins, then `pytorch_lora_weights.safetensors`, then latest training checkpoint, otherwise ask. See `references/zerogpu-and-publishing.md`.
5. **Extract metadata.** Determine base model, task (`text-to-image`, `image-to-image`, `text-to-video`, `image-to-video`, `video-to-video`), trigger words, recommended inference recipe (steps, guidance, CFG, LoRA scale, resolution), example prompts/media, and sub-task.
6. **Batch questions.** If something can't be inferred, ask the user in a single batched message.

### Phase 2: Pick the Base Pipeline

1. **Load the reference file for the base model family:**
   - `references/base-models/qwen-image.md` (Qwen-Image, Qwen-Image-Edit)
   - `references/base-models/ltx.md` (LTX family)
   - `references/base-models/krea-2.md` (Krea 2)
   If the base model isn't listed, tell the user and ask whether to proceed by analogy or stop. Don't guess silently.
2. **Verify the pipeline class against the base model's card.** This is mandatory. Fetch the base model card and read its diffusers snippet to confirm the pipeline class.
   ```python
   from huggingface_hub import ModelCard
   base_card = ModelCard.load(base_model_id)
   # Read base_card.text — find the diffusers inference snippet, note the pipeline class it imports.
   ```
   - Example: `Qwen-Image-Edit` uses `QwenImageEditPipeline`. `Qwen-Image-Edit-2509` and `Qwen-Image-Edit-2511` use `QwenImageEditPlusPipeline` — different class, different default parameters, takes a list of images instead of one.
3. **Diffusers vs native.** Default to `diffusers` when a pipeline class exists. Some LTX variants need native pipelines; see `references/base-models/ltx.md`.

### Phase 3: Design the UI

1. **Read task patterns.** Load `references/tasks.md` for baseline UI patterns (T2I, I2I, T2V, I2V, V2V).
2. **Adapt to the LoRA.** Load `references/adapting-to-the-lora.md`. Reason from the LoRA's task and inputs to a UI. Don't use a generic template.
3. **Self-check.** Write one sentence describing what a user does in 10 seconds. If it doesn't distinguish this LoRA from others of the same task, the UI isn't shaped enough.
4. **Gradio components.** Check current Gradio docs (`https://www.gradio.app/docs`) for newer components like `gr.ImageSlider` or `@gr.render`.
5. **Creative mode.** If the input shape demands custom HTML/JS, load `references/creative-mode.md` for primitives and pitfalls. Don't skip Hub custom components (e.g. `gradio_image_annotation`) before going fully bespoke.
6. **Examples.** Use `gr.Examples` with media from the LoRA repo or shared input pools (`linoyts/repo-to-space-example-inputs`, `linoyts/repo-to-space-example-videos`). Set `cache_examples=True, cache_mode="lazy"`.

### Phase 4: Write the Space Files

Write `app.py`, `requirements.txt`, and `README.md` together. Show all three to the user for one batched approval before publishing. Load `references/zerogpu-and-publishing.md` for ZeroGPU rules.

1. **`app.py`:**
   - Imports: `gradio as gr`, `torch`, `spaces`, pipeline class, preprocessing needs.
   - Constants: `LORA_REPO`, `BASE_MODEL`, recommended steps, guidance, LoRA scale, trigger word.
   - Module-level model load: `from_pretrained`, `.to("cuda")`, `load_lora_weights`. Pass `token=os.environ["HF_TOKEN"]` if private.
   - Preprocessing: CPU code at module level, GPU code inside `@spaces.GPU`.
   - Inference function: Decorated with `@spaces.GPU(duration=...)`. Validate inputs (`gr.Error`), apply trigger word, return outputs + seed. Use `gr.Progress(track_tqdm=True)`.
   - Gradio Blocks: Wire UI to inference.
2. **`requirements.txt`:** Derive from actual needs:
   - Include: Every top-level non-stdlib import in `app.py`, base-model reference "Required dependencies", LoRA card explicit mentions, and `diffusers`, `transformers`, `accelerate`, `peft`, `safetensors`. Use `git+https://github.com/huggingface/diffusers` if needed.
   - **DO NOT list:** `gradio` (controlled by `sdk_version` in README), `torch`, `spaces`, `huggingface_hub` (provided by runtime).
   - **DO NOT reflexively add:** `xformers`, `flash-attn` (cause issues on ZeroGPU).
   - Bias: Include rather than skip when uncertain (except for the above).
3. **`README.md`:** YAML frontmatter must set SDK version, hardware (`zero-a10g`), and Space title.

### Phase 5: Publish the Space

1. **Create repo (private by default).**
   ```python
   from huggingface_hub import HfApi
   api = HfApi(token=hf_token)
   repo_id = f"{username}/{space_name}"
   api.create_repo(repo_id=repo_id, repo_type="space", space_hardware="zero-a10g", private=True)
   ```
   - If 403 on `create_repo` with `space_hardware="zero-a10g"`: User isn't PRO. Retry without `space_hardware`, leave it in README YAML.
2. **Set Space secret.**
   ```python
   api.add_space_secret(repo_id=repo_id, key="HF_TOKEN", value=HF_TOKEN)
   ```
3. **Upload files.** `api.upload_file` for `app.py`, `requirements.txt`, `README.md`.
4. **Do not upload LoRA weights.** Pull from Hub at runtime.

### Phase 6: Smoke-test the Space

1. **Wait for build.** Poll `HfApi().get_space_runtime(repo_id).stage` until `RUNNING`.
   ```python
   import time
   from huggingface_hub import HfApi
   api = HfApi(token=hf_token)
   while True:
       stage = api.get_space_runtime(repo_id).stage
       if stage == "RUNNING": break
       if stage in {"BUILD_ERROR", "RUNTIME_ERROR", "CONFIG_ERROR"}:
           raise RuntimeError(f"Build failed: {stage}. Logs: https://huggingface.co/spaces/{repo_id}/logs/container")
       time.sleep(15)
   ```
2. **Verify endpoint.** `gradio info {repo_id} --token {hf_token}`
3. **Run inference.** `gradio predict {repo_id} /predict '{"prompt": "..."}' --token $env:HF_TOKEN` (PowerShell syntax for env var).
4. **Creative mode caveat.** If using custom JS, open the Space URL in a browser to verify interaction.

## Pitfalls

- **Generic template:** Don't use a one-size-fits-all demo. Tailor to the LoRA.
- **Lazy-loading model:** Load models at module level, not inside the GPU function. ZeroGPU requires this for speed and error visibility.
- **`torch.compile`:** Not supported on ZeroGPU. Do not use.
- **`cache_examples`:** Use `cache_examples=True, cache_mode="lazy"`. Plain `True` fails on ZeroGPU build.
- **Uploading LoRA weights:** Never upload weights into the Space repo. Pull from Hub at runtime.
- **Token timing:** Don't ask for the HF token only at the end. Check early if the LoRA is private.
- **Over-exposing controls:** Pick only the 1-3 controls that matter for the LoRA.
- **Wrong pipeline class:** Always verify against the base model card. `QwenImageEditPipeline` vs `QwenImageEditPlusPipeline` is a real failure mode.
- **Missing transitive deps:** e.g., `torchvision` for Qwen-Image. Derive `requirements.txt` mechanically.
- **`xformers`/`flash-attn`:** Do not add reflexively; they cause problems on ZeroGPU.
- **Publish-time YAML error:** `short_description` too long (max ~60 chars).
- **403 on create_repo:** User not on PRO. Retry without `space_hardware`.

## Verification

- **Build status:** Poll `api.get_space_runtime(repo_id).stage` until `RUNNING`. Check logs at `https://huggingface.co/spaces/{repo_id}/logs/container` if it fails.
- **Endpoint signature:** Run `gradio info {repo_id} --token {hf_token}` and confirm parameters match `app.py`.
- **Inference test:** Run `gradio predict {repo_id} /predict '{...}' --token {hf_token}`. Confirm output is plausible.
- **Creative mode:** Manually test custom JS in a browser.
- **Interpret results:**
  - 503 / sleeping: `api.restart_space(repo_id)` and retry.
  - `weight_name` error: Re-check `list_repo_files`, fix `weight_name=`.
  - Missing pipeline class: Switch `diffusers` to git main in `requirements.txt`.
  - `ImportError`: Add missing dep to `requirements.txt`.
  - OOM: Reduce resolution or steps.
  - Timeout: Bump `@spaces.GPU(duration=...)`.
