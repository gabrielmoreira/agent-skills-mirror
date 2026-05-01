# Rubric Guide — Defining Evaluation Criteria

## Default Dimensions

Every benchmark uses 4 default dimensions. You can add custom dimensions, but these 4 should always be present.

### 1. Correctness (0.0 – 1.0)

**What it measures:** Is the output technically correct?

This dimension checks whether the output produces correct results, uses APIs correctly, follows language semantics, and avoids bugs.

**Good criteria examples:**
- "SQL queries use JOINs correctly and return expected result sets"
- "React component handles state updates without stale closures"
- "Regex matches all specified patterns and rejects invalid inputs"

**Bad criteria examples:**
- "Code is correct" ← too vague, not evaluable
- "No bugs" ← impossible to verify from review alone

### 2. Completeness (0.0 – 1.0)

**What it measures:** Does the output cover all relevant aspects?

This checks whether the output addresses the full scope of the task, includes error handling, considers edge cases, and doesn't leave gaps.

**Good criteria examples:**
- "Includes input validation, error handling, and success/failure responses"
- "Covers CRUD operations for all specified entities"
- "Documents all public API methods with parameters and return types"

**Bad criteria examples:**
- "Output is complete" ← circular
- "Everything is covered" ← not specific

### 3. Pattern Adherence (0.0 – 1.0)

**What it measures:** Does the output follow the patterns the skill teaches?

This is the most skill-specific dimension. It checks whether the output applies the techniques, patterns, and conventions that the target skill instructs.

**Good criteria examples:**
- "Uses the repository pattern for data access instead of direct DB queries"
- "Applies the circuit-breaker pattern for external service calls"
- "Follows BEM naming convention for CSS classes"

**Bad criteria examples:**
- "Follows best practices" ← which practices? Be specific
- "Good patterns" ← not tied to what the skill teaches

### 4. Edge Cases (0.0 – 1.0)

**What it measures:** Does the output handle edge cases the skill warns about?

This checks whether the output anticipates and handles the specific pitfalls, gotchas, and edge cases that the skill calls out.

**Good criteria examples:**
- "Handles empty arrays, null inputs, and concurrent modifications"
- "Considers timezone differences for date comparisons"
- "Handles network timeouts and partial responses gracefully"

**Bad criteria examples:**
- "Handles edge cases" ← which ones?
- "Robust" ← not measurable

## Custom Dimensions

Add domain-specific dimensions when the default 4 don't fully capture the skill's impact.

### How to add

Add extra fields to the rubric object in `benchmark.json`:

```json
{
  "rubric": {
    "correctness": "...",
    "completeness": "...",
    "pattern_adherence": "...",
    "edge_cases": "...",
    "performance": "Considers algorithmic complexity and avoids N+1 queries",
    "security": "Validates all user inputs and uses parameterized queries",
    "readability": "Uses clear variable names and follows established code style"
  }
}
```

All dimensions flow through the evaluation and report pipeline automatically.

### When to add custom dimensions

- The skill teaches performance optimization → add `performance`
- The skill teaches security practices → add `security`
- The skill teaches code style/conventions → add `readability`
- The skill teaches API design → add `api_design`
- The skill teaches testing practices → add `test_quality`

### Naming convention

- Use `snake_case` for dimension keys
- Keep names short but descriptive (1–2 words)
- Avoid overlapping with existing dimensions

## Scoring Scale

All dimensions use the same 0.0 to 1.0 scale:

| Score | Meaning | When to assign |
|-------|---------|---------------|
| **0.0** | Completely fails | Output doesn't address the criterion at all |
| **0.25** | Barely addresses | Mentions the concept but gets it wrong or incomplete |
| **0.5** | Partially meets | Gets the basics right but misses significant aspects |
| **0.75** | Mostly meets | Solid implementation with minor gaps |
| **1.0** | Fully satisfies | Comprehensive, correct, nothing missing |

### Scoring tips

- Score against the **rubric criterion**, not general quality
- A 0.5 is not "average" — it means "partially meets the specific criterion"
- Use 0.25 and 0.75 to express nuance — don't cluster at 0, 0.5, or 1.0
- Score both variants (with/without skill) before comparing them
- If the criterion doesn't apply to the task output, score 0.5 (neutral)

## Writing Good Rubric Criteria

### The formula

A good criterion = **specific behavior** + **observable in the output**

```
"Uses [specific technique] for [specific situation] instead of [common alternative]"
```

### Checklist

For each criterion, verify:

- [ ] Is it **specific** enough that two reviewers would score similarly?
- [ ] Is it **observable** in the output (not about internal reasoning)?
- [ ] Is it **tied to the skill** (not general coding quality)?
- [ ] Does it **differentiate** — would an agent without the skill likely fail it?
