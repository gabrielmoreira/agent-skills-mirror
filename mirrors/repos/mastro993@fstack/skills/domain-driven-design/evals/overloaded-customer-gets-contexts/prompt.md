---
tags: [domain-driven-design]
max_turns: 80
timeout_seconds: 1500
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

our backend (shopkeep/) is getting really hard to change. Customer has a million optional fields, every team touches OrderService and we keep breaking each other. we're 3 teams: sales, billing, fulfillment. how should we restructure it?

Input files: shopkeep/
