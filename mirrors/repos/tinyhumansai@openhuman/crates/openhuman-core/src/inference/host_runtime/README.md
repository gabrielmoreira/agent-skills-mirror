# host_runtime

OpenHuman-owned bindings around `tinyinference-local`.

The reusable runtime implementation—Ollama and LM Studio discovery, process
lifecycle, model downloads, status, prompts, vision, and embeddings—lives in
the `tinyinference-local` crate. This directory contains only OpenHuman policy
and integration seams:

- `core.rs`: process-wide service ownership.
- `ops.rs` and `ops/`: RPC operations, prompt access checks, agent dispatch,
  scheduler-gate acquisition, and temporary-file handling.
- `schemas.rs`: OpenHuman controller registration and wire compatibility.
- `service/speech.rs`: OpenHuman STT credential routing and Piper output.
- `service/transcription.rs`: channel-facing transcription adapter shape.

Code here must call TinyInference directly. Do not copy local-runtime behavior
back into this host module.
