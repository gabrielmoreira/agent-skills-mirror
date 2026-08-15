# Ollama performance tuning — fix GPU starvation from oversized context

## Symptom
- Local inference is slow: a 27B model generates ~3 tok/s instead of ~30+.
- `nvidia-smi` shows GPU compute utilization ~5% during generation despite a strong GPU (e.g. RTX 3090 Ti, 24 GB).
- VRAM usage is low (model loads on GPU but KV cache is elsewhere) — check `curl -s localhost:11434/api/ps`.

## Root cause
Ollama sizes the KV cache from the **effective context length** at model load = min(client `context_length` request, server `OLLAMA_CONTEXT_LENGTH` env var). A 27B model at 256K context needs a ~40 GB KV cache. If that exceeds free VRAM, Ollama silently allocates it in **CPU RAM** and shuffles KV data per token → GPU idle, throughput collapses.

The binding cap is the server env var `OLLAMA_CONTEXT_LENGTH`. Hermes's `context_length` config only needs to be ≥ what conversations request; Ollama caps at the env var. Reducing the Hermes config alone does NOT free VRAM unless `OLLAMA_CONTEXT_LENGTH` is also reduced.

## Fix (persist in Windows User env, then restart the server)
```
setx OLLAMA_CONTEXT_LENGTH 65536
setx OLLAMA_KV_CACHE_TYPE q4_0
setx OLLAMA_FLASH_ATTENTION true
```
- `OLLAMA_CONTEXT_LENGTH=65536` — 64K is enough for most chat; small enough that the KV cache fits on GPU. (Hermes requires its own `context_length >= 64000`, so 65536 satisfies that too.)
- `OLLAMA_KV_CACHE_TYPE=q4_0` — 4-bit KV cache. Lets the cache + model both live in VRAM (qwen3.6:27b ≈ 17.8 GB + q4 KV ≈ 2.6 GB ≈ 20.4 GB of 24 GB).
- `OLLAMA_FLASH_ATTENTION=true` — faster attention kernels.

Apply + restart (single instance only — don't run both):
```
taskkill /F /IM "ollama app.exe" /T
taskkill /F /IM ollama.exe /T
start "" "$env:LOCALAPPDATA\Programs\Ollama\ollama app.exe"
:: or: ollama serve
```

## Verify (deterministic)
1. GPU util during generation — watch in another shell:
```
nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv -l 1
```
2. Sustained generation speed (thinking OFF for fair numbers — Qwen3 defaults to thinking mode). Pipe curl stdout into `python` (do NOT write to `/tmp` and read from `python` — MSYS/git-bash `curl` and Windows `python` resolve `/tmp` differently):
```
curl -s -m 150 -X POST http://localhost:11434/api/chat -H "Content-Type: application/json" -d "{\"model\":\"qwen3.6:27b\",\"messages\":[{\"role\":\"user\",\"content\":\"Write a detailed 150-word paragraph about why the ocean is important to Earth climate.\"}],\"think\":false,\"options\":{\"num_predict\":200,\"temperature\":0.7}}" | python -c "import sys,json;print(''.join(json.loads(l).get('message',{}).get('content','') for l in sys.stdin if l.strip()))"
```
   Wrap with `time` (bash) to measure tok/s. Healthy target on a 3090 Ti: ~30 tok/s, GPU ~90% util.

## Expected outcome (RTX 3090 Ti, qwen3.6:27b)
| Metric | Before | After |
|---|---|---|
| tok/s (sustained) | ~3 | ~33 |
| GPU util during gen | ~5% | ~90% |
| VRAM | model only | model + q4 KV ≈ 20.4 GB / 24 |

## Pitfalls
- **Don't raise `OLLAMA_CONTEXT_LENGTH` past what fits VRAM** expecting speed — it silently spills to RAM and gets slower. Bump only when a task truly needs the longer window, and accept the slowdown.
- **`think:false` matters for benchmarks** — Qwen3 defaults to thinking mode, which inflates latency and isn't representative of normal chat throughput.
- **Measure sustained, not first-token** — the first ~1–2 s includes model load/compile; sample util over a 200-token generation to see real numbers.
- **MSYS/git-bash + Windows `python` path mismatch** — writing curl output to `/tmp/g.txt` then reading it from `python` fails (different `/tmp`). Pipe curl stdout into `python -c "..."` (the verify command above does this).
