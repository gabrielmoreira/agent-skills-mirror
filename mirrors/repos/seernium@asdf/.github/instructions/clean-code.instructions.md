---
applyTo: "**/*.ts,**/*.tsx"
description: "KISS, DRY, SOLID, and YAGNI clean code principles"
---

# Clean Code & Pragmatic Engineering Rules

- **Keep it Simple (KISS):** Choose the simplest design that satisfies the current requirements. Avoid "clever" one-liners or high-complexity abstractions that hurt readability.
- **You Aren't Gonna Need It (YAGNI):** Do not write speculative code, classes, or interfaces for hypothetical future requirements. Only build what is needed now.
- **Don't Repeat Yourself (DRY) vs. AHA (Avoid Hasty Abstractions):** 
  - Do not duplicate business logic.
  - However, prefer duplication over a bad abstraction. Only abstract after seeing 3+ identical patterns.
- **Single Responsibility (SRP):**
  - A function must do exactly one thing and be named after its behavior.
  - Max function length: 40 lines. If a function is longer, extract private helper functions.
  - A file must have one primary export or a collection of closely related pure helper utilities.
- **Self-Documenting Naming:**
  - Variables must represent their contents (e.g., `isUserAuthenticated` instead of `auth`).
  - Functions must begin with action verbs (e.g., `fetchUserData`, `validateToken`).
  - Never use arbitrary abbreviations.
