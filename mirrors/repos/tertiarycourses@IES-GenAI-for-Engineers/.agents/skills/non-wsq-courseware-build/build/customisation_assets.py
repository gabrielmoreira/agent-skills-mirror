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
description: Use when I ask for a Pareto chart, an 80/20 or failure-mode analysis, or the vital few categories in a work-order table column.
---
# Water-service Pareto Chart
## Inputs
Use the table and the column I name, for example tblWorkOrders and Failure_Mode, Job_Category or Site. Count all work orders unless I ask for a subset: backlog means Status is neither Closed nor Cancelled; overdue means backlog with Due_Date before the date in Control!B2. If I do not name a table or column, ask me. Never change the source table or unrelated sheets.
## Method
1) Count the rows for each value of the column and sort from highest to lowest; break ties alphabetically.
2) Create a sheet named Pareto_<column name> (add _Overdue or _Backlog for a subset). If it exists, replace only its contents.
3) Build a summary table with formulas that read the source table: Category, Count, Share %, Cumulative %, and a Total row.
4) Create one combo chart: Count as columns, highest first, and Cumulative % as a dark grey line with markers on a secondary axis from 0% to 100%.
5) Give the columns the Northstar colours (navy #1F4E79, blue #2E75B6, teal #2A9D8F), add data labels and axis titles, no legend, and a title that states the finding, for example "3 failure modes cause 78% of all work orders".
6) Under the table, list the vital few: the categories needed to reach 80% and their combined share.
## Checks
The Count total must equal the number of rows counted. The last Cumulative % must be 100%. Report the row count, the top category and how many categories reach 80%. A Pareto shows where work concentrates; confirm the root cause on site before acting.
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


DECK_DESIGN_SKILL = '''---
name: northstar-deck-design
description: Use when I ask to make a presentation look professional, apply the Northstar brand or redesign plain slides.
---
# Northstar deck design
## Rules
1) Keep every slide, number, chart value and fact. Change only the design; never add facts.
2) Fonts: Segoe UI Semibold for titles (28-32 pt) and Segoe UI for body text (16-20 pt).
3) Colours: navy #1F4E79 for the header bar and titles, blue #2E75B6 and teal #2A9D8F for accents, light grey #F2F4F7 for cards, dark grey #404040 for body text, white slide background.
## Steps
1) Make slide 1 a title slide: navy background, large white title, a teal subtitle line, "Northstar Water Services" and the date.
2) Give every other slide a navy header bar across the top with the title in white and a thin teal line under it.
3) Turn key numbers into KPI cards: rounded light-grey rectangles with a big bold navy number and a short label under it.
4) Cut long text to at most 4 short bullets, or turn it into 2-4 icon cards. Leave plenty of white space and use the same margins on every slide.
5) Recolour charts to navy, blue and teal, with data labels and no gridlines.
6) Add a footer to every slide except slide 1: "Northstar Water Services | 30 September 2026" on the left and the slide number on the right.
## Checks
Check every slide: same fonts and colours, nothing overlaps or runs off the slide, and every number is unchanged. List any slide you could not fix.
'''
