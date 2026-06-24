---
name: thinking-socratic
description: Use before building when a request is vague, assumption-laden, or "obvious." Ask the clarifying questions that surface hidden requirements and false premises instead of guessing.
---

# Socratic Questioning

## Overview
The Socratic Method, developed by the ancient Greek philosopher Socrates, uses systematic questioning to stimulate critical thinking and illuminate ideas. Rather than providing answers, it draws out knowledge by challenging assumptions and exploring implications.

**Core Principle:** A vague or assumption-laden request is cheaper to clarify than to misbuild. The right question up front surfaces the hidden requirement or false premise that would otherwise be discovered only after the work is done.

Use this as a **pre-build clarification tool**: when a task is underspecified, ambiguous, or rests on an unstated assumption, ask the targeted question before writing code or committing to an approach — don't fill the gap with a guess.

## When to Use
- A request is vague ("make it fast", "add a dashboard", "fix the bug") and you'd otherwise guess the spec
- The request rests on an unstated assumption that might be the actual problem
- Someone asserts something is "obvious" or "everyone knows" — exactly when premises go unchecked
- A proposal jumps to a solution before the problem is defined
- Debugging, to trace a claim ("the system is slow") back to a checkable specific

Decision flow:
```
About to build/commit on an underspecified request? → yes → ASK CLARIFYING QUESTIONS FIRST
Request rests on an unexamined assumption?           → yes → PROBE THE ASSUMPTION
Stated problem is a vague symptom?                   → yes → QUESTION DOWN TO A SPECIFIC
```

## When NOT to Use
- **The request is already clear and specified.** Don't interrogate a well-defined task — just do it. Question-asking theater wastes the user's time.
- **You can answer the question yourself by checking.** If the ambiguity is resolvable by reading the code, running a command, or consulting the docs, do that instead of asking the user.
- **During execution of an agreed plan.** Clarify before building; once the spec is settled, stopping to re-question every step is friction, not rigor.
- **A genuine emergency / time-pressured incident** where acting on 70% understanding beats a round of questions — clarify the one thing that's load-bearing, then act.

## The Six Types of Socratic Questions

### 1. Clarification Questions
**Purpose:** Ensure clear understanding of the claim or concept

| Question | Use When |
|----------|----------|
| "What do you mean by X?" | Term is ambiguous |
| "Can you give me an example?" | Concept is abstract |
| "How does this relate to Y?" | Connection unclear |
| "Can you rephrase that?" | Statement is confusing |
| "What is the main point?" | Discussion is scattered |

**Example:**
> "The system needs to be fast."
> → "What do you mean by 'fast'? What latency is acceptable?"
> → "Fast for whom? End users? Batch processes?"

### 2. Assumption-Probing Questions
**Purpose:** Expose underlying beliefs that may be unexamined

| Question | Use When |
|----------|----------|
| "What are we assuming here?" | Conclusion seems too quick |
| "Is this always true?" | Generalization made |
| "What if that assumption is wrong?" | Testing robustness |
| "Why do we believe this?" | Basis unclear |
| "What would have to change for this to be false?" | Finding conditions |

**Example:**
> "We need microservices for scale."
> → "What are we assuming about our scale requirements?"
> → "Is it always true that microservices scale better?"
> → "What if a modular monolith could meet our needs?"

### 3. Reason & Evidence Questions
**Purpose:** Examine the support for a claim

| Question | Use When |
|----------|----------|
| "What evidence supports this?" | Claim is asserted |
| "How do we know this?" | Source unclear |
| "Are there other explanations?" | Causation assumed |
| "What would prove this wrong?" | Testing falsifiability |
| "Is this evidence sufficient?" | Conclusion seems strong |

**Example:**
> "Users don't want feature X."
> → "What evidence do we have for this?"
> → "How many users did we ask? How were they selected?"
> → "Could there be other explanations for the feedback?"

### 4. Perspective & Viewpoint Questions
**Purpose:** Consider alternative angles and stakeholders

| Question | Use When |
|----------|----------|
| "How would X see this?" | Single perspective dominates |
| "What's the opposite view?" | No alternatives considered |
| "Who disagrees, and why?" | Consensus seems too easy |
| "What are we not seeing?" | Blind spots suspected |
| "How does this look from [role]?" | Stakeholder impact unclear |

**Example:**
> "This API design is intuitive."
> → "How would a new developer view this?"
> → "What would someone from a different language background expect?"
> → "Who might find this confusing, and why?"

### 5. Implication & Consequence Questions
**Purpose:** Explore downstream effects and logical conclusions

| Question | Use When |
|----------|----------|
| "What follows from this?" | Implications unexplored |
| "If this is true, what else must be true?" | Testing consistency |
| "What are the consequences?" | Impact unclear |
| "How does this affect X?" | Ripple effects not considered |
| "What are the second-order effects?" | Only immediate effects seen |

**Example:**
> "We'll add this field to the API response."
> → "What follows from adding this field?"
> → "How does this affect clients that don't need it?"
> → "What are the implications for backward compatibility?"

### 6. Questions About the Question
**Purpose:** Reflect on the inquiry itself; meta-level examination

| Question | Use When |
|----------|----------|
| "Why is this question important?" | Purpose unclear |
| "What would answering this tell us?" | Value of question unclear |
| "Is this the right question?" | May be missing the point |
| "What question should we be asking?" | Reframing needed |
| "Why are we asking this now?" | Timing or priority unclear |

**Example:**
> "Which database should we use?"
> → "Why is this question important right now?"
> → "What would answering this tell us that we don't know?"
> → "Is the real question about database, or about data modeling?"

## Application Patterns

### For Requirements Gathering
```
Stakeholder: "We need a dashboard."
Clarification: "What decisions will the dashboard help you make?"
Assumptions: "What are we assuming about who will use this?"
Evidence: "What data shows this is the highest priority?"
Perspective: "How do different user roles need different views?"
Implications: "If we build this, what won't we build?"
Meta: "Is a dashboard the best solution, or is there another approach?"
```

### For Debugging
```
Report: "The system is slow."
Clarification: "Which operations are slow? How slow?"
Assumptions: "What are we assuming about where the bottleneck is?"
Evidence: "What metrics/traces support this?"
Perspective: "Is it slow for all users or specific patterns?"
Implications: "If we fix this, what else might change?"
Meta: "Is 'slow' the right frame? Could it be 'inconsistent'?"
```

### For Design Review
```
Proposal: "We should use event sourcing."
Clarification: "What do you mean by event sourcing in this context?"
Assumptions: "What are we assuming about our query patterns?"
Evidence: "What evidence suggests this fits our use case?"
Perspective: "How would ops view this? New team members?"
Implications: "What are the consequences for debugging? Storage?"
Meta: "Is the real question about event sourcing or auditability?"
```

## How to Ask Well
- **Ask the load-bearing question first**: lead with the one whose answer most changes what you'll build.
- **One or two questions, not an interrogation**: batch the few that actually gate the work; don't run all six categories for show.
- **Follow the thread**: let each answer narrow the next question instead of working from a fixed script.
- **Resolve what you can yourself**: only ask the user what you can't determine by reading the code, running a command, or checking the docs.
- **Make the assumption explicit**: "This assumes X — is that right?" beats silently guessing X.

## Verification Checklist
- [ ] Used questions from at least 3 of the 6 categories
- [ ] Probed assumptions underlying the topic
- [ ] Explored at least one alternative perspective
- [ ] Examined implications and consequences
- [ ] Reached deeper understanding than starting point
- [ ] Documented key insights from questioning

## Key Meta-Questions
- "What do I think I know, and how do I know it?"
- "What question am I not asking?"
- "What would change my mind about this?"
- "Who knows more about this than I do?"
- "What's the question behind the question?"

## Socrates' Reminder
"I know that I know nothing."

The goal is not to prove others wrong but to discover truth together. The best questions reveal what everyone—including the questioner—doesn't yet understand.
