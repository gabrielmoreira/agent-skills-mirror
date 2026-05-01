---
type: skill
lifecycle: stable
inheritance: inheritable
name: financial-analysis
description: Financial modeling, analysis frameworks, and regulatory awareness for business-minded professionals.
tier: extended
applyTo: '**/*financial*,**/*analysis*'
currency: 2026-04-22
lastReviewed: 2026-04-30
---

# Financial Analysis Skill


> Financial modeling, analysis frameworks, and regulatory awareness for business-minded professionals.

## Core Principle

Financial analysis transforms raw numbers into decisions. Every model, ratio, and forecast exists to answer one question: *Should we do this?*

## Financial Statement Analysis

### The Three Statements

| Statement | Measures | Key Question |
|-----------|----------|-------------|
| **Income Statement** | Profitability over a period | Is the business making money? |
| **Balance Sheet** | Assets, liabilities, equity at a point in time | What does the business own and owe? |
| **Cash Flow Statement** | Cash movement over a period | Where is the cash going? |

### Key Ratios

#### Profitability

| Ratio | Formula | Meaning |
|-------|---------|---------|
| Gross Margin | (Revenue − COGS) / Revenue | Pricing power and production efficiency |
| Operating Margin | Operating Income / Revenue | Core business profitability |
| Net Margin | Net Income / Revenue | Bottom-line profitability |
| ROE | Net Income / Shareholders' Equity | Return to equity holders |
| ROA | Net Income / Total Assets | Asset efficiency |

#### Liquidity

| Ratio | Formula | Healthy Range |
|-------|---------|---------------|
| Current Ratio | Current Assets / Current Liabilities | 1.5–3.0 |
| Quick Ratio | (Current Assets − Inventory) / Current Liabilities | 1.0–2.0 |
| Cash Ratio | Cash / Current Liabilities | 0.5–1.0 |

#### Leverage

| Ratio | Formula | Watch For |
|-------|---------|-----------|
| Debt-to-Equity | Total Debt / Total Equity | >2.0 signals high leverage |
| Interest Coverage | EBIT / Interest Expense | <1.5 signals debt stress |
| Debt-to-EBITDA | Total Debt / EBITDA | >4.0 may limit borrowing capacity |

## Financial Modeling

### DCF (Discounted Cash Flow)

**When to use**: Valuing a business, project, or investment based on future cash flows.

**Steps:**

1. Project free cash flows (FCF) for 5–10 years
2. Calculate terminal value (perpetuity growth or exit multiple)
3. Discount all cash flows to present value using WACC
4. Sum = enterprise value
5. Subtract net debt → equity value

**Key assumptions to document:**

- Revenue growth rate and drivers
- Margin trajectory
- Capital expenditure requirements
- Working capital changes
- Discount rate (WACC) and terminal growth rate

### Comparable Company Analysis (Comps)

| Step | Action |
|------|--------|
| 1 | Select peer group (industry, size, geography) |
| 2 | Gather trading multiples (EV/EBITDA, P/E, EV/Revenue) |
| 3 | Calculate median and mean multiples |
| 4 | Apply multiples to target company metrics |
| 5 | Derive implied valuation range |

### Scenario Analysis

Always model three cases:

| Scenario | Purpose | Probability Weight |
|----------|---------|-------------------|
| **Base** | Most likely outcome | 50–60% |
| **Upside** | Favorable conditions | 20–25% |
| **Downside** | Adverse conditions | 20–25% |

## Budgeting & Forecasting

### Budget Types

| Type | Method | Best For |
|------|--------|----------|
| **Zero-based** | Justify every line from zero | Cost control, new initiatives |
| **Incremental** | Adjust prior year ±% | Stable operations |
| **Activity-based** | Cost per activity/output | Service organizations |
| **Rolling** | Continuously extend 12-month window | Dynamic environments |

### Variance Analysis

| Variance | Formula | Interpretation |
|----------|---------|---------------|
| Favorable | Actual better than budget | Outperformance or conservative budget |
| Unfavorable | Actual worse than budget | Underperformance or aggressive budget |
| Volume variance | (Actual units − Budget units) × Budget price | Demand-driven |
| Price variance | (Actual price − Budget price) × Actual units | Pricing/cost-driven |

## Real Estate Financial Analysis

### Property Valuation Methods

| Method | Approach | Best For |
|--------|----------|----------|
| **Cap Rate** | NOI / Property Value | Income-producing properties |
| **Comparable Sales** | Recent sale prices of similar properties | Residential, land |
| **Cost Approach** | Land value + replacement cost − depreciation | Unique properties |

### Key Metrics

| Metric | Formula | Target |
|--------|---------|--------|
| Cap Rate | NOI / Purchase Price | 4–10% depending on market |
| Cash-on-Cash Return | Annual Cash Flow / Total Cash Invested | 8–12% |
| DSCR (Debt Service Coverage) | NOI / Annual Debt Service | >1.25 |
| GRM (Gross Rent Multiplier) | Price / Annual Gross Rent | Lower = better value |

## Regulatory Awareness

### Key Frameworks (Not Legal Advice)

| Framework | Scope | Applies To |
|-----------|-------|-----------|
| **SOX** (Sarbanes-Oxley) | Financial reporting controls, audit requirements | US public companies |
| **PCI-DSS** | Payment card data security | Any business processing card payments |
| **Basel III/IV** | Capital adequacy, liquidity requirements | Banks and financial institutions |
| **Dodd-Frank** | Financial stability, consumer protection | US financial institutions |
| **IFRS vs GAAP** | Accounting standards | International vs US reporting |
| **MiFID II** | Financial instrument markets | EU investment firms |

### Financial Compliance Patterns

- **Segregation of duties**: No single person controls an entire financial process
- **Audit trails**: Every financial transaction traceable to source documentation
- **Materiality thresholds**: Define what magnitude of error requires disclosure
- **Internal controls**: Preventive (approvals) and detective (reconciliations)

## Anti-Patterns

- Building models without documenting assumptions
- Using a single-point forecast instead of scenarios
- Confusing revenue with cash flow
- Ignoring working capital in projections
- Treating all debt as equivalent (ignoring covenants, maturity, rates)
- Circular references in spreadsheet models without iteration controls
