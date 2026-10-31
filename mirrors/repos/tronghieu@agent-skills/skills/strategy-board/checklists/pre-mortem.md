# Pre-mortem Check

*Run by Taleb during Phase 4, on the direction chosen at Gate 2. Session
protocol lives in `references/boardroom.md`; this checklist verifies the
output is worth the meeting.*

## Setup

- [ ] The failure premise was total and specific: "three years out, it failed
      badly" — not "what are some risks".
- [ ] Independent takes came first: each seated member wrote their failure
      history before hearing the others.
- [ ] The right lenses were seated: Taleb always; Wack if futures diverge;
      Grove if execution assumptions are load-bearing; Graham if the numbers are.

## Failure paths

- [ ] 2–3 paths, each *specific*: named mechanisms, magnitudes, and timing —
      "integration slipped 9 months and the anchor client churned", never
      "execution risk".
- [ ] At least one path attacks the evidence, not the plan (a load-bearing
      fact that turns out wrong, a biased source, a benchmark that didn't
      transfer).
- [ ] At least one path involves an actor responding — a competitor, regulator,
      or key person doing the thing our plan assumes they won't.
- [ ] At least one path attacks a dependency seam the option relies on —
      vendor API capability/latency, an integration, a partner's roadmap, an
      SI's staffing — especially for hybrid / buy-core-build-edge options.
- [ ] The ruin question was asked explicitly: does any path exceed the maximum
      tolerable loss the executive stated in the brief? If yes → restructure or
      escalate, not "mitigate".

## Outputs (into minutes and recommendation)

- [ ] Every credible path has an **earliest observable warning** — a signpost
      with a threshold, wired into `roadmap.md`.
- [ ] Cheap mitigations were actually adopted (or their rejection justified);
      expensive ones were priced, not hand-waved.
- [ ] The **risks accepted** table in `recommendation.md` lists what survives,
      plainly — the executive signs knowing what they are accepting.
- [ ] Dissent recorded in `decision-log.md`, including Taleb's, even when
      overruled — *especially* when overruled.

## Anti-theatre

- [ ] The pre-mortem changed something — a mitigation, a stage-gate, a
      signpost, a number. A pre-mortem that changed nothing was either a
      rubber stamp or run too late.
- [ ] It did not silently relitigate Gate 2: if a finding genuinely breaks the
      chosen direction, it went to the executive as exactly that.
