---
name: comment-analyzer
description: Analyzes code comments for accuracy, completeness, and long-term maintainability. Detects comment rot and misleading documentation. Use after adding or modifying code comments.
argument-hint: "[file or directory to analyze]"
user-invocable: true
---

# Comment Analyzer

Analyze code comments for accuracy, completeness, and long-term maintainability. Protect codebases from comment rot by ensuring every comment adds genuine value.

## When to Use

- After adding or modifying documentation comments or docstrings
- When reviewing existing comments for potential technical debt
- When verifying comments accurately reflect the code they describe

## Analysis Steps

1. **Verify Factual Accuracy**: Cross-reference every claim against the actual code.
   - Function signatures match documented parameters and return types
   - Described behavior aligns with actual code logic
   - Referenced types, functions, and variables exist and are used correctly
   - Edge cases mentioned are actually handled
   - Performance or complexity claims are accurate

2. **Assess Completeness**:
   - Critical assumptions or preconditions are documented
   - Non-obvious side effects are mentioned
   - Complex algorithms have their approach explained
   - Business logic rationale is captured when not self-evident

3. **Evaluate Long-term Value**:
   - Comments that merely restate obvious code should be flagged for removal
   - Comments explaining _why_ are more valuable than those explaining _what_
   - Comments that will become outdated with likely future changes should be reconsidered
   - Avoid comments referencing temporary states or transitional implementations

4. **Identify Misleading Elements**:
   - Ambiguous language with multiple possible meanings
   - Outdated references to refactored code
   - Assumptions that may no longer hold
   - TODOs or FIXMEs that may already be addressed

## Output Format

```
## Summary
Brief overview of the analysis scope and findings.

## Critical Issues
Comments that are factually incorrect or highly misleading.
- Location: [file:line]
- Issue: [specific problem]
- Suggestion: [recommended fix]

## Improvement Opportunities
- Location: [file:line]
- Current state: [what's lacking]
- Suggestion: [how to improve]

## Recommended Removals
- Location: [file:line]
- Rationale: [why it should be removed]

## Positive Findings
Well-written comments that serve as good examples (if any).
```

Analysis and feedback only — do not modify code or comments directly.
