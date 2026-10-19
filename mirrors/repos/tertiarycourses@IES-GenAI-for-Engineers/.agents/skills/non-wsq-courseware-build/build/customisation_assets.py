"""Learner-safe templates: account preferences, workbook rules and reusable Skills."""
PERSONAL_PREFS = '''Use S$ with two decimal places and thousands separators for currency displays.
Display dates as DD-MMM-YYYY.
Prefer structured references when writing Excel formulas.
Start explanations with a short plain-English summary before the detail.
'''
RULES = [
'## SOURCE AND SCOPE',
'Preserve Work_Orders, tblWorkOrders, Technicians, current Assigned_To values and source IDs.',
'Use the reporting date from Control!B2. State the selected Site, Job_Category, Status and Assigned_To scope beside every report.',
'Backlog excludes Closed and Cancelled. Overdue backlog has Due_Date strictly before Control!B2.',
'On-time closure rate uses Closed rows only, with Closed_Date <= Due_Date. Display N/A when no Closed rows remain.',
'## FORMATS AND VISUALS',
'Display recorded Cost_SGD as S$ with two decimals; keep underlying values exact. Show dates as DD-MMM-YYYY.',
'Use white backgrounds, navy titles, blue and teal accents, readable labels and named units; never use colour alone.',
'## DASHBOARD LAYOUT',
'Dashboard sheet: title in A1; Site, Job_Category, Status and Assigned_To dropdowns in B2:B5 (All plus source values); the six measures in B7:B12; data-as-at date and selected scope in D2.',
'Six KPI tiles in D4:I7, one column per tile: title in row 4, large value in row 5, short definition in row 6 and "Checks: PASS" in row 7.',
'Charts in a grid below the tiles: work orders by status and by job category side by side, then a full-width stacked bar by site (overdue backlog, other backlog, Closed, Cancelled).',
'Slicers for Site, Job_Category, Status and Assigned_To on the right of the tiles, connected to tblWorkOrders. KPI formulas use SUBTOTAL visibility so slicers and dropdowns both filter every tile and chart.',
'Put chart summaries, chart-title formulas and KPI checks on Dashboard_Summaries. Never merge cells. Hide gridlines on Dashboard.',
'## DASHBOARD STYLE',
'Tiles: white bold text on solid navy #1F4E79 (totals and rates), blue #2E75B6 (backlog, overdue) or teal #2A9D8F (Closed, cost).',
'Every chart title states the finding from a cell formula, e.g. "Changi Workshop has the most overdue backlog (18 of 50)".',
'Show data labels on bars; no gridlines; rates as % with one decimal. Each chart total must equal B7.',
'## OUTPUT AND REVIEW',
'Use structured table references. Preserve the visible .Rules sheet and unrelated sheets, charts and Prompt_Log.',
'Keep current owners separate from unapproved assignment proposals. Missing facts and approvals remain UNKNOWN.',
'Ask before replacing named output sheets. Reconcile every count, rate and chart against source rows; do not duplicate outputs on rerun.',
]
PARETO_SKILL = '''---
name: water-service-pareto
description: Create or refresh a verified Pareto Chart of Northstar water-service overdue backlog by a requested grouping column.
---
# Water-service Pareto Chart
## Required inputs
Require the actual source table, report date, selected scope, grouping column and count metric. Ask for missing inputs. In this course use tblWorkOrders, Control!B2 (2026-09-30), all sites and overdue-backlog count grouped by Job_Category or Site. Do not assume access to a web chat or another workbook.
## Source and workbook rules
Read the visible .Rules worksheet in column A. Preserve Work_Orders, Technicians, Control, Prompt_Log, .Rules, source IDs, statuses, owners and unrelated sheets. Resolve conflicting requirements explicitly; do not promise a universal precedence order or treat instructions as a security boundary.
## Method
Count rows where Status is neither Closed nor Cancelled and Due_Date is strictly before the report date. Group by the requested column. Sort count descending, then group label alphabetically for ties. Build a formula-backed Count, Cumulative_Count, Share and Cumulative_Percent summary. The last cumulative percentage is 100% when the total is positive; for zero total show N/A and explain there is no Pareto distribution.
## Output
Create only Pareto_<grouping column>, for example Pareto_Job_Category or Pareto_Site. Ask before replacing an existing matching output. Rebuild that output after review without duplicating summaries or charts. Preserve all other sheets and source records.
Create an editable Excel combo chart: descending count columns on the left axis and cumulative percentage line on the right axis fixed at 0%-100%. Label both axes, grouping, metric, date and scope. If the combo UI is unavailable, supply the correct summary and explain the manual combo-chart route; do not claim the chart exists.
## Checks
Reconcile the summary count to the eligible source rows. Check stable tie ordering, monotonic cumulative percentages and final 100%. Identify the first category set that reaches at least 80%; do not force a literal 80/20 split. Counts show contribution, not root cause, safety priority or approved actions. A rerun must preserve source records and unrelated outputs.
'''
DASHBOARD_SKILL = '''---
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
'''

WORK_ORDER_QA_SKILL = '''---
name: work-order-qa
description: Answer questions about Northstar Water Services work orders, backlog, overdue jobs, sites, technicians and service definitions from the agent's knowledge files, with definitions and citations.
---
# Northstar work-order Q&A
## Sources
Use only the agent's knowledge: Northstar_Work_Orders_Clean.xlsx (one table, 120 synthetic work orders) and Northstar_Service_Handbook.docx (sites, statuses, priorities, technicians, definitions and escalation). The reporting date is 30 September 2026. If a question needs a fact that is not in these files, say UNKNOWN and name the missing fact.
## Definitions
Backlog = Status is neither Closed nor Cancelled. Overdue = backlog with Due_Date strictly before 30 September 2026; a job due on 30 September is not overdue. On-time closure rate = Closed rows with Closed_Date on or before Due_Date divided by all Closed rows; N/A when there are no Closed rows. Unassigned = blank Assigned_To. Recorded cost = sum of Cost_SGD for the rows in scope; it is not a budget or saving.
## How to answer
1. Restate the scope you used: site, job category, status, owner and the reporting date.
2. Give the number or list first, then the definition you applied and how you counted it.
3. Show a small table when comparing sites, categories, statuses or technicians.
4. Cite the knowledge file (and sheet or handbook section) for every figure.
5. Check that parts add up to the stated total before answering.
## Boundaries
Never approve, assign, reassign, schedule, close or edit a work order, and never send messages. Present any owner suggestion as a proposal for a manager decision, with the category and available-hours evidence. Do not invent customers, people, phone numbers, causes, safety findings or savings. All data is synthetic training data.
'''

GENERIC_DASHBOARD_SKILL = '''---
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
'''
