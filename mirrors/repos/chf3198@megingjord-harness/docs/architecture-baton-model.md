# Architecture — Governance Baton Model

The baton model is Megingjord's core change-management mechanism. Every
governed change must transit all four roles in sequence before it can merge.

## Role sequence

```
Manager → Collaborator → Admin → Consultant
   ↓           ↓           ↓          ↓
 Ticket      Branch      Verify    Red-team
 + scope     + code      + CI      + approve
```

## Role responsibilities

### Manager

- Files the GitHub issue with `scope:`, `lane:`, `test_strategy:`, and ACs
- Posts `MANAGER_HANDOFF` comment on the issue **before** any file edits
- Sets direction and constraints only; never modifies source files

### Collaborator

- Creates the feature branch (`feat/<N>-slug`) and implements all ACs
- Posts `COLLABORATOR_HANDOFF` after pushing; includes `doc-coverage:` block
- Runs `npm run lint && npm test` before handing off
- Must carry a different `Signed-by` alias than Admin (CI enforces this)

### Admin

- Runs CI checks; verifies test results; opens the PR
- Posts `ADMIN_HANDOFF` confirming signer independence and deploy impact
- Handles environment: credentials, deploy targeting, runtime state
- Does not merge; merge is the Consultant's terminal gate

### Consultant

- Adversarial review: edge cases, risks, doc gaps, goal-constitution alignment
- Posts `CONSULTANT_CLOSEOUT` with `rubric_rating: N/10` (≥7 required to pass)
- Identifies post-merge follow-up tickets for non-trivial residual risk
- Terminal role: merge is blocked until `CONSULTANT_CLOSEOUT` is posted

## Artifact format

| Artifact               | Required fields                                                                                      |
| ---------------------- | ---------------------------------------------------------------------------------------------------- |
| `MANAGER_HANDOFF`      | `scope:` `lane:` `test_strategy:` `acceptance:` `Signed-by:` `Team&Model:` `Role: manager`           |
| `COLLABORATOR_HANDOFF` | `branch:` `commit:` per-AC checklist `doc-coverage:` `Signed-by:` `Team&Model:` `Role: collaborator` |
| `ADMIN_HANDOFF`        | `branch:` `commit:` `signer-independence-check:` `Signed-by:` `Team&Model:` `Role: admin`            |
| `CONSULTANT_CLOSEOUT`  | `ticket:` `verdict:` `rubric_rating:` `Signed-by:` `Team&Model:` `Role: consultant`                  |

## Team & Model signing

Every baton artifact carries structured AI-authorship provenance:

```yaml
Signed-by: Soren Mason # human alias from agents/roster.json
Team&Model: copilot:claude-sonnet-4-6@github
Role: manager # must match the artifact type
```

`scripts/global/baton-artifact-governance.js` validates:

1. All required fields are present and non-empty
2. The `Role:` field matches the artifact name (`MANAGER_HANDOFF` → `manager`)
3. Admin and Collaborator carry different `Signed-by` values

## CI gate chain

`baton-gates.yml` runs gates in dependency order:

1. `collaborator-gate` — validates `COLLABORATOR_HANDOFF` structure
2. `admin-gate` — validates `ADMIN_HANDOFF` + signer independence
3. `consultant-gate` — validates `CONSULTANT_CLOSEOUT` + rubric ≥7
4. `test-evidence` — validates `test_strategy:` matches actual test artifacts
5. `evidence-completeness` — issue must be OPEN; all four artifacts present

## Lane model

| Lane label           | Baton required           | Typical use                 |
| -------------------- | ------------------------ | --------------------------- |
| `lane:code-change`   | Full baton (all 4 roles) | Feature branches, bug fixes |
| `lane:docs-research` | Manager + Consultant     | Wiki pages, research notes  |
| `lane:config-only`   | Admin + Consultant       | Configuration-only changes  |
