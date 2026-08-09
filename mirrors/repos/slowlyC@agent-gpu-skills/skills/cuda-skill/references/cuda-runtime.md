# CUDA Runtime API Search Guide

This guide routes queries into the local CUDA Runtime API snapshot. Read MANIFEST.md for the verified version and retrieval date.

The current inventory contains:

- 38 module pages under cuda-runtime-docs/modules/;
- 67 structure or union pages under cuda-runtime-docs/data-structures/;
- cuda-runtime-docs/INDEX.md.

## Search workflow

Search for the exact symbol, then read the focused module or type page:

    rg -l 'cudaStreamSynchronize' cuda-runtime-docs
    rg -n -C 24 'cudaStreamSynchronize' +      cuda-runtime-docs/modules/group__cudart__stream.md

    rg -l 'cudaDeviceProp' cuda-runtime-docs/data-structures
    rg -n -C 20 'cudaErrorInvalidValue' cuda-runtime-docs

Use INDEX.md when the symbol name is unknown and only the feature area is known.

## Common routes

| Need | Likely module |
|---|---|
| Device selection and properties | group__cudart__device.md |
| Streams and callbacks | group__cudart__stream.md |
| Events | group__cudart__event.md |
| Allocation, copies, managed memory | group__cudart__memory.md |
| Stream-ordered pools | group__cudart__memory__pools.md |
| Graph construction and launch | group__cudart__graph.md |
| Kernel launch | group__cudart__execution.md or high-level module |
| External resources and interop | matching interop module |
| Error codes and common types | group__cudart__types.md |
| Fabric APIs | group__cudart__fabric.md |

Discover exact filenames instead of assuming:

    rg --files cuda-runtime-docs/modules | rg -i 'graph|memory|stream|fabric'

## What to verify

For every function, check:

- parameter ownership, lifetime, and alignment;
- host-side and device-side synchronization behavior;
- stream ordering and default-stream semantics;
- whether errors from earlier asynchronous work can surface;
- capture safety and CUDA Graph restrictions;
- supported devices, operating systems, and toolkit versions;
- deprecation or replacement notes.

For structures, inspect field units, reserved fields, required initialization, and the API version that consumes the structure.

## Runtime and Driver API boundaries

Runtime API symbols start with cuda; Driver API symbols normally start with cu. Similar names do not guarantee identical lifetime or context behavior.

When a question involves primary contexts, module loading, virtual memory management, or low-level handles, search cuda-driver-docs/ as well and state which API owns the behavior.

## Version-sensitive questions

The local snapshot is authoritative for its recorded version. Verify the current official Runtime API online when asking about newly added functions, deprecation state, architecture support, or behavior that may have changed after the manifest date.
