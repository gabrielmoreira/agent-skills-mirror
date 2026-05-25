# Structured Scoped Artifact Discovery

Use `<docs-root>/repo/scopes.yaml`. Match path scopes by longest prefix; use domain scopes only by explicit task/domain/contract refs; fallback to repo only when no scope exists. Scoped YAML lives under `<docs-root>/scopes/by-path/<path>/` or `<docs-root>/scopes/by-domain/<slug>/`. Verify path scopes still exist before trusting observed claims.
