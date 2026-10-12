"""Topic 1 labs for C34: Excel Fundamentals with Copilot (BrightPath recruitment data)."""

from mock_data import EXPECTED

E1 = EXPECTED[1]
E2 = EXPECTED[2]
E3 = EXPECTED[3]
_F = E3["funnel"]


def _money(v):
    return f"S${v:,.0f}" if float(v).is_integer() else f"S${v:,.2f}"


_SETUP_STEP = (
    "Copy {file} from this lab's data folder into a work-c34 folder on your computer and open it in Excel for "
    "Microsoft 365 (desktop). Work on this local copy - no OneDrive upload is needed. Check that Formulas > "
    "Calculation Options is Automatic, then open Copilot from the Copilot button on the Home tab or the floating Copilot "
    "icon at the bottom right. Read the About_This_Data sheet before you prompt."
)

_LOG = (
    "LOG (Allow editing):\n"
    "Prompt_Log already lists every prompt in this lab. For each one I ran, fill in What Copilot did and\n"
    "How I verified, and set Decision to Keep. I will tell you any row to change to Revise or Undo."
)

DOMAIN1 = [
    # ------------------------------------------------------------------ LAB 1
    dict(
        num=1,
        topic=1,
        title="Explore and Question Recruitment Pipeline Data",
        theme="Data Prep & Data Quality",
        duration=35,
        objective=(
            "LO1: confirm Copilot access and use the Chat only, Plan and Allow editing modes to prepare, check, "
            "highlight, sort and filter recruitment pipeline data"
        ),
        goal=(
            "Turn a raw candidate-pipeline export into a named Excel table, find its data-quality issues with Copilot, "
            "and answer pipeline questions with checked numbers."
        ),
        workflow=["Open locally", "Create the table", "Chat only: describe", "Plan: fix quality", "Ask, compare, filter"],
        desc=(
            "You are a talent analyst at BrightPath Talent Solutions, a fictional Singapore recruitment and staffing firm. "
            "You will meet Copilot's three modes on a real task: Allow editing turns the H1 2026 pipeline export into a named "
            "table, Chat only describes it without touching the sheet, and Plan shows you its steps before it fixes duplicate "
            "IDs and inconsistent Source labels. You will then answer pipeline questions, compare two AI models on the same "
            "question, and build a highlighted, sorted and filtered review view. Every number is checked with a formula."
        ),
        build=(
            "BrightPath_Candidate_Pipeline.xlsx in your work-c34 folder with table tblApplications, a Source_Clean column, duplicate "
            "IDs highlighted, Hired rows highlighted, a verified source-by-hires answer and a filled Prompt_Log"
        ),
        services="Excel for Microsoft 365 (desktop) · Copilot (Chat only, Plan, Allow editing, model picker) · BrightPath_Candidate_Pipeline.xlsx",
        data_files=["data/BrightPath_Candidate_Pipeline.xlsx"],
        prerequisites=[
            "A Microsoft 365 account with Copilot in Excel enabled, signed in to Excel for Microsoft 365 (desktop).",
            "A folder named work-c34 on your computer for your working copies.",
            "This lab folder downloaded, including data/BrightPath_Candidate_Pipeline.xlsx.",
        ],
        steps=[
            (
                _SETUP_STEP.format(file="BrightPath_Candidate_Pipeline.xlsx"),
                "Required state:\n"
                "File      : work-c34/BrightPath_Candidate_Pipeline.xlsx (local copy)\n"
                "Calculation Options : Automatic\n"
                "Sheets    : About_This_Data | Applications | Prompt_Log",
            ),
            (
                "Open Copilot and find the mode menu above the prompt box: Chat only (answers, no changes), Plan (shows its "
                "steps first) and Allow editing (makes the changes). Choose Allow editing and ask Copilot to turn the "
                f"Applications data into a named table. Its reply must confirm tblApplications, 13 columns and {E1['rows']} data "
                "rows. Select Done to keep the change, or Undo to reverse it. If Excel offers 'Clean data with Copilot', select "
                "Dismiss for now - you will use it in Lab 4.",
                "ALLOW EDITING:\n"
                "Format the data on the Applications sheet (from A1 to the last row and column) as an Excel table\n"
                "with headers. Name the table tblApplications. Do not change, sort or delete any values.\n"
                "Then tell me the table name, the number of columns and the number of data rows.",
            ),
            (
                "Switch to Chat only (no workbook changes). Paste the prompt below. Copilot's row count must match the "
                f"{E1['rows']} rows it reported in Step 2. If Copilot already points out Source labels such as 'Linked In' or "
                "'JobStreet ' (trailing space), note them - Step 4 checks and fixes them. You will log every prompt in Step 7.",
                "GOAL: Describe this candidate pipeline before I analyse it.\n"
                "CONTEXT: BrightPath recruitment desk, H1 2026. One row should be one application.\n"
                "DATA: Use only tblApplications.\n"
                "CONSTRAINTS: Do not change the workbook.\n"
                "OUTPUT: What a row represents, each column with its data type, the number of rows,\n"
                "        the Applied_Date range and the distinct values of Stage and Source.\n"
                "REVIEW: Tell me how you counted the rows.",
            ),
            (
                "Still in Chat only, ask Copilot to check data quality. It should report 2 repeated Application_IDs and Source "
                "values that are not in the canonical list on About_This_Data. Then switch to Plan mode and send the two changes: "
                "Copilot first shows its plan - read it, approve it, then select Done. Orange means 'this ID appears more than once': "
                "each duplicate ID is coloured in both places it occurs, so you see one orange cell near the top of the table "
                "and its twin further down (press Ctrl+End to jump to the last rows). Check that no row was deleted - the table "
                f"must still have {E1['rows']} rows.",
                "CHAT ONLY:\n"
                "Check tblApplications for data-quality issues. List any Application_ID that appears more than once,\n"
                "and any Source value that is not exactly one of: LinkedIn, JobStreet, MyCareersFuture, Referral,\n"
                "BrightPath Website, Job Fair, Talent Database. Give the count of each issue. Do not change anything.\n\n"
                "PLAN MODE:\n"
                "1) Highlight Application_ID cells that appear more than once in tblApplications with an orange fill.\n"
                "2) Add a column Source_Clean to tblApplications that trims spaces from Source and changes 'Linked In'\n"
                "   to 'LinkedIn'. Do not delete or edit any existing values.\n\n"
                "FOLLOW-UP: For each duplicated Application_ID, give the row numbers of both copies and say whether the\n"
                "two rows are identical.\n\n"
                "FOLLOW-UP: Highlight the Source cells in tblApplications where Source_Clean is different from Source\n"
                "with a yellow fill. Tell me how many cells you highlighted and list their Application_IDs.\n\n"
                "FOLLOW-UP: List the distinct Source_Clean values with a count of each. Confirm there is no 'Linked In'\n"
                f"and no value with a trailing space, and that tblApplications still has {E1['rows']} rows.",
            ),
            (
                "Ask Copilot a direct question about which sources produce hires, then ask Copilot (Allow editing) to add the two "
                "check formulas to a Checks sheet. Duplicate rows are Rejected applications, so they do not change the hire counts. "
                "Finally, open the model picker at the top of the pane (Auto by default), choose a different model, select New chat "
                "and ask the same question again. Both answers must match the Checks formulas - if a model disagrees, the formula wins.",
                "PROMPT (Chat only):\n"
                "Using tblApplications, count applications and hires (Stage = \"Hired\") by Source_Clean.\n"
                "Show a table sorted by hires, highest first, with hire rate = hires / applications.\n\n"
                "CHECK (Allow editing):\n"
                "On a sheet named Checks (create it if needed), add these formulas with a label beside each,\n"
                "then tell me the results:\n"
                "=COUNTIFS(tblApplications[Stage],\"Hired\")\n"
                "=COUNTIFS(tblApplications[Source_Clean],\"LinkedIn\",tblApplications[Stage],\"Hired\")\n\n"
                "CHAT ONLY (new chat, different model):\n"
                "Using tblApplications, count applications and hires (Stage = \"Hired\") by Source_Clean.\n"
                "Show a table sorted by hires, highest first.",
            ),
            (
                "Switch to Allow editing and build a review view, one change at a time. After each change, look at the sheet and "
                "keep it or select Undo in the Copilot pane. Finally ask Copilot how many rows the filter shows, then ask it to "
                f"clear the filter so all {E1['rows']} rows return.",
                "1) Highlight entire rows of tblApplications where Stage is \"Hired\" with a light green fill.\n"
                "2) Sort tblApplications by Interview_Score from highest to lowest, then by Days_in_Pipeline\n"
                "   from lowest to highest.\n"
                "3) Filter tblApplications to show only Client_Sector = \"Technology\" and Stage = \"Interview\".\n"
                "4) How many rows of tblApplications are visible with this filter?\n"
                f"5) Clear all filters on tblApplications and confirm all {E1['rows']} rows are visible.",
            ),
            (
                "Prompt_Log already lists every prompt in this lab with its step and mode. Ask Copilot to fill in what it did, "
                "how it was verified and your decision (Keep, Revise or Undo). Save the workbook (Ctrl+S / Cmd+S) when it is done.",
                _LOG,
            ),
        ],
        sample_prompts=[
            ("Describe", "Describe tblApplications: what one row represents, each column's data type, the row count and the Applied_Date range. Do not change the workbook."),
            ("Data quality", "List any Application_ID that appears more than once in tblApplications and any Source value that is not in the canonical list on About_This_Data."),
            ("Plan first", "Plan how you would flag duplicate Application_IDs and standardise Source. Show me the steps before you change anything."),
            ("Clean helper column", "Add a column Source_Clean that trims spaces from Source and replaces 'Linked In' with 'LinkedIn'. Do not change the original Source column."),
            ("Question", "Using tblApplications, count applications and hires by Source_Clean and show the hire rate. Sort by hires, highest first."),
            ("Question", "Which Client_Sector received the most applications, and how many? Show the count for every sector."),
            ("Highlight", "Highlight rows where Stage is Hired in light green."),
            ("Sort", "Sort tblApplications by Interview_Score from highest to lowest, then by Days_in_Pipeline from lowest to highest."),
            ("Filter", "Filter to show only Technology applications at the Interview stage."),
            ("Insight", "What's interesting about this pipeline data? Give three observations, each with the numbers behind it."),
        ],
        test=(
            f"tblApplications exists with {E1['rows']} data rows and =COUNTA(UNIQUE(tblApplications[Application_ID])) returns "
            f"{E1['unique']}. The repeated IDs are {E1['dup_ids'][0]} and {E1['dup_ids'][1]} (both Rejected); all four of their cells are orange - two near the top and their copies in the last two rows. "
            f"Copilot found {E1['variants_linkedin']} 'Linked In' and {E1['variants_jobstreet']} 'JobStreet ' (trailing space) "
            f"values, and those {E1['variants_linkedin'] + E1['variants_jobstreet']} Source cells are yellow; "
            f"=COUNTIF(tblApplications[Source_Clean],\"LinkedIn\") returns {E1['linkedin_clean_all']}. Hires total "
            f"{E1['hired']} and {E1['top_hire_source']} has the most hires ({E1['top_hire_source_n']}). The Technology + Interview "
            f"filter shows {E1['tech_interview_all']} rows. Technology received the most applications ({E1['top_sector_n']} unique). "
            f"After clearing the filter all {E1['rows']} rows are visible, and every Prompt_Log row you ran has What Copilot did, How I verified and a Decision."
        ),
        checkpoint=(
            "Keep this workbook in work-c34. Lab 2 uses a separate requisitions workbook, so a learner who is behind can "
            "start Lab 2 from its own data folder."
        ),
        troubleshooting=[
            (
                "The Copilot button is missing or greyed out.",
                "Save the file as a normal .xlsx, close and reopen it, and update Excel. Check your licence in "
                "your Microsoft 365 account and ask IT if Copilot is disabled for your tenant. Pair with a neighbour meanwhile.",
            ),
            (
                "There is no Plan option in the mode menu.",
                "Some Excel builds show only Allow editing and Chat only. Use Chat only, end the prompt with 'Show me the plan; do "
                "not change anything yet', then switch to Allow editing to carry it out.",
            ),
            (
                "'Unsupported file state' message.",
                "Save as a normal .xlsx (Strict Open XML files are not supported), close and reopen it. If the file is read-only, "
                "copy it into work-c34 and open the copy.",
            ),
            (
                "Copilot answers about the whole sheet instead of the table.",
                "Name the table (tblApplications) and the exact columns in the prompt, and click inside the table before asking.",
            ),
            (
                "Copilot's count differs from your formula.",
                "Ask Copilot how it counted (rows vs unique IDs, which Stage values). Trust the formula, record the difference "
                "and refine the prompt.",
            ),
        ],
        challenge=(
            "Ask Copilot to add a Pipeline_Status column that groups Stage into Active (Applied, Screening, Interview, Offer), "
            "Hired and Closed (Rejected, Withdrawn). Verify the three counts add up to the row count."
        ),
        reflection="Which data-quality issue would most distort a source-effectiveness report if you had not found it, and why?",
    ),
    # ------------------------------------------------------------------ LAB 2
    dict(
        num=2,
        topic=1,
        title="Generate and Verify Formula Columns and XLOOKUPs for Job Requisitions",
        theme="Formulas & XLOOKUP",
        duration=35,
        objective=(
            "LO1: use Copilot to write XLOOKUP and calculated columns from plain-English rules, explain them, "
            "and reconcile them to independent control formulas"
        ),
        goal=(
            "Add recruiter names, days open, fill rate, estimated placement fee and an ageing flag to a requisitions table, "
            "then prove each column is right."
        ),
        workflow=["Lookup", "Days open", "Fill rate & fee", "Ageing flag", "Reconcile"],
        desc=(
            "BrightPath's permanent-recruitment desk tracks 60 client job orders. You will ask Copilot to add an XLOOKUP for "
            "the recruiter's name and four calculated columns written from business rules, ask it to explain each formula, "
            "hand-check one requisition and reconcile column totals to independent formulas on the Control sheet. You will then "
            "ask Copilot which recruiter generated the most estimated fees and verify the answer."
        ),
        build=(
            "BrightPath_Job_Requisitions.xlsx with Recruiter_Name, Days_Open, Fill_Rate, Est_Fee and Ageing_Flag columns in "
            "tblRequisitions, overdue requisitions highlighted, and a Control sheet that reconciles the totals"
        ),
        services="Excel · Copilot (Allow editing, Chat only) · XLOOKUP · structured references · BrightPath_Job_Requisitions.xlsx",
        data_files=["data/BrightPath_Job_Requisitions.xlsx"],
        prerequisites=[
            "Lab 1 completed, or Copilot access confirmed on a local .xlsx file.",
            "This lab folder's data/BrightPath_Job_Requisitions.xlsx.",
        ],
        steps=[
            (
                _SETUP_STEP.format(file="BrightPath_Job_Requisitions.xlsx")
                + " Note the fee rule: Est_Fee = Filled x Monthly_Salary_Budget x 12 x Fee_Rate, and the report date in Control!B1.",
                "Tables : tblRequisitions (60 rows) | tblRecruiters (6 rows)\n"
                "Control!B1 Report_Date = 2026-06-30",
            ),
            (
                "Choose Allow editing. Ask Copilot to add the lookup column, then ask it to explain the formula and show one row "
                "next to the matching row in tblRecruiters.",
                "In tblRequisitions, add a column Recruiter_Name that looks up Recruiter_Name from tblRecruiters\n"
                "using Recruiter_ID. Use XLOOKUP and return \"Not found\" if there is no match.\n\n"
                "Then: Explain the Recruiter_Name formula, and show one row's Recruiter_ID and Recruiter_Name next to\n"
                "the matching row in tblRecruiters.",
            ),
            (
                "Ask for Days_Open with an explicit rule for open requisitions. Read the explanation, then ask Copilot to show an "
                "open row (blank Close_Date) and a closed row so you can confirm the rule.",
                "Add a column Days_Open to tblRequisitions. If Close_Date is blank, use Control!B1 minus Open_Date;\n"
                "otherwise use Close_Date minus Open_Date. Show whole numbers.\n\n"
                "FOLLOW-UP: Show one open requisition (blank Close_Date) and one closed requisition with Open_Date,\n"
                "Close_Date and Days_Open, and the subtraction behind each.",
            ),
            (
                "Ask for Fill_Rate and Est_Fee, one prompt each. Format Fill_Rate as a percentage and Est_Fee as S$ with no "
                f"decimals. Then ask Copilot to show the calculation for {E2['sample_id']}: Filled {E2['sample_detail'][0]} x S${E2['sample_detail'][1]:,} x 12 x "
                f"{E2['sample_detail'][2]:.0%} = {_money(E2['sample_fee'])}.",
                "Add a column Fill_Rate = Filled divided by Openings, formatted as a percentage.\n\n"
                "Add a column Est_Fee = Filled x Monthly_Salary_Budget x 12 x Fee_Rate, formatted as S$ with no decimals.\n"
                "Explain the formula.\n\n"
                f"FOLLOW-UP: Show the Est_Fee calculation for {E2['sample_id']} step by step.",
            ),
            (
                "Ask for the ageing flag and a highlight, then ask Copilot how many requisitions are flagged.",
                "Add a column Ageing_Flag that shows \"Overdue\" when Status is \"Open\" and Days_Open is greater than 45,\n"
                "otherwise leave it blank. Highlight rows where Ageing_Flag is \"Overdue\" with a light amber fill.\n\n"
                "FOLLOW-UP: How many rows have Ageing_Flag = \"Overdue\"?",
            ),
            (
                "Ask Copilot to build independent controls on the Control sheet with the exact formulas below. The independent "
                "formulas recalculate from the raw columns, so they do not rely on Copilot's new columns. Each pair must match.",
                "Enter these labels and formulas on the Control sheet exactly as written. Then tell me each result\n"
                "and whether each pair (B3 and B4, B6 and B7) matches:\n"
                "A3 Total Est_Fee (column)       B3 =SUM(tblRequisitions[Est_Fee])\n"
                "A4 Total fee (independent)      B4 =SUMPRODUCT(tblRequisitions[Filled],tblRequisitions[Monthly_Salary_Budget],tblRequisitions[Fee_Rate])*12\n"
                "A5 Avg days to fill (Filled)    B5 =AVERAGEIFS(tblRequisitions[Days_Open],tblRequisitions[Status],\"Filled\")\n"
                "A6 Overdue (independent)        B6 =COUNTIFS(tblRequisitions[Status],\"Open\",tblRequisitions[Days_Open],\">45\")\n"
                "A7 Overdue flags (column)       B7 =COUNTIF(tblRequisitions[Ageing_Flag],\"Overdue\")",
            ),
            (
                "In Chat only, ask which recruiter generated the most estimated fees. Then ask Copilot (Allow editing) to add the "
                "SUMIFS check to the Control sheet and to log all prompts on Prompt_Log.",
                "CHAT ONLY:\n"
                "Using tblRequisitions, which Recruiter_Name has the highest total Est_Fee? Show the total for every recruiter.\n\n"
                "CHECK (Allow editing):\n"
                "On the Control sheet, add this check for the top recruiter and tell me if it matches your answer:\n"
                "=SUMIFS(tblRequisitions[Est_Fee],tblRequisitions[Recruiter_Name],\"<name>\")\n\n" + _LOG,
            ),
        ],
        sample_prompts=[
            ("Lookup", "Add a column Recruiter_Name that looks up Recruiter_Name from tblRecruiters using Recruiter_ID with XLOOKUP. Return \"Not found\" if missing."),
            ("Duration", "Add a column Days_Open: if Close_Date is blank use Control!B1 minus Open_Date, otherwise Close_Date minus Open_Date."),
            ("Ratio", "Add a column Fill_Rate = Filled / Openings formatted as a percentage."),
            ("Business rule", "Add a column Est_Fee = Filled x Monthly_Salary_Budget x 12 x Fee_Rate, formatted as S$ with no decimals."),
            ("Flag", "Add a column Ageing_Flag that shows \"Overdue\" when Status is Open and Days_Open > 45, otherwise blank."),
            ("Explain", "Explain the formula in the selected cell step by step, and tell me how blanks are handled."),
            ("Summary row", "Add a total row to tblRequisitions that sums Openings, Filled and Est_Fee and averages Days_Open."),
            ("Question", "Which recruiter has the highest total Est_Fee? Show every recruiter's total, highest first."),
            ("Several steps", "Add Fill_Rate and Est_Fee columns, add a total row, then tell me which recruiter has the highest total Est_Fee."),
        ],
        test=(
            f"Control!B3 and B4 both show {_money(E2['fee_total'])}. B5 shows {E2['avg_days_filled']} days "
            f"({E2['filled_n']} Filled requisitions). B6 and B7 both show {E2['overdue_n']}. {E2['sample_id']} shows Est_Fee "
            f"{_money(E2['sample_fee'])} and Days_Open {E2['sample_days']}. Every Recruiter_Name resolves (no \"Not found\"). "
            f"The top recruiter by estimated fees is {E2['top_rec']} with {_money(E2['top_rec_fee'])}."
        ),
        checkpoint=(
            "Keep the workbook in work-c34. Lab 3 uses its own metrics workbook in the Lab 3 folder."
        ),
        troubleshooting=[
            (
                "Days_Open is negative or huge for open requisitions.",
                "The formula used today's date or a blank as zero. Ask Copilot to use Control!B1 explicitly, or edit the formula.",
            ),
            (
                "Est_Fee is 12 times too small or too large.",
                "Re-read the rule: fee is on first-year salary (monthly x 12). Ask Copilot to explain the formula and correct it.",
            ),
            (
                "The new column is outside the table.",
                "Click inside tblRequisitions before prompting and name the table in the prompt; or drag the table's resize handle.",
            ),
            (
                "Copilot cannot add a formula column.",
                "Confirm Calculation Options is Automatic and the data is an Excel table; if it still fails, save, close and reopen the workbook.",
            ),
        ],
        challenge=(
            "Ask Copilot to add a Fee_Achieved column that is Est_Fee for Filled requisitions only, then build a small "
            "summary of Fee_Achieved by Sector with SUMIFS. Check that the sector totals add up to the grand total. Then bring in "
            "other data: select + (Add work content) and attach Lab 1's BrightPath_Candidate_Pipeline.xlsx (Copilot can only "
            "attach files it can find in your OneDrive or SharePoint, so skip this part if you work locally only), and ask: 'Add a sheet Sector_View that compares open requisitions by Sector in this "
            "workbook with hires by Client_Sector in the attached pipeline.' Check one sector's hires with COUNTIFS in the "
            "pipeline workbook."
        ),
        reflection="Which of today's formulas would have looked correct but been wrong without a hand-check, and how did you catch it?",
    ),
    # ------------------------------------------------------------------ LAB 3
    dict(
        num=3,
        topic=1,
        title="Build PivotTables, PivotCharts and Recruitment Charts with Copilot",
        theme="PivotTables, PivotCharts & Visuals",
        duration=45,
        objective=(
            "LO1: use Copilot to build PivotTables, PivotCharts and trend, comparison, funnel and combo charts from prompts, "
            "refine them with follow-up prompts and tie each chart to a checked total"
        ),
        goal=(
            "Produce four decision-ready recruitment charts - hiring trend, hires by sector, the H1 2026 funnel and source "
            "effectiveness - each backed by a reconciled summary."
        ),
        workflow=["Pivot + line PivotChart", "Sector PivotChart", "Funnel", "Source combo", "Refine & check"],
        desc=(
            "BrightPath's leadership wants to see how hiring is moving and which sectors and sourcing channels perform best. "
            "You will ask Copilot to build PivotTables and PivotCharts from 18 months of funnel metrics and a sourcing summary, "
            "choose each chart from the question it answers, refine titles, labels, sort order and axes with follow-up "
            "prompts, and reconcile every chart to an independent SUMIFS check."
        ),
        build=(
            "BrightPath_Recruitment_Metrics.xlsx with PivotTables and four refined charts on the Charts sheet: a monthly hires "
            "line PivotChart, a sorted 2026 hires-by-sector bar PivotChart, a 2026 recruitment funnel and a hire-rate vs "
            "cost-per-hire combo chart"
        ),
        services="Excel · Copilot (Allow editing) · PivotTables, PivotCharts · line, bar, funnel and combo charts · BrightPath_Recruitment_Metrics.xlsx",
        data_files=["data/BrightPath_Recruitment_Metrics.xlsx"],
        prerequisites=[
            "Labs 1-2 completed: you can open a lab workbook, switch Copilot modes and verify with formulas.",
            "This lab folder's data/BrightPath_Recruitment_Metrics.xlsx.",
        ],
        steps=[
            (
                _SETUP_STEP.format(file="BrightPath_Recruitment_Metrics.xlsx")
                + " The Charts sheet is empty: you will create each chart there with a prompt, in a 2 x 2 grid. The data "
                "is on Monthly_Metrics and Source_Summary. Each chart answers one of the four questions below.",
                "Tables : tblMonthly (108 rows = 18 months x 6 sectors) | tblSources (7 rows)\n\n"
                "Q1 Trend      : How have total hires moved month by month since Jan 2025?\n"
                "Q2 Comparison : Which sector produced the most hires in Jan-Jun 2026?\n"
                "Q3 Funnel     : Where do candidates drop out between application and hire in 2026?\n"
                "Q4 Efficiency : Which sources convert best, and at what cost per hire?",
            ),
            (
                "Choose Allow editing. Ask Copilot to create the trend PivotTable and a line PivotChart on the Charts sheet. "
                "Then ask Copilot to check the Pivot grand total against =SUM(tblMonthly[Hires]) and name the peak month.",
                "Create a PivotTable from tblMonthly on a new sheet named Pivot_Trend with Month_Label in rows and\n"
                "Sum of Hires as values. Then create a line PivotChart of total hires by month on the Charts sheet,\n"
                "placed over A1:H18. Format it cleanly: white background, no border or effects, one blue line with\n"
                "markers, data labels above the points, light grey gridlines, axis titles Month and Hires.\n"
                "Title: \"Monthly hires, Jan 2025 - Jun 2026\".\n\n"
                "CHECK (Allow editing):\n"
                "In an empty cell on Pivot_Trend, add this formula. Tell me whether it matches the PivotTable grand total,\n"
                "and which month had the most hires:\n"
                "=SUM(tblMonthly[Hires])",
            ),
            (
                "Ask Copilot to create the 2026 sector comparison chart on the Charts sheet. Then refine it with a follow-up "
                "prompt. Ask Copilot to add the SUMIFS check for Technology's 2026 hires.",
                "Create a PivotTable on a new sheet Pivot_Sector from tblMonthly with Sector in rows and Sum of Hires,\n"
                "filtered to months in 2026 only. Then create a bar PivotChart from it on the Charts sheet, placed\n"
                "over J1:Q18, in the same clean style as the first chart.\n\n"
                "FOLLOW-UP: Sort the bars from highest to lowest and change the title to state the leading sector.\n\n"
                "CHECK (Allow editing):\n"
                "In an empty cell on Pivot_Sector, add this formula and tell me if it matches Technology's bar:\n"
                "=SUMIFS(tblMonthly[Hires],tblMonthly[Sector],\"Technology\",tblMonthly[Month],\">=\"&DATE(2026,1,1))",
            ),
            (
                "Ask Copilot to build a 2026 funnel summary with formulas on its own sheet, then create a funnel chart on the "
                "Charts sheet. Ask Copilot to show the formula in each value cell to confirm the summary uses SUMIFS, not "
                "typed numbers.",
                "On a new sheet named Funnel_2026, build a small table of 2026 totals for Applications, Screened,\n"
                "Interviews, Offers and Hires from tblMonthly using SUMIFS on Month >= 1 Jan 2026. Add a column showing\n"
                "each stage as a % of Applications. Then create a funnel chart from it with data labels on the\n"
                "Charts sheet, placed over A20:H37, in the same clean style as the first chart.\n\n"
                "FOLLOW-UP: Show the formula in each value cell of the funnel table.",
            ),
            (
                "Ask Copilot to add rate columns to tblSources and create a combo chart with two axes on the Charts sheet. "
                "Then ask it for the best hire rate and the lowest cost per hire.",
                "In tblSources add Hire_Rate = Hires / Applications (percentage, 1 decimal) and\n"
                "Cost_per_Hire = Sourcing_Spend / Hires (S$, no decimals). Create a combo chart on the Charts sheet:\n"
                "Hire_Rate as clustered columns sorted highest first, Cost_per_Hire as a line on a secondary axis.\n"
                "Label both axes with units. Place it over J20:Q37 in the same clean style as the first chart.\n\n"
                "FOLLOW-UP: Which source has the highest Hire_Rate, and which has the lowest Cost_per_Hire? Give both values.",
            ),
            (
                "Refine the four charts on the Charts sheet with short follow-up prompts, one change at a time. Add alt text to "
                "each chart.",
                "Make every chart title state the finding in one sentence.\n"
                "Use the same blue colour for all hires series and format numbers with thousands separators.\n"
                "Make the four charts on the Charts sheet the same size and line them up in a 2 x 2 grid.\n"
                "Add alt text to each chart describing what it shows.",
            ),
            (
                "Ask Copilot (Chat only) to review the charts against the four questions, then ask it to log your prompts and "
                "checks on Prompt_Log.",
                "CHAT ONLY:\n"
                "Review the four charts on the Charts sheet. For each, tell me which question it answers\n"
                "(Q1 Trend, Q2 Comparison, Q3 Funnel, Q4 Efficiency), whether the chart type suits that question,\n"
                "and one improvement. Do not change anything.\n\n"
                + _LOG,
            ),
        ],
        sample_prompts=[
            ("PivotTable", "Create a PivotTable from tblMonthly with Month_Label in rows, Sector in columns and Sum of Hires as values."),
            ("PivotChart", "Create a line PivotChart from the Pivot_Trend PivotTable showing total hires by month. Show data labels and gridlines."),
            ("Bar chart", "Create a bar chart of 2026 hires by Sector, sorted from highest to lowest."),
            ("Funnel", "Create a funnel chart of 2026 Applications, Screened, Interviews, Offers and Hires with data labels."),
            ("Combo chart", "Create a combo chart of Hire_Rate as columns and Cost_per_Hire as a line on a secondary axis."),
            ("Refine", "Change the chart title to: Technology led hiring in H1 2026."),
            ("Refine", "Sort the bars from highest to lowest and add data labels formatted with thousands separators."),
            ("Accessibility", "Add alt text to this chart that describes the trend it shows."),
            ("Review", "Is a line chart the right choice for this data? Suggest a better chart if not, and explain why."),
        ],
        test=(
            f"Pivot_Trend grand total = {E3['h1_hires'] + E3['total_2025']:,} hires (= SUM(tblMonthly[Hires])); the peak month is "
            f"{E3['peak_month']} with {E3['peak_month_hires']} hires. The 2026 sector bar chart shows {E3['top_sector']} first with "
            f"{E3['top_sector_hires']} hires and its Pivot total is {E3['h1_hires']}. The funnel shows {_F[0]:,} > {_F[1]:,} > "
            f"{_F[2]:,} > {_F[3]:,} > {_F[4]:,}. In tblSources, {E3['best_rate_source']} has the highest hire rate "
            f"({E3['best_rate']}%) and {E3['lowest_cps_source']} the lowest cost per hire (S${E3['lowest_cps']}). All four charts "
            "sit on the Charts sheet with finding-style titles, labelled axes and alt text."
        ),
        checkpoint="Keep the workbook in work-c34. Topic 2 starts from the client orders workbook in the Lab 4 folder.",
        troubleshooting=[
            (
                "The 2026 filter includes 2025 months.",
                "Ask Copilot to filter on the Month date field (>= 1 Jan 2026), not on Month_Label text, or add a Year field.",
            ),
            (
                "Copilot inserts a picture of a chart instead of a chart.",
                "That came from a Chat answer and is static. Switch to Allow editing and ask it to create a chart linked to the data.",
            ),
            (
                "The funnel chart type is not offered.",
                "Funnel charts need Excel 2019 or Microsoft 365. Ask for a sorted horizontal bar chart of the stages instead.",
            ),
            (
                "A chart lands on the PivotTable sheet, not on the Charts sheet.",
                "Ask: 'Move this chart to the Charts sheet over A1:H18' (use that chart's range), or select the chart and "
                "use Move Chart > Object in: Charts.",
            ),
            (
                "The chart has a glow or gradient border, or the data labels overlap.",
                "Ask: 'Remove the chart border and effects, use a white background and put the data labels above the "
                "points.'",
            ),
            (
                "Both series in the combo chart share one axis and the line is flat.",
                "Ask: 'Put Cost_per_Hire on a secondary axis and format it as S$'.",
            ),
        ],
        challenge=(
            "Ask Copilot for a 100% stacked column chart showing each sector's share of hires by quarter for 2025-2026, then "
            "decide whether it communicates better or worse than the bar chart, and why. Then try creating a spreadsheet from "
            "scratch: in a new blank workbook ask Copilot 'Create a spreadsheet I can use to plan and track BrightPath's July "
            "hiring campaign, with a Gantt chart visual.' Change one start date and check that the Gantt bar moves."
        ),
        reflection="Which of your four charts would most change a BrightPath leadership decision, and what check makes you trust it?",
    ),
]

# Test-it checklist: (what to check, expected result). Shown on the slide, in the
# LG and in the lab README/PDF; values come from the same EXPECTED numbers.
_CHECKS = {
    1: [
        ("Rows in tblApplications", f"{E1['rows']} rows, {E1['unique']} unique Application_IDs"),
        ("Duplicate IDs (orange)", f"{E1['dup_ids'][0]} and {E1['dup_ids'][1]} - 4 orange cells: 2 near the top, 2 in the last rows"),
        ("Fixed Source cells (yellow)", f"{E1['variants_linkedin'] + E1['variants_jobstreet']} cells: {E1['variants_linkedin']} 'Linked In' + {E1['variants_jobstreet']} 'JobStreet '"),
        ("LinkedIn count in Source_Clean", f"{E1['linkedin_clean_all']}"),
        ("Hires", f"{E1['hired']} in total; {E1['top_hire_source']} has the most ({E1['top_hire_source_n']})"),
        ("Technology + Interview filter", f"{E1['tech_interview_all']} rows; all {E1['rows']} back after clearing it"),
    ],
    2: [
        ("Total estimated fees (Control B3 and B4)", f"Both {_money(E2['fee_total'])}"),
        ("Average days to fill (B5)", f"{E2['avg_days_filled']} days ({E2['filled_n']} filled requisitions)"),
        ("Overdue requisitions (B6 and B7)", f"Both {E2['overdue_n']}"),
        (f"Sample row {E2['sample_id']}", f"Est_Fee {_money(E2['sample_fee'])}, Days_Open {E2['sample_days']}"),
        ("Recruiter_Name lookup", "Every row has a name - no \"Not found\""),
        ("Top recruiter by fees", f"{E2['top_rec']} - {_money(E2['top_rec_fee'])}"),
    ],
    3: [
        ("Total hires (Pivot_Trend)", f"{E3['h1_hires'] + E3['total_2025']:,} = SUM(tblMonthly[Hires])"),
        ("Peak month", f"{E3['peak_month']} with {E3['peak_month_hires']} hires"),
        ("2026 hires by sector", f"{E3['top_sector']} first ({E3['top_sector_hires']}); Pivot total {E3['h1_hires']}"),
        ("Funnel", f"{_F[0]:,} > {_F[1]:,} > {_F[2]:,} > {_F[3]:,} > {_F[4]:,}"),
        ("Best source", f"{E3['best_rate_source']}: highest hire rate ({E3['best_rate']}%); {E3['lowest_cps_source']}: lowest cost per hire (S${E3['lowest_cps']})"),
        ("Charts sheet", "2 PivotCharts + funnel + combo in a 2 x 2 grid (A1:Q37), clean style, finding-style titles, labelled axes and alt text"),
    ],
}
for _a in DOMAIN1:
    _a["checks"] = _CHECKS[_a["num"]]
