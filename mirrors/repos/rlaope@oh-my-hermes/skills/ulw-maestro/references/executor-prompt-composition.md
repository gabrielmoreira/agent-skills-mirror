# Executor Prompt Composition

Load this reference once the coding owner is already explicitly chosen and a prompt needs to be composed from that owner's own installed skills. It never selects the owner and never dispatches; it only arranges what is already discovered into one prompt.

## 1. Reading The Skill Set

Run `omh coding executor-skills --profile <profile> [--project-root <root>] [--unit-role <role>]` before composing anything. It is a thin, read-only wrapper over local discovery: `--profile` selects which executor's declared skills to read (`claude-code`, `codex`, or `omo-runtime`; `hermes` is rejected -- Hermes-native lanes never route through this command), `--project-root` also probes project-local Claude Code skills, and `--unit-role` additionally returns a suggested sequence and, when a genuine arrangement choice exists, a selection card.

The payload is `executor_skill_discovery/v1`: `sources` (one entry per probed location, each with a `status` of `present`, `absent`, `unreadable`, or `unsupported`, plus a `reason` when not `present`), `skills` (each entry carries `name`, `invocation`, `role`, `role_score`, and `source` -- never a description), `rejected_name_count`, and a `claim_boundary` that must ride into the composed prompt's evidence boundary unchanged. `omo-runtime` always reports its one source as `unsupported`: its host CLIs declare no skill layout this repo can verify, so the payload says so instead of coming back empty with no trace. The command also accepts the remaining executor profiles (`generic`, `omx-runtime`, `omc-runtime`); those have no probed skill layout at all and return an empty `sources` map -- treat that exactly like an all-absent result and take the explicit-generic path.

## 2. Role Recipes

Arrange the discovered skills by the unit's role, one named skill per step -- a step offering alternatives is a decision the executor must make before starting; a single named skill is a suggestion it can take or drop.

| Unit role | Sequence |
| --- | --- |
| `implementation` (also the default for an unrouted unit) | brain -> implementation -> review |
| `brain` | research -> brain |
| `research` | research -> brain |
| `review` | review |
| `design_visual` | design_visual -> implementation -> review |
| `docs` | research -> docs |

Each step names the skill's real invocation string exactly as discovery returned it -- `/name` for a user or project skill directory, `/pack:name` for a plugin-namespaced skill (the namespace comes from the plugin's own manifest, not a guessed directory name), `$name` for a Codex prompt or skill pack. Never fabricate a prefix a source did not report.

## 3. The Degradation Ladder

Never go silent when a step has nothing to arrange:

1. **Declared** -- the skill set discovery reported, per source.
2. **Discovered** -- the subset that classified into a role with a nonzero score.
3. **Explicit generic line** -- when a profile's discovery is empty or nothing classifies, state it plainly: "no installed skills discovered for `<profile>`; prompt composed generically." Then compose the prompt without a skill sequence. A silently generic prompt looks identical to a profile with real skills that were never checked; the explicit line is what tells the difference apart.

## 4. Cache-Stable Composition

Split the composed prompt into an invariant head and a varying tail. The head -- goal framing, the do/don't boundary, the skill sequence, the evidence boundary, and any content shared across every unit dispatched to this run -- must stay byte-identical across units and across re-dispatches of the same unit, so the executor's own prompt cache reuses it. Only the tail -- the specific task, known context, and unknowns for this one unit -- varies. A steering delta lands in the tail; it never rewrites the head.

## 5. Section Contract, Docs Consulted, Session Summary

Every composed prompt carries the ten required sections in order: Goal, Do, Don't, Known context, Unknowns and decision rule, Expected result, Test, Progress and blockers, Evidence boundary, Task. Include a greppable `Docs consulted:` block -- one line per source as `URL (version or retrieval date)`, or the literal line `Docs consulted: none` when no external doc was read. On report-back, hold the executor to the six-section session summary shape (goal echo, what changed, verification run, evidence and gaps, blockers, next action) so a status line never substitutes for it.

## 6. Steering Deltas

A steering message sent mid-dispatch is never a restated brief. State: the constraint that changed, the new evidence that justifies the change, the concrete action required next, and whether the verification target itself moved. A steering delta that repeats the original goal without one of these four elements has not actually steered anything.

## 7. Attribution

The role recipes, degradation ladder, and section contract are OMH's own; no external text is reproduced. The ten-section prompting contract and the six-section session summary shape are the existing `src/coding/prompting.py` and `src/coding/coding_contracts.py` contracts this reference points at, not new inventions.

## 8. Result Integration

Dispatch ends at spawn and exit -- it never merges (`docs/FANOUT.md`, `DISPATCH_CLAIM_BOUNDARY` in `src/coding/fanout_dispatch.py`). What happens after a unit's process exits is a separate, explicit phase the operator or reviewing agent owns, not something this engine or `omh coding fanout dispatch` performs on its own:

1. **Collect each unit's result.** Read the unit's `fanout_unit_result/v1` evidence -- the sidecar file the unit wrote (`unit_result_source: sidecar`) or, when no sidecar exists, the validated stdout fenced block (`unit_result_source: stdout_fenced_block`) -- and note the unit's branch/worktree state (`<repo>-fanout-<unit>` on `agent/<unit>`, one per unit, never auto-deleted; `omh coding fanout show` joins the frozen contract with the per-unit run record).
2. **Verify the integrated combination, not just each unit alone.** A unit's own `verification_commands` (`--run-verification`) only prove that one worktree in isolation; disjoint `file_scope`s can still conflict once units land together on the same base. Name that outcome an integration conflict -- a distinct failure class from a per-unit verification failure -- and re-run the goal's own verification commands against the combined result, with a review pass, before calling any of it ready.
3. **The merge itself is an explicit operator or reviewing-agent action.** No OMH command merges branches -- not dispatch, not a status or brief command. Merging the unit branches, in the contract's `merge_order`, is a manual git operation the operator or reviewing agent performs after integration verification and review pass; a dispatch receipt is never merge evidence, the same boundary this engine already holds for dispatch itself.
4. **Report merged/unmerged per unit in the closing brief.** State which units actually merged and which did not, alongside the run summary, rather than one aggregate "done" -- an integration-ready unit that has not yet been merged is not the same claim as a merged one.
