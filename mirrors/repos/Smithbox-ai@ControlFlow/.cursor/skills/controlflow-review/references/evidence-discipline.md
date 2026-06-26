# Evidence Discipline

Good reviews separate what you observed from what you inferred.

## Strong Evidence

- direct file and line references
- command output you personally ran
- repository tests or fixtures that demonstrate the behavior

## Acceptable Inference

- short extrapolations from nearby code when the connection is obvious
- architectural implications that follow directly from the implementation

Mark these as inference, not as verified facts.

## Weak Evidence

- memory of older file contents
- assumptions about framework defaults you did not verify
- "this probably breaks" with no code path or reproduction hint

## Rule

If you cannot point to the file, line, command output, or a precise reasoning path, downgrade the finding or omit it.
