# Code Coverage Reference

## Purpose

Parse, merge, and report code coverage metrics. Coverage collection commands are sourced from Stage 0 Repo Context memory (`/memories/repo/test-gen-context-<repo-name>.md`). `.coverage-progress.json` holds runtime state only (coverage numbers, iteration, status). This file covers parsing and merging only.

## Available Scripts

This skill includes two PowerShell scripts under `scripts/`:

- **`scripts/parse-cobertura.ps1`** -- Parse Cobertura XML coverage reports into structured JSON. Supports merging multiple files.
- **`scripts/parse-coverage-text.ps1`** -- Parse text-based coverage output (pytest term-missing, Jest/Vitest tables) into structured JSON. Auto-detects format.

Both scripts:
- Are self-contained PowerShell (no external dependencies)
- Support `Get-Help` for usage details
- Emit structured JSON to stdout, status messages to the host
- Accept `-Threshold` to fail with exit code 1 when coverage is below a target
- Accept `-Bottom N` to highlight the N lowest-coverage files
- Accept `-Output FILE` to write JSON to a file instead of stdout

## Important: Use a Temp Directory

**NEVER write coverage files into the repository.** Use `[System.IO.Path]::GetTempPath()` or `$env:TEMP`, not a subdirectory of the repo. Paths like `<repo>/coverage-iter1/` or `<repo>/coverage/` are violations — these will be picked up by git status and risk being committed.

```powershell
# CORRECT — outside the repo:
$coverageDir = Join-Path ([System.IO.Path]::GetTempPath()) "code-coverage-$(Get-Random)"
New-Item -ItemType Directory -Path $coverageDir -Force | Out-Null

# WRONG — inside the repo:
# $coverageDir = Join-Path $repoRoot "coverage-iter1"   ← NEVER DO THIS
```

After parsing results, clean up: `Remove-Item -Recurse -Force $coverageDir`

## Parsing Coverage Results

### Cobertura XML

```powershell
# Single file
.\scripts\parse-cobertura.ps1 coverage.cobertura.xml

# Multiple files (merged automatically)
.\scripts\parse-cobertura.ps1 coverage1.xml coverage2.xml

# With threshold check (example: 100% default; use `.coverage-progress.json` target instead of hardcoded values)
.\scripts\parse-cobertura.ps1 .\coverage\**\coverage.cobertura.xml -Threshold 100
```

### pytest text output

```powershell
pytest --cov=src --cov-report=term-missing | pwsh scripts/parse-coverage-text.ps1
```

### Jest / Vitest text output

```powershell
npx jest --coverage > jest-output.txt 2>&1
.\scripts\parse-coverage-text.ps1 -Input jest-output.txt -Format jest
```

### Script Output Format

Both scripts produce JSON with this structure:

```json
{
  "summary": {
    "line_rate": 85.0,
    "branch_rate": 72.0,
    "lines_valid": 1412,
    "lines_covered": 1200,
    "lines_uncovered": 212
  },
  "files": [
    {
      "filename": "src/MyClass.cs",
      "line_rate": 88.0,
      "branch_rate": 75.0,
      "uncovered_lines": ["15", "22-30"]
    }
  ],
  "bottom_files": [
    { "filename": "src/Bar.cs", "line_rate": 65.1 }
  ]
}
```

### Manual Parsing Reference

If scripts cannot be used:

- **Cobertura XML**: `line-rate` attribute on `<coverage>` root (multiply by 100 for %). Uncovered: `<line>` elements where `hits="0"`.
- **pytest text**: Match lines like `src/foo.py  120  15  88%  45-50, 102`. TOTAL row at the bottom.
- **Jest/Vitest text**: Table rows with `| % Stmts | % Branch | % Funcs | % Lines | Uncovered Line #s`. "All files" row is the summary.

## Multi-Language Report Merging

When a repo contains multiple languages, collect coverage for ALL languages and merge into a single report (mirrors CI behavior).

1. Run each module's coverage command (from repo context memory) into `$coverageDir` with distinct filenames per language.
2. Merge with `parse-cobertura.ps1`:
   ```powershell
   $allReports = Get-ChildItem $coverageDir -Recurse -Filter "*.cobertura.xml" | ForEach-Object { $_.FullName }
   .\scripts\parse-cobertura.ps1 @allReports
   ```
3. Report per-language AND merged totals. Include a row for EVERY detected language.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Unable to build before collecting coverage | Check readme.md or copilot-instructions.md for build guidance. Run NuGet restore first. |
| Multiple test projects produce separate reports | Pass all files to `parse-cobertura.ps1` (it merges automatically). |
| Coverage % seems artificially high | Check for trivial code (DTOs, auto-properties) inflating numbers -- consider excluding them. |
| Coverage tools not installed | Report what needs installing with install commands. Do not fail silently. |
