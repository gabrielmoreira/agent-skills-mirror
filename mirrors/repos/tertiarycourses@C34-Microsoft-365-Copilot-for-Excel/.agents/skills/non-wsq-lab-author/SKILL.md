---
name: non-wsq-lab-author
description: Create detailed, connected hands-on labs for NON-WSQ courses. Use when turning course topics into step-by-step learner activities with verification steps and troubleshooting. Labs are the only practical component — non-WSQ courses have no assessment.
---

# non-wsq-lab-author — hands-on labs for a NON-WSQ course

In a non-WSQ course the labs carry the entire practical load. There is **no
assessment**, so a lab's verification step is the learner's only feedback that
they got it right. Write every lab so it proves itself.

## Source of truth

Labs live in `labs/lab-NN-<slug>.md` and are mirrored into the deck, the Learner
Guide and the Lesson Plan by the **non-wsq-courseware-build** engine from
`data_domainN.py`. Keep the two in step: `num` is the global contiguous lab
number, `topic` matches the `course_data.TOPICS` entry.

## Required structure for every lab

1. **Goal** — the observable outcome, in one line.
2. **What you'll build** — the artifact the learner ends up holding.
3. **Prerequisites** — earlier labs and any tools/accounts needed.
4. **Steps** — numbered and executable. Name the exact file, command, menu path
   or value. No step may say "configure appropriately".
5. **Test it** — a concrete check with the expected result stated. This is the
   verification the learner self-assesses against.
6. **Troubleshooting** — the two or three failures that actually happen here,
   each with its fix.
7. **Challenge** — an independent extension for fast finishers.
8. **Reflection** — one question tying the lab back to its learning outcome.

## Rules

- **Connected, not isolated** — prefer one scenario or dataset that grows across
  the labs, with a stated checkpoint at each lab boundary so a learner who fell
  behind can rejoin.
- **Executable** — every step is something the learner can literally do; where a
  command is involved, give the command.
- **Synthetic data and placeholder secrets only.** Never instruct a learner to
  paste a real credential; use `<API_KEY>`-style placeholders and say where the
  real value belongs (a config file or env var, never a prompt or git).
- **Time-boxed** — state a realistic duration; the Lesson Plan schedule is built
  from these, and each training day must total exactly 480 minutes.
- **No assessment language.** No marks, grades, pass/fail, "competent / not yet
  competent", assessor, marking guide or answer key. A lab verifies; it does not
  assess. Likewise no WSQ, SSG, SkillsFuture, TRAQOM or funding references —
  including in the lab footer, which must carry the plain non-WSQ course code
  (e.g. `C524`), never a `TGS-` reference.

## Before you finish

Run the prohibited-content scan over the labs:

```bash
python "<non-wsq-courseware-qa-skill-dir>/scan_prohibited.py" "<course-repo>"
```

Then ask the `non-wsq-lab-reviewer` custom agent for a read-only review of
prerequisites, bounded steps, verification evidence, and continuity.
