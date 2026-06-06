---
paths:
  - "src/**/__init__.py"
  - "src/**/*.py"
---

# `__init__.py` and re-export rule

A package's `__init__.py` is its **public facade**. Consumers import from the
package, never from its internal modules.

## Pattern

```python
"""One-paragraph module docstring: what this package is and how to use it."""

from .models import Episode as Episode
from .models import MemCell as MemCell

__all__ = [
    "Episode",
    "MemCell",
]
```

- **Explicit `X as X` redundant-alias form** on each re-export. This is intentional:
  it marks the name as a deliberate public re-export (ruff `F401` / `PLC0414` aware)
  rather than an accidental unused import.
- **`__all__`** lists every public name, alphabetically sorted, matching the
  re-exports. It is the contract; keep it in sync.
- **Internal modules stay private** — don't re-export helpers that aren't part of
  the public API.
- New subpackage? Add an `__init__.py` with a docstring + `__all__` even if it
  starts small. Empty-but-documented beats missing.

This facade discipline is what lets `import-linter` forbid deep imports across
package boundaries (see [architecture.md](architecture.md)).
