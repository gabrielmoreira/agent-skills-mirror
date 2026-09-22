# Data review protocol

The data track screens reported numbers the way the figure track screens
images: a reviewed manifest first, all-pairs screening second, and a human
verdict last. Check selection follows the forensic-statistics workflow
popularized by 耿同学 and packaged in geng-skills
(https://github.com/JasonYan-Bio/geng-skills, MIT); the implementation here is
rounding-aware, pads digits per series, and corrects for multiple testing.

## Why the series manifest is the critical step

A check is only meaningful when a series is one experimental variable measured
independently: one group, one condition, one time point. `prepare` proposes a
series for each vertical block of three or more numeric cells. Before scanning,
edit `series.json` so that:

- each `values` entry is the number **as reported**, as a string, with trailing
  zeros kept (`"12.30"`, not `12.3`). Transcribe PDF tables exactly as printed;
- IDs, sample numbers, years, doses, time axes, p-values, n, and other
  design or summary columns have `"include": false`;
- mean, SD, SEM, and n columns are not mixed with raw observations;
- blocks that stack several groups are split, and wide tables are not read
  across unrelated panels;
- series that are legitimately derived from each other share a
  `derivation_group` (raw and normalized, fold change and its control,
  percent and count, unit conversion, a column computed by formula);
- `label` names the figure, panel, group, and variable.

`formula: true` means the spreadsheet computes some of those cells. Read the
formula before treating a relation involving that series as a concern.

For GRIM and GRIMMER, add one entry per reported mean or percentage to
`means`, with the SD when one is reported:

```json
{"id": "Table1-anxiety-control", "mean": "3.47", "sd": "1.12", "n": 25, "items": 1}
{"id": "Table2-female-treated", "mean": "45.8", "n": 24, "percent": true}
```

`mean` and `sd` are strings exactly as printed. `sd` is the sample SD
(n − 1); convert a reported SEM with SD = SEM × √n only when the paper says it
is SEM, and note that the conversion adds rounding. `items` is the number of
integer items summed or averaged per participant. Both checks apply only to
integer-valued responses or counts. GRIM needs `n × items` below
`10^decimals` (times 100 for percentages); GRIMMER needs an SD precise enough
to constrain the sum of squares. The script counts the rest as untestable.

For p-value recomputation, add each reported test to `tests`, normalized to
APA form:

```json
{"id": "Fig2c-KO-vs-WT", "report": "t(18) = 2.31, p = .032"}
{"id": "Table3-interaction", "report": "F(2, 45) = 3.21, p < .05"}
{"id": "Fig4a-trend", "report": "t(30) = 1.80, p = .041", "tails": 1}
```

Supported: `t(df)` (Welch fractional df included), `F(df1, df2)`,
`χ2(df)` or `chi2(df, N = n)`, `r(df)`, and `z`. The statistic keeps its
printed decimals. Set `tails: 1` only when the paper states a one-tailed test.
Biomedical papers often report only a p-value and a test name; those cannot
be recomputed without the statistic and df, so leave them out.

## Checks

| check | signal | applies when | common innocent explanations |
|---|---|---|---|
| `shared_run` | the same run of ≥4 values (≥3 distinct) appears in two places | any series | the same control group or dataset reused and declared; duplicated rows from a merge; a series pasted twice by mistake |
| `fixed_identical` / `fixed_difference` / `fixed_ratio` / `fixed_linear` | paired rows obey one constant relation within reporting precision | equal-length series, ≥4 rows, ≥3 distinct values each | normalization, background subtraction, unit conversion, percent of total, technical duplicates of one reading, spreadsheet formulas |
| `decimal_match` | paired rows share decimal parts more often than chance | both series span ≥1 whole unit | integer offsets applied by a legitimate transform; low precision; short series |
| `decimal_repetition` | one decimal part recurs within a series | ≥2 decimals, values span ≥1 unit, n ≥ 5 | instrument quantization, calibration steps, values bounded in a narrow band |
| `terminal_digit` | last digits are not uniform | ≥50 values with ≥3 significant digits | rounding to 5 or 10, instrument resolution, integer counts, values truncated by software, mixed precision |
| `benford` | first digits deviate from Benford's law | ≥100 nonzero values spanning ≥2 orders of magnitude | bounded or narrow-range quantities (percentages, pH, ratios near 1), assigned doses, sums of few terms |
| `grim` | a mean or percentage cannot arise from `n` integer responses | integer-valued data, small n | typo, a different n after exclusions, weighted or imputed means, non-integer items |
| `grimmer` | a mean and SD cannot both arise from `n` integer responses (no integer sum of squares, or wrong parity) | integer-valued data, small n, SD reported with enough decimals | SEM reported as SD, population SD (n) instead of sample SD (n − 1), a different n, typo |
| `statcheck` | the reported p does not match the p recomputed from the statistic and df | a test reported with statistic, df, and p | one-tailed test not stated, corrected p (Bonferroni, Holm), a different test than written, typo; a significance change is more serious than a small mismatch |

The p-value checks (`terminal_digit`, `benford`, `decimal_repetition`,
`decimal_match`) share one Benjamini-Hochberg family; `flagged` means
`q < alpha`, and `benford` additionally needs MAD ≥ 0.015. Deterministic
checks (`shared_run`, `fixed_*`, `grim`, `grimmer`, `statcheck`) are flagged
whenever they fire. `statcheck` allows for rounding of the printed statistic
and p, and notes when a mismatch would be consistent with a one-tailed test or
changes significance at `alpha`.
Terminal digits are padded per series before pooling, so zeros dropped by a
spreadsheet are restored without injecting zeros into higher-precision data.

## Weighing evidence

Strongest to weakest:

1. **Shared runs and exact fixed relations** between series that should be
   independent. Long runs, many rows, high precision, and an `exact` relation
   are hard to reach by chance. Check the figure legends and methods for a
   declared shared control first.
2. **GRIM/GRIMMER inconsistencies and p-values that change significance**.
   They prove an arithmetic impossibility or a reporting error, not intent;
   several in one table or analysis deserve a request for the data. A small
   p-value mismatch that keeps the same conclusion is usually a typo.
3. **Within-rounding fixed relations** on short or low-precision series. Treat
   as leads: compare with the plotted values and look for the same relation in
   other panels.
4. **Distributional anomalies** (`terminal_digit`, `decimal_*`, `benford`).
   Rarely meaningful alone. They become relevant when they cluster in the same
   series already implicated by a stronger check, or when a pooled test for
   one source deviates while comparable sources do not.

For every flagged finding, open the table dump in `tables/` and confirm the
cells, locate the series in the paper (figure, panel, legend), and look for an
explanation in methods or supplementary notes. Record negative controls: the
same check on comparable series that did not fire.

## Verdicts

Use the same five verdicts as the figure track:

- **Confirmed duplicate**: the same values appear where independent
  measurements are stated, with no declared reuse or derivation.
- **High-confidence concern**: a strong relation or run whose context cannot
  be fully checked (for example, raw data unavailable).
- **Needs raw data**: GRIM/GRIMMER or p-value inconsistencies,
  within-rounding relations, or clustered distributional anomalies that raw
  data would resolve.
- **Expected derivative**: explained by normalization, formula, declared shared
  control, or unit conversion.
- **Excluded false positive**: an artifact of manifest errors, precision, or an
  inapplicable test.

Report p and q values with their family size, never a composite "fraud score".
