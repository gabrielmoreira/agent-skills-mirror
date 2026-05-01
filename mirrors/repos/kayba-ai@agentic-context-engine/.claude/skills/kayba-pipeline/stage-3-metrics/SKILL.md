---
name: kayba-stage-3-metrics
description: Define metrics from Kayba insights, implement them as Python measurement code, run against traces, and iterate until the metrics are clean and meaningful. Trigger when the user says "run stage 3", "define metrics", "build metrics", "compute baselines", or when invoked by the kayba-pipeline orchestrator. Requires eval/stage1_insights_summary.md and eval/stage2_domain_context.md to exist.
---

# Stage 3: Metrics and Programmatic Analysis

Define metrics from insights, implement as code, run, review, iterate.

## Inputs

- **`TRACES_FOLDER`** — path to directory containing trace JSON files
- **`eval/stage1_insights_summary.md`** — output from Stage 1
- **`eval/stage2_domain_context.md`** — output from Stage 2

Read both input files before starting.

## Process

This stage is iterative. You cycle through define → implement → run → review, with a hard cap of **3 iterations**. A metric set is "clean" when ALL of the following hold:

1. **No small-sample metrics in the priority set** — every metric used for priority ranking has denominator >= 5. Metrics with denominator < 5 are kept but labeled `"confidence": "directional-only"` and excluded from priority sorting.
2. **No unexplained extremes** — no metric reads 0% or 100% unless you can write a one-sentence justification (e.g., "0% is correct because the agent never calls send_certificate anywhere in the dataset"). Record the justification in the metric's `"extreme_justification"` field.
3. **No redundant pairs** — no two metrics share > 70% of their denominator events. Check this: for each pair, compute `|events_A ∩ events_B| / min(|events_A|, |events_B|)`. If > 0.70, merge or drop one.
4. **Script runs without errors** on the full trace set.

If after 3 iterations the set is not fully clean, ship what you have and log remaining issues in `eval/baseline_metrics.json` under a top-level `"warnings"` key.

### Step 1: Define metrics

For each insight from the Kayba analysis, use the evidence fields to identify observable signals in the traces:

1. Read the insights summary — focus on evidence citations, error strings, behavioral patterns
2. For each valid insight, determine what trace signal would change if the agent followed the skill
3. Classify each metric by detector pattern type:

**Recovery detectors** — consecutive calls to the same function where first has error, next succeeds
```python
def has_recovery(calls, function_name):
    for i in range(len(calls) - 1):
        if calls[i]['name'] == function_name and is_error(calls[i]['output']):
            if calls[i+1]['name'] == function_name and is_success(calls[i+1]['output']):
                return True
    return False
```

**Loop detectors** — N+ consecutive calls to the same function (stuck agent)

**Give-up detectors** — regex match agent output for abandonment phrases ("I'm unable to", "cannot complete", "beyond my capabilities")

**Error classifiers** — match function outputs against domain-specific error patterns. Build a pattern table:
```python
ERROR_PATTERNS = {
    'pattern_name': r'regex matching the error',
    # one entry per distinct error type
}
```

**Over-exploration detectors** — ratio of explore vs action calls. Use the tool categories from Stage 2. If explore ratio exceeds threshold AND task didn't complete → analysis paralysis

**Ground-truth comparison detectors** — agent claims a value (dollar amount, flight number, policy rule) in natural language, and the preceding tool response contains the actual value. Extract candidate values from agent text via regex, then compare against structured fields in the tool response JSON. Examples:
```python
# Extract dollar amounts from agent text
DOLLAR_PATTERN = r'\$\s?([\d,]+(?:\.\d{2})?)'

# Extract flight numbers (3 letters + 3 digits)
FLIGHT_PATTERN = r'\b([A-Z]{2,3}\d{3,4})\b'

def check_agent_claims_against_tool(agent_text, preceding_tool_response):
    """Compare values the agent states against the tool response ground truth."""
    claimed_amounts = re.findall(DOLLAR_PATTERN, agent_text)
    actual_amounts = extract_amounts_from_json(preceding_tool_response)
    # A claim is fabricated if it doesn't match any actual value
    fabricated = [c for c in claimed_amounts if not any(matches(c, a) for a in actual_amounts)]
    return len(fabricated) == 0, fabricated
```
This pattern covers data accuracy (fabricated prices/flights), post-action verification (quoted vs actual cost), and policy accuracy (claimed restrictions vs policy text). These are NOT qualitative-only — regex + JSON comparison is noisy but produces a real signal. Build the detector even if it's imperfect; a noisy metric that produces a fix is better than a clean classification that produces nothing.

**Ordering/sequencing detectors** — agent performs actions in the wrong order (e.g., searches for flights before checking if the reservation is even modifiable). Check whether tool call A appears before tool call B when B should come first.

**Clean success** — threads where all tasks completed with no errors and no other tags

4. **Validate each detector before coding it at scale.** Pick 2-3 traces where you already know the ground truth from Stage 1 evidence. Run your detector logic mentally (or in a scratch script) against those traces. If it misclassifies any of them, fix the logic before writing the full implementation. This catches regex and pattern bugs early — the Stage 3 trace showed multiple iterations wasted on broken confirmation-phrase matching that a quick manual check would have caught.

### Step 2: Implement and run

1. Write `eval/compute_baselines.py` with:
   - CLI args: `--traces-dir` (required), `--output` (default: `eval/baseline_metrics.json`)
   - `load_traces(traces_dir)` — loads all JSON trace files
   - Error pattern table built from reading 20-30 traces
   - `tag_thread(thread)` — combines all detectors, returns list of tags
   - One measurement function per metric, computing `numerator / denominator`
   - `compute_all_baselines(traces_dir)` — runs all metrics, returns dict
   - Main block that runs everything and prints summary

2. Run it:
   ```
   python eval/compute_baselines.py --traces-dir {TRACES_FOLDER} --output eval/baseline_metrics.json
   ```

### Step 3: Review and iterate

Run these checks in order after every run. Each check either passes or produces a concrete fix action.

**Check A — Script health.** Did the script error or produce `null` values? → fix and re-run. This is iteration 0-cost; don't count it toward the 3-iteration cap.

**Check B — Small-sample guard.** For each metric, examine the denominator:
- denominator >= 5 → full-confidence metric, usable for priority ranking
- denominator 1-4 → label `"confidence": "directional-only"` in the output JSON. The metric stays in the report but is excluded from priority sorting in Stage 4. Do NOT drop it — small-sample metrics can still inform qualitative analysis.
- denominator 0 → the detector found no applicable events. Either the detector is broken (fix it) or the behavior genuinely doesn't occur in this trace set (log as `"confidence": "not-observed"` and move on).

**Check C — Extreme-value triage.** For any metric at exactly 0% or 100%:
- Ask: "Is there a plausible trace where this metric would NOT be extreme?" If yes → detector is likely broken, fix it.
- If no (the behavior legitimately always/never happens in this dataset) → write a one-sentence justification and add it as `"extreme_justification"` in the output. Example: M5=0% is correct because both cancellations in the dataset were on ineligible reservations.
- Do NOT reflexively drop 0%/100% metrics. A metric that correctly reads 0% is a strong signal for Stage 5 action planning.
- **Ceiling/floor flag for 100% and 0% metrics:** If a metric baseline is already at 100% (or 0% where 0% is the desired direction), add `"at_ceiling": true` (or `"at_floor": true`) to its entry in the output JSON. This signals to Stage 4 (direction setting) and Stage 5 (action planning) that the metric is already optimal and should NOT be listed as needing improvement. Stage 4 must set its direction to `"↑ maintain"` or `"— already optimal"`, never bare `"↑"`.

**Check D — Correlation / overlap audit.** For every pair of metrics, compute event overlap: `|denom_A ∩ denom_B| / min(|denom_A|, |denom_B|)`. If > 0.70:
- The two metrics are measuring overlapping populations. Keep the one with the sharper behavioral distinction (measures a more specific failure mode). Drop or merge the other.
- In the Stage 3 trace, M1 and M2 shared identical denominators (29 tool-calling turns) and were never flagged. They survived because they measure different *properties* of the same events — this is acceptable only if the numerator overlap is also checked. If both numerators move in lockstep (one is a strict subset of the other), merge them.

**Check E — Coverage (strict).** For EVERY Stage 1 insight, verify it has a corresponding metric. If an insight has no metric:
- First, try harder to build one. Can you extract values from agent text and compare against tool responses? Can you detect the wrong tool-call ordering? Can you pattern-match the failure mode with keywords + JSON field checks?
- Only after a concrete failed attempt, classify as unmeasurable with a specific reason why the approach you tried doesn't work.
- An insight classified as unmeasurable means Stage 5 will NOT produce a fix for it. That is a real cost. Treat every unmeasurable classification as a missed fix.

After checks, if any produced a fix action: apply fixes and re-run (counts as one iteration). If all checks pass → the metric set is clean. **Stop iterating.**

### Design principles

- **Target one metric per insight.** Every insight should have a metric unless it is genuinely unmeasurable (see above). If you end up with fewer metrics than insights, you are being too conservative. Directional-only metrics (denominator < 5) still count — they produce fixes in Stage 5. Only apply the redundancy check (Check D) to merge metrics that truly overlap; do not use the metric count as a reason to skip building detectors.
- **Express every metric as a ratio or percentage.** Absolute counts aren't comparable across trace sets.
- **Prefer per-event denominators over per-thread.** "% of EditScript calls with errors" is sharper than "% of threads with any EditScript error." Per-thread denominators compress information — a thread with 10 violations and a thread with 1 both count the same.
- **One metric per behavioral change.** If two would always move together, keep only the sharper one. Use Check D (overlap audit) to enforce this mechanically, not just by intuition.
- **Build a metric for EVERY insight. "Unmeasurable" is a last resort, not a default.** Before classifying an insight as unmeasurable, you MUST attempt to build a programmatic detector. The bar for "unmeasurable" is: you tried a concrete approach, it fundamentally cannot work (not just "it's noisy"), and you can explain why in one sentence.

  Specifically:
  - **"Agent claims X but tool response says Y"** — this is ALWAYS measurable. Use regex to extract values (dollar amounts, IDs, flight numbers) from agent text, compare against structured JSON fields in the preceding tool response. Noisy matches are fine — a metric that catches 70% of fabrications is far more useful than a qualitative note that catches 0%.
  - **"Agent violates policy rule Z"** — if the policy rule can be stated as a condition on trace data (tool call ordering, presence/absence of a call, argument values), build a detector. Only classify as qualitative-only if the rule requires understanding the *meaning* of free-text agent output beyond keyword/pattern matching.
  - **"Insufficient data"** — if the detector logic is clear but n < 5, build the detector anyway and label it `"confidence": "directional-only"`. Do NOT skip building the metric. A directional-only metric still produces a fix in Stage 5.

  If after genuine effort an insight truly cannot be measured programmatically, classify it as:
  - `"qualitative-only"` — requires semantic understanding that regex/JSON comparison cannot approximate. Must explain what specific semantic judgment is needed and why pattern matching fails.
  - `"insufficient-data"` — detector exists but denominator is 0 (not just small — literally zero applicable events). Note what scenarios would need to appear in traces.
  - `"needs-ground-truth"` — requires task-specific expected outcomes that aren't in the trace format.

  Record any remaining unmeasurable insights in the output JSON under a `"unmeasurable"` key. **The goal is for this list to be as short as possible — ideally empty.**

## Outputs

- `eval/compute_baselines.py` — runnable script with `--traces-dir` and `--output` CLI args
- `eval/baseline_metrics.json` — computed baseline values, structured as:
  ```json
  {
    "M1": {
      "name": "single_tool_call_compliance",
      "value": 0.414,
      "numerator": 12,
      "denominator": 29,
      "confidence": "full"
    },
    "M5": {
      "name": "cancellation_policy_compliance",
      "value": 0.0,
      "numerator": 0,
      "denominator": 2,
      "confidence": "directional-only",
      "extreme_justification": "0% correct: both cancellations in dataset were on ineligible reservations"
    },
    "warnings": ["M5 and M6 have denominator < 5; excluded from priority ranking"],
    "unmeasurable": [
      {
        "insight_id": "d7494740",
        "name": "Cabin Change Constraints",
        "classification": "insufficient-data",
        "reason": "Only 1 update_reservation_flights call in dataset"
      }
    ]
  }
  ```
