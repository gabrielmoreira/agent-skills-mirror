# What a Spec Is For: Decisions, Alternatives, and the Blast Radius

A technical spec is not a description of code you're about to write — it's a device for extracting the expensive disagreements EARLY, while they cost a meeting instead of a migration. Everything in a good spec serves that.

## The three sections that do the work

1. **The decision(s) being made.** Name them explicitly ("this spec decides: queue vs stream; sync vs async retries; where dedup lives"). Reviewers who know what's being decided review THAT; reviewers given twelve pages of design-as-fait-accompli nitpick naming.
2. **Alternatives with real trade-offs.** For each decision: 2-3 options, honest strengths of the losers, and the reason the winner wins *tied to a stated constraint*. A spec with no credible alternatives wasn't specced — it was announced. (The rejected options become the ADR graveyard later.)
3. **Blast radius.** What this touches that isn't obvious: data migrations and their order, API consumers, on-call surface, cost curve at 10× scale, the teams whose roadmap this constrains. The comment "wait, this breaks our export flow" is worth the entire spec process — design the section to fish for exactly that comment.

## Sizing the spec to the risk

One-way-door decisions (schemas, protocols, tenancy models) get full specs with review meetings. Two-way doors get a page. Uniform ceremony teaches people to skip the process exactly when it matters. Ask first: "what here is expensive to reverse?" — spec THAT; sketch the rest.

## The failure-mode section reviewers skip (and shouldn't)

Every spec answers: what happens when the dependency is down · when input is 100× expected · when the deploy is half-complete · how we detect each (the observability is part of the design, not an ops afterthought). "Failure handling: we'll retry" is the spec equivalent of "tested locally ✅".

## Review mechanics that get real feedback

Circulate with the decisions listed up top and a comment deadline · ask named reviewers for named concerns ("Priya: does this survive your team's migration?") · silence ≠ approval on one-way doors — chase the sign-offs · and record the review's outcome IN the spec ("open question §4 resolved: we'll dual-write for one release").
