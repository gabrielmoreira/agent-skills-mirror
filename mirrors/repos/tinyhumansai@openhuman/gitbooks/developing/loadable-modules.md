---
description: >-
  How capability arrives at runtime instead of compile time: the TinyBus module
  ABI, the pinned registry, admission checks, and what happens when one faults.
icon: puzzle-piece
---

# Loadable modules

Feature gates decide what compiles into the binary. Modules decide what the binary can *reach* once it is running. A module is a first-party native library, loaded into the core process, serving a small typed interface over TinyBus.

The trade is explicit: a module shares the core's address space and its crash domain, so it is trusted code and the admission checks matter. In exchange, a user who never generates a document never pays for the document writer, in download size, in resident memory, or in dependency surface.

## The registry

`crates/openhuman-core/src/modules/registry/` compiles in **fourteen** records. Only this registry may select an artifact; nothing reads a module name from config and goes looking.

| Module | Provides |
| --- | --- |
| `tinycomputer` | Desktop and browser observation and control |
| `tinysearch` | Web-search provider dispatch |
| `tinydocs` | Document extraction and `.docx` / `.pptx` synthesis |
| `tinywallet` | Key derivation and transaction signing |
| `tinyjuice` | Tool-output compression and recovery |
| `tinyvoice` | Audio framing, VAD, wake-word gating, hallucination detection |
| `tinyruntime` + `tinyruntime-nodejs` + `tinyruntime-python` | Runtime discovery and warm interpreter pools |
| `tinymcp` | The MCP client and registry |
| `tinyconnectors` | OAuth connector actions and triggers |
| `tinybox` | Sandbox capability discovery |
| `tinychannels` | Messaging channel transports |
| `tinyhosts` | Hosting provider operations |

Each record carries a version, the release it came from, and one **`PlatformAsset` per supported build**: thirteen of the fourteen publish eleven (`ubuntu-24.04` and `ubuntu-22.04` × `x86_64`/`arm64`, `macos-26` and `macos-15` × `arm64`/`x86_64`, `windows-2025-x86_64`, `windows-2022-x86_64`, `windows-11-arm64`), and `tinycomputer` publishes seven because it has no Linux backend.

Every asset carries a SHA-256 **copied verbatim from the published release's own checksum file**. Do not compute a replacement pin from a local build: the point of the digest is that it describes the artifact the release workflow signed, not the one on your machine.

## Resolution order

Each step exists to avoid the cost of the next:

1. Already serving on the host's broker.
2. An operator override: a path in `[modules].overrides`, or a `*_TEST_MODULE` environment variable.
3. The module search path: `OPENHUMAN_MODULE_PATH`, then the platform data directories.
4. Bundled releases staged into the app at build time.
5. The release cache, downloading only if `[modules].allow_download` is true.

An override **bypasses the digest check**, because the artifact is whatever is at that path. That is acceptable only because it is the operator's own file named by the operator's own config, and it is why the block cannot *add* a module that is not already in the registry.

Platform candidates are ordered newest-first with fallthrough. On Linux, glibc 2.39 or newer prefers the 24.04 build and falls back to 22.04; 2.35 or newer gets 22.04; anything older, and musl or an unknown libc, gets an **empty** candidate list, so no published artifact can load there by design.

## Admission

In order, and all of it before any module code runs:

1. Directory ownership and mode, and a regular platform library file within the size cap.
2. The digest allowlist beside the artifact, when present, which is authoritative for its directory.
3. Resolve the ABI descriptor symbol, and validate its frozen 16-byte prefix before reading the rest.
4. Validate the full descriptor: matching pointer width, endianness and target triple, a compatible TinyBus series, and module feature bits that are a subset of the host's. A module built with `panic = "abort"` is **refused**, because a panic that aborts takes the host with it.
5. Parse the manifest and resolve dependencies, rejecting missing providers, cycles and name clashes.
6. Initialize, take the vtable, attach the transport.

Each module declares its interface in its own small `*-bus` contract crate: the interface name, the object path, one constant per member, and a contract version. The bind rule is majors equal **and** the module's minor at least the host's, so a newer module serves an older host and the reverse is refused rather than half-working. Never redeclare a contract type in OpenHuman, and call members through the contract's constants rather than string literals.

## Faults are terminal

Of the eleven lifecycle states, five are terminal: rejected, faulted, failed, stopped and disabled. A module in one of those answers "unavailable" immediately and is **never retried in the same process**.

That is the direct consequence of the other rule: **the loader never unloads a library.** A stopped module releases its transport and its names, but its code, thread-locals, panic metadata and callback addresses stay mapped until the process exits. Replacing an artifact needs a restart. Retrying a faulted module in place would be running code whose invariants you already know are broken.

Untrusted code does not belong here. It belongs in a separate process, which is what the sandbox backends are for.

## Configuration

```toml
[modules]
enabled = true          # off means the features say so, rather than failing at use
allow_download = true   # false suits an air-gapped or reproducible deployment
# install_dir = "…"     # defaults to the user cache dir, then the workspace
```

Nothing is downloaded silently either way: the digest comes from the compiled-in registry rather than from the release being fetched.

The `modules` RPC namespace exposes `list`, `status` and `load` (by id, never by path), plus `computer_status` and `browser_check_readiness` for the computer module's own readiness, and `browser_forget_sites`, which forgets what browser tasks learned about one site or every site (see [jev.md](jev.md)).

## Adding or moving one

A module's behaviour belongs in the submodule that owns it, not here. The host side is the adapter: the proxy, the config it pushes at initialization, and the policy around the call. When you change a module:

1. Land the change upstream and cut a release there.
2. Move the gitlink under `vendor/`.
3. Update the record's version, release URL and digests from that release's checksum file.
4. Test both the gate-on and gate-off builds, since a leaf gate's absence should mean "absent", not "present and failing".

## See also

- [Architecture](architecture/README.md): where modules sit relative to the core.
- [Building the Rust core](building-rust-core.md): the feature gates that decide what compiles.
- [Performance and footprint](performance.md): what the lazy-loading trade is worth.
