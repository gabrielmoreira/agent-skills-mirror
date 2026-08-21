---
name: ab-testing-design-and-analysis
description: "Design, power, run, and analyze statistically valid A/B/N product experiments (sample size, duration, SRM, sequential monitoring, multiple comparisons). Use when pre-registering a test or reading out a controlled split. Not for event instrumentation, funnel diagnosis, wandb ML tracking (weights-and-biases), MVP smoke tests (mvp-scoping-and-risk-test), or RICE scoring (feature-prioritization-frameworks)."
version: 1.0.1
---

# A/B Testing Design and Analysis

This skill governs how the agent designs, powers, runs, and reads out controlled product experiments so that a shipped decision is *caused* by the change — not by noise, peeking, or a broken split. Treat every experiment as a **falsifiable bet placed in advance**: commit to a hypothesis, a metric, a sample size, and a decision rule *before* data arrives, and honor that commitment when the data is inconvenient. The entire value of an experiment is destroyed the moment you let the result you want rewrite the rules you set.

> **Prime Directive:** *Power it before you peek at it. Fix the sample size, the metric, and the decision rule in advance, check the split is honest before you trust the readout, and never let a number you wanted change the rule you set. An experiment without a pre-registered stopping rule is not an experiment — it is a search for a flattering snapshot.*

---

## When to Use

**Design triggers (planning an experiment):**
- "Set up an A/B test / A/B/N test / split test for [feature]."
- "How big does my sample need to be?" / "calculate sample size / power."
- "How long do we need to run this?" / "when can we call it?"
- "What's the MDE I can catch with our traffic?"
- "Design a multivariate / factorial test for [these elements]."
- "Help me write the hypothesis / pick the primary metric / set the alpha."
- "Should this be one-sided or two-sided?" / "what power should I use?"

**Execution triggers (monitoring a running test):**
- "Is the split healthy?" / "check for sample ratio mismatch / SRM."
- "Can I stop the test early?" / "it looks significant already, can we ship?"
- "The two arms have uneven traffic — is something broken?"

**Analysis triggers (reading out a result):**
- "Is this result statistically significant?" / "interpret this p-value / CI."
- "Did the variant win?" / "is this lift real or noise?"
- "Run a t-test / z-test / chi-square on these numbers."
- "Compute the Bayesian probability that B beats A."
- "We tested 12 metrics and 3 are significant — which do I trust?" (multiple comparisons)
- "The overall result reversed when I segmented it." (Simpson's paradox)

**Do NOT use this skill when:**
- The request is about **instrumenting events** (event naming, tracking plans, SDK setup, identity stitching). Route to **telemetry-and-event-instrumentation**. This skill *consumes* clean metrics; if events are wrong, no statistic can save you.
- The request is about **diagnosing where users drop off** and forming a UX hypothesis (funnel analysis, session replay, heuristic friction audit). Route to **conversion-funnel-optimization**, which *produces* the hypothesis this skill then tests. Boundary: funnel work decides *what* and *why*; this skill decides *how to test validly* and *whether it worked*.
- The request is **pure exploratory / observational** with no controlled assignment ("did revenue go up after we shipped X to everyone?"). A before/after with no concurrent control is a **quasi-experiment**; it cannot separate your change from seasonality. Say so and recommend a holdout or switchback design.
- The request is about **bandits / dynamic traffic allocation for pure optimization** (maximize clicks now, don't care *why*). Multi-armed bandits optimize regret, not inference. (Caveat: this skill covers *when to choose* a bandit over an A/B test — see Core Principle 8.)
- The request is about **ML model offline evaluation** (train/test splits, cross-validation, AUC). That is model validation, not product experimentation.
- The request is about **qualitative usability testing** (5-user think-alouds). That informs hypotheses but yields no statistic.

When a request straddles a boundary (e.g., "the events don't exist *and* I want to test a fix"), diagnose under the funnel skill, instrument missing events under the telemetry skill, then design and analyze the experiment here. State the handoff explicitly.

---

## Prerequisites

1. **Clean, trustworthy metrics already instrumented.** If the events are wrong, no statistic can save you — fix instrumentation first (route to telemetry-and-event-instrumentation).
2. **A defined randomization unit** with a stable, persisted identifier (user/account ID). If you cannot assign users to arms deterministically and stickily, you cannot run a valid A/B test.
3. **Knowledge of baseline metric value and variability.** For proportions: the current rate. For means: the current mean and standard deviation. Without a baseline, sample size cannot be computed.
4. **A pre-registered decision rule.** The ship/no-ship/iterate threshold must be set before data arrives. If the user has not committed to one, help them write one before proceeding.

---

## Procedure

Follow the three phases in order — **Design → Execute → Analyze** — and do not advance until each phase's gate is met. The single most common cause of a wasted experiment is starting execution before the design is fully pre-registered.

### Phase 0 — Establish Ground Truth (Before Any Math)

Resolve these before designing. If unknown, ask the user *once*, in a batch:

1. **The change and the mechanism:** What exactly is being changed, and through what causal mechanism is it expected to move the metric? ("Bigger CTA → more clicks → more signups.")
2. **The primary metric:** The single number that decides ship/no-ship. Is it a **proportion** (conversion rate), a **mean** (revenue per user, session length), a **ratio** (clicks per session), or a **count**? The metric *type* determines the test.
3. **The baseline:** The current value of the primary metric and its variability (for means, the standard deviation; for proportions, the rate itself fixes the variance).
4. **The MDE worth caring about:** The smallest effect that would change the decision — set by business value, not by what's easy to detect. This is a *judgment* made before seeing data.
5. **Traffic:** Eligible users/day entering the experiment surface. This caps what is detectable in a sane duration.
6. **Constraints & risks:** Interference/network effects (SUTVA), seasonality, concurrent experiments on the same surface, legal/consent limits, and what cannot be changed.

### Phase 1 — DESIGN (Pre-Register Everything)

#### Step 1.1 — Write the Hypothesis in Standard Form

> *Because [evidence], we believe that [specific change] will [increase/decrease] [primary metric] for [population] by at least [MDE]. We will ship if the observed effect is ≥ [MDE-relevant threshold] and statistically significant at α=[value] with no guardrail regression.*

#### Step 1.2 — Fix α, Power, and Tails

| Quantity | Symbol | Meaning | Default | Effect of making it stricter |
|---|---|---|---|---|
| Significance | α | P(declare effect \| none exists) — false positive | 0.05 | Lower α → larger N |
| Power | 1−β | P(declare effect \| effect exists) — sensitivity | 0.80 | Higher power → larger N |
| Type II rate | β | P(miss a real effect) — false negative | 0.20 | — |
| MDE | δ | Smallest effect worth detecting | business-set | Smaller MDE → **quadratically** larger N |
| Tails | — | One- vs two-sided | Two-sided | Two-sided → slightly larger N |

- **α:** default **0.05**. Lower to 0.01 when a false ship is expensive or irreversible; this raises the sample size.
- **Power:** default **0.80**; use **0.90** for high-stakes decisions. Higher power needs more sample.
- **Tails:** use **two-sided** by default — you must be able to detect a *harmful* effect, not just a beneficial one. Use one-sided only with a strong, pre-committed directional rationale. Never switch to one-sided after seeing data to scrape under 0.05.

#### Step 1.3 — Compute the Sample Size from First Principles

**For a two-proportion primary metric** (e.g., conversion rate), per-variant sample size for a two-sided test:

```
        ( z_{1−α/2} · √[2·p̄·(1−p̄)]  +  z_{1−β} · √[p₁·(1−p₁) + p₂(1−p₂)] )²
  n  =  ─────────────────────────────────────────────────────────────────────
                                    (p₂ − p₁)²

  where  p₁ = baseline rate,  p₂ = p₁ + δ (target),  p̄ = (p₁ + p₂)/2,
         z_{1−α/2} = 1.959964 (α=0.05, two-sided),  z_{1−β} = 0.841621 (power=0.80).
```

Conservative simplification (pooled variance, equal arms):

```
  n ≈ (z_{1−α/2} + z_{1−β})² · [p₁(1−p₁) + p₂(1−p₂)] / (p₂ − p₁)²
```

**Worked example (proportion):** baseline p₁ = 0.20, want to detect a **relative** +5% lift → p₂ = 0.21, so δ = 0.01.

```
  (z_{1−α/2} + z_{1−β})² = (1.95996 + 0.84162)² = (2.80158)² = 7.8489
  p₁(1−p₁) = 0.20·0.80 = 0.16
  p₂(1−p₂) = 0.21·0.79 = 0.1659
  sum = 0.3259
  n ≈ 7.8489 · 0.3259 / (0.01)² = 2.5580 / 0.0001 = 25,580 per variant
  → ~51,160 total for a 2-arm test.
```

Note: a *relative* 5% lift on a 20% base (absolute δ = 0.01) demands ~25.6k per arm; halving the MDE to 2.5% relative (δ=0.005) **quadruples** it to ~102k per arm, because N scales with 1/δ².

**For a continuous / mean primary metric** (e.g., revenue per user), use the standardized effect size (Cohen's d = δ/σ):

```
  n = 2 · (z_{1−α/2} + z_{1−β})² · σ² / δ²        (per variant, equal arms, two-sided)
```

**Worked example (mean):** σ = 40 (revenue SD), want to detect δ = $2.00.

```
  n = 2 · 7.8489 · (40²) / (2²) = 2 · 7.8489 · 1600 / 4 = 2 · 7.8489 · 400 = 6,279 per variant.
```

**For A/B/N (k variants):** split traffic across all arms and apply a multiplicity correction to α (Step 1.5), which raises per-arm N; total traffic need grows faster than linearly in k.

**For multivariate/factorial designs:** estimate main effects efficiently by sharing samples across factors, but **interaction** effects need substantially more data — only run MVT when you have the traffic to power the interactions you care about.

#### Step 1.4 — Apply Variance Reduction to Shrink N (If a Pre-Period Exists)

If users have a pre-experiment value of the metric, apply **CUPED** (Controlled-experiment Using Pre-Experiment Data). Estimate `θ = Cov(Y,X)/Var(X)` on pooled data, replace `Y` with:

```
  Y_cuped = Y − θ · (X − E[X])
```

where `Y` is the in-experiment metric, `X` is the pre-experiment covariate (same user, prior period). The mean of `Y_cuped` is an unbiased estimate of the mean of `Y` (because `E[X − E[X]] = 0`), but with lower variance. Effective sample-size savings ≈ `1 − ρ²` where ρ = corr(pre, post). A ρ of 0.7 cuts variance ~50%, which **halves the required sample size or doubles sensitivity**. Re-derive N (or achievable MDE) with the reduced variance; document the covariate and measured ρ.

#### Step 1.5 — Correct for Multiplicity (If Multiple Variants or Metrics Gate Decisions)

- **k variants vs. one control:** use **Dunnett's** correction, or Bonferroni α' = α/(k−1) as a simple bound.
- **m secondary metrics:** apply **Benjamini-Hochberg** FDR to that family; keep the *primary* metric uncorrected and decision-gating.
- State which family each metric belongs to *before* launch so corrections aren't gamed afterward.

#### Step 1.6 — Compute the Duration and Check Feasibility

```
  duration_days = ceil( total_N_required / daily_eligible_users )
  → round UP to whole weeks to absorb day-of-week seasonality.
  → enforce a minimum of one full business cycle (≥7 days, usually ≥14)
    even if N is reached sooner, so novelty effects and weekly cycles don't bias the readout.
```

If the required duration exceeds a sane window (typically >4 weeks), you are **underpowered**. Options:
1. Raise the MDE (accept detecting only bigger effects).
2. Reduce variance harder (CUPED, stratification, a less noisy metric).
3. Move the test to a higher-traffic surface.
4. Ship as a reasoned, *explicitly un-tested* decision.

**Never run an underpowered test and interpret its noise.**

#### Step 1.7 — Specify Randomization Unit, Analysis Unit, Bucketing, and Decision Rule

- **Randomization unit = analysis unit** (default: persisted user/account ID). If they must differ, pre-commit to **delta method** or **cluster-robust standard errors** to correct the variance.
- **Bucketing:** stable, sticky, salted per experiment. A user sees one variant for the test's lifetime.
- **Decision rule:** ship if primary metric ≥ MDE threshold AND statistically significant at α AND no guardrail breaches. Revert if guardrail breaches or primary significantly regresses. Iterate if inconclusive (CI too wide to decide).
- **Stopping rule:** either a fixed-horizon analysis point (commit to not peeking) or a named sequential boundary (mSPRT, O'Brien-Fleming, Pocock) with a maximum N. Freeze before launch.

#### Step 1.8 — Assess SUTVA / Interference Risk

Does the feature create cross-user spillover (social features, marketplaces, shared inventory, ML models trained on pooled data)? If yes:
- Switch to **cluster randomization** (randomize whole graphs/regions/cohorts so spillover stays within an arm).
- Or use a **switchback** design (alternate the whole system between treatment and control over time blocks to measure the equilibrium effect).
- State the interference assumption explicitly in the readout.

#### Step 1.9 — Define Guardrail Metrics with Harm Thresholds

Every experiment carries **guardrail metrics** with pre-set harm thresholds (latency, error rate, crash rate, unsubscribe rate, revenue). The experiment can only ship if the primary improves *and* no guardrail breaches. Guardrail breaches are the *only* statistically valid reason to stop a fixed-horizon test early.

#### Step 1.10 — Pre-Registration Summary (Freeze Before Launch)

Write down and freeze: hypothesis, primary metric, secondary and guardrail metrics (with thresholds), MDE, α, power, computed N and duration, randomization unit, decision rule, and stopping rule. If you change the design mid-flight, you have started a *new* experiment and the clock resets.

### Phase 2 — EXECUTE (Monitor Honestly)

#### Step 2.1 — Run an A/A Test First

Before the real test, run an A/A test (or offline replay) to verify:
- No spurious significance (at α=0.05, expect ~5% of metrics to show p<0.05 by chance — not more).
- Healthy split (no SRM).
- Instrumentation and logging are correct.

#### Step 2.2 — Ramp with a Kill Switch

- Ramp from a small exposure (e.g., 1–5% of traffic) with a verified **instant kill switch**.
- Monitor for guardrail breaches and SRM during ramp.
- Ramp to full exposure only after initial health checks pass.

#### Step 2.3 — Log an Exposure Event

- An explicit **exposure event** gates analysis to users who actually saw the change.
- Exclude staging/internal traffic, bot traffic, and users who never reached the experiment surface.

#### Step 2.4 — Check SRM Continuously

Run a chi-square test on the observed vs. expected split:

```
  χ² = Σ (observed_i − expected_i)² / expected_i
  df = k − 1 (k arms)
  p-value = 1 - chi2.cdf(χ², df)
```

If p < ~0.001, **halt the test for debugging**. Never "explain away" an SRM. Find the mechanical cause:
- Redirect timing differences
- Asymmetric bot filtering
- Exposure logged at different funnel points per arm
- Caching serving stale variants
- Bucketing hash collisions or non-uniform hash

Fix and rerun. Trusting an SRM-failing readout is the fastest way to ship a phantom win.

#### Step 2.5 — Monitor Guardrails

- Check guardrail metrics against pre-set harm thresholds continuously.
- The only valid early stops on a fixed-horizon test are **guardrail breaches** (or a valid sequential boundary crossing).
- Never stop early because the primary metric "looks significant" on a fixed-horizon test — that is peeking and inflates the false-positive rate from 5% toward 20–30%.

#### Step 2.6 — Hold the Design Fixed

Any mid-flight change (new variant, new metric, changed MDE, changed allocation) restarts the experiment and the clock. State this explicitly to stakeholders.

### Phase 3 — ANALYZE (Read Out Honestly)

#### Step 3.1 — Validate the Data

Before any analysis:
- [ ] SRM passed (χ² p > 0.001).
- [ ] Target N and minimum duration met.
- [ ] Outlier/bot rule applied as pre-committed (winsorization, capping, filtering).
- [ ] Exposure event correctly gates the analysis population.

If SRM fails, **stop**. Do not analyze. Find the cause and rerun.

#### Step 3.2 — Run the Correct Test for the Metric Type

| Metric type | Test | Notes |
|---|---|---|
| Proportion (conversion rate) | Two-proportion z-test | Use pooled or unpooled variance per design |
| Mean (revenue per user, session length) | Welch's t-test | Do not assume equal variances |
| Ratio (clicks per session, under user randomization) | Delta method | Naive variance is wrong; denominator is random and correlated within user |
| Count | Poisson/negative-binomial test | Check overdispersion |
| ≥3 arms | ANOVA + post-hoc (Tukey/Dunnett) | Apply multiplicity correction to post-hoc |
| Contingency table | Chi-square test | — |

#### Step 3.3 — Report Effect Size with Confidence Interval, Judged Against MDE

A p-value answers "is there *an* effect?"; the business needs "*how big*, and how *certain*?" Always report:
- **Point estimate** of the effect (absolute and relative lift).
- **Confidence interval** (or credible interval for Bayesian) around the effect.
- **Judgment against the pre-registered MDE**: a statistically significant 0.1% lift where you needed 2% is a *negative* business result wearing a significant hat. Conversely, an "insignificant" result with a tight CI around zero is a real, informative null; an insignificant result with a CI spanning −10% to +12% is simply *underpowered* and tells you nothing.

#### Step 3.4 — Apply Multiplicity Correction to Secondary Metrics

- **Primary metric:** uncorrected, decision-gating.
- **Secondary metric family:** Benjamini-Hochberg FDR (sort p-values `p_(1) ≤ … ≤ p_(m)`, find the largest k with `p_(k) ≤ (k/m)·α`, reject all up to k).
- **Guardrail family:** Bonferroni or Holm FWER if even one false positive is costly.
- Never report "3 of 12 metrics were significant" without a correction.

#### Step 3.5 — Segment to Understand (Not to Confirm)

Segment results by key dimensions (new vs. returning, platform, geography, traffic source) to:
- Check for **Simpson's paradox** (the overall result reverses within segments — a sign of confounding).
- Understand **heterogeneity** (the effect may be positive for one segment and negative for another).
- Treat subgroup findings as **hypothesis-generating, not confirmatory**. Do not fish for a segment where the result is significant and report it as the real result — that is HARKing.

#### Step 3.6 — Bayesian Readout (If Requested)

If a Bayesian readout is requested:
- Use **pre-committed priors** (state them before data: e.g., a weakly informative prior centered at zero).
- Report **P(B > A)** (or P(B > A) ≥ threshold for ship decision).
- Report **expected loss** (the expected regret if you ship B and it's actually worse — the Bayesian analogue of guarding against false positives).
- Do not switch priors after seeing data to get a more favorable posterior.

#### Step 3.7 — Make the Decision per the Pre-Registered Rule

- **Ship** if primary ≥ MDE threshold AND statistically significant at α AND no guardrail breaches.
- **Revert** if guardrail breaches or primary significantly regresses.
- **Iterate** if inconclusive (CI too wide to decide) — do not ship a non-significant result as if it were a win.
- Ramp the winner with continued guardrail monitoring.
- Re-check for **novelty effects** via a post-launch holdout to confirm the lift persists rather than fading.

#### Step 3.8 — Record the Learning

Log in the experiment record:
- Hypothesis and design (metric, α, power, MDE, computed N, duration, randomization unit).
- SRM and guardrail status.
- Primary result: effect size with CI, judged against MDE.
- Segmented readout and Simpson's paradox check.
- Ship/revert/iterate decision with pre-registered rationale.
- Transferable learning (what does this tell us for future experiments?).

---

## Pitfalls

### Peeking at a Fixed-Horizon Test Inflates False Positives
Stakeholders *will* look at the dashboard daily; pretending otherwise is futile. Peeking at a fixed-horizon test inflates the false-positive rate from a nominal 5% toward **20–30%**. The fix: use **always-valid inference** — **mixture Sequential Probability Ratio Tests (mSPRT)**, **group-sequential boundaries** (O'Brien-Fleming, Pocock), or **always-valid confidence sequences** — which control the error rate *no matter how often you look*. If you genuinely will not peek, a fixed-horizon test is more powerful per-sample; if you will, a sequential method is mandatory, not optional.

### HARKing (Hypothesizing After the Results are Known)
The cardinal sin of experimentation. Choosing the metric, the cutoff, or the segment after seeing the data makes the p-value meaningless. Pre-registration makes this impossible. If you change the design mid-flight, you have started a *new* experiment and the clock resets.

### Sample Ratio Mismatch (SRM)
The most under-appreciated experiment-killer. Even a tiny deviation from the intended split, at high volume, signals that *something selected which users landed in which arm* — and that same selection mechanism almost certainly biases the metric. A 50.2/49.8 split can be hugely significant at millions of users. **Never "explain away" an SRM**; find the mechanical cause and rerun.

### Randomization Unit ≠ Analysis Unit
If you bucket by **user** but analyze by **session** or **pageview**, observations are not independent (one user contributes many correlated sessions), variance is understated, and p-values are too small — you will declare false winners. Either randomize and analyze at the same grain, or use the **delta method / cluster-robust standard errors**.

### SUTVA Violations / Interference
In marketplaces, social graphs, and shared-inventory systems, treating one user changes another's experience, so the control is not a clean counterfactual and the estimated effect is biased. Detect at design time; fix with cluster randomization or switchback design. A SUTVA violation silently invalidates a standard A/B estimate.

### Twyman's Law ("Too Good to Be True")
Any result that is surprisingly large or surprisingly clean is more likely a measurement or logging error than a real effect. A 40% lift on a mature metric should trigger an *instrumentation audit*, not a celebration — check exposure logging, dedup, bot traffic, and SRM before believing it.

### Novelty and Primacy Effects
A change can spike (novelty: users click the shiny new thing) or dip (primacy: regulars are disoriented) in the first days, then revert. Defense: run ≥1 full week (usually two), segment by new-vs-returning, and re-measure the winner in a post-launch holdout.

### Outliers, Heavy Tails, and Ratio Metrics
Revenue and engagement are heavy-tailed; a few whales can dominate the mean and explode the variance. Defenses (pre-commit *before* seeing data): **winsorizing/capping** at a high percentile, **log-transformed** or **bounded** metric, or **rank-based / bootstrap** test. For **ratio metrics** (clicks/session under user randomization), the naive variance is wrong because the denominator is random and correlated within user; use the **delta method**.

### Multiple Comparisons / False Discovery
Testing m independent metrics at α inflates the family-wise false-positive probability to `1 − (1−α)^m` (≈64% at m=20, α=0.05). FWER control (Bonferroni `α/m`, or Holm step-down) bounds the probability of *any* false positive. FDR control (Benjamini-Hochberg) bounds the *expected proportion* of false discoveries among rejections. Never report "3 of 12 metrics were significant" without a correction.

### Simpson's Paradox
The overall result can reverse within segments due to confounding. Always segment by key dimensions and check whether the direction is consistent. If it reverses, the pooled number is misleading — report the segments, not just the aggregate.

### Underpowered Tests
An underpowered test produces noise dressed as a result. An "insignificant" result with a CI spanning −10% to +12% tells you nothing. If traffic can't power a small-MDE test in a sane window: test bigger swings, apply CUPED/stratification, move upstream, use Bayesian with honest wide intervals, or make the change on documented best-practice grounds and **label it un-tested**. Never dress an underpowered noisy result as a validated win.

---

## Verification

The skill's output is successful only when **every applicable** box is satisfied. Treat any unchecked item as a blocking defect.

### Design (Pre-Registration)
- [ ] A falsifiable hypothesis is written in standard form (evidence → change → effect → population → MDE).
- [ ] Exactly **one primary metric** gates the decision; secondary and **guardrail** metrics (with harm thresholds) are listed separately.
- [ ] **α**, **power (1−β)**, and **tails** are set with stated rationale (defaults α=0.05, power=0.80, two-sided).
- [ ] The **MDE** is set by business value before any data, and the **sample size is computed and shown** from baseline + MDE + α + power (correct formula for the metric type).
- [ ] **Variance reduction** (CUPED/stratification) is applied where a pre-period exists, with the covariate and measured ρ documented, and N/MDE re-derived.
- [ ] **Multiplicity** is handled: Dunnett/Bonferroni for k arms, BH-FDR for the secondary-metric family; the primary stays the single gate.
- [ ] **Duration** is computed from N ÷ daily eligible users, rounded up to whole weeks, with a ≥1-business-cycle minimum; if underpowered, the limitation is stated and an alternative chosen explicitly.
- [ ] **Randomization unit = analysis unit** (or delta-method/cluster-robust variance pre-committed); bucketing is stable, sticky, and salted per experiment.
- [ ] **SUTVA/interference** risk is assessed; cluster or switchback design chosen where spillover exists.
- [ ] The **decision rule and stopping rule** (fixed-horizon analysis point *or* named sequential boundary + max N) are frozen before launch.

### Execution
- [ ] An **A/A test** (or offline replay) passed: no spurious significance, healthy split.
- [ ] The experiment **ramped** from a small exposure with a verified instant **kill switch**.
- [ ] An explicit **exposure event** gates analysis to users who actually saw the change; staging/internal traffic excluded.
- [ ] **SRM is checked continuously** with a χ² test; any p < ~0.001 halted the test for debugging rather than being explained away.
- [ ] **Guardrails** were monitored; the only early stops were guardrail breaches (or a valid sequential boundary), never primary-metric peeking on a fixed-horizon test.
- [ ] The design was **held fixed**; any mid-flight change restarted the experiment and the clock.

### Analysis
- [ ] Data validated (SRM passed, target N/duration met, outlier/bot rule applied as pre-committed).
- [ ] The **correct test** was run for the metric type (z for proportions, Welch's t for means, delta method for ratios, ANOVA+post-hoc for ≥3 arms, χ² for contingency).
- [ ] The **effect size with a confidence/credible interval** is reported and **judged against the MDE**, not just against p<0.05.
- [ ] Any **Bayesian** readout used **pre-committed priors and decision thresholds** (P(B>A) and expected loss).
- [ ] Results are **segmented to understand** (Simpson's-paradox check, heterogeneity), with subgroup findings treated as hypothesis-generating, not confirmatory.
- [ ] The decision follows the **pre-registered rule** (ship/revert/iterate); a winner is ramped with continued guardrail monitoring and a **novelty-effect** re-check via holdout.
- [ ] Hypothesis, design, statistic, effect+CI, guardrail status, segment notes, and the transferable learning are recorded in the **experiment log**.

When all gates pass, report: the hypothesis and design (metric, α, power, MDE, computed N and duration, randomization unit), the SRM and guardrail status, the primary result as an **effect size with its interval judged against the MDE**, the segmented readout, the ship/revert/iterate decision with its pre-registered rationale, and the recorded learning. If any gate cannot be met — most often insufficient traffic to power the test, or a failed SRM — state which, why, and the remediation. **Never report a peeked, underpowered, SRM-failing, or HARKed result as a validated win.**
