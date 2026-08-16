# Implementation map

Use this map after the Skill has triggered and the task requires source inspection or modification. The implementation is generic; historical case-specific rebuild scripts are reference-only and must not be imported.

## Package boundary

Primary Python package: `src/zotero_mcp/word_citations/`

| Area | Module | Responsibility |
|---|---|---|
| Shared contracts | `models.py` | Enums and immutable records shared by preflight, scanning, clustering, run layout, and reports. |
| Run layout and hashes | `state.py` | Task ids, canonical paths, SHA-256, atomic copy/write, lineage journal, locks, recovery, rollback proposals. |
| Read-only gate | `preflight.py` | Environment, source, style, Zotero profile/database, path, and permission-intent inspection without mutation. |
| Static DOCX discovery | `docx_scan.py` | ZIP/OOXML story traversal, identifier recognition, field/revision/static-reference findings. |
| Cluster inference | `clustering.py` | Deterministic identifier grouping and explicit manual-review boundaries. |
| Zotero planning | `zotero_stage.py` | Read/write gateway protocols, item-resolution plans, explicit staging authorization, visibility verification. |
| OOXML field construction | `ooxml_fields.py` | Citation payloads, complex citation and bibliography fields, document preferences, OPC metadata. |
| Placement/candidate build | `placement.py`, `docx_build.py` | Frozen placement edits and protected candidate-package construction. |
| Frozen acceptance | `manifest.py` | Strict citation manifest, source binding, acceptance contract, canonical write-once persistence. |
| Static audit | `audit.py` | Parse candidate/destination fields, audit document data and counts, persist strict audit evidence. |
| Refresh gate | `refresh.py` | Digest-bound Refresh authorization and restricted read-only Local API visibility checks. |
| Post-Refresh closeout | `finalize.py` | Strict Refresh report loading, UI evidence, post-Refresh binding, write-once finalization. |
| CLI | `cli.py` | Side-effect-free top-level import; read-only preflight/scan plus lazy offline commands. |
| UI evidence | `scripts/word_citations/validate_word_zotero_ui.ps1` | Cancelled disposable Word/Zotero dialog evidence for citation and bibliography modes. |

## PowerShell boundary

`scripts/word_citations/refresh_word_zotero.ps1` is the sole live Word wrapper. Static inspection must verify:

- Python authorization and optional visibility gates occur before COM creation;
- a dedicated Word instance is created;
- `ZoteroRefresh` appears exactly once and has no retry loop;
- source and candidate digests are checked before and after;
- `Visible` and `DisplayAlerts` are restored;
- report writing is atomic;
- diagnostic copy is failure-only.

Parsing the file with the PowerShell AST is safe. Executing it is a separate live authorization event.

## CLI surface

Installed entry point:

```text
zotero-word-citations = zotero_mcp.word_citations.cli:main
```

Equivalent repository invocation:

```text
python -m zotero_mcp.word_citations.cli --help
```

Top-level mode performs read-only preflight and scanning. Lazy offline commands are:

- `audit`
- `finalize`
- `recover`
- `rollback-proposal`

Live Refresh is intentionally not exposed as an ordinary CLI subcommand.

## Tests by phase

Tests live under `tests/word_citations/`.

- Phase 0–3: `test_state.py`, `test_preflight.py`, `test_docx_scan*.py`, `test_clustering.py`
- Phase 4–5: `test_zotero_stage.py`, `test_zotero_stage_execution.py`, `test_ooxml_fields.py`
- Phase 6–7: placement/build/manifest tests
- Phase 8: `test_audit.py`
- Phase 9: `test_refresh.py`, `test_refresh_wrapper_contract.py`
- Phase 10: `test_finalize.py`
- Phase 11: `test_state.py`
- Phase 12: CLI contract tests, `test_package_boundary.py`, `test_protected_baseline.py`

`tests/word_citations/__init__.py` deliberately isolates its local `conftest.py` from the repository root `tests/conftest.py`.

## Documentation

Repository documentation:

- `docs/word-citations/README.md`
- `docs/word-citations/implementation-map.md`
- `docs/word-citations/protected-baseline.json`

When behavior changes, update package tests and repository docs together. Do not invent dependency versions; read them from the active runtime, lock file, or package metadata, otherwise report `unavailable`.
