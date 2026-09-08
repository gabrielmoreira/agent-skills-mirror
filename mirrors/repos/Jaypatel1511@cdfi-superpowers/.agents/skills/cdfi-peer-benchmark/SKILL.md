---
name: cdfi-peer-benchmark
description: >-
  Benchmark a bank CDFI against a peer group on FDIC call-report metrics (NIM,
  ROAA, ROAE, efficiency ratio, Tier 1 capital, loans-to-deposits, NPL ratio,
  loan-loss coverage). Use when the user says "benchmark this CDFI", wants a
  "peer comparison", or asks "how does this bank CDFI compare". Bank CDFIs only
  (FDIC-insured) — no credit unions, no unregulated loan funds. Backed by the
  audited PyPI package cdfi-benchmark; import name is `cdfibenchmark`.
compatibility: >-
  Requires Python >=3.9, pip, and network access to pypi.org plus
  api.fdic.gov/banks (FDIC BankFind — institutions and call reports; the former
  banks.data.fdic.gov host now 301-redirects there). That source covers
  FDIC-insured institutions only, which is why the skill benchmarks bank CDFIs
  and refuses credit unions and unregulated loan funds.
---

# CDFI Peer Benchmark

Benchmarks a **bank CDFI** against peers using FDIC BankFind call-report data,
via the published, audited **cdfi-benchmark** package. Renders results
faithfully, in both directions: where the package returns NaN/None it reports
N/A and **never fills a number**, and where the package returns a measured value
it declined to *grade* it reports that value with the package's own reason and
**never suppresses it**. Both halves are load-bearing — see the N/A contract
below.

## When to use

- "Benchmark First Community Bank against its peers."
- "How does this bank CDFI's NIM / ROAA / efficiency ratio compare?"
- "Build a peer group for cert 23623 and show the summary table."

## When NOT to use

- **Credit unions / CDCUs** — not in FDIC BankFind (they are NCUA-regulated).
  This package covers FDIC-insured depositories only. Decline and say so.
- **Unregulated CDFI loan funds** — no call-report data exists; out of scope.
- **CDFI Fund program data** (awards, certification) — that is `cdfi-fund-tracker`
  / `cdfi-data`, not this.
- Portfolio stress testing (`cdfi-stress-tester`) or valuation (`cdfi-val`).

### Which `cdfibenchmark` functions this skill uses, by name

The refusals above are about *packages*. This section is about *functions*, so a
request maps to a call rather than to a guess. `cdfibenchmark.__all__` has **19**
names in 0.3.1 (counted this session); the ones that decide what a user is shown
are named here. This is not a design pass over all 19 — a name absent below is
unruled, not endorsed.

**Endorsed — reach for these:**

| function | reach for it when |
|---|---|
| `generate_report` | **"give me the benchmark report."** The full Markdown report, and the only surface that renders the caveats, bases, threshold provenance and peer-group disclosures. Default to this. |
| `summary_table` | a DataFrame is genuinely wanted. Carries `basis` and `threshold_source` but **none** of the report's caveats — you then owe the user those yourself. |
| `get_financials` | pull one institution's call-report profile by CERT. |
| `search_institutions` | find a CERT by name/state/asset size. |
| `build_peer_group` | the real peer group, live from FDIC. |
| `build_sample_peer_group` | a deterministic **synthetic** demo group. Label any output built on it as illustrative. |
| `benchmark_institution` | the per-metric `BenchmarkResult` objects behind the table. |
| `rank_institution` | a percentile on one metric — and read its `reason` when `rank` is `None`. |

**Refused — do not reach for these to answer a benchmarking question:**

| function / attribute | why not |
|---|---|
| `compute_peer_metrics` | returns raw per-peer metrics with **no basis awareness**. Taking a median or a percentile off it yourself reproduces the mixed-basis defect the package records as unfixed, without the caveat the report carries. Use `benchmark_institution` / `generate_report`. |
| `get_peer_financials` | the raw peer fetch. It applies **no** dedupe, no period pinning and no nearest-by-assets selection — `build_peer_group` is what turns it into a peer group. Calling it directly rebuilds the 0.2.x defect by hand. |
| `get_institution` | returns a **raw FDIC dict**, not an `InstitutionProfile`, and carries none of the parse-layer discipline (no NaN-vs-zero rule, no plausibility bound, no `implausible_fields`). Fine for identity lookup; never a source of metrics. |
| `BENCHMARKS`, `ASSET_BUCKETS` / `HOUSE_ASSET_BUCKETS` | read them to **quote** a threshold or a band boundary with its `source`. Never restate a number from them without its HOUSE attribution, and never mutate them. |
| `InstitutionProfile(...)` built by hand | legitimate for a demo, but a hand-built profile has no `reported_*` values, so every earnings metric falls to the computed proxy — see the basis rule. Do not present one as a real institution. |

**Never fabricate the inputs.** If FDIC is unreachable or a CERT does not resolve,
report that. Do not hand-build an `InstitutionProfile` from remembered or
estimated financials and present the resulting grades as a benchmark.

## Install

```
pip install "cdfi-benchmark>=0.3.0"
```

**The floor is `>=0.3.0`, and it is load-bearing.** Below it the package grades
`loans_to_deposits` **backwards**. Executed against 0.2.1 installed from PyPI,
python3.10, this session:

```
  L/D   20%  status=WEAK
  L/D   55%  status=WEAK        <- a bank lending 55% of its deposits
  L/D   80%  status=STRONG
  L/D  200%  status=STRONG      <- a bank lending 200% of its deposits
```

`rank_institution` reads the same absent direction flag, so the percentile
inverted with the grade. Against a fixed 20-peer group spanning 50%-126%:

```
  0.2.1   L/D   55%  status=WEAK      rank=19  percentile=9.5
  0.2.1   L/D  200%  status=STRONG    rank=1   percentile=95.2
```

0.3.0 grades the metric as a **band** (`floor` 50 / `good` 80 / `warning` 95, all
HOUSE) and refuses to rank it at all. The same run at 0.3.1: 55% -> `STRONG`,
200% -> `WEAK`, `rank=None, percentile=None` with a `reason`. 0.3.0 is also where
every other surface this skill now relies on lands — `BenchmarkResult.basis` and
`GRADEABLE_BASES`, threshold provenance, `PeerGroup` and its `caveats`, and the
report disclosures.

**Deliberately not `>=0.3.1`.** 0.3.1 changed no library code, so a `>=0.3.1`
floor would refuse an install that behaves identically — a floor with no runtime
justification. Verified two ways this session: `git diff v0.3.0 v0.3.1 --
cdfibenchmark/` is empty, and the package tree at `v0.3.1` is byte-identical to
the package inside the published 0.3.0 wheel downloaded from PyPI — 11 `.py`
files on each side, recomputed here by the method the package's own CHANGELOG
publishes:

```
sha256 3f90077f200206a1d09929b868df2af43a6da325eb3e695da35f6f4ebbde9083
```

Latest on PyPI **2026-09-07: cdfi-benchmark 0.3.1** (`pip index versions
cdfi-benchmark` -> `LATEST: 0.3.1`). The `>=0.3.0` floor resolves to it.

**Import name is `cdfibenchmark`** (no underscore, no hyphen). There is no
`cdfi_benchmark` alias — `import cdfi_benchmark` will fail.

```python
import cdfibenchmark as c
```

## The scope guardrail (state it up front)

**Bank CDFIs only.** Peers are drawn from FDIC BankFind. If the user names a
credit union or a loan fund, do not force it through — explain that this tool
covers FDIC-insured bank CDFIs and MDIs only, and that credit-union benchmarking
is deliberately out of scope for this portfolio.

## The N/A contract — TWO meanings, opposite remedies (non-negotiable)

`status == "N/A"` means one of two different things in 0.3.0, and the correct
behaviour is **opposite** in each. Read `basis` before rendering any N/A.

**(1) The value is ABSENT.** `institution_value` is `NaN` or `None` — the package
could not compute the metric (a missing call-report field). **Render "N/A" and
never fill it.** Never substitute a peer median, a zero, or a plausible-looking
number. A fabricated capital ratio in a benchmark is exactly the failure this
contract exists to prevent. **This half is unchanged and nothing below weakens
it.**

**(2) The value is PRESENT but was NOT GRADED.** New in 0.3.0. The number was
measured and is returned in full; the package declined to *grade* it because its
`basis` is outside `GRADEABLE_BASES` — the threshold is calibrated to a different
measurement. **Report the value and quote the basis.** Saying "not available"
here suppresses a real measurement the package deliberately kept.

Executed this session (0.3.1, python3.10) — both meanings in one table:

```
                                     metric  institution   status                                                           basis
Net Interest Margin over total assets (NIM)     3.080000      N/A computed over TOTAL assets — not FDIC NIMY (avg earning assets)
        Return on Equity, period-end (ROAE)          NaN      N/A      computed from full-year YTD flows over period-end balances
                      Tier 1 Leverage Ratio          NaN      N/A                            no value was reported for this field
```

Row 1 is meaning (2): NIM **is 3.08%** and must be reported. Rows 2 and 3 are
meaning (1): nothing to report, and nothing to fill.

Telling them apart:

```python
import pandas as pd
from cdfibenchmark.data.schema import GRADEABLE_BASES

present_but_ungraded = (not pd.isna(r.institution_value)
                        and r.basis not in GRADEABLE_BASES)
```

There is a **third** state, which is neither: `basis` ==
`"FDIC published a value outside the plausibility bound for a percentage —
rejected as a wrong-field-class signal, not reported"`. FDIC published a value
and **this tool refused it**. The package made that a distinct basis precisely so
it could not be conflated with absent. Say that the tool refused a real filing;
do not say FDIC published nothing.

`generate_report` distinguishes all three on its face with lines this skill's
`summary_table` examples do not carry — **`Not graded:`** and **`Not shown:`**.
Quote those lines verbatim rather than composing your own (see *Rendering*
below).

## The basis rule (non-negotiable) — condition on `basis`, never on `report_date`

**This rule replaces a `report_date` rule that made the AI discredit a correct
number.** 0.3.0 PREFERS FDIC's own published series — `NIMY`, `ROA`, `ROE`,
`EEFFR` — which arrive **already annualized and over average balances**.
`get_financials` and `get_peer_financials` request those four fields at every
report date (`cdfibenchmark/data/fdic.py:156` and `:238`). On that path a 3/31
NIM of 3.08% is a correct annualized figure; calling it "roughly 4x low" would
push the user toward **12.3%**, a number no source produced.

**The judgment is the package's, not yours.** `InstitutionProfile.metric_basis()`
rules how each metric was obtained (`cdfibenchmark/data/schema.py:475`) and
`GRADEABLE_BASES` (`schema.py:233`) rules whether that basis may be graded at
all. Report that ruling. Do not form your own from the report date.

**Read `BenchmarkResult.basis` — or the `basis` column of `summary_table` — and
follow the branch it names.**

**Scope of the two branches below.** They cover the four metrics whose basis
varies with the filing — `nim`, `roaa`, `roae`, `efficiency_ratio` — which is
where reading the basis changes what you do. Derived this session: the package
defines **11** `BASIS_*` constants, **5** of them in `GRADEABLE_BASES`, over
**8** shipped metrics. The other bases are fixed per metric rather than decided
per filing: `loans_to_deposits`, `npl_ratio` and `reserve_coverage` are always
`computed from period-end balances (period-neutral)` and always gradeable, and
`tier1_ratio` has its own three states in its own section below. `BASIS_UNRULED`
is unreachable for all eight shipped metrics — every one is claimed by a branch
of `metric_basis()`. **So: two branches, not an exhaustive taxonomy of the
eleven.** If you meet a basis string that is not below, quote it and say the
skill does not rule on it rather than assuming which branch it belongs to.

### If `basis` is `FDIC published — annualized, average balances`

The value **is annualized**, at 3/31 exactly as at 12/31. Present it as it
stands. Do **not** discount it, do **not** call it un-annualized, and do **not**
multiply it by anything. It is gradeable and the package grades it.

**But this branch rules on PROVENANCE, not on plausibility — and the STRONG it
can earn is a threshold comparison, nothing more.** `reported_is_trustworthy`
decides only whether FDIC's published ratio is a *measurement* rather than a
fill. It does not ask whether the measurement is meaningful, and the package
says so on its face. Executed this session (0.3.1, python3.10), on a **hand-built**
profile whose `reported_*` fields carry the values FDIC's published series would
occupy — the same stand-in this skill uses above, since FDIC was not reachable
here. The `-700` is not invented for the demo: it is a value the package records
as really present in the population, cited below.

```
efficiency_ratio  -700.0   basis FDIC published — annualized, average balances   gradeable=True   status=STRONG
roae               999.0   basis FDIC published — annualized, average balances   gradeable=True   status=STRONG
```

The package states this hole itself rather than leaving it to be discovered.
Quote its words — `cdfibenchmark/data/schema.py:427`, `reported_is_trustworthy`,
under the heading **"WHAT THIS RULE GETS WRONG, stated rather than discovered
later"**:

> **A non-zero sentinel passes.** Only an exact 0 is tested for contradiction.
> If FDIC ever fills with -1 or 999 this trusts it.

> But -700 does grade STRONG, and this rule does not stop it; that is recorded
> as a known limitation, not fixed here.

> **It says nothing about the DENOMINATOR.** A bank with negative equity
> (CERT 12013, EQ -$23,485k) has a mathematically defined but meaningless ROE,
> and this rule trusts it.

**The remedy is NOT to doubt the number.** The same docstring records that the
only negative efficiency ratios in the population (`-700`, `-5.615`, `-1.103`)
are *"FDIC's OWN correct arithmetic over a negative noninterest expense —
reproducible from the filed financials to 0.01"*, and *"so they are not
sentinels today"*. The value is right; the **grade** is the artefact. Reinstating
doubt about FDIC-published values is the defect this rule replaced. So:

- **Report the value and the basis as they stand.** Do not discount them,
  suppress them, restate them, or substitute a corrected figure — there is no
  corrected figure to substitute.
- **Do not let `STRONG` stand by itself** when the value is one no reader would
  call strong: a negative efficiency ratio, a three-digit ROAE, any earnings
  ratio on negative equity. Report the grade, then say Status is a threshold
  comparison the package records it does **not** stop here, and quote the line
  above.
- **Say whose judgment each part is.** The value is FDIC's, the grade is the
  package's threshold comparison, and the observation that a STRONG on a
  negative efficiency ratio is not a statement about performance is **yours** —
  attribute it to yourself, not to FDIC and not to the package's grade.

### If `basis` is outside `GRADEABLE_BASES`

The package fell back to a computed proxy and **has already refused to grade
it** — `status` is `N/A` with the value fully present. Report the value, quote
the basis string, and do **not** annualize it yourself. The correct fix is a
different measurement (FDIC's published series), not a scalar.

| basis string | what it means |
|---|---|
| `computed from YTD flows through Q{q} — NOT annualized` | the `roaa`/`roae` fallback at an interim date. Understated for the period. |
| `computed from YTD flows, period unknown — NOT annualized` | same, and `report_date` was not in FDIC's 8-digit form, so the period could not be read at all. |
| `computed over TOTAL assets — not FDIC NIMY (avg earning assets)` | the `nim` fallback. **Ungradeable at EVERY period, including 12/31** — the defect here is the denominator, not the period. |

`efficiency_ratio` is the exception in the other direction: its computed fallback
carries `computed from same-period YTD flows (period-neutral)`, **is** gradeable,
and must **not** be annualized. Numerator and denominator are YTD flows over the
same period, so the period cancels exactly; annualizing it would introduce an
error where there is none.

Executed this session (0.3.1, python3.10) — one profile at `report_date =
"20260331"` (Q1), with and without FDIC's published ratios:

```
report_date: 20260331  fiscal_quarter: 1
nim                   3.08  gradeable=True  basis=FDIC published — annualized, average balances
roaa                  1.24  gradeable=True  basis=FDIC published — annualized, average balances
roae                  10.6  gradeable=True  basis=FDIC published — annualized, average balances
efficiency_ratio      61.2  gradeable=True  basis=FDIC published — annualized, average balances

nim    value=3.08   status=ADEQUATE
roaa   value=1.24   status=STRONG
roae   value=10.6   status=STRONG

=== SAME PROFILE, reported_* absent (computed fallback) ===
nim                    2.3047  gradeable=False  basis=computed over TOTAL assets — not FDIC NIMY (avg earning assets)
roaa                   0.3073  gradeable=False  basis=computed from YTD flows through Q1 — NOT annualized
roae                   2.6667  gradeable=False  basis=computed from YTD flows through Q1 — NOT annualized
efficiency_ratio      64.1026  gradeable=True   basis=computed from same-period YTD flows (period-neutral)
nim    status=N/A
roaa   status=N/A
roae   status=N/A
```

**What was and was not established here.** The profile above is **hand-built** to
stand in for what `get_financials` returns on the live path. FDIC's endpoints
were **not reachable from the session that wrote this section**, so the claim
that the live path serves `NIMY`/`ROA`/`ROE`/`EEFFR` at interim dates rests on
the package's source (`data/fdic.py:156`, which requests them unconditionally at
any `report_date`) and on the package's own recorded measurements
(`data/schema.py:191-193`: computing those three from YTD flows read
**4.30x / 4.12x / 4.01x low at a Q1 REPDTE** against FDIC's published series) —
**not on a live probe made here.** The branch behaviour above WAS executed.

### Peers at one `report_date` do NOT share one basis

Do not infer a shared basis from a shared date. Each peer's basis is decided per
institution by `reported_is_trustworthy`, so two banks at the same REPDTE can sit
on different bases. Executed this session:

```
  both peers report_date = 20260331 == 20260331
  peer 1 nim basis: FDIC published — annualized, average balances
  peer 2 nim basis: computed over TOTAL assets — not FDIC NIMY (avg earning assets)
  peer 1 nim value: 3.5  peer 2 nim value: 2.3047
  median of the two: 2.9023687580025608 <- a median across TWO BASES
```

The package records this as a known limitation of 0.3.0 that it did **not** fix.
Quote it rather than softening it — `CHANGELOG.md`, "Known limitations":

> The peer median is computed across a MIXED basis: peers whose published ratios
> are trusted contribute FDIC's measurement while peers falling back to the
> computed proxy contribute a differently-measured number, and the median does
> not say which.

> A median across two bases is a fabricated statistic even when every input is
> correct.

`compute_peer_metrics` has no basis awareness, and `BenchmarkResult.basis`
carries the **institution's** basis only — so a peer column can be labelled with
a basis that is not the peers'. State this when you present a peer median.

## Worked example — full benchmark flow (executed)

The pipeline is: `get_financials(cert)` -> build a peer group ->
`generate_report(...)` for the full disclosed report, or `summary_table(...)` for
a DataFrame. **`generate_report` is the surface that renders the caveats** — see
*Rendering* below before choosing `summary_table` alone.

`build_sample_peer_group(institution)` generates a deterministic **synthetic**
peer set — good for a reproducible demo without a live FDIC round-trip. For a
real analysis use `build_peer_group(institution, ...)` (live FDIC peers).

**UNITS: every dollar field on `InstitutionProfile` is in THOUSANDS**, because
FDIC's `ASSET`, `DEP`, `LNLSNET`, `NETINC` and the rest are reported in thousands
and `get_financials` carries them through unchanged
(`cdfibenchmark/data/fdic.py:442-450`). `total_assets=250_000` is **$250MM**, not
$250 billion. `total_assets_mm` divides by 1,000 and `asset_bucket` and the
report face both read the raw field, so a profile hand-built in dollars renders
a bank a thousand times its real size.

**`report_date` must be FDIC's 8-digit form, `"YYYYMMDD"`.** `fiscal_quarter`
parses exactly that (`schema.py:399-402`) and the live path always produces it. A
hyphenated `"2024-12-31"` yields `fiscal_quarter is None`, which sends `roaa` and
`roae` to `computed from YTD flows, period unknown — NOT annualized` and grades
them **N/A even at a Q4 date**.

```python
import pandas as pd
import cdfibenchmark as c
from cdfibenchmark import InstitutionProfile

# All dollar fields in THOUSANDS: 250_000 == $250MM.
inst = InstitutionProfile(
    cert=99999, name="Example Community Bank (SYNTHETIC)", city="Anytown", state="RI",
    report_date="20241231",
    total_assets=250_000, total_deposits=210_000,
    net_loans=170_000, net_income=2_500, interest_income=9_800,
    interest_expense=2_100, non_interest_income=1_200,
    non_interest_expense=6_400, total_equity=28_000, tier1_ratio=11.5,
    gross_loans=172_000, non_current_loans=1_500, loan_loss_allowance=2_000,
)
peers = c.build_sample_peer_group(inst)          # 20 synthetic peers, deterministic
st = c.summary_table(inst, peers)
print(inst.total_assets_mm, inst.asset_bucket, inst.fiscal_quarter)
print(st[["metric","institution","peer_median","vs_median","status","peer_count"]].to_string(index=False))
print(st[["metric","basis","threshold_source"]].to_string(index=False))
```

Actual output this session (cdfi-benchmark 0.3.1, python3.10):

```
250.0 medium 4

                                     metric  institution  peer_median  vs_median   status  peer_count
Net Interest Margin over total assets (NIM)     3.080000     3.010296   0.069704      N/A          20
                           Efficiency Ratio    71.910112    70.624617   1.285495 ADEQUATE          20
        Return on Assets, period-end (ROAA)     1.000000     0.940811   0.059189   STRONG          20
        Return on Equity, period-end (ROAE)     8.928571     8.030005   0.898566 ADEQUATE          20
                      Tier 1 Leverage Ratio    11.500000    12.830947  -1.330947   STRONG          20
                          Loans-to-Deposits    80.952381    82.661433  -1.709052 ADEQUATE          20
                  Non-Performing Loan Ratio     0.872093     1.555798  -0.683705   STRONG          20
                 Loan Loss Reserve Coverage   133.333333    80.408055  52.925278   STRONG          20
```

`summary_table` carries two further columns, `basis` and `threshold_source`, which
are how a row's grade and its warrant are read. Same run:

```
                                     metric                                                                                                   basis                                                                                                              threshold_source
Net Interest Margin over total assets (NIM)                                         computed over TOTAL assets — not FDIC NIMY (avg earning assets)                                                                                                                         HOUSE
                           Efficiency Ratio                                                    computed from same-period YTD flows (period-neutral)                                                                                                                         HOUSE
        Return on Assets, period-end (ROAA)                                              computed from full-year YTD flows over period-end balances                                                                                                                         HOUSE
        Return on Equity, period-end (ROAE)                                              computed from full-year YTD flows over period-end balances                                                                                                                         HOUSE
                      Tier 1 Leverage Ratio FDIC published (RBC1AAJ) — Tier 1 capital over adjusted average assets; a capital ratio, not annualized 12 CFR 324.12 (CBLR qualifying, lowered 9%->8% eff. 2026-07-01); 12 CFR 324.403(b)(1) (PCA well-capitalized leverage minimum)
                          Loans-to-Deposits                                                      computed from period-end balances (period-neutral)                                                                                                                         HOUSE
                  Non-Performing Loan Ratio                                                      computed from period-end balances (period-neutral)                                                                                                                         HOUSE
                 Loan Loss Reserve Coverage                                                      computed from period-end balances (period-neutral)                                                                                                                         HOUSE
```

**Three things to read off this example, none of them obvious:**

1. **NIM is `N/A` at a 12/31 date.** This profile is hand-built, so FDIC's `NIMY`
   is absent and the computed proxy is used — and the computed NIM proxy is
   **never** gradeable at any period, because its denominator is total assets
   rather than average earning assets. A 12/31 date does not rescue it. The value
   3.08% is real and must still be reported: this is meaning (2) of the N/A
   contract.
2. **ROAA and ROAE ARE graded here**, because at a Q4 date their basis is
   `computed from full-year YTD flows over period-end balances`, which is
   gradeable. At any interim date on this same hand-built path they would be
   `N/A`.
3. **Seven of the eight `threshold_source` values are `HOUSE`.** Only
   `tier1_ratio` is cited. Never present a HOUSE threshold as a regulatory one.

This example is built on **synthetic** peers. Label any output derived from
`build_sample_peer_group` as illustrative, never as a real peer comparison.

## Worked example — the N/A contract in action (executed)

Same peer group, but the institution is missing `total_equity` and `tier1_ratio`,
so ROAE and the Tier 1 ratio cannot be computed:

```python
inst2 = InstitutionProfile(
    cert=99998, name="Missing-Data Bank (SYNTHETIC)", city="X", state="RI",
    report_date="20241231",
    total_assets=250_000, total_deposits=210_000,
    net_loans=170_000, net_income=2_500, interest_income=9_800,
    interest_expense=2_100, non_interest_income=1_200,
    non_interest_expense=6_400, total_equity=None, tier1_ratio=None,
    gross_loans=172_000, non_current_loans=1_500, loan_loss_allowance=2_000,
)
st2 = c.summary_table(inst2, peers)
print(st2[["metric", "institution", "status", "basis"]].to_string(index=False))
```

Actual output this session (cdfi-benchmark 0.3.1, python3.10):

```
                                     metric  institution   status                                                           basis
Net Interest Margin over total assets (NIM)     3.080000      N/A computed over TOTAL assets — not FDIC NIMY (avg earning assets)
                           Efficiency Ratio    71.910112 ADEQUATE            computed from same-period YTD flows (period-neutral)
        Return on Assets, period-end (ROAA)     1.000000   STRONG      computed from full-year YTD flows over period-end balances
        Return on Equity, period-end (ROAE)          NaN      N/A      computed from full-year YTD flows over period-end balances
                      Tier 1 Leverage Ratio          NaN      N/A                            no value was reported for this field
                          Loans-to-Deposits    80.952381 ADEQUATE              computed from period-end balances (period-neutral)
                  Non-Performing Loan Ratio     0.872093   STRONG              computed from period-end balances (period-neutral)
                 Loan Loss Reserve Coverage   133.333333   STRONG              computed from period-end balances (period-neutral)
```

**Three N/A rows, two different meanings.** ROAE and Tier 1 are meaning (1) —
absent, `NaN`, present them as N/A and do **not** back-fill them from the peer
median. NIM is meaning (2) — the value **is 3.08%** and must be reported with its
basis. Rendering all three as "not available" would suppress a real measurement;
filling any of the three would fabricate one.

## Live FDIC path

Signatures below were read from the installed 0.3.1 wheel with
`inspect.signature` this session.

- `c.search_institutions(name=None, state=None, min_assets=None, max_assets=None,
  limit=20)` → DataFrame of FDIC banks.
- `c.get_financials(cert, report_date=None, limit=4)` → an `InstitutionProfile`
  populated from FDIC call reports, including FDIC's published `NIMY` / `ROA` /
  `ROE` / `EEFFR`.
- `c.build_peer_group(institution, same_state=False, asset_tolerance=0.5,
  min_peers=10, max_peers=50, report_date=None)` → a `PeerGroup`.
  **`report_date` is new in 0.3.0** and defaults to the institution's own — never
  left unset, because an unpinned peer query returned one row per
  institution-quarter across the whole history. The three numeric defaults come
  from `HOUSE_ASSET_TOLERANCE` / `HOUSE_MIN_PEERS` / `HOUSE_MAX_PEERS` in
  `cdfibenchmark.peers.selector` — house constants, not a supervisory
  definition.
- `c.generate_report(institution, peers, title=None)` → the full Markdown report.
- `c.rank_institution(institution, peers, metric)` → dict.
- `c.get_institution(cert)` returns a **raw FDIC dict** (not an
  `InstitutionProfile`); a nonexistent cert returns **`None`**, not an error.

**`PeerGroup` is not exported.** `from cdfibenchmark import PeerGroup` raises
`ImportError` (verified this session; `__all__` has 19 names and `PeerGroup` is
not among them). It is reachable only as
`cdfibenchmark.peers.selector.PeerGroup`. You rarely need the class — the
instance returned by `build_peer_group` carries `.caveats`, `.selection_basis`,
`.report_dates`, `.is_single_period`, `.below_min_peers` and `.asset_percentile`
directly, and it subclasses `list`, so `len()` and iteration work unchanged.

**That subclassing cuts both ways: keep the object, not a copy of its rows.**
Every attribute above lives on the `PeerGroup`, not on the peers, so `list(pg)`,
`pg[:20]`, a comprehension or a `sorted()` yields a plain `list` that has none of
them — and `generate_report` reads three of its disclosures off those attributes
with `getattr` and silently omits them. See *When the caveats silently vanish*
under the caveats section.

Data source: **`https://api.fdic.gov/banks`** (FDIC BankFind API). The historical
host `banks.data.fdic.gov/api` now answers HTTP 301 to it; 0.3.0 moved to the
canonical host and keeps the old one only as `FDIC_API_BASE_LEGACY` so a gate can
assert it is not used again. Both constants read from the installed wheel this
session.

> **Not verified here.** FDIC's endpoints were **blocked by the egress allowlist
> of the session that last updated this skill**, so no live call was made. The
> hosts, fields and signatures above are read from package source and from the
> installed wheel. Reachability from your own environment is yours to check.

## Typed errors — report, don't smooth over

The package raises **typed** exceptions; surface them, don't swallow them:

| exception | subclass of | fires on |
|---|---|---|
| `FDICAPIError` | `CDFIBenchmarkError` | FDIC API transport/HTTP failure |
| `FDICResponseError` | `CDFIBenchmarkError` | a malformed or wrong-shape FDIC response — **and one non-API case, below** |
| `CDFIBenchmarkError` | `Exception` | package base error |

Hierarchy verified this session against the installed 0.3.1 wheel:
`FDICAPIError.__mro__` and `FDICResponseError.__mro__` are both five elements,
`(<self>, CDFIBenchmarkError, Exception, BaseException, object)`. Catching
`CDFIBenchmarkError` catches both. When one is raised, report the error type and
message; do not fall back to fabricated numbers or a cached guess.

**`FDICResponseError` does not always mean FDIC misbehaved.**
`build_peer_group` raises it when the *institution's* `total_assets` is unknown,
because the asset window is then undefined. The FDIC response can be perfectly
well-formed. Reproduced this session:

```
FDICResponseError: cannot select peers for an institution with unknown assets: CERT 34352
```

Read the message before diagnosing. Reporting that as "FDIC returned a malformed
response" sends the user to look at the wrong thing.

```python
from cdfibenchmark import FDICAPIError, FDICResponseError
try:
    inst = c.get_financials(cert)
except (FDICAPIError, FDICResponseError) as e:
    # report: type(e).__name__ and str(e). Do NOT fabricate metrics.
    ...
```

## What 0.3.0 discloses that you must carry

0.3.0 spent a release making the report state its own warrant. Each item below
renders on `generate_report`'s face. **Do not paraphrase these — the package's
wording is the guardrail, and restating it in your own words is how a house rule
becomes a regulatory one in the retelling.** Where a string is quoted below it was
taken from real output generated this session.

### Threshold provenance — seven of the eight thresholds are HOUSE

Derived this session from `cdfibenchmark.BENCHMARKS`: **7 of 8** entries carry
`source == "HOUSE"` (`nim`, `efficiency_ratio`, `roaa`, `roae`,
`loans_to_deposits`, `npl_ratio`, `reserve_coverage`). **`tier1_ratio` is the
only cited one.** The report renders the distinction on every metric:

```
**Benchmark:** Strong >= 3.5% | Adequate >= 2.5% — **this tool's own threshold (HOUSE)**, not a regulatory or supervisory standard
**Benchmark:** Strong >= 8% | Adequate >= 5% — 12 CFR 324.12 (CBLR qualifying, lowered 9%->8% eff. 2026-07-01); 12 CFR 324.403(b)(1) (PCA well-capitalized leverage minimum)
```

Silence here is the failure 0.3.0 spent a release closing: an unattributed house
rule of thumb sitting in the same column as a CFR citation reads as a standard.
The package's own note on why the seven are uncited, and why inventing a citation
would be the defect (`data/schema.py:95-100`): bank capital has published
regulatory levels; earnings, efficiency, funding and reserve-coverage ratios do
not.

### `PeerGroup.caveats` — render them BEFORE any number, and only a `PeerGroup` carries them

`generate_report` prints a `> **Peer group caveats**` block above the summary
table **when two conditions both hold**: `peers` is the `PeerGroup` object
`build_peer_group` returned, **and** its `caveats` list is non-empty. An empty
list means the group is exactly what was asked for. A plain `list` means the
block is not printed at all, whatever the group's flaws — see *When the caveats
silently vanish*, below.

`PeerGroup.caveats` raises **eight** conditions. Count derived this session, not
read off the prose (`peers/selector.py:183-269`):

```
awk '/def caveats/,/^def _dedupe_by_cert/' cdfibenchmark/peers/selector.py \
  | grep -c 'out.append('
8
```

1. a dropped same-state constraint;
2. **n = 0** — not a peer comparison at all;
3. a group below `min_peers`;
4. peers **not** all at one reporting period;
5. peers all at one period that is **not the institution's** — *"Peers are at
   {date} but the institution is at {target}."* (`selector.py:223-228`). **This
   is the case the deleted `report_date` rule used to cover**: a subject at 3/31
   measured against peers at 12/31 is a YTD-flow mismatch across four quarters,
   and 0.3.0 raises it here as a caveat on the group rather than leaving you to
   infer it from two dates. Nothing else in this skill covers it, so render it;
6. a subject at the 10th percentile or below / 90th or above of its own peer
   group by assets;
7. a peer whose FDIC value the tool refused;
8. a truncated asset window.

Real output, this session:

```
> - Peer group has 1 institutions, below the requested minimum of 10. Percentiles over so few peers are not a reliable benchmark.
> - The subject is at the 0th percentile of its own peer group by assets: nearly every peer is LARGER than the institution. Comparisons against this group's median carry a size bias.
> - FDIC published a value for RBC1AAJ on 1 peer that fell outside this tool's plausibility bound for a percentage and was refused. Those peers are excluded from that metric's median and percentiles. A refusal is this tool's judgement, not FDIC's: the published values were real filings.
```

That is the enumeration read from `PeerGroup.caveats`
(`peers/selector.py:183-269`), complete at eight branches for 0.3.1 by the count
derived above — not a claim that a later version cannot add a ninth.

#### When the caveats silently vanish

`generate_report(institution, peers, title=None)` accepts **any** list. Three of
its disclosures are read off the `PeerGroup` object with `getattr` and are simply
skipped when the attribute is not there — `caveats` (`report/generator.py:182`),
`asset_percentile` (`:308`) and `selection_basis` (`:324`). Those are the only
three of the four `getattr(peers, …)` sites that lack a fallback; the fourth,
`report_dates` (`:146`), recomputes from the peers themselves and survives.

`PeerGroup` subclasses `list`, so **any** operation that returns a plain list
strips all three. Executed this session, all four forms: `list(pg)`, `pg[:20]`,
`[p for p in pg]` and `sorted(pg, key=…)` each render `> **Peer group caveats**`,
`**Peer Selection Basis:**` and `**Institution's Position in the Peer Asset
Range:**` as **absent**. There is no error and no warning — the report is just
shorter, and reads as complete.

Executed this session — the same institution and the same single peer, once as
the `PeerGroup` and once as `list(pg)`, against a third case with an ordinary
caveat-free group:

```
disclosure                                               A     B     C  summary_table
> **Peer group caveats**                              True False False    False
**How to read Status:**                               True  True  True    False
**Benchmark:**                                        True  True  True    False
**Not graded:**                                       True  True False    False
**Not shown:**                                       False False False    False
**Basis:**                                            True  True  True    False
**Peer Selection Basis:**                             True False  True    False
**Asset Bucket:**                                     True  True  True    False
**Institution's Position in the Peer Asset Range:**   True False  True    False
**Distinct Institutions:**                            True  True  True    False
**Peer Report Date:**                                 True  True  True    False
this tool's own threshold (HOUSE)                     True  True  True    False

A = PeerGroup — 3 caveats, one ungraded metric (the group printed above)
B = list(pg)  — same institution, same peer, same data
C = PeerGroup from build_sample_peer_group — 0 caveats, every metric graded
```

**Column B is the trap.** The group in column A is the one whose three caveats
are printed above — 1 peer, subject at the 0th percentile, one peer's `RBC1AAJ`
refused. Handed over as `list(pg)`, that identical group renders **zero
caveats** and no selection basis, and reads as a complete peer comparison.

**So: pass the `PeerGroup` straight through to `generate_report`.** Narrow the
group through `build_peer_group`'s own arguments — `same_state`,
`asset_tolerance`, `min_peers`, `max_peers`, `report_date` — **before** it is
built, never by filtering or slicing after. If you already hold a plain list, do
**not** hand it to `generate_report`: rebuild the group, or render `pg.caveats`
and `pg.selection_basis` from the original object yourself and state that the
peer set was modified after selection.

**Columns A and C differ too, and not by type.** `> **Peer group caveats**` and
`**Not graded:**` are absent from C because that group has no caveats and that
profile has no ungraded metric — those two lines are conditional on the *data*,
where the three above are conditional on the *type*. Neither kind is a fixed
feature of the report. Check for a line before you promise the user it is there.

### Status does NOT consult the peer columns

`BenchmarkResult.status` compares the institution's value to the fixed thresholds
and **never reads the peer median or percentiles printed beside it**. A metric can
grade STRONG while sitting below the peer median. The report says so directly,
beneath the summary table — carry this sentence whenever you show a Status column
next to peer columns:

> **How to read Status:** Status grades the **Institution** column against the
> fixed thresholds shown on each metric's **Benchmark** line below. It does
> **not** consult the Peer Median, 25th or 75th percentile columns. A metric can
> grade STRONG while sitting below the peer median, and ADEQUATE while sitting
> outside the peer range entirely. Read the grade and the peer columns as two
> separate questions — this report answers both and combines neither.

### `loans_to_deposits` is a BAND, and is deliberately not ranked

It is graded two-sided: WEAK below the HOUSE floor of 50 (under-deployed) as well
as above 95 (funding strain). All three boundaries are house numbers; there is no
regulatory loans-to-deposits level. Executed at 0.3.1 this session: `20 -> WEAK`,
`55 -> STRONG`, `80 -> STRONG`, `95 -> ADEQUATE`, `130 -> WEAK`, `200 -> WEAK`.

Because a band has no monotone better-direction, **`rank_institution` refuses to
rank it**:

```
{'rank': None, 'percentile': None, 'peer_count': 20,
 'reason': 'loans_to_deposits is graded as a band, so there is no monotone better-direction to rank on'}
```

Report the `reason`. Do not invent a percentile for this metric, and do not treat
`rank=None` as an error.

### `tier1_ratio` has THREE states, not two

Published, unreported, and **refused**. The package made refusal a distinct basis
precisely so it could not be conflated with absent. A refused value renders its
own line — real output, this session:

```
**Not shown:** FDIC published a value for this metric that falls outside this tool's plausibility bound for a percentage, so it was refused as a wrong-field-class signal rather than graded. The bound is this tool's own heuristic, not FDIC's — the published value was a real filing. See `cdfibenchmark.data.fdic` for the bound and how it was derived.
```

Never report a refusal as "FDIC published nothing."

### Peer selection: nearest by asset distance, and the window usually does not bind

`build_peer_group` fetches the whole asset window in one query and keeps the
`max_peers` banks **NEAREST the subject by `|assets - subject|`**, ties broken on
CERT. This is not the 0.2.1 behaviour and not a supervisory peer group. The group
renders its own `selection_basis`, which leads with the realized span rather than
the window, because the ±50% window is inert for most subjects and the real
breadth is set by the 50-bank cap. `PeerGroup.selection_basis` is generated text —
**read it off the object and quote it**, rather than describing the selection from
this paragraph.

## Rendering — prefer `generate_report`, and never fill an N/A

**Reach for `c.generate_report(institution, peers)` on any request for "the
benchmark report".** It is the only surface that renders the package's own
disclosures: `summary_table` returns ten columns and carries **none** of them, in
every configuration tested — that half is unconditional and is the `summary_table`
column of the matrix under *When the caveats silently vanish*.

**The `generate_report` half is NOT unconditional, and the matrix is where to
read it.** Of the twelve disclosure strings checked there, five are conditional:
three on `peers` being the `PeerGroup` object rather than a plain list
(`> **Peer group caveats**`, `**Peer Selection Basis:**`, `**Institution's
Position in the Peer Asset Range:**`) and two on the data
(`**Not graded:**` needs a present-but-ungraded metric, `**Not shown:**` needs a
refused one — it was absent from all three cases run). The remaining seven
rendered in every case.

**So do not promise a line before you have checked for it.** `generate_report`
renders each disclosure *when its condition holds*; pass the `PeerGroup`
unmodified so the type-conditional three can hold at all, then quote what the
report actually printed rather than what this skill says it can print. That
matrix is the twelve strings checked, not a claim that it is every disclosure the
report renders.

If you present `summary_table` instead, you are responsible for carrying the
`basis` and `threshold_source` columns and the caveats yourself — and for the
rule below.

### `summary_table`'s `vs_median` is the RAW difference — do not print it rounded beside rounded operands

`BenchmarkResult.vs_median` subtracts the unrounded values, deliberately, so
programmatic consumers get an exact figure. `generate_report` prints the
difference of the **rendered** operands instead, because the report shows both to
2dp. Round `vs_median` yourself and the arithmetic on the page stops adding up.
Executed this session:

```
  institution (raw) = 4.3649
  peer_median (raw) = 2.2473745332357096
  vs_median   (raw) = 2.11752546676429
  an AI rounding summary_table to 2dp prints: 4.36 , 2.25 , 2.12
  ... and 4.36 - 2.25 = 2.11, NOT 2.12
  generate_report prints instead: **vs Peer Median:** 2.11% above median
```

The package fixed this on its report face and left `vs_median` exact on purpose.
If you print a rounded difference, **compute it from the rounded operands** —
`round(inst, 2) - round(median, 2)` — or take the line from `generate_report`.

### Output-presentation rules

- Show the metric, the institution value, the peer median (and 25th/75th when
  present), the package's own `status` label, and the row's **`basis`** — do not
  invent your own verdict language.
- **Render an absent value (NaN/None) as "N/A". Never fill it.** Never substitute
  a peer median, a zero, or a plausible number.
- **Never render a present-but-ungraded value as "not available."** Report the
  number, quote its `basis`, and quote the report's own `Not graded:` line.
- **Say where a threshold comes from.** Seven of the eight are `HOUSE`. Never let
  a house rule of thumb read as a regulatory standard.
- State the peer group basis (sample vs. live FDIC) and `peer_count`, and render
  `PeerGroup.caveats` **before** any number, as the report does — **but only a
  `PeerGroup` has them.** Pass `build_peer_group`'s object to `generate_report`
  unmodified; a filtered or sliced plain `list` drops the caveats, the selection
  basis and the subject's position in the peer asset range with no error.
- If any typed FDIC error occurred, report it instead of a partial table.

## Failure modes

- **Credit union / loan fund requested** → decline (not FDIC-covered).
- **Nonexistent cert** → `get_financials`/`get_institution` return `None`; report
  "institution not found," don't proceed with an empty profile.
- **FDIC API down / malformed** → `FDICAPIError` / `FDICResponseError`; report it.
- **Missing call-report field** → NaN + `N/A` status; render as N/A, never fill.
- **Present value, ungraded basis** → `N/A` status with the value in hand;
  report the value and its `basis`. Do NOT say "not available".
- **Name search** (`search_institutions(name=...)`) matches active institutions on
  substring; a zero-hit search on a valid name form is a legitimate empty result,
  not an error.

## Caveats

- Metrics are computed from **FDIC call-report data**; they reflect the reported
  `report_date` and FDIC's data quality, not an independent audit.
- Peer groups are **heuristic**: 0.3.0 keeps the `max_peers` banks NEAREST the
  subject by asset distance out of a ±50% candidate window, pinned to one report
  date. A "peer" is a comparable-size FDIC bank, not a certified CDFI-only cohort
  and not a supervisory (UBPR) peer group. Quote `PeerGroup.selection_basis`
  rather than describing the rule from memory.
- `build_sample_peer_group` returns **synthetic** peers for demonstration; label
  any output built on it as illustrative, not a real peer comparison.
- **Read `basis` before presenting any metric** — see the basis rule above. A
  value on FDIC's published series is annualized at every report date; a value
  on the computed fallback is not graded by the package and must not be
  annualized by you. `nim`'s computed fallback is ungradeable at every period,
  including 12/31.
- **The peer median can mix bases**, even when every peer shares a `report_date`
  — the package records this as an unfixed limitation of 0.3.0 and calls such a
  median a fabricated statistic. Say so when you present one.
- Seven of the eight thresholds are **HOUSE** rules of thumb, not standards; only
  `tier1_ratio` carries a citation.
- **An FDIC-published basis is not a plausibility check.** A published ratio that
  is absurd on its face — a negative efficiency ratio, a three-digit ROAE, an
  earnings ratio on negative equity — is gradeable and grades `STRONG`. The
  package records this as a known limitation it did not fix
  (`data/schema.py:427`). Report the value; do not let the grade speak for it.
- **`generate_report`'s disclosures are conditional, not guaranteed.** Three of
  them require `peers` to be the `PeerGroup` object; two more require the data to
  trigger them. A plain `list` of the same peers renders a shorter report that
  reads as complete.
