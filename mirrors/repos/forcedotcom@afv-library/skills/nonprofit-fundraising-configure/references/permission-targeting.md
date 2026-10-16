# Permission targeting reference — nonprofit-fundraising-configure

## Org-wide role classification (steps 6, 8)

This skill provisions every active human user on the org, not just the invoking user. Query:

```sql
SELECT Id, Username, Name, UserType, IsActive, ProfileId, Profile.Name
FROM User
WHERE IsActive = true AND UserType = 'Standard'
```

`UserType = 'Standard'` alone is not sufficient — built-in integration/bot accounts (seen live:
"SalesforceIQ Integration", "Insights Integration", "Bot User", "DigitalAgent.*") also carry
`UserType = 'Standard'`. Exclude names matching those patterns before classifying.

Classify each remaining user by `Profile.Name`:

- `'System Administrator'` → **Admin** — gets `FundraisingAccess` (step 6) + `Fundraising_Admin`
  (step 8).
- `'Standard User'` → **Standard** — gets `FundraisingAccess` (step 6) + `Fundraising_User`
  (step 8).
- Anything else → gets `FundraisingAccess` only (step 6); step 8 skips them — never assign a
  group to a user this classification didn't resolve.

**Known limitation**: literal `Profile.Name` matching misses custom or cloned admin/standard
profiles (e.g. an org-specific "Admin - Fundraising" clone). Users on such a profile fall through
to the plain-permission-set-only branch and will not get a permission set group. This is an
accepted gap, not a bug to work around — do not attempt profile-permission introspection to guess
at equivalence.

Idempotency for both steps: query for an existing `PermissionSetAssignment`
(`AssigneeId`+`PermissionSetId`, or the group-assignment equivalent) before creating. Treat a
match as already-satisfied rather than re-creating it (`DUPLICATE_VALUE` otherwise) — this skill
has no persisted resume state, so every invocation replays against live org state.
