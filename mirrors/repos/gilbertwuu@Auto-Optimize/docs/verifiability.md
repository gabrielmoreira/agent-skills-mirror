# Verifiability and honesty (sole authoritative rules)

> **Sole source for R1–R5.** Phase docs only reference this section to avoid multiple conflicting “rule sets.”

### R1 — Physical artifacts (iterations)

- Each round’s output must be a **separate file on disk**; **forbidden** to use chat-only “iteration logs” instead of files.
- **Forbidden** to claim “round N changed X” if no matching `r{N}` file exists in the repo.
- **Forbidden** to narrate “five iterations” without five diffable versions on disk.
- **Forbidden** to describe a change (e.g. “added :focus-visible”) without that change **actually** in the file.

### R2 — Delivery provenance (match final track file)

- If you claim the delivery matches a final track file (“same”, “same source”, “only a comment differs”), you need **machine-checkable** sameness or a **written** statement of differences:
  - **Same**: delivery file is **byte-identical** to the final track file; or differences are only paths/explanations in a **top comment** of the delivery file as documented.
- **Forbidden** to claim sameness when `diff` / `shasum` show otherwise.
- **Forbidden** to hide large diffs behind “only one comment changed.”

### R3 — Delivery bar (acceptance first; self-score reference only)

> When generator and grader are the same model, **high self-score cannot alone mean “done”** (systematic bias). This Skill uses the **phase-1 acceptance checklist** as the hard bar; self-score is for comparison and review.

- **Phase 1** must produce **`tracks/phase-01-acceptance.md`** (or an equivalent path specified by the maintainer) with **line-item** checks (prefer mechanically testable items); the list **must not** be silently rewritten mid-flight to move goalposts (changes go back to phase 1/2 with trace). **No list or empty list** then entering phase 3 is a process violation (unless the user **waives** in the current turn).
- **Inner loop on one track**: **main termination** is **all** acceptance items satisfied against **current** artifacts; **forbidden** to end solely because self-score is “≥8”. Self-score must still be **logged each round** for the next round and phase 4; it is **not** sufficient for stop or delivery.
- **Deliverable final**: need **at least one** track with acceptance **fully checked**, and **`phase-04-output.md`** + R2; **forbidden** to ship as “final” while items remain unchecked.
- **Forbidden** to justify early stop or delivery with “only one item left but score is high” (see `phase-04-output.md` for actions).

### R4 — Environment classes (who can verify)

| Class | Meaning | Requirements for “same / verified” claims |
|-------|---------|-------------------------------------------|
| **A** | Agent/IDE: **read/write repo** and **can run terminal** (`shasum`, `cmp`, `diff`) | Before claiming **byte match** or **verified**, **must** run the check and show **command + output** (or equivalent). **Forbidden** to claim “hash matches” without running the command. |
| **B** | Chat-only: **no workspace write** or **no terminal** | Mechanical checks in R1/R2 are **soft**: **forbidden** to claim “I ran shasum locally”; must say “cannot verify here; please run: …” with a **one-line copy-paste**. Delivery wording must be “aligned with stated source; **please verify**,” **forbidden** to pretend verification is done. |

**Class B one-liner (repo root):**

```bash
FINAL_TRACK_FILE=tracks/prompt-d/r09.html DELIVERY_FILE=index.html bash scripts/skill-verify.sh
```

### R5 — “Detecting violations” (blind spots)

> The model **may not know** it is violating rules (e.g. `index.html` ≠ `r05` without read access or terminal).

- **Do not** rely on “when the AI notices it can’t comply” as the only trigger—many violations are **invisible** to the model.
- **Class A**: **Executed command output** is the **only** basis for “same”; if you cannot write `tracks/` or run checks → **stop** and tell the user what capability is missing.
- **Class B**: assume **cannot prove sameness**; **do not** output “verified” or “byte match with rXX” unless the user pasted results.
