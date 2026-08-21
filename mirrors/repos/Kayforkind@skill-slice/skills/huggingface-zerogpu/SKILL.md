---
name: huggingface-zerogpu
description: "Builds and debugs Gradio Spaces on Hugging Face ZeroGPU: @spaces.GPU, python_version pins, requirements without pinning spaces, duration/quota, pickle process isolation, CUDA wheels, and concurrency. Use when writing or reviewing ZeroGPU Space code. Not for Docker, Static, or Streamlit Spaces or general Gradio layout; never put spaces in requirements.txt."
version: 1.0.1
---

# Hugging Face ZeroGPU

## When to Use

Use this skill when you are writing, reviewing, or debugging code for **Gradio SDK Spaces running on ZeroGPU hardware**. Trigger keywords and scenarios:

- Code uses `@spaces.GPU` decorator or `import spaces`
- Configuring `python_version` or `requirements.txt` for a ZeroGPU Space
- Handling ZeroGPU-specific constraints: pickle-based process isolation, CUDA availability model, concurrency defaults
- Tuning `duration` values or debugging `ZeroGPU illegal duration` / `ZeroGPU quota exceeded` errors
- Installing CUDA-dependent packages (e.g. `flash-attn`) on ZeroGPU
- Reasoning about cold-starts, worker reuse, or why returning CUDA tensors hangs

**Out of scope:** Docker Spaces, Static Spaces, Streamlit apps (now Docker), and general Gradio component/layout coding. For general Gradio, see the `huggingface-gradio` skill. Authoritative ZeroGPU docs: https://huggingface.co/docs/hub/spaces-zerogpu — always check for current backing GPU, runtime versions, and tier thresholds, which change over time.

## Prerequisites

- A Hugging Face account with a Space set to SDK **Gradio** and hardware **ZeroGPU**.
- `spaces` package available (installed by the Gradio SDK base image on every hardware tier — no special install needed locally).
- For local dev: Python matching the Space's pinned `python_version`.
- Windows host (PowerShell) is the primary development environment. Path notes below assume Windows when relevant.

## Reference Files

Load these references from the skill directory alongside this file when the indicated situation arises:

| Reference | When to read |
|-----------|--------------|
| `references/concurrency.md` | **Always** read alongside SKILL.md when writing ZeroGPU code — handlers run concurrently by default and silent corruption is the default failure mode. |
| `references/how-zerogpu-works.md` | When reasoning about cold-starts, worker reuse, why module-scope warmup does not carry to requests, or why returning CUDA tensors hangs. |
| `references/how-quota-works.md` | When choosing `duration` values, debugging `illegal duration` vs `quota exceeded`, explaining 24h quota windows, runs-per-day limits, or pay-as-you-go billing. |
| `references/cuda-and-deps.md` | When installing CUDA-dependent packages (e.g. `flash-attn`), pinning torch side-cars, reading wheel filename tags (`cu12torch2.X`, `cp3XX`, cxx11 ABI), or using the kernels-community fallback. |

## Procedure

### 1. Pin `python_version` in README frontmatter

Pinning is **effectively required** for ZeroGPU. The runtime default is currently Python 3.10; a local 3.11+ environment will fail to install without an explicit pin. Pin to a ZeroGPU-supported version (3.12 is a reasonable default). Do not hardcode the full supported list — refer to the docs.

```yaml
# README.md frontmatter
python_version: "3.12"
```

Both `"3.12"` and `"3.12.12"` forms are accepted.

### 2. Write `requirements.txt` — do NOT pin `spaces`

**HARD RULE: Do not include `spaces` in `requirements.txt`.** The Space platform pins its own `spaces` version; a conflicting pin causes pip resolution failure at build time.

- **Hand-written `requirements.txt`**: simply omit `spaces`.
- **uv** (`pyproject.toml`-managed): declare `spaces` in `pyproject.toml` so uv co-resolves transitive constraints (notably `psutil`, which `spaces` pins), then exclude it from the export:
  ```powershell
  uv export --no-hashes --no-dev --no-emit-package spaces -o requirements.txt
  ```
  Without `spaces` in `pyproject.toml`, uv cannot see its transitive constraints and may resolve incompatible versions at build time.
- **pip-tools / Poetry**: use the equivalent exclude mechanism.

### 3. Pin `torch` to match wheel tags

If installing a CUDA-dependent wheel via direct URL, the wheel filename encodes the `torch` major.minor it was built against (e.g. `cu12torch2.8`). Pin `torch==X.Y.Z` in `requirements.txt` to match — otherwise pip may resolve a different `torch` and the Space fails on first import. See `references/cuda-and-deps.md`.

### 4. Write the basic ZeroGPU pattern

```python
import spaces
import torch
from transformers import pipeline

pipe = pipeline("text-generation", model="...", device="cuda")

@spaces.GPU
def generate(prompt: str) -> str:
    return pipe(prompt, max_new_tokens=100)[0]["generated_text"]
```

Key rules:

1. **Instantiate models at module scope** and call `.to("cuda")` eagerly. ZeroGPU handles device mapping transparently.
2. **Decorate GPU functions with `@spaces.GPU`**. The decorator is a no-op outside ZeroGPU, so it is safe in all environments.
3. **Set `duration` to the realistic worst-case** (default 60s). The platform pre-checks `requested duration` against `remaining quota` — not actual run time — so a 10s task left at 60s fails with `quota exceeded` once the user's remaining quota drops below 60s. Smaller `duration` also ranks higher in the node-level queue.
4. **`torch.compile` is NOT supported.** Use PyTorch [ahead-of-time compilation (AoTI)](https://huggingface.co/blog/zerogpu-aoti) (torch 2.8+) instead.
5. **Use `size="xlarge"` sparingly.** It allocates the full backing GPU but costs 2x quota and tends to queue longer.

```python
@spaces.GPU(duration=120)
def generate_image(prompt: str):
    return pipe(prompt).images[0]
```

### 5. Follow the CUDA availability model

Real GPU access is **only** available inside `@spaces.GPU`-decorated functions. Outside those functions, the GPU is not attached to the process.

`import spaces` **monkey-patches `torch`** so that:
- `torch.cuda.is_available()` returns `True` globally.
- `.to("cuda")` / `device="cuda"` calls at module scope succeed without error.

This is intentional: module-scope `model.to("cuda")` registers tensors with the ZeroGPU backend, which writes them to a disk offload directory at startup ("pack" step) and frees RAM. When a `@spaces.GPU` call lands, a forked GPU worker streams weights from disk into VRAM via pinned memory. Warm workers keep weights resident and skip the disk→VRAM step.

| Action | Where | Why |
|--------|-------|-----|
| `model.to("cuda")` / `pipe(..., device="cuda")` | **Module scope** | ZeroGPU registers the tensor and manages device migration |
| Actual CUDA computation (inference, kernels) | **Inside `@spaces.GPU`** | Real GPU is only attached during the decorated call |
| Branching on `torch.cuda.is_available()` | Avoid relying on it | Always returns `True` due to the monkey-patch |

**Do not run inference or CUDA kernels at module scope** — the real GPU is not attached, so operations silently run on CPU or fail.

The standard device-selection idiom remains correct:

```python
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = AutoModel.from_pretrained("...").to(device)
```

Do not hardcode `device="cuda"` — it breaks on CPU-only environments.

### 6. Load models eagerly at module scope

Load models at module scope, not lazily on first request. The Space process starts before any user arrives, so cold-start cost is paid once. Lazy loading (`global model; if model is None: ...`, `@lru_cache` wrappers, factory functions) just pushes that cost onto the first user.

### 7. Import `spaces` unconditionally — no try/except fallback

**Do not** wrap `import spaces` in `try/except` and redefine `spaces.GPU` as a no-op fallback. Off-ZeroGPU, the real `spaces` package is already a true no-op:

- Heavyweight behavior (CUDA monkey-patching, client init, startup hooks) is gated on the `SPACES_ZERO_GPU` env var, set only on ZeroGPU.
- `@spaces.GPU` returns the undecorated function unchanged off-ZeroGPU.
- Top-level `import spaces` performs only lightweight imports.

The Gradio SDK base image installs `spaces` on every hardware tier, so duplicating a Space onto dedicated GPU or CPU needs no code changes.

**Anti-pattern (do not do this):**

```python
try:
    import spaces
except ImportError:
    class spaces:  # type: ignore
        @staticmethod
        def GPU(func=None, **kwargs):
            return func if func else (lambda f: f)
```

Problems: (1) the fallback must mimic every `@spaces.GPU` call shape and drifts as the API grows; (2) it hides `spaces` from `requirements.txt` even though the Space needs it at deploy time; (3) it solves a non-problem — the real package is already a no-op locally.

**Do this instead:**

```python
import spaces

@spaces.GPU
def generate(prompt: str) -> str:
    ...
```

### 8. Tune `duration` and quota

Three things happen when you declare `@spaces.GPU(duration=N)`:

1. **Tier-max check** — each visitor tier has a per-call `duration` cap. Declaring above the cap fails immediately with `ZeroGPU illegal duration`, regardless of remaining quota. (Tier numbers change — see the docs.)
2. **Quota pre-check** — the platform compares `requested duration` against `remaining quota`. If `remaining < requested`, the call fails with `ZeroGPU quota exceeded` — even if actual work would have fit. The error shows explicit numbers, e.g. `"60s requested vs. 30s left"`.
3. **Queue priority** — the queue is node-level (all Spaces on the same node compete), and shorter declared `duration` ranks higher.

All three favor declaring the smallest realistic `duration` — including for short tasks. Explicit `@spaces.GPU(duration=15)` on a 10s task avoids premature `quota exceeded` and ranks higher.

> **`xlarge` doubles the request.** `requested = N * 2` when `size="xlarge"`, for both the tier-max check and quota pre-check. So `@spaces.GPU(duration=60, size="xlarge")` is internally a 120s request.

**Dynamic duration for variable workloads** — pass a callable that estimates per request:

```python
def estimate_duration(prompt, steps):
    return int(steps * 3.5)

@spaces.GPU(duration=estimate_duration)
def generate(prompt, steps):
    return pipe(prompt, num_inference_steps=steps).images[0]
```

For full distinction between `illegal duration` vs `quota exceeded`, runs-per-day limits, the 24h quota window, and pay-as-you-go billing, see `references/how-quota-works.md`.

### 9. Handle process isolation and pickle

`@spaces.GPU`-decorated functions run in a **separate process** managed by the ZeroGPU scheduler. Arguments and return values cross the boundary via **pickle serialization**.

Consequences:

- **Only picklable objects** can be passed in or returned. Open file handles, DB connections, locks, lambdas, and closures over unpicklable state raise `PicklingError`.
- **Do NOT return CUDA tensors directly.** Unpickling a CUDA tensor in the main process triggers `torch.cuda._lazy_init()`, which ZeroGPU blocks. Convert to CPU first: return `tensor.cpu()` or `tensor.cpu().numpy()`.
- CPU tensors, numpy arrays, PIL Images, and plain Python objects work fine.
- Large objects incur serialization overhead. Prefer lightweight returns (tensors, arrays, file paths, base64 strings) over complex object graphs.

**`gr.State` semantics across the boundary:**

Because handlers run in a separate process, `gr.State` values are **pickled on every yield** — they are NOT shared by reference.

- The generator receives a **copy** of the state (`id()` differs from the caller's).
- In-place mutations inside the generator are **invisible** to other handlers until the mutated state is explicitly yielded back.
- Yielding `gr.update()` for a `gr.State` slot **skips the update** — other handlers continue to see the pre-yield value.
- Each yield that returns the state object creates a **new copy** via pickle.

Practical guidance:
- **Do NOT assume reference semantics for `gr.State`** on ZeroGPU. Code that mutates state in a generator and expects another handler to see those mutations will silently use stale data.
- **Every yield including a `gr.State` value triggers a full pickle round-trip.** For large state, minimize how often you yield it — ideally once at the end. Use `gr.update()` for the state slot on intermediate yields.
- **CUDA tensors inside state must be moved to CPU before yielding** — same `torch.cuda._lazy_init()` issue.

### 10. Enforce concurrency safety

Handlers run **concurrently by default** on ZeroGPU. This is not opt-in. Code that worked in single-user testing can silently corrupt or leak data in production. **Always read `references/concurrency.md` before writing ZeroGPU code.**

Three rules:

1. **No mutable global state.** Concurrent requests overwrite each other.
2. **No fixed file paths for outputs.** Concurrent requests clobber the same file. Use `tempfile` for unique paths.
3. **Read-only globals are safe.** Model objects, tokenizers, configs loaded once at startup and only read during requests are safe and encouraged.

### 11. Choose call granularity — decorate the outer loop

Each entry into a `@spaces.GPU` function carries non-trivial cost: pickle round-trip, worker warm-up, CUDA re-attach, and a fresh pass through the node-level queue. Calling a decorated function from inside a hot loop multiplies these costs and adds a failure mode: a later iteration may fail to acquire a GPU slot, stalling the job mid-way.

```python
# Avoid — N GPU entries for N frames
def process_video(frames):
    return [process_frame(f) for f in frames]

@spaces.GPU(duration=...)
def process_frame(frame):
    ...

# Prefer — one GPU entry for the whole video
@spaces.GPU(duration=...)
def process_video(frames):
    return [process_frame(f) for f in frames]

def process_frame(frame):
    ...
```

If the loop mixes heavy CPU work with GPU work, wrapping the whole loop charges CPU time against the user's quota. Batching GPU work so CPU pre/post-processing stays outside the decorator is a situational optimization — not the default.

### 12. Install CUDA-dependent packages from pre-built wheels only

HF Spaces builds Docker images in a CPU-only environment. **On ZeroGPU, the build phase has no `nvcc`** because the base image is `python:3.13` (dedicated-GPU Spaces use `nvidia/cuda:*-devel-*` and have `nvcc` at build time). A CUDA-dependent package whose only distribution is sdist — e.g. bare `flash-attn` — cannot be installed via `requirements.txt` on ZeroGPU. **Only pre-built wheels work.**

ZeroGPU **runtime** does have `nvcc` available, mounted from a CUDA devel image at `/cuda-image` since 2025-07 (originally added for AoTI support). This makes `torch.export` / AoTI workflows possible inside `@spaces.GPU` calls.

**Bottom line:** install every CUDA-dependent package from a pre-built wheel. If no wheel is on PyPI, build one externally (e.g. host on HF Hub) and pin the URL. For `flash-attn`, the upstream releases page ships a fairly complete wheel matrix covering most Python × CUDA × torch combinations.

For wheel-tag reading (cxx11 ABI, `cu12torch2.X`, `cp3XX`), torch-family side-car drift, and the kernels-community fallback, see `references/cuda-and-deps.md`.

### 13. Configure `gr.Examples` caching for ZeroGPU

`gr.Examples` behavior is environment-dependent. On ZeroGPU specifically:

- `cache_examples` defaults to `True` (Spaces sets `GRADIO_CACHE_EXAMPLES=true`).
- `cache_mode` defaults to `"lazy"` (Spaces sets `GRADIO_CACHE_MODE=lazy` only on ZeroGPU).

ZeroGPU defaults to `lazy` because eager caching pre-runs every example at startup, but ZeroGPU has **no GPU attached at startup** — only during request handling. Eager caching of GPU-bound examples would fail.

When `cache_examples=True`, the `run_on_click` / `run_examples_on_click` parameter is silently ignored. If your app relies on click-populates-only behavior, set `cache_examples=False` explicitly.

To reproduce ZeroGPU example-caching behavior locally (PowerShell):

```powershell
$env:GRADIO_CACHE_EXAMPLES="true"; $env:GRADIO_CACHE_MODE="lazy"; python app.py
```

## Hardware

ZeroGPU exposes two GPU sizes that map to a fraction of the backing card:

| `size` | Slice of backing GPU | Quota cost |
|--------|----------------------|------------|
| `large` *(default)* | Half | 1x |
| `xlarge` | Full | 2x |

Default `large` gives half a physical GPU, so memory bandwidth and compute are significantly lower than the full card's specs. Use `xlarge` only when the workload genuinely needs the extra memory or compute.

> **Backing GPU changes without notice.** ZeroGPU has already migrated across GPU generations several times; older write-ups may name A100 or H200, but those are outdated. For the current backing GPU and exact per-size VRAM, always check the [ZeroGPU docs](https://huggingface.co/docs/hub/spaces-zerogpu) before sizing workloads.

## Pitfalls

- **Returning CUDA tensors hangs.** Unpickling a CUDA tensor in the main process triggers `torch.cuda._lazy_init()`, which ZeroGPU blocks. Always return `tensor.cpu()` or `tensor.cpu().numpy()`.
- **Default `duration=60` blocks low-quota users.** A 10s task left at 60s fails with `quota exceeded` once remaining quota drops below 60s. Always set `duration` to the realistic worst case.
- **`torch.compile` is NOT supported.** Use AoTI (torch 2.8+) instead.
- **`spaces` in `requirements.txt` breaks the build.** The platform pins its own `spaces` version. Omit it from `requirements.txt`; for uv, use `--no-emit-package spaces`.
- **Missing `python_version` pin.** Runtime default is 3.10; a local 3.11+ env fails to install without an explicit pin.
- **`try/except import spaces` fallback.** The real package is already a no-op off-ZeroGPU. The fallback drifts from the real API and hides `spaces` from dependencies.
- **Mutable global state under concurrency.** Handlers run concurrently by default; concurrent requests overwrite each other silently.
- **Fixed file paths for outputs.** Concurrent requests clobber the same file. Use `tempfile`.
- **`gr.State` reference semantics assumed.** State is pickled on every yield; in-place mutations are invisible until explicitly yielded back. Yielding `gr.update()` for a state slot skips the update.
- **Decorating per-iteration instead of outer loop.** N GPU entries for N items multiplies cost and risks mid-job slot-acquisition failure.
- **Bare `flash-attn` (sdist) in `requirements.txt`.** ZeroGPU build phase has no `nvcc`; only pre-built wheels work.
- **Hardcoding `device="cuda"`.** Breaks on CPU-only environments. Use the `torch.cuda.is_available()` idiom.
- **Lazy model loading.** Pushes cold-start cost onto the first user. Load eagerly at module scope.
- **Relying on `torch.cuda.is_available()` for branching.** Always returns `True` on ZeroGPU due to the monkey-patch.
- **Eager `gr.Examples` caching.** ZeroGPU has no GPU at startup; `cache_mode` defaults to `lazy` for this reason. If relying on click-populates-only, set `cache_examples=False`.

## Verification

1. **`python_version` is pinned** in README frontmatter:
   ```powershell
   Select-String -Path README.md -Pattern 'python_version'
   ```
   Expected: a line like `python_version: "3.12"`.

2. **`spaces` is NOT in `requirements.txt`:**
   ```powershell
   Select-String -Path requirements.txt -Pattern '^\s*spaces\s*='
   ```
   Expected: no matches.

3. **`torch` is pinned to match any direct-URL CUDA wheel tags** (e.g. if wheel says `cu12torch2.8`, `torch==2.8.*` must be pinned):
   ```powershell
   Select-String -Path requirements.txt -Pattern 'torch=='
   ```

4. **Every GPU function is decorated** — grep for functions doing inference and confirm `@spaces.GPU` is present:
   ```powershell
   Select-String -Path app.py -Pattern '@spaces\.GPU'
   ```

5. **No CUDA tensors returned** — check return statements inside `@spaces.GPU` functions for `.cpu()` or `.numpy()`:
   ```powershell
   Select-String -Path app.py -Pattern 'return.*\.cuda\(\)'
   ```
   Expected: no matches (returning raw CUDA tensors is a bug).

6. **No `try/except import spaces` fallback:**
   ```powershell
   Select-String -Path app.py -Pattern 'except ImportError.*spaces'
   ```
   Expected: no matches.

7. **No mutable global state written inside handlers** — review any global assignment inside `@spaces.GPU` functions. Read-only globals (models, tokenizers) are fine.

8. **No fixed output file paths** — handlers should use `tempfile`:
   ```powershell
   Select-String -Path app.py -Pattern 'tempfile'
   ```

9. **Local ZeroGPU example-caching behavior reproducible:**
   ```powershell
   $env:GRADIO_CACHE_EXAMPLES="true"; $env:GRADIO_CACHE_MODE="lazy"; python app.py
   ```
   App should start without attempting GPU work at startup.

10. **Duration is explicitly set** on every `@spaces.GPU` decorator (not relying on the 60s default for short tasks):
    ```powershell
    Select-String -Path app.py -Pattern '@spaces\.GPU\(duration='
    ```

## Related Skills

- `huggingface-gradio` — general Gradio components, layouts, and event listeners (non-ZeroGPU Gradio coding).

## Limitations

- Use this skill only when the task clearly matches ZeroGPU on Gradio SDK Spaces.
- Verify commands, API behavior, pricing, quotas, credentials, and deployment effects against current official documentation before making changes.
- Do not treat generated examples as a substitute for environment-specific tests, security review, or user approval for destructive or costly actions.
