# Agent Governance Reference

> Companion to `AGENTS.md`. Covers Team&Model signing, review guidelines,
> role taxonomy, HAMR routing, and 2026-H1 governance contracts.

## Team & Model signing

All AI-authored governed artifacts (baton handoffs, PR evidence, governance
docs) must carry structured provenance:

```yaml
Signed-by: Soren Mason # human alias from agents/roster.json
Team&Model: copilot:claude-sonnet-4-6@github
Role: manager # must match the artifact type
```

Signing aliases for this repo (copilot:claude-sonnet-4-6@github):

| Role         | Alias        |
| ------------ | ------------ |
| Manager      | Soren Mason  |
| Collaborator | Soren Harper |
| Admin        | Soren Reyes  |
| Consultant   | Soren Vale   |

Repo-local overrides may tighten the format but must **not** remove provenance.
See `instructions/team-model-signing.instructions.md`.

## Review guidelines

When reviewing a Codex PR, treat these as **release-blocking governance risks**:

- Ticket lifecycle violations (MH posted after file edits; wrong baton order)
- Signer fidelity failures (wrong alias or wrong `Role:` field in an artifact)
- Isolated worktree violations (shared checkout between concurrent agents)
- Runtime-home direct edits (`~/.copilot/` or `~/.codex/` modified in-place)
- Governed changes without matching docs, research, or wiki updates

When Codex behaviour is uncertain, consult **official OpenAI Codex docs** —
never infer from Claude or Copilot compatibility. APIs differ.

## Role taxonomy (7-role canonical set)

| Role             | Responsibilities                                                      |
| ---------------- | --------------------------------------------------------------------- |
| **Manager**      | Research, scope, ticket, acceptance criteria; no file edits           |
| **Collaborator** | Implementation, branch, tests, doc-coverage handoff                   |
| **Admin**        | CI, credentials, PR staging, deployment; signer ≠ Collaborator        |
| **Consultant**   | Adversarial review, risk assessment, rubric rating, terminal approval |
| **IT**           | Infrastructure, secrets, Tailscale fleet management                   |
| **Red-Team**     | Security assessment, prompt injection testing                         |
| **Client**       | External stakeholder; informs UX and requirements                     |

`Guest-Collaborator` is reserved but not active. `Operator` is a meta-term for
the AI agent — not a distinct role in the baton chain.
Canonical: `instructions/role-baton-routing.instructions.md` §"Role Taxonomy".

## HAMR cross-team routing

All three teams route governed provider calls through HAMR when `MEGINGJORD_HAMR_ENABLED=1`:

- Endpoint: `https://hamr.chf3198.workers.dev`
- Activate per-checkout: `npm run hamr:activate`
- Verify: `npm run hamr:sync-verify`
- Canonical contracts: `instructions/hamr-routing.instructions.md`

Default (env var unset): GitHub-native Layer-2 routing (no Cloudflare required).
See `docs/agents-workflow.md § Layer-2 routing`.

## 2026-H1 key contracts

| Contract                  | Detail                                                                             |
| ------------------------- | ---------------------------------------------------------------------------------- |
| **Doc-coverage gate**     | `COLLABORATOR_HANDOFF` must include `doc-coverage:` block on `lane:code-change`    |
| **Baton builders**        | Use `baton-comment-build.js`, `pr-comment-build.js`, `changelog-fragment-build.js` |
| **Governance chains**     | Run `npm run governance:chains:check` on governance path changes                   |
| **OTel GenAI**            | `isValidGenAI()` from `otel-genai-conformance.js` before any telemetry emit        |
| **Fleet-call-guard**      | All fleet calls must use bounded timeout; see `docs/howto/fleet-call-guard.md`     |
| **Credential guard**      | Check `credential-availability.js` before prompting user for any secret            |
| **Admin-merge-exception** | Override merges require `merge-bypass:admin-exception` label per Epic #2517        |

## Merge evidence convention

PR bodies must include:

```
merge-evidence-deferred-final: #N   # preferred (no auto-close)
Closes #N                           # backward-compat
```

Same marker required across Claude Code / Codex / Copilot.
See `governance-carve-outs/index.md` for rationale.
