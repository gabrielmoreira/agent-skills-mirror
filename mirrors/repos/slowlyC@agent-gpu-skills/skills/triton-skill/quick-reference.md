# Triton and Gluon quick reference

All paths are relative to `TRITON_REPO`, the checkout exposed at `triton-skill/repos/triton/`.
The tables reflect the validated checkout, not a fixed allowlist. Enumerate the tutorial and example directories before searching so newer additions are included.

## Triton tutorials

| Topic | Path |
|:------|:-----|
| Vector add | `python/tutorials/01-vector-add.py` |
| Fused softmax | `python/tutorials/02-fused-softmax.py` |
| Matrix multiplication and autotune | `python/tutorials/03-matrix-multiplication.py` |
| Stateless dropout | `python/tutorials/04-low-memory-dropout.py` |
| Layer normalization | `python/tutorials/05-layer-norm.py` |
| Fused attention | `python/tutorials/06-fused-attention.py` |
| External functions | `python/tutorials/07-extern-functions.py` |
| Grouped GEMM | `python/tutorials/08-grouped-gemm.py` |
| Persistent matmul | `python/tutorials/09-persistent-matmul.py` |
| Block-scaled matmul | `python/tutorials/10-block-scaled-matmul.py` |
| Programmatic dependent launch | `python/tutorials/11-programmatic-dependent-launch.py` |

## Gluon tutorials

| Topic | Path |
|:------|:-----|
| Introduction | `python/tutorials/gluon/01-intro.py` |
| Layouts | `python/tutorials/gluon/02-layouts.py` |
| Asynchronous copy | `python/tutorials/gluon/03-async-copy.py` |
| TMA | `python/tutorials/gluon/04-tma.py` |
| WGMMA | `python/tutorials/gluon/05-wgmma.py` |
| tcgen05 MMA | `python/tutorials/gluon/06-tcgen05.py` |
| Persistent work assignment | `python/tutorials/gluon/07-persistence.py` |
| Warp specialization | `python/tutorials/gluon/08-warp-specialization.py` |
| TMA gather/scatter | `python/tutorials/gluon/09-tma-gather-scatter.py` |
| tcgen05 copy | `python/tutorials/gluon/10-tcgen05-copy.py` |
| Scaled tcgen05 MMA | `python/tutorials/gluon/11-tcgen05-mma-scaled.py` |
| Cluster launch control | `python/tutorials/gluon/12-cluster-launch-control.py` |
| im2col convolution | `python/tutorials/gluon/13-conv-im2col.py` |
| Multi-CTA execution | `python/tutorials/gluon/14-multicta.py` |

## Complete examples

The validated checkout currently stores complete examples under `python/examples/gluon/`. Search all of `python/examples/` before choosing an implementation.

| Kernel | Path |
|:-------|:-----|
| Attention forward | `python/examples/gluon/01-attention-forward.py` |
| Shared convolution utilities | `python/examples/gluon/02-conv-common.py` |
| Convolution forward | `python/examples/gluon/02-conv-fprop.py` |
| Convolution data gradient | `python/examples/gluon/02-conv-dgrad.py` |
| Convolution weight gradient | `python/examples/gluon/02-conv-wgrad.py` |
| Multi-CTA matmul | `python/examples/gluon/03-matmul-multicta.py` |
| Two-CTA block-scaled matmul | `python/examples/gluon/04-2cta-block-scale-matmul.py` |
| MoE BMM1 with fused gather | `python/examples/gluon/05-moe-bmm1-fused-gather.py` |
| Overlapping accumulator work | `python/examples/gluon/06-overlapping-accumulator.py` |

## Production kernel package

```text
python/triton_kernels/triton_kernels/
├── matmul.py
├── matmul_details/
│   ├── _common.py
│   ├── _matmul.py
│   ├── _p_matmul.py
│   └── opt_flags.py
├── reduce.py
├── topk.py
├── swiglu.py
├── compaction.py
├── distributed.py
├── numerics.py
├── numerics_details/
│   ├── flexpoint.py
│   └── mxfp.py
├── tensor.py
├── tensor_details/
│   ├── bitmatrix.py
│   ├── dtype.py
│   ├── layout.py
│   └── ragged_tensor.py
├── roofline.py
└── testing.py
```

Representative searches:

```bash
rg -n 'TensorDescriptor|persistent' \
  python/triton_kernels/triton_kernels/matmul_details
rg -n 'mxfp|flexpoint' \
  python/triton_kernels/triton_kernels/numerics_details
rg -n 'swizzle|layout' \
  python/triton_kernels/triton_kernels/tensor_details
```

## Compiler source routing

| Need | Path |
|:-----|:-----|
| `tl.*` definitions | `python/triton/language/` |
| Gluon language implementation | `python/triton/experimental/gluon/` |
| Runtime and JIT | `python/triton/runtime/` |
| Python compiler entry points | `python/triton/compiler/` |
| Triton IR | `include/triton/Dialect/Triton/` |
| TritonGPU layouts and transforms | `include/triton/Dialect/TritonGPU/`, `lib/Dialect/TritonGPU/` |
| NVIDIA GPU dialect | `include/triton/Dialect/TritonNvidiaGPU/`, `lib/Dialect/TritonNvidiaGPU/` |
| Gluon dialect | `include/triton/Dialect/Gluon/`, `lib/Dialect/Gluon/` |
| GPU-to-LLVM lowering | `include/triton/Conversion/TritonGPUToLLVM/`, `lib/Conversion/TritonGPUToLLVM/` |

## Debug and profiling entry points

Use the active Triton version's environment variables and tooling rather than copying old flags from memory. Start by searching the runtime and test suite:

```bash
rg -n 'MLIR_ENABLE_DUMP|TRITON_' python/triton python/test | head -100
rg -n 'compute_sanitizer' python/triton_kernels python/test
rg -n 'roofline' python/triton_kernels
```
