# OpenAkita Bootstrap Resources

This directory is packaged into the Tauri desktop app and is intentionally
small. It bootstraps the mutable runtime environments under:

```text
~/.openakita/runtime/app-venv
~/.openakita/runtime/agent-venv
```

Expected packaged files:

- `manifest.json`: bootstrap metadata consumed by the Tauri runtime manager.
- `bin/uv` or `bin/uv.exe`: uv binary for creating venvs and installing wheels.
- `wheels/openakita-<version>-py3-none-any.whl`: OpenAkita wheel for app runtime.
- `wheelhouse/`: optional enterprise/offline dependency wheelhouse.
- `python/`: platform-specific standalone Python seed used to create the managed venvs.

`build/prepare_bootstrap_resources.py` defaults to a gitignored staging output
under `build/bootstrap-output` for local validation. CI/release and the local
desktop packaging scripts pass `--commit-resources` to write into this directory
intentionally. Do not commit generated Python, `bin/uv*`, or wheel files from a
local run unless you are updating tracked release bootstrap metadata on purpose.

The Python seed is a slim standalone interpreter, not a preinstalled OpenAkita
environment. Application dependencies remain in the mutable managed venvs so
upgrades do not require replacing the desktop installation.
