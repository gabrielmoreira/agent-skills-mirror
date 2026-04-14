# Example: one pass through the double-layer flow

Aligns expected artifacts; details are in **`docs/phase-*.md`**.

## User input

> Build me a simple expense tracker.

## Phase 1 — requirement spec (illustrative)

- **Features**: add income/expense, monthly stats, filter by category, data only in local storage.
- **Stack**: static SPA + localStorage (example).
- **Output**: single-page web, works offline.
- **Quality**: core flows work, input validation, basic a11y.
- **Acceptance**: write **`tracks/phase-01-acceptance.md`** with checkable items (e.g. element `id="balance"` exists and is a valid number); inner loop mainly terminates on **all items checked** (see `docs/phase-03-inner.md`, **R3**).

## Phase 2 — outer prompts (illustrative)

Prepare 3–4 phrasings (Prompt A/B/C…), run consistency check; write **`tracks/phase-02-consistency-check.md`**.

## Phase 3 — inner loop (illustrative)

**Each** scheme iterates in its own folder (`tracks/prompt-a/`, `prompt-b/`…) until **`docs/phase-03-inner.md` gates and termination** are met (not only one track).

Example: under `tracks/prompt-a/` write `r01.html` … `rNN.html` (diffable each round, **R1**); other tracks the same, and **`r01` must not** be a full-page copy of `prompt-a` (see **`docs/execution.md`**).

## Phase 4 — compare and deliver

Among tracks with **acceptance fully checked**, pick the highest self-score; if **no track is fully checked**, follow **`docs/phase-04-output.md`** — **do not** treat any scheme as final (**R3**).

## Verification (class A)

```bash
FINAL_TRACK_FILE=tracks/prompt-a/r05.html DELIVERY_FILE=index.html bash scripts/skill-verify.sh
```

Only if the command succeeds and policy allows may you claim delivery matches the final file (**R2/R4**).
