---
name: run
aliases:
  - execute
mcp_tool: ouroboros_execute_seed
mcp_args:
  seed_path: "$1"
  cwd: "$CWD"
  summary: "seed=$1 cwd=$CWD"
---
# Run

This fixture keeps dispatch metadata in YAML frontmatter while the markdown
body contains text that looks similar enough to catch accidental whole-file
parsing.

```yaml
mcp_tool: body_should_not_be_loaded
mcp_args:
  seed_path: body-value
  cwd: body-cwd
aliases:
  - body-alias
```

The router must ignore the body above when loading dispatch metadata.
