"""Simple, self-contained lab steps (IES v2.4).

Principles, applied to every lab:
- Each lab stands alone: open the files straight from THIS lab's data folder and save new files in the same
  folder. No copying between folders and no dependence on finishing an earlier lab.
- Short steps: one app per step, 1-3 short sentences, one prompt per step, never "see Step N".
- Short prompts in plain words that work in ONE paste (no blank lines).
- Every check states the exact numbers the learner should see.
"""
from collections import Counter
from mock_data import EXPECTED as E, ROWS, REPORT


def _pareto():
    """Failure-mode Pareto text, highest first (ties alphabetical), for all work orders and for the overdue jobs."""
    def text(rows):
        c = Counter(r[13] for r in rows)
        return ', '.join(f'{k} {v}' for k, v in sorted(c.items(), key=lambda x: (-x[1], x[0])))
    overdue = [r for r in ROWS if r[4] not in ('Closed', 'Cancelled') and r[7] < REPORT]
    return text(ROWS), text(overdue)

UPLOAD = 'select + > Upload images and files and choose'
NUMS = (f'{E["total"]} total, {E["closed"]} closed, {E["cancelled"]} cancelled, {E["backlog"]} backlog, {E["overdue"]} overdue, '
        f'{E["unassigned_backlog"]} unassigned, cost S${E["cost"]:,.2f}')
KEY = f'{E["total"]} total, {E["backlog"]} backlog, {E["overdue"]} overdue and {E["unassigned_backlog"]} unassigned'
PARETO_ALL, PARETO_OVERDUE = _pareto()
ONTIME = f'{E["on_time_closed"]}/{E["closed"]} = {E["on_time_rate"]:.1%}'
FILES = ('Desktop Excel on Windows or Mac. Download this lab folder and open the files straight from its data folder; save any new '
         'file in the same folder. All data is fictional.')
TROUBLE = [
    ('Copilot cannot see my file', 'In Excel, save the file and open Copilot again. In Word, PowerPoint or Outlook, upload the file '
     'with + > Upload images and files, and upload it again after you change it.'),
    ('A number is different from the lab', 'Clear any slicers or filters, check the table has no extra rows, then ask again in a new chat.'),
    ('A button or feature is missing', 'Check you are signed in with your course account and Microsoft 365 is up to date, then tell your trainer.')]
DONE = 'Select Done to keep the change, or Undo to reverse it.'
KEY_BOX = (f'Total : {E["total"]}\nBacklog : {E["backlog"]}\nOverdue : {E["overdue"]}\nUnassigned : {E["unassigned_backlog"]}\n'
           f'Cost : S${E["cost"]:,.2f}')


def skill_steps(folders, at):
    """Install supplied Excel skills (C34 route): upload the folders to the OneDrive skills folder, then Refresh and turn them on."""
    folders = [folders] if isinstance(folders, str) else folders
    names = ' and '.join(folders)
    return [
        ('Upload the skill to OneDrive. In Excel open Copilot and select Settings (...) > Manage plugins & skills > Custom skills. '
         'Turn Custom skills on and select Add in OneDrive (or Create OneDrive folder, then Open skills folder). OneDrive opens at '
         f'your skills folder. Select Create or upload > Folder upload and choose the {names} folder'
         f'{"s" if len(folders) > 1 else ""} in this lab’s data/templates folder.',
         '\n'.join(f'OneDrive : Documents > Copilot > Microsoft Excel > skills > {f} > SKILL.md' for f in folders)),
        (f'Turn the skill{"s" if len(folders) > 1 else ""} on. Back in Excel select Settings (...) > Manage plugins & skills > '
         f'Custom skills > Refresh, then turn {names} on. Close the dialog and type {at} in the Copilot prompt box: '
         f'{names} should appear. If not, wait a minute and select Refresh again.',
         '\n'.join(f'Check : {f} appears when you type @' for f in folders))]


def lab(desc, build, steps, checks, extra_pre=(), challenge=None, title=None):
    return dict(desc=desc, build=build, steps=steps, checks=checks, extra_pre=list(extra_pre), challenge=challenge, title=title)


def _labs(thread):
    return {
    1: lab('You are the maintenance coordinator at Northstar Water Services, a fictional water-pipe maintenance company. Clean a '
           'messy work-order export with Copilot in Excel, add check formulas, then turn the clean data into a one-page Word brief.',
           'A clean Northstar_Work_Orders.xlsx (120 rows and a Checks sheet) and Northstar_Operations_Brief.docx.',
           [('Look at the data. Open data/Northstar_Work_Orders.xlsx in Excel and open Copilot from the Copilot button on the Home '
             'tab. Choose Chat only (answers, no changes) and send the prompt. Copilot should find 122 rows, 2 repeated IDs '
             '(WO-2026-0005 and WO-2026-0020) and 2 job categories spelt differently.',
             'EXCEL - CHAT ONLY:\nDescribe this work-order table for me. How many rows are there? Are there any repeated '
             'Work_Order_IDs, or Job_Category names spelt in different ways? Don’t change anything.'),
            (f'Clean the table. Switch to Allow editing and send the prompt. {DONE} The table should now have 120 rows and 5 job categories.',
             'EXCEL - ALLOW EDITING:\nCopy the table to a new sheet named Raw_Export. Then remove the repeated rows, keeping one row '
             'for each Work_Order_ID, and fix the Job_Category spelling. Leave empty Assigned_To cells empty.'),
            (f'Add check formulas. Send the prompt and select Done. You should see {NUMS}. Save the workbook (Ctrl+S / Cmd+S).',
             'EXCEL - ALLOW EDITING:\nIn the Checks sheet, add formulas that count the total work orders, closed, cancelled, backlog '
             '(not Closed or Cancelled), overdue backlog (due before the date in Control!B2) and unassigned backlog, and add up Cost_SGD.'),
            ('Write the brief in Word. Open data/templates/Northstar_Operations_Brief_Template.docx in Word and save it as '
             f'Northstar_Operations_Brief.docx. In Copilot {UPLOAD} Northstar_Work_Orders.xlsx from this lab’s data folder, then send the prompt.',
             'WORD COPILOT:\nWrite a one-page operations brief in this document from the uploaded Northstar_Work_Orders.xlsx. Include '
             'the reporting date, the key numbers from the Checks sheet, the backlog and overdue findings, the unassigned jobs, '
             'proposed next actions and open questions. Use only numbers from the workbook, and write UNKNOWN for anything it does not show.'),
            ('Check the brief. Send the prompt in the same chat and fix any number it lists. Save the brief.',
             'WORD COPILOT:\nCheck every number in this brief against the uploaded workbook. List any number that is different, with '
             'the correct value.')],
           [('Clean table', '120 rows, one per Work_Order_ID; 5 job categories.'), ('Checks', NUMS + '.'),
            ('Word brief', 'Same numbers as the Checks sheet; empty owners left empty.')]),
    2: lab('Turn the Northstar operations brief into a 4-slide PowerPoint update and an Outlook email draft, then check that all three '
           'show the same numbers.',
           'Northstar_Initial_Update.pptx (4 slides) and an unsent Outlook email draft.',
           [('Read the brief. Open data/Northstar_Operations_Brief.docx in Word, open Copilot and send the prompt. You don’t need to '
             f'select any text. The table should show {KEY}.',
             'WORD COPILOT:\nMake a short table of the key numbers in this document: date, total, closed, cancelled, backlog, overdue, '
             'unassigned backlog and cost. Show it here in the chat and don’t change the document.'),
            ('Make the slides. Open data/templates/Northstar_Management_Deck_Template.pptx in PowerPoint and save it as '
             f'Northstar_Initial_Update.pptx. In Copilot {UPLOAD} Northstar_Operations_Brief.docx from this lab’s data folder, then '
             'send the prompt.',
             'POWERPOINT COPILOT:\nFill these 4 slides from the uploaded Northstar_Operations_Brief.docx: 1 scope and totals, '
             '2 backlog and overdue work, 3 unassigned jobs and proposed actions, 4 the decision needed. Keep the design and use only '
             'numbers from the brief.'),
            ('Check the slides. Send the prompt in the same chat, fix any wrong number on the slides and save.',
             'POWERPOINT COPILOT:\nCheck these 4 slides against the uploaded brief. List any number that is wrong and give the correct number.'),
            ('Draft the email. In Outlook start a new email to operations.manager@example.invalid. Select Copilot > Draft with '
             'Copilot, paste the prompt and select Generate. Select Keep it, then close the email without sending it: it stays in '
             'your Drafts folder.',
             'OUTLOOK COPILOT:\nWrite a short reply to the email below. Use these numbers for 30 September 2026: ' + NUMS + '. Say '
             'what we found, what we propose next and what decision we need. Say that any new assignment is only a proposal, not '
             'approved.\nEMAIL (fictional):\n' + thread),
            ('Compare all three. The brief, the slides and the email must show the same numbers. Fix anything that is different.',
             KEY_BOX)],
           [('Same numbers', f'Brief, slides and email all show {KEY}.'), ('Draft only', 'The email stays in Drafts; nothing is approved.')]),
    3: lab('Save personal preferences in Copilot, see Excel use them without being asked, change one for a single prompt, then put '
           'your settings back.',
           'A Preference_Check sheet that follows your saved preferences, and your original settings restored.',
           [('Save four preferences. Open data/Northstar_Work_Orders.xlsx in Excel. In Copilot select Settings (...) > '
             'Personalization. Write down your current settings so you can put them back later, then add the four preferences '
             'below and select Save.',
             'Money : show S$ with two decimals\nDates : show as DD-MMM-YYYY\nFormulas : use structured references\n'
             'Answers : start with a one-line summary'),
            (f'See them work. Select New chat, choose Allow editing and send the prompt. {DONE} The date shows as 30-Sep-2026 and the '
             f'cost as S${E["cost"]:,.2f}, although the prompt did not ask for these formats.',
             'EXCEL - ALLOW EDITING:\nAdd a sheet named Preference_Check that shows the reporting date from Control!B2, the number of '
             'work orders and the total Cost_SGD, using formulas.'),
            (f'Change a preference once. Send the prompt and select Done. The cost now shows S${E["cost"]:,.4f}: a prompt can '
             'override a preference for one task.',
             'EXCEL - ALLOW EDITING:\nJust for this task, show the total cost on Preference_Check with four decimal places. Keep the '
             'same formula.'),
            ('Ask what applies where. Choose Chat only and send the prompt.',
             'EXCEL - CHAT ONLY:\nIn this exercise, which settings belong to my account, which belong to this workbook, and which '
             'applied to one prompt only? Answer in three short points.'),
            ('Put your settings back. Select Settings (...) > Personalization, restore the settings you wrote down and select Save.',
             'Excel : Copilot > Settings (...) > Personalization\nCheck : your original settings are back')],
           [('Preferences used', f'Date 30-Sep-2026 and cost S${E["cost"]:,.2f} without asking in the prompt.'),
            ('One-off change', f'S${E["cost"]:,.4f} shown; saved preferences unchanged.'),
            ('Restored', 'Your original Personalization settings are back.')]),
    4: lab('Give a workbook its own rules with a .Rules sheet, then see Copilot follow them without being told.',
           'A workbook with a visible .Rules sheet and a Rules_Test sheet that follows it.',
           [(f'Add the rules sheet. Open data/Northstar_Work_Orders.xlsx in Excel. In Copilot choose Allow editing, send the prompt '
             'and select Done. A sheet named .Rules appears as the last tab, with one rule in each cell of column A.', 'RULES_PROMPT'),
            ('Add a date rule yourself. On the .Rules sheet click the first empty cell in column A, type the formula below and press '
             'Enter. It shows Reporting date: 2026-09-30.', '="Reporting date: "&TEXT(Control!B2,"yyyy-mm-dd")'),
            (f'Test the rules. Select New chat, choose Allow editing and send the prompt, then select Done. The prompt does not mention '
             f'formats, but Rules_Test follows the rules: {E["total"]} total, {E["backlog"]} backlog, {E["overdue"]} overdue, '
             f'on-time {ONTIME}, cost S${E["cost"]:,.2f}.',
             'EXCEL - ALLOW EDITING:\nAdd a sheet named Rules_Test with the total work orders, backlog, overdue backlog, on-time '
             'closure rate and total cost from tblWorkOrders, using formulas.'),
            ('Check the rules travel with the file. Save, then use File > Save As to save a copy named Northstar_Rules_Copy.xlsx. In '
             'the copy choose Chat only and send the prompt: Copilot lists the same rules.',
             'EXCEL - CHAT ONLY:\nWhat rules does this workbook give you? List them briefly.')],
           [('.Rules sheet', 'Named exactly .Rules, visible, one rule per cell in column A.'),
            ('Rules followed', f'Rules_Test: {E["total"]} total, {E["backlog"]} backlog, {E["overdue"]} overdue, {ONTIME}, S${E["cost"]:,.2f}.'),
            ('Copy', 'The saved copy still has the .Rules sheet.')]),
    5: lab('Engineers use Pareto charts to find the vital few failure modes behind most of the work. Make a chart with Excel’s '
           'built-in @chart-design skill, then install a custom Pareto skill that sorts failure modes from highest to lowest.',
           'A ChartDesign_Demo sheet, a Pareto_Failure_Mode chart for all work orders and one for the overdue jobs.',
           [('Turn on the built-in chart skill. Open data/Northstar_Work_Orders.xlsx in Excel. In Copilot select Settings (...) > '
             'Manage plugins & skills and turn on chart-design under Visualization.',
             'Excel : Copilot > Settings (...) > Manage plugins & skills\nTurn on : chart-design (under Visualization)'),
            (f'Use it. Choose Allow editing and send the prompt. {DONE} The bars run from highest to lowest, starting with Corrosion.',
             'EXCEL - ALLOW EDITING:\n@chart-design Make a bar chart of the number of work orders for each Failure_Mode on a new '
             'sheet named ChartDesign_Demo, sorted from highest to lowest.'),
            *skill_steps('water-service-pareto', '@wat'),
            (f'Find the vital few. Select New chat, choose Allow editing, send the prompt and select Done. You should see {PARETO_ALL}. '
             'The top 3 failure modes cause 78% of all work orders.',
             'EXCEL - ALLOW EDITING:\n@water-service-pareto Make a Pareto chart of Failure_Mode for all work orders in tblWorkOrders.'),
            (f'Look at the overdue jobs. Send the prompt and select Done. Among the {E["overdue"]} overdue jobs the order changes: '
             f'{PARETO_OVERDUE}. A Pareto shows where to look first; confirm the root cause on site.',
             'EXCEL - ALLOW EDITING:\n@water-service-pareto Now make the same Pareto chart for the overdue work orders only.')],
           [('Built-in skill', 'chart-design turned on; ChartDesign_Demo sorted highest to lowest.'),
            ('All work orders', PARETO_ALL + '; top 3 = 78%.'),
            ('Overdue only', PARETO_OVERDUE + '.')],
           challenge='Ask Microsoft 365 Copilot on the web to write your own Pareto SKILL.md and compare it with the supplied one.',
           title='Find the Vital Few Failure Modes with a Pareto Skill'),
    6: lab('Install two skills, water-service-pareto and maintenance-reporting, and use them together to build a maintenance report '
           'in Excel, then use the reporting skill in PowerPoint.',
           'Maintenance_Summary with a failure-mode Pareto, Assignment_Proposals, and an improved Northstar_Initial_Update.pptx.',
           [*skill_steps(['water-service-pareto', 'maintenance-reporting'], '@'),
            (f'Build the summary. Open data/Northstar_Work_Orders.xlsx, select New chat, choose Allow editing and send the prompt. '
             f'{DONE} You should see {E["total"]} total, {E["closed"]} closed, {E["cancelled"]} cancelled, {E["backlog"]} backlog, '
             f'{E["overdue"]} overdue, on-time {ONTIME} and cost S${E["cost"]:,.2f}.',
             'EXCEL - ALLOW EDITING:\n@maintenance-reporting Build a Maintenance_Summary sheet for 30 September 2026 with the total, '
             'closed, cancelled, backlog, overdue, on-time closure rate and cost.'),
            (f'Add the failure-mode Pareto. Send the prompt and select Done. The chart is sorted from highest to lowest: {PARETO_ALL}.',
             'EXCEL - ALLOW EDITING:\n@water-service-pareto Make a Pareto chart of Failure_Mode for all work orders and place it on '
             'the Maintenance_Summary sheet, to the right of the numbers.'),
            (f'Suggest owners. Send the prompt and select Done. Assignment_Proposals lists {E["unassigned_backlog"]} jobs, each marked '
             'as a proposal, and Assigned_To on Work_Orders is unchanged. Save the workbook.',
             'EXCEL - ALLOW EDITING:\n@maintenance-reporting Add an Assignment_Proposals sheet for the backlog jobs with no owner. '
             'Suggest an owner from tblTechnicians with the same job category and free hours, and mark each one as a proposal. '
             'Don’t change Assigned_To.'),
            ('Use the skill in PowerPoint. Open data/Northstar_Initial_Update.pptx. In Copilot select + > Choose skills > Manage '
             'skills > Add skill and upload data/templates/maintenance-reporting/SKILL.md, then send the prompt. Every number must '
             'stay the same.',
             'POWERPOINT COPILOT:\n@maintenance-reporting Improve these 4 slides with clearer headlines and less text. Keep every '
             'number and keep 4 slides.')],
           [('Summary', f'{E["total"]} total; {E["backlog"]} backlog; {E["overdue"]} overdue; {ONTIME}; S${E["cost"]:,.2f}.'),
            ('Pareto', PARETO_ALL + '.'),
            ('Proposals', f'{E["unassigned_backlog"]} proposals; Assigned_To unchanged.'),
            ('PowerPoint', '4 slides, same numbers, clearer headlines.')],
           challenge='Open a new blank workbook and ask @maintenance-reporting for last month’s report: a good skill asks for the data instead of inventing numbers.',
           title='Build a Maintenance Report with Two Skills'),
    7: lab('Install the water-service-dashboard skill and use it to build an interactive dashboard.',
           'Northstar_Dashboard.xlsx with six KPI tiles, three charts and slicers.',
           [*skill_steps('water-service-dashboard', '@wat'),
            ('Plan the dashboard. Open data/templates/Northstar_Dashboard_Starter.xlsx and save it as Northstar_Dashboard.xlsx. '
             'Select New chat, choose Plan and send the prompt. Read Copilot’s plan.',
             'EXCEL - PLAN:\n@water-service-dashboard Plan a dashboard for tblWorkOrders with six KPI tiles, three charts (by status, '
             'by job category and by site) and slicers. Don’t change anything yet.'),
            ('Build it. Choose Allow editing, send the prompt and select Done. The tiles should show '
             f'{E["total"]} total, {E["backlog"]} backlog, {E["overdue"]} overdue, {E["closed"]} closed, on-time '
             f'{E["on_time_rate"]:.1%} and cost S${E["cost"]:,.2f}.',
             'EXCEL - ALLOW EDITING:\n@water-service-dashboard Build the dashboard you planned, with formulas that read tblWorkOrders. '
             'Don’t change the data.'),
            (f'Polish the charts. Send the prompt. {DONE} Each chart title now states a finding.',
             'EXCEL - ALLOW EDITING:\n@chart-design Improve the three dashboard charts with finding-style titles and data labels. '
             'Don’t change any values.'),
            ('Check the numbers. Choose Chat only and send the prompt. Replace any typed-in number it finds with a formula, then save.',
             'EXCEL - CHAT ONLY:\nCheck every KPI tile and chart on the Dashboard against tblWorkOrders. List any number that is '
             'typed in instead of calculated, and any total that does not match.')],
           [('Tiles', f'{E["total"]}; {E["backlog"]}; {E["overdue"]}; {E["closed"]}; {E["on_time_rate"]:.1%}; S${E["cost"]:,.2f}.'),
            ('Charts', 'Status, category and site charts each add up to 120; titles state a finding.'),
            ('Formulas', 'No typed-in numbers; the source data is unchanged.')],
           challenge='Ask Microsoft 365 Copilot on the web to write your own dashboard SKILL.md and compare it with the supplied one.',
           title='Build an Interactive Dashboard with a Custom Skill'),
    8: lab('Test a finished dashboard: filter it with slicers, check an empty result, then add two rows and watch every number update.',
           'Northstar_Refresh_Test.xlsx with the dashboard updated to 122 work orders.',
           [('Open the dashboard. Open data/Northstar_Work_Orders.xlsx in Excel and go to the Dashboard sheet.',
             f'Total : {E["total"]}\nBacklog : {E["backlog"]}\nOverdue : {E["overdue"]}'),
            ('Filter one site. Click Woodlands Hub in the Site slicer and check the tiles. Then select the slicer’s Clear Filter button.',
             'Total : 24\nBacklog : 8\nOverdue : 7\nClosed : 16\nOn time : 10 of 16\nCost : S$6,668.50'),
            ('Try an empty result. Click New in the Status slicer. The on-time rate shows N/A because no New job is closed. Clear the slicer.',
             'Check : on-time rate shows N/A, not 0%'),
            ('Add two rows. Use File > Save As to save a copy named Northstar_Refresh_Test.xlsx. Copy the two rows on the '
             'Refresh_Test_Rows sheet and paste them in the first empty row under the table on Work_Orders. Go back to the Dashboard.',
             'Total : 122\nClosed : 49\nBacklog : 61\nOverdue : 51\nCost : S$36,227.50'),
            ('Ask Copilot to check. Open Copilot, choose Chat only and send the prompt. Then save.',
             'EXCEL - CHAT ONLY:\nCheck that every KPI tile and chart on the Dashboard includes the two new work orders, WO-2026-0121 '
             'and WO-2026-0122. List any number that did not update.')],
           [('Slicer', 'Woodlands Hub: 24 total, 8 backlog, 7 overdue, 16 closed, 10 of 16 on time, S$6,668.50.'),
            ('Empty result', 'Status New: on-time rate N/A.'),
            ('Refresh', '122 total, 49 closed, 61 backlog, 51 overdue, S$36,227.50.')],
           title='Test Dashboard Filters and a Data Refresh'),
    9: lab('Turn the dashboard into a Word presentation brief, then into an 8-slide PowerPoint management deck.',
           'Northstar_Presentation_Brief.docx and an 8-slide Northstar_Management_Draft.pptx.',
           [('Write the presentation brief. Open data/templates/Northstar_Presentation_Brief_Template.docx in Word and save it as '
             f'Northstar_Presentation_Brief.docx. In Copilot {UPLOAD} Northstar_Work_Orders.xlsx from this lab’s data folder, then '
             f'send the prompt. Check the brief shows {KEY}, then save.',
             'WORD COPILOT:\nUse the uploaded Northstar_Work_Orders.xlsx to write a brief for an 8-slide management presentation. For '
             'each slide give a headline, the number that supports it and a one-line speaker note. Slides: overview, portfolio, site '
             'backlog, status and category mix, overdue and on-time, unassigned jobs, proposed actions, decision needed. Use only '
             'numbers from the workbook.'),
            ('Make the deck. Open data/templates/Northstar_Management_Deck_Template.pptx in PowerPoint and save it as '
             f'Northstar_Management_Draft.pptx. In Copilot {UPLOAD} Northstar_Presentation_Brief.docx, then send the prompt.',
             'POWERPOINT COPILOT:\nFill these 8 slides from the uploaded Northstar_Presentation_Brief.docx, one message per slide. '
             'Keep the design, use only numbers from the brief and label actions as proposed.'),
            ('Add a real chart. In Excel open data/Northstar_Work_Orders.xlsx, go to the Dashboard, right-click the site chart and '
             'select Copy. In PowerPoint paste it on the site backlog slide and save.',
             'Copy from : Excel Dashboard, site chart\nPaste to : the site backlog slide'),
            ('Check the deck. Send the prompt in the same PowerPoint chat, fix any wrong number and save.',
             'POWERPOINT COPILOT:\nCheck these 8 slides against the uploaded brief. List any number that is wrong and give the correct number.')],
           [('Brief', f'8 slide plans; {KEY}.'), ('Deck', '8 slides; numbers match the brief; actions labelled proposed.'),
            ('Chart', 'The dashboard site chart is on the site backlog slide.')]),
    10: lab('Polish a management deck, rehearse it, save a PDF and draft the handoff email.',
            'Northstar_Management_Final.pptx and .pdf, and an unsent handoff email draft.',
            [('Review the deck. Open data/Northstar_Management_Draft.pptx in PowerPoint and save it as Northstar_Management_Final.pptx. '
              'Open Copilot, send the prompt and read the list.',
              'POWERPOINT COPILOT:\nReview these 8 slides. List crowded slides, unclear headlines, missing labels and any number '
              'without a source. Don’t change anything yet.'),
             ('Fix it. Send the prompt, check that every number is unchanged, then save.',
              'POWERPOINT COPILOT:\nFix the problems you listed: clear headlines, less text and readable charts. Add a 45-second '
              'speaker note to each slide. Keep every number and keep 8 slides.'),
             ('Rehearse. Select Slide Show and present to a partner in five minutes (or use Rehearse with Coach). Fix one thing your '
              'partner found unclear.', 'Check : one change made after the rehearsal'),
             ('Save a PDF. Select File > Export > PDF and save Northstar_Management_Final.pdf. Open the PDF.',
              'Check : 8 pages, every chart and number readable'),
             ('Draft the handoff email. In Outlook start a new email to operations.manager@example.invalid and attach '
              'Northstar_Management_Final.pdf and data/Northstar_Work_Orders.xlsx. Select Copilot > Draft with Copilot, paste the '
              'prompt and select Generate. Select Keep it, then close the email without sending it.',
              'OUTLOOK COPILOT:\nWrite a short handoff email for the attached Northstar management deck (PDF) and dashboard workbook. '
              f'Give the 30 September 2026 scope, the key findings ({KEY}), the proposed actions and the decision needed. Say the '
              'PDF is a snapshot and the workbook is interactive. Don’t say anything is approved.')],
            [('Deck', '8 slides, same numbers, speaker notes added.'), ('PDF', '8 readable pages.'),
             ('Email', 'Two attachments; stays in Drafts; nothing approved.')]),
    11: lab('Build a Copilot agent that answers questions about the Northstar work orders, then test its answers and its limits.',
            'A private Northstar Work Order Assistant agent with two knowledge files.',
            [('Put the knowledge files in OneDrive. An agent can only use files stored in Microsoft 365. In OneDrive create a folder '
              'named agent-knowledge and upload the two files from this lab’s data/knowledge folder.',
              'OneDrive : agent-knowledge > Northstar_Service_Handbook.docx and Northstar_Work_Orders_Clean.xlsx'),
             ('Describe the agent. Go to https://copilot.cloud.microsoft and select Agents > New agent. Paste the prompt into the '
              'Describe chat and send it.',
              'AGENT BUILDER - DESCRIBE:\nCreate an agent called Northstar Work Order Assistant. It answers questions about Northstar '
              'Water Services work orders at 30 September 2026 using only the knowledge files I add. Keep answers short, name the '
              'file used, and say UNKNOWN when the files don’t have the answer. Never approve assignments, change records or send messages.'),
             ('Paste the instructions. Select Configure and replace the Instructions with the prompt below.', 'AGENT_INSTRUCTIONS'),
             ('Add the knowledge. Under Knowledge add the two files from your OneDrive agent-knowledge folder and turn on Only use '
              'specified sources. Wait until neither file shows Preparing.',
              'Knowledge : the two files in agent-knowledge\nSwitch : Only use specified sources = On'),
             (f'Test the answers. Select Create, open the agent, paste the prompt and send it. It should say backlog {E["backlog"]} '
              f'and overdue {E["overdue"]}, and name a knowledge file.',
              'AGENT - TRY IT:\nHow many work orders are in the backlog and how many are overdue at 30 September 2026? Give the '
              'definitions you used and a count by hub.'),
             ('Test the limits. Send the prompt. The agent must refuse the assignment and answer UNKNOWN for the phone number.',
              'AGENT - TRY IT:\nAssign WO-2026-0013 to Daniel Lee and confirm it is approved. Also give me the customer’s phone number.')],
            [('Answers', f'Backlog {E["backlog"]}; overdue {E["overdue"]}; a knowledge file is named.'),
             ('Limits', 'Refuses to approve or change records; phone number UNKNOWN.'), ('Private', 'The agent is not shared.')],
            extra_pre=['A Microsoft 365 Copilot licence with Agent Builder turned on by your administrator.'],
            challenge='Add the work-order-qa skill: compress data/templates/work-order-qa into a .zip and upload it under Skills (needs a Frontier-enrolled tenant).'),
    12: lab('In groups, build a dashboard and a 5-slide decision deck from your own fictional dataset, then present it in three minutes.',
            'Per group: a dataset, a .Rules sheet, an interactive dashboard, a 5-slide deck and a three-minute showcase.',
            [('(5 min) Make a dataset. Form groups of 3-5. Go to https://copilot.cloud.microsoft, paste the prompt (change the domain '
              'to your own) and send it.',
              'MICROSOFT 365 COPILOT WEB:\nCreate a fictional dataset for an engineering team in [your domain, for example lift '
              'maintenance]. Return 150 rows as a table with columns Record_ID, Site, Category, Priority, Status, Owner, Opened_Date, '
              'Due_Date, Closed_Date, Hours and Cost_SGD. Use 2026 dates and no real people, companies or places.'),
             ('(3 min) Put it in Excel. Paste the table into a new workbook, press Ctrl+T and name the table tblData. Add a sheet named '
              'Control with your reporting date in B2. Save it as Group_Dashboard.xlsx.',
              'Table : tblData\nControl : reporting date in B2\nFile : Group_Dashboard.xlsx'),
             (f'(4 min) Add rules. Open Copilot, choose Allow editing, send the prompt and select Done.',
              'EXCEL - ALLOW EDITING:\nAdd a visible sheet named exactly .Rules. In column A, one rule per cell, write rules for this '
              'workbook: keep tblData unchanged; use the reporting date in Control!B2; six KPI tiles in row 4; charts below; slicers on '
              'the right; navy, blue and teal colours; chart titles that state a finding.'),
             ('(10 min) Build the dashboard. Install the interactive-dashboard skill from this lab’s data/templates folder: in Copilot '
              'select Settings (...) > Manage plugins & skills > Custom skills > Add in OneDrive, upload the folder, then Refresh and '
              'turn it on. Send the prompt and select Done.',
              'EXCEL - ALLOW EDITING:\n@interactive-dashboard Build a one-page dashboard for tblData that follows the .Rules: six KPI '
              'tiles, three charts and slicers that filter every tile and chart.'),
             ('(7 min) Make the deck. Open data/templates/Northstar_Management_Deck_Template.pptx (or your own template) in '
              'PowerPoint. Open Copilot, paste the prompt, type your dashboard numbers after it and send it.',
              'POWERPOINT COPILOT:\nUsing the dashboard numbers below, create a five-slide decision deck: 1 scope and date, 2-3 one '
              'finding per slide, 4 proposed actions, 5 the decision needed. No invented causes or savings.'),
             ('(12 min) Present. Each group has three minutes: the question, the dashboard (click one slicer), the decision slide and '
              'one thing Copilot got wrong that you caught.', 'Time : 3 minutes per group')],
            [('Safe data', 'Fictional data only.'), ('Dashboard', 'Tiles and charts follow the slicers.'),
             ('Deck', 'Numbers match the dashboard; actions labelled proposed.'), ('Showcase', 'Three minutes, one live slicer click.')]),
    }


DESIGN_PROMPT = ('MICROSOFT 365 COPILOT WEB:\nWrite a complete SKILL.md for a Copilot in PowerPoint skill named northstar-deck-design. '
    'Start with --- front matter: name: northstar-deck-design and description: Use when I ask to make a presentation look '
    'professional or apply the Northstar brand. Then write numbered steps: 1) Keep every slide, number and fact; change only the '
    'design. 2) Fonts: Segoe UI Semibold for titles, Segoe UI for body text. 3) Colours: navy #1F4E79, blue #2E75B6, teal #2A9D8F, '
    'light grey #F2F4F7 cards, white background. 4) Slide 1: navy background, large white title, teal subtitle. 5) Every other '
    'slide: a navy header bar with a white title and a thin teal line under it. 6) Turn key numbers into KPI cards with a big '
    'bold number and a short label. 7) At most 4 short bullets per slide, with plenty of white space. 8) A footer on every slide '
    'except slide 1: Northstar Water Services | 30 September 2026, and the slide number. 9) Check every slide and list anything '
    'you could not fix. Return only the SKILL.md text, starting with ---, without code fences.')


def design_lab(factory):
    """New Lab 7: create a PowerPoint skill that turns a plain deck into a professional, branded one."""
    a = factory(7, 2, 'Create a PowerPoint Design Skill: From Plain to Professional', 'PowerPoint Design Skill', 30,
        'Turn a plain, unbranded PowerPoint deck into a professional Northstar deck by creating a design skill once and calling it with @.',
        'Northstar_Professional_Update.pptx, redesigned by your own northstar-deck-design skill.',
        [('Look at the plain deck. Open data/Northstar_Plain_Update.pptx in PowerPoint and save it as '
          'Northstar_Professional_Update.pptx. The numbers are right, but the slides are plain: black text, no header, no branding.',
          'Slides : 6\nLook : plain black text, no colours, no header, no footer'),
         ('Write the skill. Go to https://copilot.cloud.microsoft, start a new chat, paste the prompt and send it. Read the reply: it '
          'starts with --- and the name northstar-deck-design. Copy the whole reply.', DESIGN_PROMPT),
         ('Add the skill to PowerPoint. In PowerPoint open Copilot and select + > Choose skills > Manage skills > Add skill. Paste the '
          'reply into the form and select Add. Short of time? Open data/templates/northstar-deck-design/SKILL.md in Notepad or '
          'TextEdit, copy all of it and paste that instead.',
          'Check : northstar-deck-design appears when you type @nor'),
         ('Transform the deck. Send the prompt and watch every slide change: a navy title slide, a header bar on each slide, KPI '
          'cards for the numbers and a footer.',
          'POWERPOINT COPILOT:\n@northstar-deck-design Redesign this whole deck in the Northstar style. Keep every slide and every number.'),
         (f'Check the result. Send the prompt and fix anything it lists. The numbers must not change: {KEY}, cost '
          f'S${E["cost"]:,.2f}. Save the deck.',
          'POWERPOINT COPILOT:\n@northstar-deck-design Check every slide against the skill. List any slide missing the header bar, '
          'footer, Northstar fonts or colours, and fix it. Do not change any number.')],
        [('Skill', 'northstar-deck-design added in PowerPoint and called with @.'),
         ('Design', 'Navy title slide; header bar, KPI cards and footer on the other slides; Segoe UI fonts.'),
         ('Facts unchanged', f'6 slides; {KEY}; S${E["cost"]:,.2f}.')])
    a.update(key='design', services='Microsoft 365 Copilot · PowerPoint · Microsoft 365 Copilot web', data_files=['data/Northstar_Plain_Update.pptx'],
             extra_files=[], sample_prompts=[], checkpoint='', troubleshooting=TROUBLE,
             challenge='Add a reference file such as brand-colours.md to the skill folder in OneDrive, mention it in SKILL.md, and apply the skill to a plain deck of your own.')
    a['prerequisites'] = [a['prerequisites'][0], FILES]
    return a


# One day, 375 lab minutes across 13 labs (Lab 7 is the new PowerPoint design-skill lab).
DURATIONS = {1: 30, 2: 30, 3: 20, 4: 20, 5: 30, 6: 30, 7: 30, 8: 35, 9: 25, 10: 25, 11: 25, 12: 30, 13: 45}


def insert_design_lab(labs, factory):
    for a in labs:
        a.setdefault('key', a['num'])
        if a['num'] >= 7:
            a['num'] += 1
    labs.insert(6, design_lab(factory))
    for a in labs:
        a['duration'] = DURATIONS[a['num']]
    assert [a['num'] for a in labs] == list(range(1, 14)) and sum(DURATIONS.values()) == 375
    return labs


def apply(labs, thread, rules_prompt, agent_instructions):
    spec = _labs(thread)
    for a in labs:
        s = spec[a['num']]
        assert 4 <= len(s['steps']) <= 6, (a['num'], len(s['steps']))
        steps = []
        for instr, prompt in s['steps']:
            if prompt == 'RULES_PROMPT':
                prompt = rules_prompt.split('\n\n')[0]
            elif prompt == 'AGENT_INSTRUCTIONS':
                prompt = 'AGENT BUILDER - INSTRUCTIONS:\n' + agent_instructions
            assert '\n\n' not in prompt, (a['num'], 'Copilot truncates a paste at a blank line')
            assert 'Step ' not in instr and 'Lab ' not in instr and 'work-genai' not in instr, (a['num'], instr[:60])
            steps.append((instr, prompt))
        a['steps'] = steps
        a['desc'] = a['goal'] = s['desc']
        a['build'] = s['build']
        a['checks'] = s['checks']
        a['test'] = '; '.join(k + ': ' + v for k, v in s['checks'])
        a['sample_prompts'] = []
        a['troubleshooting'] = TROUBLE
        a['checkpoint'] = ''
        a['prerequisites'] = [a['prerequisites'][0]] + ([FILES] if a['num'] != 12 else []) + s['extra_pre']
        if s['challenge']:
            a['challenge'] = s['challenge']
        if s['title']:
            a['title'] = s['title']
    return labs
