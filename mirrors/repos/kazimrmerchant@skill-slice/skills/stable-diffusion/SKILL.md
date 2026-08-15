---
name: stable-diffusion
description: "Runs HuggingFace Diffusers pipelines for Stable Diffusion/SDXL/Flux: txt2img, img2img, inpainting, ControlNet, and LoRA adapters on local GPU. Use when generating or transforming images from Python Diffusers code. Not for ComfyUI node graphs (comfyui), Gradio LoRA Spaces (huggingface-lora-space-builder), or hosted DALL-E/Midjourney APIs."
version: 1.0.1
author: Orchestra Research
license: MIT
dependencies: [diffusers>=0.30.0, transformers>=4.41.0, accelerate>=0.31.0, torch>=2.0.0]
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Image Generation, Stable Diffusion, Diffusers, Text-to-Image, Multimodal, Computer Vision]
---

# Stable Diffusion Image Generation

Comprehensive guide to generating and transforming images with Stable Diffusion using the HuggingFace Diffusers library. Covers text-to-image, image-to-image, inpainting, ControlNet, LoRA adapters, and memory optimization.

## When to Use

**Use this skill when you need to:**
- Generate images from natural-language text prompts (text-to-image)
- Transform existing images with text guidance (image-to-image / style transfer)
- Fill masked regions of an image (inpainting)
- Apply spatial conditioning such as edges, poses, or depth maps (ControlNet)
- Load and blend LoRA style/character adapters
- Build custom diffusion pipelines or batch-generation workflows

**Trigger keywords:** stable diffusion, text-to-image, img2img, inpainting, ControlNet, LoRA, SDXL, SD 1.5, Flux, diffusers, generate image from prompt

**Use alternatives instead when:**
- **DALL-E 3** — API-based generation without local GPU
- **Midjourney** — artistic, stylized outputs via Discord
- **Imagen** — Google Cloud integration
- **Leonardo.ai** — web-based creative workflows

## Prerequisites

### Python environment

```bash
pip install "diffusers>=0.30.0" "transformers>=4.41.0" "accelerate>=0.31.0" "torch>=2.0.0"
pip install xformers  # Optional: memory-efficient attention (NVIDIA GPUs)
pip install pillow    # Image I/O
```

### Hardware

- **GPU**: NVIDIA CUDA GPU with ≥ 6 GB VRAM for SD 1.5; ≥ 12 GB for SDXL; ≥ 16 GB for Flux.
- **CPU-only**: Works but extremely slow. Use `enable_sequential_cpu_offload()` and reduce steps to 10–20.
- **Apple Silicon**: Use `torch.device("mps")` instead of `"cuda"`.

### Windows (PowerShell) notes

- Use `pip install` commands directly in PowerShell — no path changes needed.
- If you see `CUDA out of memory`, close other GPU processes (e.g., browser hardware acceleration) before retrying.
- Model checkpoints are cached under `C:\Users\<you>\.cache\huggingface\hub\`. Set `HF_HOME` to relocate if disk space is limited:

```powershell
$env:HF_HOME = "D:\hf_cache"
```

### Reference files

Load these when you need deeper context:

- **`references/advanced-usage.md`** — Load when building custom pipelines, fine-tuning, or deploying models to production.
- **`references/troubleshooting.md`** — Load when encountering CUDA OOM, black/noise images, slow generation, or dtype mismatch errors.

## Procedure

### 1. Basic text-to-image (SD 1.5)

```python
from diffusers import DiffusionPipeline
import torch

pipe = DiffusionPipeline.from_pretrained(
    "stable-diffusion-v1-5/stable-diffusion-v1-5",
    torch_dtype=torch.float16
)
pipe.to("cuda")

image = pipe(
    "A serene mountain landscape at sunset, highly detailed",
    num_inference_steps=50,
    guidance_scale=7.5
).images[0]

image.save("output.png")
```

### 2. High-quality generation (SDXL)

```python
from diffusers import AutoPipelineForText2Image
import torch

pipe = AutoPipelineForText2Image.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    torch_dtype=torch.float16,
    variant="fp16"
)
pipe.to("cuda")
pipe.enable_model_cpu_offload()

image = pipe(
    prompt="A futuristic city with flying cars, cinematic lighting",
    negative_prompt="blurry, low quality, distorted",
    height=1024,
    width=1024,
    num_inference_steps=30,
    guidance_scale=7.5
).images[0]

image.save("output_sdxl.png")
```

### 3. Swap scheduler for faster generation

```python
from diffusers import DPMSolverMultistepScheduler

pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)

image = pipe(prompt, num_inference_steps=20).images[0]
```

**Scheduler quick reference:**

| Scheduler | Steps | Quality | Use Case |
|-----------|-------|---------|----------|
| `EulerDiscreteScheduler` | 20–50 | Good | Default choice |
| `EulerAncestralDiscreteScheduler` | 20–50 | Good | More variation |
| `DPMSolverMultistepScheduler` | 15–25 | Excellent | Fast, high quality |
| `DDIMScheduler` | 50–100 | Good | Deterministic |
| `LCMScheduler` | 4–8 | Good | Very fast (with LCM LoRA) |
| `UniPCMultistepScheduler` | 15–25 | Excellent | Fast convergence |

### 4. Reproducible generation (fixed seed)

```python
import torch

generator = torch.Generator(device="cuda").manual_seed(42)

image = pipe(
    prompt="A cat wearing a top hat",
    generator=generator,
    num_inference_steps=50
).images[0]
```

### 5. Image-to-image

```python
from diffusers import AutoPipelineForImage2Image
from PIL import Image
import torch

pipe = AutoPipelineForImage2Image.from_pretrained(
    "stable-diffusion-v1-5/stable-diffusion-v1-5",
    torch_dtype=torch.float16
).to("cuda")

init_image = Image.open("input.jpg").resize((512, 512))

image = pipe(
    prompt="A watercolor painting of the scene",
    image=init_image,
    strength=0.75,  # 0 = no change, 1 = full reimagining
    num_inference_steps=50
).images[0]

image.save("output_img2img.png")
```

### 6. Inpainting

```python
from diffusers import AutoPipelineForInpainting
from PIL import Image
import torch

pipe = AutoPipelineForInpainting.from_pretrained(
    "runwayml/stable-diffusion-inpainting",
    torch_dtype=torch.float16
).to("cuda")

image = Image.open("photo.jpg")
mask = Image.open("mask.png")  # White = inpaint region, Black = keep

result = pipe(
    prompt="A red car parked on the street",
    image=image,
    mask_image=mask,
    num_inference_steps=50
).images[0]

result.save("output_inpaint.png")
```

### 7. ControlNet (spatial conditioning)

```python
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel
import torch

controlnet = ControlNetModel.from_pretrained(
    "lllyasviel/control_v11p_sd15_canny",
    torch_dtype=torch.float16
)

pipe = StableDiffusionControlNetPipeline.from_pretrained(
    "stable-diffusion-v1-5/stable-diffusion-v1-5",
    controlnet=controlnet,
    torch_dtype=torch.float16
).to("cuda")

# control_image = a Canny edge map, OpenPose skeleton, depth map, etc.
image = pipe(
    prompt="A beautiful house in the style of Van Gogh",
    image=control_image,
    num_inference_steps=30
).images[0]
```

**Available ControlNets:**

| ControlNet | Input Type | Use Case |
|------------|------------|----------|
| `canny` | Edge maps | Preserve structure |
| `openpose` | Pose skeletons | Human poses |
| `depth` | Depth maps | 3D-aware generation |
| `normal` | Normal maps | Surface details |
| `mlsd` | Line segments | Architectural lines |
| `scribble` | Rough sketches | Sketch-to-image |

### 8. LoRA adapters

```python
from diffusers import DiffusionPipeline
import torch

pipe = DiffusionPipeline.from_pretrained(
    "stable-diffusion-v1-5/stable-diffusion-v1-5",
    torch_dtype=torch.float16
).to("cuda")

# Load single LoRA
pipe.load_lora_weights("path/to/lora", weight_name="style.safetensors")
image = pipe("A portrait in the trained style").images[0]

# Adjust LoRA strength
pipe.fuse_lora(lora_scale=0.8)

# Unload when done
pipe.unload_lora_weights()
```

**Multiple LoRAs with weighted blending:**

```python
pipe.load_lora_weights("lora1", adapter_name="style")
pipe.load_lora_weights("lora2", adapter_name="character")

pipe.set_adapters(["style", "character"], adapter_weights=[0.7, 0.5])

image = pipe("A portrait").images[0]
```

### 9. Fast prototyping with LCM (4–8 steps)

```python
from diffusers import AutoPipelineForText2Image, LCMScheduler
import torch

pipe = AutoPipelineForText2Image.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    torch_dtype=torch.float16
).to("cuda")

pipe.load_lora_weights("latent-consistency/lcm-lora-sdxl")
pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config)
pipe.fuse_lora()

image = pipe(
    "A beautiful landscape",
    num_inference_steps=4,
    guidance_scale=1.0
).images[0]
```

### 10. Batch generation

```python
# Multiple prompts in one call
prompts = [
    "A cat playing piano",
    "A dog reading a book",
    "A bird painting a picture"
]
images = pipe(prompts, num_inference_steps=30).images

# Multiple images per prompt
images = pipe(
    "A beautiful sunset",
    num_images_per_prompt=4,
    num_inference_steps=30
).images
```

### 11. Memory optimization

Apply these in order of increasing aggressiveness:

```python
# 1. Model CPU offload — moves models to CPU when not in use (minimal speed impact)
pipe.enable_model_cpu_offload()

# 2. Sequential CPU offload — more aggressive, slower
pipe.enable_sequential_cpu_offload()

# 3. Attention slicing — compute attention in chunks
pipe.enable_attention_slicing()
# Or: pipe.enable_attention_slicing("max")

# 4. xFormers memory-efficient attention (requires xformers package)
pipe.enable_xformers_memory_efficient_attention()

# 5. VAE slicing/tiling for large images
pipe.enable_vae_slicing()
pipe.enable_vae_tiling()
```

### 12. Custom VAE and component loading

```python
from diffusers import DiffusionPipeline, AutoencoderKL

vae = AutoencoderKL.from_pretrained("stabilityai/sd-vae-ft-mse")

pipe = DiffusionPipeline.from_pretrained(
    "stable-diffusion-v1-5/stable-diffusion-v1-5",
    vae=vae,
    torch_dtype=torch.float16
)
```

### Generation parameters reference

| Parameter | Default | Description |
|-----------|---------|-------------|
| `prompt` | Required | Text description of desired image |
| `negative_prompt` | None | What to avoid in the image |
| `num_inference_steps` | 50 | Denoising steps (more = better quality) |
| `guidance_scale` | 7.5 | Prompt adherence (7–12 typical) |
| `height`, `width` | 512 / 1024 | Output dimensions (must be multiples of 8) |
| `generator` | None | Torch generator for reproducibility |
| `num_images_per_prompt` | 1 | Batch size |
| `strength` (img2img) | 1.0 | How much to transform (0–1) |

## Pitfalls

- **CUDA out of memory**: Always call `pipe.enable_model_cpu_offload()` before `pipe.to("cuda")` is redundant — use one or the other. If using `enable_model_cpu_offload()`, do NOT also call `.to("cuda")`. The offload hook manages device placement.
- **Black or noise images**: Often caused by dtype mismatch. Ensure the entire pipeline uses `torch.float16` consistently. If the safety checker destroys valid images, set `pipe.safety_checker = None` (only for trusted workflows).
- **Dimensions not multiples of 8**: The VAE requires height and width to be multiples of 8 (ideally 64 for SDXL). Non-conforming sizes cause runtime errors or corrupted latents.
- **SDXL `variant="fp16"` mismatch**: If the model repo does not have an `fp16` variant, passing `variant="fp16"` will fail. Check the model card or omit the argument.
- **LoRA scale too high**: `lora_scale` above 1.0 can produce burnt or oversaturated images. Keep between 0.5–1.0 for most adapters.
- **Inpainting mask format**: Mask must be a PIL Image where white (255) = region to inpaint and black (0) = region to keep. Grayscale or RGB both work, but ensure the resolution matches the input image.
- **ControlNet image size**: The control image must match the pipeline's target resolution. Resize before passing.
- **LCM requires LCM scheduler**: Loading LCM LoRA without swapping to `LCMScheduler` produces poor results. Always pair them.
- **`enable_sequential_cpu_offload()` is slow**: It moves individual layers to GPU one at a time. Use only when `enable_model_cpu_offload()` is insufficient.
- **Apple Silicon (MPS)**: Some operations are not yet supported on MPS. If you hit errors, fall back to CPU: `pipe.to("cpu")`.
- **Never delete model caches** under `~/.cache/huggingface/hub/` (or `C:\Users\<you>\.cache\huggingface\hub\`) without confirming — re-downloading multi-GB models is costly.

## Verification

### Verify installation

```bash
python -c "import diffusers; print(diffusers.__version__)"
python -c "import torch; print(torch.cuda.is_available())"
```

**Expected output:**
```
0.30.0  # or higher
True
```

### Verify basic generation

```python
from diffusers import DiffusionPipeline
import torch

pipe = DiffusionPipeline.from_pretrained(
    "stable-diffusion-v1-5/stable-diffusion-v1-5",
    torch_dtype=torch.float16
).to("cuda")

image = pipe("a red cube on a white table", num_inference_steps=10).images[0]
image.save("test_output.png")
print(f"Image size: {image.size}, mode: {image.mode}")
```

**Expected output:**
```
Image size: (512, 512), mode: RGB
```

### Verify file was saved (PowerShell)

```powershell
Test-Path .\test_output.png
(Get-Item .\test_output.png).Length
```

**Expected:** `True` and a file size > 0 (typically 50 KB – 2 MB for a PNG).

### Verify GPU memory usage

```python
import torch
print(f"Allocated: {torch.cuda.memory_allocated() / 1024**3:.2f} GB")
print(f"Reserved:  {torch.cuda.memory_reserved() / 1024**3:.2f} GB")
```

## Related skills

- **`references/advanced-usage.md`** — Custom pipelines, fine-tuning, deployment patterns. Load when extending beyond standard inference.
- **`references/troubleshooting.md`** — Detailed error resolution. Load when encountering runtime errors or quality issues.

## Resources

- **Documentation**: https://huggingface.co/docs/diffusers
- **Repository**: https://github.com/huggingface/diffusers
- **Model Hub**: https://huggingface.co/models?library=diffusers
- **Discord**: https://discord.gg/diffusers
