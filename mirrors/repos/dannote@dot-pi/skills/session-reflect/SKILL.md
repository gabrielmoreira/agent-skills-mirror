---
name: session-reflect
description: Analyze a user's pi coding-agent session history for recurring behavior, prompting habits, workflow loops, friction, and preferences. Use when the user asks to inspect or reflect on pi sessions, common behavior patterns, agent/user interaction style, prompting habits, or personal pi workflow quality.
---

# Session Reflect

Use this skill to help the user understand their own pi usage patterns from local session logs.

## Data location

By default this skill writes only to:

```text
~/.pi/agent/cache/session-reflect/
```

It never writes analysis databases into the current project by default. Use `--db` only when the user explicitly asks for another location. Use `clean` to remove the default cache.

The skill's job is **evidence retrieval + agent judgment**. Do not turn the helper script into the analyst. Use the script to load/search/query session evidence; use your own reasoning to infer patterns cautiously.

## Core rules

- Discuss the analysis approach before implementing new tooling or making broad claims.
- Do not hardcode English behavior categories or phrase lists as conclusions.
- Treat repeated text, n-grams, FTS hits, and SQL aggregates as evidence leads, not interpretations.
- Inspect surrounding context before interpreting short user turns like “go ahead” or “what next”.
- Preserve multilingual text, typos, shorthand, pasted logs, and frustration markers as meaningful evidence.
- Cite session paths or message keys for important claims.
- Separate: observed facts, interpretations, confidence, alternative explanations, recommendations.
- When the current user message is itself a high-signal intervention, follow the recovery protocol in `references/intervention-events.md` before continuing.

## Helper script

Use `scripts/session-db.ts` as a local evidence workbench. It loads pi JSONL sessions into DuckDB and exposes SQL/search/context helpers.

Install helper dependencies from the skill directory if they are missing:

```bash
cd <dot-pi>/skills/session-reflect
bun install
```

Typical first step:

```bash
bun scripts/session-db.ts build
```

If the user points to another session root:

```bash
bun scripts/session-db.ts build --root <session-root>
```

Useful evidence commands:

```bash
bun scripts/session-db.ts doctor
bun scripts/session-db.ts preset --list
bun scripts/session-db.ts preset overview
bun scripts/session-db.ts preset exact-short-repeats
bun scripts/session-db.ts preset long-sessions
bun scripts/session-db.ts turns --role user --limit 80
bun scripts/session-db.ts turns --role user --short --limit 100
bun scripts/session-db.ts ngrams --n 2 --min-count 3 --limit 50
bun scripts/session-db.ts ngrams --n 3 --min-count 3 --limit 50
bun scripts/session-db.ts search "literal or fuzzy lead" --role user --limit 25
bun scripts/session-db.ts context <message_key> --before 4 --after 8
bun scripts/session-db.ts context <message_key> --before 4 --after 8 --compact --hide-tools
bun scripts/session-db.ts examples --text "Go ahead." --limit 5 --before 3 --after 5
bun scripts/session-db.ts sample --turns 5 --examples 2 --before 3 --after 5
bun scripts/session-db.ts interventions --limit 30 --min-score 2 --sort score
bun scripts/session-db.ts interventions --limit 30 --min-score 2 --sort recent
bun scripts/session-db.ts interventions --signal autonomy_boundary,evidence_challenge --limit 20
bun scripts/session-db.ts interventions --project quackdb --since 2026-06-01 --limit 20
bun scripts/session-db.ts interventions --sample --limit 10 --min-score 2
bun scripts/session-db.ts interventions --pasted include --limit 20 --min-score 2
bun scripts/session-db.ts interventions --pasted only --limit 20 --min-score 2
bun scripts/session-db.ts interventions --context --limit 10 --min-score 2 --sort recent --before 4 --after 6
bun scripts/session-db.ts sql "select ..."
```

Use `--format table|json|markdown` before the subcommand when output will be read by the agent or quoted in a report:

```bash
bun scripts/session-db.ts --format markdown preset exact-short-repeats
bun scripts/session-db.ts --format json context <message_key>
```

Read [references/query-cookbook.md](references/query-cookbook.md) when selecting SQL queries. Read [references/reflection-protocol.md](references/reflection-protocol.md) before producing a user-facing reflection. Read [references/intervention-events.md](references/intervention-events.md) when analyzing shouting, profanity, corrections, frustration, stop/pause requests, evidence challenges, or any high-signal user redirect.

## Recommended workflow

1. Clarify scope: recent sessions vs all sessions, coding-only vs all pi use, desired output depth.
2. Build or refresh the DuckDB evidence database with `scripts/session-db.ts build`.
3. Run a bounded first-pass evidence set: `overview`, `exact-short-repeats`, `tools`, `long-sessions`, and `sample --turns 3 --examples 2`. Add n-grams only when exact repeats do not explain enough.
4. Pick surprising evidence leads and retrieve compact context windows around representative message keys. For repeated exact turns, use `examples --text ...` for targeted sampling or `sample` for time-spread examples across top repeated turns. Use `--compact --hide-tools` first; rerun without them only when tool output matters.
5. For friction analysis, treat candidate events as broad **interventions**, not just profanity/escalation. Use `references/intervention-events.md` before generalizing.
6. Run targeted searches for explicit current-user preferences mentioned in the conversation, then inspect context.
7. Reason manually from evidence; do not let preset names, query names, repeated phrases, profanity, or all-caps become conclusions.
8. Present a concise reflection with citations and confidence levels.
9. Ask whether the user wants tooling changes, pi prompt/default changes, or deeper follow-up analysis.

## Output shape

Use this structure unless the user asks otherwise:

```markdown
# Pi session behavior reflection

## Evidence inspected

- Database/session scope
- Query types used

## Observed patterns

For each pattern:

- Observation
- Evidence
- Interpretation
- Confidence
- Alternative explanation

## Friction / failure modes

## Preferences inferred from behavior

## Recommendations to test

## Open questions
```
