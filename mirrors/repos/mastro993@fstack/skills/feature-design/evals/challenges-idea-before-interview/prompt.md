---
tags: [feature-design]
max_turns: 80
timeout_seconds: 1500
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash, WebSearch, WebFetch]
---

people keep bringing books back late at our library. i'm thinking of adding push notifications to readwell and letting members extend their booking from their phone as many times as they need. can you help me design it? code is in readwell/

Input files: readwell/README.md, readwell/package.json, readwell/GLOSSARY.md, readwell/docs/adr/0001-email-is-the-only-member-channel.md, readwell/docs/adr/0002-no-renewal-when-a-hold-is-waiting.md, readwell/docs/adr/0003-one-renewal-per-loan.md, readwell/src/db.js, readwell/src/holds.js, readwell/src/loans.js, readwell/src/reminders.js, readwell/test/loans.test.js
