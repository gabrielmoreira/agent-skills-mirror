# PR Process and Governance Workflow

Every change to this repo transits the full baton gate chain before merge.

## Baton gate chain

All PRs run `baton-gates.yml` in sequence:

```
Manager → Collaborator → Admin → Consultant
   ↓           ↓           ↓          ↓
 Ticket      Branch      Verify    Red-team
 + scope     + code      + CI      + approve
```

PR body **must** include all four artifacts:

| Artifact               | Required fields                                                                                      |
| ---------------------- | ---------------------------------------------------------------------------------------------------- |
| `MANAGER_HANDOFF`      | `scope:` `lane:` `test_strategy:` `acceptance:` `Signed-by:` `Team&Model:` `Role: manager`           |
| `COLLABORATOR_HANDOFF` | `branch:` `commit:` per-AC checklist `doc-coverage:` `Signed-by:` `Team&Model:` `Role: collaborator` |
| `ADMIN_HANDOFF`        | `branch:` `commit:` `signer-independence-check:` `Signed-by:` `Team&Model:` `Role: admin`            |
| `CONSULTANT_CLOSEOUT`  | `ticket:` `verdict:` `rubric_rating: N/10` (≥7) `Signed-by:` `Team&Model:` `Role: consultant`        |

> Admin and Collaborator must carry **different** `Signed-by` values — CI enforces this.

## Lane model

| Lane label           | Baton required           | Typical use                 |
| -------------------- | ------------------------ | --------------------------- |
| `lane:code-change`   | Full baton (all 4 roles) | Feature branches, bug fixes |
| `lane:docs-research` | Manager + Consultant     | Wiki pages, research notes  |
| `lane:config-only`   | Admin + Consultant       | Config-only changes         |

Label your issue before creating the branch; `baton-gates.yml` reads the label.

## doc-coverage block

Every `COLLABORATOR_HANDOFF` on a `lane:code-change` PR must include:

```yaml
doc-coverage:
  UPDATED: <path> — <what changed>
  N/A: <path> — <reason why not applicable>
```

See [`config/doc-coverage-matrix.yml`](../config/doc-coverage-matrix.yml) for
all surfaces that must be assessed per change type.

## PR checklist

- [ ] `npm run format:check` passes (no formatting drift)
- [ ] `npm run lint` passes (all files ≤100 lines)
- [ ] `npm run lint:readability:ci` passes (no readability regressions)
- [ ] `npm run validate:triage` passes (if skills changed)
- [ ] `npm run validate:compat` passes (if `plugin.json` changed)
- [ ] `.changes/unreleased/<issue>.md` changelog fragment created
- [ ] PR title: `type(scope): subject ≤60 chars #<N>` — conventional commits format
- [ ] Branch name: `feat/<N>-slug` or `fix/<N>-slug`

## PR title format

```
type(scope): subject ≤60 chars #<issue>
```

Allowed types: `feat` `fix` `chore` `docs` `content` `perf` `refactor` `style`
`test` `skill` `hotfix`

## Test strategy values

`test_strategy:` in `MANAGER_HANDOFF` drives the `test-evidence` CI check:

| Strategy      | CI requirement                                                    |
| ------------- | ----------------------------------------------------------------- |
| `tdd-pyramid` | Unit + integration + E2E tests present, or N/A with justification |
| `peer-review` | `CONSULTANT_CLOSEOUT` with `rubric_rating: ≥7/10`                 |
| `drift-lint`  | `docs-drift-maintenance` text appears in issue comment trail      |

## Large PRs (>10 files or >500 LOC)

Include a `BLOCKER_NOTE` section in the PR body explaining why the change is
large and confirming evidence closeout. CI's `danger-required` check enforces this.

## Baton artifact builders

Use the provided helpers to generate correctly formatted artifacts:

```bash
node scripts/global/baton-comment-build.js     # issue comment template
node scripts/global/pr-comment-build.js        # PR body template
node scripts/global/changelog-fragment-build.js # .changes/unreleased/<N>.md
```
