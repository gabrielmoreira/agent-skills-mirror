# Semantic Docs Update Rules

Update docs only when durable semantics changed.

Update relevant top-level or scoped docs for changes to:
- `PROJECT_INTENT.md`: project intent, scope, non-goals, users, journeys, or constraints
- `REPO_INVENTORY.md`: entry points, validation commands, directories, or external boundaries
- `ARCHITECTURE.md` / `DEPENDENCY_RULES.md`: architecture or dependency direction
- `DATA_FLOW.md`: transformation pipelines, side-effect flows, or error states
- `DATA_MODEL.md`: persisted/serialized formats, schemas, API contracts, or shared types
- `INVARIANTS.md`: lifecycle rules, state transitions, validation, or ownership rules
- `CONTRACTS.md`: public/internal contracts between modules/packages/services
- `TESTING_STRATEGY.md` / `VALIDATION_BASELINE.md`: test approach or known-good validation commands
- `RISK_REGISTER.md` / `DESIGN_ISSUES.md`: known risks, design issues, deferred decisions, or risk status
- `CHANGE_GUIDE.md`: safe-change workflow guidance discovered during implementation

When artifact headers exist, update `Status`, `Evidence`, or `Last validated` only when the change or validation materially affects planned/observed/currentness.

Non-duplication rules:
- Update the owner artifact first; update router/index docs only with links or short pointers.
- Do not copy detailed architecture into `CHANGE_GUIDE.md` or `AGENTS.md`.
- Do not copy scoped-local details into top-level docs unless they changed repo-wide guidance.
- If multiple docs mention the same concept, keep only one detailed source of truth and replace other copies with references.

Do not update docs for:
- purely mechanical edits
- local implementation detail with no durable semantic meaning
- test-only changes that do not reveal changed risk/invariant guidance
- formatting, naming, or low-level cleanup without architecture impact

When scoped docs exist:
- update matched scoped docs first
- update owner `CONTRACTS.md` for contract changes
- update consumer docs only for local usage/risk changes
- update `SCOPES.md` if scope status, ownership, contracts, or evidence changed
- update top-level docs only if repo-level summary/guidance changed
- leave broader reconciliation for codebase-recon Pass 8 when multiple scopes are affected
