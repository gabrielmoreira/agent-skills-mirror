# Analysis Review Gate (Red-Team Pass)

The adversarial pass: assume the analysis is wrong and try to prove it. Runs
in two situations — on your own work before any conclusion ships (Phase 6),
and as the entire Review flow when critiquing someone else's analysis,
notebook, or model (including AI-generated analysis).

Work the sections in order; earlier kills are cheaper. For each finding,
verify by running code before reporting it. Findings rank as **fatal**
(conclusion reverses or evaporates), **material** (size/confidence changes
enough to matter), or **minor**.

## 1. Does the arithmetic hold?

- [ ] Re-trace the two or three load-bearing numbers to executed code. In
      others' work, recompute them independently; silent join fan-outs and
      filtered denominators live here.
- [ ] Denominators checked: rate = events / *which* population? Changing
      denominators across a comparison fabricates trends.
- [ ] Aggregation grain consistent: averages of averages, weighted where
      weighting matters?

## 2. Could the data have produced this without the claimed effect?

- [ ] **Selection effects**: who is missing from the data, and are they
      missing *because of* the outcome? (Survivorship: analyzing only
      current customers; collider: analyzing only converted users.)
- [ ] **Data artifacts as findings**: level shifts from system migrations,
      fields populated only after a date, partial recent periods,
      definition changes mid-history — all masquerade as real effects.
- [ ] **Regression to the mean**: entities selected for being extreme
      (worst stores, top users) drift back with no intervention at all.
      Any before/after on a selected-extreme group is suspect.
- [ ] **Seasonality/mix confounds**: is the "effect" a calendar effect or a
      composition change (more of segment A this quarter)?

## 3. Do the statistics survive?

- [ ] **Simpson's check**: does the headline relationship hold within the
      major segments, or does it reverse when split?
- [ ] **Multiple comparisons**: how many tests/segments/metrics were examined
      to find this result? Twenty looks buy one fake discovery for free.
      Garden-of-forking-paths counts even without formal tests.
- [ ] **Effect size vs significance**: is the effect big enough to act on, or
      merely nonzero with big n? Conversely: is "no effect" actually "wide CI,
      learned nothing"?
- [ ] **Assumptions**: independence above all — clustered/repeated
      observations treated as independent overstate confidence (see
      `references/statistics.md`).
- [ ] **Peeking**: for experiments, was the stopping rule fixed in advance?

## 4. Does the causal language match the evidence? 

- [ ] Scan for "causes / drives / leads to / because / impact". Each instance
      earns its verb via the evidence hierarchy (statistics reference) or gets
      rewritten to "associated with".
- [ ] For each claimed driver: name a plausible confounder. If one exists and
      isn't addressed, the claim downgrades.
- [ ] Summary vs body: the executive summary must carry the *weakest* causal
      language in the chain, not the strongest.
- [ ] Model importance presented as levers? (Importance ≠ causality —
      `references/interpretation.md`.)

## 5. For models: is the score real and relevant?

- [ ] `checklists/leakage.md` ran, with its probes — not just its checkboxes.
- [ ] Validation mirrors deployment: split design matches how predictions
      will be used in time and across entities.
- [ ] Beats dummy *and* linear baselines by more than the CV spread.
- [ ] How many experiments preceded this result? Best-of-fifty CV scores are
      optimistically biased; was the holdout spent once?
- [ ] Sliced metrics reviewed: recent time periods (drift), key segments,
      groups where harm concentrates.

## 6. Robustness — does it survive being poked?

Pick the two most conclusion-threatening and run them:

- [ ] Different split/seed/time-window → same conclusion?
- [ ] Outliers excluded (or included) → same conclusion?
- [ ] Reasonable alternative definitions (of target, of segments, of the
      metric) → same conclusion?
- [ ] Placebo test where applicable: does the "effect" also appear where it
      logically can't (pre-period, unaffected group)? If yes, the method
      manufactures effects.

## 7. Honest packaging

- [ ] Uncertainty attached to every reported estimate.
- [ ] Limitations section written, specific, and includes this checklist's
      surviving concerns.
- [ ] Charts don't overclaim: axes not truncated to inflate, no dual-axis
      insinuation, ranges shown where they exist.
- [ ] "So what" passes: conclusions connect to the decision in the brief.

## Verdict

For own work: fix fatal and material findings (back to Phase 4/5); surviving
concerns go verbatim into the Limitations section. For the Review flow:
deliver findings ranked fatal → material → minor, each with the code that
demonstrates it and a concrete fix — structured per the critique format in
`references/communication.md`.
