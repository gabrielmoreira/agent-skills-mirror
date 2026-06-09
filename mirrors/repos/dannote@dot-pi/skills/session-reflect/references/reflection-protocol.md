# Reflection protocol

Use this protocol when turning pi session evidence into behavioral reflection.

## Judgment discipline

1. Start from specific examples, not labels.
2. Inspect context windows before interpreting terse turns.
3. Treat typos, casing, punctuation, repeated commands, and corrections as signals only after seeing context.
4. Do not assume English-only language or standard spelling.
5. Avoid moralizing. Describe interaction mechanics and workflow consequences.
6. Prefer “appears to”, “in these sessions”, and “one plausible interpretation” when evidence is partial.

## Pattern card

Use this internal template for each candidate pattern:

```markdown
### Candidate pattern

- Evidence lead: repeated phrase / query result / session shape
- Representative message keys:
- Context checked: yes/no
- What happened before:
- What the user did:
- What the agent did after:
- Interpretation:
- Alternative interpretation:
- Confidence: low / medium / high
```

Only promote a candidate pattern into the final answer after at least two context checks, unless the pattern is explicitly visible in the current conversation.

## Common evidence dimensions

These are dimensions to inspect, not hardcoded categories. For high-signal redirects, corrections, profanity, shouting, stop requests, or evidence challenges, also read [intervention-events.md](intervention-events.md).

- Session start style: broad request, concrete implementation, debugging, review, continuation.
- Steering style: short approvals, corrections, constraints, meta-instructions, escalation.
- Interaction loop: plan → act → inspect → continue, or discuss → refine → implement.
- Agent-control preferences: when the user wants autonomy vs discussion before action.
- Evidence expectations: tests, diffs, screenshots, citations, measurements, runtime proof.
- Friction points: premature implementation, over-packaging, wrong abstraction level, weak evidence.
- Tooling preferences: local-first, minimal architecture, JS/Bun, database/search helpers, useful libraries.

Use these dimensions as lenses while reading evidence. Do not force every session into them.

## Final reflection standards

- Cite message keys or session paths for non-obvious claims.
- Include at least one “alternative explanation” for major claims.
- Include “recommendations to test”, not permanent prescriptions.
- Mention limitations: session subset, logs may include subagent/autoresearch loops, pasted external text can distort repeated phrases.
- Repeated n-grams can be dominated by pasted instructions, benchmark text, or autoresearch templates; use context before treating them as user habits.
- Very frequent exact short turns often indicate workflow mechanics, but their meaning still depends on preceding assistant output.
- Do not analyze profanity or all-caps as a standalone category. Treat them as possible markers of broader intervention events.
