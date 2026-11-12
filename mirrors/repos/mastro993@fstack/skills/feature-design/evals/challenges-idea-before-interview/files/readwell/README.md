# Readwell

Lending desk for the Millbrook community library: about 900 members, 6,000 copies, run by volunteers.

- `src/loans.js`: checking out, renewing, and returning copies
- `src/holds.js`: the line of members waiting for a title
- `src/reminders.js`: the nightly email job (`node src/reminders.js`, run by cron at 02:00)
- `GLOSSARY.md`, `docs/adr/`: the words we use and the decisions we made

Runs on one small VPS with SQLite. Members use the website on their phones; there is no native app.

Run the tests with `node --test`.
