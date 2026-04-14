# Double-layer auto-optimization Skill — readable guide

> For **people explaining the flow to teammates** or **coming back to it later**.  
> Normative text remains in **`SKILL.md`** and **`docs/`**; this is a **guide**, not a substitute.

---

## 1. What does this Skill do?

In one sentence: **when the AI writes deliverables (pages, configs, etc.), it should not only report progress in chat—it should lock requirements, compare multiple phrasings, leave each iteration on disk, and optionally verify that delivery matches the final track file with a script.**

It fits repos that care about **quality, auditability, and postmortems**.

**Why an acceptance checklist?**  
The same model grading itself has **blind spots**. Phase 1 locks **line-item checkable** conditions (scripts/grep where possible); the inner loop mainly stops when the **checklist is fully checked**; self-scores are **reference only** to avoid moving the goalposts.

---

## 2. What does “double layer” mean?

| Layer | What | Intuition |
|-------|------|-----------|
| **Outer** | Same requirement, **different phrasings** → multiple Prompt schemes (e.g. prompt-a / b / c) | Same exam question, different ways to read the prompt |
| **Inner** | **Fixed Prompt** per scheme, repeatedly edit **code/files**, score and save each round | Same essay, draft by draft, each draft is a file you can diff |

Outer layer compares **which description works better**; inner layer compares **how good the artifact gets under that description**.

---

## 3. Four phases (overview)

Strict order; **do not heavily edit deliverables before earlier gates pass**.

| Phase | Name | Plain output |
|-------|------|----------------|
| **1** | Requirement spec | Features, stack, shape; lock **`tracks/phase-01-acceptance.md`** (checklist) |
| **2** | Multi-prompt + consistency | Same scope/stack/output type; write **`tracks/phase-02-consistency-check.md`** (with table) |
| **3** | Inner loop | Under **`tracks/prompt-*/`**, rounds **`r01`, `r02`…**; self-score **reference only**; main stop: **checklist all checked** |
| **4** | Compare & output | Among **fully checked** tracks, compare; **at least one track fully checked** for final delivery; align and verify |

---

## 4. Inner loop: when can a track stop? (per track)

**Main stop (hard gate)**: against phase-1 **`tracks/phase-01-acceptance.md`**, **every item checked** (all green). Prevents “self-score ≥8” alone as “done”.

**Cap**: **5** rounds and still not all checked → that track **cannot** be a final-delivery source; phase 4 must list gaps.

**Self-score**: still logged each round for improvement and phase 4 **relative** comparison; **not** sufficient for stop or delivery (**`verifiability.md` R3**).

Details: **`docs/phase-03-inner.md`**.

---

## 5. Verifiability rules R1–R5 (plain language)

Authoritative text: **`docs/verifiability.md`**. Summary:

| ID | Idea |
|----|------|
| **R1** | Iterations must be **files on disk**, not chat-only “I changed it” |
| **R2** | “Delivery = final file” needs **byte-level** check or **written** differences |
| **R3** | **Checklist not all checked** → no final handoff; high self-score **cannot** replace acceptance |
| **R4** | **Who can run the terminal**: if you can, run verification; if not, don’t pretend you did |
| **R5** | The model may not know it’s violating rules—**trust command output** |

---

## 6. Before delivery (optional but important)

Script **`scripts/skill-verify.sh`** (repo root):

- Checks **`tracks/phase-01-acceptance.md`** exists and has no unchecked `- [ ]` lines;
- Checks **`tracks/prompt-*/`** has at least **`r01`**, **`r02`**;
- If `FINAL_TRACK_FILE` and `DELIVERY_FILE` are set, compares **SHA256**.

Example:

```bash
FINAL_TRACK_FILE=tracks/prompt-a/r05.html DELIVERY_FILE=index.html bash scripts/skill-verify.sh
```

The script checks **presence and hash**; it does **not** replace human judgment that the inner loop ran per phase docs.

---

## 7. Maintainer-tunable defaults

By default this Skill expects:

- Phase 2 consistency **on disk** (`tracks/phase-02-consistency-check.md`)
- Non-`a` schemes’ **`r01` independently generated** (no full-page copy of prompt-a)
- Optional: straight-to-output only if allowed in root `SKILL.md` or host-specific rules

Tune via **`docs/execution.md`** (“Maintainer-tunable”).

---

## 8. Waiving the full flow

User must **write in the current message**, e.g.:

`This task waives the Skill / skips phases`

The agent **must not** infer a waiver from tone.

---

## 9. vs. “just generate a page”

| | Full Skill | Direct generate |
|--|------------|-----------------|
| **Pros** | Clear requirements, comparable schemes, file trail, hashable delivery | Faster, fewer steps |
| **Cons** | More steps, longer chats, often more tokens | Weak spec, hard to verify, “chat-only iteration” |

---

## 10. Where files live

See **`reference.md`** and the repo root **`README.md`**.

---

## 11. Read order

1. **`program.md`** — shortest path  
2. **`docs/verifiability.md`** — R1–R5  
3. **`docs/phase-01-spec.md`** … **`phase-04-output.md`**  
4. **`docs/execution.md`**  
5. **`examples.md`**  

---

## 12. Disclaimer

Not a substitute for human review, compliance, or safety decisions. Self-scores and scripts have limits—review critical work.

---

*Version: aligned with `SKILL.md`; if norms change, follow latest `docs/`.*
