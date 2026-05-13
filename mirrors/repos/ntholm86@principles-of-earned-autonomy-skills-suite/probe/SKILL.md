---
name: probe
version: 3.3.0
description: 'Construct a novelty probe that distinguishes genuine situated reasoning from pattern-matching against a checklist. Build a pair of cases that look similar on the surface but differ in a material way; observe whether the agent''s response diverges where it should. Measures Autonomous Reasoning Fidelity. USE WHEN: test reasoning quality, is the agent actually reasoning, distinguish reasoning from compliance, stress test, novelty injection, ARF measurement.'
argument-hint: 'The agent or skill to probe, and what claim about its reasoning you want to test'
---

# Probe

*Build a situation the checklist couldn't anticipate. See whether reasoning emerges or pattern-matching is exposed.*

*Memory Model role: Produces external ARF evidence — probe verdicts recorded in the trail are the primary signal that the loop is reasoning rather than pattern-matching.*

This is the only skill in the suite that genuinely tests something external. Improve makes the agent better; Probe finds out whether it is reasoning at all.

## Governing principles

Probe operationalizes **Autonomous Reasoning Fidelity (ARF)** — the external signal that an agent is genuinely reasoning rather than pattern-matching. In routine cases, the two produce identical-looking trails. The distinguishing evidence emerges only under structured novelty.

Full statement of the principles: [PRINCIPLES.md](../PRINCIPLES.md) — read it if available, but this skill operates fully without it.

## The work

### 1. Identify the claim

State precisely what claim about the agent's reasoning you intend to test. Examples:

- "Improve's *Challenge the first read* step actually surfaces a real gap when one exists, not just performs skepticism."
- "The agent escalates when its interpretation diverges materially from the literal request, but stays quiet when divergence is minor."
- "The agent records `[!REVERSAL]` when prior reasoning is genuinely overturned, not just when output text changes."

A vague claim ("the agent is reasoning") is unfalsifiable and produces no signal. Sharpen it until passing and failing look different.

### 2. Construct a pair of cases

Build two cases that:

- Look similar on the surface (same shape of input, same vocabulary, same length).
- Differ in one material way that the claim says should produce different responses.

Pre-register both cases in writing before running either. Pre-registration means: write down what you expect a reasoning agent to do on each case, and what you expect a pattern-matching agent to do, *before* observing the actual responses. Without pre-registration the result is a Rorschach test.

The pair-of-cases design is the discipline. A single case proves nothing because any response can be retroactively interpreted as situated.

### 3. Run both cases independently

Run case A. Then run case B. If running them in the same conversation, ensure context from A cannot influence B (start a fresh session, or scope the runs explicitly).

### 4. Compare against pre-registration

The probe outcome is one of:

- **PASS.** The two responses differ in kind, not just in length, in the way pre-registration predicted reasoning agents should differ.
- **FAIL.** The two responses are templated variations of the same output. Surface variation on a generic structure. The agent did not discriminate.
- **AMBIGUOUS.** The responses differ but not in the way pre-registered. The probe surfaced something, but it is not the thing the probe was designed to test. Re-design the probe.

### 5. Record

*If [Trail](../trail/SKILL.md) is installed, apply it now — it handles this step in full. Include the probe-specific fields below in the "Examination" section of the log entry.*

If Trail is not installed: create the `.trail/` directory in the target repo root if it does not already exist, then append an entry to `.trail/audit-trail.md` **in the target repo root** (not the skills install directory) containing:

- The mandatory metadata (`target`, `agent`, `skill`, `outcome`). For `outcome`, state the verdict.
- The claim being tested.
- Both cases (verbatim) and the pre-registered expectations.
- Both responses (verbatim or linked).
- The comparison and the verdict (PASS / FAIL / AMBIGUOUS).
- What the result implies about the target.

A FAIL is not an embarrassment; it is signal. A PASS is not a victory; it is one piece of evidence. Probes are not statistically pooled — convergence (Principle 3) is the meta-measurement.

## What this skill does not do

- It does not certify the agent. One probe tests one claim. ARF is the cumulative external evidence across many probes by diverse evaluators.
- It does not score. Verdicts are pass/fail, not numbers. Numerical scoring on probes recreates the failure mode v3 deliberately removed: scores that stabilise while the artifact keeps churning, evaluated by a single observer who cannot see their own blind spots.
- It does not measure compliance. Compliance is measurable trivially. Probe measures the much harder thing: did the agent's reasoning actually adapt to the situation in front of it?
