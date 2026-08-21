---
name: llama-cpp
description: "Runs local GGUF inference with llama.cpp (llama-cli, llama-server, optional llama-cpp-python) on CPU, Metal, CUDA, ROCm, or Intel GPU, including Hugging Face -hf Hub downloads. Use when the user wants llama.cpp, GGUF files, llama-cli, or llama-server. Not for Ollama install/serve (ollama-local-setup) or Ollama Cloud GLM (ollama). Never treat mmproj-*.gguf projector files as the main weights."
version: 2.1.3
license: MIT
dependencies: [llama-cpp-python>=0.2.0]
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [llama.cpp, GGUF, Quantization, Hugging Face Hub, CPU Inference, Apple Silicon, Edge Deployment, AMD GPUs, Intel GPUs, NVIDIA, URL-first]
---

# llama.cpp + GGUF

Use this skill for local GGUF inference, quant selection, or Hugging Face repo discovery for llama.cpp.

## When to Use

- Run local models on CPU, Apple Silicon, CUDA, ROCm, or Intel GPUs.
- Find the right GGUF for a specific Hugging Face repo.
- Build a `llama-server` or `llama-cli` command from the Hub.
- Search the Hub for models that already support llama.cpp.
- Enumerate available `.gguf` files and sizes for a repo.
- Decide between Q4/Q5/Q6/IQ variants for the user's RAM or VRAM.

## Prerequisites

- `llama.cpp` installed (via `winget`, `brew`, or built from source).
- `llama-cpp-python>=0.2.0` if using Python bindings.
- Internet access to reach `huggingface.co` for discovery workflows.

## Procedure

### 1. Install llama.cpp

Windows (PowerShell):
```powershell
winget install llama.cpp
```

macOS / Linux:
```bash
brew install llama.cpp
```

Build from source (all platforms):
```powershell
git clone https://github.com/ggml-org/llama.cpp
# Official docs: https://github.com/ggml-org/llama.cpp (llama-cli / llama-server)
cd llama.cpp
cmake -B build
cmake --build build --config Release
```

### 2. Model Discovery (URL-first workflow)

Prefer URL workflows before asking for `hf`, Python, or custom scripts.

1. Search for candidate repos on the Hub:
   - Base: `https://huggingface.co/models?apps=llama.cpp&sort=trending`
   - Add `search=<term>` for a model family
   - Add `num_parameters=min:0,max:24B` or similar when the user has size constraints
2. Open the repo with the llama.cpp local-app view:
   - `https://huggingface.co/<repo>?local-app=llama.cpp`
3. Treat the local-app snippet as the source of truth when it is visible:
   - Copy the exact `llama-server` or `llama-cli` command.
   - Report the recommended quant exactly as HF shows it.
4. Read the same `?local-app=llama.cpp` URL as page text or HTML and extract the section under `Hardware compatibility`:
   - Prefer its exact quant labels and sizes over generic tables.
   - Keep repo-specific labels such as `UD-Q4_K_M` or `IQ4_NL_XL`.
   - If that section is not visible in the fetched page source, say so and fall back to the tree API plus generic quant guidance.
5. Query the tree API to confirm what actually exists:
   - `https://huggingface.co/api/models/<repo>/tree/main?recursive=true`
   - Keep entries where `type` is `file` and `path` ends with `.gguf`.
   - Use `path` and `size` as the source of truth for filenames and byte sizes.
   - Separate quantized checkpoints from `mmproj-*.gguf` projector files and `BF16/` shard files.
   - Use `https://huggingface.co/<repo>/tree/main` only as a human fallback.
6. If the local-app snippet is not text-visible, reconstruct the command from the repo plus the chosen quant:
   - Shorthand quant selection: `llama-server -hf <repo>:<QUANT>`
   - Exact-file fallback: `llama-server --hf-repo <repo> --hf-file <filename.gguf>`
7. Only suggest conversion from Transformers weights if the repo does not already expose GGUF files.

### 3. Run directly from the Hugging Face Hub

```powershell
llama-cli -hf ggml-org/gemma-3-1b-it-GGUF
```

```powershell
llama-server -hf ggml-org/gemma-3-1b-it-GGUF
```

### 4. Run an exact GGUF file from the Hub

Use this when the tree API shows custom file naming or the exact HF snippet is missing.

```powershell
llama-server `
    --hf-repo microsoft/Phi-3-mini-4k-instruct-gguf `
    --hf-file Phi-3-mini-4k-instruct-q4.gguf `
    -c 4096
```

### 5. Python bindings (llama-cpp-python)

Install:
```powershell
pip install llama-cpp-python
```

CUDA build:
```powershell
$env:CMAKE_ARGS="-DGGML_CUDA=on"; pip install llama-cpp-python --force-reinstall --no-cache-dir
```

Metal build:
```powershell
$env:CMAKE_ARGS="-DGGML_METAL=on"; pip install llama-cpp-python --force-reinstall --no-cache-dir
```

Basic generation:
```python
from llama_cpp import Llama

llm = Llama(
    model_path="./model-q4_k_m.gguf",
    n_ctx=4096,
    n_gpu_layers=35,     # 0 for CPU, 99 to offload everything
    n_threads=8,
)

out = llm("What is machine learning?", max_tokens=256, temperature=0.7)
print(out["choices"][0]["text"])
```

Chat + streaming:
```python
llm = Llama(
    model_path="./model-q4_k_m.gguf",
    n_ctx=4096,
    n_gpu_layers=35,
    chat_format="llama-3",   # or "chatml", "mistral", etc.
)

resp = llm.create_chat_completion(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is Python?"},
    ],
    max_tokens=256,
)
print(resp["choices"][0]["message"]["content"])

# Streaming
for chunk in llm("Explain quantum computing:", max_tokens=256, stream=True):
    print(chunk["choices"][0]["text"], end="", flush=True)
```

Embeddings:
```python
llm = Llama(model_path="./model-q4_k_m.gguf", embedding=True, n_gpu_layers=35)
vec = llm.embed("This is a test sentence.")
print(f"Embedding dimension: {len(vec)}")
```

Load from Hub:
```python
llm = Llama.from_pretrained(
    repo_id="bartowski/Llama-3.2-3B-Instruct-GGUF",
    filename="*Q4_K_M.gguf",
    n_gpu_layers=35,
)
```

### 6. Choosing a quant

Use the Hub page first, generic heuristics second.

- Prefer the exact quant that HF marks as compatible for the user's hardware profile.
- For general chat, start with `Q4_K_M`.
- For code or technical work, prefer `Q5_K_M` or `Q6_K` if memory allows.
- For very tight RAM budgets, consider `Q3_K_M`, `IQ` variants, or `Q2` variants only if the user explicitly prioritizes fit over quality.
- For multimodal repos, mention `mmproj-*.gguf` separately. The projector is not the main model file.
- Do not normalize repo-native labels. If the page says `UD-Q4_K_M`, report `UD-Q4_K_M`.

### 7. Extracting available GGUFs from a repo

When the user asks what GGUFs exist, return:
- filename
- file size
- quant label
- whether it is a main model or an auxiliary projector

Ignore unless requested:
- README
- BF16 shard files
- imatrix blobs or calibration artifacts

Use the tree API for this step:
- `https://huggingface.co/api/models/<repo>/tree/main?recursive=true`

For a repo like `unsloth/Qwen3.6-35B-A3B-GGUF`, the local-app page can show quant chips such as `UD-Q4_K_M`, `UD-Q5_K_M`, `UD-Q6_K`, and `Q8_0`, while the tree API exposes exact file paths such as `Qwen3.6-35B-A3B-UD-Q4_K_M.gguf` and `Qwen3.6-35B-A3B-Q8_0.gguf` with byte sizes. Use the tree API to turn a quant label into an exact filename.

### 8. Output format for discovery requests

```text
Repo: <repo>
Recommended quant from HF: <label> (<size>)
llama-server: <command>
Other GGUFs:
- <filename> - <size>
- <filename> - <size>
Source URLs:
- <local-app URL>
- <tree API URL>
```

## Pitfalls

- Do not normalize repo-native quant labels. If the page says `UD-Q4_K_M`, report `UD-Q4_K_M`.
- Do not confuse `mmproj-*.gguf` projector files with the main model file. They are auxiliary.
- If the `Hardware compatibility` section is not visible in the fetched page source, say so and fall back to the tree API plus generic quant guidance.
- Only suggest conversion from Transformers weights if the repo does not already expose GGUF files.
- Ignore `BF16/` shard files and `imatrix` blobs unless explicitly requested.
- On Windows PowerShell, use backticks (`` ` ``) for line continuation in multi-line commands, not backslashes (`\`).

## Verification

### Check OpenAI-compatible server

```powershell
curl http://localhost:8080/v1/chat/completions `
  -H "Content-Type: application/json" `
  -d '{ "messages": [ {"role": "user", "content": "Write a limerick about Python exceptions"} ] }'
```

Expected: A JSON response containing a limerick in `choices[0].message.content`.

### Verify tree API response

```powershell
curl "https://huggingface.co/api/models/bartowski/Llama-3.2-3B-Instruct-GGUF/tree/main?recursive=true"
```

Expected: JSON array of objects with `type`, `path`, and `size` fields. Filter for `path` ending in `.gguf`.

## References

Load these reference files when deeper context is needed:

- **[references/hub-discovery.md](references/hub-discovery.md)** — Load when performing URL-only Hugging Face workflows, search patterns, GGUF extraction, or command reconstruction.
- **[references/advanced-usage.md](references/advanced-usage.md)** — Load when user asks about speculative decoding, batched inference, grammar-constrained generation, LoRA, multi-GPU, custom builds, or benchmark scripts.
- **[references/quantization.md](references/quantization.md)** — Load when user needs quant quality tradeoffs, Q4/Q5/Q6/IQ selection advice, model size scaling, or imatrix details.
- **[references/server.md](references/server.md)** — Load when setting up direct-from-Hub server launch, OpenAI API endpoints, Docker deployment, NGINX load balancing, or monitoring.
- **[references/optimization.md](references/optimization.md)** — Load when tuning CPU threading, BLAS, GPU offload heuristics, batch sizes, or running benchmarks.
- **[references/troubleshooting.md](references/troubleshooting.md)** — Load when diagnosing install/convert/quantize/inference/server issues, Apple Silicon quirks, or debugging.

## Resources

- **GitHub**: https://github.com/ggml-org/llama.cpp
- **Hugging Face GGUF + llama.cpp docs**: https://huggingface.co/docs/hub/gguf-llamacpp
- **Hugging Face Local Apps docs**: https://huggingface.co/docs/hub/main/local-apps
- **Hugging Face Local Agents docs**: https://huggingface.co/docs/hub/agents-local
- **Example local-app page**: https://huggingface.co/unsloth/Qwen3.6-35B-A3B-GGUF?local-app=llama.cpp
- **Example tree API**: https://huggingface.co/api/models/unsloth/Qwen3.6-35B-A3B-GGUF/tree/main?recursive=true
- **Example llama.cpp search**: https://huggingface.co/models?num_parameters=min:0,max:24B&apps=llama.cpp&sort=trending
- **License**: MIT
