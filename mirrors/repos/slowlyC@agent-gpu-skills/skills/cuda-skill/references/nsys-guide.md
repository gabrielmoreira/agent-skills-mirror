# Nsight Systems 2026.3 Quick Guide

Nsight Systems shows where time is spent across CPU threads, CUDA APIs, GPU kernels, memory operations, synchronization, and annotated application ranges.

This guide follows the latest official snapshot recorded in MANIFEST.md. It is not tied to the Nsight Systems version installed on the current machine.

## Basic capture

    nsys --version
    nsys profile --trace=cuda,nvtx,osrt +      -o report +      ./program

The primary artifact is report.nsys-rep. Open it in the GUI for timeline analysis or use CLI reports for reproducible summaries.

Limit collection to the workload of interest:

    nsys profile --delay 5 --duration 10 +      --trace=cuda,nvtx,osrt +      -o report +      ./program

For an application-controlled capture:

    nsys profile --capture-range=cudaProfilerApi +      --trace=cuda,nvtx +      -o report +      ./program

Verify available trace domains and options with nsys profile --help because they vary by platform and release.

## CLI summaries

    nsys stats report.nsys-rep
    nsys stats report.nsys-rep --report cuda_gpu_kern_sum
    nsys stats report.nsys-rep --report cuda_api_sum
    nsys stats report.nsys-rep --report cuda_gpu_mem_time_sum
    nsys stats report.nsys-rep --report nvtx_sum

List reports and format options supported by the active installation:

    nsys stats --help-reports
    nsys stats --help-formats

CSV or JSON here is a rendering of statistical reports:

    nsys stats report.nsys-rep +      --report cuda_gpu_kern_sum +      --format csv

    nsys stats report.nsys-rep +      --report cuda_api_sum +      --format json

## Data export

Use SQLite for custom relational analysis:

    nsys export --type sqlite +      --output report.sqlite +      report.nsys-rep

Use JSON Lines for event-oriented JSON export:

    nsys export --type jsonlines +      --output report.jsonl +      report.nsys-rep

Do not confuse nsys stats --format json with nsys export --type jsonlines. They serve different schemas and workflows. Confirm export types with nsys export --help before scripting across releases.

## Timeline reading order

Read the trace from the outside in:

- process and CPU-thread activity;
- CUDA API calls and blocking synchronization;
- GPU queues, kernels, and copies;
- overlap between compute and data movement;
- NVTX ranges that map work back to application phases.

Then form a specific hypothesis:

- launch gaps suggest CPU scheduling, framework, or synchronization overhead;
- long API calls may be blocking on earlier GPU work;
- serialized copy and compute may indicate stream or dependency issues;
- many tiny kernels may justify fusion, graph capture, or batching;
- low GPU occupancy in the timeline is a symptom, not a root cause.

Use Nsight Compute only after identifying the kernel that needs instruction- or metric-level analysis.

## Repeatable captures

For before and after comparison, keep:

- the exact command and environment;
- input shape, batch size, and warmup policy;
- GPU selection and clock policy;
- report.nsys-rep plus exported summaries;
- software commit and dependency versions.

CUDA Graph workloads need special care. Verify graph capture in application logs and look for graph launch activity in the trace rather than treating disabled prefill capture as failure of every phase.

## Source lookup

    rg -n -- 'nsys profile|--capture-range|--trace' +      nsys-docs/UserGuide.md
    rg -n -- 'nsys stats|--help-reports|--format' +      nsys-docs/UserGuide.md
    rg -n -- 'jsonlines|nsys export|cuda_gpu_kern_sum' +      nsys-docs/AnalysisGuide.md nsys-docs/UserGuide.md
    rg -n 'Nsight Systems 2026.3 Highlights' +      nsys-docs/ReleaseNotes.md
