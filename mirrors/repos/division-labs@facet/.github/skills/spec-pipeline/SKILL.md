---
name: spec-pipeline
description: Executes the end-to-end grounded technical engineering pipeline from literature/spec to verified code. Covers the complete S0V + S0->S5 lifecycle and human checkpoint gates.
license: Apache-2.0
user-invocable: true
argument-hint: 'Problem statement, literature source, PDF/diagram, or algorithm to implement'
---

# Facet: Specification-Driven Engineering Pipeline

Authoritative lifecycle reference for the `S0V` + `S0 -> S5` grounded translation pipeline. Gated at ingress and post-archival loop-back by the read-only `@Facet` hypervisor, coordinated internally by hidden `@Orchestrator`, and guarded deterministically by [pipeline-guards.json](../../hooks/pipeline-guards.json).

## Pipeline Stages & Delegation Trajectory

| Stage | Name | Worker Agent | Input Artifact | Contained Write Target(s) | Transition / Gate |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Boot** | Pre-Flight Seal Check | `@Facet` *(Hypervisor)* | `.pipeline_state.json` / `upstream_seals` | Read-only (`view` only) | Invokes `@Orchestrator` (or `HALT_SEAL_ERROR`) |
| **S0V** *(Conditional)* | Multimodal Vision/PDF OCR | `@Scribe` | Local/Remote PDF, Image, or Visual HTML | `SOURCE_OCR.md` (`create`-only) | `[TRANSITION: OCR -> RESEARCHER]` |
| **S0** *(Path B)* | Grounded Ideation | `@Researcher` | User Goal / `SOURCE_OCR.md` | `RESEARCH.md` (`create`-only) | **Checkpoint 0 (`[CHECKPOINT: S0 -> C0]`)** |
| **S1** | Specification Manifest | `@Researcher` | `RESEARCH.md` / `SOURCE_OCR.md` / Text Spec | `manifest.json` (`create`-only) | **Checkpoint 1 (`[CHECKPOINT: S1 -> C1]`)** |
| **S2** | Formal Discretization | `@Formalist` | `manifest.json` | `mapping.json` (`create`-only) | **Checkpoint 2 (`[CHECKPOINT: S2 -> C2]`)** |
| **S3** | Provisioning & Implementation | `@Engineer` | `mapping.json` | `requirements.txt` + `./.venv` + Production Code (`*.py`) | `[TRANSITION: S3 -> S4]` |
| **S4** | Cleanroom Verification Audit | `@Auditor` | Code + `manifest.json` + `mapping.json` | `verify_*.py` + `VERIFICATION.md` / `AUDIT_FEEDBACK.json` | **Checkpoint 3 (`[CHECKPOINT: S4 -> C3]`)** *(or Reflexion repair $\le K_{\max}$)* |
| **S5** | Terminal Archival & Loop-Back | `pipeline_guards.py` + `@Facet` | Sign-Off (`/approve` or batch) | `specs/<concept_slug>/PROVENANCE.json` | `@Facet` `view` verify -> `PRE_RUN_HALT` |

*Vision & PDF Modality Firewall:* `@Researcher`, `@Formalist`, `@Engineer`, and `@Auditor` are deterministically blocked from reading raw `.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`, `.bmp`, `.tiff`, or `.pdf` files. All visual/PDF inputs pass exclusively through `@Scribe` (`Stage 0V` -> `SOURCE_OCR.md`).

---

## The 4 Human Checkpoint Approval Gates

At each Human Checkpoint, `@Orchestrator` presents a natural technical briefing with clickable Markdown file links and SHA-256 verification hashes, concluding with the explicit command prompt and halting:

1. **Checkpoint 0 (Candidate Algorithm Gate) `[CHECKPOINT: S0 -> C0]`:**
   - Deliverable: `[RESEARCH.md](./RESEARCH.md)` authored directly by `@Researcher`.
   - Prompt: *"Ask a question about this stage, reply `/approve` to continue, or `/reset` to start over."*
2. **Checkpoint 1 (Specification Manifest Gate) `[CHECKPOINT: S1 -> C1]`:**
   - Deliverable: `[manifest.json](./manifest.json)` authored directly by `@Researcher` and validated against `[schema.json](../technical-perception/schema.json)` (highlighting any `"epistemic_status": "assumption"` claims propagated from `<uncertain>` / `<illegible/>` OCR provenance).
   - Prompt: *"Ask a question about this stage, reply `/approve` to continue, or `/reset` to start over."*
3. **Checkpoint 2 (Formal Mapping Gate) `[CHECKPOINT: S2 -> C2]`:**
   - Deliverable: `[mapping.json](./mapping.json)` authored directly by `@Formalist` conforming to `[mapping_schema.json](../formal-mapping/mapping_schema.json)`.
   - Prompt: *"Ask a question about this stage, reply `/approve` to continue, or `/reset` to start over."*
4. **Checkpoint 3 (Verification Sign-Off Gate) `[CHECKPOINT: S4 -> C3]`:**
   - Deliverable: `[VERIFICATION.md](./VERIFICATION.md)` authored directly by `@Auditor`.
   - Prompt: *"Ask a question about this stage, reply `/approve` to continue, or `/reset` to start over."*

*Contractual Commands:*
- `/approve` (or `/approve <target>`): Advances past an active Human Checkpoint. Conversational phrases ("looks good", "proceed", "yes") are rejected; questions about the active deliverable are answered read-only without advancing state.
- `/status`: Returns an instant zero-tool status pulse showing the active stage, repair counter, and SHA-256 artifact seals.
- `/reset`: Snapshots any in-progress artifacts (including `SOURCE_OCR.md` if present) to `specs/<slug>/` and resets the workspace root.
- `/add-source <domain_or_url>` (or `/add-source --workspace <domain_or_url>`, or bare `/add-source` to list): Adds a research domain to the approved `web_fetch` registry ([approved_sources.json](../../hooks/approved_sources.json) + `~/.copilot/approved_sources.local.json`).

---

## Subagent Delegation Contract
When invoking specialist subagents via `task`:
- `agent_type`: Exactly `Scribe`, `Researcher`, `Formalist`, `Engineer`, or `Auditor` (`Scribe` strictly for `Stage 0V` Vision/PDF OCR -> `SOURCE_OCR.md`).
- `name`: Subagent role identifier string (e.g. `"Researcher"`).
- `description`: 3-5 word concise UI intent string (e.g. `"Extracting equations into manifest"`).
- `prompt`: Self-contained instructions referencing absolute file paths on disk.
- `mode`: `"sync"` (waits for subagent completion).
- Leave `model`, `reasoning_effort`, and `context_tier` unset.

