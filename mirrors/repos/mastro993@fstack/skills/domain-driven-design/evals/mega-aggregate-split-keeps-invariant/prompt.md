---
tags: [domain-driven-design]
max_turns: 80
timeout_seconds: 1500
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

we keep getting `ConcurrencyError: Product version mismatch` whenever two people edit different backlog items of the same product at the same time. we added retries but it feels hacky and people still lose edits sometimes. what's wrong with our model and how should we fix it? code is in sprintly/

Input files: sprintly/
