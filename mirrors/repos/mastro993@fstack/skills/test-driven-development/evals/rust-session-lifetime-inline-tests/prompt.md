---
tags: [test-driven-development]
max_turns: 80
timeout_seconds: 1500
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

add an absolute max lifetime to sessions in sessions-rs: however often a session is touched, it expires once max_lifetime has passed since it was created (we'll default to 12h). make it configurable when creating a session.

Input files: sessions-rs/
