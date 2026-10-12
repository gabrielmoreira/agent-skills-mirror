"""Topic 3 labs for C34: Interactive Dashboards with Copilot, Skills and Rules (BrightPath recruitment and workforce data)."""

from mock_data import EXPECTED, _lab7
from data_domain1 import _LOG, _SETUP_STEP

E7 = EXPECTED[7]
E8 = EXPECTED[8]
_BM = E7["by_month"]
_RD = E8["by_dept"]["Recruitment"]
_TARGET = sum(t for _m, t in _lab7()[2])
_HVT = round(E7["hires"] / _TARGET * 100, 1)
_Q2 = sum(v for k, v in _BM.items() if k >= "2026-04")

RULES_LAB7 = """## DASHBOARD STANDARDS
This workbook builds BrightPath's H1 2026 recruitment dashboard. Never change tblApps or tblTargets.
Applications = rows of tblApps. Hires = Furthest_Stage "Hired", counted by Hire_Date month.
Offer acceptance rate = accepted / (accepted + declined). Pending offers are excluded.
Avg time to hire = average Time_to_Hire_Days of hires. Cost per hire = total Sourcing_Cost / hires.
KPI cards are formulas linked to the PivotTables (GETPIVOTDATA) so they respond to slicers - never typed numbers.
## LAYOUT
Dashboard sheet: title in A1, "Data as at 2026-06-30" in A2, KPI cards in row 4, charts in a grid below, slicers and the timeline on the right.
Put every PivotTable on a sheet named Dash_Data.
Never merge cells. Hide gridlines on the Dashboard sheet.
## VISUAL STYLE
Colours: navy #1F4E79 for hires, teal #2A9D8F for targets and comparisons, amber #F4A261 for warnings.
Every chart title states the finding, e.g. Technology led H1 hiring.
Money as S$ with no decimals, except Cost per hire with 2 decimals. Rates as % with 1 decimal. Days with 1 decimal."""

RULES_LAB8 = """## WORKFORCE DASHBOARD STANDARDS
Never change or delete existing rows of tblEmployees.
Never show Employee_ID, Monthly_Salary or any individual record on a dashboard.
The 12-month period is 2025-07-01 to 2026-06-30. Active on a date = Hire_Date on or before it and Exit_Date blank or after it.
Active headcount = employees with Status Active now, so new joiners count as soon as they are added to tblEmployees.
Attrition rate = exits in the period / ((active on 2025-07-01 + active on 2026-06-30) / 2). New joiners after 2026-06-30 do not change it.
Tenure_Years = years from Hire_Date to Exit_Date, or to 2026-06-30 if still active; use 0 for anyone hired after 2026-06-30.
Do not show any group of fewer than 5 employees. Group it into Other or leave it out.
## LAYOUT
Dashboard sheet HR_Dashboard: title in A1, "Data as at 2026-06-30" in A2, KPI cards in row 4, charts in a grid below, slicers on the right.
Put every PivotTable on a sheet named Dash_Data. Never merge cells. Hide gridlines on HR_Dashboard.
## VISUAL STYLE
Colours: navy #1F4E79 for headcount, teal #2A9D8F for hires, amber #F4A261 for exits and attrition.
Every chart title states the finding. Rates as % with 1 decimal. Years with 1 decimal."""

SKILL_DASHBOARD = """---
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
"""

DOMAIN3 = [
    # ------------------------------------------------------------------ LAB 7
    dict(
        num=7,
        topic=3,
        title="Build an Interactive Recruitment Dashboard with Rules and Skills",
        theme="Interactive Dashboard",
        duration=50,
        objective=(
            "LO3: combine a .Rules sheet, Plan mode and the chart-design and theme-design skills to build a highly visual "
            "recruitment dashboard with KPI cards, PivotCharts, slicers and a timeline, and verify every KPI"
        ),
        goal=(
            "Deliver a one-page H1 2026 recruitment dashboard that looks professional, responds to slicers and a timeline, "
            "and agrees with independent checks."
        ),
        workflow=["Write .Rules", "Build checks", "Plan mode", "Skills make it visual", "Slice & verify"],
        desc=(
            "BrightPath's Head of Recruitment wants one page that shows H1 2026 applications, hires, offer acceptance, time "
            "to hire, cost per hire and hires against target, and can be filtered by sector, source, recruiter and date. You "
            "will put the KPI definitions, layout and colours in a .Rules sheet, so the build prompt stays short. Copilot "
            "plans the dashboard in Plan mode, builds it, then @chart-design and @theme-design make it look professional. "
            "Finally you prove that every KPI, slicer and the timeline give the right numbers."
        ),
        build=(
            "BrightPath_Recruitment_Dashboard_Data.xlsx with a .Rules sheet, a Checks sheet, PivotTables on Dash_Data and a "
            "Dashboard sheet with six formula-driven KPI cards (one with traffic-light colours), four PivotCharts, Sector, "
            "Source and Recruiter slicers and a Hire_Date timeline"
        ),
        services="Excel · Copilot (Plan, Allow editing, Chat only) · .Rules · @chart-design · @theme-design · PivotCharts, slicers, timeline",
        data_files=["data/BrightPath_Recruitment_Dashboard_Data.xlsx"],
        extra_files=[("rules-template.txt", RULES_LAB7 + "\n", "the .Rules text to paste into column A")],
        prerequisites=[
            "Topic 2 completed: you can write .Rules and call skills with @.",
            "This lab folder's data workbook and rules-template.txt.",
        ],
        steps=[
            (
                _SETUP_STEP.format(file="BrightPath_Recruitment_Dashboard_Data.xlsx")
                + " Read the KPI definitions on About_This_Data - they go into the rules next.",
                "Tables : tblApps (600 applications, Jan-Jun 2026) | tblTargets (monthly hire targets)\n"
                "KPI definitions:\n"
                "  Applications          = number of rows\n"
                "  Hires                 = Furthest_Stage = \"Hired\", by Hire_Date month\n"
                "  Offer acceptance rate = accepted / (accepted + declined)   (Pending excluded)\n"
                "  Avg time to hire      = average Time_to_Hire_Days of hires\n"
                "  Cost per hire         = total Sourcing_Cost / hires",
            ),
            (
                "Write the dashboard's rules first. Select + (Add work content) > Create workbook rules, then replace the "
                "suggested rules with BrightPath's: paste rules-template.txt into .Rules!A1, or send the prompt below. From now "
                "on every prompt in this workbook follows these definitions, the layout and the colours.",
                "ALLOW EDITING:\n"
                "On the .Rules sheet, replace everything in column A with these rules, one per cell from A1 down.\n"
                "Keep each ## heading in its own cell. Do not change any other sheet.\n" + RULES_LAB7,
            ),
            (
                "Build the independent checks before the dashboard. These are the numbers the KPI cards must match.",
                "CHECK (Allow editing):\n"
                "Create a sheet named Checks. Enter these labels and formulas exactly as written, then tell me each result:\n"
                "A1 Applications        B1 =ROWS(tblApps[Application_ID])\n"
                "A2 Hires               B2 =COUNTIFS(tblApps[Furthest_Stage],\"Hired\")\n"
                "A3 Offer acceptance    B3 =COUNTIFS(tblApps[Offer_Accepted],\"Yes\")/(COUNTIFS(tblApps[Offer_Accepted],\"Yes\")+COUNTIFS(tblApps[Offer_Accepted],\"No\"))\n"
                "A4 Avg time to hire    B4 =AVERAGEIFS(tblApps[Time_to_Hire_Days],tblApps[Furthest_Stage],\"Hired\")\n"
                "A5 Cost per hire       B5 =SUM(tblApps[Sourcing_Cost])/B2\n"
                "A6 Hires vs target     B6 =B2/SUM(tblTargets[Hire_Target])",
            ),
            (
                "Switch to Plan mode and send the brief. Because the rules hold the definitions, layout and colours, the brief "
                "only says what to show. Read the plan: does it exclude Pending offers, count hires by Hire_Date month and put "
                "PivotTables on Dash_Data? Reply with corrections until it does, then approve it. Watch the steps, and select "
                "Done when Copilot finishes.",
                "PLAN MODE:\n"
                "Build a one-page, highly visual H1 2026 recruitment dashboard on the Dashboard sheet for BrightPath's\n"
                "Head of Recruitment, following the workbook rules.\n"
                "KPI cards: Applications, Hires, Offer acceptance rate, Avg time to hire, Cost per hire, Hires vs target %.\n"
                "Charts: hires by Hire_Date month vs Hire_Target (columns + line); hires by Sector (bar, sorted);\n"
                "applications by Source (bar, sorted); hires by Recruiter (column).\n"
                "Interactivity: slicers for Sector, Source and Recruiter and a timeline on Hire_Date, connected to every\n"
                "PivotTable.",
            ),
            (
                "Make it visual with skills, one prompt at a time, and keep or undo each change. @chart-design polishes every "
                "chart; the traffic-light rule makes the target card readable at a glance; @theme-design pulls the page together "
                "while keeping the rule colours.",
                "ALLOW EDITING:\n"
                "@chart-design Review every chart on the Dashboard: titles that state the finding, axis titles, data labels\n"
                "where they help, and the colours in the workbook rules.\n\n"
                "FOLLOW-UP:\n"
                "Colour the Hires vs target % card green at 100% or more, amber from 90% to 99.9% and red below 90%.\n\n"
                "FOLLOW-UP:\n"
                "@theme-design Apply a clean, modern theme to the Dashboard that keeps the colours in the workbook rules.",
            ),
            (
                "Verify. With no slicer or timeline selection, ask Copilot to compare each card with the Checks sheet and show "
                "the card formulas. Fix any difference with a targeted prompt - the most common error is including Pending offers.",
                "CHAT ONLY:\n"
                "Compare each KPI card on the Dashboard with Checks!B1:B6, with no slicer selected. Show each card's\n"
                "formula, its value, the Checks value and whether they match.\n\n"
                "ALLOW EDITING (if needed):\n"
                "The Offer acceptance rate card must exclude Offer_Accepted = \"Pending\", as the workbook rules say.\n"
                "Fix the card formula.",
            ),
            (
                "Test the interactivity. Set the Sector slicer to Technology and read the cards, then clear it. Then select "
                "April to June 2026 on the Hire_Date timeline and read the Hires card, then clear it. Ask Copilot to add the "
                "checks and compare.",
                "CHECK (Allow editing):\n"
                "On the Checks sheet, add these formulas in D1:D3 with labels in C1:C3, and tell me if they match the\n"
                "cards when Sector = Technology, and the Hires card when the timeline shows Apr-Jun 2026:\n"
                "=COUNTIFS(tblApps[Sector],\"Technology\")\n"
                "=COUNTIFS(tblApps[Sector],\"Technology\",tblApps[Furthest_Stage],\"Hired\")\n"
                "=COUNTIFS(tblApps[Hire_Date],\">=\"&DATE(2026,4,1),tblApps[Hire_Date],\"<=\"&DATE(2026,6,30))\n\n"
                "If a KPI card does not change, ask: \"Link the KPI cards to the PivotTables with GETPIVOTDATA so they respond to the slicers and timeline.\"",
            ),
            (
                "Ask Copilot (Chat only) to review the dashboard as the Head of Recruitment would, act on the valid points, and "
                "log your prompts.",
                "CHAT ONLY:\n"
                "Review this dashboard for a Head of Recruitment. What is unclear, missing or potentially misleading?\n"
                "Does it follow every rule on the .Rules sheet?\n\n" + _LOG,
            ),
        ],
        sample_prompts=[
            ("Plan", "Plan a recruitment dashboard following the workbook rules. Show me the plan first."),
            ("KPI card", "Create a KPI card for Cost per hire linked to the PivotTable with GETPIVOTDATA, formatted as S$."),
            ("Chart skill", "@chart-design Turn the hires-by-month chart into columns for hires and a line for Hire_Target."),
            ("Timeline", "Add a timeline on Hire_Date and connect it to every PivotTable on Dash_Data."),
            ("Visual cue", "Add data bars to the hires-by-recruiter table and traffic-light colours to the target card."),
            ("Theme skill", "@theme-design Apply a modern theme that keeps the colours in the workbook rules."),
            ("Review", "Does this dashboard follow every rule on the .Rules sheet? List any that it breaks."),
            ("Question", "Which recruiter made the most hires in H1 2026, and what was their average time to hire?"),
        ],
        test=(
            f"With no slicer selected the KPI cards match Checks: Applications {E7['apps']}, Hires {E7['hires']}, Offer "
            f"acceptance {E7['oar']}% ({E7['accepted']} accepted of {E7['decided']} decided; {E7['pending']} pending excluded), "
            f"Avg time to hire {E7['avg_tth']} days, Cost per hire S${E7['cph']:.2f}, Hires vs target {_HVT}% "
            f"({E7['hires']} of {_TARGET}, amber). Hires by month: "
            + ", ".join(f"{k} = {v}" for k, v in _BM.items())
            + f" (none in 2026-01). {E7['top_sector']} has the most hires ({E7['by_sector'][E7['top_sector']]}). With Sector = "
            f"Technology, Applications = {E7['tech_apps']}, Hires = {E7['tech_hires']} and Avg time to hire = "
            f"{E7['tech_avg_tth']:.1f} days. With the timeline at Apr-Jun 2026, Hires = {_Q2}. {E7['top_rec']} made the most "
            f"hires ({E7['top_rec_n']}). No KPI card contains a typed number, and the colours follow the rules."
        ),
        checkpoint="Keep the workbook in work-c34. Lab 8 turns this dashboard recipe into a reusable skill for workforce data.",
        troubleshooting=[
            (
                "Copilot builds before you approve the plan.",
                "You were in Allow editing. Select Undo, switch to Plan mode and resubmit.",
            ),
            (
                "KPI cards do not change with the slicers or timeline.",
                "Cards built with COUNTIFS on tblApps ignore slicers. Ask Copilot to link them to the PivotTables with GETPIVOTDATA.",
            ),
            (
                "The timeline cannot be added.",
                "A timeline needs a date field in a PivotTable. Ask Copilot to make sure Hire_Date is a date column and is in "
                "a PivotTable on Dash_Data.",
            ),
            (
                "Hires appear in January.",
                "The chart counts by Applied_Month. Ask Copilot to group hires by Hire_Date month, as the rules say.",
            ),
        ],
        challenge=(
            "Ask Copilot to add a small 'What changed' panel under the KPI cards with two sentences that use formulas (for "
            "example =\"Hires: \"&Checks!B2&\" of \"&SUM(tblTargets[Hire_Target])&\" target\"), so the text updates with the data."
        ),
        reflection="Which rule on your .Rules sheet saved you the most prompting, and which visual element makes the dashboard easiest to read?",
    ),
    # ------------------------------------------------------------------ LAB 8
    dict(
        num=8,
        topic=3,
        title="Turn the Dashboard into a Reusable Skill, Refresh It and Share It Safely",
        theme="Dashboard Skill, Refresh & Share",
        duration=45,
        objective=(
            "LO3: use Copilot to write a dashboard skill, run it on a workforce workbook with rules, prove the dashboard "
            "refreshes with new rows, and check it is safe to share"
        ),
        goal=(
            "Build BrightPath's workforce and attrition dashboard from a one-line skill call, prove it updates when new "
            "joiners arrive, and make sure no small group can be identified."
        ),
        workflow=["Write .Rules", "Draft skill on the web", "Run skill in Excel", "Refresh test", "Privacy & summary"],
        desc=(
            "BrightPath's HR Director needs the same kind of dashboard every month. Instead of repeating a long brief, you will "
            "ask Microsoft 365 Copilot at https://copilot.cloud.microsoft/ to write an hr-workforce-dashboard skill, "
            "save it to OneDrive and return to Excel to run it on the workforce workbook, "
            "whose .Rules sheet holds the period, the attrition definition and the privacy rule. Then you will append eight "
            "July joiners and refresh to prove the dashboard is live, check that no slicer combination exposes fewer than 5 "
            "people, and ask Copilot for a short leadership summary."
        ),
        build=(
            "An hr-workforce-dashboard skill in OneDrive, and BrightPath_Workforce_Headcount.xlsx with a .Rules sheet, helper "
            "columns, a Checks sheet and an HR_Dashboard with six KPI cards, four charts and Location and Job_Level slicers - "
            "refresh-tested and privacy-checked"
        ),
        services="Microsoft 365 Copilot web (https://copilot.cloud.microsoft/) to draft the skill · Excel Copilot to run it · .Rules · PivotTables, slicers, refresh",
        data_files=["data/BrightPath_Workforce_Headcount.xlsx"],
        extra_files=[("rules-template.txt", RULES_LAB8 + "\n", "the .Rules text to paste into column A"),
                     ("skills/hr-workforce-dashboard/SKILL.md", SKILL_DASHBOARD,
                      "ready-made skill to upload if you run short of time")],
        prerequisites=[
            "Lab 6 and Lab 7 completed: you can save a custom skill to OneDrive and build a dashboard with rules.",
            "This lab folder's data workbook, rules-template.txt and skills/hr-workforce-dashboard/SKILL.md (fallback).",
            "Access to https://copilot.cloud.microsoft/ with the same work account used in Excel and OneDrive.",
        ],
        steps=[
            (
                _SETUP_STEP.format(file="BrightPath_Workforce_Headcount.xlsx")
                + " Do not touch the New_Joiners_Jul2026 sheet until the refresh test.",
                "Table : tblEmployees (420 employees hired since 2019; Status Active or Exited)\n"
                "Period: 2025-07-01 to 2026-06-30\n"
                "Attrition rate = exits in period / ((active on 2025-07-01 + active on 2026-06-30) / 2)",
            ),
            (
                "Create the workbook rules: + (Add work content) > Create workbook rules, then paste rules-template.txt into "
                ".Rules!A1 or send the prompt below. Note the privacy rule - the skill will follow it.",
                "ALLOW EDITING:\n"
                "On the .Rules sheet, replace everything in column A with these rules, one per cell from A1 down.\n"
                "Keep each ## heading in its own cell. Do not change any other sheet.\n" + RULES_LAB8,
            ),
            (
                "Open https://copilot.cloud.microsoft/ in your browser and sign in with the same work account used in Excel. "
                "Start a new chat in Microsoft 365 Copilot on the web and paste Prompt B below to draft the skill. "
                "The web chat does not automatically see your local workbook or Excel chat, so this prompt supplies the "
                "table schema and dashboard recipe. No workbook upload is needed. Read the returned text: it must start "
                "with --- and include name: hr-workforce-dashboard and a description, followed by the numbered steps. "
                "Ask for corrections in this web chat before saving.",
                "PROMPT (Microsoft 365 Copilot web):\n"
                "Write a complete SKILL.md for a Copilot in Excel skill named hr-workforce-dashboard.\n"
                "Return reusable skill instructions; do not build a dashboard or claim to inspect my local workbook in this chat.\n"
                "Start with YAML front matter containing name: hr-workforce-dashboard and a description.\n"
                "Description: Use when I ask for a workforce, headcount or attrition dashboard from an employee table.\n"
                "Workbook context for the skill when it runs in Excel: tblEmployees has Employee_ID, Department, Location,\n"
                "Job_Level, Employment_Type, Hire_Date, Exit_Date, Exit_Type, Status, Monthly_Salary, Engagement_Score,\n"
                "and Training_Hours_YTD. Status is Active or Exited; blank Exit_Date means no recorded exit.\n"
                "The .Rules worksheet holds the reporting period (2025-07-01 to 2026-06-30 for this lab), KPI definitions,\n"
                "privacy limits and formatting. Read it at run time; ask if it is missing or unclear.\n"
                "Attrition = exits in period / ((headcount at period start + headcount at period end) / 2).\n"
                "Voluntary attrition uses voluntary exits and the same denominator; handle a zero denominator explicitly.\n"
                "Never display Employee_ID, salary, individual records or groups smaller than 5 on the dashboard.\n"
                "Steps:\n"
                "1) Read the .Rules sheet first and follow it.\n"
                "2) Add helper columns Active_Start, Exit_In_Period and Tenure_Years using the period in the rules.\n"
                "3) Create a Checks sheet with independent COUNTIFS formulas for active headcount (Status Active),\n"
                "   headcount at period start, headcount at period end, exits, voluntary exits, attrition rate and hires.\n"
                "4) Put all PivotTables on Dash_Data.\n"
                "5) Build HR_Dashboard: six KPI cards (Active headcount, Exits, Attrition rate, Voluntary attrition rate,\n"
                "   Avg tenure of active staff, Hires), charts of headcount by Department, attrition rate by Department,\n"
                "   hires vs exits by quarter and headcount by Location, and slicers for Location and Job_Level.\n"
                "6) Compare every KPI card with Checks and report any difference.\n"
                "7) Check slicer combinations for groups smaller than 5; suppress their values and report the privacy check.\n"
                "8) Use tblEmployees as a dynamic source and refresh all PivotTables after new rows are appended.\n"
                "Return only the full SKILL.md text, starting with the --- front matter, without code fences or commentary.",
            ),
            (
                "Copy the skill text from the web chat into a plain-text file named SKILL.md (not SKILL.md.txt). "
                "Do not include Markdown code fences around the file. Return to Excel: Settings (...) > Manage plugins & "
                "skills > Custom skills > Open skills folder (select Create OneDrive folder first if needed). Create the folder "
                "hr-workforce-dashboard in your OneDrive skills folder and upload the file (or upload the ready-made one from "
                "this lab folder). In Excel select Settings (...) > Manage plugins & skills > Custom skills > Refresh and turn "
                "the skill on.",
                "OneDrive : .../skills/hr-workforce-dashboard/SKILL.md\n"
                "Check    : folder name = name: line = hr-workforce-dashboard",
            ),
            (
                "Run the skill in Plan mode: one line replaces the long brief, because the skill holds the steps and the rules "
                "hold the definitions. Review the plan, approve it, and select Done when Copilot finishes.",
                "PLAN MODE:\n"
                "@hr-workforce-dashboard Build the workforce dashboard for the 12 months ending 2026-06-30.",
            ),
            (
                "Verify. Ask Copilot to compare the KPI cards with the Checks sheet the skill built, and to show the attrition "
                "formula. Compare both with the Test It values - a skill can build a wrong check too.",
                "CHAT ONLY:\n"
                "Compare each KPI card on HR_Dashboard with the Checks sheet and tell me which, if any, do not match.\n"
                "Show the formula behind the Attrition rate card.\n\n"
                "ALLOW EDITING (if needed):\n"
                "The attrition rate must use average headcount = (active on 2025-07-01 + active on 2026-06-30) / 2, as the rules say.",
            ),
            (
                "Refresh test: ask Copilot to append the 8 rows from New_Joiners_Jul2026 to tblEmployees and refresh every "
                "PivotTable. Every KPI and chart that counts active staff must update.",
                "ALLOW EDITING:\n"
                "Copy the 8 data rows in New_Joiners_Jul2026!A2:L9 to the first empty rows directly below tblEmployees\n"
                "so the table expands. Then refresh all PivotTables in the workbook and tell me the new Active headcount\n"
                "and the number of rows in tblEmployees.\n\n"
                "Expected after refresh:\n"
                f"Active headcount : {E8['active']} -> {E8['active_after']}\n"
                f"tblEmployees rows: {E8['rows']} -> {E8['rows_after']}\n"
                "New joiners by department: "
                + ", ".join(f"{k} +{v}" for k, v in E8["nj_by_dept"].items()),
            ),
            (
                "Check it is safe to share, then ask for a leadership summary that uses only dashboard numbers. Copilot drafts; "
                "you check every number before it leaves HR. Manually fill in the Step 3 / Prompt B row in Prompt_Log: "
                "record that the web chat drafted SKILL.md and how you checked the front matter and steps. "
                "Excel Copilot cannot see that web conversation. Then log the Excel prompts with Prompt I.",
                "CHAT ONLY:\n"
                "Review HR_Dashboard before I share it with the leadership team. Does any element expose individual\n"
                "employee data or a group smaller than 5? Is each KPI labelled with its period and definition?\n\n"
                "CHAT ONLY:\n"
                "Write a 5-line summary of HR_Dashboard for BrightPath's leadership team. Use only numbers shown on the\n"
                "dashboard, and label any explanation as a hypothesis to test.\n\n"
                "LOG (Allow editing):\n"
                "In Prompt_Log, leave the Step 3 / Prompt B web-chat row unchanged. For each Excel prompt I ran, fill in\n"
                "What Copilot did and How I verified, and set Decision to Keep. Do not invent results for web prompts.\n"
                "I will tell you any row to change to Revise or Undo.",
            ),
        ],
        sample_prompts=[
            ("Write a skill · Microsoft 365 Copilot web", "In the web chat at https://copilot.cloud.microsoft/, use the complete Step 3 prompt below to draft hr-workforce-dashboard. It includes the workbook schema and rules that this chat cannot see."),
            ("Run a skill", "@hr-workforce-dashboard Build the workforce dashboard for the 12 months ending 2026-06-30."),
            ("Refresh", "I added rows to tblEmployees. Refresh all PivotTables and tell me which KPI values changed."),
            ("Privacy", "Which slicer combinations show a group of fewer than 5 employees? Suggest how to suppress them."),
            ("Explain", "Explain how the Attrition rate card is calculated, step by step."),
            ("Improve the skill · Microsoft 365 Copilot web", "I will paste my current hr-workforce-dashboard SKILL.md below. Update it so it also adds a timeline on Hire_Date. Preserve its front matter, KPI definitions and privacy rules. Return the full file without code fences. If I have not pasted the file, ask me for it first."),
            ("Summary", "Write a 5-line leadership summary using only the numbers on HR_Dashboard."),
        ],
        test=(
            f"Before the refresh: Active headcount {E8['active']}, headcount on 2025-07-01 {E8['start_hc']}, exits in period "
            f"{E8['exits_12m']} ({E8['vol_exits']} voluntary), attrition rate {E8['attrition']}% and voluntary attrition "
            f"{E8['vol_attrition']}%, hires in period {E8['hires_12m']}, average tenure of active staff about "
            f"{E8['avg_tenure']} years. {E8['top_attr_dept']} has the highest attrition rate ({_RD['rate']}%, {_RD['exits']} "
            f"exits) and the largest active headcount ({_RD['hc']}). After appending the July joiners and refreshing, Active "
            f"headcount shows {E8['active_after']} and tblEmployees has {E8['rows_after']} rows. The dashboard shows no "
            "Employee_ID, salary or individual record, and the skill appears when you type @ in Excel. The saved SKILL.md "
            "starts with valid front matter and was drafted in Microsoft 365 Copilot on the web."
        ),
        checkpoint=(
            "You now have two custom skills in OneDrive. Run hr-workforce-dashboard again next month on new data, and improve "
            "the skill whenever you correct Copilot twice."
        ),
        troubleshooting=[
            (
                "The web chat asks to see my workbook or outputs a dashboard instead of SKILL.md.",
                "Use the full Step 3 prompt at https://copilot.cloud.microsoft/. Ask for reusable skill instructions only; "
                "the local workbook is used later in Excel. Do not upload it just to draft the skill.",
            ),
            (
                "The skill does not appear in Excel after saving.",
                "Use the skills folder opened from Excel, check the file is SKILL.md rather than SKILL.md.txt, and ensure "
                "the folder name and front-matter name are both hr-workforce-dashboard. Select Refresh and enable it. "
                "If custom skills are unavailable for your account, use the supplied skill text as a normal Excel prompt "
                "and record that the installation could not be completed.",
            ),
            (
                "The new rows did not join the table and nothing changed on refresh.",
                "Ask Copilot to resize tblEmployees to include the 8 new rows, then refresh all PivotTables again.",
            ),
            (
                "Attrition shows 12.2% (29 / 237) instead of 13.0%.",
                "The card divides by closing headcount only. Ask Copilot to use the average of opening and closing headcount, "
                "then add that wording to the skill.",
            ),
            (
                "The skill ignores the .Rules sheet.",
                "Check the sheet is named .Rules and is visible, and that step 1 of the skill says to read it. Start a New chat.",
            ),
            (
                "Helper columns show #VALUE! for blank Exit_Date.",
                "Ask Copilot to treat blank Exit_Date explicitly, e.g. OR([@Exit_Date]=\"\",[@Exit_Date]>DATE(2025,7,1)).",
            ),
        ],
        challenge=(
            "Improve the skill so it also adds a Timeline on Hire_Date and a chart of average Engagement_Score by Department "
            "for active staff. Save, refresh and rerun it, then check one department's average with AVERAGEIFS."
        ),
        reflection="What would happen to trust in this dashboard if one leader could filter it down to a single named team member?",
    ),
]

# Test-it checklist: (what to check, expected result).
_CHECKS = {
    7: [
        ("Applications and hires", f"{E7['apps']} applications, {E7['hires']} hires (no slicer selected)"),
        ("Offer acceptance rate", f"{E7['oar']}% = {E7['accepted']} of {E7['decided']}; {E7['pending']} pending excluded"),
        ("Time to hire, cost per hire", f"{E7['avg_tth']} days; S${E7['cph']:.2f}"),
        ("Hires vs target (amber)", f"{_HVT}% = {E7['hires']} of {_TARGET}"),
        ("Slicer: Sector = Technology", f"{E7['tech_apps']} applications, {E7['tech_hires']} hires, {E7['tech_avg_tth']:.1f} days"),
        ("Timeline: Apr-Jun 2026", f"{_Q2} hires; no KPI card holds a typed number"),
    ],
    8: [
        ("Active headcount", f"{E8['active']} before the refresh"),
        ("Exits and attrition", f"{E8['exits_12m']} exits ({E8['vol_exits']} voluntary); {E8['attrition']}% attrition"),
        ("Hires and tenure", f"{E8['hires_12m']} hires; average tenure about {E8['avg_tenure']} years"),
        ("Highest-attrition department", f"{E8['top_attr_dept']}: {_RD['rate']}% ({_RD['exits']} exits)"),
        ("Refresh test", f"After adding the July joiners: headcount {E8['active_after']}, {E8['rows_after']} rows"),
        ("Privacy", "No Employee_ID, salary, individual record or group under 5 on the dashboard"),
    ],
}
for _a in DOMAIN3:
    _a["checks"] = _CHECKS[_a["num"]]
