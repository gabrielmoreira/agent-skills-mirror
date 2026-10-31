# Data Quality Gate

Run after `profile_data.py`, before any analysis. Answer each item with
evidence (a computed number, a checked example), not assumption. Items that
can't be verified get flagged in `project-brief.md` as open risks — an
unverifiable item is a finding, not a pass.

## Provenance and coverage

- [ ] Where does this data come from, and what filtered it before it reached
      you? (An extract of "active customers" silently excludes exactly the
      churned ones you study — survivorship built into the file.)
- [ ] Row count reconciles with reality: does N match what the user believes
      exists, at the grain they believe it has?
- [ ] Time coverage matches the question: enough history, no silent
      truncation at either end, and the *most recent* data is complete (last
      week's rows often still trickling in — partial periods masquerade as
      declines).
- [ ] Is this a sample? If so, drawn how? Non-random samples restrict every
      conclusion to the sampled population.

## Structure

- [ ] Primary key confirmed unique — or duplicates explained and a
      deduplication rule decided and recorded.
- [ ] Grain confirmed: one row = one what? Joins upstream of the extract may
      have fanned out rows (revenue double-counted per order line).
- [ ] Column meanings confirmed for every column used — from a data
      dictionary or the user, not guessed from names. `status=3` means
      nothing until someone says so.

## Values

- [ ] Missingness reviewed per key column, with a mechanism hypothesis
      (see `references/eda.md`) — especially whether missingness relates to
      the outcome.
- [ ] Placeholder values hunted: 0, -1, 999, 1900-01-01, "N/A", "unknown",
      empty string — all found by looking at value frequencies, all decided
      (recode to missing? real value?).
- [ ] Ranges plausible: no negative quantities, ages over 120, dates in the
      future (unless legitimate).
- [ ] Units and currencies consistent — mixed EUR/USD or seconds/ms in one
      column is common after system migrations. Timezones: naive timestamps
      from different sources may not be comparable.
- [ ] Categorical values consistent: "VN" vs "Vietnam" vs "Viet Nam";
      case variants; renamed categories mid-history.

## Target integrity (if a target exists)

- [ ] Target constructed per the brief's operational definition, by you, with
      code — not taken on faith from a pre-computed column of unknown lineage.
- [ ] Target rate/distribution sanity-checked against business knowledge
      ("does 40% churn per month sound right to you?").
- [ ] Rows where the outcome is not yet knowable excluded (still inside the
      observation window), not labeled negative.
- [ ] Label timing understood: when is the label assigned, and could it have
      been revised later? (Fraud labels mature over months; recent months
      under-labeled.)

## Verdict

Close with one of: **fit for purpose** / **fit with recorded caveats** (list
them; carry to limitations) / **not fit** (say what's missing and stop —
recommending better data collection is a legitimate engagement outcome).
