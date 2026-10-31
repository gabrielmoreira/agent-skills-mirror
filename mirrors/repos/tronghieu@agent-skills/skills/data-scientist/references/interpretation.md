# Interpretation: What Drives the Model, What Drives the Outcome

Two different questions hide under "what drives X?": *what does the model use?*
(model explanation — answerable with the tools below) and *what actually
causes the outcome?* (a causal question — governed by the causality section of
`references/statistics.md`). Keep them separate in your head and in your
prose; conflating them is the most common interpretation failure.

## Tools, in order of preference

- **Permutation importance** (on *validation* data) — the default global
  answer to "what does the model use?". Model-agnostic, honest about
  generalization. Caveat: correlated features share credit unpredictably;
  permute correlated groups together when it matters.
- **Coefficients** — for linear/logistic models, coefficients with CIs are
  the cleanest story, *if* features are standardized and multicollinearity is
  checked (VIF — see statistics reference). With strong collinearity,
  individual coefficients are arbitrary even though predictions are fine.
- **SHAP** (if `shap` is installed; `TreeExplainer` is fast for tree models) —
  adds local explanations ("why did *this* customer score 0.9?") and
  dependence plots. Use for case-level narratives and debugging surprising
  predictions. Don't paste beeswarm plots into an executive report; translate.
- **Partial dependence / ICE plots** — the *shape* of a feature's effect
  (thresholds, saturation, U-curves). Shapes are often more actionable than
  rankings: "risk jumps once support tickets exceed 3" beats "tickets are
  important".
- **Impurity-based feature importances** (`feature_importances_`) — avoid for
  conclusions: biased toward high-cardinality features and computed on
  training data. Fine as a quick internal sanity check only.

## The sanity pass

Before presenting any importance ranking:

- **Surprises are bugs until proven insights.** A feature nobody expected at
  the top is, in order of likelihood: leakage, an artifact (ID encoding time,
  default values correlating with a system change), then a real discovery.
  Investigate in that order; the leakage checklist has the tests.
- **Importance ≠ direction.** A ranking says nothing about which way a
  feature pushes. Pair every "top drivers" list with direction and shape
  (from PDP/SHAP dependence), or you'll watch stakeholders assume the sign.
- **Importance ≠ lever.** "Tenure is the top feature" does not mean
  "increase tenure to reduce churn" — the model may be reading tenure as a
  proxy for cohort or product mix. Only causal evidence (statistics
  reference, hierarchy levels 1–2) justifies pulling a feature as a lever.
  When the user asks "so should we change X?", that's a new causal question —
  usually the honest answer is "the model can't say; here's the experiment
  that would".

## Translating for the report

In `insight-report.md`, drivers become sentences a decision-maker can act on:
feature name in business terms, direction, shape, size in business units, and
the evidence level ("associated with", unless an experiment says more).

> Customers with >3 support tickets in their first month churn at 2.4x the
> base rate (association; model driver #2; effect flattens after 5 tickets).

Rankings and plots go in an appendix; the top three drivers, translated, go in
the body. If a driver can't be translated into a sentence like the above, it
isn't understood yet — investigate before shipping it.
