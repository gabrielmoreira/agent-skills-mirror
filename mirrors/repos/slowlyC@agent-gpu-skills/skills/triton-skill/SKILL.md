---
name: triton-skill
description: >-
  Write, debug, and optimize Triton and Gluon GPU kernels from local upstream
  tutorials, production kernels, language definitions, and compiler source. Use
  when the task explicitly involves triton.jit, triton.language, tl.*, Gluon,
  TensorDescriptor, Triton autotune, TritonGPU/MLIR lowering, triton_kernels, or
  converting a CUDA kernel to Triton. Use cuda-skill for raw CUDA/PTX and NVIDIA
  architecture facts, and cutlass-skill for CUTLASS, CuTe, or CuTeDSL work.
---

# Triton and Gluon development

Use the local Triton checkout as the primary source for APIs and implementation patterns. Prefer current tutorials and source over remembered signatures because Triton and Gluon evolve quickly.

## Locate the checkout

Resolve the directory containing this `SKILL.md`, then use its `repos/triton/` child. The installer links that path to `agent-gpu-skills/third_party/triton/` or to the checkout supplied through `TRITON_REPO`.

In commands below, replace `TRITON_REPO` with the resolved absolute path:

```bash
TRITON_REPO=/absolute/path/to/triton-skill/repos/triton
```

If the checkout is missing, run this from the `agent-gpu-skills` repository and reinstall the Skill:

```bash
bash update-repos.sh triton
bash install.sh --skill triton-skill
```

## Choose the source surface

| Task | Start here |
|:-----|:-----------|
| Triton language syntax and introductory patterns | `python/tutorials/` |
| Gluon layout and architecture-level patterns | `python/tutorials/gluon/` |
| Complete example kernels | `python/examples/` |
| Production matmul, reduction, top-k and SwiGLU | `python/triton_kernels/triton_kernels/` |
| `tl.*` definitions and semantics | `python/triton/language/` |
| JIT, autotuning and runtime behavior | `python/triton/runtime/` |
| Python compiler entry points | `python/triton/compiler/` |
| Triton and GPU dialect definitions | `include/triton/Dialect/` |
| Compiler analyses, transforms and lowering | `lib/` |

Read `quick-reference.md` when choosing a tutorial, a complete example, or a production-kernel implementation.

## Query workflow

1. Identify whether the task is Triton, Gluon, or compiler internals.
2. Find the closest current tutorial or implementation for the operation and architecture.
3. Verify every API used against its definition or another current call site.
4. Preserve the target workload's shape, dtype, stride, layout, masking, and numerical contract.
5. Establish correctness before changing launch parameters or optimization strategy.

Discover current examples before relying on a remembered filename:

```bash
find "$TRITON_REPO/python/tutorials" -maxdepth 2 -type f | sort
find "$TRITON_REPO/python/examples" -type f | sort
```

Query Triton language usage and definitions:

```bash
rg -n 'tl\.dot|tl\.dot_scaled' "$TRITON_REPO/python/tutorials"
rg -n '@triton\.autotune' "$TRITON_REPO/python/tutorials"
rg -n '^def (load|store|dot|dot_scaled)' \
  "$TRITON_REPO/python/triton/language"
```

Query Gluon architecture patterns:

```bash
rg -n '@gluon\.jit' "$TRITON_REPO/python/tutorials/gluon"
rg -n 'wgmma|tcgen05|mbarrier|tma' \
  "$TRITON_REPO/python/tutorials/gluon" \
  "$TRITON_REPO/python/examples"
```

Trace production kernels:

```bash
rg -n 'persistent|TensorDescriptor' \
  "$TRITON_REPO/python/triton_kernels/triton_kernels/matmul_details"

rg -n 'mxfp|flexpoint' \
  "$TRITON_REPO/python/triton_kernels/triton_kernels/numerics_details"
```

Trace compiler definitions and lowering:

```bash
rg -n 'def.*Op' "$TRITON_REPO/include/triton/Dialect/Triton/IR"
rg -n 'Encoding' "$TRITON_REPO/include/triton/Dialect/TritonGPU/IR"
rg -n 'wgmma|tma|tcgen05' \
  "$TRITON_REPO/include/triton/Dialect/TritonNvidiaGPU"
rg -n 'Pattern|Rewrite' "$TRITON_REPO/lib/Conversion/TritonGPUToLLVM"
```

## Implementation discipline

Keep these layers separate during diagnosis:

```text
Python kernel and launch metadata
  → Triton/Gluon IR and compiler transforms
  → generated GPU code on the selected target
```

A source-level pattern does not prove that the compiled kernel uses the intended instruction or memory path. Inspect compiler output or profile data when that distinction matters. Add `cuda-skill` for PTX semantics, compute capability, Nsight, or Compute Sanitizer details.

For correctness work:

- compare against an independent reference over representative and boundary shapes;
- test masked tails, non-power-of-two dimensions, strides and dtype conversions;
- separate compilation failures from runtime correctness and numerical tolerance;
- reproduce the original dispatch and launch metadata before reducing the case.

For performance work:

- freeze the benchmark shape set and measurement method;
- confirm autotune keys cover every dimension that changes the best configuration;
- change one tile, warp, stage, persistence, or specialization choice at a time;
- verify the generated path before attributing a result to TMA, WGMMA, tcgen05, or warp specialization.

## Updating the source

From the `agent-gpu-skills` repository:

```bash
bash update-repos.sh triton
python3 scripts/validate_repo.py --require-sources
```

The checkout follows Triton `main`, while `third_party/UPSTREAMS.toml` records the commit last accepted by this Skill. Review source-map drift before updating that record.
