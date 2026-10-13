---
name: pareto-chart
description: Use when I ask for a Pareto chart, an 80/20 analysis or the vital few categories in a table column. Counts each category, sorts them from highest to lowest and draws a combo chart with a different colour for every column and a cumulative % line.
---

# Pareto chart

Show which few categories account for most of the total: a sorted count of every category, a cumulative % line, and a different colour for every column.

## Input
- A table and one category column in it, for example tblJobs and Job_Category. If I do not say which, ask me before you start.
- Optional: a threshold. The default is 80%.

## Steps
1. Never change the source table or unrelated sheets. You may replace only the matching Pareto_<column name> output sheet when rerunning this skill.
2. Create a new sheet named Pareto_<column name>, e.g. Pareto_Job_Category. If it already exists, replace its contents.
3. In A1 write "Pareto chart - <column name> in <table name>". In A2 write "Created by Copilot".
4. From A4 build a summary table with the headers Category, Count, Share %, Cumulative %. List every distinct value of the column once, sorted by Count from highest to lowest. Use formulas that read the source table so the summary updates when rows are added. Format Share % and Cumulative % as % with 1 decimal.
5. Add a Total row under the table. The Count total must equal the number of rows in the source table.
6. Create one combo chart from the summary: Count as columns on the primary axis and Cumulative % as a line with markers on a secondary axis fixed from 0% to 100%.
7. Give every column its own colour (vary colours by point, or set each point separately) from a palette of clearly different colours. Make the cumulative line dark grey. Never use one colour for all the columns.
8. Format the chart cleanly: white background, no border, shadow or gradient, data labels on the columns, no legend, axis titles "Count" and "Cumulative %", and category labels that are easy to read. The title states the finding, for example "<n> of <m> categories make up <x>% of the total".
9. Place the chart to the right of the summary table, starting at column G and about 18 rows high. Freeze the header row and do not merge cells.
10. Under the table, add "Vital few": the categories needed to reach the threshold and their combined share.

## Check before you finish
- The Count total equals the number of rows in the source table.
- Report in your reply: the number of rows, the number of categories, the top category with its count and share, and how many categories reach the threshold.
