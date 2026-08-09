# CUDA Debugging Tools Guide

Choose the narrowest tool that can test the current failure. Preserve a small deterministic reproducer and a known-correct reference.

## Build information

For sanitizer and profiler source correlation, prefer an optimized build with line information:

    nvcc -O3 -lineinfo program.cu -o program

Use device debug generation only when cuda-gdb needs it:

    nvcc -O0 -g -G program.cu -o program-debug

Device debug code can change optimization, resource use, and timing. Reproduce the final result with the normal build.

## Compute Sanitizer

Discover options supported by the installed toolkit:

    compute-sanitizer --help
    compute-sanitizer --tool memcheck --help

Run the tools separately:

    compute-sanitizer --tool memcheck ./program
    compute-sanitizer --tool racecheck ./program
    compute-sanitizer --tool initcheck ./program
    compute-sanitizer --tool synccheck ./program

**memcheck**

Use for invalid, misaligned, out-of-bounds, and leaked device-memory accesses. Read the reported access size, address space, thread coordinates, and source line.

**racecheck**

Use for shared-memory hazards and supported asynchronous-copy synchronization checks. Do not present it as a general detector for arbitrary global-memory data races. Read the current tool documentation for architecture and feature coverage.

**initcheck**

Use for supported uninitialized device-memory reads. Coverage is not equivalent to a whole-program definedness proof.

**synccheck**

Use for invalid barrier and warp-synchronization usage. A clean run does not prove that the algorithm's memory ordering is correct.

Sanitizer execution perturbs scheduling. After fixing a report, rerun correctness tests and the original workload without the sanitizer.

Useful narrowing options vary by release. Query --help before copying filters, launch-skip controls, or suppression syntax from an older note.

## CUDA launch errors

Check errors at both launch and completion boundaries:

    my_kernel<<<grid, block>>>(args);
    cudaError_t launch_status = cudaGetLastError();
    cudaError_t completion_status = cudaDeviceSynchronize();

The launch check catches configuration and immediate launch errors. Synchronization can surface asynchronous execution failures and changes program timing, so keep it in debugging or test code rather than inserting it into a performance path.

## cuda-gdb

Use batch mode for reproducible collection:

    cuda-gdb -batch +      -ex "run" +      -ex "bt" +      -ex "info cuda threads" +      ./program-debug

For interactive debugging, select the relevant kernel, block, and thread before inspecting device state. Check cuda-gdb help for command syntax because supported views vary by toolkit and platform.

## Binary inspection

Inspect embedded targets, PTX, SASS, symbols, and resource usage:

    cuobjdump -lelf ./program
    cuobjdump -ptx ./program
    cuobjdump -sass ./program
    cuobjdump -symbols ./program
    cuobjdump -res-usage ./program

Narrow text output with ripgrep:

    cuobjdump -ptx ./program | rg -n -A 100 'myKernel'
    cuobjdump -symbols ./program | rg -i 'function'
    cuobjdump -res-usage ./program | rg -n -A 8 'Function'

Use nvdisasm when control-flow or instruction-level SASS inspection requires capabilities beyond cuobjdump.

## Isolation workflow

Reproduce the failure with the smallest input and one launch when possible.

    failing application
      → focused kernel reproducer
      → sanitizer or debugger evidence
      → minimal code change
      → reference comparison
      → original workload validation

Useful test patterns include:

- zero, identity, monotonic, and boundary-size inputs;
- store-back inspection for special register layouts;
- comparison against a slow CPU or framework reference;
- padding and guard regions around buffers;
- deterministic seeds and fixed launch dimensions.

For inline PTX, tensor instructions, barriers, or memory ordering, verify the focused PTX page rather than inferring semantics from SASS or from a similar instruction.

## Limits

No single tool proves correctness:

- memcheck does not prove race freedom;
- racecheck has scoped coverage;
- synccheck does not validate the complete memory model;
- printf and synchronization can hide timing-dependent bugs;
- cuda-gdb and -G builds change execution behavior.

When tool output is clean but results differ, compare the last known-good and failing code generation, inputs, launch configuration, and dependency versions.
