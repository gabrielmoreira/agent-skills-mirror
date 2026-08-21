---
name: 3-statement-model
description: "Builds fully linked income-statement, balance-sheet, and cash-flow workbooks in openpyxl with working-capital, D&A, debt, and NOL schedules plus cash/RE tie-outs. Use for filling 3-statement templates or debugging a BS that will not balance. Do not use for DCF valuation or LBO debt waterfalls."
version: 1.0.1
author: Anthropic (adapted by Nous Research)
license: Apache-2.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [finance, three-statement, income-statement, balance-sheet, cash-flow, excel, openpyxl, modeling]
    related_skills: [excel-author, pptx-author, dcf-model, lbo-model]
---

## Overview

This skill produces fully-integrated 3-statement financial models as `.xlsx` files on disk using headless openpyxl. It covers template analysis, historical data population, projection formulas, supporting schedules (working capital, D&A, debt, NOL), cross-statement integrity checks, scenario toggles, and audit dashboards.

**Environment:** Headless openpyxl producing `.xlsx` on disk. Follow the `excel-author` skill's conventions for cell coloring, formulas, named ranges, and sensitivity tables. Recalculate before delivery by opening the workbook in Excel (full calculate + save). This folder does not ship a recalc helper.

Windows host is primary (PowerShell). Adjust path separators for macOS/Linux as needed.

## When to Use

- User asks to build or complete an integrated 3-statement financial model (IS + BS + CF)
- User provides a template `.xlsx` and asks to populate it with historicals and projections
- User needs working capital schedules, D&A roll-forwards, debt schedules, or NOL schedules linked to main statements
- User wants scenario analysis (Base / Upside / Downside) with a toggle
- User needs cross-statement integrity checks (balance check, cash tie-out, RE roll-forward)
- User asks to debug a broken model where BS doesn't balance or cash doesn't tie

**Trigger keywords:** 3-statement, integrated model, income statement, balance sheet, cash flow, working capital schedule, D&A roll-forward, debt schedule, NOL, balance check, cash tie-out, scenario toggle, financial model template

## Prerequisites

- `excel-author` skill installed (for cell coloring conventions, formula patterns, recalc script)
- Python with openpyxl available
- Template `.xlsx` file (if user provides one) or ability to build from scratch
- Historical financial data (from SEC filings, user-provided, or MCP data source)

**Reference files** (load when needed):
- `references/formulas.md` — Load when writing projection formulas, cross-statement linkages, or building the checks/audit tab. Contains all formula details for core linkages.
- `references/sec-filings.md` — Load ONLY when populating templates with public company data from SEC filings (10-K, 10-Q). Contains extraction guidance for EDGAR.

## Procedure

### Step 1: Analyze the Template Structure

Before entering any data, thoroughly review the template to understand its architecture.

**Identify tabs and their contents:**

| Common Tab Names | Contents to Look For |
|------------------|----------------------|
| IS, P&L, Income Statement | Income Statement |
| BS, Balance Sheet | Balance Sheet |
| CF, CFS, Cash Flow | Cash Flow Statement |
| WC, Working Capital | Working Capital Schedule |
| DA, D&A, Depreciation, PP&E | Depreciation & Amortization Schedule |
| Debt, Debt Schedule | Debt Schedule |
| NOL, Tax, DTA | Net Operating Loss Schedule |
| Assumptions, Inputs, Drivers | Driver assumptions and inputs |
| Checks, Audit, Validation | Error-checking dashboard |

**Template Review Checklist:**
1. Identify which tabs exist (not all templates include every schedule)
2. Note any template-specific tabs not listed above
3. Understand tab dependencies (e.g., which schedules feed into the main statements)
4. Locate input cells vs. formula cells on each tab

**Identify row structure:**
- Locate the model title at top of each tab
- Identify section headers and their visual separation
- Find the units row indicating $ millions, %, x, etc.
- Note column headers distinguishing Actuals vs. Estimates periods
- Confirm period labels (e.g., FY2024A, FY2025E)
- Identify input cells vs. formula cells (typically distinguished by font color)

**Identify column structure:**
- Confirm line item labels in leftmost column
- Verify historical years precede projection years
- Note the visual border separating historical from projected periods
- Check for consistent column order across all tabs

**Review named ranges:**
- Check existing named ranges (Formulas → Name Manager in Excel, or via openpyxl `wb.defined_names`)
- Common named ranges: Revenue growth rates, cost percentages, key outputs (Net Income, EBITDA, Total Debt, Cash), scenario selector cell
- Ensure inputs are entered in cells that feed into these named ranges

**Map the template's flow:**
- Identify which tabs feed into others (e.g., Assumptions → IS → BS → CF)
- Note any supporting schedules and their linkages to main statements
- Document the template's specific line items and structure before populating

> **VERIFY WITH USER:** After mapping the template, show the user which tabs/sections you've identified and confirm before touching any cells.

### Step 2: Populate Historical Data

**Golden Rules for Data Entry:**

| Rule | Description |
|------|-------------|
| Only edit input cells | Never overwrite cells containing formulas unless intentionally replacing the formula |
| Preserve cell references | When copying data, use Paste Values (Ctrl+Shift+V) to avoid overwriting formulas with source formatting |
| Match the template's units | Verify if template uses thousands, millions, or actual values before entering data |
| Respect sign conventions | Follow the template's existing sign convention (e.g., expenses as positive or negative) |
| Check for circular references | If the template uses iterative calculations, ensure Enable Iterative Calculation is turned on |

**Safe data entry process:**
1. Identify the exact cells designated for input (usually highlighted or labeled)
2. Enter historical data first, then verify formulas are calculating correctly for those periods
3. Enter assumption drivers that feed forecast calculations
4. Review calculated outputs to confirm formulas are working as intended
5. If a formula cell must be modified, document the original formula before making changes

**Handling pre-built formulas:**
- If formulas reference cells you haven't populated yet, expect temporary errors (#REF!, #DIV/0!) until all inputs are complete
- When formulas produce unexpected results, trace precedents to identify missing or incorrect inputs
- Never delete rows/columns without checking for formula dependencies across all tabs

> **VERIFY WITH USER:** After populating historicals, show the user the historical block and confirm values/periods match source data.

### Step 3: Build Income Statement Projections

**CRITICAL — Formulas over hardcodes (non-negotiable):**
- Every projection cell, roll-forward, linkage, and subtotal MUST be an Excel formula — never a pre-computed value
- When using Python/openpyxl: write formula strings (`ws["D15"] = "=D14*(1+Assumptions!$B$5)"`), NOT computed results (`ws["D15"] = 12500`)
- The ONLY cells that should contain hardcoded numbers are: (1) historical actuals, (2) assumption drivers in the Assumptions tab
- If you find yourself computing a value in Python and writing the result to a cell — STOP. Write the formula instead.
- Why: the model must flex when scenarios toggle or assumptions change. Hardcodes break every downstream integrity check silently.

**Projection period:**
- Templates typically project 5 years forward from last historical year
- Verify historical (A) vs. projected (E) columns are clearly separated
- Confirm columns use fiscal year notation (e.g., FY2024A, FY2025E)

**IS Quality Checks:**
- Revenue figures match source data for historical periods
- All expense line items sum to reported totals
- Subtotals (Gross Profit, EBIT, EBT, Net Income) calculate correctly
- Tax calculation logic is appropriate (handles losses correctly)
- Forecast drivers reference assumptions tab (no hardcodes)
- Period-over-period changes are directionally reasonable

> **VERIFY WITH USER:** After building IS projections, run the subtotal checks, show the user the projected IS, confirm before moving to BS.

### Step 4: Build Balance Sheet Projections

**BS Quality Checks:**
- Assets = Liabilities + Equity for every period (primary check)
- Cash balance matches Cash Flow Statement ending cash
- Working capital accounts tie to supporting schedules (if applicable)
- Retained Earnings rolls forward correctly: Prior RE + Net Income - Dividends +/- Adjustments = Ending RE
- Debt balances tie to debt schedule (if applicable)
- All balance sheet items have appropriate signs (assets positive, most liabilities positive)

> **VERIFY WITH USER:** After building BS, show the user the balance check (Assets = L+E) for every period, confirm before moving to CF.

### Step 5: Build Cash Flow Statement Projections

**CF Quality Checks:**
- Net Income at top of CFO matches Income Statement Net Income
- Non-cash add-backs (D&A, SBC, etc.) tie to their source schedules/statements
- Working capital changes have correct signs (increase in asset = use of cash = negative)
- CapEx ties to PP&E schedule or fixed asset roll-forward
- Financing activities tie to changes in debt and equity accounts on BS
- Ending Cash matches Balance Sheet Cash
- Beginning Cash equals prior period Ending Cash

**Sign Convention Reference:**

| Statement | Item | Sign Convention |
|-----------|------|-----------------|
| CFO | D&A, SBC | Positive (add-back) |
| CFO | ΔAR (increase) | Negative (use of cash) |
| CFO | ΔAP (increase) | Positive (source of cash) |
| CFI | CapEx | Negative |
| CFF | Debt issuance | Positive |
| CFF | Debt repayments | Negative |
| CFF | Dividends | Negative |

> **VERIFY WITH USER:** After building CF, show the user the cash tie-out (CF ending cash = BS cash), confirm before finalizing.

### Step 6: Build Supporting Schedules

**Working Capital Schedule:**
- AR, Inventory, AP tie to BS
- DSO, DIO, DPO reasonability checks (flag if outside normal ranges)
- Opening balances equal prior period closing balances

**D&A / PP&E Schedule:**
- Roll-forward logic: Beginning PP&E + CapEx - Disposals = Ending PP&E
- D&A ties to IS and CF (as non-cash add-back)
- CapEx ties to CF (investing activities)

**Debt Schedule:**
- Total Debt ties to BS (Current + LT Debt)
- Interest calculation ties to IS
- Roll-forward: Beginning Debt + Issuances - Repayments = Ending Debt

**NOL Schedule:**
- Beginning NOL (Year 1 / Formation) = 0 (new business starts with zero NOL)
- NOL increases only when EBT < 0 (losses must be realized to generate NOL)
- DTA ties to BS (NOL Schedule DTA = BS Deferred Tax Asset)
- NOL utilization ≤ 80% of EBT (post-2017 federal limitation)
- NOL balance is non-negative (cannot utilize more than available)
- NOL generated only when EBT < 0
- Tax expense = 0 when taxable income ≤ 0

**Equity Financing:**
- Equity issuance proceeds tie to BS Common Stock/APIC increase
- Cash increase from equity = Equity account increase (must balance)
- Equity Raise Tie-Out: ΔCommon Stock/APIC (BS) = Equity Issuance (CFF) (must = 0)
- Year 0 Equity Tie-Out: Equity Raised (Year 0) = Beginning Equity Capital (Year 1)

### Step 7: Cross-Statement Integrity Checks

After validating individual sheets, confirm the three statements are properly integrated:

| Check | Formula | Expected Result |
|-------|---------|-----------------|
| Balance Sheet Balance | Assets - Liabilities - Equity | = 0 |
| Cash Tie-Out | CF Ending Cash - BS Cash | = 0 |
| Cash Monthly vs Annual | Closing Cash (Monthly) - Closing Cash (Annual) | = 0 |
| Net Income Link | IS Net Income - CF Starting Net Income | = 0 |
| Retained Earnings | Prior RE + NI + SBC - Dividends - BS Ending RE | = 0 |
| Equity Financing | ΔCommon Stock/APIC (BS) - Equity Issuance (CFF) | = 0 |
| Year 0 Equity | Equity Raised (Year 0) - Beginning Equity Capital (Year 1) | = 0 |

Load `references/formulas.md` for all formula details when building the Checks/Audit tab.

### Step 8: Scenario Analysis (Base / Upside / Downside)

Use a scenario toggle (dropdown) in the Assumptions tab with CHOOSE or INDEX/MATCH formulas.

| Scenario | Description |
|----------|-------------|
| Base Case | Management guidance or consensus estimates |
| Upside Case | Above-guidance growth, margin expansion |
| Downside Case | Below-trend growth, margin compression |

**Key Drivers to Sensitize:** Revenue growth, Gross margin, SG&A %, DSO/DIO/DPO, CapEx %, Interest rate, Tax rate.

**Scenario Audit Checks:**
- Toggle switches all statements
- BS balances in all scenarios
- Cash ties out in all scenarios
- Hierarchy holds: Upside > Base > Downside for NI, EBITDA, FCF, margins
- Credit metrics: Upside < Base < Downside for leverage (inverted — lower is better)

### Step 9: Margin Analysis (Optional — Only if Prompted)

> Only perform margin analysis if prompted by the user or if the template explicitly requires it. If no prompt is given, skip this section.

| Margin | Formula | What It Measures |
|--------|---------|------------------|
| Gross Margin | Gross Profit / Revenue | Pricing power, production efficiency |
| EBITDA Margin | EBITDA / Revenue | Core operating profitability |
| EBIT Margin | EBIT / Revenue | Operating profitability after D&A |
| Net Income Margin | Net Income / Revenue | Bottom-line profitability |

Display margin percentages directly below each profit line item on the IS tab.

### Step 10: Credit Metrics (Optional — Only if Prompted)

> Only perform credit analysis if prompted by the user or if the template explicitly requires it. If no prompt is given, skip this section.

| Metric | Formula | What It Measures |
|--------|---------|------------------|
| Total Debt / EBITDA | Total Debt / LTM EBITDA | Leverage multiple |
| Net Debt / EBITDA | (Total Debt - Cash) / LTM EBITDA | Leverage net of cash |
| Interest Coverage | EBITDA / Interest Expense | Ability to service debt |
| Debt / Total Cap | Total Debt / (Total Debt + Equity) | Capital structure |
| Debt / Equity | Total Debt / Total Equity | Financial leverage |
| Current Ratio | Current Assets / Current Liabilities | Short-term liquidity |
| Quick Ratio | (Current Assets - Inventory) / Current Liabilities | Immediate liquidity |

**Credit Metric Hierarchy Checks:**
- Leverage: Upside < Base < Downside (lower is better)
- Coverage: Upside > Base > Downside (higher is better)
- Liquidity: Upside > Base > Downside (higher is better)

If debt covenants are known, add explicit compliance checks comparing actual metrics to covenant thresholds.

### Step 11: Build Audit/Checks Dashboard

Consolidate all validation checks into the Checks/Audit tab:

**Check Categories:**

1. **Currency Consistency** — Currency identified and documented in Assumptions; all tabs use consistent currency symbol and scale; units row matches model currency
2. **Balance Sheet Integrity** — Assets = Liabilities + Equity for each period
3. **Cash Flow Integrity** — Cash ties to BS; monthly vs annual cash; NI ties to IS; D&A ties to schedule; SBC ties to IS; ΔAR, ΔInventory, ΔAP tie to WC schedule; CapEx ties to DA schedule
4. **Retained Earnings** — Prior RE + NI + SBC - Dividends = Ending RE; show component breakdown for debugging
5. **Working Capital** — AR, Inventory, AP tie to BS; DSO, DIO, DPO reasonability checks
6. **Debt Schedule** — Total Debt ties to BS; Interest calculation ties to IS
7. **Equity Financing** — Equity issuance ties to BS Common Stock/APIC increase; Year 0 equity tie-out
8. **NOL Schedule** — Beginning NOL = 0; NOL increases only on losses; DTA ties to BS; NOL utilization ≤ 80% of EBT; non-negative balance
9. **Scenario Hierarchy** — Absolute metrics: Upside > Base > Downside; Margins: Upside > Base > Downside; Credit metrics: Upside < Base < Downside for leverage
10. **Formula Integrity** — COGS, S&M, G&A, R&D, SBC driven by % of Revenue; consistent formulas across projection years; no #REF!, #DIV/0!, #VALUE! errors
11. **Credit Metric Thresholds** — Flag metrics as Green/Yellow/Red based on covenant thresholds

**Master Check Formula:**
- If all sections pass → "✓ ALL CHECKS PASS"
- If any section fails → "✗ ERRORS DETECTED - REVIEW BELOW"

### Step 12: Final Review and Recalculate

1. Toggle through all scenarios to verify checks pass in each case
2. Review all #REF!, #DIV/0!, #VALUE!, and #NAME? errors and resolve or document
3. Confirm all input cells have been populated (search for placeholder values)
4. Verify units are consistent across all tabs
5. Save a clean version before making any additional modifications
6. Recalculate before delivery: open the `.xlsx` in Excel, force a full calculate, and save. This folder does not ship a recalc helper.

## Formatting — Professional Blue/Grey Palette

**Keep colors minimal.** Use only blues and greys for cell fills. Do NOT introduce greens, yellows, oranges, or multiple accent colors — a clean model uses restraint.

| Element | Fill | Font |
|---|---|---|
| Section headers (IS / BS / CF titles) | Dark blue `#1F4E79` | White bold |
| Column headers (FY2024A, FY2025E, etc.) | Light blue `#D9E1F2` | Black bold |
| Input cells (historicals, assumption drivers) | Light grey `#F2F2F2` or white | Blue `#0000FF` |
| Formula cells | White | Black |
| Cross-tab links | White | Green `#008000` |
| Check rows / key totals | Medium blue `#BDD7EE` | Black bold |

**That's 3 blues + 1 grey + white.** If the template has its own color scheme, follow the template instead.

Font color signals *what* a cell is (input/formula/link). Fill color signals *where* you are (header/data/check).

## Data Sources — MCP First, Web Fallback

- **If you have any structured financial-data MCP configured** (Hermes supports MCP — see `native-mcp` skill), prefer it for point-in-time comps, precedent transactions, and filings.
- **Otherwise**, fall back to:
  - `web_search` / `web_extract` against SEC EDGAR (`https://www.sec.gov/cgi-bin/browse-edgar`) for US filings
  - Company IR pages for press releases, earnings decks
  - `browser_navigate` for interactive data portals
  - User-provided data (explicitly ask when the context doesn't have it)
- **Never fabricate.** If a multiple, precedent, or filing number can't be sourced, flag the cell as `[UNSOURCED]` and surface it to the user.

For SEC filings extraction guidance, load `references/sec-filings.md`.

## Pitfalls

### Hardcodes Break Models Silently
- **Pitfall:** Computing a value in Python and writing the result to a cell instead of writing the formula.
- **Impact:** The model won't flex when scenarios toggle or assumptions change. Every downstream integrity check breaks silently.
- **Fix:** Always write formula strings in openpyxl. The ONLY hardcoded numbers should be historical actuals and assumption drivers.

### Circular Reference from Interest Expense
- **Pitfall:** Interest → Net Income → Cash → Debt Balance → Interest creates a circular reference.
- **Fix:** Enable iterative calculation in Excel: File → Options → Formulas → Enable iterative calculation. Set maximum iterations to 100, maximum change to 0.001. Add a circuit breaker toggle in Assumptions tab.

### Mixed Absolute/Relative References
- **Pitfall:** Incorrect reference types cause wrong results when formulas are copied across periods.
- **Fix:** Use `$` for absolute references to assumption cells (e.g., `Assumptions!$B$5`), relative references for period-to-period calculations.

### Deleting Rows/Columns Without Checking Dependencies
- **Pitfall:** Deleting a row or column breaks formulas across all tabs that reference it.
- **Fix:** Never delete rows/columns without checking for formula dependencies across all tabs. Use Trace Dependents first.

### Sign Convention Errors in Cash Flow
- **Pitfall:** Increase in an asset (e.g., AR) shown as positive instead of negative (use of cash).
- **Fix:** Follow the sign convention table above. Increase in asset = use of cash = negative. Increase in liability = source of cash = positive.

### NOL Utilization Exceeding 80% Limit
- **Pitfall:** Utilizing more than 80% of EBT for NOL carryforward (post-2017 federal limitation).
- **Fix:** Cap NOL utilization at 80% of EBT. Add an explicit check in the NOL schedule.

### Populating Entire Model End-to-End Without User Checkpoints
- **Pitfall:** Building the complete model and presenting it at once, only to find fundamental errors in the IS that cascade through BS and CF.
- **Fix:** Break at each statement. Show the work. Catch errors early. Follow the verify-with-user checkpoints after each step.

### Inconsistent Units Across Tabs
- **Pitfall:** One tab uses thousands, another uses millions, creating order-of-magnitude errors.
- **Fix:** Verify units before entering data. Check the units row on every tab. Document the model's currency and scale in Assumptions.

## Verification

### Formula Integrity Checks

| Check Type | Method |
|------------|--------|
| Trace precedents | Select a formula cell → Formulas → Trace Precedents to verify it references correct inputs |
| Trace dependents | Verify key inputs flow to expected output cells |
| Evaluate formula | Use Formulas → Evaluate Formula to step through complex calculations |
| Check for hardcodes | Projection formulas should reference assumptions, not contain hardcoded values |
| Test with known values | Input simple test values to verify formulas produce expected results |
| Cross-tab consistency | Ensure the same formula logic applies across all projection periods |
| Find inconsistent formulas | Use Ctrl+\ to find differences across columns |

### Cross-Statement Integrity Checks

Run these checks after model completion. All must equal zero:

| Check | Formula | Expected Result |
|-------|---------|-----------------|
| Balance Sheet Balance | `=Assets - Liabilities - Equity` | 0 |
| Cash Tie-Out | `=CF_Ending_Cash - BS_Cash` | 0 |
| Net Income Link | `=IS_Net_Income - CF_Starting_Net_Income` | 0 |
| Retained Earnings | `=Prior_RE + NI + SBC - Dividends - BS_Ending_RE` | 0 |
| Equity Financing | `=ΔCommon_Stock_APIC - Equity_Issuance_CFF` | 0 |

### Recalculation Verification

Open the output `.xlsx` in Excel, force a full calculate, save, and confirm it opens without formula errors. This folder does not ship a recalc helper.

### Quick Debug Workflow

When Master Status shows errors:
1. Scroll to find red-highlighted sections on the Checks tab
2. Identify which check category has failures
3. Navigate to source tab to investigate
4. Fix the underlying issue
5. Return to Checks tab to verify resolution
6. Re-open in Excel and force a full calculate

### Final Delivery Checklist

- [ ] All historical data matches source documents
- [ ] All projection cells are formulas (no hardcodes)
- [ ] BS balances for every period (Assets = L + E)
- [ ] CF ending cash = BS cash for every period
- [ ] RE roll-forward ties for every period
- [ ] All scenarios toggle correctly and pass checks
- [ ] No #REF!, #DIV/0!, #VALUE!, #NAME? errors
- [ ] Units consistent across all tabs
- [ ] Workbook fully recalculates and opens in Excel
- [ ] All `[UNSOURCED]` cells flagged to user

## Related Skills

- `excel-author` — Cell coloring conventions, formula patterns, recalc script, named ranges, sensitivity tables
- `dcf-model` — DCF valuation built on top of 3-statement model outputs
- `lbo-model` — LBO transaction model with debt waterfall
- `pptx-author` — Presentation output of model results

## Attribution

Adapted from Anthropic's Claude for Financial Services plugin suite (Apache-2.0). The Office-JS / Cowork live-Excel paths have been removed; this version targets headless openpyxl via the `excel-author` skill's conventions. Original: https://github.com/anthropics/financial-services
