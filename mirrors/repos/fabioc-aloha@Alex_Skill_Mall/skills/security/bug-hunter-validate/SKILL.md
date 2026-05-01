---
type: skill
lifecycle: stable
inheritance: inheritable
name: validate
description: Validate Bug Hunter scan output against the JSON schema. Checks for missing fields, invalid types, and out-of-range values.
tier: standard
applyTo: '**/*bug*,**/*hunter*,**/*validate*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Bug Hunter Validate Output

Validate the scan output file against the expected JSON schema.

## What to do

Run the validation script:

```bash
node "${PLUGIN_ROOT}/scripts/validate-output.js" .bug-hunter/last-scan-output.json
```

If the user specifies a different output file (e.g., a per-model output), validate that instead:

```bash
node "${PLUGIN_ROOT}/scripts/validate-output.js" <path-to-output-file>
```

Show the validation result to the user. If validation fails, explain which fields have issues.

## Error Handling

- **File not found**: If the specified output file doesn't exist, report: `"Output file not found at <path>. Run a scan first to generate output."` Do NOT create a dummy file.
- **Invalid JSON**: If the file contains malformed JSON, report the parse error with position. This usually means the scan was interrupted — suggest re-running.
- **Node.js not available**: If `node` is not on PATH, report the error and suggest installing Node.js or checking PATH.
- **Script not found**: If `validate-output.js` is missing, the plugin may not be installed correctly.

## Examples

**Validation passes:**
```
✅ Schema validation passed.
  - schemaVersion: 1.0
  - candidates: 5
  - All required fields present
  - Severity values valid (1-4)
  - Confidence values in range (0.0-1.0)
```

**Validation fails:**
```
❌ Schema validation failed:
  - candidates[2].severity: expected 1-4, got 5
  - candidates[3].confidence: expected 0.0-1.0, got 1.5
  - summary.filesScanned: missing required field
```

## Safety Boundaries

- **Read-only operation**: Validation NEVER modifies the output file or any other file.
- **ONLY** validate files inside the current repository. Reject absolute paths or paths containing `..`.
