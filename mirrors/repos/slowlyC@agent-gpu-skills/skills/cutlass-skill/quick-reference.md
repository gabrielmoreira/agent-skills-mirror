# CUTLASS and CuTe quick reference

All paths are relative to `CUTLASS_REPO`, the checkout exposed at `cutlass-skill/repos/cutlass/`.
This source map reflects the validated checkout, not a fixed allowlist. Enumerate the parent directories before searching so newer additions are included.

## CuTeDSL source

```text
python/CuTeDSL/cutlass/
├── base_dsl/       # DSL types, compilation, diagnostics, pointers and arrays
├── compiler/       # Compiler entry points
├── cute/           # Layout, tensor, copy, MMA and architecture operations
├── cutlass_dsl/    # CUTLASS DSL integration
├── experimental/   # Experimental primitives and task scheduling APIs
├── jax/            # JAX integration
├── pipeline/       # Pipeline abstractions
└── utils/          # Utilities and profiling helpers
```

Other Python source surfaces include `python/pycute/` for layout and swizzle utilities, and `python/cutlass_library/` for manifest and generator support.

## CuTeDSL examples

Current examples are grouped below `examples/python/CuTeDSL/`:

```text
examples/python/CuTeDSL/
├── cute/             # Architecture kernels, tutorials, notebooks and FFI
├── cute_ext/         # Extension-oriented examples
├── dsl_tutorials/    # JIT, export, FFI, JAX and TVM-FFI
├── experimental/     # Primitives and task scheduling
├── helpers/          # Shared example helpers
└── utils/            # Example utilities
```

Representative paths:

| Need | Path |
|:-----|:-----|
| Ampere SGEMM | `examples/python/CuTeDSL/cute/ampere/kernel/dense_gemm/sgemm.py` |
| Ampere tensor-op GEMM | `examples/python/CuTeDSL/cute/ampere/kernel/dense_gemm/tensorop_gemm.py` |
| Ampere elementwise | `examples/python/CuTeDSL/cute/ampere/kernel/elementwise/elementwise_add.py` |
| Ampere tutorials | `examples/python/CuTeDSL/cute/ampere/tutorial/` |
| Hopper dense GEMM | `examples/python/CuTeDSL/cute/hopper/kernel/dense_gemm/dense_gemm.py` |
| Hopper FP8 GEMM | `examples/python/CuTeDSL/cute/hopper/kernel/dense_gemm/dense_gemm_fp8_2xacc.py` |
| Hopper grouped GEMM | `examples/python/CuTeDSL/cute/hopper/kernel/grouped_gemm/grouped_gemm.py` |
| Blackwell dense GEMM | `examples/python/CuTeDSL/cute/blackwell/kernel/dense_gemm/dense_gemm.py` |
| Blackwell block-scaled GEMM | `examples/python/CuTeDSL/cute/blackwell/kernel/blockscaled_gemm/dense_blockscaled_gemm_persistent.py` |
| SM103 block-scaled GEMM | `examples/python/CuTeDSL/cute/blackwell/kernel/blockscaled_gemm/sm103_dense_blockscaled_gemm_persistent.py` |
| Blackwell grouped GEMM | `examples/python/CuTeDSL/cute/blackwell/kernel/grouped_gemm/grouped_gemm.py` |
| Blackwell MoE utilities | `examples/python/CuTeDSL/cute/blackwell/kernel/moe/` |
| Blackwell GEMM tutorials | `examples/python/CuTeDSL/cute/blackwell/tutorial/tutorial_gemm/` |
| TMA tutorials | `examples/python/CuTeDSL/cute/blackwell/tutorial/tutorial_tma/` |
| Inline PTX tutorial | `examples/python/CuTeDSL/dsl_tutorials/inline_ptx.py` |
| PDL tutorial | `examples/python/CuTeDSL/dsl_tutorials/programmatic_dependent_launch.py` |

## Representative CUTLASS C++ examples

| Need | Path |
|:-----|:-----|
| Ampere Stream-K | `examples/47_ampere_gemm_universal_streamk/` |
| Hopper warp-specialized GEMM | `examples/48_hopper_warp_specialized_gemm/` |
| Hopper CollectiveBuilder | `examples/49_hopper_gemm_with_collective_builder/` |
| Hopper FP8 GEMM | `examples/54_hopper_fp8_warp_specialized_gemm/` |
| Hopper mixed-dtype GEMM | `examples/55_hopper_mixed_dtype_gemm/` |
| Hopper grouped GEMM | `examples/57_hopper_grouped_gemm/` |
| Hopper sparse GEMM | `examples/62_hopper_sparse_gemm/` |
| Hopper blockwise scaling | `examples/67_hopper_fp8_warp_specialized_gemm_with_blockwise_scaling/` |
| Blackwell GEMM | `examples/70_blackwell_gemm/` |
| Blackwell CollectiveBuilder | `examples/71_blackwell_gemm_with_collective_builder/` |
| Blackwell narrow precision | `examples/72_blackwell_narrow_precision_gemm/` |
| Blackwell FMHA | `examples/77_blackwell_fmha/` |
| Blackwell blockwise GEMM | `examples/81_blackwell_gemm_blockwise/` |
| Blackwell sparse GEMM | `examples/83_blackwell_sparse_gemm/` |
| Hopper FMHA | `examples/88_hopper_fmha/` |
| Blackwell MoE GEMM | `examples/92_blackwell_moe_gemm/` |
| Blackwell low-latency GQA | `examples/93_blackwell_low_latency_gqa/` |

## Header routing

| Concept | Path |
|:--------|:-----|
| CuTe layout | `include/cute/layout.hpp` |
| CuTe tensor | `include/cute/tensor.hpp` |
| CuTe swizzle | `include/cute/swizzle.hpp` |
| Copy and MMA atoms | `include/cute/atom/` |
| Architecture operations | `include/cute/arch/` |
| GEMM collectives | `include/cutlass/gemm/collective/` |
| GEMM kernels and device adapters | `include/cutlass/gemm/kernel/`, `include/cutlass/gemm/device/` |
| Epilogues | `include/cutlass/epilogue/` |
| Pipelines | `include/cutlass/pipeline/` |
