# Acceptance Criteria Mapper Checklist

## Criterion Pattern

Use:

```text
Given <context>, when <agent/user does action>, then <observable result>.
Evidence: <file/output/test/reviewer note>.
```

## Good Criteria

- Observable
- Reviewable by a human
- Tied to the target artifact
- Possible to verify without private systems
- Explicit about required evidence
- Clear about safety gates

## Weak Criteria

- "High quality"
- "Better"
- "Useful"
- "Production ready"
- "Executive grade"
- "Secure"

Replace weak criteria with concrete checks.

## Safety Criteria

Add criteria for:

- explicit approval before writes or sends
- assumptions labeled
- missing evidence surfaced
- high-risk domain escalated
- private data excluded from public artifacts
