---
name: daytona-recording-artifacts
description: Daytona recording volume, screenshots, artifacts, and validation evidence. Use when the user says record Daytona, recording volume, artifacts volume, screenshots, proof, PR evidence, before/after video, or validate behavior visually.
---

# Daytona Recording Artifacts

Use this skill to collect proof that a Daytona UI flow works. Recordings are for
humans. CDP assertions and screenshots are for AI validation and fast review.
Use `daytona-flow-validator` before declaring the flow passed.

## The Volume

The reusable Daytona volume is:

```text
openwork-eval-artifacts:/daytona-artifacts
```

The helper serves it on port `8090` when `--artifacts-volume` or
`--record-video` is used.

Expected layout:

```text
/daytona-artifacts/recordings
/daytona-artifacts/screenshots
/daytona-artifacts/validation
```

## Start With Artifacts

For screenshots and validation notes without video:

```bash
bash .devcontainer/test-on-daytona.sh [branch-or-commit] --artifacts-volume
```

For full human-review evidence:

```bash
bash .devcontainer/test-on-daytona.sh [branch-or-commit] --record-video --recording-name <name>
```

`--record-video` implies `--artifacts-volume`.

## Capture Screenshot Checkpoints

Capture a persistent screenshot from the Daytona display:

```bash
daytona exec "$SANDBOX" -- 'bash .devcontainer/capture-daytona-screenshot.sh'
```

Use this after important states: welcome screen, workspace created, settings
connected, task response visible, error state reproduced, or final success.

## Stop Recording

Always stop with the helper so ffmpeg finalizes the MP4 cleanly:

```bash
daytona exec "$SANDBOX" -- 'bash .devcontainer/stop-daytona-recording.sh'
```

Do not use `kill -9`; it can corrupt the file.

After stopping, verify the recording exists and has duration:

```bash
daytona exec "$SANDBOX" -- 'ls -lh /daytona-artifacts/recordings'
daytona exec "$SANDBOX" -- 'ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 /daytona-artifacts/recordings/<name>.mp4'
```

If the duration is near zero, missing, or the file is absent, the recording is
not usable evidence.

## Get Artifact URLs

Get the artifacts base URL:

```bash
ARTIFACTS_URL=$(daytona preview-url "$SANDBOX" -p 8090 2>/dev/null | grep -v "^time=")
```

Then append paths:

```bash
echo "${ARTIFACTS_URL}/recordings/<name>.mp4"
echo "${ARTIFACTS_URL}/screenshots/<name>.png"
```

## Before And After Flow

Use before/after recordings for UI regressions or design changes:

```bash
bash .devcontainer/test-on-daytona.sh dev --record-video --recording-name my-feature-before
daytona exec "$SANDBOX" -- 'bash .devcontainer/stop-daytona-recording.sh'
daytona exec "$SANDBOX" -- "bash -lc 'cd /workspace && git fetch origin feat/my-branch:feat/my-branch && git checkout feat/my-branch'"
daytona exec "$SANDBOX" -- "bash -lc 'cd /workspace && DISPLAY=:99 .devcontainer/start-daytona-recording.sh --detach --output /daytona-artifacts/recordings/my-feature-after.mp4'"
daytona exec "$SANDBOX" -- 'bash .devcontainer/stop-daytona-recording.sh'
```

## Validation Standard

Use all three layers when possible:

- CDP/browser assertions: prove URL, text, state, accessibility tree, and process state.
- Screenshots: provide fast visual checkpoints for AI and reviewers.
- Recording: prove the full flow to humans for PR review.

Do not report success from a recording alone. The AI should inspect state with
browser tools and use screenshots to validate visible behavior before declaring
the flow passed.

When a recording is required, start it before the first user-visible action in
the flow and stop it only after the final asserted state is visible.
