---
name: maintenance-reporting
description: Use when preparing Northstar maintenance reports, Excel analysis or management slides from verified work-order data.
---
# Northstar maintenance reporting
## Inputs and scope
Require tblWorkOrders or a verified Word snapshot, reporting date and filter scope. If absent ask for them; never invent a fact. The reporting date for this course is 2026-09-30.
## Measures
Backlog excludes Closed and Cancelled. Overdue means backlog with Due_Date strictly earlier than reporting date. On-time closure rate is count of Closed with Closed_Date <= Due_Date divided by Closed; use N/A for zero Closed. Cost is SUM of Cost_SGD over the selected scope, not a budget.
## Excel behaviour
Preserve Work_Orders, source IDs and tblTechnicians. Do not overwrite source status or Assigned_To. Put proposed allocations in Assignment_Proposals with current owner, proposed owner, category/capacity check, reason and manager decision. Missing owner remains blank. Create or replace only your named output sheets Maintenance_Summary, Maintenance_Charts and Assignment_Proposals after asking before replacing an existing output. Never delete unrelated sheets. Recalculate and reconcile count, cost and denominator with Control; record filter scope. Report unresolved issues as UNKNOWN. A rerun must not duplicate output sheets or alter source records.
## PowerPoint behaviour
Use the attached verified Word snapshot and the existing deck design. Do not assume access to an Excel chat, local path or live workbook. Respect the requested slide count: four slides for the initial update; eight for the management report (overview, portfolio, backlog by site, status/category mix, SLA/overdue, assignment/capacity, proposed actions, decision request). Preserve the requested count when refining an existing deck. Preserve numbers, units, as-at date and scope; add source notes. Separate observed data from proposed action. Add no causal, savings or approval claim without evidence. Refine existing slides rather than duplicating them. Retain unrelated slides unless asked.
## Brand and checks
White background, navy titles #0B3060, blue #1F6FEB, teal #13A89E, generous whitespace, one main message per slide, labelled editable charts where feasible. Never encode status with colour alone. Verify every headline against its evidence, flag inconsistent totals, and stop if source date or scope differs. Log web/Word/Outlook/PowerPoint prompts manually: Excel cannot read those chats. Draft emails only; never send or confirm a reassignment.
