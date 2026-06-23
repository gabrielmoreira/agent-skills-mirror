---
name: solid-refactorer
description: ''
---

# Skill: SOLID Code Refactoring Checklist

This skill directs the agent through a step-by-step checklist to decompose, decouple, and refactor code, preventing monolithic and buggy "vibe" structures.

## Steps
1. **Single Responsibility (SRP):** Inspect the module. Split files or functions that handle multiple domains (e.g., combining client formatting with server-side validation/database querying).
2. **Dependency Inversion (DIP):** Make external dependencies injectable. Behind-the-scenes calls to external libraries (like `Stripe` or custom fetching helpers) should be abstracted through local TypeScript interface boundaries and injected.
3. **Open/Closed Strategy Pattern:** Replace nested `switch` or massive `if-else` blocks managing multiple execution behaviors with a registry mapping keys to action strategy handlers.
4. **Behavior Verification:** Always run all existing unit and integration tests before executing the code changes. Repeat after making changes to verify zero regressions.
