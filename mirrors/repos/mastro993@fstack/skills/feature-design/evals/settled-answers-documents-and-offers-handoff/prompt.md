---
tags: [feature-design]
max_turns: 120
timeout_seconds: 2400
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash, WebSearch, WebFetch]
---

ok we've been through all the questions on the readwell late-returns thing (code in readwell/). final answers, nothing left to ask me:

1. no push. email reminders, 3 days before the due date and again on the due date
2. members renew straight from the reminder email with one tap, no login
3. up to 2 renewals per loan instead of 1, still 21 days each
4. a hold waiting still blocks the renewal; the email says someone is waiting instead of showing the renew button
5. an overdue loan can't be renewed from the email, only at the desk
6. librarians see each renewal and when it happened in the loan's history

finish the design from here

Input files: readwell/README.md, readwell/package.json, readwell/GLOSSARY.md, readwell/docs/adr/0001-email-is-the-only-member-channel.md, readwell/docs/adr/0002-no-renewal-when-a-hold-is-waiting.md, readwell/docs/adr/0003-one-renewal-per-loan.md, readwell/src/db.js, readwell/src/holds.js, readwell/src/loans.js, readwell/src/reminders.js, readwell/test/loans.test.js
