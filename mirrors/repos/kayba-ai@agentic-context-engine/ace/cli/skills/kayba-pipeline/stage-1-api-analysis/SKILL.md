---
name: kayba-stage-1-api-analysis
description: Fetch pre-computed insights from the Kayba API and build a structured summary. Does NOT upload traces or trigger generation — analysis is assumed to already exist. Trigger when the user says "run stage 1", "get insights", "fetch skills", "kayba analyze", or when invoked by the kayba-pipeline orchestrator. Requires the kayba CLI to be installed and KAYBA_API_KEY to be set.
---

# Stage 1: Kayba API Analysis (Fetch-Only Mode)

Fetch pre-computed insights from the Kayba API. Traces have already been uploaded and analyzed — this stage only pulls results.

## Inputs

- **`TRACES_FOLDER`** — passed by the orchestrator but **ignored** in this stage. Traces are already uploaded and analyzed on the Kayba side. Do NOT upload, validate, or read trace files.

## Process

### Step 1: Setup

Ensure `eval/` directory exists at the project root.

### Step 2: Fetch insights

```
kayba insights list --json > eval/insights.json
```

If `kayba` is not found in PATH, search common locations (`.venv/bin/kayba`, project virtualenvs). If found, use the full path. If not found anywhere, report the error and stop.

If `KAYBA_API_KEY` is not set, report the error and stop.

### Step 3: Insight quality gate

Read `eval/insights.json` and run quality checks before building the summary:

1. **Empty check**: if the insights array is empty (0 insights returned), report this as a warning. Write a minimal summary noting "0 insights generated" and stop — downstream stages cannot proceed without insights.
2. **Duplicate detection**: compare insight `content` fields pairwise. If two insights cover substantially the same behavior (same section, overlapping evidence traces, similar corrective action), flag them as potential duplicates in the summary. Do not remove them — just annotate.
3. **Evidence coverage**: for each insight, check if the `evidence` field references specific traces (e.g., "task_7 turn 4"). Insights with no trace-specific evidence are lower quality — flag as "low-evidence" in the summary.
4. **Vote signal**: insights with `status: "accepted"` and `helpful > 0` have been human-validated. Insights with `status: "new"` and `helpful: 0, harmful: 0` are unvalidated — note this distinction in the summary.

Log the quality gate result: `"Insight quality: {total} insights, {accepted} accepted, {new_unvalidated} unvalidated, {duplicates} potential duplicate pairs, {low_evidence} low-evidence"`

### Step 4: Build structured summary

Extract a structured summary of each insight:
- Insight ID and title/summary (use the `section` field as the title)
- Status
- Evidence citations — specific trace references, error strings, behavioral patterns the reflector identified
- Justification / reasoning chain — the reflector's full analysis of why this is a real pattern
- Confidence score if available
- Helpful/harmful counts if available
- Quality flags from Step 3 (potential duplicate, low-evidence, unvalidated)

Write the structured summary to `eval/stage1_insights_summary.md` using this format:

```markdown
# Kayba Insights Summary

Generated from: Kayba API (pre-computed analysis)
Total insights: N
Quality: {accepted} accepted, {unvalidated} unvalidated, {duplicate_pairs} potential duplicate pairs, {low_evidence} low-evidence

## Insight: [ID] — [section title]
**Status:** [status] [quality flags if any, e.g., "[potential duplicate with ID]", "[low-evidence]", "[unvalidated]"]
**Confidence:** [score if available]
**Evidence:**
- [citation 1 — trace reference, error string, or behavioral pattern]
- [citation 2]
**Justification:** [reflector's reasoning for why this is a real pattern]
**Helpful/Harmful:** [counts if available]

---
[repeat for each insight]
```

## Error handling

- If `kayba` is not found in PATH or common locations, report the error and stop
- If `KAYBA_API_KEY` is not set, report the error and stop
- If `kayba insights list` fails (network error, auth error), report the error and stop
- If 0 insights are returned, write a minimal summary and stop — downstream stages need insights

## Outputs

- `eval/insights.json` — raw API response
- `eval/stage1_insights_summary.md` — structured summary with quality annotations for downstream stages
