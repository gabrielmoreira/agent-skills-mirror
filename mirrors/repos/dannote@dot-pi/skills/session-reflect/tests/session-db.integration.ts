import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { mkdtemp, rm, utimes, writeFile } from 'node:fs/promises'
import { join } from 'node:path'
import { tmpdir } from 'node:os'

const cwd = new URL('..', import.meta.url).pathname
let tempDir = ''
let agentDir = ''

beforeEach(async () => {
  tempDir = await mkdtemp(join(tmpdir(), 'session-reflect-test-'))
  agentDir = join(tempDir, 'agent')
})

afterEach(async () => {
  await rm(tempDir, { recursive: true, force: true })
})

describe('session-db CLI', () => {
  test('doctor reports the Pi cache path, not a project-local analysis path', async () => {
    await writeSession('project-a', 'one.jsonl', 0)

    const result = run(['--format', 'json', 'doctor'])
    const rows = JSON.parse(result.stdout.toString())

    expect(rows[0].cache_dir).toBe(join(agentDir, 'cache', 'session-reflect'))
    expect(rows[0].db_path).toBe(join(agentDir, 'cache', 'session-reflect', 'pi-sessions.duckdb'))
    expect(rows[0].default_build_limit).toBe(100)
  })

  test('build defaults to the newest 100 sessions and clean removes the DB', async () => {
    for (let index = 0; index < 101; index += 1) {
      await writeSession('project-a', `${String(index).padStart(3, '0')}.jsonl`, index)
    }

    run(['build'])

    const overview = JSON.parse(run(['--format', 'json', 'preset', 'overview']).stdout.toString())
    expect(overview[0].sessions).toBe('100')

    const doctorBeforeClean = JSON.parse(run(['--format', 'json', 'doctor']).stdout.toString())
    expect(doctorBeforeClean[0].db_exists).toBe(true)

    run(['clean'])

    const doctorAfterClean = JSON.parse(run(['--format', 'json', 'doctor']).stdout.toString())
    expect(doctorAfterClean[0].db_exists).toBe(false)
  })
})

async function writeSession(project: string, filename: string, index: number): Promise<void> {
  const sessionDir = join(agentDir, 'sessions', project)
  await Bun.$`mkdir -p ${sessionDir}`.quiet()
  const timestamp = new Date(Date.UTC(2026, 0, 1, 0, 0, index)).toISOString()
  const sessionId = `session-${index}`
  const content = [
    {
      type: 'session',
      id: sessionId,
      cwd: `/tmp/${project}`,
      timestamp
    },
    {
      type: 'message',
      timestamp,
      message: { role: 'user', content: 'Go ahead' }
    },
    {
      type: 'message',
      timestamp,
      message: { role: 'assistant', content: 'Done' }
    }
  ]
    .map((line) => JSON.stringify(line))
    .join('\n')
  const path = join(sessionDir, filename)
  await writeFile(path, `${content}\n`)
  const date = new Date(Date.UTC(2026, 0, 1, 0, 0, index))
  await utimes(path, date, date)
}

function run(args: string[]): { stdout: Buffer; stderr: Buffer } {
  const result = Bun.spawnSync({
    cmd: ['bun', 'scripts/session-db.ts', ...args],
    cwd,
    env: {
      ...process.env,
      PI_CODING_AGENT_DIR: agentDir
    },
    stdout: 'pipe',
    stderr: 'pipe'
  })

  if (result.exitCode !== 0) {
    throw new Error(
      `session-db failed (${result.exitCode})\nstdout:\n${result.stdout}\nstderr:\n${result.stderr}`
    )
  }

  return { stdout: result.stdout, stderr: result.stderr }
}
