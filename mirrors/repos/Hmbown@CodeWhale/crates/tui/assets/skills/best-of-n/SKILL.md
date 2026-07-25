---
name: best-of-n
description: Generate a small set of independent candidate solutions in worktrees, judge them against one explicit rubric, and apply the winner only after PASS verification.
metadata:
  short-description: Compare independent candidates
---

# Best of N

Use this skill when a consequential design, implementation, explanation, or
debugging task has several plausible solutions and comparison is worth the
extra model work. In Operate mode this is the preferred ensemble pattern for
high-stakes or ambiguous approaches. Do not use it for a tiny change or when
the user has already chosen the approach.

## Set The Tournament

1. Define one task, one evidence packet, and one explicit scoring rubric before
   launching candidates. Include correctness, fit to the request, simplicity,
   risk, and verification.
2. Choose `N` from 2 to 4. Default to 3. More candidates need a concrete reason.
3. Give every candidate the same task and rubric. Add only a candidate number;
   do not steer candidates toward different conclusions unless diversity is an
   explicit part of the request.
4. Prefer a session goal (`create_goal` or active `/goal`) when the tournament
   spans more than one parent turn.

## Generate Independently

Start the candidates as parallel background `agent` workers and return agent_ids
immediately so the parent stays free. For proposals, reviews, or research, keep
them read-only:

```json
{
  "action": "start",
  "name": "candidate_1",
  "prompt": "Produce candidate 1 for the task below. Return the proposal, evidence, risks, and rubric self-score. Do not edit files.\n\n<TASK AND RUBRIC>",
  "type": "general",
  "model_strength": "same",
  "write_authority": "read_only"
}
```

Launch the remaining candidates with the same contract, then use `agent` wait
or completion events to collect every result. Do not show one candidate another
candidate's answer before generation finishes.

When candidates must implement code, give each one:

- `type: "implementer"`
- `worktree: true`
- `write_authority: "worktree_write"`
- the same bounded `write_roots` or `exact_files`

Never run parallel writers in the parent checkout. Each implementer must return
`VERDICT: PASS|FAIL` with command evidence (tests/lint) — a diff alone is not
completion.

Optional diversity: pin different `model` / Fleet `fleet_profile` values when
the project has multiple capable routes; otherwise keep model strength `same`.

## Judge Once

Use one read-only reviewer/verifier worker, or the parent when the result is
small, to score all candidates against the original rubric. The judge must:

- cite evidence from each candidate rather than vote by style;
- reject candidates that violate authority, scope, or verification gates;
- reject any code candidate without PASS evidence (or re-verify it);
- name the winner and the decisive reasons;
- identify useful pieces worth combining, if any;
- say when the candidates are tied or all fail.

Do not ask candidates to vote for themselves. Do not silently merge incompatible
approaches into a new unreviewed solution.

## Integrate Only After PASS

For proposal-only work, return the winning answer with a compact score summary.
For code work:

1. Inspect the winning worktree diff.
2. Apply/merge the winner into the parent checkout only after the judge (or a
   follow-up verifier) reports PASS with real checks.
3. Re-run the repository's checks in the parent after apply. Candidate
   self-reports and style scores are not final verification.
4. Leave losing worktrees unmerged; do not pollute the parent with partials.

Stop early when one candidate reveals a hard constraint that invalidates the
tournament. Report the negative result rather than spending the remaining
budget to manufacture variety.
