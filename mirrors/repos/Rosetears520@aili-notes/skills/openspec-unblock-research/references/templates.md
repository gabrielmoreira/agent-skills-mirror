# Templates

## Minimal required input (blocked_context)

Copy and fill. Use exact error text for `error_excerpt` when available.

```json
{
  "blocker_summary": "",
  "error_excerpt": null,
  "symptoms": [],
  "already_tried": [],
  "needs": [],
  "environment": {
    "os": "",
    "shell": "",
    "runtime": { "name": "", "version": "" },
    "tools": []
  }
}
```

### already_tried item template

```json
{ "action": "", "result": "", "evidence": [] }
```

### tools item template

```json
{ "name": "", "version": "", "how_verified": "" }
```

## Minimal sink config templates

### Return only (no writes)

```json
[
  { "type": "return_only", "content": "both" }
]
```

### Write JSON report + append markdown guidance

```json
[
  { "type": "json_file", "content": "report_json", "path": "runs/unblock/report.json" },
  { "type": "markdown_append", "content": "guidance_md", "path": "runs/unblock/guidance.md" }
]
```

### Insert guidance after anchor (no implicit fallback)

```json
[
  {
    "type": "markdown_insert_after_anchor",
    "content": "guidance_md",
    "path": "tasks.md",
    "anchor": "## BLOCKED",
    "allow_fallback_append": false
  }
]
```

## guidance_md rendering template (portable)

Render as a single markdown block. Keep it stable for diffability and audit.

```md
## Unblock Report

### Facts
- Blocker: ...
- Error excerpt: `...` (or "none")
- Repro: `...` (or "unknown")
- Environment: OS=..., runtime=..., tools=...

### Unknowns / NEEDS
- ...

### Query terms
- ...

### Key conclusions
- (high|medium|low) ... (evidence: ev:...)

### Evidence pointers
- ev:...: url/path/cmd

### Open questions
- Q: ...
  - Why: ...
  - How to answer: `command` / `file path`

### Unblock steps
1. Action: ...
   - Why: ...
   - Verify: `...`
   - Fallback: ...
```

