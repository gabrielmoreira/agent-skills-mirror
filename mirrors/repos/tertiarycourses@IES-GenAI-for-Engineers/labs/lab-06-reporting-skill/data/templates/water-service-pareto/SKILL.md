---
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
