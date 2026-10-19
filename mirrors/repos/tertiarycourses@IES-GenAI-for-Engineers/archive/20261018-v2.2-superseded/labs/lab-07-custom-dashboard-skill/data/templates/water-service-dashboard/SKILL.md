---
name: water-service-dashboard
description: Build or refresh an interactive Northstar water-service dashboard with source-linked measures, four shared filters and verified charts.
---
# Interactive water-service dashboard
## Inputs and context
Require the actual tblWorkOrders source, report date in Control!B2, requested output workbook and filter scope. Ask when inputs are absent. Read visible .Rules column A. Do not assume access to a web chat or an Excel conversation from another file.
## Preserve and review
Preserve Work_Orders, tblWorkOrders, source IDs/statuses/current owners, Technicians, Control, .Rules, Prompt_Log, Pareto_* and unrelated sheets. Plan before editing. Create or replace only Dashboard, Dashboard_Summaries, Filter_Lists and the specifically reviewed verification cells. Ask before replacing existing outputs. Retain one dashboard and one chart per requested visual on reruns.
## Interaction contract
Dashboard B2:B5 are Site, Job_Category, Status and Assigned_To, initially All. All bypasses that dimension; all other selections combine with AND logic. Blank owner records remain included by All. Use validation dropdown lists and structured references; worksheet AutoFilter alone is not proof that KPI formulas change; verify the visibility term before relying on slicers.
## Measures
B7 total selected work orders. B8 backlog: Status neither Closed nor Cancelled. B9 overdue backlog: backlog plus Due_Date strictly earlier than Control!B2. B10 Closed count. B11 on-time closed rate: selected Closed_Date <= Due_Date among Closed rows only; N/A when Closed count is zero. B12 recorded Cost_SGD across every selected status; it is not a budget or saving.
## Layout (follow .Rules DASHBOARD LAYOUT)
Title in A1. Keep B2:B5 dropdowns and B7:B12 measures as a slim sidebar in A:B. Put the data-as-at date and selected scope in D2. Six KPI tiles in D4:I7, one column per tile: title (row 4), large value (row 5), short definition (row 6), "Checks: PASS" or "Checks: REVIEW" (row 7). Charts in a grid below the tiles. Slicers for Site, Job_Category, Status and Assigned_To on the right, connected to tblWorkOrders. Put chart summaries, chart-title formulas and KPI checks on Dashboard_Summaries. Never merge cells; hide gridlines on Dashboard.
## Visuals and style (follow .Rules DASHBOARD STYLE)
Tiles use white bold text on solid navy #1F4E79, blue #2E75B6 or teal #2A9D8F. Build three editable charts from formula-backed summaries of the same selected rows: status (column), job category (bar) and site (full-width stacked bar: overdue backlog, other backlog, Closed, Cancelled). Every chart title is linked to a Dashboard_Summaries formula that states the finding, e.g. "Changi Workshop has the most overdue backlog (18 of 50)". Show data labels, no gridlines, rates as % with one decimal and cost as S$ with two decimals. Each chart total equals B7. Use references that expand with tblWorkOrders, never fixed 120-row ranges.
## Interaction
Multiply every measure by SUBTOTAL(103,OFFSET(...)) row visibility so slicers and dropdowns filter every tile and chart together (AND logic). Show a warning in D3 when a slicer hides rows.
## Verification and refresh
At the course baseline (2026-09-30, All): total120, Closed48, Cancelled12, backlog60, overdue50, on-time30/48 and recorded cost35827.50. These are checks for this synthetic snapshot, not universal future values. Test a site, no Closed rows and no selected rows. Append only the supplied two test rows in a separate sandbox: total122, Closed49, backlog61, overdue51, on-time31/49 and recorded cost36227.50. Compare all original120 records to the saved baseline and reconcile every chart. Return to the untouched120-row baseline for PowerPoint.
## Boundaries
Do not approve assignments, invent causes/customer impacts/savings, send email or claim native Skill execution without observed evidence. The PowerPoint handoff is a dated static snapshot, not an automatically linked dashboard.
