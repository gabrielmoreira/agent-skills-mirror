# Codebase Audit Checklist

Use this during baseline analysis before deciding whether to attach, import, reproduce, or repair.

## Minimum audit coverage

Record:

- repository or package identity
- main entrypoints
- training path
- evaluation path
- data loading and preprocessing path
- configuration path
- metrics computation path
- output and checkpoint locations

## Implementation map

Identify:

- key classes and functions
- scripts that are likely to be run directly
- modules with high coupling
- modules where later changes are most likely to occur

## Practical constraints

Check:

- external services or downloads
- hardware assumptions
- heavy memory or compute hotspots
- brittle or undocumented environment requirements

## Baseline understanding goal

A later stage should be able to answer all of the following from your audit without reopening the entire repo:

- what the baseline does
- how it is run
- how it is evaluated
- where the main risks or bottlenecks are
- which files will matter most for future modifications
