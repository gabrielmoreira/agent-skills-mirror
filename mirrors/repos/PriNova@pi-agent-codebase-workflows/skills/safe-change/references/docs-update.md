# Semantic Docs Update Rules

Update docs only when durable semantics changed.

Update relevant top-level or scoped docs for changes to:
- architecture or dependency direction
- data model, persisted/serialized formats, schemas, API contracts, or shared types
- invariants, lifecycle rules, state transitions, validation, or ownership rules
- side-effect boundaries
- public/internal contracts between modules/packages/services
- known risks or risk status
- safe-change workflow guidance discovered during implementation

Do not update docs for:
- purely mechanical edits
- local implementation detail with no durable semantic meaning
- test-only changes that do not reveal changed risk/invariant guidance
- formatting, naming, or low-level cleanup without architecture impact

When scoped docs exist:
- update matched scoped docs first
- update owner `CONTRACTS.md` for contract changes
- update consumer docs only for local usage/risk changes
- update top-level docs only if repo-level summary/guidance changed
- leave broader reconciliation for codebase-recon Pass 8 when multiple scopes are affected
