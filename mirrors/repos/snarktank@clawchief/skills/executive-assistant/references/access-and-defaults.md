# Access and defaults

Customize this file for your own setup.

## Authority rules

Treat the following sender identities as principal-owned addresses that may authorize scheduling work on their behalf when the request is operationally clear:

- `{{PERSONAL_EMAIL}}`
- `{{PRIMARY_WORK_EMAIL}}`
- `{{SECONDARY_CALENDAR_EMAIL_1}}`
- `{{SECONDARY_CALENDAR_EMAIL_2}}`
- `{{SECONDARY_CALENDAR_EMAIL_3}}`

When mail comes from one of those addresses and the request is operationally clear, you may schedule on the principal's behalf without separately asking whether they are free.

## Calendars to check

Verify live state with:

```bash
gog calendar calendars -a {{ASSISTANT_EMAIL}} --json --results-only
```

Minimum calendar set to care about when checking availability or conflicts:

- `{{PRIMARY_WORK_EMAIL}}`
- `{{PERSONAL_EMAIL}}`
- `{{SECONDARY_CALENDAR_EMAIL_1}}`
- `{{SECONDARY_CALENDAR_EMAIL_2}}`
- `{{SECONDARY_CALENDAR_EMAIL_3}}`
- any family / personal shared calendars that materially affect availability

If one of the calendars the principal cares about is not visible in the all-calendar view, treat availability as uncertain and resolve that before booking.

## Defaults

- principal -> `{{OWNER_NAME}}`
- assistant -> `{{ASSISTANT_NAME}}`
- primary outbound operational mailbox -> `{{ASSISTANT_EMAIL}}`
- default write calendar for general business meetings -> `{{PRIMARY_WORK_EMAIL}}`
- primary proactive update route -> `{{PRIMARY_UPDATE_CHANNEL}} -> {{PRIMARY_UPDATE_TARGET}}`
- default conferencing -> Google Meet
- default event change behavior -> `--send-updates all`
