---
name: yaml-config
version: 1.1.1
description: "Reads and writes PyYAML configs with yaml.safe_load, utf-8 pathlib I/O, YAMLError line numbers, and factory-defaults deep-merge for vehicle or app parameters. Use when parsing config.yaml, dumping with sort_keys=False, or merging user overrides. Never call yaml.load without a Loader; not for GitHub Actions workflow YAML or multi-gigabyte JSONL/Parquet dumps."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-14
---

# YAML Configuration Files

## When to Use

Use this skill when:
- Reading or writing YAML configuration files.
- Loading vehicle parameters or robotics configs.
- Parsing config files with proper error handling and safe loading.
- Implementing a "factory defaults + user override" merge pattern.

Trigger keywords: `yaml`, `config`, `configuration`, `safe_load`, `yaml.dump`, `PyYAML`, `vehicle parameters`, `config parsing`.

## Prerequisites

- **Python**: 3.10+
- **PyYAML**: 6.0.1+ — install with `pip install PyYAML`
- **Windows host (primary)**: Use PowerShell for CLI commands. File paths should use `pathlib` for cross-platform safety, but note Windows backslash paths when hardcoding.

## Procedure

### 1. Reading YAML Safely

**HARD RULE**: NEVER use `yaml.load()` without specifying a `Loader`. This is a critical security vulnerability that allows arbitrary code execution (ACE). Always use `yaml.safe_load()` or `yaml.SafeLoader`.

**HARD RULE**: Avoid using `yaml.FullLoader` for untrusted input; always prefer `yaml.SafeLoader` or `yaml.safe_load()`.

```python
import yaml
from pathlib import Path

config_path = Path('config.yaml')

try:
    with config_path.open('r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
except FileNotFoundError:
    config = {}

# Access nested values using .get() to avoid KeyError
value = config.get('section', {}).get('key', 'default_value')
```

### 2. Writing YAML

**HARD RULE**: Always use `sort_keys=False` in `yaml.dump()` if the order of parameters is significant for human readability or version control diffs.

```python
import yaml
from pathlib import Path

data = {
    'settings': {
        'param1': 1.5,
        'param2': 0.1,
        'metadata': {
            'version': '2.0.0',
            'author': 'Engineering Team'
        }
    }
}

output_path = Path('output.yaml')
with output_path.open('w', encoding='utf-8') as f:
    yaml.dump(
        data,
        f,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
        indent=2
    )
```

### 3. Dump Options Reference

| Option | Value | Purpose |
|---|---|---|
| `default_flow_style` | `False` | Forces block style (vertical), essential for human-readable config files. |
| `sort_keys` | `False` | Preserves insertion order of the dictionary; critical for logical grouping in configs. |
| `allow_unicode` | `True` | Ensures non-ASCII characters are written as-is rather than escaped. |
| `indent` | `2` | Standardizes indentation for readability across editors. |

### 4. Error Handling with Line Numbers

Implement comprehensive error catching to prevent application crashes during boot-up due to malformed config files.

```python
import yaml
import logging

logger = logging.getLogger(__name__)

def parse_yaml_config(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.warning(f"Config file {file_path} not found. Using defaults.")
        return {}
    except yaml.YAMLError as e:
        logger.error(f"YAML parse error at line {e.problem_mark.line + 1}: {e}")
        raise SystemExit("Critical configuration error: Invalid YAML syntax.")
```

### 5. Optional Config Loading (Deep Merge Pattern)

This pattern is best practice for providing "Factory Defaults" that can be overridden by a user-provided config file.

```python
import os
import yaml
from pathlib import Path

def load_config(filepath, defaults=None):
    """
    Load config file and merge it over defaults.
    Returns a merged dictionary.
    """
    if defaults is None:
        defaults = {}

    path = Path(filepath)
    if not path.exists():
        return defaults

    try:
        with path.open('r', encoding='utf-8') as f:
            loaded = yaml.safe_load(f) or {}
    except yaml.YAMLError:
        return defaults

    def deep_merge(source, destination):
        for key, value in source.items():
            if isinstance(value, dict):
                node = destination.setdefault(key, {})
                deep_merge(value, node)
            else:
                destination[key] = value
        return destination

    result = defaults.copy()
    return deep_merge(loaded, result)
```

## Pitfalls

- **NEVER** use `yaml.load()` without specifying a `Loader` — arbitrary code execution vulnerability.
- **NEVER** use `yaml.FullLoader` for untrusted input — prefer `yaml.SafeLoader` or `yaml.safe_load()`.
- **NEVER** use `yaml.dump()` without `sort_keys=False` when parameter order matters for readability or VCS diffs.
- **Do not** use YAML for extremely large datasets (multi-gigabyte); use JSONL or Parquet for high-performance data serialization.
- **Always** open files with `encoding='utf-8'` to prevent OS-specific encoding crashes (especially relevant on Windows where the default encoding may be cp1252).
- **Always** access nested config values via `.get()` or a deep merge function to avoid `KeyError` at runtime.
- **Always** catch `yaml.YAMLError` and log line numbers (`e.problem_mark.line + 1`) to aid debugging malformed configs.

## Verification

Run these checks after implementing YAML config handling:

1. **Safe loader check** — verify only `yaml.safe_load` or `yaml.SafeLoader` is used; `yaml.load` is strictly forbidden:
   ```powershell
   Select-String -Path .\*.py -Pattern "yaml\.load\(" | Where-Object { $_.Line -notmatch "Loader" }
   ```
   Expected output: **empty** (no matches).

2. **Dump options check** — confirm `default_flow_style=False` and `sort_keys=False` are used for all `yaml.dump` calls:
   ```powershell
   Select-String -Path .\*.py -Pattern "yaml\.dump"
   ```
   Manually verify each call site includes both options.

3. **Encoding check** — ensure files are opened with `encoding='utf-8'`:
   ```powershell
   Select-String -Path .\*.py -Pattern "open\(" | Where-Object { $_.Line -notmatch "utf-8" }
   ```
   Review any matches for missing encoding.

4. **Missing file test** — test `load_config` with a non-existent path to confirm defaults are returned:
   ```python
   assert load_config('nonexistent.yaml', defaults={'a': 1}) == {'a': 1}
   ```

5. **YAMLError test** — validate that `yaml.YAMLError` is caught and provides a meaningful error message including line numbers.

6. **Nested config test** — verify nested configurations are handled via `.get()` or deep merge to avoid `KeyError`:
   ```python
   assert config.get('section', {}).get('key', 'default_value') == 'default_value'
   ```

## Related Skills

- File I/O handling (`pathlib`)
- Python dictionary manipulation
- Error handling and exception management
- Environment variable management (`os.environ`)
