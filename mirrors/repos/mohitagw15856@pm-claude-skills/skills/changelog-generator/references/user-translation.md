# Commit-to-Changelog Translation: Writing for the People Affected

A changelog's reader asks exactly three questions: *does anything break for me? what can I do now that I couldn't? do I need to act?* Every translation rule serves those three questions.

## The translation table

| Commit says | Changelog says |
|---|---|
| `fix: race condition in token refresh causing intermittent 401s` | "Fixed intermittent logouts some users saw during long sessions" |
| `feat: add cursor-based pagination to /v2/events` | "The events API now supports cursor pagination — fetch beyond 10k events reliably. [docs]" |
| `refactor: extract billing module` | *(nothing — internal changes don't ship to users)* |
| `chore: bump deps` | *(nothing, unless a dep fixed a CVE users care about — then say THAT)* |

The rules embedded there: describe the *symptom* users experienced, not the mechanism you fixed · describe the *capability* gained, not the implementation · silence about internals is a feature, not laziness.

## Ordering is safety-critical

**Breaking changes first, always, loudly** — with the migration path inline (not "see docs"): what breaks, who's affected, what to change, the deadline. A breaking change buried under twelve "Added" bullets is an incident you scheduled. Then: Added → Changed → Fixed → Deprecated (with removal dates) → Security.

## Voice and granularity

- Bullets start with the noun or the verb of impact ("Exports now include…", "Fixed a crash when…"), not with "We"
- One bullet per user-visible change; five commits that shipped one feature = ONE bullet
- Numbers where honest ("~40% faster cold starts on large workspaces")
- Credit external contributors and reporters by handle — it costs nothing and builds a moat

## The omission audit

Before shipping, diff the release tag list against your bullets and justify every omission as "genuinely internal". The scandal-shaped failure isn't a boring changelog; it's the removed feature or quietly-changed default that appears in NO changelog and then in a forum thread.
