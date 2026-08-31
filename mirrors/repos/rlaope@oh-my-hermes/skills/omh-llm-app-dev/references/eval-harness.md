# LLM Feature Eval Harness

Load this reference when the work is the eval suite: the golden set, the validators, and the comparison that decides whether a prompt or model swap ships.

This is a prepared contract. OMH runs no eval and observes no result. A designed comparison is not a comparison that happened.

## The Deliverables

- **golden set**
- **task-level validators**
- **baseline-vs-candidate comparison**

They are artifacts committed beside the code, not activities described in a chat log. "We tested it and it looked better" is the state this workflow exists to replace.

## 1. The Golden Set

A golden set is a small, committed collection of task inputs with their expected outcomes.

- **Seed it from real failures.** The cases worth keeping are the ones that already broke: the invoice with two dates, the question the retriever missed, the input that produced a confidently wrong answer. A golden set written from imagination measures the imagination.
- **Keep it small and adversarial.** Twenty cases that each isolate a distinct failure beat five hundred that all exercise the happy path. The cost of the set is paid on every run.
- **Store it as data.** A JSON/CSV/YAML file under version control, with a stable case ID per row, so a result can name which cases moved.
- **Grow it on every escape.** Any defect found in production becomes a case before it is fixed. This is the only mechanism that keeps the set aimed at what actually breaks.

## 2. The Validator Ladder

Prefer the most deterministic validator the task allows, and climb only when the rung below genuinely cannot express the check:

1. **Exact or normalized match** - the output is a field, an ID, a label, a number. Compare it. This is a boolean, not a similarity score.
2. **Schema and constraint checks** - the output parses, every required field is present, values are in range, referenced IDs exist. Cheap, deterministic, and catches the majority of real regressions.
3. **Programmatic property checks** - the citation resolves to a real chunk, the summary contains no entity absent from the source, the SQL parses and runs against a fixture.
4. **Model-graded rubric** - only for genuinely open outputs, and only with a fixed rubric, a pinned grader model ID, and a human-labeled sample confirming the grader agrees with people. A model-graded score with an unpinned grader is a moving ruler.

A task-level verdict is pass or fail per case. Aggregate scores hide which case broke; keep the per-case results.

## 3. The Comparison Record

Run the regression **before** the swap, not after it.

- **Same set, same validators, both sides.** Baseline and candidate run against the identical golden set. A comparison whose two sides ran different cases is not a comparison.
- **Pin both sides.** Record the exact model ID and the prompt version for baseline and for candidate. This is the reason both rails exist.
- **Capture tokens and cost per run.** Prompt tokens, completion tokens, and cost belong in the record, because a candidate that is two points better and four times more expensive is a decision, not a win.
- **Report per-case movement.** Which cases newly pass, which newly fail. A net-positive run that broke a case someone reported last month is not an improvement.
- **Missing telemetry stays null.** If the harness did not report tokens, latency, or cost, the field is null and the report says the harness did not report it. Never reconstruct a token count from a pricing table or a character count; an estimate presented beside observed numbers reads as observed.

## 4. What A Result Is Not

- A designed comparison is not a result. Until the run happened and its output was observed, every number is absent, not zero.
- A passing eval is not implementation, review, CI, or merge evidence.
- A golden-set pass rate is a statement about the golden set. It bounds the claim to the cases in the file, and the honest report says so.

## Anti-Patterns

| Pattern | Why it fails |
| --- | --- |
| Eyeballing a few outputs after a prompt edit | The sample is chosen after the change, by the person who wants it to work. |
| One aggregate quality score | It cannot say which case regressed, so it cannot block a swap. |
| Model-graded everything | An unpinned grader drifts, and a rubric nobody validated against human labels measures the grader. |
| Golden set written up front, never grown | It ossifies around the failures imagined on day one and misses every real one. |
| Comparing a candidate against a remembered baseline | The baseline was a different prompt, a different model, or a different day. Re-run it. |
| Estimating cost from a pricing page | An estimate placed beside observed metrics is read as observed. Leave it null. |
