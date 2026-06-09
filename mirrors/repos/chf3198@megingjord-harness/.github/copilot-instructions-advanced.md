# Copilot Instructions — Advanced Governance Contracts

Companion to [copilot-instructions.md](copilot-instructions.md).
All contracts in this file apply to every Copilot session in this repo.

## Harness Goal Constitution

Priority order (highest to lowest): **G1 Governance > G2 Quality > G3 Zero
Cost > G4 Privacy > G5 Portability > G6 Resilience > G7 Throughput >
G8 Observability > G9 Interoperability > G10 Maintainability.**

When a lower-priority goal overrides a higher one, record the rationale
explicitly in the ticket, PR body, or closeout evidence. Silent overrides
are a G1 governance violation.

Full definitions: `instructions/harness-goals.instructions.md`.

## Cross-Team Artifact-Write Contract

When Copilot authors a file consumed by another team's runtime (e.g., writing
`.claude/settings.json` for the Claude Code team), the following apply:

- Signal the write in `MANAGER_HANDOFF` under `cross_runtime_writes: [<path>]`.
- Reference the target runtime's schema or template.
- Tag the target team with a `TEAM_QUESTION` comment requesting sign-off.
- `MANAGER_HANDOFF` cannot be marked complete until the target team posts
  `TEAM_RESPONSE` with `verdict: schema-valid`.

The target-runtime team owns the schema/contract test. Full contract:
`instructions/cross-team-artifact-write.instructions.md`.

## Hook Behavior Overrides

Hooks in `hooks/scripts/` operate under an advisory-vs-blocking contract:

- **Advisory**: hook emits a warning but does not block the operation.
- **Blocking**: hook blocks the operation and requires explicit override.

Blocking hooks require evidence in the baton artifact before override.
Two bypass events in one session trigger an immediate Tier-2 self-anneal.

Full contract: `instructions/hook-behavior-overrides.instructions.md`.

## OWASP Agentic Security

This repo's agent runtime enforces OWASP Top 10 for Agentic Applications
(OA1–OA10). The current enforcement coverage:

| Risk                               | Status   | Harness Goal |
| ---------------------------------- | -------- | ------------ |
| OA1 Goal Hijacking                 | Enforced | G1, G2       |
| OA2 Tool Misuse                    | Enforced | G1, G4       |
| OA3 Identity Abuse                 | Enforced | G1, G4       |
| OA4 Memory Poisoning               | Enforced | G2, G4       |
| OA5 Cascading Failures             | Enforced | G6           |
| OA6 Rogue Agents                   | Enforced | G1, G9       |
| OA7 Supply Chain                   | Enforced | G4           |
| OA8 Insecure Communications        | Deferred | G4           |
| OA9 Human-Agent Trust Exploitation | Enforced | G1, G8       |
| OA10 Code Execution                | Enforced | G4           |

Full mapping: `instructions/owasp-agentic-mapping.instructions.md`.

## Skill Index and Role Taxonomy

**Skill Index**: the canonical list of available skills is auto-derived and
stored in `docs/skills-copilot.md`. Regenerate with:

```bash
node scripts/global/skill-views-derive.js
```

**Role Taxonomy**: the harness uses a 7-role canonical set:
Manager / Collaborator / Admin / Consultant / IT / Red-Team / Client.
Guest-Collaborator is reserved but not active. "Operator" is a meta-term
for the AI agent — it is not a baton role.

Full taxonomy and baton contract:
`instructions/role-baton-routing.instructions.md` §"Role Taxonomy".

## Merge-Evidence Convention (cross-runtime)

PR bodies must include merge evidence for their linked issue. Two forms:

- **Preferred**: `merge-evidence-deferred-final: #N` — satisfies the PR gate
  without triggering GitHub auto-close. Consultant closes the issue explicitly
  after posting `CONSULTANT_CLOSEOUT`.
- **Backward-compat**: `Closes #N` — triggers GitHub auto-close on merge.

This convention is uniform across Copilot, Claude Code, and Codex. Rationale:
`governance-carve-outs/index.md`.

Full contract: `global-standards.instructions.md` §"Deferred-finalize
merge-evidence contract (Epic #2295 P1.3)".
