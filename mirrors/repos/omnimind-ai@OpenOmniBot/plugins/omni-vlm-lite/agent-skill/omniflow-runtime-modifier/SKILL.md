---
name: omniflow-runtime-modifier
description: Safely inspect, edit, validate, hot reload, and recover the OmniFlow Python runtime inside OpenOmniBot. Use when changing the VLM planner, prompts, GUI execution policy, replay, retry, checker, Function, or RunLog behavior through the official OmniFlow developer override tools.
---

# Modify OmniFlow Runtime

Treat the packaged runtime as immutable. Make focused Python edits through the Android-managed
developer override.

## Workflow

1. Call `get_omniflow_python_override` without a path and record the runtime version and modified
   files.
2. Call it again with the exact `omniflow/**/*.py` path to read current source and SHA-256.
3. Change one owning file with the smallest coherent edit.
4. Call `apply_omniflow_python_override` with the path and complete file content. It validates Python
   syntax, restarts the worker, checks the runtime contract, and rolls back on failure.
5. Exercise the affected operation. Use `reload_omniflow_python_override` only when a clean worker
   restart is needed without another edit.
6. If the override is unhealthy, call `clear_omniflow_python_override` with `confirm=true` to restore
   the pinned runtime.

## Ownership

- Modify planner and prompts under `omniflow/vlm/`.
- Modify retry, checker, replay, and execution policy under `omniflow/runtime/`.
- Modify Function and RunLog behavior in their OmniFlow packages.
- Do not modify, replace, or emulate OmniTransfer. Failed target mappings must use the normal VLM
  fallback and must never replay source-device coordinates silently.
- Do not weaken payment confirmation or other user-consent boundaries.

Apply whole-file content only. Never write directly into the pinned runtime installation directory.
