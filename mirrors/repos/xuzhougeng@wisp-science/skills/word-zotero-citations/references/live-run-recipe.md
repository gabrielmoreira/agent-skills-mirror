# Reproducible live run recipe

This is the parameterized, machine-independent sequence used for the
2026-08-15 end-to-end test. Everything under `scripts/` is self-contained in
this Skill; only the zotero-mcp package itself is external.

## Preconditions (read this before starting)

1. **Zotero desktop** must be running (Local API on `127.0.0.1:23119`).
   First install/launch it, then verify the port listens.
2. **Microsoft Word** must be installed (COM automation). Only the live
   Refresh and UI-evidence steps need it; scanning/building/auditing are
   OOXML-only and work without Word.
3. **The `zotero_mcp` package** must be importable by Python:
   - if you have the zotero-mcp repository, set
     `$env:PYTHONPATH="<zotero-mcp>/src"` (or use its `.venv`);
   - otherwise install it in the active environment and confirm with
     `python -c "import zotero_mcp"`.
   The Skill scripts are self-contained; only this package is external.
4. **zotero-mcp hybrid mode** must be configured so writes work. Follow
   `zotero-mcp-configuration.md` and set `ZOTERO_LIBRARY_ID` +
   `ZOTERO_API_KEY` (+ `ZOTERO_LIBRARY_TYPE=user`, `ZOTERO_LOCAL=true`) in
   `~/.config/zotero-mcp/config.json`, then **restart the zotero-mcp
   connector** so it re-reads the file.
5. Confirm everything before a live run:
   ```powershell
   python -c "import zotero_mcp; print(zotero_mcp.__file__)"
   python -m zotero_mcp.word_citations.refresh --help   # imports the verifier
   ```
   Then continue with Step 0.

## Step 0 — prepare the Zotero task collection and item selection

1. `zotero_list_libraries` → note the personal user ID.
2. `zotero_switch_library(library_id=<user ID>, library_type='user')`.
3. `zotero_create_collection(name='<task collection>')` → capture key.
4. For every distinct DOI in the document: verify an item exists in the
   library, choose one item per DOI (never merge/delete duplicates), and add it
   to the collection. Write `zotero-item-selection.json`:

```json
{
  "schema_version": 1,
  "library_type": "user",
  "library_id": "<user ID>",
  "collection_name": "<task collection>",
  "collection_key": "<8-char key>",
  "selections": [
    {"doi": "10.1000/example", "selected_item_key": "ABCD1234",
     "candidate_item_keys": ["ABCD1234", "WXYZ5678"]}
  ]
}
```

## Step 1 — offline candidate build and static audit

```powershell
$env:PYTHONPATH="<zotero-mcp>/src"
python scripts/run_live_workflow.py candidate-build `
  --run-root "<isolated run root>" `
  --task-id "<task id>" `
  --source "<original docx>" `
  --style-id "http://www.zotero.org/styles/apa" `
  --selection "<zotero-item-selection.json>"
```

Outputs: `input/source.docx`, `input/citation-manifest.json`,
`output/documents/candidate-pre-refresh.docx`,
`output/tables/pre-refresh-static-audit.json`.

## Step 2 — one-shot Refresh authorization + wrapper

```powershell
python scripts/run_live_workflow.py authorize `
  --run-root "<isolated run root>" --attempt-id "attempt-001"

powershell -NoProfile -ExecutionPolicy Bypass `
  -File scripts/refresh_word_zotero.ps1 `
  -Authorization "<run>/output/tables/refresh-authorization.json" `
  -PythonExecutable "<venv>/Scripts/python.exe" `
  -TimeoutSeconds 600 -StableSeconds 5
```

The wrapper verifies authorization + Local API visibility, opens Word once,
calls `ZoteroRefresh` exactly once, never retries, writes an atomic report, and
only on failure creates a diagnostic copy. A failed attempt must be followed
by a **new** `--attempt-id` (fresh authorization paths) — never a re-run of the
same authorization.

## Step 3 — post-Refresh static audit

```powershell
python scripts/run_live_workflow.py post-refresh-audit `
  --run-root "<isolated run root>"
```

Validates the wrapper report (one macro call, hashes unchanged) and freezes
`output/tables/post-refresh-static-audit.json`.

## Step 4 — cancelled disposable UI evidence (two runs)

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File scripts/validate_word_zotero_ui.ps1 `
  -Authorization "<run>/output/tables/refresh-authorization.json" `
  -Mode citation `
  -WorkingCopy "<run>/output/documents/ui-working-copy-citation.docx" `
  -Report "<run>/output/tables/ui-citation-report.json" `
  -PythonExecutable "<venv>/Scripts/python.exe"

# same with -Mode bibliography and the bibliography paths
```

Each run opens a disposable copy of the destination, calls the Zotero dialog
macro once, recognizes the Zotero window (`MozillaDialogClass`), cancels it,
closes Word without saving, and proves source/destination/working-copy hashes
unchanged.

## Step 5 — freeze finalization

```powershell
python scripts/run_live_workflow.py finalize --run-root "<isolated run root>"
```

Freezes `ui-citation-evidence.json`, `ui-bibliography-evidence.json`, and the
write-once `finalization.json`.

## Step 6 — final delivery

1. Propose a delivery directory and a final name (e.g. `<original-stem>_引文完成版.docx`).
2. Wait for the user to confirm the name and path; never choose them yourself.
3. Copy exactly two files into the delivery directory: the finalized DOCX and a
   copy of the original DOCX (never move/modify the original).
4. Record the SHA-256 of both copies and compare with the finalization record.
   If the user has opened/saved the finalized DOCX in Word after finalization,
   the hash will differ — deliver the user-confirmed bytes and note the
   difference; the finalization record stays bound to the audited bytes.
5. Test/intermediate artifacts never enter the delivery directory.

## Failure iteration policy

- Keep every attempt's candidate, audit, authorization, report, and diagnostic.
- Each attempt uses a new `attempt-id` and new output paths.
- Fix the root cause offline (with a regression test), re-run the offline
  phases, then request one fresh authorization per live attempt.
- Never automate re-execution of the same authorization.

## Known real-world behaviors baked into the contracts (2026-08-15)

1. Word rejects a candidate whose `word/document.xml` drops `mc:Ignorable`-referenced
   namespace declarations ("文件可能已经损坏" / file may be corrupted). The
   builder preserves the full source namespace set; the audit test asserts zero
   missing prefixes.
2. After Refresh, Zotero rewrites `citationItems[].id` (and `itemData.id`) to
   local database numbers and renders results in the document style (author-year
   for APA, not superscript). Post-Refresh audits bind identity via stable
   `uris` item keys + DOI/PMID metadata + order; build audits remain strict.
3. The Local API collection listing includes attachments/notes; visibility
   checks skip those item types and require exactly the authorized top-level
   item keys.
