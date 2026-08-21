---
name: flash-attention
description: "Enables fused transformer attention (PyTorch scaled_dot_product_attention, the flash-attn library, optional H100 FP8 and sliding windows) so long sequences use less GPU memory and less wall time. Use for training or inference past about 512 tokens, attention OOMs, or Ampere-or-newer SDPA backends. Not for CNN or UNet blocks, CPU-only training, or float32 attention. Never assume Volta V100 kernels exist."
version: 1.0.1
author: Orchestra Research
license: MIT
dependencies: [flash-attn, torch, transformers]
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Optimization, Flash Attention, Attention Optimization, Memory Efficiency, Speed Optimization, Long Context, PyTorch, SDPA, H100, FP8, Transformers]
---

## Overview
Flash Attention provides 2-4x speedup and 10-20x memory reduction for transformer attention through IO-aware tiling and recomputation. It supports PyTorch native SDPA, the `flash-attn` library, H100 FP8, and sliding window attention.

## When to Use
- Training transformers with sequences >512 tokens.
- Running inference with long context (>2K tokens).
- GPU memory constrained (OOM with standard attention).
- Need 2-4x speedup without accuracy loss.
- Using PyTorch 2.2+ or can install `flash-attn`.

## Prerequisites
- **GPU**: NVIDIA Ampere+ (A100, A10, A30) or AMD MI200+. Turing (T4) is supported. Volta (V100) is NOT supported.
- **VRAM**: Same as standard attention (Flash Attention doesn't increase memory).
- **CUDA**: 12.0+ (11.8 minimum).
- **PyTorch**: 2.2+ for native SDPA support.

## Procedure

### Workflow 1: Enable in existing PyTorch model (Native SDPA)

1. **Check PyTorch version** (≥2.2):
```powershell
python -c "import torch; print(torch.__version__)"
```
If <2.2, upgrade:
```powershell
pip install --upgrade torch
```

2. **Enable Flash Attention backend**:
Replace standard attention:
```python
# Before (standard attention)
attn_weights = torch.softmax(q @ k.transpose(-2, -1) / math.sqrt(d_k), dim=-1)
out = attn_weights @ v

# After (Flash Attention)
import torch.nn.functional as F
out = F.scaled_dot_product_attention(q, k, v, attn_mask=mask)
```

Force Flash Attention backend:
```python
with torch.backends.cuda.sdp_kernel(
    enable_flash=True,
    enable_math=False,
    enable_mem_efficient=False
):
    out = F.scaled_dot_product_attention(q, k, v)
```

### Workflow 2: Use flash-attn library for advanced features

1. **Install flash-attn library**:
```powershell
pip install flash-attn --no-build-isolation
```

2. **Modify attention code**:
```python
from flash_attn import flash_attn_func

# Input: [batch_size, seq_len, num_heads, head_dim]
# Transpose from [batch, heads, seq, dim] if needed
q = q.transpose(1, 2)
k = k.transpose(1, 2)
v = v.transpose(1, 2)

out = flash_attn_func(
    q, k, v,
    dropout_p=0.1,
    causal=True,
    window_size=(-1, -1),  # No sliding window
    softmax_scale=None  # Auto-scale
)

out = out.transpose(1, 2)  # Back to [batch, heads, seq, dim]
```

3. **Enable advanced features**:
Sliding window attention (local attention):
```python
# Only attend to window of 256 tokens before/after
out = flash_attn_func(
    q, k, v,
    window_size=(256, 256),  # (left, right) window
    causal=True
)
```

### Workflow 3: H100 FP8 optimization (FlashAttention-3)

1. **Verify H100 GPU**:
```powershell
nvidia-smi --query-gpu=name --format=csv
# Should show "H100" or "H800"
```

2. **Install flash-attn with FP8 support**:
```powershell
pip install flash-attn --no-build-isolation
```

3. **Convert inputs to FP8 and run**:
```python
import torch
from flash_attn import flash_attn_func

q = torch.randn(2, 4096, 32, 64, device='cuda', dtype=torch.float16)
k = torch.randn(2, 4096, 32, 64, device='cuda', dtype=torch.float16)
v = torch.randn(2, 4096, 32, 64, device='cuda', dtype=torch.float16)

# Convert to float8_e4m3 (FP8)
q_fp8 = q.to(torch.float8_e4m3fn)
k_fp8 = k.to(torch.float8_e4m3fn)
v_fp8 = v.to(torch.float8_e4m3fn)

# FlashAttention-3 automatically uses FP8 kernels on H100
out = flash_attn_func(q_fp8, k_fp8, v_fp8)
```

## Pitfalls
- **ImportError: cannot import flash_attn**: Install with no-build-isolation flag: `pip install flash-attn --no-build-isolation`. Or install CUDA toolkit first: `conda install cuda -c nvidia`.
- **Slower than expected (no speedup)**: Flash Attention benefits increase with sequence length. <512 tokens: Minimal speedup (10-20%). 512-2K tokens: 2-3x speedup. >2K tokens: 3-4x speedup. Check sequence length is sufficient.
- **RuntimeError: CUDA error**: Verify GPU supports Flash Attention. `torch.cuda.get_device_capability()` should be ≥(7, 5) for Turing+. Volta (V100) is NOT supported.
- **Accuracy degradation**: Check dtype is float16 or bfloat16 (not float32). Flash Attention uses float16/bfloat16 for speed. Float32 not supported.

## Verification

1. **Verify speedup with profiling**:
```python
import torch
import torch.nn.functional as F
import torch.utils.benchmark as benchmark

def test_attention(use_flash):
    q, k, v = [torch.randn(2, 8, 2048, 64, device='cuda', dtype=torch.float16) for _ in range(3)]
    if use_flash:
        with torch.backends.cuda.sdp_kernel(enable_flash=True):
            return F.scaled_dot_product_attention(q, k, v)
    else:
        attn = (q @ k.transpose(-2, -1) / 8.0).softmax(dim=-1)
        return attn @ v

t_flash = benchmark.Timer(stmt='test_attention(True)', globals=globals())
t_standard = benchmark.Timer(stmt='test_attention(False)', globals=globals())

print(f"Flash: {t_flash.timeit(100).mean:.3f}s")
print(f"Standard: {t_standard.timeit(100).mean:.3f}s")
# Expected: 2-4x speedup for sequences >512 tokens.
```

2. **Test accuracy matches baseline**:
```python
q, k, v = [torch.randn(1, 8, 512, 64, device='cuda', dtype=torch.float16) for _ in range(3)]

out_flash = F.scaled_dot_product_attention(q, k, v)
attn_weights = torch.softmax(q @ k.transpose(-2, -1) / 8.0, dim=-1)
out_standard = attn_weights @ v

diff = (out_flash - out_standard).abs().max()
print(f"Max difference: {diff:.6f}")
# Should be <1e-3 for float16
```

## References
- Load `references/transformers-integration.md` WHEN you need to enable Flash Attention in HuggingFace Transformers (BERT, GPT, Llama models).
- Load `references/benchmarks.md` WHEN you need detailed speed and memory comparisons across GPUs and sequence lengths.
