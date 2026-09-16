# dx-org-analyze Tests

Structural consistency tests and diff computation tests for the `dx-org-analyze` skill.

## What's covered

| Test | What it checks |
|------|----------------|
| `test_consistency.sh` | Frontmatter fields, SF CLI auth documented, drift formula, severity levels, public API usage, no internal tool references, core rules |
| `test_compute_diff.sh` | Diff computation against fixture data: metadata, permissions, org values, packages, licenses, markdown report structure |

## What's not covered

- **Live org comparison** — requires two authenticated orgs. Keep as manual smoke test.
- **Drift calculation accuracy** — verify manually against known org pairs.
- **Package comparison** — requires real managed packages on the instance.
- **OrganizationSettingsDetail** — not available on all editions; test graceful fallback manually.

## Running

```bash
# Run all tests
bash tests/test_consistency.sh && bash tests/test_compute_diff.sh

# Run individually
bash tests/test_consistency.sh    # Skill structure tests
bash tests/test_compute_diff.sh   # Diff computation tests
```

Exit code `0` on pass, `1` on fail.

## Manual smoke checklist

- [ ] Triggers on "compare these two orgs"
- [ ] Lists authenticated orgs from `sf org list`
- [ ] Asks user to pick source and target
- [ ] Handles `sf org login web` when org not authenticated
- [ ] Report order: Drift Score → Summary → Details
- [ ] Drift percentages are 0-100%
- [ ] Shared components show field/body-level diff
- [ ] Permissions categorized correctly
- [ ] Handles 0 packages gracefully
- [ ] Handles different editions without breaking
- [ ] Gracefully degrades when OrganizationSettingsDetail unavailable
- [ ] Falls back to SecurityHealthCheckRisks for settings
- [ ] REST /limits/ endpoint populates org values
