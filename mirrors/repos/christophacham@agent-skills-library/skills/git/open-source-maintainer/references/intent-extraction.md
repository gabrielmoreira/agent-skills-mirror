# Intent Extraction

## At a glance

- **Purpose:** Convert raw issues/PRs into “what the user actually needs” + actionability.
- **Use when:** Analyzing items, mapping duplicates/relationships, or writing briefs.
- **Output:** Intent, severity, sentiment, actionability, relationships, and the minimal next step.

## Purpose

Surface the real need behind issues and PRs, not just the stated request.
Semantic keyword lists (intent, needs-info cues) are config-driven and can be derived from repo templates.

## Issue Intent Extraction

### Step 1: Classify Type

| Type | Signals |
|------|---------|
| Bug | "doesn't work", "error", "crash", "broken", stack traces |
| Feature | "would be nice", "could you add", "support for", "feature request" |
| Question | "how do I", "is it possible", "what does", question marks |
| Support | Configuration help, usage questions, troubleshooting |
| Meta | Project governance, contributing, community |

### Step 2: Extract Underlying Need

Ask: "What is the user actually trying to accomplish?"

Example:
- **Stated**: "Add --verbose flag to install command"
- **Underlying need**: User can't debug why installation fails
- **Better solution might be**: Better error messages, not a flag

### Step 3: Assess Severity

| Level | Criteria |
|-------|----------|
| Critical | Security vulnerability, data loss, complete breakage |
| High | Major functionality broken, no workaround |
| Medium | Functionality impaired, workaround exists |
| Low | Minor inconvenience, cosmetic, edge case |

### Step 4: Gauge Emotional State

| Tone | Signals | Response Adjustment |
|------|---------|---------------------|
| Frustrated | "still broken", "why hasn't", urgency | Acknowledge, prioritize response |
| Enthusiastic | "love this", "excited to", "great project" | Match energy, encourage |
| Neutral | Factual reporting | Standard professional tone |
| Confused | "I don't understand", "not sure if" | Patient, educational |

Sentiment scoring uses a small lexicon by default; adjust the config for non-English repos as needed.

### Step 5: Check Actionability

- **Actionable**: Clear reproduction steps, specific request, enough context
- **Needs info**: Missing environment, vague description, can't reproduce
- **Blocked**: Depends on external factor, needs design decision

## PR Intent Extraction

**PRs are intelligence sources, not merge candidates.** Your job is to extract the problem, understand the approach, and implement the fix yourself.

### Step 1: Identify the Problem Being Solved

Read:
1. PR title and description
2. Linked issues (if any)
3. Commit messages
4. The actual code changes

Ask: "What problem does this solve? Why did the contributor think this was worth doing?"

### Step 2: Assess the Approach

| Aspect | Questions |
|--------|-----------|
| Correctness | Does it actually solve the problem? |
| Completeness | Are edge cases handled? Tests included? |
| Fit | Does the approach match project patterns? |
| Scope | Is it focused or does it include unrelated changes? |

### Step 3: Extract Implementation Guidance

PRs tell you exactly how to fix the problem. Extract:
- **Root cause**: What did the contributor identify as the problem?
- **Solution approach**: What's the core fix? (e.g., use `path.sep` instead of `/`)
- **Edge cases**: What did they handle that you might miss?
- **Test cases**: What scenarios did they consider?

Use this to implement your own fix. The PR is your requirements document and reference implementation.

### Step 4: Assess Contributor Context

| Factor | How to Determine | Impact |
|--------|------------------|--------|
| First-time? | Check if first contribution to repo | Warmer welcome, more patience |
| Experienced? | Previous accepted PRs | Can be more direct |
| Maintainer? | Has write access | Different review bar |
| Drive-by? | No previous engagement | May not respond to feedback |

## Relationship Mapping

### Automated Detection (in triage.ts)

The script detects:
- Explicit mentions: "Fixes #42", "Related to #30"
- Number references: "#42" in body/comments

### Manual Enrichment

During analysis, also identify:
- **Duplicates**: Same underlying issue, different reporters
- **Root cause**: Multiple symptoms of one problem
- **Dependency**: Item A must be resolved before B
- **Conflict**: PRs that can't both be used as the basis for implementation
- **Quality**: Whether a PR actually solves the linked issue (strong/medium/weak)

### Recording Relationships

In item markdown:
```markdown
## Relationships
- Duplicate of [ISSUE:28] (same root cause)
- Addressed by [PR:38], [PR:40] (competing fixes)
- Blocks [ISSUE:50] (depends on this fix)
```

## Common Patterns

### The "Same Bug, Many Reports" Pattern
Multiple issues report the same underlying problem. Signs:
- Similar error messages
- Same affected functionality
- Clustering in time

Action: Identify the canonical issue, close duplicates with references.

### The "Competing PRs" Pattern
Multiple PRs solve the same problem differently.

Action: Evaluate each on merit, pick the best, close others with thanks.

### The "Feature Creep PR" Pattern
PR starts solving one thing, grows to include unrelated changes.

Action: Request scope reduction or split into multiple PRs.

### The "XY Problem" Pattern
User asks for X (their attempted solution) when they really need Y.

Action: Identify Y, address the actual need.

## Opportunity Extraction

During analysis, look for improvements not explicitly requested:
- Documentation gaps revealed by questions
- UX friction implied by repeated confusion
- Reliability gaps implied by flaky or brittle fixes

Record these as opportunity notes and convert high‑impact items into briefs.
