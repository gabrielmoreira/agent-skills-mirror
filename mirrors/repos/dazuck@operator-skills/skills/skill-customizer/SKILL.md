---
name: skill-customizer
description: Adapt any skill to your specific workflow, or create new ones for repetitive tasks. Use when adapting skills to your tools/process.
---

# Skill Customizer

Help operators personalize skills for their environment or create new skills for repetitive tasks.

## What Do You Need?

**Personalize an existing skill** — You have a skill that does roughly what you need, but it assumes different tools, processes, or context than yours. Run through the assumption audit to make it fit.

**Create a new skill** — You do something repeatedly (weekly or more), it takes 15+ minutes, and you keep giving Claude the same instructions. Turn it into a skill.

Ask which mode the user needs, then follow that path.

---

## How Skills Work

A skill has two parts:

**1. The Header** — tells Claude when to use it

```yaml
---
name: weekly-client-update
description: Generate weekly client status updates. Use when asked to write client updates, status reports, or weekly summaries.
---
```

The description is how Claude knows when to trigger your skill. Make it specific.

**2. The Instructions** — tells Claude what to do

- What context is needed
- Steps to follow
- What good output looks like

---

# Mode A: Personalize an Existing Skill

## Step 1: Audit the Assumptions

Every skill encodes assumptions. Read through it and extract them:

| Category         | What to Look For             | Examples                        |
| ---------------- | ---------------------------- | ------------------------------- |
| **Tools**        | Named software, platforms    | "Uses Notion" "Posts to Slack"  |
| **Cadence**      | Frequencies, schedules       | "Weekly reviews" "EOD deadline" |
| **Process**      | Steps, approvals, handoffs   | "Manager approves first"        |
| **Stakeholders** | Who's involved, notified     | "CC the CFO" "Notify #finance"  |
| **Format**       | Structure, templates, length | "4 sections" "Under 1 page"     |
| **Terminology**  | Labels, categories           | "High/Medium/Low priority"      |
| **Thresholds**   | Amounts, limits, triggers    | "Flag over $5K"                 |
| **Tone**         | Voice, formality             | "Executive audience"            |

## Step 2: Walk Through Each Assumption

For each assumption, confirm or change:

**Tools:** "This skill uses [Notion] for [docs]. What do you use?"

**Cadence:** "This assumes [weekly reviews]. What's your cadence?"

**Process:** "This [gets manager approval before sending]. Same for you?"

**Stakeholders:** "This notifies [#finance in Slack]. Who should know in your setup?"

**Format:** "Output follows [this 4-section template]. Different structure?"

**Terminology:** "This uses [High/Medium/Low] for priority. What does your team use?"

**Thresholds:** "This flags anything over [$10K]. What's your threshold?"

**Tone:** "Written for [executives]. Who's your audience?"

Group related questions. Don't overwhelm with all at once.

## Step 3: Document the Mapping

| Original                  | Your Setup              |
| ------------------------- | ----------------------- |
| Notion                    | Confluence              |
| Weekly reviews            | Twice weekly            |
| #accounts-payable         | #finance-ops            |
| Manager approval required | Team lead for >$1K only |

## Step 4: Make the Edits

Update each assumption in the skill.

**Example: Adapting a Hiring Pipeline Skill**

```markdown
# Before

1. Pull candidates from Greenhouse "Phone Screen" stage
2. Schedule weekly sync to review pipeline
3. Recruiter screens → Hiring manager → Team loop
4. HR approves all offers

# After

1. Pull candidates from Lever "Ready for Screen" stage
2. Schedule twice-weekly sync (Tue/Thu)
3. Hiring manager screens → Recruiter coordination → Team loop
4. Offers >$150K: CEO approval. Others: HR approval.
```

## Step 5: Add Your Context Section

Make assumptions explicit for future reference:

```markdown
## Our Context

- **Payment platform:** Ramp
- **Approval threshold:** $2.5K requires CEO approval
- **Payment terms:** Net-15 default
- **Fiscal year:** Calendar year (Jan-Dec)
```

## Step 6: Update the Description

If the purpose changed, update the description to match:

Before: "Process invoices using QuickBooks"
After: "Process invoices using Bill.com"

---

## Apply Everywhere

When making changes, check if the same change applies to other skills.

After updating an assumption, ask:

> "You changed [Slack → Discord]. I can check if other skills reference Slack. Want me to review those too?"

If yes, list the skills that have the same assumption and offer to walk through each one. This isn't batch editing—it's a helpful sweep to catch related changes while context is fresh.

**When to suggest this:**

- Tool swaps (Notion → Confluence, Slack → Discord)
- Company-wide terminology changes
- Threshold changes that apply across workflows
- Stakeholder changes (new CFO, reorg)

**How to do it:**

1. Identify the pattern (what changed)
2. Search other skills for the same assumption
3. List matches: "These 3 skills also reference Slack: [list]"
4. Walk through each, confirming the change applies

---

## Quick Personalization

For simple changes that don't need a full audit:

| Change Type               | Just Edit...    |
| ------------------------- | --------------- |
| Tool swap (same function) | Tool names only |
| Output destination        | Delivery step   |
| Add approval step         | Process section |
| Adjust threshold          | Number values   |
| Change term               | Find/replace    |

**Example: Tool Swap**

```markdown
# Before

1. Check "Open Invoices" in QuickBooks

# After

1. Check "Awaiting Payment" in Bill.com
```

---

# Mode B: Create a New Skill

## Step 1: Describe the Task

Answer these:

- What do you do? (Be specific)
- When do you do it? (What triggers it?)
- What information do you need to start?
- What does the output look like?

**Example:**

- "Every Monday, I write a status update for each active client"
- "Triggered by my weekly planning block"
- "I need: client name, what shipped, blockers, next week's focus"
- "Output is a 3-paragraph email under 200 words"

## Step 2: Walk Through It Once

Do the task while talking through decisions:

> "I'm writing the update for Acme Corp. First I check what shipped—dashboard redesign done. I always lead with something positive. Then the blocker—waiting on API credentials. I phrase it as 'we need X to continue' not 'you're blocking us.' Then next steps—API integration next week. Under 200 words so they read it."

## Step 3: Identify the Pattern

What's the same every time?

- The 3-paragraph structure
- Positive-first framing
- The word limit

What varies?

- Client name
- Specific accomplishments/blockers/plans

## Step 4: Draft the Skill

```yaml
---
name: weekly-client-update
description: Write weekly status updates for clients. Use when asked to write a client update or weekly status for external stakeholders.
---
```

```markdown
# Weekly Client Update

## What I Need

- Client name
- What shipped last week (1-3 items)
- Current blockers (if any)
- Next week's focus

## Structure

Three paragraphs, under 200 words:

1. **Progress**: Lead with accomplishments. Specific, not vague.
2. **Blockers**: Frame as "we need X to continue." Skip if none.
3. **Next Steps**: What's planned, timeline if known.

## Tone

- Professional but warm
- Confident, not apologetic
- Action-oriented

## Example

Subject: Weekly Update - Dashboard Project

Hi Sarah,

Great progress this week! We completed the dashboard redesign and it's now in staging for review. The new filtering system is particularly smooth.

To keep momentum, we need API credentials for your analytics platform. Once we have those, we can start data integration.

Next week we're focused on connecting live data feeds. Expecting a working demo by Friday.

Best,
[Name]
```

## Step 5: Test It

Try the skill 2-3 times with real scenarios. Check:

- Did it get the tone right?
- Is the format correct?
- Did it include anything it shouldn't?
- Did it miss anything important?

Fix specific issues you find.

## Step 6: Save It

Save to: `~/.claude/skills/[skill-name]/SKILL.md`

Example: `~/.claude/skills/weekly-client-update/SKILL.md`

---

# Quality Checklist

## Good Skills Have

- [ ] **Clear trigger** — Description says exactly when to use it
- [ ] **Specific steps** — "Check X, then Y" not "analyze the situation"
- [ ] **One example** — Shows what good output looks like
- [ ] **Right length** — Useful but readable (<300 lines)
- [ ] **Context section** — Documents key assumptions (for adapted skills)

## Common Problems

| Problem               | Fix                                                                       |
| --------------------- | ------------------------------------------------------------------------- |
| Description too vague | Add specifics: "write weekly client status emails" not "help with emails" |
| No example            | Add one real example of good output                                       |
| Tries to do too much  | Split into 2-3 focused skills                                             |
| Too rigid             | Add "adapt based on context" for variable parts                           |
| Missing context       | Add "Our Context" section with company specifics                          |
| Hardcoded values      | Make thresholds/names explicit so they're easy to find and change         |

---

# Templates

## Process/Tool Skill

```yaml
---
name: [task-name]
description: [What it does]. Use when [specific triggers].
---

# [Task Name]

## What I Need
- [Input 1]
- [Input 2]

## Process
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Output
[What the result looks like]

## Example
[One concrete example]
```

## Document/Content Skill

```yaml
---
name: [document-type]
description: Create [document type] for [audience]. Use when [triggers].
---

# [Document Type]

## Inputs
- [What info is needed]

## Structure
1. [Section 1]: [What goes here]
2. [Section 2]: [What goes here]

## Tone
- [Voice/style notes]

## Length
[Word count or page guidance]

## Example
[Full example]
```

---

# Tips

**Start small.** Personalize one skill, use it for a week, then refine. Don't try to perfect everything upfront.

**Context in CLAUDE.md.** If you have company-wide context (tools, fiscal year, approval chains) in your CLAUDE.md, skills can reference it. But skills should work standalone too.

**When in doubt, ask.** If unsure whether your description is specific enough, or if something should be one skill or two, ask Claude to review your draft.
