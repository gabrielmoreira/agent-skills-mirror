# Predictive Modeling

Discipline for the Predict flow. The governing idea: **complexity must be
earned**. Every step up — from dummy to linear, linear to trees, defaults to
tuning — is justified only by a measured improvement that survives the
validation spread. This keeps you honest and produces models people can
maintain.

## Before any model: the setup decisions

Three decisions made *before* training determine whether your metrics mean
anything. Get them wrong and everything downstream is fiction.

### 1. Target construction

Build the target exactly as framed in `project-brief.md`. Verify with code:
its rate/distribution matches business expectations, it's constructible for
every row from information that existed at the time, and rows where the
outcome is *not yet knowable* (customers still inside the churn window) are
excluded, not labeled negative.

### 2. Validation split — mirror deployment

The split must simulate how the model will actually be used: trained on what's
known, predicting what isn't. Choose by data structure:

| Data structure | Split | Why |
|---|---|---|
| Independent rows | (stratified) k-fold CV | The easy case; stratify classification |
| Any time dimension + future predictions | time-based split (train past → validate future) | Random splits let the model see the future; scores inflate, sometimes wildly |
| Repeated rows per entity (multiple orders per customer) | group split by entity (`GroupKFold`) | Same entity in train and test = memorization scored as skill |
| Both time and groups | time-based, then check entity overlap | The strictest constraint wins |

When in doubt, the time-based split is the honest default for business data —
almost all of it has a time dimension. `baseline_model.py` supports
`--time-col` and `--group-col`; your own experiments must match its split, or
comparisons are meaningless.

Keep one final holdout untouched until the end. Every experiment iterates on
CV within the training portion; the holdout is spent exactly once, on the
final model. Repeatedly checking it turns it into a validation set and its
score into an advertisement.

### 3. Preprocessing inside the pipeline

Every transform learned from data — imputation values, scaling, encodings,
feature selection — must be fit on training folds only. In scikit-learn this
means: put everything in a `Pipeline`/`ColumnTransformer` and cross-validate
the whole pipeline. Fitting a scaler on the full dataset before splitting is
the most common leakage bug in existence, and it's invisible in the code
unless you look for it.

## The ladder

### Rung 0–1: dummy and linear — run `scripts/baseline_model.py`

Mandatory. The dummy score calibrates the task's difficulty; the linear score
reveals how much signal is linearly available. Read its leakage warnings
before celebrating any score.

### Rung 2: gradient-boosted trees

For tabular business data, gradient boosting (`HistGradientBoostingClassifier`
/ `Regressor`, or XGBoost/LightGBM if installed) is the strongest sensible
default — handles nonlinearity, interactions, mixed types, and missing values
with near-zero preprocessing. Run it at defaults first: the gap between linear
and default-GBM tells you how much nonlinearity the problem contains.

Deep learning on tabular data is almost never the answer; it needs to beat
tuned GBM to justify its cost, and on typical business datasets it doesn't.

### Rung 3: feature engineering

Usually worth more than model tuning. Directions that pay off on business
data: aggregates per entity (counts, sums, recency — "days since last order"
is famously strong), ratios of raw quantities, extractions from timestamps
(hour, weekday, tenure), target encoding for high-cardinality categoricals
(**must** be fit within folds — it's the leakage-prone transform).

For every candidate feature ask the question from framing: *would this value
be available at decision time?* Log each feature batch in the experiment log
with its measured effect; features that don't move validation metrics get
deleted, not accumulated.

### Rung 4: tuning

Last, because its gains are usually smallest. Set a budget (e.g., 50 fits),
use randomized or Bayesian search over the few parameters that matter (for
GBM: learning rate, tree depth/leaves, regularization, n_estimators via early
stopping), always by CV inside the training data. Beware the quiet
overfitting of *many experiments*: after dozens of CV evaluations, the best
CV score is optimistically biased — which is exactly what the untouched
holdout exists to catch.

## Class imbalance

Rare positives (fraud, churn) need care in evaluation more than in training:

- Use PR-AUC / precision-recall, not accuracy (see
  `references/evaluation.md`).
- Prefer class weights (`class_weight='balanced'`) over oversampling;
  if you must resample, resample *training folds only* — never before the
  split, and never the validation data (that fakes the deployment prevalence).
- Don't chase a "balanced" 50/50 training set by default; modern GBMs handle
  moderate imbalance fine, and calibration suffers after resampling.

## The experiment log

Append every run to `experiment-log.md` *before* starting the next idea: data
version, split design, features, model + params, CV mean ± std, and one line
of interpretation. The log is what prevents the two classic failures — 
re-running until a good seed appears, and being unable to reproduce the
number in the final report. If a result isn't logged, it didn't happen.

## When to stop

Stop when one of these is true: the metric meets the framing brief's "good
enough to act" bar; two consecutive rungs yielded improvements smaller than
the CV standard deviation (you're fitting noise now); or the remaining gap to
the bar is clearly a data problem, not a model problem — more/better labels,
missing signal — and say exactly that in the report. Then proceed to
`references/evaluation.md` and `checklists/leakage.md`, and record the winner
in `model-card.md`.
