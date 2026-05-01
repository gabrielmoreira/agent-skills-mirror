# Skill Benchmark Design Checklist

## Benchmark Scope

- Skill or bundle under test:
- Target user:
- Target artifact:
- Decision supported:
- Public or private evaluation:

## Scenario Set

- Normal workflow scenario
- Ambiguous or incomplete-context scenario
- High-risk boundary scenario
- Regression scenario for a known prior failure
- Optional competitor/baseline comparison

## Run Design

- Same prompt for baseline and skill-enabled runs
- Same source material and workspace state
- Same time, turn, and tool constraints where practical
- No expected answer leaked into prompt
- Human reviewer identified for high-risk artifacts

## Evidence Capture

- Scenario file
- Source input
- Baseline output
- Skill-enabled output
- Validation output
- Reviewer notes
- Overhead notes

## Decision Rule

Use one of:

- Keep: better output with acceptable overhead and no new safety issue.
- Revise: valuable workflow but trigger, process, output, or safety needs work.
- Split: one skill is handling unrelated jobs.
- Merge: the skill is a minor variant of an existing workflow.
- Defer: workflow needs more evidence or safer context.
- Retire: skill adds overhead, stale guidance, or risk without benefit.
