# Leakage Gate

Run before believing — let alone reporting — any model validation metric
(non-negotiable #5). Leakage means the model had access to information that
won't exist at decision time; it inflates every metric and evaporates in
production. **Prior: a surprisingly good score is leakage until proven
otherwise.** Going from 0.75 to 0.97 AUC by adding one feature is not a
breakthrough; it's a subpoena for that feature.

## Semantic leakage — features that encode the outcome

For every feature, one question: **could this value be known at the moment
the prediction would be made?** Check the feature's *timestamp semantics*,
not its name.

- [ ] No post-outcome fields: cancellation reason, refund flag, days_to_churn,
      final invoice amount — anything filled in *because* the outcome
      happened.
- [ ] No fields updated retroactively: a `status` or `segment` column showing
      today's value for historical rows (the CRM overwrote history).
- [ ] Aggregate features computed only over each row's *past*: "customer's
      average order value" computed over all time includes post-prediction
      orders. Rolling windows anchored at prediction time.
- [ ] Target-derived transforms (target encoding, per-category outcome rates)
      fit inside training folds only.
- [ ] The framing brief's "available at decision time" line (framing question
      4) re-read and applied to the final feature list.

## Mechanical leakage — the pipeline cheats

- [ ] All preprocessing (imputation, scaling, encoding, feature selection,
      resampling) fit inside training folds — the whole pipeline
      cross-validated, not pre-transformed data.
- [ ] No entity overlap across splits: the same customer/device/document in
      train and test means memorization scored as skill. Group splits when
      rows repeat per entity.
- [ ] Time respected: training data strictly precedes validation data
      whenever predictions will be about the future. No random shuffles over
      time series.
- [ ] No duplicate or near-duplicate rows straddling the split
      (`baseline_model.py` reports exact duplicates; near-duplicates need a
      key-subset check).
- [ ] The test/holdout set touched exactly once, by the final model — not
      consulted during feature selection or model choice.

## Detection probes — when in doubt, test for it

- [ ] **Single-feature probe**: any lone feature scoring near-perfectly
      (AUC > 0.9 alone — `baseline_model.py` scans this) is a leak suspect;
      trace its lineage before keeping it.
- [ ] **Too-good-vs-baseline probe**: final model wildly above the linear
      baseline *and* above what domain intuition says is possible ("we can
      predict churn at 0.99 AUC" — no one can) → hunt the leak.
- [ ] **Importance probe**: a feature nobody expected dominating importance
      rankings (see `references/interpretation.md`) → investigate as leakage
      first.
- [ ] **Time-shuffle probe** (time-structured data): if a random split scores
      far above the time-based split, the gap measures how much the model
      profits from seeing the future — the time-based number is the real one.

## Verdict

Record in `experiment-log.md` and `model-card.md`: checked items, suspicious
features investigated (and their disposition), which probes ran. A metric
reported anywhere without this gate's stamp is a claim, not a result.
