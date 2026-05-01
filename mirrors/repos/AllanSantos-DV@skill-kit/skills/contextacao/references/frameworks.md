# Questioning Frameworks

## 5 Whys

Ask "why?" 5 times to reach the root cause.

**Application in context analysis**: when the user asks for something, question the motivation until you find the real problem.

Example:
1. Why do we need a deployment skill? → Because deployment fails frequently
2. Why does deployment fail? → Because configs change between environments
3. Why do configs change? → Because there's no standardization
4. Why is there no standardization? → Because each dev configures manually
5. Why do they configure manually? → Because there's no template/automation

**Result**: the real skill should be about config standardization, not deployment.

---

## First Principles

Decompose the problem down to fundamental facts, discarding assumptions.

**Application in context analysis**: separate what is a **verifiable fact** from what is an **inherited assumption**.

Key questions:
- What do I know for certain (fact)?
- What am I assuming by convention?
- If I started from scratch, would I reach the same conclusion?

---

## Pre-mortem

Imagine the solution failed. Ask: **why did it fail?**

**Application in context analysis**: before creating/implementing, simulate failure scenarios.

Key questions:
- If this went wrong in production, what would be the most likely cause?
- What did I overlook that someone more experienced in the domain would catch?
- Which part of the solution is most fragile?

---

## MECE (Mutually Exclusive, Collectively Exhaustive)

Ensure the analysis covers everything without overlap.

**Application in context analysis**: when decomposing the subject into the 6 axes (assumptions, scope, dependencies, sources of truth, failure modes, stakeholders), each point should be in exactly one axis, and together they should cover 100% of the relevant context.

---

## Inversion

Instead of asking "how to do it right?", ask "how to guarantee it goes wrong?"

**Application in context analysis**: identify anti-patterns and pitfalls before proposing the solution.

Key questions:
- What would I do if I wanted this skill to fail?
- What's the fastest way to deliver something useless?
- What would a critical reviewer say about this approach?
