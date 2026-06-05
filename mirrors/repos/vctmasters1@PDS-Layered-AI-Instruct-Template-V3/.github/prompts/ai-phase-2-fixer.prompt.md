---
mode: agent
description: Phase 2 Fixer - Apply HIGH-priority compliance findings to project structure, documentation, and security. Routes through governance pipeline (Router → Supervisor → Workers).
---

# `/ai-phase-2-fixer` — Phase 2 Compliance Fixer

**Purpose**: Execute Phase 2 of the AI-INSTRUCT adoption pipeline: take the compliance findings from Phase 5 (analyzer), apply HIGH-priority security fixes, migrate project structure to V5 naming conventions, and generate governance documentation (.ai/instruct.md + README.md files).

**Governance**: This command routes through the full agent delegation pipeline:
- **pds-meta-router**: Analyze scope and delegate
- **pds-pipe-scaffolder**: Plan module structure + HIGH-priority fixes
- **pds-man-naming**: Validate V5 naming conventions
- **pds-pipe-generator**: Produce files (`.ai/instruct.md`, `README.md`, `.gitignore` updates)
- **pds-pipe-validator**: Compliance check
- **pds-pipe-reviewer**: Final validation before user approval

---

## Usage

### Interactive Mode (Recommended)

```
/ai-phase-2-fixer
```

This will:
1. Ask you to confirm the compliance report location
2. Ask which priority level(s) to apply (HIGH, MEDIUM, LOW)
3. Generate a structured **plan** showing all changes
4. Wait for your **approval** before executing
5. Execute approved changes with audit logging

### Direct Mode (Advanced)

```
/ai-phase-2-fixer HIGH k:\PDS-Master-001
```

This will:
- Parse the compliance report in `k:\PDS-Master-001\.compliance-report.json`
- Plan only HIGH-priority fixes (no MEDIUM/LOW)
- Skip interactive confirmation

---

## What Phase 2 Does

### High-Priority Security Fixes (64 findings)
- ✅ Add `.env`, `.env.local`, `.env.*.local` to `.gitignore`
- ✅ Move unencrypted credential files to proper locations
- ✅ Validate certificate file permissions
- ✅ Ensure root-level `README.md` exists
- ✅ Create root-level `CONTRIBUTING.md`
- ✅ Migrate `.ai/` directory structure to V5 standards

### Module Structure Migration
- ✅ Convert directory names to kebab-case (V5 convention)
- ✅ Create `.ai/instruct.md` for each module
- ✅ Create `README.md` for modules lacking documentation
- ✅ Establish depth-priority instruction hierarchy
- ✅ Validate naming against V5 conventions

### Governance Documentation
- ✅ Generate scoped `.ai/instruct.md` per module
- ✅ Link to cross-cutting rules (conventions, maintenance, credentials)
- ✅ Establish audit trail via `.ai/logs/phase-2-*.jsonl`

---

## Workflow

```
User invokes /ai-phase-2-fixer
  ↓
Router analyzes scope + priorities
  ↓
Scaffolder plans module structure + HIGH fixes
  ↓
Naming agent validates V5 conventions
  ↓
Generator produces .ai/instruct.md, README.md, .gitignore
  ↓
Validator checks compliance
  ↓
Reviewer performs final approval gate
  ↓
[AWAIT USER APPROVAL]
  ↓
Execute approved changes with audit logging
  ↓
Update .ai/index.md
  ↓
Report results
```

---

## Input: Compliance Report

Expects `<project>/.compliance-report.json` in format:

```json
{
  "project": "PDS-Master-001",
  "timestamp": "2026-06-04T...",
  "findings": [
    {
      "id": "finding-001",
      "severity": "error",
      "category": "security",
      "path": "device/pds/file.py",
      "message": "Unencrypted .env file in git",
      "suggested_fix": "Add .env to .gitignore",
      "llm_priority": "high",
      "llm_notes": "Credential exposure risk"
    }
  ],
  "summary": {
    "total": 639,
    "by_priority": { "high": 64, "medium": 256, "low": 30 }
  }
}
```

---

## Output: Execution Plan

Before making any changes, Phase 2 generates and displays:

```json
{
  "plan_id": "phase-2-20260604-001",
  "summary": {
    "high_priority_findings": 64,
    "modules_affected": 12,
    "files_to_create": 15,
    "files_to_modify": 8
  },
  "modules": [
    {
      "name": "api-server",
      "current_path": "web-firmware-server",
      "action": "migrate",
      "fixes": [
        { "finding": "Unencrypted .env in git", "fix": "Add .env to .gitignore" }
      ],
      "files_to_generate": [".ai/instruct.md", "README.md"],
      "naming_valid": true
    }
  ],
  "governance": {
    "conventions_checked": true,
    "archive_rules_applied": true,
    "credentials_protected": true,
    "naming_validated": true
  },
  "next_step": "User approval required. Type 'approve' to execute or 'cancel' to review."
}
```

---

## Rules Applied

- **Archive-first**: Any file being replaced is archived to `.archive/` per [maintenance.md](../../.ai/maintenance.md)
- **Depth-priority**: Module `.ai/instruct.md` is always more authoritative than root
- **Never relax security**: All HIGH-priority credential/exposure fixes are mandatory
- **V5 naming**: All directory/file names follow [conventions.md](../../.ai/conventions.md)
- **Credential safety**: All `.env`, certificates, and API keys use [credentials.md](../../.ai/credentials.md) rules

---

## Approval Gate

After the plan is displayed, you must explicitly approve:

```
Approve Phase 2? [high: 64 fixes, 12 modules]
Type 'approve' to execute or 'cancel' to abort.
> _
```

Phase 2 will **not** proceed without explicit user approval.

---

## Audit Trail

All changes are logged to `.ai/logs/phase-2-*.jsonl`:

```json
{
  "timestamp": "2026-06-04T14:30:00Z",
  "event": "phase-2-execution-start",
  "plan_id": "phase-2-20260604-001",
  "priority": "high",
  "findings_applied": 64
}
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Compliance report not found" | Verify `<project>/.compliance-report.json` exists; run Phase 5 analyzer first |
| "Naming validation failed" | Review proposed module names; validate against [conventions.md](../../.ai/conventions.md) |
| "Archive path already exists" | Stale archive found; move manually to `.archive/YYYYMMDD/` or increment date |
| "Depth-priority conflict" | Check if parent `.ai/instruct.md` already defines the scope; resolve with deeper authority |

---

## Related Commands

- `/ai-validate` — Run AI-INSTRUCT drift validator (read-only compliance check)
- `/ai-reflect` — Post-task reflection; identify instruction gaps
- `/ai-update-index` — Rebuild `.ai/index.md` after Phase 2 execution
- `/ai-archive` — Manually archive a file using the V5 convention
- `/ai-route` — Route a task through the agent delegation pipeline

---

## See Also

- [`.ai/instruct.md`](../../.ai/instruct.md) — Root project authority
- [`.ai/conventions.md`](../../.ai/conventions.md) — V5 naming standards
- [`.ai/maintenance.md`](../../.ai/maintenance.md) — Archive + safety rules
- [`.ai/index.md`](../../.ai/index.md) — Master section index
- [`.github/copilot-instructions.md`](../../.github/copilot-instructions.md) — AI system meta-instructions
