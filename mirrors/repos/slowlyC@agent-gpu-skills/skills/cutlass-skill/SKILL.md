---
name: cutlass-skill
description: >-
  Write, debug, and optimize CUTLASS, CuTe, and CuTeDSL GPU kernels from local
  upstream source, examples, and headers. Use when the task explicitly involves
  CUTLASS/CuTe/CuTeDSL, cute::Layout, cute::Tensor, TiledMMA, TiledCopy,
  CollectiveBuilder, CollectiveMainloop, CollectiveEpilogue, GemmUniversal,
  KernelSchedule, EpilogueSchedule, CUTLASS pipelines, EVT, pycute, or CUTLASS
  template errors. Use cuda-skill for raw CUDA/PTX or NVIDIA architecture facts,
  and triton-skill for Triton or Gluon implementation work.
---

# CUTLASS and CuTe development

Use the local CUTLASS checkout as the primary implementation reference. Prefer current source and examples over remembered APIs because CuTeDSL paths and interfaces change frequently.

## Locate the checkout

Resolve the directory containing this `SKILL.md`, then use its `repos/cutlass/` child. The installer links that path to `agent-gpu-skills/third_party/cutlass/` or to the checkout supplied through `CUTLASS_REPO`.

In commands below, replace `CUTLASS_REPO` with the resolved absolute path:

```bash
CUTLASS_REPO=/absolute/path/to/cutlass-skill/repos/cutlass
```

If the checkout is missing, run this from the `agent-gpu-skills` repository and reinstall the Skill:

```bash
bash update-repos.sh cutlass
bash install.sh --skill cutlass-skill
```

## Choose the source surface

| Task | Start here |
|:-----|:-----------|
| CuTeDSL API and implementation | `python/CuTeDSL/cutlass/` |
| All CuTeDSL examples and tutorials | `examples/python/CuTeDSL/` |
| CUTLASS C++ examples | `examples/` |
| CUTLASS C++ kernels and builders | `include/cutlass/` |
| CuTe C++ layout, copy, and MMA | `include/cute/` |
| Python layout and swizzle utilities | `python/pycute/` |
| Python manifest and generator utilities | `python/cutlass_library/` |

Read `quick-reference.md` when mapping an operation or architecture to a concrete file in the validated checkout.

## Query workflow

1. Identify the programming surface: CuTeDSL Python, CuTe C++, or CUTLASS C++.
2. Find the closest example for the target architecture and operation.
3. Trace the example into the implementation and headers it instantiates.
4. Check dtype, layout, alignment, architecture target, schedule, and epilogue together.
5. Build or run the smallest representative example before adapting it to the target repository.

Discover files before loading a large source file:

```bash
find "$CUTLASS_REPO/examples/python/CuTeDSL" -type f | sort
find "$CUTLASS_REPO/examples" -mindepth 1 -maxdepth 1 -type d | sort
```

Search CuTeDSL definitions and usage together:

```bash
rg -n 'TiledMMA|tiled_mma' \
  "$CUTLASS_REPO/python/CuTeDSL/cutlass/cute" \
  "$CUTLASS_REPO/examples/python/CuTeDSL"

rg -n 'Pipeline|pipeline' \
  "$CUTLASS_REPO/python/CuTeDSL/cutlass/pipeline" \
  "$CUTLASS_REPO/examples/python/CuTeDSL/cute"
```

Trace CUTLASS C++ builders and kernels:

```bash
rg -n 'CollectiveBuilder' \
  "$CUTLASS_REPO/examples/49_hopper_gemm_with_collective_builder"

rg -n 'CollectiveMainloop' \
  "$CUTLASS_REPO/include/cutlass/gemm/collective"

rg -n 'GemmUniversal' \
  "$CUTLASS_REPO/include/cutlass/gemm"
```

Trace CuTe layout and architecture primitives:

```bash
rg -n 'make_layout|composition|complement' \
  "$CUTLASS_REPO/include/cute/layout.hpp"

rg -n 'TiledCopy|make_tiled_copy' "$CUTLASS_REPO/include/cute"
rg -n 'SM90_TMA|SM100_TMA' "$CUTLASS_REPO/include/cute/arch"
```

For a C++ example, inspect its `CMakeLists.txt` and build only the selected target. Replace the architecture and target below for the workload:

```bash
cmake -S "$CUTLASS_REPO" -B /tmp/cutlass-build -DCUTLASS_NVCC_ARCHS=100a
cmake --build /tmp/cutlass-build \
  --target 71_blackwell_gemm_with_collective_builder
```

Before running a CuTeDSL example, inspect the current `python/CuTeDSL/pyproject.toml` and requirements files instead of assuming a compatible CUDA or Python version.

## Implementation discipline

Keep three layers separate when diagnosing a CUTLASS kernel:

```text
problem shape and tensor layout
  → selected collective and schedule
  → generated CUDA/PTX behavior on the target architecture
```

Do not infer the selected schedule from an example directory name. Follow the instantiated types and builder parameters. When an architecture or instruction detail determines correctness, add `cuda-skill` and verify it against the CUDA or PTX reference.

For correctness work:

- preserve the original problem shapes, strides, layouts, dtypes, scaling format, and epilogue;
- compare against an independent reference implementation;
- test boundary shapes and alignment cases before performance tuning;
- treat template compilation success as necessary but not sufficient.

For performance work:

- establish a stable baseline and measurement method;
- change one schedule, tile, stage count, or epilogue choice at a time;
- record compiler resource usage and the exact architecture target;
- profile only after confirming that the measured dispatch path uses the intended kernel.

## Updating the source

From the `agent-gpu-skills` repository:

```bash
bash update-repos.sh cutlass
python3 scripts/validate_repo.py --require-sources
```

The checkout follows CUTLASS `main`, while `third_party/UPSTREAMS.toml` records the commit last accepted by this Skill. Review source-map drift before updating that record.
