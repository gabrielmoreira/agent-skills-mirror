---
name: copilot-usage-report
description: "Generate a Copilot CLI usage style report from session history. Use when asked to analyze usage patterns, generate a usage report, review prompting style, or summarize how Copilot is being used."
---

# Copilot Usage Report — Domain Knowledge

## Purpose

Generate a comprehensive usage style report by querying the `session_store_sql` tool across multiple dimensions. The report covers session shape, timing patterns, prompting style, technical fingerprint, and behavioral patterns.

## Report Structure

The report should have these sections:
1. **Overview** — high-level metrics table
2. **Session Shape** — turn count distribution
3. **When You Work** — hour-of-day and day-of-week patterns
4. **Prompting Style** — message length, verb patterns, workflow patterns, corrections
5. **Technical Fingerprint** — file types, models used
6. **Key Behavioral Patterns** — synthesized observations

## Queries

Run these queries against `session_store_sql`. Start with 90 days; widen if data is sparse.

### 1. Session overview

```sql
SELECT
  COUNT(*) as total_sessions,
  COUNT(DISTINCT repository) as unique_repos,
  MIN(created_at) as earliest,
  MAX(updated_at) as latest
FROM sessions
WHERE created_at > now() - INTERVAL '90 days'
```

### 2. Top repos

```sql
SELECT repository, COUNT(*) as session_count
FROM sessions
WHERE created_at > now() - INTERVAL '90 days'
AND repository IS NOT NULL
GROUP BY repository
ORDER BY session_count DESC
LIMIT 15
```

### 3. Message length distribution

```sql
SELECT
  COUNT(*) as total_messages,
  AVG(length(COALESCE(user_message, ''))) as avg_length,
  PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY length(COALESCE(user_message, ''))) as median_length,
  PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY length(COALESCE(user_message, ''))) as p75_length,
  PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY length(COALESCE(user_message, ''))) as p95_length
FROM turns
WHERE timestamp > now() - INTERVAL '90 days'
AND user_message IS NOT NULL
AND length(COALESCE(user_message, '')) > 0
```

### 4. Word count buckets

```sql
SELECT
  CASE
    WHEN length(COALESCE(user_message, '')) - length(REPLACE(COALESCE(user_message, ''), ' ', '')) + 1 <= 3 THEN '1-3 words'
    WHEN length(COALESCE(user_message, '')) - length(REPLACE(COALESCE(user_message, ''), ' ', '')) + 1 <= 8 THEN '4-8 words'
    WHEN length(COALESCE(user_message, '')) - length(REPLACE(COALESCE(user_message, ''), ' ', '')) + 1 <= 15 THEN '9-15 words'
    WHEN length(COALESCE(user_message, '')) - length(REPLACE(COALESCE(user_message, ''), ' ', '')) + 1 <= 30 THEN '16-30 words'
    ELSE '30+ words'
  END as word_bucket,
  COUNT(*) as count,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) as pct
FROM turns
WHERE timestamp > now() - INTERVAL '90 days'
AND user_message IS NOT NULL
AND length(COALESCE(user_message, '')) > 1
GROUP BY word_bucket
ORDER BY
  CASE word_bucket
    WHEN '1-3 words' THEN 1 WHEN '4-8 words' THEN 2
    WHEN '9-15 words' THEN 3 WHEN '16-30 words' THEN 4 ELSE 5
  END
```

### 5. Prompt verb patterns

Categorize the first word/phrase of each message:

```sql
SELECT
  CASE
    WHEN user_message ILIKE 'create a plan%' THEN 'create a plan...'
    WHEN user_message ILIKE 'implement%' THEN 'implement...'
    WHEN user_message ILIKE 'update%' THEN 'update...'
    WHEN user_message ILIKE 'add%' THEN 'add...'
    WHEN user_message ILIKE 'fix%' THEN 'fix...'
    WHEN user_message ILIKE 'investigate%' THEN 'investigate...'
    WHEN user_message ILIKE 'check%' THEN 'check...'
    WHEN user_message ILIKE 'look%' THEN 'look...'
    WHEN user_message ILIKE 'what%' THEN 'what...?'
    WHEN user_message ILIKE 'why%' THEN 'why...?'
    WHEN user_message ILIKE 'how%' THEN 'how...?'
    WHEN user_message ILIKE 'can you%' THEN 'can you...?'
    WHEN user_message ILIKE 'is %' OR user_message ILIKE 'are %' THEN 'is/are...?'
    WHEN user_message ILIKE 'does%' OR user_message ILIKE 'do %' THEN 'does/do...?'
    WHEN user_message ILIKE 'show%' THEN 'show...'
    WHEN user_message ILIKE 'find%' THEN 'find...'
    WHEN user_message ILIKE 'remove%' OR user_message ILIKE 'delete%' THEN 'remove/delete...'
    WHEN user_message ILIKE 'where%' THEN 'where...?'
    WHEN user_message ILIKE '/skill%' THEN '/command'
    WHEN user_message ILIKE 'ok%' OR user_message ILIKE 'yes%' OR user_message ILIKE 'go%'
      OR user_message ILIKE 'do it%' OR user_message ILIKE 'lgtm%' OR user_message ILIKE 'sure%'
      OR user_message ILIKE 'correct%' OR user_message ILIKE 'good%' THEN '[affirmative]'
    WHEN user_message ILIKE 'no%' OR user_message ILIKE 'skip%' OR user_message ILIKE 'don''t%'
      OR user_message ILIKE 'stop%' OR user_message ILIKE 'wait%' THEN '[correction/redirect]'
    ELSE '[other]'
  END as pattern,
  COUNT(*) as count
FROM turns
WHERE timestamp > now() - INTERVAL '90 days'
AND user_message IS NOT NULL AND length(COALESCE(user_message, '')) > 1
GROUP BY pattern
ORDER BY count DESC
```

### 6. Turns per session

```sql
SELECT
  CASE
    WHEN turn_count <= 3 THEN '1-3 turns (quick task)'
    WHEN turn_count <= 10 THEN '4-10 turns (medium task)'
    WHEN turn_count <= 30 THEN '11-30 turns (deep task)'
    WHEN turn_count <= 100 THEN '31-100 turns (marathon)'
    ELSE '100+ turns (mega session)'
  END as session_size,
  COUNT(*) as sessions,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) as pct
FROM (
  SELECT session_id, COUNT(*) as turn_count
  FROM turns t JOIN sessions s ON t.session_id = s.id
  WHERE s.created_at > now() - INTERVAL '90 days'
  AND t.user_message IS NOT NULL AND length(COALESCE(t.user_message, '')) > 1
  GROUP BY t.session_id
)
GROUP BY session_size
ORDER BY CASE session_size
  WHEN '1-3 turns (quick task)' THEN 1 WHEN '4-10 turns (medium task)' THEN 2
  WHEN '11-30 turns (deep task)' THEN 3 WHEN '31-100 turns (marathon)' THEN 4 ELSE 5
END
```

### 7. Hour-of-day distribution

```sql
SELECT
  EXTRACT(HOUR FROM timestamp AT TIME ZONE 'America/Los_Angeles') as hour_pt,
  COUNT(*) as message_count
FROM turns
WHERE timestamp > now() - INTERVAL '90 days'
AND user_message IS NOT NULL AND length(COALESCE(user_message, '')) > 5
GROUP BY hour_pt
ORDER BY hour_pt
```

### 8. Day-of-week distribution

```sql
SELECT
  CASE EXTRACT(DOW FROM timestamp AT TIME ZONE 'America/Los_Angeles')
    WHEN 0 THEN 'Sun' WHEN 1 THEN 'Mon' WHEN 2 THEN 'Tue' WHEN 3 THEN 'Wed'
    WHEN 4 THEN 'Thu' WHEN 5 THEN 'Fri' WHEN 6 THEN 'Sat'
  END as day,
  EXTRACT(DOW FROM timestamp AT TIME ZONE 'America/Los_Angeles') as dow,
  COUNT(*) as messages
FROM turns
WHERE timestamp > now() - INTERVAL '90 days'
AND user_message IS NOT NULL AND length(COALESCE(user_message, '')) > 5
GROUP BY dow, day
ORDER BY dow
```

### 9. File types touched

```sql
SELECT
  CASE
    WHEN file_path ILIKE '%.ps1' THEN '.ps1'
    WHEN file_path ILIKE '%.cs' THEN '.cs'
    WHEN file_path ILIKE '%.md' THEN '.md'
    WHEN file_path ILIKE '%.yaml' OR file_path ILIKE '%.yml' THEN '.yaml'
    WHEN file_path ILIKE '%.json' THEN '.json'
    WHEN file_path ILIKE '%.csproj' THEN '.csproj'
    ELSE 'other'
  END as ext,
  COUNT(*) as file_count
FROM session_files
WHERE first_seen_at > now() - INTERVAL '90 days'
GROUP BY ext
ORDER BY file_count DESC
```

### 10. Model preferences

```sql
SELECT usage_model as model, COUNT(*) as turns
FROM events
WHERE timestamp > now() - INTERVAL '30 days'
AND usage_model IS NOT NULL
GROUP BY usage_model
ORDER BY turns DESC
LIMIT 10
```

### 11. Sample prompts (for qualitative analysis)

```sql
SELECT substr(user_message, 1, 120) as msg
FROM turns
WHERE timestamp > now() - INTERVAL '30 days'
AND user_message IS NOT NULL
AND length(COALESCE(user_message, '')) BETWEEN 5 AND 80
ORDER BY RANDOM()
LIMIT 40
```

### 12. Workflow keywords

```sql
SELECT
  COUNT(CASE WHEN user_message ILIKE '%create a plan%' THEN 1 END) as plan_requests,
  COUNT(CASE WHEN user_message ILIKE 'implement%' AND length(COALESCE(user_message, '')) < 30 THEN 1 END) as implement_commands,
  COUNT(CASE WHEN user_message ILIKE '%commit%' THEN 1 END) as commit_mentions,
  COUNT(CASE WHEN user_message ILIKE '%PR %' OR user_message ILIKE '%pull request%' THEN 1 END) as pr_mentions,
  COUNT(CASE WHEN user_message ILIKE '%scan%' OR user_message ILIKE '%skill%' THEN 1 END) as skill_mentions,
  COUNT(CASE WHEN user_message ILIKE '%doc%' AND (user_message ILIKE '%check%' OR user_message ILIKE '%update%') THEN 1 END) as doc_check_mentions
FROM turns
WHERE timestamp > now() - INTERVAL '90 days'
AND user_message IS NOT NULL
```

## Output

Save the report to `Reports/<date>-copilot-usage-report.md` in the dotfiles repo using the date format `YYYY-MM-DD`.

### ASCII bar chart

For hour-of-day visualization, generate a proportional bar chart using `█` and `░` characters:

```
 8h ████████░░░░░░░░░░░░  486
 9h ████████████░░░░░░░░  729
```

Scale bars to 20 characters wide where the highest count fills all 20 with `█` and the rest with `░`.

### Analysis

After gathering all data, synthesize **Key Behavioral Patterns** — look for:
- **Session shape** — bimodal (quick + marathon)? steady medium?
- **Prompting brevity** — how terse vs verbose?
- **Directive vs inquisitive** — commands vs questions ratio
- **Workflow patterns** — plan→implement? direct implementation?
- **Commit preferences** — granularity, push behavior
- **Course correction style** — how redirections are phrased
- **Maintenance rituals** — recurring patterns
- **Technical domain** — dominant file types and tools

## Comparing Reports

When a previous report exists in `Reports/`, compare key metrics to show trends (sessions up/down, prompt length changes, new patterns, shift in repos or models).
