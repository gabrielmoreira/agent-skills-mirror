"""Topic 2 labs for C34: Skills and Rules (BrightPath client orders, HR-outsourcing growth and job-posting data)."""

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

SKILL_PARETO = """---
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
        title="Plot and Style Client Growth Charts with Built-in Visual Skills",
        theme="Built-in Skills: Visual Design",
        duration=40,
        objective=(
            "LO2: find, enable and call Copilot's built-in visual skills - chart-design and theme-design - to plot charts "
            "from a prompt and style them as one set, and verify what each skill produces"
        ),
        goal=(
            "Use @chart-design to plot four charts of BrightPath's HR-outsourcing growth, polish them as a set, then use "
            "@theme-design to give the whole sheet one professional look - and prove the numbers behind every chart."
        ),
        workflow=["Manage skills", "@chart-design: plot", "@chart-design: polish", "Check the numbers", "@theme-design"],
        desc=(
            "BrightPath's HR-outsourcing business sells monthly payroll and HR services to client companies, and "
            "leadership wants four clear charts of how it is growing. You will switch on the built-in visual skills in "
            "Manage plugins & skills, then call @chart-design to plot each chart - it picks the chart type and formats it "
            "using the Excel design team's guidance - and place all four in a 2 x 2 grid on a new Charts sheet. You will "
            "polish the set, ask Copilot for a Checks sheet that proves the numbers behind the charts, and finish with "
            "@theme-design to give the sheet one coordinated theme."
        ),
        build=(
            "BrightPath_HR_Outsourcing_Finance.xlsx with a Charts sheet of four skill-designed charts in a 2 x 2 grid (MRR "
            "and clients, new vs churned clients, H1 2026 spend by channel, active clients by plan), a Checks sheet that "
            "agrees with the charts, and one consistent theme"
        ),
        services="Excel · Copilot (Allow editing, Chat only) · Manage plugins & skills · @chart-design · @theme-design",
        data_files=["data/BrightPath_HR_Outsourcing_Finance.xlsx"],
        prerequisites=[
            "Lab 4 completed: you know how rules guide Copilot inside one workbook.",
            "This lab folder's data/BrightPath_HR_Outsourcing_Finance.xlsx. Skills need Excel's display language set to English.",
        ],
        steps=[
            (
                _SETUP_STEP.format(file="BrightPath_HR_Outsourcing_Finance.xlsx")
                + " The workbook holds data only: you will create every chart with a prompt, in a 2 x 2 grid on a new "
                "Charts sheet. Read the Definitions row on About_This_Data first.",
                f"Tables : tblClientMonths (18 months) | tblClients ({E5['clients']} clients) | tblSpend (spend by month and channel)\n"
                "H1 2026 : Jan-Jun 2026\n"
                "Chart 1 : MRR and active clients by month   -> Charts!A1:H18\n"
                "Chart 2 : new vs churned clients by month   -> Charts!J1:Q18\n"
                "Chart 3 : H1 2026 spend by Channel          -> Charts!A20:H37\n"
                "Chart 4 : active clients by Plan, Jun 2026  -> Charts!J20:Q37",
            ),
            (
                "Turn on the skills. In the Copilot pane select Settings (...) > Manage plugins & skills. Open the "
                "Visualisation folder and turn on chart-design (it is off by default). Open the Formatting folder and turn "
                "on theme-design - if you have no Formatting folder yet, skip it; Step 7 shows what to do. Leave every other "
                "skill as it is. Close the dialog, type @ in the prompt box and confirm chart-design is listed. Then ask "
                "Copilot which skills fit this job.",
                "Where         : Settings (...) > Manage plugins & skills - turn on only these\n"
                "Visualisation : chart-design (off by default)\n"
                "Formatting    : theme-design - only if this folder is shown\n"
                "Call a skill  : type @ and its name, e.g. @chart-design\n\n"
                "CHAT ONLY:\n"
                "Which of your skills would help me choose the right chart for this data and style the finished\n"
                "sheet? Do not change anything.",
            ),
            (
                "Call @chart-design in Allow editing. It chooses and formats the chart using the Excel design team's "
                "guidance. Your prompt says where the chart goes and how it should look, because the default placement and "
                f"style are rarely what you want. Check the values: MRR grows from {_money(E5['mrr_jan25'])} in Jan 2025 to "
                f"{_money(E5['mrr_end'])} in Jun 2026, with {E5['active_end']} active clients at the end.",
                "ALLOW EDITING:\n"
                "@chart-design On a new sheet named Charts, create a combo chart from tblClientMonths, placed over A1:H18,\n"
                "with MRR as columns and Clients_End as a line on a secondary axis, Jan 2025 to Jun 2026.\n"
                "Format it cleanly: white background, no border or effects, axis titles with units, and a title that\n"
                "states the finding.",
            ),
            (
                "Add the other three charts, one prompt each, in the same clean style. For chart 2 let the skill recommend "
                f"the chart type. Check: {E5['new_all']} clients were won and {E5['churned_all']} churned over the 18 months; "
                f"{E5['top_channel']} took the most H1 2026 spend ({_money(E5['by_channel'][E5['top_channel']]['spend'])}) and "
                f"{E5['low_channel']} the least ({_money(E5['by_channel'][E5['low_channel']]['spend'])}); in Jun 2026 "
                + ", ".join(f"{p} has {n}" for p, n in sorted(E5["active_by_plan"].items(), key=lambda kv: -kv[1]))
                + " active clients.",
                "ALLOW EDITING:\n"
                "@chart-design Recommend the best chart for new vs churned clients by month, then create it on the\n"
                "Charts sheet over J1:Q18 in the same clean style as the first chart.\n\n"
                "ALLOW EDITING:\n"
                "@chart-design Chart the sales and marketing spend for each Channel in H1 2026 (Jan-Jun) from tblSpend\n"
                "as bars, longest first, on the Charts sheet over A20:H37 in the same clean style.\n\n"
                "ALLOW EDITING:\n"
                "@chart-design Show how many active clients each Plan has in Jun 2026 from tblClients, as the chart\n"
                "type you think suits it best, on the Charts sheet over J20:Q37 in the same clean style.",
            ),
            (
                "Polish the four charts as one set with a single call. If one chart is not what you wanted, select Undo and "
                "ask again for that chart only.",
                "ALLOW EDITING:\n"
                "@chart-design Review the four charts on the Charts sheet so they read as one set: a title that states\n"
                "the finding on each, the same fonts and axis style, data labels only where they help, and all four the\n"
                "same size.",
            ),
            (
                "Never trust a chart without a check. Ask Copilot to add a Checks sheet with formulas, then compare each "
                "value with its chart. If a chart differs, ask the skill which table and filter it used, and fix the chart: "
                "the Checks sheet is the reference.",
                "CHECK (Allow editing):\n"
                "Add a Checks sheet with formulas that give the MRR and active clients in Jun 2026, the total new and\n"
                "churned clients over the 18 months, the H1 2026 spend for each Channel, and the active clients for each\n"
                "Plan, so I can check the four charts.",
            ),
            (
                "Style the workbook with @theme-design (Formatting). It applies one coordinated theme - colours, fonts and "
                "formats - to cells, tables and charts. Then steer it with a follow-up prompt. If theme-design is not in your "
                "@ list, your account does not have it yet: delete @theme-design and run the prompt as it is. If your "
                "organisation has set up a brand kit, try @brandkit instead. Then log your prompts.",
                "ALLOW EDITING:\n"
                "@theme-design Apply one clean, professional theme to the Charts and Checks sheets and all four charts.\n\n"
                "FOLLOW-UP:\n"
                "@theme-design Use navy #1F4E79 and teal #2A9D8F as the main colours, and keep every chart readable.\n\n"
                + _LOG,
            ),
        ],
        sample_prompts=[
            ("Find skills", "Which skills do you have for charts and formatting? When would I use each one?"),
            ("Chart skill", "@chart-design Recommend the best chart for new vs churned clients by month, then create it."),
            ("Chart skill", "@chart-design Chart the sales and marketing spend for each Channel in H1 2026 as bars, longest first."),
            ("Style skill", "@theme-design Apply a coordinated theme to this workbook."),
            ("Colours", "@theme-design Use navy #1F4E79 and teal #2A9D8F as the main colours on every chart."),
            ("Brand skill", "@brandkit Apply our organisation's brand colours and fonts to the charts."),
            ("Explain", "Explain why you chose this chart type for this data, and which other chart types would also work."),
            ("Question", "Which acquisition channel took the most sales and marketing spend in H1 2026, and how much was it?"),
        ],
        test=(
            f"The Charts sheet holds four charts in a 2 x 2 grid in one clean style. MRR grows from {_money(E5['mrr_jan25'])} "
            f"(Jan 2025) to {_money(E5['mrr_end'])} (Jun 2026) while active clients end at {E5['active_end']}. Over the 18 months "
            f"{E5['new_all']} clients were won and {E5['churned_all']} churned. H1 2026 spend by channel runs from "
            f"{E5['top_channel']} ({_money(E5['by_channel'][E5['top_channel']]['spend'])}) down to {E5['low_channel']} "
            f"({_money(E5['by_channel'][E5['low_channel']]['spend'])}), {_money(E5['spend_h1'])} in all. Active clients by plan: "
            + ", ".join(f"{p} {n}" for p, n in sorted(E5["active_by_plan"].items(), key=lambda kv: -kv[1]))
            + f" ({E5['active_end']} in total). The Checks sheet agrees with every chart, and @theme-design gave the sheets one "
            "consistent theme."
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
                "The chart is in the wrong place or has a border or glow.",
                "Ask: 'Move this chart to the Charts sheet over A1:H18 (use that chart's range), use a white background and "
                "remove the border and effects.'",
            ),
            (
                "@chart-design builds a different chart type from the one I wanted.",
                "The skill recommends, your words decide. Name the type in the prompt, e.g. 'as bars, longest first'.",
            ),
            (
                "@theme-design is not in my list.",
                "Your account may not have the Formatting folder yet. Ask without the skill: 'Apply one consistent colour "
                "theme and font to the Charts and Checks sheets and all four charts.'",
            ),
            (
                "A chart value differs from the Checks sheet.",
                "Ask: 'Which table, columns and filter did this chart use?' Then fix the chart's data; the Checks sheet is the reference.",
            ),
        ],
        challenge=(
            "Ask @chart-design for a fifth chart: monthly gross margin % as a line with the axis starting at 40%. Then use "
            "@theme-design so it matches the other four, and check one month's value on Client_Months."
        ),
        reflection="Which chart did the skill choose differently from the one you would have drawn, and was it better? What did the theme change that a prompt alone did not?",
    ),
    # ------------------------------------------------------------------ LAB 6
    dict(
        num=6,
        topic=2,
        title="Use Copilot to Build a Custom Pareto-Chart Skill",
        theme="Custom Skills: Pareto Chart",
        duration=45,
        objective=(
            "LO2: use Copilot on the web to write a custom SKILL.md, upload it to the OneDrive skills folder, install it in "
            "Excel and call it with @ to plot a Pareto chart from a one-line prompt"
        ),
        goal=(
            "Create a pareto-chart skill that turns any category column into a Pareto chart - a different colour for each "
            "bar and a cumulative % line - and use it to plot BrightPath's 500 job postings by job category."
        ),
        workflow=["Draft on the web", "Save SKILL.md", "Upload to OneDrive", "Install in Excel", "@pareto-chart"],
        desc=(
            "BrightPath received 500 job postings from clients in H1 2026, spread over 16 job categories. Which few "
            "categories make up most of the work? A Pareto chart answers that: bars sorted from highest to lowest and a "
            "cumulative % line that shows where the 'vital few' end. Excel's built-in Pareto chart paints every bar the same "
            "colour, so you will write a custom skill instead. You will ask Copilot on the web to write the pareto-chart "
            "SKILL.md, save it, upload it to your OneDrive skills folder, install it in Excel and call it with @ to plot the "
            "job categories - then reuse it on another column and improve it."
        ),
        build=(
            "A pareto-chart skill in your OneDrive skills folder, and BrightPath_Job_Postings.xlsx with a Pareto_Job_Category "
            "sheet and a Pareto_Client_Sector sheet - each a summary table and a Pareto chart with a different colour for every "
            "bar - plus a Checks sheet"
        ),
        services="Microsoft 365 Copilot web (https://copilot.cloud.microsoft/) to draft the skill · OneDrive skills folder · Excel Copilot (Chat only, Allow editing) · SKILL.md",
        data_files=["data/BrightPath_Job_Postings.xlsx"],
        extra_files=[("skills/pareto-chart/SKILL.md", SKILL_PARETO,
                      "ready-made skill to upload if you run short of time")],
        prerequisites=[
            "Lab 5 completed: you can find, enable and @mention skills.",
            "Access to https://copilot.cloud.microsoft/ with the same work account used in Excel and OneDrive, and to your OneDrive in a browser (custom skills are stored there).",
            "This lab folder's data workbook and skills/pareto-chart/SKILL.md (fallback).",
        ],
        steps=[
            (
                _SETUP_STEP.format(file="BrightPath_Job_Postings.xlsx")
                + " The workbook stays local; only the skill file goes in OneDrive (Steps 4-5).",
                f"Table   : tblJobs ({E6['rows']} job postings, Jan-Jun 2026)\n"
                "Columns : Job_ID, Posted_Date, Job_Category (16 values), Client_Sector (6 values), Employment_Type, "
                "Status, Openings\n"
                "Pareto  : columns = jobs per category, highest to lowest, a different colour for each column;\n"
                "          line = cumulative % of all jobs, 0% to 100% on a secondary axis",
            ),
            (
                "Draft the skill in Microsoft 365 Copilot on the web. Open https://copilot.cloud.microsoft/ in your browser and sign "
                "in with the same work account used in Excel and OneDrive. Start a new chat and paste the prompt below. The "
                "web chat cannot see your workbook, "
                "so the prompt describes the table, the chart and the colours. Read the reply: it must start with --- and "
                "include name: pareto-chart, a description that says when to use the skill, and numbered steps that give "
                "every column a different colour. Ask for corrections in this chat until you are happy.",
                "PROMPT (Microsoft 365 Copilot web):\n"
                "Write a complete SKILL.md for a Copilot in Excel skill named pareto-chart.\n"
                "Return reusable skill instructions only; do not draw a chart or claim to see my workbook in this chat.\n"
                "Start with YAML front matter containing name: pareto-chart and a description.\n"
                "Description: Use when I ask for a Pareto chart, an 80/20 analysis or the vital few categories in a table column.\n"
                "When the skill runs in Excel I will name a table and a category column, for example tblJobs and\n"
                "Job_Category. If I do not, it must ask me.\n"
                "Steps:\n"
                "1) Never change the source table or unrelated sheets. You may replace only the matching Pareto_<column name> output sheet when rerunning this skill.\n"
                "2) Create a sheet named Pareto_<column name>; if it already exists, replace only its contents.\n"
                "Build a summary table: Category, Count, Share %,\n"
                "Cumulative %, sorted by Count from highest to lowest. Use formulas that read the source table so it\n"
                "updates when rows are added, and add a Total row.\n"
                "3) Create one combo chart from the summary: Count as columns and Cumulative % as a line with markers on\n"
                "a secondary axis from 0% to 100%.\n"
                "4) Give every column a different colour. Never use one colour for all the columns. Make the line dark grey.\n"
                "5) Format the chart cleanly: white background, no border or effects, data labels on the columns, axis\n"
                "titles, no legend, and a title that states the finding, for example \"6 of 16 categories make up 83%\n"
                "of the total\".\n"
                "6) Place the chart to the right of the summary table, starting at column G.\n"
                "7) Under the table, list the vital few: the categories needed to reach 80% and their combined share.\n"
                "8) Check that the Count total equals the number of rows in the source table, and report the row count,\n"
                "the number of categories, the top category and how many categories reach 80%.\n"
                "Return only the full SKILL.md text, starting with the --- front matter, without code fences or commentary.",
            ),
            (
                "Save the reply as a plain-text file named SKILL.md. Select the whole reply and copy it - if it sits in a code "
                "block, copy only the text inside, with no ``` lines. Windows: open Notepad, paste, choose File > Save as, set "
                "Save as type to All files, type SKILL.md as the file name, set Encoding to UTF-8 and save it in work-c34. "
                "Mac: open TextEdit, choose Format > Make Plain Text, paste, choose File > Save, type SKILL.md as the name, "
                "untick 'If no extension is provided, use .txt' and save it in work-c34. Check the file is called SKILL.md, "
                "not SKILL.md.txt, and that its first line is ---.",
                "File   : work-c34/SKILL.md (plain text)\n"
                "Line 1 : ---\n"
                "Line 2 : name: pareto-chart\n"
                "Check  : no ``` lines and no text before the first ---\n"
                "Short of time? Use skills/pareto-chart/SKILL.md from this lab folder instead.",
            ),
            (
                "Open your OneDrive skills folder from Excel. In Excel open the Copilot pane and select Settings (...) > "
                "Manage plugins & skills > Custom skills. Turn the Custom skills switch on, then select Add in OneDrive (in "
                "some versions: Create OneDrive folder, then Open skills folder). Your browser opens OneDrive at the skills "
                "folder, usually Documents > Copilot > Microsoft Excel > skills. A sample folder such as make-calendar.example "
                "shows the layout: one folder per skill.",
                "Excel    : Copilot pane > Settings (...) > Manage plugins & skills > Custom skills\n"
                "Switch   : Custom skills = On\n"
                "Then     : Add in OneDrive (or Create OneDrive folder, then Open skills folder)\n"
                "OneDrive : Documents > Copilot > Microsoft Excel > skills",
            ),
            (
                "Create the skill's folder and upload SKILL.md. In the OneDrive skills folder select Create or upload > Folder, "
                "name it pareto-chart (lower case, with a hyphen) and select Create. Open the new folder, select Create or "
                "upload > Files upload, choose SKILL.md from work-c34 and select Open. When the upload finishes, SKILL.md is "
                "listed inside the pareto-chart folder.",
                "OneDrive : Documents > Copilot > Microsoft Excel > skills > pareto-chart > SKILL.md\n"
                "Check    : folder name = the name: line = pareto-chart (lower case, hyphen, no spaces)\n"
                "Check    : the file is called SKILL.md and sits directly inside the pareto-chart folder",
            ),
            (
                "Install the skill in Excel. Go back to Excel: Copilot pane > Settings (...) > Manage plugins & skills > Custom "
                "skills. Check the Custom skills switch is on and select Refresh (the round arrow). Wait until the list loads, "
                "then turn pareto-chart on. Close the dialog, click the Copilot prompt box and type @pare - pareto-chart should "
                "appear in the list. If it does not, wait a minute and select Refresh again.",
                "Excel : Copilot pane > Settings (...) > Manage plugins & skills > Custom skills > Refresh\n"
                "Then  : turn pareto-chart on, close the dialog and type @pare in the prompt box\n"
                "Check : pareto-chart appears in the list",
            ),
            (
                "Use the skill. First check that the title bar shows BrightPath_Job_Postings: a skill is available in every "
                "workbook, but it only works where its table exists. Choose Allow editing and send the one-line prompt. Copilot "
                "should create a sheet Pareto_Job_Category with a summary table and a combo chart beside it: columns from "
                f"{E6['top_cat']} ({E6['top_n']}) down to {E6['by_cat'][-1][0]} ({E6['by_cat'][-1][1]}), a different colour for "
                f"each column, and a cumulative % line that passes 80% at category {E6['n80']}. Inspect it and select Done. Then "
                "ask Copilot to add a Checks sheet so you can compare the numbers.",
                "ALLOW EDITING:\n"
                "@pareto-chart Plot a Pareto chart of Job_Category in tblJobs.\n\n"
                "CHECK (Allow editing):\n"
                "Add a Checks sheet with formulas that count all the jobs, the Customer Service jobs and the number of\n"
                "job categories, so I can check the Pareto chart.",
            ),
            (
                "Reuse it. This is the point of a skill: a different column needs only its name. Run it on Client_Sector, then "
                "ask Copilot which job categories make up the vital few.",
                "ALLOW EDITING:\n"
                "@pareto-chart Plot a Pareto chart of Client_Sector in tblJobs.\n\n"
                "CHAT ONLY:\n"
                "Which job categories together make up 80% of the postings? Give their combined share.",
            ),
            (
                "Improve the skill. A skill is a living recipe: improve it whenever you correct Copilot twice. Go back to the "
                "web chat, send the prompt below, then paste your current SKILL.md under it. Save the reply as SKILL.md as in "
                "Step 3. In OneDrive open the pareto-chart folder, select Create or upload > Files upload, choose the new "
                "SKILL.md and select Replace when OneDrive asks. In Excel select Custom skills > Refresh and rerun the skill "
                f"on Job_Category: the chart now shows a dashed 80% line and one Other column that groups the {E6['small_n']} "
                f"categories under 2% ({E6['small_total']} postings, {E6['small_share']}%). Finally log your prompts - fill in "
                "the two web-chat rows yourself, because Excel Copilot cannot see the web chat.",
                "PROMPT (Microsoft 365 Copilot web):\n"
                "I will paste my current pareto-chart SKILL.md below. Update it so the chart also shows a dashed 80%\n"
                "reference line and groups any category with less than 2% share into one Other column at the end.\n"
                "Preserve its front matter and numbered steps. Return the full file without code fences. If I have not\n"
                "pasted the file, ask me for it first.\n\n"
                "ALLOW EDITING:\n"
                "@pareto-chart Plot a Pareto chart of Job_Category in tblJobs.\n\n"
                "LOG (Allow editing):\n"
                "In Prompt_Log, leave the web-chat rows (Step 2 / Prompt A and Step 9 / Prompt F) unchanged. For each Excel\n"
                "prompt I ran, fill in What Copilot did and How I verified, and set Decision to Keep. Do not invent\n"
                "results for web prompts. I will tell you any row to change to Revise or Undo.",
            ),
        ],
        sample_prompts=[
            ("Write a skill · Microsoft 365 Copilot web", "In the web chat at https://copilot.cloud.microsoft/, use the complete Step 2 prompt below to draft pareto-chart. It describes the table, columns and chart because the web chat cannot see your workbook."),
            ("Call the skill", "@pareto-chart Plot a Pareto chart of Job_Category in tblJobs."),
            ("Reuse", "@pareto-chart Plot a Pareto chart of Client_Sector in tblJobs."),
            ("Check", "Add a Checks sheet with formulas that count all the jobs and the Customer Service jobs, so I can check the Pareto chart."),
            ("Vital few", "Which job categories together make up 80% of the postings? Show their combined share."),
            ("Explain", "Explain in plain English how to read this Pareto chart: what the columns, the line and the 80% point tell me."),
            ("Improve the skill · Microsoft 365 Copilot web", "I will paste my current pareto-chart SKILL.md below. Update it so the chart also shows a dashed 80% reference line and groups any category with less than 2% share into one Other column. Preserve its front matter and numbered steps. Return the full file without code fences. If I have not pasted the file, ask me for it first."),
        ],
        test=(
            f"tblJobs has {E6['rows']} rows and {E6['categories']} job categories, and the skill appears when you type @ in Excel. "
            f"Pareto_Job_Category lists {E6['top_cat']} first ({E6['top_n']} jobs, {E6['top_share']}%) down to "
            f"{E6['by_cat'][-1][0]} ({E6['by_cat'][-1][1]}); the cumulative % first passes 80% at category {E6['n80']} "
            f"({E6['last80']}, {E6['cum80']}%), so {E6['n80']} of {E6['categories']} categories make up {E6['cum80']}% of the "
            f"postings, and the top 3 make up {E6['top3_share']}%. Every column is a different colour and the line runs from "
            f"0% to 100% on a secondary axis. The Checks sheet shows {E6['rows']} jobs, {E6['top_n']} {E6['top_cat']} jobs and "
            f"{E6['categories']} categories. Pareto_Client_Sector starts with {E6['top_sector']} ({E6['top_sector_n']} jobs, "
            f"{E6['top_sector_share']}%) and reaches 80% at sector {E6['sector_n80']} ({E6['sector_cum80']}%). After the improved "
            f"skill, the {E6['small_n']} categories under 2% are grouped into Other ({E6['small_total']} jobs, "
            f"{E6['small_share']}%) and tblJobs is unchanged."
        ),
        checkpoint=(
            "Keep the skill: it stays in your OneDrive and works in any workbook with a table and a category column. Topic 3 "
            "uses rules and skills to build dashboards."
        ),
        troubleshooting=[
            (
                "The skill does not appear after Refresh.",
                "The folder name must match the name: line exactly (lower case, hyphens) and the file must be SKILL.md "
                "directly inside that folder. Select Refresh again and turn pareto-chart on.",
            ),
            (
                "There is no Add in OneDrive or Create OneDrive folder button.",
                "Custom skills are rolling out and depend on your licence and update channel. Use the ready-made SKILL.md to "
                "read the format, and run the same steps as a normal prompt instead.",
            ),
            (
                "Copilot says tblJobs is not present in this workbook.",
                "The skill ran in another lab's workbook. Open BrightPath_Job_Postings.xlsx and send the prompt again from "
                "its Copilot pane.",
            ),
            (
                "The web chat draws a chart or asks me to upload my workbook instead of writing SKILL.md.",
                "Paste the full Step 2 prompt again. It asks for reusable skill instructions only; the workbook is used later "
                "in Excel, so nothing needs uploading.",
            ),
            (
                "The file saved as SKILL.md.txt, or it contains ``` lines.",
                "Save as plain text with the exact name SKILL.md (Windows: Save as type All files; Mac: Format > Make Plain "
                "Text) and delete any ``` lines before the first ---.",
            ),
            (
                "All the columns are the same colour.",
                "Ask: 'Give every column a different colour and keep the cumulative line dark grey.' Then add that sentence "
                "to the skill's steps, save, refresh and rerun.",
            ),
            (
                "The cumulative % line looks flat.",
                "It is on the same axis as the columns. Ask: 'Move Cumulative % to a secondary axis from 0% to 100%.' Then "
                "add that to the skill's steps.",
            ),
        ],
        challenge=(
            "Ask Copilot in Excel to create mock data of 500 rows for another question - for example helpdesk tickets with "
            "12 issue categories, as a table named tblTickets. Run @pareto-chart on the Issue_Category column and name the "
            "vital few."
        ),
        reflection="Which report in your own job is really a Pareto question - a long list where a few causes matter most - and what would the skill's description say?",
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
        ("MRR and active clients, Jun 2026", f"{_money(E5['mrr_end'])}; {E5['active_end']} clients (Jan 2025 MRR {_money(E5['mrr_jan25'])})"),
        ("New and churned clients, 18 months", f"{E5['new_all']} new; {E5['churned_all']} churned"),
        ("H1 2026 spend, longest and shortest bar", f"{E5['top_channel']} {_money(E5['by_channel'][E5['top_channel']]['spend'])}; {E5['low_channel']} {_money(E5['by_channel'][E5['low_channel']]['spend'])}"),
        ("H1 2026 spend, all channels", _money(E5["spend_h1"])),
        ("Active clients by plan", " + ".join(str(n) for _p, n in sorted(E5["active_by_plan"].items(), key=lambda kv: -kv[1])) + f" = {E5['active_end']}"),
        ("Charts sheet", "Four charts in a 2 x 2 grid, one clean style, one theme"),
    ],
    6: [
        ("Top category", f"{E6['top_cat']}: {E6['top_n']} of {E6['rows']} jobs ({E6['top_share']}%); {E6['categories']} categories in all"),
        ("Vital few", f"{E6['n80']} of {E6['categories']} categories reach {E6['cum80']}% (80% is passed at {E6['last80']})"),
        ("Pareto chart", "Columns high to low, a different colour for each, cumulative % line 0-100% on a secondary axis"),
        ("Client_Sector Pareto", f"{E6['top_sector']} first ({E6['top_sector_n']} jobs, {E6['top_sector_share']}%); {E6['sector_n80']} sectors reach {E6['sector_cum80']}%"),
        ("Improved skill", f"{E6['small_n']} categories under 2% grouped into Other ({E6['small_total']} jobs, {E6['small_share']}%)"),
        ("Skill", "pareto-chart appears when you type @ and runs from a one-line prompt"),
    ],
}
for _a in DOMAIN2:
    _a["checks"] = _CHECKS[_a["num"]]
