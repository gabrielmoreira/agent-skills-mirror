---
name: tilelang-skill
description: >-
  Write, debug, and optimize TileLang kernels from local upstream language,
  JIT, autotuning, profiling, compiler, test, and example source. Use when the
  task explicitly involves tilelang, tilelang.language, @tilelang.jit,
  @T.prim_func, T.Kernel, T.copy, T.gemm, TileLang Profiler, Carver, TileLang
  passes, or TileLang CUDA, ROCm, Metal, and CPU backends. Use triton-skill for
  Triton or Gluon, cutlass-skill for direct CUTLASS, CuTe, or CuTeDSL work, and
  cuda-skill for raw CUDA, PTX, NVIDIA architecture, or profiling-tool facts.
---

# TileLang development

Use the local TileLang checkout as the primary source for APIs, implementation patterns, and repository-specific build instructions. Prefer current source and examples over remembered signatures because the DSL, compiler, and backend integrations evolve quickly.

## Locate the checkout

Resolve the directory containing this `SKILL.md`, then use its `repos/tilelang/` child. The installer links that path to `agent-gpu-skills/third_party/tilelang/` or to the checkout supplied through `TILELANG_REPO`.

In commands below, replace `TILELANG_REPO` with the resolved absolute path:

```bash
TILELANG_REPO=/absolute/path/to/tilelang-skill/repos/tilelang
```

If the checkout is missing, run this from the `agent-gpu-skills` repository and reinstall the Skill:

```bash
bash update-repos.sh tilelang
bash install.sh --skill tilelang-skill
```

The default checkout is a source-reference snapshot. It does not initialize TileLang's nested third-party submodules. Use a complete development checkout through `TILELANG_REPO` when building TileLang or changing its compiler.

## Choose the source surface

| Task | Start here |
|:-----|:-----------|
| Language syntax and operations | `tilelang/language/` |
| JIT wrappers, adapters, and kernel objects | `tilelang/jit/` |
| Lowering and semantic checks | `tilelang/engine/` |
| Autotuning | `tilelang/autotuner/` |
| Benchmarking and profiler helpers | `tilelang/profiler/` |
| Layout inference and representations | `tilelang/layout/`, `tilelang/analysis/` |
| Schedule recommendation and Carver | `tilelang/carver/` |
| CUDA, ROCm, Metal, and CPU Python backends | `tilelang/cuda/`, `tilelang/rocm/`, `tilelang/metal/`, `tilelang/cpu/` |
| Compiler transforms and target code generation | `src/` |
| Current kernels and end-to-end workloads | `examples/` |
| Language, compiler, backend, and regression tests | `testing/python/` |
| Repository-specific build and test commands | `.agents/skills/tilelang-build/SKILL.md` |

Read `quick-reference.md` when mapping an operation, backend, or compiler question to a concrete path in the validated checkout.

## Query workflow

1. Classify the task as kernel DSL, JIT/runtime, autotuning/profiling, or compiler/backend work.
2. Find the closest current example for the operation, target backend, architecture, dtype, and shape regime.
3. Verify each DSL operation against its Python definition, then trace lowering or backend code only as far as the question requires.
4. Preserve the workload's shapes, dtypes, layouts, memory scopes, target, launch configuration, and numerical contract.
5. Establish correctness and confirm the actual generated path before tuning.

Discover current documentation and examples before relying on a remembered filename:

```bash
find "$TILELANG_REPO/docs" -type f -name '*.md' | sort
find "$TILELANG_REPO/examples" -type f -name '*.py' | sort
```

Search kernel patterns and their definitions together:

```bash
rg -n '@tilelang\.jit|@T\.prim_func|T\.Kernel|T\.Pipelined' \
  "$TILELANG_REPO/examples"

rg -n 'T\.copy|T\.gemm|T\.alloc_shared|T\.alloc_fragment' \
  "$TILELANG_REPO/examples"

rg -n '^def (copy|gemm|alloc_shared|alloc_fragment)|class Kernel' \
  "$TILELANG_REPO/tilelang/language"
```

Trace JIT, lowering, and target selection:

```bash
rg -n 'def (compile|lower)|class .*Kernel|class .*Adapter' \
  "$TILELANG_REPO/tilelang/jit" \
  "$TILELANG_REPO/tilelang/engine"

rg -n 'target|backend|codegen' \
  "$TILELANG_REPO/tilelang/backend" \
  "$TILELANG_REPO/tilelang/cuda" \
  "$TILELANG_REPO/tilelang/rocm" \
  "$TILELANG_REPO/tilelang/metal" \
  "$TILELANG_REPO/tilelang/cpu"
```

Trace compiler transformations and generated source:

```bash
rg -n 'Pass|Lower|Legalize|Layout' \
  "$TILELANG_REPO/src/transform" \
  "$TILELANG_REPO/tilelang/engine"

rg -n 'CodeGen|codegen|Build' \
  "$TILELANG_REPO/src/cuda" \
  "$TILELANG_REPO/src/rocm" \
  "$TILELANG_REPO/src/metal" \
  "$TILELANG_REPO/src/cpu"
```

Search tuning, profiling, and nearby tests:

```bash
rg -n 'autotune|Profiler|do_bench|get_profiler' \
  "$TILELANG_REPO/examples" \
  "$TILELANG_REPO/tilelang/autotuner" \
  "$TILELANG_REPO/tilelang/profiler"

rg -n 'copy|gemm|pipelined|layout' \
  "$TILELANG_REPO/testing/python/language" \
  "$TILELANG_REPO/testing/python"
```

## Implementation discipline

Keep these layers separate during diagnosis:

```text
TileLang Python kernel and compile-time parameters
  → TileLang IR, semantic checks, and compiler transforms
  → backend source generation and native compilation
  → runtime dispatch on the selected target
```

A TileLang source construct does not prove which hardware instruction or memory path the generated kernel uses. Inspect `get_kernel_source()`, compiler traces, or profile data when that distinction matters. Add `cuda-skill` for PTX semantics, compute capability, Nsight, or Compute Sanitizer details.

TileLang contains a CuTeDSL integration under `tilelang/contrib/cutedsl/`. Use this Skill when tracing how TileLang selects or calls that integration. Use `cutlass-skill` when the task is about CuTeDSL APIs or implementations themselves.

For correctness work:

- compare against an independent reference over representative and boundary shapes;
- test tails, dynamic dimensions, layouts, dtype conversions, and backend-specific paths;
- separate DSL parsing, lowering, native compilation, runtime, and numerical failures;
- reproduce the original target and compile-time parameters before minimizing the case.

For performance work:

- freeze the benchmark shape set, warmup, repetition count, and synchronization method;
- confirm the measured call dispatches to the intended compiled kernel;
- inspect generated source before attributing a result to TMA, tensor cores, tcgen05, or a CuTeDSL path;
- change one tile, thread count, stage count, layout, or pass configuration at a time.

## Build and test routing

Before building, installing, or testing TileLang itself, read the upstream repository instructions:

```text
.agents/skills/tilelang-build/SKILL.md
```

Those instructions are versioned with the checkout and are authoritative for the current build commands. Most compiler and kernel tests require an appropriate device. Verify the active import path, build directory, target backend, and GPU before interpreting a result.

## Updating the source

From the `agent-gpu-skills` repository:

```bash
bash update-repos.sh tilelang
python3 scripts/validate_repo.py --require-sources
```

The checkout follows TileLang `main`, while `third_party/UPSTREAMS.toml` records the commit last accepted by this Skill. Review source-map drift before updating that record.
