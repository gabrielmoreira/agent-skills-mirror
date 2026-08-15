---
name: hmda-analysis
description: >-
  Pull and describe HMDA mortgage-lending data (LAR records) for a county,
  state, lender (LEI), or multiple years, and compute a CRA-PROXY borrower- and
  tract-income distribution. Use when the user says "pull HMDA data", "LAR
  records", "mortgage lending data for [county/state/lender]", or "multi-year
  HMDA". DESCRIPTIVE ONLY — this skill does not do disparity, disparate-impact,
  or fair-lending analysis. Backed by the audited PyPI package hmda-analyzer.
compatibility: >-
  Requires Python >=3.9, pip, and network access to pypi.org plus ffiec.cfpb.gov
  (CFPB HMDA API for LAR records). Pin `hmda-analyzer>=0.6.0`: 0.6.0 is where the
  geography-vintage refusal first exists, and nothing below it has one.
  Full-state and multi-year pulls transfer large volumes of records.
---

# HMDA Analysis (descriptive)

Pulls HMDA LAR data from the CFPB API and produces **descriptive** cuts —
lending by county/state/tract, top lenders, and a **CRA-proxy income
distribution** — via the published, audited **hmda-analyzer** package.

## FIREWALL — read before anything else (non-negotiable)

**This skill is DESCRIPTIVE ONLY.** It does not perform, and the AI must not
produce using it:

- disparate-impact or disparity-ratio analysis
- protected-class (race/ethnicity/sex) stratified denial or approval analysis
- any "fair lending" screening, inference, statistical significance, or
  disparity claim
- any interpretation of the CRA-proxy output as CRA performance, a CRA rating,
  or an assessment-area result

**If the user asks for inferential fair-lending analysis, decline and explain
the descriptive/inferential distinction:** this skill counts and distributes
what was lent (descriptive); disparity/disparate-impact analysis draws
inferential conclusions about *why* and *whether lending is discriminatory*,
which requires court-defensible methodology, protected-class stratification, and
significance testing that this skill deliberately does not do. Do **not** point
the user to any fair-lending tool as the "v1 alternative" — just hold the line
on the distinction.

The installed `hmda-analyzer` package *does* expose disparity functions
(`disparity_ratio`, `denial_rate_by_race`, `denial_reasons_by_race`,
`denial_rate_by_income_band`, `generate_disparity_report`, `summary_table` —
whose output is a disparity-by-race table — and `racial_composition_by_tract`).
**This skill does not wrap them.** Treat them as out of scope; if the user wants
them, that is the inferential territory above.

`denial_rate_by_income_band` is firewalled for the same reason as its siblings
even though income band is not a protected class: it ships in
`hmdaanalyzer.analysis.disparity`, its own docstring states its purpose as "to
identify income-based disparities," and it is a denial-rate stratification. This
skill distributes what was lent; it does not rate denial outcomes against a
stratifier. Verified against 0.6.0's 33 exports — the firewall list is complete.

## When to use

- "Pull 2023 HMDA LAR records for Rhode Island."
- "Show mortgage lending by county for this state."
- "Multi-year HMDA for county 17031, 2022–2023." — one basis on every key; nothing refuses.
- "Multi-year HMDA for county 17031, 2020–2023." — **spans the 2021→2022 boundary**; the package
  refuses any tract- *or* county-keyed cut on this frame. See the geography-vintage rule below.
- "Multi-year HMDA for county 17031, 2022–2024." — **spans the 2023→2024 boundary**; also refuses.
  Both are answerable, as two labelled panels or with `vintage=`, never as one pooled table.
- "What's the CRA-proxy borrower-income distribution for this pull?"

## When NOT to use

- Any request in the FIREWALL list above (disparity / fair lending / CRA
  performance).
- Pre-2018 HMDA / CIIS-era TLR — the loaders target the canonical **2018+**
  column schema.

## Install

```
pip install "hmda-analyzer>=0.6.0"
```

**Pin the floor — this is the most important line in this section.** The
geography-vintage refusal does not exist below **0.6.0**: 0.5.0 has no such
refusal at all, and that is what the floor guards against. (0.6.0 alone required
**Python >=3.11**; **0.6.1 relaxed `requires_python` back to `>=3.9`** while
keeping the refusal, so the pin installs on any interpreter this skill supports.)
Verify before quoting any number:

```python
import hmdaanalyzer as h
print(h.__version__)          # must read 0.6.0 or later
```

If it reads 0.5.0, say so and stop; do not present results from it as 0.6.0
results.

Verified 2026-08-13 against `hmda-analyzer>=0.6.0` (PyPI; resolved 0.6.1 at the
time). Quote the floor, not the resolved point version — the point version moves
on every release and this line does not.

**Dual import aliases** — both resolve to the same package and report the same
`__version__` (verified 2026-08-13 against `hmda-analyzer>=0.6.0`):

```python
import hmda_analyzer as h     # underscore alias
import hmdaanalyzer as h      # no-underscore alias — equivalent
```

## Loading data

- `load_from_api(year=2023, state=None, lei=None, county=None, limit=10000)` —
  single-year pull from the CFPB API.
- `load_range(start_year, end_year, state=None, lei=None, county=None,
  limit=10000)` — inclusive multi-year pull; adds an `activity_year` provenance
  column.
- `load_sample(n=5000, seed=42)` — offline synthetic sample (note: the sample
  frame does **not** carry the FFIEC income columns, so `cra_proxy_distribution`
  cannot run on it — use a real pull for the proxy).

**`load_range` fail-loud contract (verbatim from the package docstring):**

> * **Fail-loud, no partial.** If ANY year's fetch raises, `load_range`
>   re-raises immediately with the failing year named and returns NO frame —
>   there is no catch-and-continue and no partial result.
> * **Schema guard.** Every fetched year is validated against the canonical
>   2018+ column set; a missing or unexpected column raises
>   `SchemaValidationError` (naming the year).
> * **Provenance.** The native `activity_year` field is used and asserted to
>   match the requested year; a wrong-year payload raises
>   `ActivityYearMismatchError`.
> * **Legitimate empty.** A valid year that simply matches zero rows is NOT an
>   error — its correctly-columned empty frame participates in the concat.

So: **never report a partial multi-year result.** If `load_range` raises, name
the failing year and report the error — do not present the years that happened
to succeed.

### `limit=` truncates; it does not sample (non-negotiable)

Verbatim from the `load_from_api` docstring:

> ``limit`` TRUNCATES; it does not sample.
>     The rows you get back are the FIRST ``limit`` rows the server emitted,
>     in the file's own order. That order is not random with respect to
>     lender, geography, race, or outcome, so a denial rate computed on a
>     truncated pull describes an arbitrary slice of the state while looking
>     exactly like a statistic about the state. When the stream was cut short
>     every returned row carries ``limit_truncated = True``; when the whole
>     file fit under ``limit`` every row carries ``False``. Check that column
>     before quoting any number from the frame, and raise ``limit`` (or filter
>     by ``county=``) until it reads ``False`` if you need the population.

Every loaded frame carries the column — `limit_truncated`
(`hmdaanalyzer.data.schema.TRUNCATED_COLUMN`), written **even when `False`**, so
its absence can never be mistaken for "not truncated." Rules:

- **Never call a truncated pull a "sample."** It is the first *N* rows in server
  file order. Do not describe it as random, representative, or a sample of
  anything.
- **If `limit_truncated` is `True` anywhere, say so beside the number** — in the
  same sentence or the same table footnote, not in a preamble the number can be
  extracted away from.
- **Under `load_range`, truncation is per year.** `limit` applies to each year's
  fetch independently, so the column is **not uniform across the frame**. Check
  it per year, verbatim from the `load_range` docstring:

  > **Truncation is per year and is recorded per row.** ``limit`` applies to
  > each year's fetch independently, so a range can be complete in one year
  > and truncated in another. ``limit_truncated`` is therefore NOT uniform
  > across the returned frame — check it per year
  > (``df.groupby("activity_year")["limit_truncated"].any()``) rather than
  > once for the whole thing. A year-over-year comparison in which one year
  > was truncated and another was not is comparing a slice to a population.

## The geography-vintage rule (non-negotiable) — the package now REFUSES

**In 0.5.0 this was an instruction the AI had to remember. In 0.6.0 the package
enforces it.** Six guarded geography-keyed aggregation sites — across the five
public functions `lending_by_tract`, `lending_by_county`, `lending_desert_score`,
`racial_composition_by_tract`, and `lender_summary` (which is guarded twice, once
per key) — call one shared guard and raise **`GeographyVintageError`** on a
vintage-spanning frame. `lending_by_state` is deliberately **unguarded** (see
below).

### Rule zero: never route around the refusal

- **No `try`/`except GeographyVintageError` that proceeds anyway.** `except
  ValueError` catches it too, since every refusal in this package subclasses
  `ValueError` — do not write one around a guarded call.
- **No hand-rolled `df.groupby("census_tract")` / `groupby("county_code")`** to
  recover the number the package declined to give. That is the exact silent
  defect the guard exists to prevent, and doing it by hand does not make it true.
- **No crosswalking 2010 tracts to 2020 tracts yourself.** HMDA carries no
  sub-tract location, so any conversion allocates proportionally and produces
  fractional loan counts. The library refuses to; so do you.
- **If it refuses, that is the answer.** Report the refusal, name which of the
  two shapes below fired, and offer the two paths. A refusal is a finding about
  the question, not an obstacle to the answer.

### The two boundaries

| Boundary | Key that moves | Shape | Scope |
|---|---|---|---|
| **2021 → 2022** | census tract **and** county FIPS | GEOIDs are **reused for different ground** — silent collision | national |
| **2023 → 2024** | county FIPS (and therefore every tract GEOID's first five digits) | keys are **disjoint** — a pooled frame doubles rows | Connecticut only; the refusal is national |

**2021 → 2022 (decennial).** Data years 2018–2021 carry **2010** census tracts;
2022–2023 carry **2020** census tracts. A GEOID present in both years can denote
two different polygons, so grouping across it silently sums two places into one
row. The county key moves here too — see the Alaska correction below.

**2023 → 2024 (Connecticut).** Connecticut replaced its eight legacy counties
(`09001`…`09015`) with nine planning regions (`09110`…`09190`) for federal
statistical use — 87 FR 34235, 2022-06-06; Census lists it as the **sole**
county-equivalent change of the 2020s. It lands in the LAR at 2023→2024. The two
code sets share **zero** members, so nothing silently merges — instead a pooled
frame carries both schemes and *doubles* the row count for Connecticut, and every
statistic computed against a reference distribution (`app_percentile`,
`desert_score`, `is_lending_desert`) is computed over the combined key set and is
wrong for **both** years. The package's own measurement on CT 2023+2024: 0 shared
tract keys of 872, 1,695 of 1,742 tract-years get a wrong percentile, and 25
`is_lending_desert` verdicts flip — while the aggregate desert count moves only
384 → 381, so nothing in the output looks anomalous enough to prompt a second
look.

The authoritative maps are top-level exports; read them rather than retyping
years:

```python
h.TRACT_GEOID_BASIS_BY_YEAR   # {2018-2021: 2010, 2022: 2020, 2023: 2020}  <- 2024, 2025 ABSENT
h.COUNTY_CODE_BASIS_BY_YEAR   # {2018-2021: 2010, 2022-2023: 2020, 2024: 2023}
h.MSA_CODE_BASIS_BY_YEAR      # {2018-2021: 2010, 2022-2023: 2020, 2024: 2023}
h.basis_year("census_tract", 2024)   # -> None, i.e. UNMAPPED
```

`MSA_CODE_BASIS_BY_YEAR` has **no guard** — the package has no aggregation on
`derived_msa_md`. If you group on it yourself, you own the check.

### Two distinct refusals, with different remedies — do not conflate them

Conflating these produces advice that does not work. Both are resolved the same
two ways, but only one of them is *about* a boundary at all.

**(1) Unmapped year.** **2024 and 2025 have no cited tract basis** — they are
deliberately absent from `TRACT_GEOID_BASIS_BY_YEAR`, because nobody has read and
cited the FFIEC census file vintage for them. A single unmapped year alone is
**fine and is not refused**; pooling one with *any* other year refuses. Quoted
from the installed package (`h.lending_by_tract` on a 2023+2024 frame):

```
lending_by_tract refused: this frame pools data year(s) 2024 — for which no cited census_tract basis exists — with 2023.
  A single unmapped year on its own is fine and is NOT refused; pooling one with another year is refused because nobody can say whether the keys mean the same thing.
  To add a year: read the Census geography vintage the FFIEC census file for that year adopts (HMDA tract codes follow the FFIEC file, not the decennial delineation directly — a year can keep the 2020 delineation and still change file vintage). The CFPB *Summary of {year} Data on Mortgage Lending* states it for 2021-2023; the series does not continue past 2023, so for 2024 onward the FFIEC file is the source; confirm the basis; add the entry to TRACT_GEOID_BASIS_BY_YEAR in hmdaanalyzer/geography_vintage.py; and cite it in the comment. Do NOT infer it from the data — that is the defect this rule exists to prevent (methodology §M1.3).
  What to do instead (methodology §M5.2):
    1. ENDORSED: split at the boundary and present two panels with an explicit, labelled break. No estimation, no non-random subsetting.
    2. Narrow to one basis: lending_by_tract(df, vintage=<basis year>). This selects a coherent subset; it never merges two delineations.
    3. Aggregating up to county or MSA is NOT an escape route — those keys move too, and at overlapping boundaries (§M2.3). The county key is guarded; derived_msa_md is not, because the package has no aggregation on it.
    4. Build a crosswalk yourself, outside the library, and own the estimate. The library will not: HMDA carries no sub-tract location, so any conversion allocates proportionally and produces fractional loan counts (§M5.1).
```

This is **not** a claim that 2024 differs from 2023. It is an assertion of
ignorance. **Excluding a state does not help**, and neither does excluding
anything else — see the filtering rule below.

**(2) Two cited bases in one frame.** The frame spans a real, cited boundary.
Quoted from the installed package (`h.lending_by_county` on a 2023+2024 frame) —
the refusal names the Connecticut cause and prices itself:

```
lending_by_county refused: this frame spans more than one county_code basis — basis 2020 (2023); basis 2023 (2024).
  Caught by its own map.
  1 of 1 county_code keys appear in every year present and would be merged; they carry 100.0% (2023) and 100.0% (2024) of rows.
  This boundary is CONNECTICUT-CONFINED. The 2023->2024 county change is Connecticut replacing its eight legacy counties (09001..09015) with nine planning regions (09110..09190) for federal statistical use (87 FR 34235, 2022-06-06); Census lists it as the SOLE county-equivalent change of the 2020s. Measured independently here across all 50 states and DC (20.7M LAR rows), Connecticut is the only state whose county_code SCHEME changes. If your frame contains no Connecticut rows, the keys really do mean the same thing in both years and this refusal is costing you an analysis that would have been correct.
    It is still a refusal, deliberately: a national key scheme did change, and deciding on your behalf that your rows are unaffected is the silent inference this library exists to not make.
    FILTERING THE FRAME IS NOT A WAY THROUGH, and this message used to say it was. The verdict above is computed from the YEARS the frame spans, never from the rows it contains — so dropping every Connecticut row leaves 2023 and 2024 both present and the identical refusal fires on the filtered frame. That is deliberate (§M1.2b, coverage item 19): a verdict that depended on which rows you kept could be disarmed by subsetting. Two ways through, both exact, and both change the YEARS rather than the rows:
      a. ENDORSED: split at the boundary and present two panels with an explicit labelled break. Keeps Connecticut in, no estimation, no non-random subsetting (§M5.2 option 1).
      b. Narrow to one basis with vintage=. For this boundary that is vintage=2020 (selects the 2023 rows) or vintage=2023 (selects the 2024 rows) — the basis year, not the data year.
```

The 2021→2022 boundary produces the same shape on the tract key
(`lending_by_tract refused: this frame spans more than one census_tract basis —
basis 2010 (2021); basis 2020 (2022).`). When the refusal is reached through
`lending_desert_score`, the message names **`lending_desert_score`**, not
`lending_by_tract` — read the function name in the message; it is the one the
user called.

Note which refusal you get is a function of the **key**, not the boundary: at
2023→2024 a *tract*-keyed call hits refusal (1) — 2024 is unmapped for tracts —
while a *county*-keyed call hits refusal (2), because both 2023 and 2024 have a
cited county basis. Only the county key surfaces the Connecticut message.

### Filtering rows is never a way through — say this explicitly

It is the intuitive thing to try, so state it before the user tries it: **the
verdict is computed from the YEARS the frame spans, never from the rows it
contains.** Dropping every Connecticut row leaves 2023 and 2024 both present and
the identical refusal fires on the filtered frame. The same holds for any
row-level filter that is not a year filter — by state, county, lender, race, or
loan purpose. A verdict that depended on which rows you kept could be disarmed by
subsetting, which is precisely why it does not.

The one filter that *does* change the answer is a filter on `activity_year` — and
that is not a workaround, it is path (a) below. Do it as a labelled split, not as
a quiet subset, and never present the surviving years as though they were the
range the user asked for.

### The two paths that do work

Both change the **years**, not the rows.

**a. Split at the boundary — ENDORSED.** Two labelled panels with an explicit
break, each stamped with its basis. No estimation, no non-random subsetting, and
Connecticut stays in.

```python
early = df[df["activity_year"] <= 2021]      # 2010 tract basis
late  = df[df["activity_year"] >= 2022]      # 2020 tract basis
h.lending_by_tract(early); h.lending_by_tract(late)   # label each panel
```

**b. Narrow with `vintage=`.** Available on every guarded function this skill
wraps — `lending_by_tract`, `lending_by_county`, `lending_desert_score` and
`lender_summary` (also on `racial_composition_by_tract`, which is firewalled and
which you should not be calling). It takes the **basis year, not the data year**
— `vintage=2020`
selects the 2022–2023 rows on the tract key, `vintage=2023` selects the 2024 rows
on the county key. It is a narrowing, not an override: it never merges two
delineations, and the guard still runs afterwards, so a narrowing that leaves an
incoherent frame still refuses. Naming a basis the frame does not contain raises
rather than returning an empty table.

Guarded output carries its own provenance, and it is **always** present — report
these columns whenever you render a guarded table:

```
tract_geoid_vintage, tract_geoid_vintage_status,     # status: CITED | UNKNOWN | NO_YEAR_COLUMN
county_code_vintage, county_code_vintage_status,
vintage_dropped_rows                                  # how many rows a vintage= narrowing removed
```

`lender_summary` returns a dict and carries the same facts as explicit keys
(`census_tract_basis_year`, `census_tract_basis_status`, `county_code_basis_year`,
`county_code_basis_status`, `dropped_rows_by_year`).

### What is NOT affected

- **`cra_proxy_distribution`** classifies each row using the income percentage
  carried **on that row**, so it never joins across tracts or groups on a
  geography key. A multi-year CRA-proxy distribution spanning either boundary is
  sound, and its per-year cut remains correct. It is unguarded and does not
  refuse. Do not suppress it.
- **`lending_by_state`** is unaffected and deliberately **unguarded**, on an
  argument from absence: nothing was measured to move a state code in 2018–2025.
  Verbatim from the function's docstring — *"That is not a demonstration that
  they cannot [move]. If a state-level equivalent of Connecticut's county
  restructuring occurs, this key fails exactly as the county key did and nothing
  here would notice."*
- **`top_lenders_by_volume`**, **`lender_vs_market`**, and per-row work generally
  are unaffected — they key on `lei`, not on geography.

**`lending_by_county` IS affected — it is guarded, and this skill previously said
otherwise.** County FIPS changed at **both** boundaries. At 2021→2022, Alaska
retired `02261` (Valdez-Cordova) into `02063` (Chugach) + `02066` (Copper River).
Verified this session against live LAR, full-state Alaska pulls with
`limit_truncated=False` in both years: `02261` carries **323** rows in 2021 and
**0** in 2022; `02063` and `02066` carry **0** in 2021 and **158** and **40** in
2022. A pooled 2021+2022 `lending_by_county` fragments one county into three
rows. The scope is narrow — one county at one boundary, plus Connecticut at the
next — so **do not over-correct into "all county work is unsafe."** Single-vintage
county work is entirely sound; it is the pooled frame the package refuses.

## Worked example — descriptive lending cut (executed)

```python
import hmda_analyzer as h
df = h.load_sample()                 # 5000 rows, offline
lc = h.lending_by_county(df)
print(lc.head(5).to_string(index=False))
```

Actual output this session, on 0.6.0 (`load_sample()` is single-year 2023, so the
guard passes and stamps the basis):

```
county_code  applications  denials  originations  total_loan_volume  avg_loan_amount  denial_rate state_code  county_code_vintage county_code_vintage_status  vintage_dropped_rows
      26067             8        0             8            2976002    372000.250000          0.0         26                 2020                      CITED                     0
      42066             8        1             7            3317790    414723.750000        0.125         42                 2020                      CITED                     0
      37076             8        0             8            1497582    187197.750000          0.0         37                 2020                      CITED                     0
      12143             8        0             8            2715158    339394.750000          0.0         12                 2020                      CITED                     0
      06001             7        1             6            2661144    380163.428571     0.142857         06                 2020                      CITED                     0
```

**The three trailing columns are new in 0.6.0** and appear on every guarded
output. `county_code_vintage_status = CITED` means a basis was established from
`activity_year`; `UNKNOWN` means the year is unmapped and no basis is asserted;
`NO_YEAR_COLUMN` means the frame had no `activity_year` to derive one from. The
status is written even when a basis *was* found, so its absence can never be the
signal. `vintage_dropped_rows` is `0` here because no `vintage=` narrowing was
requested — it too is always written.

Descriptive functions this skill wraps: `lending_by_county`, `lending_by_state`,
`lending_by_tract`, `top_lenders_by_volume`, `lender_summary`, `lender_vs_market`,
`lending_desert_score`, and `cra_proxy_distribution`. (`summary_table` is **not**
wrapped — its output is a disparity-by-race table, which is firewalled; nor are
the other functions in the FIREWALL list above.)

**`lending_by_tract`, `lending_by_county`, `lending_desert_score` and
`lender_summary` are guarded** — they raise `GeographyVintageError` rather than
returning a pooled number. Check the frame's `activity_year` range before calling
them, and read the geography-vintage rule above.

### `lender_vs_market` — surface the suppression columns every time

A silent 5-application threshold (`MIN_APPLICATIONS_FOR_RATE`, in
`hmdaanalyzer.data.schema`) drops any `derived_race` group below it. In 0.5.0
groups vanished with nothing on the output recording it. **0.6.0 discloses it on
the frame**, in six columns — three per side, because the two frames are
suppressed independently:

```
lender_suppressed_groups   lender_suppressed_applications   lender_suppressed_group_names
market_suppressed_groups   market_suppressed_applications   market_suppressed_group_names
```

**Surface these whenever you render this table — the same way you surface the
CRA-proxy caveat.** An absent group that is not named reads as a group with no
lending. Verified this session on a 60-row frame: `market_suppressed_groups = 5`,
`market_suppressed_applications = 10`, `market_suppressed_group_names = "2 or more
minority races; Asian; Joint; Native Hawaiian or Other Pacific Islander; Race Not
Available"` — five protected classes gone from a table that gave no other sign.

A row absent from this table is usually absent because the **lender** had too few
applications, not because the group is unremarkable: a group can clear the
minimum market-wide and fall below it for one lender. Read the two sides
separately; the prefixes exist so neither can be mistaken for the other.

### `lending_desert_score` — read the flag, not the score

- **`is_lending_desert` is a conjunction, and it is NOT a cut on
  `desert_score`:** `(app_percentile < DESERT_PERCENTILE_THRESHOLD) &
  (denial_rate > DESERT_DENIAL_RATE_FLOOR)`, i.e. `< 25` **and** `> 0.15`. Both
  must hold. A tract can carry a very high `desert_score` and still be `False`.
  **Sorting by `desert_score` and reading the top rows as "the deserts" is
  wrong.**
- **`desert_score` weights are a presentation choice for ranking** — `(100 -
  app_percentile) * 0.6 + denial_rate * 100 * 0.4`. Nothing was fitted; no
  threshold on `desert_score` means anything. Use it to sort, not to decide.
- **`DESERT_DENIAL_RATE_FLOOR` is unvalidated** — the package says so in its own
  docstring: not a CFPB threshold, unrelated to `schema.DISPARITY_THRESHOLDS`,
  nothing fitted to produce it.
- **`app_percentile` is a percentile within the frame you passed**, not a
  national one. The same tract scores differently depending on what else is in
  the frame — which is why the vintage guard matters here more than anywhere
  else.
- **Below `DESERT_TRACT_FLOOR` (5) tracts the flag is arithmetically
  unreachable**, and the call raises **`UnreachableFlagError`** rather than
  returning a fabricated `False` for every tract. Verified this session on a
  4-tract frame:

  ```
  lending_desert_score refused: 4 tract(s) in this frame, below the floor of 5.
    is_lending_desert requires app_percentile < 25, and rank(pct=True) over n rows has minimum 100/n = 25.0 for n=4. The flag is ARITHMETICALLY UNREACHABLE here, so every tract would be returned as is_lending_desert=False whatever the data says — a fabricated negative, not a finding that the tracts were examined and cleared.
    This is neither a small-N suppression rule nor a claim that 5 tracts is statistically adequate; it is only the point below which a positive is impossible. Use lending_by_tract() for the underlying counts. (methodology §M3.3a)
  ```

  It is neither a small-N suppression rule nor a claim of statistical adequacy.
  Report it as what it says it is.
- **No housing-unit figure is read anywhere.** There is no expected volume and no
  denominator; the score is not normalised for tract size. `tract_owner_occupied_units`
  and `tract_one_to_four_family_homes` arrive in the LAR and are never used. The
  claim that a tract is scored "relative to its expected volume based on housing
  units" was in 0.5.0's docstring, was **removed in 0.6.0 as unfounded**, and must
  not appear in any output. Never write it.

## Worked example — CRA-proxy distribution (executed, LIVE data)

`cra_proxy_distribution(df, *, by="borrower"|"tract"|"both", include_purchased=False,
year_column="activity_year")` — a pure descriptive transform on a frame from
`load_from_api`/`load_range`. No fetch, no network. (In 0.6.0 the three arguments
after `df` are **keyword-only** — the `*` in the signature is real; pass them by
name.)

**`include_purchased=True` now raises `EmptyUniverseError`** when the frame
contains no `action_taken == 6` rows — which is **always**, for any API-loaded
frame: `load_from_api` and `load_range` query the CFPB Data Browser with
`actions_taken=1,2,3,4,5` (`hmdaanalyzer.data.schema.API_ACTIONS_TAKEN`), so
action 6 is never fetched, and `load_sample` generates only actions 1, 3 and 4.
Through 0.5.0 the call returned a fully populated four-row table of zeros over a
zero denominator — a reader saw "this lender purchased no LMI loans"; the fact
was "purchased loans were never fetched." Verified this session on a live RI
pull:

```
EmptyUniverseError: cra_proxy_distribution was called with include_purchased=True, but this frame contains no action_taken == 6 (purchased loan) rows, so the purchased cut has a zero denominator and nothing to distribute.
  This is NOT evidence that no loans were purchased, and the four zeros it used to return said exactly that. The two facts have one representation, so the table is refused rather than returned.
  If the frame came from load_from_api() or load_range(), that is the certain cause and not a coincidence: the CFPB query requests actions_taken=1,2,3,4,5 (hmdaanalyzer.data.schema.API_ACTIONS_TAKEN), so action 6 is absent from every frame they produce. load_sample() generates only actions 1, 3 and 4.
  To analyse purchased loans, supply a frame that contains them — load_from_file() on a CSV exported with action 6 included. To analyse everything else, drop the flag: include_purchased=False is the default and is unaffected.
```

**Purchased-loan analysis therefore requires `load_from_file` with data obtained
another way** — a CSV exported with action 6 included. Never present a zero
purchased-loan distribution as evidence that no loans were purchased, and never
work around the refusal to produce one.

Print the caveat (`r.caveat` — the `STANDARD_CRA_PROXY_CAVEAT` constant plus the
standing no-comparator line) **beneath each table**, so no single extracted
table is ever caveat-free:

```python
import hmda_analyzer as h
df = h.load_from_api(year=2023, state="RI", limit=2000)   # live CFPB pull
r = h.cra_proxy_distribution(df, by="both")
for t in r.tables:
    print(f"--- dimension={t.dimension} universe={t.universe} year={t.year} ---")
    print(t.distribution.to_string(index=False))
    print("classified_denominator:", t.classified_denominator, "  excluded:", t.excluded)
    print(r.caveat)          # STANDARD_CRA_PROXY_CAVEAT + no-comparator line — under EVERY table
    print()
```

Actual output this session on 0.6.0, byte-identical to the 0.5.0 run (2,000 RI
LAR records → 976 originations). The caveat text under each table is copied
verbatim from `r.caveat`.

**This example's own pull is TRUNCATED** — `limit=2000` cut the 2023 RI file
short, so every row carries `limit_truncated=True` and the loader printed
`Loaded 2,000 LAR records — TRUNCATED at limit=2,000. These are the first 2,000
rows in server file order, not a sample`. The distribution below therefore
describes an arbitrary 2,000-row slice of Rhode Island, **not** Rhode Island. It
is shown that way deliberately, to model the disclosure: this is what quoting a
number off a truncated frame is supposed to look like. For a population figure,
raise `limit` until `limit_truncated` reads `False`.

```
--- dimension=borrower universe=originated year=None ---
category  count  cra_proxy_share
     Low     57         0.060897
Moderate    196         0.209402
  Middle    291         0.310897
   Upper    392         0.418803
classified_denominator: 936   excluded: {'na_income': 40}
CRA-proxy distribution estimate — NOT a CRA metric, rating, grade, or performance evaluation. Not assessment-area-bound: HMDA has no assessment-area concept, so this proxy spans all HMDA lending in the requested geography — a different population than any CRA exam evaluates. Mortgage-only: CRA lending tests also cover small-business, small-farm, and community-development lending, invisible to HMDA. Reporter population != CRA-covered institutions.
Distribution only; no comparator — not interpretable as CRA performance.

--- dimension=tract universe=originated year=None ---
category  count  cra_proxy_share
     Low     45         0.046680
Moderate    137         0.142116
  Middle    464         0.481328
   Upper    318         0.329876
classified_denominator: 964   excluded: {'unknown_tract': 12}
CRA-proxy distribution estimate — NOT a CRA metric, rating, grade, or performance evaluation. Not assessment-area-bound: HMDA has no assessment-area concept, so this proxy spans all HMDA lending in the requested geography — a different population than any CRA exam evaluates. Mortgage-only: CRA lending tests also cover small-business, small-farm, and community-development lending, invisible to HMDA. Reporter population != CRA-covered institutions.
Distribution only; no comparator — not interpretable as CRA performance.
```

## Rendering the CRA-proxy output — mandatory

1. **Attach `STANDARD_CRA_PROXY_CAVEAT` verbatim to every rendered table**, plus
   the **no-comparator line** — "*Distribution only; no comparator — not
   interpretable as CRA performance.*" — on every table. Both live in
   `r.caveat`; copy them, do not paraphrase.
2. Never present a CRA-proxy share as a CRA metric, rating, grade, or
   performance figure. The word "CRA" never appears in output without "proxy"
   adjacent.
3. **Reconcile the denominator every time.** Report the classified denominator
   and the excluded counts so totals reconcile:
   borrower `936 + 40 = 976`; tract `964 + 12 = 976`. If they don't reconcile,
   something is wrong — say so.
4. Warn against **differencing** the borrower-LMI% and tract-LMI% — they are
   computed on different populations.

### Exclusion-reason vocabulary (verified in source)

Every excluded row carries one of these reasons; surface them so the AI's
denominators reconcile the same way the package's do:

| reason | meaning |
|---|---|
| `na_income` | borrower `income` is NA/blank — excluded, never imputed |
| `missing_area_median` | `ffiec_msa_md_median_family_income` is 0/blank/NA — never divide |
| `out_of_range_income` | computed borrower MFI% out of accepted range |
| `unknown_tract` | tract income % is the Unknown sentinel (0/blank/NA) |
| `out_of_range_tract_pct` | tract income % negative, non-finite, or above ceiling |
| `unknown_year` | (multi-year) row has missing/NA `activity_year` |

A missing input is **excluded and surfaced**, never imputed into an income band
and never fabricated as a plausible default.

## Bundled methodology

**`get_methodology_path` now takes a filename** — `get_methodology_path(filename:
str = "cra_proxy_methodology.md") -> Path`. The old no-argument call still
returns the CRA-proxy doc, unchanged.

```python
h.get_methodology_path()                                   # cra_proxy_methodology.md   (22,313 bytes)
h.get_methodology_path("tract_vintage_methodology.md")     # tract_vintage_methodology.md (242,085 bytes)
```

Both verified present in the installed 0.6.0 wheel this session.

**`tract_vintage_methodology.md` is the authoritative source for everything in
the geography-vintage rule above** — every rejected alternative, the measurement
behind each decision, and the §M-numbered sections the refusal messages cite
(§M1.2, §M1.3, §M3.1, §M3.2, §M3.3a, §M5.2, §M6.5, and the numbered coverage
items). When a user pushes back on a refusal, or when any vintage wording is in
question, **read and quote that file** rather than reasoning from the summary
here. It travels with the installed wheel.

Likewise, `cra_proxy_methodology.md` remains authoritative for CRA-proxy caveat
wording, the firewall, and the proxy's limitations.

## Constants — read them from the package, never retype them

Every caveat, guardrail and threshold number in this skill is copied from a
constant in the installed wheel. When you quote one, **cite the path it is
defined at**, and prefer importing it over hardcoding the value.

**Top-level exports** (`import hmdaanalyzer as h`) — 33 names in `h.__all__` in
0.6.0, up from 25 in 0.5.0:

| Constant | Value (verified in the installed 0.6.0 wheel) |
|---|---|
| `h.TRACT_GEOID_BASIS_BY_YEAR` | `{2018: 2010, 2019: 2010, 2020: 2010, 2021: 2010, 2022: 2020, 2023: 2020}` — **2024 and 2025 deliberately absent** |
| `h.COUNTY_CODE_BASIS_BY_YEAR` | `{2018–2021: 2010, 2022: 2020, 2023: 2020, 2024: 2023}` |
| `h.MSA_CODE_BASIS_BY_YEAR` | `{2018–2021: 2010, 2022: 2020, 2023: 2020, 2024: 2023}` |
| `h.STANDARD_CRA_PROXY_CAVEAT` | the CRA-proxy caveat text — quote verbatim, never paraphrase |
| `h.basis_year(key, year)` | returns the basis year, or `None` meaning UNMAPPED — no cited basis, never an inference |

**Thresholds are NOT top-level exports** — they live in submodules. Cite the
module they are *defined* in, not one that happens to re-export them:

| Constant | Defined at | Value |
|---|---|---|
| `MIN_APPLICATIONS_FOR_RATE` | `hmdaanalyzer.data.schema` | `5` |
| `API_ACTIONS_TAKEN` | `hmdaanalyzer.data.schema` | `(1, 2, 3, 4, 5)` |
| `TRUNCATED_COLUMN` | `hmdaanalyzer.data.schema` | `'limit_truncated'` |
| `DESERT_PERCENTILE_THRESHOLD` | `hmdaanalyzer.geography_vintage` | `25` |
| `DESERT_DENIAL_RATE_FLOOR` | `hmdaanalyzer.geography_vintage` | `0.15` — **unvalidated** |
| `DESERT_TRACT_FLOOR` | `hmdaanalyzer.geography_vintage` | `5` — **derived** at import from `DESERT_PERCENTILE_THRESHOLD`, not written down |

`hmdaanalyzer.analysis.disparity` and `hmdaanalyzer.analysis.geographic` import
these and `hmdaanalyzer.data.loader` imports the loader pair, so
`analysis.disparity.MIN_APPLICATIONS_FOR_RATE`, `analysis.geographic.DESERT_*` and
`data.loader.API_ACTIONS_TAKEN` all resolve to the same objects. **Do not cite
those paths.** They are re-exports; the package's own error messages cite
`hmdaanalyzer.data.schema.API_ACTIONS_TAKEN`, and `UnreachableFlagError`'s
docstring says "Both constants live in `hmdaanalyzer.geography_vintage`." Citing
a re-export sends a reader to a file where the constant cannot be changed.

`DESERT_TRACT_FLOOR` is derived, not chosen — `_derive_desert_floor(25) == 5`. Do
not describe `5` as a configured floor, and do not restate it independently of
the percentile threshold; move one and the other moves with it.

## Data source & typed errors

- Source: the **CFPB HMDA API** (`ffiec.cfpb.gov` / CFPB HMDA endpoints) — no
  cloud WAF; verified reachable this session (200 records, 101 columns, both
  FFIEC income fields present).

### Typed errors — all eight exported by 0.6.0

Report these; do not smooth them over, and do not catch them to proceed. Every
one subclasses `ValueError`, so a bare `except ValueError` swallows all of them —
which is why you must not write one around any call in this skill.

| Error | Raised when |
|---|---|
| `CFPBAPIError` | CFPB API failure |
| `SchemaValidationError` | a fetched year fails the canonical 2018+ column check (names the year) |
| `ActivityYearMismatchError` | the API returned a different year than requested |
| `MissingColumnError` | a required column for the requested cut is absent, or is present with a non-numeric dtype — verified: `cra_proxy_distribution` on the FFIEC-less sample raises it |
| `GeographyVintageError` | **new in 0.6.0** — a geography-keyed aggregation was given a frame spanning two bases, or pooling an unmapped year; also when `vintage=` selects no rows |
| `UnreachableFlagError` | **new in 0.6.0** — `lending_desert_score` on fewer than `DESERT_TRACT_FLOOR` (5) tracts, where `is_lending_desert` is arithmetically unreachable |
| `ReferenceGroupError` | **new in 0.6.0** — `disparity_ratio`'s reference group is absent (firewalled function; you should not be calling it) |
| `EmptyUniverseError` | **new in 0.6.0** — `cra_proxy_distribution(include_purchased=True)` on a frame with no action-6 rows |

## Failure modes

- **`load_range` partial failure** → the whole call raises with the failing year
  named; report the error, never the surviving years.
- **`cra_proxy_distribution` on a frame missing FFIEC columns** →
  `MissingColumnError`. Use a real `load_from_api`/`load_range` frame, not
  `load_sample`.
- **Guarded aggregation on a vintage-spanning frame** → `GeographyVintageError`.
  Report the refusal, name which of the two shapes fired, and offer the two paths
  (split at the boundary, or `vintage=`). **Never** catch it and proceed, and
  never hand-roll the `groupby` it declined.
- **`lending_desert_score` on fewer than 5 tracts** → `UnreachableFlagError`.
  Report it; do not substitute `is_lending_desert=False`.
- **`cra_proxy_distribution(include_purchased=True)`** → `EmptyUniverseError` on
  any API-loaded frame. Purchased loans are never fetched; use `load_from_file`
  with data obtained another way, or drop the flag.
- **Truncated pull** → not an error at all, and that is the hazard.
  `limit_truncated=True` rides on every row; check it (per year under
  `load_range`) and disclose it beside any number you quote.
- **A pre-0.6.0 install** — an old pin, a stale environment, a vendored wheel →
  no geography-vintage refusal at all. Check `h.__version__` before quoting
  anything.
- **User asks for disparity / fair lending / CRA performance** → decline per the
  FIREWALL.
- **CFPB API down** → `CFPBAPIError`; report it.

## Caveats

- HMDA is **2018+** schema here; earlier data is out of scope.
- The CRA-proxy is a **proxy**, not a CRA metric: not assessment-area-bound,
  mortgage-only, reporter-population ≠ CRA-covered institutions, no comparator.
  See the verbatim `STANDARD_CRA_PROXY_CAVEAT` above.
- HMDA `income` is lender-relied-upon (often combined co-applicant) income — an
  imperfect, likely upward-biased proxy for borrower income (tends to understate
  LMI borrower share).
- **HMDA geography identifiers are not comparable across two data-year
  boundaries** — 2021→2022 (2010 vs 2020 census tracts, plus Alaska's `02261`
  county split) and 2023→2024 (Connecticut's counties → planning regions). Any
  tract- or county-keyed aggregation must stay within one basis. **0.6.0 enforces
  this**: the guarded functions raise `GeographyVintageError` rather than
  returning a pooled number. See the geography-vintage rule above.
- **2024 and 2025 have no cited tract basis.** Single-year 2024 or 2025 tract
  analysis works; pooling either with any other year refuses. That is an
  assertion of ignorance, not a claim that the basis changed.
- **`limit=` truncates, it does not sample.** A truncated pull is the first *N*
  rows in server file order — never call it a sample, and disclose
  `limit_truncated` beside any number from such a frame.
- **`lending_desert_score` reads no housing-unit figure.** There is no expected
  volume and no denominator; the score is not normalised for tract size, and
  `is_lending_desert` is a conjunction rather than a cut on `desert_score`.
- **`lender_vs_market` suppresses race groups below 5 applications on each side
  independently.** The six `suppressed_*` columns must be surfaced with the
  table; an unnamed absent group reads as a group with no lending.
