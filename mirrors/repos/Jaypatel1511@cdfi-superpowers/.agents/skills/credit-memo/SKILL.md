---
name: credit-memo
description: >-
  Generate structured investment committee (IC) credit memos for CDFI loans,
  NMTC deals, equity investments, grants, and guarantees. Use when the user asks
  to "write a credit memo," "draft an IC memo," "prepare a deal memo," "generate
  a loan memo," or wants a structured underwriting write-up from deal inputs.
  Backed by the audited PyPI package credit-memo (import name `creditmemo`) —
  never fabricate financial figures, ratios, or impact metrics.
compatibility: >-
  Requires Python >=3.9 and pip with network access to pypi.org. The package
  itself imports nothing outside the standard library; the optional `[docx]`
  extra adds python-docx for Word output. No external API calls — every figure
  comes from user-supplied inputs.
---

# Credit Memo

Generates structured IC credit memos from deal data using the `credit-memo` PyPI
package instead of free-form prose. The package renders a fixed seven-section
memo (Executive Summary, Borrower Profile, Transaction Structure, Financial
Analysis, Impact Analysis, Risk Assessment, IC Recommendation) to Markdown or
Word, reproducing the caller's prose verbatim and computing only a handful of
derived figures from the caller's numbers.

## When to use

- "Write a credit memo for this $5M CDFI loan."
- "Draft an IC memo for our NMTC deal with Maple Street Grocery."
- "Generate a deal memo for this equity investment."
- "Prepare a loan write-up for the investment committee."
- "Create a credit memo for this grant / guarantee."

## When NOT to use

- NMTC eligibility lookups — that is `nmtc-eligibility`.
- NMTC transaction modeling or capital-stack structuring — that is `nmtc-calc`
  (see `references/package-index.md`), not this skill.
- Portfolio-level analysis, loan pricing, or stress testing — separate packages,
  not wrapped here.
- HMDA or fair-lending analysis — those are `hmda-analysis` (descriptive) and
  `fair-lending-screening` (inferential).
- Any memo where the user has not provided the deal inputs — this skill
  **collects** data from the user; it never invents it.

## Install

```
pip install "credit-memo>=0.2.2"
```

For Word (.docx) output:

```
pip install "credit-memo[docx]>=0.2.2"
```

`>=0.2.2` is load-bearing: 0.2.2 is the release whose memo *discloses* the four
NMTC inputs it discards (see "Known limitations"); 0.2.1 and below produce an
NMTC Structure table with nothing marking it partial.

Import name (dist name ≠ import name):

| dist | import |
|---|---|
| credit-memo | `creditmemo` |

## The no-fabrication rule (non-negotiable)

**Every number in the memo comes from the user's input or is a figure the
package derives from the user's input. NEVER fabricate, estimate, or "fill in"
a financial figure, impact metric, or risk factor.** If the user has not
provided a field, leave it unset (`None`) — do not guess. A credit memo with
invented numbers is worse than no memo: it presents fabricated data under a
structured format that implies it was underwritten.

This rule extends to:

- **Financial ratios** — DSCR, current ratio, debt-to-equity, and LTV are
  *inputs* (`FinancialData.dscr`, etc.), not computed by the package. If the
  user has not supplied a ratio, leave it `None`; the row renders `N/A`. Never
  hand-calculate one from the other figures.
- **Impact metrics** — jobs created/retained, units, patients, students. These
  are the user's projections, not yours. See the `jobs_*` trap below.
- **Risk factors** — category, severity, and mitigant come from the user's
  assessment. Do not invent risks, and do not downplay stated ones. An empty
  `risks` list renders "No risk factors were provided … it is not an assessment
  that no material risks exist" — leave it that way rather than padding.
- **Recommendation** — `approve`, `approve_conditions`, `table`, or `decline`
  is the user's (or their committee's) call. You may help articulate the basis,
  but never choose the recommendation.

**One exception:** you may suggest *categories* of information the user might
want to include ("do you have environmental risk factors to note?") — but never
fill them with assumed values.

## The recommendation rule (non-negotiable)

`DealProfile.recommendation` accepts exactly four values (matched
case-insensitively): `approve`, `approve_conditions`, `table`, `decline`.
**Never set a recommendation without the user explicitly choosing it**, and
never editorialize on whether the deal should be approved. The skill collects
and structures; the investment committee decides.

The package has **no dedicated recommendation-basis field** — the IC
Recommendation section renders the label and, for `approve_conditions`, the
numbered `conditions` list. Put the user's stated basis in `deal_summary`
(rendered as prose under Executive Summary), in the user's own words.

For `approve_conditions`, `conditions` must be enumerated — the package renders
them as "Subject to the following conditions:" — never a vague "subject to
standard conditions." An `approve_conditions` memo with an empty `conditions`
list is a defect; ask the user for the conditions.

## Core API

All imports from `creditmemo`:

```python
from creditmemo import (
    CreditMemo,
    DealProfile,
    BorrowerProfile,
    LoanTerms,
    NMTCTerms,
    FinancialData,
    ImpactData,
    RiskFactor,
    DEAL_TYPES, BORROWER_TYPES, SECTORS, RECOMMENDATIONS, SEVERITIES,
)
```

The five constants are the validated vocabularies. Every string enum is matched
case-insensitively and normalised to the canonical spelling; an unknown value
raises `ValueError` naming the allowed values.

| constant | allowed values |
|---|---|
| `DEAL_TYPES` | `loan`, `nmtc`, `equity`, `grant`, `guarantee` |
| `BORROWER_TYPES` | `nonprofit`, `for_profit`, `cdfi`, `government`, `cooperative`, `individual` |
| `SECTORS` | `affordable_housing`, `small_business`, `community_facility`, `healthcare`, `education`, `food_access`, `childcare`, `mixed_use`, `microenterprise`, `other` |
| `RECOMMENDATIONS` | `approve`, `approve_conditions`, `table`, `decline` |
| `SEVERITIES` | `High`, `Medium`, `Low` |

Note `for_profit` (underscore), not `for-profit`; a user's "for-profit" must be
mapped.

### BorrowerProfile

```python
BorrowerProfile(
    name: str,                    # required
    borrower_type: str,           # required — one of BORROWER_TYPES
    sector: str,                  # required — one of SECTORS
    state: str,                   # required — two-letter code
    city: str,                    # required
    year_founded: int | None = None,
    ceo_name: str | None = None,
    total_assets: float | None = None,
    annual_revenue: float | None = None,
    description: str | None = None,
    mission: str | None = None,
    website: str | None = None,
    is_cdfi_certified: bool | None = None,   # tri-state
    is_mdi: bool | None = None,              # tri-state
)
```

### LoanTerms

```python
LoanTerms(
    deal_type: str,               # required — one of DEAL_TYPES
    amount: float,                # required — dollars; must be > 0
    interest_rate: float | None = None,     # FRACTION: 4.5% is 0.045
    term_years: int | None = None,
    amortization_years: int | None = None,
    io_periods: int = 0,                    # interest-only months; 0 = row suppressed
    collateral: str | None = None,
    guarantor: str | None = None,
    use_of_proceeds: str | None = None,
    closing_date: str | None = None,
    maturity_date: str | None = None,
    min_dscr_covenant: float | None = None, # multiple: 1.20x is 1.20
    max_ltv: float | None = None,           # FRACTION: 80% is 0.80
    origination_fee_pct: float = 0.0,       # FRACTION; 0.0 = row suppressed
)
```

There is no `seniority`, `covenants`, or `nmtc_terms` on `LoanTerms`. Seniority
belongs in the `collateral` string ("First lien on …"); covenants beyond DSCR
and LTV go in `deal_summary`; NMTC terms go on `DealProfile.nmtc_terms`.

### NMTCTerms (NMTC deals only — attach to `DealProfile.nmtc_terms`)

```python
NMTCTerms(
    nmtc_allocation: float,       # required — dollars (the QEI)
    credit_price: float,          # required — $ of investor equity per $1 of credit: 0.81
    leverage_loan_rate: float,    # required — FRACTION — NOT RENDERED (see limitations)
    qlici_a_rate: float,          # required — FRACTION — NOT RENDERED
    qlici_b_rate: float,          # required — FRACTION — NOT RENDERED
    cde_fee_rate: float,          # required — FRACTION: 6% is 0.06
    cde_name: str | None = None,
    investor_name: str | None = None,
    compliance_years: int = 7,    # NOT RENDERED
)
```

Derived properties the memo renders: `total_nmtcs` (= allocation × 0.39),
`investor_equity` (= total_nmtcs × credit_price), `net_subsidy`
(= investor_equity − allocation × cde_fee_rate). The three required rate fields
are accepted and then discarded — you must still supply the user's real values,
never placeholders, because a later release will render them.

### FinancialData

```python
FinancialData(
    revenue_y1: float | None = None,      # OLDEST year — renders under "Year -2"
    revenue_y2: float | None = None,      # renders under "Year -1"
    revenue_y3: float | None = None,      # MOST RECENT — renders under "Most Recent"
    net_income_y1/y2/y3, ebitda_y1/y2/y3: float | None = None,   # same ordering
    total_assets: float | None = None,
    total_liabilities: float | None = None,
    net_assets_equity: float | None = None,
    cash: float | None = None,
    dscr: float | None = None,            # multiple: 1.35x is 1.35
    current_ratio: float | None = None,   # multiple
    debt_to_equity: float | None = None,  # multiple
    ltv: float | None = None,             # PERCENTAGE POINTS: 75% is 75.0 — a
                                          # fraction in (0, 1.0] raises ValueError
    projected_revenue_y1: float | None = None,
    projected_dscr_y1/y2/y3: float | None = None,
)
```

**`_y1` is the oldest year and `_y3` the most recent.** The field names do not
say so; the rendered table does (`Year -2 | Year -1 | Most Recent`). Map the
user's "most recent year revenue" to `revenue_y3`. Getting this backwards
inverts the revenue-trend sentence the memo writes.

**Scale trap:** `FinancialData.ltv` is the one percentage-point field in the
package. `interest_rate`, `max_ltv`, `origination_fee_pct`, and every
`NMTCTerms` rate are fractions. Passing `ltv=0.75` raises; passing
`max_ltv=75.0` renders "Maximum LTV of 7500.0%" without complaint.

All fields optional — pass what the user provides. A `None` ratio renders as
`N/A` in the Key Credit Metrics table; a `None` dollar figure renders `N/A` in
its table cell, and sub-tables with nothing to show are omitted. **Never fill a
`None` with a guess.**

### ImpactData

```python
ImpactData(
    jobs_created: int = 0,            # NOT optional — 0 RENDERS as "0" (see trap)
    jobs_retained: int = 0,           # NOT optional — 0 RENDERS as "0"
    affordable_units: int = 0,        # 0 = row suppressed
    sq_ft_community_space: float = 0.0,
    patients_served: int = 0,
    students_served: int = 0,
    businesses_supported: int = 0,
    is_low_income_area: bool | None = None,     # tri-state
    is_nmtc_eligible: bool | None = None,       # tri-state
    is_opportunity_zone: bool | None = None,    # tri-state
    is_minority_borrower: bool | None = None,   # tri-state
    is_women_borrower: bool | None = None,      # tri-state
    census_tract: str | None = None,
    impact_narrative: str | None = None,
)
```

**The `jobs_*` trap.** `jobs_created` and `jobs_retained` default to `0` and
are *not* suppressed on zero: an `ImpactData` nobody filled in tells the IC the
deal creates zero jobs and retains zero jobs, and the derived **Cost per Job**
(= loan amount ÷ (created + retained)) is computed from whatever is there —
filling one field and not the other inflates it by the missing share. **Ask the
user for both values on every deal and set both explicitly.** If the user does
not know, say so in `impact_narrative` in their words; a `0` in those rows reads
as "either zero or not stated," and the package cannot tell the two apart until
0.3.0.

**Tri-state flags:** `True` renders ✅, `False` renders ❌ ("Not a Low-Income
Area"), `None` is omitted. `None` means "not determined," not "no." If the user
has run `nmtc-eligibility`, carry its result through faithfully — including a
`None` from an unresolved address. If eligibility has not been checked, leave
`is_nmtc_eligible=None`; do not assume.

### RiskFactor

```python
RiskFactor(
    category: str,                # required — short label, e.g. "Revenue concentration"
    description: str,             # required
    severity: str,                # required — High | Medium | Low (case-insensitive)
    mitigant: str,                # required (singular) — how the risk is addressed
)
```

All four are required. If the user has a risk with no mitigant, ask; do not
write one for them, and do not write "None identified" unless the user says so.
Risks render grouped by severity.

### DealProfile (the top-level container)

```python
DealProfile(
    deal_name: str,                       # required
    borrower: BorrowerProfile,            # required
    loan_terms: LoanTerms,                # required
    financial_data: FinancialData,        # required — FinancialData() if nothing supplied
    impact_data: ImpactData,              # required — see the jobs_* trap
    recommendation: str,                  # required — one of RECOMMENDATIONS
    prepared_by: str,                     # required
    prepared_date: str,                   # required — ISO format preferred
    nmtc_terms: NMTCTerms | None = None,  # required in practice when deal_type == "nmtc"
    risks: list[RiskFactor] = [],
    conditions: list[str] = [],           # rendered for approve_conditions
    fund_name: str | None = None,         # None renders "Fund: N/A"
    ic_date: str | None = None,           # None renders "IC Date: TBD"
    deal_summary: str | None = None,      # free prose under Executive Summary
)
```

**Required strings are not validated.** `deal_name=None` or `prepared_by=" "`
raises nothing and reaches the memo as `None` / blank. Always supply real values
for `deal_name`, `prepared_by`, `prepared_date`, and the five required
`BorrowerProfile` strings.

### CreditMemo (generator)

```python
memo = CreditMemo(deal)          # TypeError if deal is not a DealProfile
md_text = memo.to_markdown()     # Markdown string
memo.save_markdown("memo.md")
memo.save_docx("memo.docx")      # ImportError without python-docx
memo.preview(lines=50)           # prints the first N lines
memo.section_count()             # always 7 — the renderer's fixed section tuple
```

## Workflow — how to use this skill

1. **Collect deal information from the user.** At minimum: deal name, borrower
   name / type / sector / city / state, deal type, amount, the recommendation,
   who prepared it, and the date. Ask for `jobs_created` and `jobs_retained`
   explicitly. For NMTC deals also collect allocation, credit price, CDE fee
   rate, and the three rates the package requires.

2. **Construct the data classes** from user-supplied values, mapping units
   carefully: "4.5% interest" → `interest_rate=0.045`; "75% LTV" → `ltv=75.0`;
   "max 80% LTV covenant" → `max_ltv=0.80`; "$3.2M revenue last year" →
   `revenue_y3=3_200_000`; "for-profit" → `borrower_type="for_profit"`.

3. **Generate the memo.** `CreditMemo(deal).to_markdown()` is always
   available; `.save_docx()` needs the `[docx]` extra.

4. **Present the result.** Show the Markdown to the user. Offer Word export.

5. **Iterate.** If the user wants changes, update the data classes and
   regenerate — do not hand-edit the Markdown output.

## Worked example — CDFI term loan (run against 0.2.2)

```python
from creditmemo import (
    CreditMemo, DealProfile, BorrowerProfile,
    LoanTerms, FinancialData, ImpactData, RiskFactor,
)

borrower = BorrowerProfile(
    name="Sunrise Community Health Center",
    borrower_type="nonprofit",
    sector="healthcare",
    state="CO",
    city="Greeley",
    year_founded=1973,
    annual_revenue=42_000_000,
    mission="Providing accessible healthcare to underserved communities",
)

terms = LoanTerms(
    deal_type="loan",
    amount=2_500_000,
    interest_rate=0.045,
    term_years=10,
    amortization_years=25,
    collateral="First lien on clinic facility at 123 Main St, Greeley CO",
    use_of_proceeds="Clinic expansion",
    min_dscr_covenant=1.20,
    max_ltv=0.80,
)

financials = FinancialData(
    revenue_y1=35_200_000,      # two years prior  -> "Year -2"
    revenue_y2=38_500_000,      # prior year       -> "Year -1"
    revenue_y3=42_000_000,      # most recent      -> "Most Recent"
    net_income_y1=950_000,
    net_income_y2=1_200_000,
    net_income_y3=1_800_000,
    total_assets=28_000_000,
    total_liabilities=12_000_000,
    cash=3_500_000,
    dscr=1.85,                  # user-supplied, not computed
    ltv=62.5,                   # percentage points
)

impact = ImpactData(
    jobs_created=15,
    jobs_retained=450,          # both set explicitly — see the jobs_* trap
    patients_served=2_000,
    is_low_income_area=True,
    is_nmtc_eligible=True,      # carried through from nmtc-eligibility
    census_tract="08123001500",
    impact_narrative="Expands primary care capacity by 30%; adds a dental "
        "clinic serving 2,000 additional patients/year; located in a "
        "medically underserved area (HPSA score 18).",
)

risks = [
    RiskFactor(
        category="Revenue concentration",
        description="68% Medicaid/Medicare reimbursement",
        severity="Medium",
        mitigant="Diversifying payer mix; grant funding covers 15% of operations",
    ),
    RiskFactor(
        category="Construction",
        description="Construction risk on facility expansion",
        severity="Low",
        mitigant="Fixed-price GMP contract with bonded general contractor",
    ),
]

deal = DealProfile(
    deal_name="Sunrise Community Health — Clinic Expansion",
    borrower=borrower,
    loan_terms=terms,
    financial_data=financials,
    impact_data=impact,
    recommendation="approve_conditions",
    prepared_by="CDFI Lending Team",
    prepared_date="2026-09-21",
    risks=risks,
    conditions=[
        "Receipt of executed GMP construction contract",
        "Lender's title policy in the loan amount",
    ],
    deal_summary="$2.5M senior secured loan to finance expansion of primary "
        "care and dental clinic capacity in a medically underserved area. "
        "Basis for recommendation (per lending team): growing revenue trend, "
        "50+ year operating history, adequate collateral coverage.",
)

memo = CreditMemo(deal)
print(memo.to_markdown())
memo.save_markdown("sunrise_health_memo.md")
```

What 0.2.2 renders from this (abridged): a header block (`Fund: N/A`,
`IC Date: TBD` because neither was supplied); **APPROVE SUBJECT TO CONDITIONS**
with the two conditions; a Deal Summary table (`$2,500,000 ($2.50MM)`,
`4.50%`, `10 years`); the Historical Financial Summary with the three revenue
columns and the sentence *"Revenue, Year -2 vs Most Recent: Higher — Most Recent
revenue of $42.00MM is higher than Year -2 revenue of $35.20MM"*; Key Credit
Metrics with `1.85x` DSCR against a `>= 1.25x` benchmark and `62.5%` LTV against
`<= 80%`; Impact metrics with `Total Jobs 465` and a derived
`Cost per Job $5,376.34`; ✅ Low-Income Area / ✅ NMTC Eligible Census Tract; the
two risks in Medium and Low tables; and a signature block. Footer:
`Generated by credit-memo 0.2.2`.

## Worked example — NMTC deal

```python
from creditmemo import DealProfile, LoanTerms, NMTCTerms

terms = LoanTerms(
    deal_type="nmtc",
    amount=8_500_000,
    interest_rate=0.02,
    term_years=7,
    collateral="Assignment of QLICI note",
)

nmtc = NMTCTerms(
    nmtc_allocation=10_000_000,
    credit_price=0.73,
    leverage_loan_rate=0.05,    # required; not rendered in 0.2.2
    qlici_a_rate=0.02,          # required; not rendered
    qlici_b_rate=0.01,          # required; not rendered
    cde_fee_rate=0.05,
    cde_name="Dayton CDE",
    investor_name="Big Bank CDC",
)

deal = DealProfile(..., loan_terms=terms, nmtc_terms=nmtc, ...)
```

0.2.2 renders an **NMTC Structure** table — QEI `$10.00MM`, Total NMTCs (39%)
`$3.90MM`, Credit Price `$0.73/$1`, Investor Equity `$2.85MM`, CDE Fee `5.0%`,
Estimated Net Subsidy `$2.35MM`, CDE, Tax Credit Investor — followed by the
package's own disclosure line: *"This table does not show every NMTC input the
package accepts: the leverage loan rate, the QLICI A rate, the QLICI B rate and
the compliance period are accepted by NMTCTerms and appear nowhere in this
memo, in either format. Add them by hand if the Committee needs them."* Relay
that line to the user; do not delete it.

## Known limitations (0.2.2)

These are package-level, disclosed in the package's own README. Do not work
around them by hand-editing the output; tell the user.

- **Four NMTC inputs do not reach the memo:** `leverage_loan_rate`,
  `qlici_a_rate`, `qlici_b_rate`, `compliance_years`. Three of them are
  required constructor arguments. The memo says so beneath the NMTC table.
  For an NMTC deal the QLICI rates and the 7-year compliance period are core
  terms — the user must add them to the memo by hand. Top item for 0.3.0.
- **The QLICI interest rate is rendered as a standard "Interest Rate"** in the
  Deal Summary / Proposed Terms tables, with no NMTC-specific labeling.
- **The "Benchmark" column** in Key Credit Metrics (`>= 1.25x` DSCR,
  `>= 1.0x` current ratio, `< 3.0x` debt-to-equity, `<= 80%` LTV) is a set of
  package defaults with no cited source. If the user asks, say so — they are
  not cited industry standards, and the memo does not compare against them in
  prose.
- **Ratios, rates and the credit price round a small non-zero to zero:**
  `dscr=0.001` renders `0.00x`, `cde_fee_rate=0.0001` renders `0.0%`. Ordinary
  values (`1.02` → `1.02x`) render as written. The one that bites on a real
  deal is `cde_fee_rate` at one decimal: 2.04% and 2.0% render identically.
- **`jobs_created` / `jobs_retained` cannot express "not stated"** (see the
  trap above); the five other counters are suppressed on `0` and so cannot
  express "checked, and it is zero."
- **Required strings are not validated** — `None` reaches the memo as the
  word `None`.
- **`revenue_y1` is the oldest year**, and only the rendered column headings
  say so.
- **Release process:** credit-memo's GitHub Actions workflow runs tests only
  and does not publish; the version on PyPI is the authority for what is
  released.

## Output-presentation rules

- **Always present the generated Markdown** before offering Word export.
- **Never hand-edit the generated memo.** Update the data classes and
  regenerate.
- **Relay the package's own disclosure lines** (NMTC table footnote, "No risk
  factors were provided …") verbatim rather than removing them.
- **If the user provides partial information**, generate with what you have
  and say which sections are thin. Do not pad.
- **For Word export**, `save_docx()` raises `ImportError` without
  `python-docx`; install the `[docx]` extra and retry.

## Failure modes

- **`ValueError: <field> must be one of [...]`** — a vocabulary miss
  (`"for-profit"`, `"critical"` severity, `"approved"`). Map to the canonical
  value; do not widen the vocabulary.
- **`ValueError: ltv must be in percentage points, not a fraction`** — you
  passed `ltv=0.75`; pass `75.0`.
- **`ValueError: amount must be positive`** — `LoanTerms.amount <= 0`.
- **`TypeError` on `CreditMemo(...)`** — argument is not a `DealProfile`.
- **`TypeError: missing required argument`** on a dataclass — `RiskFactor`
  needs all four fields; `NMTCTerms` needs six; `DealProfile` needs
  `recommendation`, `prepared_by`, `prepared_date`.
- **`ImportError` on `save_docx()`** — install `credit-memo[docx]`.
- **Sparse memo** — too few fields. Ask the user; do not invent.

## Caveats

- This is a **memo generation tool**, not an underwriting engine. It structures
  the user's inputs; it does not analyze creditworthiness or make lending
  recommendations. The only figures it computes are Total Jobs, Cost per Job,
  the revenue-trend sentence, and the three NMTC derived amounts — all from
  user inputs.
- All financial data, impact projections, and risk assessments in the memo are
  **the user's assertions**, structured by the package.
- The recommendation is **the user's stated recommendation**, not an
  algorithmic output.
- Word output requires the optional `python-docx` dependency.

---

**Last verified:** 2026-09-21 against `credit-memo 0.2.2` from PyPI (installed
with `[docx]`; both worked examples executed; output quoted above is what the
package rendered).
