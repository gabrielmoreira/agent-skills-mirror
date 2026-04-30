# Industrial Financing Fit Research

## Purpose

- Supports `skills/industrial/industrial-financing-fit.md`
- Intended for users matching industrial deals to lender types and likely loan structures

## U.S.-Only Assumptions

- Focus is U.S. acquisition and recapitalization financing for industrial real estate
- Includes banks, life companies, CMBS, debt funds / alternative lenders, and owner-user SBA 504 as an explicit edge case
- Excludes agency multifamily logic

## Source Table

| Source | Publisher | URL | Publish Date | Access Date | Source Type | Notes |
|--------|-----------|-----|--------------|-------------|-------------|-------|
| 504 Loans | U.S. Small Business Administration | https://www.sba.gov/funding-programs/loans/504-loans | 2026-03-30 | 2026-04-22 | Primary government source | Owner-user financing, maturities, program restrictions |
| 2025 Commercial Mortgage Program Fact Sheet | MetLife Investment Management | https://investments.metlife.com/content/dam/metlifecom/us/investments/pdf/2025-commercial-mortgage-program-fact-sheet.pdf | 2025-10 | 2026-04-22 | Quasi-primary lender source | Property types, size, terms, LTV targets |
| Core Financing Tear Sheet May 2025 | PGIM Real Estate | https://www.pgim.com/content/dam/pgim/us/en/pgim-real-estate/active/documents/program-sheets/Core-Financing-Tear-Sheet-May-2025.pdf | 2025-05 | 2026-04-22 | Quasi-primary lender source | Senior debt appetite and major property-type coverage |
| Core Debt Strategy Page | PGIM Real Estate | https://www.pgim.com/fr/en/institutional/investment-capabilities/strategies/alternatives/real-estate/debt/core-debt | n.d. | 2026-04-22 | Quasi-primary lender source | Senior debt positioning across industrial and other sectors |
| Commercial Real Estate Lending Activity Increases in Q1 2025 | CBRE | https://www.cbre.com/press-releases/commercial-real-estate-lending-activity-increases-in-q1-2025 | 2025-04 | 2026-04-22 | Institutional capital-markets research | Lender mix, spreads, debt yields, LTV |
| U.S. Capital Markets Q4 2025 | CBRE | https://www.cbre.com/insights/figures/q4-2025-us-capital-markets-figures | 2026-02-03 | 2026-04-22 | Institutional capital-markets research | Non-agency lender mix at year-end 2025 |
| Quarterly Survey of Commercial / Multifamily Mortgage Bankers Originations | MBA | https://www.mba.org/docs/default-source/research-and-forecasts/cmf-originations-index/4q25cmforiginationssurvey.pdf?sfvrsn=d55d4983_1 | 2026-02 | 2026-04-22 | Institutional industry survey | Industrial origination trends by lender type |
| CMBS Delinquency Rate Declines in February 2026 | Trepp | https://www.trepp.com/trepptalk/cmbs-delinquency-rate-declines-in-february-2026-led-by-large-office-retail-loan-extensions | 2026-03 | 2026-04-22 | Institutional market data | Industrial delinquency context for CMBS risk |
| First Half 2025 CMBS Issuance Up 35% from 2024 | Trepp | https://www.trepp.com/trepptalk/cmbs-issuance-up-in-first-half-2025 | 2025-07 | 2026-04-22 | Institutional market data | CMBS issuance and market liquidity |
| U.S. Commercial Real Estate Chartbook June 2025 | MetLife Investment Management | https://investments.metlife.com/insights/real-estate/us-commercial-real-estate-chartbook-june-2025/ | 2025-06 | 2026-04-22 | Institutional market outlook | Sector value outlook and institutional debt context |

## Key Findings

- Industrial financing fit depends on both **property profile** and **cash flow profile**.
- Banks, life companies, CMBS, and alternative lenders are all active in industrial, but they fit different use cases:
  - banks for relationship-driven and recourse-friendly executions
  - life companies for high-quality stabilized assets
  - CMBS for larger, durable cash-flow assets with bond-execution tolerance
  - debt funds and alternative lenders for transitional or flexible executions
  - SBA 504 only for eligible owner-user situations, not investment rental real estate
- Lending markets improved through 2025, but average leverage remained disciplined. CBRE reported lower average LTV and higher debt yield than the prior quarter in Q1 2025.
- Life company materials indicate a preference for institutional-quality industrial and logistics product, often at moderate leverage and larger loan sizes.
- CMBS market data suggests industrial credit remains materially healthier than office and retail in delinquency terms, but issuance and borrower fit still depend on size, documentation quality, and term durability.

## Benchmark and Formula Decisions

- The skill should sort financing fit by:
  - asset stabilization
  - WALT and rollover profile
  - tenant quality
  - market liquidity
  - loan size
  - sponsor desire for flexibility vs rate efficiency
- Default industrial fit logic:
  - high-quality stabilized asset with durable WALT -> life company, CMBS, or bank
  - smaller or relationship-driven deal -> bank
  - transitional, lease-up, or repositioning deal -> bridge / debt fund / flexible life company programs
  - owner-user occupancy case -> SBA 504 edge-case review
- The skill should not hard-code rates. It should use relative positioning:
  - banks and life companies generally lower cost than bridge
  - CMBS often competitive for durable, financeable cash flow but less flexible
  - debt funds provide structural flexibility at higher cost
- When lender-specific information is missing, use cautious ranges and note that final term selection depends on deal size, sponsor, and tenant durability.

## Conflicting Source Resolution

- Institutional market commentary on lender share changes quarter to quarter should not be turned into permanent rules; it is directional evidence of liquidity, not a timeless capital stack hierarchy.
- Lender term sheets and fact sheets reflect target execution, not guaranteed loan proceeds. Use them to define likely fit and screening logic, not underwritten certainty.
- SBA guidance is primary for 504 eligibility and should override secondary commentary.

## Edge Cases and Red Flags

- Industrial owner-user deals should not be mixed with investor-owned lease-up logic
- Near-term rollover can disqualify an otherwise institutional-quality building from low-cost permanent debt
- Specialized or functionally obsolete assets may need debt-fund or bridge execution even in strong markets
- Very small or highly bespoke deals may not fit CMBS or life company sizing even if the credit looks strong

## Open Questions

- Whether future versions should add a dedicated construction lending industrial note
- Whether C-PACE should be broken out into a separate industrial capital-stack workflow later
- Whether later versions should distinguish single-tenant net-leased industrial from multi-tenant warehouse financing as separate skills
