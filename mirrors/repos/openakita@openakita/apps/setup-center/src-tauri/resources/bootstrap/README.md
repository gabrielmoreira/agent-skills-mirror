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

The bootstrap package must not contain a full Python or conda environment. If a
Python seed is added later, keep it explicit in `manifest.json` and small enough
to preserve the lightweight installer goal.
