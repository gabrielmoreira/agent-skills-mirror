# Competency CRUD workflow — Full Spec

Consult this reference whenever the admin's ask touches competency records (list, install, create, edit, activate/deactivate, verify, delete).

Once Phase 5 of `enable-call-scoring.sh` confirms the feature is enabled (or Phase 1 detects State 3/4), Claude runs the `Next:` script from `enable-call-scoring.sh` directly, in the same turn. Records are managed via Tooling API on `EnablementCompetencyDef` (setup entity, keyPrefix `1nA`, module `conversation-udd`). Cap: **8 simultaneously active** per org (`CoachingCompetenciesFeature.MAX_ACTIVE_COMPETENCIES`).

All scripts share `shared/auth.sh` / `resolve_org_auth` (same fail-fast messages, token-reuse across chained invocations). Tooling API writes go through `sf api request rest` where practical; a subset (custom-CRUD variants, best-practice installer) drops to raw `curl` for finer request shape.

**Two parallel families:** generic scripts (`{create,edit,toggle,get}-competency.sh`) work on any competency; custom-CRUD variants (`*-custom-competency.sh`) harden the write path with SpecificCallsOnly filter JSON and richer validation. Prefer the custom variants when the admin's intent is unambiguously custom (S5-created); fall back to generic on OOTB or unknown-provenance records.

## Table of contents

- [S3 · List](#s3--list--list-competenciessh-alias---verbose--json)
- [S4 · Install OOTB set](#s4--install-ootb-set--install-ootb-competenciessh-alias---dry-run)
- [S4b · Install best-practice set](#s4b--install-best-practice-set--install-best-practice-competenciessh-alias---dry-run---only-name1name2)
- [S5 · Create custom (conversational)](#s5--create-custom-conversational--create-custom-competencysh-alias-payloadjson)
- [S6 · Edit](#s6--edit--edit-competencysh-alias-name-or-id--or-edit-custom-competencysh-alias-name-or-id-)
- [S7 · Activate/deactivate](#s7--activatedeactivate--toggle-competencysh-alias-name-or-id-activatedeactivate-or-toggle-custom-competencysh-alias-name-or-id-activatedeactivate)
- [S8 · Fetch a record](#s8--fetch-a-record--get-competencysh-alias-name-or-id---field-name-or-get-custom-competencysh-alias-name-or-id---field-name)
- [S9 · Verify](#s9--verify--verify-ootb-competenciessh-alias-name-)
- [S10 · Delete](#s10--delete--no-dedicated-script-yet-use-sf-cli-directly)
- [Execution sequence — by admin intent × org state](#execution-sequence--by-admin-intent--org-state)
- [Chaining checkpoints](#chaining-checkpoints-claude-must-respect)

## S3 · List — `list-competencies.sh <alias> [--verbose|--json]`

Enumerates current competencies. Shows `Active / 8 (max)` count.

**Output modes** (per admin-comms rule #5 — admin-safe by default):

- **Default** — `MasterLabel` + `IsActive` icon + `EvaluationScope` + `Description`. **No** record Ids, DeveloperNames, or Template enum keys. Safe to forward directly to the admin.
- **`--verbose`** — Default fields PLUS `DeveloperName`, `SourceCompetencyTemplate` enum, and `Id`. Use only when the admin explicitly asks to debug or share with support.
- **`--json`** — Raw record JSON for the calling agent to parse. Never forward this to the admin directly.

## S4 · Install OOTB set — `install-ootb-competencies.sh <alias> [--dry-run]`

Creates the 6 PRD-canonical competencies (Active Listening Skills, Relationship Building, Discovery Questioning, Objection Handling, Value Proposition Focus, Closing Urgency) with prompt bodies taken verbatim from `assets/ootb-competencies.json`. Idempotent: matches by `SourceCompetencyTemplate` and skips already-installed rows.

**`--list` mode** (`install-ootb-competencies.sh --list`) — no org alias, no auth, no write. Renders the 6 competencies (name + what each evaluates) as a markdown table straight from the asset file. This is what backs rule #13's OOTB-vs-custom question: show this table to the admin *before* they decide between the OOTB set and building custom competencies, not after installing.

Checks `IsEciCallScoringEnabled` on `ConversationalIntelligenceSettings` before writing — refuses with a pointer to `enable-call-scoring.sh` if Call Coaching isn't enabled yet, rather than creating competency records the admin can't see or use until it is.

Output is admin-safe by default — no DeveloperName suffixes, Template enum keys, or record Ids leak into per-row lines. When the org is already at the 8-active cap, records land inactive with an "activate later" hint.

**Always follow with S9** on first-time setup — see the S9 carve-out for why the verify table is the one place entity-level detail is surfaced to the admin by design.

## S4b · Install best-practice set — `install-best-practice-competencies.sh <alias> [--dry-run] [--only "Name1,Name2,..."]`

Creates the 7 Momentum best-practice reference prompts from `assets/best-practice-competencies.json` (Business Problem Diagnosis, Change Management Navigation, Discovery Excellence, Executive Vision Alignment, Multi-Stakeholder Orchestration, Product Knowledge, Enterprise Value Articulation). Parallel to S4 but with richer PRD/PURPOSE-structured prompt bodies.

Same idempotency (by `SourceCompetencyTemplate`) and cap-fallback behavior as S4. Use `--only "Name1,Name2"` to install a subset by `MasterLabel`.

## S5 · Create custom (conversational) — `create-custom-competency.sh <alias> <payload.json>`

The bash primitive expects a JSON payload with at minimum `MasterLabel` and `EvaluationInstructions`; optional `Description`, `EvaluationScope` (`AllCalls` | `SpecificCallsOnly`), `EvaluationConditions` (FilterCriteria JSON, required when scope is `SpecificCallsOnly`), `IsActive` (default `true`), `SourceCompetencyTemplate` (leave empty for custom).

**Claude's conversational role — the Q1-Q4 sequence.** When the admin asks to add a custom competency, do NOT jump to drafting. Ask these four in order, one at a time:

- **Q1. What sales skill are you trying to score?** One sentence in the admin's own words. Anchor for the whole competency.
- **Q2. What does *good* look like on a call?** 2-3 observable, call-audible behaviors (not internal states).
- **Q3. What does *not good* look like?** 2-3 concrete behaviors indicating the skill is missing or poorly applied, at the same bar.
- **Q4. Active right now?** Yes → `IsActive=true` (auto-falls back to inactive if org is at the 8-active cap; script prints an "activate later" hint). No → `IsActive=false`.

Do NOT ask about call-filter scope (Enterprise-only, discovery-only, etc.). Competencies apply to all calls today regardless of the `EvaluationScope`/`EvaluationConditions` record fields, so asking creates a false expectation for the admin. The bash primitive still accepts those fields for a future re-enablement — see S5 header — but the conversational flow leaves them defaulted (`AllCalls`) and empty.

After Q1-Q4, draft the `EvaluationInstructions` prompt using the **PURPOSE / KEY AREAS / positive-negative-indicators / EXAMPLE** structure mirrored from `assets/best-practice-competencies.json`. Show the draft to the admin — e.g. "I've put together a draft based on your answers, following the same structure as best practices:" — never "best-practice competencies" in admin-facing text; that's the internal asset/script name, not admin language (rule #6). Iterate once if they request changes, then:

1. Write the payload to a temp JSON file — `MasterLabel` (from Q1's skill name, title-cased), `EvaluationInstructions` (the drafted prompt), `Description` (a 1-sentence version of Q1), `IsActive` (from Q4). Omit `EvaluationScope`/`EvaluationConditions` — the script defaults to `AllCalls`.
2. Invoke `create-custom-competency.sh <alias> <payload.json>`.
3. Delete the temp JSON afterwards.
4. Chain into S9 verify (passing the just-created `MasterLabel`) to confirm and show the admin what got configured.

**Do not skip Q1-Q4.** The eval-readiness bar requires that admins go through a structured authoring flow, not a "just draft me something for X" one-shot. If the admin insists on skipping, still capture the minimum needed for `MasterLabel` + `EvaluationInstructions` — but push back once.

## S6 · Edit — `edit-competency.sh <alias> <name-or-id> ...` OR `edit-custom-competency.sh <alias> <name-or-id> ...`

Both take `--instructions[-file] <>` and/or `--description <>`. PATCH updates preserve Id, DeveloperName, IsActive, EvaluationScope, SourceCompetencyTemplate. Enforce 16000 / 255 char field caps.

Prefer `edit-custom-competency.sh` for competencies created via S5; use `edit-competency.sh` on OOTB or unknown-provenance competencies.

## S7 · Activate/deactivate — `toggle-competency.sh <alias> <name-or-id> <activate|deactivate>` OR `toggle-custom-competency.sh <alias> <name-or-id> <activate|deactivate>`

Flips `IsActive`. Idempotent. Enforces the 8-active cap on the activate path — refuses to activate if the org is at cap and prints the current active set so the admin can choose which to deactivate. Deactivation preserves historical `EnablementCompetencyEval` records per the entity XML comment. Same generic-vs-custom split as S6.

## S8 · Fetch a record — `get-competency.sh <alias> <name-or-id> [--field <name>]` OR `get-custom-competency.sh <alias> <name-or-id> [--field <name>]`

Returns the full record (or a single field) so Claude can load the current `EvaluationInstructions` into context before drafting an improvement. Conversational improvement suggestions are Claude's job (see S5 for the reference-prompt library); the resulting write is done via `edit-competency.sh` / `edit-custom-competency.sh`.

## S9 · Verify — `verify-ootb-competencies.sh <alias> ["Name" ...]`

Confirms expected competencies exist and are active, printing name + evaluation criteria in a markdown table. Run after S4 / S4b / S5 to catch partial installs. No args → full 6-competency OOTB set from `assets/ootb-competencies.json`; explicit `MasterLabel` values → verify a specific subset. Exits 0 only if every expected name exists AND `IsActive=true`.

**Carve-out to admin-comms rules #5 and #6.** The S9 table is the ONE place prompt-body content (`EvaluationInstructions`) is deliberately surfaced to the admin — after an install, the admin needs to see the actual names and evaluation criteria, not just a count. On first-time setup, paste the script's table output directly into the chat response. Column labels ("Competency", "Evaluation Instructions") are admin English, not raw entity API names.

## S10 · Delete — no dedicated script (yet); use `sf` CLI directly

No `delete-competency.sh` yet. Resolve the Id via `list-competencies.sh --verbose` (don't expose it to the admin), then:

```bash
sf data delete record --sobject EnablementCompetencyDef --record-id <Id> \
  --target-org <alias> --use-tooling-api
```

Report "Deleted '<MasterLabel>'" — not the Id.

**Caveats.** FK-referenced records cannot be deleted — if the competency has `EnablementCompetencyEval` rows attached, DELETE fails on foreign-key constraint; use `toggle-*-competency.sh deactivate` instead (preserves history per the entity XML comment). When in doubt, deactivate first via S7 — frees the active slot even if the subsequent delete fails on FK.

## Execution sequence — by admin intent × org state

Once Phase 1 classifies the org into State 1a / 2 / 3 / 4, the intent × state matrix below determines which scripts to chain, in what order. **Chain automatically per rule #12** — do not ask permission between steps.

| Admin intent | State 1a (no ECI) | State 2 (avail, not enabled) | State 3 (enabled, no comps) | State 4 (enabled, with comps) |
|---|---|---|---|---|
| **Enable Call Coaching** (unqualified — no OOTB/custom stated) | Refuse — needs Agentforce for Sales | `enable-call-scoring.sh` → rule #13 ask (OOTB vs custom) | Idempotent — rule #13 ask (OOTB vs custom) | Idempotent — `enable-call-scoring.sh` exits 0, chains into S3 list |
| **Install OOTB set** (explicitly asked) | (refuse) | `enable-call-scoring.sh` auto-chains into S4 → S9 | `install-ootb-competencies.sh` → S9 | `install-ootb-competencies.sh` (idempotent — skips existing templates) → S9 |
| **Install best-practice set** | (refuse) | `enable-call-scoring.sh` → `install-best-practice-competencies.sh` → S9 | `install-best-practice-competencies.sh` → S9 | `install-best-practice-competencies.sh` (idempotent) → S9 |
| **Create custom competency** | (refuse) | `enable-call-scoring.sh` → **Q1-Q4** → `create-custom-competency.sh` → S9 | **Q1-Q4** → `create-custom-competency.sh` → S9 | **Q1-Q4** → `create-custom-competency.sh` → S9 |
| **Edit competency** | (refuse) | (no competencies to edit) | (no competencies to edit) | `edit-competency.sh` (OOTB) OR `edit-custom-competency.sh` (custom) |
| **Activate / deactivate** | (refuse) | (n/a) | (n/a) | `toggle-competency.sh` OR `toggle-custom-competency.sh` |
| **Improve a competency's prompt** | (refuse) | (n/a) | (n/a) | `get-*-competency.sh` (load current) → draft (Claude) → `edit-*-competency.sh` |
| **List / audit** | (refuse) | `list-competencies.sh` (empty) | `list-competencies.sh` (empty) | `list-competencies.sh` |
| **Verify OOTB set installed** | (refuse) | (nothing to verify) | (refuse — nothing installed) | `verify-ootb-competencies.sh` |
| **Delete a competency** | (refuse) | (n/a) | (n/a) | S10 — `sf data delete record` (fall back to S7 deactivate if FK-blocked) |

## Chaining checkpoints Claude must respect

- `enable-call-scoring.sh` prints `Next: <script>` on stdout — that's a hard chain hint. Run it in the same turn without asking (rule #12), **except** the State 3 hint, which points at `install-ootb-competencies.sh --list` — render that table and ask OOTB-vs-custom (rule #13) before writing anything, unless the admin's original ask already named one.
- After S4 / S4b / S5, always run S9 verify. Paste its table to the admin (S9 carve-out).
- After S5, do NOT stop at "created" — always show the admin what got created via S9.
- Between chained scripts, `ACCESS_TOKEN` and `INSTANCE_URL` propagate through the shared shell env (per Phase 0) — no re-auth.
