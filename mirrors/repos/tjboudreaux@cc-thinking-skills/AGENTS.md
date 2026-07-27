# Agent Guidelines

This repository packages 28 Claude Code thinking skills. Treat it as a plugin marketplace project first and an eval research project second.

## First Principles

Every change to this project must serve at least one of these goals, and any major change should state which one:

1. **Maximize model performance per task** — raise measured task success of the skills and harness, across frontier SoTA models and smaller/cheaper models alike.
2. **Reduce token usage / cost per task** — at equal or better measured performance.

A change that does neither is noise. A change that trades one goal against the other must say so and show the measurement. Treat every token in a skill description or body as a cost charged against these goals: descriptions are paid on every model invocation, bodies on every skill trigger. Performance claims must name the model class measured; a win on a frontier model that harms a smaller model (or the reverse) is not a proven win.

## Skill Authoring & Eval Standards

Distilled from "Don't Ship Skills Without Evals" (Philipp Schmid, Google DeepMind) and "How I deleted 95% of my agent skills and got better results" (Nick Nisi, WorkOS):

- **Never ship a skill change without eval evidence.** Run the relevant evals on every skill diff; merge only when evals improve or coverage grows. Current post-edit evidence only — historical pre-edit results are context, not proof.
- **Measure, don't assume.** More tokens and more instructions do not imply better performance; a loaded skill can actively hurt (documented case: 97% correct without a skill, 77% with it). Trust is a pass rate, not a vibe.
- **Run ablations.** Evaluate with and without the skill. Retire a capability skill (one that teaches what the base model can't yet do) when the model matches it unaided — models improve and evals tell you when. Preference skills (this project's conventions) are durable; protect them with regression evals. Keep the eval after retiring the skill as the guard that says when to reintroduce it.
- **Guide, don't prescribe.** Skills encode gotchas, landmines, and decision boundaries — not documentation summaries. Reference point: 10,000 generated lines cut to 553 hand-written gotcha lines raised accuracy and cut eval runtime from 68 to 6 minutes.
- **Write directives, not essays.** Tell the agent when to use the skill and when not to; keep the required "When NOT to Use" boundary sharp and back it with negative trigger evals.
- **Keep skills lean and layered.** Target under 500 words per SKILL.md; push depth into reference files (progressive disclosure). The frontmatter description is the always-paid cost — every word must change routing behavior.
- **Kill no-ops.** Delete any instruction that does not change agent behavior ("write clean code", "be thorough"). Every retained line must pay for its tokens.
- **Scripts for deterministic work.** If a workflow is always the same, make it a script the agent calls — not prompt content the model re-derives at token cost.
- **Enforce, don't instruct.** Put must-happen checks in code — validators, gates, hashes, state machines — not in prose the model can skip or fake. Require verifiable artifacts (output hashes, logs, recorded runs) for claimed results.
- **Test outcomes, not paths; test early.** A handful of positive plus negative prompts per skill beats none. Prefer cheap deterministic asserts (regex/exact match) over LLM judges; run multiple trials before trusting a result (agents are non-deterministic); isolate eval runs so agents cannot mine prior state.
- **Every failure becomes harness data.** Feed eval failures back into skill gotchas, datasets, or gates — fix the harness, not just the output.

## Default Workflow

- Preserve the public skill count at 28 unless a change intentionally adds/removes a shipped skill and updates README, plugin metadata, routing cases, and eval docs together.
- Keep skill frontmatter descriptions situation-named and under 200 characters.
- Prefer agent-native instructions over human facilitation language.
- Add explicit "When NOT to Use" boundaries for every non-router skill.
- Do not commit local backups, downloaded third-party datasets, transient logs, or scratch eval runs.

## Verification

- Run `node scripts/validate-skills.js` after skill edits.
- Run `EVAL_RUN=<name> node evals/run-structural.js` after catalog edits.
- Run routing or behavioral evals only when the changed surface warrants the cost.
- Use current post-edit evidence only; historical pre-edit results are context, not proof.

## Local Backups

Global Claude assets may be backed up under `backups/` for safety. The directory is gitignored. Do not add backup archives to commits.

## Images

README and marketing images live in `assets/`. Keep generated source paths out of README links; copy selected assets into the repo and leave generator cache files untouched.
