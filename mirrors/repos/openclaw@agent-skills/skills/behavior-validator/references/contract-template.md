# Behavior Contract Template

Use this shape when the user has not provided a behavior contract. Keep it short enough that a source-blind validator can execute it without reading implementation notes.

```md
# Behavior Contract

## User-Visible Goal
<What must be true from the user's point of view.>

## Target
- Type: web app | CLI | API | generated artifact | other
- Launch or access: <URL, command, endpoint, artifact path, or setup command>
- Allowed fixtures and credential source: <fixtures plus approved secret-tool or exact environment-variable names; never values>

## User Tasks
1. <Concrete task a real user/operator performs.>
2. <Concrete task a real user/operator performs.>

## Expected Observable Behavior
- <Screen, CLI output, API response, file content, state change, or persistence rule.>
- <Failure behavior for invalid input or unavailable data.>

## Anti-Cheat Probes
- <Change fixture/input data and verify output changes accordingly.>
- <Refresh/retry/reopen and verify expected persistence or reset behavior.>
- <Try invalid/empty/boundary input and verify the promised handling.>

## Evidence Required
- <Screenshots, terminal excerpts, response snippets, file summaries, accessibility observations, or logs.>

## Out Of Scope
- <Anything the validator must not judge.>
```

Completion criterion: every user task and anti-cheat probe has an expected observable result and evidence type.
