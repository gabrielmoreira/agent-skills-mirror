# Scoped Docs Discovery

Safe-change works with both legacy unscoped reconstruction docs and hierarchical scoped docs.

If `docs/agent/SCOPES.md` is absent:
- use the existing top-level `docs/agent/*.md` workflow only

If `docs/agent/SCOPES.md` is present:
- read it during preflight
- match task target paths/files to `path` scopes by longest repo-relative path prefix
- use domain scopes only when task wording, scope tags, or contract links make them relevant
- read nearest matching scope `README.md` only if present
- read only task-relevant scoped docs, then top-level docs as fallback for missing categories or repo-wide rules
- before trusting a path scope, verify the scoped source path still exists; if not, treat scoped docs as historical/stale and fall back to top-level/source evidence
- if multiple scopes match with equal confidence, read all relevant scope summaries and note ambiguity in preflight

Cross-scope contract rule:
- when touched code imports, exposes, serializes, persists, or validates data across module/package/service boundaries, read local scoped `CONTRACTS.md` and linked owner `CONTRACTS.md` if present
- owner contract docs are source of truth; consumer docs describe local usage/risk only
- if contract ownership is unclear, identify it as a risk before implementation
