# Offline verification matrix

Use only offline, static, mocked, and synthetic fixtures unless the user separately authorizes live integration.

## Layer 1: Skill tree

Run:

```text
python scripts/verify_skill.py <skill-directory>
python <skill-creator>/scripts/quick_validate.py <skill-directory>
python <skill-creator>/scripts/package_skill.py <skill-directory> <output-directory>
```

Verify:

- folder and frontmatter names match;
- frontmatter has only `name` and `description`;
- all referenced local files exist one level below the Skill root;
- JSON eval definitions are strict and have at least 3 trigger, 3 non-trigger, and 3 task cases;
- scripts compile and have no network/Word/Zotero side effects;
- archive contains relative paths only and no cache/secret files.

## Layer 2: Focused implementation tests

Choose tests matching touched modules. For Phases 8–12 include at minimum:

```text
tests/word_citations/test_audit.py
tests/word_citations/test_refresh.py
tests/word_citations/test_refresh_wrapper_contract.py
tests/word_citations/test_finalize.py
tests/word_citations/test_state.py
tests/word_citations/test_cli_phase12_contract.py
tests/word_citations/test_package_boundary.py
```

Tests must use temporary DOCX packages, mocked HTTP/read gateways, synthetic reports, and fake process/clock data. Never run the wrapper as a test. Post-Refresh audit tests must accept Zotero-managed numeric `citationItems[].id` values and style-rendered results while still requiring stable `uris` item keys; build-phase tests keep item keys and superscript placeholders strict. Candidate-build tests must assert that `mc:Ignorable`-referenced namespace declarations survive serialization.

## Layer 3: Complete Word-citations suite

```text
python -m pytest tests/word_citations -q
```

A valid result completes with pytest exit code 0. Record exact passed/skipped counts.

## Layer 4: Static quality

```text
ruff check src/zotero_mcp/word_citations tests/word_citations
```

Include any adjacent file changed to make the suite portable or isolated.

Parse, but do not execute, PowerShell:

```powershell
$tokens = $null
$errors = $null
[System.Management.Automation.Language.Parser]::ParseFile(
  (Resolve-Path 'scripts\word_citations\refresh_word_zotero.ps1'),
  [ref]$tokens,
  [ref]$errors
) | Out-Null
if ($errors.Count -ne 0) { throw $errors }
```

Run protected baseline verification:

```text
python -m pytest tests/word_citations/test_protected_baseline.py -q
```

## Layer 5: Full project regression

Run with explicit exit propagation:

```powershell
& '.\.venv\Scripts\python.exe' -m pytest -q
$code = $LASTEXITCODE
Write-Output "__PYTEST_EXIT_CODE__=$code"
exit $code
```

If output contains `FAILED`, collection errors, timeout dumps, `KeyboardInterrupt`, or an incomplete summary, do not accept a host-level exit 0. Re-run with verbose output and thread-based pytest timeout to identify the exact test.

## Package-boundary checks

Verify in a fresh Python subprocess that importing `zotero_mcp.word_citations.cli` does not eagerly load:

- `win32com`;
- `pythoncom`;
- `pyzotero`;
- server/write modules.

Do not test this against the current pytest process because another test may already have imported those modules.

## Safety assertions

Static tests should prove:

- no case-specific historical imports;
- wrapper has one `ZoteroRefresh` call and no retry;
- diagnostic copy is failure-only;
- Local API URL restrictions are strict;
- write-once artifacts reject conflicts and tampering;
- recovery never advances past invalid lineage;
- rollback proposal never deletes or overwrites;
- source and candidate hashes are protected.

## Completion threshold

Completion requires all applicable layers to pass. If a dependency is unavailable, record the exact unavailable check rather than substituting a lower-quality test or inventing a version.

Always disclose: Word not launched; Refresh wrapper not executed; Zotero not modified.
