---
name: financial-report-generation
description: Generate balance sheets, cash flow statements, P&L reports, and executive financial summaries
license: MIT
metadata:
  author: community
  version: "1.0"
---

# Financial Report Generation

Generate formatted financial statements — income statements, balance sheets, cash flow statements — from raw transaction data or trial balance inputs. This skill applies standard accounting presentation, calculates key financial ratios, and produces executive summaries that translate numbers into actionable insights for stakeholders.

## Workflow

1. **Collect and Validate Financial Data**
   Ingest the source data: trial balance, general ledger exports, or categorized transaction records. Verify that debits equal credits and that the chart of accounts is complete. Identify the reporting period and comparative period (prior quarter or prior year). Flag any suspense account balances or unreconciled items that need resolution before reporting.

2. **Apply Accounting Standards and Classify**
   Map accounts to their proper financial statement classification: current vs. non-current assets, current vs. long-term liabilities, revenue vs. other income, operating vs. non-operating expenses. Apply accrual adjustments for prepaid expenses, deferred revenue, depreciation, and accrued liabilities. Ensure revenue recognition follows the applicable standard (ASC 606 for US GAAP or IFRS 15).

3. **Generate Financial Statements**
   Produce the three core statements in standard format. The income statement shows revenue through net income with gross profit and operating income subtotals. The balance sheet presents assets, liabilities, and equity with current/non-current breakdowns. The cash flow statement reconciles net income to operating cash flow, then shows investing and financing activities.

4. **Calculate Financial Ratios**
   Compute key ratios from the generated statements: gross margin, operating margin, net margin, current ratio, quick ratio, debt-to-equity, return on equity, days sales outstanding, inventory turnover, and free cash flow yield. Compare each ratio to the prior period and flag significant changes (>10% shift).

5. **Write Executive Summary**
   Synthesize the numbers into a narrative summary for non-financial stakeholders. Lead with the headline (revenue growth, profitability trend, cash position), then explain the 2-3 most significant drivers of performance. Highlight risks and call out items requiring management attention. Keep it to one page.

## Usage

Provide a trial balance, chart of accounts, or transaction-level data for the reporting period. Specify the reporting standard (GAAP or IFRS), period, and which statements you need.

**Example prompt:**
> Generate a Q3 2024 income statement from this trial balance data. Compare to Q3 2023. Include gross margin, operating margin, and an executive summary. We use US GAAP.

## Examples

### Example 1: Quarterly Income Statement

**Input:** Trial balance for Q3 2024 with comparative Q3 2023 data for a mid-size e-commerce company.

**Output:**

**Consolidated Income Statement — Q3 2024**

| Line Item                        | Q3 2024      | Q3 2023      | Change $     | Change % |
|----------------------------------|--------------|--------------|--------------|----------|
| **Revenue**                      |              |              |              |          |
| Product Revenue                  | $2,840,000   | $2,310,000   | +$530,000    | +22.9%   |
| Service Revenue                  | $460,000     | $380,000     | +$80,000     | +21.1%   |
| **Total Revenue**                | **$3,300,000** | **$2,690,000** | **+$610,000** | **+22.7%** |
| Cost of Goods Sold               | ($1,254,000) | ($1,049,100) | -$204,900    | +19.5%   |
| **Gross Profit**                 | **$2,046,000** | **$1,640,900** | **+$405,100** | **+24.7%** |
| Gross Margin                     | 62.0%        | 61.0%        |              | +1.0pp   |
|                                  |              |              |              |          |
| **Operating Expenses**           |              |              |              |          |
| Sales & Marketing                | ($594,000)   | ($510,800)   | -$83,200     | +16.3%   |
| Research & Development           | ($462,000)   | ($376,600)   | -$85,400     | +22.7%   |
| General & Administrative         | ($264,000)   | ($229,900)   | -$34,100     | +14.8%   |
| **Total Operating Expenses**     | **($1,320,000)** | **($1,117,300)** | **-$202,700** | **+18.1%** |
| **Operating Income**             | **$726,000** | **$523,600** | **+$202,400** | **+38.7%** |
| Operating Margin                 | 22.0%        | 19.5%        |              | +2.5pp   |
|                                  |              |              |              |          |
| Interest Expense                 | ($18,000)    | ($24,000)    | +$6,000      | -25.0%   |
| Other Income                     | $12,000      | $8,000       | +$4,000      | +50.0%   |
| **Income Before Tax**            | **$720,000** | **$507,600** | **+$212,400** | **+41.8%** |
| Income Tax Expense (25%)         | ($180,000)   | ($126,900)   | -$53,100     | +41.8%   |
| **Net Income**                   | **$540,000** | **$380,700** | **+$159,300** | **+41.8%** |
| Net Margin                       | 16.4%        | 14.2%        |              | +2.2pp   |

**Executive Summary:**
Revenue grew 22.7% year-over-year to $3.3M, driven by strong product demand and a 21% lift in service revenue from expanded support tiers. Gross margin improved 100 basis points to 62.0% as procurement renegotiations lowered COGS growth to 19.5%, below revenue growth. Operating leverage is emerging — opex grew only 18.1% against 22.7% revenue growth, expanding operating margin by 250 basis points to 22.0%. S&M efficiency improved with CAC payback declining from 14 months to 11 months. Net income of $540K is 42% above prior year. Key risk: R&D spend tracking at 14% of revenue requires monitoring to ensure product velocity justifies the investment.

### Example 2: Cash Flow Statement

**Input:** Q3 2024 income statement (above) plus balance sheet changes.

**Output:**

**Consolidated Statement of Cash Flows — Q3 2024**

| Line Item                                    | Q3 2024     |
|----------------------------------------------|-------------|
| **Operating Activities**                     |             |
| Net Income                                   | $540,000    |
| Depreciation & Amortization                  | $85,000     |
| Stock-Based Compensation                     | $42,000     |
| Changes in Working Capital:                  |             |
|   Accounts Receivable (increase)             | ($128,000)  |
|   Inventory (increase)                       | ($65,000)   |
|   Accounts Payable (increase)                | $47,000     |
|   Deferred Revenue (increase)                | $93,000     |
|   Accrued Liabilities (decrease)             | ($22,000)   |
| **Net Cash from Operations**                 | **$592,000** |
|                                              |             |
| **Investing Activities**                     |             |
| Purchase of Equipment                        | ($120,000)  |
| Capitalized Software Development             | ($75,000)   |
| **Net Cash Used in Investing**               | **($195,000)** |
|                                              |             |
| **Financing Activities**                     |             |
| Repayment of Term Loan                       | ($50,000)   |
| Proceeds from Stock Option Exercises         | $28,000     |
| **Net Cash Used in Financing**               | **($22,000)** |
|                                              |             |
| **Net Change in Cash**                       | **$375,000** |
| Cash — Beginning of Period                   | $1,240,000  |
| **Cash — End of Period**                     | **$1,615,000** |

**Key Ratios:**
| Ratio                  | Q3 2024 | Q3 2023 | Trend |
|------------------------|---------|---------|-------|
| Free Cash Flow         | $397,000| $268,000| +48%  |
| FCF Margin             | 12.0%   | 10.0%   | +2.0pp|
| Days Sales Outstanding | 35 days | 38 days | -3d   |
| Current Ratio          | 2.8x    | 2.3x    | +0.5x |
| Debt-to-Equity         | 0.15x   | 0.22x   | -0.07x|

**Analysis:** Operating cash flow of $592K exceeds net income by $52K, reflecting healthy earnings quality. The $128K AR increase is proportional to revenue growth and DSO actually improved by 3 days. Deferred revenue growth of $93K signals strong forward bookings. Free cash flow of $397K (12% margin) is up 48% YoY, funding the $120K equipment investment and $50K debt repayment while still growing cash reserves by $375K. The balance sheet is strengthening — leverage is declining and liquidity is ample at 2.8x current ratio.

## Best Practices

- Always present comparative periods (prior quarter or prior year) alongside current figures. Absolute numbers without context are not actionable.
- Calculate both dollar and percentage changes. A $50K variance means very different things for a $200K line item vs. a $5M line item.
- Reconcile the three statements — net income on the P&L should flow to retained earnings on the balance sheet and be the starting point of the cash flow statement.
- Present ratios alongside raw numbers. Margins, turns, and coverage ratios are how experienced readers evaluate financial health.
- Keep the executive summary under one page and lead with the conclusion, not the methodology.
- Round appropriately for the audience — board presentations use thousands or millions, operational reviews may need exact figures.

## Edge Cases

- **Incomplete trial balance:** If accounts are missing, note the gap explicitly rather than producing a statement that doesn't balance. A balance sheet where assets ≠ liabilities + equity is a red flag, not a rounding error.
- **Mid-period accounting changes:** If the company changed depreciation methods, revenue recognition policies, or made other accounting changes, present prior period figures on both the old and new basis with a reconciliation note.
- **Negative gross margin:** This is unusual but legitimate for early-stage hardware companies or marketplace businesses with upfront subsidies. Call it out in the summary and explain the path to positive margin.
- **Non-GAAP adjustments:** When management requests adjusted EBITDA or other non-GAAP metrics, present them clearly labeled alongside GAAP figures. Include a reconciliation from the GAAP measure to the non-GAAP measure.
- **Consolidated vs. segment reporting:** If the entity has multiple business segments, generate both consolidated statements and segment-level breakdowns. Eliminate inter-company transactions in the consolidation and note any material transfer pricing.
