# Response Stream End Extensions DOX

## Purpose

- Own finalization of assistant response stream content.

## Ownership

- Ordered Python files own final masking and stream-end log updates.

## Local Contracts

- Preserve final masking before response content is considered complete.
- Keep log state consistent with streamed chunks and final response text.
- Preserve explicit planning fields; when `thoughts` are absent, expose native
  reasoning summaries as thoughts after both streams finish.

## Work Guidance

- Coordinate finalization changes with live response and message rendering behavior.

## Verification

- Smoke-test response completion and persisted message display after changes.

## Child DOX Index

No child DOX files.
