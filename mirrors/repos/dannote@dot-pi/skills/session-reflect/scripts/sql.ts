export const PRESETS: Record<string, { description: string; sql: string }> = {
  overview: {
    description: 'Dataset size and date range',
    sql: `
      select
        count(*) as sessions,
        min(started_at) as first_session,
        max(started_at) as last_session,
        (select count(*) from messages) as messages,
        (select count(*) from messages where role = 'user') as user_messages,
        (select count(*) from tool_calls) as tool_calls
      from sessions
    `
  },
  roles: {
    description: 'Message counts by role',
    sql: `
      select role, count(*) as messages
      from messages
      group by role
      order by messages desc
    `
  },
  'recent-user-turns': {
    description: 'Recent user turns',
    sql: `
      select message_key, timestamp, project_key, left(replace(text, '\n', ' '), 500) as text
      from message_context
      where role = 'user'
      order by timestamp desc
      limit 80
    `
  },
  'short-user-turns': {
    description: 'Recent short user turns that often need context',
    sql: `
      select message_key, timestamp, project_key, left(replace(text, '\n', ' '), 300) as text
      from message_context
      where role = 'user' and length(trim(text)) between 1 and 160
      order by timestamp desc
      limit 100
    `
  },
  'exact-short-repeats': {
    description: 'Repeated exact short user turns; evidence leads only',
    sql: `
      select lower(trim(text)) as turn, count(*) as n
      from messages
      where role = 'user' and length(trim(text)) between 1 and 160
      group by 1
      having count(*) >= 3
      order by n desc, turn
      limit 100
    `
  },
  'tool-heavy-sessions': {
    description: 'Sessions with most tool calls',
    sql: `
      select s.session_id, s.project_key, s.path, count(*) as tool_calls
      from tool_calls t
      join sessions s using (session_id)
      group by s.session_id, s.project_key, s.path
      order by tool_calls desc
      limit 25
    `
  },
  'long-sessions': {
    description: 'High-iteration sessions by messages and tool calls',
    sql: `
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
      limit 25
    `
  },
  tools: {
    description: 'Tool call vocabulary',
    sql: `
      select name, count(*) as calls
      from tool_calls
      group by name
      order by calls desc
      limit 50
    `
  }
}

export function sqlString(value: string) {
  return `'${String(value).replace(/'/g, "''")}'`
}

export const INTERVENTION_SIGNALS = [
  'emotional_intensity',
  'direction_reversal',
  'abstraction_mismatch',
  'evidence_challenge',
  'convention_violation',
  'autonomy_boundary',
  'quality_disgust',
  'orientation_reset'
] as const

export type InterventionSignal = (typeof INTERVENTION_SIGNALS)[number]

export type InterventionQueryOptions = {
  limit: number
  maxLen: number
  minScore: number
  sort: 'score' | 'recent'
  signals: InterventionSignal[]
  project?: string
  since?: string
  until?: string
  pasted: 'exclude' | 'include' | 'only'
}

export function interventionCandidatesSql(options: InterventionQueryOptions) {
  const profanity = `regexp_matches(lower(text), '(fuck|shit|bullshit|wtf|fucking|бля|бляд|сука|хуй|хуе|пизд|еба|ёба|дерьм)')`
  const allCaps = `regexp_matches(text, '[A-ZА-ЯЁ]{5,}')`
  const repeatedPunctuation = `(text like '%!!!%' or text like '%???%')`
  const emotional = `(${profanity} or ${allCaps} or ${repeatedPunctuation})`
  const direction = `regexp_matches(lower(text), '\\b(stop|wait|pause|revert|undo|don.t|do not|not what i asked|wrong direction)\\b')`
  const abstraction = `regexp_matches(lower(text), '(wrong concept|wrong abstraction|wrong layer|not how .* works|building .* not|this is not how)')`
  const evidence = `regexp_matches(lower(text), '(where are the numbers|numbers to compare|did you verify|are you sure|show me|you claimed|claimed the opposite|evidence|prove)')`
  const convention = `regexp_matches(lower(text), '(we intentionally|project already|why new namespace|why json|don.t hand.?roll|existing function names|wrong namespace)')`
  const autonomy = `regexp_matches(lower(text), '(discuss before|ask me|why did you|stop autoresearch|i want to understand|where we are|what do you want to do)')`
  const quality = `regexp_matches(lower(text), '(ai slop|terrible name|stupid|what is this shit|pure shit|looks like .*shit)')`
  const orientation = `regexp_matches(lower(text), '(what is going on|wtf is going on|remind me|recap|where are we|what are next steps)')`
  const score = `
    (case when ${profanity} then 2 else 0 end) +
    (case when ${allCaps} then 1 else 0 end) +
    (case when ${repeatedPunctuation} then 1 else 0 end) +
    (case when ${direction} then 2 else 0 end) +
    (case when ${abstraction} then 3 else 0 end) +
    (case when ${evidence} then 2 else 0 end) +
    (case when ${convention} then 2 else 0 end) +
    (case when ${autonomy} then 3 else 0 end) +
    (case when ${quality} then 2 else 0 end) +
    (case when ${orientation} then 2 else 0 end)
  `
  const pasteScore = `
    (case when text like '%\`\`\`%' then 3 else 0 end) +
    (case when length(text) - length(replace(text, '\n', '')) >= 8 then 2 else 0 end) +
    (case when regexp_matches(text, '(^|\n)\\s*(\\+|-|[0-9]+\\s|\\$\\s)') then 2 else 0 end) +
    (case when length(text) > 300 and regexp_matches(text, '\\b(const|function|defp|defmodule|SELECT|WITH|import|alias|class|interface)\\b') then 2 else 0 end) +
    (case when regexp_matches(text, '(/[A-Za-z0-9_.-]+){2,}|[A-Za-z0-9_.-]+\\.(ex|exs|ts|tsx|js|json|md|yml|yaml|sql)') then 1 else 0 end)
  `

  return `
    with candidates as (
      select
        message_key,
        timestamp,
        project_key,
        ${emotional} as emotional_intensity,
        ${direction} as direction_reversal,
        ${abstraction} as abstraction_mismatch,
        ${evidence} as evidence_challenge,
        ${convention} as convention_violation,
        ${autonomy} as autonomy_boundary,
        ${quality} as quality_disgust,
        ${orientation} as orientation_reset,
        ${score} as score,
        ${pasteScore} as paste_score,
        left(replace(text, '\n', ' '), 700) as text
      from message_context
      where role = 'user'
        and length(text) <= ${options.maxLen}
        ${options.project ? `and (project_key ilike ${sqlString(`%${options.project}%`)} or cwd ilike ${sqlString(`%${options.project}%`)} or path ilike ${sqlString(`%${options.project}%`)})` : ''}
        ${options.since ? `and timestamp >= ${sqlString(options.since)}` : ''}
        ${options.until ? `and timestamp < ${sqlString(options.until)}` : ''}
        and (${[emotional, direction, abstraction, evidence, convention, autonomy, quality, orientation].join(' or ')})
    )
    select
      message_key,
      timestamp,
      project_key,
      score,
      paste_score,
      paste_score >= 3 as likely_pasted,
      array_to_string(list_filter([
        case when emotional_intensity then 'emotional_intensity' end,
        case when direction_reversal then 'direction_reversal' end,
        case when abstraction_mismatch then 'abstraction_mismatch' end,
        case when evidence_challenge then 'evidence_challenge' end,
        case when convention_violation then 'convention_violation' end,
        case when autonomy_boundary then 'autonomy_boundary' end,
        case when quality_disgust then 'quality_disgust' end,
        case when orientation_reset then 'orientation_reset' end
      ], x -> x is not null), ', ') as signals,
      text
    from candidates
    where score >= ${options.minScore}
      ${interventionSignalWhere(options.signals)}
      ${interventionPastedWhere(options.pasted)}
    order by ${options.sort === 'recent' ? 'timestamp desc, score desc' : 'score desc, timestamp desc'}
    limit ${options.limit}
  `
}

function interventionSignalWhere(signals: InterventionSignal[]) {
  if (signals.length === 0) return ''
  return `and (${signals.map((signal) => `${signal} = true`).join(' or ')})`
}

function interventionPastedWhere(mode: 'exclude' | 'include' | 'only') {
  if (mode === 'include') return ''
  if (mode === 'only') return 'and paste_score >= 3'
  return 'and paste_score < 3'
}
