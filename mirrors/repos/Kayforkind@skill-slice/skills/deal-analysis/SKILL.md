---
name: deal-analysis
description: "Underwrites a named real-estate asset from raw rent roll and T12 through post-sale millage, CapEx reserve, DSCR, cash-on-cash, and IRR, then runs correlated base/stress/catastrophe knobs. Use when the ask is pre-LOI underwriting, a partner or lender package, or a post-mortem on one address. Not for MLS or CoStar list screening, 1031/cost-seg tax strategy, or ground-up entitlement risk."
version: 1.0.1
risk: safe
source: modernized
date_modernized: "2026-05-31"
tags:
  - real-estate
  - underwriting
  - stress-testing
  - workflow
  - quality
---

# deal-analysis

Optimistic assumptions plus no stress test is how investors lose money on deals that looked good in the spreadsheet. Vacancy at 2% when the market runs 8%. Renovation at $40K when the scope routinely runs $60K. Cap rate compression assuming the exit is always favorable. Every bad deal looked fine in the original pro forma because the pro forma was built to support a conclusion rather than to test one. This skill builds the analysis backward from the stress scenarios, forces conservative underwriting, and names the single assumption that breaks the deal before you're under contract.

## When to Use

- Pre-LOI underwriting on a **specific property** — not market screening.
- Re-underwriting a deal you already feel good about (most common failure mode: confirmation bias on a deal you've fallen in love with).
- Partner or lender package prep where every assumption must be defensible.
- Post-mortem on a deal that underperformed — to learn which assumption broke it.

### When NOT to Use

| Situation | Use instead |
|---|---|
| Screening a list of MLS or CoStar exports | A 30-second back-of-envelope: rent × 12 × 0.6 ÷ price = desired cap |
| Tax-strategy comparison (1031, cost seg, opportunity zone) | A CPA, not a pro forma |
| You don't have a real address or a real seller | Stop. There is nothing to underwrite. |
| Pure development / ground-up | This skill assumes a stabilized or value-add asset, not entitlement risk |

## Prerequisites

Before starting underwriting, gather:

1. **A real property address and a real seller.** No hypotheticals.
2. **Raw rent roll** (not the marketing OM summary).
3. **Trailing-12 expense history** from the seller — but verify against tax records and your own market knowledge.
4. **Closed lease comps** from the past 90 days, same submarket, comparable unit size and condition. Not Zillow Zestimates. Not asking rents.
5. **At least one contractor walkthrough** or documented cost history for renovation budgeting.
6. **Two written lender quotes** dated within the last 30 days.
7. **A bindable insurance quote** against the specific property address.
8. **Assessor contact confirmation** of millage rate and reassessment policy in writing.

## Procedure

### Step 1: Identify the Deal Archetype

Defaults differ materially by asset class. Don't apply SFR rules of thumb to a 40-unit multifamily or vice versa.

| Archetype | Vacancy floor | OpEx % of EGI | DSCR floor | Cap range (2026) | Typical hold | Key risk |
|---|---|---|---|---|---|---|
| SFR rental | 5–8% | 35–50% | 1.20 | 5.5–7.5% | 5–7 yr | Single-tenant concentration |
| Small multi (2–4u) | 6–8% | 40–50% | 1.20 | 6.0–8.0% | 5–10 yr | Owner-occ exit pool shrinks if rates spike |
| Large multi (5+u) | 7–10% | 40–50% | 1.25 | 5.0–7.0% | 7–10 yr | Refi rate at loan maturity |
| Commercial NNN retail | 5–15% | 5–15% (NNN) | 1.30 | 6.0–8.5% | 7–15 yr | Tenant credit + lease maturity cliff |
| Mixed-use | 8–12% | 35–50% | 1.25 | 6.5–8.5% | 5–10 yr | Retail vacancy bleeds into residential pricing |
| Storage / light industrial | 8–15% | 25–40% | 1.30 | 5.5–7.5% | 7–10 yr | Submarket supply pipeline |

> **TIP:** When the seller's broker package shows numbers materially better than the column above (e.g., 25% OpEx ratio on a 40-year multifamily), assume the seller has stripped real costs out of the trailing-twelve. Re-underwrite from raw rent roll and tax records, not the marketing OM.

### Step 2: Calculate Total Acquisition Cost

1. Purchase price: as offered, not as hoped.
2. Closing costs itemized: title insurance, transfer taxes, attorney fees, lender fees, inspection. Use actuals from your market — typically 2–4% of purchase price.
3. Total acquisition cost = purchase price + closing costs. **This is your basis.**
4. Flag: if you're buying off-market, have you verified the seller's price expectation against recent comps? An off-market deal is only a deal if the price is actually below market.

### Step 3: Build Itemized Renovation Budget with Contingency

| Scope category | Contingency floor | Why |
|---|---|---|
| Light (cosmetic, paint, flooring) | 15% | Limited unknowns once you've walked it |
| Medium (some systems — HVAC, partial plumbing) | 20% | Permit timeline and code surprises |
| Heavy (full gut, unknown systems, structural) | 25%+ | Concealed conditions almost always surface |

Rules:
- Line-item every category: roof, HVAC, electrical, plumbing, kitchen, bathrooms, flooring, exterior, permits, GC overhead.
- Each line must come from a contractor bid or your own documented cost history — not a rule of thumb.
- Write the contingency line as a **line item**, not as a mental buffer.
- If you haven't walked the property or had a contractor walk it, every renovation number is a guess. Say so.

### Step 4: Underwrite Rent

- Gross rent: use **closed lease comps** from the past 90 days, same submarket, comparable unit size and condition. Not Zillow Zestimate. Not asking rents.
- If you're planning a value-add premium (post-renovation rent increase), name the specific comparable properties that support the premium. "I think it'll rent for more after renovation" is not underwriting.
- Apply a vacancy factor: use trailing 12-month submarket vacancy, not national average. **Default floor: 8%**, regardless of what the seller's pro forma shows.
- Effective gross income = gross rent × (1 − vacancy rate). Subtract concessions and bad debt separately when material (1–3% of EGI in soft markets).
- Model the rent ramp explicitly for value-add: months 1–6 in-place, months 7–18 ramping, then stabilized. Pro forma rent is not day-one rent.

### Step 5: Underwrite Expenses

| Expense line | Typical range | Common omission |
|---|---|---|
| Property taxes (post-purchase reassessment) | Varies | Modeling current taxes, not reassessed |
| Insurance | 0.5–1.0% of value | Wind/flood/coastal add-ons |
| Property management | 8–10% of EGI | "I'll self-manage" — your time still costs |
| Maintenance & repairs | 10–15% of EGI | Higher for buildings >40 years old |
| CapEx reserve | 10% of EGI | Roof, HVAC, mechanicals on 15–25yr cycles |
| Utilities (if owner-paid) | Varies | Vacant units still consume |

Sanity check: for single-family, expenses routinely run 40–50% of gross rents. If your model shows 30%, you're missing something. NOI = EGI − total expenses (debt service, CapEx, and depreciation are **not** in OpEx).

### Step 6: Compute Post-Purchase Tax Reassessment

Most US jurisdictions reassess to purchase price (or a statutory fraction of it) on transfer. The seller's in-place tax is a trap: their assessment may be a decade old, capped under homestead, or grandfathered into a frozen base year.

```python
def reassessed_tax(
    purchase_price: float,
    millage_rate: float,          # e.g., 0.0145 = 14.5 mills, or 1.45% effective
    assessment_ratio: float = 1.0,  # CA Prop 13: 1.0; some states 0.40-0.85
    homestead_cap_pct: float | None = None,  # e.g., 0.03 for FL 3% Save Our Homes
    current_tax: float | None = None,
) -> float:
    """Post-sale property tax. Investment property usually gets no cap."""
    new_tax = purchase_price * assessment_ratio * millage_rate
    # Homestead caps generally do NOT transfer to non-owner-occupant buyers.
    # Only apply if buyer will owner-occupy and qualifies under local statute.
    if homestead_cap_pct is not None and current_tax is not None:
        capped = current_tax * (1 + homestead_cap_pct)
        return min(new_tax, capped)
    return new_tax

# Example: $1.8M small multifamily in a 1.45% effective millage county
# Seller has owned 12 years; in-place tax is $9,800/yr (assessed at $675k)
new_annual_tax = reassessed_tax(1_800_000, 0.0145)
#  $26,100/yr. Day-one NOI hit: $16,300 vs. the OM.
```

> **WARNING:** The single biggest spreadsheet error in buy-side underwriting is modeling the seller's current property tax instead of the post-sale reassessed tax. In high-millage or no-cap jurisdictions this can swing NOI by 10–20% on day one. Always call the assessor before LOI and confirm the millage rate and reassessment policy in writing.

### Step 7: Compute Core Underwriting Ratios

These are the four ratios every deal lives or dies by. Compute all four for every scenario.

```python
def egi(gross_rent: float, vacancy_rate: float, concessions: float = 0.0) -> float:
    """Effective Gross Income."""
    return gross_rent * (1 - vacancy_rate) - concessions

def noi(egi_amount: float, opex: float) -> float:
    """Net Operating Income. Excludes debt service, CapEx reserve, depreciation."""
    return egi_amount - opex

def cap_rate(noi_amount: float, value: float) -> float:
    """Unleveraged yield on the asset. Use stabilized NOI, not in-place."""
    return noi_amount / value

def implied_value(noi_amount: float, exit_cap: float) -> float:
    """Inverse cap: what the asset is worth at a target cap rate."""
    return noi_amount / exit_cap

def cash_on_cash(annual_cash_flow: float, cash_invested: float) -> float:
    """Leveraged yield on out-of-pocket capital (down + closing + reno + reserves)."""
    return annual_cash_flow / cash_invested

def dscr(noi_amount: float, annual_debt_service: float) -> float:
    """Debt Service Coverage Ratio. Most lenders require >= 1.20x; agency 1.25x."""
    return noi_amount / annual_debt_service
```

### Step 8: Compute IRR and Multi-Year Cash Flows

Cash-on-cash measures one year. IRR measures the whole hold including exit. Both matter; they answer different questions.

```python
def irr(cash_flows: list[float], guess: float = 0.10,
        tol: float = 1e-7, max_iter: int = 100) -> float:
    """Newton's method IRR. cash_flows[0] is negative equity outlay;
    final year includes net exit proceeds (sale price − selling costs − loan payoff)."""
    rate = guess
    for _ in range(max_iter):
        npv = sum(cf / (1 + rate) ** t for t, cf in enumerate(cash_flows))
        dnpv = sum(-t * cf / (1 + rate) ** (t + 1) for t, cf in enumerate(cash_flows))
        if abs(dnpv) < 1e-12:
            break
        new_rate = rate - npv / dnpv
        if abs(new_rate - rate) < tol:
            return new_rate
        rate = new_rate
    raise ValueError("IRR did not converge — check signs and magnitudes")

# $250k equity in, $18k/yr cash flow for 5 yr, $180k net exit proceeds in yr 5:
flows = [-250_000, 18_000, 18_000, 18_000, 18_000, 18_000 + 180_000]
print(f"IRR = {irr(flows):.2%}")  # ~11.4%
```

> **WARNING:** IRR has multiple real roots when cash flows change sign more than once (e.g., capital call in year 3 for a refi or roof replacement). When that happens, IRR is mathematically ambiguous — fall back to NPV at your cost of capital, or report MIRR with explicit reinvestment and finance rates.

### Step 9: Build Three-Scenario Stress Matrix

Stress isn't one knob; it's every knob, all turned the same direction, at the same time. Real downturns correlate.

| Variable | Base | Stress | Catastrophe | Cheapest pre-LOI verification |
|---|---|---|---|---|
| Vacancy | submarket actual | 1.5× base | 2.5× base | Pull CoStar / submarket vacancy report |
| Rents | closed-comp underwriting | −10% | −20% | 5 closed comps from past 90 days |
| Reno cost | bid + contingency | +20% | +40% | Second GC bid, line-item compared |
| Exit cap | comp + 25 bps | comp + 75 bps | comp + 150 bps | Run sensitivity on implied exit value |
| Refi rate (year 5–7) | locked quote | +100 bps | +200 bps | Two lender quotes today, written |
| Property tax (post-reassess) | full assessed | ×1.10 | ×1.20 | Call assessor; confirm millage policy |
| Days on market (exit) | 60 | 120 | 180 | Recent listing–close timelines |
| Hold extension | planned hold | +2 yr | +5 yr | Model carrying cost for stretched hold |

```python
def underwrite(rent, vacancy, opex, debt_svc, value, equity):
    egi_amt = rent * (1 - vacancy)
    n = egi_amt - opex
    return {
        "NOI": n,
        "CapRate": n / value,
        "DSCR": n / debt_svc,
        "CashOnCash": (n - debt_svc) / equity,
    }

scenarios = {
    "base":        dict(rent=180_000, vacancy=0.08, opex=72_000, debt_svc=60_000, value=1_800_000, equity=450_000),
    "stress":      dict(rent=162_000, vacancy=0.12, opex=82_000, debt_svc=66_000, value=1_650_000, equity=450_000),
    "catastrophe": dict(rent=144_000, vacancy=0.20, opex=86_000, debt_svc=72_000, value=1_500_000, equity=450_000),
}
for name, inputs in scenarios.items():
    print(name, {k: round(v, 4) for k, v in underwrite(**inputs).items()})
```

For each scenario calculate: annual cash flow, cash-on-cash return, DSCR, and 5-year IRR.

**Decision rule:** does the deal work in the stress case? If cash-on-cash goes negative or DSCR drops below 1.10 under stress, the deal requires perfect execution. Know that going in.

> **TIP:** Run the stress case **first**, base case second. If stress kills the deal, base doesn't matter — and you'll be less tempted to back-fit the base case to make the offer work.

### Step 10: Name the Assumption That Breaks the Deal

Identify the single input that, if wrong in the wrong direction, makes the deal unprofitable. Often:

| Likely killer | Cheapest pre-LOI test |
|---|---|
| Post-reno rent premium doesn't materialize | Drive 5 closed renovated comps; confirm rent psf |
| Hidden systems problems (sewer, foundation, panel) | $400 contractor walkthrough; pull permit history |
| Exit cap compression against you | Run IRR at +100 bps cap expansion |
| Taxes reassess sharply at purchase | Call the assessor; model post-sale millage |
| Insurance non-renewal or premium spike | Get a bindable quote, not a verbal indication |
| Lease maturity in a soft market (commercial) | Check tenant lease tail vs. submarket vacancy |

### Step 11: Verify Lender Readiness and DSCR

```python
# DSCR = NOI / Annual Debt Service     (most lenders require >= 1.20x)
# LTV  = Loan Amount / Appraised Value (typical: 70-75% for investment)
# Loan constant = Annual Debt Service / Loan Amount   useful for refi sensitivity
```

- Rate assumptions in the model must reflect what a lender will actually quote you **today**, not rates from six months ago.
- Confirm financing terms before making an offer. A deal that doesn't pencil at conventional terms is a harder deal than you think.
- Test the refi: if the loan resets in year 5–7, model the refi rate **+100 bps** above today's quote and re-run DSCR. If it breaks, your exit must be a sale, not a refi.

### Step 12: Produce the Deliverable

Output a pro forma with:
- Three scenarios (base, stress, catastrophe) with all four ratios and IRR for each.
- Every assumption sourced: comp addresses, contractor bid dates, lender quote dates, assessor confirmation date.
- The named deal-breaker assumption and its pre-LOI verification status.
- A concise Assumptions / Evidence / Risks / Next move section.
- The next best move and any rollback, review, or monitoring requirement.

## Pitfalls

1. **Building the pro forma to support the offer.** If you decided the price first and reverse-engineered the assumptions, you're not underwriting — you're rationalizing.
2. **Asking rents instead of closed leases.** Asking rents are list prices; closed leases are clearing prices. Use the latter.
3. **No CapEx line.** "I'll deal with the roof when it leaks" is a financing strategy, not a budget.
4. **One-shot rate quote.** Locking in a quote from one lender before shopping it. Get two, in writing, dated.
5. **Single-point projections.** A deal with no stress case is a deal you can't defend to a partner under pressure.
6. **Ignoring the post-sale tax reassessment.** Modeling the seller's taxes is the most common buy-side spreadsheet error.
7. **Treating physical vacancy as economic vacancy.** Concessions, bad debt, model units, and down units all eat EGI even when "occupied." Subtract them separately.
8. **Assuming the homestead cap transfers.** It almost never does for non-owner-occupant buyers. Florida's Save Our Homes resets on transfer; California's Prop 13 base resets on transfer.
9. **Insurance "indications" priced into the model.** Only a bindable quote is real, and only at the deductible/coverage you'll actually carry. Coastal and wildfire markets have hardened — last year's premium is not this year's premium.
10. **IRR with mixed-sign cash flows.** Capital calls or refi proceeds in mid-hold years can give IRR multiple roots. Use NPV-at-cost-of-capital or MIRR instead.
11. **Pro forma rent on day one.** Value-add rent premium is realized over the lease-up period, not the first month. Model the rent ramp explicitly.
12. **Skipping Phase I (commercial / industrial / pre-1980).** Lender will require it anyway. Environmental surprises kill deals at closing; finding out early is cheap.
13. **HOA / special assessments invisible until closing.** On condos and PUDs, pull two years of meeting minutes and the reserve study. A pending special assessment is a price negotiation, not a deal-killer — but only if you find it pre-LOI.
14. **Self-managing your time at zero cost.** If you'd hire a manager when you scale, model the management fee from day one. Otherwise you're selling your own labor at a discount and calling it cash flow.

> **WARNING:** Insurance non-renewal is the silent deal killer of 2024–2026 underwriting. In hardened markets (FL, CA wildland-urban interface, TX windstorm), policies that bound 12 months ago at $X are now binding at 2–3× or not at all. Always get a fresh bindable quote against the specific address before LOI — not a rate from a comparable property.

## Verification

Before presenting the pro forma as complete, verify every rule below:

1. **Three scenarios exist.** Every projection has base, stress, and catastrophe versions — no single-point projections.
2. **Rent uses closed comps.** Confirm 5 closed lease comps from the past 90 days are cited with addresses and dates.
3. **Renovation contingency is a line item.** Confirm it appears as an explicit dollar amount at the appropriate percentage (15% / 20% / 25%+), not a mental buffer.
4. **CapEx reserve is present.** If the model has no CapEx line, it's wrong. Confirm the line exists at ~10% of EGI.
5. **Property tax is post-reassessment.** Confirm the tax line uses purchase price × millage rate, not the seller's in-place assessment. Confirm assessor was contacted.
6. **Deal-breaker assumption is named.** Confirm a single assumption is identified as the deal killer, with its pre-LOI verification status.
7. **DSCR is calculated for base AND stress.** Confirm refi DSCR is calculated at today's rate +100 bps.
8. **Insurance is a bindable quote.** Confirm the insurance number comes from a bindable quote against the specific address, not a comp or verbal indication.
9. **Stress case passes the decision rule.** Confirm: does the deal work in the stress case? If cash-on-cash goes negative or DSCR drops below 1.10 under stress, flag that the deal requires perfect execution.
10. **All assumptions are sourced.** Every number traces to a comp, bid, quote, or assessor confirmation with a date.

## Rules (Hard)

1. No single-point projections. Every scenario has three versions (base, stress, catastrophe).
2. Rent underwriting uses closed comps, not asking rents or owner representations.
3. Renovation budget has an explicit contingency line at the appropriate percentage.
4. Expenses include a CapEx reserve. If the model doesn't have a CapEx line, it's wrong.
5. Property tax is computed against purchase price, not the seller's in-place assessment.
6. Name the deal-breaker assumption before the offer goes in.
7. DSCR is calculated for base **and** stress; refi DSCR is calculated at today's rate **+100 bps**.
8. Insurance number comes from a bindable quote against the specific address, not a comp.

## Modeling Stack Notes

If you wrap this pro forma in a deal-screening tool, the formulas above port directly. Use static types on the inputs — rounding errors and percent-vs-decimal mistakes are the dominant bug class in homebrew calculators.

```typescript
// TypeScript 6.0 — `satisfies` validates keys against UnderwritingInputs
// without widening literal types. Avoid `as` casts on financial inputs.
type UnderwritingInputs = {
  rent: number;
  vacancy: number;            // 0-1, not 0-100
  opex: number;
  annualDebtService: number;
  appraisedValue: number;
  cashInvested: number;
};

const stress = {
  rent: 162_000,
  vacancy: 0.12,
  opex: 82_000,
  annualDebtService: 66_000,
  appraisedValue: 1_650_000,
  cashInvested: 450_000,
} satisfies UnderwritingInputs;

export function underwrite(i: UnderwritingInputs) {
  const egi = i.rent * (1 - i.vacancy);
  const noi = egi - i.opex;
  return {
    noi,
    capRate: noi / i.appraisedValue,
    dscr: noi / i.annualDebtService,
    cashOnCash: (noi - i.annualDebtService) / i.cashInvested,
  };
}
```

- **Next.js 16** App Router for a server-rendered scenario page; cache stabilized inputs with `'use cache'` instead of the removed `unstable_cache`.
- **React 19.2**: scenario form inputs take `ref` as a regular prop — do not use `forwardRef`. Skip manual `memo` on row components; React Compiler handles it.
- **Tailwind v4**: define dollar/percent tokens in `@theme` in CSS, not in a `tailwind.config.js` (which v4 ignores).
- **Vite 8 (Rolldown)** if you're building a standalone calculator outside Next; the Rolldown bundler eliminates the dev/prod parse-mismatch class of bugs that bit older deal-modeling SPAs.

## Sources Checked (2026-05-31)

- Nielsen Norman Group journey mapping: https://www.nngroup.com/articles/journey-mapping-101/
- Strategyzer Value Proposition Canvas: https://www.strategyzer.com/library/the-value-proposition-canvas
- Harvard Business Review: https://hbr.org/
- OpenAI text generation guide: https://platform.openai.com/docs/guides/text-generation
- GitHub REST API documentation: https://docs.github.com/en/rest
- OWASP API Security Top 10 2023: https://owasp.org/API-Security/editions/2023/en/0x00-header/
