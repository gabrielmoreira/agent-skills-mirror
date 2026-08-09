# CUDA Driver API Search Guide

This guide routes queries into the local CUDA Driver API snapshot. Read MANIFEST.md for the verified version and retrieval date.

The current inventory contains:

- 50 module pages under cuda-driver-docs/modules/;
- 84 structure pages under cuda-driver-docs/data-structures/;
- cuda-driver-docs/INDEX.md.

## Search workflow

Search for the exact symbol, then read the focused module or type page:

    rg -l 'cuCtxCreate' cuda-driver-docs
    rg -n -C 24 'cuCtxCreate' +      cuda-driver-docs/modules/group__cuda__ctx.md

    rg -l 'cuMemMap' cuda-driver-docs
    rg -n -C 24 'cuMemCreate|cuMemMap|cuMemSetAccess' +      cuda-driver-docs/modules/group__cuda__va.md

    rg -n -C 20 'CUDA_ERROR_INVALID_VALUE' cuda-driver-docs

Use INDEX.md when the symbol name is unknown and only the subsystem is known.

## Common routes

| Need | Likely module |
|---|---|
| Initialization and driver version | group__cuda__initialize.md, group__cuda__version.md |
| Device queries | group__cuda__device.md |
| Contexts and primary contexts | group__cuda__ctx.md, group__cuda__primary__ctx.md |
| Modules and libraries | group__cuda__module.md, group__cuda__library.md |
| Kernel launch | group__cuda__exec.md |
| Streams and events | group__cuda__stream.md, group__cuda__event.md |
| Memory allocation and copies | group__cuda__mem.md |
| Virtual memory management | group__cuda__va.md |
| Stream-ordered allocation | group__cuda__malloc__async.md |
| Graphs | group__cuda__graph.md |
| Green contexts and resources | group__cuda__green__contexts.md |
| Tensor memory | group__cuda__tensor__memory.md |
| Logical endpoints | group__cuda__logical__endpoint.md |

Discover exact filenames instead of assuming:

    rg --files cuda-driver-docs/modules | rg -i 'context|module|graph|memory|tensor'

## What to verify

For every function, check:

- initialization and current-context requirements;
- handle ownership, lifetime, and thread-safety;
- synchronization and asynchronous error propagation;
- address-space, alignment, and access permissions;
- compatibility with stream capture or CUDA Graphs;
- deprecation and version notes;
- exact CUresult values and recovery expectations.

For structures, check required initialization, reserved fields, versioned aliases, and which API consumes the structure.

## Driver and Runtime API boundaries

Driver API symbols normally start with cu; Runtime API symbols start with cuda. Runtime calls may operate through a primary context, while explicit Driver API context management can change ownership and current-context assumptions.

Do not translate between the APIs by name alone. Search both snapshots and explain the context, lifetime, and error-model differences.

## Version-sensitive questions

The local snapshot is authoritative for its recorded version. Verify the current official Driver API online for newly added entry points, deprecations, architecture-specific features, and compatibility claims made after the manifest date.
