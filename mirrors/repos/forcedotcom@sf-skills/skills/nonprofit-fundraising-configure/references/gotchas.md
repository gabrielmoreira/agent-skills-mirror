# Gotchas

Known failure modes and misreadings encountered while implementing/validating this skill, with
the correct resolution for each.

| Issue | Resolution |
|-------|------------|
| `discover` returns no match for a Fundraising settings operation | Not proof the route is absent — probe the documented `/sobjects/…` or `/query` path directly via `dispatch_readonly` (see `mcp-invocation.md`) |
| `discover` errors with `local_rate_limited` | Not a no-match — see the Error Taxonomy in `mcp-invocation.md` |
| Person Accounts enabled but no active record type | Still a hard-stop — the feature flag alone doesn't guarantee an active `RecordType` row |
| Permission set assignment silently applied to a non-human user | Query `User.UserType` before assigning; skip and report if it resolves to a service/integration user |
| Fundraising enablement treated as a plain `IndustriesSettings` metadata field | It is owned by the `FundraisingSettings` skill (`set-fundraising-org-preference`), gated on an explicit irreversibility confirmation; never write it through `/headless/metadata` |
| `FundraisingConfig`/`GiftDesignation` writes or queries fail even after `orgPreferenceEnabled = true` was confirmed, or return `400 INVALID_TYPE` instead of `404` | Both still depend on that same flag — not a permission or path issue |
| Fundraising permission set name inconsistent across orgs (`force__FundraisingAccess` vs `FundraisingAccess`) | Query `PermissionSet` for both candidate names, don't assume one |
| Permission set group shows `Status = 'Updating'` or `'Outdated'` | Both are non-ready states. Re-query until `'Updated'`; stop and report if it doesn't clear after a couple of retries |
| `IndustriesSettings` feature toggles assumed to be writable through Metadata CRUD or an `sf` deploy | They aren't — the Metadata API isn't available on every org. Two toggles use named headless operations; the other four use the generic Setup org-preference operation. `set-fundraising-org-preference` is also a named operation. Never write any of them through `/headless/metadata` or the CLI |
| Treating Prospect Research (`enablePhilResearchAgent`, Gen AI) as needing its own confirmation gate | It doesn't — same toggle batch, covered by step 5's checkpoint |
| Creating a `RecordAlertCategory` fails with `XML_PARSER_ERROR` | The `Metadata` key is `masterLabel`, not `label` — see `mcp-invocation.md → "Optional enhanced features" → Record Alerts` |
| Tooling `RecordAlertCategory` route returns `404` at the org's current API version | Some orgs don't serve this route at the newest versions — retry one or two versions lower before treating it as a capability gap |
| Assuming Record Alerts is fully configured once the category exists | Only the category is automated; the org preferences are manual guidance on the Record Alert Setup page |
| A toggle's Tooling read-back fails because `IndustriesSettings` isn't available on the org | Report the toggle as "written, unverified" and ask the admin to confirm it in Setup — never fall back to a metadata write or deploy |

More edge cases (write-response trust, resume/idempotency, pause-gate re-verification, the "who am
I" fallback, custom-profile/integration-user limits, donor External-Id) are in
`mcp-invocation.md`'s Error Taxonomy/gate sections and `permission-targeting.md`'s
known-limitations notes.
