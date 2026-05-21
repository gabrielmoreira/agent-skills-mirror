# Standup Format Guide

## Structure

Always three sections, always in this order:

```
**Done**
- [ENG-123] Title of completed issue
- fix: commit message here

**Doing**
- [ENG-124] Title of in-progress issue

**Blockers**
No blockers.
```

---

## Section Rules

### Done
What was completed yesterday.

- One bullet per Linear issue with `completedAt` set
- One bullet per GitHub commit (first line of message, deduplicated, skip merges)
- Format for Linear items: `[IDENTIFIER] Title` — e.g. `[ENG-42] Fix session timeout bug`
- Format for commits: first line of commit message — e.g. `fix: remove duplicate auth check`
- Tense: past tense implied by the format (no verb prefix needed unless the commit message has one)
- If nothing was completed: write `Nothing completed.` as the only bullet

### Doing
What is in progress right now.

- One bullet per Linear issue with state In Progress, Started, or In Review
- Format: `[IDENTIFIER] Title` — same as Done
- Tense: present continuous implied — no need to add "working on" or "continuing"
- If nothing is in progress: write `Nothing in progress.` as the only bullet

### Blockers
What is blocked and why.

- Write `No blockers.` if nothing is blocked
- Only add a blocker entry if the user explicitly mentions one, or if an issue has been In Progress for more than 3 days without a state change (createdAt vs updatedAt gap > 3 days)
- Format: `[ENG-125] Waiting on design approval` — issue + reason
- Never invent blockers

---

## Writing Rules

- No first-person pronouns: no "I", "we", "my", "our"
- No filler phrases: no "today I will", "yesterday I", "as per the discussion", "going to"
- No markdown headers inside the standup body — use bold `**Section**` labels only
- Under 200 words total
- Bullet list only — no paragraphs, no sentences that span multiple lines
- Each bullet is one issue or one commit, nothing more
- No hashtags, no em dashes

---

## Examples

**Full standup (Linear + GitHub):**
```
**Done**
- [ENG-88] Add Redis caching for session lookups
- fix: remove duplicate middleware registration
- chore: bump Next.js to 14.2.0

**Doing**
- [ENG-91] Migrate auth to OAuth2

**Blockers**
No blockers.
```

**Linear only (no GitHub repo configured):**
```
**Done**
- [OPS-14] Set up staging deployment pipeline

**Doing**
- [OPS-15] Configure load balancer health checks
- [OPS-16] Document rollback procedure

**Blockers**
No blockers.
```

**No activity:**
```
**Done**
Nothing completed.

**Doing**
Nothing in progress.

**Blockers**
No blockers.
```
