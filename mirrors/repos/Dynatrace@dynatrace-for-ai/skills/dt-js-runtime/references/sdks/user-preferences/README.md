# User Preferences (`@dynatrace-sdk/user-preferences`)

> Env: ⚠️ **BROWSER-ONLY — do NOT use in server-side JS runtime functions.**
> Status: current

Reads the logged-in user's UI preferences (theme, language, regional format, timezone) from the browser app shell. These are frontend concerns and are **not available in the server-side JS runtime**. For server-side user context, use [`app-environment`](../app-environment/README.md) (`getCurrentUserDetails`).

## Key exports (frontend use only)

All synchronous, no scopes:

| Function | Returns | Purpose |
|---|---|---|
| `getLanguage()` | `string` | User's preferred language |
| `getRegionalFormat()` | `string` | User's regional format |
| `getTheme()` | `ThemeType` | User's preferred theme |
| `getTimezone()` | `string` | User's preferred timezone (ISO 8601 / tz database format) |

Canonical reference: https://developer.dynatrace.com/develop/sdks/user-preferences/
