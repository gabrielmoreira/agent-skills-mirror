# Sector-Specific Valuation and KPI Rules

Apply these rules in addition to the common framework. A sector-specific metric replaces, rather than decorates, an inappropriate generic metric.

## 1. SaaS and Software

### Required KPIs

- ARR and ARR growth
- Net revenue retention (NRR)
- Gross retention
- RPO and current RPO
- Subscription versus services mix
- Gross margin
- FCF margin
- Rule of 40
- SBC / revenue
- Diluted-share growth
- Capitalized software development
- Customer concentration

### Valuation

Use EV/revenue only as a secondary measure. Prefer EV/FCF, FCF yield, normalized operating margin, and per-share FCF growth once FCF is positive.

### Red flags

- ARR growth falling faster than revenue growth
- NRR below 100%
- SBC / revenue above 15% without rapid decline
- FCF driven mainly by SBC or deferred revenue
- GAAP losses masked by recurring adjusted exclusions

## 2. Semiconductors and Semiconductor Equipment

### Required KPIs

- Inventory and inventory days
- Book-to-bill
- Backlog
- Utilization
- Lead times
- Channel inventory
- Customer capex
- End-market mix
- Product mix
- Gross-margin cycle
- Customer concentration

### Valuation

Use normalized/mid-cycle EPS, EBIT, and FCF. A low trailing P/E at peak margins is not cheap.

### Red flags

- Inventory growth exceeding revenue growth
- Backlog cancellation or book-to-bill below 1
- Margin well above historical median without structural evidence
- Customer capex rolling over

## 3. Industrials and Capital Goods

### Required KPIs

- Orders
- Backlog
- Book-to-bill
- Organic growth
- Price and volume
- Utilization
- Customer capex
- Aftermarket/service mix
- Working-capital requirements

### Valuation

Use EV/EBIT, EV/FCF, and normalized EPS. For highly cyclical businesses calculate mid-cycle margins.

## 4. Retail, Restaurants, and Consumer Companies

### Required KPIs

- Comparable sales
- Traffic
- Average ticket
- Unit growth
- Store-level margin
- New-unit payback
- Inventory turnover
- Markdown rate
- Customer-acquisition cost
- Direct-to-consumer mix
- International growth

### Valuation

Use P/E and FCF yield with lease-aware enterprise value where material. Distinguish growth from unit expansion, price, traffic, and mix.

### Red flags

- Price-led comps with declining traffic
- Inventory rising faster than sales
- New-unit returns deteriorating
- Buybacks funded by leverage while store economics weaken

## 5. Healthcare Services and Medical Devices

### Required KPIs

- Procedure or patient volume
- Reimbursement trends
- Utilization
- Installed base
- Consumable/recurring revenue
- Pipeline or product-launch milestones
- Gross margin
- Regulatory actions
- Customer or payer concentration

### Valuation

Use P/E, EV/EBIT, and EV/FCF. For product-concentrated businesses, scenario-test loss of exclusivity or reimbursement changes.

## 6. Commercial Biotechnology and Specialty Pharmaceuticals

### Eligibility

Exclude pre-revenue or development-stage companies. Admit only businesses with meaningful commercial revenue and a valid earnings/standard-FCF framework.

### Required KPIs

- Product-level revenue and growth
- Top-product revenue concentration (`top_product_revenue_pct`)
- Prescription, patient, or demand growth
- Gross-to-net deductions
- Market share
- Nearest material loss-of-exclusivity date (`nearest_material_loe_date`)
- ANDA/patent settlement or litigation status
- Next-generation formulation, indication, or lifecycle-extension strategy
- Replacement pipeline probability and milestones
- R&D and launch intensity
- Acquisition integration and contingent obligations
- Source IDs supporting concentration and LOE

### Valuation and Risk

Use P/E and standard FCF only when operating economics are established. Do not mix a current GAAP metric with future adjusted consensus. Treat product concentration and LOE as structural risk even when near-term growth is strong. Do not count pipeline NPV as certain value.

The evaluator applies a sector penalty when the top product is at least 50% of revenue and nearest material LOE is within five years; missing sourced concentration/LOE evidence is review-required in strict mode.

## 7. Payments, Marketplaces, and Money Movement

### Required KPIs

- TPV or payment volume and growth
- Revenue/TPV and gross-profit/TPV
- Current and prior gross-profit take rate (`gross_profit_to_tpv_pct`, `gross_profit_to_tpv_prior_pct`)
- Transaction count and active merchants/users
- Cross-border, country, and FX exposure
- Credit or chargeback losses where applicable
- Corporate cash and marketable securities
- Customer/merchant/settlement funds and restricted cash
- Standard FCF versus company-adjusted FCF
- Working-capital normalization
- Dilution and SBC
- Source IDs for cash classification and take rates

### Valuation and Risk

Use corporate cash only for net-debt analysis; settlement float is not shareholder cash. A revenue surge caused by lower-margin pass-through volume is not equivalent to gross-profit growth. Track gross-profit/TPV and operating leverage. If the take rate declines, explain whether mix, geography, competition, or accounting presentation caused it.

Strict mode requires sourced separation of corporate and settlement cash.

## 8. Banks

Do not use EV/EBITDA.

### Required KPIs

- P/TBV and P/book
- ROTCE and ROE
- Net interest margin
- Deposit beta
- Deposit mix and uninsured deposits
- Loan growth
- Nonperforming loans
- Net charge-offs
- Provision expense
- CET1
- Commercial real-estate exposure
- Securities marks and accumulated other comprehensive income

### Scenario basis

Use TBV per share or book value per share and an appropriate P/TBV or P/book multiple. Model credit and deposit stress.

## 9. Insurance

### Required KPIs

- P/book or P/TBV
- ROE
- Combined ratio
- Underwriting income
- Reserve development
- Investment income
- Catastrophe exposure
- Premium growth
- Retention

### Scenario basis

Use book/TBV per share or normalized EPS. Adjust for reserve quality and catastrophe-cycle conditions.

## 10. REITs

Do not use ordinary EPS or P/E as the primary basis.

### Required KPIs

- P/FFO and P/AFFO
- AFFO growth
- NAV premium/discount
- Same-store NOI
- Occupancy
- Leasing spreads
- Lease maturities
- Net debt / EBITDA
- Fixed-charge coverage
- Dividend payout

### Scenario basis

Use AFFO per share or NAV per share. Include refinancing and cap-rate sensitivity.

## 11. Business Development Companies (BDCs)

### Required KPIs

- Price/NAV
- Net investment income per share
- Non-accruals
- Portfolio yield
- Debt/equity
- Interest coverage
- First-lien exposure
- Payment-in-kind income
- Dividend coverage
- NAV trend

### Scenario basis

Use NAV per share or normalized NII per share. Do not use industrial-company EV/EBITDA.

## 12. MLPs and Midstream Partnerships

### Required KPIs

- Distributable cash flow per unit
- Distribution coverage
- Leverage
- Contracted versus commodity-sensitive cash flow
- Counterparty concentration
- Maintenance versus growth capex
- Unit issuance/buybacks
- IDRs or sponsor conflicts

### Scenario basis

Prefer DCF per unit, FCF per unit, and EV/EBITDA on a consistently defined basis. Treat tax structure separately.

## 13. Energy, Mining, Materials, Chemicals, Steel, and Shipping

### Required KPIs

- Commodity or freight prices
- Production/volume
- Realized price
- Unit costs
- Capacity/utilization
- Capital intensity
- Maintenance capex
- Reserve life where relevant
- Contract coverage
- Balance-sheet sensitivity

### Valuation

Use normalized commodity assumptions and mid-cycle margins. Do not annualize a spot-price windfall.

## 14. Homebuilders and Housing-Related Companies

### Required KPIs

- Orders and cancellations
- Backlog
- Community count
- ASP
- Gross margin excluding unusual items
- Incentives
- Land inventory
- Net debt/capital
- Mortgage-rate sensitivity

### Valuation

Use normalized EPS, book value, and land-cycle analysis. A low P/E at peak closings may be misleading.

## 15. Advertising, Staffing, Transportation, Airlines, and Autos

These are normally cyclicality score 3 to 5.

### Required KPIs

- Volume and utilization
- Price/yield
- Customer budget or hiring trends
- Capacity
- Load factor or miles/hours where relevant
- Used-asset values
- Backlog/order intake
- Labor and fuel/input costs

Use normalized operating margins and recession drawdown history.

## 16. Auto Dealerships and Floorplan Debt

Do not apply general-company net-debt/EBITDA mechanically to auto dealers. Obtain a sourced sector-adjusted leverage measure that explicitly excludes inventory floorplan financing when appropriate.

Required schema-v3 fields:

- `adjusted_net_debt_to_ebitda`
- `floorplan_debt_excluded = true`
- source IDs

Without these fields, route the candidate to `review_required`, not `screened_out` solely because unadjusted leverage appears high.

## 17. Commercial Biopharma LOE Stress

When a top product contributes at least 50% of revenue and a material LOE is within five years:

- calculate or source product concentration,
- record the nearest material LOE date,
- distinguish base patent, pediatric exclusivity, settlements, formulation/use patents, and replacement products,
- calculate 6x and 8x year-3 metric stress cases in addition to the generic 20% multiple-contraction case.

Product concentration may be derived as:

```text
top product revenue / total revenue
```

only when both values share the same period and source evidence.

## v3.5 Normalization Rules

- Normalize `biopharma`, `pharma`, `biotechnology`, `royalty_biopharma`, and `drug_delivery_platform` to `commercial_biopharma` when commercial product or royalty economics exist.
- Commercial biopharma requires sourced product/revenue-stream concentration, nearest material LOE, and configured 6x/8x stress scenarios.
- `peak_profit_risk=true` forces mid-cycle normalization regardless of the numeric cyclicality score.
- Sector evidence is part of the data-quality score and can cap it at 65 when missing.
