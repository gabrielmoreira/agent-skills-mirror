# AgentLogistics Codex Instructions

This repository is an open-source AI skill repository for commercial logistics,
warehousing, storage, inventory control, transportation, distribution, material
handling, and related operational analysis.

Follow `ROADMAP.md` as the development authority. Work in bounded waves and
record each wave status as `READY`, `PARTIALLY_READY`, or `BLOCKED` in the
appropriate development artifact.

## Development Rules

- Keep AgentLogistics independent from AgentSkills and ChefSkills. Use those
  repositories only as architectural references.
- Build atomic skills first. Professional roles belong in `skillsets/`.
- Separate knowledge, procedure, evidence, calculations, validation, and output
  format.
- Use progressive disclosure. Keep `SKILL.md` concise and move extended
  domain references into `references/` files.
- Do not create empty directory trees just to match the planned architecture.
  Add directories only when they contain real project content.
- Treat regulatory and safety material as jurisdiction-specific unless it is
  clearly universal.
- For calculation-oriented skills, define variables, units, formulas,
  assumptions, missing-input behavior, edge cases, interpretation, and at least
  one worked test case.
- Do not represent AI output as legal advice, engineering approval, equipment
  certification, operator certification, regulatory approval, or professional
  compliance signoff.

## Expected Skill Shape

Use this shape when a skill is introduced:

```text
skills/<domain>/<skill-name>/
  SKILL.md
  references/<task-specific-reference>.md
  agents/openai.yaml
```

Not every skill needs the same supporting files, but every skill must have a
clear trigger, non-trigger boundary, required inputs, procedure, output
contract, validation expectation, and safety boundary.

## Validation

Run the local validation wrapper before committing:

```powershell
.\scripts\validate-all.ps1
```

When new validators are added, include them in `scripts/validate-all.ps1`.
