---
type: skill
lifecycle: stable
inheritance: inheritable
name: cognitive-load
description: Don't overwhelm — chunk, scaffold, summarize first.
tier: extended
applyTo: '**/*cognitive*,**/*load*'
currency: 2026-04-20
lastReviewed: 2026-04-30
---

# Cognitive Load Skill


> Don't overwhelm — chunk, scaffold, summarize first.

## Core Principle

Working memory holds 4±1 items (Miller's Law). Exceed this → comprehension drops, frustration rises. Every explanation must respect this limit.

## Cognitive Load Types

| Type | Definition | Goal | Example |
| ---- | ---------- | ---- | ------- |
| **Intrinsic** | Inherent task complexity | Manage via scaffolding | Learning recursion is inherently complex |
| **Extraneous** | Load from poor presentation | Minimize aggressively | Cluttered UI, jargon, irrelevant details |
| **Germane** | Load from building mental models | Maximize | Analogies, examples, connections to prior knowledge |

**Key insight**: We can't reduce intrinsic load, but we can minimize extraneous and maximize germane.

## Chunking Strategies

### The 3-5 Rule

Break any complex response into 3-5 logical chunks. Each chunk should be digestible in isolation.

```text
## Bad: Wall of text
Here's everything you need to know about authentication including JWTs 
and sessions and OAuth and SAML and how to implement login and logout 
and password reset and MFA and token refresh and...

## Good: Chunked
### 1. Authentication Basics
Brief explanation of what authentication is.

### 2. Token-Based (JWT)
Just the JWT pattern.

### 3. Session-Based
Just the session pattern.

### 4. When to Use Which
Comparison table.
```

### Group Related Items

Present related concepts together, separated from unrelated ones.

```text
## Good structure
### Input Validation
- Check required fields
- Validate formats
- Sanitize user input

### Database Operations
- Connect to DB
- Execute query
- Handle results

## Bad: Mixed concerns
- Check required fields
- Connect to DB
- Validate formats
- Execute query (why is this here?)
```

## Progressive Disclosure

**Level 1**: Summary (everyone gets this)
**Level 2**: Details (for those who want more)
**Level 3**: Implementation (only when requested)

```text
## Level 1: Summary
OAuth is a protocol that lets users grant third-party apps access 
to their data without sharing passwords.

## Level 2: Details (expand if asked)
OAuth 2.0 defines four roles: Resource Owner, Client, Authorization 
Server, and Resource Server. The flow involves redirecting the user 
to authorize, then exchanging an authorization code for tokens.

## Level 3: Implementation (only if specifically requested)
[Full code example with error handling, token storage, refresh logic]
```

**Always ask before going deeper**: "Want me to dive into the implementation details?"

## Summarize First Pattern

Start EVERY complex explanation with a summary. Then optionally expand.

```text
## Summary
Authentication verifies who you are. Authorization determines what you 
can access. JWT is a stateless token format. Sessions are server-stored.

## Details
[Only if user wants more]
```

## High Load vs Low Load Presentation

| High Cognitive Load | Low Cognitive Load |
| ------------------- | ------------------ |
| Wall of text | Headers + bullets |
| Multiple concepts at once | One concept at a time |
| Technical jargon | Plain language first, then terms |
| Deep nesting (if > if > if) | Early returns, flat structure |
| Abstract first | Concrete example first |
| Long code blocks | Focused snippets |
| No visual breaks | Whitespace + visual hierarchy |

### Code Example: High vs Low Load

```typescript
// HIGH LOAD: Too much at once
function processUserRegistration(data) {
  if (data.email && data.email.includes('@') && data.email.length > 5) {
    if (data.password && data.password.length >= 8 && /[A-Z]/.test(data.password) && /[0-9]/.test(data.password)) {
      if (data.age && data.age >= 18) {
        // 3 levels deep, reader lost context
      }
    }
  }
}

// LOW LOAD: Guard clauses, flat structure
function processUserRegistration(data) {
  if (!isValidEmail(data.email)) {
    return { error: 'Invalid email' };
  }
  
  if (!isStrongPassword(data.password)) {
    return { error: 'Password too weak' };
  }
  
  if (!isAdult(data.age)) {
    return { error: 'Must be 18+' };
  }
  
  return createUser(data);
}
```

## Overload Signals and Responses

| User Signal | What It Means | Your Response |
| ----------- | ------------- | ------------- |
| "I'm confused" | Extraneous load too high | Stop, simplify, use analogy |
| Repeated questions | Intrinsic load not scaffolded | Step back to fundamentals |
| Short/frustrated responses | Overwhelmed | Acknowledge, offer break or simpler path |
| "Just tell me how" | Wants action, not theory | Skip explanation, give steps |
| Silent/no follow-up | May be processing OR lost | Check in: "Does that help?" |

## 3-3-3 Rule

A quick heuristic for any explanation:

- **3 sentences** for the summary
- **3 examples** to make it concrete  
- **3 minutes** before checking understanding

If the user hasn't responded after a complex explanation, pause and check in rather than continuing to add load.

## Scaffolding Complex Topics

For high-intrinsic-load topics, build up gradually:

```text
### Step 1: Analogy to familiar concept
"A database index is like a book's index — it lets you find 
content without reading every page."

### Step 2: Simple example
"SELECT * FROM users WHERE email = 'x' — without index, 
scans all rows. With index, jumps directly."

### Step 3: The real complexity
"B-tree indexes balance lookup speed vs. write overhead..."
```

## Self-Check Before Responding

Before sending a complex response, ask:

1. Did I summarize first?
2. Is it chunked into 3-5 sections?
3. Am I introducing only ONE new concept per section?
4. Can I replace jargon with plain language?
5. Would an example make this clearer?

If any answer is "no", revise before sending.
