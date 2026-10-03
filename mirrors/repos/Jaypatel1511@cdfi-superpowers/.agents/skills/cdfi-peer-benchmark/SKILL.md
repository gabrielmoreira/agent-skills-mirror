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
request maps to a call rather than to a guess. `cdfibenchmark.__all__` has **21**
names in 0.3.4 (counted this session; 19 in 0.3.1 — 0.3.2 added
`UNKNOWN_VERSION`, 0.3.3 added `CBLRScheduleError`, 0.3.4 added none); the ones
that decide what a user is shown are named here. This is not a design pass over
all 21 — a name
absent below is unruled, not endorsed.

**Endorsed — reach for these:**

| function | reach for it when |
|---|---|
| `generate_report` | **"give me the benchmark report."** The full Markdown report, and the only surface that renders the caveats, bases, threshold provenance and peer-group disclosures. Default to this. |
| `summary_table` | a DataFrame is genuinely wanted. Carries `basis`, `threshold_source` and (since 0.3.4) `report_withholds_peer_stats`, but **none** of the report's caveats — you then owe the user those yourself, and the thin-cell rule below. |
| `get_financials` | pull one institution's call-report profile by CERT. |
| `search_institutions` | find a CERT by name/state/asset size. |
| `build_peer_group` | the real peer group, live from FDIC. |
| `build_sample_peer_group` | a deterministic **synthetic** demo group. Label any output built on it as illustrative. |
| `benchmark_institution` | the per-metric `BenchmarkResult` objects behind the table. |
| `rank_institution` | a percentile on one metric — and read its `reason` when `rank` is `None`. It ranks over as few as one peer (at n = 1 it returns percentile 100.0 or 0.0) and does not apply the report's minimum of 5: on a row where `report_withholds_peer_stats` is set, do not present its rank or percentile (see *Thin peer cells*). Its `peer_count` is the metric's n on success and when no peer has a value (0), but the group size on its other two refusal paths, institution value missing and banded metric (cdfi-benchmark's CHANGELOG `[0.3.4]`, Known limitations 2). |

**Refused — do not reach for these to answer a benchmarking question:**

| function / attribute | why not |
|---|---|
| `compute_peer_metrics` | returns raw per-peer metrics with **no basis awareness**. Taking a median or a percentile off it yourself reproduces the mixed-basis defect the package records as unfixed, without the caveat the report carries. Use `benchmark_institution` / `generate_report`. |
| `get_peer_financials` | the raw peer fetch. It applies **no** dedupe, no period pinning and no nearest-by-assets selection — `build_peer_group` is what turns it into a peer group. Calling it directly rebuilds the 0.2.x defect by hand. |
| `get_institution` | returns a **raw FDIC dict**, not an `InstitutionProfile`, and carries none of the parse-layer discipline (no NaN-vs-zero rule, no plausibility bound, no `implausible_fields`). Fine for identity lookup; never a source of metrics. |
| `BENCHMARKS`, `ASSET_BUCKETS` / `HOUSE_ASSET_BUCKETS` | read them to **quote** a threshold or a band boundary with its `source`. Never restate a number from them without its HOUSE attribution, and never mutate them. **Not for `tier1_ratio`:** since 0.3.3 `BENCHMARKS["tier1_ratio"]` is a default (the 8% level as in force on 2026-09-22) that its own `source` says no graded report uses. The Tier 1 threshold is resolved per report date; quote the report's **Benchmark:** line or the row's `threshold_source` instead. |
| `InstitutionProfile(...)` built by hand | legitimate for a demo, but a hand-built profile has no `reported_*` values, so every earnings metric falls to the computed proxy — see the basis rule. Do not present one as a real institution. |

**Never fabricate the inputs.** If FDIC is unreachable or a CERT does not resolve,
report that. Do not hand-build an `InstitutionProfile` from remembered or
estimated financials and present the resulting grades as a benchmark.

## Install

```
pip install "cdfi-benchmark>=0.3.4"
```

**The floor is `>=0.3.4`, and it is load-bearing.** Below 0.3.4 the report
prints each metric's peer median and percentiles with **no n**, beside a group
count that does not describe them, and prints them even when one peer has a
value for the metric. 0.3.4's CHANGELOG (`[0.3.4]`, Summary) measured this at
`20260630` for CERT 16583: a group of 19 had a value for reserve coverage at 1
peer, for NPL ratio at 4 and for loans-to-deposits at 7, and the page gave 19
three times. 0.3.4 prints n wherever a peer statistic appears and **withholds**
the median, percentiles and vs-median line when 1 to 4 peers have a value (see
*Thin peer cells* below). It changes no grade and no value.

Below 0.3.3 the package also
asserts Tier 1 leverage grades that its own CHANGELOG (`[0.3.3]`, defects A–G,
with a disclosure table per version) says rest on a CBLR (community bank
leverage ratio) level that was not in force, or on the wrong operator.
0.2.1–0.3.1 graded `>= 8%` at every report date — 0.3.1's Benchmark line read
*"Strong >= 8% | Adequate >= 5% — 12 CFR 324.12 (CBLR qualifying, lowered 9%->8%
eff. 2026-07-01); 12 CFR 324.403(b)(1) (PCA well-capitalized leverage minimum)"*
— and 0.3.2 graded against 9% before 2026-07-01. Those
versions graded dates before the CBLR framework existed (before 2020-01-01),
dates in the 2020-06-30 → 2021-12-31 relief window whose level was set by a
section they do not encode, a value exactly at the level as passing where the
rule says "greater than", and missing or malformed report dates. 0.3.3 refuses
in every one of those cases — `status` N/A, the value still shown, the reason
stated — instead of asserting a grade (see *`tier1_ratio`* below). No other
metric's value or grade changes between 0.3.1 and 0.3.3. (0.1.0 and 0.2.0 were
not examined for this; the floor excludes them either way.)

**If an older version is installed, upgrade before grading anything:**

```
python -c "import cdfibenchmark; print(cdfibenchmark.__version__)"
pip install -U "cdfi-benchmark>=0.3.4"
```

Do not present a Tier 1 grade produced by a version below 0.3.3, or a peer
statistic produced by a version below 0.3.4. (Below 0.3.0
the package also grades `loans_to_deposits` backwards: a bank lending 55% of its
deposits grades WEAK and one lending 200% grades STRONG, with
`rank_institution`'s percentile inverted to match. That was an earlier floor's
reason, and `>=0.3.4` still covers it.)

**This skill deliberately does not name the newest release.** A note of the form
*"newest on PyPI, as of «date»: «version»"* is a claim that decays into a
falsehood while sitting still, and this paragraph used to be one: it named the
release current on 2026-09-07, a successor published two days later, and the
sentence sat here wrong for a fortnight. A date stamp does not make a false
statement true — it only records when it stopped being checked.

For today's answer run `pip index versions cdfi-benchmark`, or read
`references/package-index.md`, whose version cells CI re-derives from live PyPI
on every run. The floor above is a minimum, not a claim about the newest release.

**Every executed output block below was recorded against cdfi-benchmark 0.3.4**
on python 3.12.13 with pandas 3.0.6, on 2026-10-01, and says so at its location.
The 0.3.4 wheel was built from the 0.3.4 source (commit `d1fad78`)
because 0.3.4 was not yet on PyPI when these were recorded.

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

`status == "N/A"` means one of two different things (since 0.3.0), and the correct
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

**0.3.3 adds a second cause of meaning (2), for `tier1_ratio` only:** the basis
is gradeable, but `BenchmarkResult.not_graded_reason` (and the `summary_table`
column of the same name) is set, because the report date is one the CBLR
schedule refuses or the value displays as the level itself. Report the value and
quote that reason — see *`tier1_ratio`* below.

Executed this session (0.3.4, python3.12) — three rows excerpted from the output
of *Worked example — the N/A contract in action*, below:

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
                        and (r.basis not in GRADEABLE_BASES
                             or r.not_graded_reason is not None))  # 0.3.3+
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
number.** Since 0.3.0 the package PREFERS FDIC's own published series —
`NIMY`, `ROA`, `ROE`, `EEFFR` — which arrive **already annualized and over
average balances**. `get_financials` and `get_peer_financials` request those four fields at every
report date (`cdfibenchmark/data/fdic.py:158` and `:240`). On that path a 3/31
NIM of 3.08% is a correct annualized figure; calling it "roughly 4x low" would
push the user toward **12.3%**, a number no source produced.

**The judgment is the package's, not yours.** `InstitutionProfile.metric_basis()`
rules how each metric was obtained (`cdfibenchmark/data/schema.py:851`) and
`GRADEABLE_BASES` (`schema.py:599`) rules whether that basis may be graded at
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
`tier1_ratio` has its own states in its own section below — and its grade does
depend on `report_date` since 0.3.3, but that is the package's ruling, surfaced as
`not_graded_reason`, not one you make. `BASIS_UNRULED`
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
says so on its face. Executed this session (0.3.4, python3.12), on a
**hand-built** profile whose `reported_*` fields carry the values FDIC's
published series would occupy — the same stand-in this skill uses above; no
live filing with these values was probed. The `-700` is not invented for the
demo: it is a value the package records
as really present in the population, cited below.

```
efficiency_ratio  -700.0   basis FDIC published — annualized, average balances   gradeable=True   status=STRONG
roae               999.0   basis FDIC published — annualized, average balances   gradeable=True   status=STRONG
```

The package states this hole itself rather than leaving it to be discovered.
Quote its words — `cdfibenchmark/data/schema.py:803`, `reported_is_trustworthy`,
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

Executed this session (0.3.4, python3.12) — one profile at `report_date =
"20260331"` (Q1), with and without FDIC's published ratios. All dollar inputs in
thousands: total assets 78,100; interest income 2,000 and interest expense 200;
non-interest income 150; non-interest expense 1,250; net income 240; equity
9,000; plus total deposits 65,000, net loans 50,000, gross loans 51,000,
non-current loans 400, loan-loss allowance 600 and `tier1_ratio=11.5`. Those
last six do not affect the printed lines: re-run with all six changed, the
output was identical. The published-path profile adds `reported_nim=3.08`,
`reported_roaa=1.24`, `reported_roae=10.6`, `reported_efficiency_ratio=61.2`:

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
the package's source (`data/fdic.py:158`, which requests them unconditionally at
any `report_date`) and on the package's own recorded measurements
(`data/schema.py:557-559`: computing those three from YTD flows read
**4.30x / 4.12x / 4.01x low at a Q1 REPDTE** against FDIC's published series) —
**not on a live probe made here.** The branch behaviour above WAS executed.

### Peers at one `report_date` do NOT share one basis

Do not infer a shared basis from a shared date. Each peer's basis is decided per
institution by `reported_is_trustworthy`, so two banks at the same REPDTE can sit
on different bases. Executed this session (0.3.4, python3.12) — two peers built
from the Q1 profile above, peer 1 with `reported_nim=3.5` (and the other three
published ratios), peer 2 with none; the median is
`compute_peer_metrics([p1, p2])["nim"].median()`:

```
  both peers report_date = 20260331 == 20260331
  peer 1 nim basis: FDIC published — annualized, average balances
  peer 2 nim basis: computed over TOTAL assets — not FDIC NIMY (avg earning assets)
  peer 1 nim value: 3.5  peer 2 nim value: 2.3047
  median of the two: 2.9023687580025608 <- a median across TWO BASES
```

The package records this as a known limitation in its 0.3.0 CHANGELOG entry, and
no later entry through 0.3.4 records a fix.
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
(`cdfibenchmark/data/fdic.py:457-465`). `total_assets=250_000` is **$250MM**, not
$250 billion. `total_assets_mm` divides by 1,000 and `asset_bucket` and the
report face both read the raw field, so a profile hand-built in dollars renders
a bank a thousand times its real size.

**`report_date` must be FDIC's 8-digit form, `"YYYYMMDD"`.** `fiscal_quarter`
parses exactly that (`schema.py:775-778`) and the live path always produces it. A
hyphenated `"2024-12-31"` yields `fiscal_quarter is None`, which sends `roaa` and
`roae` to `computed from YTD flows, period unknown — NOT annualized` and grades
them **N/A even at a Q4 date**. Since 0.3.3 it also refuses the Tier 1 grade: the
Tier 1 row's `not_graded_reason` says the date is not in YYYYMMDD form.

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
print(st[["metric","not_graded_reason","report_withholds_peer_stats"]].to_string(index=False))
```

Actual output this session (cdfi-benchmark 0.3.4, python3.12), the first print
and the second:

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

`summary_table` carries further columns — `peer_25th` and `peer_75th`, `basis`
and `threshold_source`, since 0.3.3 `not_graded_reason`, and since 0.3.4
`report_withholds_peer_stats` (twelve columns in all; this run's
`len(st.columns)` was 12) — which are how a row's grade, its warrant and its
peer cells are read. Same run, the third print:

```
                                     metric                                                                                                   basis                                                                                                                                                                                                                                     threshold_source
Net Interest Margin over total assets (NIM)                                         computed over TOTAL assets — not FDIC NIMY (avg earning assets)                                                                                                                                                                                                                                                HOUSE
                           Efficiency Ratio                                                    computed from same-period YTD flows (period-neutral)                                                                                                                                                                                                                                                HOUSE
        Return on Assets, period-end (ROAA)                                              computed from full-year YTD flows over period-end balances                                                                                                                                                                                                                                                HOUSE
        Return on Equity, period-end (ROAE)                                              computed from full-year YTD flows over period-end balances                                                                                                                                                                                                                                                HOUSE
                      Tier 1 Leverage Ratio FDIC published (RBC1AAJ) — Tier 1 capital over adjusted average assets; a capital ratio, not annualized 12 CFR 324.12(a)(1) (CBLR qualifying level for institutions that have elected the CBLR framework: greater than 9% at this report date — 84 FR 61776, 61802, Nov. 13, 2019); 12 CFR 324.403(b)(1)(i)(D) (PCA well-capitalized leverage minimum, 5.0%)
                          Loans-to-Deposits                                                      computed from period-end balances (period-neutral)                                                                                                                                                                                                                                                HOUSE
                  Non-Performing Loan Ratio                                                      computed from period-end balances (period-neutral)                                                                                                                                                                                                                                                HOUSE
                 Loan Loss Reserve Coverage                                                      computed from period-end balances (period-neutral)                                                                                                                                                                                                                                                HOUSE
```

And the fourth. `None` on every row of both columns: 20241231 is a quarter-end
inside the schedule 0.3.4 attests (unchanged since 0.3.3), and 11.50% does not
display as the 9% level, so Tier 1 is graded; and every metric has 20 peers with
a value, so the report withholds no peer statistic:

```
                                     metric not_graded_reason report_withholds_peer_stats
Net Interest Margin over total assets (NIM)              None                        None
                           Efficiency Ratio              None                        None
        Return on Assets, period-end (ROAA)              None                        None
        Return on Equity, period-end (ROAE)              None                        None
                      Tier 1 Leverage Ratio              None                        None
                          Loans-to-Deposits              None                        None
                  Non-Performing Loan Ratio              None                        None
                 Loan Loss Reserve Coverage              None                        None
```

**Four things to read off this example, none of them obvious:**

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
4. **Tier 1's STRONG is a comparison with the CBLR level for institutions that
   have elected the CBLR framework** — "greater than 9%" at this report date,
   because 20241231 is after the framework took effect and after the 2020–2021
   relief window. The package's schedule constant `CBLR_LEVELS`
   (`cdfibenchmark.data.schema`) also holds a later, lower level, but no
   quarter-end report date resolves to it under 0.3.4 (checked this session:
   `benchmark_for("tier1_ratio", d)` over every quarter-end 2015–2030 gives 19
   dates at 9%, 20200331–20260630, 45 refused, none at the lower level). So no
   0.3.4 report grades against it; it appears only in the `BENCHMARKS` default
   `source` (see the refused-functions table above). It is not a
   finding that this bank elected CBLR or qualifies for it; cdfi-benchmark 0.3.4
   does not model election. Say so. Had the same profile carried a report date
   in a refused class, this row would read N/A with a reason — see
   *`tier1_ratio`* below.

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

Actual output this session (cdfi-benchmark 0.3.4, python3.12):

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

Signatures below were read from the installed 0.3.4 wheel with
`inspect.signature` this session (identical to 0.3.1's).

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
`ImportError` (verified this session on 0.3.4; `__all__` has 21 names and
`PeerGroup` is not among them). It is reachable only as
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

> **What was verified live.** The session that last updated this skill
> (cdfi-benchmark 0.3.4, 2026-10-01) reached `api.fdic.gov` and ran
> `get_financials`, `build_peer_group`, `summary_table`, `generate_report` and
> `get_institution` live for CERT 16583 at 20260630 (see *Peer groups can
> include uninsured trust companies*). The signatures and both host constants
> above are read from the installed wheel. Earlier sessions
> could not reach FDIC, and the passages that say so describe those sessions.
> Reachability from your own environment is yours to check.

## Typed errors — report, don't smooth over

The package raises **typed** exceptions; surface them, don't swallow them:

| exception | subclass of | fires on |
|---|---|---|
| `FDICAPIError` | `CDFIBenchmarkError` | FDIC API transport/HTTP failure |
| `FDICResponseError` | `CDFIBenchmarkError` | a malformed or wrong-shape FDIC response — **and one non-API case, below** |
| `CBLRScheduleError` | `CDFIBenchmarkError`, `RuntimeError` | new in 0.3.3: raised **at import** only if the shipped CBLR schedule constants break a data invariant. Not an `ImportError`, and no check reads your clock. |
| `CDFIBenchmarkError` | `Exception` | package base error |

Hierarchy verified this session against the installed 0.3.4 wheel:
`FDICAPIError.__mro__` and `FDICResponseError.__mro__` are both five elements,
`(<self>, CDFIBenchmarkError, Exception, BaseException, object)`;
`CBLRScheduleError.__mro__` is six, `(<self>, CDFIBenchmarkError, RuntimeError,
Exception, BaseException, object)`. Catching `CDFIBenchmarkError` catches all
three. When one is raised, report the error type and message; do not fall back
to fabricated numbers or a cached guess. A refused Tier 1 grade is **not** an
exception — it arrives as `status == "N/A"` with a `not_graded_reason`.

**`FDICResponseError` does not always mean FDIC misbehaved.**
`build_peer_group` raises it when the *institution's* `total_assets` is unknown,
because the asset window is then undefined. The FDIC response can be perfectly
well-formed. Reproduced this session (0.3.4, python3.12; a profile with CERT
34352 and every dollar field `None`):

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

## What the report discloses that you must carry (since 0.3.0)

0.3.0 spent a release making the report state its own warrant. Each item below
renders on `generate_report`'s face. **Do not paraphrase these — the package's
wording is the guardrail, and restating it in your own words is how a house rule
becomes a regulatory one in the retelling.** Where a string is quoted below it was
taken from real output generated this session.

### Threshold provenance — seven of the eight thresholds are HOUSE

Derived this session from `cdfibenchmark.BENCHMARKS`: **7 of 8** entries carry
`source == "HOUSE"` (`nim`, `efficiency_ratio`, `roaa`, `roae`,
`loans_to_deposits`, `npl_ratio`, `reserve_coverage`). **`tier1_ratio` is the
only cited one.** The report renders the distinction on every metric. From
`generate_report` on the first worked example's institution and peers (report
date 20241231), cdfi-benchmark 0.3.4, python3.12 — the NIM line and the Tier 1
line:

```
**Benchmark:** Strong >= 3.5% | Adequate >= 2.5% — **this tool's own threshold (HOUSE)**, not a regulatory or supervisory standard
**Benchmark:** Strong > 9% (a value that rounds to 9.00% is not graded) | Adequate >= 5% — 12 CFR 324.12(a)(1) (CBLR qualifying level for institutions that have elected the CBLR framework: greater than 9% at this report date — 84 FR 61776, 61802, Nov. 13, 2019); 12 CFR 324.403(b)(1)(i)(D) (PCA well-capitalized leverage minimum, 5.0%)
```

The Tier 1 line is resolved **for the report date**: it names the level in
force at that date for institutions that have elected the CBLR framework, and
at a refused date it names no level at all (see *`tier1_ratio`* below). Never
carry one report's Tier 1 line over to another report date.

Silence here is the failure 0.3.0 spent a release closing: an unattributed house
rule of thumb sitting in the same column as a CFR citation reads as a standard.
The package's own note on why the seven are uncited, and why inventing a citation
would be the defect (`data/schema.py:99-104`): bank capital has published
regulatory levels; earnings, efficiency, funding and reserve-coverage ratios do
not.

### `PeerGroup.caveats` — render them BEFORE any number, and only a `PeerGroup` carries them

`generate_report` prints a `> **Peer group caveats**` block above the summary
table **when two conditions both hold**: `peers` is the `PeerGroup` object
`build_peer_group` returned, **and** its `caveats` list is non-empty. An empty
list means the group is exactly what was asked for. A plain `list` means the
block is not printed at all, whatever the group's flaws — see *When the caveats
silently vanish*, below.

`PeerGroup.caveats` has **nine** `out.append` branches over **eight**
conditions in 0.3.4. Count derived this session from the 0.3.4 source (commit
`d1fad78`), not read off the prose. The caveats are built in
`peers/selector.py:208-325`; `report/generator.py` renders the list as it
finds it (`:575`, `getattr(peers, "caveats", [])`) and adds no group caveat. Its
per-metric **Peer statistics:** and **Thin peer cell:** lines are not
`PeerGroup.caveats` and are not counted here:

```
awk '/def caveats/,/^def _dedupe_by_cert/' cdfibenchmark/peers/selector.py \
  | grep -c 'out.append('
9
```

Nine, not eight, because 0.3.4 splits condition 3 into two mutually exclusive
branches with different texts. Conditions 6 and 7 also choose between two
wordings each (by variable, inside one `out.append`) depending on whether the
page shows any peer median.

1. a dropped same-state constraint;
2. **n = 0** — not a peer comparison at all;
3. a group below `min_peers` — **two branches**: when no metric has 5 peers
   with a value (every group of 1–4, and a larger group whose metrics are all
   thin) the caveat says the report shows no peer median or percentile;
   otherwise it keeps *"Percentiles over so few peers are not a reliable
   benchmark."*;
4. peers **not** all at one reporting period;
5. peers all at one period that is **not the institution's** — *"Peers are at
   {date} but the institution is at {target}."* (`selector.py:264-269`). **This
   is the case the deleted `report_date` rule used to cover**: a subject at 3/31
   measured against peers at 12/31 is a YTD-flow mismatch across four quarters,
   and since 0.3.0 the package raises it here as a caveat on the group rather
   than leaving you to infer it from two dates. Nothing else in this skill covers it, so render it;
6. a subject at the 10th percentile or below / 90th or above of its own peer
   group by assets;
7. a peer whose FDIC value the tool refused;
8. a truncated asset window.

Real output, this session (0.3.4, python3.12) — the `> **Peer group caveats**`
lines of `generate_report` for the first worked example's institution against a
`PeerGroup` of one hand-built peer (assets 300,000, i.e. larger than the
subject; `tier1_ratio=None` with `implausible_fields=("RBC1AAJ",)`), built with
`min_peers=10`:

```
> - Peer group has 1 institution, below the requested minimum of 10; this report shows no peer median or percentile for any metric (this tool's house minimum for showing them is 5 peers with a value for that metric).
> - The subject is at the 0th percentile of its own peer group by assets: nearly every peer is LARGER than the institution. Any comparison against this group would carry a size bias; this report shows no peer median, so it makes none.
> - FDIC published a value for RBC1AAJ on 1 peer that fell outside this tool's plausibility bound for a percentage and was refused. Those peers count as having no value for that metric (see Peers (n)). A refusal is this tool's judgement, not FDIC's: the published values were real filings.
```

The first line is condition 3's no-median branch, whose source template is
*"Peer group has {n} institution{s}, below the requested minimum of
{min_peers}; this report shows no peer median or percentile for any metric
(this tool's house minimum for showing them is 5 peers with a value for that
metric)."* Quote the rendered line, not the template. The second and third are
the no-median wordings of conditions 6 and 7.

That is the enumeration read from `PeerGroup.caveats`
(`peers/selector.py:208-325`), complete at nine branches over eight conditions
for 0.3.4 by the count derived above — not a claim that a later version cannot
add more.

#### When the caveats silently vanish

`generate_report(institution, peers, title=None)` accepts **any** list. Three of
its disclosures are read off the `PeerGroup` object with `getattr` and are simply
skipped when the attribute is not there — `caveats` (`report/generator.py:575`),
`asset_percentile` (`:719`) and `selection_basis` (`:747`). Those are the only
three of the four `getattr(peers, …)` sites that lack a fallback; the fourth,
`report_dates` (`:463`), recomputes from the peers themselves and survives.

`PeerGroup` subclasses `list`, so **any** operation that returns a plain list
strips all three. Executed this session (0.3.4), all four forms: `list(pg)`,
`pg[:20]`, `[p for p in pg]` and `sorted(pg, key=…)` each render `> **Peer group caveats**`,
`**Peer Selection Basis:**` and `**Institution's Position in the Peer Asset
Range:**` as **absent**. There is no error and no warning — the report is just
shorter, and reads as complete.

Executed this session (0.3.4, python3.12) — the same institution and the same
single peer, once as the `PeerGroup` and once as `list(pg)`, against a third
case with an ordinary caveat-free group:

```
disclosure                                             A     B     C  summary_table
> **Peer group caveats**                               True False False    False
**How to read Status:**                                True  True  True    False
**Benchmark:**                                         True  True  True    False
**Not graded:**                                        True  True False    False
**Not shown:**                                        False False False    False
**Basis:**                                             True  True  True    False
**Peer Selection Basis:**                              True False  True    False
**Asset Bucket:**                                      True  True  True    False
**Institution's Position in the Peer Asset Range:**    True False  True    False
**Distinct Institutions:**                             True  True  True    False
**Peer Report Date:**                                  True  True  True    False
this tool's own threshold (HOUSE)                      True  True  True    False
```

A = the `PeerGroup` whose three caveats are printed above — one ungraded metric
(NIM, on the computed fallback). B = `list(pg)` — same institution, same peer,
same data. C = `build_sample_peer_group` for the same institution with FDIC's
four published ratios added (`reported_nim=3.08`, `reported_roaa=1.0`,
`reported_roae=8.93`, `reported_efficiency_ratio=71.9`) — 0 caveats, every
metric graded.

All 48 cells match the 0.3.3 table this replaced. 0.3.4 also prints
**CBLR schedule verified through:** in all three cases (new in 0.3.3), and three
lines new in 0.3.4, none of them among the twelve strings above: the summary
table's `Peers (n)` column (A, B and C); **Peer statistics:**, which replaces a
metric's median and vs-median lines when fewer than 5 peers have a value (A and
B, not C); and **Thin peer cell:**, at 5–9 peers with a value (in none of the
three, since A and B have one peer and C has twenty).

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

Since 0.3.4, on a page that shows **no** peer median (every metric has fewer
than 5 peers with a value — every group of 1–4, and a larger group whose
metrics are all thin), the note keeps its first two sentences and ends instead
with this, rendered this session (0.3.4, python3.12) for column A of the matrix
above:

> This page shows no peer median or percentile for any metric, so it answers
> only the grade question.

Carry whichever version the report actually printed.

### `loans_to_deposits` is a BAND, and is deliberately not ranked

It is graded two-sided: WEAK below the HOUSE floor of 50 (under-deployed) as well
as above 95 (funding strain). All three boundaries are house numbers; there is no
regulatory loans-to-deposits level. Executed at 0.3.4 this session: `20 -> WEAK`,
`55 -> STRONG`, `80 -> STRONG`, `95 -> ADEQUATE`, `130 -> WEAK`, `200 -> WEAK`.

Because a band has no monotone better-direction, **`rank_institution` refuses to
rank it**:

```
{'rank': None, 'percentile': None, 'peer_count': 20, 'reason': 'loans_to_deposits is graded as a band, so there is no monotone better-direction to rank on'}
```

Report the `reason`. Do not invent a percentile for this metric, and do not treat
`rank=None` as an error.

### `tier1_ratio`: graded, unreported, refused by plausibility, or not graded for its date

**Four states, not two.** (1) Published and graded. (2) Unreported — basis `no
value was reported for this field`, value NaN: meaning (1) of the N/A contract.
(3) **Refused by plausibility** — FDIC published a value this tool's bound
rejected. The package made that a distinct basis precisely so it could not be
conflated with absent, and it renders its own line — real output, this session
(0.3.4, python3.12):

```
**Not shown:** FDIC published a value for this metric that falls outside this tool's plausibility bound for a percentage, so it was refused as a wrong-field-class signal rather than graded. The bound is this tool's own heuristic, not FDIC's — the published value was a real filing. See `cdfibenchmark.data.fdic` for the bound and how it was derived.
```

Never report that as "FDIC published nothing."

(4) **Present, gradeable basis, but not graded — new in 0.3.3.** The value is
shown, `status` is N/A, and `BenchmarkResult.not_graded_reason` (the
`summary_table` column of the same name, and a **Not graded:** line on the
report) says why. Since 0.3.3 the package refuses rather than asserts a Tier 1
grade when the following hold. 0.3.4 changes none of these conditions. It
rewords the relief-window `not_graded_reason` (which now ends with a URL) and,
for a missing or malformed date, the Benchmark line and the `threshold_source`
prefix (its CHANGELOG `[0.3.4]`, Fixed) — so quote what the report prints:

- the report date is **before 2020-01-01** (no CBLR framework yet);
- the report date is **2020-06-30 through 2021-12-31** (the level was set by the
  temporary 12 CFR 324.303, which 0.3.4 does not encode);
- the report date is **after 2026-09-22**, the date the CBLR schedule was
  verified through, the same in 0.3.3 and 0.3.4 (`LEVELS_VERIFIED_THROUGH`,
  shown on every report as **CBLR schedule verified through:**). This includes
  **20260930 and every later quarter** until a later release extends it;
- the report date is **missing, malformed or not a quarter-end**;
- the value **rounds to the level itself** at the report's 2 decimal places
  (e.g. 9.00% against "greater than 9%").

Rendered by 0.3.4 (python3.12) for the first worked example's institution with
only the report date changed to 20260930:

```
**Benchmark:** none applied at this report date — no CBLR qualifying level (12 CFR 324.12) or PCA leverage level (12 CFR 324.403) is applied; the reason is stated under **Not graded** below
**Status:** N/A
**Not graded:** This version's CBLR schedule was verified against the CFR as in force on 2026-09-22. This report date, 2026-09-30, is later, so no CBLR qualifying level is applied and this value is not graded. A later release of cdfi-benchmark may cover it.
```

and with the report date kept at 20241231 and `tier1_ratio=9.004`:

```
**Benchmark:** Strong > 9% (a value that rounds to 9.00% is not graded) | Adequate >= 5% — 12 CFR 324.12(a)(1) (CBLR qualifying level for institutions that have elected the CBLR framework: greater than 9% at this report date — 84 FR 61776, 61802, Nov. 13, 2019); 12 CFR 324.403(b)(1)(i)(D) (PCA well-capitalized leverage minimum, 5.0%)
**Status:** N/A
**Not graded:** This value rounds to 9.00% at the 2 decimal places this tool's report displays, which is the CBLR qualifying level for this report date itself (9%). At that precision this tool cannot state on the face of its report whether the value exceeds the level, so it does not grade it.
```

**What to do with a state-(4) row:** report the value, say it was not graded,
and quote the package's reason verbatim. **Do not supply a grade yourself** —
not by applying 8% or 9%, not from the PCA 5% leg (the package withholds that too at a
refused date), and not from memory of what an older version said. Where the
date is the cause, say that a later cdfi-benchmark release may cover it; where
the value displays as the level, say the tool cannot show which side of the level
it is on.

**Do not silently switch to an older `report_date` to obtain a grade.**
`get_financials(cert)` with no `report_date` returns the institution's most
recent filing: the 0.3.4 source (`data/fdic.py` is unchanged from 0.3.3) sorts
`REPDTE` descending and takes the first row (`data/fdic.py:172-173` and `:188`;
read from source, not probed live). Once
20260930 filings are on FDIC, that call returns a Tier 1 value 0.3.4 refuses.
You may *offer* to benchmark an earlier quarter, but only if you say explicitly
that it is a different, older period than the one the user asked about, and
you keep the refusal for the latest period on the page.

**On a graded row,** the comparison is with the level for institutions that
**have elected** the CBLR framework. 0.3.4 does not model election (its CHANGELOG
`[0.3.3]`, Known limitations 1). Never turn a Tier 1 STRONG into "this bank
qualifies for /
has elected CBLR", and cite only what the Benchmark line cites (FDIC's 12 CFR
Part 324; the package makes no claim about the OCC's or Federal Reserve's
parallel rules).

### Peer selection: nearest by asset distance, and the window usually does not bind

`build_peer_group` fetches the whole asset window in one query and keeps the
`max_peers` banks **NEAREST the subject by `|assets - subject|`**, ties broken on
CERT. This is not the 0.2.1 behaviour and not a supervisory peer group. The group
renders its own `selection_basis`, which leads with the realized span rather than
the window, because the ±50% window is inert for most subjects and the real
breadth is set by the 50-bank cap. `PeerGroup.selection_basis` is generated text —
**read it off the object and quote it**, rather than describing the selection from
this paragraph.

### Peer groups can include uninsured trust companies

`build_peer_group` draws from every FDIC call-report filer in the asset window,
and that includes filers that are **not FDIC-insured** — `INSFDIC` 0, `BKCLASS`
NC: non-deposit, non-lending trust companies. 0.3.4 does not exclude them; its
CHANGELOG (`[0.3.4]`, Known limitations 1) records this. They have no loans or
deposits, so they drop out of loans-to-deposits, NPL ratio and reserve coverage,
but they count in the peer n and statistics of NIM, efficiency, ROAA, ROAE and
Tier 1 — and a trust company's Tier 1 leverage ratio can be near 100%. They
can therefore distort peer medians. Executed this session against live FDIC
(0.3.4, python3.12), CERT 16583 at `report_date='20260630'`, default
`build_peer_group` arguments — six lines excerpted, in order, from the run's
output:

```
subject: 16583 STATE BANK OF BURRTON BURRTON KS 20260630 assets $k 9316.0
peer group size: 19 report_dates: ['20260630']
Tier 1 row: institution 9.940880227720603 peer_median 87.19254658385093 peer_count 19 status STRONG
| Tier 1 Leverage Ratio | 9.94% | 87.19% | 46.37% | 93.98% | 19 | ✅ STRONG |
**Peer Median:** 87.19% (n = 19 peers with a value for this metric)
**vs Peer Median:** 77.25 pp below median (88.6% below) [n = 19 peers with a value]
```

The package does not carry `INSFDIC` or `BKCLASS`, and `get_institution`
returned `None` for the two trust-company CERTs tried (34732, 57081): FDIC's
`/institutions` endpoint has no row for them. FDIC's `/financials` endpoint
does, at the same REPDTE. Queried this session for the 19 peers above (three of
the twelve such rows, then the count):

```
 34732  NEW COVENANT TRUST CO NA            20260630  INSFDIC=0  BKCLASS=NC  RBC1AAJ=90.75781664016958
 59047  NEUBERGER BERMAN TR CO DE NA        20260630  INSFDIC=0  BKCLASS=NC  RBC1AAJ=94.67835535251265
 33239  TRUST CO OF TOLEDO NA               20260630  INSFDIC=0  BKCLASS=NC  RBC1AAJ=100.2510355215263
rows: 19  INSFDIC=0 and BKCLASS=NC: 12
```

So 12 of the 19 peers behind that 87.19% Tier 1 median are uninsured trust
companies. Status is unaffected (it never reads a peer value); the peer columns
are what is distorted.

**When a peer statistic looks implausible** — a Tier 1 median far above any
insured bank's, an efficiency or ROAA median out of line with the subject's
size class — **check the peer list before presenting it.** Read the names off
the `PeerGroup` (`[(p.cert, p.name) for p in pg]`) and, for `INSFDIC` /
`BKCLASS`, query `https://api.fdic.gov/banks/financials` with
`filters=REPDTE:<date> AND CERT:(<cert> OR <cert> OR …)`,
`fields=CERT,NAME,INSFDIC,BKCLASS` and `limit=100`. Join the CERTs with ` OR `:
a space- or comma-separated list is rejected with HTTP 400. Set the limit: the
default of 10 silently truncated CERT 16583's 19 peers to 10 rows holding 4 of
the 12 trust companies (live, 2026-10-02). Check that `meta.total` equals the
rows returned before you count. If uninsured trust companies are in the
group, say so beside every affected peer statistic, with how many of the n they
are. Do **not** filter them out of the `PeerGroup` and hand the result to
`generate_report` — a filtered group is a plain `list` and loses the caveats
(see *When the caveats silently vanish*) — and do not compute a replacement
median yourself.

## Rendering — prefer `generate_report`, and never fill an N/A

**Reach for `c.generate_report(institution, peers)` on any request for "the
benchmark report".** It is the only surface that renders the package's own
disclosures: `summary_table` returns twelve columns in 0.3.4 (the twelfth,
new in 0.3.4, is `report_withholds_peer_stats`) and carries **none** of the
report's disclosure lines, in every configuration tested — that half is
unconditional and is the `summary_table` column of the matrix under *When the
caveats silently vanish*. (Its `not_graded_reason` column, new in 0.3.3, carries
the Tier 1 date or display reason as text. It does not carry the basis
`Not graded` sentence or any other disclosure. Its `report_withholds_peer_stats`
column carries, on a row with 1–4 peers with a value, a sentence saying the
report withholds that row's peer statistics — and it **annotates without
withholding**: the row's `peer_median`, `peer_25th`, `peer_75th` and
`vs_median` stay numeric. See *Thin peer cells*.)

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
2dp — in percentage points (`pp`), followed by the gap relative to the rendered
peer median (both since 0.3.2) and, since 0.3.4, the n it rests on. Round
`vs_median` yourself and the arithmetic on the page stops adding up. And since
0.3.4 the report prints **no** vs-median line at all when fewer than 5 peers have
a value for the metric. Executed this session (0.3.4, python3.12) on an
institution with an FDIC-published NIM of 4.3649 (`reported_nim=4.3649`, report
date 20241231, other fields as the first worked example) against a `PeerGroup`
(`min_peers=10`) of one peer, then of five identical peers, each with
`reported_nim=2.2473745332357096`:

```
--- 1 peer(s), each with NIM 2.2473745332357096 ---
  institution (raw) = 4.3649
  peer_median (raw) = 2.2473745332357096
  vs_median   (raw) = 2.11752546676429
  peer_count = 1
  report_withholds_peer_stats = The rendered report withholds this row's peer median, percentiles and vs-median: the group's one peer has a value for this metric, but 1 is below this tool's house minimum of 5. This row's peer_median, peer_25th, peer_75th and vs_median are computed over that 1 peer.
  an AI rounding summary_table to 2dp prints: 4.36 , 2.25 , 2.12
  ... and 4.36 - 2.25 = 2.11, NOT 2.12
  generate_report prints, for NIM:
    **Peer statistics:** withheld — the group's one peer has a value for this metric, but 1 is below this tool's house minimum of 5 for showing a median or percentiles.
--- 5 peer(s), each with NIM 2.2473745332357096 ---
  institution (raw) = 4.3649
  peer_median (raw) = 2.2473745332357096
  vs_median   (raw) = 2.11752546676429
  peer_count = 5
  report_withholds_peer_stats = None
  an AI rounding summary_table to 2dp prints: 4.36 , 2.25 , 2.12
  ... and 4.36 - 2.25 = 2.11, NOT 2.12
  generate_report prints, for NIM:
    **Peer Median:** 2.25% (n = 5 peers with a value for this metric)
    **vs Peer Median:** 2.11 pp above median (93.8% above) [n = 5 peers with a value]
    **Thin peer cell:** 5 of 5 peers have a value for this metric (this tool's house minimum for a peer group is 10); read the median and percentiles as indicative.
```

The raw figures are identical in both runs, and so is the rounding trap. What
differs is the report: at one peer it withholds the median and the vs-median
line and says so; at five it prints them with their n and flags the cell as
thin. The rule, true at every n:

- **First read `report_withholds_peer_stats` (or the report's Metric Detail).**
  If it is set, or `peer_count` is 0, the report shows no vs-median for that
  metric, and neither do you: no difference, rounded or raw (see *Thin peer
  cells*, below).
- **Then, if the first bullet did not apply, read `vs_median`.** If it is NaN,
  the institution has no value for the metric (meaning (1) of the N/A
  contract). Such a row has 5 or more peers with a value, so the report prints
  the peer median with its n but no **vs Peer Median:** line; you print no
  difference either: render it N/A.
- **Otherwise** (5 or more peers with a value, and an institution value), if
  you print a rounded difference, **compute it from the rounded operands** —
  `round(inst, 2) - round(median, 2)` — label it percentage points, not `%`,
  and give its n; or quote the report's own **vs Peer Median:** line, which
  the report prints on exactly such a row.

The package fixed the rounding on its report face and left `vs_median` exact on
purpose; it left it present on a withheld row on purpose too.

### Thin peer cells — reading rule (0.3.4)

The report computes each metric's peer statistics over the peers that **have a
value** for that metric, not over the group. A peer has no value when the metric
is undefined for it (a zero denominator), when a field was not reported, or when
this tool refused the published value. That per-metric count is
`BenchmarkResult.peer_count`, the `peer_count` column of `summary_table`, the
report's `Peers (n)` column, and the `[n = …]` at the end of every
**vs Peer Median:** line. It can be far below the group size. The report
withholds a metric's peer statistics below **5** peers with a value (this tool's
own minimum, HOUSE, `PEER_STAT_MIN_N` in `cdfibenchmark.data.schema`), and flags
5–9 as a **Thin peer cell:** (10 is `HOUSE_MIN_PEERS`). Read every row this way:

1. **When `report_withholds_peer_stats` is set for a row, quote it.** It is a
   string on rows with `0 < peer_count < 5` and `None` on every other row,
   including `peer_count == 0`. Quote it verbatim, or quote the report's
   **Peer statistics:** line for that metric.
2. **Never present or compute a peer median or percentile the report
   withheld.** `summary_table` still carries `peer_median`, `peer_25th`,
   `peer_75th` and `vs_median` on that row, computed over those 1–4 peers. Do
   not print them, do not compute your own from `compute_peer_metrics`, do not
   take a rank or percentile from `rank_institution` for that metric, and do
   not derive a vs-median, a rank or an "above/below peers" sentence from them.
   At `peer_count == 0` they are already absent; render N/A, as the report does.
3. **Never present any peer statistic without its n** — the metric's
   `peer_count`, not the group size. A loans-to-deposits median presented as
   "n = 19" when 7 of the 19 peers have a value (CERT 16583 at 20260630; see
   *Install*, above) is the error 0.3.4 fixed on its own page.
4. **At 5–9 peers with a value, say the comparison is thin.** Quote the
   report's **Thin peer cell:** line, or say in plain words that the median and
   percentiles rest on that few peers and are indicative only.

Status is unaffected by any of this: it never reads a peer value, so a grade on a
withheld row stands and is reported as usual.

### Output-presentation rules

- Show the metric, the institution value, the peer median (and 25th/75th when
  present) **only where the report shows them, each with its per-metric n**
  (see *Thin peer cells*), the package's own `status` label, and the row's
  **`basis`** — do not invent your own verdict language.
- **Render an absent value (NaN/None) as "N/A". Never fill it.** Never substitute
  a peer median, a zero, or a plausible number.
- **Never render a present-but-ungraded value as "not available."** Report the
  number, quote its `basis`, and quote the report's own `Not graded:` line.
- **A Tier 1 N/A with a value present and a `not_graded_reason` is a refusal,
  not a gap.** Quote the reason. Never grade it yourself against 8%, 9% or 5%.
- **Say where a threshold comes from.** Seven of the eight are `HOUSE`. Never let
  a house rule of thumb read as a regulatory standard.
- State the peer group basis (sample vs. live FDIC), the group size and each
  metric's `peer_count`, and render
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
- **Tier 1 refused for its report date or display** (0.3.3+) → `N/A` with
  `not_graded_reason`; quote it and do not invent a grade. Expected for every
  report date after 2026-09-22 (e.g. 20260930) under 0.3.4. Never swap in an
  older `report_date` silently to get a grade; offer it only as an explicitly
  different, older period.
- **cdfi-benchmark below 0.3.4 installed** → upgrade (`pip install -U
  "cdfi-benchmark>=0.3.4"`) before presenting any Tier 1 grade or peer statistic.
- **Name search** (`search_institutions(name=...)`) matches active institutions on
  substring; a zero-hit search on a valid name form is a legitimate empty result,
  not an error.

## Caveats

- Metrics are computed from **FDIC call-report data**; they reflect the reported
  `report_date` and FDIC's data quality, not an independent audit.
- Peer groups are **heuristic**: since 0.3.0 the package keeps the `max_peers`
  banks NEAREST the subject by asset distance out of a ±50% candidate window,
  pinned to one report date. A "peer" is a comparable-size FDIC bank, not a certified CDFI-only cohort
  and not a supervisory (UBPR) peer group. Quote `PeerGroup.selection_basis`
  rather than describing the rule from memory.
- `build_sample_peer_group` returns **synthetic** peers for demonstration; label
  any output built on it as illustrative, not a real peer comparison.
- **Read `basis` before presenting any metric** — see the basis rule above. A
  value on FDIC's published series is annualized at every report date; a value
  on the computed fallback is not graded by the package and must not be
  annualized by you. `nim`'s computed fallback is ungradeable at every period,
  including 12/31.
- **Peer groups can include uninsured, non-lending trust companies** (FDIC
  filers with `INSFDIC` 0, `BKCLASS` NC), which 0.3.4 does not exclude. They can
  distort peer medians — CERT 16583 at 20260630: Tier 1 peer median 87.19% over
  19 peers, 12 of them such trust companies (measured live this session). Check
  the peer list when a peer statistic looks implausible; see *Peer groups can
  include uninsured trust companies*.
- **A peer statistic rests on the peers with a value for that metric**, which
  can be far fewer than the group. Never present one without its n, and never
  present one the report withheld; see *Thin peer cells*.
- **The peer median can mix bases**, even when every peer shares a `report_date`
  — the package records this as a limitation (0.3.0, still unfixed in 0.3.4)
  and calls such a median a fabricated statistic. Say so when you present one.
- Seven of the eight thresholds are **HOUSE** rules of thumb, not standards; only
  `tier1_ratio` carries a citation. That citation is resolved per report date, is
  a comparison with the CBLR level for institutions that have **elected** the
  framework (election is not modelled), and is refused — not asserted — for
  dates before 2020-01-01, 2020-06-30 through 2021-12-31, after 2026-09-22,
  missing/malformed/non-quarter-end dates, and values that display as the level.
- **An FDIC-published basis is not a plausibility check.** A published ratio that
  is absurd on its face — a negative efficiency ratio, a three-digit ROAE, an
  earnings ratio on negative equity — is gradeable and grades `STRONG`. The
  package records this as a known limitation it did not fix
  (`data/schema.py:803`). Report the value; do not let the grade speak for it.
- **`generate_report`'s disclosures are conditional, not guaranteed.** Three of
  them require `peers` to be the `PeerGroup` object; two more require the data to
  trigger them. A plain `list` of the same peers renders a shorter report that
  reads as complete.
