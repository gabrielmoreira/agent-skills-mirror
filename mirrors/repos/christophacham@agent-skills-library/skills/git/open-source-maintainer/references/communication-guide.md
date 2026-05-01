# Communication Guide

## At a glance

- **Purpose:** Keep public communication warm, efficient, and trust-building.
- **Use when:** You are about to draft a public response (issue/PR comment, close note, duplicate consolidation).
- **Gate:** Before *any* public-facing text, load this file and follow its constraints.
- **Output:** A draft message ready for human approval (clear status + next step, no vague promises).

## Principles

1. **Warm but efficient** - Appreciate contributions without being effusive
2. **Clear expectations** - Say what's needed, don't leave ambiguity
3. **Honest about status** - Don't promise timelines; acknowledge constraints
4. **Graceful declines** - Reject work without discouraging future contribution
5. **Project-first** - Communicate like a steward focused on long-term success

## Tone Adaptation

Check `.github/maintainer/context.md` for project-specific tone. Default: professional and friendly.

## Response Templates

### Acknowledging a Good Issue

```
Thanks for the detailed report! I can reproduce this.

[Brief analysis of the issue]

I'll look into a fix. No ETA, but it's on my radar.
```

### Requesting More Information

```
Thanks for reporting! To help investigate, could you share:
- Steps to reproduce
- Expected vs actual behavior
- Environment (OS, Node version, etc.)

This will help track down the issue.
```

### First-Time Contributor Welcome

```
Welcome, and thanks for your first contribution to [project]!

[Substantive feedback on their PR/issue]
```

### Acknowledging a PR (Before Review)

```
Thanks for the PR! I'll review this when I can.

[Any initial observations or questions]
```

### Requesting Clarification on a PR

```
Thanks for the PR! A couple questions to help me extract the intent:

- [Specific question 1]
- [Specific question 2]

This helps me implement the fix directly while crediting your insights.
```

### Declining a PR Gracefully

```
Thanks for taking the time to contribute this! I appreciate the effort.

After reviewing, I've decided to take a different approach because [reason].

[If applicable: I've opened #XX which incorporates your core idea of [extracted value].]

Your contribution helped clarify the problem - thank you.
```

### Closing a PR After Implementing the Fix

```
Thanks for the PR! I implemented a fix based on your insights in [commit/PR link].

Closing this to keep the implementation in the mainline. Your contribution was very helpful.
```

### Closing as Duplicate

```
This appears to be a duplicate of #XX, which tracks the same issue.

I'm closing this to consolidate discussion. Please add any additional context to the original issue.
```

### Closing as Stale

```
Closing this due to inactivity. If this is still relevant, please reopen with any additional context and I'll take another look.
```

### Closing as Out of Scope

```
Thanks for the suggestion! After consideration, this doesn't fit the current direction of the project because [reason].

[If applicable: You might want to check out [alternative] for this use case.]
```

### Deferring an Issue

```
This is a good idea, but it's not something I can prioritize right now.

I'm labeling this as [label] for future consideration. Feel free to contribute a PR if you'd like to move it forward.
```

### Responding to Frustration

```
I understand the frustration - I wish I could move faster on this too.

[If applicable: Here's what's blocking progress: [reason]]

I appreciate your patience.
```

## Anti-Patterns

Avoid:
- **Empty promises**: "I'll get to this soon" (when you won't)
- **Over-apologizing**: Focus on what happens next
- **Vague rejections**: Always give a reason
- **Ignoring emotions**: Acknowledge frustration when present
- **Template spam**: Personalize responses to the specific situation

## Handling Difficult Situations

### Contributor Submitted Multiple Duplicate PRs
- Review the best one, reference it in closing others
- Thank them for the effort on all of them
- Explain why you chose the one you did

### Frustrated Contributor
- Acknowledge their frustration
- Explain constraints honestly
- Offer what you can (even if it's just visibility)

### Low-Quality Contribution
- Be specific about what needs improvement
- Offer to help if they're stuck
- Don't merge out of guilt - maintain standards

### Competing PRs for Same Issue
- Evaluate on technical merit
- Be transparent about selection criteria
- Thank all contributors
