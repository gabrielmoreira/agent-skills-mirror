---
name: skill-auditor
description: A comprehensive auditor for any agent skill — including Manus, OpenClaw/ClawHub, Claude, LobeHub, or custom SKILL.md-based skills. Use this skill whenever a user wants to evaluate, audit, review, score, or quality-check an agent skill before publishing, updating, or deploying. Covers two hard veto gates (structural redlines + research integrity redlines), static quality scoring across 25 criteria (ISO 25010 + OpenSSF + Agent), dynamic test input generation, multi-mode execution testing, multi-layer output evaluation with five specialized category rubrics (Evidence Insight / Protocol Design / Data Analysis / Academic Writing / Other), a Research Veto that applies to all four research categories, human eval viewer generation, actionable P0/P1/P2 optimization recommendations, and automatic skill improvement that outputs a polished, production-ready SKILL.md. Also use whenever a user says "audit my skill", "evaluate my skill", "improve my skill", or wants a corrected version after evaluation.
license: MIT
skill-author: AIPOCH
---

# Skill Auditor

This skill provides a standardized, end-to-end process for auditing any agent skill — from structural integrity to live functional performance. It combines two independent veto gates, static analysis across 25 criteria, dynamic execution, five-category specialized scoring, and human review into a single coherent workflow.

## Audit Pipeline

```
Step 1 │ Skill Veto              → ❌ HARD GATE: Structural/security redlines — any FAIL = reject
Step 2 │ Basic Evaluation        → Static quality scoring (25 criteria, 100 pts, ISO 25010 + OpenSSF + Agent)
Step 3 │ Classification          → Route to one of 5 categories + detect execution mode
Step 4 │ Dynamic Input Gen       → Generate N test inputs scaled to complexity
Step 5 │ Execution Testing       → Run skill via correct execution mode
Step 6 │ Multi-Layer Evaluation  → Basic rubric + Specialized rubric (category-specific, /60) + Assertions
        │                           ❌ HARD GATE: Research Veto — any FAIL = reject (categories 1–4 only)
Step 7 │ Human Review            → Generate eval viewer (.md) + collect per-input scores for JSON
Step 8 │ Optimization Report     → Final score + P0/P1/P2 recommendations
        │                           + emit eval_report_<n>_result.json for frontend visualization
```

**Two hard rejection gates run at Steps 1 and 6. Both are mandatory and cannot be skipped.**
All other steps run sequentially. **Step 9 always runs** — even when a veto gate fires, the polished output corrects the rejected skill rather than abandoning it.

---

## Language Policy

**All audit output must be written in English, regardless of the language used in the user's request or in the submitted skill.**

This applies to every artifact produced by this skill:
- Veto reports (Step 1 and Step 6)
- Static evaluation scores and notes (Step 2)
- Generated test inputs (Step 4)
- Execution summaries and per-output evaluations (Steps 5–6)
- The eval viewer `.md` file (Step 7)
- The final optimization report and JSON (Step 8)

If the user communicates in another language, Claude may briefly acknowledge the request in that language, but must then conduct and present the full audit in English.

---

## Step 1: Skill Veto — Structural Redlines ❌

> **HARD GATE. Any FAIL = immediate rejection. Do not proceed to Step 2.**

Read the target skill's `SKILL.md` and any bundled scripts. Check all four dimensions:

→ Full criteria: [`references/basic_veto.md`](references/basic_veto.md)

| Dimension | Immediate Rejection Triggers |
|---|---|
| **T1. Operational Stability** | Failure rate > 20%; random crashes or infinite loops; unresolvable dependency conflicts requiring manual intervention |
| **T2. Structural Consistency** | Missing required frontmatter fields (`name`, `description`); non-compliant schema; inconsistent return types or field names |
| **T3. Result Determinism** | Significant output variance on identical inputs at low temperature; no seed management; critical numerical results fluctuate randomly |
| **T4. System Security** | Direct execution of raw user-provided strings (`eval`/`exec`); no input filtering; prompt injection vectors present in scripts or instructions |

**► If any T1–T4 dimension is FAIL: stop immediately. Output the rejection report below and do not continue.**

```
SKILL VETO — REJECTED
══════════════════════════════════
Skill: <n>
Reason: Failed structural redline check
T1. Stability    : PASS / FAIL — <reason>
T2. Contract     : PASS / FAIL — <reason>
T3. Determinism  : PASS / FAIL — <reason>
T4. Security     : PASS / FAIL — <reason>

This skill must not be deployed. Fix all FAIL dimensions before resubmitting.
══════════════════════════════════
```

---

## Step 2: Basic Evaluation — 25 Criteria (ISO 25010 + OpenSSF + Shneiderman + Agent)

Read the skill's full SKILL.md and all bundled files. Score each of the 25 criteria from 0–4.

→ Full rubric with per-level descriptions: [`references/basic_evaluation.md`](references/basic_evaluation.md)

| # | Category (Framework) | Criteria | Max |
|---|---|---|---|
| 1 | **Functional Suitability** (ISO 25010) | Completeness, Correctness, Appropriateness | 12 |
| 2 | **Reliability** (ISO 25010) | Fault Tolerance, Error Reporting, Recoverability | 12 |
| 3 | **Performance & Context** (ISO 25010 + Agent) | Token Cost, Execution Efficiency | 8 |
| 4 | **Agent Usability** (Shneiderman · Gerhardt-Powals) | Learnability, Consistency, Feedback Design, Error Prevention | 16 |
| 5 | **Human Usability** (Tognazzini · Norman) | Discoverability, Forgiveness | 8 |
| 6 | **Security** (ISO 25010 + OpenSSF) | Credential Safety, Input Validation, Data Safety | 12 |
| 7 | **Maintainability** (ISO 25010) | Modularity, Modifiability, Testability | 12 |
| 8 | **Agent-Specific** (Novel) | Trigger Precision, Progressive Disclosure, Composability, Idempotency, Escape Hatches | 20 |

**Basic subtotal: __ / 100**

---

## Step 3: Classification + Execution Mode Detection

### 3.1 Classify the Skill

Read the skill's `description` frontmatter and `## When to Use` section.

→ Full category definitions: [`references/classification.md`](references/classification.md)

| # | Category | Typical Skills |
|---|---|---|
| 1 | **Evidence Insight** | Search strategy builders, database scouts, critical appraisal tools, evidence synthesizers |
| 2 | **Protocol Design** | Experimental design generators, study-type advisors, statistical power planners, validation strategists |
| 3 | **Data Analysis** | R/Python code generators, bioinformatics pipelines, statistical modeling tools, ML workflows |
| 4 | **Academic Writing** | SCI manuscript writers, abstract generators, methods/discussion drafters, cover-letter tools |
| 5 | **Other (General / Non-Research)** | All skills that do not fall into categories 1–4 |

> **Research Veto scope**: Categories 1–4 are subject to the Research Veto hard gate in Step 6. Category 5 is exempt.

### 3.2 Detect Execution Mode

Inspect the skill to determine how it is meant to be invoked.

| Mode | Indicators | How to Run in Step 5 |
|---|---|---|
| **A: Direct** | Only SKILL.md instructions, no scripts | Follow SKILL.md instructions to complete the task as Claude |
| **B: CLI / Script** | `scripts/` directory with Python/bash, CLI examples in SKILL.md | Execute via bash: `python scripts/xxx.py <args>` |
| **C: API** | API endpoint patterns, fetch/curl usage in SKILL.md | Simulate or call the API as documented |
| **D: Hybrid** | Both instructions and scripts/API | Run script for deterministic parts; Claude for reasoning/generation parts |

Record the detected mode. It will be used in Step 5.

---

## Step 4: Dynamic Input Generation

**Purpose:** Generate test inputs derived directly from the skill's own description to ensure they reflect real-world usage patterns.

### 4.1 Assess Skill Complexity

| Complexity Level | Criteria | Test Input Count (N) |
|---|---|---|
| **Simple** | Single task type, narrow scope, < 3 reference files, no branching workflow | **3 inputs** |
| **Moderate** | 2–3 task types, some branching, 3–5 reference files, moderate scope | **5 inputs** |
| **Complex** | Multiple task types, branching logic, 5+ reference files, broad or specialized scope | **7 inputs** |

Declare: `Complexity: [Simple / Moderate / Complex] → Generating N inputs`

### 4.2 Generate N Test Inputs

Use this distribution based on N:

| Slot | Type | Always Include? |
|---|---|---|
| Input 1 | Canonical / happy path | ✅ Always |
| Input 2 | Variant A (different valid use case) | ✅ Always |
| Input 3 | Edge / boundary | ✅ Always |
| Input 4 | Variant B (third central use case) | If N ≥ 5 |
| Input 5 | Stress / complex / multi-part | If N ≥ 5 |
| Input 6 | Scope boundary (slightly outside) | If N = 7 |
| Input 7 | Adversarial / ambiguous | If N = 7 |

Format each as a realistic user message. Do **not** include expected answers.

**Output:**
```
GENERATED TEST INPUTS
═══════════════════════════════════════
Skill: <n>  |  Category: <1–5 + label>  |  Mode: <A/B/C/D>
Complexity: <level>  →  Generating <N> inputs

Input 1 (Canonical)   : <prompt>
Input 2 (Variant A)   : <prompt>
Input 3 (Edge)        : <prompt>
[Input 4–7 if applicable]
═══════════════════════════════════════
```

---

## Step 5: Execution Testing

Run the skill on each of the N test inputs using the detected execution mode.

### Mode A: Direct Execution
Load the skill's SKILL.md. Follow its instructions as if you are Claude-with-this-skill responding to the user message. Complete the task in full.

### Mode B: CLI / Script Execution
```bash
python scripts/<script_name>.py "<input_text_or_path>"
```
Capture stdout/stderr. If execution fails, record the error and continue.

### Mode C: API Execution
Follow the API usage pattern documented in the skill. Construct the request, execute, capture response. If credentials are unavailable, note this and simulate the expected output based on documentation.

### Mode D: Hybrid Execution
Run the script/API component first. Pass its output to Claude for the reasoning/generation component.

### Execution Log

For each input:
```
─── Input [N] ─────────────────────────
Mode    : <A/B/C/D>
Input   : <prompt>
Output  :
<full output>
Status  : COMPLETED / ERROR / PARTIAL
Notes   : <anomalies, scope violations, unexpected behaviors>
────────────────────────────────────────
```

---

## Step 6: Multi-Layer Output Evaluation

Evaluate all N outputs across three parallel layers.

### Layer 1: Basic Rubric Scoring

→ Full criteria: [`references/basic_evaluation.md`](references/basic_evaluation.md)

For each output, score four aggregate dimensions (0–10 each):
- **Functional Correctness** (did output complete the task correctly and fully?): /10
- **Reliability & Clarity** (well-structured, consistent, clear feedback?): /10
- **Efficiency** (concise, no padding, no unnecessary context bloat?): /10
- **Scope & Safety** (stayed in scope, no harmful content, proper escape hatches?): /10

Per-output basic score: /40

### Layer 2: Specialized Rubric Scoring

Apply the rubric corresponding to the category from Step 3:

| Category | Reference File | Max |
|---|---|---|
| 1 — Evidence Insight | [`references/specialized_evaluation_literature.md`](references/specialized_evaluation_literature.md) | 60 |
| 2 — Protocol Design | [`references/specialized_evaluation_research_design.md`](references/specialized_evaluation_research_design.md) | 60 |
| 3 — Data Analysis | [`references/specialized_evaluation_data_analysis.md`](references/specialized_evaluation_data_analysis.md) | 60 |
| 4 — Academic Writing | [`references/specialized_evaluation_academic_writing.md`](references/specialized_evaluation_academic_writing.md) | 60 |
| 5 — Other | [`references/specialized_evaluation_other.md`](references/specialized_evaluation_other.md) | 60 |

Per-output specialized score: /60

### Layer 3: Assertion Checks

For each output, write and evaluate 3–5 boolean assertions derived from the skill's stated purpose.

**Assertion types:**
- **Format assertion**: "Output contains required section X"
- **Content assertion**: "Output does not fabricate specific claims"
- **Scope assertion**: "Output does not go beyond the skill's stated purpose"
- **Safety assertion**: "Output includes required disclaimers" (required for categories 1–4)
- **Completeness assertion**: "Output addresses all parts of a multi-part prompt"

Format:
```
Assertions for Input [N]:
  [PASS/FAIL] <assertion statement> — <brief justification>
  [PASS/FAIL] <assertion statement> — <brief justification>
  [PASS/FAIL] <assertion statement> — <brief justification>
  Assertion pass rate: X/Y
```

**GATE: Any safety or scope assertion FAIL on 2+ outputs → Flag for rejection review.**

### Scoring Aggregation

```
Per-output total     = Basic Score (Layer 1, /40) + Specialized Score (Layer 2, /60) = /100
Execution avg score  = Mean of all N output totals
Assertion summary    = Total passed / Total assertions
```

---

### Research Veto — Scientific Integrity Redlines ❌ *(Categories 1–4 only)*

> **HARD GATE. Run after all N outputs are evaluated. Any FAIL = immediate rejection.**
> **Skip entirely for Category 5 (Other).**

→ Full criteria and rejection report template: [`references/scientific_veto.md`](references/scientific_veto.md)

| Dimension | Immediate Rejection Triggers |
|---|---|
| **M1. Scientific Integrity** | Any output fabricates DOI/PMID numbers, invents clinical trial results, sample sizes, p-values, or efficacy data that cannot be verified |
| **M2. Practice Boundaries** | Any output makes direct diagnostic or prescriptive medical conclusions; any output lacks required medical disclaimer; any output recommends unapproved treatments without explicit caveats |
| **M3. Methodological Baseline** | Any output commits a principled methodological fallacy; any output ignores or fails to warn about ethical compliance requirements |
| **M4. Code Usability** | Any generated bioinformatics/statistical code is unrunnable (syntax errors, infinite loops, missing core dependencies). Mark N/A for categories 1 & 4 if no code is generated. |

**► If any M1–M4 dimension is FAIL: stop. Output the Research Veto rejection report. Do not proceed to Steps 7–8.**

---

## Step 7: Human Review — Eval Viewer

Generate a structured Markdown review document for human inspection.

```markdown
# Eval Viewer — <Skill Name>
Generated: <date>

## Summary Table

| Input | Type | Basic /40 | Specialized /60 | Total /100 | Assertions | Status |
|---|---|---|---|---|---|---|
| 1 | Canonical | __ | __ | __ | X/Y PASS | ✅/⚠️/❌ |
...

**Execution Average: __ / 100**
**Assertion Pass Rate: __/__**

## Detailed Outputs

### Input 1 — [Type]
**Prompt:** <input text>
**Output:** <full output>
**Scores:** Basic: __/40 | Specialized: __/60 | Total: __/100
**Assertions:**
- [PASS/FAIL] <assertion statement> — <brief justification>
- ...
```

Save as `eval_viewer_<skill_name>.md` if filesystem is available; otherwise render inline.

> **Note for reviewer:** Check ⚠️ and ❌ rows first. Patterns across 2+ outputs indicate structural skill issues.

---

## Step 8: Optimization Report

### Final Score Calculation

```
Final Score = (Static Score × 0.4) + (Execution Avg × 0.6)
```

→ Full scoring thresholds: [`references/scoring_rubric.md`](references/scoring_rubric.md)

| Score | Grade | Recommendation |
|---|---|---|
| 85–100 | ⭐ Production Ready | Deploy publicly |
| 75–84 | ✅ Limited Release | Throttled / monitored rollout |
| 60–74 | ⚠️ Beta Only | Internal / greylist only |
| < 60 | ❌ Reject | Do not deploy |

### Optimization Recommendations

| Priority | Criteria | Action |
|---|---|---|
| **P0 — Blocker** | Any veto FAIL, safety assertion FAIL, score < 60 | Must fix before any deployment |
| **P1 — Major** | Score 60–74, repeated assertion failures, Layer 1 or 2 avg < 7/10 | Fix before production release |
| **P2 — Minor** | Score 75–84, isolated output weaknesses, style/format issues | Address before full scale |

For each issue found, output:
```
[P0/P1/P2] <Issue Title>
  Observed in: Input(s) [N, M, ...]
  Problem: <what went wrong>
  Root cause: <likely cause in skill design>
  Fix: <specific, actionable change to SKILL.md or scripts>
```

### Final Report

```
══════════════════════════════════════════════════
SKILL AUDIT REPORT
══════════════════════════════════════════════════
Skill Name     : <n>
Category       : <label>
Execution Mode : <A/B/C/D>
Complexity     : <Simple/Moderate/Complex>  (N=<n> inputs)
Audited On     : <date>

── STEP 1: Structural Veto ───────────────────────
Stability    : PASS / FAIL
Contract     : PASS / FAIL
Determinism  : PASS / FAIL
Security     : PASS / FAIL

── STEP 2: Static Evaluation (25 criteria) ───────
Functional Suitability : __/12
Reliability            : __/12
Performance/Context    : __/8
Agent Usability        : __/16
Human Usability        : __/8
Security               : __/12
Maintainability        : __/12
Agent-Specific         : __/20
Static Subtotal        : __/100

── STEP 3: Classification ────────────────────────
Category       : <label>
Execution Mode : <A / B / C / D>

── STEP 4: Test Inputs ───────────────────────────
[N inputs listed with type labels]

── STEP 5: Execution Summary ─────────────────────
Input 1: [COMPLETED/PARTIAL/ERROR] — <note>
...

── STEP 6: Output Evaluation ─────────────────────
         Basic  Specialized  Total  Assertions
Input 1:  __/40    __/60    __/100   X/Y PASS
...
Execution Avg               : __/100
Total Assertion Pass Rate   : __/__

[Research Veto — Evidence Insight / Protocol Design / Data Analysis / Academic Writing only; N/A for Other]
Scientific Integrity  : PASS / FAIL / N/A
Practice Boundaries   : PASS / FAIL / N/A
Methodological Ground : PASS / FAIL / N/A
Code Usability        : PASS / FAIL / N/A

── STEP 7: Outputs ───────────────────────────────
eval_viewer_<n>.md   : SAVED ✅
eval_report_<n>_result.json : SAVED ✅

── STEP 8: Final Score ───────────────────────────
Static Score   : __/100  × 40% = __
Dynamic Score  : __/100  × 60% = __
FINAL SCORE    : __ / 100
GRADE          : ⭐/✅/⚠️/❌  [Production Ready / Limited Release / Beta Only / Reject]

Key Strengths:
- ...

Optimization Recommendations:
[P0] ...
[P1] ...
[P2] ...
══════════════════════════════════════════════════
```

### Step 7–8 JSON Output

→ Full schema + complete example: [`references/report_json_schema.md`](references/report_json_schema.md)

**JSON top-level nodes (all 7 required):**

| Node | Key rules |
|---|---|
| `meta` | `evaluator_version: "skill-auditor@1.0"` |
| `veto_gates` | `skill_veto` keys: `stability`, `contract`, `determinism`, `security` — **no T-prefixes**; `research_veto` keys: `scientific_integrity`, `practice_boundaries`, `methodological_ground`, `code_usability` — **no M-prefixes** |
| `static_score` | `categories` keys: `functional_suitability`, `reliability`, `performance_context`, `agent_usability`, `human_usability`, `security`, `maintainability`, `agent_specific` — **no cat-prefixes** |
| `dynamic_score` | Each input includes full `assertions` array (`text`, `result`, `note` per assertion) in addition to `assertions_passed` / `assertions_total` counts |
| `final` | weighted scores, grade, `deployable`, `veto_override` |
| `key_strengths` | plain-string array, 2–5 entries |
| `recommendations` | P0 → P1 → P2 sorted |

**Pre-emit checklist:**
- No T-, M-, or cat-numbered prefixes in any JSON key
- `static_score.categories` has exactly **8** un-prefixed keys; all scores within 0–max
- `dynamic_score.inputs` has exactly **N** objects; each has an `assertions` array
- Each input's `assertions_passed` equals count of `"PASS"` in its `assertions` array
- `research_veto.applicable = false` and all research veto fields `= "N/A"` for category Other
- `final.veto_override = true` if any gate is FAIL
- `recommendations` sorted P0 → P1 → P2
- All averages/weighted scores rounded to **1 decimal**; all raw scores **integers**

---


## Input Validation

This skill accepts: a SKILL.md file or skill description submitted for quality audit and improvement.

If the user's request does not involve auditing, evaluating, scoring, or improving an agent skill — for example, asking to write a story, build a website, or answer a general question — do not proceed with the audit pipeline. Instead respond:
> "Skill Auditor is designed to evaluate and improve agent skills (SKILL.md files). Your request appears to be outside this scope. Please submit a skill for auditing, or use a more appropriate tool for your task."

**Language note:** The user may submit requests or skills in any language. Always produce the full audit output in English. See [Language Policy](#language-policy) above.

---

## Reference Files

| File | Used In | Gate? |
|---|---|---|
| `references/basic_veto.md` | Step 1 — Structural redlines | ❌ Hard gate |
| `references/basic_evaluation.md` | Step 2 (static scoring) + Step 6 Layer 1 | — |
| `references/classification.md` | Step 3 — 5-category classification | — |
| `references/specialized_evaluation_literature.md` | Step 6 Layer 2 — Category 1 | — |
| `references/specialized_evaluation_research_design.md` | Step 6 Layer 2 — Category 2 | — |
| `references/specialized_evaluation_data_analysis.md` | Step 6 Layer 2 — Category 3 | — |
| `references/specialized_evaluation_academic_writing.md` | Step 6 Layer 2 — Category 4 | — |
| `references/specialized_evaluation_other.md` | Step 6 Layer 2 — Category 5 | — |
| `references/scientific_veto.md` | Step 6 Research Veto — categories 1–4 only | ❌ Hard gate |
| `references/scoring_rubric.md` | Step 8 — final score & deployment recommendation | — |
| `references/report_json_schema.md` | Step 7 (data collection) + Step 8 (JSON output) | — |

## Dependencies

- Python 3.x + standard libraries — for `scripts/evaluate_skill.py` (structural pre-checks)
- Claude — for Steps 4–8 (input generation, execution, multi-layer scoring, recommendations)

---

## Changelog

### v1.1.0 — 2026-04-02

**Scene Override additions** — Based on findings from the audit of `differential-expression-analysis`, three systematic biases were identified in `basic_evaluation.md` when applied to scientific computing + agent-first skills. Rather than modifying the shared basic evaluation criteria (which would affect all five categories), per-category scene override sections were added to the relevant specialized evaluation files.

**Files modified:**
- `references/specialized_evaluation_data_analysis.md` — Added Scene Override section covering Fault Tolerance (2.1), Forgiveness (5.2), and Recoverability (2.3)
- `references/specialized_evaluation_research_design.md` — Added Scene Override section with the same three overrides, adapted for protocol design context
- `references/specialized_evaluation_other.md` — Added Execution Mode Awareness note directing auditors to apply Category 3 overrides when the skill operates in agent-first Mode B/C/D context

**Rationale:** The three affected basic evaluation criteria assume (1) human direct CLI operation and (2) general-purpose software tools. These assumptions do not hold for scientific computing pipelines or agent-first skills, where strict input validation and hard stops are correct design decisions, and structured error codes are the appropriate recovery interface.
