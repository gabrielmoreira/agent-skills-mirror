#!/usr/bin/env bun
import { Command } from 'commander'
import fg from 'fast-glob'
import { DuckDBConnection, DuckDBInstance } from '@duckdb/node-api'
import { mkdir, readFile, rm, stat } from 'node:fs/promises'
import { basename, dirname, resolve } from 'node:path'

const AGENT_DIR = process.env.PI_CODING_AGENT_DIR ?? `${process.env.HOME}/.pi/agent`
const DEFAULT_ROOT = `${AGENT_DIR}/sessions`
const DEFAULT_CACHE_DIR = `${AGENT_DIR}/cache/session-reflect`
const DEFAULT_DB = `${DEFAULT_CACHE_DIR}/pi-sessions.duckdb`
const DEFAULT_BUILD_LIMIT = 100

type Json = Record<string, any>
type OutputFormat = 'table' | 'json' | 'markdown'

type Db = {
  instance: DuckDBInstance
  connection: DuckDBConnection
}

const PRESETS: Record<string, { description: string; sql: string }> = {
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

const program = new Command()
program
  .name('session-db')
  .description(
    'Agent helper for loading pi session JSONL into DuckDB and retrieving evidence. Do not treat output as conclusions.'
  )
  .option('--db <path>', 'DuckDB database path', DEFAULT_DB)
  .option('--cache-dir <dir>', 'cache directory used for the default DB path', DEFAULT_CACHE_DIR)
  .option('-f, --format <format>', 'output format: table, json, markdown', 'table')

program
  .command('build')
  .description('Rebuild the DuckDB evidence database from pi JSONL sessions')
  .option('--root <dir>', 'pi session log root', DEFAULT_ROOT)
  .option('--limit <n>', 'newest session files to ingest', parseIntArg, DEFAULT_BUILD_LIMIT)
  .option('--all', 'ingest all session files; can be slow')
  .action(async (opts) => {
    const dbPath = getDbPath()
    await mkdir(dirname(dbPath), { recursive: true })
    await resetDbFile(dbPath)
    const db = await openDb(dbPath)
    await rebuildSchema(db.connection)
    const limit = opts.all ? undefined : Number(opts.limit)
    const files = await newestSessionFiles(opts.root, limit)
    await ingestFiles(db.connection, files)
    await createFtsIndex(db.connection)
    await db.connection.run('checkpoint')
    await printRows(db.connection, PRESETS.overview!.sql)
  })

program
  .command('doctor')
  .description('Show session root, cache, DB path, and candidate session count')
  .option('--root <dir>', 'pi session log root', DEFAULT_ROOT)
  .action(async (opts) => {
    const files = await newestSessionFiles(opts.root, undefined)
    let dbExists = false
    let dbSize = 0
    try {
      const info = await stat(getDbPath())
      dbExists = true
      dbSize = info.size
    } catch {
      // DB has not been built yet.
    }

    printResultRows([
      {
        session_root: opts.root,
        cache_dir: getCacheDir(),
        db_path: getDbPath(),
        db_exists: dbExists,
        db_size_bytes: dbSize,
        session_files: files.length,
        default_build_limit: DEFAULT_BUILD_LIMIT
      }
    ])
  })

program
  .command('clean')
  .description('Remove the session-reflect DB files')
  .action(async () => {
    const dbPath = getDbPath()
    assertSafeDbPath(dbPath)
    await resetDbFile(dbPath)
    printResultRows([{ removed: dbPath }])
  })

program
  .command('sql <query>')
  .description('Run an arbitrary SQL query against the evidence database')
  .action(async (query) => {
    const db = await openDb(getDbPath())
    await printRows(db.connection, query)
  })

program
  .command('preset [name]')
  .description('List or run named evidence queries')
  .option('--list', 'list available presets')
  .action(async (name, opts) => {
    if (opts.list || !name) {
      printResultRows(
        Object.entries(PRESETS).map(([preset, value]) => ({
          preset,
          description: value.description
        }))
      )
      return
    }
    const preset = PRESETS[name]
    if (!preset)
      throw new Error(`Unknown preset: ${name}. Use: bun scripts/session-db.ts preset --list`)
    const db = await openDb(getDbPath())
    await printRows(db.connection, preset.sql)
  })

program
  .command('turns')
  .description('Show recent turns, usually user turns')
  .option('--role <role>', 'message role filter', 'user')
  .option('--limit <n>', 'row limit', parseIntArg, 50)
  .option('--short', 'only short messages')
  .action(async (opts) => {
    const db = await openDb(getDbPath())
    const where = [`role = ${sqlString(opts.role)}`]
    if (opts.short) where.push('length(text) between 1 and 160')
    await printRows(
      db.connection,
      `
      select message_key, timestamp, project_key, left(replace(text, '\n', ' '), 500) as text
      from message_context
      where ${where.join(' and ')}
      order by timestamp desc
      limit ${Number(opts.limit)}
    `
    )
  })

program
  .command('search <query>')
  .description('Search message text with literal ILIKE first, DuckDB FTS second')
  .option('--role <role>', 'optional role filter')
  .option('--limit <n>', 'row limit', parseIntArg, 25)
  .action(async (query, opts) => {
    const db = await openDb(getDbPath())
    const roleClause = opts.role ? `and role = ${sqlString(opts.role)}` : ''
    const literalSql = `
      select message_key, timestamp, role, project_key, cast(null as double) as score,
        left(replace(text, '\n', ' '), 700) as text
      from message_context
      where text ilike ${sqlString(`%${query}%`)} ${roleClause}
      order by timestamp desc
      limit ${Number(opts.limit)}
    `
    const literalRows = await rows(db.connection, literalSql)
    if (literalRows.length > 0) {
      printResultRows(literalRows)
      return
    }

    const ftsSql = `
      select message_key, timestamp, role, project_key,
        fts_main_messages.match_bm25(message_id, ${sqlString(query)}) as score,
        left(replace(text, '\n', ' '), 700) as text
      from message_context
      where score is not null ${roleClause}
      order by score desc, timestamp desc
      limit ${Number(opts.limit)}
    `
    try {
      await printRows(db.connection, ftsSql)
    } catch {
      printResultRows([])
    }
  })

program
  .command('examples')
  .description('Show compact context windows for repeated or searched user turns')
  .requiredOption('--text <text>', 'user turn text to find')
  .option('--contains', 'match messages containing text instead of exact normalized turn')
  .option('--limit <n>', 'number of examples', parseIntArg, 5)
  .option('--before <n>', 'turns before each match', parseIntArg, 3)
  .option('--after <n>', 'turns after each match', parseIntArg, 5)
  .option('--chars <n>', 'max chars for non-target rows', parseIntArg, 240)
  .option('--focus-chars <n>', 'max chars for matched row', parseIntArg, 700)
  .option('--hide-tools', 'omit toolResult rows from context windows', true)
  .action(async (opts) => {
    const db = await openDb(getDbPath())
    const matchPredicate = opts.contains
      ? `text ilike ${sqlString(`%${opts.text}%`)}`
      : `lower(trim(regexp_replace(text, '\\s+', ' ', 'g'))) = lower(trim(regexp_replace(${sqlString(opts.text)}, '\\s+', ' ', 'g')))`
    const matches = await rows(
      db.connection,
      `
      select message_key, timestamp, project_key, left(replace(text, '\n', ' '), 500) as text
      from message_context
      where role = 'user' and ${matchPredicate}
      order by timestamp desc
      limit ${Number(opts.limit)}
    `
    )

    if (matches.length === 0) {
      printResultRows([])
      return
    }

    for (const [index, match] of matches.entries()) {
      printSection(
        `Example ${index + 1}: ${match.message_key} — ${match.timestamp} — ${match.project_key}`
      )
      const contextRows = await compactContextRows(db.connection, String(match.message_key), {
        before: Number(opts.before),
        after: Number(opts.after),
        chars: Number(opts.chars),
        focusChars: Number(opts.focusChars),
        hideTools: Boolean(opts.hideTools)
      })
      printResultRows(contextRows)
    }
  })

program
  .command('interventions')
  .description(
    'Retrieve broad high-signal user intervention candidates; signals are evidence leads, not conclusions'
  )
  .option('--limit <n>', 'candidate limit', parseIntArg, 30)
  .option('--context', 'print compact context windows for each candidate')
  .option('--before <n>', 'turns before each candidate when --context is used', parseIntArg, 4)
  .option('--after <n>', 'turns after each candidate when --context is used', parseIntArg, 6)
  .option('--chars <n>', 'max chars for non-target rows', parseIntArg, 220)
  .option('--focus-chars <n>', 'max chars for candidate row', parseIntArg, 800)
  .option('--hide-tools', 'omit toolResult rows from context windows', true)
  .option(
    '--max-len <n>',
    'skip very long pasted/log-like user turns unless set higher',
    parseIntArg,
    2000
  )
  .option('--min-score <n>', 'minimum weighted signal score', parseIntArg, 1)
  .option('--sort <mode>', 'sort mode: score or recent', 'score')
  .option(
    '--signal <name>',
    'comma-separated signal filter, e.g. autonomy_boundary,evidence_challenge'
  )
  .option('--project <pattern>', 'ILIKE filter for project_key/cwd/path')
  .option('--since <date>', 'only candidates at or after date/timestamp')
  .option('--until <date>', 'only candidates before date/timestamp')
  .option('--sample', 'time-spread sample from the matching candidate pool')
  .option('--pool <n>', 'candidate pool size for --sample', parseIntArg, 1000)
  .option(
    '--pasted <mode>',
    'pasted/code/log-like turn handling: exclude, include, or only',
    'exclude'
  )
  .action(async (opts) => {
    const db = await openDb(getDbPath())
    const requestedLimit = Number(opts.limit)
    const candidateLimit = opts.sample
      ? Math.max(Number(opts.pool), requestedLimit)
      : requestedLimit
    const queryOptions = {
      limit: candidateLimit,
      maxLen: Number(opts.maxLen),
      minScore: Number(opts.minScore),
      sort: opts.sample ? ('recent' as const) : parseInterventionSort(opts.sort),
      signals: parseSignalFilter(opts.signal),
      project: opts.project as string | undefined,
      since: opts.since as string | undefined,
      until: opts.until as string | undefined,
      pasted: parsePastedMode(opts.pasted)
    }
    const candidatePool = await rows(db.connection, interventionCandidatesSql(queryOptions))
    const candidates = opts.sample ? evenSample(candidatePool, requestedLimit) : candidatePool

    if (!opts.context) {
      printResultRows(candidates)
      return
    }

    if (candidates.length === 0) {
      printResultRows([])
      return
    }

    for (const candidate of candidates) {
      printSection(
        `Intervention candidate: ${candidate.message_key} — ${candidate.timestamp} — ${candidate.project_key} — score=${candidate.score} — ${candidate.signals}`
      )
      printResultRows(
        await compactContextRows(db.connection, String(candidate.message_key), {
          before: Number(opts.before),
          after: Number(opts.after),
          chars: Number(opts.chars),
          focusChars: Number(opts.focusChars),
          hideTools: Boolean(opts.hideTools)
        })
      )
    }
  })

program
  .command('sample')
  .description('Sample compact contexts across the most repeated exact short user turns')
  .option('--turns <n>', 'number of repeated turns to sample', parseIntArg, 5)
  .option('--examples <n>', 'examples per repeated turn, spread across time', parseIntArg, 2)
  .option('--min-count <n>', 'minimum exact repeat count', parseIntArg, 3)
  .option('--before <n>', 'turns before each match', parseIntArg, 3)
  .option('--after <n>', 'turns after each match', parseIntArg, 5)
  .option('--chars <n>', 'max chars for non-target rows', parseIntArg, 220)
  .option('--focus-chars <n>', 'max chars for matched row', parseIntArg, 700)
  .option('--hide-tools', 'omit toolResult rows from context windows', true)
  .action(async (opts) => {
    const db = await openDb(getDbPath())
    const repeatedTurns = await rows(
      db.connection,
      `
      select lower(trim(regexp_replace(text, '\\s+', ' ', 'g'))) as turn, count(*) as n
      from messages
      where role = 'user' and length(trim(text)) between 1 and 160
      group by 1
      having count(*) >= ${Number(opts.minCount)}
      order by n desc, turn
      limit ${Number(opts.turns)}
    `
    )

    for (const turn of repeatedTurns) {
      printSection(`Repeated turn: "${turn.turn}" (${turn.n} matches)`)
      const matches = await rows(
        db.connection,
        `
        select message_key, timestamp, project_key
        from message_context
        where role = 'user'
          and lower(trim(regexp_replace(text, '\\s+', ' ', 'g'))) = ${sqlString(String(turn.turn))}
        order by timestamp desc
      `
      )
      const sampled = evenSample(matches, Number(opts.examples))
      for (const [index, match] of sampled.entries()) {
        printSection(
          `Sample ${index + 1}: ${match.message_key} — ${match.timestamp} — ${match.project_key}`
        )
        printResultRows(
          await compactContextRows(db.connection, String(match.message_key), {
            before: Number(opts.before),
            after: Number(opts.after),
            chars: Number(opts.chars),
            focusChars: Number(opts.focusChars),
            hideTools: Boolean(opts.hideTools)
          })
        )
      }
    }
  })

program
  .command('context <messageKey>')
  .description('Show surrounding turns for a message_key from turns/search output')
  .option('--before <n>', 'turns before', parseIntArg, 4)
  .option('--after <n>', 'turns after', parseIntArg, 8)
  .option('--compact', 'ellipsize context rows for agent-readable evidence windows')
  .option('--chars <n>', 'max chars for non-target rows in compact mode', parseIntArg, 280)
  .option('--focus-chars <n>', 'max chars for target row in compact mode', parseIntArg, 900)
  .option('--hide-tools', 'omit toolResult rows from the context window')
  .action(async (messageKey, opts) => {
    const db = await openDb(getDbPath())

    if (opts.compact) {
      printResultRows(
        await compactContextRows(db.connection, messageKey, {
          before: Number(opts.before),
          after: Number(opts.after),
          chars: Number(opts.chars),
          focusChars: Number(opts.focusChars),
          hideTools: Boolean(opts.hideTools)
        })
      )
      return
    }

    const contextRows = await rawContextRows(
      db.connection,
      messageKey,
      Number(opts.before),
      Number(opts.after),
      Boolean(opts.hideTools)
    )
    printResultRows(
      contextRows.map((row) => ({
        message_key: row.message_key,
        turn_index: row.turn_index,
        timestamp: row.timestamp,
        role: row.role,
        text: ellipsize(String(row.text ?? ''), 1200)
      }))
    )
  })

program
  .command('ngrams')
  .description('Mine repeated n-grams from user messages without assigning behavioral labels')
  .option('--n <n>', 'n-gram size', parseIntArg, 2)
  .option('--min-count <n>', 'minimum count', parseIntArg, 3)
  .option('--limit <n>', 'row limit', parseIntArg, 50)
  .action(async (opts) => {
    const db = await openDb(getDbPath())
    await printRows(
      db.connection,
      `
      with tokens as (
        select message_id, ordinality as pos, token
        from user_message_tokens,
          unnest(tokens) with ordinality as t(token, ordinality)
        where length(token) > 0
      ), grams as (
        select t1.message_id, t1.pos,
          string_agg(t2.token, ' ' order by t2.pos) as gram
        from tokens t1
        join tokens t2 on t2.message_id = t1.message_id and t2.pos between t1.pos and t1.pos + ${Number(opts.n) - 1}
        group by t1.message_id, t1.pos
        having count(*) = ${Number(opts.n)}
      )
      select gram, count(*) as n
      from grams
      where length(gram) > 1
      group by gram
      having count(*) >= ${Number(opts.minCount)}
      order by n desc, gram
      limit ${Number(opts.limit)}
    `
    )
  })

program.parseAsync()

function getCacheDir(): string {
  return String(program.opts().cacheDir ?? DEFAULT_CACHE_DIR)
}

function getDbPath(): string {
  const db = String(program.opts().db ?? DEFAULT_DB)
  return db === DEFAULT_DB ? `${getCacheDir()}/pi-sessions.duckdb` : db
}

function assertSafeDbPath(path: string): void {
  const resolved = resolve(path)
  const cacheDir = resolve(getCacheDir())

  if (!resolved.startsWith(`${cacheDir}/`)) {
    throw new Error(`Refusing to clean outside cache dir: ${resolved}`)
  }

  if (resolved === cacheDir || resolved === resolve(process.env.HOME ?? '/')) {
    throw new Error(`Refusing suspicious clean path: ${resolved}`)
  }
}

async function resetDbFile(path: string) {
  await rm(path, { force: true })
  await rm(`${path}.wal`, { force: true })
}

async function openDb(path: string): Promise<Db> {
  const instance = await DuckDBInstance.create(path)
  const connection = await instance.connect()
  return { instance, connection }
}

async function rebuildSchema(conn: DuckDBConnection) {
  await conn.run(`
    drop table if exists tool_calls;
    drop table if exists messages;
    drop table if exists events;
    drop table if exists sessions;
    drop sequence if exists message_id_seq;

    create table sessions(
      session_id varchar primary key,
      path varchar not null,
      cwd varchar,
      project_key varchar,
      started_at timestamp,
      ended_at timestamp,
      file_mtime timestamp
    );

    create table events(
      event_key varchar primary key,
      session_id varchar not null,
      event_index integer not null,
      event_id varchar,
      parent_id varchar,
      type varchar,
      timestamp timestamp
    );

    create table messages(
      message_key varchar primary key,
      message_id integer not null,
      session_id varchar not null,
      event_key varchar not null,
      turn_index integer not null,
      role varchar,
      timestamp timestamp,
      text varchar
    );

    create table tool_calls(
      tool_call_key varchar primary key,
      session_id varchar not null,
      message_key varchar not null,
      turn_index integer,
      name varchar,
      arguments_json json
    );

    create sequence message_id_seq start 1;
  `)
}

async function ingestFiles(conn: DuckDBConnection, files: string[]) {
  const sessionAppender = await conn.createAppender('sessions')
  const eventAppender = await conn.createAppender('events')
  const messageAppender = await conn.createAppender('messages')
  const toolAppender = await conn.createAppender('tool_calls')

  let ingested = 0
  let nextMessageId = 1
  for (const path of files) {
    const text = await readFile(path, 'utf8')
    const parsed: Json[] = []
    for (const line of text.split('\n')) {
      if (!line.trim()) continue
      try {
        parsed.push(JSON.parse(line))
      } catch {
        /* tolerate old/corrupt lines */
      }
    }
    if (parsed.length === 0) continue

    const sessionEvent = parsed.find((event) => event.type === 'session') ?? {}
    const sessionId = String(sessionEvent.id ?? basename(path).replace(/\.jsonl$/, ''))
    const timestamps = parsed
      .map((event) => event.timestamp)
      .filter(Boolean)
      .sort()
    const fileStat = await stat(path)

    appendRow(sessionAppender, [
      sessionId,
      path,
      sessionEvent.cwd ?? null,
      basename(dirname(path)),
      sessionEvent.timestamp ?? timestamps[0] ?? null,
      timestamps.at(-1) ?? null,
      fileStat.mtime.toISOString()
    ])

    let turn = 0
    for (const [eventIndex, event] of parsed.entries()) {
      const eventKey = `${sessionId}:${eventIndex}`
      appendRow(eventAppender, [
        eventKey,
        sessionId,
        eventIndex,
        event.id ?? null,
        event.parentId ?? null,
        event.type ?? null,
        event.timestamp ?? null
      ])

      if (event.type !== 'message') continue
      const msg = event.message ?? {}
      const role = msg.role ?? null
      const messageKey = `${sessionId}:m:${turn}`
      const messageId = nextMessageId++
      const contentText = contentToText(msg.content)

      appendRow(messageAppender, [
        messageKey,
        messageId,
        sessionId,
        eventKey,
        turn,
        role,
        event.timestamp ?? msg.timestamp ?? null,
        contentText
      ])

      if (Array.isArray(msg.content)) {
        let toolIndex = 0
        for (const part of msg.content) {
          if (part && typeof part === 'object' && part.type === 'toolCall') {
            appendRow(toolAppender, [
              `${messageKey}:tool:${toolIndex++}`,
              sessionId,
              messageKey,
              turn,
              part.name ?? null,
              JSON.stringify(part.arguments ?? null)
            ])
          }
        }
      }
      turn += 1
    }

    ingested += 1
    if (ingested % 100 === 0) console.error(`ingested ${ingested}/${files.length}`)
  }

  sessionAppender.closeSync()
  eventAppender.closeSync()
  messageAppender.closeSync()
  toolAppender.closeSync()

  await conn.run(`
    create or replace view message_context as
      select m.*, s.path, s.cwd, s.project_key, s.started_at
      from messages m join sessions s using (session_id);

    create or replace view user_turns as
      select * from message_context where role = 'user';

    create or replace view user_message_tokens as
      select
        message_id,
        regexp_split_to_array(
          regexp_replace(lower(text), '[^[:alnum:]А-Яа-яЁё]+', ' ', 'g'),
          '\\s+'
        ) as tokens
      from messages
      where role = 'user' and text is not null and length(trim(text)) > 0;
  `)
}

async function createFtsIndex(conn: DuckDBConnection) {
  try {
    await conn.run(`INSTALL fts; LOAD fts;`)
    await conn.run(
      `PRAGMA create_fts_index('messages', 'message_id', 'text', stemmer = 'none', stopwords = 'none', ignore = '', overwrite = 1);`
    )
  } catch (error) {
    console.error(`FTS index skipped: ${error instanceof Error ? error.message : String(error)}`)
  }
}

const INTERVENTION_SIGNALS = [
  'emotional_intensity',
  'direction_reversal',
  'abstraction_mismatch',
  'evidence_challenge',
  'convention_violation',
  'autonomy_boundary',
  'quality_disgust',
  'orientation_reset'
] as const

type InterventionSignal = (typeof INTERVENTION_SIGNALS)[number]

type InterventionQueryOptions = {
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

function interventionCandidatesSql(options: InterventionQueryOptions) {
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

async function rawContextRows(
  conn: DuckDBConnection,
  messageKey: string,
  before: number,
  after: number,
  hideTools: boolean
) {
  const targetRows = await rows(
    conn,
    `select session_id, turn_index from messages where message_key = ${sqlString(messageKey)} limit 1`
  )
  const target = targetRows[0]
  if (!target) throw new Error(`No message found for key ${messageKey}`)
  const toolClause = hideTools ? `and role != 'toolResult'` : ''
  return rows(
    conn,
    `
    select
      message_key,
      turn_index,
      timestamp,
      role,
      text,
      message_key = ${sqlString(messageKey)} as focus
    from messages
    where session_id = ${sqlString(String(target.session_id))}
      and turn_index between ${Number(target.turn_index) - before} and ${Number(target.turn_index) + after}
      ${toolClause}
    order by turn_index
  `
  )
}

async function compactContextRows(
  conn: DuckDBConnection,
  messageKey: string,
  options: { before: number; after: number; chars: number; focusChars: number; hideTools: boolean }
) {
  const contextRows = await rawContextRows(
    conn,
    messageKey,
    options.before,
    options.after,
    options.hideTools
  )
  return contextRows.map((row) => ({
    mark: row.focus ? '>>>' : '',
    message_key: row.message_key,
    turn_index: row.turn_index,
    role: row.role,
    text: ellipsize(
      String(row.text ?? ''),
      row.focus ? options.focusChars : compactLimitForRole(String(row.role ?? ''), options.chars)
    )
  }))
}

async function newestSessionFiles(root: string, limit?: number) {
  const files = await fg(['**/*.jsonl'], { cwd: root, absolute: true, onlyFiles: true })
  const stats = await Promise.all(
    files.map(async (path) => ({ path, mtime: (await stat(path)).mtimeMs }))
  )
  const sorted = stats.sort((a, b) => b.mtime - a.mtime).map((row) => row.path)
  return typeof limit === 'number' ? sorted.slice(0, limit) : sorted
}

function contentToText(content: unknown): string {
  if (typeof content === 'string') return content
  if (!Array.isArray(content)) return ''
  return content
    .map((part) => {
      if (typeof part === 'string') return part
      if (!part || typeof part !== 'object') return ''
      if ('text' in part) return String((part as { text?: unknown }).text ?? '')
      if ((part as { type?: unknown }).type === 'toolCall')
        return `[toolCall:${String((part as { name?: unknown }).name ?? 'unknown')}]`
      return `[${String((part as { type?: unknown }).type ?? 'part')}]`
    })
    .filter(Boolean)
    .join('\n')
}

function appendRow(appender: any, values: unknown[]) {
  for (const value of values) {
    if (value === null || value === undefined) appender.appendNull()
    else if (typeof value === 'number') appender.appendInteger(value)
    else appender.appendVarchar(String(value))
  }
  appender.endRow()
}

async function rows(conn: DuckDBConnection, sql: string): Promise<Json[]> {
  return (await conn.runAndReadAll(sql)).getRowObjectsJson() as Json[]
}

async function printRows(conn: DuckDBConnection, sql: string) {
  printResultRows(await rows(conn, sql))
}

function printResultRows(resultRows: Json[]) {
  const format = getFormat()
  if (format === 'json') {
    console.log(JSON.stringify(resultRows, null, 2))
    return
  }
  if (format === 'markdown') {
    console.log(markdownTable(resultRows))
    return
  }
  console.table(
    resultRows.map((row) =>
      Object.fromEntries(Object.entries(row).map(([k, v]) => [k, truncate(v)]))
    )
  )
}

function printSection(title: string) {
  if (getFormat() === 'markdown') console.log(`\n## ${title}\n`)
  else console.log(`\n${title}`)
}

function evenSample<T>(items: T[], count: number): T[] {
  if (count <= 0 || items.length === 0) return []
  if (items.length <= count) return items
  if (count === 1) return [items[0]!]
  const indexes = new Set<number>()
  for (let i = 0; i < count; i += 1) {
    indexes.add(Math.round((i * (items.length - 1)) / (count - 1)))
  }
  return [...indexes].sort((a, b) => a - b).map((index) => items[index]!)
}

function getFormat(): OutputFormat {
  const value = String(program.opts().format ?? 'table')
  if (value === 'table' || value === 'json' || value === 'markdown') return value
  throw new Error(`Unknown format: ${value}. Expected table, json, or markdown.`)
}

function markdownTable(resultRows: Json[]) {
  if (resultRows.length === 0) return '_No rows._'
  const headers = Object.keys(resultRows[0]!)
  const escape = (value: unknown) =>
    String(truncate(value)).replace(/\|/g, '\\|').replace(/\n/g, ' ')
  return [
    `| ${headers.map(escape).join(' | ')} |`,
    `| ${headers.map(() => '---').join(' | ')} |`,
    ...resultRows.map((row) => `| ${headers.map((header) => escape(row[header])).join(' | ')} |`)
  ].join('\n')
}

function truncate(value: unknown) {
  if (typeof value === 'string' && value.length > 120) return ellipsize(value, 120)
  return value
}

function compactLimitForRole(role: string, requested: number) {
  if (role === 'toolResult') return Math.min(requested, 160)
  if (role === 'assistant') return Math.min(requested, 360)
  return requested
}

function ellipsize(value: string, maxChars: number) {
  const normalized = value.replace(/\s+/g, ' ').trim()
  if (normalized.length <= maxChars) return normalized
  if (maxChars <= 1) return '…'
  return `${normalized.slice(0, maxChars - 1)}…`
}

function sqlString(value: string) {
  return `'${String(value).replace(/'/g, "''")}'`
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

function parseSignalFilter(value?: string): InterventionSignal[] {
  if (!value) return []
  const signals = value
    .split(',')
    .map((signal) => signal.trim())
    .filter(Boolean)
  for (const signal of signals) {
    if (!(INTERVENTION_SIGNALS as readonly string[]).includes(signal)) {
      throw new Error(
        `Unknown intervention signal: ${signal}. Expected one of: ${INTERVENTION_SIGNALS.join(', ')}`
      )
    }
  }
  return signals as InterventionSignal[]
}

function parseInterventionSort(value: string): 'score' | 'recent' {
  if (value === 'score' || value === 'recent') return value
  throw new Error(`Unknown intervention sort: ${value}. Expected score or recent.`)
}

function parsePastedMode(value: string): 'exclude' | 'include' | 'only' {
  if (value === 'exclude' || value === 'include' || value === 'only') return value
  throw new Error(`Unknown pasted mode: ${value}. Expected exclude, include, or only.`)
}

function parseIntArg(value: string) {
  const parsed = Number.parseInt(value, 10)
  if (!Number.isFinite(parsed)) throw new Error(`Expected integer, got ${value}`)
  return parsed
}
