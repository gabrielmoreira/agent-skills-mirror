---
name: internal-comms
description: Write internal communications using company formats. Use when writing status reports, leadership updates, company newsletters, FAQs, incident reports, project updates, or any internal communications.
source: anthropics/skills
license: Apache-2.0
---

# Internal Communications

## Document Types

### Status Report
```markdown
# [Project Name] Status Report
**Date:** [Date]
**Author:** [Name]
**Status:** 🟢 On Track / 🟡 At Risk / 🔴 Blocked

## Summary
[2-3 sentence overview]

## Progress This Week
- Completed: [items]
- In Progress: [items]
- Blocked: [items with owners]

## Key Metrics
| Metric | Target | Actual | Trend |
|--------|--------|--------|-------|
| [Metric] | [Target] | [Actual] | ⬆️/➡️/⬇️ |

## Next Week
- [Planned items]

## Risks & Mitigations
| Risk | Impact | Mitigation | Owner |
|------|--------|------------|-------|
| [Risk] | H/M/L | [Action] | [Name] |

## Asks
- [Any blockers needing escalation]
```

### Leadership Update
```markdown
# [Team] Update - [Date]

## TL;DR
[One paragraph executive summary - the only thing busy execs will read]

## Wins
- [Key accomplishment with impact]
- [Key accomplishment with impact]

## Challenges
- [Challenge]: [What we're doing about it]

## Key Decisions Needed
1. [Decision]: [Context, options, recommendation]

## Metrics Dashboard
[Include 3-5 key metrics with trends]
```

### Incident Report
```markdown
# Incident Report: [Title]

**Severity:** P0/P1/P2/P3
**Duration:** [Start] - [End]
**Impact:** [User/revenue impact]
**Status:** Resolved/Monitoring/Active

## Timeline
| Time (UTC) | Event |
|------------|-------|
| [Time] | [What happened] |

## Root Cause
[Clear explanation of what went wrong]

## Resolution
[What was done to fix it]

## Action Items
| Item | Owner | Due Date | Status |
|------|-------|----------|--------|
| [Action] | [Name] | [Date] | ⬜/✅ |

## Lessons Learned
- [What we learned]
- [What we'll do differently]
```

### All-Hands Announcement
```markdown
# [Announcement Title]

Hey team,

[Opening that sets context]

**What's happening:** [Clear, simple explanation]

**Why it matters:** [Impact and benefits]

**What you need to do:** [Specific actions if any]

**Timeline:**
- [Date]: [Milestone]
- [Date]: [Milestone]

**Questions?** [Where to ask]

[Sign-off]
```

## Writing Principles

1. **Lead with the bottom line** - Busy readers skim
2. **Be specific** - Numbers > adjectives
3. **Own problems** - "We missed" not "It was missed"
4. **Action-oriented** - Every problem has a next step
5. **Appropriate tone** - Match urgency to content

## When to use this skill
To write internal communications, use this skill for:
- 3P updates (Progress, Plans, Problems)
- Company newsletters
- FAQ responses
- Status reports
- Leadership updates
- Project updates
- Incident reports

## How to use this skill

To write any internal communication:

1. **Identify the communication type** from the request
2. **Load the appropriate guideline file** from the `examples/` directory:
    - `examples/3p-updates.md` - For Progress/Plans/Problems team updates
    - `examples/company-newsletter.md` - For company-wide newsletters
    - `examples/faq-answers.md` - For answering frequently asked questions
    - `examples/general-comms.md` - For anything else that doesn't explicitly match one of the above
3. **Follow the specific instructions** in that file for formatting, tone, and content gathering

If the communication type doesn't match any existing guideline, ask for clarification or more context about the desired format.

## Keywords
3P updates, company newsletter, company comms, weekly update, faqs, common questions, updates, internal comms
