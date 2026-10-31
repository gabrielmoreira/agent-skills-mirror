# Evaluation: Metrics and Judgment

A model is never "good" in the abstract — it's good *for a decision, at a
cost trade-off, against a baseline*. This file covers choosing metrics that
match the decision, reading them honestly, and turning a scored model into a
recommendation.

## Choose the metric from the error costs

Return to the framing brief: which mistake is more expensive? That answer —
not convention — picks the metric.

### Classification

| Situation | Metric | Notes |
|---|---|---|
| Balanced classes, symmetric costs | accuracy is acceptable | The only case where it is |
| Ranking quality, threshold not yet chosen | ROC-AUC | Insensitive to prevalence; deceptively high on imbalanced data |
| Rare positive class (fraud, churn, defects) | **PR-AUC** + precision/recall at chosen threshold | ROC-AUC of 0.95 can coexist with useless precision when positives are 0.5% |
| Probabilities feed a downstream calculation (expected value, pricing) | calibration + Brier score / log loss | See calibration below |
| Fixed capacity to act (call top 1000 customers) | precision@k / lift@k | Matches the actual operation |

**The threshold is a business decision, not 0.5.** A classifier outputs
scores; where to cut is exactly the prescriptive lever from framing. Present
it as a small table — three or four candidate thresholds with, at each, the
business-unit consequences ("flag 8% of transactions, catch 71% of fraud,
17% of flags are false alarms"). Computing that table *is* the deliverable;
choosing the row is the decision-owner's job.

**Calibration:** if anyone will read the score as a probability, check it
(reliability curve, `sklearn.calibration`). Tree ensembles are routinely
miscalibrated; `CalibratedClassifierCV` fixes most of it. An uncalibrated
"87% churn risk" is a lie with decimal places.

### Regression

| Situation | Metric | Notes |
|---|---|---|
| Errors hurt proportionally | MAE | Robust, interpretable in target units |
| Large errors hurt disproportionately | RMSE | Punishes outliers; sensitive to them too |
| Relative error is what matters | MAPE — with care | Explodes near zero actuals, asymmetric (penalizes over-forecast less); consider wMAPE or sMAPE |
| Skewed positive target (revenue, duration) | MAE on log scale, or quantile loss | Model the median/quantiles, not a mean dragged by whales |

Always report MAE *and* the target's scale ("MAE 12.4 days on a median of 30")
— an error metric without scale context is unreadable.

### Forecasting

Evaluate with rolling-origin backtests (train up to t, forecast t+h, slide
forward) — one train/test split is one sample of forecast difficulty. Compare
against the naive forecasts (last value; same period last season): a model
that can't beat "same as last week" is worse than no model, because it costs
maintenance and trust.

## Read metrics honestly

- **Uncertainty first.** Report CV mean ± std, and for the final holdout score
  a bootstrap CI (resample the test predictions). A model "better by 0.004"
  with fold std 0.01 is not better; it's noise wearing a medal.
- **Against both anchors.** Every headline metric appears next to the dummy
  and linear baselines. "PR-AUC 0.41" reads differently when dummy is 0.02
  (17x lift) vs when linear already got 0.40 (the GBM adds nothing — ship the
  linear model).
- **Sliced, not just global.** Compute the headline metric per key segment
  (region, tenure cohort, product line, time period). A global winner that
  fails on 20% of the business — or degrades in the most recent months, hinting
  at drift — needs to be reported as exactly that. Slicing is also where
  fairness problems surface; check any segment where systematically worse
  errors would harm people or violate policy.
- **Error autopsy.** Read 20 actual worst errors — the rows, not the
  aggregate. This is the fastest source of feature ideas, leakage discoveries,
  and label-quality problems, and it grounds the limitations section in
  specifics.

## The verdict

Evaluation ends with a written verdict in `model-card.md`, answering four
questions in business language: Does it clear the bar set in framing? What
does it cost when wrong, and who bears that cost? Where does it not work
(segments, conditions, time ranges)? What has to be true for these numbers to
hold in production (data distribution stable, features available at decision
time, upstream definitions unchanged)?

Before writing the verdict, run `checklists/leakage.md` — the verdict of an
unleakage-checked model is void — then take the whole thing through
`checklists/analysis-review.md` at the review gate.
