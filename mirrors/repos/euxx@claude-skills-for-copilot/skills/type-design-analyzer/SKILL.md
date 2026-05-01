---
name: type-design-analyzer
description: Analyzes type design quality by rating encapsulation, invariant expression, usefulness, and enforcement. Helps design types that make invalid states unrepresentable. Use when reviewing new types or data models.
argument-hint: "[file or directory with types/interfaces to analyze]"
user-invocable: true
---

# Type Design Analyzer

Evaluate the quality of type definitions, interfaces, and data models. The goal is to identify types that allow invalid states and suggest improvements that make invalid states unrepresentable.

## What Makes a Good Type

1. **Encapsulation**: For class-backed or opaque types, the internal structure is hidden; external code interacts through a defined interface. For structural types (interfaces, type aliases), encapsulation is achieved by keeping types unexported or by wrapping them in opaque branded types.
2. **Invariant expression**: The type's constraints are expressed in its structure, not in documentation or runtime checks.
3. **Invariant usefulness**: The expressed invariants represent meaningful domain constraints.
4. **Invariant enforcement**: The type system (not the programmer) ensures invariants are maintained.

## Analysis Steps

1. **Locate all type definitions** in scope: interfaces, type aliases, classes, enums, discriminated unions.

2. **Identify invariants** for each type — constraints that must always be true:
   - Relationships between fields (e.g., "if `status` is `done`, `completedAt` must be set")
   - Valid value ranges or formats
   - Mutual exclusivity constraints
   - Ordering or structural requirements

3. **Rate each type** across four dimensions (1–10 scale):
   - **Encapsulation** (1–10): Can external code access and mutate internals that should be private?
   - **Invariant Expression** (1–10): Are the invariants visible in the type definition itself, or only in documentation?
   - **Invariant Usefulness** (1–10): Do the expressed invariants represent meaningful real-world constraints?
   - **Invariant Enforcement** (1–10): Does the type system prevent violations at compile time?

4. **Identify specific improvements**: discriminated unions, branded types, opaque types, readonly modifiers, wrapper types.

## Output Per Type

```
### TypeName
**Location**: file:line

**Invariants Identified**:
- [list of constraints that should always hold]

**Ratings**:
- Encapsulation: X/10 — [justification]
- Invariant Expression: X/10 — [justification]
- Invariant Usefulness: X/10 — [justification]
- Invariant Enforcement: X/10 — [justification]
- **Overall**: X/10 — [weighted judgment: Invariant Enforcement counts most; Encapsulation least for structural types]

**Strengths**:
- [what the type does well]

**Concerns**:
- [specific problems with the current design]

**Recommended Improvements**:
[concrete code examples showing better type design]
```

Analysis and feedback only — do not modify code directly.
