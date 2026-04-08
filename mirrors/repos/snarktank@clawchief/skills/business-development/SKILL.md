---
name: business-development
description: "Manage Untangle business-development and outreach-tracking work using Google Workspace via gws-backed helpers. Use when handling prospecting replies, referral-partner outreach, updating the outreach tracker, logging lead status changes, booking or confirming outreach meetings tied to a lead/prospect, or maintaining the operational record of sales/outreach conversations for Untangle. Prefer this skill over executive-assistant whenever the task touches the outreach tracker, lead status, prospect pipeline, or referral-partner outreach, even if scheduling is involved."
---

# Business Development

Use this skill for outreach and prospect tracking work. Keep it separate from executive-assistant inbox clearing.

## Gotchas

- Read `~/.openclaw/workspace/clawchief/priority-map.md` at the start of every run. Treat it as the source of truth for people/program priority, urgency, and routing.
- Read `~/.openclaw/workspace/clawchief/auto-resolver.md` at the start of every run. Treat it as the source of truth for when to auto-resolve, when to draft, and when to escalate.
- Read `~/.openclaw/skills/task-system-contract/SKILL.md` at the start of every run. Treat it as the shared Todoist contract for follow-ups, blockers, delivery resilience, and no-legacy-markdown behavior.
- Never send business-development emails as R2. Initial outbound prospecting emails should send from `ryan@ryancarson.com` using `python3 ~/.openclaw/workspace/clawchief/scripts/bd_outreach.py`. Do not improvise new outbound copy unless Ryan explicitly asks.
- Do not perform LinkedIn activity as R2. Do not open LinkedIn, search LinkedIn, send connection requests, or check acceptance state unless Ryan explicitly changes this policy.
- Treat this workflow as a CRM operating system, not just a prospect spreadsheet. The Google Sheet is the live source of truth for relationship state, pipeline state, and last-touch / next-step tracking.
- The Google Sheet is the live source of truth; do not treat local prospect files as current state.
- Do not silently broaden default prospecting beyond the current default mix of Connecticut marriage counselors / divorce coaches plus small (1-2 person) Connecticut family-law firms unless Ryan explicitly changes the audience.
- Verify website before adding a new lead unless Ryan explicitly waives that requirement.
- When Ryan gives a lead directly (for example via a business card, screenshot, forwarded contact info, or personal intro), do not use LinkedIn for verification. Preserve an existing LinkedIn URL only if it is already present in the tracker or on the person's own website; otherwise leave the field blank.
- When reviewing a lead's website, actively look for a public email address before leaving `Email` blank. Check the homepage plus likely `Contact`, `About`, `Book`, `Schedule`, or similar pages when they exist.
- Ignore junk matches such as placeholder examples (`user@domain.com`), vendor / telemetry addresses (for example Sentry / Wix internals), or asset-path false positives from scraped HTML.
- If the site shows an obvious typo in the address (for example a duplicated TLD like `.com.com`) and the intended real address is clear from context, normalize it before storing it.
- Track email outreach and LinkedIn outreach as separate fields in the sheet, but do not perform new LinkedIn work as R2.
- Sweep relevant sent mail so unanswered outreach does not disappear.
- If the work touches lead status, pipeline state, or the outreach tracker, this skill owns it even when scheduling is part of the job.

## Current business-development focus

- Current short-term goal: help Untangle get its first 10 paying customers.
- Default outbound prospecting adds *10 new leads per run*, split into two categories:
  1. *5 marriage counselors or divorce coaches* — Connecticut-based practitioners who work with people going through separation or divorce and could plausibly refer clients to Untangle.
  2. *5 family law attorneys from small (1–2 person) firms* — Connecticut-based solo or two-attorney family law offices.
- When Ryan asks for "more contacts" without narrowing the audience, interpret that as a fresh batch of the 5+5 split unless the current conversation overrides it.
- Multi-state practitioners are acceptable if Connecticut is explicitly one of the states they serve.
- Do not add out-of-state prospects by default if Connecticut is not part of their geography, even if they look strong, unless Ryan explicitly asks for a broader geography.
- Prefer individual practitioners or small firms with public contact details and avoid duplicates already present in the outreach tracker.
- Prefer prospect sources that are likely to be high-signal Connecticut lists, including credential or member directories for divorce/coaching organizations and state bar directories when available.
- The Certified Divorce Coach (`CDC`) and Associate Certified Coach (`ACC`) credentials are useful discovery clues; when prospecting, check whether credential/member directories for those designations expose Connecticut practitioners.

## Verification requirements (mandatory for every new lead)

Before adding any prospect to the sheet, all three of these must pass. Drop the prospect if any fail.

1. *Connecticut location* — confirmed from the prospect's own website, not just a third-party directory listing.
2. *Website URL works* — the URL loads successfully (no 404, no dead domain, no parking page).
3. *Email is deliverable* — at minimum the email domain resolves and has valid MX records. Prefer addresses found on the prospect's own site.

If a reliable LinkedIn URL is already available from the person's own website or from an existing tracker row, preserve it. Do not use LinkedIn as a mandatory gating check for the default batch.

## Source of truth

Google Sheet ID: `{{GOOGLE_SHEET_ID}}`

Treat this sheet as the live source of truth for outreach status and relationship context. Do not rely on local `.md` or `.csv` prospect files as the current record.

Current live columns observed in the sheet header (A:R):
`Full name | First | Last | Role | Website | Email | Phone | Location | Email sent | LI sent | LI accepted | Meeting booked | LinkedIn | Ryan's Notes | R2's Notes | Date added | Partner link | Status`

Interpretation:
- `Phone` is now part of the live schema and should be preserved when present.
- `R2's Notes` is the main relationship-history field for operational context.
- `Status` should hold the current pipeline state, not just ad hoc labels.

Preferred status vocabulary going forward:
- `Research only`
- `Ready for Ryan outreach`
- `Email sent by Ryan`
- `LinkedIn sent`
- `Waiting for reply`
- `Positive reply`
- `Scheduling`
- `Meeting booked`
- `Met`
- `Active partner`
- `Not a fit`
- `Closed`
- `Needs cleanup`

Rule: when a relationship changes state, update both `R2's Notes` and `Status` in the same turn whenever practical.
For the default auto-send prospecting batch, prefer `Email sent` = `Yes` and `Status` = `Waiting for reply` once the initial email has actually gone out.

## When to update it

Update the sheet every time outreach state changes.

That includes when you:

- Ryan actually sends an outreach email
- Ryan explicitly reports a LinkedIn outreach or acceptance state change that should be logged
- get any meaningful reply
- ask for a meeting
- book, confirm, reschedule, or cancel a meeting
- record a decline / not-a-fit outcome
- learn a follow-up or next-step detail worth preserving

Do this before you mark the message handled.

Treat tracker updates as mandatory, not optional cleanup.

## Todoist follow-through

Tracker state and task state are different things.

Use the sheet as the CRM source of truth, and use Todoist for the live reminder / follow-up queue.

Rules:

- After every meaningful inbound partner / referral / prospect reply, classify the thread through the priority map before deciding whether a follow-up task is needed.
- If future work remains for Ryan or R2, create or update the Todoist follow-up task in the same turn.
- After each successful initial outreach email, create or update a Ryan Todoist follow-up task for that contact due 3 days later.
- Put partner / referral relationship work in the matching priority-map program section when clear. Default to `Business development partnerships` for partner / referral workflows and use `First 10 paying customers` only when the thread is directly about a live customer, pilot, or deal motion.
- Use stable metadata keys such as `partner-followup-<slug>` or `bd-blocker-<slug>` so repeated sweeps update one task instead of duplicating it.
- If a batch is blocked because of verification, missing public email, or tracker cleanup work, create the blocker / review task in Todoist instead of leaving the state only in notes or legacy markdown.
- If the sheet is inaccessible or the live header row does not match expectations, stop blind writes and apply the blocker rule from `~/.openclaw/skills/task-system-contract/SKILL.md`.

Example initial-outreach follow-up task:

```bash
python3 ~/.openclaw/workspace/clawchief/scripts/todoist_cli.py upsert-task \
  --content "Follow up with Jane about Untangle outreach" \
  --owner ryan \
  --section "Business development partnerships" \
  --priority 2 \
  --due-date 2026-04-11 \
  --metadata-key bd-initial-followup-jane-name-example-com \
  --meta program="Business development partnerships" \
  --meta source=initial_outreach \
  --meta kind=bd_initial_followup \
  --meta contact_email=name@example.com
```

Example partner follow-up task:

```bash
python3 ~/.openclaw/workspace/clawchief/scripts/todoist_cli.py upsert-task \
  --content "Follow up with Jane Doe on partner reply" \
  --owner r2 \
  --section "Business development partnerships" \
  --priority 2 \
  --due-date 2026-04-08 \
  --metadata-key partner-followup-jane-doe \
  --meta program="Business development partnerships" \
  --meta source=email \
  --meta kind=partner_followup
```

Example business-development blocker task:

```bash
python3 ~/.openclaw/workspace/clawchief/scripts/todoist_cli.py upsert-task \
  --content "Resolve CT prospecting source / verification blocker" \
  --owner r2 \
  --section "Business development partnerships" \
  --priority 2 \
  --due-date 2026-04-08 \
  --metadata-key bd-blocker-ct-source-reset \
  --meta program="Business development partnerships" \
  --meta source=clawchief \
  --meta kind=bd_blocker
```

## Inbound reply operating procedure

When partner / referral emails start coming back, process the inbox and the sheet as one workflow — do not treat them as separate tasks.

1. Use **message-level Gmail search** to find inbound replies, not thread-level search.
2. Review each inbound partner reply thread and identify the current state:
   - positive interest
   - meeting requested / meeting booked
   - decline / not a fit
   - question that needs a response
   - auto-reply / invalid contact / left organization
3. Check whether the person already exists in the `Leads` sheet.
4. Before leaving the thread, inspect **every column** for that row and update what changed:
   - `Full name`
   - `First`
   - `Last`
   - `Role`
   - `Website`
   - `Email`
   - `Location`
   - `Email sent`
   - `LI sent`
   - `LI accepted`
   - `Meeting booked`
   - `LinkedIn`
   - `Ryan's Notes`
   - `R2's Notes`
   - `Date added`
   - `Partner link`
   - `Status`
5. If the person is not already in the sheet, append a new row and populate all columns you can verify from the email, website, or LinkedIn.
6. Put **R2-authored operational notes** in `R2's Notes`, not `Ryan's Notes`.
7. Use `Ryan's Notes` only for notes Ryan explicitly wants preserved there or notes that clearly represent Ryan's own view.
8. Only after the sheet is current should the email be considered handled.
9. If an email response is needed, note the blocker / needed next step for Ryan instead of drafting or sending it yourself.
10. If you book a meeting through Calendly, Google appointment schedules, HubSpot, Acuity, Chili Piper, or any similar scheduler, immediately update the row after the booking succeeds.
11. If any future work remains after the CRM update, create or update the matching Todoist follow-up task before considering the thread done.

Default note patterns:
- positive reply, not booked yet -> note interest + next step needed
- meeting booked -> include the scheduled date/time
- decline -> note the decline clearly
- auto-reply / bad contact -> note what happened and any fallback contact info
- substantive questions -> note the question so the tracker reflects the blocker

Useful message-level Gmail searches:

```bash
python3 ~/.openclaw/workspace/clawchief/scripts/ea_gmail.py search --query 'subject:"Potential partnership" newer_than:30d' --max 25

python3 ~/.openclaw/workspace/clawchief/scripts/ea_gmail.py search --query 'subject:"Saw your work" newer_than:30d' --max 25

python3 ~/.openclaw/workspace/clawchief/scripts/ea_gmail.py search --query 'subject:"Untangle" newer_than:30d' --max 25
```

If Ryan asks to "process the partner replies" or says emails have come in from partners, interpret that as:
- read the inbound reply messages
- update / append the corresponding `Leads` rows
- fill any obvious missing fields worth capturing
- leave the sheet in sync before reporting back

## How to update it

1. Read the relevant email/thread context.
2. Check the current `Leads` rows to see whether the person already exists.
3. If they exist, update the existing row.
4. If they do not exist, append a new row.
5. Capture R2's operational state in `R2's Notes` with a short dated note.
6. Leave `Ryan's Notes` alone unless Ryan explicitly supplied a note for that column.

For this sheet size, inspect the current lead table and header row directly before writing:

```bash
python3 ~/.openclaw/workspace/clawchief/scripts/sheet_helper.py read --spreadsheet {{GOOGLE_SHEET_ID}} --range 'Leads!A:R'
```

Use `sheet_helper.py` for reliable multi-column writes through `gws`. For lead-row writes, prefer `lead-upsert` over raw `update` / `append`; it verifies the live header, matches the intended row deterministically, refuses ambiguous duplicates, preserves untouched columns, and appends note history instead of replacing it blindly. Current expected live column order (18 columns, A:R):
`Full name | First | Last | Role | Website | Email | Phone | Location | Email sent | LI sent | LI accepted | Meeting booked | LinkedIn | Ryan's Notes | R2's Notes | Date added | Partner link | Status`

Before writing, verify the header row still matches. If it drifted, adapt to the live header instead of blindly using stale examples.

For approved initial outreach, use the built-in Ryan templates through:

```bash
python3 ~/.openclaw/workspace/clawchief/scripts/bd_outreach.py render --role 'Marriage counselor' --first-name Jane

python3 ~/.openclaw/workspace/clawchief/scripts/bd_outreach.py send --role 'Family law attorney' --first-name Jane --to name@example.com
```

Template rules:

- `coach_therapist` / divorce coach / therapist / counselor roles -> subject `Saw your work`
- `attorney` / family-law attorney roles -> subject `New divorce assistant for CT residents just launched`
- all initial outreach sends from `ryan@ryancarson.com`
- the signature must render `Untangle` as a clickable link to `https://untangle.us`
- both default templates cc `r2@untangle.us`

If the header row cannot be verified or the sheet read fails:

- do not append or update rows blindly
- create or update a Todoist blocker task with a stable key such as `bd-blocker-sheet-schema` using the shared task-system contract
- report the schema/access problem plainly in the run summary

```bash
python3 ~/.openclaw/workspace/clawchief/scripts/sheet_helper.py lead-upsert \
  --spreadsheet {{GOOGLE_SHEET_ID}} \
  --field 'Full name=Jane Doe' \
  --field 'First=Jane' \
  --field 'Last=Doe' \
  --field 'Role=Marriage counselor' \
  --field 'Website=https://example.com' \
  --field 'Email=name@example.com' \
  --field 'Location=Connecticut' \
  --field 'Email sent=Yes' \
  --field 'Status=Waiting for reply' \
  --append-r2-note '2026-03-25: initial outreach sent from ryan@ryancarson.com using coach_therapist template.'
```

For existing-row updates where you want an extra-safe match, add an explicit identity hint:

```bash
python3 ~/.openclaw/workspace/clawchief/scripts/sheet_helper.py lead-upsert \
  --spreadsheet {{GOOGLE_SHEET_ID}} \
  --match-field 'Email=name@example.com' \
  --field 'Status=Meeting booked' \
  --field 'Meeting booked=Yes' \
  --append-r2-note '2026-03-26: meeting booked for 2026-03-29 2:00 PM ET.'
```

Only use raw `sheet_helper.py update` / `append` for rare, deliberate sheet repairs where a row number is already known and you intentionally want low-level control.

## Default conventions

- `Full name` -> full display name (e.g. `Jane Doe, LMFT`)
- `First` -> first name only
- `Last` -> last name only
- `Phone` -> public direct number when confidently verified; otherwise leave blank
- `Email sent` -> `Yes` only once Ryan has actually sent the email
- `LI sent` -> `Yes` once the LinkedIn invite is actually sent
- `LI accepted` -> `Yes` only after the invite is accepted
- `Meeting booked` -> `Yes` only when a meeting is actually scheduled/confirmed
- `Ryan's Notes` -> reserve for notes Ryan explicitly wants stored there or notes that clearly reflect Ryan's own judgment
- `R2's Notes` -> short, dated, operationally useful relationship history: what happened last, what matters about this person, what is sensitive, and the next step or blocker
- `Status` -> one clear current pipeline state using the preferred vocabulary when possible

CRM note discipline:
- append dated notes, do not overwrite important relationship history without reason
- keep notes compact and cumulative
- if there is a next step for Ryan, say it explicitly in `R2's Notes`
- if there is no next step, make that legible from `Status`

If Ryan's email assigns a follow-up (for example: find a meeting time), update the sheet with that new next step as well.

## Follow-up cadence

For unanswered outreach emails where the lead should stay active, use this cadence as the review reminder for Ryan-origin outreach and later human judgment.

- first review point: about 2 days after the last unanswered outbound
- second review point: about 5 days after the previous outbound touch
- third review point: about 7 days after that touch

Rules:

- Reset the clock after each new outbound follow-up from Ryan or each Ryan-origin auto-send that materially restarts the thread.
- Use the cadence to decide when the next follow-up review is due unless Ryan overrides it.
- Record each sent follow-up, or any important follow-up-needed note for Ryan, in `R2's Notes` with the date and a short description.
- After the third unanswered follow-up, stop the automatic sequence and surface the lead to Ryan if it still matters.
- Do not auto-follow up when the thread is sensitive, clearly closed, or Ryan told you to stop.
- Do not auto-send follow-ups from this skill unless Ryan later approves that change explicitly.

## Outreach template

- Use `python3 ~/.openclaw/workspace/clawchief/scripts/bd_outreach.py` for the approved initial outreach templates.
- Use `~/.openclaw/skills/business-development/resources/partners.md` only if Ryan explicitly asks for alternate copy beyond the built-in auto-send templates.

## Default outbound workflow

1. Verify the lead is not already in the sheet.
2. Verify the lead is actually Connecticut-based before adding them unless Ryan explicitly asks for a broader geography.
3. Multi-state leads are acceptable if Connecticut is explicitly included in their geography or service area (for example `NY + CT region`). If Connecticut is not explicit, treat the geography as insufficiently verified and leave the lead out or note the ambiguity.
4. Prefer high-signal Connecticut sources first, including credential/member directories (for example CDC / ACC directories) when they expose practitioner listings.
5. For default prospecting, stay inside the lane Ryan specified: the current default split of 5 Connecticut marriage counselors or divorce coaches plus 5 Connecticut family-law attorneys from small (1-2 person) firms. Do not expand beyond that mix unless Ryan explicitly changes the target audience.
6. Verify website before adding a new lead unless Ryan explicitly waives that rule.
7. If a LinkedIn URL is already listed on the person's own website or already exists in the tracker, preserve it. Otherwise leave the LinkedIn field blank rather than doing LinkedIn research.
8. Before leaving `Email` blank, inspect the website for a public address. Check the homepage plus likely `Contact`, `About`, `Book`, and `Schedule` pages when available.
9. Store the best real public email you find in the sheet, cleaning obvious typos when the intended address is unambiguous.
10. Ignore placeholder / system-generated junk addresses from site code (for example `user@domain.com`, Sentry / Wix telemetry, or HTML asset false positives).
11. Send the initial outreach email from `ryan@ryancarson.com` using `bd_outreach.py` once the lead is verified and you have the public email address.
12. Leave `LI sent` and `LI accepted` unchanged during the default batch unless Ryan explicitly reports a state change that should be logged.
13. Immediately update the lead row after the send succeeds via `sheet_helper.py lead-upsert`: `Email sent` -> `Yes`, append a dated note in `R2's Notes` naming the template used, and set `Status` to `Waiting for reply`.
14. After the send succeeds, create or update a Ryan Todoist follow-up task for that specific contact due 3 days later.
15. Sweep sent mail for unanswered outreach and use the default 2 / 5 / 7 cadence to decide when a review or human follow-up is due unless Ryan overrides it.
16. Record each sent follow-up, or any important follow-up-needed note for Ryan, in `R2's Notes` with the date and what happened.
17. Do not auto-send follow-ups from this skill unless Ryan later approves that change explicitly.
18. Before booking a meeting tied to outreach, treat out-of-office, travel, offsite, and similar not-available blocks as hard conflicts, not just normal meeting overlaps.
19. If calendar visibility is incomplete or those availability markers are not clearly verifiable, do not auto-book; ask Ryan or offer manual windows instead.
20. If a meeting gets booked, set `Meeting booked` to `Yes` and append a dated note with the scheduled time in `R2's Notes` unless Ryan explicitly wants it in `Ryan's Notes`.
21. If a meeting later moves or is canceled, update `R2's Notes` again with the new scheduling state so the sheet remains the source of truth.

## Sheet cleanup / replacement workflow

- If Ryan asks to remove leads by geography or otherwise prune the live list, write a local backup of the current sheet first before deleting or rewriting rows.
- When replacing removed rows with fresh leads, prefer rows with verified website and public email. Preserve a LinkedIn URL only when it is already available without doing LinkedIn work.

## LinkedIn policy

- Do not perform LinkedIn activity as R2 in recurring business-development work.
- Do not open LinkedIn, search LinkedIn, send connection requests, or check acceptance state.
- Preserve existing LinkedIn values in the tracker when they already exist from prior work or from the person's own website.
- If Ryan still wants LinkedIn done for a batch, track that as a separate Ryan-owned task rather than bundling it into the email-send step.

## CRM operating model

Think in three layers:
- Sheet fields = structured CRM state
- `R2's Notes` = compact relationship history and context
- skills / heartbeat = the updater that keeps both fresh

Every meaningful interaction should answer four CRM questions:
- who is this person and why do they matter?
- what happened most recently?
- what state is the relationship currently in?
- what is the next step, and who owns it?

If one of those answers changed, update the row.

## Operating standard

- Keep outreach state current as part of doing the work, not as an afterthought.
- Use `~/.openclaw/workspace/clawchief/priority-map.md` to decide what belongs to the active business-development motion, what should interrupt Ryan, and what can be batched.
- Use `~/.openclaw/workspace/clawchief/auto-resolver.md` to decide when to resolve the obvious next step immediately versus draft or escalate.
- Do not duplicate priority definitions here when the priority map already defines the program or person.
- Every meaningful partner thread should leave both the tracker and Todoist in sync when future work remains.
- If verification or access fails, create an explicit Todoist blocker instead of leaving the failure only in prose.
- Preserve thread context and recipient context before replying.
- For email work, preserve thread context and recipient context before summarizing what Ryan needs to do next.
- Sweep sent mail as part of business-development work so active outreach gets timely follow-up.
- Process inbound partner replies and sheet updates as one combined workflow; do not mark the email handled until the tracker is updated.
- When an outreach conversation turns into scheduling, coordinate the meeting and then update the tracker immediately after the scheduling action succeeds.
- Never rely on memory for tracker sync; the sheet must be updated in the same turn as the reply or booking work whenever practical.
- Heartbeats and recurring sweeps should review the CRM as an active queue, not just a historical log. Prefer scanning for rows with statuses like `Positive reply`, `Scheduling`, `Meeting booked`, `Needs cleanup`, or stale `Waiting for reply` rows that now need Ryan attention.
- Treat `Ready for Ryan outreach` as an exception state for researched leads that are intentionally being held before a send, not as the normal default-batch outcome.
- After a default prospecting batch sends new outreach emails, ensure each contact has a Ryan follow-up task due 3 days later before considering the batch complete.
- If an email was previously marked sent because R2 sent it by mistake, do not keep pretending Ryan sent it. Preserve the history in `R2's Notes`, correct the structured field, and set the best honest `Status`.
- Treat email and LinkedIn outreach as separate tracked actions when Ryan performs them; do not collapse them into one generic contact flag.
- Use the default 2 / 5 / 7 follow-up cadence for low-risk unanswered outreach unless Ryan says otherwise, but treat it as a review/triage cadence rather than an automatic follow-up-send rule.
- Escalate to Ryan when the reply has strategic importance, partnership implications, pricing sensitivity, or reputational risk.
