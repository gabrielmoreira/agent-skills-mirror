---
name: zapier-make-patterns
description: "Designs Zapier Zaps and Make scenarios: trigger-action chains, Paths/Routers, Formatter/data functions, iterators, and task-versus-operation cost math. Trigger on Zapier, Make, Integromat, zaps, or no-code SaaS wiring. Not a Temporal/Inngest/n8n code chair (workflow-automation). Do not use dropdown labels where APIs require IDs."
version: 1.0.1
risk: unknown
source: vibeship-spawner-skills (Apache 2.0)
date_added: 2026-02-27
---

# Zapier & Make Patterns

No-code automation democratizes workflow building. Zapier and Make (formerly Integromat) let non-developers automate business processes without writing code. But no-code doesn't mean no-complexity — these platforms have their own patterns, pitfalls, and breaking points.

**Key insight**: Zapier optimizes for simplicity and integrations (7000+ apps, linear workflows, task-based pricing). Make optimizes for power and cost-efficiency (visual branching, operations-based pricing, powerful data handling).

**Critical distinction**: No-code works until it doesn't. Know the limits.

## When to Use

Activate this skill when the user mentions or implies any of the following:

- **Zapier**, **Make**, **Integromat**, **Zap**, **scenario**, **no-code automation**
- **Trigger action**, **workflow automation**, **connect apps**, **automate**
- Building or debugging multi-step automations between SaaS apps
- Error handling, looping, branching, or data transformation in no-code platforms
- Cost optimization for task/operation-based pricing models
- Deciding between Zapier vs Make vs n8n vs code-based solutions

## Prerequisites

- A Zapier account (free tier works for testing; Pro+ required for Paths and multi-step Zaps)
- A Make account (free tier supports basic scenarios; paid tiers for higher operation limits)
- Access to the target apps you want to integrate (with appropriate permissions)
- For Windows users: PowerShell terminal available for any local scripting or webhook testing

## Procedure

### 1. Choose the Right Platform

| Platform | Best For | Pricing Model | Key Limitation |
|----------|----------|---------------|----------------|
| **Zapier** | Simple automations, maximum app coverage, beginners | Task-based (each action = 1 task) | 7000+ integrations, linear workflows |
| **Make** | Complex workflows, visual branching, budget-conscious | Operations-based (module executions) | Fewer native integrations than Zapier |
| **n8n** | Self-hosted, code-friendly, unlimited operations | Open-source / paid cloud | Requires technical users |

**Decision rule**: If the workflow is linear with 1–3 steps, use Zapier. If it needs branching, iterators, aggregators, or complex data transformation, use Make. If you need self-hosting or unlimited operations, use n8n.

### 2. Build the Core Trigger-Action Pattern

Start with the simplest viable automation before adding complexity.

**Zapier Example — Gmail to Todoist**:

```
Zap Name: "Gmail New Email → Todoist Task"

TRIGGER: Gmail - New Email
  - From: specific-sender@example.com
  - Has attachment: yes

ACTION: Todoist - Create Task
  - Project: Inbox
  - Content: {{Email Subject}}
  - Description: From: {{Email From}}
  - Due date: Tomorrow
```

**Make Example — Gmail to Todoist**:

```
Scenario: "Gmail to Todoist"

[Gmail: Watch Emails] → [Todoist: Create a Task]

Gmail Module:
  - Folder: INBOX
  - From: specific-sender@example.com

Todoist Module:
  - Project ID: (select from dropdown)
  - Content: {{1.subject}}
  - Due String: tomorrow
```

**Best practices**:
- Use descriptive Zap/Scenario names (include trigger and action apps)
- Test with real sample data before going live
- Use filters to prevent unwanted runs

### 3. Add Multi-Step Sequential Logic

Chain actions where each step's output is available to subsequent steps.

**Zapier Multi-Step Zap**:

```
Zap: "New Lead → CRM → Slack → Email"

1. TRIGGER: Typeform - New Entry
   - Form: Lead Capture Form

2. ACTION: HubSpot - Create Contact
   - Email: {{Typeform Email}}
   - First Name: {{Typeform First Name}}
   - Lead Source: "Website Form"

3. ACTION: Slack - Send Channel Message
   - Channel: #sales-leads
   - Message: "New lead: {{Typeform Name}} from {{Typeform Company}}"

4. ACTION: Gmail - Send Email
   - To: {{Typeform Email}}
   - Subject: "Thanks for reaching out!"
   - Body: (template with personalization)
```

**Make Scenario**:

```
[Typeform] → [HubSpot] → [Slack] → [Gmail]

- Each module passes data to the next
- Use {{N.field}} to reference module N's output
- Add error handlers between critical steps
```

### 4. Implement Conditional Branching

**Zapier Paths** (Pro+ required):

```
Zap: "Route Support Tickets"

1. TRIGGER: Zendesk - New Ticket

2. PATH A: If priority = "urgent"
   - Slack: Post to #urgent-support
   - PagerDuty: Create incident

3. PATH B: If priority = "normal"
   - Slack: Post to #support
   - Asana: Create task

4. PATH C: Otherwise (catch-all)
   - Slack: Post to #support-overflow
```

**Make Router**:

```
[Zendesk: Watch Tickets]
      ↓
[Router]
   ├── Route 1: priority = urgent
   │     └→ [Slack] → [PagerDuty]
   │
   ├── Route 2: priority = normal
   │     └→ [Slack] → [Asana]
   │
   └── Fallback route
         └→ [Slack: overflow]
```

**Best practices**:
- Always have a fallback/else path
- Test each path independently
- Document which conditions trigger which path

### 5. Transform Data Between Steps

**Zapier Formatter** — common transformations:

```
1. Text manipulation:
   - Split text: "John Doe" → First: "John", Last: "Doe"
   - Capitalize: "john" → "John"
   - Replace: Remove special characters

2. Date formatting:
   - Convert: "2024-01-15" → "January 15, 2024"
   - Adjust: Add 7 days to date

3. Numbers:
   - Format currency: 1000 → "$1,000.00"
   - Spreadsheet formula: =SUM(A1:A10)

4. Lookup tables:
   - Map status codes: "1" → "Active", "2" → "Pending"
```

**Make Data Functions** — built-in functions:

```
Text:
  {{lower(1.email)}}            # Lowercase
  {{substring(1.name; 0; 10)}}  # First 10 chars
  {{replace(1.text; "-"; "")}}  # Remove dashes

Arrays:
  {{first(1.items)}}            # First item
  {{length(1.items)}}           # Count items
  {{map(1.items; "id")}}        # Extract field

Dates:
  {{formatDate(1.date; "YYYY-MM-DD")}}
  {{addDays(now; 7)}}

Math:
  {{round(1.price * 0.8; 2)}}   # 20% discount, 2 decimals
```

**Best practices**:
- Transform early in the workflow
- Use filters to skip invalid data
- Log transformations for debugging

### 6. Add Error Handling

**Zapier Error Handling**:

```
1. Built-in retry (automatic):
   - Zapier retries failed actions automatically
   - Exponential backoff for temporary failures

2. Error handling step:
   Zap:
     1. [Trigger]
     2. [Action that might fail]
     3. [Error Handler]
        - If error → [Slack: Alert team]
        - If error → [Email: Send report]

3. Path-based handling:
   [Action] → Path A: Success → [Continue]
            → Path B: Error → [Alert + Log]
```

**Make Error Handlers**:

```
[Module] ──┬── Success → [Next Module]
           │
           └── Error → [Error Handler]

Error handler types:
1. Break: Stop scenario, send notification
2. Rollback: Undo completed operations
3. Commit: Save partial results, continue
4. Ignore: Skip error, continue with next item

Example:
[API Call] → Error Handler (Ignore)
           → [Log to Airtable: "Failed: {{error.message}}"]
           → Continue scenario
```

**Best practices**:
- Always add error handlers for external API calls
- Log errors to a spreadsheet/database
- Set up Slack/email alerts for critical failures
- Test failure scenarios, not just success paths

### 7. Handle Batch Processing and Loops

**Zapier Looping**:

```
Zap: "Process Order Items"

1. TRIGGER: Shopify - New Order
   - Returns: order with line_items array

2. LOOPING: For each item in line_items
   - Create inventory adjustment
   - Update product count
   - Log to spreadsheet

Note: Each loop iteration counts as tasks!
10 items = 10 tasks consumed
```

**Make Iterator + Aggregator**:

```
[Webhook: Receive Order]
      ↓
[Iterator: line_items]
      ↓ (processes each item)
[Inventory: Adjust Stock]
      ↓
[Aggregator: Collect Results]
      ↓
[Slack: Summary Message]

Iterator creates one bundle per item.
Aggregator combines results back together.
Use Array Aggregator for collecting processed items.
```

**Best practices**:
- Use aggregators to combine results
- Consider batch limits (some APIs limit to 100)
- Watch operation/task counts for cost
- Add delays for rate-limited APIs

### 8. Set Up Scheduled Automations

**Zapier Schedule Trigger**:

```
Zap: "Daily Sales Report"

TRIGGER: Schedule by Zapier
  - Every: Day
  - Time: 8:00 AM
  - Timezone: America/New_York

ACTIONS:
  1. Google Sheets: Get rows (yesterday's sales)
  2. Formatter: Calculate totals
  3. Gmail: Send report to team
```

**Make Scheduled Scenarios**:

```
Scenario Schedule Options:
  - Run once (manual)
  - At regular intervals (every X minutes)
  - Advanced: Cron expression (0 8 * * *)

[Scheduled Trigger: Every day at 8 AM]
      ↓
[Google Sheets: Search Rows]
      ↓
[Iterator: Process each row]
      ↓
[Aggregator: Sum totals]
      ↓
[Gmail: Send Report]
```

**Best practices**:
- Consider timezone differences
- Add buffer time for long-running jobs
- Log execution times for monitoring
- Don't schedule at exactly midnight (busy period)

## Pitfalls

### CRITICAL: Using Text Instead of IDs in Dropdown Fields

**Symptoms**: "Bad Request" errors, "Invalid value" messages, action fails despite correct-looking input. Works when you select from dropdown, fails with dynamic values.

**Why**: Dropdown menus display human-readable text but send IDs to APIs. When you type "Marketing Team" instead of selecting it, Zapier sends that text as the ID, which the API doesn't recognize.

**Fix — Zapier**:
1. Add a "Find" or "Search" action first (e.g., HubSpot: Find Contact → returns `contact_id`)
2. Use the returned ID in subsequent actions
3. In the dropdown, select "Use Custom Value" and map the ID from the search step

**Fix — Make**:
1. Add a Search module first (e.g., Search Contacts: filter by email → returns `contact_id`)
2. Map the ID to subsequent modules: `Contact ID: {{2.id}}` (from search module)

**Common ID fields that trip people up**:
- User/Member IDs in Slack, Teams
- Contact/Company IDs in CRMs
- Project/Folder IDs in project tools
- Category/Tag IDs in content systems

### CRITICAL: Zap Auto-Disabled at 95% Error Rate

**Symptoms**: Zap suddenly stops running, email notification about auto-disable, "This Zap was automatically turned off" message, data stops syncing.

**Why**: Zapier automatically disables Zaps that have 95% or higher error rate over 7 days.

**Prevention**:
1. Add error handling steps (Path: If error → Log + Alert)
2. Use filters to prevent bad data (only continue if email exists, amount > 0, etc.)
3. Monitor task history regularly for recurring errors

**Recovery**:
1. Check Task History for error patterns
2. Fix the root cause (auth, bad data, API changes)
3. Test with sample data
4. Re-enable the Zap manually
5. Monitor closely for next 24 hours

**Common causes**: Expired auth tokens, API rate limits, changed field names in connected apps, invalid data formats.

### HIGH: Loops Consuming Unexpected Task Counts

**Symptoms**: Task quota depleted unexpectedly, one Zap run shows as 100+ tasks, monthly limit reached in days.

**Why**: In Zapier, each iteration of a loop counts as separate tasks. An order with 50 line items and 5 actions per item = 1 trigger + (50 × 5) = 251 tasks.

**Fix**:
1. Batch operations — use "Create Many Rows" instead of loop + create
2. Aggregate before sending — collect all items, send one summary message
3. Filter before looping — only process items that need action
4. Consider Make for high-volume — Make uses operations (module executions), not per-action tasks

### HIGH: App Updates Breaking Existing Zaps

**Symptoms**: Working Zap suddenly fails, "Field not found" errors, different data format in outputs.

**Why**: When connected apps update their APIs, field names change, new required fields appear, or data formats shift.

**Fix**:
1. Check Task History for specific errors
2. Open the Zap editor to see field mapping issues
3. Re-select the trigger/action to refresh schema
4. Re-map any fields that show as "unknown"
5. Test with new sample data

**Prevention**: Subscribe to changelogs for critical apps, keep connection authorizations fresh, test Zaps after major app updates, document field mappings, use test/duplicate Zaps for experiments.

**Common offenders**: CRM field restructures, API version upgrades, OAuth scope changes, new required permissions.

### HIGH: Authentication Tokens Expiring

**Symptoms**: "Authentication failed" errors, "Please reconnect" messages, Zaps fail after weeks of working.

**Why**: OAuth tokens expire. Some apps require re-authentication every 60–90 days. If the user who connected the app leaves the company, their connection may stop working.

**Fix**:
1. Go to Settings → Apps, find the app with issues, reconnect (re-authorize), test affected Zaps

**Prevention**:
1. Use service accounts for connections — don't connect with personal accounts
2. Monitor connection health — check Apps page regularly
3. Document who connected what — track in spreadsheet, handoff process when people leave
4. Prefer connections that don't expire — API keys over OAuth when available

### MEDIUM: Webhooks Missing or Duplicating Events

**Symptoms**: Some events never trigger the Zap, same event triggers multiple times, inconsistent behavior.

**Why**: Webhooks are fire-and-forget. If Zapier's receiving endpoint is slow or unavailable, the webhook may fail. Some systems retry webhooks, causing duplicates.

**Fix — Handle duplicates**:
1. Add deduplication logic: Filter — only continue if ID not already in Airtable
2. Use idempotency: store processed IDs, skip if ID exists

```
[Webhook Trigger]
   ↓
[Airtable: Find Records] - search by event_id
   ↓
[Filter: Only continue if not found]
   ↓
[Process Event]
   ↓
[Airtable: Create Record] - store event_id
```

**Fix — Handle missed events**:
1. Use polling triggers for critical data (less real-time but more reliable)
2. Implement reconciliation: scheduled Zap to check for gaps
3. Check source system retry settings

### MEDIUM: Make Operations Consumed by Error Retries

**Symptoms**: Operations quota depleted quickly, scenario runs "succeeded" but used many operations.

**Why**: Make counts operations per module execution, including failed attempts and retries. Error handler modules consume operations. Scenarios that fail and retry can use 3–5x expected operations.

**Fix**:
1. Add error handlers that break early: `[Module] → Error → [Break]` (1 additional op) vs `[Module] → Error → [Log] → [Alert] → [Update]` (3+ ops)
2. Use ignore instead of retry when appropriate (record exists, bad data)
3. Pre-validate before expensive operations: `[Check Data] → Filter → [API Call]`
4. Optimize scenario scheduling — don't run every minute if hourly is enough

### MEDIUM: Timezone Mismatches in Scheduled Triggers

**Symptoms**: Zap runs at wrong time, "9 AM" trigger fires at 2 PM, different behavior on different days, DST causes hour shifts.

**Why**: Zapier shows times in your local timezone but may store in UTC. If you change timezones or DST occurs, scheduled times shift.

**Fix**:
1. Explicitly set timezone in schedule — don't rely on browser detection
2. Document in Zap name: "Daily Report 9AM EST"
3. Test around DST transitions
4. For global teams, use UTC as standard, convert to local in descriptions
5. Don't schedule at exactly midnight or on-the-hour (busy periods)

**Make timezone handling**: Scenarios use account timezone setting, `formatDate()` respects timezone, use `parseDate()` with explicit timezone.

## Verification

### Verify Zap is Live and Running

1. **Check Zap status**: In Zapier dashboard, confirm the Zap shows as "On" (green toggle)
2. **Run a test**: Trigger the source event manually and check Task History:
   - Go to Zapier → Task History
   - Filter by Zap name
   - Confirm the most recent run shows "Success" status
3. **Verify data arrived**: Check the destination app for the expected record/message

### Verify Make Scenario is Active

1. **Check scenario status**: In Make dashboard, confirm scenario toggle is "ON"
2. **Run manually**: Click "Run once" to execute with real data
3. **Check execution log**: View the scenario history (clock icon) — each module should show a green checkmark
4. **Verify operation count**: Check the operations counter to confirm expected consumption

### Verify Error Handling Works

1. **Intentionally trigger a failure**: Send invalid data through the workflow
2. **Confirm error handler fires**: Check that the Slack alert or log entry was created
3. **Confirm main workflow stops gracefully**: No partial/corrupt data in destination

### Verify Cost Efficiency

**Zapier task math check**:
```
Expected tasks per run = 1 (trigger) + (number of actions) + (loop iterations × actions per iteration)
```
Compare against Task History actuals. If actuals exceed expected, investigate filters or loops.

**Make operation math check**:
```
Expected operations per run = number of modules executed (including error handlers and retries)
```
Compare against Operations dashboard. If actuals are 3x+ expected, investigate retry loops.

## Related Skills

- **workflow-automation** — Code-based solutions like Inngest, Temporal for when no-code hits limits
- **agent-tool-builder** — AI agent tools and Zapier MCP integration
- **backend** — Custom backend processing for high-volume data
- **api-designer** — API design and implementation for custom integrations
- **browser-automation** — Playwright/Puppeteer integration for browser-based workflows
- **devops** — n8n or custom workflow deployment for self-hosted automation

## Limitations

- Use this skill only when the task clearly matches no-code automation on Zapier or Make.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
- No live secrets — use `YOUR_KEY` placeholders in all examples. Never paste real API keys or OAuth tokens into documentation.
