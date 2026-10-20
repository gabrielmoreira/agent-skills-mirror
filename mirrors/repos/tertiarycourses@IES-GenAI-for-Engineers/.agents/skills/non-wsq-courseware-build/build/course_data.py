"""IES GenAI for Engineers v2.4 (from the C27 Northstar pipeline): one connected maintenance scenario,
an Agent Builder lab and a group mini capstone, branded for IES Academy."""
TITLE=SHORT_TITLE='GenAI for Engineers'
COURSE_CODE=''
COURSE_PAGE=''
GITHUB_REPO='tertiarycourses/IES-GenAI-for-Engineers'
PROMPTS_PAGE='https://tertiarycourses.github.io/IES-GenAI-for-Engineers/prompts/'
VERSION='v2.4';VERSION_DATE='19 October 2026'
ORG='IES Academy';UEN=''
# Client branding consumed by the engine (defaults are the Tertiary house values).
COVER_TAG='IES ACADEMY  •  ENGINEERING';FOOTER_TAG=TITLE;COPYRIGHT_SHORT='© IES Academy'
COPYRIGHT='© 2026 IES Academy. All rights reserved.';ORG_MARK='IES ACADEMY';ORG_LOGO=None;FOOTER_URL='';CONTACT_LINE=''
MATERIALS_STEP='Open the IES Academy course folder supplied by your trainer';MATERIALS_CAPTION='Course materials: trainer-supplied IES Academy folder'
WRAP_UP_LINES=['Keep your downloaded course files; every lab folder has its own starting workbook.','Keep practising with the IES Academy course materials.']
PROMPTS_RELATIVE=False;PROMPTS_EYEBROW='IES Academy';PROMPTS_TAGLINE='One day · Northstar Water Services · Water-pipe maintenance and service.';PROMPTS_FOOTER='IES Academy'
PROMPTS_DAY_NOTE='<p><b>One day:</b> 09:30–18:30, 7.5 instructional hours: 375 minutes of guided labs (including the agent lab and the group capstone), 55 minutes of concept demonstrations, 20 minutes of briefing and recap, plus lunch and two tea breaks.</p>'
TRAINER='IES Academy Trainer';DAYS=1;DAY_MINUTES=480;INSTRUCTIONAL_MINUTES=450
MODE='Instructor-led, hands-on practical labs';DAILY_TIMING='9:30 am - 6:30 pm (1-hour lunch; two 15-minute tea breaks; 7.5 instructional hours)';DARK_THEME=False
VERSION_HISTORY=[('2.4',VERSION_DATE,'Simple, self-contained labs: short steps with one prompt each, and every lab works directly on the files in its own lab folder (no extra folder, no copying, no dependence on earlier labs); files stay local with no OneDrive upload; new Lab 7 PowerPoint design skill (plain to professional deck); Failure_Mode column and failure-mode Pareto in Labs 5-6; slides on Copilot as the agentic AI interface and on SKILL.md anatomy; Word, PowerPoint and Outlook steps upload the local file with + > Upload images and files (paste as fallback); new slide compares local upload with OneDrive / reference. OneDrive remains only for the Excel Skills folder and Agent Builder knowledge.','IES Academy'),('2.3','18 October 2026','Lab 11 Agent Builder work-order agent; Lab 12 group mini capstone; Copilot interface, AI security and Agent Builder pages; corrected key concepts; built-in @chart-design demo; dashboard with KPI tiles and slicers; lean lab folders; step-by-step prompts page.','IES Academy'),('2.2','14 October 2026','Ten connected labs: account Personalisation, visible .Rules, create/apply Pareto and reporting Skills, custom interactive-dashboard Skill, filters and controlled refresh.','IES Academy'),('2.1','13 October 2026','Water-pipe service scenario; expanded coherent prompts, pure-text Copy buttons, linked PDFs and simple data/PDF labs.','IES Academy'),('1.0','29 July 2026','Previous cross-app scenario; retained in archive.','IES Academy'),('2.0','13 October 2026','Four maintenance topics; eight connected labs, custom Excel/PowerPoint skills, interactive dashboard and management presentation.','IES Academy')]
LEARNING_OUTCOMES=[
'LO1: Integrate Word, Excel, PowerPoint and Outlook Copilot in a coherent maintenance workflow with explicit source grounding and verified prompts.',
'LO2: Distinguish account Personalisation, workbook .Rules and reusable Skills; configure, create, apply and verify Pareto and maintenance-reporting Skills using water-service evidence.',
'LO3: Create and apply a custom interactive-dashboard Skill with verified measures, shared filter scope, editable charts and controlled refresh and rerun tests.',
'LO4: Continue from the dashboard to a professional management presentation, with evidence-based headlines, source notes, rehearsal and a reviewed handoff draft.',
'LO5: Build and test a grounded work-order agent with Agent Builder, then apply the full data-to-decision workflow to your own mock or sanitised data in a group capstone.']
LO_TITLES=['Connected Copilot workflow','Reusable maintenance skills','Interactive dashboard','Professional presentation','Agents and capstone']
ICE_BREAKER=['Your name, role and one maintenance reporting task.','Which app holds the work-order source?','Which date and status definitions determine overdue work?','Check which Copilot buttons and skills menus are available in your assigned apps.']
LAB_NOTE='Northstar Water Services is a fictional water-pipe maintenance and service company. All service hubs, staff and work orders are synthetic. Use the fixed reporting date 2026-09-30; missing facts remain UNKNOWN. Proposals do not change real assignments. Training email drafts are never sent.'
LG_INTRO='This masterclass follows Northstar Water Services, a fictional water-pipe maintenance and service company, from a dirty service-work-order export to a reviewed management decision pack. Work-order IDs, categories, sites, current assignments and status definitions stay consistent across every app. The purpose is to make evidence travel accurately through the workflow, while using Copilot for drafting, analysis, reusable instructions and visual communication.'
LG_INTRO2='Study each topic’s concepts before its connected labs. Topic 2 has five labs; Topics 1, 3 and 4 have two each; Topic 5 has the agent lab and the group mini capstone. Each lab has its own instruction PDF and a lean data folder: the lab workbook and only the templates that lab uses. Copy-ready prompts are on the linked web page, step by step. Every lab is self-contained: work directly on the files in its own data folder, so you can start any lab without finishing the one before. The detailed procedures are here and in labs; the slides teach concepts and show outcomes.'
LG_SETUP=dict(needs=['Assigned Microsoft 365 account with Copilot in Word, Excel, PowerPoint and Outlook; licence and tenant settings checked before class.','Desktop Excel on Windows or Mac (current version) with English display language for Excel custom skills; workbooks stay in the downloaded lab folders, with no OneDrive upload.','The downloaded lab folders; you work directly on the files in each lab’s data folder. All sample data is synthetic.','Copilot skills access in both Excel and PowerPoint. If unavailable, the lab supplies a clearly labelled manual-instruction practice route.'],verify_text='Open one workbook and one Word/PowerPoint template; find each Copilot button. Open a lab workbook from its data folder and confirm Excel Copilot answers on it; in Word Copilot confirm + > Upload images and files can upload it (a local file cannot be found with / or @). Use the app-created custom skills folder rather than guessing a path. Keep Formulas > Calculation Options > Automatic. Never paste account passwords into a prompt.',conventions=['App-labelled prompts run in the named app; a prompt in one app is not automatically visible to another.','Use Chat only for inspection, Plan for reviewed proposals, and Allow editing for authorised workbook changes when these modes are available.','All comparisons use the same source table, reporting date and filter scope. Missing values remain UNKNOWN; zero closed denominator is N/A.'])
S_PERSONAL='https://support.microsoft.com/en-us/excel/copilot/copilot-in-excel-personalization'
S_RULES='https://support.microsoft.com/en-us/excel/copilot/copilot-in-excel-rules'
S_EXCEL='https://support.microsoft.com/en-us/excel/copilot/copilot-in-excel-skills'
S_PPT='https://support.microsoft.com/en-us/powerpoint/copilot/copilot-in-powerpoint-skills'
S_WORD='https://support.microsoft.com/en-gb/word/copilot/draft-and-add-content-with-copilot-in-word'
S_FILES='https://support.microsoft.com/en-us/microsoft-365-copilot/file-formats-supported-by-microsoft-365-copilot'
S_DASH='https://support.microsoft.com/en-us/excel/create-and-share-a-dashboard-with-excel-and-microsoft-groups'
S_SLICER='https://support.microsoft.com/en-us/excel/get-started/use-slicers-to-filter-data'
S_SLIDE='https://support.microsoft.com/en-us/powerpoint/copilot/add-a-slide-from-a-file-with-copilot-in-powerpoint'
S_BUILTIN='https://support.microsoft.com/en-us/excel/copilot/copilot-in-excel-built-in-skills'
S_OVERVIEW='https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-overview'
S_PRIVACY='https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-privacy'
S_PROMPTS='https://support.microsoft.com/en-us/microsoft-365-copilot/get-started-writing-prompts-in-microsoft-365-copilot'
S_AGENT='https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/agent-builder-build-agents'
S_AGENT_KNOW='https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/agent-builder-add-knowledge'
S_AGENT_SKILLS='https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/declarative-agent-skills'
def sec(lab,title,definition,why,how,example,uses,avoids,sources):
 return dict(lab=lab,title=title,definition=definition,why=why,how=how,example=example,use_when=uses,avoid_when=avoids,sources=sources)
SECTIONS=[
sec(1,'Grounding Across Microsoft 365',
'Grounding gives an AI request the specific evidence it should use. A work-grounded Copilot experience can use permitted organisational content; a file-grounded request uses selected files or supplied text. Neither makes an inaccessible file available merely because its local path is typed into a prompt. Word, Excel, PowerPoint and Outlook have different current-document and file-reference experiences. Treat each app handoff as a new grounding task.',
'A maintenance figure can be correct in Excel yet become wrong in an email when the source, reporting date or filter scope changes. Explicit grounding prevents unsupported owner assignments, stale reporting periods and invented approvals from entering the pack. A Copilot response is a draft or hypothesis until the underlying evidence has been checked.',
['Identify the authoritative work-order table.','Provide goal, context, source and expected output.','Review against the named evidence.','Pass a verified snapshot to the next app.'],
['Excel analyses tblWorkOrders; Word receives the checked summary.','PowerPoint receives the reviewed Word brief; Outlook receives the same checked values.','An Excel chat transcript is not an automatic PowerPoint data source.'],
['The source is accessible and the output has an explicit audience.'],['The prompt assumes access to another app chat or local path.'],[S_FILES,S_WORD]),
sec(1,'Work-Order Grain and Reporting Measures',
'A row represents one work order, identified by Work_Order_ID. Site, job category, priority, status and current assignment are dimensions used to group or filter records. Measures are defined calculations. The source is a snapshot at 30 September 2026: current backlog excludes Closed and Cancelled; overdue backlog also has a Due_Date before that date. Closed orders are counted separately from jobs still in the queue.',
'An exact duplicated export row changes counts and cost without representing new work. Normalising a category spelling must not change the business meaning or assign a missing owner. Named Excel tables and structured references let formulas expand when legitimate new rows are appended. Preserve the raw export so a cleaning decision can be traced.',
['Define one ID per work order.','Find exact repeated export records.','Standardise labels without inventing facts.','Reconcile cleaned counts and cost.'],
['122 raw rows contain 120 distinct work-order IDs.','Total = Closed + Cancelled + Backlog after exact duplicate removal.','Due on 30 September is not overdue at the 30 September snapshot.'],
['You have consistent IDs and a fixed reporting date.'],['Duplicate IDs contain conflicting records or reporting scope is unknown.'],[S_DASH]),
sec(2,'Prompts and Verified App Handoffs',
'A useful prompt combines the intended goal, operational context, named source and output expectations. The handoff object is a verified artifact, such as a Word brief with a checked metric table and source links. It is not an assumption that another app can remember the preceding conversation. For maintenance, expectations should specify exact dates, status vocabulary, current versus proposed assignments and missing-value behaviour.',
'The same number may have different meaning when a chart counts all work orders while an email calls it open backlog. A cross-app evidence register records the claim, value, source table, filter scope and date. This provides a small reproducible contract for each output and lets a reviewer identify a mismatch before it becomes a management decision.',
['Write the goal and audience.','Upload the local file or paste the verified source.','Specify definitions and missing-value behaviour.','Reconcile the returned claims.'],
['Goal: draft a maintenance update for the operations manager.','Source: reviewed Northstar operations brief, all filters All, 30 September.','Expectation: label assignment suggestions as proposals and leave unknown approvals UNKNOWN.'],
['A reviewed brief can be selected or its checked text pasted.'],['Only an unverified summary is available.'],[S_WORD,S_SLIDE,S_FILES]),
sec(2,'Outlook Drafting and Operational Decisions',
'Copilot can help structure a draft email from supplied context. A synthetic text thread is quoted context, not a live Outlook conversation; the course explicitly uses it that way. The writer remains responsible for recipients, claims, attachments, tone and the distinction between a proposed action and an approved instruction. Saving a draft does not send it or authorise a work-order change.',
'An apparently routine update can accidentally promise technician reassignment or imply that a manager approved a recovery plan. Current assignment is recorded data; proposed assignment is a separate planning output. Available hours are one input to planning, not evidence of approval or guaranteed productivity. The final email should request the decision rather than claim it has happened.',
['Provide the synthetic thread and checked facts.','Draft a concise update.','Review recipients, facts and action wording.','Save the unsent draft and evidence.'],
['Current owner blank; proposed owner Aisha remains unapproved.','A draft addressed to example.invalid is a training artifact.','The handoff says decision requested, not decision approved.'],
['You can check the evidence and review the draft before use.'],['The task would imply a real approval or send without review.'],[S_FILES]),
sec(3,'Skills, Prompts and Workbook Rules',
'A prompt is one request. A custom skill is a reusable set of instructions that tells Copilot when and how to perform a recurring task. SKILL.md contains required YAML name and description followed by the instructions. Each skill needs its own folder with a matching name. Workbook-specific rules describe constraints for one workbook; a skill can carry the same maintenance process across repeated reports and supported apps.',
'The skill makes stable definitions and review boundaries reusable: backlog excludes two terminal statuses, overdue uses a fixed date, missing owners stay missing and output reruns do not duplicate sheets. It does not supply absent work-order data or turn an unsupported app feature into an available one. Skill availability must be verified separately in the app where it will run.',
['Identify a recurring task.','Separate stable rules from current inputs.','Write name, description and instructions.','Install, invoke and inspect the result.'],
['maintenance-reporting contains definitions and output boundaries.','Each request still supplies this month’s source, date and scope.','Native skill use and pasted manual instructions are recorded differently.'],
['The same reporting method recurs and can be tested.'],['Inputs or desired behaviour are still undefined.'],[S_EXCEL,S_PPT]),
sec(3,'Custom Skill Discovery in Each App',
'Excel uses its Manage plugins & skills interface and an app-created OneDrive skills folder. PowerPoint uses Choose skills and Manage skills with an Add skill/upload route or its own custom skills folder. The app UI resolves the supported folder; a guessed universal path is unreliable. Refresh and enable the skill, then verify the exact name in each app before invoking it by @mention or the menu.',
'Folder-name/frontmatter mismatches, an extra .txt extension, unavailable licence features and disabled skills can all prevent discovery. A web Copilot authoring conversation can produce the complete Markdown text, but the learner still saves, installs and tests it. Excel cannot log the web chat automatically. Clear installation evidence prevents confusing a manually pasted policy with a native reusable skill.',
['Save complete UTF-8 SKILL.md.','Use the app-created skills location.','Refresh and verify the matching name.','Run and record a smoke test.'],
['Folder maintenance-reporting matches YAML name maintenance-reporting.','Excel and PowerPoint both show the skill before native invocation.','If a menu is absent, manual practice is labelled feature unavailable.'],
['The app exposes its supported skill installation controls.'],['A missing menu is being treated as successful installation.'],[S_EXCEL,S_PPT]),
sec(4,'Repeatability and Safe Skill Reruns',
'Repeatability means the same verified inputs and method yield equivalent business measures and a controlled output structure. A safe rerun preserves source IDs, statuses, assignments and unrelated sheets. It creates or replaces only explicitly named outputs after review. The concept is similar to idempotence: rerunning should not append duplicate summaries, inflate totals or silently destroy a learner’s unrelated work.',
'Reporting skills may be used every week or month, so uncontrolled output accumulation quickly creates conflicting summaries. An input guard asks for missing data; a replacement guard identifies the output to change. Test those guards using a copy and compare row count, sums, sheet inventory and output measures before and after, rather than relying on Copilot saying it was careful.',
['Capture the source fingerprint and outputs.','Request a reviewed rerun plan.','Replace only named output areas.','Compare source and measures again.'],
['120 source IDs remain 120 after rerunning Maintenance_Summary.','Missing report date causes a clarification request, not invented numbers.','A second output sheet is a defect when replacement was requested.'],
['Named output boundaries and reconciliation checks exist.'],['The skill can overwrite source rows or unrelated sheets.'],[S_EXCEL,S_PPT]),
sec(4,'Assignment Proposals and Capacity Evidence',
'Assignment planning combines the work category, existing owner, estimated hours, technician primary category and available hours. These inputs help generate a proposal; they do not prove complete operational suitability, approved schedules or safety authorisation. Keep Current_Assigned_To separate from Proposed_Assigned_To and use an explicit manager-decision field. Missing evidence is UNKNOWN, not a confident allocation.',
'The same skill can improve Excel analysis and PowerPoint wording by preserving this boundary. Excel shows category/capacity checks and assumptions in a proposals sheet; PowerPoint explains the findings and requests a decision. A polished visual must not conceal uncertain capacity or make the proposed owner look like the current owner.',
['Identify unassigned backlog.','Compare category and available hours.','Record the proposal and assumptions.','Request the manager decision.'],
['Unassigned work is counted only within nonterminal statuses.','Available hours minus proposed effort is a planning check.','The source Assigned_To stays unchanged until a real authorised operational update.'],
['A manager can review the proposal and missing constraints.'],['The report claims automatic approval or verified safety qualification.'],[S_EXCEL,S_PPT]),
sec(5,'Dashboard Measures and Denominators',
'A dashboard measure needs a business definition, numerator, denominator where relevant, date rule and filter scope. Total orders describes the selected portfolio. Backlog is the selected nonterminal work. Overdue is a subset of backlog. On-time closure rate describes Closed rows only: closed on or before their due date divided by Closed rows. Recorded cost sums selected Cost_SGD; it is not a budget variance or inferred savings.',
'Changing the denominator can make an attractive rate meaningless. If the selected data contains no Closed rows, the on-time rate is N/A because it is undefined; a displayed 0% would falsely suggest failed delivery. A Measures dictionary and independent control sheet make the definitions inspectable. A fixed reporting date gives reproducible comparisons, while TODAY would change the snapshot over time.',
['Define source fields and scope.','Compute count and denominator.','Handle empty selections explicitly.','Reconcile against controls.'],
['Closed-only rate is different from closed/total completion share.','A due-today backlog item is not overdue under a strict before-date rule.','All selected status/chart counts reconcile to total selected work orders.'],
['Measures have agreed definitions and evidence.'],['A zero denominator is being represented as a measured 0%.'],[S_DASH]),
sec(5,'Visual Dashboard Design for Maintenance',
'A dashboard should make an operational decision easier. KPI cards summarise magnitude; bar charts compare sites, categories or status counts. Labels, units and source/date context define what each visual means. Site backlog and total orders by site answer different questions and must have different names. Use a line chart for a genuine ordered time series, not unordered site names.',
'Consistent chart scales, short labels, whitespace and limited accents help a manager compare the work queue quickly. Colour alone is insufficient to distinguish statuses. A category count is evidence of frequency, not a causal diagnosis; a busy site is not necessarily performing badly. Choose the visual based on the question and include the limitation that prevents overinterpretation.',
['Name the maintenance decision.','Choose the measure and comparison.','Use an appropriate labelled chart.','Check meaning and readability.'],
['Status count chart shows the portfolio mix.','Site backlog chart excludes Closed and Cancelled.','A category count does not establish the root cause of overdue jobs.'],
['The visual has a clear audience and question.'],['Decorative charts hide an ambiguous metric.'],[S_DASH]),
sec(6,'One Filter Scope for Every Visual',
'Interactive means a learner-controlled selection changes the evidence shown. This course’s portable route uses four dropdowns and formula measures with AND logic. All bypasses one dimension only. Every KPI and chart uses the same selected rows. Optional slicers filter connected PivotTables; they do not automatically alter unrelated formulas or every table on the sheet. PivotTables sharing a slicer need the same source.',
'A dashboard can appear interactive while only one chart changes. Test a single-site selection, a combined category/owner selection and an empty selection. Check the displayed scope and compare every chart total with the selected total. Worksheet AutoFilter and formula-selector filters are different mechanisms; hiding source rows does not prove that formulas have changed scope.',
['Define the selector cells.','Apply the same AND mask everywhere.','Test each control and edge case.','Reconcile selected chart and KPI totals.'],
['Woodlands Hub plus All in other selectors isolates that site.','Status New gives zero Closed and N/A closure rate.','A slicer must connect to every intended PivotTable.'],
['All output calculations follow the same scope.'],['A selector only changes a decorative title or one chart.'],[S_SLICER,S_DASH]),
sec(6,'Refresh Tests and Static Snapshots',
'A refresh test deliberately introduces known new records and verifies the expected delta. Table references should expand when rows are appended; PivotTables additionally need a refresh and valid source extent. The course adds two rows in a sandbox copy so the live baseline remains 120 rows. A Word/PDF/PowerPoint snapshot freezes evidence and does not automatically update when the Excel dashboard changes.',
'A correct dashboard today may fail after the next export if formulas reference a fixed cell range. Known delta testing reveals that failure. Preserving a separate baseline prevents a test record from contaminating the management pack. A snapshot should record source, as-at date, filters and version so its claims remain interpretable after the workbook is refreshed.',
['Save an isolated sandbox copy.','Append known unique test rows.','Recalculate and verify expected deltas.','Handoff the untouched baseline.'],
['Two test rows increase total by2 and recorded cost byS$400.','Only one new row adds to backlog/overdue; the other adds to on-time Closed.','The final deck uses the untouched 120-row baseline, not the test copy.'],
['A predictable change can be checked independently.'],['Test rows are being mixed into the report without disclosure.'],[S_DASH]),
sec(7,'From Dashboard Evidence to a Decision Story',
'A management presentation transforms evidence into a sequence of observations, implications, proposed actions and a decision request. Each slide needs one defensible headline and a register entry linking the claim to its measure, source, reporting date and filter scope. A chart contains data; the headline interprets it. That interpretation must stay within what the data supports.',
'Copilot can accelerate outlines and drafting, but a persuasive invented conclusion is still wrong. Before generating the deck, use Word to organise an eight-slide brief with a supporting chart and limitation for each claim. This explicit bridge makes the Excel-to-PowerPoint handoff reliable and avoids assuming a workbook can be used by every presentation-generation mode.',
['Freeze the verified dashboard snapshot.','Register each proposed claim.','Write a reviewed Word brief.','Generate and reconcile the deck.'],
['Backlog by site supports prioritisation, not a proven cause.','Available-hours evidence supports a capacity discussion, not confirmed allocation.','The final slide asks management to decide on a proposed plan.'],
['Every headline has a checked measure and clear scope.'],['The story introduces savings, causes or approvals absent from evidence.'],[S_WORD,S_SLIDE,S_FILES]),
sec(7,'Charts, Templates and Source Provenance',
'A template supplies slide layouts, typography and colours; it does not supply correct facts. PowerPoint Copilot can draft slides from selected supported files. Reviewed Word briefs are a reliable narrative input for this course. Excel charts may be embedded for editing or pasted as images; both are copies of a reporting state unless a separate supported link is deliberately configured and tested.',
'Approximate AI-generated charts can contradict source values while looking plausible. Replace them with reviewed charts or verified tables and keep source/date notes. Distinguish all-work-order counts from backlog-only counts. A professional presentation uses consistent units and chart semantics, not just a consistent palette.',
['Upload or paste the reviewed brief.','Apply the existing template.','Insert verified charts or tables.','Record source and snapshot scope.'],
['An editable embedded chart remains a copy rather than a tested live link.','An image is labelled as a snapshot at 30 September.','All eight slides use one reviewed baseline.'],
['The chart object or image can be verified against the register.'],['A visual is assumed accurate because Copilot produced it.'],[S_SLIDE,S_FILES]),
sec(8,'Professional Refinement and Rehearsal',
'Refinement improves the clarity of the existing evidence without changing its meaning. Claim-led titles, short visible text, readable axes, consistent chart styles and concise speaker notes help an audience understand the maintenance decision. Rehearsal tests whether the audience can identify the reporting scope, the key finding and the decision required. It produces observed feedback, not a fabricated checklist completion.',
'A well-designed deck can still fail when the speaker’s notes contain different numbers or a proposal is spoken as an approved action. Review notes as part of the evidence pack and inspect the exported PDF at presentation size. Exporting can alter layout or font rendering, so the PDF must be opened and checked rather than assumed identical to the source.',
['Audit the draft against evidence.','Apply reviewed design changes.','Rehearse and record actual feedback.','Inspect PPTX and exported PDF.'],
['One message per slide; chart labels remain readable.','A 45-second note explains evidence and limitation.','Partner feedback leads to one recorded revision.'],
['The message and decision can be understood quickly.'],['Polish hides an unsupported claim or unreadable chart.'],[S_PPT]),
sec(8,'Reviewed Handoff and Artifact Lifecycle',
'The final pack contains an interactive Excel dashboard, a fixed reporting brief, a static PowerPoint/PDF snapshot, the custom skill and a reviewed communication draft. These artifacts have different lifecycles. The dashboard may refresh; the skill defines a method; the presentation records a dated claim set. Link each file accurately and preserve the evidence register so a later reader knows what was reviewed.',
'Updating one artifact without the others creates inconsistent communication. Reconcile the final pack and explicitly state that actions remain proposed and the email remains a draft. Versioned source and archived superseded artifacts let the team revisit an earlier report without confusing it with the current one. A missing link is UNKNOWN until an actual accessible link is supplied.',
['Reconcile final artifacts.','Record actual filenames and links.','Review the handoff draft.','Preserve the dated snapshot and skill.'],
['PowerPoint and PDF both show eight slides/pages from the same baseline.','Outlook does not claim a missing attachment was sent.','The next update reruns the method with new verified inputs.'],
['Current versions and review evidence are explicit.'],['A refreshed dashboard is assumed to rewrite an old presentation.'],[S_FILES,S_PPT])]

# New lab numbers retain the existing evidence chain while expanding Topic 2.
LAB_TOPIC={1:1,2:1,3:2,4:2,5:2,6:2,7:3,8:3,9:4,10:4,11:5,12:5}
for section in SECTIONS:section['lab']={1:1,2:2,3:6,4:6,5:7,6:8,7:9,8:10}[section['lab']]
SECTIONS[4:4]=[
sec(3,'Account Personalisation and Specific Requests',
'Excel Copilot Personalisation stores account-level preferences for display, writing style and formula conventions. Saved preferences apply to subsequent prompts across workbooks and devices using that account. They are not stored in or shared with a workbook. A specific task instruction can supersede a preference for that task.',
'Consistent S$ display and short explanations reduce repetitive requests without changing numeric values. Preferences must not replace the workbook’s business definitions. A private before-state note lets learners restore their previous account settings after the controlled exercise.',
['Choose recurring display preferences.','Save them to the account.','Compare two workbook outputs.','Test a specific request and restore.'],
['A value of 35827.5 can display as S$35,827.50 or S$35,827.5000.','Changing a number format does not change its numeric value.','Another user opening the file does not receive your account preferences.'],
['The preference applies to many reports on your account.'],['The instruction is a workbook-specific business rule or source change.'],[S_PERSONAL]),
sec(4,'Visible Workbook .Rules and Formula Results',
'A visible worksheet named exactly .Rules, including the dot, supplies workbook-specific Copilot instructions in column A. Use one idea per cell and English for fully supported behaviour. The sheet travels with a copied workbook. Rules provide guidance for Copilot; they do not enforce formulas, permissions or security controls.',
'The workbook can carry stable scope, status, cost-display and preservation instructions alongside the source. A formula cell may supply a reporting-date instruction: Copilot reads its recalculated result on the next request. That does not automatically recalculate or update every AI-created output.',
['Name the visible sheet exactly .Rules.','Place one instruction per column-A cell.','Recalculate a formula-driven rule.','Check the next output and copied workbook.'],
['The date rule returns Reporting date: 2026-09-30 from Control!B2.','Hidden .Rules is not used; keep the final sheet visible.','No universal precedence among rules, preferences and Skills is assumed.'],
['Conventions belong to this workbook and should travel with it.'],['You need a security boundary or are assuming hidden rules apply.'],[S_RULES,S_PERSONAL,S_EXCEL]),
sec(5,'Pareto Skill: Find the Vital Few Failure Modes',
'A Pareto chart sorts categories from highest to lowest count and adds a cumulative-percentage line. Engineers use it to find the vital few failure modes or root-cause categories that account for most of the work, so improvement effort goes where it matters most. Here each Northstar work order records its Failure_Mode.',
'The water-service-pareto Skill turns the method into reusable instructions: count, sort high to low, add Share % and Cumulative %, chart it and list the categories needed to reach 80%. Counts must reconcile to the source rows. A Pareto shows where work concentrates; the engineer still confirms the root cause on site before acting.',
['Choose the table and the column to analyse.','Count and sort from highest to lowest.','Add Share % and Cumulative %.','List the vital few that reach 80%.'],
['All 120 work orders: Corrosion 42, Joint seal leak 30, Valve seat wear 22.','These 3 of 8 failure modes cause 78% of the work.','Overdue jobs only: Joint seal leak moves to the top (14 of 50).'],
['You need to decide which failure modes to tackle first.'],['A count is treated as a proven cause without checking on site.'],[S_EXCEL]),
sec(7,'Custom Dashboard Skill as a Reusable Contract',
'water-service-dashboard is a separate custom Skill whose instructions define inputs, six KPI formulas, four shared filter selectors, three editable charts and controlled output boundaries. Visible .Rules carries workbook conventions. The request still supplies the actual source, fixed date and chosen scope. Installing another reporting Skill does not install this dashboard method.',
'A reusable contract makes every KPI and chart obey the same AND filter logic and allows a safe refresh using table references. Input and replacement guards protect the source and existing Pareto evidence. Rerun evidence includes sheet/chart inventory and source checks, not just a claim that the Skill ran successfully.',
['Author and review the complete SKILL.md.','Install and verify the dashboard name.','Invoke a plan and build the reviewed output.','Test common filters, append refresh and reruns.'],
['Dashboard B2:B5 select site, category, status and owner.','B7:B12 and all chart summaries use the identical selected rows.','A 122-row sandbox is separate from the untouched 120-row baseline.'],
['A recurring dashboard needs consistent measures and review guards.'],['Tenant Skill access or source preservation is being assumed.'],[S_EXCEL,S_DASH])]


# ---- The big picture (deck opening): Copilot is the agentic AI interface; the Office apps are its tools.
COPILOT_HUB=dict(title='Copilot: One Agentic AI Interface, Four Tools',kicker='THE BIG PICTURE',
  center=('Microsoft 365 Copilot','Agentic AI interface: understands your request, plans the steps and acts in each app'),
  apps=[('Excel','Cleans data, writes formulas, builds charts and dashboards.','217346'),
        ('Word','Drafts and checks reports and briefs from your files.','2B579A'),
        ('PowerPoint','Builds and redesigns decks from a brief.','C43E1C'),
        ('Outlook','Drafts emails and replies for you to review.','0F6CBD')],
  flow='You ask in plain English   →   Copilot plans and acts in the app   →   You review and approve')
S_PPT_SKILLS='https://support.microsoft.com/en-us/powerpoint/copilot/copilot-in-powerpoint-skills'

# ---- IES v2.3 concept pages -------------------------------------------------
def _with_tiles(section, title, items, cols=2, kicker='KEY POINTS', size=15):
    section['tiles'] = dict(title=title, items=items, cols=cols, kicker=kicker, size=size); return section
INTERFACE = _with_tiles(sec(1,'The Microsoft 365 Copilot Interface',
'Copilot in the browser and in each Office app shares one set of controls. Microsoft Copilot (copilot.cloud.microsoft) and the Copilot pane in Word, Excel, PowerPoint and Outlook offer a model selector, new chat and chat history, a + menu to reference files and choose skills, settings for Personalization and Manage plugins & skills, and in Excel a mode switch between Chat only, Plan and Allow editing. Agents & Skills in the left pane opens your agents and Agent Builder.',
'Knowing where each control lives lets you choose how much reasoning, context and authority Copilot gets for a task. A new chat starts a clean context; a reference adds a specific file; a mode decides whether Copilot only answers, proposes a plan or edits the file. The green shield confirms enterprise data protection for work data.',
['Pick the model and start a new chat.','Reference the file or choose a skill.','Choose Chat only, Plan or Allow editing.','Review history, settings and skills.'],
['Auto is the default model; Think deeper suits multi-step analysis.','Local file: upload it with +. OneDrive file: reference it with /.','Chat only for inspection, Plan before edits, Allow editing to apply.'],
['You need to control context, reasoning depth or edit permissions.'],['You assume a chat in one app is visible in another.'],[S_OVERVIEW,S_EXCEL]),
'The Microsoft 365 Copilot Interface',[
('Model selection','Auto, Quick response or Think deeper; Auto chooses for you.'),
('New chat','Starts a clean conversation; each chat is its own context.'),
('History','Earlier chats in the left pane to reopen or continue.'),
('Mode','Excel/Word: Chat only, Plan or Allow editing (Edit).'),
('+ Add content','Upload a local file, / a OneDrive file, or choose a skill.'),
('Personalisation','Settings (...) > Personalization: your account preferences.'),
('Skills & plugins','Settings (...) > Manage plugins & skills; call one with @.'),
('Agents','Agents & Skills in the left pane; build with Agent Builder.'),
('Data protection','The green shield shows enterprise data protection is on.')],cols=3,kicker='INTERFACE',size=13)
INTERFACE['compare']=dict(title='Two Ways to Give Copilot a File: Local or OneDrive',
  headers=['Aspect','Local file (this course)','OneDrive / SharePoint file'],rows=[
  ('Where it lives','Your computer, e.g. the downloaded lab folder.','OneDrive or SharePoint in Microsoft 365.'),
  ('In Excel','Desktop Excel Copilot works on the open workbook; no upload needed.','Excel desktop or web; AutoSave keeps the cloud copy current.'),
  ('In Word, PowerPoint, Outlook','+ > Upload images and files, then pick the file on your device.','Type / or use + > Attach cloud files and pick the file.'),
  ('/ or @ mention','Not available: / lists only cloud files; @ calls skills and agents.','/ lists the OneDrive and SharePoint files you can open.'),
  ('After you edit','The upload is a copy: upload again after changing the file.','The reference reads the latest saved cloud version.'),
  ('Use it for','Training labs and files you do not want in the cloud.','Shared team files, agent knowledge and folder references.')])
AI_SECURITY = _with_tiles(sec(2,'AI Security: Five Principles',
'AI security is the set of habits and controls that keep data, decisions and systems safe when people work with AI assistants and agents. Five principles apply to every Copilot task in this course: data control, permission control, human in the loop, traceability, and using a well-tested model rather than the newest one for important work.',
'Copilot only surfaces data a user can already access and does not use prompts to train its foundation models, but people can still overshare, give an agent too much access, accept an unchecked draft or lose track of what was used. The principles turn those risks into checks you can perform before work leaves your hands.',
['Share only the data the task needs.','Limit access for people, agents and skills.','Review and approve before anything takes effect.','Log sources, prompts, versions and checks.'],
['Use synthetic or sanitised data in training and demos.','An agent gets Can chat access, not Can edit, unless needed.','A Copilot email stays a draft until a person reviews it.'],
['The output could reach other people, systems or decisions.'],['Confidential data is pasted into an unapproved tool or a draft is sent unchecked.'],[S_PRIVACY,S_OVERVIEW]),
'5 Principles of AI Security',[
('Data control','Share only what the task needs; use synthetic or sanitised data.'),
('Permission control','Least privilege for files, agents, skills and sharing.'),
('Human in the loop','Plan, review and approve before edits, emails or decisions.'),
('Traceability','Log prompts, sources, versions and checks for every output.'),
('Well-tested models','Prefer proven, approved models over the newest release.')],cols=3,kicker='AI SECURITY',size=14)
BUILTIN = sec(5,'Built-in and Custom Skills',
'Copilot in Excel ships with built-in skills you call with @, such as @chart-design for charts. @chart-design applies the Excel design team’s chart guidance and @theme-design handles workbook formatting. Built-in skills are turned on in Settings (...) > Manage plugins & skills; chart-design sits under Visualization and is off by default. A custom skill is your own SKILL.md for a method Excel does not know, such as the water-service Pareto or dashboard.',
'Start with a built-in skill when the task is generic, such as making a clear chart. Write a custom skill when the method carries your own rules: which rows count, how ties sort, which outputs may be replaced and which checks must pass. Both are reusable; only the custom one knows Northstar.',
['Turn on chart-design under Visualization.','Call @chart-design for a generic chart.','Spot the rules it cannot know.','Write a custom SKILL.md for those rules.'],
['@chart-design draws a clean bar chart of work orders by failure mode.','It does not add the cumulative line or the vital-few list.','water-service-pareto adds both, the same way every time.'],
['A generic design task or your own repeatable method.'],['You expect a built-in skill to know your business rules.'],[S_BUILTIN,S_EXCEL])
AGENT_BUILDER = _with_tiles(sec(11,'What Is Agent Builder?',
'Agent Builder is the no-code tool in Microsoft Copilot for creating your own specialist agent. An agent is a focused version of Copilot with its own name, instructions, knowledge, skills, capabilities and starter prompts. You open it from Agents & Skills > New agent, describe the agent in plain English or fill in Configure, test it in Try it, then create and share it.',
'An agent packages a recurring job, here answering work-order questions, so colleagues get consistent, grounded and bounded answers without rewriting prompts. Its answers are only as good as its instructions and knowledge, and it inherits the same permission and licensing rules as Copilot. Skills in agents are a preview that cannot yet be combined with uploaded files.',
['Describe the agent’s job.','Configure instructions and knowledge.','Add a Skill and starter prompts.','Test, create and share safely.'],
['Knowledge: the handbook and the clean work-order file from OneDrive.','Skill: work-order-qa sets definitions, citations and UNKNOWN rules.','Boundary test: the agent refuses to approve a reassignment.'],
['A recurring question set needs consistent, grounded answers.'],['The agent would need to change records or act without review.'],[S_AGENT,S_AGENT_KNOW,S_AGENT_SKILLS]),
'Agent Builder: What You Configure',[
('Describe','Chat with Agent Builder to draft the agent in plain English.'),
('Name & description','What the agent is for; shown to people you share it with.'),
('Instructions','Role, sources, definitions, tone and boundaries (8,000 characters).'),
('Knowledge','OneDrive/SharePoint files, uploads or websites it can search.'),
('Skills','Reusable SKILL.md packages uploaded as a .zip (preview).'),
('Try it & share','Test, select Create, then share as Can chat or Can edit.')],cols=3,kicker='AGENT BUILDER',size=14)
CAPSTONE = sec(12,'Mini Capstone: From Your Data to a Decision',
'The mini capstone applies the whole course to a dataset your group chooses: safe data, workbook .Rules, a dashboard Skill, an interactive dashboard, a verified decision deck and a short showcase. Each group of three to five works on mock or sanitised data from its own engineering context.',
'Repeating the workflow on unfamiliar data shows what transfers: definitions written as rules, reusable skills, independent checks and a decision-focused story. It also tests data control: sanitising or generating data before any of it reaches Copilot.',
['Choose safe data and roles.','Write .Rules and build with a Skill.','Verify KPIs and slicers.','Build the deck and showcase.'],
['A 150-row synthetic lift-maintenance table replaces real records.','Six KPI tiles reconcile to independent COUNTIFS.','A five-slide deck ends with the decision requested.'],
['You can explain every number from your own data.'],['The dataset contains personal, customer or confidential information.'],[S_DASH,S_RULES,S_EXCEL])
SECTIONS.insert(0,INTERFACE)
# AI security is the course's closing message (deck: before Thank You; LG: closing section).
CLOSING_TILES=dict(AI_SECURITY['tiles'],kicker='CLOSING MESSAGE')
LG_WRAPUP=dict(title='Closing: 5 Principles of AI Security',intro=AI_SECURITY['definition']+' '+AI_SECURITY['why'],
               sections=[dict(title=t,text=d) for t,d in AI_SECURITY['tiles']['items']]+[dict(title='Put the principles into practice',bullets=AI_SECURITY['how']+AI_SECURITY['example'])])
SECTIONS.insert(next(i for i,x in enumerate(SECTIONS) if x['title'].startswith('Pareto Skill')),BUILTIN)
SECTIONS += [AGENT_BUILDER, CAPSTONE]
SKILL_ANATOMY = _with_tiles(sec(5,'What Is a Skill? Inside SKILL.md',
'A skill is a folder with a SKILL.md file. The file starts with metadata between two --- lines: a name, which must match the folder name, and a description that says when to use the skill. The body below it holds the steps and procedure Copilot follows. The folder can also hold reference files, such as a template, an example or a data list, that the steps point to.',
'Skills are triggered on demand: Copilot reads a skill only when you call it with @name or your request matches its description, so skills do not crowd every chat. Write a method once, install it once, and it runs the same way in every file. Excel and PowerPoint both use this format.',
['Name the skill and describe when to use it.','Write the steps, rules and checks.','Add reference files to the folder if needed.','Install it, then call it with @name.'],
['name: water-service-pareto (the same as its folder name).','description: Use when I ask for a Pareto chart or failure-mode analysis.','Steps: count, sort high to low, add Cumulative %, list the vital few.'],
['You repeat the same method in many files.'],['The task is a one-off question a single prompt can answer.'],[S_EXCEL,S_PPT_SKILLS]),
'Anatomy of a Skill',[
('Triggered on demand','Loaded only when you @mention it or your request matches its description.'),
('Metadata','Between --- lines: name (same as the folder) and description (when to use it).'),
('Steps and procedure','The body: numbered steps, rules and the checks Copilot must run.'),
('Reference files','The folder can also hold templates, examples or data the steps refer to.'),
('One folder per skill','skills > pareto-chart > SKILL.md, plus any reference files.'),
('Install once, reuse','Works in every file; turn it on or off in Manage skills.')],cols=3,kicker='SKILLS',size=14)
SECTIONS.insert(next(i for i,x in enumerate(SECTIONS) if x is BUILTIN),SKILL_ANATOMY)
# A new Lab 7 (PowerPoint design skill) follows Lab 6: later labs move up by one.
for section in SECTIONS:
    if section['lab']>=7: section['lab']+=1
LAB_TOPIC={1:1,2:1,3:2,4:2,5:2,6:2,7:2,8:3,9:3,10:4,11:4,12:5,13:5}
SECTIONS.insert(next(i for i,x in enumerate(SECTIONS) if x['lab']>7),_with_tiles(sec(7,'PowerPoint Design Skill: From Plain to Professional',
'A design skill holds your brand rules, fonts, colours, header bar, footer, KPI cards and spacing, as steps Copilot in PowerPoint follows. Called on a plain deck, it redesigns every slide the same way while keeping every slide, number and fact.',
'Most decks start plain: black text, no header, no branding. Restyling slide by slide is slow and inconsistent. A design skill makes a professional look one prompt away and the same for every deck the team produces.',
['Write the brand rules as a SKILL.md.','Add it with + > Choose skills > Manage skills > Add skill.','Call it on a plain deck.','Check every number is unchanged.'],
['Title slide: navy background, white title, teal subtitle.','Content slides: navy header bar, KPI cards, footer with slide number.','Numbers such as 120 work orders and 50 overdue stay the same.'],
['Many decks need the same professional look.'],['The skill is allowed to change numbers or add facts.'],[S_PPT_SKILLS]),
'Northstar Deck Design Rules',[
('Fonts','Segoe UI Semibold titles; Segoe UI body text.'),
('Colours','Navy #1F4E79, blue #2E75B6, teal #2A9D8F, light grey cards.'),
('Header and footer','Navy title bar on every slide; footer with date and slide number.'),
('KPI cards','Big bold numbers with a short label instead of long sentences.'),
('Space','At most 4 short bullets; the same margins on every slide.'),
('Keep the facts','Every slide, number and chart value stays the same.')],cols=3,kicker='DESIGN SKILL',size=14))
_scope=next(x for x in SECTIONS if x['title']=='One Filter Scope for Every Visual')
_scope['definition']=('Interactive means a learner-controlled selection changes the evidence shown. This dashboard has two controls that work together: four dropdowns in B2:B5 and four table slicers. All bypasses one dimension only; selections combine with AND. Every KPI tile and chart summary multiplies the dropdown mask by SUBTOTAL row visibility, so a slicer that hides source rows changes every measure too.')
_scope['why']=('A dashboard can appear interactive while only one chart changes. Test a single-site selection with the dropdown and with the slicer, a combined category/owner selection and an empty selection. Check the scope line and the D3 slicer banner, and compare every chart total with the selected total.')
_scope['example']=['Woodlands Hub in B2 or in the Site slicer gives 24 work orders.','Status New gives zero Closed and an N/A closure rate.','D3 warns while any slicer hides source rows.']
TOPICS=[]
for n,title,subtitle,concepts in [
(1,'Fundamentals of Microsoft 365 Copilot','One verified maintenance workflow across four apps',[('Large language models','Understand your request and generate natural-language answers.'),('Grounding','Answers anchored in your work data: emails, files, meetings.'),('Permissions & privacy','Shows only data you can access; prompts do not train the models.'),('Prompts','State the goal, context, source and expectations.')]),
(2,'Personalisation, .Rules and Skills for Excel','Account preferences, workbook conventions and reusable methods',[('Personalisation','Your account preferences, applied across every workbook.'),('.Rules','Visible column-A instructions that travel with the workbook.'),('Skills','Reusable methods: built-in @chart-design, or your own SKILL.md such as Pareto and dashboard Skills.')]),
(3,'Interactive Dashboards with Custom Skills','Create the Skill, build the dashboard and prove interactions',[('Measures','Six formula KPIs with clear denominators and N/A rules.'),('Visual design','KPI tiles and charts whose titles state the finding.'),('Interactions','Dropdowns and slicers filter every tile and chart.'),('Refresh','Known deltas in an isolated test copy.')]),
(4,'Create a Professional Presentation with PowerPoint Copilot','Continue the dashboard into a decision pack',[('Evidence story','Observation, implication, action and decision.'),('Charts','Reviewed values, provenance and snapshot date.'),('Refinement','Hierarchy, notes and actual rehearsal feedback.'),('Handoff','Reconciled pack and unsent communication.')]),
(5,'Copilot Agents and Mini Capstone','Build a work-order agent, then apply the whole workflow in groups',[('Agent Builder','Create a specialist Copilot agent without code.'),('Knowledge','OneDrive files the agent searches and cites.'),('Instructions & Skills','Role, rules and a reusable work-order Q&A method.'),('Mini capstone','Groups turn safe data into a dashboard and decision deck.')])]:
 TOPICS.append(dict(num=n,code=str(n),title=title,subtitle=subtitle,concepts=concepts,sections=[s for s in SECTIONS if LAB_TOPIC[s['lab']]==n]))
TOPIC_RECAPS={1:[('LO1','Same work-order evidence across four apps.'),('Verify','120 clean IDs and reconciled brief/update/draft.')],2:[('LO2','Personalisation, .Rules, built-in @chart-design, Pareto and reporting Skills tested.'),('Verify','Preserved source plus missing-input and rerun tests.')],3:[('LO3','Six KPI tiles and three charts follow four dropdowns and slicers.'),('Verify','Baseline controls and known refresh deltas.')],4:[('LO4','Eight-slide evidence story and reviewed handoff.'),('Verify','PDF, notes, register and actual rehearsal agree.')],5:[('LO5','A grounded work-order agent and a group dashboard and decision deck.'),('Verify','Agent answers match Control; capstone figures reconcile to the group data.')]}
DAY_THEMES={1:'Maintenance workflow, custom skills, interactive dashboard, management presentation, Copilot agent and group capstone'}
def SCHEDULE(lab_titles):
 from datetime import datetime,timedelta
 blocks=[(10,'admin','Welcome, learning outcomes, app access and Northstar scenario')]
 durations=[30,30,20,20,30,30,30,35,25,25,25,30,45]
 demonstrations={1:(10,1),3:(25,2),8:(10,3),10:(5,4),12:(5,5)}
 for n,d in enumerate(durations,1):
  if n in demonstrations:
   mins,topic=demonstrations[n];blocks.append((mins,'topic',f'Topic {topic}: concepts and demonstration'))
  blocks.append((d,'lab',lab_titles([n])))
  if n in (2,8):blocks.append((15,'break','Tea break'))
  if n==5:blocks.append((60,'lunch','Lunch'))
 blocks.append((10,'recap','LO1-LO5 recap, capstone reflections and questions'))
 now=datetime(2026,10,14,9,30);rows=[]
 for mins,kind,text in blocks:
  end=now+timedelta(minutes=mins);rows.append((now.strftime('%H:%M'),end.strftime('%H:%M'),mins,kind,text));now=end
 assert sum(m for _,_,m,k,_ in rows if k!='lunch')==480
 assert sum(m for _,_,m,k,_ in rows if k not in ('lunch','break'))==450
 return {1:(DAY_THEMES[1],rows)}
GLOSSARY=[('Agent','A specialist Copilot with its own instructions, knowledge and skills.'),('Agent Builder','The Microsoft Copilot tool to describe, configure, test and share an agent.'),('Built-in skill','A ready-made Copilot skill such as @chart-design, turned on in Manage plugins & skills.'),('Slicer','A clickable filter connected to a table; here it filters every dashboard tile and chart.'),('Personalisation','Account-level Copilot preferences; not embedded in a workbook.'),('.Rules','Visible workbook sheet with column-A instructions for Copilot.'),('Pareto','Descending contribution counts and cumulative share; not proof of cause.'),('Grounding','Supplying accessible evidence for the current request.'),('Backlog','Selected work with Status neither Closed nor Cancelled.'),('Overdue','Backlog due strictly before the fixed reporting date.'),('Skill','Reusable instructions in a matching folder and SKILL.md file.'),('Snapshot','A dated, scoped copy of verified evidence.'),('Structured reference','A formula reference to a named Excel table or its columns.'),('Denominator','The population used to calculate a rate.'),('Proposed assignment','A suggested owner awaiting a real manager decision.')]
NEXT_STEPS=dict(title='Your Next Maintenance Report',items=['Use a copy and a new explicit reporting date.','Supply verified source/date/scope and test skill reruns.','Reconcile every claim and decision boundary.'])
LG_GLOSSARY=GLOSSARY
THANK_YOU=dict(title='Thank You',subtitle='Keep your maintenance evidence connected.')

# Full explanations remain in the LG; concise concept cards keep C34 slides readable.
for section in SECTIONS:
    first=section['definition'].split('. ')[0]+'.'
    why=section['why'].split('. ')[0]+'.'
    section['brief']=dict(what=first,why=why,check=section['example'][0],flow=dict(title=section['title'],steps=section['how']),prompts=['Name the source, reporting date and selected scope.','Explain the result using checked evidence.'],verify=section['example'][1:],try_title='Apply the Concept',try_head='PROMPT PRINCIPLES',check_head='EVIDENCE TO CHECK')
