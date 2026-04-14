# Execution constraints and phase order

## Cost and scope

- Default **3–4** schemes, max **5** (cost control).
- Inner loop: **one change per round**, max **5** rounds.
- Do not repeatedly ask “should I continue?” **Run to completion** means: per **`phase-03-inner.md`**, iterate **each** `prompt-*` track until **termination** or **5 rounds**—not “always 5 rounds,” and not the agent quitting early on its own.
- In repos using this Skill, maintainers may state in root `SKILL.md` or host-specific rules whether “requirements already concrete → skip straight to output” is allowed, or whether extra gates (phase 2 on disk, independent `r01`, etc.) apply.
- The goal is **quality**, not delay.

## Strict execution (aligned with `SKILL.md`)

- The agent **must** follow this file, **`phase-03-inner.md`**, **`phase-04-output.md`**, **`verifiability.md`**, etc.; **must not** shorten or skip any `prompt-*` track’s inner loop or gates for undocumented reasons (e.g. “save work,” fewer tokens, “non-final track can be shorter”).
- **Each track** must run until **`phase-03-inner.md` termination**: mainly **`tracks/phase-01-acceptance.md` all checked**, capped at **5** rounds, plus **gates** (currently at least **r01**, **r02** per scheme). **Self-score alone cannot mean “done”** (R3). Claiming “inner loop done” in phase 4 without this is a **process violation**.

## Phase execution

- **Strict order**: requirements → outer schemes → inner loop → compare. No skipping phases.
- **Each phase must produce explicit output** before the next.
- **Gates block the next phase** until fixed and re-checked.
- **Consistency check is mandatory**; skipping it before inner loop is a violation.

## Multi-scheme inner independence (default)

1. **Phase 2 on disk**: before phase 3, write or update **`tracks/phase-02-consistency-check.md`** with the full block required in `phase-02-prompts.md` (heading **`## Scheme consistency check`**, per-scheme lines, and **result**).
2. **Scheme–dimension table**: same file must include **scheme / track dir / phase-02 dimension / note**.
3. **Independent `r01`**: for `prompt-b`, `prompt-c`, … **`r01` must not** be a full-page copy of `prompt-a` with comments tweaked; generate **per scheme**, visibly different structure or layout from `prompt-a/r01`.

> **Maintainer-tunable**: defaults above can be adjusted via root `SKILL.md` or host-specific rules (IDE rules, OpenClaw, etc.).

## Honesty and verification (read when executing)

**Sole rules: `verifiability.md` (R1–R5).** Reminder only:

- Do not treat similar wording in different files as multiple rule sets; on R1–R5 ambiguity, **`verifiability.md` wins**; phase flow and gates follow **`phase-*.md`** and **`execution.md`** in a way compatible with R1–R5.
- **Class A**: “same” claims need **terminal evidence**; recommend `scripts/skill-verify.sh` at repo root (see `program.md`).
- **Class B**: do not pretend file-level checks ran; give user commands and “please confirm” wording (R4, R5).
