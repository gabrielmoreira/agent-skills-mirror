---
name: kayba-stage-5-action-plan
description: Triage each insight into discard/code-fix/prompt-fix and produce a prioritized action plan with specific recommendations. Trigger when the user says "run stage 5", "make action plan", "triage skills", or when invoked by the kayba-pipeline orchestrator. Requires eval outputs from stages 1-4.
---

# Stage 5: Action Plan

Triage each insight and produce a concrete, prioritized action plan.

## Inputs

- `eval/stage1_insights_summary.md` — insights from Kayba
- `eval/stage2_domain_context.md` — domain context
- `eval/baseline_metrics.md` — the evaluation rubric
- `eval/baseline_metrics.json` — baseline values
- `eval/compute_baselines.py` — measurement code

Read all files before starting.

## Process

### 1. Triage each insight

For each insight/skill, answer three questions in order: Is it valid? Is it already handled? Is it a code fix or prompt fix?

#### 1a. Validity check

- Does it describe a real, recurring problem visible in traces — or noise from a one-off edge case?
- Is it actionable — can the agent actually change this behavior given its tools and context?
- If not valid → verdict: **discard** with a one-sentence reason.

#### 1b. "Already handled" verification

Do not rely on memory or assumption. Run these checks and cite what you find:

1. **Grep the codebase** for 2-3 key terms from the insight (tool names, error strings, behavioral keywords). Example: for an insight about cancellation eligibility, grep for `cancel`, `eligibility`, `criteria`.
2. **Read the existing system prompt text** — check `AGENT_INSTRUCTION` in the agent file and the domain policy file. Quote any existing language that addresses this behavior.
3. **Verdict:**
   - If existing text partially covers it → **keep** as a strengthening fix, note what's missing.
   - If no existing coverage → **keep**.
   - If existing prompt text already covers the behavior thoroughly AND the baseline metric is >= 95% → **discard** (cite the existing text and metric). A high baseline alone is NOT sufficient to discard — if the metric is below 95%, there are still failures to fix. An 87% baseline means 1 in 8 attempts still fails; that is worth fixing.

#### 1c. Code-vs-prompt decision tree

Walk through this tree for every non-discarded insight:

```
Q1: Can the agent fix this by following different instructions?
    (Does it have the right tools, correct data in tool responses,
     and sufficient context to behave correctly?)
  │
  ├─ YES → PROMPT FIX
  │        The agent has everything it needs but acts wrong.
  │        A system prompt addition would fix it.
  │
  └─ NO → Q2: What is the agent missing?
           │
           ├─ Tool doesn't exist, schema is wrong, API returns
           │  incomplete data, infrastructure drops information,
           │  timeout/error not surfaced to agent
           │  → CODE FIX
           │    Name the file, function, and specific change.
           │
           └─ The agent has partial information but the prompt
              can't fully compensate (e.g., needs a new tool
              but a heuristic prompt workaround exists)
              → PROMPT FIX (primary) + CODE FIX (optional)
                Note both. Mark the code fix as "optional" with
                a one-sentence justification for why it's lower priority.
```

**Ambiguity default:** When genuinely uncertain, default to **prompt fix** and add a note: `"Classification uncertain — defaulting to prompt fix. Revisit if prompt change doesn't move metrics."` This is safer because prompt fixes are cheaper to test and revert, and Stage 7 handles prompt fixes and code fixes through different paths.

Use the reflector's reasoning from Stage 1 insights — it often explicitly identifies root causes that clarify the code-vs-prompt distinction.

### 2. Consolidate related insights

Before writing recommendations, merge insights that are redundant. Two insights should merge when ALL three conditions hold:

1. **Same target behavior** — they describe the agent doing (or failing to do) the same thing.
2. **Overlapping fix text** — the prompt instructions you'd write for each would share >50% of their content.
3. **Addressing one substantially addresses the other** — fixing insight A would fix >80% of the cases described by insight B.

**When NOT to merge** — two insights about the same tool or domain area but different failure modes should remain separate. Example: "agent doesn't check cancellation eligibility" and "agent doesn't execute cancellation after user confirms" both involve `cancel_reservation` but are completely different behavioral failures with different prompt fixes. Keep them separate.

For each merge, document:
- Which insight IDs are combined
- Which insight's framing is primary (use the one with stronger trace evidence)
- What, if anything, is lost from the secondary insight (add it as a sub-point)

### 3. Write specific recommendations

For each insight (after merging):

- **Discards:** one sentence on why it's not valid or actionable.
- **Code fixes:** what code/schema/infrastructure to change. Name the file, the function, the specific change. If Stage 7 needs to find the right code location, give it enough to grep for.
- **Prompt fixes:** the exact instruction text to add to the system prompt, where it should go (e.g., appended to `AGENT_INSTRUCTION`, added to domain policy, or as a standalone skill block), and why this wording over alternatives.

### 4. Assess risk per fix

For each non-discarded fix, assess whether the change could break currently-working behaviors:

| Risk | Definition | Example |
|------|-----------|---------|
| **None** | Change is additive; no existing behavior could be affected | Adding a new metric to compute_baselines.py |
| **Low** | Change targets a behavior that is currently failing; working cases are unrelated | Adding a cancellation checklist when current cancellation compliance is 0% |
| **Medium** | Change modifies a behavior where some cases already work correctly | Strengthening confirmation protocol when 28.6% already succeed — could the new wording break the working 28.6%? |
| **High** | Change rewrites or constrains a behavior that mostly works | Restricting tool-call patterns when 41.4% already comply — overly rigid wording could cause the agent to under-call tools |

For Medium and High risk fixes, add a one-sentence mitigation: what to watch for, or how to word the prompt to preserve working cases.

### 5. Handle qualitative-only insights — STILL PRODUCE FIXES

Some insights from Stage 3 may be flagged as "unmeasurable." **These still get fixes.** An insight that the agent fabricates data or violates policy is a real problem whether or not we can measure it programmatically. Treat them the same as any other insight:

- Run the same triage (validity → already-handled → code-vs-prompt) as every other insight.
- Include them in the **priority-ranked implementation list** alongside all other fixes. They are NOT second-class.
- Use the trace evidence from the insight (not the metric) to assess impact and priority. If the insight has strong trace evidence showing clear failures, rank it accordingly.
- For prioritization: since there is no metric denominator, use confidence = 0.5 and estimate impact from the severity described in the insight evidence.
- In the fix entry, note that this fix has no programmatic metric for automated before/after comparison, so improvement should be verified via manual trace review or LLM-as-judge after generating new traces.

Only relegate an insight to a non-actionable "Monitor Items" section if the triage concludes it should be **discarded** (not valid or not actionable). Being unmeasurable is NOT a reason to skip fixing it.

### 6. Link to metrics

For each non-discarded fix, identify which metric(s) from the rubric would move if this fix is implemented. Use the metric IDs from `eval/baseline_metrics.md` (e.g., M1, M2).

### 7. Prioritize

Rank non-discarded fixes using this formula:

```
Priority Score = Impact × Confidence × Tier Bonus ÷ Risk Factor
```

Where:
- **Impact** = estimated metric delta. Use the gap between baseline and 100% as the ceiling. A fix expected to close 50% of that gap on M1 (baseline 41.4%) has impact = 0.5 × (1.0 - 0.414) = 0.293.
- **Confidence** = sample size reliability. Use the denominator from `baseline_metrics.json`:
  - denominator >= 20: confidence = 1.0
  - denominator 10-19: confidence = 0.8
  - denominator 5-9: confidence = 0.6
  - denominator < 5: confidence = 0.3
- **Tier Bonus** = leading metrics get a 1.5x multiplier (they validate adoption), lagging and quality get 1.0x. Rationale: leading metrics move first and tell you if your fix is even being adopted — you want those signals early.
- **Risk Factor** = None: 1.0, Low: 1.0, Medium: 1.5, High: 2.0

You do not need to compute exact scores to three decimal places. The formula is a tiebreaker and sanity check. The point is:
- High-impact, high-confidence, leading-metric fixes with low risk go first.
- Low-confidence fixes (small denominators) get deprioritized even if the metric is at 0%.
- High-risk fixes get deprioritized unless impact is overwhelming.

After scoring, apply one manual adjustment pass: if a fix is a prerequisite for another fix (e.g., "confirmation protocol" must exist before "post-confirmation execution" can be measured), promote the prerequisite even if its standalone score is lower.

## Output format

Write to `eval/action_plan.md`:

```markdown
# Action Plan

## Summary
- Total insights: N
- Discarded: X (with reasons)
- Code fixes: Y
- Prompt fixes: Z
- Fixes without programmatic metric (verify manually): Q

## Implementation Priority
| Rank | Fix | Type | Metrics | Risk | Score rationale |
|------|-----|------|---------|------|-----------------|
| 1 | [name] | prompt | M1, M2 | Low | [one-line: why this ranks here] |
| 2 | ... | ... | ... | ... | ... |

---

## Skill: [insight ID(s)] — [title]
**Summary:** [one-line description of what the skill addresses]
**Verdict:** `prompt fix` | `code fix` | `discard`
**Classification path:** [which branch of the decision tree — e.g., "Agent has tools and data but acts wrong → prompt fix"]
**Rationale:** [why this verdict — reference specific trace evidence from insights]
**Risk:** None | Low | Medium | High — [one-sentence justification]
**Risk mitigation:** [for Medium/High only — what to watch for or how to preserve working cases]
**Recommendation:** [specific change to make]
**Files to modify:** [list of files, for code fixes]
**Metric link:** [which metrics would move, with baseline values]
**Already-handled check:** [what you grepped, what existing prompt text you found, verdict]

---
[repeat for each insight]

## Consolidated Prompt Skills
[After all per-insight entries, list the final merged prompt skill texts in priority order, ready for Stage 7 to implement]

## Monitor Items (Non-Actionable Only)
[Only insights that were triaged as genuinely non-actionable — e.g., the agent cannot change this behavior, or the insight is noise. Unmeasurable insights that are still real problems should appear in the priority list above, NOT here.]
```

Group related insights under cluster headings when they address the same underlying behavior. For merged insights, list all constituent insight IDs in the heading.

## Outputs

- `eval/action_plan.md`
