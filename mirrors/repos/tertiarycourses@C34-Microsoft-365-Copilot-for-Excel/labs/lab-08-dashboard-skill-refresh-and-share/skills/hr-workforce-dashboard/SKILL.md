---
name: hr-workforce-dashboard
description: Use when I ask for a workforce, headcount or attrition dashboard from an employee table. Builds checks, helper columns, PivotTables, KPI cards, charts and slicers, and verifies every KPI.
---

# HR workforce dashboard

Build a one-page, interactive workforce dashboard that HR leaders can trust and safely share.

## Before you start
1. Read the .Rules sheet and follow it. If there is no .Rules sheet, ask me for the period and the KPI definitions.
2. Find the employee table (e.g. tblEmployees) with Department, Location, Job_Level, Hire_Date, Exit_Date, Exit_Type and Status.
3. Never change or delete existing rows. Never show Employee_ID, salary or individual records on the dashboard.

## Steps
1. Add helper columns to the employee table, using the period in the rules:
   - Active_Start = TRUE if the employee was active on the first day of the period.
   - Exit_In_Period = TRUE if Exit_Date falls inside the period.
   - Tenure_Years = years from Hire_Date to Exit_Date, or to the last day of the period if still active, 1 decimal; 0 for anyone hired after the period.
2. Create a Checks sheet with independent COUNTIFS formulas, label in column A and formula in column B: active headcount (Status Active), headcount at period start, headcount at period end, exits in period, voluntary exits, attrition rate (exits / average of start and end headcount) and hires in period.
3. Put all PivotTables on a sheet named Dash_Data.
4. Build the dashboard sheet named in the rules:
   - Six KPI cards: Active headcount, Exits, Attrition rate, Voluntary attrition rate, Avg tenure of active staff, Hires.
   - Four charts: active headcount by Department (bar, sorted), attrition rate by Department (bar), hires vs exits by quarter (clustered column), active headcount by Location (bar).
   - Slicers for Location and Job_Level connected to every PivotTable.
5. Follow the layout and colours in the rules. Give every chart a title that states the finding.

## Verify before you finish
- Compare every KPI card with the Checks sheet, with no slicer selected, and report any difference.
- List any slicer combination that shows fewer than 5 employees.
- In your reply, give each KPI value and say which checks passed.
