---
name: openspec-bootstrap-opsx
description: Bootstrap OPSX architecture map from existing codebase using a structured five-phase workflow (init → scan → map → review → promote).
license: MIT
compatibility: Requires openspec CLI.
metadata:
  author: openspec
  version: "2.0"
  generatedBy: "1.2.0-cpyu.9"
---

Bootstrap the OPSX architecture map from the existing codebase.

This is a **structured, multi-phase** workflow. Each phase produces intermediate artifacts in `openspec/bootstrap/` before writing formal OPSX files.

Treat `openspec/config.yaml` as the source of truth for authoring policy, but consume its compiled projection semantics: prose-bearing bootstrap artifacts follow the projected documentation language policy, while canonical headings, IDs, schema keys, paths, and commands stay unchanged.

**Input**: No argument required. Scope hints (folders, domain names) are passed to init.

**Steps**

1. **Determine current phase**
   ```bash
   openspec bootstrap status --json
   ```
   - If no workspace exists, start with init
   - If workspace exists and is in progress, resume from the current phase
   - If workspace exists and is completed, restart explicitly with `openspec bootstrap init --mode refresh --restart`

2. **Execute the current phase**

   Get phase-specific instructions:
   ```bash
   openspec bootstrap instructions [phase] --json
   ```

   **Phase: init**
   ```bash
   openspec bootstrap init --mode full
   ```
   Creates workspace at `openspec/bootstrap/` with scope configuration.
   Supported upgrade paths:
   - `specs-based -> full`
   - `raw -> full`
   - `raw -> opsx-first`
   - `formal-opsx -> refresh`
   Use `opsx-first` only for `raw` repositories when you want the formal OPSX bundle plus a README-only specs starter now, and full behavior specs later.
   Use `refresh` only for repositories that already have the formal OPSX bundle and need a delta-first refresh that merges reviewed changes back into the existing formal files.
   Use `--restart` only when a completed retained workspace already exists and you want a fresh run; it snapshots the old `openspec/bootstrap/` into `openspec/bootstrap-history/` first.

   **Phase: scan**
   - Read `package.json`, `README`, OpenSpec config, `openspec/specs/`
   - Scan source code for structural boundaries
   - Write `openspec/bootstrap/evidence.yaml` with candidate domains:
     ```yaml
     domains:
       - id: dom.cli
         confidence: high
         sources: [code:src/cli/, spec:openspec/specs/cli/]
         intent: CLI entry point and command routing
   ```
   - Run `openspec bootstrap validate` to verify gates
   - In `refresh`, treat the current formal OPSX bundle as the baseline and use git diff only to narrow scan scope when a stored anchor commit is still reachable

   **Phase: map**
   - For each domain in evidence.yaml, create `openspec/bootstrap/domain-map/<domain-id>.yaml`:
     ```yaml
     domain:
       id: dom.cli
       type: domain
       intent: CLI entry point and command routing
       status: active
     capabilities:
       - id: cap.cli.init
         type: capability
         intent: Initialize OpenSpec in a project
         status: active
     relations:
       - from: cap.cli.init
         to: dom.cli
         type: contains
     code_refs:
       - id: cap.cli.init
         refs:
           - path: src/core/init.ts
             line_start: 1
     ```
   - Map incrementally — one domain at a time
   - Run `openspec bootstrap status` to track per-domain progress
   - Run `openspec bootstrap validate` after all domains mapped

   **Phase: review**
   - Validate regenerates review.md and candidate OPSX files from current `evidence.yaml` and `domain-map/*.yaml`
   - Review each domain checkbox in review.md
   - In `refresh`, review the delta summary against the current formal OPSX baseline instead of re-approving the whole model
   - Check all validation checkboxes
   - If evidence or domain maps change, rerun validate and re-approve the regenerated review
   - Low-confidence domains appear first for priority review

   **Phase: promote**
   ```bash
   openspec bootstrap promote -y
   ```
   Re-validates all upstream gates before writing.
   - `opsx-first`: writes the formal OPSX three-file bundle plus only `openspec/specs/README.md`
   - `full` on `raw`: writes the formal OPSX bundle plus one validated spec per mapped capability
   - `full` on `specs-based`: preserves existing specs, adds only missing capability specs, and fails fast on target-path conflicts
   - `refresh` on `formal-opsx`: merges the reviewed delta into the existing formal OPSX bundle, preserves existing specs, adds only missing specs for newly added capabilities, and fails fast on conflicts
   Retains the bootstrap workspace on success for audit history.
   Start the next refresh run with `openspec bootstrap init --mode refresh --restart`, which snapshots the retained workspace into `openspec/bootstrap-history/`.

3. **After each phase action**
   - Run `openspec bootstrap validate` to verify gate conditions
   - Run `openspec bootstrap status` to confirm phase advancement
   - Continue to next phase

**Evidence Guidelines**
- Use repository evidence only — do not fabricate
- Attach confidence levels: high (multiple sources), medium (single source), low (inferred)
- Prefer fewer domains with solid evidence over exhaustive noise
- Each domain should map to a clear architectural boundary

**Mapping Guidelines**
- Capability IDs follow `cap.<domain>.<action>` convention
- Code references must point to existing files
- Relations capture structural ownership (contains) and runtime dependencies (depends_on)
- Mark uncertain mappings for review attention

**Guardrails**
- Do NOT write directly to formal OPSX files — use the bootstrap workspace
- Do NOT fabricate code references
- Do NOT skip the review phase
- Do NOT treat stale review.md checkboxes as approval after evidence or mappings change
- Keep the graph small enough to audit in one sitting
