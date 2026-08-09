# CUDA Performance Traps

Use this page as a hypothesis checklist, not as a diagnosis table. Measure the affected kernel and verify metric availability on the active GPU before drawing conclusions.

## Uncoalesced global memory access

Symptoms can include excess memory sectors, poor useful-byte efficiency, and low achieved bandwidth.

Check thread-to-address mapping, alignment, stride, vector width, and partial-warp behavior. Reshape the data or map adjacent lanes to adjacent elements when possible.

Do not use a universal sectors-per-request threshold. Transaction behavior depends on access width, cache path, architecture, and instruction.

## Shared-memory bank conflicts

Conflicts serialize accesses within a warp when multiple lanes target different addresses in the same bank.

Check the element size, leading dimension, lane mapping, broadcasts, and architecture-specific bank organization. Padding or swizzling can help, but may increase footprint or address arithmetic.

Confirm with a current shared-memory section or queried metric. Metric names differ across NCU versions and chips.

## Warp divergence

Divergence matters when active lanes follow different paths for enough instructions to affect useful issue throughput.

Check branch distribution, predication, loop trip counts, early exits, and whether work can be grouped by path. Reordering work may improve control flow while harming memory locality, so measure both.

## Register pressure and occupancy

High register use can reduce resident warps or trigger spills. Lowering register use can also increase instructions and make code slower.

Inspect ptxas resource output, local-memory traffic, launch limits, and achieved occupancy. Treat occupancy as a capacity constraint, not an optimization objective by itself.

## Excess synchronization

Block barriers, memory fences, atomics, host synchronizations, and implicit stream dependencies can serialize work.

Use Nsight Systems to locate gaps and blocking API calls. Use the programming guide and PTX memory model to determine whether weaker scope, different ordering, or pipeline restructuring is correct.

Never remove synchronization based only on timing. Run compute-sanitizer and correctness tests after any change.

## Small kernels and launch overhead

Many short kernels can be dominated by CPU dispatch, framework overhead, or dependency gaps.

Consider fusion, batching, persistent execution, or CUDA Graphs only after the timeline shows launch overhead is material. Fusion can increase registers, reduce occupancy, or duplicate work.

## Copy and allocation overhead

Repeated allocation, pageable transfers, unnecessary format conversion, and serialized copies can dominate end-to-end time even when kernels are efficient.

Profile the whole request with Nsight Systems. Check memory-pool reuse, pinned-memory policy, copy direction, stream dependencies, and overlap.

## Cache assumptions

A high cache hit rate is not automatically useful, and a low hit rate is not automatically bad. Streaming kernels may perform well with little reuse.

Measure requested bytes, transferred bytes, latency exposure, and overall throughput. Avoid tuning cache hints without a reproducible access pattern and architecture-specific evidence.

## Measurement discipline

Before and after comparisons should keep input, warmup, launch selection, clocks, and software build fixed.

Discover supported NCU data before scripting:

    ncu --list-sections
    ncu --query-metrics

Profile one representative launch:

    ncu --kernel-name regex:myKernel +      --launch-count 1 +      -o kernel-report +      ./program

Use ncu-guide.md for collection strategy, nsys-guide.md for system-level analysis, and the Best Practices Guide for general optimization rationale.
