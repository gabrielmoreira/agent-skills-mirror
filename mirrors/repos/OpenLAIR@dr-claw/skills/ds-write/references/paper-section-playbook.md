# Paper Section Playbook

Use this reference when the output is a paper or paper-like report.

## Introduction

The introduction should usually answer:

- why this problem matters now
- what the baseline or prevailing route does
- what concrete bottleneck remains
- what the quest changed
- what evidence supports that change
- what the contribution scope really is

After experiments stabilize, revisit the introduction and shrink any claim that no longer matches the evidence.

## Related work

Do more than list papers.
Show:

- which prior routes are closest
- which assumption, mechanism, or scope differs
- why the current quest is not just a rename of prior work

## Method

Keep the method section faithful to the implemented path:

- no fictional components
- no omitted caveats that materially change interpretation
- no theory section detached from the code

If equations are used:

- define symbols
- tie the objective or mechanism back to the implementation
- avoid decorative math that explains nothing

## Experiments

Prefer this flow:

1. setup and evaluation contract
2. main comparison
3. ablations or component analysis
4. robustness or error analysis
5. limitations visible from the results

All numerical claims should point to specific tables, figures, or artifact paths.

## Limitations

Limitations should be concrete:

- what was not tested
- what remained unstable
- which claims were intentionally downgraded
- which comparisons were not comparable enough to use

## Conclusion

The conclusion should summarize what was actually shown, not restate the highest hope from the start of the quest.
