"""
"What it does" text for every step prompt on the prompts page, keyed by lab number
and prompt letter (the letters prompt_rows() assigns in step order).

build_prompts_page.py fails the build if a prompt has no explanation or an
explanation has no prompt, so after adding, removing or reordering a lab's prompts,
update the letters here to match.
"""

_LOG = ("Fills in your Prompt_Log: for each prompt you ran, what Copilot did and how you checked it. "
        "This is your record of the lab.")

EXPLAIN = {
    1: {
        "A": "Turns the raw Applications data into an Excel table named tblApplications, so every later prompt can "
             "refer to it by name. Copilot reports the columns and rows so you can confirm nothing was lost.",
        "B": "Asks Copilot to describe the data before you analyse it: what a row is, each column's type, the row "
             "count, the date range and the Stage and Source values. Chat only, so nothing changes.",
        "C": "Looks for data-quality problems - duplicate Application_IDs and misspelt Source labels - and counts "
             "each. It only reports; nothing is fixed yet.",
        "D": "Copilot shows its plan first, then highlights duplicate IDs in orange and adds a cleaned Source_Clean "
             "column. The original values stay untouched.",
        "E": "Checks whether each duplicate is a true copy or two different applications sharing an ID, with the "
             "row numbers of both.",
        "F": "Highlights in yellow the Source cells the cleanup changed and lists their IDs, so you can see exactly "
             "what was fixed.",
        "G": "Confirms the cleanup worked: no 'Linked In', no trailing spaces, and the table still has 242 rows.",
        "H": "Copilot's answer: applications, hires and hire rate by source, sorted by hires. You verify it with "
             "formulas in the next prompt.",
        "I": "Adds two COUNTIFS formulas on a Checks sheet so you can verify Copilot's hire counts with formulas "
             "you can see.",
        "J": "Asks the same question in a new chat with a different model. If the answers differ, the formulas on "
             "Checks decide which is right.",
        "K": "Highlights every hired candidate's row in light green so the hires stand out.",
        "L": "Sorts the table by interview score (highest first), then by days in the pipeline (shortest first).",
        "M": "Filters the table to Technology candidates at the Interview stage.",
        "N": "Asks how many rows the filter shows. Compare it with the count Excel shows at the bottom of the window.",
        "O": "Clears every filter and confirms all 242 rows are back, so later steps see the full data.",
        "P": _LOG,
    },
    2: {
        "A": "Adds a Recruiter_Name column that looks up each requisition's recruiter in tblRecruiters with "
             "XLOOKUP, showing \"Not found\" for an ID with no match.",
        "B": "Copilot explains the XLOOKUP in plain English and shows one row next to its match in tblRecruiters, "
             "so you can check the lookup by eye.",
        "C": "Adds Days_Open: how long each requisition has been open, using the report date in Control!B1 for "
             "those still open.",
        "D": "Shows one open and one closed requisition with the subtraction behind each, so you can confirm both "
             "halves of the rule.",
        "E": "Adds Fill_Rate - positions filled divided by openings - as a percentage.",
        "F": "Adds Est_Fee from the fee rule (filled x monthly salary x 12 x fee rate) in S$, and explains the "
             "formula.",
        "G": "Walks through the fee calculation for one requisition, JOB-2002, so you can check it by hand.",
        "H": "Adds an Ageing_Flag that marks open requisitions older than 45 days as \"Overdue\" and highlights "
             "those rows amber.",
        "I": "Asks how many requisitions are flagged Overdue. The next prompt checks this with an independent "
             "formula.",
        "J": "Puts independent control formulas on the Control sheet. Each pair must match; if one does not, one of "
             "Copilot's columns is wrong.",
        "K": "Asks which recruiter generated the most estimated fees, with every recruiter's total. Chat only.",
        "L": "Adds a SUMIFS check for the top recruiter so a formula confirms Copilot's answer. Replace <name> with "
             "the recruiter Copilot named.",
        "M": _LOG,
    },
    3: {
        "A": "Builds a PivotTable of total hires by month on Pivot_Trend, then a cleanly formatted line chart from "
             "it on the Charts sheet (top left). Answers Q1 Trend.",
        "B": "Adds a SUM of all hires and asks whether it matches the PivotTable grand total, and which month had "
             "the most hires.",
        "C": "Builds a PivotTable of 2026 hires by sector, then a bar chart from it on the Charts sheet (top right). "
             "Answers Q2 Comparison.",
        "D": "Sorts the bars from highest to lowest and makes the title say which sector led.",
        "E": "Adds a SUMIFS of Technology's 2026 hires. It must match Technology's bar.",
        "F": "Builds a 2026 funnel table (Applications to Hires) with SUMIFS on a new sheet, then a funnel chart on "
             "the Charts sheet (bottom left). Answers Q3 Funnel.",
        "G": "Shows the formula behind each funnel number, so you can confirm they are formulas, not typed values.",
        "H": "Adds Hire_Rate and Cost_per_Hire to tblSources, then a combo chart - rate as columns, cost as a line "
             "on a second axis - on the Charts sheet (bottom right). Answers Q4 Efficiency.",
        "I": "Asks for the best hire rate and the lowest cost per hire, with values, to compare with the chart.",
        "J": "Rewrites each chart title to state its finding, e.g. Technology led hiring in H1 2026.",
        "K": "Makes hires the same blue in every chart and adds thousands separators.",
        "L": "Makes the four charts the same size and lines them up in a 2 x 2 grid.",
        "M": "Adds alt text to every chart so screen-reader users know what it shows.",
        "N": "Copilot reviews each chart against the four questions: does the chart type fit, and one improvement. "
             "Chat only.",
        "O": _LOG,
    },
    4: {
        "A": "Lists the messy values in Status, Region and Client and groups the ones that mean the same thing "
             "(e.g. WIP and In Progress). Chat only - this is your cleanup checklist.",
        "B": "Writes the workbook rules into the .Rules sheet. Copilot reads them on every later prompt, so you do "
             "not have to repeat them.",
        "C": "Creates Orders_Clean, a cleaned copy of every order that follows the rules: standard statuses, "
             "regions, client names, dates and money.",
        "D": "Adds check formulas that count orders and distinct values and total the budget, so you can confirm "
             "the cleanup.",
        "E": "Adds Rate (looked up by Owner), Delivered_Value, Budget_Used and an Over_Budget flag to the clean "
             "table.",
        "F": "Adds two more checks - total delivered value and the over-budget count - then lists the over-budget "
             "orders.",
        "G": "Adds a new rule to .Rules: highlight over-budget rows in light red.",
        "H": "Re-applies every workbook rule to tblOrdersClean, including the new highlight rule.",
        "I": _LOG,
    },
    5: {
        "A": "Asks Copilot which of its built-in skills fit this job: the finance analysis and the model audit. "
             "Chat only.",
        "B": "Uses the chart-design skill to create a combo chart: MRR as columns and client count as a line on a "
             "second axis.",
        "C": "Uses chart-design again to polish the chart for a leadership slide: a finding-style title, axis "
             "titles and one data label.",
        "D": "The unit-economics skill plans, then calculates CAC, ARPA, margin, churn, LTV, LTV:CAC and payback on "
             "a new sheet and lists its assumptions. Review the plan before you approve it.",
        "E": "Builds independent check formulas for each unit-economics measure, so you can verify the skill's "
             "numbers.",
        "F": "Compares the check formulas with the Unit_Economics sheet and explains any difference.",
        "G": "Uses the check-model skill to audit Headcount_Budget for typed numbers, inconsistent formulas and "
             "totals that miss rows. It only reports.",
        "H": "Fixes the issues the audit found and gives the corrected FY2027 total cost.",
        "I": "Uses the theme-design skill to give the four sheets one consistent, professional look.",
        "J": _LOG,
    },
    6: {
        "A": "Copilot writes a complete SKILL.md for an interview-calendar skill: read tblInterviews, build a "
             "weekly calendar, flag clashes and summarise. Chat only - you save the text as the skill file.",
        "B": "Runs your new skill to build the interview calendar for the week of 6 July 2026.",
        "C": "Adds a COUNTIFS of that week's interviews. It must match the number of interviews on the calendar.",
        "D": "Runs the skill again for another week with a short prompt, to show it is reusable.",
        "E": "Updates the skill so the summary also shows interview hours per interviewer and the reply names the "
             "busiest day.",
        "F": _LOG,
    },
    7: {
        "A": "Writes the dashboard rules into .Rules - KPI definitions, layout and colours - so every later prompt "
             "follows them.",
        "B": "Builds independent check formulas for the six KPIs. The dashboard cards must match these.",
        "C": "Copilot plans, then builds the dashboard: six KPI cards, four charts, slicers and a timeline. Review "
             "the plan before you approve it.",
        "D": "Uses chart-design to review every chart: finding-style titles, axis titles, useful data labels and "
             "the colours in the rules.",
        "E": "Adds traffic-light colours (green, amber, red) to the Hires vs target card.",
        "F": "Uses theme-design to give the dashboard a clean, modern look while keeping the rule colours.",
        "G": "Compares each KPI card with the Checks sheet and shows each card's formula. Chat only.",
        "H": "Only if needed: fixes the Offer acceptance card so pending offers are left out, as the rules say.",
        "I": "Adds filtered check formulas to confirm the cards change correctly with the Technology slicer and the "
             "Apr-Jun timeline.",
        "J": "Only if needed: links any KPI card that ignores the slicers to the PivotTables with GETPIVOTDATA.",
        "K": "Copilot reviews the dashboard as a Head of Recruitment would - what is unclear, missing or misleading "
             "- and checks it against the rules. Chat only.",
        "L": _LOG,
    },
    8: {
        "A": "Writes the workforce dashboard rules into .Rules: definitions, privacy limits (no individual data, no "
             "group under 5), layout and colours.",
        "B": "Microsoft 365 Copilot on the web (https://copilot.cloud.microsoft/) drafts the complete "
             "hr-workforce-dashboard SKILL.md from the supplied schema and recipe. Save the returned text, then "
             "install and run it in Excel. No workbook upload is needed to draft the skill.",
        "C": "Runs your skill to plan, then build the workforce dashboard for the 12 months to 30 June 2026. Review "
             "the plan before you approve it.",
        "D": "Compares each KPI card with the Checks sheet and shows the attrition formula. Chat only.",
        "E": "Only if needed: fixes the attrition rate to use average headcount, as the rules say.",
        "F": "Adds 8 new joiners to the employee table, refreshes every PivotTable and reports the new headcount - "
             "the refresh test.",
        "G": "A privacy review before sharing: does anything show an individual or a group smaller than 5, and is "
             "every KPI labelled? Chat only.",
        "H": "Writes a 5-line leadership summary that uses only the dashboard's numbers and labels any explanation "
             "as a hypothesis.",
        "I": "Logs the Excel prompts, preserving the web-chat Prompt B row that you fill in manually. Excel cannot see the web conversation.",
    },
}

# ---------------------------------------------------------------------------
# "Formulas explained" for every prompt that contains a formula (or asks Copilot
# to write one), keyed like EXPLAIN. Each entry is (title, [(formula, meaning)]).
# The prompts page shows them under "What it does".
_TBL = "tbl...[Column] is a structured reference: the whole column of that Excel table, so the formula grows with the data."

FORMULAS = {
    1: {
        "I": ("Formulas explained", [
            ('=COUNTIFS(tblApplications[Stage],"Hired")',
             "Counts the rows whose Stage is exactly \"Hired\" - the total number of hires. " + _TBL),
            ('=COUNTIFS(tblApplications[Source_Clean],"LinkedIn",tblApplications[Stage],"Hired")',
             "COUNTIFS takes pairs of (column, condition) and counts rows that meet ALL of them: Source_Clean is "
             "LinkedIn AND Stage is Hired. It uses the cleaned Source_Clean column, so 'Linked In' spellings are "
             "already fixed."),
        ]),
    },
    2: {
        "A": ("The formula Copilot should write", [
            ('=XLOOKUP([@Recruiter_ID],tblRecruiters[Recruiter_ID],tblRecruiters[Recruiter_Name],"Not found")',
             "[@Recruiter_ID] is this row's ID. XLOOKUP finds it in tblRecruiters[Recruiter_ID] and returns the "
             "Recruiter_Name on the same row. The 4th argument is what to show when there is no match."),
        ]),
        "C": ("The formula Copilot should write", [
            ('=IF([@Close_Date]="",Control!$B$1-[@Open_Date],[@Close_Date]-[@Open_Date])',
             "IF(test, if-true, if-false). A blank Close_Date means the requisition is still open, so it counts days "
             "from Open_Date to the report date in Control!B1 ($ locks the cell). Otherwise it counts days from "
             "Open_Date to Close_Date. Subtracting two dates gives the number of days."),
        ]),
        "E": ("The formula Copilot should write", [
            ("=[@Filled]/[@Openings]",
             "Positions filled divided by openings on the same row; formatted as a percentage, 2 / 4 shows as 50%."),
        ]),
        "F": ("The formula Copilot should write", [
            ("=[@Filled]*[@Monthly_Salary_Budget]*12*[@Fee_Rate]",
             "Filled placements x monthly salary x 12 months = first-year salary of all placements; x Fee_Rate "
             "(e.g. 20%) = BrightPath's placement fee."),
        ]),
        "H": ("The formula Copilot should write", [
            ('=IF(AND([@Status]="Open",[@Days_Open]>45),"Overdue","")',
             "AND is TRUE only when both tests are TRUE: still Open AND open more than 45 days. Then the cell shows "
             "\"Overdue\"; otherwise \"\" leaves it blank."),
        ]),
        "J": ("Formulas explained", [
            ("=SUM(tblRequisitions[Est_Fee])", "Adds up the Est_Fee column Copilot created."),
            ("=SUMPRODUCT(tblRequisitions[Filled],tblRequisitions[Monthly_Salary_Budget],tblRequisitions[Fee_Rate])*12",
             "An independent re-calculation of the same total: SUMPRODUCT multiplies Filled x salary x fee rate "
             "row by row and adds the results; x 12 makes it annual. If it equals B3, the Est_Fee column is right."),
            ('=AVERAGEIFS(tblRequisitions[Days_Open],tblRequisitions[Status],"Filled")',
             "Average of Days_Open, using only the rows whose Status is Filled - the average days to fill a job."),
            ('=COUNTIFS(tblRequisitions[Status],"Open",tblRequisitions[Days_Open],">45")',
             "Counts rows that are Open AND older than 45 days, straight from the data. Conditions such as \">45\" "
             "go in quotes."),
            ('=COUNTIF(tblRequisitions[Ageing_Flag],"Overdue")',
             "Counts the rows Copilot flagged Overdue. It must equal B6; if not, the Ageing_Flag formula is wrong."),
        ]),
        "L": ("Formulas explained", [
            ('=SUMIFS(tblRequisitions[Est_Fee],tblRequisitions[Recruiter_Name],"<name>")',
             "SUMIFS(sum column, criteria column, criteria): adds Est_Fee only on rows for that recruiter. Replace "
             "<name> with the name Copilot gave you, inside the quotes."),
        ]),
    },
    3: {
        "B": ("Formulas explained", [
            ("=SUM(tblMonthly[Hires])",
             "Adds every month's hires for every sector (Jan 2025 - Jun 2026). It must equal the PivotTable's grand total."),
        ]),
        "E": ("Formulas explained", [
            ('=SUMIFS(tblMonthly[Hires],tblMonthly[Sector],"Technology",tblMonthly[Month],">="&DATE(2026,1,1))',
             "Adds Hires only where Sector is Technology AND Month is on or after 1 Jan 2026 - Technology's H1 2026 "
             "hires. \">=\"&DATE(2026,1,1) joins the operator to a date so SUMIFS can compare dates."),
        ]),
    },
    4: {
        "D": ("Formulas explained", [
            ("=ROWS(tblOrdersClean[Order_ID])", "Counts the rows in the clean table - it should still be 64 orders."),
            ("=COUNTA(UNIQUE(tblOrdersClean[Status]))",
             "UNIQUE lists each different Status once; COUNTA counts that list. 5 means every messy spelling became "
             "one of the 5 allowed statuses. B3 and B4 do the same for Region and Client."),
            ('=COUNTIF(tblOrdersClean[Status],"In Progress")', "Counts orders whose Status is In Progress (WIP was renamed)."),
            ("=SUM(tblOrdersClean[Budget])", "Adds every order's budget, to compare with the raw data."),
        ]),
        "F": ("Formulas explained", [
            ("=SUM(tblOrdersClean[Delivered_Value])", "Adds the delivered value of every order."),
            ('=COUNTIF(tblOrdersClean[Over_Budget],"Yes")', "Counts the orders the Over_Budget column marks Yes."),
        ]),
    },
    5: {
        "E": ("Formulas explained", [
            ('=SUMIFS(tblClientMonths[New_Clients],tblClientMonths[Month],">="&DATE(2026,1,1))',
             "New clients won from January 2026 on (H1 2026). B2 does the same for sales & marketing spend."),
            ("=B2/B1", "CAC (customer acquisition cost) = H1 spend / H1 new clients."),
            ("=INDEX(tblClientMonths[MRR],18)/INDEX(tblClientMonths[Clients_End],18)",
             "INDEX(column, 18) picks row 18 = June 2026, the latest month. Monthly revenue / clients = ARPA, the "
             "average revenue per account per month."),
            ('=AVERAGEIFS(tblClientMonths[Gross_Margin_Pct],tblClientMonths[Month],">="&DATE(2026,1,1))',
             "Average gross margin % over H1 2026."),
            ("=AVERAGE(FILTER(tblClientMonths[Churned_Clients]/tblClientMonths[Clients_Start],tblClientMonths[Month]>=DATE(2026,1,1)))",
             "Churned / clients at start gives each month's churn rate; FILTER keeps only 2026 months; AVERAGE "
             "gives the average monthly churn."),
            ("=B4*B5/B6", "LTV (lifetime value) = ARPA x gross margin / monthly churn - the profit one client brings over their life."),
            ("=B7/B3", "LTV to CAC: how many times a client pays back what it cost to win them (3 or more is healthy)."),
            ("=B3/(B4*B5)", "Payback months = CAC / monthly gross profit per client."),
        ]),
    },
    6: {
        "C": ("Formulas explained", [
            ('=COUNTIFS(tblInterviews[Interview_Date],">="&DATE(2026,7,6),tblInterviews[Interview_Date],"<="&DATE(2026,7,10))',
             "Counts interviews dated on or after Mon 6 July AND on or before Fri 10 July 2026 - using the same "
             "column twice gives a date range. It should equal the number of interviews on the calendar (23)."),
        ]),
    },
    7: {
        "B": ("Formulas explained", [
            ("=ROWS(tblApps[Application_ID])", "Applications = the number of rows in the table."),
            ('=COUNTIFS(tblApps[Furthest_Stage],"Hired")', "Hires = rows whose furthest stage is Hired."),
            ('=COUNTIFS(tblApps[Offer_Accepted],"Yes")/(COUNTIFS(tblApps[Offer_Accepted],"Yes")+COUNTIFS(tblApps[Offer_Accepted],"No"))',
             "Offer acceptance = accepted / (accepted + declined). Pending offers are in neither count, so they are "
             "left out - exactly as the KPI definition says."),
            ('=AVERAGEIFS(tblApps[Time_to_Hire_Days],tblApps[Furthest_Stage],"Hired")',
             "Average time to hire, averaged over hired candidates only."),
            ("=SUM(tblApps[Sourcing_Cost])/B2", "Cost per hire = total sourcing cost of all applications / number of hires (B2)."),
            ("=B2/SUM(tblTargets[Hire_Target])", "Hires vs target = hires / the sum of the monthly hire targets; format as %."),
        ]),
        "I": ("Formulas explained", [
            ('=COUNTIFS(tblApps[Sector],"Technology")', "Technology applications - must match the Applications card when the Sector slicer is Technology."),
            ('=COUNTIFS(tblApps[Sector],"Technology",tblApps[Furthest_Stage],"Hired")', "Technology hires - must match the Hires card for Technology."),
            ('=COUNTIFS(tblApps[Hire_Date],">="&DATE(2026,4,1),tblApps[Hire_Date],"<="&DATE(2026,6,30))',
             "Hires dated 1 Apr - 30 Jun 2026 - must match the Hires card when the timeline shows Apr-Jun 2026."),
        ]),
    },
    8: {
        "D": ("The attrition formula to look for", [
            ("Attrition = exits in the period / ((active on 2025-07-01 + active on 2026-06-30) / 2)",
             "Exits divided by AVERAGE headcount (start + end, halved), not by today's headcount. Using today's "
             "headcount is the most common error - Prompt E fixes it."),
        ]),
    },
}


# "What it does" for the first five sample prompts of each lab - shown beside each
# prompt on the deck's "Sample Prompts - Lab n" slide. Keyed by lab number, in the
# same order as the lab's sample_prompts. Formulas are what Copilot typically writes.
SAMPLE_EXPLAIN = {
    1: [
        "Chat only: Copilot reads the table and reports what a row is, each column's type, the row count and the "
        "date range. Nothing in the sheet changes.",
        "Reports duplicate IDs and Source values that are not on the canonical list, so you see the problems before "
        "fixing anything.",
        "Plan mode: Copilot lists its steps and waits. You approve or correct the plan before any cell changes.",
        "Writes e.g. =SUBSTITUTE(TRIM([@Source]),\"Linked In\",\"LinkedIn\"): TRIM removes extra spaces, SUBSTITUTE "
        "fixes the spelling. The original Source stays as it was.",
        "Counts applications and hires (Stage = \"Hired\") for each Source_Clean value; hire rate = hires / "
        "applications. Check it with COUNTIFS.",
    ],
    2: [
        "Writes e.g. =XLOOKUP([@Recruiter_ID], tblRecruiters[Recruiter_ID], tblRecruiters[Recruiter_Name], "
        "\"Not found\"): finds this row's ID in tblRecruiters and returns the name.",
        "Writes e.g. =IF([@Close_Date]=\"\", Control!$B$1-[@Open_Date], [@Close_Date]-[@Open_Date]): still open? "
        "count to the report date; closed? count to the close date.",
        "Writes =[@Filled]/[@Openings]: this row's filled positions divided by its openings, e.g. 4 of 4 = 100%.",
        "Writes =[@Filled]*[@Monthly_Salary_Budget]*12*[@Fee_Rate]: monthly salary x 12 = annual salary, x fee rate, "
        "x positions filled. JOB-2002: 4 x S$4,900 x 12 x 25% = S$58,800.",
        "Writes =IF(AND([@Status]=\"Open\", [@Days_Open]>45), \"Overdue\", \"\"): Overdue only when both tests are "
        "true; otherwise the cell stays blank.",
    ],
    3: [
        "Builds a summary with no formulas: one row per month, one column per sector, each cell the total hires. "
        "Check the grand total against =SUM(tblMonthly[Hires]).",
        "Draws a line chart linked to the PivotTable, so it changes when the PivotTable is filtered or refreshed.",
        "Totals 2026 hires for each sector and draws bars, longest first, so the top sector stands out.",
        "Shows how many candidates remain at each stage, from applications down to hires, so you see where people "
        "drop out.",
        "Puts two measures with different units on one chart: hire rate (%) as columns on the left axis, cost per "
        "hire (S$) as a line on the right axis.",
    ],
    4: [
        "Copilot reads the workbook's current formats (dates, money, tables) and writes them as rules on a new "
        ".Rules sheet.",
        "Adds one line to column A of .Rules; from now on every chart Copilot makes in this workbook uses those "
        "colours.",
        "A one-line prompt is enough: Copilot reads .Rules and applies every rule - statuses, regions, client names, "
        "dates, money - to a clean copy.",
        "Lists each spelling with its count and groups variants such as WIP and In Progress, so you know what the "
        "rules must fix.",
        "Rate: =XLOOKUP([@Owner], tblRateCard[Owner], tblRateCard[Hourly_Rate]) finds the owner's rate. "
        "Delivered_Value: =[@Hours_Logged]*[@Rate], hours x rate.",
    ],
    5: [
        "Chat only: Copilot lists the skills you can call - Formatting, Visualization and Finance - and when each "
        "one helps.",
        "Calls the chart-design skill: it picks a suitable chart type, then builds and formats the chart.",
        "Calls the unit-economics skill: CAC = spend / new clients and payback = CAC / (ARPA x gross margin), for each "
        "channel. Check against your Checks sheet.",
        "Calls the check-model skill to audit the sheet: typed numbers where formulas should be, formulas unlike their "
        "neighbours, totals that miss rows.",
        "Calls the theme-design skill: one coordinated set of colours and fonts for cells, tables and charts.",
    ],
    6: [
        "Copilot writes the whole SKILL.md: a name and description at the top, then the steps. You save it in your "
        "OneDrive skills folder.",
        "Copilot reads a skill file and explains its steps in plain English - a quick review before you save or run it.",
        "Runs your custom skill from one line: it builds the Monday-to-Friday calendar and flags clashes.",
        "The same skill for a new week - no need to repeat the instructions.",
        "Finds overlapping interviews with the same interviewer, or onsite interviews in the same room, and lists "
        "both IDs.",
    ],
    7: [
        "Plan mode: Copilot proposes the dashboard - KPI cards, charts, slicers - using the definitions in .Rules, "
        "and waits for your approval.",
        "Reads the totals from the PivotTable with GETPIVOTDATA (sourcing cost / hires), so the card follows the "
        "slicers instead of showing a fixed number.",
        "Calls chart-design for a combo chart: hires as columns and the monthly target as a line, so each month is "
        "seen against target.",
        "Adds a date slider for Hire_Date; connected to every PivotTable, it filters all charts and cards together.",
        "Data bars draw a bar inside each cell; traffic-light colours turn the target card green, amber or red by "
        "the % reached.",
    ],
    8: [
        "Copilot writes the dashboard recipe as a SKILL.md; its first step reads .Rules, so every run uses the same "
        "definitions.",
        "Runs the skill: helper columns, Checks sheet, PivotTables, KPI cards, charts and slicers - all from one line.",
        "Refreshes every PivotTable after new rows were added and reports which KPIs moved, e.g. headcount 237 to 245.",
        "Finds filter combinations that would show fewer than 5 people, so you can hide or group them before sharing.",
        "Explains the card's formula: exits in the period / ((opening + closing headcount) / 2) = 29 / 223.5 = 13.0%.",
    ],
}
