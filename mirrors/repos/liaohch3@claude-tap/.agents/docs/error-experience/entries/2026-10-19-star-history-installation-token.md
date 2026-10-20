# Star-history updates failed with the Actions installation token

Date: 2026-10-19

## Failure

Scheduled runs [39070567461](https://github.com/liaohch3/claude-tap/actions/runs/39070567461)
and [39167455090](https://github.com/liaohch3/claude-tap/actions/runs/39167455090)
failed while generating charts. The script replaced all GraphQL errors with a
generic message, hiding the cause.

## Diagnosis

The exact query succeeded locally with the maintainer account. A diagnostic run
using the existing workflow and its unchanged read-only token returned
`Resource not accessible by integration`:
[run 39249803396](https://github.com/liaohch3/claude-tap/actions/runs/39249803396).
This distinguished an authorization failure from a network or rendering failure.

## Correction

Use GitHub's [aggregate star-history endpoint](https://docs.github.com/en/rest/activity/starring#get-repository-star-history)
instead of listing individual stargazers. It supplies paginated weekly totals and
daily counts with metadata read permission. Expand those daily counts into chart
timestamps, sort the reverse-ordered pages, and validate the totals before rendering.
The charts now use day-resolution aggregate data rather than individual star times.

Keep the existing read-only generation job and grant write permission only to
the separate asset publish job. No personal token, new permission, schedule change, or package release is
needed. Preserve sanitized HTTP status and API error messages for future failures.

## Prevention

- Test with the same token class used by automation; a maintainer token alone is
  insufficient evidence of workflow compatibility.
- Prefer aggregate data when no individual user data is needed.
- Cover pagination, day offsets, duplicate weeks, invalid counts, and redacted
  permission errors with regression tests.
- Validate the real API-to-PNG path and the existing workflow's generate and
  publish jobs before declaring recovery.
