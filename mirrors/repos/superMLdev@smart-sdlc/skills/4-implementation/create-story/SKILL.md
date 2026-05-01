---
name: create-story
description: "Create a single user story outside of a full epic breakdown. Use when the user says 'create a story', 'add a story', or 'I need a new story for X'."
---

# Create Story

## Goal

Create one well-formed user story with full acceptance criteria, ready for sprint planning and JIRA.

---

## Activation

Ask (or infer from the user's request):
1. Which epic does this story belong to?
2. What feature or behavior does it cover?
3. Which persona / user benefits?

---

## Story Creation

Walk through story fields interactively:

### 1. User Story
Draft: "As a {persona}, I want to {action} so that {outcome}."
Present draft. Ask: "Does this capture the intent?"

### 2. Context
Ask: "Any background the developer needs? Existing code, APIs, or architecture decisions to reference?"

### 3. Acceptance Criteria
Guide the user through ACs:
- "What must happen for this to be done?"
- "What happens in the error/edge case?"
- Push for at least 3 ACs (happy path, alternate path, error path)
Format: `Given / When / Then`

### 4. Technical Notes
Ask: "Any specific architecture notes? Which component owns this? Any relevant ADRs or data models?"

### 5. Story Points
Estimate together using the scale:
| Points | Meaning |
|--------|---------|
| 1 | < 2 hours |
| 2 | < half day |
| 3 | ~1 day |
| 5 | 2–3 days |
| 8 | ~1 week |
| 13 | Too large — split it |

### 6. Dependencies
Ask: "Does this block anything? Is it blocked by any other story?"

---

## Save

Assign next available S-ID from the backlog.

Save to `{implementation_artifacts}/stories/S-{id}-{slug}.md`.

Update `{project_name}-backlog.md` to include the new story under its epic.

---

## JIRA Offer

> "Story created: S-{id}: {title}. Want to create this in JIRA now? (`jira-create-story`)"
