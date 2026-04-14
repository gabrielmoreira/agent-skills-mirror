# program.md — lightweight entry

**Shortest path for agents**: read this section first, then open phase files under `docs/` as needed. The normative entry is **`SKILL.md`**; layout and adoption are in **`reference.md`**.

> **Host-agnostic**: no specific IDE required—Cursor, VS Code, CLI, OpenClaw, or any Skill-capable loader.

## Three parts (structure of this Skill)

| Part | Path | Role |
|------|------|------|
| **Verify script** (maintained by humans) | `scripts/skill-verify.sh` (repo root) | Structure checks; optional hash/byte compare of delivery vs final track file |
| **Iteration artifacts** (written by the agent per round) | `tracks/prompt-*/r*.html` etc. | One file per round; see phase 3 |
| **Entry points** | **`SKILL.md`** + **this file** | `SKILL.md` is the Skill entry; this file is the shortest path |

## Order of execution (mandatory)

**Principle**: follow **`SKILL.md`** and **`execution.md`** in full; do not shorten for undocumented reasons (see **`execution.md` “Strict execution”**).

1. Read **`docs/verifiability.md`** (R1–R5, sole authority)
2. **`docs/phase-01-spec.md`** → **`phase-02-prompts.md`** (finish with **`tracks/phase-02-consistency-check.md` on disk**) → **`phase-03-inner.md`** → **`phase-04-output.md`**
3. For details, read **`docs/execution.md`**

## Machine verification (class A, before delivery)

Run at **repository root** (adjust `FINAL_TRACK_FILE` to your final track file):

```bash
FINAL_TRACK_FILE=tracks/prompt-d/r09.html DELIVERY_FILE=index.html bash scripts/skill-verify.sh
```

- Exit code **0**: structure OK; if both files exist, SHA256 matches.
- **Non-zero**: do not claim “delivery bytes match final track file.”

**Class B**: give the user this one-liner; do not claim you ran it.

## Flow (abbreviated)

```
Phase 1 spec + acceptance checklist on disk → Phase 2 multi-prompt + consistency → Phase 3 per-track file iterations → Phase 4 compare
                                                              ↓
No track fully checked → no final delivery (see verifiability.md R3 + phase-04-output.md; self-score is reference only)
```

See **`examples.md`** for a walkthrough.
