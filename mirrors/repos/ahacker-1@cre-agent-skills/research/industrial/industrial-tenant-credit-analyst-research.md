# Industrial Tenant Credit Analyst Research

## Purpose

- Supports `skills/industrial/industrial-tenant-credit-analyst.md`
- Intended for users evaluating industrial tenant quality, concentration, rollover risk, and release probability

## U.S.-Only Assumptions

- Focus is occupied U.S. industrial assets
- Tenants may be public companies, PE-backed middle-market firms, private distributors, manufacturers, or logistics providers
- Credit analysis is acquisition-oriented and qualitative plus quantitative, not a replacement for full corporate credit underwriting

## Source Table

| Source | Publisher | URL | Publish Date | Access Date | Source Type | Notes |
|--------|-----------|-----|--------------|-------------|-------------|-------|
| U.S. Industrial Tenant Demand Study | JLL | https://www.jll.com/en-us/insights/industrial-tenant-demand-study | 2025-08-13 | 2026-04-22 | Institutional research | Tenant categories and demand shifts |
| U.S. Industrial Real Estate Market Indicators | JLL | https://www.jll.com/en-us/insights/market-dynamics/industrial-market-statistics-trends | 2026-01 | 2026-04-22 | Institutional research | National leasing and absorption context |
| The Inland Empire Leads the Nation in Large Industrial Leases for 2025 | CBRE | https://www.cbre.com/press-releases/the-inland-empire-leads-the-nation-in-large-industrial-leases-for-2025 | 2026-02-01 | 2026-04-22 | Institutional market research | Large-lease occupier mix and geography |
| 2025 Annual Report | Prologis / SEC | https://www.sec.gov/Archives/edgar/data/0001045609/000119312526115137/d72446dars.pdf | 2026-03 | 2026-04-22 | Primary public filing | Rollover mark-to-market and occupancy resilience |
| Q4 2025 and Full Year 2025 Earnings Release | Prologis / SEC | https://www.sec.gov/Archives/edgar/data/1045609/000119312526017256/pld-ex99_1.htm | 2026-01 | 2026-04-22 | Primary public filing | Top customers and remaining lease expirations |
| 2025 Annual Report | STAG Industrial / SEC | https://www.sec.gov/Archives/edgar/data/0001479094/000147909426000009/stag-20251231.htm | 2026-02 | 2026-04-22 | Primary public filing | WALT and expiration concentration evidence |
| Annual Report | Rexford Industrial Realty / SEC | https://www.sec.gov/Archives/edgar/data/1571283/000157128323000019/rexfordindustrialrealty_ars.pdf | 2023-02 | 2026-04-22 | Primary public filing | Releasing, re-lease cost, and tenant demand risks |
| Quarterly Retail E-Commerce Sales | U.S. Census Bureau | https://www.census.gov/retail/ecommerce.html | 2026-03-10 | 2026-04-22 | Primary government source | Retail and fulfillment demand backdrop |
| Transborder Freight Data Annual Report: 2025 | Bureau of Transportation Statistics | https://www.bts.gov/newsroom/transborder-freight-data-annual-report-2025-0 | 2026-03 | 2026-04-22 | Primary government source | Cross-border freight support for logistics users |
| Applied Automation in the Warehouse Boosts Value Across Stakeholders | Prologis Research | https://www.prologis.com/insights-news/research/applied-automation-warehouse-boosts-value-across-stakeholders | 2026-04 | 2026-04-22 | Quasi-primary market participant research | Building functionality affects tenant retention and reletting risk |

## Key Findings

- Industrial tenant credit work must look beyond a generic credit score. The key question is whether the tenant is both **financially durable** and **replaceable** at the subject building.
- User type matters. 3PLs, retailers, manufacturers, and specialized occupiers carry different margin profiles, space needs, and relocation behavior.
- Public industrial REIT disclosures suggest that rollover economics remain favorable in many institutional markets, but replacement assumptions depend heavily on building quality and submarket depth.
- Tenant concentration should be evaluated using:
  - annual base rent
  - occupied square footage
  - building criticality
  - release probability if the tenant vacates
- Facility-specific fit matters. A weak-credit tenant in generic shallow-bay space can be easier to replace than a mid-credit tenant in highly specialized space with fewer alternative users.

## Benchmark and Formula Decisions

- The skill should score tenant risk across:
  - financial durability
  - industry cyclicality
  - building dependence
  - replaceability
  - lease durability
  - concentration
- Separate **tenant credit risk** from **asset release risk**.
- Require explicit flags for:
  - parent guarantee presence
  - public vs private reporting visibility
  - high share of rent from one tenant
  - near-term rollover
  - specialized build-out
  - tenant option packages
- Avoid using multifamily-style tenant turnover assumptions. Industrial tenant rollover is lumpy and often capital-intensive.

## Conflicting Source Resolution

- National tenant demand reports show category-level demand, but single-asset underwriting must weight local release probability more heavily than national sector strength.
- Public REIT metrics are useful for industrial leasing behavior, but they reflect stronger portfolios than many middle-market or private-market acquisitions.
- Macro freight and e-commerce indicators are directional only; they should support demand narratives, not override tenant-specific underwriting.

## Edge Cases and Red Flags

- Credit tenants with short remaining term can still create material rollover risk if replacement costs are high
- Tenants in specialized manufacturing or cold-chain space may be harder to replace than their rent roll share suggests
- Private-company tenants with no parent guaranty should trigger lower-confidence analysis and stronger downside assumptions
- A tenant can be operationally important to a location without being corporate-investment-grade

## Open Questions

- Whether future versions should include a lightweight framework for private-company financial statement review
- Whether credit scoring should vary by industrial subtype
- Whether future packs should split logistics-user credit from manufacturing-user credit
