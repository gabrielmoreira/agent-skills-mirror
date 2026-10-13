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
             "refer to it by name. Copilot reports the rows and columns so you can confirm nothing was lost.",
        "B": "Asks Copilot to describe the data before you analyse it: what a row is, the date range and the Stage "
             "and Source values. Chat only, so nothing changes.",
        "C": "Asks Copilot to look for problems - repeated IDs and Source names spelt more than one way. It only "
             "reports; nothing is fixed yet.",
        "D": "Plan mode: Copilot shows its steps first, then highlights the repeated IDs in orange and adds a tidied "
             "Source_Clean column. The original Source column stays as it was.",
        "E": "Copilot's answer: applications, hires and hire rate for each source. The next prompt checks it.",
        "F": "Copilot writes the check formulas for you on a Checks sheet, so you can confirm its hire counts without "
             "typing a formula. Send prompt E again with a different model and compare both answers with this sheet.",
        "G": "Highlights every hired candidate's row in light green so the hires stand out.",
        "H": "Sorts the table by interview score, highest first.",
        "I": "Filters the table to Technology candidates at the Interview stage and asks how many there are. Compare "
             "with the count at the bottom of the Excel window.",
        "J": _LOG,
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
        "A": "Asks Copilot which of its skills suit charting and styling, so you know what to call. Chat only - "
             "nothing changes.",
        "B": "Uses the chart-design skill to build a combo chart on a new Charts sheet: MRR as columns and client "
             "count as a line on a second axis. Your prompt sets the position (A1:H18) and a clean style.",
        "C": "Chart-design recommends a chart type for new vs churned clients, then draws it next to the first chart.",
        "D": "Totals each channel's H1 2026 spend and draws bars, longest first, so the biggest spender is obvious.",
        "E": "Counts the active clients on each plan in June 2026 and draws the chart type the skill thinks suits it "
             "best.",
        "F": "One more chart-design call to make the four charts read as a set: finding-style titles, matching fonts "
             "and axes, the same size.",
        "G": "Copilot writes the check formulas for you on a Checks sheet, so each chart can be compared with a "
             "number you can see - without typing a formula.",
        "H": "Uses the theme-design skill to give the sheets and charts one coordinated set of colours, fonts and "
             "formats.",
        "I": "Steers the theme with your own colours - navy and teal - while keeping every chart readable. A prompt "
             "can direct a skill.",
        "J": _LOG,
    },
    6: {
        "A": "Microsoft 365 Copilot on the web (https://copilot.cloud.microsoft/) writes the complete pareto-chart SKILL.md from the table, "
             "chart and colour instructions. Save the returned text, upload it to OneDrive and install it in Excel. "
             "No workbook upload is needed to draft the skill.",
        "B": "Runs your new skill: a Pareto_Job_Category sheet with the count, share and cumulative % of each "
             "category, and a combo chart with a different colour for every column.",
        "C": "Copilot writes check formulas on a Checks sheet - total jobs, Customer Service jobs and the number of "
             "categories - to compare with the chart.",
        "D": "The same skill on a different column: a Pareto chart of Client_Sector from one short prompt.",
        "E": "Chat only: reads the Pareto summary and names the categories that reach 80% - the 'vital few' - with "
             "their combined share.",
        "F": "Copilot on the web updates the skill: a dashed 80% line, and one Other column for categories under 2%. "
             "You paste your current SKILL.md under the prompt.",
        "G": "Runs the improved skill again on Job_Category, to see the 80% line and the Other column.",
        "H": "Logs the Excel prompts and leaves the two web-chat rows (A and F) for you to fill in by hand. Excel "
             "cannot see the web conversation.",
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
        "F": ("The formulas Copilot should write", [
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
        "G": ("The formulas Copilot should write", [
            ("=INDEX(tblClientMonths[MRR],18)",
             "INDEX(column, 18) picks row 18 = June 2026, the latest month. Clients_End works the same way."),
            ("=SUM(tblClientMonths[New_Clients])",
             "Adds the clients won in all 18 months. Churned_Clients works the same way."),
            ('=SUMIFS(tblSpend[Spend],tblSpend[Channel],"LinkedIn Ads",tblSpend[Month],">="&DATE(2026,1,1))',
             "Adds Spend for one channel from 1 Jan 2026 (H1 2026). \">=\"&DATE(2026,1,1) joins an operator to a date so "
             "SUMIFS can compare dates. Copilot writes one formula per channel."),
            ('=COUNTIFS(tblClients[Plan],"Full HR Outsourcing",tblClients[Status],"Active")',
             "Counts the clients on one plan whose Status is Active. Copilot writes one formula per plan."),
        ]),
    },
    6: {
        "B": ("What the skill's summary table does", [
            ("=COUNTIFS(tblJobs[Job_Category],A5)",
             "Counts the rows of tblJobs whose Job_Category equals the category named in A5. It reads the table, so "
             "the chart updates when you add rows."),
            ("=SUM($B$5:B5)/SUM($B$5:$B$20)",
             "A running total of Count divided by the grand total: the cumulative % that draws the line. $ locks the "
             "start of the range, so the total grows one row at a time."),
        ]),
        "C": ("The formulas Copilot should write", [
            ("=ROWS(tblJobs[Job_ID])", "Counts the rows of tblJobs - the number of jobs."),
            ('=COUNTIFS(tblJobs[Job_Category],"Customer Service")',
             "Counts the rows whose Job_Category is exactly Customer Service - the tallest column."),
            ("=COUNTA(UNIQUE(tblJobs[Job_Category]))",
             "UNIQUE lists each category once; COUNTA counts that list - the number of columns on the chart."),
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
        "Copilot reads the whole table and sums it up in five short points - a quick first look before you dig in.",
        "Counts the applications for each sector and names the top one (Technology).",
        "Counts the candidates at the Offer stage for each recruiter, so you see whose candidates are closest to a hire.",
        "Colours the rows with the top interview score so the strongest candidates stand out.",
        "Copilot looks for patterns - e.g. which sources or sectors convert best - and backs each one with numbers "
        "you can check.",
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
        "Chat only: Copilot lists the skills for charts and formatting and says when each one helps.",
        "Chart-design picks a chart type that compares the two series month by month, then draws it.",
        "Totals the H1 2026 spend of each channel and draws bars, longest first - LinkedIn Ads (S$191,590) leads.",
        "Calls theme-design: one coordinated set of colours, fonts and formats for cells, tables and charts.",
        "Directs the theme with your own colours - navy for the main series, teal for comparisons.",
    ],
    6: [
        "Copilot on the web writes the whole pareto-chart SKILL.md. You save it and upload it to the OneDrive skills "
        "folder.",
        "Runs your skill: sorted counts, a cumulative % line and a different colour for each column - Customer "
        "Service (145 jobs) leads.",
        "The same skill on another column - no need to repeat the instructions.",
        "Copilot writes the check formulas: 500 jobs in all and 145 Customer Service jobs - they must match the chart.",
        "Adds up the shares until 80% is passed: the first six categories make up 83.0%.",
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
