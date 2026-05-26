---
mode: agent
description: Run the AI-INSTRUCT drift validator and report findings.
---

# /ai-validate

Run the project's instruction-drift validator and surface results clearly.

## Steps

1. Read [.github/dev-specs.md](../dev-specs.md) to confirm the developer shell and OS.
2. Run the validator from the project root using the platform-appropriate shell:
   - **Windows / pwsh**: `pwsh -NoProfile -File .github/scripts/validate-instructions.ps1`
   - **macOS / Linux** (pwsh installed): same command — `pwsh` works cross-platform.
3. Capture stdout and the exit code.
4. If exit code is `0`: report "Validation passed" and the number of files scanned.
5. If exit code is non-zero: list each reported issue, grouped by category:
   - Unfilled `[DATE]` placeholders
   - Retired `§` syntax
   - Missing `## Contents` TOC tables
   - Frontmatter problems (missing `mode:` / `description:`)
   - Broken or unresolvable relative markdown links
6. For each issue, propose a one-line fix. **Do not auto-edit** unless the user asks — `/ai-validate` is a reporting tool. Filling unambiguous placeholders (e.g. today's date for a stale `**Last Updated**`) is the only safe auto-fix and should still be confirmed first.
7. Exit with a one-sentence summary of action taken or recommended next step (e.g., "Run `/ai-update-index` after fixing the broken links.").

## Notes

- The validator script lives at [.github/scripts/validate-instructions.ps1](../scripts/validate-instructions.ps1). If it is missing, that itself is the finding — instruct the user to restore from git or reinstall the template.
- This prompt does not commit, push, or modify config — it only reads and reports.
