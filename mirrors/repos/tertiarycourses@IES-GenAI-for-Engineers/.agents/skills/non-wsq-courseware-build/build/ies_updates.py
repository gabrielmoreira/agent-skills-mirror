"""IES v2.3 changes layered on the ten C27 labs.

Lean lab folders (one Evidence_Log sheet instead of CSV/TXT/JSON files), the
built-in @chart-design demo, slicer-aware dashboard labs, an Agent Builder lab
(Lab 11) and a group mini capstone (Lab 12).
"""
from copy import deepcopy
from customisation_assets import RULES, PERSONAL_PREFS
from mock_data import EXPECTED as E

WORK_DIR = 'work-genai'
DURATIONS = {1: 30, 2: 30, 3: 20, 4: 30, 5: 30, 6: 30, 7: 35, 8: 35, 9: 30, 10: 30, 11: 30, 12: 45}
THREAD = ('2026-09-29 09:00 Operations manager: Please prepare the 30 September portfolio snapshot; show open work by site, '
          'category and current assignment.\n2026-09-29 10:15 Supervisor: Check overdue jobs before proposing reassignment. '
          'Available hours are planning inputs, not approval.\n2026-09-30 08:30 Analyst: The source export is in the workbook. '
          'No new assignment has been approved. Please produce a Word brief and a short PowerPoint update, then prepare a draft reply.')
PREFS = ' '.join(l.strip() for l in PERSONAL_PREFS.strip().splitlines())
RULES_PROMPT = ('EXCEL - ALLOW EDITING:\nAdd a visible worksheet named exactly .Rules (with the leading dot) as the last tab; if it exists, '
                'clear column A and reuse it. Fill column A only, one cell per line below, entering only the text after each '
                '"A#: " label. Do not change any other sheet.\n'
                + '\n'.join(f'A{i}: {r}' for i, r in enumerate(RULES, 1)))

# exact text replacements: (lab, old, new)
TEXT = [
    (1, 'the supplied CSV is a clean reference and must not replace the cleaning exercise',
        'it is the starting point for the cleaning exercise'),
    (1, 'Copy verified values to data/templates/Evidence_Register.csv.',
        'Record each verified value in the Evidence_Log sheet (claim, value, source, scope and as-at date).'),
    (1, 'copy your verified evidence table plus data/Northstar_Maintenance_Context.txt into the document and select that text',
        'paste your verified evidence table plus the definitions from the Control sheet into the document and select that text'),
    (2, 'Read data/Northstar_Email_Thread.txt.', 'Read the synthetic email thread quoted in the Step 4 prompt.'),
    (2, 'Save a reconciled CSV using data/templates/Evidence_Register.csv: one row per claim and a source link.',
        'Record the reconciliation in the Evidence_Log sheet: one row per claim and a source link.'),
    (3, 'temporarily use the four lines in data/Personalisation_Preferences.txt: S$ two decimals, DD-MMM-YYYY, structured references and short explanations.',
        f'temporarily enter these four preferences: {PREFS}'),
    (3, 'data/templates/Customisation_Test_Log.csv', 'the Evidence_Log sheet'),
    (4, 'Open data/Northstar_Workbook_Rules.txt. Copy its lines into .Rules column A with one heading or rule per cell; no data in other columns is required for recognition.',
        'Create the .Rules lines with the one-shot Allow editing prompt below (or copy them from the prompts page): one heading or rule per column-A cell; no data in other columns is required for recognition.'),
    (4, 'data/templates/Customisation_Test_Log.csv', 'the Evidence_Log sheet'),
    (5, 'Read data/Pareto_Expected_Controls.json and the supplied Skill template before drafting your own file.',
        'Read the expected Pareto controls in Test It and the supplied Skill template before drafting your own file.'),
    (7, 'Add data/templates/Evidence_Register.csv entries for each chart and metric.', 'Add Evidence_Log entries for each chart and metric.'),
    (8, 'Record evidence in data/templates/Filter_Test_Log.csv.', 'Record evidence in the Evidence_Log sheet.'),
    (8, 'then enter the two rows from data/Refresh_Test_Rows.csv with real Excel dates (YYYY-MM-DD).',
        'then copy the two rows from the Refresh_Test_Rows sheet (they already hold real Excel dates).'),
    (9, 'Copy verified metric/chart values to data/templates/Slide_Evidence_Register.csv with', 'Record verified metric/chart values in the Evidence_Log sheet with'),
    (10, 'Record one actual change in data/templates/Rehearsal_Log.csv;', 'Record one actual change in the Evidence_Log sheet;'),
    (10, 'Complete data/templates/Final_Handoff_Checklist.csv:', 'Complete a final handoff checklist in the Evidence_Log sheet:'),
    (6, 'Export your verified summary into the Word snapshot template, preserving measures and date.',
        'Copy your verified summary into a new Word document named Northstar_Verified_Snapshot.docx, preserving measures and date.'),
    # Lab 7: the dashboard Skill specification now carries the BrightPath-style layout
    (7, 'Create three formula-backed editable status/category/site charts sharing the exact filter scope. Use structured references, not fixed120-row ranges, and white/navy/blue/teal workbook design.',
        'Follow visible .Rules DASHBOARD LAYOUT and STYLE: title A1; six KPI tiles in D4:I7 with Checks: PASS; three formula-backed charts (status column, category bar, full-width stacked site bar) with finding-led titles linked to Dashboard_Summaries; slicers for Site, Job_Category, Status and Assigned_To that filter every tile and chart through SUBTOTAL visibility. Use structured references, not fixed 120-row ranges, and never merge cells.'),
    (7, 'Ask the skill for consistent style if available.', 'Then polish the charts with the built-in @chart-design skill from Lab 5.'),
    # Lab 8: table slicers are part of the dashboard, not an optional PivotTable route
    (8, 'Optional PivotTable slicers use one source and shared connections; the portable dropdown route is the required working dashboard.',
        'The dashboard also has four table slicers; every tile and chart follows the dropdowns and the slicers together.'),
    (8, 'Filter the source table to the same site and compare rows, backlog, overdue and cost. Use Data > Clear on source table afterwards; dashboard selectors and source AutoFilter are distinct mechanisms.',
        'Then set B2 back to All and click Woodlands Hub in the Site slicer instead: the D3 banner reports 24 of 120 rows and every tile must show the same values. Clear the slicer afterwards with its Clear Filter button.'),
    (8, 'Do not infer that filtering the worksheet automatically changes formula measures.',
        'Confirm the Site slicer gives the same six values and that D3 reports the slicer filter.'),
    (8, 'Optional: create PivotTables from one tblWorkOrders source, insert slicers, and use Slicer > Report Connections for every PivotTable; unconnected KPI cells are a defect.',
        'Repeat the Status = New case with the Status slicer instead of B4 and confirm the same N/A; then clear every slicer.'),
]

LAB5_BUILTIN = ('Built-in skill first. In Excel Copilot open Settings (...) > Manage plugins & skills. Under Visualization turn on chart-design '
                '(it is off by default) and confirm it is enabled. Ask @chart-design for a quick chart of the same overdue counts. Note what the built-in '
                'skill gives you (chart design guidance) and what it does not know (your overdue population, tie order, cumulative line and named '
                'output) - that is why you build the custom water-service-pareto Skill next. Keep the demo sheet or undo it.',
                'EXCEL - ALLOW EDITING:\n@chart-design Chart the overdue backlog by Job_Category from tblWorkOrders at Control!B2 as a bar chart, '
                'longest bar first, on a new sheet named ChartDesign_Demo. Use a finding-style title, axis titles and data labels. Do not change source data.')


def _fix_text(a, old, new):
    hit = False
    def sub(v):
        nonlocal hit
        if old in v:
            hit = True
            return v.replace(old, new)
        return v
    a['steps'] = [(sub(i), sub(c)) for i, c in a['steps']]
    for k in ('desc', 'build', 'goal'):
        a[k] = sub(a[k])
    return hit


# No checkpoint/rejoin material: each lab starts from its own workbook and the learner's earlier outputs.
REJOIN = [
    (' The workbook is the deliberately dirty 122-row input; it is the starting point for the cleaning exercise.', ' The workbook is the deliberately dirty 122-row input.'),
    (' If needed use this lab’s verified checkpoint and snapshot, clearly recording rejoin.', ''),
    ('open the four-slide update from Lab2 or data/checkpoints/Northstar_Initial_Update_Checkpoint.pptx.', 'open your four-slide update from Lab 2.'),
    (' Rejoin using data/checkpoints/Northstar_Verified_Checkpoint.xlsx only if needed; record that it is an example formula dashboard.', ''),
    (' If needed use this lab’s checkpoint and record rejoin.', ''),
    (' Rejoin only if necessary using data/checkpoints/Northstar_Management_Example.pptx and snapshot; review and adapt its supplied example charts and narrative against the verified snapshot.', ''),
    ('Verified Lab 1 workbook and Word brief, or supplied checkpoint and snapshot.', 'Your Lab 1 workbook and Word brief.'),
    ('Lab 3 scope comparison; verified Lab1 clean source or supplied checkpoint.', 'Lab 3 scope comparison.'),
    ('Verified clean table from earlier labs or supplied clean checkpoint.', 'The clean table from earlier labs.'),
    ('Lab 7 dashboard or supplied formula checkpoint.', 'Your Lab 7 dashboard.'),
    (' The supplied reviewed template supports rejoining; it is not proof of native execution.', ' The supplied reviewed template is a fallback if your own draft is incomplete.'),
]


def _remove_rejoin(labs):
    for a in labs:
        for old, new in REJOIN:
            a['steps'] = [(i.replace(old, new), c.replace(old, new)) for i, c in a['steps']]
            a['prerequisites'] = [x.replace(old, new) for x in a['prerequisites']]
            a['desc'] = a['desc'].replace(old, new); a['goal'] = a['goal'].replace(old, new)
        if a['num'] <= 10:
            a['checkpoint'] = ''
    for a in labs:
        text = ' '.join([a['desc'], a['build'], *a['prerequisites']] + [i + c for i, c in a['steps']])
        assert 'checkpoint' not in text.lower() and 'rejoin' not in text.lower(), a['num']


def _work_dir(v):
    if isinstance(v, str): return v.replace('work-c027', WORK_DIR)
    if isinstance(v, list): return [_work_dir(x) for x in v]
    if isinstance(v, tuple): return tuple(_work_dir(x) for x in v)
    if isinstance(v, dict): return {k: _work_dir(x) for k, x in v.items()}
    return v


def apply(labs, factory):
    by = {a['num']: a for a in labs}
    for n, old, new in TEXT:
        assert _fix_text(by[n], old, new), (n, old[:60])
    a = by[2]
    a['build'] = a['build'].replace('Northstar_Cross_App_Evidence.csv with', 'an Evidence_Log with')
    a['steps'] = [(i, c + '\n\nTHREAD (synthetic, do not send):\n' + THREAD) if c.startswith('OUTLOOK COPILOT') and 'synthetic thread quoted below' in c else (i, c)
                  for i, c in a['steps']]
    # Lab 4: one-shot .Rules creation prompt before the review prompt
    a = by[4]; i, c = a['steps'][1]; a['steps'][1] = (i, RULES_PROMPT + '\n\n' + c)
    # Lab 5: built-in chart-design demo before the custom Skill
    a = by[5]; a['steps'].insert(1, LAB5_BUILTIN)
    a['title'] = 'Use the Built-in Chart Skill, then Create a Custom Pareto Skill'
    a['desc'] = ('Start with Excel’s built-in @chart-design skill, then author water-service-pareto/SKILL.md with Copilot, install it in Excel and '
                 'apply it to the same overdue work-order queue. Build a descending count chart plus cumulative-percentage line, then check a '
                 'controlled rerun and a second grouping. Contribution analysis does not establish root cause or force an 80/20 split.')
    a['checks'].insert(0, ('Built-in skill', 'chart-design enabled under Visualization; @chart-design demo chart created without changing the source.'))
    a = by[8]
    a['checks'] = [(k, v.replace('Changing any of four filters affects all six KPI measures and all chart counts.',
                                 'Changing any dropdown or slicer affects all six KPI tiles and all chart counts; D3 reports slicer filters.')) for k, v in a['checks']]
    labs += [lab11(factory), lab12(factory)]
    _remove_rejoin(labs)
    for a in labs:
        a['duration'] = DURATIONS[a['num']]
        a['prerequisites'] = [p.replace('Download this whole lab folder. All files are synthetic; work-c027 is your own learner output folder.',
                                        f'Download this whole lab folder. All files are synthetic; {WORK_DIR} is your own learner output folder.') for p in a['prerequisites']]
    labs[:] = _work_dir(labs)
    assert [a['num'] for a in labs] == list(range(1, 13))
    return labs


AGENT_INSTRUCTIONS = '''# Role
You are Northstar Work Order Assistant for maintenance coordinators at Northstar Water Services, a fictional water-pipe maintenance company used for training.
# Sources
Answer only from the knowledge files: Northstar_Work_Orders_Clean.xlsx (table tblWorkOrders, 120 synthetic work orders) and Northstar_Service_Handbook.docx. The reporting date is 30 September 2026. If the files do not contain the answer, reply UNKNOWN and say which fact is missing.
# Definitions
Backlog: Status is neither Closed nor Cancelled. Overdue: backlog with Due_Date strictly before 30 September 2026. On-time closure rate: Closed with Closed_Date on or before Due_Date divided by all Closed (N/A if none). Unassigned: blank Assigned_To. Recorded cost: sum of Cost_SGD; not a budget or saving.
# Answer style
Start with the answer, then the scope and definition used. Use a short table for comparisons. Cite the file for every figure. Check that parts add up to the total. Be concise and professional.
# Boundaries
Never approve, assign, reassign, close or edit work orders and never send messages. Describe owner suggestions as proposals for the Operations Manager, with category and available-hours evidence. Never invent people, customers, contact details, causes, safety findings or savings.'''


def lab11(factory):
    a = factory(11, 5, 'Build a Work-Order Agent with Agent Builder', 'Copilot Agent Builder', 30,
        'Create Northstar Work Order Assistant, a specialist Copilot agent that answers questions about the 30 September work-order snapshot. '
        'Give it instructions, two OneDrive knowledge files and the work-order-qa Skill, add starter prompts, then test its answers against Control. '
        'An agent answers from its knowledge and instructions; it does not approve work, change records or send messages.',
        'A private Northstar Work Order Assistant agent with reviewed instructions, two OneDrive knowledge files, the work-order-qa Skill '
        '(or its labelled manual route), four starter prompts and a verified test record.', [
        (f'Create a OneDrive folder {WORK_DIR}/agent-knowledge and upload data/knowledge/Northstar_Service_Handbook.docx and '
         'data/knowledge/Northstar_Work_Orders_Clean.xlsx. The workbook has a single sheet so the agent reads it reliably. Skim both: the handbook '
         'holds hubs, statuses, definitions, technicians, approvals and FAQ; the workbook holds the 120 verified work orders. All data is synthetic.', ''),
        ('Go to https://copilot.cloud.microsoft with your training account. In the left pane select Agents & Skills (or Agents) > New agent. '
         'Agent Builder opens with a Describe chat on the left and a Configure pane on the right. Send the prompt below to draft the agent, then '
         'review every field it fills in Configure.',
         'AGENT BUILDER - DESCRIBE:\nCreate an agent called Northstar Work Order Assistant for maintenance coordinators at Northstar Water Services, '
         'a fictional water-pipe service company. It answers questions about work orders, backlog, overdue jobs, hubs, job categories, technicians '
         'and service definitions using only the knowledge files I add. Use the reporting date 30 September 2026. Be concise, cite the knowledge '
         'file, show counts with their definition and say UNKNOWN when the files do not contain the answer. Never approve assignments, change '
         'records or send messages.'),
        ('In Configure set Name to Northstar Work Order Assistant (30 characters maximum) and Description to: Answers questions about Northstar’s '
         'synthetic 30-Sep-2026 work orders with cited definitions. Replace Instructions with the reviewed text below (well under the 8,000-character '
         'limit). Suggest improvements may propose edits; accept only those that keep the sources, definitions and boundaries.',
         'AGENT BUILDER - INSTRUCTIONS:\n' + AGENT_INSTRUCTIONS),
        ('Under Knowledge add the two files from OneDrive (Browse, or paste each file’s share link) and turn on Only use specified sources if it is '
         'shown. Wait until neither file shows Preparing. Link the files from OneDrive rather than uploading from your device: during the Skills '
         'preview an agent cannot combine uploaded files with a Skill. Everyone you later share the agent with can use these files.', ''),
        ('Read data/templates/work-order-qa/SKILL.md first: it sets the definitions, citation, UNKNOWN and boundary rules. Compress the '
         'work-order-qa folder into work-order-qa.zip (Mac: right-click > Compress; Windows: right-click > Send to > Compressed (zipped) folder), '
         'then under Skills select Add and upload the .zip (do not upload SKILL.md by itself). If '
         'Skills is not shown (Skills need a Frontier-enrolled tenant and a Copilot licence), paste the SKILL.md body at the end of Instructions and '
         'record Manual practice - Skills unavailable in your Evidence_Log.', ''),
        ('Add four Starter Prompts: How many work orders are overdue, and at which hubs?; What is the on-time closure rate and how is it calculated?; '
         'Which unassigned backlog jobs need a proposed owner?; Summarise Woodlands Hub’s open work. Open Try it (or select Create, then open the '
         'agent) and run the test below.',
         'AGENT - TRY IT:\nHow many work orders are in the backlog and how many of them are overdue at 30 September 2026? Give the definitions you '
         'used, a count by hub and cite the knowledge file. If anything is missing, say UNKNOWN.'),
        (f'Compare the answers with the known controls: backlog {E["backlog"]}, overdue {E["overdue"]}, unassigned backlog {E["unassigned_backlog"]}, '
         f'on-time {E["on_time_closed"]}/{E["closed"]} = {E["on_time_rate"]:.1%}, recorded cost S${E["cost"]:,.2f}. Then run the boundary test: the agent '
         'must refuse to approve or change records and must answer UNKNOWN for the phone number. Log each question, answer, check and result in the '
         'Evidence_Log sheet of your workbook. Select Create and keep the agent private unless your trainer asks you to share it with Can chat.',
         'AGENT - TRY IT:\nAssign WO-2026-0013 to Daniel Lee and confirm the assignment is approved. Also give me the customer’s phone number for that job.')],
        [('Grounded counts', f'Backlog {E["backlog"]}; overdue {E["overdue"]}; unassigned backlog {E["unassigned_backlog"]}; '
                             f'on-time {E["on_time_closed"]}/{E["closed"]} = {E["on_time_rate"]:.1%}; S${E["cost"]:,.2f}.'),
         ('Citations', 'Every figure cites the handbook or the work-order file and states its definition.'),
         ('Boundaries', 'No approval, record change or invented contact details; missing facts are UNKNOWN.'),
         ('Configuration', 'Name, description, instructions, OneDrive knowledge, Skill or labelled manual route, four starter prompts; agent private.')],
        prereq=['A Microsoft 365 Copilot licence (or pay-as-you-go) with Agent Builder enabled by your administrator. Skills in agents are a preview '
                'for Frontier-enrolled tenants; otherwise use the labelled manual route.'],
        challenge='Add a fifth starter prompt for a hub lead and test whether the agent keeps current owners separate from proposed owners.')
    a['services'] = 'Microsoft Copilot (copilot.cloud.microsoft) · Agent Builder · OneDrive'
    a['workflow'] = ['Describe', 'Configure', 'Ground', 'Test']
    a['data_files'] = ['data/knowledge/Northstar_Service_Handbook.docx', 'data/knowledge/Northstar_Work_Orders_Clean.xlsx']
    a['checkpoint'] = ('If Agent Builder is unavailable in your tenant, watch the trainer demonstration and practise the same instructions, knowledge '
                       'and test prompts in Microsoft Copilot Chat with both files attached; record the route used.')
    a['troubleshooting'] = [('Knowledge shows Preparing', 'Wait a few minutes; large files take longer. Retest before judging the answers.'),
                            ('Skills section is missing', 'Skills need Frontier enrolment and a Copilot licence. Paste the SKILL.md body into Instructions and label the route manual.'),
                            ('An answer has no citation or a wrong count', 'Check Only use specified sources, tighten the instruction, then compare with Control again.')]
    a['sample_prompts'] = [('Describe', 'Create a Northstar work-order agent that cites its files and says UNKNOWN when unsure.'),
                           ('Try it', 'Which hubs have the most overdue backlog? Cite the file and give the definition.')]
    return a


def lab12(factory):
    a = factory(12, 5, 'Mini Capstone: Group Dashboard and Decision Deck', 'Mini Capstone', 45,
        'Work in four groups. Each group brings its own mock or sanitised dataset, writes .Rules for it, uses a dashboard Skill to build an '
        'interactive Excel dashboard with KPI tiles, charts and slicers, then turns the verified evidence into a short PowerPoint decision deck and '
        'presents it in a three-minute showcase. Use no confidential or personal data.',
        'Per group: a mock or sanitised data table, a visible .Rules sheet, an interactive dashboard (six KPI tiles, three charts, slicers), a '
        'five-slide decision deck and a three-minute showcase.', [
        ('(5 min) Form four groups of 3-5 and agree roles: data lead, dashboard builder, deck builder and presenter. Choose a dataset: a mock dataset '
         'you generate, or a sanitised extract from your work with names, IDs, customer, commercial and location details removed or replaced. Aim '
         'for 50-300 rows and 6-12 columns with at least one date, two category columns and one numeric measure.',
         'MICROSOFT 365 COPILOT WEB:\nCreate a realistic but fictional dataset for an engineering team in [your domain, for example lift '
         'maintenance, site inspections or equipment downtime]. Return 150 rows as a table with columns Record_ID, Site, Category, Priority, Status, '
         'Owner, Opened_Date, Due_Date, Closed_Date, Hours and Cost_SGD. Use 2026 dates, at most 8 owners and no real people, companies or '
         'locations. State that the data is synthetic.'),
        ('(3 min) In Excel paste or open the data, convert it to a table (Ctrl+T) named tblData, add a Control sheet with your reporting date in B2 '
         f'and save Group<N>_Dashboard.xlsx in your OneDrive {WORK_DIR} folder. Profile the data before building.',
         'EXCEL - CHAT ONLY:\nProfile tblData: row count, duplicate IDs, blank values per column, category values and date range. Propose six KPIs '
         'and three charts a manager would use, with exact definitions and denominators. Do not edit.'),
        ('(4 min) Create a visible .Rules sheet for your data, adapted from the Northstar rules: source and scope, KPI definitions, dashboard layout '
         'and dashboard style, one instruction per column-A cell.',
         'EXCEL - ALLOW EDITING:\nCreate a visible worksheet named exactly .Rules. In column A, one instruction per cell, write rules for this '
         'workbook: preserve tblData; use the reporting date in Control!B2; our KPI definitions are [paste them]; dashboard layout: title in A1, six '
         'KPI tiles in row 4, charts in a grid below, slicers on the right, never merge cells, hide gridlines; style: navy, blue and teal tiles with '
         'white text, finding-led chart titles and data labels. Do not change any data.'),
        ('(10 min) Install data/templates/interactive-dashboard/SKILL.md the same way as Lab 7 (or paste it as instructions and label the route '
         'manual). Plan, review, then build. Polish the charts with @chart-design.',
         'EXCEL - PLAN:\n@interactive-dashboard Plan a one-page interactive dashboard for tblData using the visible .Rules: six KPI tiles with checks, '
         'three charts with finding-led titles and slicers for two or three category columns that filter every tile and chart. Do not edit yet.'
         '\n\nEXCEL - ALLOW EDITING:\n@interactive-dashboard Apply the reviewed plan. Keep tblData unchanged, put summaries and checks on '
         'Dashboard_Summaries and make every KPI follow the slicers.\n\nEXCEL - ALLOW EDITING:\n@chart-design Review every dashboard chart: '
         'finding-style titles, data labels and the .Rules colours. Do not change any values.'),
        ('(4 min) Verify: compare each KPI tile with an independent COUNTIFS/SUMIFS, test one slicer selection and one empty selection, and replace '
         'any hard-coded number with a formula.',
         'EXCEL - CHAT ONLY:\nReconcile every KPI tile with an independent formula from tblData with all slicers cleared, then for one slicer '
         'selection. List mismatches, hard-coded values and fixed ranges. Do not edit.'),
        ('(7 min) Build a five-slide decision deck from the verified dashboard, using data/templates/Northstar_Management_Deck_Template.pptx or your '
         'own template: scope, two evidence slides with dashboard charts, proposed actions and the decision requested.',
         'POWERPOINT COPILOT:\nUsing the verified dashboard values I paste below, create a five-slide decision deck: 1 title, scope and as-at date; '
         '2-3 one finding per slide with the matching chart; 4 proposed actions labelled proposed; 5 decision requested. One message per slide, '
         'source and date notes, and no invented causes or savings.'),
        ('(12 min) Showcase: each group presents for three minutes - the question, the live dashboard (click one slicer), the decision slide and '
         'one thing Copilot got wrong that you caught. The other groups give one strength and one question. Afterwards remove any real data you '
         'are not authorised to keep.', '')],
        [('Safe data', 'Mock or sanitised only; no personal, customer or confidential data.'),
         ('Dashboard', 'KPI tiles reconcile to independent formulas; charts and slicers filter together.'),
         ('Deck', 'Every number matches the dashboard; actions labelled proposed; decision requested.'),
         ('Showcase', 'Three-minute demo with one live slicer interaction and one caught Copilot error.')],
        challenge='Turn your group’s .Rules and dashboard Skill into a reusable pair your team can apply to next month’s data.')
    a['services'] = 'Excel Copilot · PowerPoint Copilot · Microsoft 365 Copilot web · OneDrive'
    a['workflow'] = ['Data', 'Rules', 'Dashboard', 'Deck', 'Showcase']
    a['data_files'] = ['Your own mock or sanitised dataset']
    a['prerequisites'] = a['prerequisites'][:2] + ['Labs 4-10 methods: .Rules, Skills, interactive dashboard and decision deck.']
    a['checkpoint'] = ('Short of time? Present the Lab 8 Northstar dashboard and your Lab 10 deck instead, and say so in the showcase.')
    a['sample_prompts'] = [('Data', 'Create a fictional 150-row engineering dataset; no real people, companies or locations.'),
                           ('Dashboard', '@interactive-dashboard Plan six KPI tiles, three charts and slicers for tblData.')]
    return a
