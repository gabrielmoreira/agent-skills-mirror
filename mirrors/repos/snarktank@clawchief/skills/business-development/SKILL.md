---
name: business-development
description: "Manage {{BUSINESS_NAME}} business-development and outreach-tracking work using Google Workspace via gog. Use when handling prospecting replies, referral-partner outreach, updating the outreach tracker, logging lead status changes, booking or confirming outreach meetings tied to a lead/prospect, or maintaining the operational record of sales/outreach conversations for {{BUSINESS_NAME}}. Prefer this skill over executive-assistant whenever the task touches the outreach tracker, lead status, prospect pipeline, or referral-partner outreach, even if scheduling is involved."
---

# Business Development

Use this skill for outreach and prospect tracking work. Keep it separate from executive-assistant inbox clearing.

## Gotchas

- The Google Sheet is the live source of truth; do not treat local prospect files as current state.
- Do not silently broaden default prospecting beyond `{{TARGET_MARKET}}` in `{{TARGET_GEOGRAPHY}}` unless {{OWNER_NAME}} explicitly changes the audience.
- Verify website + LinkedIn before adding a new lead unless {{OWNER_NAME}} explicitly waives that requirement.
- When reviewing a lead's website, actively look for a public email address before leaving `Email` blank. Check the homepage plus likely `Contact`, `About`, `Book`, `Schedule`, or similar pages when they exist.
- Ignore junk matches such as placeholder examples (`user@domain.com`), vendor / telemetry addresses (for example Sentry / Wix internals), or asset-path false positives from scraped HTML.
- If the site shows an obvious typo in the address (for example a duplicated TLD like `.com.com`) and the intended real address is clear from context, normalize it before storing it.
- Track email outreach and LinkedIn outreach as separate actions.
- Sweep relevant sent mail so unanswered outreach does not disappear.
- Prefer a dedicated agent-controlled browser profile for LinkedIn work; do not default to {{OWNER_NAME}}'s live personal Chrome attach flow unless he is physically present and explicitly wants that mode.
- If the work touches lead status, pipeline state, or the outreach tracker, this skill owns it even when scheduling is part of the job.

## Current business-development focus

- Current short-term goal: help {{BUSINESS_NAME}} get its first 10 paying customers.
- Default outbound prospecting focus: leads that fit `{{TARGET_MARKET}}` in `{{TARGET_GEOGRAPHY}}` and could plausibly refer customers to {{BUSINESS_NAME}}.
- When {{OWNER_NAME}} asks for "more contacts" without narrowing the audience, interpret that as fresh uncontacted leads that fit `{{TARGET_MARKET}}` in `{{TARGET_GEOGRAPHY}}` unless the current conversation overrides it.
- Multi-region leads are acceptable if `{{TARGET_GEOGRAPHY}}` is explicitly included in their geography or service area.
- Do not add out-of-geography prospects by default if `{{TARGET_GEOGRAPHY}}` is not part of their stated geography unless {{OWNER_NAME}} explicitly asks for a broader geography.
- Do not silently broaden the target list beyond `{{TARGET_MARKET}}` unless {{OWNER_NAME}} explicitly changes the audience.
- Prefer individual practitioners or small firms with public contact details and avoid duplicates already present in the outreach tracker.
- Before adding a new lead, verify that the website URL works and that the LinkedIn URL resolves to the intended person or organization. Treat website + LinkedIn verification as a default requirement unless {{OWNER_NAME}} explicitly says otherwise.
- Prefer prospect sources that are likely to be high-signal for `{{TARGET_MARKET}}` in `{{TARGET_GEOGRAPHY}}`, including relevant member directories or professional lists when available.

## Source of truth

Google Sheet ID: `{{GOOGLE_SHEET_ID}}`

Note: this sheet currently has a different column layout from the earlier temporary outreach tracker. Do not assume example commands from an older sheet are correct without checking the current `Leads` header row first.

Treat this sheet as the live source of truth for outreach status. Do not rely on local `.md` or `.csv` prospect files as the current record.

## When to update it

Update the sheet every time outreach state changes.

That includes when you:

- send the initial outreach email
- send a LinkedIn connection request
- get any meaningful reply
- ask for a meeting
- book, confirm, reschedule, or cancel a meeting
- record a decline / not-a-fit outcome
- learn a follow-up or next-step detail worth preserving

Do this before you mark the message handled.

Treat tracker updates as mandatory, not optional cleanup.

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
   - `Name`
   - `Role`
   - `Website`
   - `Email`
   - `Location`
   - `Email sent`
   - `LI connect sent`
   - `LI connect accpeted`
   - `Meeting booked`
   - `LinkedIn`
   - `{{OWNER_NAME}}'s Notes`
   - `{{ASSISTANT_NAME}}'s Notes`
   - `Date added`
   - `Partner link`
5. If the person is not already in the sheet, append a new row and populate all columns you can verify from the email, website, or LinkedIn.
6. Put **{{ASSISTANT_NAME}}-authored operational notes** in `{{ASSISTANT_NAME}}'s Notes`, not `{{OWNER_NAME}}'s Notes`.
7. Use `{{OWNER_NAME}}'s Notes` only for notes {{OWNER_NAME}} explicitly wants preserved there or notes that clearly represent {{OWNER_NAME}}'s own view.
8. Only after the sheet is current should the email be considered handled.
9. If you book a meeting through Calendly, Google appointment schedules, HubSpot, Acuity, Chili Piper, or any similar scheduler, immediately update the row after the booking succeeds.

Default note patterns:
- positive reply, not booked yet -> note interest + next step needed
- meeting booked -> include the scheduled date/time
- decline -> note the decline clearly
- auto-reply / bad contact -> note what happened and any fallback contact info
- substantive questions -> note the question so the tracker reflects the blocker

Useful message-level Gmail searches:

```bash
gog gmail messages search 'subject:"Potential partnership" newer_than:30d' -a {{ASSISTANT_EMAIL}} --all --include-body --json --results-only

gog gmail messages search 'subject:"Saw your work" newer_than:30d' -a {{ASSISTANT_EMAIL}} --all --include-body --json --results-only
```

If {{OWNER_NAME}} asks to "process the partner replies" or says emails have come in from partners, interpret that as:
- read the inbound reply messages
- update / append the corresponding `Leads` rows
- fill any obvious missing fields worth capturing
- leave the sheet in sync before reporting back

## How to update it

1. Read the relevant email/thread context.
2. Check the current `Leads` rows to see whether the person already exists.
3. If they exist, update the existing row.
4. If they do not exist, append a new row.
5. Capture {{ASSISTANT_NAME}}'s operational state in `{{ASSISTANT_NAME}}'s Notes` with a short dated note.
6. Leave `{{OWNER_NAME}}'s Notes` alone unless {{OWNER_NAME}} explicitly supplied a note for that column.

For this sheet size, inspect the current lead table and header row directly before writing:

```bash
gog sheets get {{GOOGLE_SHEET_ID}} 'Leads!A:N' -a {{ASSISTANT_EMAIL}} --json --results-only
```

Use `--values-json` for reliable multi-column writes. Current expected column order is:
`Name | Role | Website | Email | Location | Email sent | LI connect sent | LI connect accpeted | Meeting booked | LinkedIn | {{OWNER_NAME}}'s Notes | {{ASSISTANT_NAME}}'s Notes | Date added | Partner link`

```bash
gog sheets update {{GOOGLE_SHEET_ID}} 'Leads!A13:N13' --values-json='[["Name","Role","https://example.com","name@example.com","{{TARGET_GEOGRAPHY}}","Yes","Yes","No","No","https://www.linkedin.com/in/example/","","2026-03-25: sent email. 2026-03-25: sent LinkedIn connection request with note.","2026-03-25",""]]' -a {{ASSISTANT_EMAIL}} --json --results-only

gog sheets append {{GOOGLE_SHEET_ID}} 'Leads!A:N' --values-json='[["Name","Role","https://example.com","name@example.com","{{TARGET_GEOGRAPHY}}","No","No","No","No","https://www.linkedin.com/in/example/","","2026-03-25: verified website + LinkedIn.","2026-03-25",""]]' -a {{ASSISTANT_EMAIL}} --json --results-only
```

## Default conventions

- `Email sent` -> `Yes` once the initial outreach email is actually sent
- `LinkedIn connection request sent` -> `Yes` once the LinkedIn invite is actually sent
- `LI connect accpeted` -> `Yes` only after the invite is accepted
- `Meeting booked` -> `Yes` only when a meeting is actually scheduled/confirmed
- `{{OWNER_NAME}}'s Notes` -> reserve for notes {{OWNER_NAME}} explicitly wants stored there or notes that clearly reflect {{OWNER_NAME}}'s own judgment
- `{{ASSISTANT_NAME}}'s Notes` -> short, dated, operationally useful summary of the latest state, including follow-up touches, scheduling status, declines, and blockers

If {{OWNER_NAME}}'s email assigns a follow-up (for example: find a meeting time), update the sheet with that new next step as well.

## Follow-up cadence

For unanswered outreach emails where the lead should stay active, use this default cadence unless {{OWNER_NAME}} overrides it:

- first follow-up: about 2 days after the last unanswered outbound
- second follow-up: about 5 days after the previous follow-up
- third follow-up: about 7 days after the previous follow-up

Rules:

- Reset the clock after each new outbound follow-up.
- Record each follow-up in `{{ASSISTANT_NAME}}'s Notes` with the date and a short description.
- After the third unanswered follow-up, stop the automatic sequence and surface the lead to {{OWNER_NAME}} if it still matters.
- Do not auto-follow up when the thread is sensitive, clearly closed, or {{OWNER_NAME}} told you to stop.

## Outreach template

- For default partner / referral outreach to counselors, coaches, and similar professionals, use `~/.openclaw/skills/business-development/resources/partners.md` as the canonical source for the email subject, email body, and LinkedIn note.
- Treat that file as the default wording source unless {{OWNER_NAME}} explicitly asks for a different draft for a specific campaign or audience.
- Personalize placeholders like `{first-name}` and make only light edits needed for fit, accuracy, or deliverability.

## Default outbound workflow

1. Verify the lead is not already in the sheet.
2. Verify the lead actually fits `{{TARGET_MARKET}}` in `{{TARGET_GEOGRAPHY}}` before adding them unless {{OWNER_NAME}} explicitly asks for a broader audience or geography.
3. Multi-region leads are acceptable if `{{TARGET_GEOGRAPHY}}` is explicitly included in their geography or service area. If the target geography is not explicit, treat the geography as insufficiently verified and leave the lead out or note the ambiguity.
4. Prefer high-signal sources first, including relevant directories, association lists, or niche databases that reliably surface `{{TARGET_MARKET}}` in `{{TARGET_GEOGRAPHY}}`.
5. For default prospecting, stay inside the lane {{OWNER_NAME}} specified: `{{TARGET_MARKET}}` in `{{TARGET_GEOGRAPHY}}`. Do not silently broaden beyond that unless {{OWNER_NAME}} explicitly changes the target audience.
6. Verify website + LinkedIn URL before adding a new lead unless {{OWNER_NAME}} explicitly waives that rule.
7. Before leaving `Email` blank, inspect the website for a public address. Check the homepage plus likely `Contact`, `About`, `Book`, and `Schedule` pages when available.
8. Store the best real public email you find in the sheet, cleaning obvious typos when the intended address is unambiguous.
9. Ignore placeholder / system-generated junk addresses from site code (for example `user@domain.com`, Sentry / Wix telemetry, or HTML asset false positives).
10. Send the initial outreach email using the subject/body in `partners.md`.
11. If a valid LinkedIn URL exists, send the LinkedIn connection request note from `partners.md` too.
12. Update `Email sent` and `LinkedIn connection request sent` independently in the sheet.
13. Sweep sent mail for unanswered outreach and send follow-ups on the default 2 / 5 / 7 cadence unless {{OWNER_NAME}} overrides it.
14. Record each follow-up in `{{ASSISTANT_NAME}}'s Notes` with the date and what was sent.
15. Before booking a meeting tied to outreach, treat out-of-office, travel, offsite, and similar not-available blocks as hard conflicts, not just normal meeting overlaps.
16. If calendar visibility is incomplete or those availability markers are not clearly verifiable, do not auto-book; ask {{OWNER_NAME}} or offer manual windows instead.
17. If a meeting gets booked, set `Meeting booked` to `Yes` and append a dated note with the scheduled time in `{{ASSISTANT_NAME}}'s Notes` unless {{OWNER_NAME}} explicitly wants it in `{{OWNER_NAME}}'s Notes`.
18. If a meeting later moves or is canceled, update `{{ASSISTANT_NAME}}'s Notes` again with the new scheduling state so the sheet remains the source of truth.

## Sheet cleanup / replacement workflow

- If {{OWNER_NAME}} asks to remove leads by geography or otherwise prune the live list, write a local backup of the current sheet first before deleting or rewriting rows.
- When replacing removed rows with fresh leads, prefer fully verified profile URLs in the `LinkedIn` column.
- If {{OWNER_NAME}} explicitly wants speed over completeness and only a LinkedIn search-fallback URL is available, it is acceptable to add the row temporarily, but note in `{{ASSISTANT_NAME}}'s Notes` that the LinkedIn URL is a search fallback and still needs verification.
- After a rushed add, do a cleanup pass later to replace search-fallback URLs with verified profile URLs when practical.

## LinkedIn browser workflow

For LinkedIn work, first read `~/.openclaw/skills/business-development/references/linkedin-browser.md`.

Short version:
- Prefer a dedicated agent-controlled browser profile (`openclaw` or a dedicated `linkedin` profile) for unattended LinkedIn work.
- Use remote CDP (for example Browserbase / Browserless) if the founder wants the browser decoupled from the Mac.
- Treat `profile="user"` / Chrome attach as a fallback only when {{OWNER_NAME}} is present to approve the attach prompt and the live signed-in Chrome session specifically matters.
- For acceptance checks, only mark `LI connect accpeted = Yes` on clear evidence, preferably a visible `1st` connection badge.
- Treat visible `Pending` as not accepted.
- Do not mark accepted from `Message` alone.

## Operating standard

- Keep outreach state current as part of doing the work, not as an afterthought.
- Preserve thread context and recipient context before replying.
- Sweep sent mail as part of business-development work so active outreach gets timely follow-up.
- Process inbound partner replies and sheet updates as one combined workflow; do not mark the email handled until the tracker is updated.
- When an outreach conversation turns into scheduling, coordinate the meeting and then update the tracker immediately after the scheduling action succeeds.
- Never rely on memory for tracker sync; the sheet must be updated in the same turn as the reply or booking work whenever practical.
- Treat email and LinkedIn outreach as separate tracked actions; do not collapse them into one generic contact flag.
- Use the default 2 / 5 / 7 follow-up cadence for low-risk unanswered outreach unless {{OWNER_NAME}} says otherwise.
- Escalate to {{OWNER_NAME}} when the reply has strategic importance, partnership implications, pricing sensitivity, or reputational risk.
