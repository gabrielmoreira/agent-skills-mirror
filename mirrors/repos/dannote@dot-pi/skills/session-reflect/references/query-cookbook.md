# Query cookbook

Use these DuckDB queries as evidence-gathering starting points. Adapt them freely. Prefer built-in presets first, then custom SQL.

## Data location

By default the helper writes its DuckDB cache to `~/.pi/agent/cache/session-reflect/pi-sessions.duckdb`. Use `doctor` to inspect paths and `clean` to remove the cache.

## Helper output formats

Place `--format` before the subcommand:

```bash
bun scripts/session-db.ts --format table preset overview
bun scripts/session-db.ts --format json turns --role user --limit 20
bun scripts/session-db.ts --format markdown context <message_key>
```

## Presets

```bash
bun scripts/session-db.ts doctor
bun scripts/session-db.ts preset --list
bun scripts/session-db.ts preset overview
bun scripts/session-db.ts preset roles
bun scripts/session-db.ts preset recent-user-turns
bun scripts/session-db.ts preset short-user-turns
bun scripts/session-db.ts preset exact-short-repeats
bun scripts/session-db.ts preset tool-heavy-sessions
bun scripts/session-db.ts preset long-sessions
bun scripts/session-db.ts preset tools
```

Presets are query shortcuts, not behavioral categories. `build` recreates the DuckDB file from scratch so FTS/index state cannot leak across runs.

## Dataset overview

```sql
select
  count(*) as sessions,
  min(started_at) as first_session,
  max(started_at) as last_session
from sessions;
```

```sql
select role, count(*) as messages
from messages
group by role
order by messages desc;
```

## Recent user turns

```sql
select message_key, timestamp, project_key, left(replace(text, '\n', ' '), 500) as text
from message_context
where role = 'user'
order by timestamp desc
limit 100;
```

## Repeated exact short turns

```sql
select lower(trim(text)) as turn, count(*) as n
from messages
where role = 'user'
  and length(trim(text)) between 1 and 160
group by 1
having count(*) >= 3
order by n desc, turn
limit 100;
```

## Repeated prompt starts without assigning meaning

```sql
with starts as (
  select
    regexp_extract(lower(trim(text)), '^([^\n]{1,120})', 1) as first_line
  from messages
  where role = 'user'
)
select first_line, count(*) as n
from starts
where length(first_line) > 0
group by first_line
having count(*) >= 2
order by n desc
limit 100;
```

## Tool-heavy sessions

```sql
select s.session_id, s.project_key, s.path, count(*) as tool_calls
from tool_calls t
join sessions s using (session_id)
group by s.session_id, s.project_key, s.path
order by tool_calls desc
limit 25;
```

## Long/high-iteration sessions

```sql
select
  s.session_id,
  s.project_key,
  s.path,
  count(*) filter (where m.role = 'user') as user_turns,
  count(*) filter (where m.role = 'assistant') as assistant_turns,
  count(t.tool_call_key) as tool_calls
from sessions s
left join messages m using (session_id)
left join tool_calls t on t.message_key = m.message_key
group by s.session_id, s.project_key, s.path
order by user_turns + assistant_turns + tool_calls desc
limit 25;
```

## Context window around a message

Prefer the helper command. Start compact to reduce token count:

```bash
bun scripts/session-db.ts --format markdown context <message_key> --before 4 --after 8 --compact --hide-tools
bun scripts/session-db.ts --format markdown context <message_key> --before 4 --after 8 --compact --chars 220 --focus-chars 700
```

Rerun without `--compact` only when full text or tool output is important.

## Multiple examples for a repeated turn

Use this after `exact-short-repeats` finds a promising repeated turn:

```bash
bun scripts/session-db.ts --format markdown examples --text "Go ahead." --limit 5 --before 3 --after 5
bun scripts/session-db.ts --format markdown examples --text "whats next" --contains --limit 5
```

Default matching is normalized exact text. Use `--contains` for broader retrieval.

## Time-spread samples across top repeated turns

Use this to avoid judging only the newest examples:

```bash
bun scripts/session-db.ts --format markdown sample --turns 5 --examples 2 --before 3 --after 5
```

The command finds top repeated exact short user turns, then samples matching contexts spread across time.

## Intervention candidates

Use this for broad high-signal user redirects, not just profanity/shouting:

```bash
bun scripts/session-db.ts --format markdown interventions --limit 30 --min-score 2 --sort score
bun scripts/session-db.ts --format markdown interventions --limit 30 --min-score 2 --sort recent
bun scripts/session-db.ts --format markdown interventions --signal autonomy_boundary,evidence_challenge --limit 20
bun scripts/session-db.ts --format markdown interventions --project quackdb --since 2026-06-01 --limit 20
bun scripts/session-db.ts --format markdown interventions --sample --limit 10 --min-score 2
bun scripts/session-db.ts --format markdown interventions --pasted include --limit 20 --min-score 2
bun scripts/session-db.ts --format markdown interventions --pasted only --limit 20 --min-score 2
bun scripts/session-db.ts --format markdown interventions --context --limit 10 --min-score 2 --sort recent --before 4 --after 6
```

Signals are retrieval leads. `score` is a rough retrieval priority, not severity. Use `--min-score 2` to suppress many single weak markers such as uppercase identifiers. Use `--sort score` for strongest candidates and `--sort recent` for current-session investigation. Use `--signal` for one or more comma-separated signals, `--project` for project/path/cwd filtering, `--since/--until` for date windows, and `--sample` for time-spread examples. `--pasted exclude` is the default; use `--pasted include` to audit all candidates and `--pasted only` to inspect likely pasted/code/log false positives. Read [intervention-events.md](intervention-events.md) before interpreting results.

Equivalent SQL:

```sql
with target as (
  select session_id, turn_index
  from messages
  where message_key = '<message_key>'
)
select m.message_key, m.turn_index, m.role, left(m.text, 1200) as text
from messages m, target t
where m.session_id = t.session_id
  and m.turn_index between t.turn_index - 4 and t.turn_index + 8
order by m.turn_index;
```

## FTS / text search

Use the helper first:

```bash
bun scripts/session-db.ts search "some phrase" --role user --limit 25
```

The helper tries literal `ILIKE` matches before DuckDB FTS. This is intentional: literal phrase hits are often better evidence for human judgment than broad BM25 term matches.

Direct FTS query:

```sql
select
  message_key,
  timestamp,
  role,
  project_key,
  fts_main_messages.match_bm25(message_id, 'query terms') as score,
  left(replace(text, '\n', ' '), 700) as text
from message_context
where score is not null
order by score desc
limit 25;
```

## Tool usage vocabulary

```sql
select name, count(*) as calls
from tool_calls
group by name
order by calls desc
limit 50;
```

## Caveats

- Pasted logs and subagent outputs can appear as user messages and distort n-gram counts.
- Autoresearch loops can dominate recent sessions.
- FTS scoring is a retrieval aid, not semantic similarity.
- Short turns require context before interpretation.
