# Nsight Compute 2026.2.1 Quick Guide

Nsight Compute explains why a selected CUDA kernel behaves as measured. Use Nsight Systems first when the slow region or launch is not yet known.

This guide follows the latest official snapshot recorded in MANIFEST.md. It is not tied to the NCU version installed on the current machine.

## Discover the active tool

Sets, section identifiers, metrics, and chip support vary by release and architecture. Query before constructing a profile command:

    ncu --version
    ncu --list-sets
    ncu --list-sections
    ncu --query-metrics

For full metric suffixes:

    ncu --query-metrics-mode suffix --metrics sm__throughput

Use ncu-docs/NsightComputeCli.md for CLI semantics and ncu-docs/ProfilingGuide.md for metric interpretation.

## Start narrow

    ncu --kernel-name regex:myKernel +      --launch-count 1 +      -o my-kernel +      ./program

If the same kernel appears during warmup:

    ncu --kernel-name regex:myKernel +      --launch-skip 10 +      --launch-count 1 +      -o my-kernel +      ./program

Use exact input, launch configuration, clocks, and software build when comparing reports.

## Choose data by question

The default basic set is a useful first pass. Add only the sections needed for the current hypothesis:

    ncu --list-sections
    ncu --section LaunchStats +      --section Occupancy +      --kernel-name regex:myKernel +      -o launch-and-occupancy +      ./program

Before copying a section identifier from an older note, confirm it with --list-sections. Current identifiers such as LaunchStats and SchedulerStats differ from names used in some older notes.

Use --set full only when the collection cost and replay behavior are acceptable. Full collection can require many passes and can perturb cache state or application behavior.

## Metric selection

Prefer sections for exploratory analysis because they include related metrics and rules. Use explicit metrics for stable automated experiments:

    ncu --query-metrics-mode suffix --metrics METRIC_BASE
    ncu --metrics FULL_METRIC_NAME +      --kernel-name regex:myKernel +      --launch-count 1 +      ./program

Do not assume a metric exists across all GPUs. Metric names, suffixes, and availability depend on the chip and NCU release.

## Interpret in layers

Read the report in this order:

- launch dimensions, register use, shared memory, and achieved occupancy;
- compute and memory throughput relative to the measured workload;
- instruction mix and issue behavior;
- memory traffic, access pattern, and cache behavior;
- warp stalls and scheduler state;
- source or SASS correlation when line information is available.

High occupancy is not automatically good, and low occupancy is not automatically the bottleneck. Connect each metric to elapsed time and a testable hypothesis.

## Reports and comparison

    ncu --import my-kernel.ncu-rep
    ncu --csv --page raw --import my-kernel.ncu-rep

Keep before and after reports:

    ncu --kernel-name regex:myKernel -o before ./program_before
    ncu --kernel-name regex:myKernel -o after ./program_after

Compare the same kernel invocation and input. If code generation changed, also compare ptxas resource output and SASS.

## Common collection problems

**No kernel matched**

Check --kernel-name-base and use a quoted regex. List or inspect actual demangled names before widening the filter.

**Permission error**

Performance-counter access may be restricted by the driver or system policy. Follow the official deployment guidance rather than changing permissions blindly.

**Too many replays or unstable values**

Collect fewer sections, isolate one launch, control application state, and consider whether replay changes caches or synchronization.

**Unsupported metric**

Query metrics for the active device or chip. Do not replace it with a similarly named metric without reading its definition.

## Source lookup

    rg -n -i 'sets and sections|replay' ncu-docs/ProfilingGuide.md
    rg -n -- '--kernel-name|--list-sections|--query-metrics' +      ncu-docs/NsightComputeCli.md
    rg -n 'Updates in 2026.2.1' ncu-docs/ReleaseNotes.md
