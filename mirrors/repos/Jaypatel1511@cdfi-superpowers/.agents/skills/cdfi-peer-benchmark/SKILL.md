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
  banks.data.fdic.gov (FDIC BankFind — institutions and call reports). That
  source covers FDIC-insured institutions only, which is why the skill benchmarks
  bank CDFIs and refuses credit unions and unregulated loan funds.
---

# CDFI Peer Benchmark

Benchmarks a **bank CDFI** against peers using FDIC BankFind call-report data,
via the published, audited **cdfi-benchmark** package. Renders results faithfully:
where the package returns NaN/None/`N/A`, the AI reports N/A — it never fills a
number.

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

## Install

```
pip install "cdfi-benchmark>=0.2.1"
```

Verified this session: **cdfi-benchmark 0.2.1** (PyPI).

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

## The NaN-not-fabrication contract (non-negotiable)

The package returns **NaN** for any metric it cannot compute (e.g. a missing
call-report field), and labels its status **`N/A`**. The AI must render that as
"N/A" / "not available" and **never** substitute a peer median, a zero, or a
plausible-looking number. A fabricated capital ratio in a benchmark is exactly
the failure this contract exists to prevent.

## The period-basis rule (non-negotiable)

**NIM, ROAA, and ROAE are not annualized at interim report dates.** Disclosed verbatim in
`cdfi-benchmark` 0.2.1 `CHANGELOG.md`, "Known issues":

> **Annualization / period basis (D4) is deferred to 0.3.0.** NIM, ROAA, and
> ROAE are computed from as-reported YTD flows without annualizing interim
> periods, so non-Q4 figures are not annualized. The decision (adopt the FDIC
> precomputed `NIMY` / `ROA` / `ROE` fields) is made and lands in 0.3.0; it is
> intentionally out of scope for this field-semantics release.

Each of these three divides a **year-to-date flow** by a **point-in-time stock**, so at an interim
`report_date` the numerator covers part of a year while the denominator does not. A 3/31 date reads
roughly **4× low**, 6/30 roughly **2× low**, 9/30 roughly **1.33× low**. Only a **12/31**
`report_date` is correct as reported.

The other five metrics — Efficiency Ratio, Tier 1 Leverage Ratio, Loans-to-Deposits, Non-Performing
Loan Ratio, Loan Loss Reserve Coverage — are ratios of same-period flows or of stocks to stocks, and
are **not** affected.

Rules:

- **Read `report_date` before presenting NIM, ROAA, or ROAE.** If it is not a 12/31 date, say so in
  the same breath as the number: these are un-annualized YTD figures, understated for the period.
- **Do not annualize them yourself.** Multiplying by four turns a package-reported figure into one
  you invented, and the correct fix (the FDIC precomputed `NIMY` / `ROA` / `ROE` fields) is a
  different computation, not a scalar. Report what the package returned, labeled.
- **Distinguish the relative read from the level read.** If the institution and every peer share the
  same `report_date`, they carry the same period scaling, so "above / below the peer median"
  survives an interim date — the *magnitude* still does not. **Verify the peer `report_date`s match
  the institution's before relying on even the relative read.** A subject at 3/31 compared against
  peers at 12/31 is un-annualized against annualized, and distorts the comparison in the same ~4×
  direction. State which claim you are making, and say whether the dates matched.
- If the user asks for an annualized figure, say the package does not produce one yet and that it
  lands in `cdfi-benchmark` 0.3.0 — do not compute it.

## Worked example — full benchmark flow (executed)

The pipeline is: `get_financials(cert)` → build a peer group →
`benchmark_institution(...)` → `summary_table(...)`.

`build_sample_peer_group(institution)` generates a deterministic synthetic peer
set — good for a reproducible demo without a second live FDIC round-trip. For a
real analysis use `build_peer_group(institution, ...)` (live FDIC peers).

```python
import pandas as pd
import cdfibenchmark as c
from cdfibenchmark import InstitutionProfile

inst = InstitutionProfile(
    cert=99999, name="Example Community Bank", city="Anytown", state="RI",
    report_date="2024-12-31", total_assets=250_000_000, total_deposits=210_000_000,
    net_loans=170_000_000, net_income=2_500_000, interest_income=9_800_000,
    interest_expense=2_100_000, non_interest_income=1_200_000,
    non_interest_expense=6_400_000, total_equity=28_000_000, tier1_ratio=11.5,
    gross_loans=172_000_000, non_current_loans=1_500_000, loan_loss_allowance=2_000_000,
)
peers = c.build_sample_peer_group(inst)          # 20 synthetic peers, deterministic
st = c.summary_table(inst, peers)
print(st.to_string(index=False))
```

Actual output this session:

```
                     metric  institution  peer_median  peer_25th  peer_75th  vs_median   status  peer_count
  Net Interest Margin (NIM)     3.080000     3.010296   2.804187   3.259659   0.069704 ADEQUATE          20
           Efficiency Ratio    71.910112    70.624617  64.647189  80.842358   1.285495 ADEQUATE          20
Return on Avg Assets (ROAA)     1.000000     0.940811   0.717540   1.072620   0.059189   STRONG          20
Return on Avg Equity (ROAE)     8.928571     8.030005   6.523744  10.491227   0.898566 ADEQUATE          20
      Tier 1 Leverage Ratio    11.500000    12.830947  10.664911  14.552562  -1.330947   STRONG          20
          Loans-to-Deposits    80.952381    82.661433  68.312007  91.397624  -1.709052   STRONG          20
  Non-Performing Loan Ratio     0.872093     1.555798   1.139816   2.220471  -0.683705   STRONG          20
 Loan Loss Reserve Coverage   133.333333    80.408055  58.106357 122.518310  52.925278   STRONG          20
```

Note the `report_date` is **2024-12-31**. That is the one period basis at which NIM, ROAA, and ROAE
need no annualization — this example is deliberately Q4 and is **not** evidence that interim dates
are safe. At a 3/31, 6/30, or 9/30 date those three rows require the period-basis disclosure above.

## Worked example — the NaN contract in action (executed)

Same peer group, but the institution is missing `total_equity` (so ROAE and the
Tier 1 ratio cannot be computed):

```python
inst2 = InstitutionProfile(
    cert=99998, name="Missing-Data Bank", city="X", state="RI",
    report_date="2024-12-31", total_assets=250_000_000, total_deposits=210_000_000,
    net_loans=170_000_000, net_income=2_500_000, interest_income=9_800_000,
    interest_expense=2_100_000, non_interest_income=1_200_000,
    non_interest_expense=6_400_000, total_equity=None, tier1_ratio=None,
    gross_loans=172_000_000, non_current_loans=1_500_000, loan_loss_allowance=2_000_000,
)
st2 = c.summary_table(inst2, peers)
print(st2[["metric", "institution", "status"]].to_string(index=False))
```

Actual output this session:

```
                     metric  institution   status
  Net Interest Margin (NIM)     3.080000 ADEQUATE
           Efficiency Ratio    71.910112 ADEQUATE
Return on Avg Assets (ROAA)     1.000000   STRONG
Return on Avg Equity (ROAE)          NaN      N/A
      Tier 1 Leverage Ratio          NaN      N/A
          Loans-to-Deposits    80.952381   STRONG
  Non-Performing Loan Ratio     0.872093   STRONG
 Loan Loss Reserve Coverage   133.333333   STRONG
```

Present the ROAE and Tier 1 rows as **N/A** exactly as the package does. Do not
back-fill them from the peer median.

## Live FDIC path (verified working)

- `c.search_institutions(state="RI", limit=5)` → DataFrame of FDIC banks
  (verified this session).
- `c.get_financials(cert)` → an `InstitutionProfile` populated from FDIC call
  reports (`get_financials(cert, report_date=None, limit=4)`).
- `c.build_peer_group(inst, same_state=False, asset_tolerance=0.5, min_peers=10,
  max_peers=50)` → live peer `InstitutionProfile` list.
- `c.get_institution(cert)` returns a **raw FDIC dict** (not an
  `InstitutionProfile`); a nonexistent cert returns **`None`**, not an error.

Data source: `banks.data.fdic.gov` (FDIC BankFind API) — no cloud WAF; verified
reachable this session.

## Typed errors — report, don't smooth over

The package raises **typed** exceptions; surface them, don't swallow them:

| exception | subclass of | fires on |
|---|---|---|
| `FDICAPIError` | `CDFIBenchmarkError` | FDIC API transport/HTTP failure |
| `FDICResponseError` | `CDFIBenchmarkError` | malformed/unexpected FDIC response |
| `CDFIBenchmarkError` | `Exception` | package base error |

Hierarchy verified this session (`FDICAPIError.__mro__` and
`FDICResponseError.__mro__` both include `CDFIBenchmarkError`). When one is
raised, report the error type and message; do not fall back to fabricated
numbers or a cached guess.

```python
from cdfibenchmark import FDICAPIError, FDICResponseError
try:
    inst = c.get_financials(cert)
except (FDICAPIError, FDICResponseError) as e:
    # report: type(e).__name__ and str(e). Do NOT fabricate metrics.
    ...
```

## Output-presentation rules

- Show the metric, the institution value, the peer median (and 25th/75th when
  present), and the package's own `status` label — do not invent your own
  verdict language.
- Render every NaN/None/`N/A` cell as "N/A". Never fill it.
- State the peer group basis (sample vs. live FDIC) and `peer_count`.
- If any typed FDIC error occurred, report it instead of a partial table.

## Failure modes

- **Credit union / loan fund requested** → decline (not FDIC-covered).
- **Nonexistent cert** → `get_financials`/`get_institution` return `None`; report
  "institution not found," don't proceed with an empty profile.
- **FDIC API down / malformed** → `FDICAPIError` / `FDICResponseError`; report it.
- **Missing call-report field** → NaN + `N/A` status; render as N/A.
- **Name search** (`search_institutions(name=...)`) matches active institutions on
  substring; a zero-hit search on a valid name form is a legitimate empty result,
  not an error.

## Caveats

- Metrics are computed from **FDIC call-report data**; they reflect the reported
  `report_date` and FDIC's data quality, not an independent audit.
- Peer groups are **heuristic** (asset-band / state filters); a "peer" is a
  comparable-size FDIC bank, not a certified CDFI-only cohort.
- `build_sample_peer_group` returns **synthetic** peers for demonstration; label
  any output built on it as illustrative, not a real peer comparison.
- **NIM, ROAA, and ROAE are un-annualized YTD figures at any interim `report_date`** — see the
  period-basis rule above. Only a 12/31 `report_date` is annualized as reported. Every other metric
  in the summary table is period-consistent.
