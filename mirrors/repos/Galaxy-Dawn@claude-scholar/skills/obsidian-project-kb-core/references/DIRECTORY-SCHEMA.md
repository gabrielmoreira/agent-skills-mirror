# Directory Schema

The only default project root is:

```text
Research/{project-slug}/
```

Required files and folders:

```text
00-Hub.md
01-Plan.md
02-Index.md
Sources/
  Papers/
  Web/
  Docs/
  Data/
  Interviews/
  Notes/
Knowledge/
Experiments/
Results/
  Reports/
Writing/
Daily/
Maps/
Archive/
_system/
  registry.md
  schema.md
  lint-report.md
```

Defaults:
- `Sources/Papers/` is the only default paper-note directory.
- `Results/Reports/` is the default subdirectory for round or batch experiment reports.
- `Maps/` contains derived artifacts only.
- `Daily/` is preserved by default.

Do not create by default:
- top-level `Papers/`
- `project/KB/`
- project-local JSON or YAML note registries
- `.base` files unless explicitly requested
