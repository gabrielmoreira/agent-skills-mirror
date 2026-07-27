---
name: cuda-skill
description: "Query current NVIDIA CUDA, PTX ISA, Runtime API, Driver API, Programming Guide, Best Practices, Nsight Compute, and Nsight Systems references. Use for direct CUDA C++ or PTX work, and for framework tasks only when they need NVIDIA ISA, API, architecture, or tool facts. Triggers include inline PTX, WMMA, WGMMA, TMA, tcgen05, mbarrier, fabric operations, CUDA APIs and Graphs, memory ordering, compute capability, Ampere, Hopper, Blackwell, Rubin, nsys, ncu, and compute-sanitizer."
---

# NVIDIA CUDA Reference

Use this skill as the source of truth for CUDA, PTX, NVIDIA GPU architecture, and NVIDIA profiling or debugging tools. Prefer the local official-document snapshots, then verify against NVIDIA's current online documentation when a fact is version-sensitive or absent locally.

For framework-specific implementation, use the corresponding skill first:

- Triton or Gluon kernel code: triton-skill
- CUTLASS, CuTe, or CuTeDSL code: cutlass-skill
- SGLang serving and kernels: sglang-skill

Add this skill when those tasks require CUDA API, PTX ISA, architecture, or NVIDIA tool facts.

## Locate the references

Resolve the directory containing this SKILL.md, then use its references/ child. Do not assume a Cursor, Claude, or Codex-specific install path.

In examples below, set a task-scoped variable to the resolved absolute path:

    CUDA_REFS=/absolute/path/to/cuda-skill/references

Read MANIFEST.md before making version claims. It records the snapshot version, source URL, and document inventory.

## Source routing

| Question | Primary source |
|---|---|
| PTX syntax, semantics, ISA or target requirements | ptx-docs/ |
| CUDA Runtime functions, errors, and structs | cuda-runtime-docs/ |
| CUDA Driver functions, contexts, modules, VMM | cuda-driver-docs/ |
| CUDA programming model and feature behavior | cuda-guide/ |
| General CUDA optimization guidance | best-practices-guide/ |
| Nsight Compute metrics, sections, and CLI | ncu-docs/, ncu-guide.md |
| Nsight Systems tracing and CLI | nsys-docs/, nsys-guide.md |
| Correctness tools and cuda-gdb | debugging-tools.md |
| NVTX instrumentation | nvtx-patterns.md |
| Frequent performance mistakes | performance-traps.md |

The short guide files are search maps, not substitutes for the full official snapshots.

## Query workflow

Start with file discovery. Do not load a large chapter or the whole specification when a focused page exists.

    # Discover focused PTX pages.
    rg -l -i 'wgmma\.mma_async' "$CUDA_REFS/ptx-docs"

    # Read the relevant lines with context.
    rg -n -C 12 'Target ISA Notes|PTX ISA Notes|wgmma\.mma_async' \
      "$CUDA_REFS/ptx-docs/9-instruction-set"

    # Runtime and Driver API lookup.
    rg -l 'cudaStreamSynchronize' "$CUDA_REFS/cuda-runtime-docs"
    rg -l 'cuMemMap' "$CUDA_REFS/cuda-driver-docs"

    # Programming and optimization concepts.
    rg -l -i 'thread block cluster' "$CUDA_REFS/cuda-guide"
    rg -l -i 'coalesc' "$CUDA_REFS/best-practices-guide"

For PTX instructions, inspect all of the following before answering:

- instruction syntax and operands;
- semantic description and memory ordering;
- PTX ISA introduction version;
- target ISA or sm_* requirements;
- architecture-specific restrictions and undefined behavior.

Keep these four layers separate:

    PTX ISA version
      → virtual target accepted by the assembler
      → toolkit/compiler support
      → physical GPU capability

A documented target does not by itself prove that the local toolkit accepts it or that the current machine implements it. For unreleased or preview architectures such as Rubin, verify the current official online documentation.

## CUDA API lookup

Search by exact symbol first, then read the containing module and related type pages.

    rg -n -C 20 'cudaErrorInvalidValue' "$CUDA_REFS/cuda-runtime-docs"
    rg -n -C 25 'cudaLaunchKernelEx' "$CUDA_REFS/cuda-runtime-docs"
    rg -n -C 25 'cuCtxCreate' "$CUDA_REFS/cuda-driver-docs"
    rg -n -C 25 'cuMemCreate|cuMemMap' "$CUDA_REFS/cuda-driver-docs"

Check parameter lifetime, synchronization behavior, error propagation, version notes, and deprecation status. Do not infer Runtime API behavior from a similarly named Driver API function.

## Debugging workflow

Minimize the reproducer, preserve the failing launch configuration, then use the narrowest correctness tool:

    compute-sanitizer --tool memcheck ./program
    compute-sanitizer --tool racecheck ./program
    compute-sanitizer --tool initcheck ./program
    compute-sanitizer --tool synccheck ./program

Use debugging-tools.md for tool options and limitations. After a fix, rerun the original workload because sanitizer execution changes scheduling and timing.

## Profiling workflow

Use Nsight Systems to locate time and overlap problems, then Nsight Compute to explain one selected kernel.

    nsys profile -o report ./program
    nsys stats report.nsys-rep --report cuda_gpu_kern_sum

    ncu --list-sets
    ncu --list-sections
    ncu --query-metrics
    ncu --kernel-name regex:myKernel --launch-count 1 -o report ./program

Metric names, section identifiers, predefined sets, and report formats can change between releases and architectures. Discover what the active tool supports, then confirm semantics in the latest local Nsight documentation. Do not bind guidance to the machine's installed NCU version.

Base conclusions on measured evidence:

- timeline placement, launch gaps, synchronization, and CPU/GPU overlap from Nsight Systems;
- achieved throughput, instruction mix, stalls, memory traffic, occupancy, and source correlation from Nsight Compute;
- compiler resource usage from ptxas -v or the build log.

Change one hypothesis at a time and remeasure against the same baseline.

## Architecture questions

For Ampere, Hopper, Blackwell, or Rubin questions, distinguish public architecture disclosures from ISA availability. Check:

- cuda-guide/05-appendices/compute-capabilities.md;
- the instruction's PTX ISA and target notes;
- ptx-docs/13-release-notes/;
- current NVIDIA architecture or CUDA release documentation when local snapshots do not cover the claim.

Do not identify a GPU architecture solely from a failed CUDA runtime query or a product label. Use explicit compute-capability or compilation-target evidence when available.

## Updating the snapshots

Always scrape into a fresh staging root. --force overwrites matching files but does not delete the output directory or unrelated files.

    cd /path/to/agent-gpu-skills
    uv run scrape_docs.py all \
      --output-dir /tmp/cuda-docs-staging \
      --force

    diff -qr cuda_skill/references/ptx-docs \
      /tmp/cuda-docs-staging/ptx-docs

Review version changes, page-count changes, renamed files, and representative instruction/API pages before merging. Do not remove obsolete live files without explicit user approval.

Run the repository validator after any update:

    python3 scripts/validate_cuda_skill.py

## Answer quality

State which document version supports the answer. Cite the focused local file and section when possible. If online verification was required, link the official NVIDIA page and label any inference. Avoid hardcoded performance thresholds unless they come from the user's measurements or a cited document.
