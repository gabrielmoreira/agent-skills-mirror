# Claude Project Notes

Follow `AGENTS.md` for repository workflow.

Key project facts:
- Shipped skill count: 39.
- `thinking-scientific-method` is the shipped hypothesis-differential debugging skill. Do not reintroduce a separate v2 variant.
- Eval claims must identify whether they are pre-edit, post-edit, directional, or statistically significant.
- Backups of global Claude state belong in `backups/` and must remain uncommitted.

Common verification commands:

```bash
node scripts/validate-skills.js
EVAL_RUN=local node evals/run-structural.js
EVAL_RUN=local node evals/run-routing.js
```
