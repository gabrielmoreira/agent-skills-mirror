---
name: vllm
description: "Serves LLMs with vLLM PagedAttention and continuous batching: OpenAI-compatible /v1/chat/completions, GPTQ/AWQ/FP8 quantization, tensor parallelism, and offline LLM.generate. Use when deploying high-throughput GPU inference endpoints or fitting 30B-70B models. Not for TRL training, llama.cpp CPU/edge, or using vLLM only as an inspect-ai/lighteval backend."
version: 1.0.1
author: Orchestra Research
license: MIT
dependencies: [vllm, torch, transformers]
platforms: [linux, macos]
metadata:
  hermes:
    tags: [vLLM, Inference Serving, PagedAttention, Continuous Batching, High Throughput, Production, OpenAI API, Quantization, Tensor Parallelism]
---

# vLLM — High-Performance LLM Serving

## Overview

vLLM achieves up to 24x higher throughput than standard HuggingFace transformers through PagedAttention (block-based KV cache) and continuous batching (mixing prefill/decode requests). It provides an OpenAI-compatible API server, offline batch inference, quantization support (GPTQ/AWQ/FP8), and tensor parallelism for multi-GPU deployments.

## When to Use

Use vLLM when:
- Deploying production LLM APIs targeting 100+ req/sec
- Serving OpenAI-compatible endpoints (`/v1/chat/completions`, `/v1/completions`)
- Fitting large models (30B–70B) into limited GPU memory via quantization
- Building multi-user applications (chatbots, assistants, RAG backends)
- Running offline batch inference over large datasets efficiently
- You need low latency with high throughput on NVIDIA GPUs

**Use alternatives instead when:**
- **llama.cpp**: CPU/edge inference, single-user scenarios
- **HuggingFace transformers**: Research, prototyping, one-off generation
- **TensorRT-LLM**: NVIDIA-only, need absolute maximum performance
- **Text-Generation-Inference**: Already invested in HuggingFace ecosystem

## Prerequisites

### Hardware Requirements

| Model Size | Minimum GPU | Notes |
|---|---|---|
| 7B–13B | 1x A10 (24GB) or A100 (40GB) | Single GPU sufficient |
| 30B–40B | 2x A100 (40GB) | Use `--tensor-parallel-size 2` |
| 70B+ | 4x A100 (40GB) or 2x A100 (80GB) | Use AWQ/GPTQ quantization |

Supported platforms: NVIDIA (primary), AMD ROCm, Intel GPUs, TPUs.

### Software Installation

```bash
pip install vllm
```

Dependencies: `vllm`, `torch`, `transformers`.

## Procedure

### Workflow 1: Basic Offline Inference

1. **Import and initialize the LLM engine:**

```python
from vllm import LLM, SamplingParams

llm = LLM(model="meta-llama/Llama-3-8B-Instruct")
sampling = SamplingParams(temperature=0.7, max_tokens=256)
```

2. **Generate text:**

```python
outputs = llm.generate(["Explain quantum computing"], sampling)
print(outputs[0].outputs[0].text)
```

### Workflow 2: OpenAI-Compatible Server

1. **Launch the server:**

```bash
vllm serve meta-llama/Llama-3-8B-Instruct
```

2. **Query with the OpenAI SDK:**

```python
from openai import OpenAI
client = OpenAI(base_url='http://localhost:8000/v1', api_key='EMPTY')
print(client.chat.completions.create(
    model='meta-llama/Llama-3-8B-Instruct',
    messages=[{'role': 'user', 'content': 'Hello!'}]
).choices[0].message.content)
```

### Workflow 3: Production API Deployment

Follow this checklist:

```
Deployment Progress:
- [ ] Step 1: Configure server settings
- [ ] Step 2: Test with limited traffic
- [ ] Step 3: Enable monitoring
- [ ] Step 4: Deploy to production
- [ ] Step 5: Verify performance metrics
```

**Step 1: Configure server settings**

Choose configuration based on your model size:

```bash
# For 7B-13B models on single GPU
vllm serve meta-llama/Llama-3-8B-Instruct \
  --gpu-memory-utilization 0.9 \
  --max-model-len 8192 \
  --port 8000

# For 30B-70B models with tensor parallelism
vllm serve meta-llama/Llama-2-70b-hf \
  --tensor-parallel-size 4 \
  --gpu-memory-utilization 0.9 \
  --quantization awq \
  --port 8000

# For production with caching and metrics
vllm serve meta-llama/Llama-3-8B-Instruct \
  --gpu-memory-utilization 0.9 \
  --enable-prefix-caching \
  --enable-metrics \
  --metrics-port 9090 \
  --port 8000 \
  --host 0.0.0.0
```

**Step 2: Test with limited traffic**

Run a load test before production:

```bash
pip install locust
# Create test_load.py with sample requests
# Run: locust -f test_load.py --host http://localhost:8000
```

Verify TTFT (time to first token) < 500ms and throughput > 100 req/sec.

**Step 3: Enable monitoring**

vLLM exposes Prometheus metrics on port 9090:

```bash
curl http://localhost:9090/metrics | grep vllm
```

Key metrics to monitor:
- `vllm:time_to_first_token_seconds` — Latency
- `vllm:num_requests_running` — Active requests
- `vllm:gpu_cache_usage_perc` — KV cache utilization

**Step 4: Deploy to production**

Use Docker for consistent deployment:

```bash
docker run --gpus all -p 8000:8000 \
  vllm/vllm-openai:latest \
  --model meta-llama/Llama-3-8B-Instruct \
  --gpu-memory-utilization 0.9 \
  --enable-prefix-caching
```

**Step 5: Verify performance metrics**

Check that deployment meets targets:
- TTFT < 500ms (for short prompts)
- Throughput > target req/sec
- GPU utilization > 80%
- No OOM errors in logs

> **Load `references/server-deployment.md`** when you need Docker Compose, Kubernetes manifests, or load balancer configurations for production deployment.

### Workflow 4: Offline Batch Inference

Follow this checklist:

```
Batch Processing:
- [ ] Step 1: Prepare input data
- [ ] Step 2: Configure LLM engine
- [ ] Step 3: Run batch inference
- [ ] Step 4: Process results
```

**Step 1: Prepare input data**

```python
prompts = []
with open("prompts.txt") as f:
    prompts = [line.strip() for line in f]
print(f"Loaded {len(prompts)} prompts")
```

**Step 2: Configure LLM engine**

```python
from vllm import LLM, SamplingParams

llm = LLM(
    model="meta-llama/Llama-3-8B-Instruct",
    tensor_parallel_size=2,
    gpu_memory_utilization=0.9,
    max_model_len=4096
)

sampling = SamplingParams(
    temperature=0.7,
    top_p=0.95,
    max_tokens=512,
    stop=["</s>", "\n\n"]
)
```

**Step 3: Run batch inference**

vLLM automatically batches requests for efficiency — no need to manually chunk prompts:

```python
outputs = llm.generate(prompts, sampling)
```

**Step 4: Process results**

```python
import json

results = []
for output in outputs:
    results.append({
        "prompt": output.prompt,
        "generated": output.outputs[0].text,
        "tokens": len(output.outputs[0].token_ids)
    })

with open("results.jsonl", "w") as f:
    for result in results:
        f.write(json.dumps(result) + "\n")

print(f"Processed {len(results)} prompts")
```

### Workflow 5: Quantized Model Serving

Follow this checklist:

```
Quantization Setup:
- [ ] Step 1: Choose quantization method
- [ ] Step 2: Find or create quantized model
- [ ] Step 3: Launch with quantization flag
- [ ] Step 4: Verify accuracy
```

**Step 1: Choose quantization method**

- **AWQ**: Best for 70B models, minimal accuracy loss
- **GPTQ**: Wide model support, good compression
- **FP8**: Fastest on H100 GPUs

**Step 2: Find or create quantized model**

Use pre-quantized models from HuggingFace (e.g., `TheBloke/Llama-2-70B-AWQ`).

**Step 3: Launch with quantization flag**

```bash
vllm serve TheBloke/Llama-2-70B-AWQ \
  --quantization awq \
  --tensor-parallel-size 1 \
  --gpu-memory-utilization 0.95
```

Result: 70B model fits in ~40GB VRAM.

**Step 4: Verify accuracy**

Compare quantized vs non-quantized responses to confirm task-specific performance is unchanged.

> **Load `references/quantization.md`** when you need detailed AWQ/GPTQ/FP8 setup instructions, model preparation steps, or accuracy comparison benchmarks.

## Pitfalls

### Out of Memory During Model Loading

Reduce memory usage:

```bash
vllm serve MODEL \
  --gpu-memory-utilization 0.7 \
  --max-model-len 4096
```

Or use quantization:

```bash
vllm serve MODEL --quantization awq
```

### Slow First Token (TTFT > 1 second)

Enable prefix caching for repeated prompts:

```bash
vllm serve MODEL --enable-prefix-caching
```

For long prompts, enable chunked prefill:

```bash
vllm serve MODEL --enable-chunked-prefill
```

### Model Not Found Error

Use `--trust-remote-code` for custom models:

```bash
vllm serve MODEL --trust-remote-code
```

### Low Throughput (< 50 req/sec)

Increase concurrent sequences:

```bash
vllm serve MODEL --max-num-seqs 512
```

Check GPU utilization with `nvidia-smi` — should be > 80%.

### Inference Slower Than Expected

Tensor parallelism must use power-of-2 GPU counts:

```bash
vllm serve MODEL --tensor-parallel-size 4  # Not 3
```

Enable speculative decoding for faster generation:

```bash
vllm serve MODEL --speculative-model DRAFT_MODEL
```

> **Load `references/troubleshooting.md`** when you encounter detailed error messages, need debugging steps, or require performance diagnostics beyond the common issues above.

> **Load `references/optimization.md`** when you need PagedAttention tuning details, continuous batching configuration, or benchmark results for your specific hardware.

## Verification

### Verify Server Is Running

```bash
curl http://localhost:8000/v1/models
```

Expected: JSON response listing available models.

### Verify Chat Completions

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"meta-llama/Llama-3-8B-Instruct","messages":[{"role":"user","content":"Hello!"}]}'
```

Expected: JSON response with `choices[0].message.content` containing generated text.

### Verify Metrics Endpoint

```bash
curl http://localhost:9090/metrics | grep vllm
```

Expected: Prometheus-format metrics including `vllm:time_to_first_token_seconds`, `vllm:num_requests_running`, and `vllm:gpu_cache_usage_perc`.

### Verify GPU Utilization

```bash
nvidia-smi
```

Expected: GPU utilization > 80% under load, no OOM errors in vLLM logs.

### Verify Performance Targets

| Metric | Target |
|---|---|
| TTFT (short prompts) | < 500ms |
| Throughput | > 100 req/sec |
| GPU utilization | > 80% |
| OOM errors in logs | None |

## Related skills

- **llama.cpp** — CPU/edge inference for single-user scenarios
- **text-generation-inference** — HuggingFace ecosystem serving alternative
- **tensorrt-llm** — Maximum NVIDIA-only performance

## Resources

- Official docs: https://docs.vllm.ai
- GitHub: https://github.com/vllm-project/vllm
- Paper: "Efficient Memory Management for Large Language Model Serving with PagedAttention" (SOSP 2023)
- Community: https://discuss.vllm.ai
