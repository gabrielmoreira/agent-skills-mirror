# Scenario Test Authoring Checklist

## Scenario Prompt

- Names a real user job
- Produces a reviewable artifact
- Does not name the skill directly unless testing skill invocation wording
- Does not include the answer
- Avoids private data and live-system requirements
- Includes approval language for high-risk work

## Routing

- Uses exact skill folder names
- Includes supporting skills only when they materially change the workflow
- Avoids over-routing to unrelated bundles
- Adds new skills only after the folder exists or the scenario is explicitly
  documenting planned work

## Files

- `tests/scenarios/<scenario-name>.md`
- `tests/expected-routing.yaml`

## Validation

Run:

```powershell
.\scripts\validate-skills.ps1
```

Expected result:

- scenario count increases when a file is added
- every expected route maps to an existing skill folder
- docs consistency still passes
