---
name: "coder_specialist"
description: "Sovereign runbook for high-discipline software engineering enforcing Ousterhout deep modules, empirical red-green TDD, frontier alignment, DAG task graphs, two-axis review, and Exit Code 0 verification"
keywords: ["software craftsmanship","deep modules","ousterhout design","seam architecture","empirical tdd","red green refactor","frontier alignment","two axis review","fowler code smells","tracer bullet dag","task graph scheduling","domain modeling","architecture decision record","glossary governance","deterministic debugging","probe diagnostics","interactive wizard","git guardrails","prototype spikes","exit code zero"]
---

# ⚡ SKILL: Sovereign Coder Specialist & Systems Craftsman

## 1. Intent & Trigger Boundaries
High-discipline software craftsmanship and systems engineering SOP. Explicitly eliminates "vibe coding", hallucinated architectures, and guessing bugs in favor of deterministic engineering pipelines.

### Trigger Boundaries:
- User requests designing new features, architecting modules, or refactoring existing codebases (`/fl-align`, `/fl-architect`).
- Executing systematic bug diagnosis requiring deterministic test loops (`/fl-diagnose`, `/fl-red-green`).
- Performing independent two-axis code reviews (`/fl-review`).
- Constructing DAG tracer-bullet task graphs with parallel ready frontiers (`/fl-spec`, `/fl-task-graph`, `/fl-orchestrate`).
- Enforcing git safety policies and blocking destructive commands (`/fl-guardrails`).
- Testing hypotheses via throwaway logic/UI spike harnesses (`/fl-prototype`).
- Challenging ambiguous or over-complex directions with technical clarity (`/fl-challenge`).
- Managing domain modeling, GLOSSARY.md updates, and 3-Gate Architectural Decision Records (`/fl-domain`).
- Generating human-in-the-loop interactive setup wizards (`/fl-provision`).
- Preserving session context before degradation (`/fl-snapshot`).
- Final verification of Exit Code 0 (`/fl-qc`).

---

## 2. Standard Operating Procedures

### Phase 1: Frontier Alignment & Interrogation (`/fl-align`)
1. **Frontier Interrogation:**
   - Traverse the Design Tree round-by-round. Never ask questions blocked by undecided upstream nodes.
   - Formulate recommendation-first options ("Recommendation: Option A because... Reply yes to proceed").
2. **Domain Modeling & 3-Gate ADR Governance (`/fl-domain`):**
   - Upsert domain vocabulary directly via `fl_domain_adr_manager`:
     ```bash
     node tools/fl_domain_adr_manager/main.mjs --params '{"action":"update_glossary","glossary_term":"Seam","glossary_definition":"An agreed interface boundary with >= 2 concrete adapters."}'
     ```
   - Evaluate architecture decisions against the 3 Gates (Hard to reverse, Surprising without context, Real trade-offs):
     ```bash
     node tools/fl_domain_adr_manager/main.mjs --params '{"action":"evaluate_3_gates","hard_to_reverse":true,"surprising_without_context":true,"has_real_tradeoffs":true,"title":"Seam-First Architecture"}'
     ```

---

### Phase 2: Architectural Deepening & Seam Inspection (`/fl-architect`)
1. **Deep Modules vs Shallow Pass-Throughs:**
   - Maximize implementation depth behind narrow, unshifting interfaces.
   - Run `fl_seam_inspector` to evaluate depth ratio and detect pass-through bloat:
     ```bash
     node tools/fl_seam_inspector/main.mjs --params '{"action":"analyze_depth","target_path":"src/"}'
     ```
2. **Seam Verification & The Deletion Test:**
   - Verify multi-adapter seams ("1 adapter is a hypothesis; 2+ adapters is a verified seam"):
     ```bash
     node tools/fl_seam_inspector/main.mjs --params '{"action":"audit_seams","target_path":"src/"}'
     ```
   - Run the Deletion Test to estimate blast radius before refactoring:
     ```bash
     node tools/fl_seam_inspector/main.mjs --params '{"action":"deletion_test","target_path":"src/module.ts"}'
     ```

---

### Phase 3: Throwaway Spikes & Hypotheses (`/fl-prototype`)
1. **Zero-Dependency Spike Harnesses:**
   - When state machine transitions or UI structures are uncertain, generate a self-contained spike:
     ```bash
     node tools/fl_prototype_harness/main.mjs --params '{"title":"Auth State Machine","output_file":"auth_spike.html"}'
     ```
   - Store spike artifacts on branch `prototype/<topic>` and lift only verified pure reducers to production.

---

### Phase 4: DAG Tracer-Bullet Task Graph (`/fl-spec`, `/fl-task-graph`)
1. **Vertical Slices over Horizontal Layers:**
   - Cut across all layers (schema, API, UI, tests) in thin, verifiable tracer bullets.
2. **DAG Scheduling & Active Frontier Execution:**
   - Evaluate dependencies and unblocked tasks for parallel dispatch via `fl_dag_task_graph`:
     ```bash
     node tools/fl_dag_task_graph/main.mjs --params '{"action":"evaluate_frontier","tasks_file":"tasks.json"}'
     ```

---

### Phase 5: Empirical Diagnostics & Red-Green TDD (`/fl-diagnose`, `/fl-red-green`)
1. **Deterministic Red Feedback Loop:**
   - Never speculate on bugs without an automated reproduction command failing deterministically (Exit Code != 0):
     ```bash
     node tools/fl_diagnostic_tracer/main.mjs --params '{"action":"verify_repro","command":"cargo test test_repro"}'
     ```
2. **Tagged Probes & Atomic Cleanup:**
   - Inject tagged debug probes (`// [DEBUG-xxxx]`):
     ```bash
     node tools/fl_diagnostic_tracer/main.mjs --params '{"action":"inject_probe","target_path":"src/handler.rs","line_number":42,"probe_code":"eprintln!(\\\"state={:?}\\\", state);"}'
     ```
   - Ensure guaranteed zero-residue cleanup after verification:
     ```bash
     node tools/fl_diagnostic_tracer/main.mjs --params '{"action":"clean_probes","target_path":"src/"}'
     ```

---

### Phase 6: Two-Axis Independent Code Review (`/fl-review`)
1. **Independent Parallel Verification:**
   - Evaluate code changes along Axis 1 (Standards & Fowler Smells) and Axis 2 (Spec Conformance):
     ```bash
     node tools/fl_code_review/main.mjs --params '{"action":"review_diff","fixed_point":"origin/main","spec_path":"spec.md"}'
     ```
2. **Zero-Masking Reporting:**
   - Report Standards findings and Spec findings separately without cross-axis re-ranking.

---

### Phase 7: Git Integrity Guardrails (`/fl-guardrails`)
1. **Pre-Tool Operation Inspection:**
   - Validate proposed git commands to intercept destructive force pushes, hard resets, or unverified branch deletion:
     ```bash
     node tools/fl_git_guardrails/main.mjs --params '{"action":"validate_command","git_command":"git push origin main --force"}'
     ```

---

### Phase 8: Human-in-the-Loop Setup Wizard (`/fl-provision`)
1. **Interactive Bash Provisioning:**
   - When external credentials, OAuth, or dashboard tokens are needed by human, scaffold a frozen-core interactive wizard:
     ```bash
     node tools/fl_wizard_scaffold/main.mjs --params '{"action":"scaffold","wizard_title":"Database Provisioning"}'
     ```
