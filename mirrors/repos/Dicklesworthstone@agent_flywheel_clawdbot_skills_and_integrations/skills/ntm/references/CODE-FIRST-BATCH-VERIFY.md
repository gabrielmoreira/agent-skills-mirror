# Code-First / Batch-Verify — The Two-Phase Swarm Pump

<!-- TOC: Problem | Insight | State Machine | Phase 1 | Phase 2 | Triggers | The Pump | Enforcement | Gotchas | Honest-Credit Binding -->

## Contents

- [The Loop At A Glance](#the-loop-at-a-glance) — diagram + Phase-2 close commands
- [The Problem](#the-problem) / [The Insight](#the-insight)
- [The State Machine](#the-state-machine) — tracker policy encoding
- [Phase 1 — Code-First Wave](#phase-1--code-first-wave-all-agents-parallel-no-test-builds)
- [Phase 2 — Batch Verify and Close](#phase-2--batch-verify-and-close-orchestrator-once-per-wave)
- [Triggers](#triggers-phase-1--phase-2) / [The Pump](#the-pump-why-closing-refills-work)
- [Enforcement](#enforcement-what-keeps-it-honest) / [Hard-Won Gotchas](#hard-won-gotchas)
- [Honest-Credit Binding](#honest-credit-binding)

## The Loop At A Glance

A throughput doctrine for running a large NTM swarm (e.g., 12 codex panes)
against one repository with one expensive build/test path. Proven in
production swarms, then hardened with policy-level enforcement. It routinely
delivers ~20×–100× the closure throughput of per-item building.

```text
┌─ PHASE 1: CODE-FIRST WAVE (all N panes, parallel, no test builds) ──────┐
│  each agent:  claim highest-priority ready bead (assignee lock)         │
│               -> WRITE real code + real tests (same bead)               │
│               -> syntax gate at most (cargo check -p <crate>)           │
│               -> COMMIT immediately (bead ID + touched scope)           │
│               -> batch_pending when substantively complete              │
│               -> next bead                                              │
└──────────────────────────────────┬──────────────────────────────────────┘
     trigger: earliest of ready-pool dry | debt ceiling | articulation
              point verifiable | scope frontier | time/risk | rate dip
                                   v
┌─ PHASE 2: BATCH VERIFY + CLOSE (orchestrator, once per wave) ───────────┐
│  commit-flush -> ONE build/test over git-derived touched scope          │
│  -> fix compile errors FIRST (early-abort = lying green prefix)         │
│  -> cluster failures by file -> rework to SAME assignee                 │
│  -> re-run to green (every attempt retained)                            │
│  -> gate report + close ONLY green, citing the run                      │
└──────────────────────────────────┬──────────────────────────────────────┘
                                   v
              closes unblock dependents -> ready pool refills
                          -> next Phase-1 wave
```

Quick commands (Phase-2 close flow):

```bash
br gate report <id> --gate batch_verify --provider batch-orchestrator \
  --status pass --to closed --note "run:<id> commit:<sha> suites:<...>"
br close <id> --reason "<evidence>" --transition-comment "<batch summary>"
```

## The Problem

A swarm of N agents sharing one repo and one build backend has a brutal
bottleneck: **builds, not coding**. Large crates take minutes per compile;
remote build offload (rch) serializes same-project builds; N agents building
per-bead means N × minutes of mostly-queued, mostly-redundant compilation —
plus disk blowups from N target dirs and local-fallback thrash.

## The Insight

Writing and reading code is cheap and embarrassingly parallel. Building and
testing is expensive and serialized. So: **separate them**. Let all N agents
write real code at full speed without building; run the build/test exactly
once, centrally, over everyone's combined changes; close in bursts.

## The State Machine

Encode the doctrine in tracker policy, not etiquette (br `.beads/policy.yaml`):

```text
open/rework -> in_progress -> batch_pending -> closed
                   ^                |
                   +---- rework <---+   (failures return to the SAME assignee)
```

- ready = `open` or `rework`; the assignee is the claim lock; `--actor` on
  every mutation.
- Poison gates make every non-batch path to `closed` unsatisfiable; only
  `batch_pending -> closed` under the real `batch_verify` gate can close.
- `allow_bypass: false`; close reason required; self-close forbidden.
- Capacity caps bound verification debt (e.g., in_progress hard 12;
  in_progress + batch_pending hard 24).
- Per-assignee one-in-progress usually cannot be expressed in tracker policy —
  the orchestrator enforces it via preflight before granting a claim and
  monitors violations every tick.

Canary this enforcement at swarm startup with disposable items (illegal
direct close, double claim, close without gate, stale revision-scoped PASS).
Policy files are claims until canaried — one real startup canary found three
invariants that were silently unenforced.

## Phase 1 — Code-First Wave (all agents, parallel, no test builds)

Each agent, in a loop:

1. Claim the highest-priority ready bead (assignee lock, `--actor`).
2. Write the **real code and its real tests** — same bead, no placeholders.
3. Run at most a syntax gate (`cargo check -p <crate>` or equivalent). No
   `cargo test`, no remote builds, no proof-waiting.
4. Commit immediately with the bead ID and touched scope
   (`"… — code-first, batch-test pending"`).
5. Move the bead to `batch_pending` ONLY when substantively complete: code
   plus tests written, bead-linked commit, owned paths respected, every
   acceptance checkbox mapped to a concrete test, no known defect.
   `batch_pending` earns no capability credit; it frees claim capacity.
6. Take the next bead.

Commit rate during Phase 1 is a **saturation signal for the orchestrator,
never an agent KPI** — the moment agents are scored on commits you get
microcommit pumping (see HONEST-CREDIT in the vibing-with-ntm skill).

## Phase 2 — Batch Verify and Close (orchestrator, once per wave)

1. **Commit-flush** the swarm so the tree is consistent; record the clean
   HEAD/tree SHA.
2. Run **one** build/test pass over the union of touched scope on a
   dedicated orchestrator target directory (exempt from build-kill).
   Touched scope is derived from the `wave_base..verified_head` git diff
   range plus reverse dependents (e.g., Cargo reverse deps) and the non-code
   ownership map — **never from agent-declared scope**.
3. **Fix compile errors first.** A single test-target compile error makes
   `cargo test` abort early and report a misleadingly green prefix (a real
   wave saw "240/0 green" that was actually 793/17 once it compiled). Only a
   fully-compiling run yields a true pass/fail count.
4. Cluster remaining failures **by file**, and return each failing bead to
   `rework` for the same assignee with the exact assertion and location. The
   verifier triages; it does not silently finish the work.
5. Re-run until green. First-attempt failures stay recorded; rerun-until-green
   is not flake proof — every attempt is retained in the wave receipt.
6. Record the `batch_verify` gate and close only green `batch_pending` beads,
   citing the run:

   ```bash
   br gate report <id> --gate batch_verify --provider batch-orchestrator \
     --status pass --to closed --note "run:<id> commit:<sha> suites:<...>"
   br close <id> --reason "<evidence>" --transition-comment "<batch summary>"
   ```

7. The verification receipt is **revision-bound**: HEAD/tree SHA, dirty
   inventory, toolchain and lockfile identities, exact commands, selected
   tests, seeds/subjects, and the exact bead list. Any HEAD or relevant-file
   movement invalidates the run. Gate results are revision-scoped — a PASS
   recorded against an earlier status revision is not effective for a later
   close after rework (canary this; the FAIL-overwrite at rework dispatch is
   defense-in-depth, not the primary defense).

Coverage rule: a green union suite must map **every closing bead to the exact
tests that exercised its touched behavior**. Never close a wave off one broad
green command.

## Triggers (Phase 1 → Phase 2)

Flip on the **earliest** of — never on the commit-rate dip alone (with a large
graph the ready pool may never drain, so the dip may never come):

- ready-pool depletion;
- verification-debt ceiling (policy caps on in_progress + batch_pending);
- an articulation-point bead becoming verifiable (its dependents are starving);
- a touched-scope frontier (the wave now spans too much to verify cheaply);
- an elapsed-time or risk bound;
- a commit-rate dip (one signal among several).

Self-pacing; no fixed timer.

## The Pump (Why Closing Refills Work)

Trackers unblock a dependent only when its blocker is **closed** — not when it
is committed-but-pending. During Phase 1 the ready pool drains and does not
refill; the unblock wave fires only at the Phase-2 close step, when green
beads close and their dependents flip to ready in a burst. So the loop is a
pump: each Phase-2 pass closes a layer, which unblocks the next layer, which
feeds the next Phase-1 wave. **Periodic cycles keep the swarm fed; one giant
end-pass would starve it.**

## Enforcement (What Keeps It Honest)

Agents want to build — to "prove" their work — so the model is actively
enforced, not requested:

- **Build-kill:** every tick the orchestrator kills per-agent test/full-build
  processes. Scope the kill by owned PID/pane target directory — never broad
  process-name kills (`cargo check` is exempt, as is the orchestrator's own
  batch-verify target dir).
- **Explicit directive:** the syntax gate is the per-bead maximum; commit
  immediately; no remote-proof waiting.
- **KPI reframing:** Phase-1 success is wave saturation, measured by the
  orchestrator; per-bead closures arrive in bursts during Phase 2 and
  capability credit exists only there.
- **Central closure:** only the orchestrator closes, with cited evidence;
  genuinely incomplete work stays in_progress/rework with a comment — never
  false-close. A close by anyone else is reopened with an incident comment.
- **Watchdogs:** disk trajectory and build-process counts every tick — a
  spike means enforcement slipped; re-kill.

## Hard-Won Gotchas

- **Shared main, no git surgery.** One agent's `git reset` can orphan a
  peer's commit. Before assuming loss, verify with
  `git merge-base --is-ancestor <sha> HEAD`.
- **Stale rate-limit displays.** A "usage limit" message persists in a pane
  buffer and the CLI won't auto-retry; nudge and confirm before idling a pane
  (a false outage once idled a swarm for ~5.5 hours).
- **Degraded Agent Mail.** Fall back to bead-assignee locking instead of
  blocking on mail reservations.
- **Never silence stderr in evidence-bearing commands.** A verification chain
  run with `>/dev/null 2>&1` can silently fail mid-chain and manufacture a
  false empirical claim; keep and store all output from canaries and verify
  runs.
- **Early-abort greens.** Any aggregated test command that can abort early on
  a compile error will report a misleading prefix as if it were the total.

## Honest-Credit Binding

This doctrine only works when credit is honest: no fixture-as-live-proof, no
gate self-weakening, no close-pump, no refusal-only closes, no
placeholder-macro commits. The incentive layer — named reward-hacking
patterns, Goodhart controls, refusal calibration, and how to encode all of it
into beads (root meta bead with inherited `agent_context`, frozen checkbox
acceptance criteria, no-claim boundaries, blocked-born external leaves) —
lives in the vibing-with-ntm skill's HONEST-CREDIT reference. Load both
before running a wave; encode both in the repo's AGENTS.md and in the work
items themselves so every swarm agent sees the law at claim time, not just
the orchestrator.
