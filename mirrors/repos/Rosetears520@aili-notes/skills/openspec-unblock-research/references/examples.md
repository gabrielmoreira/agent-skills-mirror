# Examples

## Example blocked_context (Worker → Supervisor)

```json
{
  "blocker_summary": "pytest fails due to ImportError in xili.cli",
  "error_excerpt": "ImportError: cannot import name 'X' from 'xili' (D:\\\\python_project\\\\XiLiSuite\\\\xili\\\\__init__.py)",
  "symptoms": [
    "fails every run on Windows",
    "only after upgrading dependency Y"
  ],
  "already_tried": [
    { "action": "uv run -- pytest -q", "result": "same ImportError" },
    { "action": "checked xili/__init__.py exports", "result": "X not exported" }
  ],
  "needs": [
    "full traceback",
    "dependency versions: uv lock / pip freeze equivalent"
  ],
  "environment": {
    "os": "Windows 11",
    "shell": "powershell",
    "runtime": { "name": "python", "version": "3.11.7" },
    "tools": [
      { "name": "uv", "version": "0.4.0", "how_verified": "uv --version" }
    ]
  }
}
```

## Example sinks (caller-configured)

```json
[
  { "type": "json_file", "content": "report_json", "path": "runs/unblock/report.json" },
  { "type": "markdown_insert_after_anchor", "content": "guidance_md", "path": "tasks.md", "anchor": "## BLOCKED", "allow_fallback_append": false },
  { "type": "return_only", "content": "both" }
]
```

## Example guidance rendering (guidance_md)

- **Facts**
  - Error: `ImportError: ...`
  - Repro: `uv run -- pytest -q`
- **Key conclusions**
  - (high) `xili.__init__` no longer exports `X`; imports must use `xili.foo.X` (evidence: `ev:repo:...`)
- **Unblock steps**
  1. Change `from xili import X` → `from xili.foo import X`; verify via `uv run -- pytest -q`.
  2. If still failing, print import graph via `python -X importtime -c "import xili"` and attach output.

