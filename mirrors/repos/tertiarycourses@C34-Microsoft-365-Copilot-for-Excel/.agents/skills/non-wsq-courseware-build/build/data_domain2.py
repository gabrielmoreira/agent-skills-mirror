"""Topic 2 labs for C34: Skills and Rules (BrightPath client orders, finance and interview data)."""

from mock_data import EXPECTED, STATUSES, REGIONS
from data_domain1 import _LOG, _SETUP_STEP

E4 = EXPECTED[4]
E5 = EXPECTED[5]
E6 = EXPECTED[6]
_S = E4["sample"]


def _money(v):
    return f"S${v:,.0f}"


# ---------------------------------------------------------------- .Rules text (Lab 4)
# One rule per line = one rule per cell in column A of the .Rules sheet. "##" lines are headings.
RULES_LAB4 = """## ABOUT THIS WORKBOOK
Orders_Raw is the original export. Do not sort, delete or add rows on Orders_Raw. Build cleaned data on new sheets.
One row = one client order, identified by Order_ID.
Put "Created by Copilot" and today's date in cell A1 of every new sheet you create (except the Checks sheet), and start the data in row 3.
## DATA VALUES
Status must be one of: Open, In Progress, On Hold, Completed, Cancelled. Map every variation: WIP and Ongoing = In Progress; Done and Closed - filled = Completed; Not started and New = Open; Paused and Hold = On Hold; Canceled and Client cancelled = Cancelled.
If Notes say the work is paused, the Status is On Hold, whatever the Status column says.
Region must be one of: CENTRAL, EAST, NORTH, NORTH-EAST, WEST (upper case). For example C = CENTRAL and Northeast = NORTH-EAST.
Client is the short trading name with no legal suffix, in title case. For example QUILLON SYSTEMS PTE. LTD. = Quillon Systems.
Owner names are trimmed and in title case, exactly as in tblRateCard[Owner].
## DATES AND MONEY
Text dates in Orders_Raw are day-first. For example 09/03/2026 is 9 March 2026.
Show dates as dd-mmm-yyyy, for example 09-Mar-2026.
Budget is in Singapore dollars. Convert text such as 12.5k, SGD 12,500 and $12,500 to the number 12500.
Format money as S$ with thousands separators and no decimals, e.g. S$12,500. Show negative values in red in brackets.
## TABLES AND FORMULAS
Format every new data range as an Excel table named tbl + the sheet name without underscores, e.g. tblOrdersClean.
Use XLOOKUP for lookups and return "Not found" when there is no match.
Never merge cells."""

SKILL_CALENDAR = """---
name: interview-calendar
description: Use when I ask for an interview calendar, an interview schedule or interview clashes for a week. Builds a Monday-to-Friday calendar from the interviews table and flags double-bookings.
---

# Interview calendar

Turn the list of interviews into a weekly calendar that a recruiter can read at a glance, and flag clashes.

## Input
- The interviews table (tblInterviews) with Interview_ID, Role, Interviewer, Interview_Date, Start_Time, Duration_Min, Mode and Room.
- A week start date (a Monday). If I do not give one, ask me for it before you start.

## Steps
1. Never change tblInterviews or any existing sheet.
2. Create a new sheet named Cal_<week start as yyyy-mm-dd>, e.g. Cal_2026-07-06. If it already exists, replace its contents.
3. In A1 write "Interview calendar - week of <week start as dd mmm yyyy>". In A2 write "Created by Copilot".
4. Build the grid from row 4: column A holds 30-minute time slots from 09:00 to 17:30; columns B to F are Monday to Friday, with the date in each header.
5. Place every interview of that week in each slot it covers (an interview of 60 minutes fills two slots). Show "Interviewer - Role (Mode)". If two interviews share a slot, show both, separated by " | ".
6. Colour Onsite interviews light blue and Video interviews light green.
7. Find clashes: two interviews on the same date that overlap in time AND have the same Interviewer, or are both Onsite in the same Room. Colour those calendar cells red.
8. Below the grid, add a table Clashes with Type (Interviewer or Room), Interview_ID 1, Interview_ID 2, Who or Room, Date and Time. If there are none, write "No clashes this week".
9. Next to it, add a Summary table: interviews per day, interviews per Interviewer and the week total.
10. Freeze the header row and time column, set column widths so the text is readable, and do not merge cells.

## Check before you finish
- The number of interviews placed equals the number of rows in tblInterviews for that week.
- Report the week total, the busiest day and every clash in your reply.
"""


DOMAIN2 = [
    # ------------------------------------------------------------------ LAB 4
    dict(
        num=4,
        topic=2,
        title="Clean Messy Client Orders with Cleanup, Personalisation and Rules",
        theme="Workbook Rules & Personalisation",
        duration=40,
        objective=(
            "LO2: set personal preferences, use Copilot's automated cleanup, and write a .Rules worksheet that makes "
            "Copilot clean and calculate a messy export the same way every time"
        ),
        goal=(
            "Turn a messy client-orders export into a clean, consistent table with short prompts, because the "
            "workbook's .Rules sheet already holds the standards."
        ),
        workflow=["Personalise", "Automated cleanup", "Create .Rules", "Apply the rules", "Rules + XLOOKUP"],
        desc=(
            "BrightPath's order system exports client orders that several people typed by hand: 'WIP', 'in progress' and "
            "'Ongoing' all mean In Progress, regions are written 23 ways and client names carry 'Pte Ltd' suffixes. You will "
            "save your own preferences in Personalization, try Copilot's automated cleanup, then create a .Rules sheet that "
            "defines the workbook's standards. With the rules in place, a one-line prompt builds a clean table, and the same "
            "rules shape the XLOOKUP and budget columns you add next."
        ),
        build=(
            "Your Personalization (saved to your account) and BrightPath_Client_Orders_Raw.xlsx with a .Rules sheet, a clean tblOrdersClean "
            "table (5 statuses, 5 regions, 12 clients), Rate, Delivered_Value, Budget_Used and Over_Budget columns, and a "
            "Checks sheet that proves the clean-up"
        ),
        services="Excel · Copilot (Allow editing, Chat only) · Personalization · Clean data with Copilot · .Rules worksheet · XLOOKUP",
        data_files=["data/BrightPath_Client_Orders_Raw.xlsx"],
        extra_files=[("rules-template.txt", RULES_LAB4 + "\n", "the .Rules text to paste into column A")],
        prerequisites=[
            "Topic 1 completed: you can switch Copilot modes, keep or undo changes, and verify with formulas.",
            "This lab folder's data/BrightPath_Client_Orders_Raw.xlsx and rules-template.txt.",
        ],
        steps=[
            (
                _SETUP_STEP.format(file="BrightPath_Client_Orders_Raw.xlsx")
                + " Scroll through Orders_Raw and spot three ways the same status or region is written.",
                "Sheets : About_This_Data | Orders_Raw (64 orders, not a table) | Rate_Card (tblRateCard) | Prompt_Log\n"
                f"Messy : {E4['raw_status_distinct']} Status spellings | {E4['raw_region_distinct']} Region spellings | "
                f"{E4['raw_client_distinct']} Client spellings\n"
                f"Clean : {len(STATUSES)} statuses | {len(REGIONS)} regions | {E4['clients']} clients",
            ),
            (
                "Personalisation is about you, not this file. In the Copilot pane select Settings (...) > Personalization, type "
                "the preferences below one per line, select Save and then start a New chat. They now apply in every workbook you "
                "open. A prompt that asks for something different still wins.",
                "Charts      : Use column charts rather than bar charts unless the category labels are long.\n"
                "Colours     : Use navy #1F4E79 and teal #2A9D8F as the main chart colours.\n"
                "Layout      : Never merge cells; leave one empty column between blocks of content.\n"
                "PivotTables : Give fields readable names, e.g. Hires instead of Sum of Hires.",
            ),
            (
                "Try automated cleanup. Click inside Orders_Raw and select Data > Clean Data (or Show suggestions if Excel offers "
                "'Clean data with Copilot'). Hover over each suggestion to see the cells it affects, then Apply the extra-space "
                "and capitalisation fixes. Then ask Copilot what is still inconsistent: cleanup fixes typing, but it cannot know "
                "that WIP means In Progress or that C means CENTRAL - that needs rules.",
                "CHAT ONLY:\n"
                "On Orders_Raw, list the distinct values in Status, Region and Client with a count of each. Group the\n"
                "values that probably mean the same thing. Do not change anything.",
            ),
            (
                "Create the rules sheet. In the prompt box select + (Add work content) > Create workbook rules. Copilot adds a "
                ".Rules sheet with suggested rules. Replace them with BrightPath's rules: open rules-template.txt from this lab "
                "folder, copy every line, click .Rules!A1 and paste (each line lands in its own cell in column A), or send the "
                "prompt below. Keep the .Rules sheet visible - Copilot ignores a hidden one.",
                "ALLOW EDITING:\n"
                "On the .Rules sheet, replace everything in column A with these rules, one per cell from A1 down.\n"
                "Keep each ## heading in its own cell. Do not change any other sheet.\n" + RULES_LAB4,
            ),
            (
                "Apply the rules with a one-line prompt in a New chat. Copilot reads .Rules before it works, so you do not repeat "
                f"the standards. Inspect the result: A1 says Created by Copilot, the table is tblOrdersClean, {E4['paused_ids'][0]} "
                f"and {E4['paused_ids'][1]} are On Hold (their notes say the work is paused), dates read like 09-Mar-2026 and "
                "budgets are numbers formatted as S$. Select Done to keep it.",
                "ALLOW EDITING:\n"
                "Create a new sheet Orders_Clean with a clean copy of every order on Orders_Raw, following the workbook rules.",
            ),
            (
                "Prove the clean-up. Ask Copilot to add independent checks on a Checks sheet. Each result must equal the "
                "expected value in Test It.",
                "CHECK (Allow editing):\n"
                "Create a sheet named Checks. Enter these labels and formulas exactly as written, then tell me each result:\n"
                "A1 Orders              B1 =ROWS(tblOrdersClean[Order_ID])\n"
                "A2 Distinct statuses   B2 =COUNTA(UNIQUE(tblOrdersClean[Status]))\n"
                "A3 Distinct regions    B3 =COUNTA(UNIQUE(tblOrdersClean[Region]))\n"
                "A4 Distinct clients    B4 =COUNTA(UNIQUE(tblOrdersClean[Client]))\n"
                "A5 In Progress         B5 =COUNTIF(tblOrdersClean[Status],\"In Progress\")\n"
                "A6 Total budget        B6 =SUM(tblOrdersClean[Budget])",
            ),
            (
                "Add calculated columns. The rules already say to use XLOOKUP with 'Not found' and how to format money, so the "
                f"prompt only states the business logic. Check one row by hand: {_S['id']} is {_S['hours']} hours x "
                f"S${_S['rate']} ({_S['owner']}) = {_money(_S['value'])} against a budget of {_money(_S['budget'])}, so it is over budget.",
                "ALLOW EDITING:\n"
                "In tblOrdersClean add: Rate from tblRateCard by Owner; Delivered_Value = Hours_Logged x Rate;\n"
                "Budget_Used = Delivered_Value / Budget as a percentage with 1 decimal; Over_Budget = \"Yes\" when\n"
                "Delivered_Value is greater than Budget, otherwise \"No\".\n\n"
                "FOLLOW-UP:\n"
                "On the Checks sheet, add the label Total delivered value in A7 with =SUM(tblOrdersClean[Delivered_Value]) "
                "in B7, and the label Over budget in A8 with =COUNTIF(tblOrdersClean[Over_Budget],\"Yes\") in B8.\n"
                "Then list the over-budget orders.",
            ),
            (
                "Add a rule, then reuse it. Rules can grow: ask Copilot to add one, then apply it with a short prompt. Rules are "
                "saved in the file, so a colleague who opens this workbook gets them too. Log your prompts.",
                "ALLOW EDITING:\n"
                "Add a rule under ## TABLES AND FORMULAS on the .Rules sheet: Highlight rows where Over_Budget is Yes in\n"
                "light red.\n\n"
                "ALLOW EDITING:\n"
                "Apply the workbook rules to tblOrdersClean.\n\n" + _LOG,
            ),
        ],
        sample_prompts=[
            ("Create rules", "Create a .Rules worksheet based on the formatting already used in this workbook."),
            ("Add a rule", "Add a rule to my .Rules worksheet that all charts should use navy #1F4E79 and teal #2A9D8F."),
            ("Apply rules", "Create a new sheet Orders_Clean with a clean copy of Orders_Raw, following the workbook rules."),
            ("Find variants", "List the distinct values in Status and Region with counts, and group the ones that mean the same thing."),
            ("Rules + lookup", "Add Rate from tblRateCard by Owner and Delivered_Value = Hours_Logged x Rate to tblOrdersClean."),
            ("Question", "Which client has the largest total budget, and how many orders does it have?"),
            ("Explain", "Which rules on the .Rules sheet did you follow to clean the Status column? Give two examples."),
            ("New sheet", "Create a new sheet showing orders with a budget over S$50,000 by Owner."),
        ],
        test=(
            f"tblOrdersClean has {E4['rows']} orders with exactly {len(STATUSES)} statuses, {len(REGIONS)} regions and "
            f"{E4['clients']} clients. Status counts: "
            + ", ".join(f"{k} {v}" for k, v in E4["status_counts"].items())
            + f". {E4['paused_ids'][0]} and {E4['paused_ids'][1]} are On Hold. Total budget {_money(E4['total_budget'])}; total "
            f"delivered value {_money(E4['total_value'])}; {E4['over_n']} orders are over budget. {E4['top_client']} has the "
            f"largest total budget ({_money(E4['top_client_budget'])}). Orders_Raw still has its original {E4['rows']} rows."
        ),
        checkpoint="Keep the workbook in work-c34. Your Personalization stays with your account for the rest of the course.",
        troubleshooting=[
            (
                "Copilot ignores the rules.",
                "The sheet must be named exactly .Rules (with the full stop), be visible, and have the rules in column A. Start "
                "a New chat after changing it.",
            ),
            (
                "Create workbook rules is not in the + menu.",
                "Create a sheet named .Rules yourself and paste rules-template.txt into A1, or ask Copilot: 'Create a .Rules "
                "worksheet with these rules ...'.",
            ),
            (
                "There is no Clean Data button.",
                "It is rolling out and may be missing in your build. Skip Step 3 - the rules in Steps 4-5 do the same job.",
            ),
            (
                "ORD-302 or ORD-303 still shows Open.",
                "Copilot missed the Notes rule. Ask: 'Apply the rule about paused work in Notes to tblOrdersClean.'",
            ),
        ],
        challenge=(
            "Make a rule respond to the workbook: put a dropdown in .Rules!B1 with Executive and Analyst, and in A20 enter "
            "=IF(B1=\"Executive\",\"New summary sheets show totals only\",\"New summary sheets include a detail table\"). Switch "
            "the dropdown and ask for an order summary by Region each time."
        ),
        reflection="Which three corrections do you give Copilot most often? Which belong in Personalization, and which in a workbook's .Rules?",
    ),
    # ------------------------------------------------------------------ LAB 5
    dict(
        num=5,
        topic=2,
        title="Analyse HR-Outsourcing Finances with Built-in Skills",
        theme="Built-in Skills: Visual & Finance",
        duration=40,
        objective=(
            "LO2: find, enable and call Copilot's built-in skills - chart-design, unit-economics, check-model and "
            "theme-design - and verify what each skill produces"
        ),
        goal=(
            "Use four built-in skills to chart BrightPath's recurring revenue, calculate client unit economics, audit a "
            "headcount budget model and style the results - then prove the numbers."
        ),
        workflow=["Manage skills", "@chart-design", "@unit-economics", "@check-model", "@theme-design"],
        desc=(
            "BrightPath's HR-outsourcing business sells monthly payroll and HR services to client companies. Finance wants "
            "to know whether winning clients pays off and whether next year's headcount budget is right. You will switch on "
            "skills in Manage plugins & skills, call them with @, and let each one do a specialist job: @chart-design builds "
            "the revenue chart, @unit-economics works out CAC, LTV and payback, @check-model finds the errors in the budget "
            "model, and @theme-design styles the workbook. A Checks sheet proves every headline number."
        ),
        build=(
            "BrightPath_HR_Outsourcing_Finance.xlsx with a skill-designed MRR chart, a Unit_Economics sheet, a corrected "
            "Headcount_Budget, a Checks sheet that agrees with the skills, and a consistent theme"
        ),
        services="Excel · Copilot (Allow editing, Plan, Chat only) · @chart-design · @unit-economics · @check-model · @theme-design",
        data_files=["data/BrightPath_HR_Outsourcing_Finance.xlsx"],
        prerequisites=[
            "Lab 4 completed: you know how rules guide Copilot inside one workbook.",
            "This lab folder's data/BrightPath_HR_Outsourcing_Finance.xlsx. Skills need Excel's display language set to English.",
        ],
        steps=[
            (
                _SETUP_STEP.format(file="BrightPath_HR_Outsourcing_Finance.xlsx")
                + " Read the Definitions row on About_This_Data - you will hold the finance skill to these.",
                "Tables : tblClientMonths (18 months) | tblClients | tblSpend | Headcount_Budget (cost model)\n"
                "H1 2026 = Jan-Jun 2026\n"
                "CAC     = sales & marketing spend / new clients\n"
                "ARPA    = MRR / active clients at Jun 2026\n"
                "LTV     = ARPA x gross margin / monthly churn\n"
                "Payback = CAC / (ARPA x gross margin), in months",
            ),
            (
                "Turn on the skills. In the Copilot pane select Settings (...) > Manage plugins & skills. Open the Finance "
                "folder and turn on unit-economics and check-model. Open the Visualisation folder and turn on chart-design (it is "
                "off by default). Leave every other skill as it is. Close the dialog, type @ in the prompt box and confirm all "
                "three are listed. theme-design (Step 7) sits in a Formatting folder that is still rolling out - if you have no "
                "Formatting folder, skip it; Step 7 shows what to do.",
                "Where         : Settings (...) > Manage plugins & skills - turn on only these\n"
                "Finance       : unit-economics, check-model\n"
                "Visualisation : chart-design (off by default)\n"
                "Formatting    : theme-design - only if this folder is shown\n"
                "Call a skill  : type @ and its name, e.g. @chart-design\n\n"
                "CHAT ONLY:\n"
                "Which of your skills would help me analyse client acquisition cost and churn in this workbook, and\n"
                "which would help me audit the Headcount_Budget sheet? Do not change anything.",
            ),
            (
                "Call @chart-design (Visualisation) in Allow editing. It chooses and formats the chart using the Excel design "
                f"team's guidance. Check the values: MRR grows from {_money(E5['mrr_jan25'])} in Jan 2025 to "
                f"{_money(E5['mrr_end'])} in Jun 2026, with {E5['active_end']} active clients at the end.",
                "ALLOW EDITING:\n"
                "@chart-design Create a combo chart on a new sheet Charts from tblClientMonths: MRR as columns and\n"
                "Clients_End as a line on a secondary axis, Jan 2025 to Jun 2026.\n\n"
                "FOLLOW-UP:\n"
                "@chart-design Improve this chart for a leadership slide: a title that states the finding, axis titles\n"
                "with units, and a data label on the last month only.",
            ),
            (
                "Call the finance skill @unit-economics in Plan mode, so you can review its approach before it builds. Check that "
                "the plan uses H1 2026 and the About_This_Data definitions; reply with corrections if not, then approve and "
                "select Done.",
                "PLAN MODE:\n"
                "@unit-economics Analyse the unit economics of BrightPath's HR-outsourcing clients for H1 2026 using\n"
                "tblClientMonths, tblClients and tblSpend. Use the definitions on About_This_Data. Put the results on a\n"
                "new sheet Unit_Economics: CAC, ARPA, gross margin, monthly churn, LTV, LTV:CAC and payback months, plus\n"
                "CAC by Channel. List your assumptions.",
            ),
            (
                "Never trust a skill's numbers without a check. Ask Copilot to add these independent formulas, then compare them "
                "with the Unit_Economics sheet. If they differ, ask the skill to show its calculation and use the definition.",
                "CHECK (Allow editing):\n"
                "Create a sheet named Checks. Enter these labels and formulas exactly as written, then tell me each result:\n"
                "A1 New clients H1      B1 =SUMIFS(tblClientMonths[New_Clients],tblClientMonths[Month],\">=\"&DATE(2026,1,1))\n"
                "A2 S&M spend H1        B2 =SUMIFS(tblClientMonths[Sales_Marketing_Spend],tblClientMonths[Month],\">=\"&DATE(2026,1,1))\n"
                "A3 CAC                 B3 =B2/B1\n"
                "A4 ARPA                B4 =INDEX(tblClientMonths[MRR],18)/INDEX(tblClientMonths[Clients_End],18)\n"
                "A5 Gross margin        B5 =AVERAGEIFS(tblClientMonths[Gross_Margin_Pct],tblClientMonths[Month],\">=\"&DATE(2026,1,1))\n"
                "A6 Monthly churn       B6 =AVERAGE(FILTER(tblClientMonths[Churned_Clients]/tblClientMonths[Clients_Start],tblClientMonths[Month]>=DATE(2026,1,1)))\n"
                "A7 LTV                 B7 =B4*B5/B6\n"
                "A8 LTV to CAC          B8 =B7/B3\n"
                "A9 Payback months      B9 =B3/(B4*B5)\n\n"
                "FOLLOW-UP:\n"
                "Compare Checks!B3:B9 with the Unit_Economics sheet. Show any value that differs and why.",
            ),
            (
                "Audit a model with @check-model. Ask for the findings first in Chat only, read them, then switch to Allow editing "
                f"and ask for the fixes. It should find three problems: a typed number in {E5['hard_cell']}, an 11-month formula "
                f"in {E5['eleven_cell']} and a total in {E5['total_cell']} that misses the last role.",
                "CHAT ONLY:\n"
                "@check-model Audit the Headcount_Budget sheet: look for typed numbers in formula columns, formulas that\n"
                "differ from their neighbours, and totals that miss rows. List each issue with its cell, what is wrong and\n"
                "the fix. Do not change anything yet.\n\n"
                "ALLOW EDITING:\n"
                "Fix the issues you found on Headcount_Budget and tell me the new Total FY2027 cost.",
            ),
            (
                "Style the workbook with @theme-design (Formatting). It applies one coordinated theme to cells, tables and charts. "
                "If theme-design is not in your @ list, your account does not have it yet: delete @theme-design and run the rest "
                "of the prompt as it is. If your organisation has set up a brand kit, try @brandkit instead. Then log your prompts.",
                "ALLOW EDITING:\n"
                "@theme-design Apply one clean, professional theme to the Charts, Unit_Economics, Checks and\n"
                "Headcount_Budget sheets.\n\n" + _LOG,
            ),
        ],
        sample_prompts=[
            ("Find skills", "Which skills do you have for charts, formatting and finance? When would I use each one?"),
            ("Chart skill", "@chart-design Recommend the best chart for new vs churned clients by month, then create it."),
            ("Finance skill", "@unit-economics Compare CAC and payback months by acquisition Channel for H1 2026."),
            ("Audit skill", "@check-model Check this sheet for hardcoded numbers, broken formulas and totals that miss rows."),
            ("Style skill", "@theme-design Apply a coordinated theme to this workbook."),
            ("Brand skill", "@brandkit Apply our organisation's brand colours and fonts to the charts."),
            ("Explain", "Explain how you calculated LTV, step by step, with the cells you used."),
            ("Question", "Which acquisition channel has the lowest CAC in H1 2026, and how many clients did it bring?"),
        ],
        test=(
            f"Checks: new clients in H1 2026 = {E5['new_h1']}, S&M spend = {_money(E5['spend_h1'])}, CAC = "
            f"{_money(E5['cac'])}, ARPA = {_money(E5['arpa'])}, gross margin = {E5['gm_h1']}%, monthly churn = "
            f"{E5['churn_m']}%, LTV = about {_money(E5['ltv'])}, LTV:CAC = {E5['ltv_cac']} and payback = {E5['payback']} "
            f"months. {E5['best_channel']} has the lowest CAC ({_money(E5['by_channel'][E5['best_channel']]['cac'])}) and "
            f"{E5['worst_channel']} the highest ({_money(E5['by_channel'][E5['worst_channel']]['cac'])}). @check-model found "
            f"{E5['hard_cell']} ({E5['hard_role']}, typed number), {E5['eleven_cell']} ({E5['eleven_role']}, 11 months) and "
            f"{E5['total_cell']} (total misses {E5['last_role']}); after the fixes the total rises from "
            f"{_money(E5['budget_reported'])} to {_money(E5['budget_correct'])}."
        ),
        checkpoint="Keep the workbook in work-c34. Lab 6 needs your OneDrive for one thing only: custom skills are stored there.",
        troubleshooting=[
            (
                "Manage plugins & skills is missing or greyed out.",
                "Wait 10 seconds - it loads after the pane. Then check Excel is up to date and the Office display language is English.",
            ),
            (
                "A skill is not listed when I type @.",
                "Turn it on in Manage plugins & skills, or type its full name: an @mention works even when the skill is off.",
            ),
            (
                "The skill's CAC or LTV differs from Checks.",
                "Skills use their own defaults. Ask: 'Use the definitions on About_This_Data and recalculate CAC and LTV.'",
            ),
            (
                "@check-model changes the sheet straight away.",
                "You were in Allow editing. Select Undo, switch to Chat only and ask for the findings first.",
            ),
        ],
        challenge=(
            "Ask @unit-economics for a client cohort table by Sign_Date quarter showing how many clients from each cohort are "
            "still active. Check one cohort with COUNTIFS on tblClients."
        ),
        reflection="Which skill saved you the most time, and which of its numbers would you not have trusted without the Checks sheet?",
    ),
    # ------------------------------------------------------------------ LAB 6
    dict(
        num=6,
        topic=2,
        title="Use Copilot to Build a Custom Interview-Calendar Skill",
        theme="Custom Skills: Calendar",
        duration=45,
        objective=(
            "LO2: use Copilot to write a custom SKILL.md, save it in the OneDrive skills folder, call it with @, and improve it "
            "so a weekly task runs from a one-line prompt"
        ),
        goal=(
            "Create an interview-calendar skill that turns BrightPath's interview list into a weekly calendar with clashes "
            "flagged - and reuse it for the next week with one short prompt."
        ),
        workflow=["Skills folder", "Copilot writes SKILL.md", "Save & refresh", "@interview-calendar", "Reuse & improve"],
        desc=(
            "Every Friday a BrightPath coordinator turns next week's interview bookings into a calendar and hunts for "
            "double-bookings. That is a repeatable recipe, so it should be a skill. You will open the sample calendar skill in "
            "your OneDrive skills folder, ask Copilot to write a new SKILL.md for interview-calendar, save it in its own folder, "
            "refresh the skills list and call it with @. The same one-line prompt then builds the next week's calendar."
        ),
        build=(
            "An interview-calendar skill in your OneDrive skills folder, and BrightPath_Interview_Schedule.xlsx with "
            "Cal_2026-07-06 and Cal_2026-07-13 calendar sheets, each with clashes flagged and a summary"
        ),
        services="Excel · Copilot (Chat only, Allow editing) · Manage plugins & skills · OneDrive skills folder · SKILL.md",
        data_files=["data/BrightPath_Interview_Schedule.xlsx"],
        extra_files=[("skills/interview-calendar/SKILL.md", SKILL_CALENDAR,
                      "ready-made skill to upload if you run short of time")],
        prerequisites=[
            "Lab 5 completed: you can find, enable and @mention skills.",
            "Access to your OneDrive in a browser (custom skills are stored in a OneDrive folder).",
            "This lab folder's data workbook and skills/interview-calendar/SKILL.md (fallback).",
        ],
        steps=[
            (
                _SETUP_STEP.format(file="BrightPath_Interview_Schedule.xlsx")
                + " The workbook stays local; only the skill file goes in OneDrive (Step 2).",
                "Table  : tblInterviews (41 interviews, 6-17 July 2026)\n"
                "Week 1 : Mon 6 July - Fri 10 July 2026\n"
                "Week 2 : Mon 13 July - Fri 17 July 2026\n"
                "Clash  : same Interviewer overlapping, or two Onsite interviews in the same Room overlapping",
            ),
            (
                "Create your skills folder. In the Copilot pane select Settings (...) > Manage plugins & skills > Custom skills and "
                "turn the Custom skills switch on. Then select Add in OneDrive (in some versions: Create OneDrive folder, then Open "
                "skills folder). OneDrive opens a folder named skills, usually under Documents > Copilot > Microsoft Excel. Open the sample calendar skill folder (e.g. make-calendar.example) and read its "
                "SKILL.md: a front matter block between --- lines, then plain-English steps.",
                "Folder      : skills/<skill-name>/   (folder name = the skill name, lower case with hyphens)\n"
                "File        : SKILL.md\n"
                "Front matter: name (the skill name) and description (when Copilot should use it)\n"
                "Body        : the steps Copilot follows - plain English, no code needed",
            ),
            (
                "Let Copilot write the skill. In Excel, choose Chat only and send the prompt below. Read the reply: it should start "
                "with --- name: interview-calendar, have a description that says when to use it, and list clear steps. Ask for "
                "changes until you are happy.",
                "CHAT ONLY:\n"
                "Write a Copilot in Excel custom skill as a complete SKILL.md file.\n"
                "Name: interview-calendar\n"
                "Description: Use when I ask for an interview calendar, schedule or clashes for a week.\n"
                "The skill must:\n"
                "1) Read tblInterviews (Interview_ID, Role, Interviewer, Interview_Date, Start_Time, Duration_Min, Mode, Room).\n"
                "2) Ask for the week start date (a Monday) if I do not give one.\n"
                "3) Create a sheet Cal_<yyyy-mm-dd> with Monday to Friday as columns and 30-minute rows from 09:00 to 17:30.\n"
                "4) In each slot show Interviewer - Role (Mode); colour Onsite light blue and Video light green.\n"
                "5) Flag clashes: overlapping interviews with the same Interviewer, or Onsite interviews in the same Room.\n"
                "   Colour them red and list them in a Clashes table under the calendar.\n"
                "6) Add a summary of interviews per day and per Interviewer.\n"
                "7) Never change tblInterviews.\n"
                "Return only the SKILL.md text, starting with the --- front matter.",
            ),
            (
                "Save the skill. Copy Copilot's reply into a plain-text editor (Notepad, or TextEdit in plain-text mode) and save "
                "it as SKILL.md. In the OneDrive skills folder select New > Folder, name it interview-calendar, open it and Upload "
                "SKILL.md. Short of time? Upload skills/interview-calendar/SKILL.md from this lab folder instead.",
                "OneDrive : .../skills/interview-calendar/SKILL.md\n"
                "Check    : the folder name and the name: line are both exactly interview-calendar\n"
                "Check    : the file is called SKILL.md (not SKILL.md.txt)",
            ),
            (
                "Make Excel see the new skill: Settings (...) > Manage plugins & skills > Custom skills, check the Custom skills "
                "switch is on and select Refresh (the round arrow). Wait until the list loads, then turn interview-calendar on. Close the dialog and type @inter in the prompt box - the skill should appear.",
                "",
            ),
            (
                "Run the skill in Allow editing with a one-line prompt. First check that the title bar shows "
                "BrightPath_Interview_Schedule: the skill is available in every workbook, but it only works where tblInterviews "
                "exists. When it finishes, inspect the calendar and select Done. "
                "Then ask Copilot to add the check formula and compare it with the number of interviews on the calendar.",
                "ALLOW EDITING:\n"
                "@interview-calendar Build the calendar for the week starting Monday 6 July 2026.\n\n"
                "CHECK (Allow editing):\n"
                "In an empty cell to the right of the calendar, add this formula and tell me whether it matches the\n"
                "number of interviews on the calendar:\n"
                "=COUNTIFS(tblInterviews[Interview_Date],\">=\"&DATE(2026,7,6),tblInterviews[Interview_Date],\"<=\"&DATE(2026,7,10))",
            ),
            (
                "Reuse it. This is the point of a skill: next week's calendar needs only the skill name and a date. Week 2 has no "
                "clashes - check the skill says so.",
                "ALLOW EDITING:\n"
                "@interview-calendar Week starting 13 July 2026.",
            ),
            (
                "Improve the skill. Ask Copilot to update the file, save it over SKILL.md in OneDrive, select Refresh in Custom "
                "skills and rerun week 1. A skill is a living recipe: improve it whenever you correct Copilot twice. Log your prompts.",
                "CHAT ONLY:\n"
                "Update the interview-calendar SKILL.md so the summary also shows total interview hours per Interviewer,\n"
                "and the reply lists the busiest day. Return the full updated file.\n\n" + _LOG,
            ),
        ],
        sample_prompts=[
            ("Write a skill", "Write a SKILL.md for a skill named weekly-recruiter-report that summarises interviews by Interviewer and Client for a given week, with a small bar chart."),
            ("Explain a skill", "Read this SKILL.md and tell me what Copilot will do, step by step, and anything that is unclear."),
            ("Call a skill", "@interview-calendar Build the calendar for the week starting Monday 6 July 2026."),
            ("Reuse", "@interview-calendar Week starting 13 July 2026."),
            ("Clash check", "List every interview clash in tblInterviews for 6-10 July 2026 with both Interview_IDs."),
            ("Improve", "Update the skill so Video interviews show the Teams icon text [Teams] and the calendar prints on one A4 page."),
            ("Question", "Which interviewer has the most interviews in the week of 6 July, and on which day?"),
        ],
        test=(
            f"Week of 6 July: {E6['w1']} interviews ("
            + ", ".join(f"{k} {v}" for k, v in E6["by_day"].items())
            + f"), {E6['w1_hours']:g} interview hours, {E6['w1_video']} by video; the COUNTIFS check returns {E6['w1']}. The "
            f"skill flags {len(E6['clashes'])} clashes: "
            + "; ".join(f"{c[1]} and {c[2]} ({c[0].lower()} clash: {c[3]}, {c[4]})" for c in E6["clashes"])
            + f". {E6['busiest']} has the most interviews ({E6['busiest_n']}). Week of 13 July: {E6['w2']} interviews and no "
            "clashes. The skill appears when you type @ and tblInterviews is unchanged."
        ),
        checkpoint=(
            "Keep the skill: it stays in your OneDrive and works in any workbook with an interviews table. Topic 3 uses "
            "rules and skills to build dashboards."
        ),
        troubleshooting=[
            (
                "The skill does not appear after Refresh.",
                "The folder name must match the name: line exactly (lower case, hyphens) and the file must be SKILL.md inside "
                "that folder. Select Refresh again.",
            ),
            (
                "There is no Add in OneDrive or Create OneDrive folder button.",
                "Custom skills are rolling out and depend on your licence and update channel. Use the ready-made SKILL.md to "
                "read the format, and run the same steps as a normal prompt instead.",
            ),
            (
                "Copilot says tblInterviews is not present in this workbook.",
                "The skill ran in another lab's workbook. Open BrightPath_Interview_Schedule.xlsx and send the prompt again "
                "from its Copilot pane.",
            ),
            (
                "The calendar misses a clash.",
                "Ask: 'Check again for overlapping interviews with the same Interviewer or the same Onsite Room on each day.' "
                "Then add that wording to the skill's steps.",
            ),
            (
                "The file saved as SKILL.md.txt or with formatting.",
                "Save as plain text with the exact name SKILL.md. In TextEdit choose Format > Make Plain Text first.",
            ),
        ],
        challenge=(
            "Ask Copilot to write a second skill, weekly-recruiter-report, that summarises interviews by Interviewer and Client "
            "for a given week with a small bar chart. Save it, refresh and call it."
        ),
        reflection="Which weekly or monthly task in your own job would make the best first custom skill, and what would its description say?",
    ),
]

# Test-it checklist: (what to check, expected result).
_CHECKS = {
    4: [
        ("Orders and distinct values (Checks B1:B4)", f"{E4['rows']} orders; {len(STATUSES)} statuses, {len(REGIONS)} regions, {E4['clients']} clients"),
        ("Status counts", ", ".join(f"{k} {v}" for k, v in E4["status_counts"].items())),
        ("Paused orders", f"{E4['paused_ids'][0]} and {E4['paused_ids'][1]} are On Hold"),
        ("Total budget (B6)", _money(E4["total_budget"])),
        ("Delivered value and over budget (B7, B8)", f"{_money(E4['total_value'])}; {E4['over_n']} orders over budget"),
        (f"Sample {_S['id']}", f"{_S['hours']} h x S${_S['rate']} = {_money(_S['value'])} vs budget {_money(_S['budget'])} - Over_Budget Yes"),
    ],
    5: [
        ("New clients and spend, H1 2026", f"{E5['new_h1']} clients; {_money(E5['spend_h1'])}"),
        ("CAC and ARPA", f"{_money(E5['cac'])}; {_money(E5['arpa'])}"),
        ("Margin and monthly churn", f"{E5['gm_h1']}%; {E5['churn_m']}%"),
        ("LTV, LTV:CAC, payback", f"About {_money(E5['ltv'])}; {E5['ltv_cac']}; {E5['payback']} months"),
        ("CAC by channel", f"Lowest {E5['best_channel']} {_money(E5['by_channel'][E5['best_channel']]['cac'])}; highest {E5['worst_channel']} {_money(E5['by_channel'][E5['worst_channel']]['cac'])}"),
        ("@check-model fixes", f"{E5['hard_cell']}, {E5['eleven_cell']}, {E5['total_cell']}: total {_money(E5['budget_reported'])} -> {_money(E5['budget_correct'])}"),
    ],
    6: [
        ("Week of 6 July", f"{E6['w1']} interviews = the COUNTIFS check"),
        ("By day", ", ".join(f"{k.split()[0]} {v}" for k, v in E6["by_day"].items())),
        ("Clashes flagged", "; ".join(f"{c[1]}/{c[2]} {c[3]}" for c in E6["clashes"])),
        ("Busiest interviewer", f"{E6['busiest']} ({E6['busiest_n']} interviews)"),
        ("Week of 13 July", f"{E6['w2']} interviews, no clashes"),
        ("Skill", "interview-calendar appears when you type @ and runs from a one-line prompt"),
    ],
}
for _a in DOMAIN2:
    _a["checks"] = _CHECKS[_a["num"]]
