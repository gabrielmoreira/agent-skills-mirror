---
name: skill-benchmark
description: "**MEASUREMENT SKILL** — Benchmark framework for measuring skill effectiveness. A/B tests agent outputs with and without a target skill, scoring correctness, completeness, and pattern adherence. USE FOR: validating skill quality, comparing before/after skill changes, proving skill ROI with data. DO NOT USE FOR: general testing, unit tests, CI pipelines."
argument-hint: Path to the skill directory you want to benchmark
license: MIT
---

# Skill Benchmark — Measure Skill Effectiveness

You are a benchmark orchestrator. Your job is to measure whether a target skill **actually improves** agent output quality through controlled A/B testing.

The core idea: run identical tasks with and without the skill injected, score both outputs against a rubric, and produce a comparative report. If the skill works, the "with skill" outputs should consistently score higher.

## Workflow Overview

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐     ┌──────────┐
│ 1. Read Skill│────▶│ 2. Provision │────▶│ 3. Execute  │────▶│ 4. Evaluate  │────▶│ 5. Report│
│   (parse)    │     │  (gen tasks) │     │  (A/B test)  │     │  (score)     │     │ (HTML)   │
└─────────────┘     └──────────────┘     └─────────────┘     └──────────────┘     └──────────┘
```

**Pipeline**: Read → Provision → Execute → Evaluate → Report

All scripts live in this skill's `scripts/` directory. **Treat them as black boxes** — run `--help` to learn usage, do NOT read their source code.

## Step 1: Read the Target Skill

Parse the target skill's `SKILL.md` to understand what it teaches:

1. Read the full `SKILL.md` file at the path provided by the user.
2. Extract from the frontmatter:
   - `name` — skill identifier
   - `description` — what the skill teaches
3. Read the body and identify:
   - **Domain** — what subject area (e.g., testing, Docker, Git workflows)
   - **Key concepts** — the specific patterns, rules, or techniques taught
   - **Pitfalls mentioned** — what the skill warns against
   - **References** — any referenced docs (you'll need these for task design)

Store this analysis — you'll use it in Step 2 to generate relevant tasks.

## Output Directory

Before running any scripts, create the output directory structure.

The output dir name follows the pattern: `bench-{skill-name}-{YYYYMMDD-HHmmss}/`

> **The timestamp MUST be the real current date+time (to the second) — never replace it with labels like "runs3", "final", or any other suffix. The seconds-precision timestamp is what guarantees uniqueness.**

**Default location**: current working directory.
**Custom location**: if the user specifies a directory, use that as the parent for the bench dir.
**skill-kit internal evaluations**: always use `skill-benchmarks/` at the skill-kit repo root.

Create the directories:
```
<output-dir>/bench-{skill-name}-{YYYYMMDD-HHmmss}/
  data/
  results/
```

All subsequent commands will use explicit paths into this structure.

## Step 2: Provision Tasks

Generate benchmark tasks that test whether the skill's knowledge makes a real difference.

### 2a. Run the provisioning script

```bash
python scripts/provision.py --skill-path <path-to-SKILL.md> --count <N> --output <bench-dir>/data/benchmark.json
```

This reads the SKILL.md, extracts metadata and key topics, and outputs a `benchmark.json` template with skeleton tasks.

### 2b. Complete the benchmark tasks

The script outputs a template — you must fill it with **concrete, realistic tasks**. For each task:

1. Write a clear `prompt` that a developer might actually ask
2. Design the prompt so the skill's knowledge would meaningfully improve the response
3. Define rubric criteria specific to what the skill teaches

**Task design principles:**

✅ **Good tasks** test knowledge the skill provides:
- "Implement a retry mechanism for this API call" (if the skill teaches resilience patterns)
- "Write a Dockerfile for this Node.js app" (if the skill teaches Docker best practices)

❌ **Bad tasks** are too generic or don't need the skill:
- "Write a hello world program" (any agent can do this)
- "Explain what Docker is" (factual recall, not applied knowledge)

**Each task must include a rubric** with scoring criteria. Use the 4 default dimensions (see `references/rubric-guide.md`):

| Dimension | What it measures |
|-----------|-----------------|
| `correctness` | Is the output technically correct? |
| `completeness` | Does it cover all relevant aspects? |
| `pattern_adherence` | Does it follow the patterns the skill teaches? |
| `edge_cases` | Does it handle edge cases the skill warns about? |

Write each rubric criterion as a **specific, evaluable statement** tied to what the skill teaches. Example:

```json
{
  "correctness": "Uses connection pooling instead of per-request connections",
  "completeness": "Includes error handling, retry logic, and graceful degradation",
  "pattern_adherence": "Follows the circuit-breaker pattern described in the skill",
  "edge_cases": "Handles timeout, connection refused, and partial failure scenarios"
}
```

Save the completed `benchmark.json` to `<bench-dir>/data/`.

## Step 3: Execute Tasks (A/B Testing)

For each task in `benchmark.json`, dispatch **two sub-agents** that produce outputs independently.

### Configuration: runs per task

By default, each task runs once (`--runs 1`). For statistical significance, use `--runs N` (recommended: 3):

- Each run dispatches 2 sub-agent calls (with + without skill)
- Total calls = tasks × runs × 2
- Example: 5 tasks × 3 runs = 30 sub-agent calls

The `--runs` value is passed to `evaluate.py prepare` later. Plan your file naming accordingly.

### Directory setup

Results go in the `<bench-dir>/results/` directory (already created in the Output Directory step).

### For each task, for each run (1..N):

**Sub-agent A (WITH skill):**
- System prompt: inject the full content of the target skill's SKILL.md
- User prompt: the task's `prompt` field
- Save output to:
  - If runs=1: `<bench-dir>/results/task-{id}-with.md`
  - If runs>1: `<bench-dir>/results/task-{id}-run-{N}-with.md`

**Sub-agent B (WITHOUT skill):**
- System prompt: default (no skill injected)
- User prompt: the exact same task `prompt`
- Save output to:
  - If runs=1: `<bench-dir>/results/task-{id}-without.md`
  - If runs>1: `<bench-dir>/results/task-{id}-run-{N}-without.md`

### Execution rules

- Both sub-agents receive **identical** task prompts — the ONLY difference is the skill injection
- Do NOT give Sub-agent B any hints about what the skill teaches
- Run all tasks before proceeding to evaluation (do not score incrementally)
- If a sub-agent fails to produce output, record the failure and continue

### Sub-agent dispatch pattern

Use whatever sub-agent mechanism is available in your environment. The key contract:

```
For runs=1 (default):
  Sub-agent A: system=<SKILL.md> user=<prompt> → results/task-{id}-with.md
  Sub-agent B: system=(default)  user=<prompt> → results/task-{id}-without.md

For runs=N (N>1):
  For each run 1..N:
    Sub-agent A: system=<SKILL.md> user=<prompt> → results/task-{id}-run-{N}-with.md
    Sub-agent B: system=(default)  user=<prompt> → results/task-{id}-run-{N}-without.md
```

## Step 4: Evaluate

Score each pair of outputs against the task's rubric.

### 4a. Prepare the evaluation

```bash
python scripts/evaluate.py prepare --benchmark <bench-dir>/data/benchmark.json --results-dir <bench-dir>/results/ --output <bench-dir>/data/evaluation.json --runs <N>
```

The `--runs` flag (default: 1) tells the script how many runs to expect per task. It reads the matching result files and produces an `evaluation.json` with structured comparisons for you to score. Each task contains a `runs` array with per-run outputs.

### 4b. Score each comparison

For each task in `evaluation.json`, you'll see both outputs side-by-side with the rubric criteria. Assign a score from **0.0 to 1.0** for each dimension, for each variant:

| Score | Meaning |
|-------|---------|
| 0.0 | Completely fails the criterion |
| 0.25 | Barely addresses it |
| 0.5 | Partially meets the criterion |
| 0.75 | Mostly meets it with minor gaps |
| 1.0 | Fully satisfies the criterion |

**Scoring discipline:**

✅ Score based ONLY on the rubric criteria — not general quality
✅ Score both variants before moving to the next task (avoids drift)
✅ Be consistent — same quality = same score regardless of variant

❌ Do NOT give bonus points for style, verbosity, or unrelated quality
❌ Do NOT let the order (with/without) bias your scoring
❌ Do NOT assume "with skill" should always score higher — measure, don't confirm

Fill the scores directly in `<bench-dir>/data/evaluation.json`.

### 4c. Finalize scores

```bash
python scripts/evaluate.py finalize --evaluation <bench-dir>/data/evaluation.json --output <bench-dir>/data/scores.json
```

This computes aggregate scores, deltas, and statistical summary.

## Step 5: Generate Report

```bash
python scripts/report.py --scores <bench-dir>/data/scores.json --template assets/report-template.html --output <bench-dir>/report.html --lang <language-code>
```

The `--lang` flag sets the report language. Supported: `en` (English, default), `pt` (Portuguese), `es` (Spanish). **Always use the user's native language.**

This produces a self-contained HTML dashboard with:
- **Radar chart**: per-dimension comparison (with vs without skill)
- **Bar chart**: per-task delta scores (how much the skill helped per task)
- **Summary stats**: average delta, win rate, strongest/weakest dimensions

Open the generated `report.html` in a browser to view results.

## Configuration

### Task count

Default: 5 tasks. Override with `--count`:

```bash
python scripts/provision.py --skill-path <path> --count 10 --output benchmark.json
```

**Guidelines:**
- 3–5 tasks: quick sanity check
- 8–10 tasks: thorough validation
- 15+: overkill for most skills, but useful for regression suites

### Runs per task

Default: 1 run. Override with `--runs` in the `evaluate.py prepare` step:

```bash
python scripts/evaluate.py prepare --benchmark benchmark.json --results-dir results/ --output evaluation.json --runs 3
```

Each run produces independent sub-agent calls (with + without skill), so total calls = tasks × runs × 2.

**Guidelines:**
- 1 run: quick check (default, backward compatible)
- 3 runs: recommended for statistical confidence
- 5+ runs: thorough, useful for marginal skills

When using multiple runs, name result files as `task-{id}-run-{N}-with.md` / `task-{id}-run-{N}-without.md`.
For single-run mode (`--runs 1` or omitted), the old format `task-{id}-with.md` still works.

### Custom dimensions

Add custom rubric dimensions beyond the default 4. In the benchmark.json, add fields to the rubric object:

```json
{
  "rubric": {
    "correctness": "...",
    "completeness": "...",
    "pattern_adherence": "...",
    "edge_cases": "...",
    "performance": "Custom: considers runtime/complexity implications",
    "security": "Custom: handles input validation and injection risks"
  }
}
```

The evaluation pipeline handles any number of dimensions — they flow through scoring and into the report automatically.

### Multiple score files (cross-benchmark averaging)

To compare across separate benchmark runs (different benchmarks, not within-task runs), the report script accepts multiple score files:

```bash
python scripts/report.py --scores scores-run-1.json scores-run-2.json --output report.html
```

This averages aggregates across files and shows cross-benchmark variance.

## Self-Evaluation (Dogfooding)

This skill can benchmark **itself**. Point it at its own SKILL.md and measure whether the skill-benchmark instructions actually help an agent produce better benchmarks.

### Why self-evaluate?

If skill-benchmark is effective, an agent with these instructions should produce higher-quality benchmark tasks, more precise rubrics, and more insightful score interpretations than an agent without them. Self-evaluation proves (or disproves) this with data.

### How to run

```bash
python scripts/provision.py --self-evaluate --output <bench-dir>/data/benchmark.json
```

This generates a `benchmark.json` with **5 pre-filled tasks** specifically designed to test benchmarking ability:

1. Design benchmark tasks and rubrics for a given mock skill
2. Score two agent outputs against a rubric with justification
3. Interpret a scores.json and recommend skill improvements
4. Create a complete evaluation rubric for a described skill
5. Explain mixed benchmark results (positive and negative deltas)

These tasks are **pre-filled** — no manual TODO completion needed. The `--count` flag is ignored in self-evaluate mode.

The rest of the pipeline works exactly the same:

```bash
# Execute A/B tests (Step 3) — save to <bench-dir>/results/
# Evaluate outputs (Step 4)
python scripts/evaluate.py prepare --benchmark <bench-dir>/data/benchmark.json --results-dir <bench-dir>/results/ --output <bench-dir>/data/evaluation.json
# ... score comparisons ...
python scripts/evaluate.py finalize --evaluation <bench-dir>/data/evaluation.json --output <bench-dir>/data/scores.json
# Generate report (Step 5)
python scripts/report.py --scores <bench-dir>/data/scores.json --template assets/report-template.html --output <bench-dir>/report.html --lang <language-code>
```

### skill-kit internal evaluations

When benchmarking skills that are part of the skill-kit repo itself (dogfooding), results go in a fixed location:

```
<skill-kit-repo-root>/skill-benchmarks/bench-{skill-name}-{YYYYMMDD-HHmmss}/
```

These results are committed to the repo so users can see comparative benchmark data.

### What self-eval results tell you

- **High delta across dimensions** → The skill-benchmark instructions meaningfully improve an agent's benchmarking ability
- **High pattern_adherence but low correctness** → Instructions teach the format well but don't improve benchmark quality
- **Negative deltas** → The instructions may be over-constraining or confusing the agent

## Interpreting Results

### The delta is what matters

For each dimension, the **delta** = score_with_skill − score_without_skill.

| Delta | Interpretation |
|-------|---------------|
| > 0.3 | **Strong impact** — the skill meaningfully improves output |
| 0.1 – 0.3 | **Moderate impact** — the skill helps but isn't transformative |
| -0.1 – 0.1 | **No significant impact** — the skill doesn't change output quality |
| < -0.1 | **Negative impact** — the skill may be confusing or misleading |

### Win rate

Percentage of tasks where the "with skill" variant scored higher overall. A good skill should have win rate > 70%.

### Dimension analysis

Look at which dimensions improve most:
- **High correctness delta, low pattern_adherence delta**: skill teaches correct approaches but doesn't establish strong patterns
- **High pattern_adherence, low edge_cases**: skill teaches patterns but misses edge cases
- **Uniform improvement across all dimensions**: well-rounded skill

### Red flags

⚠️ **Delta < 0 on any dimension**: the skill may be teaching something counterproductive
⚠️ **High variance across runs**: the skill's impact is inconsistent (prompt-dependent)
⚠️ **High correctness but negative completeness**: the skill narrows focus too much

## Decision Tree

```
User provides skill path or requests self-evaluation
│
├─ Is this a self-evaluation? (--self-evaluate flag or user asks to "evaluate yourself")
│  └─ YES → Run provision.py --self-evaluate, skip Step 2b (tasks are pre-filled)
│
├─ Does SKILL.md exist at path?
│  ├─ NO → Report error, ask for correct path
│  └─ YES → Parse frontmatter + body
│
├─ Run provision.py
│  ├─ Script error → Check --help, fix args, retry once
│  └─ Success → Review template
│
├─ Complete benchmark.json with concrete tasks
│  ├─ < 3 meaningful tasks → Warn: may not be statistically useful
│  └─ Tasks ready → Proceed to execution
│
├─ Execute A/B tests
│  ├─ Sub-agent failure → Record failure, continue with remaining
│  └─ All complete → Check results/ directory
│
├─ Evaluate outputs
│  ├─ Run evaluate.py prepare
│  ├─ Score each comparison (0.0–1.0 per dimension)
│  └─ Run evaluate.py finalize
│
└─ Generate report
   ├─ Run report.py
   └─ Present summary + link to report.html
```

## File Structure Reference

After a complete benchmark run, the output directory contains:

```
bench-{skill-name}-{YYYYMMDD-HHmmss}/
  report.html               ← Visual dashboard (at the root)
  data/
    benchmark.json           ← Task definitions + rubrics
    evaluation.json          ← Scored comparisons
    scores.json              ← Computed aggregates
  results/
    task-01-with.md          ← Sub-agent A output (runs=1 format)
    task-01-without.md       ← Sub-agent B output (runs=1 format)
    task-01-run-1-with.md    ← Sub-agent A output (runs>1 format)
    task-01-run-1-without.md ← Sub-agent B output (runs>1 format)
    task-01-run-2-with.md
    task-01-run-2-without.md
    ...
```

## Common Pitfalls

❌ **Designing tasks that don't need the skill** → Every task must test knowledge the skill specifically teaches. Generic coding tasks won't show a delta.

❌ **Vague rubric criteria** → "Output should be good" is not evaluable. Write criteria tied to specific behaviors: "Uses parameterized queries instead of string concatenation for SQL."

❌ **Scoring bias** → Score both outputs before comparing. Don't let expectations about "with skill should be better" influence scores.

❌ **Too few tasks** → 1–2 tasks can't establish a pattern. Use at least 3, ideally 5+.

❌ **Ignoring negative deltas** → If "with skill" scores lower on some dimension, that's valuable signal — the skill may need revision.

✅ **Good benchmark = specific tasks + specific rubrics + honest scoring**
