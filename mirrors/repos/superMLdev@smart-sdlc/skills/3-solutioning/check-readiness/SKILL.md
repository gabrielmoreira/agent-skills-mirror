---
name: check-readiness
description: "Verify that all prerequisite artifacts exist and are complete before starting the next phase. Use when the user says 'are we ready to start development', 'check readiness', or 'verify phase prerequisites'."
---

# Readiness Check Workflow

## Goal

Confirm that every required artifact for the upcoming phase is present, complete, and signed off. Produce a clear go / not-ready decision with a specific remediation list for any gaps.

---

## Step 1: Identify the Target Phase

Ask: Which phase are you about to start?
- [ ] Planning (needs: PRD)
- [ ] Architecture (needs: PRD, product sign-off)
- [ ] Team Lead / Sprint Planning (needs: Architecture doc, Epics)
- [ ] Development (needs: Sprint plan, Stories with ACs)
- [ ] QA (needs: Development sign-off, all stories implemented)
- [ ] Release (needs: QA sign-off, release checklist)

---

## Step 2: Check Required Artifacts

For the chosen phase, verify each prerequisite:

Read `_superml/config.yml` and check the `artifacts` section.

| Artifact | Config Key | Status |
|----------|------------|--------|
| PRD | `prd_complete` | ✔ / ✗ |
| Architecture doc | `architecture_complete` | ✔ / ✗ |
| Epics & Stories | `epics_complete` | ✔ / ✗ |
| Dev sign-off | `implementation_signed_off` | ✔ / ✗ |
| QA sign-off | `qa_signed_off` | ✔ / ✗ |

---

## Step 3: Verify File Existence

For each artifact flagged `true` in config, verify the file actually exists:

```
{docsPath}/product/prd.md
{docsPath}/architecture/architecture.md
{docsPath}/planning/epics.md
```

If a flag is `true` but the file is missing: flag as **INCOMPLETE** (config/file mismatch).

---

## Step 4: Readiness Decision

**READY** — all prerequisites are marked complete and files exist.

> ✅ All prerequisites confirmed. You're ready to start [phase name].

**NOT READY** — one or more prerequisites are missing or incomplete.

> ❌ Cannot start [phase name]. Missing prerequisites:
>
> 1. [artifact] — [action to fix]
> 2. [artifact] — [action to fix]

---

## Step 5: Output

Log the readiness check to `{docsPath}/planning/readiness-check-{date}.md` with:
- Phase being checked
- Each artifact: status + file path
- Go / Not-Ready decision
- Remediation steps (if not ready)
