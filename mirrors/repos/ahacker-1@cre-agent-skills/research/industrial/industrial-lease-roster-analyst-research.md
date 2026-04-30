# Industrial Lease Roster Analyst Research

## Purpose

- Supports `skills/industrial/industrial-lease-roster-analyst.md`
- Intended for analysts reviewing industrial rent rolls, lease rosters, rollover schedules, and income durability

## U.S.-Only Assumptions

- Focus is leased industrial real estate in the United States
- Analysis assumes institutional lease rosters, rent rolls, or lease abstracts are available or can be reconstructed
- Lease structures may be triple net, modified gross, or mixed across a multi-tenant asset
- Goal is acquisitions screening, not property management billing administration

## Source Table

| Source | Publisher | URL | Publish Date | Access Date | Source Type | Notes |
|--------|-----------|-----|--------------|-------------|-------------|-------|
| Q4 2025 and Full Year 2025 Earnings Release | Prologis / SEC | https://www.sec.gov/Archives/edgar/data/1045609/000119312526017256/pld-ex99_1.htm | 2026-01 | 2026-04-22 | Primary public filing | Turnover costs, occupancy, lease metrics |
| 2025 Annual Report | Prologis / SEC | https://www.sec.gov/Archives/edgar/data/0001045609/000119312526115137/d72446dars.pdf | 2026-03 | 2026-04-22 | Primary public filing | Mark-to-market, rent change on rollover, occupancy |
| 2025 Annual Report | STAG Industrial / SEC | https://www.sec.gov/Archives/edgar/data/0001479094/000147909426000009/stag-20251231.htm | 2026-02 | 2026-04-22 | Primary public filing | WALT, scheduled lease expirations |
| Annual Report | Rexford Industrial Realty / SEC | https://www.sec.gov/Archives/edgar/data/1571283/000157128323000019/rexfordindustrialrealty_ars.pdf | 2023-02 | 2026-04-22 | Primary public filing | Triple net and modified gross lease structure, reletting costs |
| 2024 Annual Report | EastGroup Properties / SEC | https://www.sec.gov/Archives/edgar/data/49600/000004960025000019/egp-20241231.htm | 2025-02 | 2026-04-22 | Primary public filing | Industrial operating and leasing context |
| Commercial Real Estate Terms and Definitions | NAIOP | https://www.naiop.org/education-and-career/industry-terms-and-definitions/ | n.d. | 2026-04-22 | Institutional glossary | Clear definitions for dock, clear height, and industrial terminology |
| Rent Abatement in Commercial Leases: Free Rent & CAM Impact | CAMAudit | https://www.camaudit.io/resources/lease-language/rent-abatement-clause | 2026-04 | 2026-04-22 | Practitioner explainer | Effective rent and reimbursement treatment during abatements |
| Commercial Lease Addendum for Expense Reimbursement | HAR Form Library | https://content.har.com/FormManager/pdf/20.pdf | 2025-12 | 2026-04-22 | Quasi-primary form source | CAM, tax, and insurance reimbursement mechanics |
| U.S. Industrial Tenant Demand Study | JLL | https://www.jll.com/en-us/insights/industrial-tenant-demand-study | 2025-08-13 | 2026-04-22 | Institutional research | Tenant demand and user-type shifts |
| The Inland Empire Leads the Nation in Large Industrial Leases for 2025 | CBRE | https://www.cbre.com/press-releases/the-inland-empire-leads-the-nation-in-large-industrial-leases-for-2025 | 2026-02-01 | 2026-04-22 | Institutional market research | Large-format lease evidence and tenant categories |

## Key Findings

- Industrial lease roster analysis should center on **income durability**, not just occupancy. WALT, rollover cliffs, scheduled rent steps, free-rent burnoff, and tenant concentration matter more than a multifamily-style "loss to lease" view alone.
- Rollover must be evaluated by both **square footage** and **revenue**. A single high-rent or mission-critical tenant can distort asset-level exposure even when occupied square footage looks diversified.
- Effective rent matters. Free rent, abatements, and reimbursement timing can materially change near-term cash flow without changing face rent.
- The roster should identify lease structure by tenant whenever possible. Triple net, modified gross, and partial reimbursement structures should not be blended into a single rent assumption.
- National industrial operators are still showing strong mark-to-market on rollover, but that should not be used as a universal assumption. In-place rent upside is highly dependent on location, subtype, tenant quality, and downtime risk.

## Benchmark and Formula Decisions

- Use a required lease roster output that includes:
  - tenant
  - suite or building
  - leased square feet
  - annual base rent
  - rent per square foot
  - lease start and expiration
  - renewal or termination options
  - reimbursement structure
  - free-rent or abatement period
  - expansion or contraction rights
- Include WALT measured by:
  - leased square feet
  - annual base rent
- Flag rollover concentration at both the annual and quarterly level.
- Separate revenue analysis into:
  - contractual base rent
  - reimbursements
  - temporary abatements and concessions
  - near-term mark-to-market or rollover risk
- Do not use multifamily-style loss-to-lease as the primary metric. For industrial, the primary forward-looking metric is rent roll-down or roll-up at expiration, adjusted for downtime, TI, and LC.

## Conflicting Source Resolution

- Public REIT filings show strong rent change on rollover, but those portfolios skew toward large institutional owners and are not a safe default for every local industrial deal.
- Lease form sources and reimbursement addenda are useful for mechanics, but they should not be treated as universal legal outcomes; landlord form and state law still matter.
- Tenant demand studies are better for explaining which user groups are active than for setting rent or downtime defaults.

## Edge Cases and Red Flags

- Single-tenant or low-tenant-count assets can appear stable until one lease dominates the rent roll and compresses underwriting flexibility.
- Short WALT is not automatically negative if the asset is located in a constrained infill market with proven releasing demand and strong mark-to-market opportunity.
- Flex industrial rosters require special attention to office-heavy space, because downtime and tenant replacement costs can differ materially from pure warehouse product.
- Abatement periods, early termination rights, and landlord-funded relocation or expansion concessions can create hidden short-term cash flow dips.

## Open Questions

- Whether later versions should include a formal downtime/TI/LC matrix by subtype
- Whether rent-step normalization should live in the lease roster skill or only in the underwriting model builder
- Whether future versions should include cold storage or manufacturing-specific lease roster adjustments
