---
name: interactive-dashboard
description: Build a one-page interactive Excel dashboard (KPI tiles, finding-led charts and slicers) from any named table, following the workbook .Rules, with verified KPIs.
---
# Interactive dashboard from any table
## Before you start
Read the visible .Rules sheet and follow it. Find the named source table (for example tblData) and the reporting date in Control!B2. If the table, date, KPI definitions or category columns are missing, ask for them. Never change or delete source rows. Do not show personal data or individual records on the dashboard.
## Build
1. Plan first: list six KPIs with exact definitions and denominators, three charts that each answer a manager's question, and two or three category columns for slicers. Wait for approval.
2. Put chart summaries, chart-title formulas and KPI checks on a sheet named Dashboard_Summaries. Use structured references that expand with the table, never fixed row ranges.
3. Dashboard sheet: title in A1, data-as-at date and scope in A2, six KPI tiles in row 4 (title, large value, short definition, Checks: PASS or REVIEW), charts in a grid below, slicers on the right connected to the source table. Never merge cells; hide gridlines.
4. Multiply every KPI and summary by SUBTOTAL(103,OFFSET(...)) row visibility so the slicers filter every tile and chart together.
5. Style: white text on navy #1F4E79, blue #2E75B6 or teal #2A9D8F tiles; chart titles that state the finding from a cell formula; data labels; no gridlines; rates as % with one decimal.
## Verify before you finish
Compare every KPI with an independent COUNTIFS/SUMIFS with all slicers cleared, then for one slicer selection and one empty selection (show N/A for zero denominators). Confirm each chart total equals the selected total. Report each KPI value and which checks passed. Rerunning must replace only Dashboard and Dashboard_Summaries after asking.
