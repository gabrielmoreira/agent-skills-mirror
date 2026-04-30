# Industrial Underwriting Model Builder Research

## Purpose

- Supports `skills/industrial/industrial-underwriting-model-builder.md`
- Intended for analysts building acquisition models for U.S. industrial assets

## U.S.-Only Assumptions

- Focus is stabilized and transitional industrial assets in the United States
- Model is acquisition-oriented, not development-only
- Underwriting must account for industrial lease structure, rollover, downtime, TI, LC, reimbursements, and building function

## Source Table

| Source | Publisher | URL | Publish Date | Access Date | Source Type | Notes |
|--------|-----------|-----|--------------|-------------|-------------|-------|
| Industrial Space Demand Forecast, First Quarter 2026 | NAIOP | https://www.naiop.org/research-and-publications/research-reports/reports/industrial-space-demand-forecast-first-quarter-2026/ | 2026-03 | 2026-04-22 | Institutional research | Macro absorption and rent pressure context |
| U.S. Industrial Real Estate Market Indicators | JLL | https://www.jll.com/en-us/insights/market-dynamics/industrial-market-statistics-trends | 2026-01 | 2026-04-22 | Institutional research | Vacancy, asking rent, leasing activity |
| U.S. Industrial MarketBeat | Cushman & Wakefield | https://www.cushmanwakefield.com/en/united-states/insights/us-marketbeats/us-industrial-marketbeat | 2026-04 | 2026-04-22 | Institutional research | Newer-building demand, absorption, supply |
| 2025 Annual Report | Prologis / SEC | https://www.sec.gov/Archives/edgar/data/0001045609/000119312526115137/d72446dars.pdf | 2026-03 | 2026-04-22 | Primary public filing | Occupancy, mark-to-market, build-to-suit share |
| Q4 2025 and Full Year 2025 Earnings Release | Prologis / SEC | https://www.sec.gov/Archives/edgar/data/1045609/000119312526017256/pld-ex99_1.htm | 2026-01 | 2026-04-22 | Primary public filing | Tenant improvements, leasing commissions, turnover costs |
| 2025 Annual Report | STAG Industrial / SEC | https://www.sec.gov/Archives/edgar/data/0001479094/000147909426000009/stag-20251231.htm | 2026-02 | 2026-04-22 | Primary public filing | WALT and expiration profile context |
| Annual Report | Rexford Industrial Realty / SEC | https://www.sec.gov/Archives/edgar/data/1571283/000157128323000019/rexfordindustrialrealty_ars.pdf | 2023-02 | 2026-04-22 | Primary public filing | Re-leasing costs, operating expense recovery context |
| Rent Abatement in Commercial Leases: Free Rent & CAM Impact | CAMAudit | https://www.camaudit.io/resources/lease-language/rent-abatement-clause | 2026-04 | 2026-04-22 | Practitioner explainer | Treatment of concessions and reimbursements |
| Applied Automation in the Warehouse Boosts Value Across Stakeholders | Prologis Research | https://www.prologis.com/insights-news/research/applied-automation-warehouse-boosts-value-across-stakeholders | 2026-04 | 2026-04-22 | Quasi-primary market participant research | Functional obsolescence and capital competitiveness |
| U.S. Industrial Tenant Demand Study | JLL | https://www.jll.com/en-us/insights/industrial-tenant-demand-study | 2025-08-13 | 2026-04-22 | Institutional research | Demand by user type and sector |

## Key Findings

- Industrial underwriting must model the lease profile first and then layer in market assumptions. Base rent, reimbursement structure, and rollover schedule drive revenue more than a multifamily-style occupancy snapshot.
- Effective industrial NOI is sensitive to:
  - rent steps
  - free rent
  - downtime
  - TI
  - LC
  - release probability
  - reimbursement leakage
- Public industrial landlord disclosures confirm that turnover costs are real and material. They should not be hidden inside a generic reserve line.
- Modern building functionality affects underwritten release assumptions. Submarket strength alone is not enough if the building is outdated.
- Underwriting should separate stabilized cash flow from value-creation assumptions such as re-leasing, spec upgrades, power work, dock expansion, or office demising changes.

## Benchmark and Formula Decisions

- Require model inputs for:
  - current and market rent
  - contractual steps
  - reimbursement structure
  - WALT
  - rollover schedule
  - downtime
  - TI per square foot
  - LC as percentage of rent or per square foot
  - capital projects and spec upgrades
- Separate income into:
  - contractual base rent
  - reimbursements
  - temporary abatements
  - percentage or specialty income only when actually present
- Separate costs into:
  - recoverable operating expenses
  - non-recoverable expenses
  - capitalized leasing costs
  - capital maintenance and competitiveness spend
- Do not use a flat national downtime, TI, or LC assumption. The skill should produce scenario-aware assumptions anchored to:
  - subtype
  - tenant size
  - market depth
  - building competitiveness

## Conflicting Source Resolution

- Market reports describe aggregate vacancy and demand, while public REIT filings reflect execution within stronger portfolios. The model should use public REIT data to remind users that rollover economics can be powerful, but not to force optimistic release assumptions.
- Concession treatment varies by lease. Model logic must reflect lease-specific cash flow rather than assuming all abatements suspend reimbursements.
- Institutional reports often emphasize modern bulk product; shallow-bay and flex assets may need different release and capital assumptions.

## Edge Cases and Red Flags

- Single-tenant assets with near-term rollover can swing from bond-like income to full speculative release risk
- Functional obsolescence can overwhelm otherwise acceptable rent metrics
- Flex industrial often requires higher TI and leasing friction than pure warehouse product
- Assets with partial gross or modified gross structures can under-recover expenses versus initial underwriting expectations

## Open Questions

- Whether future versions should include a separate industrial development model
- Whether future versions should include market-specific TI/LC matrices
- Whether cold storage or manufacturing assets need dedicated underwriting modules rather than only subtype adjustments
