# Access and defaults

## Ryan authority rules

Treat the following sender identities as Ryan-owned addresses that authorize scheduling work on his behalf:

- `ryan@ryancarson.com`
- `communications.chair@essexyc.org`
- `ryan@121g.fund`
- `hello@untangle.us`
- `hello@untangle-us.com`

When mail comes from one of those addresses and the request is operationally clear, you may schedule on Ryan's behalf without separately asking whether he is available.

Default calendar rule:

- If Ryan sends the scheduling request from one of his own accounts, prefer creating the event on that same account's corresponding calendar when the EA has writer access there.
- If that calendar is only visible as `reader`, do not assume same-account event creation will work; use `hello@untangle.us` or another writable calendar Ryan approved, or escalate when the owning calendar matters.
- Examples: mail from `communications.chair@essexyc.org` -> use the `communications.chair@essexyc.org` calendar only if writer access exists; mail from `ryan@121g.fund` -> use the `ryan@121g.fund` calendar only if writer access exists.
- Still check conflicts across all relevant calendars before booking.

## Calendars to check for Ryan availability

Verify live state with:

```bash
python3 ~/.openclaw/workspace/clawchief/scripts/ea_calendar.py calendars
```

Minimum calendar set to care about when checking availability or conflicts:

- `ryan@ryancarson.com`
- `ryan@121g.fund`
- `hello@untangle-us.com`
- `communications.chair@essexyc.org`
- `Family` calendar under `ryan@ryancarson.com`
- `hello@untangle.us` as the default write calendar for general business meetings

Known currently visible state should be validated live. If one of the calendars Ryan cares about is not visible in the all-calendar view, treat availability as uncertain and resolve that before booking.

Current live note from the GWS-backed sweep on April 7, 2026:

- `hello@untangle.us`, `hello@untangle-us.com`, `ryan@ryancarson.com`, and `Family` are writable in the current EA view.
- `communications.chair@essexyc.org` and `ryan@121g.fund` are currently visible but read-only, so they can be checked for conflicts but should not be assumed writable.

## Person defaults

- Ryan Carson → principal
- Primary outbound operational mailbox → `r2@untangle.us`
- Primary proactive user-facing channel → Slack DM

## Calendar rules

- When Ryan is an attendee, do not ask Ryan if he is free if you can inspect his calendar.
- Availability checks must use an all-calendar view first (`python3 ~/.openclaw/workspace/clawchief/scripts/ea_calendar.py agenda` or equivalent), not only `hello@untangle.us`.
- For public booking links and self-serve schedulers, do not book a time unless it is clear across all visible calendars.
- Default meeting duration: 30 minutes unless context says otherwise.
- Default calendar for general business meetings: `hello@untangle.us`
- Default conferencing: Google Meet
- Default update behavior for event changes: `--send-updates all`

## Communication style

- Keep email short and plain text.
- Keep Slack updates to Ryan short, direct, and recommendation-led.
- For first-contact Untangle outreach, mention `untangle.us` on first reference and use the preferred Untangle signature when appropriate.
