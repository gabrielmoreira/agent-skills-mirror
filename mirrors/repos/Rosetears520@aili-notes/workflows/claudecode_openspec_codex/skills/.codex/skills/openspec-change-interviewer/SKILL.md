---
name: openspec-change-interviewer
description: Interview the user to clarify and complete an OpenSpec change package under openspec/changes/CHANGE_ID/ by reading existing proposal/design/tasks and specs files, asking high-information-gain questions (no assumptions), then writing the refined content back into those files and validating with openspec validate CHANGE_ID --strict.
---

# OpenSpec Change Interviewer (Instruction-Only)

Follow these instructions when this skill is invoked to refine and complete an OpenSpec change directory. The output MUST be persisted as edits inside `openspec/changes/<change-id>/` (not only in chat).

## Invocation

- Preferred: `$openspec-change-interviewer <change-id>`
- If `<change-id>` is missing, ask the user for it once, then proceed.

## Non-negotiables

- Do not “fill in” requirements/design/AC by guessing. Ask questions; record unresolved items as open questions.
- Merge rather than rewrite: preserve existing author content and structure whenever possible.
- If restructuring is necessary, keep original text under an appendix section in the same file (so reviewers can diff intent).
- Never record unconfirmed information as fact. Use `Assumption:` / `Open Question:` labels.

## Phase A — Read & Diagnose (before interviewing)

1. Resolve the change directory

- `change_dir = openspec/changes/<change-id>/`
- If missing, stop and ask whether to create scaffolding (do not create without confirmation).

2. Inventory and read (this order)

- `tasks.md` (or `task.md` if present instead)
- `proposal.md` (if present)
- `design.md` (if present)
- `specs/` directory (if present): read all `*.md`/`*.txt` spec files (start with the smallest/highest-level file first if there are many).

3. Build a concise “gap list” to drive questions
   Focus on missing or ambiguous items that would block implementation/review:

- Goal/success criteria unclear or unmeasurable
- In-scope vs out-of-scope not explicit (MVP boundary)
- Primary flows/journeys incomplete (including failure paths, retries, rollback)
- Interfaces undefined (API/event shapes, auth, versioning, error codes)
- Data model unclear (entities/fields, lifecycle, constraints, migrations)
- Architecture decisions missing (partitioning, dependencies, trade-offs)
- Non-functional requirements missing (perf, reliability, security, privacy)
- Acceptance criteria not executable (no clear “how to verify”)
- Operational concerns missing (observability, alerts, runbooks)

Do not start writing “final” text yet—only prepare the questions.

## Phase B — Interview (multi-round, high-information-gain)

Ask questions in rounds (no fixed per-round limit). Decide how many to ask per round dynamically based on the remaining gaps and the user’s responsiveness. Start broad, then drill down. Keep each question concise and prioritize by information gain. If the user says `先这样` or `按目前信息写回`, stop asking and proceed to Phase C with remaining items recorded as open questions.

When listing questions, use a Markdown ordered list and rely on auto-numbering (write `1.` for every item) to avoid numbering gaps.

### Order of inquiry

1. Goals and success

- Who benefits? What pain is solved?
- What measurable outcome indicates success?
- What constraints are non-negotiable (timeline, compatibility, compliance)?

2. Scope boundaries

- In-scope vs out-of-scope (explicit)
- MVP vs follow-ups/roadmap
- Backward compatibility expectations

3. Key flows

- Happy path step-by-step
- Failure/timeout paths and user-visible behavior
- Idempotency, retries, rollback, and partial failure handling

4. Data and interfaces

- Entities and fields (required/optional), validation rules
- APIs/events: request/response, authz/authn, versioning, error codes
- Data ownership and source-of-truth

5. Architecture and trade-offs

- Where does the logic live (modules/services)?
- Alternatives considered and why rejected
- Performance, consistency, caching, and scaling assumptions

6. Risks and acceptance

- Risk register + mitigations
- Test strategy (unit/integration/e2e/manual) + runnable commands where possible
- Executable acceptance criteria

### Branching triggers (ask immediately when mentioned)

- Multi-tenancy → isolation model, tenant identifiers, cross-tenant access controls, migrations
- Offline/background sync → conflict resolution, retry/backoff, state reconciliation
- Security/privacy/GDPR → data retention, audit logs, encryption, PII handling
- UI/UX → empty/loading/error states, permission-denied copy, a11y/i18n needs

## Phase C — Write-back (persist into the change directory)

Write updates into existing files; create new files only if there is no natural home. Prefer ASCII kebab-case filenames for new specs (e.g., `api.md`, `data-model.md`, `migration.md`, `acceptance.md`, `ux.md`).

### `tasks.md` (or `task.md`)

- Ensure tasks are actionable and sequenced.
- For each task, include acceptance and test details (either inline or as a short sub-block) so completion is verifiable.
- Preserve any existing task conventions (e.g., `[#R12]` refs) rather than inventing a new format.

### `proposal.md`

- Fill missing: Why/Goals, In/Out of scope, Success metrics, Impact areas, Rollout/rollback, Risks, Open questions.
- Keep it decision-light: proposal explains “what/why” and high-level impacts.

### `design.md`

- Capture the chosen approach and trade-offs: architecture, data model, interfaces, failure handling, security, observability, migration/compat plan, alternatives, decision log.
- If options were discussed, record: choice + rationale + rejected alternatives.

### `specs/*.md` (implementation-closest)

Goal: make specs implementable and testable. Put details closest to code behavior here.

- If this repo uses OpenSpec delta style, keep the required headers:
  - `## ADDED Requirements`, `## MODIFIED Requirements`, `## REMOVED Requirements`, `## RENAMED Requirements`
  - `### Requirement: ...`
  - At least one `#### Scenario: ...` per requirement
- Add concrete details: fields, examples, state transitions, error handling, auth rules, and acceptance criteria mapping.
- Maintain traceability by linking: requirement → design decision → acceptance/test.

If you restructure a file, append `## Appendix: Original Draft` and move the prior text there.

## Validation

After write-back, validate and fix formatting issues using the repo’s OpenSpec CLI (not via Python runners).

Try in this order:

1. If `openspec` is available on PATH:

- `openspec validate <change-id> --strict`

2. If not on PATH, try common repo-local entrypoints (use the first one that exists/is executable):

- `./openspec validate <change-id> --strict`
- `./bin/openspec validate <change-id> --strict`
- `./tools/openspec validate <change-id> --strict`
- `./scripts/openspec validate <change-id> --strict`

3. If none of the above exist, report that validation could not be run automatically and ask the user for the correct validation command for this repo. Do not guess.
