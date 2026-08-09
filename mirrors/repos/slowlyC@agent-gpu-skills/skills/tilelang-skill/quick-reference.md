# TileLang quick reference

All paths are relative to `TILELANG_REPO`, the checkout exposed at `tilelang-skill/repos/tilelang/`.
This source map reflects the validated checkout, not a fixed allowlist. Enumerate the parent directories before searching so newer documentation, examples, backends, and passes are included.

## Documentation routing

| Need | Path |
|:-----|:-----|
| Programming model and lowering overview | `docs/get_started/overview.md` |
| Supported target model | `docs/get_started/targets.md` |
| Kernel definitions, launch, loops, memory, and JIT | `docs/programming_guides/language_basics.md` |
| Language instructions | `docs/programming_guides/instructions.md` |
| Software pipelining | `docs/programming_guides/software_pipeline.md` |
| Cluster and TMA programming | `docs/programming_guides/cluster_tma.md` |
| Autotuning | `docs/programming_guides/autotuning.md` |
| Kernel debugging | `docs/tutorials/debug_tools_for_tilelang.md` |
| Lowering trace | `docs/tools/lower_trace.md` |
| Compiler pass diff | `docs/tools/pass_diff.md` |
| Static analysis tools | `docs/tools/analyzer.md` |
| Compiler implementation notes | `docs/compiler_internals/` |
| Runtime implementation notes | `docs/runtime_internals/` |
| Operator-oriented guides | `docs/deeplearning_operators/` |

## Representative examples

Search all of `examples/` before choosing an implementation. The entries below are landmarks, not an allowlist.

| Need | Path |
|:-----|:-----|
| End-to-end JIT, correctness, source inspection, and profiling | `examples/quickstart.py` |
| GEMM baseline | `examples/gemm/example_gemm.py` |
| GEMM autotuning | `examples/gemm/example_gemm_autotune.py` |
| SM100 tcgen05 GEMM | `examples/gemm_sm100/gemm_tcgen5mma.py` |
| SM100 block-scaled GEMM | `examples/blockscaled_gemm_sm100/` |
| SM100 FP8xFP4 workload | `examples/deepseek_v4/fp8_fp4_gemm_1d1d_sm100.py` |
| FlashAttention | `examples/flash_attention/` |
| SM100 FlashAttention | `examples/flash_attention_sm100/` |
| Flash decoding | `examples/flash_decoding/` |
| DeepSeek MLA | `examples/deepseek_mla/` |
| Fused MoE | `examples/fusedmoe/example_fusedmoe_tilelang.py` |
| KDA kernels | `examples/kda/` |
| Gated DeltaNet kernels | `examples/gdn/` |
| AMD kernels | `examples/amd/` |

## Python source routing

| Concept | Path |
|:--------|:-----|
| Language exports and operations | `tilelang/language/` |
| Copy, GEMM, reduction, scan, and allocation operations | `tilelang/language/copy_op.py`, `tilelang/language/gemm_op.py`, `tilelang/language/reduce_op.py`, `tilelang/language/scan_op.py`, `tilelang/language/allocate.py` |
| Kernel context and structured loops | `tilelang/language/kernel.py`, `tilelang/language/loop.py` |
| Parser and eager frontend | `tilelang/language/parser/`, `tilelang/language/eager/` |
| JIT kernel and framework adapters | `tilelang/jit/` |
| Lowering and semantic checks | `tilelang/engine/` |
| Autotuning | `tilelang/autotuner/` |
| Benchmark and profiler helpers | `tilelang/profiler/` |
| Layout representations and visualization | `tilelang/layout/`, `tilelang/analysis/` |
| Schedule recommendation and Carver | `tilelang/carver/` |
| Target and generic backend interfaces | `tilelang/backend/` |
| CUDA backend | `tilelang/cuda/` |
| ROCm backend | `tilelang/rocm/` |
| Metal backend | `tilelang/metal/` |
| CPU backend | `tilelang/cpu/` |
| TileLang-to-CuTeDSL integration | `tilelang/contrib/cutedsl/` |

## Compiler and runtime source routing

| Concept | Path |
|:--------|:-----|
| Compiler transformations | `src/transform/` |
| CUDA lowering and code generation | `src/cuda/` |
| ROCm lowering and code generation | `src/rocm/` |
| Metal lowering and code generation | `src/metal/` |
| CPU lowering and code generation | `src/cpu/` |
| Runtime implementation | `src/runtime/` |
| Layout inference and representation | `src/layout/` |
| Tile language operations | `src/op/` |
| Target templates | `src/tl_templates/` |

## Tests and repository development

| Need | Path |
|:-----|:-----|
| Python language and operation tests | `testing/python/language/` |
| Autotuning tests | `testing/python/autotune/` |
| Backend tests | `testing/python/backend/` |
| CUDA-specific tests | `testing/python/cuda/` |
| AMD-specific tests | `testing/python/amd/` |
| Debugging and compiler-trace tests | `testing/python/debug/` |
| Regression and issue tests | `testing/python/issue/` |
| Current build, install, and test instructions | `.agents/skills/tilelang-build/SKILL.md` |

The sparse checkout contains these source surfaces but does not initialize nested third-party submodules. Use a complete TileLang development checkout when a build, native dependency, or submodule implementation is part of the task.
